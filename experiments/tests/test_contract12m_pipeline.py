"""The driver of the contract-graph revision (scripts/run_contract12m_pipeline.py, docs/revision_contract_graph.md
section 12), its gate A SQL files (sql/24 to 35 and 43) and the match rule of scripts/balance_audit.py.

Nothing here reaches the network or BigQuery. The code of the variant runs in subprocesses with
CONTRACT_REP_VARIANT=contract12m, since scripts/common.py reads the variant once, at import."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap

import pytest

from conftest import EXPERIMENTS, SCRIPTS

JOB_KEYS = {"logs5", "ends", "tx_senders", "emitters", "creations", "rpc_queue", "contracts", "bal_pre", "bal",
            "anchor_blocks", "bal_audit", "structure"}
VIEWS = {f"bigquery-public-data.goog_blockchain_arbitrum_one_us.{v}"
         for v in ("transactions", "receipts", "decoded_events", "blocks", "logs")}


def run_py(code: str, variant: str | None = "contract12m", cwd=SCRIPTS) -> subprocess.CompletedProcess:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
    env.pop("CONTRACT_REP_VARIANT", None)
    env.pop("CONTRACT_REP_RPC_URL", None)
    if variant:
        env["CONTRACT_REP_VARIANT"] = variant
    return subprocess.run([sys.executable, "-c", textwrap.dedent(code)], cwd=cwd, env=env, capture_output=True,
                          text=True, encoding="utf-8")


def run_json(code: str):
    out = run_py(code)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout.strip().splitlines()[-1])


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
                          "gate_b": list(d.GATE_B), "prefix": d.PREFIX, "campaign": d.CAMPAIGN, "cap": d.CAP_USD,
                          "ratios": [d.DRY_RATIO, d.BILL_RATIO],
                          "manifest": d.MANIFEST.relative_to(d.ROOT).as_posix()}))
    """)
    assert r["steps"] == ["check", "subset", "ends", "activity", "queue", "typing", "load", "contracts", "balances",
                          "anchors", "audit", "structure", "constants", "pairs", "rest", "checks", "download"]
    assert all(r["funcs"])
    assert r["gate_b"] == r["steps"][-5:]
    assert (r["prefix"], r["campaign"], r["cap"], r["ratios"]) == ("c12_", "contract12m:", 14.0, [1.25, 1.5])
    assert r["manifest"] == "data/2-processed-tables-and-evaluations/revised-contract-12m/run_manifest.json"


@pytest.mark.parametrize("steps", [["constants"], ["pairs"], ["rest"], ["checks"], ["download"],
                                   ["structure", "constants"]])
def test_gate_b_steps_refuse(steps):
    env = {**os.environ, "CONTRACT_REP_VARIANT": "contract12m", "PYTHONDONTWRITEBYTECODE": "1"}
    out = subprocess.run([sys.executable, "scripts/run_contract12m_pipeline.py", *steps, "--dry-run"], cwd=EXPERIMENTS,
                         env=env, capture_output=True, text=True)
    assert out.returncode != 0
    assert "gate B: not yet written" in out.stderr and "section 12" in out.stderr, out.stderr
    assert "$" not in out.stdout  # nothing ran before the refusal


def test_every_job_has_its_sql_file_and_is_committed_at_gate_a():
    r = run_json("""
        import json
        import run_contract12m_pipeline as d
        import run_discovery as rd
        from common import load_config
        jobs = d.all_jobs(load_config())
        print(json.dumps({"keys": [j.key for j in jobs], "nos": [j.no for j in jobs], "sql": [j.sql for j in jobs],
                          "exists": [(d.ROOT / "sql" / j.sql).exists() for j in jobs], "files": list(d.SQL_FILES),
                          "committed": list(d.COMMITTED), "pilot": list(d.PILOT_COMMITTED),
                          "discovery": list(rd.COMMITTED), "on_disk": [(d.ROOT / f).exists() for f in d.COMMITTED]}))
    """)
    assert set(r["keys"]) == JOB_KEYS and len(r["keys"]) == len(JOB_KEYS)
    assert all(r["exists"])
    assert sorted(r["sql"]) == sorted(r["files"])
    assert all(s.startswith(f"{n}_c12_") for s, n in zip(r["sql"], r["nos"]))
    # The gate A list of revision section 12, the revision first (its commit is the reference point).
    assert r["committed"] == [
        "docs/revision_contract_graph.md", "docs/discovery_protocol.md", "config/overlay_contract12m.yaml",
        "config/contract_reputation.yaml", "scripts/run_contract12m_pipeline.py", "scripts/run_bq.py",
        "scripts/common.py", "scripts/check_account_code.py", "scripts/balance_audit.py", "scripts/download_table.py",
        "scripts/crawl.py", "scripts/run_discovery.py", "scripts/scoring.py", "scripts/stats.py", "scripts/graphs.py",
        *(f"sql/{f}" for f in r["files"])]
    assert all(r["on_disk"]) and len(set(r["committed"])) == len(r["committed"])
    # The structure step checks the pilot's record of the files run_discovery.py records, all of them committed here.
    assert r["pilot"] == r["discovery"] and set(r["pilot"]) <= set(r["committed"])


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


def test_jobs_create_only_c12_tables_and_read_what_they_may():
    jobs = run_json(PROBE)
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


def test_public_views_are_named_and_allowed():
    jobs = run_json(PROBE)
    readers = {k for k, j in jobs.items() if j["outside"]}
    assert readers == {"tx_senders", "emitters", "creations", "bal_pre", "anchor_blocks"}
    for key, j in jobs.items():
        assert j["outside"] == sorted(j["public"]), key
        assert set(j["public"]) <= VIEWS, key
    assert {v.rsplit(".", 1)[1] for k in readers for v in jobs[k]["public"]} == {
        "transactions", "decoded_events", "receipts", "logs", "blocks"}


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


def test_job_parameters_follow_the_configuration():
    r = run_json("""
        import json
        import run_contract12m_pipeline as d
        from common import load_config
        cfg = load_config()
        jobs = {j.key: j for j in d.all_jobs(cfg)}
        print(json.dumps({k: [j.params, j.subs] for k, j in jobs.items()}))
    """)
    assert r["logs5"][0] == {"start_ts": "2025-04-01 00:00:00 UTC", "mid_ts": "2026-07-01 00:00:00 UTC",
                             "end_ts": "2026-10-01 00:00:00 UTC"}
    assert r["emitters"][0] == {"start_ts": "2025-04-01 00:00:00 UTC", "end_ts": "2026-10-01 00:00:00 UTC"}
    # K holds the system addresses like any other end (revision section 4.3); the node set leaves them out.
    assert r["rpc_queue"][0] == {"sender_salt": "audit-sender-v1:", "untyped_salt": "audit-untyped-v1:"}
    assert r["contracts"][0] == {"system_first": "0x" + "00" * 19 + "01", "system_last": "0x" + "00" * 19 + "ff"}
    assert r["rpc_queue"][1] == {"AUDIT_SENDERS": "1000", "AUDIT_UNTYPED": "1000"}
    assert r["bal"][0]["t1"] == "2026-03-31 23:59:59 UTC" and r["bal"][0]["tobs"] == "2026-06-30 23:59:59 UTC"
    assert r["bal"][0]["end_0930"] == "2026-09-30 23:59:59 UTC"
    assert r["bal"][0]["obs_start"] == "2023-10-01 00:00:00 UTC"
    assert r["bal_pre"][0] == {"obs_start": "2023-10-01 00:00:00 UTC", "start_ts": "2025-04-01 00:00:00 UTC",
                               "tobs_end": "2026-07-01 00:00:00 UTC"}
    assert r["bal_audit"][0] == {"audit_salt": "bal-audit-v1:", "per_cell": "150", "dust_digits": "6"}
    assert r["structure"][0] == {"start_ts": "2025-04-01 00:00:00 UTC", "t1": "2026-03-31 23:59:59 UTC",
                                 "dust_digits": "6"}


def test_the_queue_keeps_the_system_addresses_and_the_node_set_drops_them():
    # Revision section 4.3 defines K without the system addresses' exception; section 4.1 makes them never
    # contracts, and user accounts only by rule 1 (a transaction sender). So sql/29 reads no system bounds and
    # sql/31 applies them to c12_contracts and to the RPC-typed part of c12_user_accounts, not to the senders.
    import re

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
    import re
    with open(EXPERIMENTS / "data" / "0-usd-token-list-and-prices" / "listed_tokens.csv", encoding="utf-8") as f:
        selected = {r["address"].lower() for r in csv.DictReader(f) if str(r["selected"]).lower() == "true"}
    sql = (EXPERIMENTS / "sql" / "32_c12_bal_pre.sql").read_text(encoding="utf-8")
    assert set(re.findall(r"'(0x[0-9a-f]{40})'", sql)) == selected and len(selected) == 5


def test_estimates_are_positive_and_cover_every_read():
    r = run_json("""
        import json
        import run_contract12m_pipeline as d
        from common import load_config
        cfg = load_config()
        full = d.estimates({t: 1_000_000 for t in d.ESTIMATE_TABLES})
        none = d.estimates({})
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
                          "none": {k: list(e.missing) for k, e in none.items()},
                          "bounded": {k: list(e.missing) for k, e in bounded.items()},
                          "statements": {k: len(v) for k, v in d.READS.items()}, "cover": cover,
                          "min": d.MIN_TABLE}))
    """)
    assert set(r["full"]) == JOB_KEYS
    for key, (first, whole, missing) in r["full"].items():
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


def test_command_carries_the_checks_of_run_bq():
    r = run_json("""
        import json
        import run_contract12m_pipeline as d
        from common import load_config
        job = d.jobs(load_config())["activity"][0]
        cmd = d.command(job, d.Estimate(1000, 3000), dry=True)
        print(json.dumps(cmd[1:]))
    """)
    flag = lambda name: r[r.index(name) + 1]  # noqa: E731
    assert r[0] == "scripts/run_bq.py" and r[1] == "sql/26_c12_tx_senders.sql" and r[-1] == "--dry-run"
    assert flag("--label").startswith("contract12m: ") and flag("--require-prefix") == "c12_"
    assert flag("--campaign") == "contract12m:" and flag("--campaign-cap") == "14.0"
    assert flag("--expect-bytes") == "3000" and flag("--max-dry-bytes") == "1250"
    assert flag("--allow-public") == "bigquery-public-data.goog_blockchain_arbitrum_one_us.transactions"
    assert flag("--param") == "end_ts=2026-10-01 00:00:00 UTC" and "--force" not in r


def test_inputs_refuse_uncommitted_files():
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


def test_steps_wait_for_the_steps_before_them():
    r = run_json("""
        import json
        import run_contract12m_pipeline as d

        def m(*runs, check=()):
            return {"steps": [{"step": s, "passed": p} for s, p in runs],
                    "checks_run": [] if check is None else [{"problems": list(check)}]}

        passed = [(s, True) for s in d.CHAIN]
        upto = lambda step: passed[:d.CHAIN.index(step)]  # noqa: E731
        print(json.dumps({
            "chain": list(d.CHAIN),
            "free": [d.prerequisites("check", m(check=None)), d.prerequisites("constants", m(check=None))],
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
    assert r["chain"] == ["subset", "ends", "activity", "queue", "typing", "load", "contracts", "balances", "anchors",
                          "audit", "structure"]
    assert r["free"] == [[], []]
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


# The audit and structure steps with BigQuery, the downloads and the two local scripts faked (nothing is run or
# billed). Each case starts from a manifest whose steps before audit (or before structure) passed, with an earlier
# balance_audit.json and feasibility_t1.json on disk.
STEPS_FAKED = r"""
    import json, sys, types
    from pathlib import Path
    import pandas as pd
    import run_contract12m_pipeline as d
    from common import load_config

    cfg = load_config()
    pairs = [(f"0x{i:040x}", f"0x{i + 1:040x}", "allow_capped") for i in range(6000)]
    d.client_and_dataset = lambda cfg: (None, "dissertation-bq.contract_rep")
    d.inputs = lambda dry: {"head": "abc123"}
    d.Run.job = lambda self, job: calls.append(f"job {job.no}")
    d.Run.sizes = lambda self, *names: {n: 6000 for n in names}
    d.sh = lambda cmd: calls.append("download " + cmd[2].split(".")[-1])
    d.read_parts = lambda stem, columns=None: pd.DataFrame(pairs, columns=["a", "b", "layer"])

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
