"""stats.py against evaluate_alignment.bootstrap_alignment of the wallet-reputation reference."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from conftest import load_reference

from stats import PairedBootstrap, kendall_tau_b, percentile_ci, spearman

N_BOOT = 120


@pytest.fixture(scope="module")
def ref():
    return load_reference("evaluate_alignment")


@pytest.fixture(scope="module")
def merged(ref) -> pd.DataFrame:
    """Scores of the bootstrapped methods and every proxy of the transfer, allowance and Sybil families."""
    rng = np.random.default_rng(21)
    n = 90
    base = rng.lognormal(size=n)
    frame = {}
    for i, method_id in enumerate(ref.BOOTSTRAP_METHODS):
        s = base * rng.lognormal(sigma=0.5 + 0.1 * i, size=n)
        s[rng.random(n) < 0.2] = 0.0  # absent from the graph
        frame[ref.METHODS[method_id]] = s
    frame["in_degree"] = rng.poisson(1 + 2 * base).astype(float)
    frame["in_value"] = np.round(base * rng.lognormal(size=n), 1)
    frame["in_approve_degree"] = rng.poisson(base).astype(float)
    in_approve_value = base * rng.lognormal(size=n)
    in_approve_value[rng.random(n) < 0.1] = np.nan  # undefined for some members
    frame["in_approve_value"] = in_approve_value
    ratio = np.zeros(n)
    ratio[:3] = [0.5, 1.0, 0.25]  # rare non-zero values: many resamples are constant and skipped
    frame["inbound_counterparty_ratio"] = ratio
    frame["transfer_tenure_days"] = np.round(rng.uniform(0, 300, n))
    frame["active_months"] = rng.integers(0, 4, n).astype(float)
    return pd.DataFrame(frame)


@pytest.fixture(scope="module")
def expected(ref, merged):
    methods = {m: ref.METHODS[m] for m in ref.BOOTSTRAP_METHODS}
    return ref.bootstrap_alignment(merged, methods, n_boot=N_BOOT, seed=42)


@pytest.fixture(scope="module")
def boot(ref, merged) -> PairedBootstrap:
    bs = PairedBootstrap(len(merged), n_boot=N_BOOT, seed=42)
    for method_id in ref.BOOTSTRAP_METHODS:
        bs.add(method_id, merged[ref.METHODS[method_id]])
    bs.add_frame(merged, [p for p in ref.ALL_PROXIES if p in merged.columns])
    return bs


def _families(ref, merged) -> dict[str, list[str]]:
    return {
        f: [p for p in proxies if p in merged.columns]
        for f, proxies in ref.PROXY_FAMILIES.items()
        if any(p in merged.columns for p in proxies)
    }


def test_per_label_intervals_match_reference(ref, expected, boot):
    skipped = 0
    for method_id, per_proxy in expected["proxy_ci"].items():
        for proxy, row in per_proxy.items():
            got = boot.tau(method_id, proxy)
            assert got == row, (method_id, proxy)
            skipped += N_BOOT - row["n_boot"]
    assert skipped > 0  # the fixture does exercise skipped resamples


def test_family_means_match_reference(ref, merged, expected, boot):
    families = _families(ref, merged)
    for method_id, per_family in expected["family_ci"].items():
        for family, labels in families.items():
            got = boot.family(method_id, labels)
            if family not in per_family:
                assert got is None
                continue
            want = per_family[family]
            assert got["n_boot"] == want["n_boot"]
            for key in ("mean_tau", "ci_low", "ci_high"):
                assert abs(got[key] - want[key]) < 1e-15, (method_id, family, key)


def test_contrasts_match_reference(ref, merged, expected, boot):
    families = _families(ref, merged)

    def spec(pair):
        m, key = pair
        return (m, families[key]) if key in ref.PROXY_FAMILIES else (m, key)

    want = {row["label"]: row for row in expected["tau_diff"]}
    assert want
    for label, a, b, _group in ref.TAU_DIFF_CONTRASTS:
        got = boot.contrast(spec(a), spec(b))
        if label not in want:
            assert got is None
            continue
        row = want[label]
        assert got["n_boot"] == row["n_boot"]
        assert got["share_positive"] == row["share_positive"]
        for mine, theirs in (("a_tau", row["a"]["tau"]), ("b_tau", row["b"]["tau"]), ("delta_tau", row["delta_tau"])):
            assert abs(got[mine] - theirs) < 1e-15, (label, mine)
        assert abs(got["ci_low"] - row["ci_low"]) < 1e-15
        assert abs(got["ci_high"] - row["ci_high"]) < 1e-15


def test_inter_method_interval_matches_reference(expected, boot):
    got = boot.tau("endorserank_vt", "awp_paper")
    assert got == expected["inter_method_ci"]


def test_parallel_prefetch_equals_serial(ref, merged):
    pairs = [(m, p) for m in ref.BOOTSTRAP_METHODS[:3] for p in ("in_degree", "in_approve_value")]
    serial = PairedBootstrap(len(merged), n_boot=N_BOOT, seed=42)
    parallel = PairedBootstrap(len(merged), n_boot=N_BOOT, seed=42)
    for bs in (serial, parallel):
        bs.add_frame(merged.rename(columns={v: k for k, v in ref.METHODS.items()}))
    serial.prefetch(pairs)
    parallel.prefetch(pairs, workers=2)
    for pair in pairs:
        np.testing.assert_array_equal(parallel.samples(*pair), serial.samples(*pair))


def test_guards_and_intervals():
    x = np.arange(10.0)
    assert kendall_tau_b(x[:4], x[:4]) is None
    assert kendall_tau_b(x, np.ones(10)) is None
    assert spearman(x, np.ones(10)) is None
    y = x.copy()
    y[:6] = np.nan  # four finite pairs remain
    assert kendall_tau_b(x, y) is None
    assert abs(kendall_tau_b(x, -x) + 1.0) < 1e-12
    assert percentile_ci([]) == (None, None)
    samples = np.random.default_rng(0).normal(size=400)
    assert percentile_ci(samples) == (np.percentile(samples, 2.5), np.percentile(samples, 97.5))
    with pytest.raises(ValueError):
        PairedBootstrap(10, n_boot=5).add("short", x[:9])
