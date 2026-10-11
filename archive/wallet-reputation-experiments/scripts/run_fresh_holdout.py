#!/usr/bin/env python3
"""Evaluate the registered fresh holdout (scores frozen on 31 May 2026, labels June-August 2026).

Three modes:

  --spring-check  Reruns the published spring spender holdout (freeze 28 February,
                  labels March-May) through this code path and compares every
                  coefficient with the published spring summary
                  (data/3-published-results-for-thesis/spring-holdout-2026-03-to-2026-05/
                  eval_summary_spenders.json).
                  Run it first: if it does not reproduce the thesis numbers, stop.
  --fixtures      Synthetic events moved to straddle the new freeze date (offline test).
  (default)       The registered evaluation on the June-August extraction. Refuses to
                  run unless the registration is committed with status 'registered'.

Outputs go to data/2-processed-tables-and-evaluations/registered-replication-2026-06-to-2026-08/.
The spring summaries are never written.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import load_config, save_json  # noqa: E402
from fresh_holdout import (  # noqa: E402
    REGISTRATION_PATH,
    build_cohort_frame,
    combine_events,
    evaluate,
    fresh_data_status,
    load_fresh_events,
    load_registration,
    load_spring_events,
    registration_check,
    shift_fixture_frames,
    window_config,
)
from holdout import (  # noqa: E402
    HOLDOUT_CONTRASTS,
    build_holdout_fixture_frames,
    correlate_holdout,
    evaluate_primary_criterion,
    holdout_tau_diff,
)
from project_paths import PUBLISHED_SPRING_HOLDOUT_DIR, REPLICATION_DIR  # noqa: E402

SPRING_PUBLISHED = PUBLISHED_SPRING_HOLDOUT_DIR / "eval_summary_spenders.json"
SPRING_LABELS = ("future_new_approvers", "future_new_transfer_senders")
FIXTURE_SHIFT_DAYS = 91  # moves the fixture freeze from early February to early May


def _matched_wallets(config: dict) -> list[str] | None:
    path = Path(config["paths"]["wallet_rankings"])
    if not path.exists():
        return None
    return pd.read_parquet(path)["wallet"].astype(str).str.lower().tolist()


def _fmt(x: object) -> str:
    return "  n/a" if x is None else f"{float(x):+.3f}"


def print_report(summary: dict) -> None:
    for cohort, block in summary.get("cohorts", {}).items():
        print(f"== {cohort}: n={block['n_wallets']} (freeze {block['score_end']})")
        for lab, prev in block.get("prevalence", {}).items():
            print(f"   {lab:32s} defined={prev['n_defined']:5d} nonzero={prev['n_nonzero']:5d}")
        methods = block["alignment"]["methods"]
        labels = [lab for lab in block.get("prevalence", {}) if lab != "future_close_count"]
        for method, stats in methods.items():
            cells = []
            for lab in labels:
                st = stats.get(lab, {})
                cells.append(f"{lab[:14]}={_fmt(st.get('kendall_tau'))}")
            print(f"   {method:22s} " + "  ".join(cells))
        if "september_primary_rule" in block:
            print(f"   14 September rule on this window: met={block['september_primary_rule']['met']}")
    if summary.get("contrasts"):
        print("== registered contrasts")
        for c in summary["contrasts"]:
            r = c.get("result") or {}
            print(
                f"   {c['id']:3s} {c['kind']:10s} {c['cohort']:8s} {c['a']} - {c['b']} on {c['label']}: "
                f"delta={_fmt(r.get('delta_tau'))} ci=[{_fmt(r.get('ci_low'))}, {_fmt(r.get('ci_high'))}] "
                f"{c['test']} -> {'PASS' if c['passed'] else 'FAIL'} ({c['reason']})"
            )
    if summary.get("decision"):
        print(f"== decision: {summary['decision']}")
    sens = summary.get("sensitivity") or {}
    for key, block in sens.items():
        print(f"== sensitivity ({key}), reported only")
        for c in block.get("contrasts", []):
            r = c.get("result") or {}
            print(
                f"   {c['id']:3s} {c['cohort']:8s} {c['a']} - {c['b']} on {c['label']}: "
                f"delta={_fmt(r.get('delta_tau'))} ci=[{_fmt(r.get('ci_low'))}, {_fmt(r.get('ci_high'))}] "
                f"{c['test']} -> {'PASS' if c['passed'] else 'FAIL'}"
            )
        if "september_primary_rule" in block:
            print(f"   14 September rule under this rule: met={block['september_primary_rule']['met']}")


def run_spring_check(config: dict, n_boot: int | None) -> int:
    """Spender cohort on the spring window; compare with the published summary."""
    if n_boot is not None:
        config["reputation"]["holdout"]["bootstrap_resamples"] = n_boot
    events = load_spring_events(config)
    merged, methods, meta = build_cohort_frame(config, events, "spenders", None, with_liquidation=False)
    ho = config["reputation"]["holdout"]
    boot = int(ho.get("bootstrap_resamples", 400))
    seed = int(ho.get("bootstrap_seed", 42))
    alignment = correlate_holdout(merged, methods, labels=SPRING_LABELS, n_resamples=boot, seed=seed)
    sept = holdout_tau_diff(merged, HOLDOUT_CONTRASTS, n_resamples=boot, seed=seed)
    exploratory = holdout_tau_diff(
        merged,
        (("C-PR minus AWP (exploratory)", "coupled_pr", "awp", "future_new_approvers", "exploratory"),),
        n_resamples=boot,
        seed=seed,
    )
    out = {
        "mode": "spring_check",
        **meta,
        "alignment": alignment,
        "september_contrasts": sept,
        "september_primary_rule": evaluate_primary_criterion(sept),
        "exploratory_cpr_minus_awp_on_new_approvers": exploratory,
        "at": datetime.now(timezone.utc).isoformat(),
    }
    mismatches = 0
    if SPRING_PUBLISHED.exists():
        published = json.loads(SPRING_PUBLISHED.read_text(encoding="utf-8"))
        print(f"n: this run {meta['n_wallets']}, published {published.get('n_wallets')}")
        if meta["n_wallets"] != published.get("n_wallets"):
            mismatches += 1
        pub_methods = published.get("alignment", {}).get("methods", {})
        for method in methods:
            if method not in pub_methods:
                # Added after the spring summary was published (awp_paper); nothing to compare.
                for lab in SPRING_LABELS:
                    mine = alignment["methods"].get(method, {}).get(lab, {}).get("kendall_tau")
                    print(f"  {method:22s} {lab:28s} this={_fmt(mine)} (not in the published summary)")
                continue
            for lab in SPRING_LABELS:
                mine = alignment["methods"].get(method, {}).get(lab, {}).get("kendall_tau")
                theirs = pub_methods.get(method, {}).get(lab, {}).get("kendall_tau")
                ok = mine is not None and theirs is not None and abs(mine - theirs) < 5e-4
                mismatches += 0 if ok else 1
                print(f"  {method:22s} {lab:28s} this={_fmt(mine)} published={_fmt(theirs)} {'ok' if ok else 'MISMATCH'}")
        out["published_compare"] = {"path": str(SPRING_PUBLISHED), "mismatches": mismatches}
    else:
        print(f"Published spring summary not found at {SPRING_PUBLISHED}; printing only.")
    row = exploratory[0] if exploratory else {}
    print(
        f"exploratory C-PR - AWP on new approval pairs: delta={_fmt(row.get('delta_tau'))} "
        f"ci=[{_fmt(row.get('ci_low'))}, {_fmt(row.get('ci_high'))}]"
    )
    out_dir = REPLICATION_DIR
    save_json(out_dir / "spring_check.json", out)
    print(f"wrote {out_dir / 'spring_check.json'}; mismatches={mismatches}")
    return 0 if mismatches == 0 else 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--registration", type=Path, default=REGISTRATION_PATH)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--spring-check", action="store_true")
    mode.add_argument("--fixtures", action="store_true")
    parser.add_argument("--n-wallets", type=int, default=48, help="fixture size")
    parser.add_argument(
        "--bootstrap",
        type=int,
        default=None,
        help="resample count; only for --fixtures and --spring-check (the registered run uses 400)",
    )
    parser.add_argument(
        "--allow-unregistered",
        action="store_true",
        help="evaluate the fresh window without a committed registration; the output is marked exploratory",
    )
    args = parser.parse_args()

    config = load_config()
    if args.spring_check:
        return run_spring_check(config, args.bootstrap)

    reg = load_registration(args.registration)
    cfg = window_config(config, reg)
    out_path = Path(reg["evaluation"]["output"])

    if args.fixtures:
        if args.bootstrap is not None:
            cfg["reputation"]["holdout"]["bootstrap_resamples"] = args.bootstrap
        frames = shift_fixture_frames(build_holdout_fixture_frames(n_wallets=args.n_wallets), FIXTURE_SHIFT_DAYS)
        events = {k: frames[k] for k in ("approvals", "transfers", "decoded")}
        matched = frames["wallets"]["wallet"].tolist()
        summary = evaluate(cfg, reg, events, matched)
        summary.update({"mode": "fixtures", "registration": reg["registration"], "at": datetime.now(timezone.utc).isoformat()})
        out_path = out_path.with_name("fixtures_summary.json")
        save_json(out_path, summary)
        print_report(summary)
        print(f"wrote {out_path}")
        return 0

    if args.bootstrap is not None:
        parser.error("--bootstrap is not allowed for the registered evaluation")

    ok, problems, states = registration_check(reg)
    if not ok and not args.allow_unregistered:
        print("The registration is not in place, so the fresh evaluation will not run:")
        for p in problems:
            print(f"  - {p}")
        return 1
    status = fresh_data_status(reg)
    if not status["complete"]:
        print("The June-August extraction is incomplete:")
        print(json.dumps(status, indent=2))
        print("Run scripts/extract_fresh_window.py --extract first.")
        return 1

    spring = load_spring_events(config)
    fresh = load_fresh_events(reg)
    events = {
        "approvals": combine_events(spring["approvals"], fresh["approvals"]),
        "transfers": combine_events(spring["transfers"], fresh["transfers"]),
        "decoded": combine_events(spring["decoded"], fresh["decoded"]),
    }
    summary = evaluate(cfg, reg, events, _matched_wallets(config))
    summary.update(
        {
            "mode": "registered" if ok else "exploratory_unregistered",
            "registration": reg["registration"],
            "registration_sha256": reg.get("_sha256"),
            "plan_sha256": reg.get("_plan_sha256"),
            "registration_git": states,
            "registration_problems": problems,
            "fresh_files": status,
            "at": datetime.now(timezone.utc).isoformat(),
        }
    )
    save_json(out_path, summary)
    print_report(summary)
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
