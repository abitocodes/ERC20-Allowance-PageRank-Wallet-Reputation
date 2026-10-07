"""Registered fresh holdout (labels from June to August 2026): shared logic.

The registration is config/fresh_holdout_2026q3.yaml. This module reads it,
builds the in-memory configuration for the new window, loads the spring and
fresh events, adds the trader liquidation label, judges the registered rule
and reruns it under the registered sensitivity analyses, which never enter the
decision. Nothing here writes to the spring data or to the spring summaries.
"""

from __future__ import annotations

import copy
import hashlib
import os
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import yaml

from common import ROOT
from project_paths import current_path
from holdout import (
    HOLDOUT_CONTRASTS,
    correlate_holdout,
    evaluate_primary_criterion,
    filter_transfers_as_of,
    future_approval_labels,
    future_gmx_labels,
    future_transfer_labels,
    holdout_bounds,
    holdout_tau_diff,
    label_prevalence,
    latest_positive_as_of,
    resolve_score_wallets,
    score_awp,
    score_awp_paper,
    score_endorserank,
    scores_to_frame,
    t1_connected_wallets,
)
from pagerank import build_awp_edges, build_endorserank_edges

REGISTRATION_PATH = ROOT / "config" / "fresh_holdout_2026q3.yaml"

APPROVAL_COLUMNS = (
    "block_timestamp",
    "block_number",
    "transaction_hash",
    "log_index",
    "token_address",
    "owner",
    "spender",
    "value",
)
TRANSFER_COLUMNS = (
    "block_timestamp",
    "block_number",
    "transaction_hash",
    "log_index",
    "token_address",
    "from_address",
    "to_address",
    "value",
)
DECODED_COLUMNS = (
    "block_timestamp",
    "block_number",
    "transaction_hash",
    "log_index",
    "account",
    "base_pnl_usd",
    "is_liquidation",
    "size_delta_usd",
)

LIQUIDATION_LABELS = (
    "future_liquidation_free_rate",
    "future_zero_liquidation",
    "future_close_count",
)

# Labels reported for every score in both cohorts.
REPORT_LABELS = (
    "future_new_approvers",
    "future_new_transfer_senders",
    "future_liquidation_free_rate",
    "future_zero_liquidation",
    "close_success_count",
    "realized_gain_proxy",
    "close_success_rate",
    "non_loss_close_rate",
)

COHORTS = ("spenders", "traders")

# Scores recomputed with wallets outside a graph kept as isolated nodes; only
# the methods that leave cohort wallets out of their graph need a variant (every
# spender is in the allowance graph, every trader in the union graph of C-PR).
ISOLATED_VARIANTS = {"endorserank": "endorserank_isolated", "awp": "awp_isolated"}


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def file_sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve(value: str) -> str:
    path = Path(value)
    if path.is_absolute():
        return str(path)
    # The registration is frozen and names the data folders as they were before
    # the renaming of 1 October 2026; current_path() gives today's names.
    return str(ROOT / current_path(value))


def load_registration(path: Path | None = None) -> dict[str, Any]:
    """Read the registration file and resolve its relative paths against ROOT."""
    reg_path = Path(path) if path else REGISTRATION_PATH
    with reg_path.open(encoding="utf-8") as f:
        reg = yaml.safe_load(f)
    reg["_path"] = str(reg_path)
    reg["_sha256"] = file_sha256(reg_path)
    plan = reg.get("registration", {}).get("plan")
    if plan:
        reg["registration"]["plan"] = _resolve(plan)
        reg["_plan_sha256"] = file_sha256(Path(reg["registration"]["plan"]))
    for key, value in list(reg.get("extraction", {}).items()):
        if isinstance(value, str) and ("/" in value or "\\" in value):
            reg["extraction"][key] = _resolve(value)
    output = reg.get("evaluation", {}).get("output")
    if output:
        reg["evaluation"]["output"] = _resolve(output)
    return reg


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )


def git_file_state(path: Path) -> dict[str, Any]:
    """Tracked/clean state of one file and the last commit that touched it."""
    state: dict[str, Any] = {
        "path": str(path),
        "tracked": False,
        "clean": False,
        "last_commit": None,
        "error": None,
    }
    if not path.exists():
        state["error"] = "missing"
        return state
    try:
        top = _git(["rev-parse", "--show-toplevel"], path.parent)
    except OSError as exc:
        state["error"] = f"git unavailable: {exc}"
        return state
    if top.returncode != 0:
        state["error"] = "not inside a git repository"
        return state
    root = Path(top.stdout.strip())
    try:
        rel_path = path.resolve().relative_to(root.resolve())
    except ValueError:
        rel_path = Path(os.path.relpath(os.path.normcase(str(path.resolve())), os.path.normcase(str(root.resolve()))))
    rel = str(rel_path).replace("\\", "/")
    state["tracked"] = _git(["ls-files", "--error-unmatch", "--", rel], root).returncode == 0
    status = _git(["status", "--porcelain", "--", rel], root)
    state["clean"] = status.returncode == 0 and not status.stdout.strip()
    # Last commit that changed the content: --follow looks through the folder
    # move of 1 October 2026 and the filter skips renames that left it unchanged.
    log = _git(["log", "-1", "--follow", "--diff-filter=AM", "--format=%H %cI", "--", rel], root)
    if log.returncode == 0 and log.stdout.strip():
        state["last_commit"] = log.stdout.strip()
    return state


def registration_check(reg: dict[str, Any]) -> tuple[bool, list[str], dict[str, Any]]:
    """True only when the status is 'registered' and both files are committed."""
    problems: list[str] = []
    status = str(reg.get("registration", {}).get("status", "")).strip().lower()
    if status != "registered":
        problems.append(f"registration status is '{status or 'missing'}', not 'registered'")
    files = {"registration": Path(reg["_path"])}
    plan = reg.get("registration", {}).get("plan")
    if plan:
        files["plan"] = Path(plan)
    states = {name: git_file_state(p) for name, p in files.items()}
    for name, st in states.items():
        if st["error"]:
            problems.append(f"{name}: {st['error']}")
            continue
        if not st["tracked"]:
            problems.append(f"{name} file is not committed")
        elif not st["clean"]:
            problems.append(f"{name} file has uncommitted changes")
    return (not problems), problems, states


def window_config(config: dict[str, Any], reg: dict[str, Any]) -> dict[str, Any]:
    """Copy of the pipeline configuration with the registered window in place."""
    cfg = copy.deepcopy(config)
    ho = cfg["reputation"].setdefault("holdout", {})
    win = reg["window"]
    ho["score_end"] = win["score_end"]
    ho["outcome_start"] = win["outcome_start"]
    ho["outcome_end"] = win["outcome_end"]
    ev = reg.get("evaluation", {})
    ho["bootstrap_resamples"] = int(ev.get("bootstrap_resamples", ho.get("bootstrap_resamples", 400)))
    ho["bootstrap_seed"] = int(ev.get("bootstrap_seed", ho.get("bootstrap_seed", 42)))
    ho["min_closes"] = int(ev.get("min_closes_in_window", ho.get("min_closes", 3)))
    return cfg


# ---------------------------------------------------------------------------
# Loading events
# ---------------------------------------------------------------------------


def parquet_files(raw_dir: Path, combined_name: str | None = None) -> list[Path]:
    """Same file choice as common.load_raw_parquet_dir, without loading."""
    if combined_name and (raw_dir / combined_name).exists():
        return [raw_dir / combined_name]
    if not raw_dir.exists():
        return []
    return sorted(p for p in raw_dir.glob("*.parquet") if "synthetic" not in p.name)


def read_events(paths: list[Path], columns: tuple[str, ...]) -> pd.DataFrame:
    frames = []
    for path in paths:
        names = set(pq.ParquetFile(path).schema_arrow.names)
        cols = [c for c in columns if c in names]
        frames.append(pd.read_parquet(path, columns=cols))
    if not frames:
        return pd.DataFrame(columns=list(columns))
    return pd.concat(frames, ignore_index=True)


def combine_events(*frames: pd.DataFrame) -> pd.DataFrame:
    """Concatenate event frames and drop exact duplicates of one log."""
    parts = [f for f in frames if f is not None and not f.empty]
    if not parts:
        return frames[0] if frames else pd.DataFrame()
    out = pd.concat(parts, ignore_index=True)
    if {"transaction_hash", "log_index"} <= set(out.columns):
        out = out.drop_duplicates(subset=["transaction_hash", "log_index"], keep="first")
    return out.reset_index(drop=True)


def load_spring_events(config: dict[str, Any]) -> dict[str, pd.DataFrame]:
    paths = config["reputation"]["paths"]
    approvals = read_events(
        parquet_files(Path(paths["raw_approvals_dir"]), "approvals_arbitrum.parquet"),
        APPROVAL_COLUMNS,
    )
    transfers = read_events(
        parquet_files(Path(paths["raw_transfers_dir"]), "transfers_arbitrum.parquet"),
        TRANSFER_COLUMNS,
    )
    decoded_path = Path(config["paths"]["decoded_events"])
    decoded = (
        read_events([decoded_path], DECODED_COLUMNS)
        if decoded_path.exists()
        else pd.DataFrame(columns=list(DECODED_COLUMNS))
    )
    return {"approvals": approvals, "transfers": transfers, "decoded": decoded}


def load_fresh_events(reg: dict[str, Any]) -> dict[str, pd.DataFrame]:
    ex = reg["extraction"]
    approvals = read_events(parquet_files(Path(ex["raw_approvals_dir"])), APPROVAL_COLUMNS)
    transfers = read_events(parquet_files(Path(ex["raw_transfers_dir"])), TRANSFER_COLUMNS)
    decoded_path = Path(ex["decoded_gmx"])
    decoded = (
        read_events([decoded_path], DECODED_COLUMNS)
        if decoded_path.exists()
        else pd.DataFrame(columns=list(DECODED_COLUMNS))
    )
    return {"approvals": approvals, "transfers": transfers, "decoded": decoded}


def fresh_data_status(reg: dict[str, Any]) -> dict[str, Any]:
    """Which monthly fresh files exist, per kind."""
    ex = reg["extraction"]
    labels = [m[0] for m in reg["window"]["months"]]
    out: dict[str, Any] = {}
    for kind, key, prefix in (
        ("approvals", "raw_approvals_dir", "approvals_"),
        ("transfers", "raw_transfers_dir", "transfers_"),
        ("gmx", "raw_gmx_dir", "gmx_event_logs_"),
    ):
        folder = Path(ex[key])
        present = sorted(p.name for p in folder.glob(f"{prefix}*.parquet")) if folder.exists() else []
        missing = [lab for lab in labels if f"{prefix}{lab}.parquet" not in present]
        out[kind] = {"present": present, "missing_months": missing}
    out["decoded_gmx"] = Path(ex["decoded_gmx"]).exists()
    out["complete"] = all(not out[k]["missing_months"] for k in ("approvals", "transfers", "gmx")) and out[
        "decoded_gmx"
    ]
    return out


# ---------------------------------------------------------------------------
# Labels
# ---------------------------------------------------------------------------


def future_liquidation_labels(
    decoded: pd.DataFrame,
    outcome_start: pd.Timestamp,
    outcome_end: pd.Timestamp,
    wallets: list[str],
    min_closes: int,
) -> pd.DataFrame:
    """Trader-side risk label on GMX V2 closes inside the outcome window.

    ``future_liquidation_free_rate`` is 1 minus the share of the wallet's closes
    that were liquidations (the definition of ``liquidation_free_rate`` in
    proxy_metrics), and is defined only for wallets with at least
    ``min_closes`` closes in the window. Other wallets get NaN.
    """
    base = pd.DataFrame({"wallet": [w.lower() for w in wallets]})
    if decoded is None or decoded.empty:
        for col in LIQUIDATION_LABELS:
            base[col] = np.nan
        return base
    work = decoded.copy()
    work["block_timestamp"] = pd.to_datetime(work["block_timestamp"], utc=True)
    work = work[(work["block_timestamp"] >= outcome_start) & (work["block_timestamp"] <= outcome_end)]
    work["wallet"] = work["account"].astype(str).str.lower()
    work["is_liquidation"] = work["is_liquidation"].fillna(False).astype(bool)
    agg = work.groupby("wallet").agg(
        closes=("is_liquidation", "size"),
        liquidations=("is_liquidation", "sum"),
    )
    agg = agg[agg["closes"] >= int(min_closes)]
    out = base.merge(agg, left_on="wallet", right_index=True, how="left")
    out["future_liquidation_free_rate"] = 1.0 - out["liquidations"] / out["closes"]
    out["future_zero_liquidation"] = (out["liquidations"] == 0).astype(float).where(out["closes"].notna())
    out["future_close_count"] = out["closes"].astype(float)
    return out[["wallet", *LIQUIDATION_LABELS]]


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------


def cohort_wallets(
    cohort: str,
    latest_t1: pd.DataFrame,
    matched: list[str] | None,
) -> list[str] | None:
    if cohort == "spenders":
        if latest_t1.empty:
            return []
        return sorted(set(latest_t1["spender"].astype(str).str.lower()))
    if cohort == "traders":
        return matched
    raise ValueError(f"unknown cohort: {cohort}")


def build_cohort_frame(
    config: dict[str, Any],
    events: dict[str, pd.DataFrame],
    cohort: str,
    matched: list[str] | None,
    with_liquidation: bool = True,
) -> tuple[pd.DataFrame, list[str], dict[str, Any]]:
    """Scores frozen at score_end and every label counted in the outcome window."""
    # Imported here so that importing this module does not pull in the CLI.
    from run_holdout_eval import _score_methods

    score_end, outcome_start, outcome_end = holdout_bounds(config)
    rep = config["reputation"]
    min_closes = int(rep["holdout"].get("min_closes", 3))
    approvals = events["approvals"]
    transfers = events["transfers"]
    decoded = events.get("decoded")

    latest_t1 = latest_positive_as_of(approvals, score_end)
    transfers_t1 = filter_transfers_as_of(transfers, score_end)
    er_edges = build_endorserank_edges(latest_t1)
    awp_edges = build_awp_edges(
        transfers_t1,
        score_end,
        float(rep["awp_decay_k"]),
        float(rep["awp_decay_t0_days"]),
    )
    t1_nodes = t1_connected_wallets(er_edges, awp_edges)
    wallets = resolve_score_wallets(cohort_wallets(cohort, latest_t1, matched), t1_nodes)
    if not wallets:
        raise RuntimeError(f"No wallets in the {cohort} cohort at {score_end}.")

    scores = _score_methods(latest_t1, transfers_t1, score_end, wallets, config)
    scores["awp_paper"] = score_awp_paper(transfers_t1, score_end, wallets, config)
    variants = {
        ISOLATED_VARIANTS["endorserank"]: score_endorserank(latest_t1, wallets, config, isolated=True),
        ISOLATED_VARIANTS["awp"]: score_awp(transfers_t1, score_end, wallets, config, isolated=True),
    }
    frame = scores_to_frame(wallets, {**scores, **variants})
    approvals_lab = future_approval_labels(approvals, latest_t1, outcome_start, outcome_end, wallets)
    flow_lab = future_transfer_labels(transfers, transfers_t1, outcome_start, outcome_end, wallets)
    merged = frame.merge(approvals_lab, on="wallet", how="left").merge(flow_lab, on="wallet", how="left")
    if decoded is not None and not decoded.empty:
        gmx_lab = future_gmx_labels(decoded, outcome_start, outcome_end, wallets, min_closes)
        merged = merged.merge(gmx_lab, on="wallet", how="left")
    if with_liquidation:
        liq = future_liquidation_labels(decoded, outcome_start, outcome_end, wallets, min_closes)
        merged = merged.merge(liq, on="wallet", how="left")
    meta = {
        "cohort": cohort,
        "score_end": str(score_end),
        "outcome_start": str(outcome_start),
        "outcome_end": str(outcome_end),
        "n_wallets": len(wallets),
        "n_t1_allowance_rows": int(len(latest_t1)),
        "n_t1_transfers": int(len(transfers_t1)),
        "n_er_edges": int(len(er_edges)),
        "n_awp_edges": int(len(awp_edges)),
    }
    return merged, list(scores.keys()), meta


def contrast_specs(reg: dict[str, Any]) -> list[dict[str, Any]]:
    """Registered hypotheses first, then the secondary contrasts, in file order."""
    ev = reg["evaluation"]
    specs: list[dict[str, Any]] = []
    for h in ev.get("hypotheses", []):
        specs.append(
            {
                "id": h["id"],
                "kind": "hypothesis",
                "cohort": h["cohort"],
                "a": h.get("a", ev["method"]),
                "b": h.get("b", ev["comparator"]),
                "label": h["label"],
                "test": h["test"],
            }
        )
    for s in ev.get("secondary", []):
        if "label" not in s:
            continue
        specs.append(
            {
                "id": s["id"],
                "kind": "secondary",
                "cohort": s["cohort"],
                "a": s["a"],
                "b": s["b"],
                "label": s["label"],
                "test": s["test"],
            }
        )
    return specs


def judge(row: dict[str, Any] | None, test: str, margin: float) -> dict[str, Any]:
    """Superiority: interval above zero. Non-inferiority: lower bound above -margin."""
    if not row or row.get("ci_low") is None or row.get("ci_high") is None:
        return {"passed": False, "reason": "no interval (label too sparse or constant)"}
    lo = float(row["ci_low"])
    if test == "superiority":
        passed = lo > 0.0
        reason = f"lower bound {lo:+.4f} {'>' if passed else '<='} 0"
    elif test == "non_inferiority":
        passed = lo > -float(margin)
        reason = f"lower bound {lo:+.4f} {'>' if passed else '<='} -{float(margin):.3f}"
    else:
        raise ValueError(f"unknown test: {test}")
    return {"passed": bool(passed), "reason": reason}


def evaluate_contrasts(
    merged_by_cohort: dict[str, pd.DataFrame],
    reg: dict[str, Any],
    n_resamples: int,
    seed: int,
    specs: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    margin = float(reg["evaluation"].get("non_inferiority_margin", 0.02))
    out: list[dict[str, Any]] = []
    for spec in contrast_specs(reg) if specs is None else specs:
        merged = merged_by_cohort.get(spec["cohort"])
        row: dict[str, Any] | None = None
        if merged is not None:
            rows = holdout_tau_diff(
                merged,
                ((f"{spec['id']}: {spec['a']} minus {spec['b']}", spec["a"], spec["b"], spec["label"], spec["id"]),),
                n_resamples=n_resamples,
                seed=seed,
            )
            row = rows[0] if rows else None
        verdict = judge(row, spec["test"], margin)
        out.append({**spec, "margin": margin if spec["test"] == "non_inferiority" else None, "result": row, **verdict})
    return out


def decide(contrasts: list[dict[str, Any]], reg: dict[str, Any]) -> dict[str, Any]:
    hyps = [c for c in contrasts if c["kind"] == "hypothesis"]
    rule = str(reg["evaluation"].get("decision", "all"))
    if rule != "all":
        raise ValueError(f"unsupported decision rule: {rule}")
    met = bool(hyps) and all(c["passed"] for c in hyps)
    return {
        "rule": "every registered hypothesis holds",
        "met": met,
        "hypotheses": {c["id"]: c["passed"] for c in hyps},
    }


def comparator_swap_specs(reg: dict[str, Any], comparator: str) -> list[dict[str, Any]]:
    """The registered contrasts that involve the comparator, with ``comparator`` in its place."""
    base = reg["evaluation"]["comparator"]
    out: list[dict[str, Any]] = []
    for spec in contrast_specs(reg):
        if base not in (spec["a"], spec["b"]):
            continue
        out.append(
            {
                **spec,
                "a": comparator if spec["a"] == base else spec["a"],
                "b": comparator if spec["b"] == base else spec["b"],
            }
        )
    return out


def isolated_frame(merged: pd.DataFrame) -> pd.DataFrame:
    """The cohort frame with each method in ISOLATED_VARIANTS scored by its isolated-node variant."""
    work = merged.copy()
    for method, variant in ISOLATED_VARIANTS.items():
        col = f"{variant}_score"
        if col in work.columns:
            work[f"{method}_score"] = work[col]
    return work


def evaluate_sensitivity(
    merged_by_cohort: dict[str, pd.DataFrame],
    reg: dict[str, Any],
    n_resamples: int,
    seed: int,
) -> dict[str, Any]:
    """The registered sensitivity analyses; reported beside the decision, never part of it."""
    sens = reg["evaluation"].get("sensitivity") or {}
    out: dict[str, Any] = {}
    comparator = sens.get("comparator")
    if comparator:
        contrasts = evaluate_contrasts(
            merged_by_cohort, reg, n_resamples, seed, specs=comparator_swap_specs(reg, comparator)
        )
        out["comparator"] = {
            "replaces": reg["evaluation"]["comparator"],
            "with": comparator,
            "contrasts": contrasts,
            "decision_rule_on_these": decide(contrasts, reg),
        }
    rule = sens.get("missing_wallet_rule")
    if rule:
        if rule != "isolated_nodes":
            raise ValueError(f"unsupported missing_wallet_rule: {rule}")
        frames = {cohort: isolated_frame(m) for cohort, m in merged_by_cohort.items()}
        contrasts = evaluate_contrasts(frames, reg, n_resamples, seed)
        block: dict[str, Any] = {
            "rule": rule,
            "rescored": sorted(ISOLATED_VARIANTS),
            "contrasts": contrasts,
            "decision_rule_on_these": decide(contrasts, reg),
        }
        if "spenders" in frames:
            primary = tuple(c for c in HOLDOUT_CONTRASTS if c[4] in ("primary_a", "primary_b"))
            sept = holdout_tau_diff(frames["spenders"], primary, n_resamples=n_resamples, seed=seed)
            block["september_contrasts"] = sept
            block["september_primary_rule"] = evaluate_primary_criterion(sept)
        out["missing_wallet_rule"] = block
    return out


def evaluate(
    config: dict[str, Any],
    reg: dict[str, Any],
    events: dict[str, pd.DataFrame],
    matched: list[str] | None,
    cohorts: tuple[str, ...] = COHORTS,
) -> dict[str, Any]:
    """Run both cohorts on the configured window and judge the registered rule."""
    ho = config["reputation"]["holdout"]
    n_boot = int(ho.get("bootstrap_resamples", 400))
    seed = int(ho.get("bootstrap_seed", 42))
    merged_by_cohort: dict[str, pd.DataFrame] = {}
    report: dict[str, Any] = {"cohorts": {}}
    for cohort in cohorts:
        merged, methods, meta = build_cohort_frame(config, events, cohort, matched)
        merged_by_cohort[cohort] = merged
        labels = tuple(lab for lab in REPORT_LABELS if lab in merged.columns)
        block: dict[str, Any] = {
            **meta,
            "methods": methods,
            "prevalence": label_prevalence(merged, labels + ("future_close_count",)),
            "alignment": correlate_holdout(merged, methods, labels=labels, n_resamples=n_boot, seed=seed),
        }
        if cohort == "spenders":
            sept = holdout_tau_diff(merged, HOLDOUT_CONTRASTS, n_resamples=n_boot, seed=seed)
            block["september_contrasts"] = sept
            block["september_primary_rule"] = evaluate_primary_criterion(sept)
        report["cohorts"][cohort] = block
    contrasts = evaluate_contrasts(merged_by_cohort, reg, n_boot, seed)
    report["contrasts"] = contrasts
    report["decision"] = decide(contrasts, reg)
    report["sensitivity"] = evaluate_sensitivity(merged_by_cohort, reg, n_boot, seed)
    report["bootstrap"] = {"n_boot": n_boot, "seed": seed, "ci_level": 0.95}
    return report


def shift_fixture_frames(frames: dict[str, pd.DataFrame], days: int) -> dict[str, pd.DataFrame]:
    """Move the synthetic holdout events so that they straddle another freeze date."""
    out: dict[str, pd.DataFrame] = {}
    for name, frame in frames.items():
        work = frame.copy()
        if "block_timestamp" in work.columns:
            work["block_timestamp"] = pd.to_datetime(work["block_timestamp"], utc=True) + pd.Timedelta(days=days)
        out[name] = work
    return out
