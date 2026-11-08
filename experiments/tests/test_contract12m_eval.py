"""The evaluation code of the contract-graph variant (CONTRACT_REP_VARIANT=contract12m) that the gate B amendment of
docs/revision_contract_graph.md section 13 names: rule B's two applied criteria and their two readings, never "Rule B
met", no trader or GMX output, the isolated-node sensitivity, members outside the graph, the baselines of section 9,
the comparisons inside the union graph, the uncapped sensitivity, the label split, the cohorts and spender classes of
the members table, the contract-only nodes, the refusals of the commit and download checks (in every script, and in
run_robustness for the earlier outputs it reads), and the scripts whose part for this variant is not written yet.

Every evaluation script runs in a subprocess on a sandbox copy of experiments/{scripts,config,docs} (a git repository
of its own with an isolated configuration) holding the synthetic world of tests/c12_world.py, under the recorder of
that module, which logs every paired bootstrap, score_all call and parquet read. Nothing reaches a git repository
outside the sandbox, BigQuery or the network, and nothing is written outside pytest's tmp folders. The expectations
are computed from the world's tables, not from the evaluation code.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
import sys
import textwrap
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pytest

import c12_world as w
from conftest import SCRIPTS
from stats import kendall_tau_b

# The names of the evaluation code that the tests rely on and that no decision fixes (design_tests.md section 10, with
# the keys of design_eval.md where design_check.md M4 adopts them); one edit here aligns a test, never an assertion.
NAMES = {
    "provenance": "provenance",                                          # I2: {"head", "sha256": {rel: hex}, ...}
    "rule_b_blocks": ("rule_b", "sensitivity_awp", "sensitivity_isolated"),  # I3
    "applied_rule_b": "applied_rule_b",                                  # I4: (bs, comp, delta, with_f6)
    "baselines_w0": ("t1_in_approve_degree", "t1_in_approve_value", "t1_in_degree", "t1_in_degree_union"),  # I5
    "baselines_w1": ("in_approve_degree", "in_approve_value", "in_degree", "in_degree_union"),
    "coverage": "cohort_coverage",                                       # I6 (M4 b): [list]["union_graph"] = {n, share}
    "coverage_part": "union_graph",
    "no_rule": "decides no rule",                                        # I7
    "label_split": "label_split",                                        # I8 (M4 a): labels[L] = {total, ...}
    "split_parts": ("user_accounts", "contracts", "other"),
    "spender_account_types": "spender_account_types",                    # I9 (M4 d: every class, untyped included)
    "union_in_degree": "union_in_degree",                                # I11: (g, ids) -> pd.Series
    "in_union_graph": "in_union_graph",                                  # I11: (g, ids) -> bool array
    "not_committed": "refused: not committed without local changes:",    # I12
    "uncapped": "uncapped_allowances",                                   # I13: {note, w0, w1}
    "baseline_contrasts": "baseline_contrasts",                          # M4 c: the C-PR minus union in-degree rows
    "stopped": "stopped:",                                               # M4 e: a criterion without a contrast
}
METHODS = ("endorserank", "endorserank_activity", "awp", "cpr_l100", "cpr_l0", "cpr_l25", "cpr_l50", "cpr_l75", "spr")
UNIFORM_RESTARTS = ("endorserank", "cpr_l100", "cpr_l0", "cpr_l25", "cpr_l50", "cpr_l75")   # F8
ACTIVITY_RESTARTS = ("awp", "endorserank_activity")
APPR, SEND = "future_new_approvers", "future_new_transfer_senders"
W0_LABELS = (APPR, SEND, "future_revoke_count", "future_drain_owners")
W1_LABELS = (APPR, SEND)
PROXIES = ("in_degree", "in_value", "in_approve_degree", "in_approve_value", "inbound_counterparty_ratio",
           "transfer_tenure_days", "active_months")
DELTA = 0.01                                                     # the registered margin (docs/registration_w1.md)
OUTPUTS = {"run_same_window": "same-window/eval_summary.json", "run_holdout": "holdout-w0/eval_summary.json",
           "run_registered": "window-w1/eval_summary.json", "run_robustness": "robustness/robustness.json"}
FOLDERS = ("same-window", "holdout-w0", "window-w1", "robustness")
# Per script: the member list it evaluates, its freeze, the key of its count in the summary, its main vectors besides
# the scores and the baselines it adds (the matched cohort's proxies include the raw degrees on the capped graph).
COHORTS = {
    "run_same_window": ("cohort_tobs", "tobs", "cohort", PROXIES, ("in_approve_degree", "in_approve_value",
                                                                    "in_degree")),
    "run_holdout": ("spenders_w0", "t1", "spenders", W0_LABELS, NAMES["baselines_w0"]),
    "run_registered": ("spenders_w1", "tobs", "spenders", W1_LABELS, NAMES["baselines_w1"]),
}
VERDICT_KEYS = {"holds", "pass", "f1_f2_hold", "rule_b_not_met", "rule_b_reading", "decision", "rule_a",
                "rule_a_primary", "rule_a_secondary"}
RULE_B_MET = re.compile(r"rule[\s_]*b[\s_]+(is[\s_]+)?(met|holds)\b", re.I)                  # T12
# The keys of a rule-B block (revision section 11, D19): the two applied criteria and their readings, and F6 where the
# registration has it; RULE_B_NAMES are the only keys of any summary that name rule B (F5).
RULE_B_KEYS = {"F1", "F2", "f1_f2_hold", "rule_b_not_met", "rule_b_reading"}
F6_KEYS = {"F6a", "F6b", "F6"}
RULE_B_NAMED = re.compile(r"rule[\s_]*b", re.I)
RULE_B_NAMES = {"rule_b", "rule_b_not_met", "rule_b_reading"}
TRADER_KEYS = {"F3", "F4", "F5", "P", "Q", "R1", "R2", "R3", "decision", "traders", "trader_taus",
               "traders_liquidated", "traders_all_liquidated", "neutral_w0", "neutral_w1", "neutral_rules",
               "cpr_minus_endorserank_liq"}
TRADER_WORDS = re.compile(r"gmx|trader|liquidat|\bneutral", re.I)                             # T13
TRADER_CRITERIA = re.compile(r"\bF[345]\b|\bR[123]\b")
REGISTERED_RESULTS = re.compile(r"\bregistered results?\b", re.I)
SCORE_TABLES = ("same-window/cohort_scores", "holdout-w0/spender_scores", "window-w1/spender_scores")
SPLIT_COLUMNS = {f"n_t1_{p}" for p in w.PARTS} | {f"{lab}_{p}" for lab in w.LABELS for p in w.PARTS}


# --------------------------------------------------------------------------- helpers


def strings(obj) -> list[str]:
    """Every key and every string value of a JSON object, at any depth."""
    if isinstance(obj, dict):
        return [*(str(k) for k in obj), *(x for v in obj.values() for x in strings(v))]
    if isinstance(obj, list):
        return [x for v in obj for x in strings(v)]
    return [obj] if isinstance(obj, str) else []


def string_values(obj) -> list[str]:
    """Every string value of a JSON object, at any depth (no keys)."""
    if isinstance(obj, dict):
        return [x for v in obj.values() for x in string_values(v)]
    if isinstance(obj, list):
        return [x for v in obj for x in string_values(v)]
    return [obj] if isinstance(obj, str) else []


def all_keys(obj) -> set[str]:
    if isinstance(obj, dict):
        return {str(k) for k in obj} | {k for v in obj.values() for k in all_keys(v)}
    if isinstance(obj, list):
        return {k for v in obj for k in all_keys(v)}
    return set()


def dicts(obj):
    """Every dict of a JSON object, at any depth."""
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from dicts(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from dicts(v)


def noted(obj, note: str = NAMES["no_rule"]) -> list[dict]:
    """The dicts of ``obj`` one of whose direct values is a string containing ``note``."""
    return [d for d in dicts(obj) if any(isinstance(v, str) and note in v for v in d.values())]


def tau(x, y) -> float:
    return kendall_tau_b(np.asarray(x, dtype=np.float64), np.asarray(y, dtype=np.float64))


def B_main(rec: dict, n: int, labels) -> dict:
    """The vectors of the first recorded bootstrap with ``n`` members holding every score and the vectors ``labels``
    (the main bootstrap of a script: every script creates it first)."""
    found = w.boots(rec, n=n, has=(*METHODS, *labels))
    assert found, f"no recorded bootstrap of {n} members holds every score and {list(labels)}"
    return found[0]["vectors"]


def restricted(vector: list[float], keep: list[bool]) -> list[float]:
    return [v for v, k in zip(vector, keep) if k]


def pair_ends(world: w.World, tag: str) -> set[int]:
    """The node ids that are an end of a capped allowance or a transfer pair at the freeze (self-pairs included)."""
    out: set[int] = set()
    for stem in (f"allow_pairs_{tag}", f"transfer_pairs_{tag}"):
        f = world.frames[stem]
        out |= set(f["src"].astype(int)) | set(f["dst"].astype(int))
    return out


def union_pairs(world: w.World, tag: str, allow_stem: str = "allow_pairs") -> pd.DataFrame:
    """The union graph of the freeze from the world's tables: distinct (src, dst), src != dst, in either layer (the
    allowance layer of ``allow_stem``: the capped one, or allow_pairs_uncapped for the uncapped sensitivity)."""
    parts = [world.frames[s][["src", "dst"]] for s in (f"{allow_stem}_{tag}", f"transfer_pairs_{tag}")]
    u = pd.concat(parts, ignore_index=True).astype(np.int64).drop_duplicates()
    return u[u["src"] != u["dst"]]


def inside_union(world: w.World, tag: str, ids: list[int]) -> list[bool]:
    u = union_pairs(world, tag)
    ends = set(u["src"]) | set(u["dst"])
    return [i in ends for i in ids]


def world_baselines(world: w.World, tag: str, ids: list[int],
                    allow_stem: str = "allow_pairs") -> dict[str, list[float]]:
    """The baselines of revision section 9 at the freeze, counted from the world's tables as graphs.raw_degrees (of
    d39775c) counts them on the capped graph (or on the allowance layer of ``allow_stem``), and the union in-degree
    |{u != v: (u, v) in either layer}|."""
    a, t = world.frames[f"{allow_stem}_{tag}"], world.frames[f"transfer_pairs_{tag}"]
    in_approve_degree = a.groupby("dst")["src"].nunique()
    in_approve_value = a.groupby("dst")["w_raw"].sum()
    other = t[t["src"] != t["dst"]]
    in_degree = other.groupby("dst")["src"].nunique()
    union = union_pairs(world, tag, allow_stem).groupby("dst").size()
    get = lambda s: [float(s.get(i, 0.0)) for i in ids]  # noqa: E731
    return {"in_approve_degree": get(in_approve_degree), "in_approve_value": get(in_approve_value),
            "in_degree": get(in_degree), "in_degree_union": get(union)}


def run_code(code: str, variant: str | None, spec, tmp: Path, *, cwd: Path, git_root: Path | None = None,
             args: tuple[str, ...] = ()):
    """``code`` in a fresh interpreter under ``variant``; its cases come through a JSON file (T11), its result is the
    last line of stdout as JSON."""
    tmp.mkdir(parents=True, exist_ok=True)
    path = tmp / "cases.json"
    path.write_text(json.dumps(spec), encoding="utf-8")
    env = w.variant_env(variant)
    if git_root is not None:
        env = w.git_env(git_root, env)
    out = subprocess.run([sys.executable, "-c", textwrap.dedent(code), str(path), *args], cwd=cwd, env=env,
                         capture_output=True, text=True, encoding="utf-8", timeout=900)
    assert out.returncode == 0, out.stdout[-2000:] + out.stderr[-4000:]
    return json.loads(out.stdout.strip().splitlines()[-1])


def output_folders(exp: Path) -> list[str]:
    proc = exp / w.PROC_REL
    return sorted(f for f in FOLDERS if (proc / f).exists())


def c12_variant(tmp: Path, change: str | None) -> tuple[Path, w.World]:
    """A fresh git sandbox holding the contract world, clean or with one change of c12_world.CHANGES."""
    exp = w.sandbox(tmp, git=True)
    return exp, w.contract_world(exp, change=change)


# --------------------------------------------------------------------------- the clean runs


@pytest.fixture(scope="module")
def c12_runs(tmp_path_factory) -> dict:
    """The four evaluation scripts of this variant, in the order of run_usd_local.ps1, on the clean world in one git
    sandbox, with the traps of the trader code and of the registered account types installed; each must exit 0."""
    tmp = tmp_path_factory.mktemp("c12")
    exp = w.sandbox(tmp / "sandbox", git=True)
    world = w.contract_world(exp)
    head = w.sandbox_git(exp, "rev-parse", "HEAD").strip()
    before = w.snapshot(exp.parent)
    runs = {}
    for s in w.C12_SCRIPTS:
        rec = tmp / f"rec_{s}.json"
        out = w.run_script(exp, s, "contract12m", rec=rec, traps=True)
        assert out.returncode == 0, f"{s} exited {out.returncode}:\n{out.stdout[-2000:]}\n{out.stderr[-4000:]}"
        runs[s] = {"summary": json.loads((exp / w.PROC_REL / OUTPUTS[s]).read_text(encoding="utf-8")),
                   "rec": w.load_record(rec), "stdout": out.stdout, "stderr": out.stderr}
    return {"runs": runs, "world": world, "exp": exp, "head": head, "before": before, "after": w.snapshot(exp.parent)}


def summary(c12_runs: dict, script: str) -> dict:
    return c12_runs["runs"][script]["summary"]


def record(c12_runs: dict, script: str) -> dict:
    return c12_runs["runs"][script]["rec"]


# --------------------------------------------------------------------------- rule B (revision section 11, D19)


def test_rule_b_reports_two_criteria_without_a_decision(c12_runs):
    """E1: F1 and F2 with their tests and the two readings of revision section 11, in the main block and in the two
    registered sensitivity analyses, each block with exactly its keys; F6 where the registration has it; no
    decision, F3, F4 or F5 anywhere; the numbers are those of the recorded main W1 bootstrap."""
    s = summary(c12_runs, "run_registered")
    assert s["delta"] == DELTA and s["applied_criteria"] == ["F1", "F2"]
    # exactly these keys: a block cannot carry a verdict of rule B under another name (F5)
    exact = {"rule_b": RULE_B_KEYS | F6_KEYS, "sensitivity_awp": RULE_B_KEYS,
             "sensitivity_isolated": RULE_B_KEYS | F6_KEYS | {"isolated_walks", "iterations", "spender_taus"}}
    assert set(exact) == set(NAMES["rule_b_blocks"])
    for name in NAMES["rule_b_blocks"]:
        block = s[name]
        assert set(block) == exact[name], (name, sorted(set(block) ^ exact[name]))
        f1, f2 = block["F1"], block["F2"]
        assert (f1["test"], f2["test"]) == ("superiority", "non_inferiority"), name
        assert f1["holds"] is (f1["ci_low"] > 0) and f2["holds"] is (f2["ci_low"] > -DELTA), name
        hold = f1["holds"] and f2["holds"]
        assert block["f1_f2_hold"] is hold and block["rule_b_not_met"] is (not hold), name
        assert block["rule_b_reading"] == ("both applied criteria hold" if hold else "not met"), name
    for name in ("rule_b", "sensitivity_isolated"):
        f6a, f6b = s[name]["F6a"], s[name]["F6b"]
        assert f6a["test"] == "no_worse" and f6a["holds"] is (f6a["ci_high"] >= 0), name
        assert f6b["test"] == "superiority" and f6b["holds"] is (f6b["ci_low"] > 0), name
        assert s[name]["F6"] is (f6a["holds"] and f6b["holds"]), name
    assert not {"F6", "F6a", "F6b"} & set(s["sensitivity_awp"])
    assert not {"decision", "F3", "F4", "F5"} & all_keys(s)
    # The numbers are those of the main W1 bootstrap (the first one of 51 spenders with every score), API-free.
    M = B_main(record(c12_runs, "run_registered"), 51, W1_LABELS)
    expected = {("rule_b", "F1"): ("cpr_l50", "cpr_l0", APPR), ("rule_b", "F2"): ("cpr_l50", "cpr_l0", SEND),
                ("rule_b", "F6a"): ("cpr_l50", "cpr_l100", APPR), ("rule_b", "F6b"): ("cpr_l50", "cpr_l0", SEND),
                ("sensitivity_awp", "F1"): ("cpr_l50", "awp", APPR),
                ("sensitivity_awp", "F2"): ("cpr_l50", "awp", SEND)}
    for (block, crit), (a, b, label) in expected.items():
        got = s[block][crit]
        assert abs(got["a_tau"] - tau(M[a], M[label])) <= 1e-12, (block, crit)
        assert abs(got["b_tau"] - tau(M[b], M[label])) <= 1e-12, (block, crit)
        assert got["n_boot"] == 400, (block, crit)


TRUTH = r"""
    import json, sys
    from pathlib import Path
    sys.path.insert(0, sys.argv[2])
    import run_registered as r

    class FakeBoot:
        def __init__(self, table):
            self.table, self.asked = table, []

        def contrast(self, a, b):
            self.asked.append([list(a), list(b)])
            return self.table[f"{b[0]}|{b[1]}"]

    out = []
    for case in json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")):
        boot = FakeBoot(case["table"])
        try:
            out.append({"result": getattr(r, case["fn"])(boot, case["comp"], case["delta"], case["with_f6"]),
                        "asked": boot.asked})
        except SystemExit as e:
            out.append({"exit": str(e), "asked": boot.asked})
    print(json.dumps(out))
"""


def contrast(ci_low: float, ci_high: float = 0.5) -> dict:
    return {"a_tau": 0.3, "b_tau": 0.2, "delta_tau": 0.1, "ci_low": ci_low, "ci_high": ci_high,
            "share_positive": 0.9, "n_boot": 400}


def test_applied_rule_b_truth_table(tmp_path):
    """E2: the thresholds of F1 (superiority), F2 (non-inferiority by δ), F6a (no worse) and F6b (superiority) at
    their boundaries, the four combinations of F1 and F2 with their readings, no F6 without it, the contrasts asked
    (C-PR(λ=0.5) minus the comparator), and a criterion whose contrast has no value stops the run (M4 e)."""
    fn = NAMES["applied_rule_b"]
    eps = 1e-12
    cases, expect = [], []

    def case(comp, with_f6, **lows):
        """lows: ci_low of F1 (comp, APPR) and F2 (comp, SEND); ci_high of F6a (cpr_l100, APPR); F6b shares the F2
        contrast when comp is cpr_l0."""
        table = {f"{comp}|{APPR}": lows.get("f1"), f"{comp}|{SEND}": lows.get("f2"),
                 f"cpr_l100|{APPR}": lows.get("f6a"), f"cpr_l0|{SEND}": lows.get("f6b", lows.get("f2"))}
        cases.append({"fn": fn, "comp": comp, "delta": DELTA, "with_f6": with_f6, "table": table})

    for f1 in (eps, 0.0):                                        # F1 holds at ci_low 1e-12, not at 0
        for f2 in (-DELTA + eps, -DELTA):                        # F2 holds at -0.01 + 1e-12, not at -0.01
            for comp in ("cpr_l0", "awp"):
                case(comp, comp == "cpr_l0", f1=contrast(f1), f2=contrast(f2), f6a=contrast(0.0, 0.0))
                expect.append({"comp": comp, "F1": f1 > 0, "F2": f2 > -DELTA})
    for hi in (0.0, -eps):                                       # F6a holds at ci_high 0, not at -1e-12
        for low in (eps, 0.0):                                   # F6b holds at ci_low 1e-12, not at 0
            case("cpr_l0", True, f1=contrast(0.1), f2=contrast(low), f6a=contrast(-0.2, hi))
            expect.append({"comp": "cpr_l0", "F1": True, "F2": True, "F6a": hi >= 0, "F6b": low > 0})
    n_judged = len(cases)
    for missing in ("f1", "f2", "f6a"):                          # a contrast without a value stops the run
        lows = {"f1": contrast(0.1), "f2": contrast(0.1), "f6a": contrast(0.0, 0.1)}
        lows[missing] = None
        case("cpr_l0", True, **lows)
    out = run_code(TRUTH, "contract12m", cases, tmp_path, cwd=SCRIPTS, args=(str(SCRIPTS),))

    for i, (got, exp) in enumerate(zip(out[:n_judged], expect)):
        assert "exit" not in got, (i, got)
        r, comp, with_f6 = got["result"], exp["comp"], cases[i]["with_f6"]
        keys = {"F1", "F2", "f1_f2_hold", "rule_b_not_met", "rule_b_reading"} | (
            {"F6a", "F6b", "F6"} if with_f6 else set())
        assert set(r) == keys, (i, sorted(r))
        assert (r["F1"]["holds"], r["F2"]["holds"]) == (exp["F1"], exp["F2"]), (i, exp)
        assert (r["F1"]["test"], r["F2"]["test"]) == ("superiority", "non_inferiority")
        assert r["F1"]["ci_low"] == cases[i]["table"][f"{comp}|{APPR}"]["ci_low"]       # the contrast is passed on
        hold = exp["F1"] and exp["F2"]
        assert r["f1_f2_hold"] is hold and r["rule_b_not_met"] is (not hold)
        assert r["rule_b_reading"] == ("both applied criteria hold" if hold else "not met")
        asked = [[["cpr_l50", APPR], [comp, APPR]], [["cpr_l50", SEND], [comp, SEND]]]
        if with_f6:
            asked += [[["cpr_l50", APPR], ["cpr_l100", APPR]], [["cpr_l50", SEND], ["cpr_l0", SEND]]]
            assert r["F6a"]["test"] == "no_worse" and r["F6b"]["test"] == "superiority"
            if "F6a" in exp:
                assert (r["F6a"]["holds"], r["F6b"]["holds"]) == (exp["F6a"], exp["F6b"]), (i, exp)
            assert r["F6"] is (r["F6a"]["holds"] and r["F6b"]["holds"])
        assert got["asked"] == asked, i
    for got in out[n_judged:]:
        assert "exit" in got and got["exit"].startswith(NAMES["stopped"]), got
    # the four combinations of (F1, F2) were all met
    assert {(e["F1"], e["F2"]) for e in expect} == {(True, True), (True, False), (False, True), (False, False)}


def test_no_output_says_rule_b_is_met(c12_runs):
    """E3: no key, string value or console line of the four runs, and no JSON under the sandbox's PROC, says that
    rule B is met or holds; the readings and the key rule_b_not_met do not match the pattern (T12). In the four
    summaries no key names rule B but rule_b, rule_b_not_met and rule_b_reading, and no string value is 'met' or
    'holds' on its own (a verdict under another key, such as {"rule_b_verdict": "met"}, F5)."""
    for ok in ("rule_b_not_met", "not met", "both applied criteria hold", "F1 and F2, two of rule B's criteria"):
        assert not RULE_B_MET.search(ok)
    for bad in ("Rule B met", "rule B is met", "rule_b_holds", "RULE B HOLDS"):
        assert RULE_B_MET.search(bad)
    for s, r in c12_runs["runs"].items():
        named = sorted(k for k in all_keys(r["summary"]) if RULE_B_NAMED.match(k) and k not in RULE_B_NAMES)
        assert not named, (s, named)
        bare = sorted({v for v in string_values(r["summary"]) if v.strip().lower() in ("met", "holds")})
        assert not bare, (s, bare)
    texts = []
    for s, r in c12_runs["runs"].items():
        texts += strings(r["summary"]) + [r["stdout"], r["stderr"]]
    for p in sorted((c12_runs["exp"] / w.PROC_REL).rglob("*.json")):
        texts += strings(json.loads(p.read_text(encoding="utf-8")))
    for stem in SCORE_TABLES:
        texts += pq.read_schema(w.part_paths(c12_runs["exp"] / w.PROC_REL / stem)[0]).names
    hits = sorted({t[:200] for t in texts if RULE_B_MET.search(t)})
    assert not hits, f"outputs say that rule B is met or holds: {hits}"


def test_no_trader_or_gmx_output_in_this_variant(c12_runs):
    """E4: the four runs exited 0 although labels.load_closes, trader_labels, strata_tau and account_types raise (the
    recorder's traps), so none was called; no trader score table, no trader or GMX key, word or criterion (F3-F5, P,
    Q, R1-R3) in any summary or score table, and every isolated set the scores were computed with is a cohort of
    contracts."""
    exp, world = c12_runs["exp"], c12_runs["world"]
    assert not sorted(p.name for p in exp.parent.rglob("trader_scores*"))
    for s, r in c12_runs["runs"].items():
        assert not all_keys(r["summary"]) & TRADER_KEYS, (s, sorted(all_keys(r["summary"]) & TRADER_KEYS))
        texts = strings(r["summary"]) + [r["stdout"]]
        hits = sorted({t[:120] for t in texts if TRADER_WORDS.search(t) or TRADER_CRITERIA.search(t)})
        assert not hits, (s, hits)
    for stem in SCORE_TABLES:
        names = pq.read_schema(w.part_paths(exp / w.PROC_REL / stem)[0]).names
        assert not [c for c in names if TRADER_WORDS.search(c)], (stem, names)
    cohorts = [world.contracts(name) for name in w.LISTS]
    for s, r in c12_runs["runs"].items():
        for call in r["rec"]["score_all"]:
            assert call["tag"] in ("t1", "tobs"), (s, call["tag"])
            assert call["isolated"] is None or call["isolated"] in cohorts, (s, call["isolated"])


# --------------------------------------------------------------------------- sensitivity 2 and the members


def test_isolated_sensitivity_adds_the_members_to_every_walk_but_spr(c12_runs):
    """E5 (revision section 11, F8): Sensitivity 2 isolates exactly the W1 contract spenders in every walk but S-PR,
    the coupled walks included; a spender outside both layers then scores above 0 under every walk with uniform
    restarts and stays at 0 under the walks with activity restarts; S-PR is unchanged."""
    world, rec = c12_runs["world"], record(c12_runs, "run_registered")
    ids = world.spenders_w1
    calls = [c for c in rec["score_all"] if c["isolated"] is not None]
    assert calls and all(c["isolated"] == ids for c in calls), [c["isolated"] for c in calls]
    covered = set().union(*(set(c["methods"] or METHODS) for c in calls))
    assert covered == set(METHODS) - {"spr"} and not any("spr" in (c["methods"] or METHODS) for c in calls)
    M = B_main(rec, len(ids), W1_LABELS)
    others = [b["vectors"] for b in w.boots(rec, n=len(ids), has=(*METHODS, *W1_LABELS))[1:]]
    isolated = [v for v in others if all(v[x] == M[x] for x in W1_LABELS) and v["cpr_l50"] != M["cpr_l50"]]
    assert len(isolated) == 1, "one recorded bootstrap of the W1 spenders with the isolated scores"
    I = isolated[0]
    pos = {i: k for k, i in enumerate(ids)}
    outside = sorted(set(world.outside_both) & set(ids))
    assert outside == [45, 65, 85, 149]
    for i in outside:
        k = pos[i]
        assert all(M[m][k] == 0 for m in METHODS), i
        assert all(I[m][k] > 0 for m in UNIFORM_RESTARTS), (i, {m: I[m][k] for m in UNIFORM_RESTARTS})
        assert all(I[m][k] == 0 for m in ACTIVITY_RESTARTS), (i, {m: I[m][k] for m in ACTIVITY_RESTARTS})
    assert I["spr"] == M["spr"]
    for i in sorted(set(world.transfer_only) & set(ids)):                 # no allowance pair: lifted in cpr_l100
        assert M["cpr_l100"][pos[i]] == 0 < I["cpr_l100"][pos[i]], i
    for i in sorted(set(world.allow_only) & set(ids)):                    # no transfer pair: lifted in cpr_l0
        assert M["cpr_l0"][pos[i]] == 0 < I["cpr_l0"][pos[i]], i
    s = summary(c12_runs, "run_registered")["sensitivity_isolated"]
    assert abs(s["F1"]["a_tau"] - tau(I["cpr_l50"], I[APPR])) <= 1e-12
    assert abs(s["F1"]["b_tau"] - tau(I["cpr_l0"], I[APPR])) <= 1e-12


# A small graph with pairs of weight 0, which contract12m keeps, as (src, dst, weight, w_raw, max_sig): the allowance
# pair 6 -> 7 has w_er 0 (dust) and w_raw > 0, 8 -> 8 and 9 -> 2 have both weights 0; the transfer pair 10 -> 0 has
# w_awp 0 and w_raw > 0, 11 -> 12, 9 -> 1 and 7 -> 7 have both weights 0. Member 5 ends no pair.
ZERO_PAIRS = {"allow": [(0, 1, 1.0, 2.0, 0.9), (1, 2, 0.5, 1.0, 0.8), (2, 0, 0.7, 3.0, 0.7), (3, 1, 0.4, 0.5, 0.6),
                        (6, 7, 0.0, 1.5, 0.5), (8, 8, 0.0, 0.0, 0.4), (9, 2, 0.0, 0.0, 0.3)],
              "transfer": [(0, 2, 1.0, 1.0, 0.9), (2, 1, 0.6, 2.0, 0.8), (1, 0, 0.3, 0.7, 0.7), (4, 3, 0.8, 1.2, 0.6),
                           (10, 0, 0.0, 0.9, 0.5), (11, 12, 0.0, 0.0, 0.4), (9, 1, 0.0, 0.0, 0.3),
                           (7, 7, 0.0, 0.0, 0.2)]}
ZERO_COLUMNS = {"allow": ("src", "dst", "w_er", "w_raw", "max_sig"),
                "transfer": ("src", "dst", "w_awp", "w_raw", "max_sig")}
ZERO_MEMBERS = [1, 3, 5, 6, 7, 8, 9, 10, 11]
# The layers and weight columns of each walk that Sensitivity 2 isolates (graphs.score_all).
WALK_COLUMNS = {"endorserank": (("allow", "w_er"),), "endorserank_activity": (("allow", "w_er"),),
                "awp": (("transfer", "w_awp"),), "cpr_l100": (("allow", "w_raw"),), "cpr_l0": (("transfer", "w_raw"),),
                **{m: (("allow", "w_raw"), ("transfer", "w_raw")) for m in ("cpr_l25", "cpr_l50", "cpr_l75")}}
ISOLATED_PROBE = r"""
    import json, sys
    from pathlib import Path
    sys.path.insert(0, sys.argv[2])
    import numpy as np
    import pandas as pd
    import graphs

    case = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    g = graphs.Graphs("tobs", pd.DataFrame(case["allow"]), pd.DataFrame(case["transfer"]))
    out, _ = graphs.score_all(g, case["params"], methods=tuple(case["methods"]), isolated=np.array(case["ids"]))
    print(json.dumps({m: {"ids": [int(i) for i in s.index], "scores": [float(x) for x in s]} for m, s in out.items()}))
"""


def test_isolated_nodes_are_the_members_without_a_positive_pair_in_the_walk(tmp_path, params):
    """E5, unit (revision section 11): contract12m keeps the pairs of weight 0, which the walks drop, so under it
    score_all adds as isolated nodes to each walk but S-PR the members that end no pair of positive weight in that
    walk's layers and weight columns (w_er for the EndorseRank walks, w_awp for AWP, w_raw for C-PR, both layers for
    the coupled walks): a member that ends only pairs of weight 0 is not left at 0. Under the earlier variants a member
    that ends any pair of the walk's layers is not added, as at d39775c. The expected walks are the solver's own on
    the expected isolated nodes."""
    from scoring import activeness, coupled_pagerank, weighted_pagerank

    frames = {k: pd.DataFrame(rows, columns=ZERO_COLUMNS[k]) for k, rows in ZERO_PAIRS.items()}
    members = set(ZERO_MEMBERS)

    def ends(m: str, positive: bool) -> set[int]:
        out: set[int] = set()
        for layer, col in WALK_COLUMNS[m]:
            f = frames[layer][frames[layer][col] > 0] if positive else frames[layer]
            out |= {int(x) for x in (*f["src"], *f["dst"])}
        return out

    def walk(m: str, extra: set[int]) -> pd.Series:
        a, t, x = frames["allow"], frames["transfer"], np.array(sorted(extra), dtype=np.int64)
        if m in ("endorserank", "endorserank_activity"):
            act = activeness(a["src"], a["dst"], a["max_sig"]) if m == "endorserank_activity" else None
            return weighted_pagerank(a["src"], a["dst"], a["w_er"], teleport=act, extra_nodes=x, **params)[0]
        if m == "awp":
            act = activeness(t["src"], t["dst"], t["max_sig"])
            return weighted_pagerank(t["src"], t["dst"], t["w_awp"], teleport=act, extra_nodes=x, **params)[0]
        if m in ("cpr_l100", "cpr_l0"):
            f = a if m == "cpr_l100" else t
            return weighted_pagerank(f["src"], f["dst"], f["w_raw"], extra_nodes=x, **params)[0]
        lam = {"cpr_l25": 0.25, "cpr_l50": 0.5, "cpr_l75": 0.75}[m]
        return coupled_pagerank([(a["src"], a["dst"], a["w_raw"], lam), (t["src"], t["dst"], t["w_raw"], 1.0 - lam)],
                                extra_nodes=x, **params)[0]

    zero_only = {m: members & (ends(m, False) - ends(m, True)) for m in WALK_COLUMNS}
    assert all(zero_only.values()), zero_only        # every walk has a member that ends only pairs of weight 0 in it
    spec = {k: {c: [r[i] for r in rows] for i, c in enumerate(ZERO_COLUMNS[k])} for k, rows in ZERO_PAIRS.items()}
    spec.update(params=params, methods=list(WALK_COLUMNS), ids=ZERO_MEMBERS)
    for variant in ("contract12m", *w.EARLIER_VARIANTS):
        got = run_code(ISOLATED_PROBE, variant, spec, tmp_path / variant, cwd=tmp_path, args=(str(SCRIPTS),))
        assert sorted(got) == sorted(WALK_COLUMNS), (variant, sorted(got))
        for m in WALK_COLUMNS:
            want = walk(m, members - ends(m, positive=variant == "contract12m"))
            assert got[m]["ids"] == [int(i) for i in want.index], (variant, m, got[m]["ids"])
            assert got[m]["scores"] == [float(x) for x in want], (variant, m)
            inside = set(got[m]["ids"])
            if variant == "contract12m":
                assert members <= inside, (m, sorted(members - inside))
            else:
                assert not zero_only[m] & inside, (variant, m, sorted(zero_only[m] & inside))


@pytest.mark.parametrize("script", list(COHORTS))
def test_members_outside_the_graph_stay_and_score_zero(c12_runs, script):
    """E6 (revision section 8, D6, D21): no contract member is dropped; every member without a pair at the freeze
    scores 0 under every score and baseline; the coverage of the union graph is counted from the world's tables."""
    world, s, rec = c12_runs["world"], summary(c12_runs, script), record(c12_runs, script)
    name, tag, count, vectors, baselines = COHORTS[script]
    ids = world.contracts(name)
    assert len(ids) == {"cohort_tobs": 40, "spenders_w0": 50, "spenders_w1": 51}[name]
    assert s[count] == len(ids)
    M = B_main(rec, len(ids), vectors)
    ends = pair_ends(world, tag)
    without = [i for i in ids if i not in ends]
    assert without == sorted(set(world.outside_both) & set(ids))
    for i in without:
        k = ids.index(i)
        nonzero = {v: M[v][k] for v in (*METHODS, *baselines) if M[v][k] != 0}
        assert not nonzero, (i, nonzero)
    coverage = {name: (ids, tag)}
    if script == "run_holdout":
        coverage["cohort_t1"] = (world.contracts("cohort_t1"), "t1")
    for lst, (members, freeze) in coverage.items():
        n_in = sum(inside_union(world, freeze, members))
        got = s[NAMES["coverage"]][lst][NAMES["coverage_part"]]
        assert got == {"n": n_in, "share": n_in / len(members)}, (lst, got, n_in)


def test_a_contract_member_without_a_node_is_refused(tmp_path):
    """E6, refusal: a contract member that nodes lacks (node 149, the highest address) makes run_registered refuse
    and write nothing (D6: a contract member is never dropped)."""
    exp, world = c12_variant(tmp_path / "sandbox", "member_without_node")
    out = w.run_script(exp, "run_registered", "contract12m", rec=tmp_path / "rec.json")
    assert out.returncode != 0 and "refused:" in out.stderr and world.target["address"] in out.stderr, out.stderr
    assert not output_folders(exp)


def test_inside_union_graph_sensitivity_decides_no_rule(c12_runs):
    """E7 (D19, D21): the comparisons inside the union graph run on a bootstrap of the inside members (their label or
    proxy vectors are the main ones restricted, in id order), carry the note that they decide no rule, and no dict
    with that note holds a verdict; the rule B blocks do not carry it."""
    world = c12_runs["world"]
    for script, (name, tag, _, vectors, _) in COHORTS.items():
        ids, rec, s = world.contracts(name), record(c12_runs, script), summary(c12_runs, script)
        keep = inside_union(world, tag, ids)
        n_in = sum(keep)
        assert 0 < n_in < len(ids)
        M = B_main(rec, len(ids), vectors)
        found = [b for b in w.boots(rec, n=n_in, has=(*METHODS, *vectors))
                 if all(b["vectors"][v] == restricted(M[v], keep) for v in vectors)]
        assert found, f"{script}: no bootstrap of the {n_in} members inside the union graph"
        blocks = noted(s)
        assert blocks, f"{script}: no dict says that it {NAMES['no_rule']}"
        for d in blocks:
            assert not all_keys(d) & VERDICT_KEYS, (script, sorted(all_keys(d) & VERDICT_KEYS))
        assert s["in_union_graph"]["n"] == n_in and noted(s["in_union_graph"]), script
    s = summary(c12_runs, "run_registered")
    for name in NAMES["rule_b_blocks"]:
        assert not any(isinstance(v, str) and NAMES["no_rule"] in v for v in s[name].values()), name


# --------------------------------------------------------------------------- baselines and the uncapped sensitivity


def test_baselines_on_the_contract_graph(c12_runs):
    """E8 (revision section 9, D20): the baselines of the main W0 and W1 bootstraps are the raw degrees on the capped
    contract graph and the union in-degree on G, counted from the world's tables; they are 0 outside the graph; C-PR
    minus the union in-degree is reported on both labels at W0 and W1."""
    world = c12_runs["world"]
    for script, tag, names, labels in (("run_holdout", "t1", NAMES["baselines_w0"], W0_LABELS),
                                       ("run_registered", "tobs", NAMES["baselines_w1"], W1_LABELS)):
        name = COHORTS[script][0]
        ids = world.contracts(name)
        M = B_main(record(c12_runs, script), len(ids), labels)
        expected = world_baselines(world, tag, ids)
        prefix = "t1_" if tag == "t1" else ""
        for base, values in expected.items():
            got = M[prefix + base]
            if base == "in_approve_value":
                np.testing.assert_allclose(got, values, rtol=1e-12, atol=0, err_msg=f"{script} {base}")
            else:
                assert got == values, (script, base)
        assert sorted(prefix + b for b in expected) == sorted(names)
        for i in sorted(set(world.outside_both) & set(ids)):
            assert all(M[b][ids.index(i)] == 0 for b in names), (script, i)
    rows = {(r["a"], r["b"], r["outcome"]) for r in summary(c12_runs, "run_holdout")[NAMES["baseline_contrasts"]]}
    assert {("cpr_l50", "t1_in_degree_union", APPR), ("cpr_l50", "t1_in_degree_union", SEND)} <= rows, rows
    s = summary(c12_runs, "run_registered")
    M = B_main(record(c12_runs, "run_registered"), 51, W1_LABELS)
    for label in (APPR, SEND):
        a, b = tau(M["cpr_l50"], M[label]), tau(M["in_degree_union"], M[label])
        hits = [d for d in dicts(s) if isinstance(d.get("a_tau"), float) and isinstance(d.get("b_tau"), float)
                and abs(d["a_tau"] - a) <= 1e-12 and abs(d["b_tau"] - b) <= 1e-12]
        assert hits, f"no W1 contrast of C-PR minus the union in-degree on {label}"


def test_union_in_degree_follows_the_crawl_graph():
    """E8, unit (I11): graphs.union_in_degree counts what crawl.CrawlGraph.union_in_degree counts (distinct other
    contracts with a pair in either layer, whatever the weight), 0 for an id without one; a node with only a
    self-loop is outside the union graph."""
    import crawl
    import graphs

    n = 7
    allow = [(0, 1), (1, 2), (3, 3), (4, 1), (6, 2)]            # 3: a self-loop only
    transfer = [(0, 1), (2, 0), (5, 5), (4, 2)]                 # (0, 1) in both layers; 5: a self-loop only
    zero = {(6, 2)}                                             # a pair of weight 0 is still a pair

    def frame(pairs, weight):
        return pd.DataFrame({"src": [p[0] for p in pairs], "dst": [p[1] for p in pairs],
                             weight: [0.0 if p in zero else 1.0 for p in pairs],
                             "w_raw": [0.0 if p in zero else 2.0 for p in pairs], "max_sig": 0.5})

    def layer(pairs, names):
        src = np.array([p[0] for p in pairs], dtype=np.int64)
        dst = np.array([p[1] for p in pairs], dtype=np.int64)
        return crawl.Layer(src, dst, {k: np.array([0.0 if p in zero else 1.0 for p in pairs]) for k in names})

    g = graphs.Graphs("t1", frame(allow, "w_er"), frame(transfer, "w_awp"))
    cg = crawl.CrawlGraph(np.array([w.contract(i) for i in range(n)], dtype=object),
                          layer(allow, crawl.ALLOW_WEIGHTS), layer(transfer, crawl.TRANSFER_WEIGHTS))
    ids = np.array([0, 1, 2, 3, 4, 5, 6, 9])                    # 9 is no node
    got = getattr(graphs, NAMES["union_in_degree"])(g, ids)
    expected = pd.Series(cg.union_in_degree(), index=np.arange(n)).reindex(ids, fill_value=0)
    assert got.index.tolist() == ids.tolist() and got.tolist() == expected.tolist()
    assert got.tolist() == [1, 2, 3, 0, 0, 0, 0, 0]               # 2: from 1, 4 and 6 (a pair of weight 0)
    inside = getattr(graphs, NAMES["in_union_graph"])(g, ids)
    assert inside.tolist() == [True, True, True, False, True, False, True, False]


def test_uncapped_sensitivity_uses_the_uncapped_layer_and_decides_nothing(c12_runs):
    """E9 (revision section 5, D4): the uncapped sensitivity scores the W0 and W1 spenders of the main summaries on
    the uncapped allowance layer beside the same transfer layer, and counts the baselines of section 9 on that graph
    (from the world's uncapped tables: the in-approve degree and value and the union in-degree move with it, the
    in-degree of the transfer layer does not); only run_robustness reads the uncapped stems; it decides no rule; the
    slope and sample blocks are still there."""
    world = c12_runs["world"]
    rob = record(c12_runs, "run_robustness")
    for script, labels in (("run_holdout", W0_LABELS), ("run_registered", W1_LABELS)):
        name, tag = COHORTS[script][:2]
        ids = world.contracts(name)
        main = B_main(record(c12_runs, script), len(ids), labels)
        found = [b["vectors"] for b in w.boots(rob, n=len(ids), has=(*METHODS, *labels))
                 if all(b["vectors"][x] == main[x] for x in labels)]
        assert len(found) == 1, f"{script}: one bootstrap of the uncapped sensitivity with the main labels"
        U = found[0]
        for m in ("awp", "cpr_l0"):                               # the transfer layer is the same
            assert U[m] == main[m], (script, m)
        prefix = "t1_" if tag == "t1" else ""
        uncapped = world_baselines(world, tag, ids, allow_stem="allow_pairs_uncapped")
        capped = world_baselines(world, tag, ids)
        assert sorted(prefix + b for b in uncapped) == sorted(COHORTS[script][4]), script
        for base, values in uncapped.items():                     # counted on the uncapped graph, not the capped one
            if base == "in_approve_value":
                np.testing.assert_allclose(U[prefix + base], values, rtol=1e-12, atol=0, err_msg=f"{script} {base}")
            else:
                assert U[prefix + base] == values, (script, base)
        assert uncapped["in_degree"] == capped["in_degree"] == main[prefix + "in_degree"], script
        gain = sorted(set(world.uncapped_gain) & set(ids))
        assert gain == [60, 70], script
        for i in gain:                    # at least 10 in-edges that only the uncapped layer holds (c12_world)
            k = ids.index(i)
            assert U[prefix + "in_approve_degree"][k] >= main[prefix + "in_approve_degree"][k] + 10, (script, i)
            assert U[prefix + "in_degree_union"][k] >= main[prefix + "in_degree_union"][k], (script, i)
            if script == "run_holdout":
                assert U["endorserank"][k] != main["endorserank"][k], i
    stems = {f"{w.GRAPH_REL}/allow_pairs_uncapped_{tag}" for tag in ("t1", "tobs")}
    assert stems <= set(rob["read_parts"])
    for s in ("run_same_window", "run_holdout", "run_registered"):
        assert not [r for r in record(c12_runs, s)["read_parts"] if "uncapped" in r], s
    out = summary(c12_runs, "run_robustness")
    block = out[NAMES["uncapped"]]
    assert {"w0", "w1"} <= set(block) and noted(block) and block in noted(out)
    assert not all_keys(block) & VERDICT_KEYS, sorted(all_keys(block) & VERDICT_KEYS)
    for window, tag in (("w0", "t1"), ("w1", "tobs")):
        assert block[window]["allowance_pairs"] == {"capped": world.rows[f"allow_pairs_{tag}"],
                                                    "uncapped": world.rows[f"allow_pairs_uncapped_{tag}"]}
    assert "value_slope" in out and "sample_definition" in out


# --------------------------------------------------------------------------- labels, cohorts and nodes


@pytest.mark.parametrize("script, window", [("run_holdout", "w0"), ("run_registered", "w1")])
def test_label_split_is_a_description(c12_runs, script, window):
    """E10 (revision section 8, D8): each label's total over the contract spenders, its parts from user accounts,
    contracts and other accounts (they add up), the means of the two rates, all from the world's tables; no score
    vector, contrast or τ is named after a part."""
    world, s = c12_runs["world"], summary(c12_runs, script)
    spenders = set(world.members(f"spenders_{window}", "contract"))
    lab = world.u12_frames[f"labels_{window}"].set_index("wallet")
    split = world.frames[f"label_split_{window}"].set_index("wallet")
    lab, split = lab.loc[lab.index.isin(spenders)], split.loc[split.index.isin(spenders)]
    assert len(lab) == len(split) == len(spenders)
    block = s[NAMES["label_split"]]
    assert block["spenders"] == len(spenders) and not all_keys(block) & VERDICT_KEYS
    parts = dict(zip(NAMES["split_parts"], w.PARTS))
    for col in w.LABELS:
        got = block["labels"][col]
        if col in ("future_revoke_rate", "future_keep_rate"):
            assert abs(got["mean"] - lab[col].mean()) <= 1e-12, col
            assert abs(sum(got[f"mean_{k}"] for k in parts) - got["mean"]) <= 1e-9, col
            for k, p in parts.items():
                assert abs(got[f"mean_{k}"] - split[f"{col}_{p}"].mean()) <= 1e-12, (col, k)
        elif col == "future_revoke_value":
            total = float(lab[col].sum())
            assert abs(got["total"] - total) <= 1e-9 * max(1.0, abs(total)), col
            assert abs(sum(got[k] for k in parts) - got["total"]) <= 1e-9 * max(1.0, abs(total)), col
            for k, p in parts.items():
                assert abs(got[k] - float(split[f"{col}_{p}"].sum())) <= 1e-9 * max(1.0, abs(total)), (col, k)
        else:
            assert got["total"] == int(lab[col].sum()), col
            assert sum(got[k] for k in parts) == got["total"], col
            for k, p in parts.items():
                assert got[k] == int(split[f"{col}_{p}"].sum()), (col, k)
    for r in c12_runs["runs"].values():
        named = {v for b in r["rec"]["boot"] for v in b["vectors"]}
        assert not named & SPLIT_COLUMNS and not [v for v in named if re.search(r"_(user|contract|other)$", v)]
    outside = {k: v for k, v in s.items() if k != NAMES["label_split"]}
    assert not set(strings(outside)) & SPLIT_COLUMNS


def test_a_label_split_that_does_not_add_up_is_refused(tmp_path):
    """E10, refusal (T18): a part of label_split_w0 one higher than the label (its parts rehashed by the download
    record, so that the download check passes) makes run_holdout refuse, naming the stem and the spender."""
    exp, world = c12_variant(tmp_path / "sandbox", "split_off")
    out = w.run_script(exp, "run_holdout", "contract12m", rec=tmp_path / "rec.json")
    err = out.stderr
    assert out.returncode != 0 and "refused:" in err and "label_split_w0" in err and "do not add up" in err, err
    assert world.target["address"] in err, err
    assert not output_folders(exp)


def test_cohorts_and_spender_classes_follow_the_new_reads(c12_runs):
    """E11 (revision section 8, D7): the spender classes are the members table's (every class, untyped 0), the
    matched cohort is its contract members (= nodes.is_cohort), and the system spender is reported, not refused."""
    world = c12_runs["world"]
    for script, name, n in (("run_holdout", "spenders_w0", 50), ("run_registered", "spenders_w1", 51)):
        counts = Counter(c for _, c, _ in world.lists[name])
        expected = {c: counts.get(c, 0) for c in ("contract", "user_account", "system", "untyped")}
        assert expected == {"contract": n, "user_account": 2, "system": 1, "untyped": 0}
        assert summary(c12_runs, script)[NAMES["spender_account_types"]] == expected, script
    s = summary(c12_runs, "run_same_window")
    nodes = world.frames["nodes"]
    cohort = sorted(int(i) for i in nodes.loc[nodes["is_cohort"], "id"])
    assert cohort == world.cohort_tobs and s["cohort"] == len(cohort) == 40
    by_class = s["members"]["cohort_tobs"]["by_class"]
    assert by_class == {"contract": 40, "user_account": 5, "system": 0, "untyped": 0}
    assert B_main(record(c12_runs, "run_same_window"), 40, PROXIES)


def test_an_untyped_spender_is_refused(tmp_path):
    """E11, refusal: an untyped W1 spender makes run_registered refuse (job 42 spender_untyped_w1)."""
    exp, world = c12_variant(tmp_path / "sandbox", "untyped_spender")
    out = w.run_script(exp, "run_registered", "contract12m", rec=tmp_path / "rec.json")
    err = out.stderr
    assert out.returncode != 0 and "refused:" in err and "untyped" in err and world.target["address"] in err, err
    assert not output_folders(exp)


CLASSES = r"""
    import json, sys
    from pathlib import Path
    sys.path.insert(0, sys.argv[2])
    import common
    import labels

    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    cls = labels.contract_types(spec["addresses"])
    print(json.dumps({"classes": {a: (c if isinstance(c, str) else None) for a, c in cls.items()},
                      "code_hashes": list(common.SMART_ACCOUNT_CODE_HASHES)}))
"""
NODE_CLASS = {"node_typed_eoa": "eoa", "node_listed_smart_account": "smart_account"}


@pytest.mark.parametrize("change", list(NODE_CLASS))
def test_every_node_is_a_contract(tmp_path, change):
    """E12 (plan section 8, revision sections 5 and 13): a node that is not a contract under the account types makes
    every evaluation script refuse, naming it with its class (run_robustness given summaries of the three scripts
    before it that record this download, since it checks them first); the clean world passes (the module's clean
    runs). The classes are those of the typing output with the smart-account lists of the amendment of 9 November
    2026 applied, as sql/31 reads them. Two such nodes: one typed eoa, and one that the typing output types a
    contract on a listed code hash, which labels.contract_types counts as a smart account, a user account (a contract
    off the lists stays a contract, a smart account of the reads stays one)."""
    exp, world = c12_variant(tmp_path / "sandbox", change)
    assert world.target["id"] == 120
    target = world.target["address"]
    if change == "node_listed_smart_account":
        row = world.types_frame.set_index("address").loc[target]
        got = run_code(CLASSES, "contract12m", {"addresses": [target, w.contract(119), w.user(11)]},
                       tmp_path / "classes", cwd=exp, args=(str(exp / "scripts"),))
        assert (row["account_class"], row["code_hash"]) == ("contract", got["code_hashes"][0])
        assert got["classes"] == {target: "smart_account", w.contract(119): "contract", w.user(11): "smart_account"}
    for s in w.C12_SCRIPTS:
        if s == "run_robustness":     # it first checks the outputs of the three before it (EVAL-2), which refused
            earlier_summaries(exp, world)
        out = w.run_script(exp, s, "contract12m", rec=tmp_path / f"rec_{s}.json")
        err = out.stderr
        assert out.returncode != 0 and "refused:" in err and f"{target} ({NODE_CLASS[change]})" in err, (s, err)
        if s == "run_robustness":
            assert output_folders(exp) == sorted(EARLIER), output_folders(exp)
        else:
            assert not output_folders(exp), s


# --------------------------------------------------------------------------- the commit and download refusals


REQUIRE = r"""
    import json, subprocess, sys
    from pathlib import Path
    sys.path.insert(0, sys.argv[2])
    import common

    def fail(*args, **kwargs):
        raise AssertionError("called")

    if common.VARIANT != "contract12m":                # earlier variants: no git command, nothing read
        subprocess.run = fail
        common.load_json = fail
    out = []
    for case in json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")):
        try:
            got = {"committed": common.require_committed(*case["files"]),
                   "downloaded": common.require_downloaded(*case["stems"])} if case["both"] else \
                {"committed": common.require_committed(*case["files"])}
            out.append({"result": got})
        except SystemExit as e:
            out.append({"exit": str(e)})
    print(json.dumps(out))
"""


def test_require_committed_refuses_in_this_variant_only(tmp_path):
    """E13, unit (D18; M4 g; H1): require_committed returns HEAD and the SHA-256 of common.EVAL_COMMITTED and its
    files, and refuses a file with local changes and an untracked one; under every earlier variant both require_*
    return None without any git command or read."""
    root = tmp_path / "sandbox"
    exp, _ = c12_variant(root, None)
    head = w.sandbox_git(exp, "rev-parse", "HEAD").strip()
    rel = "scripts/graphs.py"
    case = [{"files": [rel], "stems": [], "both": False}]
    run = lambda name, v: run_code(REQUIRE, v, case, tmp_path / name, cwd=exp, git_root=root,  # noqa: E731
                                   args=(str(exp / "scripts"),))
    (got,) = run("clean", "contract12m")
    committed = ("docs/revision_contract_graph.md", "config/overlay_contract12m.yaml",
                 "config/contract_reputation.yaml", "scripts/common.py", rel)
    assert got == {"result": {"committed": {"head": head, "sha256": {
        r: hashlib.sha256((exp / r).read_bytes()).hexdigest() for r in committed}}}}, got
    refusal = f"{NAMES['not_committed']} {rel}"
    path = exp / rel
    path.write_bytes(path.read_bytes() + b"\n")
    assert run("modified", "contract12m") == [{"exit": refusal}]
    w.sandbox_git(exp, "checkout", "-q", "--", rel)
    w.sandbox_git(exp, "rm", "--cached", "-q", rel)
    assert run("untracked", "contract12m") == [{"exit": refusal}]
    w.sandbox_git(exp, "add", "--", rel)
    assert not w.sandbox_git(exp, "status", "--porcelain", "--", "scripts", "config", "docs").strip()
    both = [{"files": [rel, "scripts/x.py"], "stems": ["nodes", "no_such_stem"], "both": True}]
    for v in w.EARLIER_VARIANTS:
        assert run_code(REQUIRE, v, both, tmp_path / v, cwd=exp, git_root=root, args=(str(exp / "scripts"),)) == [
            {"result": {"committed": None, "downloaded": None}}], v


def test_evaluation_scripts_record_their_provenance(c12_runs):
    """E13, clean runs (I2, M4 g): each output records the sandbox HEAD and the SHA-256 of the revision, the overlay,
    the base configuration and every project module the script imports (and docs/registration_w1.md for
    run_registered), transitively and inside functions too (T8); and, under inputs, every gate B stem the script
    read (its recorded read_parts) with the SHA-256 of each of its parts, the record of the download step (F4)."""
    exp = c12_runs["exp"]
    docs = {"docs/revision_contract_graph.md", "config/overlay_contract12m.yaml", "config/contract_reputation.yaml"}
    record_of_download = json.loads((exp / w.MANIFEST_REL).read_text(encoding="utf-8"))["results"]["download"]["files"]
    for s in w.C12_SCRIPTS:
        prov = summary(c12_runs, s)[NAMES["provenance"]]
        expected = docs | w.project_imports(s, exp / "scripts") | (
            {"docs/registration_w1.md"} if s == "run_registered" else set())
        assert prov["head"] == c12_runs["head"], s
        assert set(prov["sha256"]) == expected, (s, sorted(set(prov["sha256"]) ^ expected))
        for rel, digest in prov["sha256"].items():
            assert digest == hashlib.sha256((exp / rel).read_bytes()).hexdigest(), (s, rel)
        read = {r.split("/")[-1] for r in record(c12_runs, s)["read_parts"] if r.startswith(w.GRAPH_REL + "/")}
        inputs = prov["inputs"]
        assert read and read <= set(inputs), (s, sorted(read - set(inputs)))
        assert set(inputs) <= set(w.INTERFACE), (s, sorted(set(inputs) - set(w.INTERFACE)))
        for stem, parts in inputs.items():
            assert parts and parts == w.part_sha256(exp / w.GRAPH_REL / stem) == record_of_download[stem]["sha256"], (
                s, stem)


def changed(world: w.World, stem: str) -> pd.DataFrame:
    """The world's frame of ``stem`` with its first double column raised by one: other content, other parts."""
    col = next(c for c, t in w.INTERFACE[stem].items() if t == "double")
    frame = world.frames[stem].copy()
    frame[col] = frame[col] + 1.0
    return frame


def graph_stems(exp: Path, script: str) -> tuple[str, ...]:
    """GRAPH_STEMS of the sandbox's scripts/<script>.py, the gate B stems it verifies and records as its inputs."""
    tree = ast.parse((exp / "scripts" / f"{script}.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "GRAPH_STEMS"
                                                for t in node.targets):
            return tuple(ast.literal_eval(node.value))
    raise AssertionError(f"{script}.py defines no GRAPH_STEMS")


# script -> a gate B stem it reads that no other evaluation script of its run needs (F4: a GRAPH_STEMS without it
# would read it unverified)
TAMPERED = {"run_same_window": "proxies_tobs", "run_holdout": "label_split_w0", "run_registered": "label_split_w1",
            "run_robustness": "allow_pairs_uncapped_t1"}


@pytest.mark.parametrize("script", list(TAMPERED))
def test_evaluation_scripts_refuse_a_stem_the_download_did_not_verify(tmp_path, script):
    """E17 through the scripts (F4; revision section 13: every evaluation script reads the gate B tables only as the
    download step verified them): a stem the script reads, rewritten with other content after the download step
    recorded its parts, makes the script refuse, naming it, before it reads a table, scores or bootstraps anything;
    nothing is written."""
    exp, world = c12_variant(tmp_path / "sandbox", None)
    stem = TAMPERED[script]
    assert stem in graph_stems(exp, script)
    recorded = w.part_sha256(world.stem(stem))
    w.write_stem(world, stem, changed(world, stem), rehashed=False)
    assert w.part_sha256(world.stem(stem)) != recorded
    rec = tmp_path / "rec.json"
    out = w.run_script(exp, script, "contract12m", rec=rec)
    err = out.stderr
    assert out.returncode != 0 and (f"refused: the parts of graph-tables-contract-12m/{stem} are not those the "
                                    "download step verified") in err, err[-3000:]
    logged = w.load_record(rec)
    assert logged["read_parts"] == [] and logged["boot"] == [] and logged["score_all"] == [], logged["read_parts"]
    assert not output_folders(exp)


EARLIER = {"same-window": "run_same_window", "holdout-w0": "run_holdout", "window-w1": "run_registered"}


def earlier_summaries(exp: Path, world: w.World, *, skip: str | None = None, bare: str | None = None) -> None:
    """The eval summaries of the three scripts before run_robustness as they record their provenance inputs on the
    world's current download (the parts of every stem of their GRAPH_STEMS), but ``skip`` missing and ``bare``
    without provenance inputs; run_robustness reads nothing else of them before its refusals."""
    for folder, script in EARLIER.items():
        path = exp / w.PROC_REL / folder / "eval_summary.json"
        path.unlink(missing_ok=True)
        if folder == skip:
            continue
        prov = {"head": "abc123"} if folder == bare else {
            "inputs": {s: w.part_sha256(world.stem(s)) for s in graph_stems(exp, script)}}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"provenance": prov}), encoding="utf-8")


def test_robustness_refuses_evaluations_of_another_download(tmp_path):
    """EVAL-2 (revision section 13): run_robustness joins the outputs of the earlier evaluations by node id to scores
    it computes from the current tables, so it refuses unless the gate B inputs each of their summaries records are
    the parts of the last verified download: after a new download that changed proxies_tobs (which run_robustness
    does not read itself) or label_split_w1, with a summary that records no inputs or is missing, and with a stem of
    those inputs that the download did not verify. Each refusal names the folder or the stem and comes before any
    table is read, scored or bootstrapped; nothing is written."""
    exp, world = c12_variant(tmp_path / "sandbox", None)
    stems = {folder: graph_stems(exp, script) for folder, script in EARLIER.items()}
    assert "proxies_tobs" in stems["same-window"] and "label_split_w1" in stems["window-w1"]
    assert not {"proxies_tobs", "label_split_w1"} & set(graph_stems(exp, "run_robustness"))
    original = {s: world.frames[s].copy() for s in ("proxies_tobs", "label_split_w1")}

    def refusal(name: str) -> str:
        rec = tmp_path / f"rec_{name}.json"
        out = w.run_script(exp, "run_robustness", "contract12m", rec=rec)
        logged = w.load_record(rec)
        assert out.returncode != 0, (name, out.stdout[-2000:])
        assert logged["read_parts"] == [] and logged["boot"] == [] and logged["score_all"] == [], name
        assert not (exp / w.PROC_REL / "robustness").exists(), name
        (line,) = [x for x in out.stderr.splitlines() if x.startswith("refused:")]
        return line

    def reset() -> None:
        for s, frame in original.items():
            w.write_stem(world, s, frame)
        earlier_summaries(exp, world)

    again = ("refused: {} was computed from gate B tables other than those of the last download; run "
             "scripts/{}.py again before scripts/run_robustness.py")
    none = ("refused: {}/eval_summary.json records no gate B inputs (provenance.inputs); run scripts/{}.py before "
            "scripts/run_robustness.py")
    reset()
    w.write_stem(world, "proxies_tobs", changed(world, "proxies_tobs"))         # rest, checks and download again
    assert refusal("new_proxies") == again.format("same-window", "run_same_window")
    reset()
    w.write_stem(world, "label_split_w1", changed(world, "label_split_w1"))
    assert refusal("new_split") == again.format("window-w1", "run_registered")
    reset()
    earlier_summaries(exp, world, bare="holdout-w0")
    assert refusal("no_inputs") == none.format("holdout-w0", "run_holdout")
    earlier_summaries(exp, world, skip="window-w1")
    assert refusal("missing") == none.format("window-w1", "run_registered")
    reset()
    w.write_stem(world, "proxies_tobs", changed(world, "proxies_tobs"), rehashed=False)   # not a download at all
    assert refusal("unverified").startswith("refused: the parts of graph-tables-contract-12m/proxies_tobs are not "
                                            "those the download step verified")


DIRTY = {   # script -> (file, how): a local change (one more line) or a file made untracked
    "run_same_window": (("scripts/run_same_window.py", "modified"), ("scripts/graphs.py", "modified"),
                        ("scripts/stats.py", "untracked")),
    "run_holdout": (("scripts/run_holdout.py", "modified"), ("scripts/graphs.py", "modified"),
                    ("docs/revision_contract_graph.md", "modified"), ("config/overlay_contract12m.yaml", "modified"),
                    ("config/contract_reputation.yaml", "modified")),
    "run_registered": (("scripts/run_registered.py", "modified"), ("scripts/graphs.py", "modified"),
                       ("docs/registration_w1.md", "modified")),
    "run_robustness": (("scripts/run_robustness.py", "modified"), ("scripts/graphs.py", "modified")),
}


@pytest.mark.parametrize("script", list(DIRTY))
def test_evaluation_scripts_refuse_unless_committed(tmp_path, script):
    """E13 (D18, revision section 12): a file the script needs with a local change, or untracked, makes it refuse
    before it reads any input or writes any output; the file restored, the next case starts from HEAD."""
    exp, _ = c12_variant(tmp_path / "sandbox", None)
    for k, (rel, how) in enumerate(DIRTY[script]):
        path = exp / rel
        if how == "modified":
            path.write_bytes(path.read_bytes() + b"\n")
        else:
            w.sandbox_git(exp, "rm", "--cached", "-q", rel)
        rec = tmp_path / f"rec_{k}.json"
        out = w.run_script(exp, script, "contract12m", rec=rec)
        assert out.returncode != 0 and NAMES["not_committed"] in out.stderr and rel in out.stderr, (rel, out.stderr)
        assert not output_folders(exp), rel
        logged = w.load_record(rec)
        assert logged["read_parts"] == [] and logged["boot"] == [] and logged["score_all"] == [], rel
        if how == "untracked":
            w.sandbox_git(exp, "add", "--", rel)
        w.sandbox_git(exp, "checkout", "-q", "--", rel)
        assert not w.sandbox_git(exp, "status", "--porcelain", "--", "scripts", "config", "docs").strip(), rel


DOWNLOADED = r"""
    import json, sys
    from pathlib import Path
    sys.path.insert(0, sys.argv[2])
    import common

    common.GRAPH = Path(sys.argv[3])
    out = []
    for case in json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")):
        common.PROC = Path(case["proc"])
        try:
            out.append({"result": common.require_downloaded(*case["stems"])})
        except SystemExit as e:
            out.append({"exit": str(e)})
    print(json.dumps(out))
"""


def test_evaluation_reads_only_the_verified_downloads(tmp_path):
    """E17 (H1; EVAL 16.3 item 8): require_downloaded refuses without the run manifest, without a last passing checks
    or download, when a gate B step ran after the last download, when constants, pairs or rest ran after the last
    checks, and when the parts of a stem are not those the download step recorded (or not recorded); otherwise it
    returns the SHA-256 of every part."""
    exp = tmp_path / "world" / "experiments"
    world = w.contract_world(exp)
    good = json.loads(world.manifest.read_text(encoding="utf-8"))
    stems = ["nodes", "allow_pairs_tobs", "proxies_tobs", "label_split_w0", "members"]

    def steps(*names, failed=()):
        return [{"step": s, "passed": s not in failed or k != max(i for i, x in enumerate(names) if x == s)}
                for k, s in enumerate(names)]

    def files(change=None):
        f = json.loads(json.dumps(good["results"]["download"]["files"]))
        if change == "sha":
            f["proxies_tobs"]["sha256"] = {p: "0" * 64 for p in f["proxies_tobs"]["sha256"]}
        elif change == "unrecorded":
            del f["label_split_w0"]
        return f

    gate_b = w.GATE_B_STEPS
    cases = {
        "missing": None,
        "no_checks": {"steps": steps("constants", "pairs", "rest", "download"), "files": files()},
        "checks_failed": {"steps": steps(*gate_b, failed=("checks",)), "files": files()},
        "last_checks_failed": {"steps": steps(*gate_b[:4], "checks", "download", failed=("checks",)),
                               "files": files()},
        "download_failed": {"steps": steps(*gate_b, failed=("download",)), "files": files()},
        "rest_after_download": {"steps": steps(*gate_b, "rest"), "files": files()},
        "checks_after_download": {"steps": steps(*gate_b, "checks"), "files": files()},
        "rest_after_checks": {"steps": steps(*gate_b[:4], "rest", "download"), "files": files()},
        "constants_and_pairs_after_checks": {"steps": steps(*gate_b[:4], "constants", "pairs", "download"),
                                             "files": files()},
        "parts_changed": {"steps": steps(*gate_b), "files": files("sha")},
        "parts_unrecorded": {"steps": steps(*gate_b), "files": files("unrecorded")},
        "passes": {"steps": steps(*gate_b), "files": files()},
        "passes_after_a_second_download": {"steps": steps(*gate_b, "rest", "checks", "download"), "files": files()},
    }
    spec = []
    for name, m in cases.items():
        proc = tmp_path / "proc" / name
        proc.mkdir(parents=True)
        if m is not None:
            (proc / "run_manifest.json").write_text(json.dumps({"variant": "contract12m", "steps": m["steps"],
                                                                "jobs": [], "results": {"download": {
                                                                    "files": m["files"]}}}), encoding="utf-8")
        spec.append({"proc": str(proc), "stems": stems})
    got = dict(zip(cases, run_code(DOWNLOADED, "contract12m", spec, tmp_path / "run", cwd=exp,
                                   args=(str(SCRIPTS), str(world.graph)))))
    expected_refusals = {
        "missing": "run_manifest.json is missing; the evaluation reads the gate B tables only after the checks and "
                   "download steps",
        "no_checks": "records no last run of the step checks that passed",
        "checks_failed": "records no last run of the step checks that passed",
        "last_checks_failed": "records no last run of the step checks that passed",
        "download_failed": "records no last run of the step download that passed",
        "rest_after_download": "refused: rest ran after the last download",
        "checks_after_download": "refused: checks ran after the last download",
        "rest_after_checks": "refused: rest ran after the last checks",
        "constants_and_pairs_after_checks": "refused: constants, pairs ran after the last checks",
        "parts_changed": "refused: the parts of graph-tables-contract-12m/proxies_tobs are not those the download step "
                         "verified",
        "parts_unrecorded": "refused: the parts of graph-tables-contract-12m/label_split_w0 are not those the download "
                            "step verified",
    }
    for name, text in expected_refusals.items():
        assert "exit" in got[name] and got[name]["exit"].startswith("refused:") and text in got[name]["exit"], (
            name, got[name])
    for name in ("passes", "passes_after_a_second_download"):
        assert got[name] == {"result": {s: w.part_sha256(world.stem(s)) for s in stems}}, (name, got[name])


# --------------------------------------------------------------------------- rule A, outputs and unfinished scripts


PREFIXED = [("C-PR minus C-PR (l=1)", "cpr_l50", "cpr_l100", APPR),     # rule A, docs/analysis_plan.md
            ("C-PR minus C-PR (l=0)", "cpr_l50", "cpr_l0", SEND)]


def test_rule_a_on_the_contract_graph(c12_runs):
    """E14 (revision section 11, D10): rule A's primary part on W0 and its secondary part on the matched cohort are
    read from their own contrasts and family means; the matched cohort's proxies are those of proxies_tobs and its
    allowance family the raw degrees on the capped T_obs graph."""
    world = c12_runs["world"]
    h = summary(c12_runs, "run_holdout")
    rows = h["contrasts_prefixed"]
    assert [(r["label"], r["a"], r["b"], r["outcome"]) for r in rows] == PREFIXED
    appr, send = rows
    ra = h["rule_a_primary"]
    assert ra["no_worse_on_new_approvals"] is (appr["ci_high"] >= 0)
    assert ra["better_on_new_senders"] is (send["ci_low"] > 0)
    assert ra["pass"] is (ra["no_worse_on_new_approvals"] and ra["better_on_new_senders"])
    s = summary(c12_runs, "run_same_window")
    sec, fam = s["rule_a_secondary"], s["families"]
    for f in ("transfer", "allowance"):
        best = sec[f]["best_layer"]
        other = {"cpr_l100": "cpr_l0", "cpr_l0": "cpr_l100"}[best]
        assert fam[best][f]["mean_tau"] >= fam[other][f]["mean_tau"], f
        assert sec[f]["best_ci"] == [fam[best][f]["ci_low"], fam[best][f]["ci_high"]], f
        assert sec[f]["cpr"] == fam["cpr_l50"][f]["mean_tau"], f
        assert sec[f]["pass"] is (sec[f]["best_ci"][0] <= sec[f]["cpr"] <= sec[f]["best_ci"][1]), f
    syb = {m: fam[m]["sybil_stability"]["mean_tau"] for m in ("cpr_l50", "cpr_l100", "cpr_l0")}
    assert sec["sybil_stability"]["pass"] is (syb["cpr_l50"] > max(syb["cpr_l100"], syb["cpr_l0"]))
    assert sec["pass"] is all(sec[k]["pass"] for k in ("transfer", "allowance", "sybil_stability"))
    ids = world.cohort_tobs
    M = B_main(record(c12_runs, "run_same_window"), len(ids), PROXIES)
    prox = world.frames["proxies_tobs"].set_index("wallet").loc[[w.contract(i) for i in ids]]
    for c in ("in_degree", "in_value", "inbound_counterparty_ratio", "transfer_tenure_days", "active_months"):
        assert M[c] == [float(x) for x in prox[c]], c
    expected = world_baselines(world, "tobs", ids)
    assert M["in_approve_degree"] == expected["in_approve_degree"]
    np.testing.assert_allclose(M["in_approve_value"], expected["in_approve_value"], rtol=1e-12, atol=0)


def test_a_member_without_a_proxy_row_is_refused(tmp_path):
    """E14, refusal (T18): a member of the matched cohort without a row of proxies_tobs (it would become NaN and drop
    out of its τ) makes run_same_window refuse, naming the wallet."""
    exp, world = c12_variant(tmp_path / "sandbox", "proxy_missing")
    out = w.run_script(exp, "run_same_window", "contract12m", rec=tmp_path / "rec.json")
    err = out.stderr
    assert out.returncode != 0 and "refused:" in err and "proxies_tobs" in err and world.target["address"] in err, err
    assert not output_folders(exp)


def test_contract12m_writes_only_its_own_folders(c12_runs):
    """E15 (revision introduction and section 12): the runs wrote only under revised-contract-12m/{same-window,
    holdout-w0, window-w1, robustness}; nothing else changed or went missing, no registered-w1 folder was written, and
    no output speaks of registered results."""
    before, after = c12_runs["before"], c12_runs["after"]
    prefix = f"experiments/{w.PROC_REL}/"
    changed = sorted(k for k in after if before.get(k) != after[k])
    assert not sorted(set(before) - set(after))
    outside = [k for k in changed if not (k.startswith(prefix) and k[len(prefix):].split("/")[0] in FOLDERS)]
    assert not outside, outside
    assert {k[len(prefix):].split("/")[0] for k in changed} == set(FOLDERS)
    assert f"{prefix}window-w1/eval_summary.json" in after
    assert not [k for k in after if "/registered-w1/" in k]
    texts = [x for r in c12_runs["runs"].values() for x in (*strings(r["summary"]), r["stdout"], r["stderr"])]
    assert not [t[:120] for t in texts if REGISTERED_RESULTS.search(t)]


def test_unfinished_scripts_refuse_the_contract_graph_variant(tmp_path):
    """E16 (D22; T14): run_supplementary, sybil_model, describe_data, export_latex and publish_results refuse this
    variant before BigQuery (a fake client that raises), git (trapped) or any file is touched."""
    exp = w.sandbox(tmp_path / "sandbox")
    w.contract_world(exp)
    before = w.snapshot(exp.parent)
    for s in w.UNFINISHED_SCRIPTS:
        out = w.run_script(exp, s, "contract12m", traps=False, git_trap=True, fake_bigquery=True,
                           argv=["--no-figures"] if s == "export_latex" else ())
        err = out.stderr
        assert out.returncode != 0 and re.search(r"refused: .*(contract-graph|contract12m)", err), (s, err[-2000:])
        assert "AssertionError" not in err, (s, err[-2000:])
        assert w.snapshot(exp.parent) == before, s
    assert not (exp.parent / "dissertation").exists()
