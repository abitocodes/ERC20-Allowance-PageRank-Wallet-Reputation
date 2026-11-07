#!/usr/bin/env python3
"""The discovery-order test of docs/discovery_protocol.md: the structure pilot and the crawl runs.

It belongs to the contract-graph variant: CONTRACT_REP_VARIANT is set to contract12m when unset, and
any other variant is refused.

  python scripts/run_discovery.py --window t1 --feasibility
      The structure pilot of protocol section 7. It reads the structure table of job 35
      (graph-tables-contract-12m/struct_t1: a, b as 0x hex, layer in allow_capped, allow_uncapped,
      transfer), the account types (contract-types/c12_account_types) and the W0 lists of the
      twelve-month analysis (graph-tables-usd-12m/cohort_t1 and the wallet column of labels_w0), and
      writes revised-contract-12m/discovery/feasibility_t1.json: nodes and edges per layer and of
      the union (capped allowances and transfers, self-loops ignored), the bow-tie, |SCC u OUT|, its
      union pairs, the WCC that holds the giant SCC and its union pairs, the share of SCC u OUT with
      a capped allowance in-edge, the coverage of the W0 cohort and the W0 spender cohort (members
      typed as contracts), the account types (counts by class, wallet kind and proxy kind over the
      queue and over the nodes of the union graph), the code families (the 50 largest groups of
      contract nodes by code hash, and every group with a member whose entryPoint() answers a
      canonical EntryPoint), the projected run time T(rho) and the rules for the primary mode, rho,
      q and the stop flags. It computes no weight, importance, crawl, curve, label, constant or
      degree ranking: it never imports scoring.py, graphs.py or stats.py and calls only the
      structure and rule functions of crawl.py. It refuses once the
      protocol is fixed, since its output is then pinned by its hash. When a stop flag is set it
      still writes the file and exits with status 2: the run stops before gate B.

  python scripts/run_discovery.py [--window tobs|t1] [--mode out|both] [--workers N]
      The main runs of sections 4 to 6 and 8. Without --window, T_obs then t1; without --mode, the
      primary mode then the other one; the rho/4 sensitivity runs with the primary mode only. Each
      run refuses unless the section "Protocol fixed" below is filled and the files in COMMITTED are
      committed without local changes. It reads the gate B tables of graph-tables-contract-12m
      (nodes, allow_pairs_{tag}, transfer_pairs_{tag}, importance_{tag} with node id -1 for a typed
      contract outside G, and the one-row inflow_untyped_{tag} with its column usd), builds U, the seeds and
      the hot sets, runs every crawl over (seed, ordering) tasks in --workers processes (default
      1; the results do not depend on it), checks the invariants (every crawl visits U; the final
      walk of each walk crawl equals the scoring function on G restricted to U within 1e-9) and
      writes revised-contract-12m/discovery/discovery_{tag}_{mode}.json with the parquet parts
      discovery_{tag}_{mode}_hot_visits (visit index of every hot contract for every seed and
      ordering) and discovery_{tag}_{mode}_hot_sets (membership). Only the run of T_obs in the
      primary mode decides (protocol section 6; "decides": true): the other files report the same
      contrasts without a verdict, with the facts of their intervals only (above 0, below 0).

The section "Protocol fixed" of docs/discovery_protocol.md (from its "## Protocol fixed" heading to the
next "## " heading) must hold a fenced block marked json; the first one is read, and it must be one
JSON object with exactly these keys (the fences start their lines):

    ```json
    {
      "date": "2026-11-09",
      "feasibility": "data/2-processed-tables-and-evaluations/revised-contract-12m/discovery/feasibility_t1.json",
      "sha256": "<64 lowercase hex digits: the SHA-256 of that file>",
      "U": 123456, "E_U": 1234567, "WCC": 234567, "E_WCC": 2345678,
      "rho": 0.01,
      "q": 0.01,
      "primary_mode": "out"
    }
    ```

date is YYYY-MM-DD; the path is relative to experiments/ and must be the pilot output; the hash
must match the file on disk; U, E_U, WCC and E_WCC must be JSON integers equal to the pilot's sizes, and rho, q and
primary_mode the values that the rules of protocol section 7, applied by this code with the discovery
settings of this run, set from those sizes; the pilot must have set no stop flag, recorded every file
in COMMITTED as committed and the discovery settings of the overlay as they are, recorded its own
counts as its rule inputs, and recorded rules that the rules of this code give again from them. rho
and q are JSON numbers (or decimal strings) read as the decimal fractions they are written as. Only
when the run goes on after a refusal of protocol section 8 (a pilot output whose hash differs from the
pinned one, a pilot on other files, settings, inputs or code, or a t1 graph whose sizes differ from the
pilot's) or after a stop flag of section 7 does the object carry one more key, "author_decision" (a
non-empty string). rho, q and primary_mode are still the values the rules set, except that the author
chooses rho (0 < rho <= 1) when no rho is within the budget. Before any crawl, the t1 graph of the
gate B tables must have the sizes the pilot fixed (job 35 counts the same pairs), or the run stops
unless the author decided.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing
import os
import re
import subprocess
import sys
import time
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from datetime import date, datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

if __name__ == "__main__":
    os.environ.setdefault("CONTRACT_REP_VARIANT", "contract12m")
    # One thread per process: the sparse products are single-threaded and the results do not
    # depend on the number of workers.
    for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_var, "1")
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import common  # noqa: E402
import crawl  # noqa: E402

ROOT = common.ROOT
DISC = common.PROC / "discovery"
FEASIBILITY = DISC / "feasibility_t1.json"
PROTOCOL = ROOT / "docs" / "discovery_protocol.md"
STRUCT = common.GRAPH / "struct_t1"
COHORT_W0 = common.GRAPH_U12 / "cohort_t1"
LABELS_W0 = common.GRAPH_U12 / "labels_w0"
# The protocol, the revision, the overlay and the crawl code, with the modules the main runs read their inputs
# through (graphs.py loads the gate B tables under the variant's paths of common.py) and the base configuration,
# whose solver (reputation) and bootstrap (alignment) settings the main runs use.
COMMITTED = ("docs/discovery_protocol.md", "docs/revision_contract_graph.md", "config/overlay_contract12m.yaml",
             "scripts/crawl.py", "scripts/run_discovery.py", "scripts/scoring.py", "scripts/stats.py",
             "scripts/graphs.py", "scripts/common.py", "config/contract_reputation.yaml")
LAYERS = ("allow_capped", "allow_uncapped", "transfer")
UNION_LAYERS = ("allow_capped", "transfer")
USER_CLASSES = ("eoa", "eoa_7702", "smart_account")
# The columns of the account types the pilot reads, the kinds it counts and the number of largest code families.
TYPE_COLUMNS = ("address", "account_class", "wallet_kind", "proxy_kind", "code_hash", "code_size", "implementation",
                "entry_point")
TYPE_KINDS = ("account_class", "wallet_kind", "proxy_kind")
TOP_FAMILIES = 50
FIXED_KEYS = ("date", "feasibility", "sha256", "U", "E_U", "WCC", "E_WCC", "rho", "q", "primary_mode")
FINAL_TOLERANCE = 1e-9
IMPORTANCES = ("i_t", "i_a")
TARGET = {"i_t": "user-account inflow", "i_a": "user-authorised value"}
DEMAND = "user-account demand"
STRENGTH = ("V1", "V2", "V3")   # strongest first
LEAD = ("Ordered by C-PR on the contracts read so far, a crawl from a random contract of the giant strongly "
        "connected component")
NO_ANSWER = ("The question of the discovery-order test has no answer: an importance with too few hot contracts "
             "carries no verdict.")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _rel(path: Path) -> str:
    """``path`` relative to experiments/ when it lies there."""
    try:
        return Path(path).resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _git(*args: str, root: Path = ROOT) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True).stdout.strip()


def code_state(files: Sequence[str], root: Path = ROOT) -> dict[str, Any]:
    """HEAD, the SHA-256 of ``files`` and whether each is committed without local changes."""
    clean = {}
    for rel in files:
        try:
            clean[rel] = not _git("status", "--porcelain", "--", rel, root=root) and bool(
                _git("log", "-1", "--format=%H", "--", rel, root=root))
        except (OSError, subprocess.CalledProcessError):
            clean[rel] = False
    try:
        head = _git("rev-parse", "HEAD", root=root)
    except (OSError, subprocess.CalledProcessError):
        head = None
    return {"head": head, "sha256": {rel: sha256_file(root / rel) for rel in files if (root / rel).exists()},
            "committed": clean}


def committed(files: Sequence[str] = COMMITTED, root: Path = ROOT) -> dict[str, Any]:
    """Refuse unless every file is committed without local changes; return HEAD and their hashes."""
    state = code_state(files, root)
    bad = [rel for rel, ok in state["committed"].items() if not ok]
    if bad:
        raise SystemExit("refused: not committed without local changes: " + ", ".join(bad))
    return {"head": state["head"], "sha256": state["sha256"]}


# --------------------------------------------------------------------------- Protocol fixed


def protocol_fixed(path: Path = PROTOCOL) -> dict | None:
    """The JSON object of the section "Protocol fixed", or None while the section holds none."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    start = next((i for i, line in enumerate(lines) if re.match(r"## Protocol fixed\b", line)), None)
    if start is None:
        raise SystemExit(f"refused: {Path(path).name} has no section 'Protocol fixed'")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    section = "\n".join(lines[start + 1:end])
    block = re.search(r"^```json[ \t]*\n(.*?)\n```", section, flags=re.S | re.M)
    if block is None:
        return None
    try:
        value = json.loads(block.group(1))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"refused: the json block of 'Protocol fixed' does not parse: {exc}") from None
    if not isinstance(value, dict):
        raise SystemExit("refused: the json block of 'Protocol fixed' must hold one object")
    return value


def pilot_counts(pilot: dict[str, Any]) -> dict[str, Any] | None:
    """The counts the rules of protocol section 7 read, as the pilot itself reports them: its four sizes, the capped
    allowance edges between contracts and the share of SCC u OUT with a capped allowance in-edge (None if the pilot
    lacks one of them)."""
    try:
        return {**{k: int(pilot["sizes"][k]) for k in ("U", "E_U", "WCC", "E_WCC")},
                "allow_capped_edges": int(pilot["layers"]["allow_capped"]["edges"]),
                "allow_in_share": float(pilot["capped_allowance_in_edge_share"]["U"])}
    except (KeyError, TypeError, ValueError):
        return None


def check_fixed(block: dict | None, feasibility: Path = FEASIBILITY, root: Path = ROOT,
                discovery: dict[str, Any] | None = None) -> dict[str, Any]:
    """Validate the Protocol fixed object against the pilot output; return rho, q and the primary mode.

    rho, q and the primary mode must be the values that the rules of protocol section 7, as this code applies them
    with ``discovery`` (cfg["discovery"] of this run), set from the pilot's sizes, with or without an
    author_decision; only when no rho is within the budget does the author choose rho (protocol section 8). Unless
    the object carries an author_decision the runner also refuses (protocol section 8) a pilot output whose hash is
    not the pinned one, a pilot that set a stop flag (as recorded, or as the rules set it from the pilot's own
    counts), a pilot that ran on files that were not committed or with other discovery settings, a pilot whose
    recorded rule inputs are not its own counts, and a pilot whose recorded rules the rules of this code do not
    give from those inputs (the pilot of other code)."""
    if block is None:
        raise SystemExit("refused: docs/discovery_protocol.md has no filled section 'Protocol fixed' "
                         "(a json block, see the docstring of run_discovery.py)")
    keys = set(block)
    missing = sorted(set(FIXED_KEYS) - keys)
    extra = sorted(keys - set(FIXED_KEYS) - {"author_decision"})
    if missing or extra:
        raise SystemExit(f"refused: 'Protocol fixed' lacks {missing} or has unknown keys {extra}")
    try:
        date.fromisoformat(str(block["date"]))
    except ValueError:
        raise SystemExit("refused: 'Protocol fixed' needs a date YYYY-MM-DD") from None
    decision = block.get("author_decision")
    if decision is not None and not (isinstance(decision, str) and decision.strip()):
        raise SystemExit("refused: author_decision must be a non-empty string")
    expected = Path(feasibility).resolve().relative_to(Path(root).resolve()).as_posix()
    if block["feasibility"] != expected:
        raise SystemExit(f"refused: 'Protocol fixed' must name {expected}, not {block['feasibility']}")
    if not Path(feasibility).exists():
        raise SystemExit(f"refused: {expected} is missing")
    pinned, actual = str(block["sha256"]).lower(), sha256_file(feasibility)
    if pinned != actual:
        if decision is None:
            raise SystemExit(f"refused: the SHA-256 in 'Protocol fixed' does not match {expected}")
        print(f"warning: the SHA-256 in 'Protocol fixed' does not match {expected} (author_decision: {decision})")
    pilot = common.load_json(feasibility)
    sizes = pilot.get("sizes")
    if not isinstance(sizes, dict) or any(k not in sizes for k in ("U", "E_U", "WCC", "E_WCC")):
        raise SystemExit("refused: the structure pilot records no sizes U, E_U, WCC and E_WCC")
    for k in ("U", "E_U", "WCC", "E_WCC"):
        v = block[k]
        if not isinstance(v, int) or isinstance(v, bool) or v != sizes[k]:
            raise SystemExit(f"refused: 'Protocol fixed' gives {k} = {v!r}, the pilot {sizes[k]!r}")
    rules = pilot.get("rules")
    if discovery is None:
        raise SystemExit("refused: the discovery settings differ from those the structure pilot ran with (none "
                         "were given, so the rules of protocol section 7 cannot be applied)")
    counts = pilot_counts(pilot)
    # rho, q and the mode depend on the four sizes only; the stop counts enter the stop flags alone.
    expected = crawl.rules(counts or {**{k: int(pilot["sizes"][k]) for k in ("U", "E_U", "WCC", "E_WCC")},
                                      "allow_capped_edges": 0, "allow_in_share": 0.0}, discovery)

    def share(value: Any, name: str) -> Fraction:
        try:
            return crawl.decimal(value)
        except (TypeError, ValueError):
            raise SystemExit(f"refused: {name} = {value!r} is not a number") from None

    rho, q = share(block["rho"], "rho"), share(block["q"], "q")
    # The values the rules of section 7 set; an author's decision chooses rho only when none is within the budget.
    off = [name for name, ok in (
        ("rho", expected["rho"] is None or rho == share(expected["rho"], "the rules' rho")),
        ("q", q == share(expected["q"], "the rules' q")),
        ("the primary mode", block["primary_mode"] == expected["primary_mode"])) if not ok]
    if off:
        raise SystemExit(f"refused: {', '.join(off)} of 'Protocol fixed' differ from the values that the rules of "
                         "protocol section 7 set from the sizes of the structure pilot (an author_decision chooses "
                         "rho only when no rho is within the budget)")
    if decision is None:
        if (not isinstance(rules, dict) or rules.get("stopped") is not False or counts is None
                or expected["stopped"]):
            raise SystemExit("refused: the structure pilot stopped the run, or records no rules or no counts for "
                             "its stop flags; only an author_decision goes on")
        # The rules are those of committed code and of the settings the main runs use. A file of COMMITTED that
        # the pilot's record lacks counts as not committed, as in the driver's structure step.
        state = (pilot.get("code") or {}).get("committed") or {}
        dirty = sorted({rel for rel, ok in state.items() if ok is not True}
                       | ({rel for rel in COMMITTED if rel not in state} if state else set()))
        if not state or dirty:
            raise SystemExit("refused: the structure pilot did not run on committed files "
                             f"({', '.join(dirty) or 'no record'}); only an author_decision goes on")
        if discovery is None or json.loads(json.dumps(_clean(discovery))) != pilot.get("discovery_config"):
            raise SystemExit("refused: the discovery settings differ from those the structure pilot ran with; only "
                             "an author_decision goes on")
        # The pilot's rules must be those of this code: computed again from the counts the pilot recorded.
        inputs = pilot.get("rule_inputs")
        if not isinstance(inputs, dict) or any(inputs.get(k) != v for k, v in counts.items()):
            raise SystemExit("refused: the structure pilot records no rule inputs, or rule inputs other than its "
                             "own counts (its sizes, capped allowance edges and capped allowance in-edge share); "
                             "only an author_decision goes on")
        if json.loads(json.dumps(_clean(crawl.rules(inputs, discovery)))) != rules:
            raise SystemExit("refused: the rules of this code give other values than the structure pilot recorded "
                             "from the same inputs, so the pilot ran other code; only an author_decision goes on")
    if not (0 < rho <= 1 and 0 < q <= 1 and block["primary_mode"] in crawl.MODES):
        raise SystemExit("refused: rho and q must lie in (0, 1] and the mode be out or both")
    return {"date": str(block["date"]), "rho": rho, "q": q, "primary_mode": block["primary_mode"],
            "author_decision": decision, "feasibility_sha256": actual, "pinned_sha256": pinned,
            "sizes": {k: int(block[k]) for k in ("U", "E_U", "WCC", "E_WCC")}}


# --------------------------------------------------------------------------- structure pilot


def _hex(values: Any) -> list[str]:
    """Addresses as lowercase 0x hex, from 20-byte binary values or from strings."""
    values = pd.Series(values)
    if values.empty:
        return []
    if isinstance(values.iloc[0], (bytes, bytearray, memoryview)):
        return ["0x" + bytes(v).hex() for v in values]
    return values.astype(str).str.lower().tolist()


def _is_system(address: str, top: int) -> bool:
    return int(address, 16) <= top


def _type_frame(types: pd.DataFrame) -> pd.DataFrame:
    """The account types with lowercase 0x addresses and the text columns as strings ("" where empty)."""
    out = pd.DataFrame({"address": _hex(types["address"])}, index=range(len(types)))
    for col in TYPE_COLUMNS[1:]:
        if col == "code_size":
            out[col] = pd.to_numeric(types[col].reset_index(drop=True), errors="coerce")
            continue
        v = types[col].reset_index(drop=True).astype(object)
        out[col] = v.where(v.notna(), "").astype(str)
    for col in ("code_hash", "implementation", "entry_point"):
        out[col] = out[col].str.lower()
    return out


def _counts(values: pd.Series) -> dict[str, int]:
    return {str(k): int(v) for k, v in values.value_counts().sort_index().items()}


def account_types(types: pd.DataFrame, nodes: Sequence[str]) -> dict[str, Any]:
    """Counts by account class, wallet kind and proxy kind over every row of the types (the queue) and over the
    nodes of the union graph (an address without a type row counts as "untyped"; an empty value as "")."""
    t = _type_frame(types)
    first = t.drop_duplicates("address").set_index("address")
    sub = first.reindex(list(nodes))
    untyped = sub["account_class"].isna()
    sub = sub.loc[:, list(TYPE_KINDS)].astype(object)
    sub.loc[untyped.to_numpy(), :] = "untyped"
    return {
        "queue": {"rows": int(len(t)), **{k: _counts(t[k]) for k in TYPE_KINDS}},
        "union_nodes": {"nodes": int(len(sub)), "untyped": int(untyped.sum()),
                        **{k: _counts(sub[k]) for k in TYPE_KINDS}},
    }


def _most_frequent(values: pd.Series) -> Any:
    """The most frequent value, a tie to the lowest; None when there is none."""
    vc = values.dropna().value_counts()
    if vc.empty:
        return None
    return min(vc.index[vc == vc.max()].tolist())


def code_families(types: pd.DataFrame, nodes: Sequence[str], canonical: Sequence[str],
                  top: int = TOP_FAMILIES) -> dict[str, Any]:
    """The code families of revision section 13 among the union-graph nodes whose class is contract.

    largest: the ``top`` largest groups by code hash (a tie to the lower hash); canonical_entry_point: every group
    with a member whose entry_point is a canonical EntryPoint. Each group gives its size n, the most frequent code
    size and proxy kind, the most frequent non-empty implementation ("" if none) and the count of every
    entry_point answer ("" included); a canonical group also gives n_canonical, its members with such an answer.
    """
    t = _type_frame(types).drop_duplicates("address")
    t = t[t["address"].isin(set(nodes)) & (t["account_class"] == "contract")]
    canon = {str(c).lower() for c in canonical}
    t = t.assign(canonical=t["entry_point"].isin(canon))
    sizes = t.groupby("code_hash", sort=True).size()
    order = sorted(sizes.items(), key=lambda kv: (-int(kv[1]), str(kv[0])))
    hit = set(t.loc[t["canonical"], "code_hash"])
    wanted = {h for h, _ in order[:top]} | hit
    members = {h: g for h, g in t[t["code_hash"].isin(wanted)].groupby("code_hash", sort=True)}

    def family(h: str) -> dict[str, Any]:
        g = members[h]
        size = _most_frequent(g["code_size"])
        impl = _most_frequent(g.loc[g["implementation"] != "", "implementation"])
        return {"code_hash": h, "n": int(len(g)), "code_size": None if size is None else int(size),
                "proxy_kind": _most_frequent(g["proxy_kind"]), "implementation": impl or "",
                "entry_points": _counts(g["entry_point"])}

    return {
        "contracts": int(len(t)), "groups": int(sizes.size),
        "largest": [family(h) for h, _ in order[:top]],
        "canonical_entry_point": [{**family(h), "n_canonical": int(members[h]["canonical"].sum())}
                                  for h, _ in order if h in hit],
    }


def feasibility(cfg: dict[str, Any], struct: pd.DataFrame, types: pd.DataFrame, cohort: Sequence[str],
                spenders: Sequence[str]) -> dict[str, Any]:
    """Every item of protocol section 7 from the structure table, the account types and the W0 lists."""
    d = cfg["discovery"]
    s = pd.DataFrame({"a": _hex(struct["a"]), "b": _hex(struct["b"]), "layer": struct["layer"].astype(str)})
    unknown = sorted(set(s["layer"]) - set(LAYERS))
    if unknown:
        raise SystemExit(f"struct_t1 has unknown layers {unknown}")
    rows = len(s)
    s = s.drop_duplicates(ignore_index=True)
    loop = (s["a"] == s["b"]).to_numpy()
    self_loops = {lay: int((loop & (s["layer"] == lay).to_numpy()).sum()) for lay in LAYERS}
    s = s[~loop].reset_index(drop=True)
    # Node ids in address order.
    codes, uniques = pd.factorize(pd.concat([s["a"], s["b"]], ignore_index=True), sort=True)
    addresses = np.asarray(uniques, dtype=object)
    n = addresses.size
    a, b = codes[: len(s)].astype(np.int64), codes[len(s):].astype(np.int64)
    layer = s["layer"].to_numpy(dtype=object)
    node = {}
    layers = {}
    for lay in LAYERS:
        m = layer == lay
        node[lay] = np.zeros(n, dtype=bool)
        node[lay][a[m]] = True
        node[lay][b[m]] = True
        layers[lay] = {"edges": int(m.sum()), "nodes": int(node[lay].sum()), "self_loops": self_loops[lay]}
    mu = np.isin(layer, UNION_LAYERS)
    bt = crawl.bow_tie(n, a[mu], b[mu])
    sizes = bt.sizes()
    in_u = bt.scc | bt.out
    capped = layer == "allow_capped"
    has_in = np.zeros(n, dtype=bool)
    has_in[b[capped]] = True
    has_in_u = np.zeros(n, dtype=bool)
    has_in_u[b[capped & in_u[a]]] = True
    # The share of SCC u OUT with a capped allowance in-edge (the stop rule of section 7).
    n_u = max(int(in_u.sum()), 1)
    share_in = float(has_in[in_u].sum() / n_u)
    within = {"U": in_u, "WCC": bt.wcc}
    part_edges = {k: {lay: int(((layer == lay) & m[a] & m[b]).sum()) for lay in LAYERS} for k, m in within.items()}

    cls = pd.Series(types["account_class"].astype(str).to_numpy(), index=_hex(types["address"]))
    cls = cls[~cls.index.duplicated()]
    top = int(cfg["contract_graph"]["system_address_max"])
    node_cls = cls.reindex(list(addresses))
    node_types = {str(k): int(v) for k, v in node_cls.fillna("untyped").value_counts().sort_index().items()}

    index = pd.Index(addresses)

    def coverage(members: Sequence[str]) -> dict[str, Any]:
        m = sorted(set(_hex(members)))
        c = cls.reindex(m)
        contracts = [x for x, k in zip(m, c) if k == "contract" and not _is_system(x, top)]
        pos = index.get_indexer(contracts)
        pos = pos[pos >= 0]
        masks = {**node, "union": ~bt.isolated, "U": in_u, "WCC": bt.wcc}
        k = max(len(contracts), 1)
        return {
            "members": len(m), "contracts": len(contracts),
            "user_accounts": int(c.isin(USER_CLASSES).sum()), "untyped": int(c.isna().sum()),
            "covered": {key: {"n": int(mask[pos].sum()), "share": float(mask[pos].sum() / k)}
                        for key, mask in masks.items()},
        }

    union_nodes = list(addresses[~bt.isolated])
    entry_points = cfg["contract_graph"]["entry_points"]
    canonical = list(entry_points.values()) if isinstance(entry_points, dict) else list(entry_points)

    rule_sizes = {k: int(sizes[k]) for k in ("U", "E_U", "WCC", "E_WCC")}
    rule_sizes.update(allow_capped_edges=layers["allow_capped"]["edges"], allow_in_share=share_in)
    rules = crawl.rules(rule_sizes, d)
    return {
        "window": "t1",
        # Top-level copies of the sizes and the rule outputs, for the driver's run manifest.
        **{k: rule_sizes[k] for k in ("U", "E_U", "WCC", "E_WCC")},
        **{k: rules[k] for k in ("rho", "q", "primary_mode", "stopped")},
        "struct_rows": rows, "duplicate_rows": rows - len(s) - int(loop.sum()),
        "layers": layers,
        "union": {"layers": list(UNION_LAYERS), "nodes": sizes["nodes"], "edges": sizes["edges"]},
        "bow_tie": {k: sizes[k] for k in ("scc", "in", "out", "other")},
        "sizes": {k: sizes[k] for k in ("U", "E_U", "WCC", "E_WCC")},
        "layer_edges_within": part_edges,
        "capped_allowance_in_edge_share": {"U": share_in, "U_from_U": float(has_in_u[in_u].sum() / n_u)},
        "node_types": node_types,
        "system_addresses": int(sum(_is_system(x, top) for x in addresses)),
        "coverage": {"w0_cohort": coverage(cohort), "w0_spenders": coverage(spenders)},
        "account_types": account_types(types, union_nodes),
        "code_families": code_families(types, union_nodes, canonical),
        "rules": rules,
        "rule_inputs": rule_sizes,
        "discovery_config": d,
    }


def run_feasibility(cfg: dict[str, Any], *, struct: Path = STRUCT, types: Path = common.TYPES,
                    cohort: Path = COHORT_W0, labels: Path = LABELS_W0, out: Path = FEASIBILITY,
                    protocol: Path = PROTOCOL, root: Path = ROOT) -> dict[str, Any]:
    """Read the pilot inputs, write the pilot output; refuses once the protocol is fixed."""
    if protocol_fixed(protocol) is not None:
        raise SystemExit("refused: the protocol is fixed, so feasibility_t1.json is pinned by its hash")
    started = time.perf_counter()
    report = feasibility(
        cfg,
        common.read_parts(struct, ["a", "b", "layer"]),
        common.read_parts(types, list(TYPE_COLUMNS)),
        _hex(common.read_parts(cohort, ["address"])["address"]),
        _hex(common.read_parts(labels, ["wallet"])["wallet"]),
    )
    report["created_at"] = now()
    report["seconds"] = round(time.perf_counter() - started, 1)
    report["code"] = code_state(COMMITTED, root)
    common.save_json(_clean(report), out)
    return report


# --------------------------------------------------------------------------- crawl tasks


@dataclass(frozen=True)
class Task:
    seed_index: int   # 0 = the seed with the lowest hash
    seed: int         # node id in the universe graph
    ordering: str
    rho: str          # exact fraction, e.g. "1/100"


_WORKER: dict[str, Any] = {}


def _init_worker(graph: crawl.CrawlGraph, mode: str, cfg: dict[str, Any], params: dict[str, Any],
                 refs: dict[str, np.ndarray], grid: np.ndarray) -> None:
    _WORKER.clear()
    _WORKER.update(graph=graph, adj=crawl.Adjacency.build(graph, mode), mode=mode, cfg=cfg, params=params,
                   refs=refs, grid=grid)


def _run_task(task: Task) -> dict[str, Any]:
    w = _WORKER
    g = w["graph"]
    c = crawl.Crawl(g, task.seed, task.ordering, mode=w["mode"], rho=task.rho, cfg=w["cfg"],
                    params=w["params"], adjacency=w["adj"])
    r = c.run()
    final = None
    if task.ordering in crawl.WALKS:
        got = crawl.dense(c.final_scores(), g.n)
        final = float(np.max(np.abs(got - w["refs"][task.ordering]))) if g.n else 0.0
    grid = w["grid"]
    cum = np.cumsum(r.edges_read)
    cost = cum[np.minimum(grid, r.visits) - 1] / max(g.union_src.size, 1) if r.visits else np.zeros(grid.size)
    return {"visit_index": r.visit_index.astype(np.int32), "visits": r.visits, "recomputes": r.recomputes,
            "iterations": r.iterations, "solves": r.solves, "tied": r.tied, "picks": max(r.visits - 1, 0),
            "cost": cost, "seconds": r.seconds, "final_diff": final,
            "batches_ok": bool(r.batch_sizes.sum() == r.visits - 1)}


def run_crawls(graph: crawl.CrawlGraph, tasks: Sequence[Task], *, mode: str, cfg: dict[str, Any],
               params: dict[str, Any], refs: dict[str, np.ndarray], grid: np.ndarray,
               workers: int = 1) -> dict[Task, dict[str, Any]]:
    """Every task, in this process (workers <= 1) or in a spawned process pool; same results either way."""
    args = (graph, mode, cfg, params, refs, grid)
    if workers <= 1 or len(tasks) < 2:
        _init_worker(*args)
        return {t: _run_task(t) for t in tasks}
    with ProcessPoolExecutor(max_workers=min(workers, len(tasks)), mp_context=multiprocessing.get_context("spawn"),
                             initializer=_init_worker, initargs=args) as pool:
        return dict(zip(tasks, pool.map(_run_task, tasks, chunksize=1)))


def _task_weight(ordering: str) -> int:
    """Heavier crawls first, so that the pool ends together."""
    return {"spr": 0}.get(ordering, 1 if ordering in crawl.WALKS else 2)


# --------------------------------------------------------------------------- measures


class Measures:
    """AUCs, intervals and contrasts over the hot sets of one run (protocol section 6)."""

    def __init__(self, n: int, visits: dict[tuple[str, str], np.ndarray], hot: dict[str, np.ndarray],
                 n_boot: int, seed: int, ci: float = 0.95):
        import stats

        self.stats, self.n, self.visits, self.hot = stats, n, visits, hot
        self.n_boot, self.seed, self.ci = n_boot, seed, ci
        self._idx: dict[int, np.ndarray] = {}

    def idx(self, size: int) -> np.ndarray:
        if size not in self._idx:
            self._idx[size] = self.stats.resample_matrix(size, self.n_boot, self.seed)
        return self._idx[size]

    def t(self, key: tuple[str, str], hot: str, seeds: slice | None = None) -> np.ndarray:
        v = self.visits[key]
        if seeds is not None:
            v = v[seeds]
        return v[:, self.hot[hot]]

    def g(self, key: tuple[str, str], hot: str, x: Any, seeds: slice | None = None) -> np.ndarray:
        """g-bar_x of every hot contract: g_x averaged over seeds."""
        return crawl.visit_scores(self.t(key, hot, seeds), self.n, x).mean(axis=0)

    def per_seed(self, key: tuple[str, str], hot: str, x: Any, seeds: slice | None = None) -> np.ndarray:
        return crawl.visit_scores(self.t(key, hot, seeds), self.n, x).mean(axis=1)

    def auc(self, key: tuple[str, str], hot: str, x: Any, seeds: slice | None = None) -> dict[str, Any]:
        h = int(self.hot[hot].size)
        if h == 0:
            return {"auc": None, "n_hot": 0}
        gbar = self.g(key, hot, x, seeds)
        per = self.per_seed(key, hot, x, seeds)
        lo, hi = self.stats.percentile_ci(gbar[self.idx(h)].mean(axis=1), self.ci)
        t = self.t(key, hot, seeds)
        return {"auc": float(gbar.mean()), "lo": lo, "hi": hi, "n_hot": h, "per_seed": per.tolist(),
                "seed_sd": float(per.std(ddof=1)) if per.size > 1 else None,
                "seed_min": float(per.min()), "seed_max": float(per.max()),
                "visits_50": crawl.visits_to_reach(t, 0.5).tolist(), "visits_90": crawl.visits_to_reach(t, 0.9).tolist()}

    def contrast(self, a: tuple[str, str], b: tuple[str, str], hot: str, x: Any,
                 seeds: slice | None = None) -> dict[str, Any]:
        h = int(self.hot[hot].size)
        if h == 0:
            return {"point": None, "lo": None, "hi": None, "share_positive": None, "n": 0}
        return self.stats.paired_mean_contrast(self.g(a, hot, x, seeds), self.g(b, hot, x, seeds), self.idx(h),
                                               self.ci)

    def seed_contrast(self, a: tuple[str, str], b: tuple[str, str], hot: str, x: Any) -> dict[str, Any]:
        """The same contrast with a bootstrap over seeds (per-seed AUCs)."""
        if self.hot[hot].size == 0:
            return {"point": None, "lo": None, "hi": None, "share_positive": None, "n": 0}
        pa, pb = self.per_seed(a, hot, x), self.per_seed(b, hot, x)
        return self.stats.paired_mean_contrast(pa, pb, self.idx(pa.size), self.ci)


def _above(d: dict[str, Any]) -> bool:
    return d.get("lo") is not None and d["lo"] > 0


def _below(d: dict[str, Any]) -> bool:
    return d.get("hi") is not None and d["hi"] < 0


def secondary_share(q: Fraction, d: dict[str, Any]) -> Fraction:
    """The secondary share of protocol section 6: the other of the two shares, q_secondary when q is q_primary and
    q_primary when q is q_small."""
    small = crawl.decimal(q) == crawl.decimal(d["q_small"])
    return crawl.decimal(d["q_primary"]) if small else crawl.decimal(d["q_secondary"])


def verdict(d1: dict[str, Any], d2: dict[str, Any], n_hot: int, min_hot: int) -> dict[str, Any]:
    """V1, V2 or V3 of protocol section 6 and the sentences an interval below 0 adds."""
    if n_hot < min_hot:
        return {"verdict": None, "descriptive": True, "extra": []}
    code = "V1" if _above(d1) and _above(d2) else "V2" if _above(d1) else "V3"
    extra = []
    if _below(d1):
        extra.append("A breadth-first crawl reached them sooner.")
    if _below(d2):
        extra.append("A crawl ordered by the number of contract backlinks reached them sooner.")
    return {"verdict": code, "descriptive": False, "extra": extra}


def _sentence(code: str, what: str) -> str:
    if code == "V1":
        return (f"{LEAD} reached the contracts of the universe with the most {what} sooner than a breadth-first "
                "crawl and than a crawl ordered by the number of contract backlinks.")
    if code == "V2":
        return (f"{LEAD} reached the contracts of the universe with the most {what} sooner than a breadth-first "
                "crawl, but not sooner than a crawl ordered by the number of contract backlinks.")
    return (f"{LEAD} did not reach the contracts of the universe with the most {what} sooner than a breadth-first "
            "crawl.")


def statements(decisions: dict[str, dict[str, Any]]) -> list[str]:
    """The verdict wording of protocol section 6. The two importances are stated once when their verdicts and added
    sentences agree, and separately otherwise; stated separately, they are followed by the answer to the question
    of section 1, the weaker verdict (V2 weaker than V1, V3 than V2) for user-account demand. An importance with
    too few hot contracts is descriptive only, and the question then has no answer."""
    given = {k: v for k, v in decisions.items() if not v["descriptive"]}
    out = []
    keys = list(given)
    if len(keys) == 2 and (given[keys[0]]["verdict"], given[keys[0]]["extra"]) == (
            given[keys[1]]["verdict"], given[keys[1]]["extra"]):
        what = f"{TARGET[keys[0]]} and those with the most {TARGET[keys[1]]}"
        out.append(" ".join([_sentence(given[keys[0]]["verdict"], what), *given[keys[0]]["extra"]]))
    else:
        for k, v in given.items():
            out.append(" ".join([_sentence(v["verdict"], TARGET[k]), *v["extra"]]))
        if len(keys) == 2:
            weaker = max((v["verdict"] for v in given.values()), key=STRENGTH.index)
            out.append(f"Over both importances, the weaker verdict: {_sentence(weaker, DEMAND)}")
    for k, v in decisions.items():
        if v["descriptive"]:
            out.append(f"Fewer than the minimum number of hot contracts for {TARGET[k]}: descriptive only.")
    if len(given) < len(decisions):
        out.append(NO_ANSWER)
    return out


# --------------------------------------------------------------------------- main runs


def full_graph(nodes: pd.DataFrame, allow: pd.DataFrame, transfer: pd.DataFrame) -> tuple[crawl.CrawlGraph, np.ndarray]:
    """The contract graph on positions 0..N-1 (node ids in increasing order) and the node id of each."""
    nodes = nodes.sort_values("id", ignore_index=True)
    ids = nodes["id"].to_numpy(dtype=np.int64)
    if np.unique(ids).size != ids.size:
        raise SystemExit("nodes repeats an id")

    def pos(col: pd.Series) -> np.ndarray:
        v = col.to_numpy(dtype=np.int64)
        p = np.searchsorted(ids, v)
        if v.size and ((p >= ids.size).any() or (ids[np.minimum(p, ids.size - 1)] != v).any()):
            raise SystemExit("a pair names a node id that nodes lacks")
        return p

    def layer(df: pd.DataFrame, weights: Sequence[str]) -> crawl.Layer:
        return crawl.Layer(pos(df["src"]), pos(df["dst"]), {w: df[w].to_numpy(dtype=np.float64) for w in weights})

    try:
        graph = crawl.CrawlGraph(nodes["address"].astype(str).str.lower().to_numpy(dtype=object),
                                 layer(allow, crawl.ALLOW_WEIGHTS), layer(transfer, crawl.TRANSFER_WEIGHTS))
    except ValueError as exc:
        raise SystemExit(f"the gate B tables do not form a crawl graph: {exc}") from None
    return graph, ids


def _round(a: np.ndarray, digits: int = 6) -> list:
    return [None if not np.isfinite(x) else round(float(x), digits) for x in np.asarray(a, dtype=np.float64)]


def _band(rows: np.ndarray) -> dict[str, list]:
    rows = np.atleast_2d(rows)
    return {"mean": _round(rows.mean(axis=0)), "min": _round(rows.min(axis=0)), "max": _round(rows.max(axis=0))}


def _clean(obj: Any) -> Any:
    """JSON-ready: numpy scalars and arrays to Python, NaN and infinities to None, fractions to strings."""
    if isinstance(obj, dict):
        return {str(k): _clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_clean(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return _clean(obj.tolist())
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, (float, np.floating)):
        return float(obj) if np.isfinite(obj) else None
    if isinstance(obj, Fraction):
        return str(obj)
    return obj


def _positions(ids: np.ndarray, values: np.ndarray) -> np.ndarray:
    """Position of each value in the sorted ``ids``, -1 where it is missing."""
    p = np.searchsorted(ids, values)
    hit = (p < ids.size) & (ids[np.minimum(p, max(ids.size - 1, 0))] == values) if ids.size else p < 0
    return np.where(hit, p, -1)


IMPORTANCE_COLUMNS = ("id", "i_t", "i_a", "n_t", "n_a")
OUTSIDE_G = -1   # the node id of a typed contract that is not a node of G (importance_{tag})
NOT_DECIDING = "outside the decision (protocol section 6)"


def importance_positions(ids: np.ndarray, imp: pd.DataFrame) -> np.ndarray:
    """Position in the sorted node ids of every row of importance_{tag}, -1 for a contract outside G.

    The table holds every typed contract with a positive I_T or I_A, with its node id when it is a node of G and
    -1 otherwise (protocol section 8). A node id that nodes lacks, a node of G listed twice or a negative or
    non-finite importance stops the run.
    """
    missing = sorted(set(IMPORTANCE_COLUMNS) - set(imp.columns))
    if missing:
        raise SystemExit(f"importance lacks the columns {missing}")
    if (ids == OUTSIDE_G).any():
        raise SystemExit(f"nodes uses the id {OUTSIDE_G}, which importance reserves for contracts outside G")
    v = imp["id"].to_numpy(dtype=np.int64)
    p = _positions(ids, v)
    if ((p < 0) & (v != OUTSIDE_G)).any():
        raise SystemExit(f"importance names a node id that nodes lacks (contracts outside G carry {OUTSIDE_G})")
    if np.unique(v[p >= 0]).size != int((p >= 0).sum()):
        raise SystemExit("importance lists a node of G twice")
    for col in IMPORTANCE_COLUMNS[1:]:
        x = imp[col].to_numpy(dtype=np.float64)
        if not np.isfinite(x).all() or (x < 0).any():
            raise SystemExit(f"importance.{col} must be finite and non-negative")
    return p


def read_inflow_untyped(tag: str) -> float:
    """inflow_untyped_{tag}: the one-row table of the US dollars that user accounts sent to untyped addresses of E
    (an empty sum, NULL, is 0)."""
    df = common.read_parts(common.GRAPH / f"inflow_untyped_{tag}", ["usd"])
    if len(df) != 1:
        raise SystemExit(f"inflow_untyped_{tag} must hold one row, not {len(df)}")
    usd = df["usd"].iloc[0]
    usd = 0.0 if pd.isna(usd) else float(usd)
    if not np.isfinite(usd) or usd < 0:
        raise SystemExit(f"inflow_untyped_{tag}.usd must be finite and non-negative")
    return usd


def top_share(values: np.ndarray, member: np.ndarray, share: Any) -> dict[str, Any]:
    """The share of the top ceil(share x rows) rows by ``values`` (ceil computed exactly) that lies in ``member``.

    The top holds exactly that many rows. When the rows tied at the cut value do not all fit, each tied row takes
    the same fraction of the slots left, so that the result does not depend on the order of the rows.
    """
    x = np.asarray(values, dtype=np.float64)
    k = crawl.ceil_share(share, x.size)
    if k == 0:
        return {"rows": 0, "share_in_U": None, "tied_at_cut": 0, "slots_at_cut": 0}
    cut = np.partition(x, x.size - k)[x.size - k]
    above, tied = x > cut, x == cut
    slots = k - int(above.sum())
    held = float((above & member).sum()) + slots * float((tied & member).sum()) / float(tied.sum())
    return {"rows": k, "share_in_U": held / k, "tied_at_cut": int(tied.sum()), "slots_at_cut": slots}


def coverage(full: crawl.CrawlGraph, ids: np.ndarray, bt: crawl.BowTie, universe: np.ndarray,
             imp: pd.DataFrame, inflow_untyped: float) -> dict[str, Any]:
    """The coverage diagnostics of protocol section 6 over every row of importance_{tag}.

    For I_T and I_A: the share of the sum held by U (the universe of the mode), by each part of the bow-tie of G
    (SCC, IN, OUT, other, and the nodes of G without a union edge) and by the contracts outside G (id -1), which
    together make 1; and the share of the top 1% of rows that lies in U. inflow_untyped is reported as a value.
    """
    p = importance_positions(ids, imp)
    in_g = p >= 0
    p = np.where(in_g, p, 0)
    in_u = np.zeros(full.n, dtype=bool)
    in_u[universe] = True
    member = in_g & in_u[p]
    parts = {"scc": bt.scc, "in": bt.in_, "out": bt.out, "other": bt.other, "isolated": bt.isolated}
    label = np.full(p.size, "outside_g", dtype=object)
    for name, mask in parts.items():
        label[in_g & mask[p]] = name
    out: dict[str, Any] = {"contracts": int(p.size), "outside_g": int((~in_g).sum())}
    for col in IMPORTANCES:
        x = imp[col].to_numpy(dtype=np.float64)
        total = x.sum()
        out[col] = {
            "total": float(total),
            "share_U": float(x[member].sum() / total) if total > 0 else None,
            "share_by_part": {k: float(x[label == k].sum() / total) if total > 0 else None
                              for k in (*parts, "outside_g")},
            "top_1pct": top_share(x, member, Fraction(1, 100)),
        }
    out["inflow_untyped_usd"] = float(inflow_untyped)
    return out


def graph_sizes(tag: str) -> dict[str, Any]:
    """The bow-tie sizes (U, E_U, WCC, E_WCC, ...) of the contract graph of one freeze from the gate B tables."""
    import graphs

    g = graphs.load_graphs(tag)
    full, _ = full_graph(graphs.load_nodes(), g.allow, g.transfer)
    return crawl.bow_tie(full.n, full.union_src, full.union_dst).sizes()


def match_pilot(sizes: dict[str, Any], fixed: dict[str, Any]) -> dict[str, bool]:
    """Compare the t1 graph with the sizes the structure pilot fixed: job 35 counts the same pairs as the gate B
    tables, so they must agree; a difference stops the run unless 'Protocol fixed' carries an author_decision."""
    pilot = fixed.get("sizes") or {}
    match = {k: int(sizes[k]) == int(v) for k, v in pilot.items()}
    if not all(match.values()):
        msg = f"the t1 graph differs from the structure pilot: {pilot} against { {k: sizes[k] for k in pilot} }"
        if not fixed.get("author_decision"):
            raise SystemExit(f"refused: {msg}; only an author_decision in 'Protocol fixed' goes on")
        print(f"warning: {msg} (author_decision: {fixed['author_decision']})")
    return match


def run_window(tag: str, mode: str, fixed: dict[str, Any], provenance: dict[str, Any], cfg: dict[str, Any],
               workers: int) -> Path:
    """One main run: every crawl of one freeze in one reveal mode, the measures and the outputs."""
    import graphs
    from scoring import pagerank_params

    d = cfg["discovery"]
    params = pagerank_params(cfg)
    lambdas = sorted(crawl.decimal(x) for x in d["lambda_grid"])
    if crawl.decimal(d["lambda_primary"]) != Fraction(1, 2) or lambdas != [Fraction(1, 4), Fraction(3, 4)]:
        raise SystemExit("the lambdas of the overlay differ from the walks cpr_l25, cpr_l50 and cpr_l75")
    started = time.perf_counter()
    primary = mode == fixed["primary_mode"]
    # The decision is read at T_obs in the primary mode only; every other run reports without a verdict.
    decides = tag == "tobs" and primary
    rho = fixed["rho"]
    q = fixed["q"]
    x_all = [float(d["x_primary"]), *(float(x) for x in d["x_secondary"])]
    x1 = float(d["x_primary"])

    nodes = graphs.load_nodes()
    g = graphs.load_graphs(tag)
    imp = common.read_parts(common.GRAPH / f"importance_{tag}")
    inflow_untyped = read_inflow_untyped(tag)
    full, ids = full_graph(nodes, g.allow, g.transfer)
    importance_positions(ids, imp)  # the checks of the table, before any crawl
    bt = crawl.bow_tie(full.n, full.union_src, full.union_dst)
    sizes = bt.sizes()
    pilot = fixed.get("sizes") or {}
    pilot_match = match_pilot(sizes, fixed) if tag == "t1" else None
    universe = bt.universe(mode)
    gu, pos_u = full.restrict(universe)
    n = gu.n
    node_ids = ids[pos_u]
    seeds = crawl.pick_seeds(gu.address, np.flatnonzero(bt.scc[pos_u]), int(d["n_seeds"]), d["seed_salt"])
    print(f"{tag} {mode}: |U| = {n:,}, |E_U| = {gu.union_src.size:,}, {seeds.size} seeds, rho = {rho}")

    # Importance on U (contracts without a row hold 0; the rows outside G, id -1, are in no universe) and the
    # importances in the manner of Cho et al.
    p = _positions(node_ids, imp["id"].to_numpy(dtype=np.int64))
    hit = p >= 0
    values = {}
    for col in ("i_t", "i_a", "n_t", "n_a"):
        v = np.zeros(n)
        v[p[hit]] = imp[col].to_numpy(dtype=np.float64)[hit]
        values[col] = v
    refs = {m: crawl.full_scores(gu, m, params) for m in crawl.WALKS}
    values["ib_u"] = gu.union_in_degree().astype(np.float64)
    values["ir"] = refs["cpr_l50"]
    hub_ids = crawl.hubs(values["ib_u"], d)
    q2 = secondary_share(q, d)
    hot: dict[str, np.ndarray] = {}
    for col in values:
        hot[f"{col}@q"] = np.flatnonzero(crawl.hot_set(values[col], q))
    for col in IMPORTANCES:
        hot[f"{col}@q2"] = np.flatnonzero(crawl.hot_set(values[col], q2))
        hot[f"{col}@q-nohubs"] = crawl.without_hubs(hot[f"{col}@q"], hub_ids)

    # Crawls: every ordering on every seed at rho; with the primary mode, rho/4 on the first seeds.
    rho_key = str(rho)
    rho4 = rho / int(d["rho_sensitivity"]["divisor"])
    n4 = int(d["rho_sensitivity"]["seeds"])
    grid = crawl.curve_grid(n, int(d["curve_points"]))
    tasks = [Task(i, int(s), o, rho_key) for i, s in enumerate(seeds) for o in crawl.ORDERINGS]
    if primary:
        tasks += [Task(i, int(s), o, str(rho4)) for i, s in enumerate(seeds[:n4]) for o in crawl.ORDERINGS]
    tasks.sort(key=lambda t: (_task_weight(t.ordering), t.rho != rho_key, t.ordering, t.seed_index))
    results = run_crawls(gu, tasks, mode=mode, cfg=d, params=params, refs=refs, grid=grid, workers=workers)

    # Invariants.
    failures = []
    for t, r in results.items():
        if r["visits"] != n or not (r["visit_index"] > 0).all():
            failures.append(f"{t.ordering} seed {t.seed_index} rho {t.rho}: visited {r['visits']} of {n}")
        if not r["batches_ok"]:
            failures.append(f"{t.ordering} seed {t.seed_index} rho {t.rho}: batches do not add up")
        if r["final_diff"] is not None and not r["final_diff"] <= FINAL_TOLERANCE:
            failures.append(f"{t.ordering} seed {t.seed_index} rho {t.rho}: final walk differs by {r['final_diff']:.3g}")
    if failures:
        raise SystemExit("invariants failed:\n  " + "\n  ".join(failures))

    def matrix(o: str, r: str) -> np.ndarray:
        rows = sorted(((t.seed_index, t) for t in results if t.ordering == o and t.rho == r), key=lambda x: x[0])
        return np.vstack([results[t].pop("visit_index") for _, t in rows])

    visits = {(o, rho_key): matrix(o, rho_key) for o in crawl.ORDERINGS}
    if primary:
        visits.update({(o, str(rho4)): matrix(o, str(rho4)) for o in crawl.ORDERINGS})
    # References that are not crawls: the order by full-graph C-PR, by union in-degree, and the ideal
    # order of each hot set (its contracts first, by decreasing importance).
    visits[("ref_cpr", "")] = crawl.rank_order(refs["cpr_l50"]).astype(np.int32)[None, :]
    visits[("ref_ib_u", "")] = crawl.rank_order(values["ib_u"]).astype(np.int32)[None, :]
    for h, members in hot.items():
        mask = np.zeros(n, dtype=bool)
        mask[members] = True
        visits[(f"ref_ideal:{h}", "")] = crawl.ideal_order(values[h.split("@")[0]], mask).astype(np.int32)[None, :]
    al = cfg["alignment"]
    ms = Measures(n, visits, hot, int(al["bootstrap_resamples"]), int(al["bootstrap_seed"]))

    def key(o: str) -> tuple[str, str]:
        return (o, rho_key)

    # AUC of every ordering and reference on every hot set and x.
    aucs: dict[str, Any] = {}
    for h in hot:
        aucs[h] = {}
        for o in (*crawl.ORDERINGS, "ref_cpr", "ref_ib_u", "ref_ideal"):
            k = (f"ref_ideal:{h}", "") if o == "ref_ideal" else (o, "") if o.startswith("ref_") else key(o)
            aucs[h][o] = {f"x={x}": ms.auc(k, h, x) for x in x_all}
        aucs[h]["random_curve"] = {f"x={x}": crawl.random_auc(n, x) for x in x_all}
        aucs[h]["ideal_curve"] = {f"x={x}": crawl.ideal_auc(int(hot[h].size), n, x) for x in x_all}

    def pair(a: str, b: str, h: str, x: float = x1) -> dict[str, Any]:
        return {"a": a, "b": b, "hot_set": h, "x": x, **ms.contrast(key(a), key(b), h, x)}

    def d1_d2(h: str, x: float = x1, walk: str = "cpr_l50") -> dict[str, Any]:
        return {"D1": pair(walk, "bfs", h, x), "D2": pair(walk, "ib_u", h, x)}

    decision: dict[str, Any] = {}
    for col in IMPORTANCES:
        h = f"{col}@q"
        dd = d1_d2(h)
        v = verdict(dd["D1"], dd["D2"], int(hot[h].size), int(d["min_hot"]))
        if decides:
            decision[col] = {"hot_set": h, "n_hot": int(hot[h].size), **dd, **v}
        else:
            # The same contrasts without a verdict (protocol section 6): no V1/V2/V3 code and no sentence, only
            # which intervals lie above 0 and which below.
            decision[col] = {"hot_set": h, "n_hot": int(hot[h].size), **dd,
                             "above_zero": [k for k in ("D1", "D2") if _above(dd[k])],
                             "below_zero": [k for k in ("D1", "D2") if _below(dd[k])]}
    if decides:
        decision["statements"] = statements({c: decision[c] for c in IMPORTANCES})
    else:
        decision["statements"] = []
        decision["note"] = NOT_DECIDING

    walk_vs_count = [("endorserank", "ib_a"), ("endorserank_activity", "ib_a"), ("cpr_l100", "ib_a"),
                     ("awp", "ib_t"), ("cpr_l0", "ib_t"), ("cpr_l50", "ib_a"), ("cpr_l50", "ib_t")]
    walk_pairs = [("cpr_l50", "cpr_l0"), ("cpr_l50", "awp"), ("cpr_l50", "cpr_l100"), ("cpr_l50", "endorserank"),
                  ("spr", "cpr_l0")]
    primary_hot = [f"{c}@q" for c in IMPORTANCES]
    fixed_order: dict[str, Any] = {
        "1_walk_vs_count": [pair(a, b, h) for a, b in walk_vs_count for h in primary_hot],
        "2_walk_contrasts": [pair(a, b, h) for a, b in walk_pairs for h in primary_hot],
        "3_lambda": {m: {h: {**d1_d2(h, walk=m), "vs_cpr_l50": pair(m, "cpr_l50", h)} for h in primary_hot}
                     for m in ("cpr_l25", "cpr_l75")},
        "4_cho": {"hot_sets": {h: d1_d2(h) for h in ("ib_u@q", "ir@q")},
                  "replication_contrast": pair("cpr_l50", "ib_u", "ib_u@q")},
    }
    sens: dict[str, Any] = {
        "x": {f"x={x}": {h: d1_d2(h, x) for h in primary_hot} for x in x_all[1:]},
        "q_secondary": {"q": float(q2), **{h: d1_d2(h) for h in (f"{c}@q2" for c in IMPORTANCES)}},
        "no_hubs": {"hubs": int(hub_ids.size), **{h: d1_d2(h) for h in (f"{c}@q-nohubs" for c in IMPORTANCES)}},
        "importance_counts": {h: d1_d2(h) for h in ("n_t@q", "n_a@q")},
        "seed_bootstrap": {h: {"D1": ms.seed_contrast(key("cpr_l50"), key("bfs"), h, x1),
                               "D2": ms.seed_contrast(key("cpr_l50"), key("ib_u"), h, x1)} for h in primary_hot},
        "other_mode": _rel(DISC / f"discovery_{tag}_{'both' if mode == 'out' else 'out'}.json"),
    }
    if primary:
        first = slice(0, n4)
        k4 = {o: (o, str(rho4)) for o in crawl.ORDERINGS}
        sens["rho_quarter"] = {
            "rho": str(rho4), "seeds": n4,
            "auc": {h: {o: ms.auc(k4[o], h, x1, first) for o in crawl.ORDERINGS} for h in primary_hot},
            "auc_same_seeds_at_rho": {h: {o: ms.auc(key(o), h, x1, first) for o in crawl.ORDERINGS}
                                      for h in primary_hot},
            "contrasts": {h: {"D1": ms.contrast(k4["cpr_l50"], k4["bfs"], h, x1, first),
                              "D2": ms.contrast(k4["cpr_l50"], k4["ib_u"], h, x1, first)} for h in primary_hot},
        }
    fixed_order["5_sensitivities"] = sens

    # Curves on the grid: P_ST and P_CS (I_T, I_A), captured importance and the cost axis.
    rank = {c: crawl.rank_order(values[c]) for c in IMPORTANCES}
    curves: dict[str, Any] = {"grid": grid.tolist(), "P_ST": {}, "P_CS": {}, "captured": {}, "cost": {}}
    for c in IMPORTANCES:
        h = f"{c}@q"
        curves["P_ST"][c] = {o: _band(crawl.p_st(ms.t(key(o), h), grid)) for o in crawl.ORDERINGS}
        curves["P_ST"][c]["ideal"] = _round(crawl.ideal_curve(grid, int(hot[h].size)))
        curves["P_ST"][c]["random"] = _round(crawl.random_curve(grid, n))
        curves["P_CS"][c] = {o: _band(crawl.p_cs(visits[key(o)], rank[c], grid)) for o in crawl.ORDERINGS}
        curves["captured"][c] = {o: _band(crawl.captured(visits[key(o)], values[c], grid)) for o in crawl.ORDERINGS}
    for o in crawl.ORDERINGS:
        rows = [res["cost"] for t, res in sorted(results.items(), key=lambda kv: kv[0].seed_index)
                if t.ordering == o and t.rho == rho_key]
        curves["cost"][o] = _band(np.vstack(rows))

    # Diagnostics.
    zero = (values["i_t"] == 0) & (values["i_a"] == 0)
    first_1, first_10 = crawl.ceil_share(0.01, n), crawl.ceil_share(0.1, n)
    diag: dict[str, Any] = {"ties": {}, "wasted_visits": {}, "hub_visits": {}}
    for o in crawl.ORDERINGS:
        rs = [res for t, res in results.items() if t.ordering == o and t.rho == rho_key]
        picks = sum(r["picks"] for r in rs)
        diag["ties"][o] = sum(r["tied"] for r in rs) / picks if picks else None
        v = visits[key(o)]
        diag["wasted_visits"][o] = {
            "first_1pct": float(np.mean([zero[v_row <= first_1].mean() for v_row in v])),
            "first_10pct": float(np.mean([zero[v_row <= first_10].mean() for v_row in v])),
        }
        hv = v[:, hub_ids]
        diag["hub_visits"][o] = {"mean": _round(hv.mean(axis=0), 1), "min": hv.min(axis=0).tolist(),
                                 "max": hv.max(axis=0).tolist()}
    diag["hubs"] = [{"node_id": int(node_ids[i]), "address": str(gu.address[i]), "ib_u": int(values["ib_u"][i])}
                    for i in hub_ids]
    diag["coverage"] = coverage(full, ids, bt, universe, imp, inflow_untyped)

    runs = {}
    for o in crawl.ORDERINGS:
        for r_key in sorted({t.rho for t in results}):
            rs = [res for t, res in results.items() if t.ordering == o and t.rho == r_key]
            if rs:
                runs[f"{o}@{r_key}"] = {
                    "crawls": len(rs), "seconds": sum(r["seconds"] for r in rs),
                    "recomputes": float(np.mean([r["recomputes"] for r in rs])),
                    "solves": float(np.mean([r["solves"] for r in rs])),
                    "iterations": float(np.mean([r["iterations"] for r in rs])),
                    "max_final_diff": max((r["final_diff"] for r in rs if r["final_diff"] is not None), default=None),
                }

    out = {
        "window": tag, "mode": mode, "primary_mode": fixed["primary_mode"], "is_primary": primary, "decides": decides,
        "created_at": now(), "seconds": round(time.perf_counter() - started, 1), "workers": workers,
        "protocol": {**{k: fixed[k] for k in ("date", "rho", "q", "author_decision", "feasibility_sha256")},
                     "rho_float": float(rho), "rho_quarter": str(rho4) if primary else None,
                     "q_secondary": float(q2), "x": x_all, "solver": params,
                     "bootstrap": {"resamples": int(al["bootstrap_resamples"]), "seed": int(al["bootstrap_seed"])}},
        "provenance": provenance,
        "sizes": {"graph": {"nodes": full.n, "allow_pairs": full.allow.size, "transfer_pairs": full.transfer.size,
                            **sizes},
                  "universe": {"U": n, "E_U": int(gu.union_src.size), "allow_pairs": gu.allow.size,
                               "transfer_pairs": gu.transfer.size},
                  "pilot": pilot or None, "matches_pilot": pilot_match},
        "seeds": [{"index": i, "node_id": int(node_ids[s]), "address": str(gu.address[s])} for i, s in enumerate(seeds)],
        "hot_sets": {h: int(v.size) for h, v in hot.items()},
        "auc": aucs,
        "decision": decision,
        "fixed_order": fixed_order,
        "curves": curves,
        "diagnostics": diag,
        "runs": runs,
        "invariants": {"all_visited": True, "final_walks_within": FINAL_TOLERANCE,
                       "max_final_diff": max((r["final_diff"] for r in results.values() if r["final_diff"] is not None),
                                             default=None)},
    }
    stem = DISC / f"discovery_{tag}_{mode}"
    path = stem.with_suffix(".json")
    common.save_json(_clean(out), path)

    union_hot = np.unique(np.concatenate([v for v in hot.values()] + [np.empty(0, np.int64)]))
    frames = []
    for (o, r_key), v in visits.items():
        sub = v[:, union_hot]
        seeds_col = np.repeat(np.arange(sub.shape[0]) if r_key else np.array([-1]), union_hot.size)
        frames.append(pd.DataFrame({"ordering": o, "rho": r_key, "seed": seeds_col.astype(np.int16),
                                    "node_id": np.tile(node_ids[union_hot], sub.shape[0]),
                                    "visit_index": sub.ravel().astype(np.int32)}))
    common.write_parts(pd.concat(frames, ignore_index=True), Path(f"{stem}_hot_visits"))
    common.write_parts(pd.DataFrame([{"hot_set": h, "node_id": int(node_ids[i])} for h, v in hot.items() for i in v],
                                    columns=["hot_set", "node_id"]), Path(f"{stem}_hot_sets"))
    print(f"wrote {_rel(path)}: " + (" | ".join(decision["statements"]) if decides else NOT_DECIDING))
    return path


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--window", choices=crawl.FREEZES)
    ap.add_argument("--feasibility", action="store_true", help="the structure pilot (section 7; t1 only)")
    ap.add_argument("--mode", choices=crawl.MODES)
    ap.add_argument("--workers", type=int, default=1)
    args = ap.parse_args(argv)
    if not common.CONTRACT_GRAPH:
        raise SystemExit("run_discovery.py belongs to the contract-graph variant (CONTRACT_REP_VARIANT=contract12m)")
    cfg = common.load_config()
    if args.feasibility:
        if args.window != "t1" or args.mode:
            raise SystemExit("--feasibility runs on --window t1 only, without --mode")
        report = run_feasibility(cfg)
        r, s = report["rules"], report["sizes"]
        print(f"wrote {_rel(FEASIBILITY)}: |U| = {s['U']:,}, |E_U| = {s['E_U']:,}, "
              f"|WCC| = {s['WCC']:,}; rho = {r['rho']}, q = {r['q']}, mode = {r['primary_mode']}")
        if r["stopped"]:
            print("stopped before gate B (protocol section 7), the author decides: "
                  + ", ".join(k for k, v in r["stop"].items() if v))
            return 2
        return 0
    if args.workers < 1:
        raise SystemExit("--workers must be at least 1")
    fixed = check_fixed(protocol_fixed(PROTOCOL), FEASIBILITY, ROOT, cfg.get("discovery"))
    provenance = committed(COMMITTED, ROOT)
    provenance["feasibility_sha256"] = fixed["feasibility_sha256"]
    provenance["pinned_sha256"] = fixed.get("pinned_sha256")   # differs from it only by an author's decision
    # Before any crawl, at either freeze: the rules were set on the t1 pilot, so the t1 graph must be its graph.
    match_pilot(graph_sizes("t1"), fixed)
    windows = [args.window] if args.window else list(crawl.FREEZES)
    other = "both" if fixed["primary_mode"] == "out" else "out"
    modes = [args.mode] if args.mode else [fixed["primary_mode"], other]
    for tag in windows:
        for mode in modes:
            run_window(tag, mode, fixed, provenance, cfg, args.workers)
    return 0


if __name__ == "__main__":
    sys.exit(main())
