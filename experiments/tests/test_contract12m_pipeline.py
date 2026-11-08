"""The driver of the contract-graph revision (scripts/run_contract12m_pipeline.py, docs/revision_contract_graph.md
section 12 and its gate B amendment of section 13): its gate A SQL files (sql/24 to 35 and 43), the gate B steps
(constants, pairs, rest, checks, download: sql/36 to 42), their refusals, estimates, projection and downloads, and the
match rule of scripts/balance_audit.py.

Nothing here reaches the network or BigQuery. The code of the variant runs in subprocesses with
CONTRACT_REP_VARIANT=contract12m, since scripts/common.py reads the variant once, at import. The gate B steps run in
trees under tmp_path (run_gate_b and the prelude GATE_B): copies of the committed files, a structure pilot, a
'Protocol fixed' block, a run manifest and a ledger, with git, the BigQuery client, the jobs and the downloads faked;
every test that runs a step in a tree also checks that the real ledger, run manifest, constants and gate B folders
are as they were."""

from __future__ import annotations

import ast
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import textwrap

import pytest
import yaml

import c12_world as w
from conftest import EXPERIMENTS, SCRIPTS

JOB_KEYS_A = {"logs5", "ends", "tx_senders", "emitters", "creations", "rpc_queue", "contracts", "bal_pre", "bal",
              "anchor_blocks", "bal_audit", "structure"}
JOB_KEYS_B = {"triples", "user_events", "constants", "pairs", "cohorts", "proxies", "labels_w0", "labels_w1",
              "node_ids", "importance", "checks"}
JOB_KEYS = JOB_KEYS_A | JOB_KEYS_B
VIEWS = {f"bigquery-public-data.goog_blockchain_arbitrum_one_us.{v}"
         for v in ("transactions", "receipts", "decoded_events", "blocks", "logs")}
GATE_B_STEPS = ("constants", "pairs", "rest", "checks", "download")
FIRST_JOB = {"constants": "triples", "pairs": "pairs", "rest": "cohorts", "checks": "checks"}
CONSTANTS_REL = "data/0-usd-token-list-and-prices/contract-12m/constants.json"
USD12M_CONSTANTS_REL = "data/0-usd-token-list-and-prices/usd-12m/constants.json"
MANIFEST_REL = "data/2-processed-tables-and-evaluations/revised-contract-12m/run_manifest.json"
LEDGER_REL = "data/bq_ledger.json"
FEASIBILITY_REL = "data/2-processed-tables-and-evaluations/revised-contract-12m/discovery/feasibility_t1.json"
# Paths a tree that is not rebound would write: they must be as they were after every run_gate_b.
REAL_PATHS = (LEDGER_REL, MANIFEST_REL, CONSTANTS_REL, USD12M_CONSTANTS_REL, w.GRAPH_REL, w.PROC_REL,
              "docs/discovery_protocol.md", "docs/revision_contract_graph.md")


def overlay_cap() -> float:
    overlay = yaml.safe_load((EXPERIMENTS / "config" / "overlay_contract12m.yaml").read_text(encoding="utf-8"))
    return float(overlay["contract_graph"]["campaign_cap_usd"])


CAP_USD = overlay_cap()


def amendment_lists() -> dict:
    """The smart-account lists of the amendment of 9 November 2026 as the revision itself writes them (section 13,
    the fenced json block with the key smart_account_extension)."""
    import re
    text = (EXPERIMENTS / "docs" / "revision_contract_graph.md").read_text(encoding="utf-8")
    blocks = [json.loads(b) for b in re.findall(r"^[ \t]*```json[ \t]*\n(.*?)\n[ \t]*```", text, flags=re.S | re.M)]
    found = [b["smart_account_extension"] for b in blocks if "smart_account_extension" in b]
    assert len(found) == 1, f"{len(found)} smart_account_extension blocks in the revision"
    return found[0]


SMART_HASHES = tuple(amendment_lists()["code_hashes"])
SMART_PAIRS = tuple(f"{h}:{i}" for h, i in amendment_lists()["code_hash_implementations"])


def run_py(code: str, variant: str | None = "contract12m", *args: str, cwd=SCRIPTS) -> subprocess.CompletedProcess:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
    env.pop("CONTRACT_REP_VARIANT", None)
    env.pop("CONTRACT_REP_RPC_URL", None)
    if variant:
        env["CONTRACT_REP_VARIANT"] = variant
    return subprocess.run([sys.executable, "-c", textwrap.dedent(code), *args], cwd=cwd, env=env, capture_output=True,
                          text=True, encoding="utf-8")


def run_json(code: str, variant: str | None = "contract12m", *args: str):
    out = run_py(code, variant, *args)
    assert out.returncode == 0, out.stdout[-2000:] + out.stderr[-4000:]
    return json.loads(out.stdout.strip().splitlines()[-1])


def real_state() -> dict:
    """REAL_PATHS under experiments/: the SHA-256 of a file, {path: (size, mtime)} of every file of a folder (its
    parquet parts can be large; a write changes them), None when absent."""
    out = {}
    for rel in REAL_PATHS:
        p = EXPERIMENTS / rel
        if not p.exists():
            out[rel] = None
        elif p.is_dir():
            out[rel] = {f.relative_to(p).as_posix(): (f.stat().st_size, f.stat().st_mtime_ns)
                        for f in sorted(p.rglob("*")) if f.is_file()}
        else:
            out[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def run_gate_b(tmp_path, body: str, cases, **spec) -> dict:
    """GATE_B + ``body`` in a contract12m subprocess; the case specification goes in tmp_path/spec.json (the command
    line of Windows is too short for it). Returns the JSON of the last stdout line, after checking that nothing of
    REAL_PATHS changed."""
    path = tmp_path / "spec.json"
    path.write_text(json.dumps({"tmp": str(tmp_path), "cases": cases, **spec}), encoding="utf-8")
    before = real_state()
    out = run_py(GATE_B + textwrap.dedent(body), "contract12m", str(path))
    assert real_state() == before, "a gate B step wrote into the real experiments folder"
    assert out.returncode == 0, out.stdout[-3000:] + out.stderr[-6000:]
    return json.loads(out.stdout.strip().splitlines()[-1])


# The prelude of every gate B subprocess: a tree per case (the committed files copied
# from experiments/, a pilot, 'Protocol fixed', a run manifest, a ledger), the driver's paths rebound to it, and fakes
# of git, the BigQuery client, the jobs, the table sizes and the projection.
GATE_B = textwrap.dedent(r'''
    import contextlib, hashlib, io, json, shutil, sys
    from datetime import datetime, timezone
    from pathlib import Path
    from types import SimpleNamespace
    from google.api_core.exceptions import NotFound
    import common, crawl, graphs
    import run_discovery as rd
    import run_contract12m_pipeline as d

    SPEC = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    EXP = common.ROOT                       # the real experiments folder: read only
    cfg = common.load_config()
    DCFG = json.loads(json.dumps(rd._clean(cfg["discovery"])))
    OLD = datetime(2026, 10, 28, tzinfo=timezone.utc)
    BIG = {"U": 100_000, "E_U": 200_000, "WCC": 150_000, "E_WCC": 300_000, "allow_capped_edges": 6000,
           "allow_in_share": 0.5}
    CONSTANTS = {"m_transfer_usd": 170.0, "m_allowance_usd": 100.0, "cap_allowance_usd": 19000.0,
                 "cap_user_usd": 2500.0, "b_transfer": 0.00646242522745947, "b_allowance": 0.010986122886681098}
    REAL = {n: getattr(d, n) for n in ("refuse_projected_cap", "list_rows", "sh")}
    REAL_JOB, REAL_SIZES, REAL_RUN = d.Run.job, d.Run.sizes, d.subprocess.run
    sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


    def rebind(root):
        d.ROOT = root
        d.MANIFEST, d.LEDGER = root / d.MANIFEST_REL, root / d.LEDGER_REL
        d.FEASIBILITY, d.PROTOCOL = root / d.FEASIBILITY_REL, root / "docs" / "discovery_protocol.md"
        d.USD_CONSTANTS = root / d.CONSTANTS_REL
        d.GRAPH = common.GRAPH = graphs.EXPORT = root / "data/1-raw-blockchain-extracts/graph-tables-contract-12m"
        d.PROC = root / "data/2-processed-tables-and-evaluations/revised-contract-12m"
        d.STRUCT_T1, d.BAL_AUDIT = d.GRAPH / "struct_t1", d.GRAPH / "bal_audit"
        d.ANCHOR_BLOCKS, d.BALANCE_AUDIT = d.GRAPH / "anchor_blocks", d.PROC / "typing" / "balance_audit.json"


    def write_pilot(root, inputs=BIG, change=None):     # fixed_setup of test_crawl.py at the real relative path
        rules = json.loads(json.dumps(rd._clean(crawl.rules(inputs, DCFG))))
        pilot = {"sizes": {k: inputs[k] for k in ("U", "E_U", "WCC", "E_WCC")}, "rules": rules, "rule_inputs": inputs,
                 "layers": {k: {"edges": inputs["allow_capped_edges"], "nodes": 0, "self_loops": 0}
                            for k in ("allow_capped", "allow_uncapped", "transfer")},
                 "capped_allowance_in_edge_share": {"U": inputs["allow_in_share"]},
                 "code": {"head": "abc123", "committed": {rel: True for rel in rd.COMMITTED}},
                 "discovery_config": DCFG, **(change or {})}
        common.save_json(pilot, root / d.FEASIBILITY_REL)
        return pilot


    def block_for(case, pilot, feas):    # case["block"]: "valid" (default) | "none" | "no_date" | "wrong_sha" | dict
        kind = case.get("block", "valid")
        if kind == "none":
            return None
        b = {"date": "2026-11-09", "feasibility": d.FEASIBILITY_REL, "sha256": sha(feas), **pilot["sizes"],
             "rho": pilot["rules"]["rho"], "q": pilot["rules"]["q"], "primary_mode": pilot["rules"]["primary_mode"]}
        if kind == "no_date":
            del b["date"]
        if kind == "wrong_sha":
            b["sha256"] = "0" * 64
        if isinstance(kind, dict):
            b.update(kind)
        return b


    def write_protocol(root, block):
        text = "# Protocol\n\n## 7. Rules\n\nText.\n\n## Protocol fixed\n\n(Added at gate B.)\n"
        if block is not None:
            text += "\nFixed by rule.\n\n```json\n" + json.dumps(block, indent=2) + "\n```\n"
        (root / "docs" / "discovery_protocol.md").write_text(text, encoding="utf-8")


    def tree(root, case):
        for rel in (*d.COMMITTED, *d.COMMITTED_B):
            if not rel.startswith("data/"):
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(EXP / rel, root / rel)
        feas = root / d.FEASIBILITY_REL
        if case.get("pilot"):                                      # the download step: the pilot of the synthetic world
            pilot = case["pilot"]
            common.save_json(pilot, feas)
        else:
            pilot = write_pilot(root, {**BIG, **case.get("pilot_inputs", {})})
        write_protocol(root, block_for(case, pilot, feas))
        steps = [{"step": s, "passed": True} for s in d.CHAIN_A]
        if case.get("structure") == "stopped":
            steps.append({"step": "structure", "passed": False})
        st = {"layers": case.get("layers", {"allow_capped": 5000, "allow_uncapped": 9000, "transfer": 20000}),
              "self_pairs": case.get("self_pairs", {"allow_capped": 10, "allow_uncapped": 12, "transfer": 30}),
              "pilot_exit_code": 0, "feasibility": {"path": d.FEASIBILITY_REL, "sha256": sha(feas)}}
        if case.get("structure") == "no_pilot":
            st["feasibility"] = None
        if case.get("structure") == "other_sha":
            st["feasibility"]["sha256"] = "f" * 64
        m = {"variant": "contract12m", "steps": steps, "jobs": [], "results": {"structure": st},
             "checks_run": [{"problems": case.get("check_problems", [])}]}
        c = case.get("constants")    # None | "written" | "committed" | "dirty" | "stale" | "failed" | a key of HELD
        if c:
            path = root / d.CONSTANTS_REL
            common.save_json({"computed_at": "2026-11-10T00:00:00+00:00", **CONSTANTS}, path)
            m["steps"].append({"step": "constants", "passed": c != "failed"})
            m["results"]["constants"] = {"path": d.CONSTANTS_REL,
                                         "constants_sha256": "0" * 64 if c == "stale" else sha(path)}
        m["steps"] += [{"step": s, "passed": p} for s, p in case.get("steps", [])]
        common.save_json(m, root / d.MANIFEST_REL)
        common.save_json({"usd_per_tib": 6.25, "jobs": [{"usd": case.get("campaign", 0.0),
                                                         "label": "contract12m: earlier", "variant": "contract12m",
                                                         "budget_usd": 60.0}]},
                         root / d.LEDGER_REL)


    # The files of the commit c0ffee that holds constants.json, by the case's constants state.
    HELD = {"mixed": (*d.CONSTANTS_COMMIT, "scripts/graphs.py"), "alone": (d.CONSTANTS_REL,),
            "no_ledger": (d.CONSTANTS_REL, d.MANIFEST_REL), "no_manifest": (d.CONSTANTS_REL, d.LEDGER_REL)}


    def fake_git(case):
        status = dict(case.get("status", {}))
        c = case.get("constants")
        log = {d.CONSTANTS_REL: "c0ffee" if c in ("committed", "mixed", "dirty", *HELD) else ""}
        log.update(case.get("log", {}))
        diff = {"c0ffee": "\n".join("experiments/" + r for r in HELD.get(c, d.CONSTANTS_COMMIT))}
        if case.get("constants") == "dirty":
            status[d.CONSTANTS_REL] = " M " + d.CONSTANTS_REL
        calls = []

        def git(*args):
            calls.append(list(args))
            if args[0] == "status":
                return status.get(args[-1], "")
            if args[:3] == ("log", "-1", "--format=%H"):
                return log.get(args[-1], "abc123")
            if args[0] == "log":
                return "abc123 2026-11-07T00:00:00+00:00"
            if args == ("rev-parse", "HEAD"):
                return "abc123"
            if args == ("rev-parse", "--show-prefix"):
                return "experiments/"
            if args[0] == "diff-tree":
                return diff.get(args[-1], "")
            raise AssertionError(f"unexpected git {args}")
        return git, calls


    class FakeClient:   # the free metadata and tabledata calls the driver makes
        def __init__(self, tables, rows):
            self.tables, self.rows = tables, rows

        def get_table(self, name):
            key = name.split("contract_rep.", 1)[-1]
            if key not in self.tables:
                raise NotFound(name)
            t = self.tables[key]
            return SimpleNamespace(num_rows=t.get("rows", 0), num_bytes=t.get("bytes", 0), expires=None,
                                   time_partitioning=SimpleNamespace(type_="MONTH", field="block_timestamp")
                                   if t.get("partitioned") else None,
                                   modified=datetime.fromisoformat(t["modified"]) if "modified" in t else OLD,
                                   schema=[SimpleNamespace(name=k, field_type=v)
                                           for k, v in t.get("schema", {}).items()])

        def list_rows(self, name):
            return [dict(r) for r in self.rows[name.split("contract_rep.", 1)[-1]]]

        def get_dataset(self, ds):
            return SimpleNamespace(default_table_expiration_ms=None, default_partition_expiration_ms=None)

        def list_tables(self, ds, max_results=None):
            return [SimpleNamespace(table_id=k) for k in self.tables]


    def tables_for(case):   # SOURCES and SOURCES_B as they were, plus the case's tables, without case["drop"]
        t = {n: {"rows": 1000, "partitioned": n in ("logs_obs", "logs_w1", "u_approvals", "u_transfers",
                                                   "u_approvals_w1", "u_transfers_w1")}
             for n in (*d.SOURCES, *d.SOURCES_B)}
        t["u_tokens"]["rows"] = 5
        t.update(case.get("tables", {}))
        for name in case.get("drop", []):
            t.pop(name, None)
        return t


    def prepare(name, case):     # the tree and every fake of one case
        root = Path(SPEC["tmp"]) / name
        tree(root, case)
        rebind(root)
        d.git, git_calls = fake_git(case)

        def client(cfg):
            if case.get("client") == "raise":                      # proves that a refusal came first
                raise SystemExit("client created")
            return FakeClient(tables_for(case), case.get("rows", {})), "dissertation-bq.contract_rep"
        d.client_and_dataset = client
        calls, seen = [], []

        def job(self, j):
            calls.append(f"job {j.no} {j.key}")
            seen.append({"key": j.key, "params": j.params})
            if case.get("stop_at_job", True):
                raise SystemExit(f"reached {j.key}")
        d.Run.job = REAL_JOB if case.get("real_job") else job
        d.Run.sizes = REAL_SIZES if "sizes" not in case else (lambda self, *n: {k: case["sizes"][k] for k in n})
        d.refuse_projected_cap = REAL["refuse_projected_cap"] if case.get("projection") == "real" else \
            (lambda client, ds, m, step, cfg: {"usd": 0.0, "faked": True})
        d.sh, d.subprocess.run = REAL["sh"], REAL_RUN
        d.AUTHOR_DECISION = case.get("author")
        return root, calls, seen, git_calls


    def run_case(name, case, steps, setup=None):
        root, calls, seen, git_calls = prepare(name, case)
        if setup:
            setup(root)
        before = (root / d.MANIFEST_REL).read_bytes()
        results, out = [], io.StringIO()
        with contextlib.redirect_stdout(out):
            for step in steps:
                try:
                    getattr(d, f"step_{step}")(cfg, bool(case.get("dry")))
                    results.append("ok")
                except SystemExit as e:
                    results.append(str(e))
        after = (root / d.MANIFEST_REL).read_bytes()
        return {"results": results, "calls": calls, "jobs": seen, "stdout": out.getvalue(), "git": git_calls,
                "manifest_changed": before != after, "manifest": json.loads(after)}
''')


# --------------------------------------------------------------------------- the variant, the steps, the files


def test_driver_refuses_the_other_variants():
    for variant in ("registered", "usd", "usd12m"):
        out = run_py("import run_contract12m_pipeline", variant)
        assert out.returncode != 0 and "contract-graph variant" in out.stderr, variant
    out = run_py("import run_contract12m_pipeline as d; print(d.VARIANT)", None)  # unset: the driver's own
    assert out.returncode == 0 and out.stdout.strip() == "contract12m", out.stderr


def test_steps_are_in_the_order_of_the_revision():
    r = run_json("""
        import json
        import run_contract12m_pipeline as d
        print(json.dumps({"steps": list(d.STEPS), "funcs": [callable(getattr(d, f"step_{s}", None)) for s in d.STEPS],
                          "gate_b": d.GATE_B, "chain": list(d.CHAIN), "chain_a": list(d.CHAIN_A),
                          "prefix": d.PREFIX, "campaign": d.CAMPAIGN, "cap": d.CAP_USD,
                          "ratios": [d.DRY_RATIO, d.BILL_RATIO],
                          "manifest": d.MANIFEST.relative_to(d.ROOT).as_posix()}))
    """)
    assert r["steps"] == ["check", "subset", "ends", "activity", "queue", "typing", "load", "contracts", "balances",
                          "anchors", "audit", "structure", "constants", "pairs", "rest", "checks", "download"]
    assert all(r["funcs"])
    assert list(r["gate_b"]) == r["steps"][-5:]
    assert r["gate_b"] == {"constants": "jobs 36", "pairs": "job 37", "rest": "jobs 38 to 41", "checks": "job 42",
                           "download": "the downloads of the gate B tables"}
    assert r["chain"] == r["steps"][1:] and r["chain_a"] == r["steps"][1:12]
    # the cap of the overlay, which the gate B commit may raise within the budget of the variant (revision section 12)
    assert (r["prefix"], r["campaign"], r["cap"], r["ratios"]) == ("c12_", "contract12m:", CAP_USD, [1.25, 1.5])
    assert 14.0 <= CAP_USD <= 60.0
    assert r["manifest"] == MANIFEST_REL


def test_every_job_has_its_sql_file():
    r = run_json("""
        import json
        import run_contract12m_pipeline as d
        import run_discovery as rd
        from common import load_config
        cfg = load_config()
        jobs = d.jobs(cfg)
        print(json.dumps({"keys": [j.key for j in d.all_jobs(cfg)],
                          "steps": {s: [[j.key, j.no, j.sql] for j in js] for s, js in jobs.items()},
                          "exists": [(d.ROOT / "sql" / j.sql).exists() for j in d.all_jobs(cfg)],
                          "files": list(d.SQL_FILES), "files_b": list(d.SQL_FILES_B),
                          "committed": list(d.COMMITTED), "committed_b": list(d.COMMITTED_B),
                          "eval_files_b": list(d.EVAL_FILES_B), "feasibility": d.FEASIBILITY_REL,
                          "pilot": list(d.PILOT_COMMITTED), "discovery": list(rd.COMMITTED),
                          "on_disk": [(d.ROOT / f).exists() for f in d.COMMITTED + d.COMMITTED_B
                                      if not f.startswith("data/")]}))
    """)
    assert set(r["keys"]) == JOB_KEYS and len(r["keys"]) == len(JOB_KEYS)
    assert all(r["exists"])
    jobs_a = [j for s, js in r["steps"].items() if s not in GATE_B_STEPS for j in js]
    jobs_b = {s: js for s, js in r["steps"].items() if s in GATE_B_STEPS}
    assert {k for k, _, _ in jobs_a} == JOB_KEYS_A
    assert sorted(sql for _, _, sql in jobs_a) == sorted(r["files"])
    gate_b_files = {p.name for p in (EXPERIMENTS / "sql").glob("*.sql") if re.fullmatch(r"(3[6-9]|4[0-2])_c12_.*\.sql",
                                                                                         p.name)}
    assert {sql for js in jobs_b.values() for _, _, sql in js} == set(r["files_b"]) == gate_b_files
    for key, no, sql in [*jobs_a, *(j for js in jobs_b.values() for j in js)]:
        assert sql.startswith(f"{no}_c12_"), key
    assert {s: {no for _, no, _ in js} for s, js in jobs_b.items()} == {
        "constants": {36}, "pairs": {37}, "rest": {38, 39, 40, 41}, "checks": {42}}
    assert "download" not in r["steps"]
    # The gate A list of revision section 12, the revision first (its commit is the reference point); gate B adds its
    # own list (the gate B amendment of section 13) and leaves this one unchanged.
    assert r["committed"] == [
        "docs/revision_contract_graph.md", "docs/discovery_protocol.md", "config/overlay_contract12m.yaml",
        "config/contract_reputation.yaml", "scripts/run_contract12m_pipeline.py", "scripts/run_bq.py",
        "scripts/common.py", "scripts/check_account_code.py", "scripts/balance_audit.py", "scripts/download_table.py",
        "scripts/crawl.py", "scripts/run_discovery.py", "scripts/scoring.py", "scripts/stats.py", "scripts/graphs.py",
        *(f"sql/{f}" for f in r["files"])]
    assert r["eval_files_b"] == ["scripts/common.py", "scripts/labels.py", "scripts/graphs.py", "scripts/usd.py",
                                 "scripts/run_same_window.py", "scripts/run_holdout.py", "scripts/run_registered.py",
                                 "scripts/run_robustness.py", "scripts/run_discovery.py"]
    assert r["feasibility"] == FEASIBILITY_REL
    assert r["committed_b"] == [*(f"sql/{f}" for f in r["files_b"]), "scripts/labels.py", "scripts/usd.py",
                                "scripts/run_same_window.py", "scripts/run_holdout.py", "scripts/run_registered.py",
                                "scripts/run_robustness.py", FEASIBILITY_REL]
    assert len(set(r["committed_b"])) == len(r["committed_b"]) and not set(r["committed_b"]) & set(r["committed"])
    assert all(r["on_disk"]) and len(set(r["committed"])) == len(r["committed"])
    # The structure step checks the pilot's record of the files run_discovery.py records, all of them committed here.
    assert r["pilot"] == r["discovery"] and set(r["pilot"]) <= set(r["committed"])


# --------------------------------------------------------------------------- what the jobs create and read


PROBE = r"""
    import json, re
    import run_contract12m_pipeline as d
    import run_bq
    from common import load_config
    cfg = load_config()
    project, dataset = cfg["bigquery"]["project_id"], cfg["bigquery"]["dataset"]
    strip = lambda s: re.sub(r"--[^\n]*", "", s)
    made, out = set(), {}
    for step in d.STEPS:
        if step == "load":
            made.add("c12_account_types")  # job 30, the load job
        for job in d.jobs(cfg).get(step, []):
            sql = d.sql_text(job)
            run_bq.check_tables(sql, project, dataset, d.PREFIX, list(job.allow), list(job.public))
            body = strip(sql)
            created, read = d.tables_of(job, cfg)
            outside = {f"{p}.{t}" for p, t in re.findall(r"`([\w-]+\.[\w-]+)\.(\w+)`", body)
                       if p != f"{project}.{dataset}"}
            out[job.key] = {
                "step": step, "creates": sorted(created), "reads": sorted(read), "outside": sorted(outside),
                "public": list(job.public), "allow": list(job.allow),
                "left": re.findall(r"__[A-Z][A-Z0-9_]*__", body),
                "params": sorted(set(re.findall(r"@(\w+)", body)) ^ set(job.params)),
                "early": sorted(t for t in read if t.startswith("c12_") and t not in made),
                "start": job.params.get("start_ts")}
            made |= created
    print(json.dumps(out))
"""


@pytest.fixture(scope="module")
def probe() -> dict:
    return run_json(PROBE)


def test_jobs_create_only_c12_tables_and_read_what_they_may(probe):
    jobs = probe
    assert set(jobs) == JOB_KEYS
    for key, j in jobs.items():
        assert j["creates"] and all(t.startswith("c12_") for t in j["creates"]), key
        assert not j["left"], (key, j["left"])
        assert not j["params"], (key, j["params"])  # every @parameter is passed, and only those
        assert not j["early"], (key, j["early"])  # c12_ inputs come from earlier jobs
        assert set(j["reads"]) - {t for t in j["reads"] if t.startswith("c12_")} == set(j["allow"]), key
    assert jobs["logs5"]["creates"] == ["c12_logs5"] and jobs["ends"]["creates"] == ["c12_ends", "c12_pairs5"]
    assert jobs["contracts"]["creates"] == ["c12_contracts", "c12_events_cc", "c12_user_accounts"]
    assert jobs["structure"]["creates"] == ["c12_struct_t1"] and jobs["bal_audit"]["creates"] == ["c12_bal_audit"]
    assert "c12_account_types" in jobs["contracts"]["reads"]
    assert jobs["logs5"]["start"] == jobs["structure"]["start"] == "2025-04-01 00:00:00 UTC"


def test_public_views_are_named_and_allowed(probe):
    jobs = probe
    readers = {k for k, j in jobs.items() if j["outside"]}
    assert readers == {"tx_senders", "emitters", "creations", "bal_pre", "anchor_blocks"}
    for key, j in jobs.items():
        assert j["outside"] == sorted(j["public"]), key
        assert set(j["public"]) <= VIEWS, key
    assert {v.rsplit(".", 1)[1] for k in readers for v in jobs[k]["public"]} == {
        "transactions", "decoded_events", "receipts", "logs", "blocks"}


def test_gate_b_jobs_create_and_read_what_they_may(probe):
    jobs = {k: j for k, j in probe.items() if k in JOB_KEYS_B}
    assert set(jobs) == JOB_KEYS_B and {j["step"] for j in jobs.values()} == set(GATE_B_STEPS) - {"download"}
    for key, j in jobs.items():
        assert not j["left"] and not j["params"] and not j["early"], key
        assert {t for t in j["reads"] if not t.startswith("c12_")} == set(j["allow"]), key
        assert j["public"] == [] and j["outside"] == [], key
    assert {k: j["creates"] for k, j in jobs.items()} == {
        "triples": ["c12_allow_triples"], "user_events": ["c12_user_events"], "constants": ["c12_constants"],
        "pairs": ["c12_allow_pairs", "c12_allow_pairs_unc", "c12_transfer_pairs"],
        "cohorts": ["c12_cohort_t1", "c12_cohort_tobs", "c12_members"], "proxies": ["c12_proxies_tobs"],
        "labels_w0": ["c12_label_parts_w0", "c12_x_label_split_w0"],
        "labels_w1": ["c12_label_parts_w1", "c12_x_label_split_w1"],
        "node_ids": sorted(["c12_nodes", "c12_x_nodes", "c12_x_members", "c12_x_allow_pairs_tobs",
                            "c12_x_allow_pairs_t1", "c12_x_allow_pairs_unc_tobs", "c12_x_allow_pairs_unc_t1",
                            "c12_x_transfer_pairs_tobs", "c12_x_transfer_pairs_t1"]),
        "importance": sorted(["c12_importance_raw", "c12_importance_tobs", "c12_importance_t1",
                              "c12_inflow_untyped_tobs", "c12_inflow_untyped_t1", "c12_describe_allowances"]),
        "checks": ["c12_checks"]}
    made_b = {t for j in jobs.values() for t in j["creates"]}
    assert set(w.DOWNLOADS) <= made_b                       # every downloaded table is made by a gate B job
    label_inputs = re.compile(r"logs_obs|logs_w1|u12_(approvals|transfers|allow_triples)_\w+")
    assert {k for k, j in jobs.items() if any(label_inputs.fullmatch(t) for t in j["reads"])} == {"labels_w0",
                                                                                                  "labels_w1"}
    readers = lambda table: {k for k, j in jobs.items() if table in j["reads"]}  # noqa: E731
    assert readers("c12_logs5") == {"user_events"}          # c12_logs5 read once in gate B
    assert readers("c12_events_cc") == {"triples", "constants", "pairs", "proxies"}
    lists = ("u12_cohort_tobs", "u12_cohort_t1", "u12_labels_w0", "u12_labels_w1")
    assert {k for k, j in jobs.items() if set(lists) & set(j["reads"])} == {"cohorts", "checks"}
    assert {k: jobs[k]["start"] for k in ("triples", "user_events", "constants", "pairs", "importance", "checks")} == {
        k: probe["structure"]["start"] for k in ("triples", "user_events", "constants", "pairs", "importance",
                                                  "checks")}
    assert probe["structure"]["start"] == "2025-04-01 00:00:00 UTC"


def test_check_tables_refuses_a_public_view_not_allowed():
    out = run_py("""
        import run_contract12m_pipeline as d
        import run_bq
        from common import load_config
        cfg = load_config()
        job = d.jobs(cfg)["activity"][0]
        try:
            run_bq.check_tables(d.sql_text(job), "dissertation-bq", "contract_rep", "c12_", [], [])
            print("passed")
        except SystemExit as e:
            print("refused" if "other datasets" in str(e) else str(e))
    """)
    assert out.stdout.strip() == "refused", out.stdout + out.stderr


# --------------------------------------------------------------------------- parameters


FREEZES = {"start_ts": "2025-04-01 00:00:00 UTC", "t1": "2026-03-31 23:59:59 UTC",
           "tobs_start": "2025-07-01 00:00:00 UTC", "tobs": "2026-06-30 23:59:59 UTC"}
SYSTEM_BOUNDS = {"system_first": "0x" + "00" * 19 + "01", "system_last": "0x" + "00" * 19 + "ff"}


def test_job_parameters_follow_the_configuration():
    r = run_json("""
        import json
        import run_contract12m_pipeline as d
        from common import load_config
        cfg = load_config()
        c = {"b_transfer": 0.00646242522745947, "b_allowance": 0.010986122886681098, "cap_allowance_usd": 19000.0,
             "cap_user_usd": 2500.0}
        jobs = {j.key: j for j in d.all_jobs(cfg)}
        given = {j.key: j for js in d.jobs(cfg, c).values() for j in js}
        print(json.dumps({"placeholders": {k: [j.params, j.subs] for k, j in jobs.items()},
                          "constants": {k: [j.params, j.subs] for k, j in given.items()}}))
    """)
    p = r["placeholders"]
    assert p["logs5"][0] == {"start_ts": "2025-04-01 00:00:00 UTC", "mid_ts": "2026-07-01 00:00:00 UTC",
                             "end_ts": "2026-10-01 00:00:00 UTC"}
    assert p["emitters"][0] == {"start_ts": "2025-04-01 00:00:00 UTC", "end_ts": "2026-10-01 00:00:00 UTC"}
    # K holds the system addresses like any other end (revision section 4.3); the node set leaves them out.
    assert p["rpc_queue"][0] == {"sender_salt": "audit-sender-v1:", "untyped_salt": "audit-untyped-v1:"}
    # Since the amendment of 9 November 2026 the node set also takes the smart-account lists (revision section 13).
    assert p["contracts"][0] == {**SYSTEM_BOUNDS, "ext_code_hashes": ",".join(SMART_HASHES),
                                 "ext_pairs": ",".join(SMART_PAIRS)}
    assert p["rpc_queue"][1] == {"AUDIT_SENDERS": "1000", "AUDIT_UNTYPED": "1000"}
    assert p["bal"][0]["t1"] == "2026-03-31 23:59:59 UTC" and p["bal"][0]["tobs"] == "2026-06-30 23:59:59 UTC"
    assert p["bal"][0]["end_0930"] == "2026-09-30 23:59:59 UTC"
    assert p["bal"][0]["obs_start"] == "2023-10-01 00:00:00 UTC"
    assert p["bal_pre"][0] == {"obs_start": "2023-10-01 00:00:00 UTC", "start_ts": "2025-04-01 00:00:00 UTC",
                               "tobs_end": "2026-07-01 00:00:00 UTC"}
    assert p["bal_audit"][0] == {"audit_salt": "bal-audit-v1:", "per_cell": "150", "dust_digits": "6"}
    assert p["structure"][0] == {"start_ts": "2025-04-01 00:00:00 UTC", "t1": "2026-03-31 23:59:59 UTC",
                                 "dust_digits": "6"}
    # gate B, with the placeholders a dry run takes before constants.json
    unlimited = "1.15e+77"
    assert p["triples"] == [{**FREEZES, "dust_digits": "6"}, {}]
    assert p["user_events"] == [{"start_ts": FREEZES["start_ts"], "tobs": FREEZES["tobs"]}, {}]
    assert p["constants"] == [{"start_ts": FREEZES["start_ts"], "t1": FREEZES["t1"], "unlimited": unlimited}, {}]
    assert p["pairs"] == [{**FREEZES, "b_transfer": "0.01", "b_allowance": "0.01", "cap_allowance": "1000000.0"}, {}]
    assert p["cohorts"] == [SYSTEM_BOUNDS, {}]
    assert p["proxies"] == [{"start_ts": FREEZES["tobs_start"], "anchor_ts": FREEZES["tobs"]}, {}]
    assert p["labels_w0"] == [
        {"start_ts": "2025-04-01 00:00:00 UTC", "t1": "2026-03-31 23:59:59 UTC", "out_start": "2026-04-01 00:00:00 UTC",
         "out_end": "2026-06-30 23:59:59 UTC"},
        {"TAG": "w0", "FREEZE": "t1", "APPROVALS": "u12_approvals_t1", "TRANSFERS": "u12_transfers_t1",
         "SEEN": "u12_transfers_t1", "LOGS": "logs_obs"}]
    assert p["labels_w1"] == [
        {"start_ts": "2025-07-01 00:00:00 UTC", "t1": "2026-06-30 23:59:59 UTC", "out_start": "2026-07-01 00:00:00 UTC",
         "out_end": "2026-09-30 23:59:59 UTC"},
        {"TAG": "w1", "FREEZE": "tobs", "APPROVALS": "u12_approvals_w1", "TRANSFERS": "u12_transfers_w1",
         "SEEN": "u12_transfers_tobs", "LOGS": "logs_w1"}]
    assert p["node_ids"] == [{}, {}]
    assert p["importance"] == [{**FREEZES, "dust_digits": "6", "cap_user": "1000000.0", "min_usd": "1.0",
                                "unlimited": unlimited, "cap_allowance": "1000000.0"}, {}]
    assert p["checks"] == [{**FREEZES, "dust_digits": "6", **SYSTEM_BOUNDS}, {}]
    # with the constants of constants.json: repr of each float in pairs and importance, nothing else changes
    c = r["constants"]
    assert c["pairs"][0] == {**p["pairs"][0], "b_transfer": "0.00646242522745947",
                             "b_allowance": "0.010986122886681098", "cap_allowance": "19000.0"}
    assert c["importance"][0] == {**p["importance"][0], "cap_user": "2500.0", "cap_allowance": "19000.0"}
    assert set(c) == set(p) and all(c[k] == p[k] for k in p if k not in ("pairs", "importance"))
    assert c["pairs"][1] == p["pairs"][1] and c["importance"][1] == p["importance"][1]


def test_label_jobs_take_the_twelve_month_label_inputs():
    """Job 39 recounts the u12 labels with sql/16 on the inputs of the twelve-month label jobs: the same
    parameters and substitutions, the table sql/16 reads as u_transfers named as __SEEN__, and exactly the tables
    that the renamed sql/16 reads may be read."""
    theirs = run_json(r"""
        import json, re
        import run_usd12m_pipeline as u
        import run_bq
        from common import load_config, ROOT
        cfg = load_config()
        project, dataset = cfg["bigquery"]["project_id"], cfg["bigquery"]["dataset"]
        ds = rf"`{re.escape(project)}\.{re.escape(dataset)}\.(\w+)`"
        out = {}
        for job in u.jobs(cfg)["rest"]:
            if job.key not in ("labels_w0", "labels_w1"):
                continue
            sql = (ROOT / "sql" / job.sql).read_text(encoding="utf-8")
            for k, v in job.subs.items():
                sql = sql.replace(f"__{k}__", v)
            sql = re.sub(r"--[^\n]*", "", run_bq.apply_renames(sql, [f"{k}={v}" for k, v in job.renames.items()],
                                                                project, dataset))
            created = set(re.findall(rf"CREATE\s+(?:OR\s+REPLACE\s+)?(?:TABLE|VIEW)\s+{ds}", sql))
            out[job.key] = {"params": job.params, "subs": job.subs, "renames": job.renames,
                            "reads": sorted(set(re.findall(ds, sql)) - created)}
        print(json.dumps(out))
    """, "usd12m")
    ours = run_json("""
        import json
        import run_contract12m_pipeline as d
        from common import load_config
        jobs = {j.key: j for j in d.all_jobs(load_config())}
        print(json.dumps({k: {"params": jobs[k].params, "subs": jobs[k].subs, "allow": list(jobs[k].allow)}
                          for k in ("labels_w0", "labels_w1")}))
    """)
    assert set(theirs) == set(ours) == {"labels_w0", "labels_w1"}
    for key in ours:
        assert ours[key]["params"] == theirs[key]["params"], key
        assert ours[key]["subs"] == {**theirs[key]["subs"], "SEEN": theirs[key]["renames"]["u_transfers"]}, key
        assert set(ours[key]["allow"]) == set(theirs[key]["reads"]), key
    assert set(ours["labels_w0"]["allow"]) == {"u12_allow_triples_t1", "u12_approvals_t1", "u12_transfers_t1",
                                               "logs_obs", "u_tokens"}
    assert set(ours["labels_w1"]["allow"]) == {"u12_allow_triples_tobs", "u12_approvals_w1", "u12_transfers_w1",
                                               "u12_transfers_tobs", "logs_w1", "u_tokens"}


def test_the_smart_account_lists_are_those_of_the_amendment():
    # Revision section 13, amendment of 9 November 2026: the lists and counts of common are the amendment's, sorted,
    # lowercase 0x hex of the right lengths, without overlap and without the mixed beacon family 0x14044459; the
    # driver passes them to sql/31 as the amendment writes them.
    import re
    r = run_json("""
        import json, common
        print(json.dumps({"hashes": list(common.SMART_ACCOUNT_CODE_HASHES),
                          "pairs": [list(p) for p in common.SMART_ACCOUNT_IMPLEMENTATIONS],
                          "typed": common.SMART_ACCOUNT_TYPED, "params": common.smart_account_sql_params()}))
    """)
    a = amendment_lists()
    assert r["hashes"] == a["code_hashes"] == sorted(a["code_hashes"]) and len(r["hashes"]) == 20
    assert r["pairs"] == a["code_hash_implementations"] == sorted(a["code_hash_implementations"])
    assert r["typed"] == {"code_hashes": a["typed_contracts"]["code_hashes"],
                          "implementations": a["typed_contracts"]["code_hash_implementations"]}
    assert all(re.fullmatch(r"0x[0-9a-f]{64}", h) for h in r["hashes"])
    assert all(re.fullmatch(r"0x[0-9a-f]{64}", h) and re.fullmatch(r"0x[0-9a-f]{40}", i) for h, i in r["pairs"])
    assert not set(r["hashes"]) & {h for h, _ in r["pairs"]}
    assert "0x14044459af17bc4f0f5aa2f658cb692add77d1302c29fe2aebab005eea9d1162" not in r["hashes"]
    # the failing implementations of the getter test are not listed
    assert not {"0x22839de35030139d5c7a48f45e703d5204586606", "0x847a02f6845f4bd4a4c914f4c17889b67187893e"} & {
        i for _, i in r["pairs"]}
    assert r["params"] == {"ext_code_hashes": ",".join(SMART_HASHES), "ext_pairs": ",".join(SMART_PAIRS)}


def test_the_extension_moves_the_listed_contracts_and_nothing_else():
    r = run_json("""
        import json, pandas as pd, common
        h = common.SMART_ACCOUNT_CODE_HASHES[0]
        kh, ki = common.SMART_ACCOUNT_IMPLEMENTATIONS[0]
        t = pd.DataFrame({
            "address": [f"0x{i:040x}" for i in range(7)],
            "account_class": ["contract", "eoa", "contract", "contract", "contract", "smart_account", "contract"],
            "code_hash": [h, h, kh, kh, "0x" + "ab" * 32, kh, "0x" + h[2:].upper()],
            "implementation": ["", "", ki, "0x" + "cd" * 20, ki, ki, None],
            "wallet_kind": ["", "", "", "", "", "safe", ""]})
        out = common.with_smart_account_extension(t)
        print(json.dumps({"moved": common.smart_account_extension(t).tolist(),
                          "classes": out["account_class"].tolist(), "kinds": out["wallet_kind"].tolist(),
                          "input": t["account_class"].tolist()}))
    """)
    # a listed hash (any case) or a listed (hash, implementation) pair, of class contract only
    assert r["moved"] == [True, False, True, False, False, False, True]
    assert r["classes"] == ["smart_account", "eoa", "smart_account", "contract", "contract", "smart_account",
                            "smart_account"]
    assert r["kinds"] == ["erc4337", "", "erc4337", "", "", "safe", "erc4337"]
    assert r["input"][0] == "contract"  # the frame read is not changed in place


def test_sql31_applies_the_lists_in_both_typed_views_and_not_to_the_events():
    import re
    sql = re.sub(r"--[^\n]*", "", (EXPERIMENTS / "sql" / "31_c12_contracts.sql").read_text(encoding="utf-8"))
    first, rest = sql.split("c12_user_accounts", 1)
    second, events = rest.split("c12_events_cc", 1)
    for part in (first, second):
        assert part.count("IN UNNEST(SPLIT(@ext_code_hashes, ','))") == 1
        assert part.count("IN UNNEST(SPLIT(@ext_pairs, ','))") == 1
        assert "IF(account_class = 'contract'" in part  # only contracts move
        assert "LOWER(code_hash)" in part and "LOWER(IFNULL(implementation, ''))" in part
    assert "@ext" not in events


def test_the_contracts_step_counts_what_the_lists_move():
    r = run_json("""
        import json, pandas as pd, common
        import run_contract12m_pipeline as d
        h = common.SMART_ACCOUNT_CODE_HASHES[0]; kh, ki = common.SMART_ACCOUNT_IMPLEMENTATIONS[0]
        t = pd.DataFrame({"address": ["0x1", "0x2", "0x3", "0x4"], "account_class": ["contract"] * 3 + ["eoa"],
                          "code_hash": [h, kh, "0x" + "ab" * 32, ""], "implementation": ["", ki, "", ""]})
        print(json.dumps(d.extension_counts(t)))
    """)
    assert r == {"typed_contracts": 3, "moved": 2, "moved_by_code_hash": 1, "moved_by_implementation": 1,
                 "contracts_after": 1}


def test_the_lists_move_the_counts_of_the_amendment_on_the_typing_output():
    # On the typing output of 8 November 2026 (on disk only where the parquet parts were downloaded), the lists move
    # exactly the counts that the amendment states, and the reads they rest on are recorded at the typing block.
    stem = EXPERIMENTS / "data" / "1-raw-blockchain-extracts" / "contract-types"
    if not (stem / "c12_account_types.part000.parquet").exists():
        pytest.skip("the typing output is not on disk (its parquet parts live on Drive)")
    r = run_json("""
        import json, common, run_contract12m_pipeline as d
        cols = ["address", "account_class", "code_hash", "implementation"]
        print(json.dumps(d.extension_counts(common.read_parts(common.TYPES, cols))))
    """)
    a = amendment_lists()["typed_contracts"]
    assert (r["moved_by_code_hash"], r["moved_by_implementation"]) == (a["code_hashes"], a["code_hash_implementations"])
    assert r["moved"] == 192_656 and r["contracts_after"] == r["typed_contracts"] - 192_656
    # The getter test of item 2 covers every group with its signature, and its passing groups are the listed pairs.
    reads = json.loads((stem / "c12_smart_account_reads.json").read_text(encoding="utf-8"))
    assert reads["block"] == 513_216_506 and reads["block_hex"] == "0x1e970ffa"
    groups = reads["item2_getter_test"]["groups"]
    assert len(groups) == 15
    passed = sorted([g["code_hash"], g["implementation"]] for g in groups if g["passes"])
    assert passed == amendment_lists()["code_hash_implementations"]
    assert sum(g["contracts"] for g in groups if g["passes"]) == a["code_hash_implementations"]
    out = run_json("""
        import json, common
        t = common.read_parts(common.TYPES, ["address", "account_class", "code_hash", "implementation", "entry_point",
                                             "has_validate_userop", "has_paymaster_selector", "proxy_kind"])
        sig = ((t["account_class"] == "contract") & (t["proxy_kind"] == "erc1967") & t["has_validate_userop"]
               & ~t["has_paymaster_selector"] & (t["entry_point"] == ""))
        print(json.dumps(sorted(map(list, t[sig].groupby(["code_hash", "implementation"]).size().index))))
    """)
    assert out == sorted([g["code_hash"], g["implementation"]] for g in groups)


def test_the_size_check_of_job_31_follows_the_last_run():
    # Moving addresses from the contracts to the user accounts keeps their sum; the last run fixes both sizes.
    r = run_json("""
        import json, run_contract12m_pipeline as d
        ext = {"moved": 10, "contracts_after": 90}
        first = {"c12_contracts": 100, "c12_user_accounts": 500}
        again = {**first, "smart_account_extension": {"moved": 10}}
        print(json.dumps([
            d.expected_sizes(first, ext, {"c12_contracts": 90, "c12_user_accounts": 510}),
            d.expected_sizes(first, ext, {"c12_contracts": 90, "c12_user_accounts": 500}),
            d.expected_sizes(first, ext, {"c12_contracts": 80, "c12_user_accounts": 520}),
            d.expected_sizes({"c12_contracts": 90, "c12_user_accounts": 510, "smart_account_extension": {"moved": 10}},
                             ext, {"c12_contracts": 90, "c12_user_accounts": 510}),
            d.expected_sizes({}, ext, {"c12_contracts": 90, "c12_user_accounts": 0})]))
    """)
    assert r[0] == [{"c12_contracts": 90, "c12_user_accounts": 510}, True]
    assert r[1][1] is False and r[2][1] is False  # one table did not change, or more than the lists moved
    assert r[3] == [{"c12_contracts": 90, "c12_user_accounts": 510}, True]  # the same lists run again
    assert r[4] == [{"c12_contracts": "at most 90"}, True]


def test_the_structure_step_needs_a_run_of_job_31_with_the_lists():
    r = run_json("""
        import json, run_contract12m_pipeline as d
        ext = {"typed_contracts": 3, "moved": 2, "moved_by_code_hash": 1, "moved_by_implementation": 1,
               "contracts_after": 1}
        d.typed_extension = lambda m: (ext, "")
        steps = lambda passed: [{"step": "contracts", "passed": passed}]
        out = [d.lists_applied({"steps": [], "results": {}}),
               d.lists_applied({"steps": steps(False), "results": {"contracts": {"smart_account_extension": ext}}}),
               d.lists_applied({"steps": steps(True), "results": {"contracts": {"c12_contracts": 9}}}),
               d.lists_applied({"steps": steps(True), "results": {"contracts": {"smart_account_extension": ext}}})]
        d.typed_extension = lambda m: (None, "c12_account_types is not on disk")
        out.append(d.lists_applied({"steps": steps(True), "results": {"contracts": {"smart_account_extension": ext}}}))
        print(json.dumps(out))
    """)
    assert r[0] == r[1] == "the last run of contracts did not pass"
    assert r[2] == "the last run of contracts was not made with the smart-account lists"  # the run of 8 November
    assert r[3] == ""
    assert r[4] == "c12_account_types is not on disk"


def test_the_typing_output_must_be_the_one_job_30_loaded(tmp_path):
    r = run_json(f"""
        import json, pandas as pd, common, run_contract12m_pipeline as d
        from pathlib import Path
        stem = Path(r"{tmp_path}") / "c12_account_types"
        d.TYPES = stem
        missing = d.typed_extension({{"results": {{}}}})
        common.write_parts(pd.DataFrame({{"address": ["0x1"], "account_class": ["eoa"], "code_hash": [""],
                                          "implementation": [""]}}), stem)
        name = d.part_paths(stem)[0].name
        other = d.typed_extension({{"results": {{"load": {{"source_sha256": {{name: "0" * 64}}}}}}}})
        same = d.typed_extension({{"results": {{"load": {{"source_sha256": {{name: d.sha256(d.part_paths(stem)[0])}}}}}}}})
        print(json.dumps([missing, other, same[1]]))
    """)
    assert r[0] == [None, "c12_account_types is not on disk"]
    assert r[1] == [None, "the parts of c12_account_types on disk are not those job 30 loaded"]
    assert r[2].startswith("the smart-account lists move")  # a toy output does not hold the amendment's counts


def test_the_queue_keeps_the_system_addresses_and_the_node_set_drops_them():
    # Revision section 4.3 defines K without the system addresses' exception; section 4.1 makes them never
    # contracts, and user accounts only by rule 1 (a transaction sender). So sql/29 reads no system bounds and
    # sql/31 applies them to c12_contracts and to the RPC-typed part of c12_user_accounts, not to the senders.
    def code(name: str) -> str:
        return re.sub(r"--[^\n]*", "", (EXPERIMENTS / "sql" / name).read_text(encoding="utf-8"))

    queue, nodes = code("29_c12_rpc_queue.sql"), code("31_c12_contracts.sql")
    assert "system_first" not in queue and "system_last" not in queue
    first, rest = nodes.split("c12_user_accounts", 1)
    second, events = rest.split("c12_events_cc", 1)
    tx_part, rpc_part = second.split("UNION ALL", 1)
    assert "@system_first" in first and "@system_last" in first
    assert "@system" not in tx_part and "@system_first" in rpc_part and "@system_last" in rpc_part
    assert "@system" not in events


def test_windows_follow_the_revision_and_a_changed_window_is_refused():
    out = run_py("""
        import run_contract12m_pipeline as d
        from common import load_config
        cfg = load_config()
        w = d.windows(cfg)
        print(w["typing_start"], "|", w["typing_end"], "|", w["tobs"])
        cfg["contract_graph"]["typing_end"] = "2026-11-01 00:00:00 UTC"
        try:
            d.windows(cfg)
        except SystemExit:
            print("refused")
    """)
    assert out.returncode == 0, out.stderr
    assert out.stdout.splitlines() == ["2025-04-01 00:00:00 UTC | 2026-10-01 00:00:00 UTC | 2026-06-30 23:59:59 UTC",
                                       "refused"]


def test_the_token_literals_of_sql32_are_the_five_tokens():
    import csv
    with open(EXPERIMENTS / "data" / "0-usd-token-list-and-prices" / "listed_tokens.csv", encoding="utf-8") as f:
        selected = {r["address"].lower() for r in csv.DictReader(f) if str(r["selected"]).lower() == "true"}
    sql = (EXPERIMENTS / "sql" / "32_c12_bal_pre.sql").read_text(encoding="utf-8")
    assert set(re.findall(r"'(0x[0-9a-f]{40})'", sql)) == selected and len(selected) == 5


# --------------------------------------------------------------------------- estimates and the projection


def test_estimates_are_positive_and_cover_every_read():
    r = run_json("""
        import json
        import run_contract12m_pipeline as d
        from common import load_config
        cfg = load_config()
        full = d.estimates({t: 1_000_000 for t in d.ESTIMATE_TABLES})
        none = d.estimates({})
        sources = d.estimates({t: 1000 for t in ("u_tokens", "u_prices", "u12_cohort_tobs", "u12_cohort_t1",
                                                 "u12_labels_w0", "u12_labels_w1", "logs_obs", "logs_w1")})
        bounded = d.estimates({"c12_logs5": 1_000_000})
        cover = {}
        for job in d.all_jobs(cfg):
            created, read = d.tables_of(job, cfg)
            covered = set()
            for statement in d.READS[job.key]:
                for t in statement:
                    covered |= {t.table} if isinstance(t, d.Read) else set(t.covers)
            cover[job.key] = [sorted(set(read) | set(job.public)), sorted(covered - created)]
        print(json.dumps({"full": {k: [e.first, e.whole, list(e.missing)] for k, e in full.items()},
                          "full_b": {k: [e.first, e.whole, list(e.missing)] for k, e in d.estimates(
                              {t: 10**6 for t in d.ESTIMATE_TABLES}).items()},
                          "none": {k: list(e.missing) for k, e in none.items()},
                          "sources": {k: list(e.missing) for k, e in sources.items()},
                          "bounded": {k: list(e.missing) for k, e in bounded.items()},
                          "statements": {k: len(v) for k, v in d.READS.items()}, "cover": cover,
                          "min": d.MIN_TABLE}))
    """)
    assert set(r["full"]) == JOB_KEYS
    for key, (first, whole, missing) in r["full"].items():
        assert 0 < first <= whole and not missing, key
    for key, (first, whole, missing) in r["full_b"].items():
        assert 0 < first <= whole and not missing, key
    assert r["statements"]["ends"] == 2 and r["statements"]["contracts"] == 3
    # with 1,000,000 rows every c12_ read is at least 10 MB: first statement of ends is one read of c12_logs5
    assert r["full"]["ends"][0] == max(r["min"], 1_000_000 * 55)
    assert r["none"]["logs5"] == [] and r["none"]["anchor_blocks"] == []
    assert r["none"]["ends"] == ["c12_logs5"] and "c12_ends" in r["none"]["tx_senders"]
    assert r["none"]["contracts"] == ["c12_account_types", "c12_logs5", "c12_tx_senders"]
    assert r["bounded"]["ends"] == []  # c12_pairs5 is bounded by c12_logs5 within the job
    for key, (reads, covered) in r["cover"].items():
        assert reads == covered, key
    # with the rows of the source tables only, a gate B job lacks exactly the c12_ tables it reads
    assert {k: v for k, v in r["sources"].items() if k in JOB_KEYS_B} == {
        "triples": ["c12_bal", "c12_events_cc"],
        "user_events": ["c12_contracts", "c12_ends", "c12_logs5", "c12_rpc_queue", "c12_tx_senders",
                        "c12_user_accounts"],
        "constants": ["c12_allow_triples", "c12_events_cc", "c12_user_events"],
        "pairs": ["c12_allow_triples", "c12_events_cc"], "cohorts": ["c12_contracts", "c12_user_accounts"],
        "proxies": ["c12_cohort_tobs", "c12_events_cc"],
        "labels_w0": ["c12_contracts", "c12_members", "c12_user_accounts"],
        "labels_w1": ["c12_contracts", "c12_members", "c12_user_accounts"],
        "node_ids": ["c12_allow_pairs", "c12_allow_pairs_unc", "c12_contracts", "c12_members", "c12_transfer_pairs"],
        "importance": ["c12_allow_triples", "c12_bal", "c12_contracts", "c12_nodes", "c12_user_events"],
        "checks": r["sources"]["checks"]}
    assert r["sources"]["checks"] and all(t.startswith("c12_") for t in r["sources"]["checks"])


def test_reads_have_one_entry_per_statement():
    r = run_json(r"""
        import json, re
        import run_contract12m_pipeline as d
        from common import load_config
        cfg = load_config()
        project, dataset = cfg["bigquery"]["project_id"], cfg["bigquery"]["dataset"]
        ds = rf"`{re.escape(project)}\.{re.escape(dataset)}\.(\w+)`"
        made = rf"CREATE\s+(?:OR\s+REPLACE\s+)?(?:TABLE|VIEW)\s+{ds}"
        out = {}
        for job in d.all_jobs(cfg):
            body = re.sub(r"--[^\n]*", "", d.sql_text(job))
            statements = [s for s in body.split(";") if re.search(made, s)]
            out[job.key] = {
                "creates": len(re.findall(r"CREATE\s+(?:OR\s+REPLACE\s+)?(?:TABLE|VIEW)", body)),
                "reads": [sorted(set(re.findall(ds, s)) - set(re.findall(made, s))) for s in statements],
                "entries": [sorted({t.table for t in st if isinstance(t, d.Read)}) for st in d.READS[job.key]],
                "covered": [sorted({t.table for t in st if isinstance(t, d.Read)}
                                   | {c for t in st if isinstance(t, d.Measured) for c in t.covers})
                            for st in d.READS[job.key]]}
        print(json.dumps(out))
    """)
    assert set(r) == JOB_KEYS
    for key, j in r.items():
        assert len(j["entries"]) == j["creates"] == len(j["reads"]), key
    for key in ("triples", "user_events", "constants", "pairs", "proxies"):
        # the costly read is in the first statement, which the dry run of run_bq.py counts (1.25 x its estimate)
        costly = {"c12_events_cc", "c12_logs5"} & set(r[key]["reads"][0])
        assert costly and costly <= set(r[key]["entries"][0]), key
    for key in JOB_KEYS_B:      # every statement of a gate B job reads exactly the tables of its entry
        assert r[key]["reads"] == r[key]["covered"], key


def test_measured_terms_of_gate_b():
    r = run_json("""
        import json
        import run_contract12m_pipeline as d
        from common import load_config
        jobs = {j.key: j for j in d.all_jobs(load_config())}
        keys = [k for s in d.GATE_B for k in [j.key for j in d.jobs(load_config()).get(s, [])]]
        measured = [[k, i, n, t.bytes, list(t.covers)] for k in keys for i, st in enumerate(d.READS[k])
                    for n, t in enumerate(st) if isinstance(t, d.Measured)]
        reads = sorted({t.table for k in keys for st in d.READS[k] for t in st if isinstance(t, d.Read)})
        print(json.dumps({"measured": measured, "reads": reads, "sources_b": list(d.SOURCES_B),
                          "w0": [d.CAL_39_W0.bytes, list(d.CAL_39_W0.covers)],
                          "w1": [d.CAL_39_W1.bytes, list(d.CAL_39_W1.covers)],
                          "allow": {k: list(jobs[k].allow) for k in ("labels_w0", "labels_w1")}}))
    """)
    assert [m[:3] for m in r["measured"]] == [["labels_w0", 0, 0], ["labels_w1", 0, 0]]
    assert r["measured"][0][3:] == r["w0"] and r["measured"][1][3:] == r["w1"]
    assert set(r["w0"][1]) == set(r["allow"]["labels_w0"]) and set(r["w1"][1]) == set(r["allow"]["labels_w1"])
    # no Read of a gate B job names a table under the calibrated terms: they are counted by the bills only
    assert not set(r["reads"]) & (set(r["sources_b"]) | {"logs_obs", "logs_w1"}), r["reads"]
    ledger = {j.get("job_id"): j for j in json.loads((EXPERIMENTS / LEDGER_REL).read_text(encoding="utf-8"))["jobs"]}
    for (job_id, label), (nbytes, _) in ((("92c0b37c-0659-4f63-8aa7-0f335265d9fe", "usd12m: W0 labels"), r["w0"]),
                                         (("f66a1ca1-d501-4011-ac63-3f46e0815825", "usd12m: W1 labels"), r["w1"])):
        entry = ledger[job_id]
        assert (entry["label"], entry["sql"], entry["bytes_billed"]) == (label, "sql/16_usd_labels.sql", nbytes)
    assert (r["w0"][0], r["w1"][0]) == (53_868_494_848, 49_754_931_200)


def test_bounds_with_factors():
    r = run_json("""
        import json
        import run_contract12m_pipeline as d
        full = {t: 10**6 for t in d.ESTIMATE_TABLES}
        bounded = d.estimates({**full, "c12_importance_raw": None})["importance"]
        exact = d.estimates({**full, "c12_importance_raw": 10**6})["importance"]
        print(json.dumps({"bounded": [bounded.first, bounded.whole, list(bounded.missing)],
                          "exact": [exact.first, exact.whole, list(exact.missing)],
                          "ends": list(d.estimates({"c12_logs5": 10**6})["ends"].missing)}))
    """)
    # first: c12_user_events 110, c12_bal 60, u_tokens 30, u_prices 38 bytes a row; then c12_importance_raw at its
    # bound 2 x c12_contracts + 2 (70 and 24 bytes), c12_nodes (30) and c12_allow_triples (52)
    assert r["bounded"] == [238_000_000, 726_000_376, []]
    assert r["bounded"][1] == 238_000_000 + 2 * ((2 * 10**6 + 2) * 70 + 30 * 10**6) + 2 * (2 * 10**6 + 2) * 24 \
        + 52 * 10**6
    assert r["exact"] == [238_000_000, 238_000_000 + 2 * (70 * 10**6 + 30 * 10**6) + 2 * 24 * 10**6 + 52 * 10**6, []]
    assert r["ends"] == []                            # the string bound of gate A unchanged


def test_priced_rows_from_logical_bytes():
    r = run_json("""
        import json
        import run_contract12m_pipeline as d
        print(json.dumps([d.priced_rows(10, 10 * 109 + 7 * 8)] + [d.priced_rows(*x) for x in (
            (10, 1093), (10, 1082), (10, 1178), (None, 5), (5, None))]))
    """)
    assert r == [7, None, None, None, None, None]


# The tables of the projection test: the gate A tables at their real rows.
L5, PAIRS5, CONTRACTS, USERS, BAL, STRUCT = 1_240_275_042, 73_058_133, 1_120_000, 22_600_000, 2 * 10**7, 3_130_000
ENDS, QUEUE, SENDERS = 25_537_280, 6_230_270, 17_477_779
LISTS = {"u12_cohort_tobs": 6_483, "u12_cohort_t1": 6_343, "u12_labels_w0": 7_962, "u12_labels_w1": 7_995}
LAYERS = {"allow_capped": 29_000, "allow_uncapped": 98_000, "transfer": 2_900_000}
SELF_PAIRS = {"allow_capped": 1_000, "allow_uncapped": 2_000, "transfer": 100_000}
MIN = 10 * 2**20


def gate_a_tables(n: int, nbytes: int) -> dict:
    """{table: {rows, bytes}} of the tables the gate B jobs read before they exist, c12_events_cc with n rows."""
    return {"c12_events_cc": {"rows": n, "bytes": nbytes}, "c12_logs5": {"rows": L5, "bytes": 109 * L5 + 8 * 10**9},
            "c12_pairs5": {"rows": PAIRS5}, "c12_contracts": {"rows": CONTRACTS}, "c12_user_accounts": {"rows": USERS},
            "c12_bal": {"rows": BAL}, "c12_ends": {"rows": ENDS}, "c12_rpc_queue": {"rows": QUEUE},
            "c12_tx_senders": {"rows": SENDERS}, **{k: {"rows": v} for k, v in LISTS.items()},
            "u_tokens": {"rows": 5}, "u_prices": {"rows": 5_480}, "c12_struct_t1": {"rows": STRUCT}}


def per_job_bounds(n: int, ue: int, tr: int, ap: int, apu: int, tp: int) -> dict:
    """The billed upper bound of each gate B job, statement by statement of READS (c12_pairs5 read by job 42 as
    73,058,133 x 68 = 4,967,953,044 B), whose sum the comment above gate_b_projection collapses."""
    m = lambda x: max(MIN, x)  # noqa: E731
    c, ua, bal, st, imp = CONTRACTS, USERS, BAL, STRUCT, 2 * CONTRACTS + 2
    return {
        "triples": m(101 * n) + m(60 * bal) + 2 * MIN,
        "user_events": m(109 * L5) + m(22 * ENDS) + m(44 * QUEUE) + m(22 * SENDERS) + m(22 * ua) + m(22 * c),
        "constants": m(19 * n) + m(30 * tr) + m(20 * ue),
        "pairs": m(63 * n) + 2 * m(74 * tr),
        "cohorts": 2 * (MIN + m(22 * ua)) + 4 * MIN + m(22 * c) + m(41 * ua),
        "proxies": m(63 * n) + MIN,
        "labels_w0": 53_868_494_848 + m(22 * c) + m(22 * ua) + 2 * MIN,
        "labels_w1": 49_754_931_200 + m(22 * c) + m(22 * ua) + 2 * MIN,
        "node_ids": m(44 * ap) + m(44 * apu) + m(44 * tp) + MIN + m(22 * c) + m(56 * c) + MIN + m(98 * ap)
        + m(82 * ap) + 2 * m(82 * apu) + m(98 * tp) + m(82 * tp) + 6 * m(30 * c),
        "importance": m(110 * ue) + m(60 * bal) + 2 * MIN + 2 * (m(70 * imp) + m(30 * c)) + 2 * m(24 * imp)
        + m(52 * tr),
        "checks": m(22 * c) + m(22 * ua) + m(78 * c) + m(56 * c) + m(152 * tr) + m(90 * ap) + m(90 * apu)
        + m(74 * tp) + m(64 * ap) + m(48 * ap) + 2 * m(48 * apu) + m(64 * tp) + m(48 * tp) + m(104 * st)
        + PAIRS5 * 68 + 2 * m(84 * c) + m(54 * imp) + 18 * MIN,
    }


def test_projection_bounds_and_closed_form():
    n, priced = 6 * 10**8, 570_000_000
    spec = {"exact": gate_a_tables(n, 109 * n + 8 * priced), "loose": gate_a_tables(n, 109 * n + 3)}
    spec["missing"] = {k: v for k, v in spec["exact"].items() if k != "c12_events_cc"}
    r = run_json(f"""
        import json
        import run_contract12m_pipeline as d
        from common import load_config
        cfg = load_config()
        spec = json.loads({json.dumps(json.dumps(spec))})
        m = {{"results": {{"structure": {{"layers": {json.dumps(LAYERS)}, "self_pairs": {json.dumps(SELF_PAIRS)}}}}}}}
        keys = d.gate_b_keys(cfg)
        out = {{"keys": keys, "rest": d.gate_b_keys(cfg, "rest"), "download": d.gate_b_keys(cfg, "download")}}
        for name, tables in spec.items():
            meta = {{t: tables.get(t) for t in d.ESTIMATE_TABLES}}
            out[name] = {{"bounds": d.projected_rows(meta, m), "projection": d.gate_b_projection(meta, m, keys)}}
        print(json.dumps(out))
    """)
    assert r["keys"] == ["triples", "user_events", "constants", "pairs", "cohorts", "proxies", "labels_w0",
                         "labels_w1", "node_ids", "importance", "checks"]
    assert r["rest"] == r["keys"][4:] and r["download"] == []
    s_c, s_u, s_t = (LAYERS[k] + SELF_PAIRS[k] for k in ("allow_capped", "allow_uncapped", "transfer"))
    a = n - priced
    b = r["exact"]["bounds"]
    want = {"c12_allow_triples": min(a, 5 * s_u) + a, "c12_allow_pairs": s_c + a, "c12_allow_pairs_unc": s_u + a,
            "c12_transfer_pairs": s_t + min(priced, PAIRS5), "c12_user_events": L5 - n, "c12_nodes": CONTRACTS,
            "c12_x_nodes": CONTRACTS, "c12_importance_raw": 2 * CONTRACTS + 2,
            "c12_cohort_tobs": LISTS["u12_cohort_tobs"], "c12_cohort_t1": LISTS["u12_cohort_t1"],
            "c12_members": 28_783, "c12_x_members": 28_783, "c12_proxies_tobs": LISTS["u12_cohort_tobs"],
            "c12_label_parts_w0": LISTS["u12_labels_w0"], "c12_label_parts_w1": LISTS["u12_labels_w1"],
            "c12_x_label_split_w0": LISTS["u12_labels_w0"], "c12_x_label_split_w1": LISTS["u12_labels_w1"],
            "_priced_rows": priced, "_a_rows_bound": a, "_n_events_cc": n}
    assert sum(LISTS.values()) == 28_783 and (s_c, s_u, s_t) == (30_000, 100_000, 3_000_000)
    assert {k: b[k] for k in want} == want
    assert not set(b) & set(spec["exact"])               # no bound for a table that exists
    per = per_job_bounds(n, b["c12_user_events"], b["c12_allow_triples"], b["c12_allow_pairs"],
                         b["c12_allow_pairs_unc"], b["c12_transfer_pairs"])
    assert 109 * L5 == 135_189_979_578 and 22 * ENDS + 44 * QUEUE + 22 * SENDERS == 1_220_463_178
    p = r["exact"]["projection"]
    assert p["complete"] is True and p["missing"] == []
    assert {k: v["whole"] for k, v in p["jobs"].items()} == per
    assert p["bytes"] == sum(per.values())
    collapsed = (245_368_823_448 + 246 * n + 130 * b["c12_user_events"] + 382 * b["c12_allow_triples"]
                 + 426 * b["c12_allow_pairs"] + 394 * b["c12_allow_pairs_unc"] + 410 * b["c12_transfer_pairs"]
                 + 120 * BAL + 1_214 * CONTRACTS + 173 * USERS + 104 * STRUCT)
    assert abs(p["bytes"] - collapsed) <= 10**8
    assert p["usd"] == round(p["bytes"] / 2**40 * 6.25, 4)
    # without an exact count of the priced rows every row of c12_events_cc counts as an A row and a priced transfer
    loose = r["loose"]["bounds"]
    assert loose["_priced_rows"] is None and loose["_a_rows_bound"] == n
    assert (loose["c12_allow_triples"], loose["c12_allow_pairs"], loose["c12_allow_pairs_unc"],
            loose["c12_transfer_pairs"]) == (min(n, 5 * s_u) + n, s_c + n, s_u + n, s_t + min(n, PAIRS5))
    assert r["loose"]["projection"]["bytes"] > p["bytes"]
    assert r["missing"]["bounds"] is None
    assert r["missing"]["projection"]["complete"] is False and r["missing"]["projection"]["usd"] is None


def test_cap_logic_on_fake_metadata():
    r = run_json("""
        import json
        import run_contract12m_pipeline as d
        small = d.estimates({t: 1_000_000 for t in d.ESTIMATE_TABLES})
        large = d.estimates({t: 10_000_000_000 for t in d.ESTIMATE_TABLES})
        keys = set(small)
        print(json.dumps({
            "small": d.cap_problems(small, 0.0, 0.0, 60.0),
            "large": d.cap_problems(large, 0.0, 0.0, 1e9),
            "campaign": d.cap_problems(small, d.CAP_USD - 0.01, 0.0, 1e9),
            "budget": d.cap_problems(small, 0.0, 59.99, 60.0),
            "done": d.cap_problems(small, d.CAP_USD - 0.01, 59.99, 60.0, done=keys),
            "known_usd": d.usd(sum(e.whole for e in small.values()))}))
    """)
    assert r["small"] == [] and 7 < r["known_usd"] < 14
    assert len(r["large"]) == 1 and "cap" in r["large"][0]
    assert len(r["campaign"]) == 1 and "cap" in r["campaign"][0]
    assert len(r["budget"]) == 1 and "budget" in r["budget"][0]
    assert r["done"] == []


def least_cent(total: float) -> float:
    """The least amount in whole cents that ``total`` does not pass when they are compared as floats, as over_cap
    compares the campaign and the projection with the cap (a cap written X in the overlay is float(X))."""
    c = math.floor(total * 100) - 2
    while total > c / 100:
        c += 1
    return c / 100


# (cap, campaign, projection, ledger, budget) -> the two lines. The sums of the first three pass the cap of USD 14 by
# less than half a cent, so the two-decimal figures of the line 'gate B projected' read 14.00 of 14.00; the sum of
# the fourth is a float just above 14 (a campaign summed from the ledger carries such bits).
NEEDED = {
    "rounds_to_the_cap": ((14.0, 11.004, 2.9964, 50.0, 60.0),
                          ("cap needed: USD 14.01 (above the cap of USD 14.00)",
                           "budget needed: USD 53.00, within the budget of USD 60")),
    "four_decimals": ((14.0, 4.1936, 9.8065, 4.1936, 60.0),
                      ("cap needed: USD 14.01 (above the cap of USD 14.00)",
                       "budget needed: USD 14.01, within the budget of USD 60")),
    "rounded_sum_below": ((14.0, 11.8049, 3.1364, 11.8049, 60.0),
                          ("cap needed: USD 14.95 (above the cap of USD 14.00)",
                           "budget needed: USD 14.95, within the budget of USD 60")),
    "float_above_the_cap": ((14.0, 10.000000000000002, 4.0, 56.0, 60.0),
                            ("cap needed: USD 14.01 (above the cap of USD 14.00)",
                             "budget needed: USD 60.00, within the budget of USD 60")),
    "at_the_cap": ((14.0, 10.0, 4.0, 10.0, 60.0),
                   ("cap needed: USD 14.00 (within the cap of USD 14.00)",
                    "budget needed: USD 14.00, within the budget of USD 60")),
    "just_below": ((14.0, 4.1949, 9.8049, 4.1949, 60.0),
                   ("cap needed: USD 14.00 (within the cap of USD 14.00)",
                    "budget needed: USD 14.00, within the budget of USD 60")),
    "budget_passed": ((14.0, 1.0, 3.9968, 56.0036, 60.0),
                      ("cap needed: USD 5.00 (within the cap of USD 14.00)",
                       "budget needed: USD 60.01, above the budget of USD 60")),
    "budget_reached": ((14.0, 1.0, 4.0, 56.0, 60.0),
                       ("cap needed: USD 5.00 (within the cap of USD 14.00)",
                        "budget needed: USD 60.00, within the budget of USD 60")),
    "raised_cap": ((20.0, 11.004, 2.9964, 50.0, 60.0),
                   ("cap needed: USD 14.01 (within the cap of USD 20.00)",
                    "budget needed: USD 53.00, within the budget of USD 60")),
}


def test_check_prints_the_cap_and_the_budget_that_the_projection_needs():
    """D1 (the gate B amendment of revision section 13 sets the cap from these lines): after a complete projection
    the check prints the cap and the budget that the campaign and the ledger with the projection need, in whole cents
    rounded up from the unrounded sums, and whether each is within or above the cap and the budget exactly as
    over_cap, the test of every gate B step, judges it; a cap set to the printed amount is never refused. The line
    before it rounds the campaign and the projection to cents, so it can read 14.00 of 14.00 when the sum passes 14.
    An incomplete projection prints neither line."""
    cases = {k: v[0] for k, v in NEEDED.items()}
    r = run_json(f"""
        import contextlib, io, json
        import run_contract12m_pipeline as d
        out = {{}}
        bounds = {{"_n_events_cc": 10, "_priced_rows": 7, "_a_rows_bound": 3}}
        for name, (cap, campaign, usd, spent, budget) in json.loads({json.dumps(json.dumps(cases))}).items():
            d.CAP_USD = cap
            proj = {{"complete": True, "missing": [], "bounds": bounds, "jobs": {{"triples": {{"first": 10**9,
                    "whole": 10**9}}}}, "bytes": 10**9, "usd": usd}}
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                d.print_projection(proj, {{"triples": 36}}, campaign, spent, budget)
            out[name] = {{"stdout": buf.getvalue(), "over": d.over_cap(usd, campaign, spent, budget)}}
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            d.print_projection({{"complete": False, "missing": ["c12_events_cc"], "bounds": bounds, "usd": None}},
                               {{}}, 1.0, 1.0, 60.0)
        out["incomplete"] = {{"stdout": buf.getvalue()}}
        print(json.dumps(out))
    """)
    for name, ((cap, campaign, usd, spent, budget), want) in NEEDED.items():
        lines = r[name]["stdout"].splitlines()
        needed = [line for line in lines if re.match(r"(cap|budget) needed: ", line)]
        assert needed == list(want), (name, needed)
        assert lines[-2:] == list(want), (name, lines[-3:])            # the last two lines of the projection
        # within or above exactly as over_cap judges it, and the amount the least whole cent it does not pass
        over = r[name]["over"]
        assert ("above" in want[0]) == any("passes the cap" in o for o in over), name
        assert ("above" in want[1]) == any("passes the budget" in o for o in over), name
        assert want[0] == (f"cap needed: USD {least_cent(campaign + usd):.2f} "
                           f"({'above' if campaign + usd > cap else 'within'} the cap of USD {cap:.2f})"), name
        assert want[1].startswith(f"budget needed: USD {least_cent(spent + usd):.2f}, "), name
    # the rounded figures of the line before say 14.00 of 14.00 although the sum passes the cap
    assert ("campaign USD 11.00 + 3.00 = 14.00 of 14.00" in r["rounds_to_the_cap"]["stdout"]
            and "passes the cap" in r["rounds_to_the_cap"]["over"][0])
    assert "needed" not in r["incomplete"]["stdout"] and "projection: waits for c12_events_cc" in r["incomplete"][
        "stdout"]


def test_command_carries_the_checks_of_run_bq():
    r = run_json("""
        import json
        import run_contract12m_pipeline as d
        from common import load_config
        cfg = load_config()
        job = d.jobs(cfg)["activity"][0]
        labels = {j.key: j for j in d.all_jobs(cfg)}["labels_w0"]
        est = d.estimates({t: 10**6 for t in d.ESTIMATE_TABLES})["labels_w0"]
        print(json.dumps({"activity": d.command(job, d.Estimate(1000, 3000), dry=True)[1:],
                          "labels": d.command(labels, est, dry=False)[1:], "first": est.first, "whole": est.whole,
                          "cap": d.CAP_USD}))
    """)
    a = r["activity"]
    flag = lambda cmd, name: cmd[cmd.index(name) + 1]  # noqa: E731
    assert a[0] == "scripts/run_bq.py" and a[1] == "sql/26_c12_tx_senders.sql" and a[-1] == "--dry-run"
    assert flag(a, "--label").startswith("contract12m: ") and flag(a, "--require-prefix") == "c12_"
    assert flag(a, "--campaign") == "contract12m:" and flag(a, "--campaign-cap") == str(r["cap"]) == str(CAP_USD)
    assert flag(a, "--expect-bytes") == "3000" and flag(a, "--max-dry-bytes") == "1250"
    assert flag(a, "--allow-public") == "bigquery-public-data.goog_blockchain_arbitrum_one_us.transactions"
    assert flag(a, "--param") == "end_ts=2026-10-01 00:00:00 UTC" and "--force" not in a
    c = r["labels"]
    values = lambda name: [c[i + 1] for i, x in enumerate(c) if x == name]  # noqa: E731
    assert c[:2] == ["scripts/run_bq.py", "sql/39_c12_label_parts.sql"] and "--dry-run" not in c
    assert values("--sub") == ["TAG=w0", "FREEZE=t1", "APPROVALS=u12_approvals_t1", "TRANSFERS=u12_transfers_t1",
                               "SEEN=u12_transfers_t1", "LOGS=logs_obs"]
    assert len(values("--allow-read")) == 5 and len(values("--param")) == 4
    assert flag(c, "--require-prefix") == "c12_" and flag(c, "--campaign") == "contract12m:"
    assert flag(c, "--campaign-cap") == str(CAP_USD) and flag(c, "--label") == "contract12m: W0 label parts by " \
                                                                                "account class"
    assert flag(c, "--expect-bytes") == str(r["whole"]) and flag(c, "--max-dry-bytes") == str(int(1.25 * r["first"]))
    assert "--allow-public" not in c and "--force" not in c


# --------------------------------------------------------------------------- committed files and the order of the steps


def test_inputs_refuse_uncommitted_files(tmp_path):
    out = run_py("""
        import run_contract12m_pipeline as d
        d.git = lambda *a: " M docs/revision_contract_graph.md" if a[0] == "status" else "abc"
        try:
            d.inputs(False)
            print("ran")
        except SystemExit as e:
            print("refused" if str(e).startswith("refused") else "other")
        print(sorted(d.inputs(True)))  # a dry run only warns
        d.git = lambda *a: "" if a[0] == "status" else "abc"
        d.COMMITTED = tuple(r for r in d.COMMITTED if (d.ROOT / r).exists())
        print(sorted(d.inputs(False)["sha256"]) == sorted(d.COMMITTED))
    """)
    assert out.returncode == 0, out.stderr
    lines = out.stdout.strip().splitlines()
    assert lines[0] == "refused"
    assert "warning: not committed" in out.stdout
    assert lines[-2] == "['head', 'revision_commit', 'sha256']" and lines[-1] == "True"
    # A gate B step checks COMMITTED_B as well, and refuses on it even in a dry run; a gate A step does not read it.
    r = run_gate_b(tmp_path, r'''
        out = {}
        root, calls, seen, git_calls = prepare("dirty", {"status": {"sql/37_c12_pairs.sql": " M sql/37_c12_pairs.sql"}})
        for label, call in (("dry_b", lambda: d.inputs(True, gate_b=True)),
                            ("run_b", lambda: d.inputs(False, gate_b=True)),
                            ("dry_a", lambda: d.inputs(True)), ("run_a", lambda: d.inputs(False))):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                try:
                    call()
                    res = "ok"
                except SystemExit as e:
                    res = str(e)
            out[label] = {"result": res, "stdout": buf.getvalue()}
        root, calls, seen, git_calls = prepare("clean", {})
        v = d.inputs(False, gate_b=True)
        out["clean"] = {"keys": sorted(v["sha256"]), "files": sorted(list(d.COMMITTED) + list(d.COMMITTED_B)),
                        "match": all(v["sha256"][rel] == sha(root / rel) for rel in v["sha256"]), "head": v["head"]}
        print(json.dumps(out))
    ''', {})
    for label in ("dry_b", "run_b"):
        assert r[label]["result"] == "refused: not committed without local changes: sql/37_c12_pairs.sql", label
    assert r["dry_a"] == {"result": "ok", "stdout": ""} and r["run_a"]["result"] == "ok"
    assert r["clean"]["keys"] == r["clean"]["files"] and r["clean"]["match"] and r["clean"]["head"] == "abc123"
    assert FEASIBILITY_REL in r["clean"]["keys"] and "sql/42_c12_checks.sql" in r["clean"]["keys"]


def test_steps_wait_for_the_steps_before_them():
    r = run_json("""
        import json
        import run_contract12m_pipeline as d

        def m(*runs, check=()):
            return {"steps": [{"step": s, "passed": p} for s, p in runs],
                    "checks_run": [] if check is None else [{"problems": list(check)}]}

        passed = [(s, True) for s in d.CHAIN]
        upto = lambda step: passed[:d.CHAIN.index(step)]  # noqa: E731
        gate_a = [(s, True) for s in d.CHAIN_A]
        gate_b = [(s, True) for s in ("constants", "pairs", "rest", "checks", "download")]
        print(json.dumps({
            "chain": list(d.CHAIN), "steps": list(d.STEPS),
            "free": [d.prerequisites("check", m(check=None))],
            "constants": d.prerequisites("constants", m(*gate_a)),
            "constants_after_failed_structure": d.prerequisites("constants", m(*gate_a, ("structure", False))),
            "pairs_after_constants_again": d.prerequisites("pairs", m(*gate_a, *gate_b, ("constants", True))),
            "download_after_constants_again": d.prerequisites("download", m(*gate_a, *gate_b, ("constants", True))),
            "checks_without_pairs": d.prerequisites("checks", m(*gate_a, ("constants", True), ("constants", True))),
            "subset": [d.prerequisites("subset", m()), d.prerequisites("subset", m(check=None)),
                       d.prerequisites("subset", m(check=["the dataset has a default expiration"]))],
            "structure": d.prerequisites("structure", m(*upto("structure"))),
            "audit_failed": d.prerequisites("structure", m(*upto("audit"), ("audit", False))),
            "audit_missing": d.prerequisites("structure", m(*upto("audit"))),
            "balances_again": d.prerequisites("structure", m(*upto("structure"), ("balances", True))),
            "then_again": d.prerequisites("structure", m(*upto("structure"), ("balances", True), ("anchors", True),
                                                         ("audit", True))),
            "anchors_early": d.prerequisites("anchors", m(*upto("typing"))),
            "unfinished": d.prerequisites("load", m(*upto("typing"), ("typing", None))),
            # check is the first gate A step: every later step waits for a last check without problems
            "later_check_failed": {s: d.prerequisites(s, m(*upto(s), check=["logs_obs was modified on 2026-11-08"]))
                                   for s in d.CHAIN},
            "later_no_check": d.prerequisites("balances", m(*upto("balances"), check=None)),
        }))
    """)
    assert r["chain"] == r["steps"][1:] and len(r["chain"]) == 16
    assert r["free"] == [[]]
    assert r["constants"] == []
    assert r["constants_after_failed_structure"] == ["a run of structure that passes (the last one did not)"]
    assert r["pairs_after_constants_again"] == []
    assert r["download_after_constants_again"] == ["a run of pairs after the last run of constants",
                                                   "a run of rest after the last run of constants",
                                                   "a run of checks after the last run of constants"]
    assert r["checks_without_pairs"] == ["a run of pairs", "a run of rest"]
    assert r["subset"] == [[], ["a check without problems"], ["a check without problems (the last one found some)"]]
    assert r["structure"] == [] and r["then_again"] == []
    assert r["audit_failed"] == ["a run of audit that passes (the last one did not)"]
    assert r["audit_missing"] == ["a run of audit"]
    # balances run again after the balance check: the anchors and the check must be run again
    assert r["balances_again"] == ["a run of anchors after the last run of balances",
                                   "a run of audit after the last run of balances"]
    assert r["anchors_early"] == ["a run of typing", "a run of load", "a run of contracts", "a run of balances"]
    assert r["unfinished"] == ["a run of typing that passes (the last one did not)"]
    assert r["later_check_failed"] == {s: ["a check without problems (the last one found some)"] for s in r["chain"]}
    assert r["later_no_check"] == ["a check without problems"]


# --------------------------------------------------------------------------- the gate A steps audit and structure


# The audit and structure steps with BigQuery, the downloads and the two local scripts faked (nothing is run or
# billed). Each case starts from a manifest whose steps before audit (or before structure) passed, with an earlier
# balance_audit.json and feasibility_t1.json on disk, and a protocol whose 'Protocol fixed' holds no block yet.
STEPS_FAKED = r"""
    import json, sys, types
    from pathlib import Path
    import pandas as pd
    import run_contract12m_pipeline as d
    from common import load_config

    cfg = load_config()
    pairs = [(f"0x{i:040x}", f"0x{i + 1:040x}", "allow_capped") for i in range(6000)]
    d.client_and_dataset = lambda cfg: (None, "dissertation-bq.contract_rep")
    d.inputs = lambda dry, gate_b=False: {"head": "abc123"}
    d.Run.job = lambda self, job: calls.append(f"job {job.no}")
    d.Run.sizes = lambda self, *names: {n: 6000 for n in names}
    d.sh = lambda cmd: calls.append("download " + cmd[2].split(".")[-1])
    d.read_parts = lambda stem, columns=None: pd.DataFrame(pairs, columns=["a", "b", "layer"])
    d.lists_applied = lambda m: ""  # the guard of the smart-account lists has its own test

    def fake_run(cmd, cwd=None):  # scripts/balance_audit.py and the structure pilot
        name = Path(cmd[1]).name
        calls.append(name)
        rc, write = script[name]
        if write:
            path = d.BALANCE_AUDIT if name == "balance_audit.py" else d.FEASIBILITY
            listed = [rel for rel in d.PILOT_COMMITTED if rel != "scripts/graphs.py" or case != "pilot_partial"]
            code = {"committed": {rel: rel != "scripts/scoring.py" or case != "pilot_dirty" for rel in listed}}
            path.write_text(json.dumps({"passed": rc == 0, "U": 7, "stopped": False, "run": "this one", "code": code}))
        return types.SimpleNamespace(returncode=rc)

    d.subprocess.run = fake_run
    out = {}
    for case in sys.argv[2:]:
        tmp = Path(sys.argv[1]) / case
        tmp.mkdir()
        d.ROOT = tmp
        d.MANIFEST, d.BALANCE_AUDIT, d.FEASIBILITY = (tmp / n for n in ("run_manifest.json", "balance_audit.json",
                                                                         "feasibility_t1.json"))
        d.PROTOCOL = tmp / "protocol.md"
        d.PROTOCOL.write_text("## Protocol fixed\n\n(Added at gate B.)\n", encoding="utf-8")
        first = "structure" if case.startswith("pilot") else "audit"
        steps = [{"step": s, "passed": True} for s in d.CHAIN[:d.CHAIN.index(first)]]
        if case in ("audit_failed", "decision"):
            steps.append({"step": "audit", "passed": False})
        d.MANIFEST.write_text(json.dumps({"variant": "contract12m", "steps": steps, "jobs": [], "results": {},
                                          "checks_run": [{"problems": []}]}))
        d.BALANCE_AUDIT.write_text(json.dumps({"passed": True, "share": 0.9958, "run": "an earlier one"}))
        d.FEASIBILITY.write_text(json.dumps({"U": 5, "run": "an earlier one"}))
        script = {"balance_audit.py": (2, False) if case == "audit_stale" else (0, True),  # no endpoint answered
                  "run_discovery.py": (1, False) if case == "pilot_stale" else (0, True)}  # refused, no report
        d.AUTHOR_DECISION = "the failed pairs are understood" if case == "decision" else None
        calls, results = [], []
        for step in (["structure"] if first == "structure" or case in ("audit_failed", "decision")
                     else ["audit", "structure"]):
            try:
                getattr(d, f"step_{step}")(cfg, False)
                results.append("ok")
            except SystemExit as e:
                results.append(str(e))
        out[case] = {"results": results, "calls": calls, "manifest": json.loads(d.MANIFEST.read_text())}
    print(json.dumps(out))
"""


CONTRACTS_FAKED = r"""
    import json, sys, types
    from pathlib import Path
    import pandas as pd
    import run_contract12m_pipeline as d
    from common import load_config

    cfg = load_config()
    EXT = {"typed_contracts": 100, "moved": 10, "moved_by_code_hash": 4, "moved_by_implementation": 6,
           "contracts_after": 90}
    GOOD, BAD = {"c12_contracts": 90, "c12_user_accounts": 510, "c12_events_cc": 7}, \
        {"c12_contracts": 90, "c12_user_accounts": 500, "c12_events_cc": 7}
    pairs = [(f"0x{i:040x}", f"0x{i + 1:040x}", "allow_capped") for i in range(6000)]
    d.client_and_dataset = lambda cfg: (None, "dissertation-bq.contract_rep")
    d.inputs = lambda dry: {"head": "abc123"}
    d.sh = lambda cmd: calls.append("download")
    d.read_parts = lambda stem, columns=None: pd.DataFrame(pairs, columns=["a", "b", "layer"])
    d.typed_extension = lambda m: (None, "c12_account_types is not on disk") if state["no_parts"] else (EXT, "")

    def job(self, j):
        calls.append(f"job {j.no}" + (" dry" if self.dry else ""))
        if j.no == 31 and not self.dry and state["job_error"]:
            raise SystemExit("stopped: job 31 failed")

    d.Run.job = job
    d.Run.sizes = lambda self, *names: {n: {**state["sizes"], "c12_struct_t1": 6000}[n] for n in names}

    def fake_run(cmd, cwd=None):  # the structure pilot
        calls.append(Path(cmd[1]).name)
        code = {"committed": {rel: True for rel in d.PILOT_COMMITTED}}
        d.FEASIBILITY.write_text(json.dumps({"U": 7, "stopped": False, "code": code}))
        return types.SimpleNamespace(returncode=0)

    d.subprocess.run = fake_run
    out = {}
    for case in sys.argv[2:]:
        tmp = Path(sys.argv[1]) / case
        tmp.mkdir()
        d.ROOT = tmp
        d.MANIFEST, d.FEASIBILITY = tmp / "run_manifest.json", tmp / "feasibility_t1.json"
        d.PROTOCOL = tmp / "protocol.md"            # before gate B: 'Protocol fixed' holds no block
        d.PROTOCOL.write_text("## Protocol fixed\n\n(Added at gate B.)\n", encoding="utf-8")
        # the runs of 8 November 2026: every step of gate A passed, job 31 without the lists
        steps = [{"step": s, "passed": True} for s in d.CHAIN_A]
        d.MANIFEST.write_text(json.dumps({"variant": "contract12m", "steps": steps, "jobs": [], "checks_run": [
            {"problems": []}], "results": {"contracts": {"c12_contracts": 100, "c12_user_accounts": 500,
                                                         "c12_events_cc": 7}}}))
        plan = {"refused_no_parts": [("contracts", False, dict(no_parts=True))],
                "dry_no_parts": [("contracts", True, dict(no_parts=True)), ("structure", True, dict(no_parts=True))],
                "size_fail_then_good": [("contracts", False, dict(sizes=BAD)), ("contracts", False, dict(sizes=GOOD))],
                "job_fail_then_good": [("contracts", False, dict(sizes=GOOD)), ("contracts", False, dict(job_error=True)),
                                       ("contracts", False, dict(sizes=GOOD))],
                "structure_first": [("structure", False, dict(decision="jobs 32 to 34 and 43 stand"))],
                "structure_after": [("contracts", False, dict(sizes=GOOD)),
                                    ("structure", False, dict(decision="jobs 32 to 34 and 43 stand"))]}[case]
        calls, results = [], []
        for step, dry, opts in plan:
            state = {"no_parts": False, "job_error": False, "sizes": GOOD, **opts}
            d.AUTHOR_DECISION = opts.get("decision")
            try:
                getattr(d, f"step_{step}")(cfg, dry)
                results.append("ok")
            except SystemExit as e:
                results.append(str(e))
        out[case] = {"results": results, "calls": calls, "manifest": json.loads(d.MANIFEST.read_text())}
    print(json.dumps(out))
"""


def test_the_steps_of_job_31_and_job_35_keep_to_the_smart_account_lists(tmp_path):
    # Revision section 13, amendment of 9 November 2026: contracts checks the lists before it is recorded and the
    # sizes after the job against the last run that passed; structure refuses, whatever the author decides, until a
    # run of contracts with the lists passed.
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8",
           "CONTRACT_REP_VARIANT": "contract12m"}
    env.pop("CONTRACT_REP_RPC_URL", None)
    cases = ["refused_no_parts", "dry_no_parts", "size_fail_then_good", "job_fail_then_good", "structure_first",
             "structure_after"]
    out = subprocess.run([sys.executable, "-c", textwrap.dedent(CONTRACTS_FAKED), str(tmp_path), *cases], cwd=SCRIPTS,
                         env=env, capture_output=True, text=True, encoding="utf-8")
    assert out.returncode == 0, out.stderr
    r = json.loads(out.stdout.strip().splitlines()[-1])
    n = len(STEPS_IN_CHAIN)
    c = r["refused_no_parts"]
    assert c["results"] == ["refused: c12_account_types is not on disk (revision section 13, amendment of "
                            "9 November 2026)"]
    assert c["calls"] == [] and len(c["manifest"]["steps"]) == n  # nothing was recorded
    c = r["dry_no_parts"]
    assert c["results"] == ["ok", "ok"] and c["calls"] == ["job 31 dry", "job 35 dry"]
    assert len(c["manifest"]["steps"]) == n
    c = r["size_fail_then_good"]
    assert c["results"][0].startswith("stopped: job 31 gave") and c["results"][1] == "ok"
    runs = [e for e in c["manifest"]["steps"] if e["step"] == "contracts"][-2:]
    assert [e["passed"] for e in runs] == [False, True]
    res = c["manifest"]["results"]["contracts"]
    assert res["expected"] == {"c12_contracts": 90, "c12_user_accounts": 510}  # from the run that passed
    assert res["previous"]["c12_contracts"] == 100 and res["smart_account_extension"]["moved"] == 10
    c = r["job_fail_then_good"]
    assert c["results"] == ["ok", "stopped: job 31 failed", "ok"]
    res = c["manifest"]["results"]["contracts"]
    # judged against the run with the lists, which moved the same contracts: both sizes stay
    assert res["expected"] == {"c12_contracts": 90, "c12_user_accounts": 510}
    assert res["previous"]["c12_contracts"] == 90
    c = r["structure_first"]
    assert c["results"] == ["refused: the last run of contracts was not made with the smart-account lists; run "
                            "contracts first (revision section 13, amendment of 9 November 2026)"]
    assert c["calls"] == [] and len(c["manifest"]["steps"]) == n
    c = r["structure_after"]
    assert c["results"] == ["ok", "ok"] and c["calls"] == ["job 31", "job 35", "download", "run_discovery.py"]
    last = c["manifest"]["steps"][-1]
    assert (last["step"], last["passed"], last["author_decision"]) == ("structure", True, "jobs 32 to 34 and 43 stand")
    assert last["waited_for"] == [f"a run of {s} after the last run of contracts" for s in ("balances", "anchors",
                                                                                         "audit")]


STEPS_IN_CHAIN = ("subset", "ends", "activity", "queue", "typing", "load", "contracts", "balances", "anchors", "audit",
                  "structure")


def test_a_failed_or_missing_balance_check_stops_the_structure_step(tmp_path):
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8",
           "CONTRACT_REP_VARIANT": "contract12m"}
    env.pop("CONTRACT_REP_RPC_URL", None)
    cases = ["audit_failed", "decision", "audit_stale", "audit_fresh", "pilot_stale", "pilot_dirty", "pilot_partial"]
    out = subprocess.run([sys.executable, "-c", textwrap.dedent(STEPS_FAKED), str(tmp_path), *cases], cwd=SCRIPTS,
                         env=env, capture_output=True, text=True, encoding="utf-8")
    assert out.returncode == 0, out.stderr
    r = json.loads(out.stdout.strip().splitlines()[-1])
    audit, structure = ["job 43", "download c12_bal_audit", "download c12_anchor_blocks", "balance_audit.py"], \
        ["job 35", "download c12_struct_t1", "run_discovery.py"]
    # after a failed balance check, structure refuses before job 35, the download and the pilot
    c = r["audit_failed"]
    assert c["results"] == ["refused: structure waits for a run of audit that passes (the last one did not) (the "
                            "steps run in the order of STEPS; --author-decision TEXT goes on all the same and is "
                            "recorded)"]
    assert c["calls"] == [] and len(c["manifest"]["steps"]) == 10
    # unless the author decides; the manifest records the decision and what was missing
    c = r["decision"]
    assert c["results"] == ["ok"] and c["calls"] == structure
    last = c["manifest"]["steps"][-1]
    assert (last["step"], last["passed"], last["author_decision"]) == ("structure", True,
                                                                      "the failed pairs are understood")
    assert last["waited_for"] == ["a run of audit that passes (the last one did not)"]
    assert "after_gate_b" not in last                     # a gate A decision is not one taken after gate B
    # balance_audit.py exits before writing (exit 2: no endpoint gave a block, so no check was made): the earlier
    # passing verdict is not this run's, the step is to be run again, and structure waits
    c = r["audit_stale"]
    assert c["results"][0].startswith("stopped: the balance check gave no result (exit 2, no new balance_audit.json")
    assert "run the audit step again" in c["results"][0]
    assert c["results"][1].startswith("refused: structure waits for a run of audit that passes")
    assert c["calls"] == audit
    assert c["manifest"]["results"]["audit"]["balance_audit"] is None and c["manifest"]["steps"][-1]["passed"] is False
    c = r["audit_fresh"]
    assert c["results"] == ["ok", "ok"] and c["calls"] == audit + structure
    assert c["manifest"]["results"]["audit"]["balance_audit"]["passed"] is True
    assert c["manifest"]["results"]["structure"]["feasibility"]["U"] == 7
    assert [s["passed"] for s in c["manifest"]["steps"][-2:]] == [True, True]
    # the pilot writes no report: the earlier feasibility_t1.json is not this run's result
    c = r["pilot_stale"]
    assert c["results"] == ["stopped: the structure pilot exited with 1 or wrote no feasibility_t1.json"]
    assert c["manifest"]["results"]["structure"]["feasibility"] is None
    assert c["manifest"]["steps"][-1]["passed"] is False and c["calls"] == structure
    # a pilot on files with local changes would be refused by the main runs: the step stops at once
    c = r["pilot_dirty"]
    assert c["results"][0].startswith("stopped: the structure pilot did not run on committed files (scripts/scoring.py)")
    assert c["manifest"]["results"]["structure"]["pilot_not_committed"] == ["scripts/scoring.py"]
    assert c["manifest"]["steps"][-1]["passed"] is False
    # a pilot whose record lacks a file of PILOT_COMMITTED stops the step as well
    c = r["pilot_partial"]
    assert c["results"][0].startswith("stopped: the structure pilot did not run on committed files (scripts/graphs.py)")
    assert c["manifest"]["results"]["structure"]["pilot_not_committed"] == ["scripts/graphs.py"]
    assert c["manifest"]["steps"][-1]["passed"] is False


# --------------------------------------------------------------------------- the gate B refusals


P17_CASES = {"no_block": {"block": "none"}, "no_date": {"block": "no_date"}, "wrong_sha": {"block": "wrong_sha"},
             "other_pilot": {"structure": "other_sha"}, "no_pilot": {"structure": "no_pilot"},
             "stopped_pilot": {"pilot_inputs": {"allow_capped_edges": 100}}, "valid": {},
             "decided": {"block": {"author_decision": "re-serialised", "sha256": "0" * 64}}}
# The first result of each refused case (it starts with the first text and contains the second).
P17_REFUSED = {
    "no_block": ("refused: docs/discovery_protocol.md has no filled section 'Protocol fixed'", ""),
    "no_date": ("refused: 'Protocol fixed' lacks ['date']", ""),
    "wrong_sha": ("refused: the SHA-256 in 'Protocol fixed' does not match", FEASIBILITY_REL),
    "other_pilot": ("refused: 'Protocol fixed' pins", "the structure step wrote ffffffffffff"),
    "no_pilot": ("refused: the run manifest records no pilot written by the structure step", ""),
    "stopped_pilot": ("refused: the structure pilot stopped the run", ""),
    "decided": ("refused: 'Protocol fixed' pins 000000000000", "")}
CONSTANTS_FIRST = f"refused: the constants must be committed on their own before this step: {CONSTANTS_REL} is " \
                  f"missing; run the 'constants' step first"


@pytest.fixture(scope="module")
def protocol_cases(tmp_path_factory) -> dict:
    return run_gate_b(tmp_path_factory.mktemp("p17"), r'''
        out = {}
        for cname, case in SPEC["cases"].items():
            for step in d.GATE_B:
                for dry in (False, True):
                    r = run_case(f"{cname}-{step}-{int(dry)}", {**case, "dry": dry}, [step])
                    r["last"] = r.pop("manifest")["steps"][-1]
                    r["feasibility_sha256"] = sha(d.FEASIBILITY)
                    out[f"{cname}|{step}|{int(dry)}"] = r
        print(json.dumps(out))
    ''', P17_CASES)


@pytest.mark.parametrize("case", list(P17_CASES))
def test_gate_b_steps_refuse_unless_the_protocol_is_fixed(protocol_cases, case):
    """Revision section 12, protocol section 8: every gate B step, its dry run too, refuses unless 'Protocol fixed'
    passes run_discovery.check_fixed and pins the pilot that the structure step wrote (the three hashes agree, even
    with an author_decision)."""
    for step in GATE_B_STEPS:
        r = {dry: protocol_cases[f"{case}|{step}|{dry}"] for dry in (0, 1)}
        if case in P17_REFUSED:
            start, also = P17_REFUSED[case]
            for dry in (0, 1):
                (res,) = r[dry]["results"]
                assert res.startswith(start) and also in res, (step, dry, res)
                assert r[dry]["calls"] == [] and r[dry]["manifest_changed"] is False, (step, dry)
                assert r[dry]["git"] == [], (step, dry)            # the check of 'Protocol fixed' reads no git
            assert r[0]["results"] == r[1]["results"], step        # the same text dry or not
            continue
        # valid: constants reaches its first job; the later steps need the constants committed on their own
        if step == "constants":
            for dry in (0, 1):
                assert r[dry]["results"] == ["reached triples"], dry
            last = r[0]["last"]
            assert r[0]["manifest_changed"] and last["step"] == "constants" and "passed" not in last
            assert last["gate_b"]["protocol_fixed"]["pinned_sha256"] == r[0]["feasibility_sha256"]
            assert last["gate_b"]["protocol_fixed"]["date"] == "2026-11-09"
            assert last["gate_b"]["constants"] is None
        else:
            assert r[0]["results"] == [CONSTANTS_FIRST] and r[0]["calls"] == [], step
            assert r[0]["manifest_changed"] is False, step
            assert "warning: the constants must be committed on their own before this step:" in r[1]["stdout"], step
            if step == "download":          # no job: the dry run prints the 16 commands and returns
                assert r[1]["results"] == ["ok"] and r[1]["calls"] == []
                assert r[1]["stdout"].count("$ scripts/download_table.py contract_rep.") == 16
            else:
                assert r[1]["results"] == [f"reached {FIRST_JOB[step]}"], step
        assert r[1]["manifest_changed"] is False, step


P18_RELS = ("sql/36_c12_constants.sql", "scripts/run_registered.py", FEASIBILITY_REL, "scripts/common.py")


@pytest.fixture(scope="module")
def uncommitted_cases(tmp_path_factory) -> dict:
    return run_gate_b(tmp_path_factory.mktemp("p18"), r'''
        out = {}
        order = list(d.GATE_B)
        for i, rel in enumerate(SPEC["cases"]):
            for how in ("modified", "never"):
                change = {"status": {rel: " M " + rel}} if how == "modified" else {"log": {rel: ""}}
                for step in order:
                    for dry in (False, True):
                        case = {**change, "dry": dry, "constants": None if step == "constants" else "committed",
                                "steps": [[s, True] for s in order[1:order.index(step)]]}
                        r = run_case(f"r{i}-{how}-{step}-{int(dry)}", case, [step])
                        r.pop("manifest")
                        out[f"{rel}|{how}|{step}|{int(dry)}"] = r
                prepare(f"r{i}-{how}-gate_a", change)
                try:
                    d.inputs(False)
                    out[f"{rel}|{how}|gate_a"] = "ok"
                except SystemExit as e:
                    out[f"{rel}|{how}|gate_a"] = str(e)
        rel = SPEC["cases"][0]
        for step in order:              # 'Protocol fixed' is checked before the files
            r = run_case(f"order-{step}", {"block": "none", "status": {rel: " M " + rel}}, [step])
            out[f"order|{step}"] = r["results"]
        print(json.dumps(out))
    ''', list(P18_RELS))


@pytest.mark.parametrize("rel", P18_RELS)
def test_gate_b_steps_refuse_uncommitted_gate_b_files(uncommitted_cases, rel):
    """Revision section 12 and its gate B amendment: a gate B step refuses, dry or not, a file of COMMITTED or
    COMMITTED_B with local changes or never committed, after 'Protocol fixed' and the constants passed and before any
    job; a gate A step checks only COMMITTED."""
    for how in ("modified", "never"):
        for step in GATE_B_STEPS:
            for dry in (0, 1):
                r = uncommitted_cases[f"{rel}|{how}|{step}|{dry}"]
                assert r["results"] == [f"refused: not committed without local changes: {rel}"], (how, step, dry)
                assert r["calls"] == [] and "$" not in r["stdout"], (how, step, dry)
                assert r["manifest_changed"] is False, (how, step, dry)
        gate_a = uncommitted_cases[f"{rel}|{how}|gate_a"]
        if rel == "scripts/common.py":                   # a file of COMMITTED: gate A refuses it too
            assert gate_a == f"refused: not committed without local changes: {rel}", how
        else:
            assert gate_a == "ok", how
    for step in GATE_B_STEPS:                            # 'Protocol fixed' first
        (res,) = uncommitted_cases[f"order|{step}"]
        assert res.startswith("refused: docs/discovery_protocol.md has no filled section 'Protocol fixed'"), res


def test_gate_a_steps_refuse_once_the_protocol_is_fixed(tmp_path):
    """Revision section 12: once 'Protocol fixed' holds a block, every gate A step from subset to structure refuses
    before it creates a client, records or runs anything, dry or not."""
    r = run_gate_b(tmp_path, r'''
        def files(root):
            return {p.relative_to(root).as_posix(): sha(p) for p in sorted(root.rglob("*")) if p.is_file()}

        out = {}
        for step in d.CHAIN_A:
            for dry in (False, True):
                name = f"{step}-{int(dry)}"
                root, calls, seen, git_calls = prepare(name, {"client": "raise"})
                before, buf = files(root), io.StringIO()
                with contextlib.redirect_stdout(buf):
                    try:
                        getattr(d, f"step_{step}")(cfg, dry)
                        res = "ok"
                    except SystemExit as e:
                        res = str(e)
                out[name] = {"result": res, "same": files(root) == before, "calls": calls, "git": git_calls,
                             "stdout": buf.getvalue()}
        root, calls, seen, git_calls = prepare("open", {"client": "raise", "block": "none"})
        try:
            d.step_subset(cfg, True)
            out["open"] = "ok"
        except SystemExit as e:
            out["open"] = str(e)
        print(json.dumps(out))
    ''', {})
    chain_a = ("subset", "ends", "activity", "queue", "typing", "load", "contracts", "balances", "anchors", "audit",
               "structure")
    for step in chain_a:
        for dry in (0, 1):
            c = r[f"{step}-{dry}"]
            assert c["result"] == (f"refused: {step} is a gate A step, and docs/discovery_protocol.md holds 'Protocol "
                                   "fixed': no step from subset to structure runs again after gate B "
                                   "(docs/revision_contract_graph.md section 12)"), (step, dry)
            assert c["same"] and c["calls"] == [] and c["git"] == [] and c["stdout"] == "", (step, dry)
    assert r["open"] == "client created"         # without a block the check lets subset through


P20_CASES = {"structure_constants": {"args": ["structure", "constants", "--dry-run"]},
             "check_structure": {"args": ["check", "structure"]},
             "constants_pairs": {"args": ["constants", "pairs"]},
             "pairs_without_block": {"args": ["pairs"], "block": "none"},
             "constants_dirty": {"args": ["constants"],
                                 "status": {"sql/42_c12_checks.sql": " M sql/42_c12_checks.sql"}}}


def test_main_refuses_before_any_step_runs(tmp_path):
    """Revision section 12: a command line one of whose steps would be refused at its start is refused before any of
    them runs."""
    r = run_gate_b(tmp_path, r'''
        out = {}
        for cname, case in SPEC["cases"].items():
            prepare(cname, case)
            ran = []
            for s in d.STEPS:
                setattr(d, f"step_{s}", (lambda s: lambda cfg, dry: ran.append(s))(s))
            sys.argv = ["run_contract12m_pipeline.py", *case["args"]]
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                try:
                    res = f"returned {d.main()}"
                except SystemExit as e:
                    res = str(e)
            out[cname] = {"result": res, "ran": ran, "stdout": buf.getvalue()}
        print(json.dumps(out))
    ''', P20_CASES)
    gate_a = "refused: structure is a gate A step"
    assert r["structure_constants"]["result"].startswith(gate_a)
    assert r["check_structure"]["result"].startswith(gate_a) and "windows:" not in r["check_structure"]["stdout"]
    assert r["constants_pairs"]["result"].startswith(
        f"refused: pairs needs the constants committed on their own: {CONSTANTS_REL} is missing")
    assert r["pairs_without_block"]["result"].startswith(
        "refused: docs/discovery_protocol.md has no filled section 'Protocol fixed'")
    assert r["constants_dirty"]["result"] == "refused: not committed without local changes: sql/42_c12_checks.sql"
    for name, c in r.items():
        assert c["ran"] == [] and "$" not in c["stdout"], name


# --------------------------------------------------------------------------- the constants


ROW = {"m_transfer": 169.33098583990733, "p99_transfer": 18575.27831372273, "p10_transfer": 0.2,
       "p90_transfer": 2421.4, "n_transfers": 492666999, "m_allowance": 99.97003979708168, "p99_allowance": 1e5,
       "p10_allowance": 1.1, "p90_allowance": 9.9e4, "n_latest_allowances": 5000, "n_positive_allowances": 4000,
       "n_capped_to_zero": 1000, "n_capped_below_allowance": 800, "n_unlimited_positive": 300,
       "m_user_transfer": 20.5, "p99_user_transfer": 2481.7, "p10_user_transfer": 0.5, "p90_user_transfer": 900.0,
       "n_user_transfers": 12345678}
P21_BASE = {"sizes": {"c12_allow_triples": 7, "c12_user_events": 8, "c12_constants": 1},
            "rows": {"c12_constants": [ROW]}, "stop_at_job": False}
P21_CASES = {"ok": P21_BASE,
             **{f"m_transfer_{k}": {**P21_BASE, "rows": {"c12_constants": [{**ROW, "m_transfer": v}]}}
                for k, v in (("none", None), ("zero", 0), ("nan", float("nan")), ("negative", -5))},
             "u_user_0994": {**P21_BASE, "rows": {"c12_constants": [{**ROW, "p99_user_transfer": 0.994}]}},
             "u_user_0996": {**P21_BASE, "rows": {"c12_constants": [{**ROW, "p99_user_transfer": 0.996}]}},
             "two_rows": {**P21_BASE, "rows": {"c12_constants": [ROW, ROW]}},
             "columns": {**P21_BASE, "rows": {"c12_constants": [{k: v for k, v in ROW.items()
                                                                 if k != "n_user_transfers"}]}},
             "dry": {**P21_BASE, "dry": True},
             "committed": {**P21_BASE, "constants": "committed"},
             "committed_dry": {**P21_BASE, "constants": "committed", "dry": True}}


@pytest.fixture(scope="module")
def constants_cases(tmp_path_factory) -> dict:
    before = real_state()
    r = run_gate_b(tmp_path_factory.mktemp("p21"), r'''
        out = {}
        for cname, case in SPEC["cases"].items():
            # one path: the step writes ROOT / CONSTANTS_REL, whatever common.USD_CONSTANTS says
            elsewhere = Path(SPEC["tmp"]) / "elsewhere" / cname / "constants.json"
            r = run_case(cname, case, ["constants"], setup=lambda root: setattr(d, "USD_CONSTANTS", elsewhere))
            r["elsewhere"] = elsewhere.exists()
            path = Path(SPEC["tmp"]) / cname / d.CONSTANTS_REL
            r["file"] = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
            r["file_sha256"] = sha(path) if path.exists() else None
            m = r.pop("manifest")
            r["last"], r["result"] = m["steps"][-1], m["results"].get("constants")
            out[cname] = r
        print(json.dumps(out))
    ''', P21_CASES)
    # the real constants of usd12m and of this variant (bytes or absence) are as before
    assert {k: v for k, v in real_state().items() if "constants" in k} == {k: v for k, v in before.items()
                                                                           if "constants" in k}
    return r


def test_constants_step_writes_rounded_constants(constants_cases):
    """Revision section 7: the constants step runs the three jobs 36, rounds the row of c12_constants to two
    significant digits, writes constants.json and asks for its commit on its own."""
    r = constants_cases["ok"]
    assert r["results"] == ["ok"]
    assert r["calls"] == ["job 36 triples", "job 36 user_events", "job 36 constants"]
    assert not any(c["elsewhere"] for c in constants_cases.values())     # one path: ROOT / CONSTANTS_REL
    f = r["file"]
    assert list(f) == ["computed_at", "source", "window", "raw", "m_transfer_usd", "m_allowance_usd",
                       "cap_allowance_usd", "cap_user_usd", "b_transfer", "b_allowance", "unlimited_base_units",
                       "dust_token", "rule"]
    assert [f[k] for k in ("m_transfer_usd", "m_allowance_usd", "cap_allowance_usd", "cap_user_usd", "b_transfer",
                           "b_allowance", "unlimited_base_units", "dust_token")] == [
        170.0, 100.0, 19000.0, 2500.0, 0.00646242522745947, 0.010986122886681098, 1.15e+77, 1e-06]
    assert f["window"] == ["2025-04-01 00:00:00 UTC", "2026-03-31 23:59:59 UTC"]
    assert f["raw"] == ROW and all(isinstance(f["raw"][k], int) for k in ROW if isinstance(ROW[k], int))
    assert "sql/36_c12_constants.sql" in f["source"] and f["rule"].startswith("b = ln 3 / m")
    assert r["result"]["constants"] == {k: f[k] for k in ("m_transfer_usd", "m_allowance_usd", "cap_allowance_usd",
                                                          "cap_user_usd", "b_transfer", "b_allowance")}
    assert r["result"]["constants_sha256"] == r["file_sha256"] and r["result"]["path"] == CONSTANTS_REL
    assert r["last"]["step"] == "constants" and r["last"]["passed"] is True
    assert f"commit {CONSTANTS_REL}, {MANIFEST_REL} and {LEDGER_REL} on their own (precedent 77a1e49)" in r["stdout"]


@pytest.mark.parametrize("case, problem", [("m_transfer_none", "m_transfer = None"),
                                           ("m_transfer_zero", "m_transfer = 0"),
                                           ("m_transfer_nan", "m_transfer = nan"),
                                           ("m_transfer_negative", "m_transfer = -5"),
                                           ("u_user_0994", "U_user = 0.99 is below discovery.min_usd_account = 1.0")])
def test_constants_that_are_not_usable_are_not_written(constants_cases, case, problem):
    r = constants_cases[case]
    (res,) = r["results"]
    assert res.startswith("stopped: the constants are not usable (") and problem in res, res
    assert res.endswith("nothing was written") and r["file"] is None
    assert r["last"]["passed"] is False


def test_constants_step_stops_on_the_shape_of_c12_constants_and_runs_once(constants_cases):
    r = constants_cases["u_user_0996"]                   # 0.996 rounds to 1.0, the floor itself
    assert r["results"] == ["ok"] and r["file"]["cap_user_usd"] == 1.0
    r = constants_cases["two_rows"]
    assert r["results"] == ["stopped: c12_constants holds 2 rows, not one"] and r["file"] is None
    assert r["last"]["passed"] is False
    r = constants_cases["columns"]                      # the columns of sql/36_c12_constants.sql, in order
    assert r["results"][0].startswith("stopped: c12_constants has the columns") and r["file"] is None
    assert r["last"]["passed"] is False
    r = constants_cases["dry"]
    assert r["results"] == ["ok"] and r["calls"] == ["job 36 triples", "job 36 user_events", "job 36 constants"]
    assert r["file"] is None and r["manifest_changed"] is False
    for name in ("committed", "committed_dry"):          # computed once (revision section 7)
        r = constants_cases[name]
        (res,) = r["results"]
        assert res.startswith(f"refused: {CONSTANTS_REL} is committed (c0ffee"), name
        assert r["calls"] == [] and r["manifest_changed"] is False, name


P22_STATES = (None, "failed", "stale", "dirty", "written", "mixed", "alone", "no_ledger", "no_manifest", "committed")


def exactly(missing: tuple[str, ...], extra: tuple[str, ...]) -> str:
    """The problem of a commit of constants.json that does not hold exactly it, the run manifest and the ledger (D8):
    the files it lacks and the files it holds besides them, as git names them from the repository root."""
    names = lambda rels: sorted("experiments/" + r for r in rels)  # noqa: E731
    return (f"the commit c0ffee that holds {CONSTANTS_REL} must hold exactly it, {MANIFEST_REL} and {LEDGER_REL}: "
            f"missing {names(missing)}, extra {names(extra)}; commit the constants on their own with the run manifest "
            "and the ledger (precedent 77a1e49)")


P22_PROBLEMS = {None: f"{CONSTANTS_REL} is missing; run the 'constants' step first",
                "failed": "the last run of constants did not pass",
                "stale": f"{CONSTANTS_REL} is not the file the last run of constants wrote",
                "dirty": f"{CONSTANTS_REL} has local changes or is not committed",
                "written": f"{CONSTANTS_REL} has local changes or is not committed",
                "mixed": exactly((), ("scripts/graphs.py",)),
                "alone": exactly((MANIFEST_REL, LEDGER_REL), ()),
                "no_ledger": exactly((LEDGER_REL,), ()),
                "no_manifest": exactly((MANIFEST_REL,), ())}


@pytest.fixture(scope="module")
def committed_constants_cases(tmp_path_factory) -> dict:
    return run_gate_b(tmp_path_factory.mktemp("p22"), r'''
        out = {}
        order = list(d.GATE_B)
        for step in ("pairs", "rest", "checks", "download"):
            before = [[s, True] for s in order[1:order.index(step)]]
            for c in SPEC["cases"]:
                r = run_case(f"{step}-{c}", {"constants": c, "steps": before}, [step])
                r["last"] = r.pop("manifest")["steps"][-1]
                path = Path(SPEC["tmp"]) / f"{step}-{c}" / d.CONSTANTS_REL
                r["constants_sha256"] = sha(path) if path.exists() else None
                out[f"{step}|{c}"] = r
            r = run_case(f"{step}-dry", {"constants": None, "steps": before, "dry": True}, [step])
            r.pop("manifest")
            out[f"{step}|dry"] = r
        print(json.dumps(out))
    ''', list(P22_STATES))


@pytest.mark.parametrize("step", ["pairs", "rest", "checks", "download"])
def test_gate_b_steps_need_the_constants_committed_on_their_own(committed_constants_cases, step):
    """Revision sections 7 and 12: every gate B step after constants refuses unless constants.json is the file the
    last passing run of constants wrote, committed on its own in a commit that holds exactly it, the run manifest and
    the ledger (a commit with another file, or without the manifest or the ledger, is refused, D8); a dry run warns
    and takes the placeholder constants."""
    for state in P22_STATES:
        r = committed_constants_cases[f"{step}|{state}"]
        if state != "committed":
            (res,) = r["results"]
            assert res.startswith("refused: the constants must be committed on their own before this step: "), res
            assert P22_PROBLEMS[state] in res, (state, res)
            assert r["calls"] == [] and r["manifest_changed"] is False, state
            continue
        if step == "download":     # no job: past the refusals, the step asks for the rows of the tables to download
            assert r["results"][0].startswith("stopped: [") and "were not created" in r["results"][0]
        else:
            assert r["results"] == [f"reached {FIRST_JOB[step]}"]
        assert r["last"]["step"] == step and r["last"]["gate_b"]["constants"] == {
            "path": CONSTANTS_REL, "sha256": r["constants_sha256"], "commit": "c0ffee"}
        if step == "pairs":       # the pairs job takes the constants of the file, as repr of each float
            (job,) = r["jobs"]
            assert {k: job["params"][k] for k in ("b_transfer", "b_allowance", "cap_allowance")} == {
                "b_transfer": "0.00646242522745947", "b_allowance": "0.010986122886681098",
                "cap_allowance": "19000.0"}
    r = committed_constants_cases[f"{step}|dry"]
    assert "warning: the constants must be committed on their own before this step:" in r["stdout"]
    assert "(the dry run takes placeholder constants)" in r["stdout"]
    if step == "download":
        assert r["results"] == ["ok"] and r["calls"] == []
    else:
        assert r["results"] == [f"reached {FIRST_JOB[step]}"] and r["manifest_changed"] is False
        if step == "pairs":
            assert r["jobs"][0]["params"]["b_transfer"] == "0.01"


# --------------------------------------------------------------------------- the projection and the cap


def projection_tables(n: int = 12 * 10**8) -> dict:
    """The gate A tables of the projection test with c12_events_cc at n rows, 90 per cent of them priced."""
    return gate_a_tables(n, 109 * n + 8 * (9 * n // 10))


def test_projection_refuses_a_gate_b_step_above_the_cap(tmp_path):
    """Revision sections 12 and 13: a gate B step refuses when the campaign and the projection of the gate B jobs from
    it on would pass the cap of the overlay; no decision passes it, and a projection that cannot be made refuses too."""
    tables = projection_tables()
    base = {"projection": "real", "tables": tables, "layers": LAYERS, "self_pairs": SELF_PAIRS}
    cases = {"over": {**base, "campaign": CAP_USD - 1.0, "author": "go on"},
             "under": {**base, "campaign": 0.0},
             "missing": {**base, "tables": {k: v for k, v in tables.items() if k != "c12_events_cc"}}}
    r = run_gate_b(tmp_path, r'''
        out = {}
        for cname, case in SPEC["cases"].items():
            r = run_case(cname, case, ["constants"])
            r["last"] = r.pop("manifest")["steps"][-1]
            out[cname] = r
        print(json.dumps(out))
    ''', cases)
    (res,) = r["over"]["results"]
    assert res.startswith("refused: the gate B jobs from constants on are projected at up to USD"), res
    assert "no decision passes it" in res and f"it passes the cap of USD {CAP_USD:.2f}" in res
    assert float(re.search(r"projected at up to USD ([0-9.]+)", res).group(1)) > 1.0   # so not a matter of the cap
    assert r["over"]["calls"] == [] and r["over"]["manifest_changed"] is False
    assert r["under"]["results"] == ["reached triples"]
    projection = r["under"]["last"]["gate_b"]["projection"]
    assert projection["usd"] > 1.0 and projection["campaign_usd"] == 0.0 and set(projection["jobs"]) == JOB_KEYS_B
    (res,) = r["missing"]["results"]
    assert res.startswith("refused: no projection of the gate B jobs from constants on:"), res
    assert r["missing"]["manifest_changed"] is False


# --------------------------------------------------------------------------- the rest and checks steps


def test_rest_step_checks_the_t1_rows_against_the_pilot(tmp_path):
    r = run_gate_b(tmp_path, r'''
        base = {t: 1000 for t in d.REST_TABLES}
        base.update({"c12_x_allow_pairs_t1": 5010, "c12_x_allow_pairs_unc_t1": 9012, "c12_x_transfer_pairs_t1": 20030,
                     "c12_cohort_tobs": 6000, "c12_proxies_tobs": 6000, "u12_cohort_tobs": 6483, "u12_cohort_t1": 6343,
                     "u12_labels_w0": 7962, "u12_labels_w1": 7995, "c12_members": 28783, "c12_x_members": 28783,
                     "c12_nodes": 120000, "c12_x_nodes": 120000, "c12_label_parts_w0": 7962,
                     "c12_label_parts_w1": 7995, "c12_x_label_split_w0": 7962, "c12_x_label_split_w1": 7995,
                     "c12_inflow_untyped_tobs": 1, "c12_inflow_untyped_t1": 1})
        out = {}
        for cname, change in SPEC["cases"].items():
            case = {"constants": "committed", "steps": [["pairs", True]], "stop_at_job": False,
                    "sizes": {**base, **change}}
            r = run_case(cname, case, ["rest"])
            m = r.pop("manifest")
            r["last"], r["result"] = m["steps"][-1], m["results"].get("rest")
            out[cname] = r
        print(json.dumps(out))
    ''', {"equal": {}, "transfer_off": {"c12_x_transfer_pairs_t1": 20029}, "inflow_zero": {"c12_inflow_untyped_t1": 0}})
    c = r["equal"]
    assert c["results"] == ["ok"]
    assert c["calls"] == ["job 38 cohorts", "job 38 proxies", "job 39 labels_w0", "job 39 labels_w1",
                          "job 40 node_ids", "job 41 importance"]
    ident = c["result"]["identities"]
    assert all(v["expected"] == v["actual"] for v in ident.values()) and c["last"]["passed"] is True
    # the layers and self-pairs of the structure step: 5,000 + 10, 9,000 + 12, 20,000 + 30
    assert {k: ident[k]["expected"] for k in ("c12_x_allow_pairs_t1", "c12_x_allow_pairs_unc_t1",
                                              "c12_x_transfer_pairs_t1", "c12_members")} == {
        "c12_x_allow_pairs_t1": 5010, "c12_x_allow_pairs_unc_t1": 9012, "c12_x_transfer_pairs_t1": 20030,
        "c12_members": 28783}
    (res,) = r["transfer_off"]["results"]
    assert res.startswith("stopped: ['c12_x_transfer_pairs_t1'] do not have their expected rows"), res
    assert "the t1 rows must be the structure pilot's pairs" in res and r["transfer_off"]["last"]["passed"] is False
    (res,) = r["inflow_zero"]["results"]
    assert res.startswith("stopped: ['c12_inflow_untyped_t1'] do not have their expected rows"), res
    assert r["inflow_zero"]["last"]["passed"] is False


def sql42_names() -> list[str]:
    text = re.sub(r"--[^\n]*", "", (EXPERIMENTS / "sql" / "42_c12_checks.sql").read_text(encoding="utf-8"))
    return re.findall(r"'(\w+)' AS check_name", text) + re.findall(r"UNION ALL\s+SELECT '(\w+)'", text)


def test_checks_step_requires_every_invariant_of_sql42(tmp_path):
    names = sql42_names()
    assert len(names) == 64 and len(set(names)) == 64
    rows = [{"check_name": n, "violations": 0} for n in names]
    cases = {"all_zero": rows,
             "one_violation": [{**x, "violations": 1} if x["check_name"] == "struct_transfer_t1" else x
                               for x in rows],
             "missing": [x for x in rows if x["check_name"] != "labels_recount_w1"],
             "extra": [*rows, {"check_name": "not_a_check", "violations": 0}],
             "null": [{**x, "violations": None} if x["check_name"] == "dust_rule" else x for x in rows]}
    r = run_gate_b(tmp_path, r'''
        out = {"expected": list(d.EXPECTED_CHECKS)}
        for cname, rows in SPEC["cases"].items():
            case = {"constants": "committed", "steps": [["pairs", True], ["rest", True]], "stop_at_job": False,
                    "rows": {"c12_checks": rows}}
            r = run_case(cname, case, ["checks"])
            m = r.pop("manifest")
            r["last"], r["result"] = m["steps"][-1], m["results"].get("checks")
            out[cname] = r
        print(json.dumps(out))
    ''', cases)
    assert r["expected"] == names
    c = r["all_zero"]
    assert c["results"] == ["ok"] and c["calls"] == ["job 42 checks"]
    assert c["result"] == {"checks": {n: 0 for n in names}, "names_missing_or_unknown": []}
    assert c["last"]["passed"] is True
    expected = {"one_violation": "stopped: an invariant of sql/42 does not hold: {'struct_transfer_t1': 1}",
                "missing": "stopped: an invariant of sql/42 does not hold: {}; names missing or unknown: "
                           "['labels_recount_w1']",
                "extra": "stopped: an invariant of sql/42 does not hold: {}; names missing or unknown: ['not_a_check']",
                "null": "stopped: an invariant of sql/42 does not hold: {'dust_rule': None}"}
    for name, text in expected.items():
        assert r[name]["results"] == [text], name
        assert r[name]["last"]["passed"] is False, name


# --------------------------------------------------------------------------- the download step


P26_BODY = r'''
sys.path.insert(0, str(EXP / "tests"))
import c12_world as cw
from collections import Counter

NAMES = {"cohort_tobs": "matched_cohort", "cohort_t1": "cohort_t1", "spenders_w0": "spenders_w0",
         "spenders_w1": "spenders_w1"}
worlds = {}


def graph_sizes(nodes, allow, transfer):
    full, _ = rd.full_graph(nodes, allow, transfer)
    s = crawl.bow_tie(full.n, full.union_src, full.union_dst).sizes()
    return {k: int(s[k]) for k in ("U", "E_U", "WCC", "E_WCC")}


def drop_one_transfer_pair(world, pilot):
    """Leave out of the source one t1 transfer pair between two contracts of the pilot's universe that no capped
    allowance pair joins, so that E_U of the downloaded t1 graph is the pilot's minus one."""
    nodes, allow, tr = (world.frames[s] for s in ("nodes", "allow_pairs_t1", "transfer_pairs_t1"))
    full, ids = rd.full_graph(nodes, allow, tr)
    bt = crawl.bow_tie(full.n, full.union_src, full.union_dst)
    in_u, pos = bt.scc | bt.out, {int(i): k for k, i in enumerate(ids)}
    capped = set(zip(allow["src"].tolist(), allow["dst"].tolist()))
    for k, (s, t) in enumerate(zip(tr["src"].tolist(), tr["dst"].tolist())):
        if s == t or (s, t) in capped or not (in_u[pos[s]] and in_u[pos[t]]):
            continue
        keep = tr.drop(index=tr.index[k]).reset_index(drop=True)
        after = graph_sizes(nodes, allow, keep)
        if after["U"] == pilot["sizes"]["U"] and after["E_U"] == pilot["sizes"]["E_U"] - 1:
            cw.write_stem(world, "transfer_pairs_t1", keep)
            return {"pair": [int(s), int(t)], "sizes": after}
    raise AssertionError("no transfer pair of the universe without a capped allowance pair")


def world_for(kind):
    if kind not in worlds:
        src = Path(SPEC["tmp"]) / f"src-{kind}" / "experiments"
        world = cw.contract_world(src, change=kind if kind in cw.CHANGES else None)
        pilot = cw.pilot_from_world(world, cfg)                # the pilot of the world's full t1 tables
        dropped = drop_one_transfer_pair(world, pilot) if kind == "t1_off" else None
        if kind == "schema":                                   # importance_t1.n_t written as float64
            import pyarrow as pa, pyarrow.parquet as pq
            stem = world.graph / "importance_t1"
            for p in cw.part_paths(stem):
                t = pq.read_table(p)
                i = t.schema.get_field_index("n_t")
                pq.write_table(t.set_column(i, "n_t", t.column("n_t").cast(pa.float64())), p, compression="zstd")
        worlds[kind] = (world, pilot, dropped)
    return worlds[kind]


out = {"downloads": [list(x) for x in d.DOWNLOADS], "world_downloads": [list(x) for x in cw.DOWNLOADS.items()],
       "interface": sorted(cw.INTERFACE), "interface_types": hasattr(d, "INTERFACE_TYPES")}
for cname, opt in SPEC["cases"].items():
    world, pilot, dropped = world_for(opt["world"])
    rows = dict(world.table_rows)
    sidecar = {"c12_x_nodes": rows["c12_x_nodes"] - 1} if opt.get("sidecar") else {}
    case = {"pilot": pilot, "constants": "committed",
            "layers": {k: int(v["edges"]) for k, v in pilot["layers"].items()},
            "self_pairs": {k: int(v["self_loops"]) for k, v in pilot["layers"].items()},
            "steps": [["pairs", True], ["rest", True], ["checks", opt.get("checks", True)]], "sizes": rows}
    cmds = []

    def setup(root, world=world, cmds=cmds, sidecar=sidecar):
        def sh(cmd):
            cmds.append([str(c) for c in cmd[1:]])
            cw.download_copy(world, cmd[2], Path(cmd[3]), rows=sidecar.get(cmd[2].split(".")[-1]))
        d.sh = sh
    r = run_case(cname, case, ["download"], setup=setup)
    m = r.pop("manifest")
    r["last"], r["download"] = m["steps"][-1], m["results"].get("download")
    r["cmds"] = cmds
    r["expected_cmds"] = [["scripts/download_table.py", f"contract_rep.{t}", str(d.GRAPH / s)] for t, s in d.DOWNLOADS]
    r["parts"] = {s: cw.part_sha256(d.GRAPH / s) for _, s in d.DOWNLOADS}
    r["source_parts"] = {s: cw.part_sha256(world.graph / s) for _, s in d.DOWNLOADS}
    r["rows"] = world.rows
    folder = d.PROC / "cohort"
    r["cohort_files"] = {n: json.loads((folder / f"{n}.json").read_text(encoding="utf-8"))
                         for n in NAMES.values() if (folder / f"{n}.json").exists()}
    nodes = set(world.frames["nodes"]["address"])
    expect = {}
    for lst, name in NAMES.items():
        members = world.lists[lst]
        keep = [a for a, c, _ in members if (c != "user_account" if lst.startswith("cohort") else c == "contract")]
        expect[name] = {"listed": len(members), "by_class": dict(sorted(Counter(c for _, c, _ in members).items())),
                        "cohort": len(keep),
                        "contracts_in_nodes": int(sum(c == "contract" and a in nodes for a, c, _ in members))}
    r["expect_cohorts"], r["dropped"], r["pilot_sizes"], r["target"] = expect, dropped, pilot["sizes"], world.target
    out[cname] = r
print(json.dumps(out, default=str))
'''
P26_CASES = {"clean": {"world": "clean"}, "sidecar": {"world": "clean", "sidecar": True},
             "checks_failed": {"world": "clean", "checks": False}, "t1_off": {"world": "t1_off"},
             "member_without_node": {"world": "member_without_node"}}


@pytest.fixture(scope="module")
def download_cases(tmp_path_factory) -> dict:
    return run_gate_b(tmp_path_factory.mktemp("p26"), P26_BODY, P26_CASES)


def test_download_step_writes_and_verifies_the_contract_graph_tables(download_cases):
    """Protocol section 8, revision section 8: the download step writes the 16 gate B stems into
    graph-tables-contract-12m, records the SHA-256 of every part, reads them back as the discovery runner does (the
    t1 graph of the pinned pilot, its union and bow-tie, the t1 rows, importance, the untyped inflow, members against
    nodes) and writes the
    cohort summaries; nothing reaches the real folders of the variant (run_gate_b)."""
    r = download_cases
    assert r["downloads"] == r["world_downloads"] == [list(x) for x in w.DOWNLOADS.items()]
    stems = [s for _, s in r["downloads"]]
    assert len(stems) == 16 and set(stems) == set(w.INTERFACE) == set(r["interface"])
    assert not {"labels_w0", "labels_w1", "cohort"} & set(stems)     # the labels stay in graph-tables-usd-12m
    c = r["clean"]
    assert c["results"] == ["ok"] and c["last"]["passed"] is True
    assert c["cmds"] == c["expected_cmds"] and len(c["cmds"]) == 16
    assert [line[2:] for line in c["stdout"].splitlines() if line.startswith("$ ")] == [" ".join(x) for x in
                                                                                       c["expected_cmds"]]
    files = c["download"]["files"]
    assert list(files) == stems
    for table, stem in r["downloads"]:
        assert files[stem] == {"table": table, "rows": c["rows"][stem], "sha256": c["parts"][stem]}, stem
        assert c["parts"][stem] == c["source_parts"][stem] and c["parts"][stem], stem
    v = c["download"]["verify"]
    assert v["passed"] is True
    assert v["pilot_match"] and all(v["pilot_match"].values()) and set(v["pilot_match"]) == {"U", "E_U", "WCC",
                                                                                            "E_WCC"}
    assert v["union_match"] and all(v["union_match"].values())
    assert {k: x["expected"] for k, x in v["t1_rows"].items()} == {k: x["actual"] for k, x in v["t1_rows"].items()}
    assert set(v["t1_rows"]) == {"allow_pairs_t1", "allow_pairs_uncapped_t1", "transfer_pairs_t1"}
    assert v["importance_tobs"]["outside_g"] == w.IMPORTANCE_OUTSIDE == 5 and v["importance_t1"]["outside_g"] == 5
    assert v["inflow_untyped_t1"] == 987.25 and v["inflow_untyped_tobs"] == 1234.5
    assert v["members"]["n_without_node"] == 0 and not any(v["members"]["flags_off"].values())
    assert set(v["members"]["flags_off"]) == set(w.NODE_FLAGS)
    cohorts = c["cohort_files"]
    assert set(cohorts) == {"matched_cohort", "cohort_t1", "spenders_w0", "spenders_w1"}
    for name, want in c["expect_cohorts"].items():
        assert {k: cohorts[name][k] for k in want} == want, name
    assert cohorts["matched_cohort"]["user_accounts_by_source"] == {"rpc_eoa": 1, "rpc_eoa_7702": 1,
                                                                    "rpc_smart_account": 2, "tx_sender": 1}
    assert cohorts["cohort_t1"]["in_tobs_cohort"] == 30
    assert c["download"]["cohorts"]["cohort_t1"]["in_tobs_cohort"] == 30


def test_download_step_stops_on_tables_that_are_not_the_pilots(download_cases):
    r = download_cases
    n = r["clean"]["rows"]["nodes"]
    c = r["sidecar"]                     # a download that lost a row of nodes
    assert c["results"] == [f"stopped: nodes: {n - 1} rows downloaded, c12_x_nodes has {n}"]
    assert c["last"]["passed"] is False and len(c["cmds"]) == 1
    c = r["t1_off"]                      # a t1 transfer pair of the pilot's universe left out: E_U drops by one
    assert c["dropped"]["sizes"]["E_U"] == c["pilot_sizes"]["E_U"] - 1
    (res,) = c["results"]
    assert res.startswith("stopped: the downloaded tables fail the reader's checks: refused: the t1 graph differs "
                          "from the structure pilot"), res
    assert c["last"]["passed"] is False
    c = r["member_without_node"]         # a contract member of a list without its node
    (res,) = c["results"]
    assert res.startswith("stopped: the downloaded tables differ from the pinned pilot or from each other"), res
    assert c["download"]["verify"]["members"]["n_without_node"] == 1
    assert c["download"]["verify"]["members"]["contracts_without_node"] == [c["target"]["address"]]
    assert c["last"]["passed"] is False
    c = r["checks_failed"]               # the step waits for a run of checks that passes
    (res,) = c["results"]
    assert res.startswith("refused: download waits for a run of checks that passes (the last one did not)"), res
    assert c["cmds"] == [] and c["manifest_changed"] is False


def test_download_step_refuses_a_stem_off_the_interface_types(tmp_path):
    """Optional: verify_downloads compares the arrow schema of every stem with INTERFACE_TYPES."""
    if not run_json("import json, run_contract12m_pipeline as d; print(json.dumps(hasattr(d, 'INTERFACE_TYPES')))"):
        pytest.skip("the driver defines no INTERFACE_TYPES (an optional schema check of the downloads)")
    r = run_gate_b(tmp_path, P26_BODY, {"schema": {"world": "schema"}})
    (res,) = r["schema"]["results"]
    assert res.startswith("stopped:") and "importance_t1" in res, res


# --------------------------------------------------------------------------- decisions, changed sources, bills


AUTHOR = "the pairs job was run by hand"


def test_author_decision_after_gate_b_is_recorded(tmp_path):
    """Revision section 13: after gate B --author-decision passes only the order of the steps; the run manifest marks
    the decision, and it passes none of the gate B refusals."""
    cases = {"decided": {"author": AUTHOR}, "no_author": {}, "no_block": {"author": AUTHOR, "block": "none"},
             "over_cap": {"author": AUTHOR, "projection": "real", "tables": projection_tables(), "layers": LAYERS,
                          "self_pairs": SELF_PAIRS, "campaign": CAP_USD + 0.5}}
    r = run_gate_b(tmp_path, r'''
        out = {}
        for cname, case in SPEC["cases"].items():
            r = run_case(cname, {**case, "constants": "committed"}, ["rest"])
            r["last"] = r.pop("manifest")["steps"][-1]
            out[cname] = r
        print(json.dumps(out))
    ''', cases)
    c = r["decided"]
    assert c["results"] == ["reached cohorts"]
    last = c["last"]
    assert last["step"] == "rest" and last["waited_for"] == ["a run of pairs"]
    assert last["author_decision"] == AUTHOR and last["after_gate_b"] is True
    assert "gate_a_decision" not in last          # the structure run took no decision, so none covers the wait
    assert "going on by the author's decision" in c["stdout"] and "_change-record-contract-graph.md" in c["stdout"]
    assert r["no_author"]["results"][0].startswith("refused: rest waits for a run of pairs")
    assert r["no_block"]["results"][0].startswith(
        "refused: docs/discovery_protocol.md has no filled section 'Protocol fixed'")
    (res,) = r["over_cap"]["results"]
    assert res.startswith("refused: the gate B jobs from rest on are projected at up to USD") and \
        "no decision passes it" in res, res
    for name in ("no_author", "no_block", "over_cap"):
        assert r[name]["calls"] == [] and r[name]["manifest_changed"] is False, name


# The runs of gate A as the amendment of 9 November 2026 (revision section 13) left them: the runs of 8 November 2026
# up to audit and the first structure run, whose pilot stopped; job 31 again with the smart-account lists; and
# structure again by the author's decision that the runs of jobs 32 to 34 and 43 stand. The new pilot set only
# few_capped_allowance_in_edges, and 'Protocol fixed' pins it with the decision to go on after that stop.
ORDER_WAITS = [f"a run of {s} after the last run of contracts" for s in ("balances", "anchors", "audit")]
STRUCTURE_WAIT = "a run of structure that passes (the last one did not)"
CHECK_WAIT = "a check without problems (the last one found some)"
STRUCTURE_AT = "2026-11-08T17:16:55+00:00"
STAND = "jobs 32 to 34 and 43 read no table that job 31 writes, so their runs of 8 November 2026 stand"
GO_ON = "the new pilot set only few_capped_allowance_in_edges, so the discovery-order test goes on"
STOPPED_PILOT = {"pilot_inputs": {"allow_in_share": 0.0043},
                 "block": {"author_decision": GO_ON, "decision_covers": ["few_capped_allowance_in_edges"]}}
ORDER_REFUSAL = "(the steps run in the order of STEPS; --author-decision TEXT goes on all the same and is recorded)"
DECIDED_BODY = r'''
    def planned(case):          # the case's runs of gate A (and checks) in place of the tree's; what follows is kept
        def setup(root):
            path = root / d.MANIFEST_REL
            m = json.loads(path.read_text(encoding="utf-8"))
            m["steps"] = case["gate_a"] + m["steps"][len(d.CHAIN_A):]
            m["checks_run"] = case.get("checks_run", m["checks_run"])
            common.save_json(m, path)
        return setup

    out = {}
    for cname, case in SPEC["cases"].items():
        r = run_case(cname, case, [case["step"]], setup=planned(case))
        r["last"] = r.pop("manifest")["steps"][-1]
        out[cname] = r
    print(json.dumps(out))
'''


def planned_gate_a(passed: bool | None = False, waited_for=tuple(ORDER_WAITS)) -> list[dict]:
    """The step entries of gate A in that state; the last structure entry with ``passed`` (None: it stopped before it
    recorded its result), ``waited_for`` and the author's decision."""
    last = {"step": "structure", "started_at": STRUCTURE_AT, "waited_for": list(waited_for), "author_decision": STAND}
    if passed is not None:
        last["passed"] = passed
    return [*({"step": s, "passed": True} for s in STEPS_IN_CHAIN[:-1]), {"step": "structure", "passed": False},
            {"step": "contracts", "passed": True}, last]


def decided_case(step: str, **case) -> dict:
    """A run of ``step`` in that state, after the gate B steps before it passed (constants committed from pairs on)."""
    return {**STOPPED_PILOT, "gate_a": planned_gate_a(), "step": step,
            "constants": None if step == "constants" else "committed",
            "steps": [[s, True] for s in GATE_B_STEPS[1:GATE_B_STEPS.index(step)]], **case}


def test_gate_b_steps_go_on_by_the_decisions_taken_before_gate_b(tmp_path):
    """Revision section 13, amendment of 9 November 2026: a gate B step needs no new decision for exactly the waits
    that the decisions taken before gate B cover, those that the last structure run recorded under its author's
    decision and, when 'Protocol fixed' on its pilot carries an author_decision, the wait for a structure run that
    passes. Its run records them as a gate A decision that points to that structure entry, not as after_gate_b. Any
    other wait still needs --author-decision, and the run marks it after_gate_b."""
    pairs_failed = [["pairs", False]]
    cases = {**{f"planned-{s}": decided_case(s) for s in GATE_B_STEPS},     # the case names are folder names
             "planned_dry": decided_case("constants", dry=True),
             "further": decided_case("rest", steps=pairs_failed),
             "further_decided": decided_case("rest", steps=pairs_failed, author=AUTHOR),
             # a pilot without a stop, pinned without a decision: the order waits alone
             "pilot_passed": decided_case("constants", pilot_inputs={}, block="valid", gate_a=planned_gate_a(True)),
             "no_fixed_decision": decided_case("constants", pilot_inputs={}, block="valid", author=AUTHOR)}
    r = run_gate_b(tmp_path, DECIDED_BODY, cases)
    j = len(planned_gate_a()) - 1                       # the index of the last structure entry
    covered = {"structure_index": j, "structure_started_at": STRUCTURE_AT, "waited_for": [*ORDER_WAITS, STRUCTURE_WAIT]}
    by_run = (f"the author's decision of the last structure run (steps[{j}] of the run manifest, started at "
              f"{STRUCTURE_AT})")

    def note(step: str, waits: list[str], by: str = by_run + " and the author_decision of 'Protocol fixed' on its "
             "pilot") -> str:
        return (f"note: {step} waits for {'; '.join(waits)}, which decisions taken before gate B cover ({by}); the run "
                "manifest records them as a gate A decision (gate_a_decision), not as taken after gate B")

    for step in GATE_B_STEPS:
        c = r[f"planned-{step}"]
        if step == "download":   # no job: past the refusals, the step asks for the rows of the tables to download
            assert c["results"][0].startswith("stopped: [") and "were not created" in c["results"][0], c["results"]
        else:
            assert c["results"] == [f"reached {FIRST_JOB[step]}"], (step, c["results"])
        last = c["last"]
        assert last["step"] == step and last["gate_a_decision"] == covered, (step, last)
        assert not {"after_gate_b", "waited_for", "author_decision"} & set(last), (step, last)
        assert last["gate_b"]["protocol_fixed"]["author_decision"] == GO_ON, step
        assert last["gate_b"]["protocol_fixed"]["decision_covers"] == ["few_capped_allowance_in_edges"], step
        assert note(step, covered["waited_for"]) in c["stdout"].splitlines(), (step, c["stdout"])
        assert "going on by the author's decision" not in c["stdout"] and "after_gate_b" not in c["stdout"], step
    c = r["planned_dry"]                                # the dry run says the same and records nothing
    assert c["results"] == ["reached triples"] and c["manifest_changed"] is False
    assert note("constants", covered["waited_for"]) in c["stdout"].splitlines() and "warning:" not in c["stdout"]
    # a wait that no decision before gate B covers: refused, or recorded as taken after gate B
    pairs_wait = "a run of pairs that passes (the last one did not)"
    c = r["further"]
    assert c["results"] == [f"refused: rest waits for {pairs_wait} {ORDER_REFUSAL}"], c["results"]
    assert c["calls"] == [] and c["manifest_changed"] is False
    assert note("rest", covered["waited_for"]) in c["stdout"].splitlines()
    c = r["further_decided"]
    assert c["results"] == ["reached cohorts"]
    last = c["last"]
    assert last["gate_a_decision"] == covered and last["waited_for"] == [pairs_wait]
    assert last["author_decision"] == AUTHOR and last["after_gate_b"] is True
    assert "going on by the author's decision" in c["stdout"] and "_change-record-contract-graph.md" in c["stdout"]
    # without a stop, the structure run's decision covers the order waits alone
    c = r["pilot_passed"]
    assert c["results"] == ["reached triples"]
    assert c["last"]["gate_a_decision"] == {**covered, "waited_for": ORDER_WAITS}
    assert not {"after_gate_b", "waited_for", "author_decision"} & set(c["last"])
    assert note("constants", ORDER_WAITS, by_run) in c["stdout"].splitlines()
    # a structure run that did not pass, with no author_decision in 'Protocol fixed': its wait needs a new decision
    c = r["no_fixed_decision"]
    assert c["results"] == ["reached triples"]
    last = c["last"]
    assert last["gate_a_decision"] == {**covered, "waited_for": ORDER_WAITS}
    assert last["waited_for"] == [STRUCTURE_WAIT] and last["author_decision"] == AUTHOR and last["after_gate_b"] is True


def test_decisions_taken_before_gate_b_cover_only_the_state_they_were_taken_on(tmp_path):
    """The decisions of the last structure run and of 'Protocol fixed' cover the waits of a gate B step only while that
    run is the last of gate A: once a step of gate A ran after it, or when it stopped before it recorded its result,
    they cover none; and a wait for a check that it recorded is covered only while no check ran after it started (a
    check without a time counts as later)."""
    with_check = planned_gate_a(waited_for=[CHECK_WAIT, *ORDER_WAITS])
    earlier = {"at": "2026-11-08T09:00:00+00:00", "problems": ["logs_obs was modified on 2026-11-08"]}
    later = {"at": "2026-11-09T09:00:00+00:00", "problems": ["u_prices was modified on 2026-11-09"]}
    cases = {"gate_a_after": decided_case("constants", gate_a=[*planned_gate_a(), {"step": "audit", "passed": True}]),
             "unfinished": decided_case("constants", gate_a=planned_gate_a(None)),
             "check_same": decided_case("constants", gate_a=with_check, checks_run=[earlier]),
             "check_since": decided_case("constants", gate_a=with_check, checks_run=[earlier, later], author=AUTHOR),
             "check_no_time": decided_case("constants", gate_a=with_check, checks_run=[{"problems": ["p"]}])}
    r = run_gate_b(tmp_path, DECIDED_BODY, cases)
    refused = {"gate_a_after": [*ORDER_WAITS[:2], STRUCTURE_WAIT],   # audit ran again: the order of balances, anchors
               "unfinished": [*ORDER_WAITS, STRUCTURE_WAIT], "check_no_time": [CHECK_WAIT]}
    for name, waits in refused.items():
        c = r[name]
        want = f"refused: constants waits for {'; '.join(waits)} {ORDER_REFUSAL}"
        assert c["results"] == [want], (name, c["results"])
        assert c["calls"] == [] and c["manifest_changed"] is False, name
    for name in ("gate_a_after", "unfinished"):
        assert "gate_a_decision" not in r[name]["stdout"], name
    covered = {"structure_index": len(with_check) - 1, "structure_started_at": STRUCTURE_AT}
    c = r["check_same"]                                 # the check that the structure run went on after
    assert c["results"] == ["reached triples"]
    assert c["last"]["gate_a_decision"] == {**covered, "waited_for": [CHECK_WAIT, *ORDER_WAITS, STRUCTURE_WAIT]}
    assert not {"after_gate_b", "waited_for", "author_decision"} & set(c["last"])
    c = r["check_since"]                                # a later check found problems: they need a new decision
    assert c["results"] == ["reached triples"]
    assert c["last"]["gate_a_decision"] == {**covered, "waited_for": [*ORDER_WAITS, STRUCTURE_WAIT]}
    assert c["last"]["waited_for"] == [CHECK_WAIT] and c["last"]["after_gate_b"] is True


CALIBRATED_AT = "2026-10-28T09:09:32+00:00"     # the ledger's time of 92c0b37c-..., the W0 label job's bill
# (table, modified, refused) of sources modified before 7 November: an input of job 39's measured terms (a
# twelve-month view or base table, logs_obs, logs_w1, u_tokens) modified after that bill is refused by rest and
# checks, at or just before it passes; any other source passes as at gate A.
CALIBRATION_CASES = {
    "view_after": ("u12_approvals_t1", "2026-11-03T12:00:00+00:00", True),
    "base_after": ("u_transfers_w1", "2026-11-06T23:59:59+00:00", True),
    "logs_obs_after": ("logs_obs", "2026-10-30T00:00:00+00:00", True),
    "logs_w1_second_after": ("logs_w1", "2026-10-28T09:09:33+00:00", True),
    "u_tokens_after": ("u_tokens", "2026-11-01T08:00:00+00:00", True),
    "at_the_bill": ("u12_transfers_t1", CALIBRATED_AT, False),
    "second_before": ("u12_allow_triples_tobs", "2026-10-28T09:09:31+00:00", False),
    "u_prices_after": ("u_prices", "2026-11-03T12:00:00+00:00", False),
    "labels_after": ("u12_labels_w0", "2026-11-05T00:00:00+00:00", False),
}


def test_rest_and_checks_refuse_changed_sources(tmp_path):
    """Revision section 8 and the gate B amendment of section 13: job 39 is estimated from the bills of the
    twelve-month label jobs, which hold only while the tables they read are as they were: rest and checks refuse a
    changed or missing source table, and an input of the bills (CALIBRATED) modified after the first of them,
    2026-10-28T09:09:32Z, though before 7 November (D6, I4); a source that job 39 does not read passes as at gate A,
    and pairs reads none of them."""
    cases = {"modified": {"tables": {"u12_transfers_w1": {"rows": 0, "modified": "2026-11-08T00:00:00+00:00"}}},
             "absent": {"drop": ["u12_allow_triples_t1"]},
             **{k: {"tables": {t: {"rows": 5 if t == "u_tokens" else 1000, "modified": at,
                                   "partitioned": t in ("logs_obs", "logs_w1", "u_transfers_w1")}}}
                for k, (t, at, _) in CALIBRATION_CASES.items()},
             "two": {"tables": {t: {"rows": 1000, "modified": "2026-11-02T00:00:00+00:00"}
                                for t in ("u12_transfers_tobs", "u_approvals")}}}
    r = run_gate_b(tmp_path, r'''
        out = {}
        for cname, case in SPEC["cases"].items():
            for step, before in (("pairs", []), ("rest", [["pairs", True]]),
                                 ("checks", [["pairs", True], ["rest", True]])):
                r = run_case(f"{cname}-{step}", {**case, "constants": "committed", "steps": before}, [step])
                r.pop("manifest")
                out[f"{cname}|{step}"] = r
        out["calibrated"] = [list(d.CALIBRATED), d.CALIBRATED_AT]
        print(json.dumps(out))
    ''', cases)
    assert r["calibrated"][1] == CALIBRATED_AT
    reason = (" (the gate B jobs read these tables as they were; job 39 is estimated from the bills of the "
              "twelve-month label jobs on them)")
    after = "{} was modified at {}, after the first bill that calibrates job 39, at " + CALIBRATED_AT
    refused = {"modified": "u12_transfers_w1 was modified on 2026-11-08 or expires",
               "absent": "the source table u12_allow_triples_t1 does not exist",
               "two": "; ".join(after.format(t, "2026-11-02T00:00:00+00:00") for t in ("u12_transfers_tobs",
                                                                                         "u_approvals"))}
    refused.update({k: after.format(t, at) for k, (t, at, bad) in CALIBRATION_CASES.items() if bad})
    for name in cases:
        for step in ("rest", "checks"):
            c = r[f"{name}|{step}"]
            if name in refused:
                assert c["results"] == [f"refused: {refused[name]}{reason}"], (name, step, c["results"])
                assert c["calls"] == [] and c["manifest_changed"] is False, (name, step)
            else:
                assert c["results"] == [f"reached {FIRST_JOB[step]}"], (name, step, c["results"])
        assert r[f"{name}|pairs"]["results"] == ["reached pairs"], name
    assert {t for t, _, bad in CALIBRATION_CASES.values() if bad} <= set(r["calibrated"][0])
    assert not {"u_prices", "u12_labels_w0"} & set(r["calibrated"][0])        # sources that job 39 does not read


SOURCE_TIMES = ("2026-10-27T23:59:59+00:00", CALIBRATED_AT, "2026-10-28T09:09:33+00:00", "2026-11-06T23:59:59+00:00",
                "2026-11-07T00:00:00+00:00", "2026-11-08T12:00:00+00:00")


def test_the_source_check_of_gate_a_is_unchanged():
    """D6, I4: the calibrated inputs of job 39 are a second test of source_problems, on the tables passed to it as
    calibrated (CALIBRATED: SOURCES_B and the logs_obs, logs_w1 and u_tokens that the twelve-month label jobs read,
    against the ledger's time of the first calibrating bill); without it the function gives what the source check of
    the check step of d39775c gives on every table, and with it a table outside CALIBRATED, or one that the rule of
    gate A already names, gets the same text."""
    old = w.git_blob(w.GATE_A, "scripts/run_contract12m_pipeline.py")
    if old is None:
        pytest.skip(f"commit {w.GATE_A} is not available")
    # the loop over the source tables' metadata in step_check of d39775c, as a function of that metadata
    tree = ast.parse(old.decode("utf-8"))
    ns: dict = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "SOURCES_BEFORE"
                                                for t in node.targets):
            ns["SOURCES_BEFORE"] = ast.literal_eval(node.value)
    (step,) = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "step_check"]
    (loop,) = [n for n in ast.walk(step) if isinstance(n, ast.For) and ast.unparse(n.iter) == "meta.items()"]
    fn = ast.parse("def gate_a(meta):\n    problems = []\n    return problems").body[0]
    fn.body.insert(1, loop)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), "d39775c:step_check", "exec"), ns)
    gate_a = ns["gate_a"]
    r = run_json(f"""
        import json
        import run_contract12m_pipeline as d
        times = {json.dumps(list(SOURCE_TIMES))}
        cases = [[name, None] for name in (*d.SOURCES, *d.SOURCES_B)]
        cases += [[name, {{"modified": t, "expires": e}}] for name in (*d.SOURCES, *d.SOURCES_B) for t in times
                  for e in (None, "2027-01-01T00:00:00+00:00")]
        print(json.dumps({{"sources": list(d.SOURCES), "sources_b": list(d.SOURCES_B), "before": d.SOURCES_BEFORE,
                          "calibrated": list(d.CALIBRATED), "at": d.CALIBRATED_AT,
                          "covers": sorted({{*d.CAL_39_W0.covers, *d.CAL_39_W1.covers}}),
                          "cases": [[n, v, d.source_problems({{n: v}}), d.source_problems({{n: v}}, d.CALIBRATED)]
                                    for n, v in cases]}}))
    """)
    assert r["before"] == ns["SOURCES_BEFORE"] == "2026-11-07"
    assert set(r["calibrated"]) == set(r["sources_b"]) | set(r["covers"])
    assert set(r["covers"]) - set(r["sources_b"]) == {"logs_obs", "logs_w1", "u_tokens"}
    ledger = json.loads((EXPERIMENTS / LEDGER_REL).read_text(encoding="utf-8"))["jobs"]
    bills = {j["job_id"]: j["at"] for j in ledger if j.get("job_id") in ("92c0b37c-0659-4f63-8aa7-0f335265d9fe",
                                                                          "f66a1ca1-d501-4011-ac63-3f46e0815825")}
    assert r["at"] == min(bills.values()) == bills["92c0b37c-0659-4f63-8aa7-0f335265d9fe"] == CALIBRATED_AT
    assert len(r["cases"]) == len(r["sources"] + r["sources_b"]) * (1 + 2 * len(SOURCE_TIMES))
    for name, meta, plain, calibrated in r["cases"]:
        old_text = gate_a({name: meta})
        assert plain == old_text, (name, meta, plain, old_text)
        late = meta is not None and meta["modified"] > CALIBRATED_AT and not old_text
        if name in r["calibrated"] and late:
            assert calibrated == [f"{name} was modified at {meta['modified']}, after the first bill that calibrates "
                                  f"job 39, at {CALIBRATED_AT}"], (name, meta, calibrated)
        else:
            assert calibrated == old_text, (name, meta, calibrated)


def test_a_gate_b_job_stops_after_a_bill_above_one_and_a_half_times_its_estimate(tmp_path):
    """Revision section 12: the real Run.job of a gate B job runs run_bq.py with its estimate (faked here: the
    ledger gains the entry a run_bq.py run would write) and stops after a bill above 1.5 times the estimate."""
    r = run_gate_b(tmp_path, r'''
        rows = {t: 10**6 for t in d.ESTIMATE_TABLES}
        est = d.estimates(rows)["pairs"]
        out = {"est": [est.first, est.whole]}
        for cname, factor in SPEC["cases"].items():
            commands = []

            def setup(root, factor=factor, commands=commands):
                def fake_run(cmd, cwd=None, **kw):
                    commands.append([str(c) for c in cmd[1:]])
                    ledger = json.loads(d.LEDGER.read_text(encoding="utf-8"))
                    billed = int(factor * est.whole)
                    ledger["jobs"].append({"job_id": "j1", "at": "2026-11-10T00:00:00+00:00",
                                           "label": "contract12m: pair tables of both freezes",
                                           "bytes_estimated": est.first, "bytes_billed": billed, "usd": d.usd(billed)})
                    d.LEDGER.write_text(json.dumps(ledger), encoding="utf-8")
                    return SimpleNamespace(returncode=0)
                d.subprocess.run = fake_run
            case = {"constants": "committed", "real_job": True,
                    "tables": {t: {"rows": 10**6} for t in d.ESTIMATE_TABLES}}
            r = run_case(cname, case, ["pairs"], setup=setup)
            d.subprocess.run = REAL_RUN
            m = r.pop("manifest")
            r["manifest_jobs"], r["commands"], r["last"] = m["jobs"], commands, m["steps"][-1]
            out[cname] = r
        print(json.dumps(out))
    ''', {"over": 1.6, "under": 1.4})
    first, whole = r["est"]
    c = r["over"]
    (res,) = c["results"]
    assert res.startswith("stopped: pairs billed") and "more than 1.5 times its estimate" in res, res
    (job,) = c["manifest_jobs"]
    assert (job["key"], job["no"], job["bytes_expected"], job["bytes_first_expected"], job["bytes_billed"]) == (
        "pairs", 37, whole, first, int(1.6 * whole))
    for name in ("over", "under"):
        (cmd,) = r[name]["commands"]
        assert cmd[:2] == ["scripts/run_bq.py", "sql/37_c12_pairs.sql"] and "--dry-run" not in cmd, name
        assert cmd[cmd.index("--max-dry-bytes") + 1] == str(int(1.25 * first)), name
        assert cmd[cmd.index("--expect-bytes") + 1] == str(whole), name
    assert r["under"]["results"] == ["ok"] and r["under"]["last"]["passed"] is True


# --------------------------------------------------------------------------- local helpers of the gate A steps


def test_account_types_must_cover_the_queue():
    out = run_py("""
        import pandas as pd
        import run_contract12m_pipeline as d
        queue = pd.DataFrame({"address": ["0x01", "0x02", "0x03"], "reason": ["cohort", "counterparty", "audit_sender"],
                              "is_emitter": [True, False, False], "is_created": [False, False, True]})
        types = pd.DataFrame({"address": ["0x01", "0x02", "0x03"],
                              "account_class": ["contract", "smart_account", "eoa"]})
        r = d.types_against_queue(types, queue)
        print(r["by_class"], r["by_reason"]["cohort"], r["audit_senders_with_code"])
        for bad in (types.iloc[:2], types.assign(account_class=["contract", "wallet", "eoa"]),
                    pd.concat([types, types.iloc[:1]])):
            try:
                d.types_against_queue(bad, queue)
                print("accepted")
            except SystemExit:
                print("refused")
    """)
    assert out.returncode == 0, out.stderr
    assert out.stdout.splitlines() == ["{'contract': 1, 'eoa': 1, 'smart_account': 1} {'contract': 1} 0",
                                       "refused", "refused", "refused"]


def test_system_range_and_dust_digits():
    out = run_py("""
        import run_contract12m_pipeline as d
        print(d.system_range(255), d.dust_digits(1e-6))
        for f, x in ((d.system_range, 0), (d.system_range, 256), (d.dust_digits, 2e-6)):
            try:
                f(x)
                print("accepted")
            except SystemExit:
                print("refused")
    """)
    assert out.returncode == 0, out.stderr
    assert out.stdout.splitlines() == [f"('0x{'00' * 19}01', '0x{'00' * 19}ff') 6", "refused", "refused", "refused"]


def test_balance_audit_match_rule_on_toy_rows():
    r = run_json("""
        import json
        import pandas as pd
        import balance_audit as b
        dust = 1e-6
        single = [
            b.matches(1e15, 1e15 + 5e5, 6, dust),    # 0.5e-9 relative, far above the dust of one base unit
            b.matches(1e15, 1e15 + 5e6, 6, dust),    # 5e-9 relative and above the dust
            b.matches(-3.0, 0.0, 18, dust),          # a negative reconstruction is clipped to 0
            b.matches(5e11, 0.0, 18, dust),          # 0.5e-6 token of an 18-decimal token: within the dust
            b.matches(2e12, 0.0, 18, dust),          # 2e-6 token: not within it
            b.matches(1_000_000.0, 1_000_000.5, 6, dust),
            b.matches(1.0, float("nan"), 6, dust),   # the RPC gave no value
            b.matches(1.0, None, 6, dust),
        ]
        cfg = {"dust_token": dust, "min_match": 0.98, "min_match_dormant": 0.99}

        def frame(bad_dormant, bad_active):
            n = 100
            onchain = [1e6] * n
            for i in range(bad_dormant):
                onchain[i] = 5e6  # dormant rows (n_w1 = 0) that do not match
            for i in range(bad_active):
                onchain[n - 1 - i] = 5e6  # rows with a transfer in W1 that do not match
            return pd.DataFrame({"bal_tobs": [1e6] * n, "bal_0930": [1e6] * n, "decimals": [6] * n,
                                 "n_w1": [0] * 50 + [3] * 50, "onchain": onchain})

        out = {"single": single}
        for name, (bd, ba, mode) in {"archive_2": (1, 1, "archive"), "archive_3": (2, 1, "archive"),
                                     "latest_active": (0, 5, "latest"), "latest_1": (1, 0, "latest"),
                                     "latest_0": (0, 0, "latest")}.items():
            v = b.judge(frame(bd, ba), mode, cfg)
            out[name] = [v["judged"], v["matched"], v["share"], v["threshold"], v["passed"], v["reference"]]
        out["host"] = [b.host("https://user:secret@arb.example.org:8443/v2/KEY?x=1"),
                       b.host("https://arb1.arbitrum.io/rpc")]
        print(json.dumps(out))
    """)
    assert r["single"] == [True, False, True, True, False, True, False, False]
    assert r["archive_2"] == [100, 98, 0.98, 0.98, True, "bal_tobs"]
    assert r["archive_3"] == [100, 97, 0.97, 0.98, False, "bal_tobs"]
    assert r["latest_active"] == [50, 50, 1.0, 0.99, True, "bal_0930"]  # mismatches after June do not count
    assert r["latest_1"] == [50, 49, 0.98, 0.99, False, "bal_0930"]
    assert r["latest_0"][4] is True
    assert r["host"] == ["arb.example.org:8443", "arb1.arbitrum.io"]


def test_balance_audit_endpoints_put_the_key_first_and_never_print_it():
    out = run_py("""
        import os
        os.environ["CONTRACT_REP_RPC_URL"] = "https://provider.example/v2/SECRETKEY"
        import balance_audit as b
        from common import load_config
        urls = b.endpoints(load_config())
        print(urls[0] == os.environ["CONTRACT_REP_RPC_URL"], [b.host(u) for u in urls])
    """)
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == ("True ['provider.example', 'arb1.arbitrum.io', 'arbitrum-one.public.blastapi.io']")


AUDIT_MAIN = r"""
    import json, os, sys
    from pathlib import Path
    import pandas as pd
    import balance_audit as b
    from common import write_parts
    tmp, mode = Path(sys.argv[1]), sys.argv[2]
    archive, flaky = mode in ("archive", "archive_after_error"), [mode == "archive_after_error"]
    os.environ["CONTRACT_REP_RPC_URL"] = "https://provider.example/v2/SECRETKEY"
    b.OUT = tmp / "out"
    usdc = "0xaf88d065e77c8cc2239327c5edb3a432268e5831"
    owners = [f"0x{i:040x}" for i in range(1, 7)]
    write_parts(pd.DataFrame({"token": [usdc] * 6, "owner": owners, "bal_tobs": [0.0, -2.0, 5e6, 7e6, 1e6, 3e6],
                              "bal_0930": [0.0, 0.0, 5e6, 7e6, 9e6, 3e6], "n_w1": [0, 0, 0, 0, 2, 0],
                              "decimals": [6] * 6, "cell": ["zero", "zero", "positive", "positive", "positive",
                                                            "positive"]}), tmp / "bal_audit")
    write_parts(pd.DataFrame({"anchor": ["t1", "tobs", "end_0930"], "block_number": [100, 200, 300]}),
                tmp / "anchor_blocks")
    tobs = {owners[i]: v for i, v in enumerate([0, 0, 5_000_000, 7_000_000, 1_000_000, 3_000_000])}
    latest = {owners[i]: v for i, v in enumerate([0, 0, 5_000_000, 7_000_000, 4_000_000, 3_000_000])}
    seen = []

    def send(self, url, payload):  # the network, mocked: the keyed endpoint first, then the public ones
        seen.append((b.host(url), payload if isinstance(payload, dict) else payload[0]["params"][1]))
        if mode == "outage":
            return None, "HTTP 503"
        if isinstance(payload, dict):
            return {"jsonrpc": "2.0", "id": 1, "result": hex(999)}, ""
        out = []
        for c in payload:
            owner, block = "0x" + c["params"][0]["data"][-40:], c["params"][1]
            if block == hex(200) and mode == "probe_fails":
                return None, "HTTP 504"   # every request at the T_obs block fails
            if block == hex(200) and flaky[0] and b.host(url) == "provider.example":
                flaky[0] = False  # one rate limit in an HTTP 200 body, then the provider serves the block
                out.append({"jsonrpc": "2.0", "id": c["id"], "error": {"code": 429, "message": "Too Many Requests"}})
            elif block == hex(200) and not archive:
                error = {"code": -32000, "message": "missing trie node"}
                out.append({"jsonrpc": "2.0", "id": c["id"], "error": error})
            else:
                value = (tobs if block == hex(200) else latest)[owner]
                out.append({"jsonrpc": "2.0", "id": c["id"], "result": "0x" + f"{value:064x}"})
        return out, ""

    b.Rpc.send = send
    b.time.sleep = lambda s: None
    sys.argv = ["balance_audit.py", "--sample", str(tmp / "bal_audit"), "--anchors", str(tmp / "anchor_blocks")]
    rc = b.main()
    path = b.OUT / "balance_audit.json"
    text = path.read_text(encoding="utf-8") if path.exists() else "{}"
    print(json.dumps({"rc": rc, "out": json.loads(text), "secret": "SECRETKEY" in text,
                      "csv": (b.OUT / "balance_audit.csv").exists(), "hosts": sorted({h for h, _ in seen})}))
"""


@pytest.mark.parametrize("mode", ["archive", "archive_after_error", "latest", "probe_fails", "outage"])
def test_balance_audit_main_with_the_network_mocked(tmp_path, mode):
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8",
           "CONTRACT_REP_VARIANT": "contract12m"}
    out = subprocess.run([sys.executable, "-c", textwrap.dedent(AUDIT_MAIN), str(tmp_path), mode], cwd=SCRIPTS,
                         env=env, capture_output=True, text=True, encoding="utf-8")
    assert out.returncode == 0, out.stderr
    assert "SECRETKEY" not in out.stdout + out.stderr
    r = json.loads(out.stdout.strip().splitlines()[-1])
    if mode == "outage":
        # No endpoint answers anything, the latest block included: no check is made (exit 2) and nothing written.
        assert r["rc"] == 2 and r["out"] == {} and not r["csv"]
        return
    assert r["csv"] and not r["secret"]
    o = r["out"]
    assert o["mode"] == ("archive" if mode.startswith("archive") else "latest") and o["rows"] == 6
    if mode.startswith("archive"):
        # every pair is judged at the T_obs block; the negative reconstruction is clipped to 0 and matches. A rate
        # limit in an HTTP 200 body is retried (revision section 4.2 rule 2), so it does not decide the mode.
        assert (o["block"], o["judged"], o["matched"], o["passed"], r["rc"]) == (200, 6, 6, True, 0)
        assert o["hosts"] == ["provider.example", "arb1.arbitrum.io", "arbitrum-one.public.blastapi.io"]
        assert set(o["archive_probe"].values()) == {"served"}
        assert o["archive_probe_attempts"]["provider.example"] == (2 if mode == "archive_after_error" else 1)
    else:
        # No endpoint serves the T_obs block, whether it answers with an error or fails every attempt (rule 2): the
        # latest block, judged on the owners without a transfer in W1 (owner 5 moved tokens).
        assert (o["block"], o["judged"], o["matched"], o["passed"], r["rc"]) == (999, 5, 5, True, 0)
        assert o["overall_share"] == round(5 / 6, 6)
        assert set(o["archive_probe"].values()) == (
            {"error: missing trie node"} if mode == "latest" else {"no answer"})
        assert set(o["archive_probe_attempts"].values()) == {1 + 3}   # retried three times
    assert set(o["archive_probe"]) == {"provider.example", "arb1.arbitrum.io", "arbitrum-one.public.blastapi.io"}
    assert set(o["calls_per_host"]) <= set(o["archive_probe"])
