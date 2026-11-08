"""Trader labels from decoded GMX V2 closes, and helpers shared by the holdout runs; for the contract-graph
variant, the cohorts, spender sets and label split of docs/revision_contract_graph.md section 8 from its gate B
tables, and the check that every node is a contract under the account types of section 4 with the smart-account
lists of section 13."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from common import (GRAPH, GRAPH_U12, PROC_SHARED, RAW, SMART_ACCOUNT_CODE_HASHES, SMART_ACCOUNT_IMPLEMENTATIONS, TYPES,
                    load_json, part_paths, read_parts, rel_path, with_smart_account_extension)

TRADER_LABELS = {
    "liquidation_free_rate": "Liquidation-free close rate",
    "no_liquidation": "No liquidation",
    "profitable_closes": "Profitable closes",
    "realized_gain": "Realized gain",
    "profitable_share": "Profitable share",
    "non_loss_share": "Non-loss share",
}


def load_closes(tags: tuple[str, ...] = ("obs",)) -> pd.DataFrame:
    frames = [read_parts(PROC_SHARED / "gmx" / f"gmx_contract_closes_{t}_decoded") for t in tags]
    df = pd.concat(frames, ignore_index=True)
    df["block_timestamp"] = pd.to_datetime(df["block_timestamp"], utc=True)
    df["pnl"] = df["base_pnl_usd"].astype(float) / 1e30
    df["account"] = df["account"].str.lower()
    return df


def trader_labels(closes: pd.DataFrame, start: str, end: str, min_closes: int) -> pd.DataFrame:
    """One row per account with at least ``min_closes`` closes in [start, end].

    A close counts as profitable when it is not a liquidation and its base PnL is
    positive, and as a loss when it is not a liquidation and its base PnL is negative,
    so a liquidated close is neither (the non-loss share counts it as not a loss).
    """
    w = closes[(closes["block_timestamp"] >= pd.Timestamp(start)) & (closes["block_timestamp"] <= pd.Timestamp(end))]
    w = w.assign(win=(~w["is_liquidation"]) & (w["pnl"] > 0),
                 loss=(~w["is_liquidation"]) & (w["pnl"] < 0),
                 gain=w["pnl"].clip(lower=0))
    g = w.groupby("account").agg(closes=("win", "size"), liquidations=("is_liquidation", "sum"),
                                 profitable_closes=("win", "sum"), losses=("loss", "sum"),
                                 realized_gain=("gain", "sum"))
    g = g[g["closes"] >= min_closes].copy()
    g["liquidation_free_rate"] = 1.0 - g["liquidations"] / g["closes"]
    g["no_liquidation"] = (g["liquidations"] == 0).astype(float)
    g["profitable_share"] = g["profitable_closes"] / g["closes"]
    g["non_loss_share"] = 1.0 - g["losses"] / g["closes"]
    return g.astype(float)


def account_types() -> pd.DataFrame:
    """Account type of every address read so far (cohort candidates, holdout spenders, GMX accounts)."""
    frames = []
    for stem in (RAW / "cohort" / "candidate_account_types", RAW / "cohort" / "holdout_spender_types",
                 RAW / "gmx" / "gmx_account_types", RAW / "gmx" / "gmx_account_types_w1"):
        try:
            frames.append(read_parts(stem)[["address", "code_kind"]])
        except FileNotFoundError:
            pass
    return pd.concat(frames, ignore_index=True).drop_duplicates("address").set_index("address")["code_kind"]


def strata_tau(score: np.ndarray, label: np.ndarray, closes: np.ndarray, edges=(3, 5, 10, 25)) -> float | None:
    """Kendall tau_b within strata of closes (3-4, 5-9, 10-24, 25+), weighted by wallet pairs."""
    from stats import kendall_tau_b
    bins = np.digitize(closes, edges[1:])
    num = den = 0.0
    for b in np.unique(bins):
        m = bins == b
        n = int(m.sum())
        t = kendall_tau_b(score[m], label[m]) if n >= 5 else None
        if t is None:
            continue
        pairs = n * (n - 1) / 2
        num += t * pairs
        den += pairs
    return num / den if den else None


# --------------------------------------------------------------------------- the contract-graph variant
# (docs/revision_contract_graph.md sections 4, 5, 8 and 13; called only under CONTRACT_REP_VARIANT=contract12m)

MEMBER_LISTS = ("cohort_tobs", "cohort_t1", "spenders_w0", "spenders_w1")      # members.list (sql/38_c12_cohorts.sql)
MEMBER_CLASSES = ("contract", "user_account", "system", "untyped")
USER_SOURCES = ("tx_sender", "rpc_eoa", "rpc_eoa_7702", "rpc_smart_account")
NODE_FLAGS = {"cohort_tobs": "is_cohort", "cohort_t1": "is_cohort_t1", "spenders_w0": "is_spender_w0",
              "spenders_w1": "is_spender_w1"}
LABEL_COLUMNS = ("future_new_approvers", "future_revoke_count", "future_revoke_rate", "future_keep_rate",
                 "future_revoke_value", "future_new_transfer_senders", "future_drain_owners")   # sql/16
SPLIT_COUNTS = ("future_new_approvers", "future_revoke_count", "future_new_transfer_senders", "future_drain_owners")
SPLIT_RATES = ("future_revoke_rate", "future_keep_rate")
PARTS = {"user_accounts": "_user", "contracts": "_contract", "other": "_other"}   # column suffixes of label_split
PART_SOURCES = {"user_accounts": "c12_user_accounts", "contracts": "c12_contracts",
                "other": "the zero address of mints, system addresses and untyped addresses"}
UNION_NOTE = "decides no rule (docs/revision_contract_graph.md section 8)"
UNCAPPED_NOTE = "decides no rule (docs/revision_contract_graph.md section 5)"
SPLIT_NOTE = "secondary description outside every rule (docs/revision_contract_graph.md section 8)"
# The amendment that extends rule 3(b) of section 4.2. contract_types applies its lists:
# common.SMART_ACCOUNT_CODE_HASHES and common.SMART_ACCOUNT_IMPLEMENTATIONS.
EXTENSION = "docs/revision_contract_graph.md section 13, amendment of 9 November 2026"
ADDRESS = r"0x[0-9a-f]{40}"


def load_members() -> pd.DataFrame:
    """The members table of the gate B download (graph-tables-contract-12m/members, sql/38_c12_cohorts.sql): one row
    per member of each list of MEMBER_LISTS with its class of revision section 4 (contract, user account, system
    address or untyped); columns list, address, class and source (a user account's source, else NaN)."""
    where = f"refused: {GRAPH.name}/members"
    m = read_parts(GRAPH / "members")
    cols = ["list", "address", "class", "source"]
    missing = [c for c in cols if c not in m.columns]
    if missing:
        raise SystemExit(f"{where} lacks the columns {missing}")
    m = m[cols].copy()
    for c in ("list", "address", "class"):
        m[c] = m[c].astype(str)
    lists = sorted({str(v) for v in m.loc[~m["list"].isin(MEMBER_LISTS), "list"]})
    if lists:
        raise SystemExit(f"{where} holds lists outside {MEMBER_LISTS}: {lists[:5]}")
    classes = sorted({str(v) for v in m.loc[~m["class"].isin(MEMBER_CLASSES), "class"]})
    if classes:
        raise SystemExit(f"{where} holds classes outside {MEMBER_CLASSES}: {classes[:5]}")
    if m.duplicated(["list", "address"]).any():
        raise SystemExit(f"{where} repeats a (list, address)")
    odd = m.loc[~m["address"].str.fullmatch(ADDRESS, na=False), "address"]
    if len(odd):
        raise SystemExit(f"{where} holds {len(odd)} address(es) that are not lowercase 0x hex of 20 bytes "
                         f"({', '.join(str(a) for a in odd.head(3))})")
    user = (m["class"] == "user_account").to_numpy()
    sourced = m["source"].notna().to_numpy()
    if (user & ~sourced).any():
        raise SystemExit(f"{where} holds {int((user & ~sourced).sum())} user account(s) without a source")
    if (~user & sourced).any():
        raise SystemExit(f"{where} holds a source for {int((~user & sourced).sum())} member(s) that are not user "
                         "accounts")
    sources = sorted({str(v) for v in m.loc[user & ~m["source"].isin(USER_SOURCES).to_numpy(), "source"]})
    if sources:
        raise SystemExit(f"{where} holds sources outside {USER_SOURCES}: {sources[:5]}")
    return m


def u12_stem(name: str) -> Path:
    """The twelve-month list ``name`` of MEMBER_LISTS on disk: the cohorts of graph-tables-usd-12m, or its labels,
    whose wallets are the spenders."""
    return GRAPH_U12 / {"cohort_tobs": "cohort", "cohort_t1": "cohort_t1", "spenders_w0": "labels_w0",
                        "spenders_w1": "labels_w1"}[name]


def u12_addresses(name: str) -> list[str]:
    """The addresses of the twelve-month list ``name`` as lowercase 0x hex, in the order on disk (the cohorts hold
    20-byte binary addresses, the labels the wallet as text)."""
    stem = u12_stem(name)
    if name.startswith("cohort"):
        out = ["0x" + bytes(a).hex() for a in read_parts(stem, ["address"])["address"]]
    else:
        out = read_parts(stem, ["wallet"])["wallet"].astype(str).str.lower().tolist()
    if len(set(out)) != len(out):
        raise SystemExit(f"refused: {GRAPH_U12.name}/{stem.name} repeats an address")
    return out


def contract_members(name: str, nodes: pd.DataFrame,
                     members: pd.DataFrame | None = None) -> tuple[pd.DataFrame, dict]:
    """The cohort of revision section 8 from the twelve-month list ``name`` (D7): for a cohort the members that are
    not user accounts, each a contract; for a spender set the members that are contracts, the others reported by
    class and an untyped one refused. Every kept member is a node flagged for its list and is never dropped.
    Returns the kept members indexed by node id in increasing order (column address) and their counts."""
    m = load_members() if members is None else members
    g = m[m["list"] == name]
    listed = u12_addresses(name)
    have = set(g["address"])
    if have != set(listed) or len(g) != len(listed):
        raise SystemExit(f"refused: the members of {name} in {GRAPH.name}/members are not those of "
                         f"{GRAPH_U12.name}/{u12_stem(name).name} ({len(set(listed) - have)} missing, "
                         f"{len(have - set(listed))} extra)")
    cls = g["class"]
    if name.startswith("cohort"):
        keep = g[cls != "user_account"]
        bad = keep[keep["class"] != "contract"]
        if len(bad):
            raise SystemExit(f"refused: {len(bad)} member(s) of u12_{name} are neither user accounts nor contracts "
                             f"({_examples(bad)}); job 42 (cohort_not_contract_{name[7:]}) stops the run on them")
    else:
        bad = g[cls == "untyped"]
        if len(bad):
            raise SystemExit(f"refused: {len(bad)} spender(s) of u12_labels_{name[-2:]} are untyped "
                             f"({_examples(bad)}); job 42 (spender_untyped_{name[-2:]}) stops the run on them")
        keep = g[cls == "contract"]
    pos = nodes.set_index(nodes["address"].astype(str))["id"]
    ids = pos.reindex(keep["address"].to_numpy())
    if ids.isna().any():
        lacking = keep["address"].to_numpy()[ids.isna().to_numpy()]
        raise SystemExit(f"refused: {len(lacking)} contract member(s) of {name} have no node id "
                         f"({', '.join(lacking[:5])}); nodes holds every contract member of the four lists "
                         "(docs/discovery_protocol.md section 8, job 42 nodes_set)")
    flag = NODE_FLAGS[name]
    flagged = set(nodes.loc[nodes[flag].astype(bool), "address"].astype(str))
    if flagged != set(keep["address"]):
        raise SystemExit(f"refused: nodes.{flag} marks {len(flagged):,} contracts, {name} has {len(keep):,} contract "
                         "members, not the same (job 42 node_flags)")
    frame = pd.DataFrame({"address": keep["address"].to_numpy()},
                         index=pd.Index(ids.to_numpy(np.int64), name="id")).sort_index()
    counts = {"list": name, "listed": int(len(g)),
              "by_class": {c: int((cls == c).sum()) for c in MEMBER_CLASSES},
              "user_accounts_by_source": {s: int((g["source"] == s).sum()) for s in USER_SOURCES},
              "cohort": int(len(frame))}
    return frame, counts


def _examples(frame: pd.DataFrame, k: int = 5) -> str:
    return ", ".join(f"{a} ({c})" for a, c in zip(frame["address"].head(k), frame["class"].head(k)))


def spender_cohort(window: str, nodes: pd.DataFrame,
                   members: pd.DataFrame | None = None) -> tuple[pd.DataFrame, dict]:
    """The W0 or W1 spender cohort of revision section 8 with its labels: the spenders of
    graph-tables-usd-12m/labels_{window} that are contracts (D7), indexed by node id ("id") in increasing order,
    with the column wallet and the seven label columns of sql/16 unchanged (D8)."""
    if part_paths(GRAPH / f"labels_{window}"):
        raise SystemExit(f"refused: {GRAPH.name} holds labels_{window}; the labels of this revision are those of "
                         f"{GRAPH_U12.name} (docs/revision_contract_graph.md section 8)")
    frame, counts = contract_members(f"spenders_{window}", nodes, members)
    lab = read_parts(GRAPH_U12 / f"labels_{window}")
    missing = sorted(set(LABEL_COLUMNS) - set(lab.columns))
    if missing:
        raise SystemExit(f"refused: {GRAPH_U12.name}/labels_{window} lacks {missing}")
    lab["wallet"] = lab["wallet"].astype(str).str.lower()
    out = lab.set_index("wallet").loc[frame["address"].to_numpy(), list(LABEL_COLUMNS)].reset_index()
    out.index = pd.Index(frame.index.to_numpy(np.int64), name="id")
    return out, counts


def contract_types(addresses) -> pd.Series:
    """account_class of each address in the account types of revision section 4 (contract-types/c12_account_types)
    with the smart-account lists of the amendment of 9 November 2026 (revision section 13) applied by
    common.with_smart_account_extension, as sql/31 and the structure pilot apply them: a typed contract whose code hash
    is listed, or whose code hash and implementation are a listed pair, is a smart account, so a user account. NaN
    where the reads hold no row (plan section 7: account_types() stays, contract_types() is added)."""
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.parquet as pq

    meta_path = TYPES.with_suffix(".json")
    meta = load_json(meta_path) if meta_path.exists() else {}
    rel = rel_path(TYPES)
    if meta.get("complete") is not True or meta.get("pending"):
        raise SystemExit(f"refused: {rel}.json records no complete read (complete true, pending 0)")
    paths = part_paths(TYPES)
    if not paths:
        raise SystemExit(f"refused: no parts for {rel}")
    addr = pd.Index(pd.Series(list(addresses), dtype=object).astype(str))
    want = pa.array(addr.tolist(), type=pq.read_schema(paths[0]).field("address").type)
    # The rows of the addresses asked for, part by part: the lists need the code hash and the implementation of a row,
    # and only these rows keep them.
    hits = []
    for p in paths:
        t = pq.read_table(p, columns=["address", "account_class", "code_hash", "implementation"])
        hits.append(t.filter(pc.is_in(t["address"], value_set=want)))
    df = pa.concat_tables(hits).to_pandas()
    if df["address"].duplicated().any():
        raise SystemExit(f"refused: {rel} repeats an address")
    df = with_smart_account_extension(df)
    return df.set_index(df["address"].astype(str))["account_class"].astype(object).reindex(addr)


def assert_contract_only(nodes: pd.DataFrame, cfg: dict) -> dict:
    """Every node is lowercase 0x hex, above the system range and of class 'contract' under the account types of
    revision section 4 with the smart-account lists of section 13 (contract_types; section 5: every node of every
    graph is a contract). The lists are applied here to the typing output itself, so a node that they make a smart
    account is refused, also when the node set came from a run of job 31 without them. Job 42 (nodes_not_contract)
    also checks in BigQuery that every node is in c12_contracts, so that no node sent a transaction. The record names
    the extension and the sizes of its lists."""
    addr = nodes["address"].astype(str)
    if not addr.str.fullmatch(ADDRESS, na=False).all():
        raise SystemExit("refused: nodes holds an address that is not lowercase 0x hex of 20 bytes")
    top = f"0x{int(cfg['contract_graph']['system_address_max']):040x}"
    low = addr[addr <= top]
    if len(low):
        raise SystemExit(f"refused: nodes holds {len(low)} system address(es) or the zero address "
                         f"({', '.join(low.head(5))}); they are never graph nodes (revision section 4.1)")
    cls = contract_types(addr)
    if cls.isna().any():
        raise SystemExit(f"refused: {int(cls.isna().sum())} node(s) have no account type "
                         f"({', '.join(cls.index[cls.isna()][:5])})")
    other = cls[cls != "contract"]
    if len(other):
        raise SystemExit(f"refused: {len(other)} node(s) are not contracts under the account types with the "
                         "smart-account lists of revision section 13 "
                         f"({', '.join(f'{a} ({c})' for a, c in other.head(5).items())}); every node of every graph "
                         "is a contract (docs/revision_contract_graph.md section 5)")
    return {"nodes": int(len(addr)), "typed_contracts": int(len(addr)), "types": rel_path(TYPES),
            "smart_account_extension": {"amendment": EXTENSION, "code_hashes": len(SMART_ACCOUNT_CODE_HASHES),
                                        "code_hash_implementations": len(SMART_ACCOUNT_IMPLEMENTATIONS)}}


def _wallets(wallets, k: int = 3) -> str:
    """Up to ``k`` wallets for a refusal message."""
    return ", ".join(str(w) for w in list(wallets)[:k])


def label_split(window: str, lab: pd.DataFrame) -> dict:
    """The label split of revision section 8 for the spender cohort ``lab`` (spender_cohort): each label of sql/16
    in its parts from user accounts, contracts and other accounts, which must add up to the label; a description
    outside every rule (no τ, contrast or verdict is computed on a part)."""
    split = read_parts(GRAPH / f"label_split_{window}")
    split["wallet"] = split["wallet"].astype(str)
    if split["wallet"].duplicated().any():
        raise SystemExit(f"refused: label_split_{window} repeats a spender")
    split = split.set_index("wallet")
    w = lab["wallet"].astype(str).to_numpy()
    lacking = sorted(set(w) - set(split.index))
    if lacking:
        raise SystemExit(f"refused: label_split_{window} lacks {len(lacking)} spender(s) of the cohort "
                         f"({_wallets(lacking)})")
    s = split.loc[w]
    off = (s["spender_class"].astype(str) != "contract").to_numpy()
    if off.any():
        raise SystemExit(f"refused: label_split_{window} does not class every spender of the cohort as a contract: "
                         f"{int(off.sum())} spender(s) ({_wallets(w[off])})")
    n = int(len(s))
    owners = {k: s[f"n_t1{suf}"].to_numpy(np.int64) for k, suf in PARTS.items()}
    off = sum(owners.values()) != s["n_t1"].to_numpy(np.int64)
    if np.any(off):
        raise SystemExit(f"refused: label_split_{window}: the parts of n_t1 do not add up to n_t1 for "
                         f"{int(np.sum(off))} spender(s) ({_wallets(w[off])})")
    labels = {}
    for col in LABEL_COLUMNS:
        total = lab[col].to_numpy()
        parts = {k: s[f"{col}{suf}"].to_numpy() for k, suf in PARTS.items()}
        summed = parts["user_accounts"] + parts["contracts"] + parts["other"]
        # twice the tolerances of job 42, which compares the parts with its recount and the recount with the label
        if col in SPLIT_COUNTS:
            ok = summed.astype(np.int64) == total.astype(np.int64)
        elif col in SPLIT_RATES:
            ok = np.abs(summed - total) <= 2e-12
        else:                                        # future_revoke_value
            ok = np.abs(summed - total) <= 2e-9 * np.maximum(1.0, np.abs(total))
        if not ok.all():
            raise SystemExit(f"refused: label_split_{window}: the parts of {col} do not add up to the label of "
                             f"{GRAPH_U12.name}/labels_{window} for {int((~ok).sum())} spender(s) "
                             f"({_wallets(w[~ok])}) (job 42 label_parts_sum_{window})")
        if col in SPLIT_RATES:
            labels[col] = {"mean": float(total.mean()) if n else None,
                           **{f"mean_{k}": (float(v.mean()) if n else None) for k, v in parts.items()}}
            continue
        cast = int if col in SPLIT_COUNTS else float
        tot = total.sum()
        labels[col] = {"total": cast(tot), **{k: cast(v.sum()) for k, v in parts.items()},
                       **{f"share_{k}": (float(v.sum() / tot) if tot else None) for k, v in parts.items()},
                       "spenders_with_label": int((total > 0).sum()),
                       **{f"spenders_with_{k}": int((v > 0).sum()) for k, v in parts.items()}}
    return {"note": SPLIT_NOTE, "spenders": n, "parts": dict(PART_SOURCES),
            "owners_at_freeze": {"total": int(s["n_t1"].sum()), **{k: int(v.sum()) for k, v in owners.items()}},
            "labels": labels}
