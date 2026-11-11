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
from common import (BQ_PREFIX, CONTRACT_GRAPH, ONE_YEAR, PROC, REVISED, ROOT, USD_CONSTANTS, USD_INPUTS,  # noqa: E402
                    load_config, save_json)
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


def first_commit_with(doc: str, text: str) -> str | None:
    """Time (UTC) of the first commit in which ``doc`` holds ``text`` (git log -S)."""
    out = subprocess.run(["git", "log", "-S", text, "--format=%H %cI", "--", doc],
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


def _pair_counts(frame: pd.DataFrame, weights: tuple[str, ...]) -> dict:
    """Rows, self-pairs, distinct sources and destinations of a pair table, and its rows of positive weight."""
    out = {"pairs": int(len(frame)), "self_pairs": int((frame["src"] == frame["dst"]).sum()),
           "sources": int(frame["src"].nunique()), "destinations": int(frame["dst"].nunique())}
    for w in weights:
        out[f"positive_{w}"] = int((frame[w] > 0).sum())
    # The largest numbers of pairs that one source and one destination hold, and the pairs of the ten largest sources.
    by_src, by_dst = frame["src"].value_counts(), frame["dst"].value_counts()
    out["largest_source_pairs"] = int(by_src.iloc[0]) if len(by_src) else 0
    out["largest_destination_pairs"] = int(by_dst.iloc[0]) if len(by_dst) else 0
    out["pairs_of_ten_largest_sources"] = int(by_src.iloc[:10].sum())
    return out


def contract_graph_description(cfg: dict) -> dict:
    """The contract-graph variant, from the files on disk only (no BigQuery call): the driver's run manifest, the
    record of the account-type reads, the gate B tables as the download step verified them, the constants, the
    balance check and the ledger."""
    from common import GRAPH, TYPES_DIR, read_parts, require_downloaded, sha256_file
    from graphs import load_graphs, load_nodes

    inputs = require_downloaded("nodes", "allow_pairs_tobs", "allow_pairs_t1", "allow_pairs_uncapped_tobs",
                                "allow_pairs_uncapped_t1", "transfer_pairs_tobs", "transfer_pairs_t1",
                                "importance_tobs", "importance_t1", "inflow_untyped_tobs", "inflow_untyped_t1",
                                "describe_allowances")
    manifest = json.loads((PROC / "run_manifest.json").read_text(encoding="utf-8"))
    res = manifest["results"]
    types = json.loads((TYPES_DIR / "c12_account_types.json").read_text(encoding="utf-8"))
    ext = res["contracts"]["smart_account_extension"]
    by_class = dict(types["counts_account_class"])
    wallets = {k: v for k, v in types["counts_wallet_kind"].items() if k}
    after = {**by_class, "contract": by_class["contract"] - ext["moved"],
             "smart_account": by_class["smart_account"] + ext["moved"]}
    if after["contract"] != res["contracts"]["c12_contracts"]:
        raise SystemExit("refused: the typed contracts less the moved smart accounts are not the rows of c12_contracts")
    out: dict = {"variant": "contract12m"}
    out["events"] = {
        "five_token_rows": res["subset"]["c12_logs5"],
        "distinct_pairs": res["ends"]["c12_pairs5"],
        "addresses": res["ends"]["c12_ends"],
        "transaction_senders": res["activity"]["c12_tx_senders"],
        "rpc_queue": res["queue"]["c12_rpc_queue"],
        "contracts": res["contracts"]["c12_contracts"],
        "user_accounts": res["contracts"]["c12_user_accounts"],
        "rows_between_contracts": res["contracts"]["c12_events_cc"],
        "latest_allowances_between_contracts_both_freezes": res["constants"]["rows"]["c12_allow_triples"],
        "user_account_rows_toward_contracts": res["constants"]["rows"]["c12_user_events"],
    }
    out["account_types"] = {
        "block": types["block_number"], "block_pinned": bool(types["pinned_served"]),
        "read_from": types["read_at"], "read_until": types["updated_at"], "hosts": list(types["served_by"]),
        "rpc_calls": types["rpc_calls"], "addresses": types["n"], "aborted_addresses": len(types["aborted_addresses"]),
        "code_kind": types["counts"], "typed": by_class, "wallet_kind_typed": wallets,
        "proxy_kind": types["counts_proxy_kind"], "probes": types["probes"],
        "extension": {"moved": ext["moved"], "by_code_hash": ext["moved_by_code_hash"],
                      "by_implementation": ext["moved_by_implementation"]},
        "after_extension": after,
        "wallet_kind_after_extension": {**wallets, "erc4337": wallets.get("erc4337", 0) + ext["moved"]},
        "by_reason": res["typing"]["by_reason"],
        "audit_senders_with_code": res["typing"]["audit_senders_with_code"],
    }
    nodes = load_nodes()
    out["nodes"] = {"contracts": int(len(nodes)), **{k: int(nodes[k].sum()) for k in
                    ("is_cohort", "is_cohort_t1", "is_spender_w0", "is_spender_w1")}}
    listed = pd.read_csv(USD_INPUTS / "listed_tokens.csv")
    sym = dict(zip(listed["address"].str.lower(), listed["symbol"]))
    desc = read_parts(GRAPH / "describe_allowances")
    cols = [c for c in desc.columns if c not in ("tag", "token")]
    out["pairs"], out["allowances"], out["importance"] = {}, {}, {}
    for tag in ("tobs", "t1"):
        g = load_graphs(tag)
        unc = read_parts(GRAPH / f"allow_pairs_uncapped_{tag}")
        out["pairs"][tag] = {"allowance_capped": _pair_counts(g.allow, ("w_er", "w_raw")),
                             "allowance_uncapped": _pair_counts(unc, ("w_er", "w_raw")),
                             "transfer": _pair_counts(g.transfer, ("w_awp", "w_raw"))}
        d = desc[desc["tag"] == tag]
        total = {c: (float(d[c].sum()) if c.startswith("sum_") else int(d[c].sum())) for c in cols}
        total["share_capped_to_zero"] = total["n_capped_to_zero"] / total["n_latest_positive"]
        total["share_unlimited"] = total["n_unlimited"] / total["n_latest_positive"]
        per = [{"symbol": sym.get(r["token"], r["token"]), "token": r["token"],
                **{c: (float(r[c]) if c.startswith("sum_") else int(r[c])) for c in cols}}
               for r in d.sort_values("n_latest_positive", ascending=False).to_dict(orient="records")]
        out["allowances"][tag] = {"total": total, "per_token": per}
        imp = read_parts(GRAPH / f"importance_{tag}")
        out["importance"][tag] = {
            "contracts": int(len(imp)), "outside_nodes": int((imp["id"] < 0).sum()),
            "with_i_t": int((imp["i_t"] > 0).sum()), "with_i_a": int((imp["i_a"] > 0).sum()),
            "with_both": int(((imp["i_t"] > 0) & (imp["i_a"] > 0)).sum()),
            "i_t_usd": float(imp["i_t"].sum()), "i_a_usd": float(imp["i_a"].sum()),
            "inflow_untyped_usd": float(read_parts(GRAPH / f"inflow_untyped_{tag}")["usd"].sum()),
        }
    out["anchor_blocks"] = {r["anchor"]: int(r["block_number"]) for r in res["anchors"]["blocks"]}
    audit = json.loads((PROC / "typing" / "balance_audit.json").read_text(encoding="utf-8"))
    out["balance_check"] = {k: audit[k] for k in ("mode", "block", "rows", "judged", "matched", "share",
                                                    "threshold", "passed")}
    out["balance_check"]["balances"] = res["balances"]["c12_bal"]
    out["constants"] = json.loads(USD_CONSTANTS.read_text(encoding="utf-8"))
    out.update(window_prices(cfg))
    ledger = json.loads((ROOT / "data" / "bq_ledger.json").read_text(encoding="utf-8"))
    jobs = [j for j in ledger["jobs"] if j.get("label", "").startswith("contract12m:")]
    out["timing"] = {
        "revision_commit_utc": revision_commit("docs/revision_contract_graph.md"),
        "protocol_commit_utc": revision_commit("docs/discovery_protocol.md"),
        "protocol_fixed_commit_utc": first_commit_with("docs/discovery_protocol.md", '"primary_mode"'),
        "contract12m_jobs": len(jobs),
        "contract12m_jobs_usd": round(sum(j["usd"] for j in jobs), 2),
        "bigquery_usd_total": round(sum(j["usd"] for j in ledger["jobs"]), 2),
        "bigquery_tib_billed": round(sum(j["bytes_billed"] for j in ledger["jobs"]) / 2**40, 3),
        "budget_usd": float(cfg["bigquery"]["budget_usd"]),
    }
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    out["provenance"] = {"head": head or None, "inputs": inputs,
                         "run_manifest_sha256": sha256_file(PROC / "run_manifest.json"),
                         "account_types_json_sha256": sha256_file(TYPES_DIR / "c12_account_types.json")}
    return out


def main() -> int:
    cfg = load_config()
    if CONTRACT_GRAPH:
        out = contract_graph_description(cfg)
        save_json(out, PROC / "describe" / "describe.json")
        print(out["events"], out["account_types"]["after_extension"], out["timing"])
        return 0
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
