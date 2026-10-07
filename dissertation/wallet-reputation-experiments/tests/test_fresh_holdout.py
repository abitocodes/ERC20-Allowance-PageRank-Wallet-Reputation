"""Fresh holdout (June-August 2026): registration, labels and rule (no BigQuery)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from common import load_config  # noqa: E402
from extract_fresh_window import merge_parts, month_done, plan_steps, split_month, stray_parts  # noqa: E402
from fresh_holdout import (  # noqa: E402
    combine_events,
    comparator_swap_specs,
    contrast_specs,
    decide,
    evaluate,
    future_liquidation_labels,
    isolated_frame,
    judge,
    load_registration,
    registration_check,
    shift_fixture_frames,
    window_config,
)
from holdout import build_holdout_fixture_frames, holdout_bounds, score_awp  # noqa: E402
from project_paths import RAW_REPLICATION_DIR, REPLICATION_DIR  # noqa: E402
from proxy_metrics import compute_liquidation_proxies  # noqa: E402


def test_registration_matches_the_registered_design() -> None:
    reg = load_registration()
    assert reg["registration"]["id"] == "fresh-holdout-2026q3"
    assert [m[0] for m in reg["window"]["months"]] == ["2026-06", "2026-07", "2026-08"]
    ev = reg["evaluation"]
    assert ev["method"] == "coupled_pr" and ev["comparator"] == "awp"
    assert ev["bootstrap_resamples"] == 400 and ev["bootstrap_seed"] == 42
    assert abs(float(ev["non_inferiority_margin"]) - 0.02) < 1e-12
    hyps = {h["id"]: (h["cohort"], h["label"], h["test"]) for h in ev["hypotheses"]}
    assert hyps == {
        "F1": ("spenders", "future_new_approvers", "superiority"),
        "F2": ("spenders", "future_new_transfer_senders", "non_inferiority"),
        "F3": ("traders", "future_liquidation_free_rate", "non_inferiority"),
    }
    # The frozen file names the folders as they were before 1 October 2026; they
    # resolve to the replication folders of today.
    for key in ("raw_approvals_dir", "raw_transfers_dir", "raw_gmx_dir"):
        path = Path(reg["extraction"][key])
        assert path.is_absolute() and path.is_relative_to(RAW_REPLICATION_DIR)
    for key in ("decoded_gmx", "manifest"):
        assert Path(reg["extraction"][key]).is_relative_to(REPLICATION_DIR)
    assert Path(reg["evaluation"]["output"]).is_relative_to(REPLICATION_DIR)
    assert ev["sensitivity"] == {"comparator": "awp_paper", "missing_wallet_rule": "isolated_nodes"}


def test_comparator_swap_reruns_f1_to_f4_against_the_published_form() -> None:
    reg = load_registration()
    specs = comparator_swap_specs(reg, "awp_paper")
    assert [s["id"] for s in specs] == ["F1", "F2", "F3", "F4"]
    assert all(s["a"] == "coupled_pr" and s["b"] == "awp_paper" for s in specs)
    original = {s["id"]: s for s in contrast_specs(reg)}
    for s in specs:
        assert (s["cohort"], s["label"], s["test"]) == tuple(original[s["id"]][k] for k in ("cohort", "label", "test"))


def test_isolated_rule_rescores_only_endorserank_and_awp() -> None:
    frame = pd.DataFrame(
        {
            "wallet": ["0x1", "0x2"],
            "endorserank_score": [0.5, 0.0],
            "endorserank_isolated_score": [0.4, 0.1],
            "awp_score": [0.0, 0.3],
            "awp_isolated_score": [0.2, 0.25],
            "coupled_pr_score": [0.6, 0.4],
        }
    )
    out = isolated_frame(frame)
    assert out["endorserank_score"].tolist() == [0.4, 0.1]
    assert out["awp_score"].tolist() == [0.2, 0.25]
    assert out["coupled_pr_score"].tolist() == [0.6, 0.4]
    assert frame["awp_score"].tolist() == [0.0, 0.3]


def test_isolated_awp_scores_a_wallet_without_transfers_like_a_sender() -> None:
    config = load_config()
    t = pd.Timestamp("2026-05-01", tz="UTC")
    transfers = pd.DataFrame(
        {
            "block_timestamp": [t, t],
            "from_address": ["0xa", "0xb"],
            "to_address": ["0xb", "0xc"],
            "value": [5.0, 2.0],
        }
    )
    end = pd.Timestamp("2026-05-31 23:59:59", tz="UTC")
    wallets = ["0xa", "0xb", "0xc", "0xd"]
    zero_rule = score_awp(transfers, end, wallets, config)
    isolated = score_awp(transfers, end, wallets, config, isolated=True)
    assert "0xd" not in zero_rule
    assert abs(isolated["0xd"] - isolated["0xa"]) < 1e-12 and isolated["0xd"] > 0


def test_window_config_changes_only_the_window() -> None:
    config = load_config()
    reg = load_registration()
    cfg = window_config(config, reg)
    score_end, start, end = holdout_bounds(cfg)
    assert str(score_end).startswith("2026-05-31 23:59:59")
    assert str(start).startswith("2026-06-01 00:00:00")
    assert str(end).startswith("2026-08-31 23:59:59")
    for key in ("damping", "pagerank_tolerance", "max_iterations", "awp_decay_k", "awp_decay_t0_days", "hybrid"):
        assert cfg["reputation"][key] == config["reputation"][key]
    # The spring window in the pipeline configuration is left as it was.
    assert str(holdout_bounds(config)[0]).startswith("2026-02-28 23:59:59")


def test_liquidation_label_matches_the_proxy_definition() -> None:
    t = pd.Timestamp("2026-06-10", tz="UTC")
    rows = []
    for c in range(5):  # wallet a: 5 closes, 2 liquidations
        rows.append({"account": "0xA", "block_timestamp": t, "base_pnl_usd": 1.0, "is_liquidation": c < 2})
    for c in range(2):  # wallet b: only 2 closes, below the threshold
        rows.append({"account": "0xb", "block_timestamp": t, "base_pnl_usd": 1.0, "is_liquidation": False})
    for c in range(4):  # wallet c: 4 closes in May, outside the window
        rows.append(
            {"account": "0xc", "block_timestamp": pd.Timestamp("2026-05-20", tz="UTC"), "base_pnl_usd": 1.0, "is_liquidation": True}
        )
    decoded = pd.DataFrame(rows)
    start = pd.Timestamp("2026-06-01", tz="UTC")
    end = pd.Timestamp("2026-08-31 23:59:59", tz="UTC")
    wallets = ["0xa", "0xb", "0xc", "0xd"]
    lab = future_liquidation_labels(decoded, start, end, wallets, min_closes=3).set_index("wallet")
    assert abs(lab.loc["0xa", "future_liquidation_free_rate"] - 0.6) < 1e-12
    assert lab.loc["0xa", "future_zero_liquidation"] == 0.0
    assert lab.loc["0xa", "future_close_count"] == 5.0
    for w in ("0xb", "0xc", "0xd"):
        assert np.isnan(lab.loc[w, "future_liquidation_free_rate"])
        assert np.isnan(lab.loc[w, "future_zero_liquidation"])
    in_window = decoded[pd.to_datetime(decoded["block_timestamp"], utc=True) >= start]
    ref = compute_liquidation_proxies(in_window, wallets, min_closes=3).set_index("wallet")
    assert abs(ref.loc["0xa", "liquidation_free_rate"] - lab.loc["0xa", "future_liquidation_free_rate"]) < 1e-12


def test_judge_superiority_and_non_inferiority() -> None:
    assert judge({"ci_low": 0.001, "ci_high": 0.2}, "superiority", 0.02)["passed"] is True
    assert judge({"ci_low": -0.001, "ci_high": 0.2}, "superiority", 0.02)["passed"] is False
    assert judge({"ci_low": -0.019, "ci_high": 0.01}, "non_inferiority", 0.02)["passed"] is True
    assert judge({"ci_low": -0.02, "ci_high": 0.01}, "non_inferiority", 0.02)["passed"] is False
    assert judge(None, "superiority", 0.02)["passed"] is False
    assert judge({"ci_low": None, "ci_high": None}, "non_inferiority", 0.02)["passed"] is False


def test_decision_needs_every_hypothesis() -> None:
    reg = load_registration()
    specs = contrast_specs(reg)
    assert [s["id"] for s in specs] == ["F1", "F2", "F3", "F4", "F5"]
    rows = [{**s, "passed": s["id"] != "F2"} for s in specs]
    assert decide(rows, reg)["met"] is False
    rows = [{**s, "passed": s["kind"] == "hypothesis"} for s in specs]
    assert decide(rows, reg)["met"] is True


def test_fixture_run_scores_before_the_freeze_and_labels_after_it() -> None:
    config = load_config()
    reg = load_registration()
    cfg = window_config(config, reg)
    cfg["reputation"]["holdout"]["bootstrap_resamples"] = 40
    frames = shift_fixture_frames(build_holdout_fixture_frames(n_wallets=48), 91)
    score_end, start, end = holdout_bounds(cfg)
    assert frames["approvals"]["block_timestamp"].min() < score_end < frames["approvals"]["block_timestamp"].max()
    events = {k: frames[k] for k in ("approvals", "transfers", "decoded")}
    summary = evaluate(cfg, reg, events, frames["wallets"]["wallet"].tolist())
    assert set(summary["cohorts"]) == {"spenders", "traders"}
    assert [c["id"] for c in summary["contrasts"]] == ["F1", "F2", "F3", "F4", "F5"]
    assert isinstance(summary["decision"]["met"], bool)
    spenders = summary["cohorts"]["spenders"]
    assert "september_primary_rule" in spenders
    assert "awp_paper" in spenders["methods"]
    prev = summary["cohorts"]["traders"]["prevalence"]
    assert prev["future_liquidation_free_rate"]["n_defined"] > 0
    sens = summary["sensitivity"]
    assert [c["id"] for c in sens["comparator"]["contrasts"]] == ["F1", "F2", "F3", "F4"]
    assert all(c["b"] == "awp_paper" for c in sens["comparator"]["contrasts"])
    iso = sens["missing_wallet_rule"]
    assert [c["id"] for c in iso["contrasts"]] == ["F1", "F2", "F3", "F4", "F5"]
    assert isinstance(iso["september_primary_rule"]["met"], bool)
    # The sensitivity analyses never change the decision.
    assert summary["decision"]["hypotheses"] == {c["id"]: c["passed"] for c in summary["contrasts"][:3]}


def test_combine_events_drops_duplicate_logs() -> None:
    a = pd.DataFrame({"transaction_hash": ["0x1", "0x2"], "log_index": [0, 0], "value": [1, 2]})
    b = pd.DataFrame({"transaction_hash": ["0x2", "0x3"], "log_index": [0, 0], "value": [2, 3]})
    out = combine_events(a, b)
    assert list(out["transaction_hash"]) == ["0x1", "0x2", "0x3"]


def test_extraction_plan_writes_only_to_fresh_folders(tmp_path: Path) -> None:
    reg = load_registration()
    steps = plan_steps(reg)
    assert len(steps) == 9
    spring = load_config()["reputation"]["paths"]
    for step in steps:
        out = Path(step["out_path"]).as_posix()
        assert Path(step["out_path"]).is_relative_to(RAW_REPLICATION_DIR)
        assert not out.startswith(Path(spring["raw_approvals_dir"]).as_posix() + "/")
        assert not out.startswith(Path(spring["raw_transfers_dir"]).as_posix() + "/")
    halves = split_month("2026-06", "2026-06-01 00:00:00 UTC", "2026-07-01 00:00:00 UTC", 2)
    assert halves == [
        ("2026-06a", "2026-06-01 00:00:00 UTC", "2026-06-16 00:00:00 UTC"),
        ("2026-06b", "2026-06-16 00:00:00 UTC", "2026-07-01 00:00:00 UTC"),
    ]


def test_split_parts_merge_into_one_month(tmp_path: Path) -> None:
    reg = load_registration()
    for key in ("raw_approvals_dir", "raw_transfers_dir", "raw_gmx_dir"):
        reg["extraction"][key] = str(tmp_path / key)
    steps = plan_steps(reg, ("approvals",), split=2)
    june = [s for s in steps if s["month"] == "2026-06"]
    for i, step in enumerate(june):
        Path(step["out_path"]).parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame({"x": [i]}).to_parquet(step["out_path"], index=False)
    assert merge_parts(steps) == ["approvals_2026-06.parquet"]
    merged = pd.read_parquet(tmp_path / "raw_approvals_dir" / "approvals_2026-06.parquet")
    assert list(merged["x"]) == [0, 1]
    assert all(month_done(s) for s in june)
    # An unsplit run must not silently ignore half-finished parts.
    july_a = [s for s in steps if s["label"] == "2026-07a"][0]
    pd.DataFrame({"x": [9]}).to_parquet(july_a["out_path"], index=False)
    assert stray_parts(plan_steps(reg, ("approvals",), split=1)) == ["approvals_2026-07a.parquet"]


def test_draft_registration_blocks_extraction() -> None:
    reg = load_registration()
    reg["registration"]["status"] = "draft"
    ok, problems, _ = registration_check(reg)
    assert ok is False
    assert any("not 'registered'" in p for p in problems)
