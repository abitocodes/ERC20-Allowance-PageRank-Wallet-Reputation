"""The twelve-month variant (docs/revision_one_year_window.md): paths, overlay, frozen files, the jobs
of scripts/run_usd12m_pipeline.py and the checks of scripts/run_bq.py."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import textwrap

import pytest

from conftest import EXPERIMENTS, SCRIPTS

BASE = "fab8d63"  # master when the twelve-month variant was added
FROZEN = ["docs/analysis_plan.md", "docs/registration_w1.md", "docs/revision_price_weighting.md",
          "config/contract_reputation.yaml",
          *sorted(f"sql/{p.name}" for p in (EXPERIMENTS / "sql").glob("*.sql") if re.match(r"(0\d|1\d)_", p.name))]


def run_py(code: str, variant: str | None, cwd=SCRIPTS) -> subprocess.CompletedProcess:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
    env.pop("CONTRACT_REP_VARIANT", None)
    if variant:
        env["CONTRACT_REP_VARIANT"] = variant
    return subprocess.run([sys.executable, "-c", textwrap.dedent(code)], cwd=cwd, env=env, capture_output=True,
                          text=True, encoding="utf-8")


def test_usd12m_paths_are_its_own():
    out = run_py("""
        import common
        print(common.GRAPH.name, common.PROC.name, common.PUB.name, common.USD_CONSTANTS.parent.name,
              common.BQ_PREFIX, common.REVISED, common.ONE_YEAR, common.W1_DIR)
    """, "usd12m")
    assert out.returncode == 0, out.stderr
    assert out.stdout.split() == ["graph-tables-usd-12m", "revised-usd-12m", "revised-usd-12m", "usd-12m", "u12_",
                                  "True", "True", "window-w1"]


@pytest.mark.parametrize("variant,start,w0_start", [
    (None, "2023-10-01 00:00:00 UTC", None),
    ("usd", "2023-10-01 00:00:00 UTC", None),
    ("usd12m", "2025-07-01 00:00:00 UTC", "2025-04-01 00:00:00 UTC"),
])
def test_overlay_applies_only_to_usd12m(variant, start, w0_start):
    out = run_py("""
        import json, common
        cfg = common.load_config()
        print(json.dumps([cfg["period"]["start_ts"], cfg["holdout"].get("start_ts")]))
    """, variant)
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == f'["{start}", ' + (f'"{w0_start}"' if w0_start else "null") + "]"


def test_overlay_with_another_key_is_refused(tmp_path):
    bad = tmp_path / "overlay.yaml"
    bad.write_text('period:\n  start_ts: "2025-07-01 00:00:00 UTC"\n  end_ts: "2026-01-01 00:00:00 UTC"\n',
                   encoding="utf-8")
    out = run_py(f"""
        import pathlib, common
        common.OVERLAY_PATH = pathlib.Path(r"{bad}")
        common.load_config()
    """, "usd12m")
    assert out.returncode != 0


def _blob(rev: str, rel: str) -> bytes | None:
    out = subprocess.run(["git", "show", f"{rev}:./{rel}"], cwd=EXPERIMENTS, capture_output=True)
    return out.stdout if out.returncode == 0 else None


def test_frozen_files_are_unchanged():
    if _blob(BASE, "docs/analysis_plan.md") is None:
        pytest.skip(f"commit {BASE} is not available")
    assert len(FROZEN) == 4 + 19
    for rel in FROZEN:
        old = _blob(BASE, rel)
        assert old is not None, rel
        assert (EXPERIMENTS / rel).read_bytes().replace(b"\r\n", b"\n") == old.replace(b"\r\n", b"\n"), rel


PROBE = """
    import json, re, sys
    import run_usd12m_pipeline as d
    import run_bq
    from common import load_config
    cfg = load_config()
    project, dataset = cfg["bigquery"]["project_id"], cfg["bigquery"]["dataset"]
    ds = rf"`{re.escape(project)}\\.{re.escape(dataset)}\\.(\\w+)`"
    strip = lambda s: re.sub(r"--[^\\n]*", "", s)
    made, out = set(), {}
    for step in ("tokens", "cohorts", "constants", "pairs", "rest", "checks"):
        for job in d.jobs(cfg)[step]:
            sql = (d.ROOT / "sql" / job.sql).read_text(encoding="utf-8")
            for k, v in job.subs.items():
                sql = sql.replace(f"__{k}__", v)
            sql = run_bq.apply_renames(sql, [f"{a}={b}" for a, b in job.renames.items()], project, dataset)
            run_bq.check_tables(sql, project, dataset, d.PREFIX, list(job.allow))
            body = strip(sql)
            left = re.findall(r"__[A-Z][A-Z0-9_]*__", body)
            assert not left, (job.key, left)
            used = set(re.findall(r"@(\\w+)", body))
            assert used == set(job.params), (job.key, used ^ set(job.params))
            created = set(re.findall(rf"CREATE\\s+(?:OR\\s+REPLACE\\s+)?(?:TABLE|VIEW)\\s+{ds}", sql, flags=re.I))
            read = set(re.findall(ds, sql)) - created
            early = sorted(t for t in read if t.startswith("u12_") and t not in made)
            assert not early, (job.key, early)
            made |= created
            out[job.key] = {"start": job.params.get("start_ts"), "reads": sorted(read), "creates": sorted(created)}
    print(json.dumps(out))
"""


def test_jobs_create_only_u12_tables_and_read_what_they_may():
    out = run_py(PROBE, "usd12m")
    assert out.returncode == 0, out.stderr
    import json
    jobs = json.loads(out.stdout)
    assert set(jobs) == {"tokens", "cohorts", "constants", "pairs_tobs", "pairs_t1", "proxies", "labels_w0",
                         "labels_w1", "node_ids", "describe", "checks"}
    for key, j in jobs.items():
        assert all(t.startswith("u12_") for t in j["creates"]), key
    tobs, t1 = "2025-07-01 00:00:00 UTC", "2025-04-01 00:00:00 UTC"
    for key in ("tokens", "pairs_tobs", "proxies", "labels_w1"):
        assert jobs[key]["start"] == tobs, key
    for key in ("constants", "pairs_t1", "labels_w0"):
        assert jobs[key]["start"] == t1, key
    # the W0 jobs read the t1 views, the T_obs and W1 jobs the T_obs and W1 views
    assert {"u12_approvals_t1", "u12_transfers_t1"} <= set(jobs["constants"]["reads"])
    assert "u12_transfers_tobs" not in jobs["labels_w0"]["reads"]
    assert {"u12_approvals_w1", "u12_transfers_w1", "u12_transfers_tobs"} <= set(jobs["labels_w1"]["reads"])


def test_only_the_cohorts_job_reads_the_33_month_event_tables():
    out = run_py(PROBE, "usd12m")
    import json
    jobs = json.loads(out.stdout)
    for key, j in jobs.items():
        if key != "cohorts":
            assert not {"u_approvals", "u_transfers", "u_approvals_w1", "u_transfers_w1"} & set(j["reads"]), key


def test_estimates_cover_every_job():
    if not (EXPERIMENTS / "data" / "bq_ledger.json").exists():
        pytest.skip("no ledger")
    out = run_py("""
        import json
        import run_usd12m_pipeline as d
        from common import load_config
        cfg = load_config()
        src = d.Sources({name: 1_000_000 for name in d.META_TABLES})
        est = d.estimates(src, cfg, d.calibration())
        keys = sorted(j.key for jobs in d.jobs(cfg).values() for j in jobs)
        print(json.dumps({"est": est, "keys": keys, "months": d.month_list(d.WINDOWS["tobs_start"], d.WINDOWS["tobs_end"])}))
    """, "usd12m")
    assert out.returncode == 0, out.stderr
    import json
    r = json.loads(out.stdout)
    assert sorted(r["est"]) == r["keys"]
    for key, (first, whole) in r["est"].items():
        assert 0 < first <= whole, key
    assert r["months"] == [f"2025-{m:02d}" for m in range(7, 13)] + [f"2026-{m:02d}" for m in range(1, 7)]


def test_run_usd_pipeline_refuses_the_other_variants():
    for variant in ("usd12m", "registered"):
        out = subprocess.run([sys.executable, "scripts/run_usd_pipeline.py", "load", "--dry-run"], cwd=EXPERIMENTS,
                             env={**os.environ, "CONTRACT_REP_VARIANT": variant, "PYTHONDONTWRITEBYTECODE": "1"},
                             capture_output=True, text=True)
        assert out.returncode != 0 and "run_usd_pipeline.py belongs to" in out.stderr, variant


def test_driver_refuses_the_other_variants():
    for variant in ("usd", "registered"):
        out = run_py("import run_usd12m_pipeline", variant)
        assert out.returncode != 0 and "twelve-month variant" in out.stderr, variant


def test_driver_refuses_uncommitted_inputs():
    out = run_py("""
        import run_usd12m_pipeline as d
        d.git = lambda *a: " M docs/revision_one_year_window.md" if a[0] == "status" else "abc"
        try:
            d.inputs(False)
        except SystemExit as e:
            print("refused" if str(e).startswith("refused") else "other")
    """, "usd12m")
    assert out.stdout.strip() == "refused", out.stderr


def test_check_tables_refuses_writes_and_reads_outside_the_prefix():
    import run_bq
    p, d = "dissertation-bq", "contract_rep"

    def t(name):
        return f"`{p}.{d}.{name}`"

    ok = f"CREATE OR REPLACE TABLE {t('u12_a')} AS SELECT * FROM {t('u12_b')} JOIN {t('u_prices')} USING (x)"
    run_bq.check_tables(ok, p, d, "u12_", ["u_prices"])
    run_bq.check_tables("-- DELETE and DROP in a comment\n" + ok, p, d, "u12_", ["u_prices"])
    for bad in (f"CREATE TABLE {t('u_a')} AS SELECT 1",
                f"CREATE TABLE {t('u12_a')} AS SELECT * FROM {t('u_transfers')}",
                f"INSERT INTO {t('u12_a')} SELECT 1",
                f"CREATE TABLE {t('u12_a')} AS SELECT * FROM `other-project.other.x`"):
        with pytest.raises(SystemExit):
            run_bq.check_tables(bad, p, d, "u12_", ["u_prices"])


def test_renames_replace_whole_table_names_only():
    import run_bq
    sql = "SELECT * FROM `p.d.u_transfers` JOIN `p.d.u_transfers_w1` USING (x)"
    out = run_bq.apply_renames(sql, ["u_transfers=u12_transfers_tobs"], "p", "d")
    assert "`p.d.u12_transfers_tobs`" in out and "`p.d.u_transfers_w1`" in out
    with pytest.raises(SystemExit):
        run_bq.apply_renames(sql, ["u_nothing=u12_x"], "p", "d")


def test_export_latex_writes_the_decay_figure_for_usd12m(tmp_path):
    env = {**os.environ, "CONTRACT_REP_VARIANT": "usd12m", "PYTHONDONTWRITEBYTECODE": "1"}
    out = subprocess.run([sys.executable, "scripts/export_latex.py", "--tables-dir", str(tmp_path / "t"),
                          "--figures-dir", str(tmp_path / "f")], cwd=EXPERIMENTS, env=env, capture_output=True,
                         text=True)
    assert out.returncode == 0, out.stdout + out.stderr
    assert (tmp_path / "f" / "logistic-decay.pdf").exists()
