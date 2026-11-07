"""The contract-graph variant as a whole (CONTRACT_REP_VARIANT=contract12m, docs/revision_contract_graph.md and
docs/discovery_protocol.md), beside the variants before it.

- the paths, the configuration and the run_bq.py budget of every variant, and the earlier variants against the
  scripts/common.py of the commit before this revision;
- the overlay check, the public views that run_bq.check_tables lets through, the table names and writes it
  refuses (and the jobs of the twelve-month driver it still accepts), and the frozen files;
- the gate A pieces fed into one another: the driver's typing command parsed and run by
  scripts/check_account_code.py, its output checked against the queue by the driver and read by the structure
  pilot of scripts/run_discovery.py, the pilot's edge counts against the driver's, the shared paths, and the
  free check step on fake metadata.

Nothing here reaches the network or BigQuery: the code of a variant runs in a subprocess (scripts/common.py
reads the variant once, at import), the RPC is a fake behind requests.Session.post, and the BigQuery client is
a fake that stops before any job."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import textwrap

import pyarrow.parquet as pq
import pytest
import yaml

from conftest import CONFIG_PATH, EXPERIMENTS, SCRIPTS

VARIANTS = ("registered", "usd", "usd12m", "contract12m")
OVERLAYS = {"usd12m": EXPERIMENTS / "config" / "overlay_usd12m.yaml",
            "contract12m": EXPERIMENTS / "config" / "overlay_contract12m.yaml"}
BASE = "69c7d12"  # the last commit of scripts/common.py and scripts/run_bq.py before this revision
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

    tmp, base_rev = Path(sys.argv[1]), (sys.argv[2:] or [None])[0]
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
    before = None
    if base_rev and common.VARIANT != "contract12m":
        src = subprocess.run(["git", "show", base_rev + ":./scripts/common.py"], cwd=common.ROOT,
                             capture_output=True, check=True).stdout
        base = types.ModuleType("common_base")
        base.__file__ = common.__file__  # the same ROOT
        exec(compile(src, common.__file__, "exec"), base.__dict__)
        names = ("VARIANT", "CONFIG_PATH", "DATA", "RAW", "PROC_SHARED", "USD_INPUTS", "GRAPH", "PROC", "PUB",
                 "USD_CONSTANTS", "BQ_PREFIX", "W1_DIR", "REVISED", "ONE_YEAR")
        before = {"differ": [n for n in names if getattr(base, n) != getattr(common, n)],
                  "same_config": base.load_config() == common.load_config()}
    print(json.dumps({"paths": paths, "flags": flags, "config": common.load_config(),
                      "settings": list(run_bq.settings()), "outcome": outcome, "ledger_jobs": jobs,
                      "before": before}))
"""


@pytest.fixture(scope="module")
def probes(tmp_path_factory) -> dict[str, dict]:
    base = [BASE] if _blob(BASE, "scripts/common.py") is not None else []
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


def test_the_registered_evaluation_refuses_the_contract_graph_variant():
    # The trader criteria are not applied in this variant (revision sections 2 and 11): run_registered.py, which
    # computes them, stops before it reads anything; the other variants keep TRADERS.
    out = run_py("import run_registered; run_registered.main()", "contract12m")
    assert out.returncode != 0 and "trader criteria" in out.stderr and "not written yet" in out.stderr
    for variant in ("registered", "usd", "usd12m"):
        r = run_py("import common; print(common.TRADERS)", variant)
        assert r.returncode == 0 and r.stdout.strip() == "True", variant


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
            "uncommitted": [sorted(files - set(d.COMMITTED)), sorted(files - set(rd.COMMITTED))]}))
    """, "contract12m"))
    assert r == {"queue": True, "types": True, "pilot_types": True, "struct": True, "feasibility": True,
                 "cohort": True, "labels": True, "audit_out": True, "audit_in": [True, True], "uncommitted": [[], []]}


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
    rep = rd.run_feasibility(cfg, struct=tmp / "struct_t1", types=d.TYPES, cohort=tmp / "cohort_t1",
                             labels=tmp / "labels_w0", out=tmp / "feasibility_t1.json")
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


# The check step of the driver on fake metadata: the source tables of the earlier builds and the public views
# exist with the columns the jobs read, no c12_ table exists yet. Before gate A it only warns and writes
# nothing; once the files are committed it records the check in the run manifest. One case per argument
# (state:campaign USD), each with its own manifest and ledger.
CASES = ("preview:0", "committed:0", "committed:13")
CHECK = r"""
    import contextlib, io, json, re, sys
    from datetime import datetime, timezone
    from pathlib import Path
    from types import SimpleNamespace
    from google.api_core.exceptions import NotFound
    import run_contract12m_pipeline as d
    from common import load_config

    sql32 = (d.ROOT / "sql" / "32_c12_bal_pre.sql").read_text(encoding="utf-8")
    literals = sorted(set(re.findall(r"'(0x[0-9a-f]{40})'", sql32)))
    when = datetime(2026, 10, 28, tzinfo=timezone.utc)

    def table(rows, schema, partitioned=False):
        tp = SimpleNamespace(type_="MONTH", field="block_timestamp") if partitioned else None
        return SimpleNamespace(num_rows=rows, num_bytes=10 * rows, time_partitioning=tp, modified=when, expires=None,
                               schema=[SimpleNamespace(name=n, field_type=t) for n, t in schema.items()])

    tables = {"logs_obs": table(10**9, {"block_timestamp": "TIMESTAMP"}, True),
              "logs_w1": table(10**8, {"block_timestamp": "TIMESTAMP"}, True),
              "u_tokens": table(5, {"token": "BYTES", "decimals": "INTEGER"}),
              "u_prices": table(5000, {"token": "BYTES", "day": "DATE", "price_usd": "FLOAT"}),
              "u12_cohort_tobs": table(6000, {"address": "BYTES"}), "u12_cohort_t1": table(6000, {"address": "BYTES"}),
              "u12_labels_w0": table(8000, {"wallet": "STRING"}), "u12_labels_w1": table(8000, {"wallet": "STRING"}),
              **{v: table(0, {c: "STRING" for c in d.VIEW_COLUMNS[k]}) for k, v in d.VIEWS.items()}}

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
    out = {}
    for case in sys.argv[2:]:
        state, campaign = case.split(":")
        tmp = Path(sys.argv[1]) / f"{state}-{campaign}"
        tmp.mkdir()
        d.MANIFEST, d.LEDGER = tmp / "run_manifest.json", tmp / "bq_ledger.json"
        d.LEDGER.write_text(json.dumps({"jobs": [{"usd": float(campaign), "label": "contract12m: earlier"}]}))
        changes = "" if state == "committed" else " M scripts/crawl.py"
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
    if float(campaign):
        assert r["result"].startswith("check failed") and "cap of USD 14.00" in r["result"]
    else:
        assert r["result"] == "passed" and "check passed" in r["stdout"]
    if state == "preview":
        assert "warning: not committed" in r["stdout"] and "not recorded in run_manifest.json" in r["stdout"]
        assert r["manifest"] is None
    else:
        (entry,) = r["manifest"]["checks_run"]
        assert entry["head"] == "abc123" and entry["existing_c12"] == []
        assert bool(entry["problems"]) == bool(float(campaign))
        assert entry["estimates"]["logs5"]["missing"] == [] and "c12_logs5" in entry["waits"]["ends"]
        assert set(entry["waits"]) == {k for k in entry["estimates"] if k not in ("logs5", "anchor_blocks")}
