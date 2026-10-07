"""Proxy orientation, isolated nodes, token selection, spender classes and the published AWP form (no BigQuery)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_spender_code import code_kind  # noqa: E402
from classify_spenders import classify  # noqa: E402
from pagerank import (  # noqa: E402
    build_awp_paper_edges,
    build_endorserank_vt_edges,
    logistic_time_decay,
    value_transform,
    weighted_pagerank,
)
from proxy_metrics import compute_inverse_risk_proxies  # noqa: E402
from run_robustness_eval import _top_token_addresses  # noqa: E402

SMALL = "0x" + "a" * 40
LARGE = "0x" + "b" * 40


def _closes(account: str, pnls: list[float]) -> list[dict]:
    return [{"account": account, "base_pnl_usd": str(p), "is_liquidation": False} for p in pnls]


def test_inverse_risk_ranks_smaller_losses_higher() -> None:
    decoded = pd.DataFrame(_closes(SMALL, [10, -5, 3]) + _closes(LARGE, [10, -50, 3]))
    out = compute_inverse_risk_proxies(decoded, [SMALL, LARGE]).set_index("wallet")
    assert out.loc[SMALL, "loss_avoidance"] > out.loc[LARGE, "loss_avoidance"]
    assert out.loc[SMALL, "worst_close_pnl_score"] > out.loc[LARGE, "worst_close_pnl_score"]
    assert out.loc[SMALL, "non_loss_close_rate"] == out.loc[LARGE, "non_loss_close_rate"]


def test_isolated_nodes_score_like_nodes_without_in_edges() -> None:
    edges = pd.DataFrame(
        {"from_node": ["a", "a", "b"], "to_node": ["b", "c", "c"], "weight": [1.0, 3.0, 2.0]}
    )
    plain = weighted_pagerank(edges, max_iter=300)
    with_isolated = weighted_pagerank(edges, max_iter=300, extra_nodes={"x", "y"})
    assert with_isolated["x"] == with_isolated["y"] == with_isolated["a"]
    ratios = [with_isolated[n] / plain[n] for n in ("a", "b", "c")]
    assert max(ratios) - min(ratios) < 1e-6


def test_top_tokens_by_value_and_by_count() -> None:
    transfers = pd.DataFrame({"token_address": ["A", "A", "B"], "value": [1.0, 1.0, 1e30]})
    allowances = pd.DataFrame({"token_address": ["C"], "value": [5.0]})
    assert _top_token_addresses(transfers, allowances, 1, rank_by="value") == ["b"]
    assert _top_token_addresses(transfers, allowances, 1, rank_by="count") == ["a"]


def test_spender_classes_from_activity() -> None:
    activity = pd.DataFrame(
        {
            "address": ["0x1", "0x2", "0x2", "0x4"],
            "activity": ["emitted_log", "sent_transaction", "emitted_log", "sent_transaction"],
        }
    )
    out = classify(activity, ["0x1", "0x2", "0x3", "0x4"]).set_index("wallet")["account_type"]
    assert out.to_dict() == {"0x1": "contract", "0x2": "both", "0x3": "inactive", "0x4": "eoa"}


def test_code_kind_separates_contracts_eoas_and_delegations() -> None:
    assert code_kind("0x") == "none"
    assert code_kind(None) == "none"
    assert code_kind("0x6080604052") == "contract"
    assert code_kind("0xef0100" + "ab" * 20) == "eip7702"
    assert code_kind("0xEF0100" + "AB" * 20) == "eip7702"


def test_value_transform_is_bounded_and_increasing() -> None:
    v = value_transform(pd.Series([0.0, 0.5, 1.0, 10.0, 1e30]), b=1.0).to_numpy()
    assert v[0] == 0.0
    assert np.all(np.diff(v) >= 0) and np.all(v < 1.0 + 1e-15)
    assert abs(v[1] - (2.0 / (1.0 + np.exp(-0.5)) - 1.0)) < 1e-15
    assert v[3] > 0.9999


def test_published_awp_edges_and_activeness() -> None:
    end = pd.Timestamp("2026-05-31", tz="UTC")
    day = pd.Timedelta(days=1)
    transfers = pd.DataFrame(
        {
            "block_timestamp": [end - 10 * day, end - 100 * day, end - 50 * day, end - 5 * day, end - 1 * day],
            "from_address": ["a", "a", "a", "c", "c"],
            "to_address": ["b", "b", "d", "b", "c"],
            "value": [1e18, 3e18, 0.0, 2e6, 7.0],
        }
    )
    edges, activeness = build_awp_paper_edges(transfers, end, k=0.01, t0_days=180, b=1.0)
    decay = logistic_time_decay(pd.Series([10.0, 100.0, 50.0, 5.0, 1.0]), 0.01, 180).to_numpy()
    w = edges.set_index(["from_node", "to_node"])["weight"]
    # Each a -> b transfer counts once whatever its amount, discounted by its age.
    assert abs(w[("a", "b")] - (decay[0] + decay[1])) < 1e-12
    # The zero-value transfer adds no edge but counts as activity.
    assert ("a", "d") not in w.index
    assert abs(activeness["a"] - (decay[0] + decay[2])) < 1e-12
    # A self-transfer keeps its edge, as in AWP, but Eq. 2 leaves it out of activeness.
    assert abs(w[("c", "c")] - decay[4] * (2.0 / (1.0 + np.exp(-7.0)) - 1.0)) < 1e-12
    assert abs(activeness["c"] - decay[3]) < 1e-12
    assert "b" not in activeness


def test_published_awp_restarts_follow_activeness() -> None:
    edges = pd.DataFrame({"from_node": ["a", "c"], "to_node": ["b", "b"], "weight": [1.0, 1.0]})
    scores = weighted_pagerank(edges, max_iter=300, teleport={"a": 0.9, "c": 0.3})
    assert abs(scores["a"] / scores["c"] - 3.0) < 1e-9
    assert scores["b"] > scores["a"]


def test_endorserank_takes_awp_weights_on_allowances() -> None:
    end = pd.Timestamp("2026-05-31", tz="UTC")
    day = pd.Timedelta(days=1)
    allowances = pd.DataFrame(
        {
            "block_timestamp": [end - 20 * day, end - 60 * day, end - 30 * day, end - 2 * day],
            "owner": ["o", "o", "o", "p"],
            "spender": ["s", "s", "t", "s"],
            "token_address": ["x", "y", "x", "x"],
            "value": [2.0**256 - 1, 50.0, 1e6, 3e18],
        }
    )
    edges, activeness = build_endorserank_vt_edges(allowances, end, k=0.01, t0_days=180, b=1.0)
    decay = logistic_time_decay(pd.Series([20.0, 60.0, 30.0, 2.0]), 0.01, 180).to_numpy()
    w = edges.set_index(["from_node", "to_node"])["weight"]
    # One term per token; an unlimited approval counts like a small one.
    assert abs(w[("o", "s")] - (decay[0] + decay[1])) < 1e-12
    assert abs(w[("o", "t")] - decay[2]) < 1e-12
    # AWP's restart weight of an owner: the latest approval to each spender, by its age.
    assert abs(activeness["o"] - (max(decay[0], decay[1]) + decay[2])) < 1e-12
    assert abs(activeness["p"] - decay[3]) < 1e-12

