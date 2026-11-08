"""The contract-graph variant as a whole (CONTRACT_REP_VARIANT=contract12m, docs/revision_contract_graph.md and
docs/discovery_protocol.md), beside the variants before it.

- the paths, the configuration and the run_bq.py budget of every variant, and the earlier variants against the
  scripts/common.py of the commit before this revision;
- the overlay check, the public views that run_bq.check_tables lets through, the table names and writes it
  refuses (and the jobs of the twelve-month driver it still accepts), and the frozen files;
- the gate A pieces fed into one another: the driver's typing command parsed and run by
  scripts/check_account_code.py, its output checked against the queue by the driver and read by the structure
  pilot of scripts/run_discovery.py, the pilot's edge counts against the driver's, the shared paths, and the
  free check step on fake metadata, also with every gate A job run and the projection of gate B complete;
- at gate B: the earlier variants keep the outputs and the code path of the gate A commit d39775c (their six
  evaluation scripts on a synthetic world under the code of d39775c and of this tree, the shared modules, the
  statements they execute, the tracked outputs and the ledger), the gate A files that gate B must not change, the
  .gitattributes that keeps the pinned files of this variant byte for byte, and the committed gate B state
  ('Protocol fixed', the dated amendment of revision section 13 and the pilot it pins; these tests carry
  gate_b_state in their names and fail until the gate B documents are written).

Nothing here reaches the network or BigQuery: the code of a variant runs in a subprocess (scripts/common.py
reads the variant once, at import), the RPC is a fake behind requests.Session.post, and the BigQuery client is
a fake that stops before any job. History is read with git show, ls-tree and cat-file only, and attributes with
git check-attr; the scripts that the gate B tests run work on sandbox copies (tests/c12_world.py), and nothing is
written outside pytest's tmp folders."""

from __future__ import annotations

import copy
import difflib
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import textwrap
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pytest
import yaml

import c12_world as w
from conftest import CONFIG_PATH, EXPERIMENTS, SCRIPTS, gate_b_amendment_files, slow

VARIANTS = ("registered", "usd", "usd12m", "contract12m")
OVERLAYS = {"usd12m": EXPERIMENTS / "config" / "overlay_usd12m.yaml",
            "contract12m": EXPERIMENTS / "config" / "overlay_contract12m.yaml"}
BASE = "69c7d12"  # the last commit of scripts/common.py and scripts/run_bq.py before this revision
BASE_B = w.GATE_A  # the gate A commit of this revision (d39775c): the earlier variants keep its common.py names
RAW = "data/1-raw-blockchain-extracts"
PROC, PUB, USD = "data/2-processed-tables-and-evaluations", "data/3-published-results-for-thesis", \
    "data/0-usd-token-list-and-prices"
PUBLIC = "bigquery-public-data.goog_blockchain_arbitrum_one_us"

# SHA-256 of the committed versions (git show HEAD:<path> with CRLF read as LF, HEAD 9e21743 of 7 November 2026):
# the earlier analyses' plan, registration, revisions, configuration, SQL and drivers, which this revision must
# not change (docs/revision_contract_graph.md, introduction).
FROZEN = {
    "docs/analysis_plan.md": "b5fb36456c924edf2af0f1b2e3f95a30c033ff2105221bcd9c74e1b52e5ba46c",
    "docs/registration_w1.md": "34cd6dfeb56b8fb8a553cb24afbff06c6a94e6f69a2eb7f7d642b0cc39e54b2c",
    "docs/revision_price_weighting.md": "80cae0735ae97bfb743dbac98a39e2f35f41bf3621a340db8ed01385f70febc6",
    "docs/revision_one_year_window.md": "4fb88ebf46f261ad4ad63404183ecc6fd0be453531e43a731f21464a4afdfe35",
    "config/contract_reputation.yaml": "2ea235021241fa408f8776d55c2b594d34ced0ca1dad44e16f22775c5db8297f",
    "config/overlay_usd12m.yaml": "ac4f284c3961128e1fff762211d1fbbd8eb37df9d4480c788ac01cff6c829889",
    "sql/01_materialize_logs.sql": "6b9b86157802b377987913a2ae064c70044a7f6ed00a2a023930936908ee41c2",
    "sql/02_spender_candidates.sql": "28263f11e99bd0641f72d8248237add28f48e575855aed23cbe05f2af1c9961c",
    "sql/03_ego_events.sql": "e5a5bf2c4424ae56021bcd10d8915a46f78f955e9a290b4e16e91230a8db705c",
    "sql/04_anchor_pairs.sql": "68f01fb7b741564b60ed0cb5679bf501a837aeb31bcbf839d386ba568a12fc7e",
    "sql/05_proxies_same_window.sql": "3938ee029304b8ed72ebffce3bc3b62b0b4bedda98f1d3b976974f89cf92f48a",
    "sql/06_holdout_labels.sql": "10886006cf6bcd76d93ed3c9384b5ff734465e64009d24b3410aae849f4be9ab",
    "sql/07_gmx_accounts.sql": "afaace7d6e374f5dcebd4ade5ea7cfe258de1fcfe55b57190a8c2899a48a9011",
    "sql/08_export_ids.sql": "2405bd5b3753c9b0b9df2a3d55bf44b14caafb5833aa931cbd6c78d4d6f6916f",
    "sql/09_gmx_contract_closes.sql": "642bffefaea6747932f2ddf43fc5c1b7ef491c2c1a3f989788868165ef9787aa",
    "sql/10_describe.sql": "9ad16fb8157a5801c6723efee48bb4f1060504ad8da6628a7f05005d17888e4d",
    "sql/11_top_tokens.sql": "451515c019b2ee54c8681fe9edfc66c1d2c43c65325527d6f8da0636c20b9673",
    "sql/12_usd_ego.sql": "46a53b912ccf5b748ef026743f52e773ef903a7760529fefd3389811eeb7bdd1",
    "sql/13_usd_constants.sql": "97a1c515bc08f92144ad2663e73f464f7f29d01b6016a989fc93148428b71641",
    "sql/14_usd_anchor_pairs.sql": "a30a11a3cce49e1714f74fd9cd194c05278566a23e9ab568921c34f71302b66e",
    "sql/15_usd_proxies.sql": "2a595ce5d48c3fe39a45d21bea8dcac211a3d518ad2c090926374407459cda0f",
    "sql/16_usd_labels.sql": "3dcdab4b6a91835d8f50f373760868090f6d0e3d1977cfd7cfe8cec00d4fb20d",
    "sql/17_usd_export_ids.sql": "62d388f145f0c9f176fb39c426d05c26c91f565d9080d2f2321b7d16c5f55d23",
    "sql/18_usd_describe.sql": "1eec0acb8db26e64f5762f63cd88f3423339cb5e1ca0c04ca3b93c4ec0e7a73f",
    "sql/19_usd_load.sql": "28638530329150a331e7f00114e958116bbf6f0b1147b24e1bfdae5485e2d798",
    "sql/20_usd12m_token_rows.sql": "ea30aeee8e5fe6142bd0022ac066ddf7592c229e4e3f6dda9ee1acf31bc90062",
    "sql/21_usd12m_cohorts.sql": "12cc7797e5d9b862771f9eac6d441623062f67ea2bd3b9220178b5c94b981f12",
    "sql/22_usd12m_describe.sql": "6022a31d3c2ed51703200c2331fd1d03651bf72a096cb91ba9b33102fa7a0c6d",
    "sql/23_usd12m_checks.sql": "99debd4bfa00e2077cfc904a8fd94547ca0d80069ae29b03084b8cde10d7bf18",
    "scripts/run_usd12m_pipeline.py": "ab65bd86d57101570fe3dfdd2b77b6b5a46cb78b5d893d808973f29f0df92754",
    "scripts/run_usd_pipeline.py": "9cc7ad122d1ca2bef69e2f45e2c0b58e89351c381336a22e4cd7f3e792f2f7f5",
}


def run_py(code: str, variant: str | None, *args: str) -> subprocess.CompletedProcess:
    """``code`` in a fresh interpreter under ``variant`` (None or 'registered': unset), from scripts/."""
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
    env.pop("CONTRACT_REP_VARIANT", None)
    env.pop("CONTRACT_REP_RPC_URL", None)
    if variant and variant != "registered":
        env["CONTRACT_REP_VARIANT"] = variant
    return subprocess.run([sys.executable, "-c", textwrap.dedent(code), *args], cwd=SCRIPTS, env=env,
                          capture_output=True, text=True, encoding="utf-8")


def last_json(out: subprocess.CompletedProcess):
    assert out.returncode == 0, out.stdout[-2000:] + out.stderr[-4000:]
    return json.loads(out.stdout.strip().splitlines()[-1])


def merged(variant: str) -> dict:
    """The configuration a variant should get: the base file, with the variant's overlay merged by section."""
    cfg = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    if variant in OVERLAYS:
        for section, values in yaml.safe_load(OVERLAYS[variant].read_text(encoding="utf-8")).items():
            cfg.setdefault(section, {}).update(values)
    return json.loads(json.dumps(cfg))


def _blob(rev: str, rel: str) -> bytes | None:
    out = subprocess.run(["git", "show", f"{rev}:./{rel}"], cwd=EXPERIMENTS, capture_output=True)
    return out.stdout if out.returncode == 0 else None


# --------------------------------------------------------------------------- paths, configuration and budget


# Per variant: the paths of scripts/common.py, its flags and config, and run_bq.py's settings and its main()
# on a ledger of USD 45 with a job expected to bill USD 10 (refused under a budget of 50, not under 60). The
# BigQuery client is a fake installed before run_bq is imported: its dry run answers, and the job after it
# raises, so nothing is billed and the ledger is not written. For an earlier variant, given the commit BASE,
# also the names and the configuration of the scripts/common.py of that commit against the current one.
VARIANT_PROBE = r"""
    import json, subprocess, sys, types
    from pathlib import Path

    class WouldRun(Exception):
        pass

    def fake_bigquery():
        m = types.ModuleType("google.cloud.bigquery")

        class QueryJobConfig:
            def __init__(self, dry_run=False, **kwargs):
                self.dry_run = dry_run

        class ScalarQueryParameter:
            def __init__(self, name, kind, value):
                self.name, self.value = name, value

        class Client:
            def __init__(self, project=None):
                pass

            def query(self, sql, job_config=None):
                if not job_config.dry_run:
                    raise WouldRun()
                return types.SimpleNamespace(total_bytes_processed=1000)

        m.QueryJobConfig, m.ScalarQueryParameter, m.Client = QueryJobConfig, ScalarQueryParameter, Client
        return m

    import google.cloud
    sys.modules["google.cloud.bigquery"] = google.cloud.bigquery = fake_bigquery()
    import common
    import run_bq

    tmp, base_rev, base_b = Path(sys.argv[1]), *(None if a == "-" else a for a in sys.argv[2:4])
    rel = lambda p: None if p is None else p.relative_to(common.ROOT).as_posix()
    paths = {n: rel(getattr(common, n)) for n in ("GRAPH", "PROC", "PUB", "USD_CONSTANTS", "TYPES_DIR", "TYPES",
                                                  "GRAPH_U12", "OVERLAY_PATH")}
    flags = {n: getattr(common, n) for n in ("VARIANT", "BQ_PREFIX", "W1_DIR", "REVISED", "ONE_YEAR",
                                             "CONTRACT_GRAPH", "TRADERS")}
    run_bq.LEDGER = tmp / "bq_ledger.json"
    run_bq.LEDGER.write_text(json.dumps({"usd_per_tib": 6.25, "jobs": [{"usd": 45.0, "label": "earlier"}]}),
                             encoding="utf-8")
    (tmp / "q.sql").write_text("SELECT 1", encoding="utf-8")
    sys.argv = ["run_bq.py", str(tmp / "q.sql"), "--expect-bytes", str(int(10 / run_bq.USD_PER_TIB * 2**40))]
    try:
        outcome = "refused" if run_bq.main() == 2 else "other"
    except WouldRun:
        outcome = "would run"
    jobs = len(json.loads(run_bq.LEDGER.read_text(encoding="utf-8"))["jobs"])

    def against(rev, names):
        src = subprocess.run(["git", "show", rev + ":./scripts/common.py"], cwd=common.ROOT,
                             capture_output=True, check=True).stdout
        base = types.ModuleType("common_base")
        base.__file__ = common.__file__  # the same ROOT
        exec(compile(src, common.__file__, "exec"), base.__dict__)
        return {"differ": [n for n in names if getattr(base, n) != getattr(common, n)],
                "same_config": base.load_config() == common.load_config()}

    names = ("VARIANT", "CONFIG_PATH", "DATA", "RAW", "PROC_SHARED", "USD_INPUTS", "GRAPH", "PROC", "PUB",
             "USD_CONSTANTS", "BQ_PREFIX", "W1_DIR", "REVISED", "ONE_YEAR")
    earlier = common.VARIANT != "contract12m"
    before = against(base_rev, names) if base_rev and earlier else None
    # the gate A commit of this revision: its common.py gives the earlier variants the same names and configuration
    names_b = (*names, "CONTRACT_GRAPH", "TRADERS", "TYPES_DIR", "TYPES", "GRAPH_U12", "OVERLAY_PATH", "OVERLAY_KEYS")
    before_b = against(base_b, names_b) if base_b and earlier else None
    print(json.dumps({"paths": paths, "flags": flags, "config": common.load_config(),
                      "settings": list(run_bq.settings()), "outcome": outcome, "ledger_jobs": jobs,
                      "before": before, "before_b": before_b}))
"""


@pytest.fixture(scope="module")
def probes(tmp_path_factory) -> dict[str, dict]:
    base = [rev if _blob(rev, "scripts/common.py") is not None else "-" for rev in (BASE, BASE_B)]
    out = {}
    for variant in VARIANTS:
        r = run_py(VARIANT_PROBE, variant, str(tmp_path_factory.mktemp(variant)), *base)
        out[variant] = {**last_json(r), "stdout": r.stdout}
    return out


def _paths(graph: str, folder: str | None, constants: str, overlay: str | None) -> dict:
    return {"GRAPH": f"{RAW}/{graph}", "PROC": f"{PROC}/{folder}" if folder else PROC,
            "PUB": f"{PUB}/{folder}" if folder else PUB, "USD_CONSTANTS": f"{USD}/{constants}",
            "TYPES_DIR": f"{RAW}/contract-types", "TYPES": f"{RAW}/contract-types/c12_account_types",
            "GRAPH_U12": f"{RAW}/graph-tables-usd-12m", "OVERLAY_PATH": overlay}


EXPECTED = {
    "registered": (_paths("graph-tables", None, "constants.json", None),
                   ["registered", "u_", "registered-w1", False, False, False, True]),
    "usd": (_paths("graph-tables-usd", "revised-usd", "constants.json", None),
            ["usd", "u_", "window-w1", True, False, False, True]),
    "usd12m": (_paths("graph-tables-usd-12m", "revised-usd-12m", "usd-12m/constants.json",
                      "config/overlay_usd12m.yaml"),
               ["usd12m", "u12_", "window-w1", True, True, False, True]),
    "contract12m": (_paths("graph-tables-contract-12m", "revised-contract-12m", "contract-12m/constants.json",
                           "config/overlay_contract12m.yaml"),
                    ["contract12m", "c12_", "window-w1", True, True, True, False]),
}


@pytest.mark.parametrize("variant", VARIANTS)
def test_paths_and_flags_of_each_variant(probes, variant):
    paths, flags = EXPECTED[variant]
    assert probes[variant]["paths"] == paths
    assert list(probes[variant]["flags"].values()) == flags


@pytest.mark.parametrize("variant", VARIANTS)
def test_load_config_of_each_variant(probes, variant):
    cfg = probes[variant]["config"]
    assert cfg == merged(variant)
    assert cfg["bigquery"]["budget_usd"] == (60 if variant == "contract12m" else 50)
    assert ("contract_graph" in cfg, "discovery" in cfg) == ((variant == "contract12m",) * 2)
    if variant in ("registered", "usd"):
        assert cfg == json.loads(json.dumps(yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))))
    if variant != "registered":
        # every overlay keeps the base file's other settings
        base = merged("registered")
        assert cfg["bigquery"]["project_id"] == base["bigquery"]["project_id"]
        assert cfg["reputation"] == base["reputation"] and cfg["period"]["end_ts"] == base["period"]["end_ts"]


@pytest.mark.parametrize("variant", VARIANTS)
def test_run_bq_budget_follows_the_variant(probes, variant):
    budget = 60.0 if variant == "contract12m" else 50.0
    p = probes[variant]
    assert p["settings"] == ["dissertation-bq", "contract_rep", budget]
    # main() reads the same budget: with USD 45 in the ledger a job of USD 10 passes 50 but not 60
    assert f"ledger so far USD 45.00 of {budget:.0f}" in p["stdout"]
    assert p["outcome"] == ("would run" if variant == "contract12m" else "refused")
    assert p["ledger_jobs"] == 1


@pytest.mark.parametrize("variant", ["registered", "usd", "usd12m"])
def test_earlier_variants_behave_as_before_this_revision(probes, variant):
    if probes[variant]["before"] is None:
        pytest.skip(f"commit {BASE} is not available")
    assert probes[variant]["before"] == {"differ": [], "same_config": True}
    assert probes["contract12m"]["before"] is None


def test_an_unknown_variant_is_refused():
    out = run_py("import common", "contract")
    assert out.returncode != 0 and "must be one of" in out.stderr


OVERLAY_PROBE = r"""
    import json, sys
    from pathlib import Path
    import common

    out = []
    for path in sys.argv[1:]:
        common.OVERLAY_PATH = Path(path)
        try:
            common.load_config()
            out.append("accepted")
        except SystemExit as e:
            out.append("refused" if "must set exactly" in str(e) else str(e))
    print(json.dumps(out))
"""


def _overlay_cases(variant: str, tmp_path, changes: dict) -> list[str]:
    """The real overlay, then one changed copy per entry of ``changes`` (name -> function on the overlay)."""
    paths = [str(OVERLAYS[variant])]
    for name, change in changes.items():
        overlay = yaml.safe_load(OVERLAYS[variant].read_text(encoding="utf-8"))
        change(overlay)
        path = tmp_path / f"{variant}_{name}.yaml"
        path.write_text(yaml.safe_dump(overlay), encoding="utf-8")
        paths.append(str(path))
    return paths


def test_an_overlay_with_an_extra_or_a_missing_key_is_refused(tmp_path):
    changes = {
        "extra_key": lambda o: o["discovery"].update(extra=1),
        "extra_base_key": lambda o: o["bigquery"].update(dataset="other"),
        "extra_section": lambda o: o.update(reputation={"damping": 0.9}),
        "missing_key": lambda o: o["discovery"].pop("min_hot"),
        "missing_nested": lambda o: o["contract_graph"].pop("balance"),
        "missing_section": lambda o: o.pop("holdout"),
    }
    assert last_json(run_py(OVERLAY_PROBE, "contract12m", *_overlay_cases("contract12m", tmp_path, changes))) == \
        ["accepted"] + ["refused"] * len(changes)
    changes = {
        "budget": lambda o: o.update(bigquery={"budget_usd": 60}),  # only the contract-graph overlay raises it
        "missing_key": lambda o: o.pop("holdout"),
        "contract_graph": lambda o: o.update(contract_graph={"pinned_block": 1}),
    }
    assert last_json(run_py(OVERLAY_PROBE, "usd12m", *_overlay_cases("usd12m", tmp_path, changes))) == \
        ["accepted"] + ["refused"] * len(changes)


# --------------------------------------------------------------------------- run_bq checks and frozen files


def test_check_tables_lets_through_exactly_the_listed_public_views():
    import run_bq

    p, d = "dissertation-bq", "contract_rep"
    tx, blocks, logs = f"{PUBLIC}.transactions", f"{PUBLIC}.blocks", f"{PUBLIC}.logs"
    sql = (f"CREATE OR REPLACE TABLE `{p}.{d}.c12_x` AS SELECT * FROM `{tx}` JOIN `{blocks}` USING (block_number) "
           f"JOIN `{p}.{d}.c12_y` USING (block_number)")
    run_bq.check_tables(sql, p, d, "c12_", [], [tx, blocks])
    run_bq.check_tables(sql, p, d, "c12_", [], (blocks, tx, logs))  # a listed view the file does not read is fine
    for allowed in ([], [tx], [blocks], [f"{PUBLIC}.transaction", blocks], [f"{PUBLIC}.transactions_v2", blocks],
                    [PUBLIC, blocks], [f"bigquery-public-data.crypto_ethereum.transactions", blocks],
                    [tx.upper(), blocks]):
        with pytest.raises(SystemExit, match="other datasets"):
            run_bq.check_tables(sql, p, d, "c12_", [], allowed)
    with pytest.raises(SystemExit, match=r"other datasets.*'" + re.escape(tx) + "'"):
        run_bq.check_tables(sql, p, d, "c12_", [], [blocks])  # the refusal names the view
    # the same view name in another project or dataset is another view
    for other in (f"other-project.goog_blockchain_arbitrum_one_us.transactions",
                  "bigquery-public-data.goog_blockchain_ethereum_mainnet_us.transactions"):
        with pytest.raises(SystemExit, match="other datasets"):
            run_bq.check_tables(f"CREATE TABLE `{p}.{d}.c12_x` AS SELECT * FROM `{other}`", p, d, "c12_", [], [tx])
    # allow_public never lets a project table through: the prefix rule and allow_read still decide
    own = f"CREATE TABLE `{p}.{d}.c12_x` AS SELECT * FROM `{p}.{d}.u_tokens`"
    with pytest.raises(SystemExit, match="outside c12_"):
        run_bq.check_tables(own, p, d, "c12_", [], [f"{p}.{d}.u_tokens"])
    run_bq.check_tables(own, p, d, "c12_", ["u_tokens"])
    # and it does not lift the other refusals
    with pytest.raises(SystemExit, match="another way"):
        run_bq.check_tables(f"DELETE FROM `{tx}` WHERE TRUE", p, d, "c12_", [], [tx])


def test_check_tables_refuses_names_it_cannot_see_and_other_writes():
    import run_bq

    p, d = "dissertation-bq", "contract_rep"
    head = f"CREATE OR REPLACE TABLE `{p}.{d}.c12_x` AS SELECT * "
    refused = {
        "names tables": [head + "FROM contract_rep.u12_labels_w0",                    # two parts, default project
                         head + f"FROM `{p}.{d}.u_*`", head + f"FROM `{p}.{d}.logs_obs$20250401`",
                         head + f"FROM {PUBLIC}.traces",                                # unquoted
                         head + "FROM `bigquery-public-data`.goog_blockchain_arbitrum_one_us.traces",  # split quotes
                         head + "FROM other_dataset.t",
                         "SET @@dataset_id = 'contract_rep';\n" + head + "FROM u12_labels_w0",
                         f"CREATE OR REPLACE EXTERNAL TABLE `{p}.{d}.u_tokens` OPTIONS (uris = ['gs://b/x'])",
                         f"CREATE SNAPSHOT TABLE `{p}.{d}.c12_s` CLONE `{p}.{d}.logs_obs`"],
        "another way": [f"ALTER TABLE `{p}.{d}.logs_obs` SET OPTIONS (expiration_timestamp = CURRENT_TIMESTAMP())",
                        f"LOAD DATA OVERWRITE `{p}.{d}.u_tokens` FROM FILES (format = 'PARQUET', uris = ['gs://b/*'])",
                        "EXECUTE IMMEDIATE 'SELECT 1'", "EXPORT DATA OPTIONS (uri = 'gs://b/*') AS SELECT 1"],
    }
    for message, sqls in refused.items():
        for sql in sqls:
            with pytest.raises(SystemExit, match=message):
                run_bq.check_tables(sql, p, d, "c12_", ["logs_obs", "u_tokens"])
    # names in comments and string literals, EXTRACT and IS DISTINCT FROM are not table names
    run_bq.check_tables("-- reads contract_rep.u_tokens and bigquery-public-data.x.y\n" + head
                        + f"FROM `{p}.{d}.c12_y` AS t  # contract_rep.z\nWHERE t.s != 'contract_rep.u_tokens' "
                        "AND EXTRACT(DATE FROM t.ts) > DATE '2025-04-01' AND t.a IS DISTINCT FROM t.b /* x.y.z */",
                        p, d, "c12_", [])


# Every job of the twelve-month driver as run_bq.py builds it (--sub, then --rename) against the checks of
# --require-prefix u12_: the stricter name and write checks refuse none of them.
EARLIER_JOBS = r"""
    import json
    import run_bq
    import run_usd12m_pipeline as u
    from common import load_config

    cfg = load_config()
    p, d = cfg["bigquery"]["project_id"], cfg["bigquery"]["dataset"]
    out = {}
    for jobs in u.jobs(cfg).values():
        for j in jobs:
            sql = (u.ROOT / "sql" / j.sql).read_text(encoding="utf-8")
            for k, v in j.subs.items():
                sql = sql.replace(f"__{k}__", v)
            sql = run_bq.apply_renames(sql, [f"{a}={b}" for a, b in j.renames.items()], p, d)
            try:
                run_bq.check_tables(sql, p, d, u.PREFIX, list(j.allow))
                out[j.key] = "passed"
            except SystemExit as e:
                out[j.key] = str(e)
    print(json.dumps(out))
"""


def test_the_twelve_month_jobs_pass_check_tables_as_before():
    r = last_json(run_py(EARLIER_JOBS, "usd12m"))
    assert len(r) == 11 and set(r.values()) == {"passed"}, r


def test_allow_public_needs_require_prefix(tmp_path, monkeypatch):
    import run_bq

    def no_client(*args, **kwargs):
        raise AssertionError("BigQuery was reached")

    sql = tmp_path / "q.sql"
    sql.write_text(f"SELECT * FROM `{PUBLIC}.blocks`", encoding="utf-8")
    monkeypatch.setattr(run_bq.bigquery, "Client", no_client)
    monkeypatch.setattr(sys, "argv", ["run_bq.py", str(sql), "--allow-public", f"{PUBLIC}.blocks", "--dry-run"])
    with pytest.raises(SystemExit, match="needs --require-prefix"):
        run_bq.main()


DISPATCH = r"""
    import json
    import common
    import run_registered as r

    class Sentinel(Exception):
        pass

    def reached(*args, **kwargs):
        raise Sentinel()

    def read(*args, **kwargs):
        raise AssertionError("read before the dispatch")

    calls = []
    r.main_contract_graph = lambda: calls.append("main_contract_graph") or 7
    r.load_config = reached
    common.read_parts = r.read_parts = read
    try:
        out = {"returned": r.main()}
    except Sentinel:
        out = {"returned": "load_config"}
    print(json.dumps({**out, "calls": calls, "traders": common.TRADERS}))
"""


def test_the_trader_criteria_stay_with_the_earlier_variants():
    # The trader criteria (F3, F4, F5, P, Q, R1-R3) are not applied in this variant (revision sections 2 and 11):
    # under contract12m, run_registered.main() hands over to main_contract_graph() before it reads anything; the
    # other variants keep TRADERS and reach the registered evaluation (its load_config), never the new branch.
    assert last_json(run_py(DISPATCH, "contract12m")) == {"returned": 7, "calls": ["main_contract_graph"],
                                                          "traders": False}
    for variant in ("registered", "usd", "usd12m"):
        assert last_json(run_py(DISPATCH, variant)) == {"returned": "load_config", "calls": [], "traders": True}, \
            variant


def test_frozen_files_are_unchanged():
    numbered = sorted(f"sql/{p.name}" for p in (EXPERIMENTS / "sql").glob("*.sql")
                      if re.match(r"(0[1-9]|1\d|2[0-3])_", p.name))
    assert numbered == sorted(k for k in FROZEN if k.startswith("sql/")) and len(numbered) == 23
    for rel, digest in FROZEN.items():
        body = (EXPERIMENTS / rel).read_bytes().replace(b"\r\n", b"\n")
        assert hashlib.sha256(body).hexdigest() == digest, rel


# --------------------------------------------------------------------------- the gate A pieces together


def test_shared_paths_agree_across_the_scripts():
    r = last_json(run_py("""
        import json
        import balance_audit as b
        import common
        import labels
        import run_contract12m_pipeline as d
        import run_discovery as rd
        # the discovery files are committed at gate A and checked again by every main run
        files = {"docs/revision_contract_graph.md", "docs/discovery_protocol.md", "config/overlay_contract12m.yaml",
                 "scripts/crawl.py", "scripts/run_discovery.py"}
        print(json.dumps({
            "queue": d.QUEUE == common.TYPES_DIR / "c12_rpc_queue", "types": d.TYPES == common.TYPES,
            "pilot_types": rd.run_feasibility.__kwdefaults__["types"] == common.TYPES,
            "struct": d.STRUCT_T1 == rd.STRUCT == common.GRAPH / "struct_t1",
            "feasibility": d.FEASIBILITY == rd.FEASIBILITY == common.PROC / "discovery" / "feasibility_t1.json",
            "cohort": rd.COHORT_W0 == common.GRAPH_U12 / "cohort_t1",
            "labels": rd.LABELS_W0 == common.GRAPH_U12 / "labels_w0",
            "audit_out": d.BALANCE_AUDIT == b.OUT / "balance_audit.json",
            "audit_in": [d.BAL_AUDIT == common.GRAPH / "bal_audit", d.ANCHOR_BLOCKS == common.GRAPH / "anchor_blocks"],
            "uncommitted": [sorted(files - set(d.COMMITTED)), sorted(files - set(rd.COMMITTED))],
            # gate B: the evaluation reads the lists the pilot read, and the manifest the driver writes
            "members": [labels.u12_stem("spenders_w0") == rd.LABELS_W0, labels.u12_stem("cohort_t1") == rd.COHORT_W0],
            "manifest": d.MANIFEST == common.PROC / "run_manifest.json"}))
    """, "contract12m"))
    assert r == {"queue": True, "types": True, "pilot_types": True, "struct": True, "feasibility": True,
                 "cohort": True, "labels": True, "audit_out": True, "audit_in": [True, True], "uncommitted": [[], []],
                 "members": [True, True], "manifest": True}


def test_pilot_inputs_of_the_twelve_month_analysis_have_the_columns_it_reads():
    import common

    stems = {"cohort_t1": ("address", "binary"), "labels_w0": ("wallet", "string")}
    parts = {name: common.part_paths(common.GRAPH_U12 / name) for name in stems}
    if not all(parts.values()):
        pytest.skip("graph-tables-usd-12m is not on disk (the parquet data live on Drive)")
    for name, (column, kind) in stems.items():
        for path in parts[name]:
            field = pq.read_schema(path).field(column)
            assert str(field.type) == kind, (path.name, field.type)
            if kind == "binary":
                values = pq.read_table(path, columns=[column]).column(0).to_pylist()
                assert values and all(len(v) == 20 for v in values), path.name


# The driver's typing command run by check_account_code.py on a fake RPC, then the driver's queue check and the
# structure pilot on its output (its account types and code families included). Five queue addresses: two plain
# contracts with one code (one probe, copied), a Safe proxy (probed by itself), an externally owned account and an
# EIP-7702 account; every read must be at the pinned block.
CHAIN = r"""
    import json, sys
    from pathlib import Path
    import pandas as pd
    import requests
    import check_account_code as cac
    import run_contract12m_pipeline as d
    import run_discovery as rd
    from common import load_config, load_json, read_parts, write_parts

    tmp = Path(sys.argv[1])
    cfg = load_config()
    pinned = int(cfg["contract_graph"]["pinned_block"])
    addr = lambda n: f"0x{n:040x}"
    word = lambda v: v.to_bytes(32, "big").hex()
    C1, C2, C3, E1, E2, UNTYPED, OWNER = (addr(n) for n in (0xC0001, 0xC0002, 0xC0003, 0xE0001, 0xE0002, 0xF0001, 0xA1))
    plain = "0x6080604052348015600f57600080fd5b"
    code = {cac.PROBE_ADDRESS: "0x6080604052", C1: plain, C2: plain,
            C3: "0x608060405273ffffffffffffffffffffffffffffffffffffffff6000541663a619486e", E2: "0xef0100" + "11" * 20}
    calls = {(C3, "0xe75235b8"): "0x" + word(1), (C3, "0xa0e67e2b"): "0x" + word(32) + word(1) + "00" * 12 + OWNER[2:]}
    blocks, urls = set(), set()

    class Response:
        status_code, text = 200, ""

        def __init__(self, body):
            self.body = body

        def json(self):
            return self.body

    def post(session, url, json=None, timeout=None, **kwargs):  # the RPC, faked: no request leaves the process
        urls.add(url)
        out = []
        for c in json if isinstance(json, list) else [json]:
            head = {"jsonrpc": "2.0", "id": c["id"]}
            method, params = c["method"], c["params"]
            if method == "eth_blockNumber":
                out.append({**head, "result": hex(pinned + 1000)})
                continue
            blocks.add(params[-1])
            if method == "eth_getCode":
                out.append({**head, "result": code.get(params[0], "0x")})
            elif method == "eth_call":
                result = calls.get((params[0]["to"], params[0]["data"]))
                out.append({**head, "result": result} if result else
                           {**head, "error": {"code": 3, "message": "execution reverted"}})
            else:
                out.append({**head, "result": "0x" + "00" * 32})
        return Response(out if isinstance(json, list) else out[0])

    requests.Session.post = post
    real = vars(cac.parse_args(d.typing_command(cfg)[2:]))
    real["paths"] = [real["input"] == str(d.QUEUE), real["output_stem"] == str(d.TYPES)]
    d.QUEUE, d.TYPES = tmp / "c12_rpc_queue", tmp / "c12_account_types"
    write_parts(pd.DataFrame({"address": [C1, C2, C3, E1, E2],
                              "reason": ["cohort", "counterparty", "cohort", "audit_sender", "spender"],
                              "is_emitter": [True, False, True, False, False],
                              "is_created": [True, False, False, False, False]}), d.QUEUE)
    cmd = d.typing_command(cfg)
    rc = cac.main(cmd[2:])
    types = read_parts(d.TYPES)
    meta = load_json(d.TYPES.with_suffix(".json"))
    check = d.types_against_queue(types, read_parts(d.QUEUE))

    struct = pd.DataFrame({"a": [C1, C2, C1, C1, C2, C1, C2], "b": [C2, C1, C1, C2, C1, C1, C1],
                           "layer": ["allow_capped"] * 3 + ["allow_uncapped"] * 3 + ["transfer"]})
    write_parts(struct, tmp / "struct_t1")
    write_parts(pd.DataFrame({"address": [bytes.fromhex(a[2:]) for a in (C1, C3, E1, UNTYPED)]}), tmp / "cohort_t1")
    write_parts(pd.DataFrame({"wallet": [C2, E2], "future_new_approvers": [1, 2]}), tmp / "labels_w0")
    # A protocol whose 'Protocol fixed' holds no block yet: the real one holds it after the gate B commit, and the
    # pilot refuses to run once the protocol is fixed.
    (tmp / "protocol.md").write_text("## Protocol fixed\n\n(Added at gate B.)\n", encoding="utf-8")
    rep = rd.run_feasibility(cfg, struct=tmp / "struct_t1", types=d.TYPES, cohort=tmp / "cohort_t1",
                             labels=tmp / "labels_w0", out=tmp / "feasibility_t1.json", protocol=tmp / "protocol.md")
    layers, self_pairs = d.structure_counts(read_parts(tmp / "struct_t1"))
    names = {C1: "C1", C2: "C2", C3: "C3", E1: "E1", E2: "E2"}
    safe = types.set_index("address").loc[C3]
    print(json.dumps({
        "real": real, "rc": rc, "complete": d.typing_complete(meta), "blocks": sorted(blocks), "urls": sorted(urls),
        "classes": {names[a]: k for a, k in zip(types["address"], types["account_class"])},
        "safe": [safe["wallet_kind"], int(safe["threshold"]), int(safe["n_owners"]), safe["proxy_kind"],
                 bool(safe["has_master_copy"])],
        "probes": meta["probes"], "plain_hash": types.set_index("address").loc[C1, "code_hash"],
        "meta": {k: meta[k] for k in ("block_number", "pinned_requested", "pinned_served", "rpc")},
        "meta_hosts": sorted(meta["rpc_calls"]),
        "url_in_json": "://" in d.TYPES.with_suffix(".json").read_text(encoding="utf-8"),
        "check": check, "pilot_layers": {k: v["edges"] for k, v in rep["layers"].items()},
        "pilot_self_loops": {k: v["self_loops"] for k, v in rep["layers"].items() if v["self_loops"]},
        "driver_layers": layers, "driver_self_pairs": self_pairs, "node_types": rep["node_types"],
        "coverage": {k: [v["members"], v["contracts"], v["user_accounts"], v["untyped"]]
                     for k, v in rep["coverage"].items()},
        "account_types": rep["account_types"], "families": rep["code_families"],
        "stop": rep["rules"]["stop"]["few_capped_allowance_edges"]}))
"""


def test_typing_output_feeds_the_queue_check_and_the_structure_pilot(tmp_path):
    r = last_json(run_py(CHAIN, "contract12m", str(tmp_path)))
    overlay = yaml.safe_load(OVERLAYS["contract12m"].read_text(encoding="utf-8"))["contract_graph"]
    real = r["real"]
    # interface 1: the driver's command as check_account_code.py parses it
    assert real["paths"] == [True, True]
    assert (real["input_parquet"], real["block"], real["fallback_latest"], real["probe_wallets"]) == (
        True, overlay["pinned_block"], True, True)
    assert real["rpc"] == overlay["rpc_urls"] and (real["workers"], real["batch"], real["column"]) == (4, 25, "address")
    # the reads: every one at the pinned block, to the overlay's endpoints only, recorded with host names only
    assert r["rc"] == 0 and r["complete"]
    assert r["blocks"] == [hex(overlay["pinned_block"])] and r["urls"] == sorted(overlay["rpc_urls"])
    assert r["meta"] == {"block_number": overlay["pinned_block"], "pinned_requested": overlay["pinned_block"],
                         "pinned_served": True, "rpc": "arb1.arbitrum.io"}
    assert r["meta_hosts"] == ["arb1.arbitrum.io", "arbitrum-one.public.blastapi.io"] and not r["url_in_json"]
    assert r["classes"] == {"C1": "contract", "C2": "contract", "C3": "smart_account", "E1": "eoa", "E2": "eoa_7702"}
    # the Safe proxy is probed by itself (its slot 0, empty here, read first); the two plain contracts share a code
    # hash, so one is probed and copied
    assert r["safe"] == ["safe", 1, 1, "safe", True]
    assert r["probes"] == {"safe_slots": 1, "representatives": 1, "safe_proxies": 1, "copied": 1}
    # interface 2: the driver's queue check takes the output as it is
    check = r["check"]
    assert check["addresses"] == 5 and check["audit_senders_with_code"] == 0
    assert check["by_class"] == {"contract": 2, "eoa": 1, "eoa_7702": 1, "smart_account": 1}
    assert check["by_reason"]["cohort"] == {"contract": 1, "smart_account": 1}
    assert check["emitters_by_class"] == {"contract": 1, "smart_account": 1}
    # interface 3: the pilot reads the account types, and counts the edges as the driver's stop check does
    assert r["pilot_layers"] == r["driver_layers"] == {"allow_capped": 2, "allow_uncapped": 2, "transfer": 1}
    assert r["pilot_self_loops"] == r["driver_self_pairs"] == {"allow_capped": 1, "allow_uncapped": 1}
    assert r["node_types"] == {"contract": 2} and r["stop"]
    # members typed as contracts are covered; user accounts and addresses outside the types are counted apart
    assert r["coverage"] == {"w0_cohort": [4, 1, 2, 1], "w0_spenders": [2, 1, 1, 0]}
    # the account types and code families the pilot reports, from the columns check_account_code.py writes
    assert r["account_types"] == {
        "queue": {"rows": 5, "account_class": {"contract": 2, "eoa": 1, "eoa_7702": 1, "smart_account": 1},
                  "wallet_kind": {"": 4, "safe": 1}, "proxy_kind": {"none": 4, "safe": 1}},
        "union_nodes": {"nodes": 2, "untyped": 0, "account_class": {"contract": 2}, "wallet_kind": {"": 2},
                        "proxy_kind": {"none": 2}}}
    assert r["families"] == {"contracts": 2, "groups": 1, "canonical_entry_point": [], "largest": [
        {"code_hash": r["plain_hash"], "n": 2, "code_size": 16, "proxy_kind": "none", "implementation": "",
         "entry_points": {"": 2}}]}


# The check step of the driver on fake metadata: the source tables of the earlier builds, the twelve-month tables
# and base tables under the views that job 39 reads (SOURCES_B) and the public views exist with the columns the jobs
# read, no c12_ table exists yet. Before gate A it only warns and writes nothing; once the files are committed it
# records the check in the run manifest. One case per argument (state:campaign USD), each with its own manifest,
# ledger and protocol: 'Protocol fixed' holds no block, except in the case fixed. The campaign of the third case
# is one dollar below the overlay's cap, which the gate B commit may raise (revision section 13).
CAP = float(yaml.safe_load(OVERLAYS["contract12m"].read_text(encoding="utf-8"))["contract_graph"]["campaign_cap_usd"])
CASES = ("preview:0", "committed:0", f"committed:{CAP - 1:g}", "fixed:0")
CHECK = r"""
    import contextlib, io, json, re, sys
    from datetime import datetime, timezone
    from pathlib import Path
    from types import SimpleNamespace
    from google.api_core.exceptions import NotFound
    import run_contract12m_pipeline as d
    from common import load_config

    NL = chr(10)
    sql32 = (d.ROOT / "sql" / "32_c12_bal_pre.sql").read_text(encoding="utf-8")
    literals = sorted(set(re.findall(r"'(0x[0-9a-f]{40})'", sql32)))
    when = datetime(2026, 10, 28, tzinfo=timezone.utc)

    def table(rows, schema, partitioned=False, nbytes=None, modified=when):
        tp = SimpleNamespace(type_="MONTH", field="block_timestamp") if partitioned else None
        return SimpleNamespace(num_rows=rows, num_bytes=10 * rows if nbytes is None else nbytes, time_partitioning=tp,
                               modified=modified, expires=None,
                               schema=[SimpleNamespace(name=n, field_type=t) for n, t in schema.items()])

    tables = {"logs_obs": table(10**9, {"block_timestamp": "TIMESTAMP"}, True),
              "logs_w1": table(10**8, {"block_timestamp": "TIMESTAMP"}, True),
              "u_tokens": table(5, {"token": "BYTES", "decimals": "INTEGER"}),
              "u_prices": table(5000, {"token": "BYTES", "day": "DATE", "price_usd": "FLOAT"}),
              "u12_cohort_tobs": table(6000, {"address": "BYTES"}), "u12_cohort_t1": table(6000, {"address": "BYTES"}),
              "u12_labels_w0": table(8000, {"wallet": "STRING"}), "u12_labels_w1": table(8000, {"wallet": "STRING"}),
              **{v: table(0, {c: "STRING" for c in d.VIEW_COLUMNS[k]}) for k, v in d.VIEWS.items()},
              # SOURCES_B: the twelve-month triples and views and the base tables under them
              "u12_allow_triples_t1": table(4_555_079, {"owner": "BYTES"}),
              "u12_allow_triples_tobs": table(4_185_287, {"owner": "BYTES"}),
              **{v: table(0, {"block_timestamp": "TIMESTAMP"}) for v in (
                  "u12_approvals_t1", "u12_approvals_w1", "u12_transfers_t1", "u12_transfers_tobs",
                  "u12_transfers_w1")},
              **{b: table(10**9, {"block_timestamp": "TIMESTAMP"}, True) for b in (
                  "u_approvals", "u_transfers", "u_approvals_w1", "u_transfers_w1")}}
    assert set(d.SOURCES_B) <= set(tables)
    base = dict(tables)
    # The tables of gate A that the gate B jobs read, at the rows of the projection test of the driver (c12_events_cc
    # with an exact count of its priced rows), so that the projection of the gate B jobs is complete.
    n, priced, logs5 = 6 * 10**8, 5 * 10**8, 1_240_275_042
    gate_a_c12 = {"c12_events_cc": table(n, {}, nbytes=109 * n + 8 * priced),
                  "c12_logs5": table(logs5, {}, nbytes=109 * logs5 + 8 * 10**9),
                  **{k: table(v, {}) for k, v in (("c12_pairs5", 73_058_133), ("c12_contracts", 1_120_000),
                                                  ("c12_user_accounts", 22_600_000), ("c12_bal", 2 * 10**7),
                                                  ("c12_ends", 25_537_280), ("c12_rpc_queue", 6_230_270),
                                                  ("c12_tx_senders", 17_477_779), ("c12_struct_t1", 3_130_000))}}
    cfg = load_config()
    gate_b_keys = set(d.gate_b_keys(cfg))
    gate_a_jobs = [{"step": "earlier", "key": j.key} for j in d.all_jobs(cfg) if j.key not in gate_b_keys]

    class Client:  # the free metadata calls of the check, answered from the tables above
        def get_dataset(self, ds):
            return SimpleNamespace(default_table_expiration_ms=None, default_partition_expiration_ms=None)

        def list_tables(self, ds, max_results=None):
            return [SimpleNamespace(table_id=n) for n in tables if "." not in n]

        def get_table(self, name):
            key = name if name in tables else name.rsplit(".", 1)[-1]
            if key not in tables:
                raise NotFound(name)
            return tables[key]

        def list_rows(self, name):
            assert name.endswith(".u_tokens"), name
            return [{"token": bytes.fromhex(t[2:]), "decimals": 18} for t in literals]

    d.client_and_dataset = lambda cfg: (Client(), "dissertation-bq.contract_rep")
    out = {"gate_b_keys": sorted(gate_b_keys)}
    for case in sys.argv[2:]:
        # states: preview, committed and fixed (above); done (every gate A job run), projected and projected_fixed
        # (also the tables of gate A, so the projection is complete) and calibrated (an input of job 39 modified on
        # 3 November 2026)
        state, campaign = case.split(":")
        tmp = Path(sys.argv[1]) / f"{state}-{campaign}"
        tmp.mkdir()
        tables = dict(base, **(gate_a_c12 if state.startswith("projected") else {}))
        if state == "calibrated":
            tables["u12_approvals_t1"] = table(0, {"block_timestamp": "TIMESTAMP"},
                                               modified=datetime(2026, 11, 3, 12, tzinfo=timezone.utc))
        d.MANIFEST, d.LEDGER = tmp / "run_manifest.json", tmp / "bq_ledger.json"
        d.LEDGER.write_text(json.dumps({"jobs": [{"usd": float(campaign), "label": "contract12m: earlier"}]}))
        if state in ("done", "projected", "projected_fixed"):
            d.MANIFEST.write_text(json.dumps({"variant": "contract12m", "steps": [], "jobs": gate_a_jobs,
                                              "results": {}}))
        d.PROTOCOL = tmp / "protocol.md"
        block = {"date": "2026-11-09", "sha256": "ab" * 32, "U": 1, "E_U": 1, "WCC": 1, "E_WCC": 1}
        fixed = state in ("fixed", "projected_fixed")
        body = "```json" + NL + json.dumps(block) + NL + "```" if fixed else "(Added at gate B.)"
        d.PROTOCOL.write_text("## Protocol fixed" + NL + NL + body + NL, encoding="utf-8")
        changes = " M scripts/crawl.py" if state == "preview" else ""
        d.git = lambda *a, changes=changes: changes if a[0] == "status" else "abc123"
        text = io.StringIO()
        with contextlib.redirect_stdout(text):
            try:
                d.step_check(load_config(), dry=False)
                result = "passed"
            except SystemExit as e:
                result = str(e)
        m = json.loads(d.MANIFEST.read_text(encoding="utf-8")) if d.MANIFEST.exists() else None
        out[case] = {"result": result, "manifest": m, "stdout": text.getvalue()}
    print(json.dumps(out))
"""


@pytest.fixture(scope="module")
def checks(tmp_path_factory) -> dict[str, dict]:
    return last_json(run_py(CHECK, "contract12m", str(tmp_path_factory.mktemp("check")), *CASES))


@pytest.mark.parametrize("case", CASES)
def test_check_step_on_fake_metadata(checks, case):
    state, campaign = case.split(":")
    r = checks[case]
    # the measured parts: job 24 whole, job 34 a few MB; the jobs that wait are listed with their known part
    assert re.search(r"logs5\s+24\s+226\.2\s+226\.2\s+1\.286\s+ready", r["stdout"])
    assert re.search(r"anchor_blocks\s+34\s+0\.0\s+0\.0\s+0\.000\s+ready", r["stdout"])
    assert re.search(r"bal_pre\s+32\s+547\.0\s+547\.0\s+3\.109\s+waits for c12_logs5 from logs5", r["stdout"])
    # gate B: job 39's calibrated term (the bill of the twelve-month W0 label job, 53,868,494,848 B, and its bounded
    # second statement at the 10 MB floor) with the c12 tables it waits for; the projection waits for job 31's tables
    assert re.search(r"labels_w0\s+39\s+53\.9\s+53\.9\s+0\.306\s+waits for c12_contracts from contracts \(job 31\)",
                     r["stdout"])
    assert "projection: waits for c12_events_cc and the other tables of job 31" in r["stdout"]
    if float(campaign):
        assert r["result"].startswith("check failed") and f"cap of USD {CAP:.2f}" in r["result"]
    else:
        assert r["result"] == "passed" and "check passed" in r["stdout"]
    if state == "fixed":
        assert "gate B: 'Protocol fixed' of 2026-11-09 pins abababababab" in r["stdout"]
    else:
        assert "gate B: docs/discovery_protocol.md holds no 'Protocol fixed' block yet" in r["stdout"]
    if state == "preview":
        assert "warning: not committed" in r["stdout"] and "not recorded in run_manifest.json" in r["stdout"]
        assert r["manifest"] is None
    else:
        (entry,) = r["manifest"]["checks_run"]
        assert entry["head"] == "abc123" and entry["existing_c12"] == []
        assert bool(entry["problems"]) == bool(float(campaign))
        assert entry["estimates"]["logs5"]["missing"] == [] and "c12_logs5" in entry["waits"]["ends"]
        assert set(entry["waits"]) == {k for k in entry["estimates"] if k not in ("logs5", "anchor_blocks")}
        assert entry["projection"]["complete"] is False
        if state == "fixed":
            assert entry["gate_b"]["protocol_fixed"]["date"] == "2026-11-09"
        else:
            assert entry["gate_b"]["protocol_fixed"] is None


# The check of gate B's preview and after it, a quarter dollar below the cap: every gate A job run (done), the tables
# of gate A there too so that the projection is complete (projected, with 'Protocol fixed' in projected_fixed), the
# campaign at 0 with that projection, and an input of job 39 modified after the bills that calibrate it.
CASES_B = (f"done:{CAP - 0.25:g}", f"projected:{CAP - 0.25:g}", f"projected_fixed:{CAP - 0.25:g}", "projected:0",
           "calibrated:0")


@pytest.fixture(scope="module")
def checks_b(tmp_path_factory) -> dict[str, dict]:
    return last_json(run_py(CHECK, "contract12m", str(tmp_path_factory.mktemp("check_b")), *CASES_B))


def test_check_step_judges_the_gate_b_jobs_by_their_projection(checks_b):
    # D4 (design C24): the check tests the known estimates of the gate A jobs not yet run against the cap and the
    # budget; the gate B jobs are judged by their projection alone, which only warns while 'Protocol fixed' holds no
    # block and fails the check once it holds one. With every gate A job run, a campaign at which the known parts of
    # the gate B jobs would pass the cap passes while the projection waits for job 31. A complete projection prints
    # the cap and the budget it needs (D1). D6: an input of job 39's measured terms modified after the first bill
    # that calibrates them fails the check.
    from test_contract12m_pipeline import least_cent

    gate_b, camp = set(checks_b["gate_b_keys"]), CAP - 0.25
    r = checks_b[f"done:{camp:g}"]
    assert r["result"] == "passed" and "check passed" in r["stdout"], r["result"]
    (entry,) = r["manifest"]["checks_run"]
    assert entry["problems"] == [] and entry["projection"]["complete"] is False
    known_b = sum(e["whole"] for k, e in entry["estimates"].items() if k in gate_b) / 2**40 * 6.25
    assert camp + known_b > CAP, known_b      # the known parts of the gate B jobs would pass the cap with it
    assert "projection: waits for c12_events_cc and the other tables of job 31" in r["stdout"]
    assert " needed: " not in r["stdout"]
    for state in ("projected", "projected_fixed"):
        r = checks_b[f"{state}:{camp:g}"]
        (entry,) = r["manifest"]["checks_run"]
        proj = entry["projection"]
        assert proj["complete"] is True and set(proj["jobs"]) == gate_b, proj.get("missing")
        z = proj["usd"]
        assert z > 0.25, z                    # with the campaign it passes the cap; with the ledger it stays in budget
        over = (f"the gate B jobs not yet run are projected at up to USD {z:.2f}; with the campaign so far (USD "
                f"{camp:.2f}) it passes the cap of USD {CAP:.2f}")
        assert [line for line in r["stdout"].splitlines() if " needed: " in line] == [
            f"cap needed: USD {least_cent(camp + z):.2f} (above the cap of USD {CAP:.2f})",
            f"budget needed: USD {least_cent(camp + z):.2f}, within the budget of USD 60"], state
        assert not [p for p in entry["problems"] if "known estimates" in p], entry["problems"]
        if state == "projected":
            assert r["result"] == "passed" and entry["problems"] == [], r["result"]
            assert f"warning: {over}; the gate B commit sets the cap" in r["stdout"]
        else:
            assert entry["problems"] == [over] and r["result"] == "check failed:\n  " + over, r["result"]
    r = checks_b["projected:0"]
    z = r["manifest"]["checks_run"][0]["projection"]["usd"]
    assert r["result"] == "passed" and "warning: the gate B jobs" not in r["stdout"]
    assert f"cap needed: USD {least_cent(z):.2f} (within the cap of USD {CAP:.2f})" in r["stdout"]
    assert f"budget needed: USD {least_cent(z):.2f}, within the budget of USD 60" in r["stdout"]
    r = checks_b["calibrated:0"]
    assert r["result"].startswith("check failed") and ("u12_approvals_t1 was modified at 2026-11-03T12:00:00+00:00, "
                                                       "after the first bill that calibrates job 39, at "
                                                       "2026-10-28T09:09:32+00:00") in r["result"], r["result"]
    (entry,) = r["manifest"]["checks_run"]
    assert [p for p in entry["problems"] if "u12_approvals_t1" in p] and len(entry["problems"]) == 1


# --------------------------------------------------------------------------- gate B: the earlier variants


def compare_data(a: Path, b: Path) -> list[str]:
    """The files of a/data and b/data that differ: in one folder only, a parquet table that is not equal, or any
    other file whose bytes differ."""
    sa, sb = w.snapshot(a / "data"), w.snapshot(b / "data")
    bad = sorted(set(sa) ^ set(sb))
    for rel in sorted(set(sa) & set(sb)):
        if rel.endswith(".parquet"):
            if not pq.read_table(a / "data" / rel).equals(pq.read_table(b / "data" / rel)):
                bad.append(rel)
        elif sa[rel] != sb[rel]:
            bad.append(rel)
    return bad


@pytest.mark.parametrize("variant", ["usd12m", pytest.param("registered", marks=slow), pytest.param("usd", marks=slow)])
def test_earlier_variants_write_the_same_outputs_as_at_gate_a(tmp_path, variant):
    # O1 (revision introduction): the six evaluation scripts of an earlier variant, under the code of the gate A
    # commit and under this tree, each on the same synthetic world (tests/c12_world.py), with git trapped (no git
    # command under an earlier variant): both exit 0, and after each script both data folders hold the same files,
    # every JSON byte-identical and every parquet table equal. describe_data, export_latex and publish_results need
    # BigQuery, the manuscript or the clock; O3 covers their code. The two sandboxes run side by side.
    exps = {"old": w.sandbox(tmp_path / "old", w.GATE_A), "new": w.sandbox(tmp_path / "new")}
    for exp in exps.values():
        w.earlier_world(exp, variant)
    assert not compare_data(exps["old"], exps["new"])
    with ThreadPoolExecutor(max_workers=2) as pool:
        for script in w.EARLIER_SCRIPTS:
            outs = dict(zip(exps, pool.map(lambda e: w.run_script(e, script, variant, traps=False, git_trap=True),
                                           exps.values())))
            for code, out in outs.items():
                assert out.returncode == 0, f"{code} {script}:\n{out.stdout[-1500:]}\n{out.stderr[-3000:]}"
            diff = compare_data(exps["old"], exps["new"])
            assert not diff, f"after {script} under {variant} the outputs differ: {diff[:10]}"


def load_base(name: str, tmp: Path, monkeypatch):
    """scripts/<name>.py of the gate A commit as a module of its own (the scoring_base pattern of test_crawl.py),
    registered as <name>_base for the test (its dataclasses look their module up)."""
    src = w.git_blob(w.GATE_A, f"scripts/{name}.py")
    if src is None:
        pytest.skip(f"commit {w.GATE_A} is not available")
    path = tmp / f"{name}_base.py"
    path.write_bytes(src)
    spec = importlib.util.spec_from_file_location(f"{name}_base", path)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, f"{name}_base", module)
    spec.loader.exec_module(module)
    return module


def random_pairs(seed: int) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    """Allowance and transfer pairs on random node ids with duplicates, zero weights and a self-loop, and member
    ids, some of them outside both layers."""
    rng = np.random.default_rng(seed)
    nodes = np.sort(rng.choice(10_000, 80, replace=False))

    def layer(m, weight, count):
        f = pd.DataFrame({"src": nodes[rng.integers(0, 60, m)], "dst": nodes[rng.integers(0, 60, m)],
                          count: rng.integers(1, 4, m), weight: rng.lognormal(size=m), "w_raw": rng.lognormal(size=m),
                          "max_sig": rng.uniform(0.01, 1.0, m)})
        f.loc[rng.random(m) < 0.1, weight] = 0.0
        f.loc[rng.random(m) < 0.05, "w_raw"] = 0.0
        loop = f.iloc[[0]].assign(dst=f["src"].iloc[0])
        return pd.concat([f, f.iloc[:5], loop], ignore_index=True)

    return layer(300, "w_er", "n_tokens"), layer(400, "w_awp", "n_transfers"), np.sort(rng.choice(nodes, 40, False))


def test_shared_modules_give_the_earlier_variants_the_same_results(tmp_path, monkeypatch, params, probes):
    # O2 (the scoring_base pattern): graphs, labels and usd of the gate A commit, loaded as modules of their own,
    # give the results of this tree on the inputs the earlier variants pass; common.py gives every earlier variant
    # the names and configuration of the gate A commit (VARIANT_PROBE with BASE_B).
    import common
    import graphs
    import labels
    import usd

    old = {name: load_base(name, tmp_path, monkeypatch) for name in ("graphs", "labels", "usd")}
    for seed in range(4):
        allow, transfer, ids = random_pairs(seed)
        g_new, g_old = graphs.Graphs("t1", allow, transfer), old["graphs"].Graphs("t1", allow, transfer)
        for kw in ({}, {"methods": ("endorserank", "awp"), "isolated": ids},
                   {"methods": ("cpr_l100", "cpr_l0"), "isolated": ids}):
            new_s, new_it = graphs.score_all(g_new, params, **kw)
            old_s, old_it = old["graphs"].score_all(g_old, params, **kw)
            assert list(new_s) == list(old_s) and new_it == old_it, (seed, kw.get("methods"))
            for m in new_s:
                pd.testing.assert_series_equal(new_s[m], old_s[m], check_exact=True)
        pd.testing.assert_frame_equal(graphs.raw_degrees(g_new, ids), old["graphs"].raw_degrees(g_old, ids),
                                      check_exact=True)
    # the loaders, in the old call form and with the default stem named
    allow, transfer, ids = random_pairs(7)
    export = tmp_path / "export"
    common.write_parts(pd.DataFrame({"id": np.arange(5), "address": [w.contract(i) for i in range(5)],
                                     "is_cohort": [True, False, True, False, True]}), export / "nodes")
    common.write_parts(allow, export / "allow_pairs_t1")
    common.write_parts(transfer, export / "transfer_pairs_t1")
    monkeypatch.setattr(graphs, "EXPORT", export)
    monkeypatch.setattr(old["graphs"], "EXPORT", export)
    for new_g in (graphs.load_graphs("t1"), graphs.load_graphs("t1", "allow_pairs")):
        old_g = old["graphs"].load_graphs("t1")
        assert new_g.tag == old_g.tag
        pd.testing.assert_frame_equal(new_g.allow, old_g.allow, check_exact=True)
        pd.testing.assert_frame_equal(new_g.transfer, old_g.transfer, check_exact=True)
    pd.testing.assert_frame_equal(graphs.load_nodes(), old["graphs"].load_nodes(), check_exact=True)
    # the account types of the earlier variants and the trader labels
    raw = tmp_path / "raw"
    types = {"cohort/candidate_account_types": (0, 6), "cohort/holdout_spender_types": (4, 9),
             "gmx/gmx_account_types": (8, 12), "gmx/gmx_account_types_w1": (11, 14)}
    for stem, (lo, hi) in types.items():
        common.write_parts(pd.DataFrame({"address": [w.contract(i) for i in range(lo, hi)],
                                         "code_kind": [("contract", "none", "eip7702")[i % 3] for i in range(lo, hi)],
                                         "account_class": "x"}), raw / stem)
    monkeypatch.setattr(labels, "RAW", raw)
    monkeypatch.setattr(old["labels"], "RAW", raw)
    pd.testing.assert_series_equal(labels.account_types(), old["labels"].account_types(), check_exact=True)
    rng = np.random.default_rng(3)
    k = 400
    closes = pd.DataFrame({"account": [w.trader(int(i)) for i in rng.integers(0, 30, k)],
                           "block_timestamp": pd.Timestamp("2026-04-01", tz="UTC")
                           + pd.to_timedelta(rng.integers(0, 120 * 24, k), unit="h"),
                           "pnl": rng.normal(0.0, 100.0, k), "is_liquidation": rng.random(k) < 0.2})
    args = (closes, "2026-04-01 00:00:00 UTC", "2026-06-30 23:59:59 UTC", 3)
    pd.testing.assert_frame_equal(labels.trader_labels(*args), old["labels"].trader_labels(*args), check_exact=True)
    score, label, n = rng.random(60), rng.random(60), rng.integers(3, 40, 60)
    assert labels.strata_tau(score, label, n) == old["labels"].strata_tau(score, label, n)
    # usd on the inputs of test_usd.py
    u, o = usd, old["usd"]
    for x, d in ((123.456, 2), (0.0012345, 2), (98765.0, 3), (0.0, 2)):
        assert u.round_sig(x, d) == o.round_sig(x, d)
    z = np.array([0.0, 1e-9, 0.5, 49.9, 50.0, 400.0, 2000.0, 1e9, 1e62])
    for m in (0.37, 12.0, 50.0, 840.0, 2.5e6):
        assert u.slope_for_median(m) == o.slope_for_median(m)
        np.testing.assert_array_equal(u.value_transform_sql(z, u.slope_for_median(m)),
                                      o.value_transform_sql(z, o.slope_for_median(m)))
    for mod in (u, o):
        with pytest.raises(ValueError):
            mod.slope_for_median(0.0)
    unlimited = float(2**256 - 1)
    value, dec, price = [2.5e6, 1.5e8, 3e17, 1e3, unlimited], [6, 8, 18, 2, 18], [1.0, 6e4, 2500.0, 1.08, 2500.0]
    np.testing.assert_array_equal(u.usd_value(value, dec, price), o.usd_value(value, dec, price))
    np.testing.assert_array_equal(u.token_amount(value, dec), o.token_amount(value, dec))
    np.testing.assert_array_equal(u.is_unlimited([unlimited, 1e30]), o.is_unlimited([unlimited, 1e30]))
    np.testing.assert_array_equal(u.capped([1e66, 10.0], 5e5), o.capped([1e66, 10.0], 5e5))
    prices = pd.DataFrame({"token": ["a", "a", "a", "b"],
                           "day": ["2024-01-02", "2024-01-03", "2024-01-06", "2024-01-04"],
                           "price_usd": [1.0, 1.1, 1.3, 50.0], "confidence": [0.99, 0.99, 0.98, 0.9]})
    pd.testing.assert_frame_equal(u.fill_daily(prices, "2024-01-01", "2024-01-07"),
                                  o.fill_daily(prices, "2024-01-01", "2024-01-07"), check_exact=True)
    for mod in (u, o):
        with pytest.raises(ValueError):
            mod.fill_daily(pd.concat([prices, prices.iloc[:1]]), "2024-01-01", "2024-01-07")
    # common.py: every earlier variant gets the names and configuration of the gate A commit
    if probes["registered"]["before_b"] is None:
        pytest.skip(f"commit {BASE_B} is not available")
    for variant in ("registered", "usd", "usd12m"):
        assert probes[variant]["before_b"] == {"differ": [], "same_config": True}, variant
    assert probes["contract12m"]["before_b"] is None


@pytest.mark.parametrize("rel", w.CODE_PATH_FILES)
def test_earlier_variants_take_the_code_of_gate_a(rel):
    # O3 (revision introduction; design_tests.md 2.5 with check H3): the statements that the variants registered,
    # usd and usd12m execute (CONTRACT_GRAPH = False, TRADERS = True folded; docstrings, imports of names the gate A
    # file lacks and new top-level definitions left out) are those of d39775c, except the functions of
    # c12_world.ALLOWED_CHANGES, which O2 checks by their results. The style this enforces: the earlier variants'
    # statements stay as they are; contract12m code lives in new functions and constants, reached by `if
    # CONTRACT_GRAPH: return f()` or in blocks guarded by `if CONTRACT_GRAPH:`, `if not CONTRACT_GRAPH:` or `if
    # TRADERS:`.
    old = w.git_blob(w.GATE_A, rel)
    if old is None:
        pytest.skip(f"commit {w.GATE_A} is not available")
    diff = w.code_path_differences(rel, old.decode("utf-8"), (EXPERIMENTS / rel).read_text(encoding="utf-8"))
    assert not diff, f"{rel}: the code of the earlier variants differs from {w.GATE_A} in {diff}"


def test_the_code_path_check_sees_an_unguarded_statement():
    # O3, the check itself: a statement added to main() outside a guard, or in a branch that the earlier variants
    # take, is a difference; a guarded contract12m block and a new function are not.
    old = w.git_blob(w.GATE_A, "scripts/run_holdout.py")
    if old is None:
        pytest.skip(f"commit {w.GATE_A} is not available")
    src = old.decode("utf-8").replace("\r\n", "\n")
    head = "def main() -> int:\n"
    assert head in src
    assert w.code_path_differences("run_holdout", src, src) == []
    guarded = src.replace(head, head + "    if CONTRACT_GRAPH:\n        prov = require_committed()\n") + \
        "\n\ndef added_for_contract12m():\n    return 1\n"
    assert w.code_path_differences("run_holdout", src, guarded) == []
    for changed in (src.replace(head, head + "    prov = require_committed()\n"),
                    src.replace(head, head + "    if not CONTRACT_GRAPH:\n        prov = require_committed()\n")):
        assert w.code_path_differences("run_holdout", src, changed) == ["main"]


C12_FOLDERS = ("graph-tables-contract-12m", "contract-types", "revised-contract-12m", "contract-12m")


def test_tracked_outputs_of_the_earlier_variants_are_those_of_gate_a():
    # O4 (T7): every data file of the gate A commit outside the contract12m folders, the ledger and the README files
    # is still there and equals its d39775c blob (CRLF read as LF).
    files = w.commit_files(w.GATE_A, ("data",))
    if files is None:
        pytest.skip(f"commit {w.GATE_A} is not available")
    bad, checked = [], 0
    for rel, blob in files:
        parts = rel.split("/")
        if rel == "data/bq_ledger.json" or parts[-1] == "README.md" or set(parts) & set(C12_FOLDERS):
            continue
        path = EXPERIMENTS / rel
        checked += 1
        if not path.is_file():
            bad.append(f"{rel}: deleted")
        elif path.read_bytes().replace(b"\r\n", b"\n") != blob.replace(b"\r\n", b"\n"):
            bad.append(f"{rel}: changed")
    assert checked > 100 and not bad, bad


def test_ledger_only_grows_with_contract12m_jobs():
    # O4: the ledger of the gate A commit is a prefix of the current one, its price is unchanged, and every later
    # job is a job of this variant's campaign under its budget.
    old = w.git_blob(w.GATE_A, "data/bq_ledger.json")
    if old is None:
        pytest.skip(f"commit {w.GATE_A} is not available")
    old, new = json.loads(old), json.loads((EXPERIMENTS / "data" / "bq_ledger.json").read_text(encoding="utf-8"))
    assert new["usd_per_tib"] == old["usd_per_tib"]
    assert new["jobs"][:len(old["jobs"])] == old["jobs"]
    for job in new["jobs"][len(old["jobs"]):]:
        assert job["label"].startswith("contract12m: ") and job["variant"] == "contract12m", job.get("label")
        assert job["budget_usd"] == 60.0, job.get("label")


# SHA-256 of the gate A versions (d39775c, CRLF read as LF; check_account_code.py as amended in 52d3aa1, revision
# section 4.3, and sql/31_c12_contracts.sql as amended in caf97c3, the amendment of 9 November 2026 of revision
# section 13) of the files that gate B must not change (revision section 12 and the decisions' list of what may
# change), with the scripts outside gate B's scope (T16).
FROZEN_GATE_A = {
    "scripts/run_bq.py": "dda10e81897503c647fced175300b50a625f8963347a34f6cbe77b8ad7dbebb7",
    "scripts/check_account_code.py": "0b28e563f338b29e29a7a553f4633aa492ac2394b1efe234cda30bf2ed8e0746",
    "scripts/balance_audit.py": "8656ca08b85737cb0dc165185542226e30a1e0b3056d949197eab6a9dfbc98c2",
    "scripts/download_table.py": "c4263b1685afaff0c5c5d509da697a38c918a7833edf86d7f10a4230ebc96b4d",
    "scripts/crawl.py": "3611540a01f3e0514e755be747c1957ca43e38b4caa38c61397344d7dee71064",
    "scripts/scoring.py": "ea0e9fcc60e647a1facd01ea8d45f3d12ed6de753dd63bf263c2e6cf063a9984",
    "scripts/stats.py": "7fa2c4ea51f886a38753008ad807ba5e914700589e6f9d968b3d5f036a1d4e47",
    "sql/24_c12_logs5.sql": "c273f09eb2fc09f9249064a75786abdb3ca5a4fa61083949bbcd8dcee0ccad21",
    "sql/25_c12_ends.sql": "89a46ff5c3d960d7c6fea102811fab9da76c769b8b118aa675ed6fce3134c6c9",
    "sql/26_c12_tx_senders.sql": "f0248d0d55d47a664fb03ff12db727a6cec681a338e390fdbcd2fac19752187b",
    "sql/27_c12_emitters.sql": "8900a32ad0eab231251d878e16825be0bda708f812cbd024395b951c68cce474",
    "sql/28_c12_creations.sql": "232ee6cab8f5affafae2b2a968f1d963c175c4816cd9fa4109a722cef01904bd",
    "sql/29_c12_rpc_queue.sql": "116164f5ce66894ca7947f525b97d5823c900e62d6ecf8da472d087dc77f8a29",
    "sql/31_c12_contracts.sql": "08e932d0f62eae1f73254e099ea8a50d3d9108c3b043deec409653951373be1c",
    "sql/32_c12_bal_pre.sql": "c4ec9cbd7eeade4fedff7253f605aec21afec2ac5ab1611ec1a92ff358215c6b",
    "sql/33_c12_bal.sql": "35999be73f81df5c43ec16e47ad3f16c30b93fb2b6ef11af698a05f7d893b82c",
    "sql/34_c12_anchor_blocks.sql": "bb56b2c8e6574f23fc5e07a1670cd8e237c3e318399e671dcf6802b913ca6491",
    "sql/35_c12_structure.sql": "b6dac39ff9a3274b45927906b04bad453357d98fa5d5a49104b3a6a86e5604e8",
    "sql/43_c12_bal_audit.sql": "7679609a3747055095f8440756d44dc79f2b328cc69d1359a3d961fc2bbdf9b2",
    # outside gate B's scope (D22: run_benchmark.py unchanged; run_usd_local.ps1 needs no change; the registered
    # pipeline's scripts)
    "scripts/run_benchmark.py": "ea787eacf76697cd54f2772b912e741388b708f2db472ab4d3182f8caf0e77a1",
    "scripts/run_usd_local.ps1": "00c33d5a5b4e56e1a5a2bf89e88a24da2de2c16a33e5ddeaca1b1dc8f2f9faa6",
    "scripts/build_cohort.py": "058af31e373487c885d6b860a75cb1ee74d8c985341065ad0b85f7eab2faf1b6",
    "scripts/chainlink_check.py": "4abb0717210b0e15e3fbdff7a2e77ddd2350334a1d12b6d81b70e2175d704015",
    "scripts/decode_gmx_events.py": "e4cb4a65b0ba538f950268b16df5b56daac65125a4748f884ec0e60c87a51a62",
    "scripts/extract_w1.py": "7066946f699a19f78d44e1a7364c6b36b67ed43b061a782b6fdf983680fcec2e",
    "scripts/token_metadata.py": "4899a54b9d03488d43be530cf265f6b7660ce896a709fc369f0731b9c1829e5f",
    "scripts/usd_inputs.py": "129b116f77a61d449142e07b539c35539ebeddb60dea2c39f881212db6ac60cb",
    "scripts/download_graph_tables.sh": "708f6a7d18009fca4ea2a6f46da9f1dc63f8ae15247a4c720315170636149f66",
}


def lf_sha256(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def test_gate_a_files_gate_b_must_not_change():
    # O5 (revision section 12; D3): the pinned gate A files are unchanged, and the overlay differs from that of
    # d39775c at most in the one line of the campaign cap, which stays between USD 14 and the budget of USD 60.
    changed = [rel for rel, digest in FROZEN_GATE_A.items() if lf_sha256((EXPERIMENTS / rel).read_bytes()) != digest]
    assert not changed, changed
    old = w.git_blob(w.GATE_A, "config/overlay_contract12m.yaml")
    if old is None:
        pytest.skip(f"commit {w.GATE_A} is not available")
    old_text = old.decode("utf-8")
    new_text = OVERLAYS["contract12m"].read_text(encoding="utf-8")
    old_cfg, new_cfg = yaml.safe_load(old_text), yaml.safe_load(new_text)
    cap = float(new_cfg["contract_graph"].pop("campaign_cap_usd"))
    old_cfg["contract_graph"].pop("campaign_cap_usd")
    assert new_cfg == old_cfg
    lines = [line for line in difflib.ndiff(old_text.splitlines(), new_text.splitlines()) if line[:2] in ("- ", "+ ")]
    assert len(lines) in (0, 2) and all("campaign_cap_usd:" in line for line in lines), lines
    assert 14.0 <= cap <= 60.0 == float(new_cfg["bigquery"]["budget_usd"])


MANIFEST_REL = "data/2-processed-tables-and-evaluations/revised-contract-12m/run_manifest.json"


def started_after(entry: dict, moment: datetime) -> bool:
    """Whether a step entry of the run manifest has a started_at after ``moment`` (a time without an offset is UTC)."""
    text = entry.get("started_at")
    if not text:
        return False
    t = datetime.fromisoformat(text)
    return (t if t.tzinfo else t.replace(tzinfo=timezone.utc)) > moment


def test_gate_a_steps_ran_on_the_files_of_gate_a():
    # O5, provenance: every step of the gate A chain in the run manifest of this variant recorded, for every file
    # of the driver's COMMITTED, the SHA-256 of its d39775c version or of its version after the dated amendment of
    # revision section 4.3 (52d3aa1), the bytes with LF or the same text with CRLF. A step that started after the
    # commit of the amendment of 9 November 2026 (caf97c3, revision section 13, after which job 31 and the structure
    # pilot ran again) may also have recorded the versions of that commit, and no step before it. So no gate A step
    # ran on other files than those of gate A as amended when it started.
    path = EXPERIMENTS / MANIFEST_REL
    if not path.exists():
        pytest.skip("the run manifest of the contract-graph variant is not on disk")
    revs = (w.GATE_A, *w.GATE_A_AMENDED)
    missing = [rev for rev in revs if not w.commit_exists(rev)]
    if missing:
        pytest.skip(f"commit {', '.join(missing)} is not available")
    committed, chain_a = last_json(run_py("import json, run_contract12m_pipeline as d; "
                                          "print(json.dumps([d.COMMITTED, d.CHAIN_A]))", "contract12m"))
    versions = {}                                   # (commit, file) -> SHA-256 of its bytes with LF and with CRLF
    for rev in revs:
        for rel in committed:
            blob = w.git_blob(rev, rel)
            assert blob is not None, (rev, rel)
            lf = blob.replace(b"\r\n", b"\n")
            versions[rev, rel] = {hashlib.sha256(lf).hexdigest(),
                                  hashlib.sha256(lf.replace(b"\n", b"\r\n")).hexdigest()}
    before = (w.GATE_A, w.STYLUS_AMENDMENT)
    since = w.commit_time(w.SMART_ACCOUNT_AMENDMENT)
    entries = [e for e in json.loads(path.read_text(encoding="utf-8"))["steps"] if e["step"] in chain_a]
    assert entries
    bad = []
    for e in entries:
        accepted = (*before, w.SMART_ACCOUNT_AMENDMENT) if started_after(e, since) else before
        for rel in committed:
            if not any((e.get("sha256") or {}).get(rel) in versions[rev, rel] for rev in accepted):
                bad.append((e["step"], e.get("started_at"), rel))
    assert not bad, bad


# The folders whose files are pinned by their SHA-256 as written (feasibility_t1.json by 'Protocol fixed' and the run
# manifest, constants.json by the manifest; common.save_json writes CRLF on Windows) and must be committed byte for
# byte, and the folder of the first pilot's structure table, which the amendment of 9 November 2026 keeps byte for
# byte (revision section 13); a path in each, and paths of the earlier variants, of the other graph tables of this
# variant and the ledger, which keep git's settings.
BYTE_FOR_BYTE = ("data/2-processed-tables-and-evaluations/revised-contract-12m",
                 "data/0-usd-token-list-and-prices/contract-12m",
                 "data/1-raw-blockchain-extracts/graph-tables-contract-12m/first_pilot_2026-11-08")
ATTR_PATHS = {"data/2-processed-tables-and-evaluations/revised-contract-12m/discovery/feasibility_t1.json": "unset",
              "data/2-processed-tables-and-evaluations/revised-contract-12m/run_manifest.json": "unset",
              "data/2-processed-tables-and-evaluations/revised-contract-12m/same-window/eval_summary.json": "unset",
              "data/0-usd-token-list-and-prices/contract-12m/constants.json": "unset",
              "data/1-raw-blockchain-extracts/graph-tables-contract-12m/first_pilot_2026-11-08/struct_t1.json": "unset",
              "data/1-raw-blockchain-extracts/graph-tables-contract-12m/struct_t1.json": "unspecified",
              "data/2-processed-tables-and-evaluations/revised-usd-12m/run_manifest.json": "unspecified",
              "data/2-processed-tables-and-evaluations/revised-usd-12m/same-window/eval_summary.json": "unspecified",
              "data/0-usd-token-list-and-prices/usd-12m/constants.json": "unspecified",
              "data/bq_ledger.json": "unspecified",
              "scripts/run_contract12m_pipeline.py": "unspecified"}


def test_pinned_contract12m_files_are_committed_byte_for_byte():
    # D2: on a checkout with core.autocrlf the pinned files would be committed with LF and checked out elsewhere with
    # other bytes than their hashes; the .gitattributes at the repository root unsets text for the two folders of
    # this variant and the folder of the first pilot's structure table only (git check-attr: unset), and nothing else
    # (the earlier variants, the other graph tables, the ledger, the code: unspecified).
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=EXPERIMENTS, capture_output=True, text=True)
    if top.returncode != 0:
        pytest.skip("experiments/ is not in a git work tree")
    root = Path(top.stdout.strip())
    prefix = EXPERIMENTS.resolve().relative_to(root.resolve()).as_posix()
    rules = [line.strip() for line in (root / ".gitattributes").read_text(encoding="utf-8").splitlines()
             if line.strip() and not line.lstrip().startswith("#")]
    assert rules == [f"{prefix}/{folder}/** -text" for folder in BYTE_FOR_BYTE], rules
    out = subprocess.run(["git", "check-attr", "text", "--", *ATTR_PATHS], cwd=EXPERIMENTS, capture_output=True,
                         text=True, check=True)
    got = {}
    for line in out.stdout.splitlines():
        path, attr, value = line.rsplit(": ", 2)
        assert attr == "text", line
        got[path] = value
    assert got == ATTR_PATHS, {p: (got.get(p), v) for p, v in ATTR_PATHS.items() if got.get(p) != v}


# --------------------------------------------------------------------------- gate B: the committed state (T10)


PROTOCOL_REL, REVISION_REL = "docs/discovery_protocol.md", "docs/revision_contract_graph.md"


def lf_lines(data: bytes | str) -> list[str]:
    text = data.decode("utf-8") if isinstance(data, bytes) else data
    return text.replace("\r\n", "\n").split("\n")


def test_gate_b_state_protocol_changes_only_in_protocol_fixed():
    # O6 (protocol, line 5): the protocol changes only in its last section, 'Protocol fixed', which holds exactly
    # one fenced json block.
    old = w.git_blob(w.GATE_A, PROTOCOL_REL)
    if old is None:
        pytest.skip(f"commit {w.GATE_A} is not available")
    old_lines, new_lines = lf_lines(old), lf_lines((EXPERIMENTS / PROTOCOL_REL).read_bytes())
    k = old_lines.index("## Protocol fixed")
    assert new_lines[:k + 1] == old_lines[:k + 1], "the protocol changed before 'Protocol fixed'"
    section = new_lines[k + 1:]
    assert not [line for line in section if line.startswith("## ")], "'Protocol fixed' is not the last section"
    blocks = re.findall(r"^```json[ \t]*\n(.*?)\n```", "\n".join(section), flags=re.S | re.M)
    assert len(blocks) == 1, f"'Protocol fixed' holds {len(blocks)} json blocks, not one (written at gate B)"


def protocol_fixed_json(text: str) -> dict | None:
    """The object of the first fenced json block of the section 'Protocol fixed' of the protocol ``text`` (the
    section O6 checks), None without one."""
    lines = lf_lines(text)
    section = "\n".join(lines[lines.index("## Protocol fixed") + 1:])
    m = re.search(r"^```json[ \t]*\n(.*?)\n```", section, flags=re.S | re.M)
    return json.loads(m.group(1)) if m else None


def as_written(x) -> str:
    """A number of the pilot or of 'Protocol fixed' as its JSON writes it (a decimal string as it is)."""
    return x if isinstance(x, str) else json.dumps(x)


def test_gate_b_state_revision_changes_only_by_its_dated_amendment():
    # O7 (revision section 13; D24; check M5; F7): the revision of 52d3aa1 differs from d39775c only by the dated
    # amendment of section 4.3 made during the reads (insertions inside section 4.3); the revision of caf97c3 differs
    # from that of 52d3aa1 only by the dated amendment of 9 November 2026 (insertions after the line "After gate B,
    # nothing in this file changes." that hold its heading and the json block smart_account_extension of its lists);
    # and the revision differs from that of caf97c3 only by insertions after that amendment. They hold the dated
    # amendment of gate B under its own heading ("- *Amendment of <day> November 2026 (gate B)", not before
    # 9 November), with every placeholder of the draft filled, whose first item gives the sizes, the edges, the share
    # and the rules of the pilot that 'Protocol fixed' pins as that file records them, which names the evaluation
    # code file by file (the driver's EVAL_FILES_B, in order, by the parser of conftest.py) and the ledger jobs and
    # bytes of job 39's calibrated estimate, and which keeps the campaign cap of the overlay, or raises it to the
    # overlay's cap, in the draft's own sentence.
    revs = (w.GATE_A, w.STYLUS_AMENDMENT, w.SMART_ACCOUNT_AMENDMENT)
    blobs = [w.git_blob(rev, REVISION_REL) for rev in revs]
    missing = [rev for rev, blob in zip(revs, blobs) if blob is None]
    if missing:
        pytest.skip(f"commit {', '.join(missing)} is not available")
    a_lines, m_lines, s_lines = (lf_lines(blob) for blob in blobs)
    s43, s5 = a_lines.index("### 4.3 RPC queue and reads"), a_lines.index("## 5. Edges")
    ops_43 = [op for op in difflib.SequenceMatcher(a=a_lines, b=m_lines, autojunk=False).get_opcodes()
              if op[0] != "equal"]
    assert ops_43 and all(op[0] == "insert" and s43 < op[1] < s5 for op in ops_43), ops_43
    inserted_43 = "\n".join(line for op in ops_43 for line in m_lines[op[3]:op[4]])
    assert "*Amendment of 8 November 2026, made during the reads of this section and before gate B:*" in inserted_43
    # The amendment of 9 November 2026 (caf97c3): insertions after the end of section 13's preamble only.
    after = next(i for i, line in enumerate(m_lines) if "After gate B, nothing in this file changes." in line)
    assert m_lines.index("## 13. Amendments") < after
    ops_13 = [op for op in difflib.SequenceMatcher(a=m_lines, b=s_lines, autojunk=False).get_opcodes()
              if op[0] != "equal"]
    assert ops_13 and all(op[0] == "insert" and op[1] > after for op in ops_13), ops_13
    inserted_13 = "\n".join(line for op in ops_13 for line in s_lines[op[3]:op[4]])
    assert "*Amendment of 9 November 2026" in inserted_13
    blocks = [json.loads(b) for b in re.findall(r"^[ \t]*```json[ \t]*\n(.*?)\n[ \t]*```", inserted_13,
                                                 flags=re.S | re.M)]
    assert [list(b) for b in blocks] == [["smart_account_extension"]], [list(b) for b in blocks]
    # The amendment of gate B: insertions after the last line of the amendment of 9 November 2026 only, so that the
    # date check reads the heading of gate B and not the date of 9 November.
    text = (EXPERIMENTS / REVISION_REL).read_text(encoding="utf-8")
    assert "[GATE B:" not in text, f"{text.count('[GATE B:')} placeholders of the gate B draft are not filled"
    new_lines = lf_lines(text)
    end = max(i for i, line in enumerate(s_lines) if line.strip())
    ops = [op for op in difflib.SequenceMatcher(a=s_lines, b=new_lines, autojunk=False).get_opcodes()
           if op[0] != "equal"]
    assert ops and all(op[0] == "insert" for op in ops), [op for op in ops if op[0] != "insert"]
    assert all(op[1] > end for op in ops), "an insertion before the end of the amendment of 9 November 2026"
    inserted = "\n".join(line for op in ops for line in new_lines[op[3]:op[4]])
    heading = re.search(r"^- \*Amendment of (\d{1,2}) November 2026 \(gate B\)", inserted, flags=re.M)
    assert heading, "the amendment of gate B carries no dated heading '- *Amendment of <day> November 2026 (gate B)'"
    assert not inserted[:heading.start()].strip(), "text inserted before the heading of the amendment of gate B"
    assert 9 <= int(heading.group(1)) <= 30, heading.group(0)
    eval_files = tuple(last_json(run_py("import json, run_contract12m_pipeline as d; "
                                        "print(json.dumps(list(d.EVAL_FILES_B)))", "contract12m")))
    assert set(eval_files) <= set(re.findall(r"scripts/[a-z0-9_]+\.py", inserted))
    assert gate_b_amendment_files(text) == eval_files
    for fact in ("92c0b37c-0659-4f63-8aa7-0f335265d9fe", "f66a1ca1-d501-4011-ac63-3f46e0815825", "53,868,494,848",
                 "49,754,931,200"):
        assert fact in inserted, fact
    # The first item of the amendment: the pilot that 'Protocol fixed' pins, as that file records it (O8 ties the
    # block to the file); ρ is the pilot's, or the block's when no ρ of the grid was within the budget.
    block = protocol_fixed_json((EXPERIMENTS / PROTOCOL_REL).read_text(encoding="utf-8"))
    assert isinstance(block, dict), "docs/discovery_protocol.md holds no 'Protocol fixed' block (written at gate B)"
    pilot = json.loads((EXPERIMENTS / block["feasibility"]).read_text(encoding="utf-8"))
    items = [line for line in inserted.split("\n") if line.startswith("  - ")]
    first = items[0]
    assert first.startswith("  - When this amendment was made,"), first[:80]
    figures = [f"|U| = {pilot['U']:,},", f"|E_U| = {pilot['E_U']:,},", f"|WCC| = {pilot['WCC']:,},",
               f"|E_WCC| = {pilot['E_WCC']:,} and", f" {pilot['layers']['allow_capped']['edges']:,} capped allowance "
               "edges between contracts at t1",
               f" {100 * pilot['capped_allowance_in_edge_share']['U']:.2f}% of SCC ∪ OUT had a capped allowance "
               "in-edge;"]
    assert all(pilot[k] == pilot["sizes"][k] for k in ("U", "E_U", "WCC", "E_WCC"))
    rules = (f"q = {as_written(pilot['q'])} and the primary mode `{pilot['primary_mode']}`, as \"Protocol fixed\" "
             "records")
    if pilot["rho"] is None:
        figures += ["no ρ of the grid was within the budget, so the author chose ρ = "
                    f"{as_written(block['rho'])} ", f"its rules set {rules}"]
    else:
        figures.append(f"its rules set ρ = {as_written(pilot['rho'])}, {rules}")
    missing = [f for f in figures if f not in first]
    assert not missing, f"the first item of the amendment lacks {missing}"
    # The cap: the draft's sentence for the cap of USD 14 kept, or for the cap raised to the overlay's, which is not
    # below the cap that the check printed as needed (D1) and not above the budget
    if CAP == 14.0:
        assert "The cap of USD 14 stays." in inserted and "The cap of the campaign is raised" not in inserted, \
            "the overlay keeps the cap of USD 14, and the amendment does not say so in the draft's sentence"
    else:
        assert f"The cap of the campaign is raised to USD {CAP:g} (" in inserted, f"the amendment states no cap {CAP:g}"
        assert "The cap of USD 14 stays." not in inserted
        m = re.search(rf"The cap of the campaign is raised to USD {re.escape(f'{CAP:g}')} \([^)]*\bneed USD "
                      r"([0-9]+\.[0-9]{2})\b", inserted)
        assert m and float(m.group(1)) <= CAP <= 60.0, "the raised cap is not at least the cap needed, within USD 60"


FIXED_PROBE = r"""
    import json
    import common
    import crawl
    import run_contract12m_pipeline as d
    import run_discovery as rd

    cfg = common.load_config()
    out = {"block": rd.protocol_fixed(), "feasibility_rel": d.FEASIBILITY_REL, "manifest_rel": d.MANIFEST_REL}
    block = out["block"]
    if isinstance(block, dict):
        try:
            fixed = rd.check_fixed(block, rd.FEASIBILITY, rd.ROOT, cfg["discovery"])
            out["check_fixed"] = {k: (str(v) if k in ("rho", "q") else v) for k, v in fixed.items()}
        except SystemExit as e:
            out["check_fixed"] = str(e)
        try:
            d.gate_b_ready(cfg)
            out["gate_b_ready"] = True
        except SystemExit as e:
            out["gate_b_ready"] = str(e)
        counts = rd.pilot_counts(common.load_json(rd.FEASIBILITY)) if rd.FEASIBILITY.exists() else None
        if counts is not None:  # q and the mode from the block's sizes, with the pilot's own stop counts
            sizes = {k: block.get(k) for k in ("U", "E_U", "WCC", "E_WCC")}
            stops = {k: counts[k] for k in ("allow_capped_edges", "allow_in_share")}
            rules = crawl.rules({**sizes, **stops}, cfg["discovery"])
            out["rules"] = rd._clean(rules)
            out["q_matches"] = crawl.decimal(block["q"]) == crawl.decimal(rules["q"])
    print(json.dumps(out, default=str))
"""


def test_gate_b_state_protocol_fixed_block_is_valid():
    # O8 (protocol section 8; D14, D24; check L8): 'Protocol fixed' pins the pilot of the structure step, which
    # check_fixed and the driver's gate_b_ready accept, with q and the primary mode of the rules of protocol
    # section 7 on its sizes; the gate B commit tracks the pilot, byte for byte (D2), and the run manifest, whose
    # structure run wrote it.
    r = last_json(run_py(FIXED_PROBE, "contract12m"))
    block = r["block"]
    assert isinstance(block, dict), "docs/discovery_protocol.md holds no 'Protocol fixed' block (written at gate B)"
    fixed_keys = ("date", "feasibility", "sha256", "U", "E_U", "WCC", "E_WCC", "rho", "q", "primary_mode")
    decision = block.get("author_decision")
    optional = {"author_decision", "decision_covers"} & set(block)
    assert set(block) == set(fixed_keys) | optional
    assert decision is None or (isinstance(decision, str) and decision.strip())
    # The amendment of 9 November 2026 (revision section 13) limits the decision to go on to the one stop flag that
    # the pinned pilot set: decision_covers, with author_decision only, as check_fixed reads it.
    assert "decision_covers" not in block or decision is not None
    if decision is not None:
        assert block.get("decision_covers") == ["few_capped_allowance_in_edges"], block.get("decision_covers")
        assert r["check_fixed"]["decision_covers"] == ["few_capped_allowance_in_edges"], r["check_fixed"]
    assert date.fromisoformat(block["date"]) >= date(2026, 11, 7)
    assert block["feasibility"] == r["feasibility_rel"]
    assert re.fullmatch(r"[0-9a-f]{64}", block["sha256"])
    assert all(isinstance(block[k], int) and not isinstance(block[k], bool) for k in ("U", "E_U", "WCC", "E_WCC"))
    assert isinstance(r["check_fixed"], dict), r["check_fixed"]
    assert r["gate_b_ready"] is True, r["gate_b_ready"]
    assert r.get("rules"), "the pilot pinned by 'Protocol fixed' records no counts"
    assert r["q_matches"] and block["primary_mode"] == r["rules"]["primary_mode"], (block, r["rules"])
    m = json.loads((EXPERIMENTS / r["manifest_rel"]).read_text(encoding="utf-8"))
    assert m["results"]["structure"]["feasibility"]["sha256"] == block["sha256"]
    last = [e for e in m["steps"] if e["step"] == "structure"][-1]
    assert last.get("passed") is True or decision is not None
    for rel in (r["feasibility_rel"], r["manifest_rel"]):
        out = subprocess.run(["git", "ls-files", "--error-unmatch", "--", rel], cwd=EXPERIMENTS, capture_output=True)
        assert out.returncode == 0, f"{rel} is not tracked"
    head = w.git_blob("HEAD", r["manifest_rel"])
    assert head is not None and json.loads(head)["results"]["structure"]["feasibility"]["sha256"] == block["sha256"]
    # D2: the pilot is committed byte for byte, so the blob of HEAD is the pinned file on every checkout
    pilot = w.git_blob("HEAD", r["feasibility_rel"])
    assert pilot is not None and hashlib.sha256(pilot).hexdigest() == block["sha256"], \
        "the committed pilot is not the file 'Protocol fixed' pins (line ends converted?)"
    assert pilot == (EXPERIMENTS / r["feasibility_rel"]).read_bytes()


# --------------------------------------------------------------------------- gate B: the real data (slow, optional)


@slow
def test_earlier_evaluations_reproduce_their_committed_outputs(tmp_path):
    # O9: run_same_window, run_holdout and run_registered under usd12m on the real twelve-month tables (read only;
    # every output goes to a tmp PROC), with the code of d39775c and of this tree: the two summaries are
    # byte-identical, and so equal the tracked summary whenever the d39775c one does (a library version can change
    # bits; only the code is tested).
    graph = EXPERIMENTS / w.U12_REL
    if not list(graph.glob("nodes.part*.parquet")):
        pytest.skip("graph-tables-usd-12m is not on disk (the parquet data live on Drive)")
    exps = {"old": w.sandbox(tmp_path / "old", w.GATE_A), "new": w.sandbox(tmp_path / "new")}
    paths = {"GRAPH": graph, "GRAPH_U12": graph, "RAW": EXPERIMENTS / w.RAW_REL,
             "PROC_SHARED": EXPERIMENTS / w.PROC_SHARED_REL}
    for script, folder in (("run_same_window", "same-window"), ("run_holdout", "holdout-w0"),
                           ("run_registered", "window-w1")):
        got = {}
        for code, exp in exps.items():
            proc = tmp_path / f"proc_{code}"
            out = w.run_script(exp, script, "usd12m", traps=False, git_trap=True, paths={**paths, "PROC": proc},
                               timeout=6 * 3600)
            assert out.returncode == 0, f"{code} {script}:\n{out.stdout[-1500:]}\n{out.stderr[-3000:]}"
            got[code] = (proc / folder / "eval_summary.json").read_bytes()
        assert got["old"] == got["new"], script
        tracked = w.git_blob(w.GATE_A, f"{w.EARLIER_PROC_REL['usd12m']}/{folder}/eval_summary.json")
        if tracked is not None and lf_lines(tracked) == lf_lines(got["old"]):
            assert lf_lines(got["new"]) == lf_lines(tracked), script


@slow
def test_earlier_parquet_data_match_the_gate_a_drive_manifest():
    # O10: every file of the Drive manifest of d39775c under contract-reputation/ (experiments/data) outside the
    # contract12m folders, the ledger and the README files whose local copy exists keeps its size and MD5 (a text
    # file tracked in git may be checked out with other line ends than the uploaded copy: CRLF read as LF, or LF
    # written as CRLF, counts as the same file, as in O4).
    blob = w.git_blob(w.GATE_A, "drive-manifest.json")
    if blob is None:
        pytest.skip(f"commit {w.GATE_A} is not available")
    bad = []
    for f in json.loads(blob)["files"]:
        if not f["path"].startswith("contract-reputation/"):
            continue
        rel = f["path"][len("contract-reputation/"):]
        parts = rel.split("/")
        if rel == "bq_ledger.json" or parts[-1] == "README.md" or set(parts) & set(C12_FOLDERS):
            continue
        local = EXPERIMENTS / "data" / rel
        if not local.is_file():
            continue
        raw = local.read_bytes()
        lf = raw.replace(b"\r\n", b"\n")
        same = {(len(b), hashlib.md5(b).hexdigest()) for b in (raw, lf, lf.replace(b"\n", b"\r\n"))}
        if (f["size"], f["md5"]) not in same:
            bad.append(rel)
    assert not bad, bad


def test_usd12m_tables_equal_the_committed_manuscript_tables(tmp_path):
    # O11 (plan section 8; check M5): the tables export_latex writes under usd12m from the tracked twelve-month
    # summaries equal those the manuscript holds at its HEAD; a failure here with O1 passing points to a change
    # before gate B, not to gate B. Skipped without the manuscript submodule.
    thesis = EXPERIMENTS.parent / "dissertation" / "overleaf-github"
    summaries = EXPERIMENTS / w.EARLIER_PROC_REL["usd12m"]
    if not (thesis / ".git").exists() or not (summaries / "same-window" / "eval_summary.json").exists():
        pytest.skip("the manuscript submodule or the twelve-month summaries are not on disk")
    out = subprocess.run([sys.executable, "scripts/export_latex.py", "--tables-dir", str(tmp_path / "tables"),
                          "--figures-dir", str(tmp_path / "figures"), "--no-figures"], cwd=EXPERIMENTS,
                         env=w.variant_env("usd12m"), capture_output=True, text=True, encoding="utf-8", timeout=1800)
    assert out.returncode == 0, out.stdout[-2000:] + out.stderr[-3000:]
    written = sorted((tmp_path / "tables").glob("*.tex"))
    assert written
    differ = []
    for tex in written:
        head = subprocess.run(["git", "show", f"HEAD:results/tables/{tex.name}"], cwd=thesis, capture_output=True)
        if head.returncode != 0 or lf_lines(head.stdout) != lf_lines(tex.read_bytes()):
            differ.append(tex.name)
    assert not differ, differ
