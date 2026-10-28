#!/usr/bin/env python3
"""Descriptive statistics of the extracted data for Chapters 3, 4 and Appendix 8.4.

Reads the two BigQuery tables written by sql/10_describe.sql (monthly event counts and
amount shares) and the decoded GMX closes, and writes data/2-.../describe/describe.json:
monthly counts per stream, the share of transfers and latest allowances of at least
10 base units, unlimited allowances and the owners that hold them, GMX V2 closes and
accounts of contract traders per quarter, and the timing of the plan, scan A, the
registration and scan B.
The twelve-month variant (CONTRACT_REP_VARIANT=usd12m) reads the u12_describe_* tables of
sql/22_usd12m_describe.sql and adds the price days and the Chainlink check inside its windows.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import BQ_PREFIX, ONE_YEAR, PROC, REVISED, ROOT, USD_CONSTANTS, USD_INPUTS, load_config, save_json  # noqa: E402
from labels import load_closes  # noqa: E402


def bq_json(sql: str) -> list[dict]:
    out = subprocess.run(["bq", "query", "--use_legacy_sql=false", "--format=json", "--max_rows=100000", sql],
                         capture_output=True, text=True, check=True, shell=True).stdout
    return json.loads(out[out.index("["):])


def job_times(job_id: str) -> dict:
    out = subprocess.run(["bq", "show", "--format=json", "-j", f"dissertation-bq:US.{job_id}"],
                         capture_output=True, text=True, check=True, shell=True).stdout
    st = json.loads(out)["statistics"]
    conv = lambda ms: datetime.fromtimestamp(int(ms) / 1000, timezone.utc).isoformat(timespec="seconds")
    return {"created": conv(st["creationTime"]), "ended": conv(st["endTime"])}


def revision_commit(doc: str = "docs/revision_price_weighting.md") -> str | None:
    """Time (UTC) of the commit that added ``doc``."""
    out = subprocess.run(["git", "log", "--diff-filter=A", "--format=%H %cI", "--", doc],
                         cwd=ROOT, capture_output=True, text=True).stdout.strip().splitlines()
    if not out:
        return None
    sha, when = out[-1].split()
    return f"{sha[:7]} {datetime.fromisoformat(when).astimezone(timezone.utc).isoformat(timespec='seconds')}"


def table_json(ds: str, table: str) -> list[dict]:
    """Every row of a small table: tabledata.list (not billed) in the twelve-month variant, a query otherwise."""
    if not ONE_YEAR:
        return bq_json(f"SELECT * FROM `{ds}.{table}`")
    from google.cloud import bigquery
    client = bigquery.Client(project=ds.split(".")[0])
    return [dict(r.items()) for r in client.list_rows(f"{ds}.{table}")]


def window_prices(cfg: dict) -> dict:
    """Twelve-month variant: the price days of the selected tokens and the Chainlink check on the days its
    windows cover, from the start of the W0 score window to the end of W1."""
    first, last = cfg["holdout"]["start_ts"][:10], cfg["registered_window"]["outcome_end"][:10]
    listed = pd.read_csv(USD_INPUTS / "listed_tokens.csv")
    sel = listed[listed["selected"].astype(str).str.lower() == "true"]
    sym = dict(zip(sel["address"].str.lower(), sel["symbol"]))
    prices = pd.read_csv(USD_INPUTS / "daily_prices_usd.csv")
    prices["address"] = prices["address"].str.lower()
    p = prices[prices["address"].isin(list(sym)) & (prices["day"] >= first) & (prices["day"] <= last)]
    flag = lambda col: col.astype(str).str.lower() == "true"  # noqa: E731
    per = [{"symbol": sym[a], "address": a, "days": int(len(g)), "second_key_days": int((g["key"] == "second").sum()),
            "filled_days": int(flag(g["filled"]).sum()), "spike_days": int(flag(g["spike"]).sum())}
           for a, g in p.groupby("address")]
    chk = pd.read_csv(USD_INPUTS / "chainlink_check.csv")
    c = chk[(chk["day"] >= first) & (chk["day"] <= last)]
    days = (datetime.fromisoformat(last) - datetime.fromisoformat(first)).days + 1
    return {
        "price_days": {"first_day": first, "last_day": last, "days": days, "per_token": per},
        "chainlink_check_in_windows": {
            "dates": int(c["day"].nunique()),
            "per_token": {s: {"n": int(len(g)), "median": float(g["rel_diff"].abs().median()),
                              "max": float(g["rel_diff"].abs().max())} for s, g in c.groupby("symbol")}},
    }


def revised_amounts(ds: str) -> dict:
    """Token list, the rows it and the revised cohort leave out, amounts in USD (sql/18_usd_describe.sql;
    sql/22_usd12m_describe.sql in the twelve-month variant)."""
    tok = pd.DataFrame(table_json(ds, f"{BQ_PREFIX}describe_tokens"))
    num_cols = [c for c in tok.columns if c not in ("token", "listed")]
    tok[num_cols] = tok[num_cols].astype(float)
    listed = pd.read_csv(USD_INPUTS / "listed_tokens.csv")
    sym = dict(zip(listed["address"].str.lower(), listed["symbol"]))
    tok["symbol"] = tok["token"].map(lambda a: sym.get(a, "all unlisted tokens"))
    lst, other = tok[tok["token"] != "unlisted"], tok[tok["token"] == "unlisted"]
    streams = ("approvals", "transfers", "approvals_w1", "transfers_w1")
    reg_total = {s: int(tok[f"reg_{s}"].sum()) for s in streams}
    reg_listed = {s: int(lst[f"reg_{s}"].sum()) for s in streams}
    rev = {s: int(lst[f"rev_{s}"].sum()) for s in streams}
    rows = {
        "registered_ego": reg_total,
        "unlisted_tokens": {"tokens": int(other["tokens"].sum()) if len(other) else 0,
                            **{s: reg_total[s] - reg_listed[s] for s in streams}},
        "listed_tokens_outside_revised_ego": {s: reg_listed[s] - rev[s] for s in streams},
        "revised_ego": rev,
        "revised_share_of_registered": {s: rev[s] / reg_total[s] if reg_total[s] else None for s in streams},
        "revised_transfers_without_price": int(lst["rev_transfers_without_price"].sum()),
    }
    per_token = lst.sort_values("rev_transfers", ascending=False)[
        ["token", "symbol", *[f"reg_{s}" for s in streams], *[f"rev_{s}" for s in streams],
         "rev_transfer_usd", "rev_transfer_usd_w1", "rev_transfers_without_price"]]
    vals = {r["what"]: r for r in table_json(ds, f"{BQ_PREFIX}describe_values")}
    a, t = vals["latest_allowances_tobs"], vals["transfers_obs"]
    pa, pt = [float(x) for x in a["usd_percentiles"]], [float(x) for x in t["usd_percentiles"]]
    n_a = int(a["n"])
    amounts = {
        "latest_allowances_tobs": n_a, "unlimited_allowances": int(a["unlimited"]),
        "unlimited_share": int(a["unlimited"]) / n_a, "allowances_at_or_above_cap": int(a["at_or_above_cap"]),
        "allowances_at_or_above_cap_share": int(a["at_or_above_cap"]) / n_a,
        "owners": int(a["owners"]), "owners_with_unlimited": int(a["owners_unlimited"]),
        "owners_with_both_kinds": int(vals["owners_both_kinds_tobs"]["owners_both"]),
        "finite_allowance_usd_percentiles_tobs": {f"p{q}": pa[q] for q in (10, 25, 50, 75, 90, 99)},
        "transfers_obs": int(t["n"]),
        "transfer_usd_percentiles_obs": {f"p{q}": pt[q] for q in (10, 25, 50, 75, 90, 99)},
    }
    prices = pd.read_csv(USD_INPUTS / "daily_prices_usd.csv")
    fill = prices.groupby("address").agg(days=("day", "size"), filled_days=("filled", "sum"),
                                         first_day=("day", "min"), min_confidence=("confidence", "min"))
    fill.index = fill.index.str.lower()
    fill["symbol"] = fill.index.map(sym)
    return {
        "rows": rows,
        "per_token": per_token.to_dict(orient="records"),
        "amounts": amounts,
        "constants": json.loads(USD_CONSTANTS.read_text(encoding="utf-8")),
        "prices": fill.reset_index().to_dict(orient="records"),
        "listed_tokens": int(len(listed)),
        "priced_tokens": int((listed["priced"].astype(str).str.lower() == "true").sum()),
        "selected_tokens": int((listed["selected"].astype(str).str.lower() == "true").sum()),
        "listed_without_price": json.loads((USD_INPUTS / "usd_inputs.json").read_text(encoding="utf-8"))["listed_without_price"],
    }


def main() -> int:
    cfg = load_config()
    ds = f"{cfg['bigquery']['project_id']}.{cfg['bigquery']['dataset']}"
    if REVISED:
        if ONE_YEAR:
            monthly = pd.DataFrame(table_json(ds, f"{BQ_PREFIX}describe_monthly")).sort_values(
                ["stream", "month"]).reset_index(drop=True)
        else:
            monthly = pd.DataFrame(bq_json(f"SELECT * FROM `{ds}.u_describe_monthly` ORDER BY stream, month"))
        monthly["n"] = monthly["n"].astype(int)
        out = revised_amounts(ds)
        if ONE_YEAR:
            out.update(window_prices(cfg))
        closes = load_closes(("obs", "w1"))
        q = closes.assign(quarter=closes["block_timestamp"].dt.tz_convert(None).dt.to_period("Q").astype(str))
        gmx = q.groupby("quarter").agg(closes=("account", "size"), accounts=("account", "nunique"),
                                       liquidations=("is_liquidation", "sum")).reset_index()
        ledger = json.loads((ROOT / "data" / "bq_ledger.json").read_text(encoding="utf-8"))
        revised_jobs = [j for j in ledger["jobs"] if j.get("label", "").startswith("revised")]
        if ONE_YEAR:
            # The twelve-month jobs read the US-dollar ego tables of sql/12 and sql/19 through views.
            ego = [j for j in revised_jobs if j.get("sql") in ("sql/12_usd_ego.sql", "sql/19_usd_load.sql")]
            jobs12 = [j for j in ledger["jobs"] if j.get("label", "").startswith("usd12m:")]
            out["timing"] = {
                "revision_commit_utc": revision_commit(),
                "window_revision_commit_utc": revision_commit("docs/revision_one_year_window.md"),
                "usd_ego_tables_jobs_usd": round(sum(j["usd"] for j in ego), 2),
                "usd12m_jobs_usd": round(sum(j["usd"] for j in jobs12), 2),
            }
        else:
            out["timing"] = {
                "revision_commit_utc": revision_commit(),
                "revised_jobs_usd": round(sum(j["usd"] for j in revised_jobs), 2),
            }
        out["timing"].update({
            "bigquery_usd_total": round(sum(j["usd"] for j in ledger["jobs"]), 2),
            "bigquery_tib_billed": round(sum(j["bytes_billed"] for j in ledger["jobs"]) / 2**40, 3),
        })
        out["monthly_counts"] = monthly.to_dict(orient="records")
        out["gmx_contract_traders_by_quarter"] = gmx.to_dict(orient="records")
        save_json(out, PROC / "describe" / "describe.json")
        print(out["rows"], out["amounts"], out["timing"])
        return 0
    monthly = pd.DataFrame(bq_json(f"SELECT * FROM `{ds}.describe_monthly` ORDER BY stream, month"))
    monthly["n"] = monthly["n"].astype(int)
    values = {r["what"]: {k: (int(v) if v not in (None, "") else None) for k, v in r.items() if k != "what"}
              for r in bq_json(f"SELECT * FROM `{ds}.describe_values`")}
    t = values["transfers_ego"]
    a = values["latest_allowances_tobs"]
    shares = {
        "transfers_ego": t["n"], "transfers_ge10_share": t["ge10"] / t["n"],
        "latest_allowances_tobs": a["n"], "allowances_ge10_share": a["ge10"] / a["n"],
        "unlimited_allowances": a["ge1e30"], "unlimited_share": a["ge1e30"] / a["n"],
        "owners": a["owners"], "owners_with_unlimited": a["owners_unlimited"],
        "owners_with_both_kinds": values["owners_both_kinds_tobs"]["owners_both"],
    }
    closes = load_closes(("obs", "w1"))
    q = closes.assign(quarter=closes["block_timestamp"].dt.tz_convert(None).dt.to_period("Q").astype(str))
    gmx = q.groupby("quarter").agg(closes=("account", "size"), accounts=("account", "nunique"),
                                   liquidations=("is_liquidation", "sum")).reset_index()
    ledger = json.loads((ROOT / "data" / "bq_ledger.json").read_text(encoding="utf-8"))
    scan_a = next(j for j in ledger["jobs"] if j["label"].startswith("scan A"))
    scan_b = next(j for j in ledger["jobs"] if j["label"].startswith("scan B"))
    timing = {
        "plan_commit_43d8045_utc": "2026-10-09T13:41:27+00:00",
        "scan_a": job_times(scan_a["job_id"]),
        "registration_commit_0d3a057_utc": "2026-10-09T16:49:32+00:00",
        "scan_b": job_times(scan_b["job_id"]),
        "bigquery_usd_total": round(sum(j["usd"] for j in ledger["jobs"]), 2),
        "bigquery_tib_billed": round(sum(j["bytes_billed"] for j in ledger["jobs"]) / 2**40, 3),
    }
    save_json({"monthly_counts": monthly.to_dict(orient="records"), "amounts": shares,
               "gmx_contract_traders_by_quarter": gmx.to_dict(orient="records"), "timing": timing},
              PROC / "describe" / "describe.json")
    print(shares, timing)
    return 0


if __name__ == "__main__":
    sys.exit(main())
