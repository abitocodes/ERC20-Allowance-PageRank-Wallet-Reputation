"""scripts/check_account_code.py: the registered usage, unchanged, and the account-type reads of the
contract-graph revision (docs/revision_contract_graph.md sections 4.2 and 4.3). The RPC is mocked at
requests.Session.post: no test reaches the network."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
import subprocess
import sys
import textwrap
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

import pandas as pd
import pyarrow.parquet as pq
import pytest
import requests
import yaml

from conftest import CONFIG_PATH, EXPERIMENTS, SCRIPTS
import check_account_code as cac
from common import part_paths, read_parts, write_parts

OLD_REV = "1747e64"  # the last commit of the registered version of the script
PUBLIC = "https://public.example/rpc"
OTHER = "https://other.example/v1/rpc"
SECRET_URL = "https://user:pw-SECRET@provider.example/v2/KEY-SECRET?apikey=Q-SECRET"
USDC = cac.PROBE_ADDRESS
SLOT = "360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
EP06 = "0x5ff137d4b0fdcd49dca30c7cf57e578a026d2789"
EP07 = "0x0000000071727de22e5e9d8baf0edac6f37da032"
REVERT = {"error": {"code": 3, "message": "execution reverted"}}
GET_THRESHOLD, GET_OWNERS, ENTRY_POINT = "0xe75235b8", "0xa0e67e2b", "0xb0d691fe"


def addr(n: int) -> str:
    return f"0x{n:040x}"


def clone(impl: str) -> str:
    return "0x363d3d373d3d3d363d73" + impl[2:] + "5af43d82803e903d91602b57fd5bf3"


PLAIN = "0x6080604052348015600f57600080fd5b"
# The runtime code of the GnosisSafeProxy of v1.3.0 (its metadata tail stands for any): masterCopy() as the
# top four bytes of a PUSH32 word. Every Safe proxy of a version has this code; the singleton sits in slot 0.
SAFE_PROXY = ("0x608060405273ffffffffffffffffffffffffffffffffffffffff600054167fa619486e000000000000000000000000"
              "0000000000000000000000000000000060003514156050578060005260206000f35b3660008037600080366000845af4"
              "3d6000803e60008114156070573d6000fd5b3d6000f3fea2646970667358221220d1429297349653a4918076d650332de1"
              "a1068c5f3e07c5c82360c277770b955264736f6c63430007060033")
SAFE_PROXY_PUSH4 = "0x608060405273ffffffffffffffffffffffffffffffffffffffff6000541663a619486e"   # the PUSH4 form
MULTISIG = "0x6080604052" + "63e75235b8" + "146100"   # not a Safe, but answers getThreshold()
SINGLETON = "0x6080604052600436106100" + "63e75235b8" + "63a0e67e2b"
ERC1967_PROXY = "0x608060405261" + "7f" + SLOT + "545af43d"
ACCOUNT_V06 = "0x6080604052" + "633a871cdd" + "146100"
ACCOUNT_V07 = "0x6080604052" + "6319822f7c" + "146110"
PAYMASTER = ACCOUNT_V07 + "6352b7512c" + "14"
DELEGATED = "0xef0100" + "11" * 20
O1, O2 = addr(0xA1), addr(0xA2)


def uint(v: int) -> dict:
    return {"result": "0x" + v.to_bytes(32, "big").hex()}


def address_word(a: str) -> dict:
    return {"result": "0x" + "00" * 12 + a[2:]}


def address_array(items: list[str]) -> dict:
    data = (32).to_bytes(32, "big") + len(items).to_bytes(32, "big")
    data += b"".join(bytes(12) + bytes.fromhex(a[2:]) for a in items)
    return {"result": "0x" + data.hex()}


class FakeResponse:
    def __init__(self, status: int, body=None, text: str = ""):
        self.status_code, self.body, self.text = status, body, text

    def json(self):
        return self.body


class FakeChain:
    """JSON-RPC hosts in memory: code, ERC-1967 slots, Safe singletons (slot 0) and eth_call answers, the
    blocks a host does not serve, faults, and every call received and answered."""

    def __init__(self, latest: int = 0x5000):
        self.latest = latest
        self.code = {USDC: "0x6080604052"}
        self.slots: dict[str, str] = {}                    # address -> ERC-1967 implementation
        self.slot0: dict[str, str] = {}                    # address -> Safe singleton in storage slot 0
        self.answers: dict[tuple[str, str], dict] = {}     # (to, selector) -> answer; others revert
        self.unserved: dict[str, set[int]] = {}            # host -> blocks answered with an error
        self.empty: dict[str, set[int]] = {}               # host -> blocks answered with no code
        self.fault = None                                  # (host, payload) -> response, exception or None
        self.received: Counter = Counter()                 # host -> JSON-RPC calls received
        self.answered: list[tuple[str, str, list]] = []    # (host, method, params)

    def post(self, url: str, payload) -> FakeResponse:
        host = urlsplit(url).hostname
        items = payload if isinstance(payload, list) else [payload]
        self.received[host] += len(items)
        if self.fault is not None:
            res = self.fault(host, items)
            if isinstance(res, BaseException):
                raise res
            if res is not None:
                return res
        out = [self.answer(host, it) for it in items]
        return FakeResponse(200, out if isinstance(payload, list) else out[0])

    def answer(self, host: str, item: dict) -> dict:
        method, params = item["method"], item["params"]
        self.answered.append((host, method, params))
        head = {"jsonrpc": "2.0", "id": item["id"]}
        if method == "eth_blockNumber":
            return {**head, "result": hex(self.latest)}
        block = int(params[-1], 16)
        if block in self.unserved.get(host, ()):
            return {**head, "error": {"code": -32000, "message": "missing trie node"}}
        if method == "eth_getCode":
            empty = block in self.empty.get(host, ())
            return {**head, "result": "0x" if empty else self.code.get(params[0], "0x")}
        if method == "eth_getStorageAt":
            store = {"0x" + SLOT: self.slots, cac.SAFE_SLOT: self.slot0}[params[1]]   # no other slot is read
            impl = store.get(params[0])
            return {**head, "result": "0x" + ("00" * 12 + impl[2:] if impl else "00" * 32)}
        if method == "eth_call":
            return {**head, **self.answers.get((params[0]["to"], params[0]["data"]), REVERT)}
        raise AssertionError(method)

    def calls(self, method: str) -> list[list]:
        return [p for _, m, p in self.answered if m == method]

    def code_reads(self) -> list[str]:
        """Addresses read with eth_getCode, without the block probes."""
        return [p[0] for p in self.calls("eth_getCode") if p[0] != USDC]

    def storage_reads(self, slot: str) -> list[str]:
        """Addresses whose storage ``slot`` was read, in address order."""
        return sorted(p[0] for p in self.calls("eth_getStorageAt") if p[1] == slot)

    def call_targets(self) -> set[str]:
        return {p[0]["to"] for p in self.calls("eth_call")}


@pytest.fixture
def chain(monkeypatch) -> FakeChain:
    fake = FakeChain()

    def post(session, url, json=None, timeout=None, **kwargs):
        return fake.post(url, json)

    monkeypatch.setattr(requests.Session, "post", post)
    monkeypatch.delenv(cac.ENV_URL, raising=False)
    monkeypatch.setattr(cac, "BACKOFF_CAP", 0.0)
    monkeypatch.setattr(cac, "SAVE_SECONDS", 0.0)
    return fake


@pytest.fixture(scope="module")
def cfg12() -> dict:
    """The configuration under CONTRACT_REP_VARIANT=contract12m, merged as scripts/common.py merges it."""
    cfg = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    overlay = yaml.safe_load((EXPERIMENTS / "config" / "overlay_contract12m.yaml").read_text(encoding="utf-8"))
    for section, values in overlay.items():
        cfg.setdefault(section, {}).update(values)
    return cfg


@pytest.fixture(scope="module")
def rules(cfg12) -> cac.Rules:
    return cac.Rules.from_config(cfg12["contract_graph"])


@pytest.fixture
def variant12(monkeypatch, cfg12) -> None:
    monkeypatch.setattr(cac, "load_config", lambda: copy.deepcopy(cfg12))


def csv_input(tmp_path: Path, addresses: list[str], name: str = "in.csv") -> Path:
    path = tmp_path / name
    pd.DataFrame({"address": addresses}).to_csv(path, index=False)
    return path


def run(*args) -> int:
    return cac.main([str(a) for a in args])


def meta_of(stem: Path) -> dict:
    return json.loads(stem.with_suffix(".json").read_text(encoding="utf-8"))


# --- pure functions -----------------------------------------------------------------------------

@pytest.mark.parametrize("code,kind", [
    (None, "none"), ("0x", "none"), ("0x0", "none"), ("0X", "none"),
    (DELEGATED, "eip7702"), ("0xEF0100" + "AB" * 20, "eip7702"),
    ("0xef0100" + "11" * 19, "contract"), ("0xef0100" + "11" * 21, "contract"), ("0xef0200" + "11" * 20, "contract"),
    ("0x00", "contract"), (PLAIN, "contract"),
])
def test_code_kind(code, kind):
    assert cac.code_kind(code, "0xef0100") == kind


def test_eip1167_and_erc1967_are_recognised_from_the_code(rules):
    impl = addr(0x9001)
    code = bytes.fromhex(clone(impl)[2:])
    assert len(code) == 45 and cac.eip1167_implementation(code) == impl
    assert cac.eip1167_implementation(code + b"\x00\x2a") == impl      # a clone with immutable arguments
    assert cac.eip1167_implementation(b"\x60" + code) == ""            # the pattern inside other code
    assert cac.eip1167_implementation(code[:44]) == ""
    assert cac.code_features(code, rules)[:2] == ("eip1167", impl)
    assert cac.code_features(bytes.fromhex(ERC1967_PROXY[2:]), rules)[:2] == (None, "")   # its slot is read
    assert cac.code_features(bytes.fromhex(PLAIN[2:]), rules)[:2] == ("none", "")


def hexcode(code: str) -> bytes:
    return bytes.fromhex(code[2:])


@pytest.mark.parametrize("code,found", [
    (SAFE_PROXY, True),                                                # PUSH32, as the Safe proxies compile it
    (SAFE_PROXY_PUSH4, True),                                          # PUSH4
    ("0x6080" + "7f" + "a619486e" + "00" * 28 + "6000", True),
    ("0x6080" + "7f" + "a519486e" + "00" * 28, False),                 # another selector
    ("0x6080" + "63" + "a519486e", False),
    ("0x6080" + "7f" + "a619486e" + "00" * 27 + "01", False),          # PUSH32 with non-zero low bytes
    ("0x6080" + "7f" + "a619486e" + "11" * 28, False),
    ("0x6080" + "62" + "a619486e", False),                             # PUSH3, not PUSH4
    ("0x6080" + "a619486e" + "00" * 28, False),                        # no push byte
    (PLAIN, False),
])
def test_master_copy_selector_is_recognised_in_both_push_forms(rules, code, found):
    assert cac.has_master_copy(hexcode(code)) is found
    kind, impl, mc = cac.code_features(hexcode(code), rules)[:3]
    assert (kind, impl, mc) == ("safe" if found else "none", "", found)


def test_proxy_kind_of_a_safe_proxy(rules):
    impl = addr(0x9001)
    clone_with_selector = hexcode(clone(impl)) + hexcode(SAFE_PROXY_PUSH4)    # immutable arguments that hold it
    assert cac.code_features(clone_with_selector, rules)[:3] == ("eip1167", impl, True)
    both = hexcode(ERC1967_PROXY) + hexcode(SAFE_PROXY_PUSH4)
    assert cac.code_features(both, rules)[:3] == (None, "", True)             # pending until its slot is read
    assert cac.proxy_after_slot(True, True) == "erc1967"
    assert cac.proxy_after_slot(False, True) == "safe"
    assert cac.proxy_after_slot(False, False) == "none"


def test_push4_tests_need_the_push4_byte(rules):
    def flags(code: str) -> tuple[bool, bool]:
        return cac.code_features(bytes.fromhex(code[2:]), rules)[3:]

    assert flags(ACCOUNT_V06) == (True, False)
    assert flags(ACCOUNT_V07) == (True, False)
    assert flags(PAYMASTER) == (True, True)
    assert flags("0x6080" + "6219822f7c") == (False, False)           # PUSH3, not PUSH4
    assert flags(PLAIN) == (False, False)


@pytest.mark.parametrize("threshold,owners,expected", [   # the decoded answers are recorded whatever the kind
    (uint(1), address_array([O1]), (1, 1, "safe")),
    (uint(1000), address_array([O1, O2]), (1000, 2, "safe")),
    (uint(0), address_array([O1]), (0, 1, "")),                        # a Safe proxy never set up
    (uint(0), address_array([]), (0, 0, "")),
    (uint(1001), address_array([O1]), (1001, 1, "")),
    (uint(1), address_array([]), (1, 0, "")),                          # a Safe singleton has no owners
    (uint(2**63 - 1), address_array([O1]), (2**63 - 1, 1, "")),
    (uint(2**63), address_array([O1]), (cac.INT64_MAX, 1, "")),        # capped for the int64 column
    (uint(2**256 - 1), REVERT, (cac.INT64_MAX, -1, "")),
    (REVERT, address_array([O1]), (-1, 1, "")),
    (uint(2), REVERT, (2, -1, "")),
    ({"result": "0x" + "00" * 30 + "02"}, address_array([O1]), (-1, 1, "")),   # 31 bytes
    ({"result": uint(2)["result"] + "00"}, address_array([O1]), (-1, 1, "")),  # 33 bytes
    (uint(2), {"result": "0x" + "00" * 31 + "20"}, (2, -1, "")),               # no length word
    (uint(2), {"result": address_array([O1, O2])["result"][:-64]}, (2, -1, "")),  # an owner short
    (uint(2), {"result": address_array([O1])["result"][:-64] + "ff" + "00" * 11 + O1[2:]}, (2, -1, "")),
])
def test_safe_test(rules, threshold, owners, expected):
    t, n, _, wallet = cac.evaluate([threshold, owners, REVERT], False, False, rules)
    assert (t, n, wallet) == expected


@pytest.mark.parametrize("entry,vu,pm,kind", [
    (address_word(EP07), True, False, "erc4337"),
    (address_word(EP06), True, False, "erc4337"),
    (address_word("0x4337084d9e255ff0702461cf8895ce9e3b5ff108"), True, False, "erc4337"),
    (address_word(addr(0x4337)), True, False, ""),                     # not a canonical EntryPoint
    (address_word(EP07), False, False, ""),                            # no validateUserOp selector
    (address_word(EP07), True, True, ""),                              # a paymaster selector excludes
    (REVERT, True, False, ""),
    ({"result": address_word(EP07)["result"] + "00"}, True, False, ""),
])
def test_erc4337_test(rules, entry, vu, pm, kind):
    threshold, n_owners, entry_point, wallet = cac.evaluate([REVERT, REVERT, entry], vu, pm, rules)
    assert wallet == kind and (threshold, n_owners) == (-1, -1)
    data = entry.get("result", "")
    assert entry_point == ("0x" + data[-40:] if len(data) == 66 else "")


TIMEOUT = {"error": {"code": -32000, "message": "execution aborted (timeout = 5s)"}}


def test_call_failures_are_told_from_rpc_errors():
    assert cac.is_call_failure({"code": 3, "message": "execution reverted: GS000", "data": "0x08c379a0"})
    assert cac.is_call_failure({"code": -32000, "message": "execution reverted"})
    assert cac.is_call_failure({"code": -32000, "message": "invalid opcode: INVALID"})
    assert cac.is_call_failure({"code": -32000, "message": "stack underflow (0 <=> 1)"})
    assert cac.is_call_failure({"code": -32000, "message": "stack limit reached 1024 (1023)"})
    assert cac.is_call_failure({"code": -32000, "message": "out of gas"})
    # The node's abort at its time limit is not the account's answer: the batch is sent again.
    assert not cac.is_call_failure(TIMEOUT["error"]) and cac.is_aborted_error(TIMEOUT["error"])
    assert cac.is_aborted(TIMEOUT) and not cac.is_aborted(REVERT) and not cac.is_aborted(uint(1))
    assert not cac.is_call_failure({"code": -32005, "message": "rate limit exceeded"})
    assert not cac.is_call_failure({"code": -32000, "message": "header not found"})
    assert not cac.is_call_failure({"code": -32000, "message": "missing trie node"})
    assert not cac.is_call_failure({"code": -32603, "message": "Internal error"})
    # An EVM word inside an RPC message does not make it the call's failure; the message must begin with it.
    assert not cac.is_call_failure({"code": -32000, "message": "upstream request reverted by the gateway"})
    assert not cac.is_call_failure({"code": -32000, "message": "request failed: out of gas allowance quota"})


def test_batch_answers_are_matched_by_id():
    def failure(k, e):
        return cac.is_call_failure(e)

    ok = [{"jsonrpc": "2.0", "id": 1, "result": "0x2"}, {"jsonrpc": "2.0", "id": 0, "result": "0x1"}]
    assert [a["result"] for a in cac.parse_batch(ok, 2, cac.is_quantity, None)[0]] == ["0x1", "0x2"]
    assert cac.parse_batch({"id": 0, "result": "0x1"}, 1, cac.is_quantity, None)[0] == [{"id": 0, "result": "0x1"}]
    assert cac.parse_batch(ok[:1], 2, cac.is_quantity, None)[0] is None                  # an answer missing
    assert cac.parse_batch([{"id": 0, "result": None}], 1, cac.is_quantity, None)[0] is None
    reverted = [{"id": 0, **REVERT}]
    assert cac.parse_batch(reverted, 1, cac.is_quantity, None)[0] is None                # sent again
    assert cac.parse_batch(reverted, 1, cac.is_quantity, failure)[0] == reverted
    limited = [{"id": 0, "error": {"code": -32005, "message": "rate limit exceeded"}}]
    assert cac.parse_batch(limited, 1, cac.is_quantity, failure)[0] is None
    # failed(k, error) is asked about the call k: here only the second call may fail.
    two = [{"id": 0, **REVERT}, {"id": 1, **REVERT}]
    assert cac.parse_batch(two, 2, cac.is_quantity, lambda k, e: k == 1)[0] is None
    assert cac.parse_batch(two[1:] + [{"id": 0, "result": "0x1"}], 2, cac.is_quantity, lambda k, e: k == 1)[0]


def test_rpc_urls_and_hosts(monkeypatch, cfg12):
    monkeypatch.delenv(cac.ENV_URL, raising=False)
    assert cac.rpc_urls(None, cfg12, use_env=True) == [cfg12["accounts"]["rpc_url"]]
    assert cac.rpc_urls([OTHER, PUBLIC, OTHER], cfg12, use_env=True) == [OTHER, PUBLIC]
    monkeypatch.setenv(cac.ENV_URL, SECRET_URL)
    assert cac.rpc_urls([PUBLIC], cfg12, use_env=True) == [SECRET_URL, PUBLIC]
    assert cac.rpc_urls(None, cfg12, use_env=True) == [SECRET_URL, cfg12["accounts"]["rpc_url"]]
    # The registered usage never reads the variable.
    assert cac.rpc_urls(None, cfg12, use_env=False) == [cfg12["accounts"]["rpc_url"]]
    assert cac.rpc_urls([PUBLIC], cfg12, use_env=False) == [PUBLIC]
    assert cac.host_of(SECRET_URL) == "provider.example"
    assert cac.host_of("http://localhost:8547/") == "localhost:8547"
    monkeypatch.setenv(cac.ENV_URL, "provider.example/v2/KEY-SECRET")
    with pytest.raises(SystemExit) as exc:
        cac.rpc_urls([PUBLIC], cfg12, use_env=True)
    assert "SECRET" not in str(exc.value)
    args = cac.parse_args(["in.csv", "out", "--rpc", OTHER, PUBLIC, "--rpc", SECRET_URL])
    assert args.rpc == [OTHER, PUBLIC, SECRET_URL] and (args.workers, args.batch) == (4, 25)


def test_overlay_settings_reach_the_rules():
    code = textwrap.dedent("""
        import json, check_account_code as c
        from common import load_config
        r = c.Rules.from_config(load_config()["contract_graph"])
        print(json.dumps({"slot": r.slot_hex, "eps": sorted(r.entry_points), "max": r.threshold_max,
                          "calls": list(r.calls), "vu": [x.hex() for x in r.validate_user_op],
                          "pm": [x.hex() for x in r.validate_paymaster]}))
    """)
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "CONTRACT_REP_VARIANT": "contract12m"}
    out = subprocess.run([sys.executable, "-c", code], cwd=SCRIPTS, env=env, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert json.loads(out.stdout) == {
        "slot": "0x" + SLOT, "max": 1000, "calls": [GET_THRESHOLD, GET_OWNERS, ENTRY_POINT],
        "eps": sorted([EP06, EP07, "0x4337084d9e255ff0702461cf8895ce9e3b5ff108",
                       "0x433709009b8330fda32311df1c2afa402ed8d009"]),
        "vu": ["633a871cdd", "6319822f7c"], "pm": ["63f465c77e", "6352b7512c"]}


# --- the registered usage -----------------------------------------------------------------------

def old_script(tmp_path: Path, monkeypatch):
    src = subprocess.run(["git", "show", f"{OLD_REV}:./scripts/check_account_code.py"], cwd=EXPERIMENTS,
                         capture_output=True)
    if src.returncode != 0:
        pytest.skip(f"commit {OLD_REV} is not available")
    path = tmp_path / "old_check_account_code.py"
    path.write_bytes(src.stdout)
    monkeypatch.setattr(sys, "path", list(sys.path))
    spec = importlib.util.spec_from_file_location("old_check_account_code", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


R1, R2, R3, R4, R5 = ("0x" + t * 20 for t in ("a1", "b2", "c3", "d4", "e5"))
REGISTERED = [R3, "0x" + R1[2:].upper(), R2, R4, R1, R5]


def registered_chain(chain: FakeChain) -> None:
    chain.code.update({R2: DELEGATED, R3: PLAIN, R5: "0x0"})


def test_registered_usage_writes_what_the_old_script_wrote(tmp_path, chain, monkeypatch):
    old = old_script(tmp_path, monkeypatch)
    registered_chain(chain)
    inp = csv_input(tmp_path, REGISTERED)
    monkeypatch.setattr(sys, "argv", ["check_account_code.py", str(inp), str(tmp_path / "old"), "--column", "address"])
    assert old.main() == 0
    old_hosts = set(chain.received)
    chain.received.clear()
    assert run(inp, tmp_path / "new", "--column", "address") == 0
    assert set(chain.received) == old_hosts == {"arb1.arbitrum.io"}    # accounts.rpc_url
    a, b = (pq.read_table(part_paths(tmp_path / s)[0]) for s in ("old", "new"))
    assert b.column_names == cac.BASE_COLUMNS and a.equals(b) and a.schema.equals(b.schema)
    assert read_parts(tmp_path / "new")["account_class"].tolist() == ["eoa", "eoa_7702", "contract", "eoa", "eoa"]
    m_old, m_new = meta_of(tmp_path / "old"), meta_of(tmp_path / "new")
    for key in ("block_number", "block_hex", "counts", "n"):
        assert m_old[key] == m_new[key], key
    assert m_new["rpc"] == "arb1.arbitrum.io" and m_new["pinned_requested"] is None and m_new["complete"]
    assert "resume_key" not in m_new and "rules" not in m_new and "served_by" not in m_new


def test_registered_usage_never_reads_the_provider_variable(tmp_path, chain, monkeypatch):
    # Set for the reads of the contract-graph revision, the variable must not redirect the registered usage
    # (no --block, no --probe-wallets), which reads accounts.rpc_url as the committed script did.
    registered_chain(chain)
    monkeypatch.setenv(cac.ENV_URL, SECRET_URL)
    inp = csv_input(tmp_path, REGISTERED)
    assert run(inp, tmp_path / "types") == 0
    assert set(chain.received) == {"arb1.arbitrum.io"}
    assert meta_of(tmp_path / "types")["rpc"] == "arb1.arbitrum.io"
    # A resumed registered output stays on accounts.rpc_url as well.
    chain.received.clear()
    assert run(csv_input(tmp_path, REGISTERED + [addr(0xBEEF)], "more.csv"), tmp_path / "types") == 0
    assert set(chain.received) == {"arb1.arbitrum.io"}
    # The reads of the revision put the provider first.
    chain.received.clear()
    assert run(inp, tmp_path / "pinned", "--block", 100) == 0
    assert set(chain.received) == {"provider.example", "arb1.arbitrum.io"}
    assert meta_of(tmp_path / "pinned")["rpc"] == "provider.example"


def test_output_of_the_old_script_resumes(tmp_path, chain, monkeypatch):
    old = old_script(tmp_path, monkeypatch)
    registered_chain(chain)
    monkeypatch.setattr(sys, "argv", ["x", str(csv_input(tmp_path, REGISTERED, "all.csv")), str(tmp_path / "ref")])
    assert old.main() == 0
    monkeypatch.setattr(sys, "argv", ["x", str(csv_input(tmp_path, REGISTERED[:3], "first.csv")), str(tmp_path / "out")])
    assert old.main() == 0
    chain.answered.clear()
    assert run(tmp_path / "all.csv", tmp_path / "out") == 0
    assert sorted(chain.code_reads()) == [R4, R5]
    pd.testing.assert_frame_equal(read_parts(tmp_path / "out"), read_parts(tmp_path / "ref"))


# --- pass 2 -------------------------------------------------------------------------------------

E1, D1, C1, C2 = addr(0x1001), addr(0x1002), addr(0x1003), addr(0x1004)
S1, S2, S3, G1 = addr(0x2001), addr(0x2002), addr(0x2003), addr(0x2100)
K1, K2 = addr(0x3001), addr(0x3002)
P1, P2, P3, P4 = addr(0x4001), addr(0x4002), addr(0x4003), addr(0x4004)
A1, M1 = addr(0x5001), addr(0x5002)
T1, T2, T3 = addr(0x6001), addr(0x6002), addr(0x6003)
IMPL_A, IMPL_B = addr(0x9001), addr(0x9002)
WORLD = [M1, P4, E1, T2, S3, K2, P2, D1, C1, S1, T3, G1, K1, P1, C2, S2, P3, A1, T1]
EXPECTED = {  # address: (code_kind, proxy_kind, implementation, wallet_kind, account_class, threshold, n_owners)
    E1: ("none", "none", "", "", "eoa", -1, -1),
    D1: ("eip7702", "none", "", "", "eoa_7702", -1, -1),
    C1: ("contract", "none", "", "", "contract", -1, -1),
    C2: ("contract", "none", "", "", "contract", -1, -1),             # copied from C1: no getThreshold() word
    S1: ("contract", "safe", G1, "", "contract", 0, 0),               # the lowest Safe proxy, never set up
    S2: ("contract", "safe", G1, "safe", "smart_account", 2, 2),      # Safe proxies are probed one by one
    S3: ("contract", "safe", G1, "safe", "smart_account", 1, 1),      # (their singleton G1 sits in slot 0)
    G1: ("contract", "none", "", "", "contract", 1, 0),               # threshold 1 but no owners
    T1: ("contract", "none", "", "", "contract", 0, -1),              # answers getThreshold(): the hash is
    T2: ("contract", "none", "", "safe", "smart_account", 3, 2),      # probed address by address
    T3: ("contract", "none", "", "", "contract", -1, -1),
    K1: ("contract", "eip1167", IMPL_A, "erc4337", "smart_account", -1, -1),
    K2: ("contract", "eip1167", IMPL_A, "erc4337", "smart_account", -1, -1),   # copied from K1
    P1: ("contract", "erc1967", IMPL_A, "erc4337", "smart_account", -1, -1),
    P2: ("contract", "erc1967", IMPL_A, "", "contract", -1, -1),      # same code, another EntryPoint
    P3: ("contract", "erc1967", IMPL_B, "", "contract", -1, -1),      # implementation with a paymaster selector
    P4: ("contract", "none", "", "", "contract", -1, -1),             # empty slot: not a proxy
    A1: ("contract", "none", "", "erc4337", "smart_account", -1, -1),
    M1: ("contract", "none", "", "", "contract", -1, -1),             # own paymaster selector
}


def world(chain: FakeChain) -> None:
    chain.code.update({D1: DELEGATED, C1: PLAIN, C2: PLAIN, S1: SAFE_PROXY, S2: SAFE_PROXY, S3: SAFE_PROXY,
                       G1: SINGLETON, T1: MULTISIG, T2: MULTISIG, T3: MULTISIG,
                       K1: clone(IMPL_A), K2: clone(IMPL_A), P1: ERC1967_PROXY, P2: ERC1967_PROXY,
                       P3: ERC1967_PROXY, P4: ERC1967_PROXY, A1: ACCOUNT_V06, M1: PAYMASTER,
                       IMPL_A: ACCOUNT_V07, IMPL_B: PAYMASTER})
    chain.slots.update({P1: IMPL_A, P2: IMPL_A, P3: IMPL_B})
    chain.slot0.update({S1: G1, S2: G1, S3: G1})
    chain.answers.update({
        (S1, GET_THRESHOLD): uint(0), (S1, GET_OWNERS): address_array([]),
        (S2, GET_THRESHOLD): uint(2), (S2, GET_OWNERS): address_array([O1, O2]),
        (S3, GET_THRESHOLD): uint(1), (S3, GET_OWNERS): address_array([O2]),
        (G1, GET_THRESHOLD): uint(1), (G1, GET_OWNERS): address_array([]),
        (T1, GET_THRESHOLD): uint(0), (T2, GET_THRESHOLD): uint(3), (T2, GET_OWNERS): address_array([O1, O2]),
        (K1, ENTRY_POINT): address_word(EP07), (P1, ENTRY_POINT): address_word(EP07),
        (P2, ENTRY_POINT): address_word(addr(0x4337)), (P3, ENTRY_POINT): address_word(EP07),
        (P4, ENTRY_POINT): address_word(EP07), (A1, ENTRY_POINT): address_word(EP06),
        (M1, ENTRY_POINT): address_word(EP07),
    })


@pytest.mark.parametrize("workers,batch", [(1, 25), (4, 2)])
def test_probe_wallets(tmp_path, chain, variant12, workers, batch):
    world(chain)
    stem = tmp_path / "types"
    assert run(csv_input(tmp_path, WORLD), stem, "--probe-wallets", "--rpc", PUBLIC, "--workers", workers,
               "--batch", batch) == 0
    df = read_parts(stem)
    assert list(df.columns) == cac.PROBE_COLUMNS and not df.isna().any().any()
    assert df["address"].tolist() == sorted(WORLD)
    table = pq.read_table(part_paths(stem)[0])
    assert table.schema.remove_metadata().equals(cac.PROBE_SCHEMA)
    rows = df.set_index("address")
    for a, (kind, proxy, impl, wallet, cls, threshold, n_owners) in EXPECTED.items():
        r = rows.loc[a]
        assert (r.code_kind, r.proxy_kind, r.implementation, r.wallet_kind, r.account_class, r.threshold,
                r.n_owners) == (kind, proxy, impl, wallet, cls, threshold, n_owners), a
        code = bytes.fromhex(chain.code[a][2:]) if a in chain.code and chain.code[a] != "0x0" else b""
        assert r.code_size == len(code) and r.code_hash == (cac.keccak_hex(code) if code else ""), a
    assert rows.loc[K1, "entry_point"] == EP07 and rows.loc[P2, "entry_point"] == addr(0x4337)
    assert rows.loc[S1, "entry_point"] == "" and rows.loc[E1, "entry_point"] == ""
    assert rows.loc[[P1, P2, K1], "has_validate_userop"].all() and not rows.loc[[P1, P2], "has_paymaster_selector"].any()
    assert rows.loc[P3, "has_paymaster_selector"] and not rows.loc[[P4, C1], "has_validate_userop"].any()
    assert set(rows.index[rows["has_master_copy"]]) == {S1, S2, S3}
    # Address by address: ERC-1967 proxies, Safe proxies and the hash whose representative T1 answered
    # getThreshold(); one representative for every other hash; implementations once (the Safe singleton G1
    # among them); the ERC-1967 slots of the codes that hold the constant, and slot 0 of the Safe proxies only.
    assert chain.call_targets() == {C1, S1, S2, S3, G1, T1, T2, T3, K1, P1, P2, P3, P4, A1, M1}
    assert len(chain.calls("eth_call")) == 3 * 15
    assert chain.storage_reads("0x" + SLOT) == [P1, P2, P3, P4]
    assert chain.storage_reads(cac.SAFE_SLOT) == [S1, S2, S3]
    assert len(chain.calls("eth_getStorageAt")) == 7
    assert sorted(chain.code_reads()) == sorted(WORLD + [IMPL_A, IMPL_B, G1])
    meta = meta_of(stem)
    assert meta["complete"] and meta["pending"] == 0 and meta["n"] == len(WORLD)
    assert meta["counts_wallet_kind"] == {"": 12, "erc4337": 4, "safe": 3}
    assert meta["counts_account_class"] == {"smart_account": 7, "contract": 10, "eoa": 1, "eoa_7702": 1}
    assert meta["counts_proxy_kind"] == {"none": 11, "erc1967": 3, "safe": 3, "eip1167": 2}
    assert meta["probes"] == {"storage_reads": 4, "safe_slots": 3, "implementations": 3, "representatives": 7,
                              "erc1967": 3, "safe_proxies": 3, "threshold_hashes": 2, "copied": 2}
    assert meta["aborted_addresses"] == []
    assert meta["rpc_calls"] == dict(chain.received)
    assert meta["rules"]["safe_slot"] == cac.SAFE_SLOT and set(meta["resume_key"]) == set(cac.KEY_PARTS)


@pytest.mark.parametrize("code", [SAFE_PROXY, SAFE_PROXY_PUSH4])
def test_a_safe_proxy_never_set_up_does_not_type_its_version(tmp_path, chain, variant12, code):
    # Every Safe proxy of a version has the same code. The lowest address, never set up (threshold 0, no
    # owners), must not decide for the Safes set up after it: Safe proxies are probed address by address.
    chain.code.update({S1: code, S2: code, S3: code})
    chain.answers.update({(S1, GET_THRESHOLD): uint(0), (S1, GET_OWNERS): address_array([]),
                          (S2, GET_THRESHOLD): uint(2), (S2, GET_OWNERS): address_array([O1, O2]),
                          (S3, GET_THRESHOLD): uint(1), (S3, GET_OWNERS): address_array([O1])})
    stem = tmp_path / "types"
    assert run(csv_input(tmp_path, [S3, S2, S1]), stem, "--probe-wallets", "--rpc", PUBLIC) == 0
    assert chain.call_targets() == {S1, S2, S3}
    rows = read_parts(stem).set_index("address")
    assert len(set(rows["code_hash"])) == 1 and rows["has_master_copy"].all() and set(rows["proxy_kind"]) == {"safe"}
    assert rows["wallet_kind"].to_dict() == {S1: "", S2: "safe", S3: "safe"}
    assert rows["threshold"].to_dict() == {S1: 0, S2: 2, S3: 1}
    assert rows["n_owners"].to_dict() == {S1: 0, S2: 2, S3: 1}
    assert meta_of(stem)["probes"] == {"safe_slots": 3, "safe_proxies": 3}
    assert meta_of(stem)["counts_proxy_kind"] == {"safe": 3}
    # Slot 0 holds no address here: no implementation is found and the proxies' own code is examined.
    assert set(rows["implementation"]) == {""} and sorted(chain.code_reads()) == sorted([S1, S2, S3])


# A Safe-pattern proxy (the masterCopy() selector, its singleton in slot 0) whose singleton is an ERC-4337 account
# (PUSH4 validateUserOp of v0.7, no paymaster selector) and whose entryPoint() answers the canonical v0.7 EntryPoint:
# rule 3(b) examines the singleton's code, so it is a smart account. The same proxy code with an empty slot 0 has
# no implementation found, so its own code is examined (revision section 4.3), and it stays a contract. A code
# that holds both the ERC-1967 constant and the selector, with an empty ERC-1967 slot, is a Safe proxy as well.
X1, X2, X3, SING = addr(0x7001), addr(0x7002), addr(0x7003), addr(0x9007)
BOTH = ERC1967_PROXY + SAFE_PROXY_PUSH4[2:]


@pytest.mark.parametrize("workers,batch", [(1, 25), (2, 1)])
def test_the_code_of_a_safe_proxy_examined_is_its_singletons(tmp_path, chain, variant12, workers, batch):
    chain.code.update({X1: SAFE_PROXY, X2: SAFE_PROXY, X3: BOTH, SING: ACCOUNT_V07})
    chain.slot0.update({X1: SING, X3: SING})
    chain.answers.update({(x, ENTRY_POINT): address_word(EP07) for x in (X1, X2, X3)})
    stem = tmp_path / "types"
    assert run(csv_input(tmp_path, [X3, X2, X1]), stem, "--probe-wallets", "--rpc", PUBLIC, "--workers", workers,
               "--batch", batch) == 0
    rows = read_parts(stem).set_index("address")
    got = rows[["proxy_kind", "implementation", "has_validate_userop", "has_paymaster_selector", "entry_point",
                "wallet_kind", "account_class"]].to_dict("index")
    assert got == {
        X1: {"proxy_kind": "safe", "implementation": SING, "has_validate_userop": True, "has_paymaster_selector": False,
             "entry_point": EP07, "wallet_kind": "erc4337", "account_class": "smart_account"},
        X2: {"proxy_kind": "safe", "implementation": "", "has_validate_userop": False, "has_paymaster_selector": False,
             "entry_point": EP07, "wallet_kind": "", "account_class": "contract"},
        X3: {"proxy_kind": "safe", "implementation": SING, "has_validate_userop": True, "has_paymaster_selector": False,
             "entry_point": EP07, "wallet_kind": "erc4337", "account_class": "smart_account"}}
    assert chain.storage_reads("0x" + SLOT) == [X3] and chain.storage_reads(cac.SAFE_SLOT) == [X1, X2, X3]
    assert chain.code_reads().count(SING) == 1                       # the singleton's code is read once
    meta = meta_of(stem)
    assert meta["complete"] and meta["probes"] == {"storage_reads": 1, "safe_slots": 3, "implementations": 1,
                                                   "safe_proxies": 3}


def test_a_hash_that_answers_get_threshold_is_probed_address_by_address(tmp_path, chain, variant12):
    # T1, the representative of its hash, answers getThreshold() with a 32-byte word (here above the int64
    # range), so T2 and T3 are each probed; C1 does not answer, so its result is copied to C2.
    chain.code.update({T1: MULTISIG, T2: MULTISIG, T3: MULTISIG, C1: PLAIN, C2: PLAIN})
    chain.answers.update({(T1, GET_THRESHOLD): uint(2**256 - 1), (T3, GET_THRESHOLD): uint(2),
                          (T3, GET_OWNERS): address_array([O1]), (C2, GET_THRESHOLD): uint(1),
                          (C2, GET_OWNERS): address_array([O1])})
    stem = tmp_path / "types"
    assert run(csv_input(tmp_path, [T3, C2, T2, T1, C1]), stem, "--probe-wallets", "--rpc", PUBLIC) == 0
    assert chain.call_targets() == {T1, T2, T3, C1}            # C2's own answers are never read
    rows = read_parts(stem).set_index("address")
    assert rows["threshold"].to_dict() == {C1: -1, C2: -1, T1: cac.INT64_MAX, T2: -1, T3: 2}
    assert rows["n_owners"].to_dict() == {C1: -1, C2: -1, T1: -1, T2: -1, T3: 1}
    assert rows["wallet_kind"].to_dict() == {C1: "", C2: "", T1: "", T2: "", T3: "safe"}
    assert not rows["has_master_copy"].any() and set(rows["proxy_kind"]) == {"none"}
    meta = meta_of(stem)
    assert meta["complete"] and meta["probes"] == {"representatives": 2, "threshold_hashes": 2, "copied": 1}
    assert str(pq.read_table(part_paths(stem)[0]).schema.field("threshold").type) == "int64"


def test_a_call_aborted_at_every_attempt_fails_its_test(tmp_path, chain, variant12):
    # getOwners() of C1 runs past the node's time limit at every attempt: the batch is sent ABORT_ATTEMPTS
    # times, then C1's Safe test fails, the run completes, and the aborted call and its address are recorded.
    chain.code.update({C1: PLAIN, S1: SAFE_PROXY})
    chain.answers.update({(C1, GET_THRESHOLD): uint(1), (C1, GET_OWNERS): TIMEOUT,
                          (S1, GET_THRESHOLD): uint(2), (S1, GET_OWNERS): address_array([O1, O2])})
    stem = tmp_path / "types"
    assert run(csv_input(tmp_path, [C1, S1]), stem, "--probe-wallets", "--rpc", PUBLIC) == 0
    rows = read_parts(stem).set_index("address")
    assert tuple(rows.loc[C1, ["wallet_kind", "account_class", "threshold", "n_owners"]]) == ("", "contract", 1, -1)
    assert rows.loc[S1, "wallet_kind"] == "safe"
    assert len(chain.calls("eth_call")) == 6 * cac.ABORT_ATTEMPTS
    meta = meta_of(stem)
    assert meta["complete"] and meta["probes"]["aborted_calls"] == 1 and meta["aborted_addresses"] == [C1]


def abort_once(chain: FakeChain, targets: set[tuple[str, str]], hosts: set[str] | None = None, times: int = 1):
    """A fault that answers the calls in ``targets`` with the node's abort, ``times`` batches long (on every
    host, or always on ``hosts``), and every other call as the chain does."""
    left = [times]

    def fault(host, items):
        if not any(it["method"] == "eth_call" and (it["params"][0]["to"], it["params"][0]["data"]) in targets
                   for it in items):
            return None
        if hosts is None and not left[0] or hosts is not None and host not in hosts:
            return None
        left[0] -= 1
        out = []
        for it in items:
            answer = chain.answer(host, it)
            if it["method"] == "eth_call" and (it["params"][0]["to"], it["params"][0]["data"]) in targets:
                answer = {"jsonrpc": "2.0", "id": it["id"], **TIMEOUT}
            out.append(answer)
        return FakeResponse(200, out)

    return fault


@pytest.mark.parametrize("how", ["once", "always on one host"])
def test_an_abort_at_the_time_limit_is_sent_again(tmp_path, chain, variant12, how):
    # A Safe set up with two owners has its getOwners() aborted once, or at every attempt on the URL in use: the
    # batch is sent again (to the next URL after ROTATE_AFTER failures) and the Safe is typed from its answers.
    chain.code.update({S1: SAFE_PROXY})
    chain.answers.update({(S1, GET_THRESHOLD): uint(2), (S1, GET_OWNERS): address_array([O1, O2])})
    chain.fault = abort_once(chain, {(S1, GET_OWNERS)}, hosts={"public.example"} if how != "once" else None)
    stem = tmp_path / "types"
    assert run(csv_input(tmp_path, [S1]), stem, "--probe-wallets", "--rpc", PUBLIC, OTHER) == 0
    row = read_parts(stem).set_index("address").loc[S1]
    assert (row.threshold, row.n_owners, row.wallet_kind, row.account_class) == (2, 2, "safe", "smart_account")
    attempts = 2 if how == "once" else cac.ROTATE_AFTER + 1
    assert len(chain.calls("eth_call")) == 3 * attempts
    meta = meta_of(stem)
    assert meta["complete"] and "aborted_calls" not in meta["probes"] and meta["aborted_addresses"] == []


def test_abort_retries_reach_the_next_url_whatever_the_other_threads_do(chain):
    # With several workers the other threads' successes keep resetting the failures of the URL in use, so the
    # rotation of the pool never comes; the batch still sends its retries after an abort to the next URL.
    chain.code.update({S1: SAFE_PROXY})
    chain.answers.update({(S1, GET_THRESHOLD): uint(2), (S1, GET_OWNERS): address_array([O1, O2])})
    chain.fault = abort_once(chain, {(S1, GET_OWNERS)}, hosts={"public.example"})
    rpc = cac.Rpc([PUBLIC, OTHER])
    send = rpc.send

    def busy_send(i, payload):
        out = send(i, payload)
        with rpc.lock:
            rpc.streak = 0
        return out

    rpc.send = busy_send
    calls = [("eth_call", [{"to": S1, "data": sel}, "0x10"]) for sel in (GET_THRESHOLD, GET_OWNERS, ENTRY_POINT)]
    answers = rpc.batch(calls, failed=lambda k, e: cac.is_call_failure(e), settle=lambda k, e: cac.is_aborted_error(e))
    assert not any(map(cac.is_aborted, answers)) and rpc.at == 0
    hosts = [h for h, m, _ in chain.answered if m == "eth_call"]
    assert hosts == ["public.example"] * 3 * cac.ROTATE_AFTER + ["other.example"] * 3


def abort_at(chain: FakeChain, schedule: dict[tuple[str, str], set[int]]):
    """A fault that answers the call (to, selector) with the node's abort at the eth_call batches numbered in
    ``schedule`` (1, 2, ... over every host), and every other call as the chain does."""
    seen = [0]

    def fault(host, items):
        if not any(it["method"] == "eth_call" for it in items):
            return None
        seen[0] += 1
        out = []
        for it in items:
            answer = chain.answer(host, it)
            if it["method"] == "eth_call" and seen[0] in schedule.get((it["params"][0]["to"], it["params"][0]["data"]), ()):
                answer = {"jsonrpc": "2.0", "id": it["id"], **TIMEOUT}
            out.append(answer)
        return FakeResponse(200, out)

    return fault


def test_each_call_keeps_its_first_answer_that_is_not_an_abort(tmp_path, chain, variant12):
    # Two Safes share a probe batch. getOwners() of S1 is aborted at the odd attempts and that of S2 at the even
    # ones: each call keeps its first answer, so the batch is sent twice, both are Safes and no call failed.
    chain.code.update({S1: SAFE_PROXY, S2: SAFE_PROXY})
    chain.answers.update({(S1, GET_THRESHOLD): uint(2), (S1, GET_OWNERS): address_array([O1, O2]),
                          (S2, GET_THRESHOLD): uint(1), (S2, GET_OWNERS): address_array([O1])})
    chain.fault = abort_at(chain, {(S1, GET_OWNERS): {1, 3, 5}, (S2, GET_OWNERS): {2, 4, 6}})
    stem = tmp_path / "types"
    assert run(csv_input(tmp_path, [S1, S2]), stem, "--probe-wallets", "--rpc", PUBLIC) == 0
    rows = read_parts(stem).set_index("address")
    assert rows["wallet_kind"].to_dict() == {S1: "safe", S2: "safe"}
    assert rows["n_owners"].to_dict() == {S1: 2, S2: 1}
    assert len(chain.calls("eth_call")) == 6 * 2
    meta = meta_of(stem)
    assert meta["complete"] and "aborted_calls" not in meta["probes"] and meta["aborted_addresses"] == []


def test_a_representative_aborted_only_at_the_last_attempt_keeps_its_answer(tmp_path, chain, variant12):
    # getOwners() of C1 is aborted at every attempt, so its batch is sent ABORT_ATTEMPTS times. getThreshold() of T1,
    # the representative of a hash in the same batch, answers 2 until the last attempt aborts it: T1 keeps its first
    # answer, so the rest of its hash is probed address by address, and only C1 is listed.
    chain.code.update({C1: PLAIN, T1: MULTISIG, T2: MULTISIG, T3: MULTISIG})
    chain.answers.update({(C1, GET_THRESHOLD): uint(1), (C1, GET_OWNERS): TIMEOUT,
                          (T1, GET_THRESHOLD): uint(2), (T1, GET_OWNERS): address_array([O1, O2]),
                          (T2, GET_THRESHOLD): uint(1), (T2, GET_OWNERS): address_array([O1]),
                          (T3, GET_THRESHOLD): uint(3), (T3, GET_OWNERS): address_array([O1, O2, O2])})
    chain.fault = abort_at(chain, {(T1, GET_THRESHOLD): {cac.ABORT_ATTEMPTS}})
    stem = tmp_path / "types"
    assert run(csv_input(tmp_path, [T3, T2, T1, C1]), stem, "--probe-wallets", "--rpc", PUBLIC) == 0
    rows = read_parts(stem).set_index("address")
    assert rows["wallet_kind"].to_dict() == {C1: "", T1: "safe", T2: "safe", T3: "safe"}
    assert rows["threshold"].to_dict() == {C1: 1, T1: 2, T2: 1, T3: 3}
    meta = meta_of(stem)
    assert meta["probes"] == {"representatives": 2, "threshold_hashes": 2, "aborted_calls": 1}
    assert meta["aborted_addresses"] == [C1]


def test_abort_retries_start_at_the_url_that_gave_the_first_abort(chain):
    # The first URL is rate-limited three times, so the pool moves to the next URL, which aborts getOwners(): the
    # retries go ROTATE_AFTER times to that URL and then to the next in turn (revision section 4.3, Probes).
    chain.code.update({S1: SAFE_PROXY})
    chain.answers.update({(S1, GET_THRESHOLD): uint(2), (S1, GET_OWNERS): address_array([O1, O2])})
    aborts = abort_once(chain, {(S1, GET_OWNERS)}, hosts={"other.example"})
    limited = [cac.ROTATE_AFTER]

    def fault(host, items):
        if host == "public.example" and limited[0]:
            limited[0] -= 1
            return FakeResponse(429, text="rate limited")
        return aborts(host, items)

    chain.fault = fault
    rpc = cac.Rpc([PUBLIC, OTHER])
    calls = [("eth_call", [{"to": S1, "data": sel}, "0x10"]) for sel in (GET_THRESHOLD, GET_OWNERS, ENTRY_POINT)]
    answers = rpc.batch(calls, failed=lambda k, e: cac.is_call_failure(e), settle=lambda k, e: cac.is_aborted_error(e))
    assert not any(map(cac.is_aborted, answers))
    hosts = [h for h, m, _ in chain.answered if m == "eth_call"]
    assert hosts == ["other.example"] * 3 * cac.ROTATE_AFTER + ["public.example"] * 3


def test_abort_retries_pass_over_a_url_that_goes_down(chain):
    # The first URL aborts getOwners() and then fails every request: after ROTATE_AFTER failed attempts in a row the
    # batch's retries move to the next URL, which answers, instead of using up every attempt on the dead one.
    chain.code.update({S1: SAFE_PROXY})
    chain.answers.update({(S1, GET_THRESHOLD): uint(2), (S1, GET_OWNERS): address_array([O1, O2])})
    aborts = abort_once(chain, {(S1, GET_OWNERS)}, hosts={"public.example"})
    answered = [0]

    def fault(host, items):
        if host == "public.example" and any(it["method"] == "eth_call" for it in items):
            answered[0] += 1
            if answered[0] > 1:
                return FakeResponse(503, text="down")
        return aborts(host, items)

    chain.fault = fault
    rpc = cac.Rpc([PUBLIC, OTHER])
    calls = [("eth_call", [{"to": S1, "data": sel}, "0x10"]) for sel in (GET_THRESHOLD, GET_OWNERS, ENTRY_POINT)]
    answers = rpc.batch(calls, failed=lambda k, e: cac.is_call_failure(e), settle=lambda k, e: cac.is_aborted_error(e))
    assert not any(map(cac.is_aborted, answers))
    hosts = [h for h, m, _ in chain.answered if m == "eth_call"]
    assert hosts == ["public.example"] * 3 + ["other.example"] * 3
    assert answered[0] == 1 + cac.ROTATE_AFTER


def test_an_answer_with_an_abort_ends_the_run_of_failures_of_the_url_in_use(chain):
    # Two failures at the URL in use (other threads'), then this batch's answer there, usable but for an abort, then
    # one failure and an answer: the answer ended the run of failures, so the URL in use stays the first one.
    chain.code.update({S1: SAFE_PROXY})
    chain.answers.update({(S1, GET_THRESHOLD): uint(2), (S1, GET_OWNERS): address_array([O1, O2])})
    aborts = abort_once(chain, {(S1, GET_OWNERS)})
    seen = [0]

    def fault(host, items):
        seen[0] += 1
        return FakeResponse(503, text="busy") if seen[0] == 2 else aborts(host, items)

    chain.fault = fault
    rpc = cac.Rpc([PUBLIC, OTHER])
    rpc.streak = 2
    calls = [("eth_call", [{"to": S1, "data": sel}, "0x10"]) for sel in (GET_THRESHOLD, GET_OWNERS, ENTRY_POINT)]
    answers = rpc.batch(calls, failed=lambda k, e: cac.is_call_failure(e), settle=lambda k, e: cac.is_aborted_error(e))
    assert not any(map(cac.is_aborted, answers)) and (rpc.at, rpc.streak) == (0, 0)
    assert {h for h, m, _ in chain.answered if m == "eth_call"} == {"public.example"} and seen[0] == 3


def test_an_abort_of_a_call_to_a_system_address_follows_the_abort_rule(tmp_path, chain, variant12):
    # Every other error of a call to a system address is its failure at once, but the node's abort is sent again.
    SYS = addr(0x70)
    chain.code.update({SYS: "0xfe"})
    chain.answers.update({(SYS, GET_THRESHOLD): uint(5)})
    chain.fault = abort_once(chain, {(SYS, GET_THRESHOLD)})
    stem = tmp_path / "types"
    assert run(csv_input(tmp_path, [SYS]), stem, "--probe-wallets", "--rpc", PUBLIC) == 0
    row = read_parts(stem).set_index("address").loc[SYS]
    assert (row.threshold, row.wallet_kind, row.account_class) == (5, "", "contract")
    assert len(chain.calls("eth_call")) == 3 * 2
    meta = meta_of(stem)
    assert meta["aborted_addresses"] == [] and "aborted_calls" not in meta["probes"]


def test_one_serving_endpoint_takes_every_abort_attempt_and_is_recorded(tmp_path, chain, variant12):
    # Only one endpoint serves the block: the reads go there only, so all ABORT_ATTEMPTS attempts of an aborted call
    # do too, and the JSON records the endpoints that serve the block.
    chain.code.update({C1: PLAIN})
    chain.answers.update({(C1, GET_THRESHOLD): uint(1), (C1, GET_OWNERS): TIMEOUT})
    chain.unserved["public.example"] = {100}
    stem = tmp_path / "types"
    assert run(csv_input(tmp_path, [C1]), stem, "--block", 100, "--probe-wallets", "--rpc", PUBLIC, OTHER) == 0
    hosts = Counter(h for h, m, _ in chain.answered if m == "eth_call")
    assert hosts == {"other.example": 3 * cac.ABORT_ATTEMPTS}
    meta = meta_of(stem)
    assert meta["served_by"] == ["other.example"] and meta["aborted_addresses"] == [C1]


def test_an_aborted_representative_is_probed_again_before_its_hash_is_decided(tmp_path, chain, variant12):
    # Three Safes set up, sharing one code without masterCopy() (the shape of the proxies before v1.1.0). The
    # getThreshold() of the lowest, the representative, is aborted once: it is asked again, answers 2, and the
    # other two are probed one by one instead of being given a copy of a failed call.
    chain.code.update({T1: MULTISIG, T2: MULTISIG, T3: MULTISIG})
    chain.answers.update({(T1, GET_THRESHOLD): uint(2), (T1, GET_OWNERS): address_array([O1, O2]),
                          (T2, GET_THRESHOLD): uint(1), (T2, GET_OWNERS): address_array([O1]),
                          (T3, GET_THRESHOLD): uint(3), (T3, GET_OWNERS): address_array([O1, O2, O2])})
    chain.fault = abort_once(chain, {(T1, GET_THRESHOLD)})
    stem = tmp_path / "types"
    assert run(csv_input(tmp_path, [T3, T2, T1]), stem, "--probe-wallets", "--rpc", PUBLIC) == 0
    rows = read_parts(stem).set_index("address")
    assert rows["wallet_kind"].to_dict() == {T1: "safe", T2: "safe", T3: "safe"}
    assert rows["threshold"].to_dict() == {T1: 2, T2: 1, T3: 3}
    assert meta_of(stem)["probes"] == {"representatives": 1, "threshold_hashes": 2}
    assert chain.call_targets() == {T1, T2, T3}


def test_any_error_of_a_call_to_a_system_address_is_its_failure(tmp_path, chain, variant12, monkeypatch):
    # A system address runs a precompile, which may answer with an error that no EVM code gives; the call fails
    # its test at once. The same error from any other address is the RPC's, and the request is sent again.
    monkeypatch.setattr(cac, "RETRIES", 2)
    odd = {"error": {"code": -32000, "message": "unauthorized caller to access-controlled method"}}
    SYS = addr(0x70)
    chain.code.update({SYS: "0xfe", C1: PLAIN})
    chain.answers.update({(a, sel): odd for a in (SYS, C1) for sel in (GET_THRESHOLD, GET_OWNERS, ENTRY_POINT)})
    stem = tmp_path / "types"
    assert run(csv_input(tmp_path, [SYS]), stem, "--probe-wallets", "--rpc", PUBLIC) == 0
    row = read_parts(stem).set_index("address").loc[SYS]
    assert (row.code_kind, row.wallet_kind, row.threshold, row.n_owners) == ("contract", "", -1, -1)
    assert len(chain.calls("eth_call")) == 3
    assert run(csv_input(tmp_path, [C1], "c1.csv"), tmp_path / "c1", "--probe-wallets", "--rpc", PUBLIC) == 1
    assert not meta_of(tmp_path / "c1")["complete"]


def test_probe_wallets_needs_the_contract_graph_settings(tmp_path, chain, monkeypatch):
    base = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    monkeypatch.setattr(cac, "load_config", lambda: copy.deepcopy(base))
    with pytest.raises(SystemExit, match="contract12m"):
        run(csv_input(tmp_path, [C1]), tmp_path / "types", "--probe-wallets")
    assert not chain.received


def test_an_output_is_resumed_only_in_its_own_mode(tmp_path, chain, variant12):
    chain.code[C1] = PLAIN
    inp = csv_input(tmp_path, [C1])
    assert run(inp, tmp_path / "base", "--rpc", PUBLIC) == 0
    with pytest.raises(SystemExit, match="refused"):
        run(inp, tmp_path / "base", "--rpc", PUBLIC, "--probe-wallets")
    assert run(inp, tmp_path / "probe", "--rpc", PUBLIC, "--probe-wallets") == 0
    with pytest.raises(SystemExit, match="refused"):
        run(inp, tmp_path / "probe", "--rpc", PUBLIC)


# --- inputs -------------------------------------------------------------------------------------

def test_parquet_queue_input(tmp_path, chain):
    chain.code[C1] = PLAIN
    queue = pd.DataFrame({"address": [C1, E1, C1, D1.upper().replace("0X", "0x")],
                          "reason": ["k", "k", "cohort", "audit"]})
    write_parts(queue, tmp_path / "queue")
    assert run(tmp_path / "queue", tmp_path / "types", "--input-parquet", "--rpc", PUBLIC) == 0
    assert sorted(chain.code_reads()) == sorted([C1, E1, D1])
    binary = pd.DataFrame({"address": [bytes.fromhex(a[2:]) for a in (C1, E1)]})
    write_parts(binary, tmp_path / "cohort")
    chain.answered.clear()
    assert run(tmp_path / "cohort", tmp_path / "types2", "--input-parquet", "--rpc", PUBLIC) == 0
    assert read_parts(tmp_path / "types2")["address"].tolist() == sorted([C1, E1])


def test_values_that_are_not_addresses_are_refused(tmp_path, chain):
    with pytest.raises(SystemExit, match="not addresses"):
        run(csv_input(tmp_path, [C1, "0x1234"]), tmp_path / "types", "--rpc", PUBLIC)
    assert not chain.received


# --- RPC URLs, hosts and blocks -----------------------------------------------------------------

def test_json_and_parquet_hold_host_names_only(tmp_path, chain, variant12, monkeypatch, capsys):
    world(chain)
    monkeypatch.setenv(cac.ENV_URL, SECRET_URL)
    leak = requests.ConnectionError(
        "HTTPSConnectionPool(host='provider.example', port=443): Max retries exceeded with url: "
        "/v2/KEY-SECRET?apikey=Q-SECRET (Caused by ...)")
    chain.fault = lambda host, items: leak if host == "provider.example" else None
    stem = tmp_path / "types"
    assert run(csv_input(tmp_path, WORLD), stem, "--rpc", PUBLIC, "--probe-wallets") == 0
    meta = meta_of(stem)
    assert meta["rpc"] == "public.example"
    assert meta["rpc_calls"] == dict(chain.received) == {"provider.example": cac.ROTATE_AFTER,
                                                         "public.example": meta["rpc_calls"]["public.example"]}
    text = stem.with_suffix(".json").read_text(encoding="utf-8")
    printed = "".join(capsys.readouterr())
    values = read_parts(stem).astype(str).to_numpy().ravel().tolist()
    for blob in (text, printed, *values):
        for secret in ("SECRET", "/v2", "apikey", "pw-", "user:", "://"):
            assert secret not in blob, secret
    assert all(b"SECRET" not in p.read_bytes() for p in part_paths(stem))


def test_errors_name_hosts_only(tmp_path, chain, variant12, monkeypatch, capsys):
    monkeypatch.setenv(cac.ENV_URL, SECRET_URL)
    monkeypatch.setattr(cac, "RETRIES", 4)
    chain.fault = lambda host, items: (
        requests.ConnectionError(f"Max retries exceeded with url: /v2/KEY-SECRET?apikey=Q-SECRET ({host})")
        if host == "provider.example" else FakeResponse(503, text=f"upstream {SECRET_URL} is down"))
    assert run(csv_input(tmp_path, [C1]), tmp_path / "types", "--rpc", PUBLIC, "--probe-wallets") == 1
    err = capsys.readouterr().err
    assert "kept failing" in err and "SECRET" not in err and "/v2" not in err


def test_rotation_to_the_next_url_and_calls_per_host(tmp_path, chain):
    chain.code[C1] = PLAIN
    chain.fault = lambda host, items: FakeResponse(503, text="busy") if host == "other.example" else None
    stem = tmp_path / "types"
    assert run(csv_input(tmp_path, [C1, E1, D1]), stem, "--rpc", OTHER, PUBLIC, "--batch", 1, "--workers", 1) == 0
    assert chain.received["other.example"] == cac.ROTATE_AFTER
    assert meta_of(stem)["rpc_calls"] == dict(chain.received)
    assert meta_of(stem)["rpc"] == "public.example"


def test_a_requested_block_is_read_where_it_is_served(tmp_path, chain, monkeypatch):
    chain.code[C1] = PLAIN
    monkeypatch.setenv(cac.ENV_URL, SECRET_URL)
    chain.unserved["public.example"] = {513216506}
    stem = tmp_path / "types"
    assert run(csv_input(tmp_path, [C1, E1]), stem, "--block", 513216506, "--fallback-latest", "--rpc", PUBLIC) == 0
    meta = meta_of(stem)
    assert (meta["block_number"], meta["block_hex"], meta["pinned_requested"], meta["pinned_served"]) == \
        (513216506, hex(513216506), 513216506, True)
    reads = [(h, p) for h, m, p in chain.answered if m == "eth_getCode" and p[0] != USDC]
    assert {h for h, _ in reads} == {"provider.example"} and {p[1] for _, p in reads} == {hex(513216506)}


INTERNAL = {"error": {"code": -32603, "message": "Internal error"}}


@pytest.mark.parametrize("answer,failures,served", [
    ("rate limit", cac.PROBE_RETRIES, True),           # three retries after a failed first attempt
    ("rate limit", cac.PROBE_RETRIES + 1, False),      # every attempt failed: not serving, the latest block instead
    ("internal error", 1, True),                       # an error answer is retried too
    ("internal error", cac.PROBE_RETRIES, True),
    ("missing state", cac.PROBE_RETRIES + 1, False),
])
def test_a_failed_block_probe_is_retried_three_times(tmp_path, chain, answer, failures, served):
    # Revision section 4.2 rule 2: a failed request or a rate limit is retried three times before an endpoint
    # counts as not serving the block. Every endpoint fails the probe of block 100 ``failures`` times.
    chain.code[C1] = PLAIN
    left = {"public.example": failures, "other.example": failures}
    seen: Counter = Counter()   # probes of block 100 per host, every attempt

    def fault(host, items):
        if items[0]["params"] == [USDC, hex(100)]:
            seen[host] += 1
        if left[host] and items[0]["params"] == [USDC, hex(100)]:
            left[host] -= 1
            if answer == "rate limit":
                return FakeResponse(429, text="Too Many Requests")
            error = INTERNAL if answer == "internal error" else {
                "error": {"code": -32000, "message": "missing trie node 1a2b (path ) state is not available"}}
            return FakeResponse(200, [{"jsonrpc": "2.0", "id": items[0]["id"], **error}])
        return None

    chain.fault = fault
    stem = tmp_path / "types"
    assert run(csv_input(tmp_path, [C1]), stem, "--block", 100, "--fallback-latest", "--rpc", PUBLIC, OTHER) == 0
    meta = meta_of(stem)
    assert (meta["block_number"], meta["pinned_requested"], meta["pinned_served"]) == (
        (100, 100, True) if served else (chain.latest, 100, False))
    # One attempt and at most PROBE_RETRIES retries per endpoint; a usable answer ends them.
    assert seen == {h: min(failures + 1, 1 + cac.PROBE_RETRIES) for h in ("public.example", "other.example")}


@pytest.mark.parametrize("how", ["error", "no code"])
def test_fallback_to_the_latest_block(tmp_path, chain, how):
    chain.code[C1] = PLAIN
    for host in ("public.example", "other.example"):
        (chain.unserved if how == "error" else chain.empty)[host] = {100}
    stem = tmp_path / "types"
    with pytest.raises(SystemExit, match="refused"):
        run(csv_input(tmp_path, [C1, E1]), stem, "--block", 100, "--rpc", PUBLIC, OTHER)
    assert not part_paths(stem) and not stem.with_suffix(".json").exists()
    chain.answered.clear()
    assert run(tmp_path / "in.csv", stem, "--block", 100, "--fallback-latest", "--rpc", PUBLIC, OTHER) == 0
    meta = meta_of(stem)
    assert (meta["block_number"], meta["block_hex"], meta["pinned_requested"], meta["pinned_served"]) == \
        (chain.latest, hex(chain.latest), 100, False)
    assert {p[1] for p in chain.calls("eth_getCode") if p[0] != USDC} == {hex(chain.latest)}
    assert read_parts(stem)["code_kind"].tolist() == ["none", "contract"]


def keyed(meta: dict, addresses=(C1,), rules: cac.Rules | None = None) -> dict:
    """``meta`` with the resume_key of a run of this script on ``addresses`` (pass 1 only without ``rules``)."""
    prefix = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))["accounts"]["delegation_prefix"]
    return {**meta, "resume_key": cac.resume_key(rules, prefix, list(addresses))}


@pytest.mark.parametrize("meta,args,ok", [
    ({"block_number": 100, "block_hex": "0x64", "pinned_requested": 100, "pinned_served": True}, [200], False),
    ({"block_number": 100, "block_hex": "0x64"}, [200], False),          # an earlier read without --block
    ({"block_number": 100, "block_hex": "0x64"}, [100], True),
    ({"block_number": 0x5000, "block_hex": "0x5000", "pinned_requested": 100, "pinned_served": False}, [100], False),
    ({"block_number": 0x5000, "block_hex": "0x5000", "pinned_requested": 100, "pinned_served": False},
     [100, "--fallback-latest"], True),
    ({"block_number": 100, "block_hex": "0x64", "pinned_requested": 100, "pinned_served": True}, [], True),
])
def test_resume_only_at_the_same_block(tmp_path, chain, meta, args, ok):
    chain.code[C1] = PLAIN
    stem = tmp_path / "types"
    stem.with_suffix(".json").write_text(json.dumps(keyed(meta)), encoding="utf-8")
    argv = [csv_input(tmp_path, [C1]), stem, "--rpc", PUBLIC] + (["--block", *args] if args else [])
    if not ok:
        with pytest.raises(SystemExit, match="refused"):
            run(*argv)
        assert not chain.received
        return
    assert run(*argv) == 0
    assert {p[1] for p in chain.calls("eth_getCode") if p[0] != USDC} == {meta["block_hex"]}
    assert meta_of(stem)["block_number"] == meta["block_number"]
    # Without its resume_key (an output of the registered usage, or of an earlier version), a read of the
    # revision does not resume it.
    if args:
        stem.with_suffix(".json").write_text(json.dumps(meta), encoding="utf-8")
        chain.received.clear()
        with pytest.raises(SystemExit, match="records no resume_key"):
            run(*argv)
        assert not chain.received


@pytest.mark.parametrize("args", [["--block", 100], []])
def test_resume_refused_when_the_block_is_no_longer_served(tmp_path, chain, args):
    stem = tmp_path / "types"
    stem.with_suffix(".json").write_text(json.dumps(keyed({"block_number": 100, "block_hex": "0x64",
                                                           "pinned_requested": 100, "pinned_served": True})))
    chain.unserved["public.example"] = {100}
    with pytest.raises(SystemExit, match="refused: no RPC serves block"):
        run(csv_input(tmp_path, [C1]), stem, "--rpc", PUBLIC, *args)
    assert not chain.code_reads()


NEW_EP = addr(0x4337)


def test_a_resume_needs_the_same_script_rules_and_addresses(tmp_path, chain, cfg12, monkeypatch):
    # An account with validateUserOp (v0.7) whose entryPoint() answers an EntryPoint the rules do not list is a
    # contract. Once that EntryPoint is added (an amendment of revision section 13), or the queue changes, or the
    # script does, a rerun on the output on disk is refused: a resumed run would keep the finished rows, and the
    # representatives of the code hashes, of the earlier one. A fresh output types the account by the new rules.
    chain.code.update({A1: ACCOUNT_V07, C1: PLAIN, C2: PLAIN})
    chain.answers[(A1, ENTRY_POINT)] = address_word(NEW_EP)
    amended = copy.deepcopy(cfg12)
    amended["contract_graph"]["entry_points"]["new"] = NEW_EP
    config = [cfg12]
    monkeypatch.setattr(cac, "load_config", lambda: copy.deepcopy(config[0]))
    inp = csv_input(tmp_path, [A1, C1, C2])
    flags = ["--probe-wallets", "--block", 100, "--rpc", PUBLIC]
    stem = tmp_path / "types"
    assert run(inp, stem, *flags) == 0
    assert read_parts(stem).set_index("address").loc[A1, "account_class"] == "contract"
    chain.answered.clear()
    assert run(inp, stem, *flags) == 0                                # the same files: resumed, nothing read
    assert not chain.code_reads() and not chain.calls("eth_call")

    def refused(match: str, inp_=inp) -> None:
        chain.received.clear()
        with pytest.raises(SystemExit, match=match):
            run(inp_, stem, *flags)
        assert not chain.received

    config[0] = amended
    refused("under other rules")
    config[0] = cfg12
    c3 = addr(0x1009)
    refused("for other input addresses", csv_input(tmp_path, [A1, C1, C2, c3], "more.csv"))
    refused("for other input addresses", csv_input(tmp_path, [A1, C1, c3], "other.csv"))
    script = tmp_path / "check_account_code.py"
    script.write_bytes(cac.SCRIPT.read_bytes() + b"\n# changed\n")
    monkeypatch.setattr(cac, "SCRIPT", script)
    refused("with another version of check_account_code.py")
    script.write_bytes(cac.SCRIPT.read_bytes().replace(b"\n# changed\n", b"").replace(b"\n", b"\r\n"))
    assert run(inp, stem, *flags) == 0                                # line endings alone change nothing
    # A fresh output under the amended rules types the account as a smart account.
    config[0] = amended
    assert run(inp, tmp_path / "fresh", *flags) == 0
    row = read_parts(tmp_path / "fresh").set_index("address").loc[A1]
    assert (row.entry_point, row.wallet_kind, row.account_class) == (NEW_EP, "erc4337", "smart_account")
    assert meta_of(tmp_path / "fresh")["rules"]["entry_points"] == sorted(amended["contract_graph"]["entry_points"]
                                                                          .values())


def test_parts_without_a_block_record_are_refused(tmp_path, chain):
    write_parts(pd.DataFrame({"address": [C1], "code_kind": ["contract"], "account_class": ["contract"]}),
                tmp_path / "types")
    with pytest.raises(SystemExit, match="records no block"):
        run(csv_input(tmp_path, [C1]), tmp_path / "types", "--rpc", PUBLIC)
    assert not chain.received


# --- resuming -----------------------------------------------------------------------------------

@pytest.mark.parametrize("probe", [False, True])
def test_resume_of_pass_1(tmp_path, chain, variant12, monkeypatch, probe):
    world(chain)
    monkeypatch.setattr(cac, "SAVE_EVERY", 1)
    monkeypatch.setattr(cac, "RETRIES", 2)
    bad = sorted(WORLD)[9]
    chain.fault = lambda host, items: (FakeResponse(503, text="busy") if any(
        it["method"] == "eth_getCode" and it["params"][0] == bad for it in items) else None)
    inp = csv_input(tmp_path, sorted(WORLD))
    flags = ["--rpc", PUBLIC, "--batch", 2, "--workers", 1] + (["--probe-wallets"] if probe else [])
    stem = tmp_path / "types"
    assert run(inp, stem, *flags) == 1
    first = read_parts(stem)
    assert 0 < len(first) < len(WORLD) and not meta_of(stem)["complete"]
    assert set(first["address"]) <= set(sorted(WORLD)[:9])
    chain.fault, chain.answered[:] = None, []
    assert run(inp, stem, *flags) == 0
    # Pass 1 reads the rest; pass 2 reads each implementation once (G1, the singleton of the Safe proxies, is
    # also an address of the input).
    again = Counter(chain.code_reads()) - Counter([IMPL_A, IMPL_B, G1] if probe else [])
    assert not set(again) & set(first["address"]) and max(again.values()) == 1
    assert sorted(a for a in again if a in WORLD) == sorted(set(WORLD) - set(first["address"]))
    meta = meta_of(stem)
    assert meta["complete"] and meta["rpc_calls"] == dict(chain.received)    # the calls of both runs
    assert run(inp, tmp_path / "whole", *flags) == 0
    pd.testing.assert_frame_equal(read_parts(stem), read_parts(tmp_path / "whole"))


@pytest.mark.parametrize("method,target", [("eth_call", P2), ("eth_call", T3), ("eth_getStorageAt", P4)])
def test_resume_of_pass_2(tmp_path, chain, variant12, monkeypatch, method, target):
    world(chain)
    monkeypatch.setattr(cac, "SAVE_EVERY", 1)
    monkeypatch.setattr(cac, "RETRIES", 2)

    def fault(host, items):
        if any(it["method"] == method and (it["params"][0] if method != "eth_call" else it["params"][0]["to"]) == target
               for it in items):
            return FakeResponse(503, text="busy")
        return None

    chain.fault = fault
    inp = csv_input(tmp_path, WORLD)
    flags = ["--rpc", PUBLIC, "--batch", 3, "--workers", 1, "--probe-wallets"]
    stem = tmp_path / "types"
    assert run(inp, stem, *flags) == 1
    first = read_parts(stem)
    meta = meta_of(stem)
    pending = set(first.loc[first["wallet_kind"].isna(), "address"])
    assert len(first) == len(WORLD) and not meta["complete"] and meta["pending"] == len(pending) > 0
    contracts = {a for a, e in EXPECTED.items() if e[0] == "contract"}
    assert target in pending and pending <= contracts
    unread = set(first.loc[first["proxy_kind"].isna(), "address"])
    no_singleton = set(first.loc[first["implementation"].isna(), "address"])   # Safe proxies, slot 0 unread
    if target == P2:   # the slots are read and the probes of the first stage before P2 are done
        assert not unread and not no_singleton and pending == {P2, P3, P4, A1, M1, T1, T2, T3}
    elif target == T3:  # the first stage is done and T2 of the second: T1 answered getThreshold() with 0
        assert not unread and not no_singleton and pending == {T3}
        assert tuple(first.set_index("address").loc[T2, ["threshold", "wallet_kind"]]) == (3, "safe")
    else:              # the slots of the first batch are read, no probe is done
        assert unread == {P4} and no_singleton == {S1, S2, S3} and pending == contracts
    chain.fault, chain.answered[:] = None, []
    assert run(inp, stem, *flags) == 0
    assert not set(chain.code_reads()) & (set(WORLD) - {G1})           # pass 1 is not read again
    assert set(chain.storage_reads("0x" + SLOT)) == unread
    assert set(chain.storage_reads(cac.SAFE_SLOT)) == no_singleton
    assert chain.call_targets() <= pending
    if target == T3:   # T3 is probed itself, not given the results of T1
        assert chain.call_targets() == {T3}
    meta = meta_of(stem)
    assert meta["complete"] and meta["pending"] == 0 and meta["rpc_calls"] == dict(chain.received)
    assert run(inp, tmp_path / "whole", *flags) == 0
    pd.testing.assert_frame_equal(read_parts(stem), read_parts(tmp_path / "whole"))
    # Every address is probed or copied once over both runs; only the implementations of proxies still
    # pending are read again.
    resumed, whole = (dict(meta_of(s)["probes"]) for s in (stem, tmp_path / "whole"))
    assert resumed.pop("implementations") >= whole.pop("implementations") and resumed == whole
