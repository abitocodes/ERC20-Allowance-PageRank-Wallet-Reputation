"""Holdout cutoff and label tests (no BigQuery)."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from common import load_config  # noqa: E402
from holdout import (  # noqa: E402
    build_holdout_fixture_frames,
    future_approval_labels,
    holdout_bounds,
    latest_positive_as_of,
    t1_positive_pairs,
)
from run_holdout_eval import run_holdout  # noqa: E402


def test_latest_as_of_drops_post_cutoff_and_revokes() -> None:
    approvals = pd.DataFrame(
        [
            {
                "block_timestamp": "2026-02-01T00:00:00Z",
                "block_number": 1,
                "log_index": 0,
                "token_address": "0xaaa",
                "owner": "0x" + "1" * 40,
                "spender": "0x" + "2" * 40,
                "value": 100,
            },
            {
                "block_timestamp": "2026-04-01T00:00:00Z",
                "block_number": 2,
                "log_index": 0,
                "token_address": "0xaaa",
                "owner": "0x" + "1" * 40,
                "spender": "0x" + "2" * 40,
                "value": 999,
            },
            {
                "block_timestamp": "2026-02-10T00:00:00Z",
                "block_number": 3,
                "log_index": 0,
                "token_address": "0xaaa",
                "owner": "0x" + "3" * 40,
                "spender": "0x" + "2" * 40,
                "value": 0,
            },
        ]
    )
    latest = latest_positive_as_of(approvals, pd.Timestamp("2026-02-28 23:59:59", tz="UTC"))
    assert len(latest) == 1
    assert float(latest.iloc[0]["value"]) == 100


def test_future_new_and_revoke_labels() -> None:
    owner_t1 = "0x" + "a" * 40
    owner_new = "0x" + "b" * 40
    spender = "0x" + "c" * 40
    token = "0x" + "d" * 40
    approvals = pd.DataFrame(
        [
            {
                "block_timestamp": "2026-02-01T00:00:00Z",
                "block_number": 1,
                "log_index": 0,
                "token_address": token,
                "owner": owner_t1,
                "spender": spender,
                "value": 10,
            },
            {
                "block_timestamp": "2026-04-01T00:00:00Z",
                "block_number": 2,
                "log_index": 0,
                "token_address": token,
                "owner": owner_new,
                "spender": spender,
                "value": 5,
            },
            {
                "block_timestamp": "2026-04-02T00:00:00Z",
                "block_number": 3,
                "log_index": 0,
                "token_address": token,
                "owner": owner_t1,
                "spender": spender,
                "value": 0,
            },
        ]
    )
    latest = latest_positive_as_of(approvals, pd.Timestamp("2026-02-28 23:59:59", tz="UTC"))
    assert (owner_t1, spender) in t1_positive_pairs(latest)
    labels = future_approval_labels(
        approvals,
        latest,
        pd.Timestamp("2026-03-01", tz="UTC"),
        pd.Timestamp("2026-05-31", tz="UTC"),
        [spender],
    )
    row = labels.iloc[0]
    assert row["future_new_approvers"] == 1
    assert row["future_revoke_count"] == 1
    assert row["future_revoke_rate"] == 1.0
    assert row["future_keep_rate"] == 0.0
    assert row["future_revoke_value"] == 10.0


def test_drain_and_aave_labels() -> None:
    from holdout import future_aave_labels, future_drain_labels

    owner = "0x" + "1" * 40
    spender = "0x" + "2" * 40
    token = "0x" + "3" * 40
    start = pd.Timestamp("2026-03-01", tz="UTC")
    end = pd.Timestamp("2026-05-31", tz="UTC")
    approvals = pd.DataFrame(
        [
            {
                "block_timestamp": "2026-04-01T00:00:00Z",
                "block_number": 1,
                "log_index": 0,
                "token_address": token,
                "owner": owner,
                "spender": spender,
                "value": 100.0,
            }
        ]
    )
    transfers = pd.DataFrame(
        [
            {
                "block_timestamp": "2026-04-01T02:00:00Z",
                "from_address": owner,
                "to_address": "0x" + "9" * 40,
                "token_address": token,
                "value": 80.0,
            }
        ]
    )
    drain = future_drain_labels(approvals, transfers, start, end, [spender])
    assert drain.iloc[0]["future_drain_owners"] == 1
    assert drain.iloc[0]["future_no_drain"] == 0

    aave = pd.DataFrame(
        [
            {
                "user": spender,
                "event_type": "borrow",
                "block_timestamp": "2026-04-01T00:00:00Z",
            },
            {
                "user": spender,
                "event_type": "liquidation_call",
                "block_timestamp": "2026-04-02T00:00:00Z",
            },
        ]
    )
    labs = future_aave_labels(aave, start, end, [spender, "0x" + "8" * 40])
    by = labs.set_index("wallet")
    assert by.loc[spender, "future_aave_liq_count"] == 1
    assert by.loc[spender, "future_aave_not_liquidated"] == 0
    assert pd.isna(by.loc["0x" + "8" * 40, "future_aave_not_liquidated"])


def test_run_holdout_fixtures_is_t1_vs_t2() -> None:
    config = load_config()
    frames = build_holdout_fixture_frames(n_wallets=24, seed=1)
    summary = run_holdout(
        config,
        frames["approvals"],
        frames["transfers"],
        frames["decoded"],
        frames["wallets"]["wallet"].tolist(),
    )
    assert summary["protocol"] == "t1_score_vs_t2_label"
    score_end, outcome_start, _ = holdout_bounds(config)
    assert pd.Timestamp(summary["score_end"]) == score_end
    assert pd.Timestamp(summary["outcome_start"]) == outcome_start
    assert "endorserank" in summary["methods"]
    assert "awp" in summary["methods"]
    er = summary["alignment"]["methods"]["endorserank"]["future_new_approvers"]
    assert er["n"] >= 5
    assert "kendall_tau" in er
    # Hybrids, baselines, the flow-side label and the paired contrasts are present.
    for method in ("coupled_pr", "coupled_pr_l25", "coupled_pr_l75", "seeded_pr", "t1_in_approve_degree", "t1_in_degree"):
        assert method in summary["methods"], method
    flow = summary["alignment"]["methods"]["awp"]["future_new_transfer_senders"]
    assert flow["n"] >= 5
    roles = {row["role"] for row in summary["tau_diff"]}
    assert {"primary_a", "primary_b", "increment", "single_layer"} <= roles
    assert set(summary["primary_criterion"]) >= {"met", "delta_a", "delta_b"}


def test_future_transfer_senders_counts_only_new_counterparties() -> None:
    from holdout import future_transfer_labels

    wallet = "0x" + "1" * 40
    old_sender = "0x" + "2" * 40
    new_sender = "0x" + "3" * 40
    token = "0x" + "4" * 40
    rows = [
        {"block_timestamp": "2026-02-01T00:00:00Z", "from_address": old_sender, "to_address": wallet, "token_address": token, "value": 1.0},
        {"block_timestamp": "2026-04-01T00:00:00Z", "from_address": old_sender, "to_address": wallet, "token_address": token, "value": 1.0},
        {"block_timestamp": "2026-04-02T00:00:00Z", "from_address": new_sender, "to_address": wallet, "token_address": token, "value": 1.0},
        {"block_timestamp": "2026-04-03T00:00:00Z", "from_address": new_sender, "to_address": wallet, "token_address": token, "value": 1.0},
        {"block_timestamp": "2026-04-04T00:00:00Z", "from_address": wallet, "to_address": wallet, "token_address": token, "value": 1.0},
    ]
    transfers = pd.DataFrame(rows)
    t1 = transfers[pd.to_datetime(transfers["block_timestamp"], utc=True) <= pd.Timestamp("2026-02-28", tz="UTC")]
    labels = future_transfer_labels(
        transfers, t1, pd.Timestamp("2026-03-01", tz="UTC"), pd.Timestamp("2026-05-31", tz="UTC"), [wallet]
    )
    assert labels.iloc[0]["future_new_transfer_senders"] == 1.0


def _two_layer_fixture() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Two layers on the same node set {a, b, c, d} with different edge patterns."""
    a, b, c, d = ("0x" + ch * 40 for ch in "abcd")
    layer_a = pd.DataFrame(
        [
            {"from_node": a, "to_node": b, "weight": 3.0},
            {"from_node": b, "to_node": c, "weight": 1.0},
            {"from_node": c, "to_node": a, "weight": 2.0},
            {"from_node": d, "to_node": a, "weight": 1.0},
        ]
    )
    layer_b = pd.DataFrame(
        [
            {"from_node": a, "to_node": d, "weight": 5.0},
            {"from_node": b, "to_node": d, "weight": 1.0},
            {"from_node": c, "to_node": b, "weight": 1.0},
            {"from_node": d, "to_node": c, "weight": 4.0},
        ]
    )
    return layer_a, layer_b


def test_coupled_pagerank_nests_single_layer_solutions() -> None:
    from pagerank import coupled_pagerank, weighted_pagerank

    layer_a, layer_b = _two_layer_fixture()
    er = weighted_pagerank(layer_a, damping=0.85, tol=1e-12, max_iter=1000)
    awp = weighted_pagerank(layer_b, damping=0.85, tol=1e-12, max_iter=1000)
    c1 = coupled_pagerank([(layer_a, 1.0), (layer_b, 0.0)], damping=0.85, tol=1e-12, max_iter=1000)
    c0 = coupled_pagerank([(layer_a, 0.0), (layer_b, 1.0)], damping=0.85, tol=1e-12, max_iter=1000)
    for node in er:
        assert abs(c1[node] - er[node]) < 1e-9
        assert abs(c0[node] - awp[node]) < 1e-9
    mid = coupled_pagerank([(layer_a, 0.5), (layer_b, 0.5)], damping=0.85, tol=1e-12, max_iter=1000)
    assert abs(sum(mid.values()) - 1.0) < 1e-9
    assert mid != er and mid != awp


def test_coupled_pagerank_single_layer_node_follows_that_layer() -> None:
    from pagerank import coupled_pagerank

    a, b, c = ("0x" + ch * 40 for ch in "abc")
    layer_a = pd.DataFrame([{"from_node": a, "to_node": b, "weight": 1.0}])
    layer_b = pd.DataFrame([{"from_node": b, "to_node": c, "weight": 1.0}, {"from_node": c, "to_node": b, "weight": 1.0}])
    scores = coupled_pagerank([(layer_a, 0.5), (layer_b, 0.5)], damping=0.85, tol=1e-12, max_iter=1000)
    assert set(scores) == {a, b, c}
    assert abs(sum(scores.values()) - 1.0) < 1e-9
    # a has an out-edge in the first layer only, so its whole step goes to b
    # (no half-step is lost to the missing layer); a receives teleport mass only.
    assert scores[b] > scores[a]
    assert scores[c] > scores[a]
    # Renormalisation: a's row is identical whatever the weight of the layer it lacks.
    alt = coupled_pagerank([(layer_a, 0.1), (layer_b, 0.9)], damping=0.85, tol=1e-12, max_iter=1000)
    assert abs(alt[a] - scores[a]) < 1e-9


def test_personalised_teleport_moves_mass_towards_seed() -> None:
    from pagerank import weighted_pagerank

    a, b, c = ("0x" + ch * 40 for ch in "abc")
    edges = pd.DataFrame(
        [
            {"from_node": a, "to_node": b, "weight": 1.0},
            {"from_node": b, "to_node": c, "weight": 1.0},
            {"from_node": c, "to_node": a, "weight": 1.0},
        ]
    )
    uniform = weighted_pagerank(edges, damping=0.85, tol=1e-12, max_iter=1000)
    seeded = weighted_pagerank(edges, damping=0.85, tol=1e-12, max_iter=1000, teleport={c: 1.0})
    assert seeded[c] > uniform[c]
    assert abs(sum(seeded.values()) - 1.0) < 1e-9
