#!/usr/bin/env python3
"""Post-clearance re-extraction (review item C-01): replay the BigQuery jobs of the ledger in a replica.

The earlier extracts stay as they are: their ledger (data/bq_ledger.json), tables and result folders are never
written. The replica is a copy of experiments/{scripts,sql,config,docs,tests} at one commit, outside the
repositories and its own git repository, in which only the dataset name differs (config/reextract.yaml:
contract_rep -> contract_rep_r1). Every paid query runs through the replica's own scripts/run_bq.py, which bills
the replica's own ledger, with the label prefix and the cap of the campaign.

Commands (run from experiments/ of the real repository):
  plan                 the jobs to replay, in ledger order, with the tables each creates, the tables no replayed job
                       creates (local steps), the earlier bills, and the SQL files modified after their job ran
  replica [--force]    build the replica (git archive of HEAD; dataset renamed in config and sql/; inputs copied;
                       git init and commit); refuses an existing replica
  status               the replica ledger against the plan: done, failed, next, billed so far
  next [--only N,M] [--until N] [--dry-run]
                       run the jobs of the plan that the replica ledger has not finished, in ledger order, stopping
                       before a local step that has not been marked done or after job N; a finished job is never
                       billed again; refuses a job whose SQL names the old dataset or a dataset other than the
                       project's and the public one, a job whose constants differ from the ledger, and a job whose
                       expected bill would pass the cap; stops after a job that billed more than bill_ratio_stop
                       times its earlier bill
  local NAME           run a local step in the replica: downloads (not billed) compared exactly with the earlier
                       downloads, RPC reads at the earlier block, loads (not billed); its comparisons go to the
                       replica's data/r1_local_compare.json, and the step is marked done
  done-local NAME      mark a local step done (after its commands ran in the replica)
  compare-meta [--scans]
                       row counts of the replayed tables, old against new, from table metadata (free); with --scans
                       also the monthly partitions of logs_obs and logs_w1 (one INFORMATION_SCHEMA query through the
                       replica's run_bq.py, billed at the 10 MB minimum)
  compare-results NAME FOLDER...
                       compare every file of the earlier FOLDERs (below data/) with the replica's: parquet parts as
                       tables (compare_stems), JSON value by value (keys of run times, commits, hosts and paths
                       counted apart as volatile), other files byte for byte (line ends aside); writes the
                       replica's data/r1_compare_results_NAME.json
  manifest             write the record folder data/4-post-clearance-reextraction/
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CONFIG = ROOT / "config" / "reextract.yaml"
RECORD = ROOT / "data" / "4-post-clearance-reextraction"
PROJECT = "dissertation-bq"
OLD = "contract_rep"


def load_cfg() -> dict:
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


def replica_root(cfg: dict) -> Path:
    return Path(cfg["replica"])


def ledger_jobs(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))["jobs"]


def old_jobs() -> list[dict]:
    return ledger_jobs(ROOT / "data" / "bq_ledger.json")


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --------------------------------------------------------------------------- SQL text of a job

def rename_dest(dest: str, dataset: str) -> str:
    ds, table = dest.split(".", 1)
    if ds != OLD:
        raise SystemExit(f"destination {dest} is not in {OLD}")
    return f"{dataset}.{table}"


def job_sql(job: dict, root: Path, dataset: str) -> str:
    """The SQL of a ledger job as run_bq.py sends it: __DEST__, --sub, then --rename (run_bq.apply_renames)."""
    sql = (root / job["sql"]).read_text(encoding="utf-8")
    if job.get("dest"):
        sql = sql.replace("__DEST__", f"{PROJECT}.{rename_dest(job['dest'], dataset)}")
    for sub in job.get("subs") or []:
        key, value = sub.split("=", 1)
        sql = sql.replace(f"__{key}__", value)
    for r in job.get("renames") or []:
        old, new = r.split("=", 1)
        pat = re.compile(rf"`{re.escape(PROJECT)}\.{re.escape(dataset)}\.{re.escape(old)}`")
        sql, n = pat.subn(f"`{PROJECT}.{dataset}.{new}`", sql)
        if n == 0:
            raise SystemExit(f"rename {r} matches nothing in {job['sql']}")
    return sql


_COMMENT = re.compile(r"--[^\n]*")


def tables(sql: str, dataset: str) -> tuple[set[str], set[str]]:
    """(created, read) tables of the project dataset; comments left out."""
    body = _COMMENT.sub(" ", sql)
    ds = rf"`{re.escape(PROJECT)}\.{re.escape(dataset)}\.(\w+)`"
    created = set(re.findall(rf"CREATE\s+(?:OR\s+REPLACE\s+)?(?:TABLE|VIEW)\s+{ds}", body, flags=re.I))
    read = set(re.findall(ds, body)) - created
    return created, read


def foreign(sql: str, dataset: str, public: str) -> list[str]:
    """Names of other datasets than the project dataset and the public one, and any mention of the old dataset."""
    body = _COMMENT.sub(" ", sql)
    out = []
    for m in re.finditer(r"`([\w-]+)\.([\w-]+)\.(\w+)`", body):
        p, d, _ = m.groups()
        if f"{p}.{d}" in (f"{PROJECT}.{dataset}", public):
            continue
        out.append(m.group(0))
    if dataset != OLD and re.search(rf"\b{re.escape(OLD)}\.", body):
        out.append(f"old dataset {OLD}")
    return sorted(set(out))


# --------------------------------------------------------------------------- the plan

def usable(j: dict) -> bool:
    # exploratory jobs ran SQL outside sql/ (a scratch folder) and belong to neither analysis
    return bool(j.get("sql")) and j["sql"].startswith("sql/") and not j.get("error")


def select(cfg: dict, jobs: list[dict]) -> list[int]:
    """1-based ledger positions to replay: the targets and the jobs that made the tables they read."""
    ok = [i for i, j in enumerate(jobs, 1) if usable(j)]
    info = {i: tables(job_sql(jobs[i - 1], ROOT, OLD), OLD) for i in ok}
    t = cfg["targets"]
    want = set(t["registered"]) | set(t.get("extra", []))
    if t["contract12m"] == "all":
        want |= {i for i in ok if jobs[i - 1].get("variant") == "contract12m"}
    else:
        want |= set(t["contract12m"])
    # a job made again later on the same tables (a rerun after a fix) is replaced by the last one
    last = {}
    for i in ok:
        for tab in info[i][0]:
            last[tab] = i
    want = {max(last[tab] for tab in info[i][0]) if info[i][0] else i for i in want if i in info}
    todo = sorted(want)
    while todo:
        i = todo.pop()
        for tab in info[i][1]:
            makers = [m for m in ok if m < i and tab in info[m][0]]
            if makers and makers[-1] not in want:
                want.add(makers[-1])
                todo.append(makers[-1])
    return sorted(want)


def sql_history(job: dict) -> list[str]:
    """Commits after the job that modified its SQL file (a commit that only added the file is not counted)."""
    out = subprocess.run(["git", "log", f"--since={job['at']}", "--diff-filter=M", "--format=%h %cI %s", "--",
                          job["sql"]], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout
    return [line for line in out.splitlines() if line.strip()]


def plan_rows(cfg: dict) -> tuple[list[dict], dict]:
    jobs = old_jobs()
    rows, made, external = [], set(), {}
    for i in select(cfg, jobs):
        j = jobs[i - 1]
        c, r = tables(job_sql(j, ROOT, OLD), OLD)
        for tab in sorted(r - made):
            external.setdefault(tab, i)
        made |= c
        rows.append({"job": i, "sql": j["sql"], "label": j.get("label", ""), "variant": j.get("variant"),
                     "usd": j.get("usd", 0.0), "bytes_billed": j.get("bytes_billed", 0), "creates": sorted(c),
                     "reads": sorted(r), "modified_after": sql_history(j)})
    return rows, external


def cmd_plan(cfg: dict, args) -> int:
    rows, external = plan_rows(cfg)
    local = {s["before_job"]: name for name, s in cfg["local_steps"].items()}
    for r in rows:
        if r["job"] in local:
            print(f"    -- local step {local[r['job']]}")
        flag = f"  MODIFIED AFTER: {r['modified_after']}" if r["modified_after"] else ""
        print(f"{r['job']:>3} {r['usd']:7.3f} {Path(r['sql']).name:28} {r['label'][:58]}{flag}")
    print(f"\n{len(rows)} jobs, earlier bills USD {sum(r['usd'] for r in rows):.2f}")
    print("tables no replayed job creates, and the local step that makes each:")
    for tab, first in sorted(external.items()):
        steps = [n for n, s in cfg["local_steps"].items() if tab in s.get("makes", [])]
        print(f"  {tab}: first read by job {first}; {steps or 'NO LOCAL STEP'}")
    return 0


# --------------------------------------------------------------------------- the replica

def git_out(*a: str, cwd: Path = ROOT) -> str:
    return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                          check=True).stdout


def rewrite_dataset(text: str, new: str) -> tuple[str, int]:
    return re.subn(rf"(?<![\w-]){re.escape(PROJECT)}\.{re.escape(OLD)}\.", f"{PROJECT}.{new}.", text)


def cmd_replica(cfg: dict, args) -> int:
    rep = replica_root(cfg)
    if rep.exists():
        raise SystemExit(f"{rep} exists; the replica is built once (move it away to build it afresh)")
    head = git_out("rev-parse", "HEAD").strip()
    top = Path(git_out("rev-parse", "--show-toplevel").strip())
    rel = ROOT.resolve().relative_to(top.resolve()).as_posix()
    rep.mkdir(parents=True)
    tar = rep.parent / "_replica.tar"
    subprocess.run(["git", "archive", "--format=tar", f"--output={tar}", head,
                    *(f"{rel}/{f}" for f in cfg["replica_folders"])],
                   cwd=top, check=True)
    tmp = rep.parent / "_replica_tmp"
    tmp.mkdir()
    subprocess.run(["tar", "-xf", str(tar), "-C", str(tmp)], check=True)
    for f in cfg["replica_folders"]:
        shutil.move(str(tmp / rel / f), str(rep / f))
    shutil.rmtree(tmp)
    tar.unlink()
    # the one change: the dataset name, in the configuration and in the SQL files
    changed = {}
    conf = rep / "config" / "contract_reputation.yaml"
    text = conf.read_text(encoding="utf-8")
    text2, n = re.subn(rf"(?m)^(\s*dataset:\s*){re.escape(OLD)}\s*$", rf"\g<1>{cfg['new_dataset']}", text)
    if n != 1:
        raise SystemExit("the dataset line of contract_reputation.yaml was not found exactly once")
    conf.write_bytes(text2.encode("utf-8"))
    changed["config/contract_reputation.yaml"] = n
    for f in sorted((rep / "sql").glob("*.sql")):
        t = f.read_bytes().decode("utf-8")
        t2, n = rewrite_dataset(t, cfg["new_dataset"])
        if n:
            f.write_bytes(t2.encode("utf-8"))
            changed[f"sql/{f.name}"] = n
        if re.search(rf"\b{re.escape(OLD)}\.", _COMMENT.sub(" ", t2)):
            raise SystemExit(f"sql/{f.name} still names {OLD} after the rename")
    for d in cfg["replica_inputs"]:
        src = ROOT / d
        shutil.copytree(src, rep / d)
    (rep / "data").mkdir(exist_ok=True)
    (rep / "REPLICA.md").write_text(
        "# Replica for the post-clearance re-extraction (review item C-01)\n\n"
        f"Built {now()} from commit {head} of the public repository ({rel}/), by scripts/reextract.py replica.\n"
        f"Only change: dataset `{OLD}` -> `{cfg['new_dataset']}` in config/contract_reputation.yaml and sql/*.sql.\n"
        f"Inputs copied as they are: {', '.join(cfg['replica_inputs'])}.\n"
        "The ledger of this replica is data/bq_ledger.json; it holds only the re-extraction.\n",
        encoding="utf-8")
    (rep / "replica_build.json").write_text(json.dumps({
        "built_at": now(), "source_commit": head, "source_path": rel, "folders": cfg["replica_folders"],
        "inputs": cfg["replica_inputs"], "old_dataset": OLD, "new_dataset": cfg["new_dataset"],
        "renamed": changed}, indent=2), encoding="utf-8")
    (rep / ".gitignore").write_text("__pycache__/\n*.parquet\ndata/_work/\n.pytest_cache/\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=rep, check=True)
    subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=rep, check=True)
    subprocess.run(["git", "add", "-A"], cwd=rep, check=True)
    subprocess.run(["git", "commit", "-q", "-m", f"replica of {head} with dataset {cfg['new_dataset']}"],
                   cwd=rep, check=True)
    print(f"replica at {rep} from {head}; renamed: {sum(changed.values())} names in {len(changed)} files")
    return 0


# --------------------------------------------------------------------------- running the jobs

def rep_ledger(cfg: dict) -> list[dict]:
    return ledger_jobs(replica_root(cfg) / "data" / "bq_ledger.json")


def label_of(cfg: dict, i: int, j: dict) -> str:
    return f"{cfg['campaign']} job {i}: {j.get('label', '')}"


def finished(cfg: dict) -> dict[int, dict]:
    out = {}
    for e in rep_ledger(cfg):
        m = re.match(rf"{re.escape(cfg['campaign'])} job (\d+):", e.get("label", ""))
        if m and not e.get("error"):
            out[int(m.group(1))] = e
    return out


def campaign_usd(cfg: dict) -> float:
    return sum(e.get("usd", 0.0) for e in rep_ledger(cfg) if e.get("label", "").startswith(cfg["campaign"]))


def local_done(cfg: dict) -> set[str]:
    d = replica_root(cfg) / "data" / "_r1_steps"
    return {p.stem for p in d.glob("*.json")} if d.exists() else set()


def cmd_status(cfg: dict, args) -> int:
    rows, _ = plan_rows(cfg)
    fin = finished(cfg)
    local = {s["before_job"]: n for n, s in cfg["local_steps"].items()}
    ld = local_done(cfg)
    nxt = None
    for r in rows:
        if r["job"] in local:
            print(f"    -- local step {local[r['job']]}: {'done' if local[r['job']] in ld else 'NOT DONE'}")
        e = fin.get(r["job"])
        st = f"done USD {e['usd']:.3f} (earlier {r['usd']:.3f})" if e else "-"
        if not e and nxt is None:
            nxt = r["job"]
        print(f"{r['job']:>3} {Path(r['sql']).name:28} {st}")
    print(f"\ncampaign {cfg['campaign']!r}: USD {campaign_usd(cfg):.4f} of {cfg['cap_usd']:.2f}; next job {nxt}")
    return 0


def table_rows(cfg: dict, table: str) -> list[dict]:
    from google.cloud import bigquery
    client = bigquery.Client(project=PROJECT)
    t = client.get_table(f"{PROJECT}.{cfg['new_dataset']}.{table}")
    return [dict(r.items()) for r in client.list_rows(t)]  # tabledata.list: not billed


def constants_problem(cfg: dict, i: int, j: dict) -> str | None:
    """Recompute the constants a job takes as parameters from the new constants table; None if they agree."""
    src = next((t for t, c in cfg["constants"].items() if i in c["jobs"]), None)
    if src is None:
        return None
    rows = table_rows(cfg, src)
    if len(rows) != 1:
        return f"{src} has {len(rows)} rows"
    row = {k: float(v) for k, v in rows[0].items() if v is not None and isinstance(v, (int, float))}
    p = j["params"]
    expect: dict[str, float] = {}
    sys.path.insert(0, str(HERE))
    from usd import round_sig, slope_for_median  # the rule of the three pipelines
    if "b_transfer" in p:
        expect["b_transfer"] = slope_for_median(round_sig(row["m_transfer"]))
        expect["b_allowance"] = slope_for_median(round_sig(row["m_allowance"]))
    if "cap_allowance" in p:
        expect["cap_allowance"] = round_sig(row["p99_transfer"])
    if "cap_user" in p:
        expect["cap_user"] = round_sig(row["p99_user_transfer"])
    bad = [f"{k}: ledger {p[k]}, new {v!r}" for k, v in expect.items() if not math.isclose(float(p[k]), v,
                                                                                            rel_tol=1e-12)]
    return "; ".join(bad) or None


def run_job(cfg: dict, i: int, j: dict, dry: bool, again: bool = False) -> int:
    rep = replica_root(cfg)
    ds = cfg["new_dataset"]
    sql = job_sql(j, rep, ds)
    bad = foreign(sql, ds, cfg["public_dataset"])
    if bad:
        raise SystemExit(f"refused job {i}: its SQL names {bad}")
    prob = constants_problem(cfg, i, j) if not dry else None
    if prob:
        raise SystemExit(f"STOP before job {i}: the constants differ from the ledger after rounding: {prob}")
    expected = int(max(j.get("bytes_billed", 0), j.get("bytes_estimated", 0), j.get("bytes_expected", 0)) * 1.05)
    spent = campaign_usd(cfg)
    exp_usd = expected / 2**40 * 6.25
    if not dry and spent + exp_usd > cfg["cap_usd"]:
        raise SystemExit(f"refused job {i}: campaign USD {spent:.2f} + expected {exp_usd:.2f} passes the cap")
    cmd = [sys.executable, "-B", "-X", "utf8", "scripts/run_bq.py", j["sql"], "--label", label_of(cfg, i, j) + (" (run again after a missing local step)" if again else ""),
           "--campaign", cfg["campaign"], "--campaign-cap", str(cfg["cap_usd"]), "--expect-bytes", str(expected)]
    if j.get("dest"):
        cmd += ["--dest", rename_dest(j["dest"], ds)]
    for k, v in (j.get("params") or {}).items():
        cmd += ["--param", f"{k}={v}"]
    for s in j.get("subs") or []:
        cmd += ["--sub", s]
    for r in j.get("renames") or []:
        cmd += ["--rename", r]
    if dry:
        cmd.append("--dry-run")
    env = dict(os.environ)
    if j.get("variant"):
        env["CONTRACT_REP_VARIANT"] = j["variant"]
    else:
        env.pop("CONTRACT_REP_VARIANT", None)
    print(f"\n== job {i}: {j.get('label', '')}  (earlier USD {j.get('usd', 0):.3f}, expect <= {exp_usd:.3f})",
          flush=True)
    rc = subprocess.run(cmd, cwd=rep, env=env).returncode
    if rc != 0 or dry:
        return rc
    e = finished(cfg).get(i)
    if e and j.get("bytes_billed") and e["bytes_billed"] > cfg["bill_ratio_stop"] * j["bytes_billed"] + 50 * 2**20:
        print(f"STOP: job {i} billed {e['bytes_billed']:,} bytes, more than {cfg['bill_ratio_stop']} times the "
              f"earlier {j['bytes_billed']:,}")
        return 3
    return 0


def cmd_next(cfg: dict, args) -> int:
    rows, _ = plan_rows(cfg)
    jobs = old_jobs()
    fin = finished(cfg)
    only = {int(x) for x in args.only.split(",")} if args.only else None
    local = {s["before_job"]: n for n, s in cfg["local_steps"].items()}
    ld = local_done(cfg)
    for r in rows:
        i = r["job"]
        if only is not None and i not in only:
            continue
        if i in fin and not (args.rerun and only is not None):
            continue
        if only is None and i in local and local[i] not in ld:
            print(f"stopped before job {i}: local step {local[i]} is not done ({cfg['local_steps'][local[i]]['what']})")
            return 0
        rc = run_job(cfg, i, jobs[i - 1], args.dry_run, again=bool(args.rerun and i in fin))
        if rc:
            print(f"stopped at job {i} (exit {rc})")
            return rc
        if args.until and i >= args.until:
            break
    print(f"campaign USD {campaign_usd(cfg):.4f} of {cfg['cap_usd']:.2f}")
    return 0


def cmd_done_local(cfg: dict, args) -> int:
    if args.name not in cfg["local_steps"]:
        raise SystemExit(f"no local step {args.name}")
    d = replica_root(cfg) / "data" / "_r1_steps"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{args.name}.json").write_text(json.dumps({"step": args.name, "done_at": now(), "note": args.note},
                                                    indent=2), encoding="utf-8")
    print(f"local step {args.name} marked done")
    return 0


# --------------------------------------------------------------------------- local steps

BLAST = "https://arbitrum-one.public.blastapi.io"
ARB1 = "https://arb1.arbitrum.io/rpc"


def rep_run(cfg: dict, *args: str, variant: str | None = None) -> None:
    """Run a script of the replica in the replica (its data/, its configuration, its ledger)."""
    env = dict(os.environ)
    if variant:
        env["CONTRACT_REP_VARIANT"] = variant
    else:
        env.pop("CONTRACT_REP_VARIANT", None)
    print("$", " ".join(args), flush=True)
    rc = subprocess.run([sys.executable, "-B", "-X", "utf8", "-W", "ignore", *args], cwd=replica_root(cfg),
                        env=env).returncode
    if rc:
        raise SystemExit(f"stopped: {args[0]} exited with {rc}")


def read_stem(stem: Path):
    sys.path.insert(0, str(HERE))
    from common import read_parts
    return read_parts(stem)


def compare_frames(old, new, name: str) -> dict:
    """Exact, order-free comparison of two tables: same columns, same rows (float columns to rtol 1e-12)."""
    import numpy as np
    import pandas as pd
    rec = {"name": name, "rows_old": int(len(old)), "rows_new": int(len(new)),
           "columns_old": list(map(str, old.columns)), "columns_new": list(map(str, new.columns))}
    if list(old.columns) != list(new.columns) or len(old) != len(new):
        rec["same"] = False
        return rec

    def norm(df):
        df = df.copy()
        for c in df.columns:
            if df[c].dtype == object:
                df[c] = df[c].map(lambda v: v.hex() if isinstance(v, (bytes, bytearray)) else v)
        floats = [c for c in df.columns if pd.api.types.is_float_dtype(df[c])]
        keys = [c for c in df.columns if c not in floats]
        return df.sort_values(keys + floats, kind="mergesort").reset_index(drop=True), floats, keys

    o, floats, keys = norm(old)
    n, _, _ = norm(new)
    diff = None
    for c in keys:
        eq = o[c].astype(str).to_numpy() == n[c].astype(str).to_numpy()
        if not eq.all():
            diff = (c, int(np.argmin(eq)))
            break
    if diff is None:
        for c in floats:
            eq = np.isclose(o[c].to_numpy(float), n[c].to_numpy(float), rtol=1e-12, atol=0.0, equal_nan=True)
            if not eq.all():
                diff = (c, int(np.argmin(eq)))
                break
    rec["same"] = diff is None
    if diff:
        c, k = diff
        rec["first_difference"] = {"column": c, "sorted_row": k, "old": str(o.iloc[k].to_dict())[:600],
                                   "new": str(n.iloc[k].to_dict())[:600]}
    return rec


def compare_stems(old_stem: Path, new_stem: Path, name: str) -> dict:
    """compare_frames on parquet parts read with pyarrow, sorted in Arrow (for tables of 10^8 rows)."""
    import glob
    import numpy as np
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.parquet as pq

    def read(stem):
        t = pa.concat_tables([pq.read_table(p) for p in sorted(glob.glob(f"{stem}.part*.parquet"))])
        for i, f in enumerate(t.schema):  # list columns (raw topics) compared as their text, since Arrow sorts no lists
            if pa.types.is_list(f.type) or pa.types.is_large_list(f.type):
                t = t.set_column(i, f.name, pa.array([None if v is None else repr(v) for v in t[f.name].to_pylist()]))
        return t

    o, n = read(old_stem), read(new_stem)
    rec = {"name": name, "rows_old": o.num_rows, "rows_new": n.num_rows, "columns_old": o.schema.names,
           "columns_new": n.schema.names}
    if o.schema.names != n.schema.names or o.num_rows != n.num_rows:
        rec["same"] = False
        return rec
    floats = [f.name for f in o.schema if pa.types.is_floating(f.type)]
    keys = [f.name for f in o.schema if f.name not in floats]
    order = [(c, "ascending") for c in keys + floats]
    o = o.take(pc.sort_indices(o, sort_keys=order))
    n = n.take(pc.sort_indices(n, sort_keys=order))
    diff = None
    for c in keys:
        eq = pc.equal(o[c], n[c]).to_numpy(zero_copy_only=False)
        nulls = (pc.is_null(o[c]).to_numpy(zero_copy_only=False) & pc.is_null(n[c]).to_numpy(zero_copy_only=False))
        eq = np.where(nulls, True, eq.astype(object)).astype(bool) if nulls.any() else eq.astype(bool)
        if not eq.all():
            diff = (c, int(np.argmin(eq)))
            break
        del eq
    if diff is None:
        for c in floats:
            a, b = o[c].to_numpy(zero_copy_only=False), n[c].to_numpy(zero_copy_only=False)
            eq = np.isclose(a.astype(float), b.astype(float), rtol=1e-12, atol=0.0, equal_nan=True)
            if not eq.all():
                diff = (c, int(np.argmin(eq)))
                break
    rec["same"] = diff is None
    if diff:
        c, k = diff
        rec["first_difference"] = {"column": c, "sorted_row": k, "old": str(o.slice(k, 1).to_pylist())[:600],
                                   "new": str(n.slice(k, 1).to_pylist())[:600]}
    return rec


def record_compare(cfg: dict, rec: dict) -> None:
    p = replica_root(cfg) / "data" / "r1_local_compare.json"
    data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    rec["compared_at"] = now()
    data[rec["name"]] = rec
    p.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    state = "SAME" if rec["same"] else "DIFFERENT " + json.dumps(rec.get("first_difference"), default=str)
    print(f"compare {rec['name']}: old {rec['rows_old']:,} new {rec['rows_new']:,} -> {state}")


def download_and_compare(cfg: dict, table: str, rel_stem: str, old_rel: str | None = None,
                         variant: str | None = None) -> dict:
    """Download a table of the new dataset into the replica (Storage Read API, not billed) and compare it with the
    earlier download of the same table, if the real repository has one."""
    rep = replica_root(cfg)
    new_stem = rep / "data" / rel_stem
    if not (new_stem.parent / f"{new_stem.name}.json").exists():
        new_stem.parent.mkdir(parents=True, exist_ok=True)
        rep_run(cfg, "scripts/download_table.py", f"{cfg['new_dataset']}.{table}", str(new_stem), variant=variant)
    old_stem = ROOT / "data" / (old_rel or rel_stem)
    if not (old_stem.parent / f"{old_stem.name}.json").exists():
        print(f"no earlier download of {table} at {old_stem}")
        return {"name": table, "same": None}
    rec = compare_stems(old_stem, new_stem, table)
    record_compare(cfg, rec)
    return rec


def load_csv(cfg: dict, table: str, csv: Path, schema: list[tuple[str, str]]) -> None:
    """A load job (not billed) of a CSV file with a header into the new dataset, replacing the table."""
    from google.cloud import bigquery
    client = bigquery.Client(project=PROJECT)
    jc = bigquery.LoadJobConfig(source_format=bigquery.SourceFormat.CSV, skip_leading_rows=1,
                                write_disposition="WRITE_TRUNCATE", ignore_unknown_values=True,
                                schema=[bigquery.SchemaField(n, t) for n, t in schema])
    with open(csv, "rb") as f:
        job = client.load_table_from_file(f, f"{PROJECT}.{cfg['new_dataset']}.{table}", job_config=jc)
    job.result()
    t = client.get_table(f"{PROJECT}.{cfg['new_dataset']}.{table}")
    print(f"loaded {table}: {t.num_rows:,} rows (load job {job.job_id}, not billed)")


def typing(cfg: dict, csv: Path, rel_stem: str, block: int, rpcs: list[str], old_rel: str | None = None,
           extra: tuple[str, ...] = (), variant: str | None = None) -> dict:
    """Account types at the earlier block (never another), compared address by address with the earlier read."""
    rep = replica_root(cfg)
    stem = rep / "data" / rel_stem
    stem.parent.mkdir(parents=True, exist_ok=True)
    rep_run(cfg, "scripts/check_account_code.py", str(csv), str(stem), "--block", str(block), "--rpc", *rpcs,
            *extra, variant=variant)
    meta = json.loads((stem.parent / f"{stem.name}.json").read_text(encoding="utf-8"))
    if int(meta.get("block_number", -1)) != block:
        raise SystemExit(f"STOP: {rel_stem} was read at block {meta.get('block_number')}, not {block}")
    cols = ["address", "code_kind", "account_class"]
    rec = compare_frames(read_stem(ROOT / "data" / (old_rel or rel_stem))[cols], read_stem(stem)[cols],
                         f"types:{rel_stem}")
    record_compare(cfg, rec)
    return rec


def step_gmx_types(cfg: dict) -> str:
    import pandas as pd
    rep = replica_root(cfg)
    rec = download_and_compare(cfg, "gmx_accounts", "1-raw-blockchain-extracts/gmx/gmx_accounts_obs")
    g = read_stem(rep / "data" / "1-raw-blockchain-extracts" / "gmx" / "gmx_accounts_obs")
    work = rep / "data" / "_work"
    work.mkdir(parents=True, exist_ok=True)
    # the rule of the earlier list data/_work/gmx_ge3.csv (closes >= 3), which gives that list from the earlier table
    ge3 = sorted(set(g.loc[g["closes"] >= 3, "account"].str.lower()))
    pd.DataFrame({"address": ge3}).to_csv(work / "gmx_ge3.csv", index=False)
    t = typing(cfg, work / "gmx_ge3.csv", "1-raw-blockchain-extracts/gmx/gmx_account_types", 513219999, [BLAST])
    types = read_stem(rep / "data" / "1-raw-blockchain-extracts" / "gmx" / "gmx_account_types")
    contracts = sorted(types.loc[types["code_kind"] == "contract", "address"])
    pd.DataFrame({"address": contracts}).to_csv(work / "gmx_contracts.csv", index=False)
    load_csv(cfg, "gmx_contract_accounts", work / "gmx_contracts.csv", [("address", "STRING")])
    return (f"gmx_accounts same={rec['same']}; {len(ge3)} accounts with >= 3 closes; types at 513219999 "
            f"same={t['same']}; {len(contracts)} contracts loaded as gmx_contract_accounts")


def rep_sql_job(cfg: dict, name: str, sql: str, label: str, expect_bytes: int = 20 * 2**20) -> None:
    """A small query that a local step of the earlier run sent with the bq CLI, sent here through the replica's
    run_bq.py so that the replica ledger bills it (the SQL file is kept in the replica's data/_r1_sql/)."""
    rep = replica_root(cfg)
    lab = f"{cfg['campaign']} local: {label}"
    if any(e.get("label") == lab and not e.get("error") for e in rep_ledger(cfg)):
        print(f"{name}: already in the replica ledger, not billed again")
        return
    f = rep / "data" / "_r1_sql" / f"{name}.sql"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(sql, encoding="utf-8")
    bad = foreign(sql, cfg["new_dataset"], cfg["public_dataset"])
    if bad:
        raise SystemExit(f"refused {name}: its SQL names {bad}")
    rep_run(cfg, "scripts/run_bq.py", str(f), "--label", lab, "--campaign",
            cfg["campaign"], "--campaign-cap", str(cfg["cap_usd"]), "--expect-bytes", str(expect_bytes))


def step_cohort(cfg: dict) -> str:
    """scripts/build_cohort.py of the registered analysis: the candidates' account types at the block of the earlier
    read, the matched cohort, and its load into BigQuery. build_cohort.py sends its CREATE TABLE with the bq CLI,
    outside the ledger; here the same rows are written and loaded, and the query goes through run_bq.py."""
    import pandas as pd
    rep = replica_root(cfg)
    sys.path.insert(0, str(HERE))
    from common import save_json, write_parts
    rec = download_and_compare(cfg, "spender_candidates", "1-raw-blockchain-extracts/cohort/spender_candidates")
    cand = read_stem(rep / "data" / "1-raw-blockchain-extracts" / "cohort" / "spender_candidates")
    work = rep / "data" / "_work"
    work.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"address": sorted(cand["spender"])}).to_csv(work / "candidates.csv", index=False)
    t = typing(cfg, work / "candidates.csv", "1-raw-blockchain-extracts/cohort/candidate_account_types", 513216506,
               [ARB1, BLAST])
    types = read_stem(rep / "data" / "1-raw-blockchain-extracts" / "cohort" / "candidate_account_types")
    # build_cohort.main(), lines 27-43, as they stand
    yml = yaml.safe_load((rep / "config" / "contract_reputation.yaml").read_text(encoding="utf-8"))
    df = cand.merge(types, left_on="spender", right_on="address", how="left")
    if int(df["code_kind"].isna().sum()):
        raise SystemExit("candidates without an account type")
    cohort = df[df["code_kind"] == "contract"].drop(columns=["address"]).rename(columns={"spender": "wallet"})
    cohort = cohort.sort_values("wallet").reset_index(drop=True)
    out = rep / "data" / "2-processed-tables-and-evaluations" / "cohort"
    write_parts(cohort, out / "matched_cohort")
    save_json({
        "rule": f"contract spenders with non-zero approvals from >= {yml['cohort']['min_owners']} distinct owners, "
                f"{yml['period']['start_ts']} to {yml['period']['observation_end']}",
        "candidates": int(len(df)),
        "by_code_kind": df["code_kind"].value_counts().to_dict(),
        "cohort": int(len(cohort)),
    }, out / "matched_cohort.json")
    c = compare_frames(read_stem(ROOT / "data" / "2-processed-tables-and-evaluations" / "cohort" / "matched_cohort"),
                       read_stem(out / "matched_cohort"), "matched_cohort")
    record_compare(cfg, c)
    cohort[["wallet"]].to_csv(work / "_cohort_upload.csv", index=False)
    load_csv(cfg, "cohort_hex", work / "_cohort_upload.csv", [("wallet", "STRING")])
    ds = f"{PROJECT}.{cfg['new_dataset']}"
    rep_sql_job(cfg, "cohort_from_hex", f"CREATE OR REPLACE TABLE `{ds}.cohort` AS "
                f"SELECT FROM_HEX(SUBSTR(wallet, 3)) AS address FROM `{ds}.cohort_hex`\n",
                "cohort to BYTES (the bq query of build_cohort.py)")
    return (f"spender_candidates same={rec['same']}; types at 513216506 same={t['same']}; matched_cohort "
            f"{len(cohort):,} same={c['same']}; loaded cohort")


def step_u_load(cfg: dict) -> str:
    """run_usd_pipeline.step_load: the selected tokens and the daily prices, the input files as they are."""
    import pandas as pd
    rep = replica_root(cfg)
    usd = rep / "data" / "0-usd-token-list-and-prices"
    lst = pd.read_csv(usd / "listed_tokens.csv")
    priced = lst[lst["selected"].astype(str).str.lower() == "true"][["address", "symbol", "name", "decimals"]]
    work = rep / "data" / "_work" / "usd"
    work.mkdir(parents=True, exist_ok=True)
    priced.to_csv(work / "u_tokens_load.csv", index=False)
    old = (ROOT / "data" / "_work" / "usd" / "u_tokens_load.csv").read_bytes()
    same = old.replace(b"\r\n", b"\n") == (work / "u_tokens_load.csv").read_bytes().replace(b"\r\n", b"\n")
    load_csv(cfg, "u_tokens_hex", work / "u_tokens_load.csv",
             [("address", "STRING"), ("symbol", "STRING"), ("name", "STRING"), ("decimals", "INTEGER")])
    load_csv(cfg, "u_prices_hex", usd / "daily_prices_usd.csv",
             [("address", "STRING"), ("day", "DATE"), ("price_usd", "FLOAT"), ("confidence", "FLOAT"),
              ("filled", "BOOLEAN"), ("filled_from", "DATE")])
    return f"{len(priced)} selected tokens (load file same as the earlier one: {same}); prices loaded"


def step_c12_typing(cfg: dict) -> str:
    """run_contract12m_pipeline steps typing and load: the queue, its account types at the pinned block with the
    smart-account probes over the overlay's public endpoints, without --fallback-latest, and the load."""
    import pyarrow as pa
    import pyarrow.parquet as pq
    rep = replica_root(cfg)
    rec = download_and_compare(cfg, "c12_rpc_queue", "1-raw-blockchain-extracts/contract-types/c12_rpc_queue",
                               variant="contract12m")
    ov = yaml.safe_load((rep / "config" / "overlay_contract12m.yaml").read_text(encoding="utf-8"))["contract_graph"]
    block = int(ov["pinned_block"])
    queue = rep / "data" / "1-raw-blockchain-extracts" / "contract-types" / "c12_rpc_queue"
    stem = rep / "data" / "1-raw-blockchain-extracts" / "contract-types" / "c12_account_types"
    rep_run(cfg, "scripts/check_account_code.py", str(queue), str(stem), "--input-parquet", "--block", str(block),
            "--probe-wallets", "--workers", "4", "--batch", "25",
            *[x for url in ov["rpc_urls"] for x in ("--rpc", str(url))], variant="contract12m")
    meta = json.loads((stem.parent / f"{stem.name}.json").read_text(encoding="utf-8"))
    if meta.get("complete") is not True or int(meta.get("block_number", -1)) != block:
        raise SystemExit(f"STOP: the account types are not complete at block {block} (resume with the same command)")
    types = read_stem(stem)
    old = read_stem(ROOT / "data" / "1-raw-blockchain-extracts" / "contract-types" / "c12_account_types")
    t = compare_frames(old, types, "types:c12_account_types")
    record_compare(cfg, t)
    from google.cloud import bigquery
    client = bigquery.Client(project=PROJECT)
    table = f"{PROJECT}.{cfg['new_dataset']}.c12_account_types"
    jc = bigquery.LoadJobConfig(source_format=bigquery.SourceFormat.PARQUET,
                                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE)
    tmp = rep / "data" / "_work" / "c12_account_types.parquet"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pandas(types, preserve_index=False), tmp)
    with tmp.open("rb") as f:
        job = client.load_table_from_file(f, table, job_config=jc, location="US")
    job.result()
    tmp.unlink()
    n = client.get_table(table).num_rows
    if n != len(types):
        raise SystemExit(f"STOP: {table} has {n} rows, not {len(types)}")
    return f"queue same={rec['same']}; {len(types):,} account types at {block} same={t['same']}; loaded ({job.job_id})"


def step_types_extra(cfg: dict) -> str:
    """The two later account-type reads of the registered analysis and the reload of gmx_contract_accounts before
    job 16 (earlier: 9 October 2026, the table modified at the time of job 16 with 43,543 rows). The rules, each of
    which gives the earlier list (data/_work/) from the earlier tables:
      holdout_extra.csv: the W0 label spenders that are not cohort candidates, read at block 513,233,527;
      w1_types_todo.csv: the W1 label spenders and the W1 GMX accounts with >= 3 closes not read before, read at
                         block 513,257,476;
      gmx_contract_accounts: the contracts of all four reads (data/_work/all_contracts.csv)."""
    import pandas as pd
    rep = replica_root(cfg)
    raw = rep / "data" / "1-raw-blockchain-extracts"
    work = rep / "data" / "_work"
    recs = [download_and_compare(cfg, t, f"1-raw-blockchain-extracts/graph-tables/{t}") for t in ("labels_w0", "labels_w1")]
    recs.append(download_and_compare(cfg, "gmx_accounts_w1", "1-raw-blockchain-extracts/gmx/gmx_accounts_w1"))
    cand = set(read_stem(raw / "cohort" / "candidate_account_types")["address"])
    gmx = set(read_stem(raw / "gmx" / "gmx_account_types")["address"])
    hold = sorted(set(read_stem(raw / "graph-tables" / "labels_w0")["wallet"]) - cand)
    pd.DataFrame({"address": hold}).to_csv(work / "holdout_extra.csv", index=False)
    t1 = typing(cfg, work / "holdout_extra.csv", "1-raw-blockchain-extracts/cohort/holdout_spender_types", 513233527,
                [BLAST])
    typed = cand | gmx | set(hold)
    w1x = set(read_stem(raw / "graph-tables" / "labels_w1")["wallet"]) - typed
    g1 = read_stem(raw / "gmx" / "gmx_accounts_w1")
    g3 = set(g1.loc[g1["closes"] >= 3, "account"].str.lower()) - typed
    todo = sorted(w1x | g3)
    pd.DataFrame({"address": todo}).to_csv(work / "w1_types_todo.csv", index=False)
    t2 = typing(cfg, work / "w1_types_todo.csv", "1-raw-blockchain-extracts/gmx/gmx_account_types_w1", 513257476,
                [BLAST])
    stems = (raw / "cohort" / "candidate_account_types", raw / "cohort" / "holdout_spender_types",
             raw / "gmx" / "gmx_account_types", raw / "gmx" / "gmx_account_types_w1")
    contracts = sorted(set().union(*[set(d.loc[d["code_kind"] == "contract", "address"])
                                     for d in (read_stem(s) for s in stems)]))
    pd.DataFrame({"address": contracts}).to_csv(work / "all_contracts.csv", index=False)
    old = set(pd.read_csv(ROOT / "data" / "_work" / "all_contracts.csv")["address"])
    same = old == set(contracts)
    record_compare(cfg, {"name": "all_contracts", "rows_old": len(old), "rows_new": len(contracts), "same": same})
    load_csv(cfg, "gmx_contract_accounts", work / "all_contracts.csv", [("address", "STRING")])
    return (f"labels and gmx_accounts_w1 same={[r['same'] for r in recs]}; holdout {len(hold):,} types same="
            f"{t1['same']}; W1 {len(todo):,} types same={t2['same']}; {len(contracts):,} contracts (same={same}) "
            "loaded as gmx_contract_accounts")


def step_reg_downloads(cfg: dict) -> str:
    """The downloads of the registered analysis (scripts/download_graph_tables.sh and the GMX closes), each compared
    with the earlier download. The query of download_graph_tables.sh that makes x_nodes goes through run_bq.py."""
    ds = f"{PROJECT}.{cfg['new_dataset']}"
    rep_sql_job(cfg, "x_nodes", f"CREATE OR REPLACE TABLE `{ds}.x_nodes` AS SELECT id, address, is_cohort FROM "
                f"`{ds}.nodes`\n", "x_nodes (the bq query of download_graph_tables.sh)", expect_bytes=2 * 2**30)
    g = "1-raw-blockchain-extracts/graph-tables"
    pairs = [("x_nodes", f"{g}/nodes")]
    for t in ("t1", "tobs"):
        pairs += [(f"x_allow_pairs_{t}", f"{g}/allow_pairs_{t}"), (f"x_transfer_pairs_{t}", f"{g}/transfer_pairs_{t}")]
    pairs += [("proxies_tobs", f"{g}/proxies_tobs"), ("labels_w0", f"{g}/labels_w0"), ("labels_w1", f"{g}/labels_w1"),
              ("x_top_token_pairs", f"{g}/top_token_pairs"),
              ("gmx_closes_obs", "1-raw-blockchain-extracts/gmx/gmx_contract_closes_obs"),
              ("gmx_closes_w1", "1-raw-blockchain-extracts/gmx/gmx_contract_closes_w1")]
    out = {t: download_and_compare(cfg, t, stem)["same"] for t, stem in pairs}
    return "registered downloads: " + ", ".join(f"{t}={v}" for t, v in out.items())


U12_DOWNLOADS = (("u12_cohort_tobs", "cohort"), ("u12_cohort_t1", "cohort_t1"), ("u12_x_nodes", "nodes"),
                 ("u12_x_allow_pairs_tobs", "allow_pairs_tobs"), ("u12_x_transfer_pairs_tobs", "transfer_pairs_tobs"),
                 ("u12_x_allow_pairs_t1", "allow_pairs_t1"), ("u12_x_transfer_pairs_t1", "transfer_pairs_t1"),
                 ("u12_proxies_tobs", "proxies_tobs"), ("u12_labels_w0", "labels_w0"), ("u12_labels_w1", "labels_w1"))


# The twelve-month tables the contract-graph evaluation reads (labels.py u12_stem, run_holdout, run_registered,
# run_robustness, run_discovery). The other six of U12_DOWNLOADS belong to the twelve-month USD analysis only, and
# no replayed job makes them.
U12_READ_BY_C12 = ("u12_cohort_tobs", "u12_cohort_t1", "u12_labels_w0", "u12_labels_w1")


def step_u12_downloads(cfg: dict) -> str:
    """The downloads of step download of run_usd12m_pipeline.py (its DOWNLOADS, copied here because that step names
    the old dataset) that the contract-graph evaluation reads, each compared with the earlier download. Not billed."""
    g = "1-raw-blockchain-extracts/graph-tables-usd-12m"
    out = {t: download_and_compare(cfg, t, f"{g}/{stem}", variant="usd12m")["same"]
           for t, stem in U12_DOWNLOADS if t in U12_READ_BY_C12}
    return "twelve-month downloads: " + ", ".join(f"{t}={v}" for t, v in out.items())


# The gate B tables of step download of run_contract12m_pipeline.py (its DOWNLOADS, copied here because its download
# names the old dataset), with their stems in graph-tables-contract-12m.
C12_DOWNLOADS = (("c12_x_nodes", "nodes"),
                 ("c12_x_allow_pairs_tobs", "allow_pairs_tobs"), ("c12_x_transfer_pairs_tobs", "transfer_pairs_tobs"),
                 ("c12_x_allow_pairs_t1", "allow_pairs_t1"), ("c12_x_transfer_pairs_t1", "transfer_pairs_t1"),
                 ("c12_x_allow_pairs_unc_tobs", "allow_pairs_uncapped_tobs"),
                 ("c12_x_allow_pairs_unc_t1", "allow_pairs_uncapped_t1"),
                 ("c12_importance_tobs", "importance_tobs"), ("c12_importance_t1", "importance_t1"),
                 ("c12_inflow_untyped_tobs", "inflow_untyped_tobs"), ("c12_inflow_untyped_t1", "inflow_untyped_t1"),
                 ("c12_proxies_tobs", "proxies_tobs"),
                 ("c12_x_label_split_w0", "label_split_w0"), ("c12_x_label_split_w1", "label_split_w1"),
                 ("c12_x_members", "members"), ("c12_describe_allowances", "describe_allowances"))
C12_GRAPH = "1-raw-blockchain-extracts/graph-tables-contract-12m"
C12_PROC = "2-processed-tables-and-evaluations/revised-contract-12m"


def json_same(cfg: dict, rel: str, name: str, ignore: tuple[str, ...] = ()) -> dict:
    """A JSON output of the replica compared with the earlier one, keys in ``ignore`` (times, hosts) left out."""
    def strip(v):
        if isinstance(v, dict):
            return {k: strip(x) for k, x in v.items() if k not in ignore}
        if isinstance(v, list):
            return [strip(x) for x in v]
        return v
    old = json.loads((ROOT / "data" / rel).read_text(encoding="utf-8"))
    new = json.loads((replica_root(cfg) / "data" / rel).read_text(encoding="utf-8"))
    d = json_diff(strip(old), strip(new))
    rec = {"name": name, "rows_old": 1, "rows_new": 1, "same": not d["differ"],
           "first_difference": d["differ"][:20] or None, "volatile": d["volatile"]}
    record_compare(cfg, rec)
    return rec


def step_c12_audit(cfg: dict) -> str:
    """run_contract12m_pipeline step audit without its job (job 43 is replayed by 'next'): the downloads of
    c12_bal_audit and c12_anchor_blocks and the balanceOf check of balance_audit.py at the T_obs block."""
    a = download_and_compare(cfg, "c12_bal_audit", f"{C12_GRAPH}/bal_audit", variant="contract12m")
    b = download_and_compare(cfg, "c12_anchor_blocks", f"{C12_GRAPH}/anchor_blocks", variant="contract12m")
    rep = replica_root(cfg)
    rep_run(cfg, "scripts/balance_audit.py", "--sample", str(rep / "data" / C12_GRAPH / "bal_audit"),
            "--anchors", str(rep / "data" / C12_GRAPH / "anchor_blocks"), variant="contract12m")
    out = json.loads((rep / "data" / C12_PROC / "typing" / "balance_audit.json").read_text(encoding="utf-8"))
    if out.get("passed") is not True:
        raise SystemExit(f"STOP: the balance check did not pass: {out}")
    c = json_same(cfg, f"{C12_PROC}/typing/balance_audit.json", "balance_audit.json",
                  ignore=("hosts", "host", "read_at", "at", "started_at", "finished_at", "seconds", "elapsed_s"))
    return (f"bal_audit same={a['same']}, anchor_blocks same={b['same']}; balance check passed "
            f"(block {out.get('block')}, {out.get('matched')}/{out.get('judged')}); json same={c['same']}")


def step_c12_structure(cfg: dict) -> str:
    """run_contract12m_pipeline step structure without its job (job 35): the download of c12_struct_t1 and the
    structure pilot (run_discovery.py --window t1 --feasibility), its report compared with the earlier one."""
    s = download_and_compare(cfg, "c12_struct_t1", f"{C12_GRAPH}/struct_t1", variant="contract12m")
    rep_run(cfg, "scripts/run_discovery.py", "--window", "t1", "--feasibility", variant="contract12m")
    c = json_same(cfg, f"{C12_PROC}/discovery/feasibility_t1.json", "feasibility_t1.json",
                  ignore=("started_at", "finished_at", "written_at", "at", "seconds", "elapsed_s", "committed",
                          "files", "git", "head", "commit"))
    return f"struct_t1 same={s['same']}; feasibility_t1.json same={c['same']}"


def step_c12_downloads(cfg: dict) -> str:
    """run_contract12m_pipeline step download: the gate B tables into graph-tables-contract-12m, each compared with
    the earlier download. Not billed."""
    out = {t: download_and_compare(cfg, t, f"{C12_GRAPH}/{stem}", variant="contract12m")["same"]
           for t, stem in C12_DOWNLOADS}
    bad = [t for t, v in out.items() if v is not True]
    if bad:
        raise SystemExit(f"STOP: downloads that differ from the earlier ones: {bad}")
    return f"{len(out)} gate B downloads, all same"


STEPS_LOCAL = {"gmx_types": step_gmx_types, "reg_downloads": step_reg_downloads, "cohort": step_cohort, "u_load": step_u_load,
               "types_extra": step_types_extra, "c12_typing": step_c12_typing, "u12_downloads": step_u12_downloads,
               "c12_audit": step_c12_audit, "c12_structure": step_c12_structure, "c12_downloads": step_c12_downloads}


def cmd_local(cfg: dict, args) -> int:
    if args.name not in STEPS_LOCAL:
        raise SystemExit(f"no local step {args.name}; known: {sorted(STEPS_LOCAL)}")
    args.note = STEPS_LOCAL[args.name](cfg)
    print(args.note)
    return cmd_done_local(cfg, args)


# --------------------------------------------------------------------------- comparison

def cmd_compare_meta(cfg: dict, args) -> int:
    from google.cloud import bigquery
    client = bigquery.Client(project=PROJECT)
    rows, _ = plan_rows(cfg)
    out = {"compared_at": now(), "tables": {}}
    for r in rows:
        for tab in r["creates"]:
            rec = {}
            for name, ds in (("old", OLD), ("new", cfg["new_dataset"])):
                try:
                    t = client.get_table(f"{PROJECT}.{ds}.{tab}")
                    rec[name] = {"rows": t.num_rows, "bytes": t.num_bytes}
                except Exception:
                    rec[name] = None
            if rec["new"] is None:
                continue
            rec["same_rows"] = bool(rec["old"]) and rec["old"]["rows"] == rec["new"]["rows"]
            out["tables"][tab] = rec
            o = rec["old"]["rows"] if rec["old"] else None
            print(f"{tab:32} old {o if o is not None else '-':>14} new {rec['new']['rows']:>14} "
                  f"{'same' if rec['same_rows'] else 'DIFFERENT'}")
    if args.scans:
        rep = replica_root(cfg)
        sql = rep / "data" / "_r1_partitions.sql"
        dest = f"{cfg['new_dataset']}.r1_partitions_compare"
        sql.write_text(
            "-- monthly partitions of the two scans, earlier and new (metadata only)\n"
            f"CREATE OR REPLACE TABLE `{PROJECT}.{dest}` AS\n"
            f"SELECT 'old' AS ds, table_name, partition_id, total_rows FROM `{PROJECT}.{OLD}.INFORMATION_SCHEMA."
            "PARTITIONS` WHERE table_name IN ('logs_obs', 'logs_w1')\nUNION ALL\n"
            f"SELECT 'new', table_name, partition_id, total_rows FROM `{PROJECT}.{cfg['new_dataset']}."
            "INFORMATION_SCHEMA.PARTITIONS` WHERE table_name IN ('logs_obs', 'logs_w1')\n", encoding="utf-8")
        cmd = [sys.executable, "-B", "-X", "utf8", "scripts/run_bq.py", str(sql), "--label",
               f"{cfg['campaign']} compare: monthly partitions of the scans (metadata)", "--campaign",
               cfg["campaign"], "--campaign-cap", str(cfg["cap_usd"]), "--expect-bytes", str(20 * 2**20)]
        if subprocess.run(cmd, cwd=rep).returncode:
            return 1
        parts: dict = {}
        for row in table_rows(cfg, "r1_partitions_compare"):
            parts.setdefault(row["table_name"], {}).setdefault(row["partition_id"], {})[row["ds"]] = row["total_rows"]
        out["partitions"] = parts
        for tab, ps in sorted(parts.items()):
            for pid, v in sorted(ps.items()):
                o, n = v.get("old"), v.get("new")
                d = "" if o == n else f"  DIFFERENT ({(n or 0) - (o or 0):+,})"
                print(f"{tab} {pid} old {o:>14,} new {n:>14,}{d}" if o is not None and n is not None
                      else f"{tab} {pid} old {o} new {n}  DIFFERENT")
    p = replica_root(cfg) / "data" / "r1_compare_meta.json"
    p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"written {p}")
    return 0


VOLATILE = re.compile(r"(^|_)(at|time|times|timing|seconds|elapsed|duration|runtime|started|ended|commit|head|"
                      r"sha256|sha|git|host|hosts|path|paths|provenance|computed|written|downloaded|read|served|"
                      r"calls|rpc|job|job_id|jobs|wall|cpu|python|platform|machine|version|built)(_|$)", re.I)


def json_diff(a, b, path: str = "", out: dict | None = None) -> dict:
    """Walk two JSON values. out: exact (count), close (numbers within rtol 1e-12), volatile (keys of run times,
    commits, hosts, paths: differences expected), and first (the first other difference)."""
    if out is None:
        out = {"equal": 0, "close": 0, "volatile": [], "differ": []}
    key = path.rsplit(".", 1)[-1]
    if VOLATILE.search(key):
        if a != b:
            out["volatile"].append(path)
        return out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            if k not in a or k not in b:
                out["differ"].append({"path": f"{path}.{k}", "old": a.get(k, "<missing>"), "new": b.get(k, "<missing>")})
            else:
                json_diff(a[k], b[k], f"{path}.{k}", out)
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out["differ"].append({"path": path, "old": f"list of {len(a)}", "new": f"list of {len(b)}"})
            return out
        for i, (x, y) in enumerate(zip(a, b)):
            json_diff(x, y, f"{path}[{i}]", out)
        return out
    if a == b:
        out["equal"] += 1
    elif (isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool)
          and math.isclose(float(a), float(b), rel_tol=1e-12, abs_tol=1e-300)):
        out["close"] += 1
    else:
        out["differ"].append({"path": path, "old": a, "new": b})
    return out


def cmd_compare_results(cfg: dict, args) -> int:
    """Compare the evaluation outputs of the replica with the earlier ones, folder by folder."""
    rep = replica_root(cfg)
    report = {"compared_at": now(), "folders": args.folders, "files": {}}
    for folder in args.folders:
        old_dir = ROOT / "data" / folder
        for f in sorted(old_dir.rglob("*")):
            if f.is_dir():
                continue
            rel = f.relative_to(ROOT / "data").as_posix()
            new = rep / "data" / rel
            if f.suffix == ".parquet":
                if ".part" in f.name and not f.name.endswith(".part000.parquet"):
                    continue
                stem = f.parent / f.name.split(".part")[0]
                if not new.exists():
                    report["files"][rel] = {"state": "missing in the replica"}
                    continue
                rec = compare_stems(stem, new.parent / f.name.split(".part")[0], rel)
                report["files"][rel] = {"state": "same" if rec["same"] else "DIFFERENT", **{
                    k: v for k, v in rec.items() if k in ("rows_old", "rows_new", "first_difference")}}
            elif f.suffix == ".json":
                if not new.exists():
                    report["files"][rel] = {"state": "missing in the replica"}
                    continue
                d = json_diff(json.loads(f.read_text(encoding="utf-8")), json.loads(new.read_text(encoding="utf-8")))
                state = "same" if not d["differ"] and not d["close"] else ("same to rtol 1e-12" if not d["differ"]
                                                                          else "DIFFERENT")
                report["files"][rel] = {"state": state, "equal": d["equal"], "close": d["close"],
                                        "volatile": d["volatile"][:20], "n_differ": len(d["differ"]),
                                        "first_differences": d["differ"][:10]}
            else:
                if not new.exists():
                    report["files"][rel] = {"state": "missing in the replica"}
                    continue
                same = f.read_bytes().replace(b"\r\n", b"\n") == new.read_bytes().replace(b"\r\n", b"\n")
                report["files"][rel] = {"state": "same bytes" if same else "DIFFERENT bytes"}
            r = report["files"][rel]
            extra = f" ({r['n_differ']} values; first {json.dumps(r['first_differences'][0], default=str)[:300]})" \
                if r.get("n_differ") else ""
            print(f"{r['state']:22} {rel}{extra}")
    out = rep / "data" / f"r1_compare_results_{args.name}.json"
    out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"written {out}")
    return 0


def cmd_manifest(cfg: dict, args) -> int:
    rep = replica_root(cfg)
    RECORD.mkdir(parents=True, exist_ok=True)
    rows, external = plan_rows(cfg)
    (RECORD / "plan.json").write_text(json.dumps({"rows": rows, "local": external}, indent=2), encoding="utf-8")
    for name in ("data/bq_ledger.json", "replica_build.json", "data/r1_compare_meta.json"):
        if (rep / name).exists():
            shutil.copy2(rep / name, RECORD / Path(name).name.replace("bq_ledger", "r1_bq_ledger"))
    steps = rep / "data" / "_r1_steps"
    if steps.exists():
        shutil.copytree(steps, RECORD / "local_steps", dirs_exist_ok=True)
    print(f"record written to {RECORD}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("plan")
    sub.add_parser("replica")
    sub.add_parser("status")
    n = sub.add_parser("next")
    n.add_argument("--only", default="")
    n.add_argument("--until", type=int, default=0)
    n.add_argument("--dry-run", action="store_true")
    n.add_argument("--rerun", action="store_true",
                   help="with --only: run those jobs again (after a local step that the first run lacked)")
    d = sub.add_parser("done-local")
    d.add_argument("name")
    d.add_argument("--note", default="")
    lo = sub.add_parser("local")
    lo.add_argument("name")
    c = sub.add_parser("compare-meta")
    c.add_argument("--scans", action="store_true")
    cr = sub.add_parser("compare-results")
    cr.add_argument("name")
    cr.add_argument("folders", nargs="+", help="folders below data/, e.g. 2-processed-tables-and-evaluations/same-window")
    sub.add_parser("manifest")
    args = ap.parse_args()
    cfg = load_cfg()
    fn = {"plan": cmd_plan, "replica": cmd_replica, "status": cmd_status, "next": cmd_next,
          "done-local": cmd_done_local, "local": cmd_local, "compare-results": cmd_compare_results, "compare-meta": cmd_compare_meta, "manifest": cmd_manifest}
    return fn[args.command](cfg, args)


if __name__ == "__main__":
    sys.exit(main())
