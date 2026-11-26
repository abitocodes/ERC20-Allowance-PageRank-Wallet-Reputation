"""Tests of scripts/reextract.py (post-clearance re-extraction, review item C-01). Free: no BigQuery, no RPC."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import reextract as rx  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def cfg():
    return rx.load_cfg()


@pytest.fixture(scope="module")
def jobs():
    return rx.old_jobs()


def test_config_keeps_the_campaign_apart(cfg):
    assert cfg["old_dataset"] == "contract_rep" and cfg["new_dataset"] == "contract_rep_r1"
    assert cfg["campaign"] == "r1:" and cfg["cap_usd"] == 50.0
    assert Path(cfg["replica"]).resolve() != ROOT.resolve()
    assert not str(Path(cfg["replica"]).resolve()).lower().startswith(str(ROOT.parents[2].resolve()).lower())


def test_selection_is_both_analyses_and_their_sources(cfg, jobs):
    sel = rx.select(cfg, jobs)
    assert set(range(1, 18)) <= set(sel)                      # the registered analysis, all 17 jobs
    c12 = {i for i, j in enumerate(jobs, 1) if j.get("variant") == "contract12m" and not j.get("error")}
    assert {63, 68, 75}.isdisjoint(sel)                       # reruns and the failed job are replaced
    assert c12 - {63, 68, 75} <= set(sel)
    assert {19, 20, 47, 48, 49, 50, 52, 53} <= set(sel)       # the u_* and u12_* tables the c12 jobs read
    assert all(rx.usable(jobs[i - 1]) for i in sel)
    assert len(sel) == 48
    assert abs(sum(jobs[i - 1]["usd"] for i in sel) - 43.92) < 0.01


def test_every_table_read_is_made_before_it_is_read(cfg):
    rows, external = rx.plan_rows(cfg)
    made = {t for s in cfg["local_steps"].values() for t in s["makes"]}
    assert set(external) == made
    for tab, first in external.items():
        step = next(s for s in cfg["local_steps"].values() if tab in s["makes"])
        assert step["before_job"] <= first


def test_no_replayed_sql_was_modified_after_its_job(cfg):
    rows, _ = rx.plan_rows(cfg)
    assert [r["job"] for r in rows if r["modified_after"]] == []


def test_job_sql_renames_and_destination(jobs):
    j = jobs[48]  # job 49: usd12m pairs at tobs, with renames
    sql = rx.job_sql(j, ROOT, "contract_rep")
    assert "u12_allow_pairs_tobs" in sql and "`dissertation-bq.contract_rep.u_allow_pairs_tobs`" not in sql
    scan = rx.job_sql(jobs[0], ROOT, "contract_rep_r1")
    assert "CREATE TABLE `dissertation-bq.contract_rep_r1.logs_obs`" in scan


def test_foreign_names_are_refused():
    pub = "bigquery-public-data.goog_blockchain_arbitrum_one_us"
    ok = "SELECT * FROM `dissertation-bq.contract_rep_r1.x` JOIN `bigquery-public-data.goog_blockchain_arbitrum_one_us.logs`"
    assert rx.foreign(ok, "contract_rep_r1", pub) == []
    assert rx.foreign("SELECT * FROM `dissertation-bq.contract_rep.x`", "contract_rep_r1", pub)
    assert rx.foreign("SELECT * FROM `other-proj.ds.t`", "contract_rep_r1", pub) == ["`other-proj.ds.t`"]
    assert rx.foreign("-- contract_rep.x in a comment\nSELECT 1", "contract_rep_r1", pub) == []


def test_dataset_rewrite_touches_only_full_names():
    text = "`dissertation-bq.contract_rep.logs_obs` and `dissertation-bq.contract_rep_r1.x` and contract_reputation"
    out, n = rx.rewrite_dataset(text, "contract_rep_r1")
    assert n == 1
    assert out.count("contract_rep_r1.") == 2 and "contract_reputation" in out


def test_every_sql_file_is_renamed_completely():
    for f in sorted((ROOT / "sql").glob("*.sql")):
        out, _ = rx.rewrite_dataset(f.read_text(encoding="utf-8"), "contract_rep_r1")
        assert not rx.foreign(out, "contract_rep_r1", "bigquery-public-data.goog_blockchain_arbitrum_one_us"), f.name


def test_labels_carry_the_campaign_and_the_job(cfg, jobs):
    lab = rx.label_of(cfg, 12, jobs[11])
    assert lab.startswith("r1: job 12: ") and "scan B" in lab


def test_nothing_writes_the_earlier_ledger():
    src = (ROOT / "scripts" / "reextract.py").read_text(encoding="utf-8")
    assert "bq_ledger.json\").write" not in src and "LEDGER.write" not in src


def test_json_diff_sorts_values():
    a = {"tau": 0.5, "n": 3, "elapsed_seconds": 10, "ci": [0.1, 0.2], "x": 1.0}
    b = {"tau": 0.5, "n": 3, "elapsed_seconds": 12, "ci": [0.1, 0.2 + 1e-17], "x": 1.1}
    d = rx.json_diff(a, b)
    assert d["volatile"] == [".elapsed_seconds"]
    assert [x["path"] for x in d["differ"]] == [".x"]
    assert d["equal"] >= 3
