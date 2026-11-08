#!/usr/bin/env python3
"""Read the account type of addresses on an Arbitrum RPC: code, proxies and smart accounts.

Pass 1 reads eth_getCode for every address. Bytecode means a contract. No bytecode, or an
EIP-7702 delegation designator (0xef0100 followed by a 20-byte address), means an externally
owned account. All reads use one block, recorded in the output, so the classification refers to
one state of the chain: without --block the latest block at the first read (as in the account-type
reads of the registered analysis); with --block N the block N, and with --fallback-latest the
latest block at the first read if no RPC serves N (docs/revision_contract_graph.md section 4.2).
An RPC serves a block if it returns code for native USDC there; a request that fails, is rate
limited or is answered with an error is retried PROBE_RETRIES times before the RPC counts as not
serving it.

Pass 2 (--probe-wallets, with the settings of cfg["contract_graph"] of the contract-graph variant,
CONTRACT_REP_VARIANT=contract12m) examines every contract at the same block (revision sections 4.2
and 4.3):
  - proxies from the code: a code that begins with the EIP-1167 clone pattern carries its
    implementation; a code that holds the ERC-1967 implementation slot constant is an ERC-1967
    proxy if that slot (eth_getStorageAt) holds a non-zero address; any other code that holds the
    masterCopy() selector 0xa619486e (as PUSH4, or as the first four bytes of a PUSH32 word followed
    by 28 zero bytes, as the Safe proxies compile it) is a Safe proxy (has_master_copy), whose
    implementation is its singleton, the address in its storage slot 0 (none if the slot holds 0);
  - PUSH4 (0x63) followed by a validateUserOp or a validatePaymasterUserOp selector, searched in
    the implementation's code for a proxy whose implementation was found (read once per
    implementation) and in the own code otherwise;
  - eth_call of getThreshold(), getOwners() and entryPoint(). A Safe returns a threshold from 1 to
    safe_threshold_max and a non-empty owner list; an ERC-4337 account returns a canonical
    EntryPoint, has a validateUserOp selector and no paymaster selector. Both are smart accounts,
    which the revision counts as user accounts. A reverted or malformed call fails its test: an
    error is the call's own failure when its code is 3 or its message begins with an error of the
    EVM or with an error that an Arbitrum Stylus program gives when it cannot run at the block read
    (STYLUS_FAILURES), and so is every other error of a call to a system address, which runs a
    precompile, not code.
    Any other error is the RPC's and the batch is sent again. A call the node aborts at its time
    limit, a system address's included, is sent again too: ROTATE_AFTER attempts in all at the URL
    that gave the first abort, then ROTATE_AFTER at the next URL in turn (a URL that fails ROTATE_AFTER
    requests in a row meanwhile is passed over for the next). Each call keeps its first answer that is
    not an abort, and a call fails its test only if all ABORT_ATTEMPTS attempts abort it (counted as
    probes.aborted_calls, with the probed addresses in aborted_addresses of the JSON).
    The decoded answers are recorded for every probed address: threshold (the getThreshold() word
    if it is exactly 32 bytes, else -1), n_owners (the length of the decoded getOwners() list, else
    -1) and entry_point.
  The calls are made address by address on ERC-1967 proxies, on Safe proxies (every Safe proxy of a
  version has the same code, and its threshold and owners sit in its storage) and, in a second
  stage, on every other address of a code hash whose representative answered getThreshold() with a
  32-byte word, whatever its value. Every other code hash is probed on one representative (the
  lowest address) and its results are copied to every address with that hash (revision 4.3, Probes).

Usage:
    python scripts/check_account_code.py INPUT OUTPUT_STEM [--column address] [--input-parquet]
        [--block N] [--fallback-latest] [--rpc URL ...] [--workers 4] [--batch 25] [--probe-wallets]

INPUT is a CSV file, or with --input-parquet a parquet part stem (scripts/common.py). The RPC URLs
are tried in order: every --rpc, or accounts.rpc_url of the configuration without --rpc. In the
reads of the contract-graph revision (--block or --probe-wallets, or the resumption of an output
they wrote) the environment variable CONTRACT_REP_RPC_URL comes first if it is set (a provider URL
with a key is read only from there); the registered usage never reads it. A request that keeps
failing moves on to the next URL. Writes OUTPUT_STEM parquet parts (address, code_kind,
account_class, and with --probe-wallets the code, proxy and probe columns) and OUTPUT_STEM.json with
the block and how it was chosen, the host names (never a URL), the times of the reads, the counts
and the RPC calls per host. Progress is saved as the reads go: a restart skips the addresses already
read and resumes pass 2, at the same block only. In the reads of the revision the JSON also records
resume_key (the SHA-256 of this script, of the rules of pass 2 and of the input addresses) and the
rules, and a restart resumes only with the same three, so that a resumed output is the output of a
run from scratch; otherwise the output must be moved away and read afresh.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import re
import sys
import threading
import time
from collections import Counter, deque
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence
from urllib.parse import urlsplit

import pandas as pd
import pyarrow as pa
import requests
from Crypto.Hash import keccak

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_config, part_paths, read_parts, write_parts  # noqa: E402

BATCH = 25            # JSON-RPC calls per request
WORKERS = 4           # threads that send requests
RETRIES = 15          # attempts per request, over the RPC URLs in turn
ROTATE_AFTER = 3      # consecutive failures of the URL in use before the next URL is used (an answer ends a run,
                      # one usable but for the node's aborts included)
PROBE_RETRIES = 3     # retries of a block probe on one URL after a failed request, a rate limit or an error
                      # answer (revision section 4.2 rule 2), so 1 + PROBE_RETRIES attempts
ABORT_ATTEMPTS = 2 * ROTATE_AFTER  # answered attempts of a call the node aborts at its time limit, ROTATE_AFTER per
                                   # URL in turn from the one of the first abort; a call aborted at all of them fails
BACKOFF_CAP = 60.0    # seconds; the wait after attempt k is min(2 ** k, BACKOFF_CAP)
TIMEOUT = 60          # seconds per HTTP request
SAVE_EVERY = 200      # batches between progress saves, ...
SAVE_SECONDS = 60.0   # ... at least this many seconds apart
ENV_URL = "CONTRACT_REP_RPC_URL"
# Native USDC has had code since long before any block read here: an RPC that answers a read of its
# code at a block with an error or with no code does not serve that block.
PROBE_ADDRESS = "0xaf88d065e77c8cc2239327c5edb3a432268e5831"
EIP1167_PREFIX = bytes.fromhex("363d3d373d3d3d363d73")
EIP1167_SUFFIX = bytes.fromhex("5af43d82803e903d91602b57fd5bf3")
PUSH4 = b"\x63"
# masterCopy() of the Safe proxies (revision section 4.3): PUSH4 of the selector, or PUSH32 of the selector
# shifted to the top of the word (the form of the Safe proxies of v1.1.1, v1.3.0 and v1.4.1).
MASTER_COPY = bytes.fromhex("a619486e")
MASTER_COPY_FORMS = (PUSH4 + MASTER_COPY, b"\x7f" + MASTER_COPY + bytes(28))
# Storage slot 0 of a Safe proxy holds its singleton (revision section 4.3), the address masterCopy() returns.
SAFE_SLOT = "0x" + "00" * 32
INT64_MAX = 2**63 - 1  # the threshold column is int64; a larger getThreshold() word is recorded as this
ADDRESS = re.compile(r"0x[0-9a-f]{40}")
HEX = re.compile(r"0[xX](?:[0-9a-fA-F]{2})*")
ADDRESS_MASK = (1 << 160) - 1
CLASS = {"contract": "contract", "none": "eoa", "eip7702": "eoa_7702"}
BASE_COLUMNS = ["address", "code_kind", "account_class"]
PROBE_COLUMNS = BASE_COLUMNS + ["code_size", "code_hash", "proxy_kind", "implementation", "has_master_copy",
                                "threshold", "n_owners", "entry_point", "has_validate_userop",
                                "has_paymaster_selector", "wallet_kind"]
# The columns kept in memory with --probe-wallets (account_class follows from code_kind and wallet_kind).
# While a contract waits for pass 2 its wallet_kind is null, its proxy_kind too while its ERC-1967 slot
# is unread, and the implementation of a Safe proxy while its slot 0 is unread; a finished output has no
# null.
STORED = [c for c in PROBE_COLUMNS if c != "account_class"]
_TEXT = pa.large_string()
PROBE_SCHEMA = pa.schema([
    ("address", _TEXT), ("code_kind", _TEXT), ("account_class", _TEXT), ("code_size", pa.int64()),
    ("code_hash", _TEXT), ("proxy_kind", _TEXT), ("implementation", _TEXT), ("has_master_copy", pa.bool_()),
    ("threshold", pa.int64()),
    ("n_owners", pa.int64()), ("entry_point", _TEXT), ("has_validate_userop", pa.bool_()),
    ("has_paymaster_selector", pa.bool_()), ("wallet_kind", _TEXT)])
# The beginnings of the messages of the errors the EVM gives for a failed execution (go-ethereum's core/vm
# errors, which the Arbitrum nodes return, e.g. "execution reverted: GS000", "invalid opcode: INVALID",
# "stack underflow (0 <=> 1)"): an eth_call error whose message begins with one of them, or whose code is 3 (a
# revert), is the call's own failure, so the test it serves fails. Any other error is the RPC's and the request
# is sent again.
CALL_FAILURES = ("execution reverted", "out of gas", "invalid opcode", "invalid jump destination",
                 "stack underflow", "stack overflow", "stack limit reached", "write protection",
                 "return data out of bounds", "invalid code", "max call depth exceeded", "gas uint64 overflow",
                 "nonce uint64 overflow", "insufficient balance for transfer", "contract address collision",
                 "max code size exceeded", "max initcode size exceeded", "contract creation code storage out of gas")
# The beginnings of the messages of the errors an Arbitrum Stylus (WASM) program gives when it cannot run at the
# block read (Nitro's programs errors, e.g. "error ProgramNeedsUpgrade(2, 3)" for a program activated under an older
# Stylus version): the program's state at that block is the account's answer, so the call fails its test, as with
# an error of the EVM (revision section 4.3, amendment of 8 November 2026).
STYLUS_FAILURES = ("error programnotactivated", "error programneedsupgrade", "error programexpired",
                   "error programnotwasm")
# The node's abort of a call that runs past its time limit (go-ethereum's "execution aborted (timeout = 5s)").
# The limit is wall-clock time and differs between nodes and with their load, so an abort is not an answer of
# the account: the batch is sent again, each call keeps its first answer that is not an abort, and an abort counts
# as the call's failure only if all ABORT_ATTEMPTS attempts aborted that call.
ABORTED = "execution aborted"


def code_kind(code: str | None, prefix: str) -> str:
    c = (code or "0x").lower()
    if c in ("0x", "0x0"):
        return "none"
    if c.startswith(prefix) and len(c) == 2 + 2 * 23:
        return "eip7702"
    return "contract"


def post(session: requests.Session, url: str, payload, retries: int = 15):
    """One JSON-RPC request with retries (scripts/token_metadata.py uses it)."""
    last = ""
    for attempt in range(retries):
        try:
            resp = session.post(url, json=payload, timeout=60)
            if resp.status_code == 200:
                body = resp.json()
                if isinstance(body, list) and any("error" in item for item in body):
                    last = str([item["error"] for item in body if "error" in item][:1])
                else:
                    return body
            else:
                last = f"HTTP {resp.status_code}: {resp.text[:120]}"
        except (requests.RequestException, ValueError) as exc:
            last = repr(exc)
        time.sleep(min(2**attempt, 60))
    raise RuntimeError(f"RPC {url} kept failing: {last}")


# --- values -------------------------------------------------------------------------------------

def host_of(url: str) -> str:
    """Host name (and port) of a URL, without credentials, path or query: all that is recorded of it."""
    parts = urlsplit(url)
    try:
        port = parts.port
    except ValueError:
        port = None
    host = parts.hostname or ""
    return f"{host}:{port}" if port else host


def hex_bytes(value: Any) -> bytes | None:
    """The bytes of a 0x-prefixed hex string ('0x' and '0x0' are empty), or None if it is not one."""
    if not isinstance(value, str):
        return None
    if value in ("0x0", "0X0"):
        return b""
    return bytes.fromhex(value[2:]) if HEX.fullmatch(value) else None


def is_quantity(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"0x[0-9a-fA-F]+", value) is not None


def storage_value(value: Any) -> int | None:
    """The integer in a storage word (at most 32 bytes of hex), or None if it is not one."""
    if not isinstance(value, str) or not re.fullmatch(r"0x[0-9a-fA-F]{0,64}", value):
        return None
    return int(value[2:] or "0", 16)


def keccak_hex(data: bytes) -> str:
    h = keccak.new(digest_bits=256)
    h.update(data)
    return "0x" + h.hexdigest()


# --- the rules of revision sections 4.2 and 4.3 -------------------------------------------------

@dataclass(frozen=True)
class Rules:
    """Selectors, EntryPoints, threshold bound, ERC-1967 slot and system addresses of cfg["contract_graph"]."""

    validate_user_op: tuple[bytes, ...]    # PUSH4 followed by each selector
    validate_paymaster: tuple[bytes, ...]
    slot: bytes
    entry_points: frozenset[str]
    threshold_max: int
    calls: tuple[str, str, str]            # getThreshold(), getOwners(), entryPoint()
    system_max: int                        # 0x...01 to this address are the system addresses (precompiles)

    @classmethod
    def from_config(cls, cg: dict) -> Rules:
        sel = cg["selectors"]

        def selector(x: str) -> str:
            if not (isinstance(x, str) and re.fullmatch(r"0x[0-9a-f]{8}", x)):
                raise SystemExit(f"contract_graph.selectors: {x!r} is not a 4-byte selector")
            return x

        def push4(xs: Iterable[str]) -> tuple[bytes, ...]:
            return tuple(PUSH4 + bytes.fromhex(selector(x)[2:]) for x in xs)

        slot = str(cg["erc1967_slot"]).lower()
        if not re.fullmatch(r"0x[0-9a-f]{64}", slot):
            raise SystemExit("contract_graph.erc1967_slot is not a 32-byte word")
        entry_points = frozenset(str(v).lower() for v in cg["entry_points"].values())
        if not all(ADDRESS.fullmatch(e) for e in entry_points):
            raise SystemExit("contract_graph.entry_points must be addresses")
        system_max = int(cg["system_address_max"])
        if not 1 <= system_max <= 255:
            raise SystemExit("contract_graph.system_address_max must be from 1 to 255")
        return cls(push4(sel["validate_user_op"]), push4(sel["validate_paymaster_user_op"]),
                   bytes.fromhex(slot[2:]), entry_points, int(cg["safe_threshold_max"]),
                   (selector(sel["get_threshold"]), selector(sel["get_owners"]), selector(sel["entry_point"])),
                   system_max)

    @property
    def slot_hex(self) -> str:
        return "0x" + self.slot.hex()

    def is_system(self, address: str) -> bool:
        """Whether the address is a system address 0x...01 to 0x...<system_max> (revision section 4.1)."""
        return 1 <= int(address, 16) <= self.system_max

    def record(self) -> dict[str, Any]:
        """Everything that decides pass 2, as JSON: the settings and the code patterns of this script."""
        return {"validate_user_op": [x.hex() for x in self.validate_user_op],
                "validate_paymaster_user_op": [x.hex() for x in self.validate_paymaster],
                "erc1967_slot": self.slot_hex, "safe_slot": SAFE_SLOT, "entry_points": sorted(self.entry_points),
                "safe_threshold_max": self.threshold_max, "calls": list(self.calls),
                "system_address_max": self.system_max, "master_copy": [f.hex() for f in MASTER_COPY_FORMS],
                "eip1167": [EIP1167_PREFIX.hex(), EIP1167_SUFFIX.hex()]}


def eip1167_implementation(code: bytes) -> str:
    """The implementation of an EIP-1167 clone, or '' unless the code begins with the clone pattern
    363d3d373d3d3d363d73 <20-byte implementation> 5af43d82803e903d91602b57fd5bf3."""
    if len(code) >= 45 and code[:10] == EIP1167_PREFIX and code[30:45] == EIP1167_SUFFIX:
        return "0x" + code[10:30].hex()
    return ""


def has_push4(code: bytes, needles: Iterable[bytes]) -> bool:
    """Whether the code holds the byte 0x63 (PUSH4) followed by one of the selectors."""
    return any(n in code for n in needles)


def has_master_copy(code: bytes) -> bool:
    """Whether the code holds the masterCopy() selector as PUSH4 (63 a619486e) or as the first four bytes
    of a PUSH32 word (7f a619486e followed by 28 zero bytes)."""
    return any(form in code for form in MASTER_COPY_FORMS)


def proxy_after_slot(slot_set: bool, master_copy: bool) -> str:
    """The proxy kind of a code that is not a clone, once its ERC-1967 slot is known (or not needed)."""
    return "erc1967" if slot_set else ("safe" if master_copy else "none")


def code_features(code: bytes, rules: Rules) -> tuple[str | None, str, bool, bool, bool]:
    """Proxy kind (None while the ERC-1967 slot is still to be read), implementation, the masterCopy()
    test and the validateUserOp and paymaster tests of the code itself. A clone stays an EIP-1167 clone
    whatever else its code holds."""
    impl = eip1167_implementation(code)
    mc = has_master_copy(code)
    kind = "eip1167" if impl else (None if rules.slot in code else proxy_after_slot(False, mc))
    return kind, impl, mc, has_push4(code, rules.validate_user_op), has_push4(code, rules.validate_paymaster)


def code_row(address: str, code_hex: str, prefix: str, rules: Rules | None) -> tuple:
    """The pass-1 row of an address (the fields of STORED with --probe-wallets); the code is not kept. A Safe
    proxy's implementation is null until its slot 0 is read in pass 2."""
    kind = code_kind(code_hex, prefix)
    if rules is None:
        return address, kind
    code = hex_bytes(code_hex) or b""
    size, digest = len(code), (keccak_hex(code) if code else "")
    if kind != "contract":
        return address, kind, size, digest, "none", "", False, -1, -1, "", False, False, ""
    proxy, impl, mc, vu, pm = code_features(code, rules)
    return address, kind, size, digest, proxy, None if proxy == "safe" else impl, mc, -1, -1, "", vu, pm, None


def return_data(answer: dict) -> bytes | None:
    """The return data of an eth_call, or None if the call failed or the result is not hex."""
    return None if answer.get("error") is not None else hex_bytes(answer.get("result"))


def word(answer: dict) -> bytes | None:
    """The return data if it is exactly one 32-byte word."""
    data = return_data(answer)
    return data if data is not None and len(data) == 32 else None


def decode_address_array(data: bytes | None) -> list[str] | None:
    """An ABI-encoded dynamic address[] (offset, length, items), or None if the data is malformed."""
    if data is None or len(data) < 64:
        return None
    off = int.from_bytes(data[:32], "big")
    if off + 32 > len(data):
        return None
    n = int.from_bytes(data[off:off + 32], "big")
    end = off + 32 + 32 * n
    if end > len(data):
        return None
    words = [data[k:k + 32] for k in range(off + 32, end, 32)]
    if any(any(w[:12]) for w in words):
        return None
    return ["0x" + w[12:].hex() for w in words]


def evaluate(answers: Sequence[dict], vu: bool, pm: bool, rules: Rules) -> tuple[int, int, str, str]:
    """(threshold, n_owners, entry_point, wallet_kind) from the answers of getThreshold(), getOwners()
    and entryPoint() and the PUSH4 tests of the examined code (revision section 4.2 rule 3). The decoded
    answers are recorded whatever the wallet kind: threshold is the getThreshold() word if the answer is
    exactly 32 bytes (at most INT64_MAX), else -1; n_owners is the number of decoded owners, else -1."""
    t, owners, ep = word(answers[0]), decode_address_array(return_data(answers[1])), word(answers[2])
    threshold = min(int.from_bytes(t, "big"), INT64_MAX) if t is not None else -1
    n_owners = len(owners) if owners is not None else -1
    entry = "0x" + ep[12:].hex() if ep is not None and any(ep[12:]) else ""
    if 1 <= threshold <= rules.threshold_max and n_owners >= 1:
        return threshold, n_owners, entry, "safe"
    if entry in rules.entry_points and vu and not pm:
        return threshold, n_owners, entry, "erc4337"
    return threshold, n_owners, entry, ""


def is_call_failure(error: Any) -> bool:
    """Whether an eth_call error is the EVM's (a revert or another failed execution), not the RPC's: code 3, or a
    message that begins with one of CALL_FAILURES or STYLUS_FAILURES. A node's abort at its time limit is not one
    (is_aborted)."""
    if not isinstance(error, dict):
        return False
    if error.get("code") == 3:
        return True
    message = str(error.get("message", "")).strip().lower()
    return message.startswith(CALL_FAILURES) or message.startswith(STYLUS_FAILURES)


def is_aborted_error(error: Any) -> bool:
    """Whether an eth_call error is the node's abort of the call at its time limit."""
    return isinstance(error, dict) and str(error.get("message", "")).strip().lower().startswith(ABORTED)


def is_aborted(answer: dict) -> bool:
    """Whether the node aborted the call at its time limit (left on a call only if all ABORT_ATTEMPTS aborted it)."""
    return is_aborted_error(answer.get("error"))


# --- RPC ----------------------------------------------------------------------------------------

def rpc_urls(cli: Sequence[str] | None, cfg: dict, *, use_env: bool) -> list[str]:
    """Every --rpc in order, else accounts.rpc_url; with ``use_env`` (the reads of the contract-graph revision)
    CONTRACT_REP_RPC_URL first if it is set. The registered usage never reads the variable."""
    env = os.environ.get(ENV_URL, "").strip() if use_env else ""
    named = [(ENV_URL, env)] if env else []
    if cli:
        named += [(f"--rpc number {k + 1}", u) for k, u in enumerate(cli)]
    else:
        named.append(("accounts.rpc_url", str(cfg["accounts"]["rpc_url"])))
    urls: list[str] = []
    for name, url in named:
        if urlsplit(url).scheme not in ("http", "https") or not host_of(url):
            raise SystemExit(f"{name} is not an http(s) URL")
        if url not in urls:
            urls.append(url)
    return urls


def parse_batch(body: Any, n: int, valid: Callable[[Any], bool],
                failed: Callable[[int, Any], bool] | None) -> tuple[list[dict] | None, str]:
    """The n answers of a batch in request order, or None and why the batch must be sent again. An
    answer with an error is kept only if ``failed(k, error)`` accepts the error of call k as the call's
    own failure."""
    if n == 1 and isinstance(body, dict) and "id" in body:  # a batch of one answered without the list
        body = [body]
    if not isinstance(body, list):
        return None, f"not a batch answer: {str(body)[:160]}"
    got: dict[int, dict] = {}
    for item in body:
        if isinstance(item, dict) and type(item.get("id")) is int and 0 <= item["id"] < n:
            got[item["id"]] = item
    if len(got) < n:
        return None, f"{n - len(got)} of {n} answers missing"
    for k in range(n):
        error = got[k].get("error")
        if error is not None:
            if failed is None or not failed(k, error):
                return None, f"error {str(error)[:160]}"
        elif not valid(got[k].get("result")):
            return None, f"malformed result {str(got[k].get('result'))[:60]}"
    return [got[k] for k in range(n)], ""


class RpcError(RuntimeError):
    """A request that kept failing; its message names hosts only."""


class Rpc:
    """JSON-RPC batches over an ordered list of URLs: retries with backoff, rotation to the next URL
    when the one in use keeps failing, and the number of calls sent to each host. No URL, path,
    query or credential ever appears in a message."""

    def __init__(self, urls: Sequence[str]):
        self.urls = list(urls)
        self.hosts = [host_of(u) for u in self.urls]
        self.pool = list(range(len(self.urls)))   # the URLs in use, in order
        self.at = 0                               # position in pool of the URL in use
        self.streak = 0                           # its consecutive failures
        self.calls: Counter[str] = Counter()      # JSON-RPC calls sent per host, every attempt
        self.lock = threading.Lock()
        self.local = threading.local()
        self.stop = threading.Event()
        secrets: set[str] = set()
        for u in self.urls:
            p = urlsplit(u)
            secrets |= {u, u.rstrip("/"), p.path, p.query, p.fragment, p.username or "", p.password or ""}
            if "@" in p.netloc:
                secrets.add(p.netloc)
        self._secrets = sorted((s for s in secrets if s not in ("", "/")), key=len, reverse=True)

    def scrub(self, text: str) -> str:
        for s in self._secrets:
            text = text.replace(s, "...")
        return text

    def use(self, indices: Sequence[int]) -> None:
        """Send requests to these URLs only, in this order."""
        with self.lock:
            self.pool, self.at, self.streak = list(indices), 0, 0

    def answered(self) -> str:
        """The host that answered this thread's last batch."""
        return getattr(self.local, "host", "")

    def _session(self) -> requests.Session:
        session = getattr(self.local, "session", None)
        if session is None:
            session = self.local.session = requests.Session()
        return session

    def _wait(self, attempt: int) -> None:
        if self.stop.wait(min(2.0 ** attempt, BACKOFF_CAP)):
            raise RpcError("stopped")

    def send(self, i: int, payload: list[dict]) -> tuple[Any, str]:
        """One HTTP request to URL i: the decoded body and '', or None and the error."""
        with self.lock:
            self.calls[self.hosts[i]] += len(payload)
        try:
            resp = self._session().post(self.urls[i], json=payload, timeout=TIMEOUT)
            if resp.status_code != 200:
                return None, self.scrub(f"HTTP {resp.status_code}: {resp.text[:120]}")
            return resp.json(), ""
        except Exception as exc:  # requests' errors, invalid JSON, anything else the transport raises
            return None, self.scrub(f"{type(exc).__name__}: {exc}")[:300]

    def batch(self, calls: Sequence[tuple[str, list]], valid: Callable[[Any], bool] | None = None,
              failed: Callable[[int, Any], bool] | None = None,
              settle: Callable[[int, Any], bool] | None = None) -> list[dict]:
        """The answers to the calls, sent as one JSON-RPC batch until every answer is usable: a result
        that ``valid`` accepts (default: hex data) or an error that ``failed(k, error)`` accepts for call k.
        An error that ``settle`` accepts and ``failed`` does not (the node's abort of the call at its time
        limit) is no answer of the call: each call keeps its first answer that is not such an abort, and the
        batch is sent again while a call has none. An attempt whose answers are usable but for such aborts,
        with a call still left without an answer, counts towards ABORT_ATTEMPTS; at the ABORT_ATTEMPTS-th, a
        call aborted at every one of them keeps its abort as its failure. From the first abort on, the batch's
        attempts go to the URLs in turn, from the one that gave the first abort, whatever the other threads'
        requests do to the URL in use: a URL takes ROTATE_AFTER counted attempts, and ROTATE_AFTER failed
        attempts in a row (no usable answer) also move the batch to the next URL."""
        valid = valid or (lambda r: hex_bytes(r) is not None)
        payload = [{"jsonrpc": "2.0", "id": k, "method": m, "params": p} for k, (m, p) in enumerate(calls)]

        def failed_or_settled(k: int, error: Any) -> bool:
            return (failed is not None and failed(k, error)) or settle(k, error)

        def aborted(k: int, answer: dict) -> bool:
            error = answer.get("error")
            return error is not None and settle(k, error) and not (failed is not None and failed(k, error))

        kept: dict[int, dict] = {}   # call k: its first answer that is not an abort
        last, unsettled = "", 0      # unsettled: the attempts counted towards ABORT_ATTEMPTS
        pos: int | None = None       # from the first abort on, the pool position of this batch's attempts
        here = fails = 0             # counted attempts at pos, and failed attempts in a row at pos
        for attempt in range(RETRIES):
            if self.stop.is_set():
                raise RpcError("stopped")
            with self.lock:
                at = self.at if pos is None else pos
                i = self.pool[at % len(self.pool)]
            body, err = self.send(i, payload)
            counted = False
            if body is not None:
                answers, err = parse_batch(body, len(payload), valid, failed)
                if answers is None and settle is not None:
                    settled, _ = parse_batch(body, len(payload), valid, failed_or_settled)
                    if settled is not None:   # usable but for the node's aborts
                        for k, answer in enumerate(settled):
                            if k not in kept and not aborted(k, answer):
                                kept[k] = answer
                        if len(kept) == len(payload):
                            answers = settled
                        else:
                            counted = True
                            if pos is None:
                                pos = at      # the URL that gave the first abort
                            unsettled, here, fails = unsettled + 1, here + 1, 0
                            if unsettled >= ABORT_ATTEMPTS:
                                answers = settled
                            elif here >= ROTATE_AFTER:
                                pos, here = pos + 1, 0
                if answers is not None:
                    answers = [kept.get(k, answer) for k, answer in enumerate(answers)]
                    with self.lock:
                        if self.pool[self.at] == i:
                            self.streak = 0
                    self.local.host = self.hosts[i]
                    return answers
            if counted:
                last = f"{self.hosts[i]}: the node aborted a call at its time limit"
                with self.lock:
                    if self.pool[self.at] == i:
                        self.streak = 0   # the URL answered: its run of failures ends
            else:
                last = f"{self.hosts[i]}: {self.scrub(err)}"
                if pos is not None:   # a failed attempt during the abort retries
                    fails += 1
                    if fails >= ROTATE_AFTER:
                        pos, here, fails = pos + 1, 0, 0
                with self.lock:
                    if self.pool[self.at] == i:
                        self.streak += 1
                        if self.streak >= ROTATE_AFTER and len(self.pool) > 1:
                            self.at, self.streak = (self.at + 1) % len(self.pool), 0
            if attempt + 1 < RETRIES:
                self._wait(attempt)
        raise RpcError(f"{calls[0][0]} kept failing after {RETRIES} attempts; last: {last}")

    def serves(self, i: int, block_hex: str) -> bool:
        """Whether URL i serves the block: USDC has code there (revision section 4.2 rule 2). An answer with
        no code means no. A failed request, a rate limit, an error answer (such as a missing state) or a
        malformed one is retried PROBE_RETRIES times, and means no only when every attempt fails."""
        payload = [{"jsonrpc": "2.0", "id": 0, "method": "eth_getCode", "params": [PROBE_ADDRESS, block_hex]}]
        for attempt in range(1 + PROBE_RETRIES):
            body, _ = self.send(i, payload)
            if body is not None:
                answers, _ = parse_batch(body, 1, lambda r: hex_bytes(r) is not None, None)
                if answers is not None:
                    return bool(hex_bytes(answers[0]["result"]))
            if attempt < PROBE_RETRIES:
                self._wait(attempt)
        return False


def run_ordered(fn: Callable[[Any], Any], chunks: Sequence[Any], workers: int, apply: Callable[[Any], None],
                save: Callable[[], None], rpc: Rpc) -> None:
    """fn on every chunk with ``workers`` threads, the results applied in order. Progress is saved
    every SAVE_EVERY chunks (at most once per SAVE_SECONDS) and, after an error, before it is raised."""
    workers = max(1, workers)
    source = iter(chunks)
    last, since = time.monotonic(), 0
    with ThreadPoolExecutor(workers) as ex:
        queue: deque[Future] = deque(ex.submit(fn, c) for c in itertools.islice(source, 4 * workers))
        try:
            while queue:
                apply(queue.popleft().result())
                queue.extend(ex.submit(fn, c) for c in itertools.islice(source, 1))
                since += 1
                if since >= SAVE_EVERY and time.monotonic() - last >= SAVE_SECONDS:
                    save()
                    last, since = time.monotonic(), 0
        except BaseException:
            rpc.stop.set()
            for f in queue:
                f.cancel()
            save()
            raise


# --- block and output ---------------------------------------------------------------------------

def clean_meta(meta: dict) -> dict:
    """An earlier JSON with every URL in it replaced by its host (older runs recorded the URL)."""
    return {k: host_of(v) if isinstance(v, str) and "://" in v else v for k, v in meta.items()}


def check_resume(meta: dict, block: int | None, fallback: bool, name: str) -> None:
    """Refuse to resume, with --block N, an output read at another block: resume only at the same block."""
    if block is None or "block_number" not in meta:
        return
    pinned, requested = int(meta["block_number"]), meta.get("pinned_requested")
    if requested is None:
        if pinned != block:
            raise SystemExit(f"refused: {name} is pinned to block {pinned:,}, not to block {block:,}; "
                             "a run resumes only at the same block")
    elif int(requested) != block:
        raise SystemExit(f"refused: {name} is pinned to block {pinned:,} (requested {int(requested):,}), "
                         f"not to block {block:,}; a run resumes only at the same block")
    elif not meta.get("pinned_served") and not fallback:
        raise SystemExit(f"refused: {name} is pinned to the latest block {pinned:,} because block {block:,} "
                         "was not served; resume it with --fallback-latest")


SCRIPT = Path(__file__).resolve()
KEY_PARTS = {"script_sha256": "with another version of check_account_code.py",
             "rules_sha256": "under other rules (selectors, EntryPoints, slots, bounds or the delegation prefix)",
             "input_sha256": "for other input addresses", "input_n": "for another number of input addresses"}


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def resume_key(rules: Rules | None, prefix: str, addresses: Sequence[str]) -> dict[str, Any]:
    """What a resumed read of the contract-graph revision must share with the run that wrote the output: this
    script (line endings aside, as git may rewrite them), everything that decides passes 1 and 2, and the set of
    input addresses. A resumed output then equals the output of a run from scratch: no finished row is decided
    again, and a code hash keeps the representative it had."""
    decides = json.dumps({"delegation_prefix": str(prefix).lower(), "pass_2": rules.record() if rules else None},
                         sort_keys=True)
    return {"script_sha256": _sha256(SCRIPT.read_bytes().replace(b"\r\n", b"\n")),
            "rules_sha256": _sha256(decides.encode()),
            "input_sha256": _sha256("\n".join(sorted(set(addresses))).encode()),
            "input_n": len(set(addresses))}


def check_key(meta: dict, key: dict[str, Any], name: str) -> None:
    """Refuse to resume an output written by another script, under other rules or for other addresses."""
    stored = meta.get("resume_key")
    if not isinstance(stored, dict):
        raise SystemExit(f"refused: {name} records no resume_key, so it may have been written by another version "
                         "of check_account_code.py; move the output away to read afresh")
    differ = [why for part, why in KEY_PARTS.items() if stored.get(part) != key[part]]
    if differ:
        raise SystemExit(f"refused: {name} was written {', '.join(differ)}; a run resumes only with the same "
                         "script, rules and input addresses, so that its output is that of a run from scratch "
                         "(move the output away to read afresh)")


def pin(rpc: Rpc, block: int | None, fallback: bool) -> tuple[dict, str]:
    """The block of every read (revision section 4.2 rule 2), its record and how it was chosen."""
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    def latest() -> tuple[int, str]:
        bn = rpc.batch([("eth_blockNumber", [])], valid=is_quantity)[0]["result"]
        return int(bn, 16), rpc.answered()

    def record(host: str, number: int, served: bool | None) -> dict:
        return {"rpc": host, "block_number": number, "block_hex": hex(number), "read_at": now,
                "pinned_requested": block, "pinned_served": served}

    if block is None:
        number, host = latest()
        return record(host, number, None), "the latest block at the first read"
    serving = [i for i in range(len(rpc.urls)) if rpc.serves(i, hex(block))]
    if serving:
        rpc.use(serving)
        return (record(rpc.hosts[serving[0]], block, True),
                "requested; served by " + ", ".join(rpc.hosts[i] for i in serving))
    if not fallback:
        raise SystemExit(f"refused: no RPC serves block {block:,} (--fallback-latest pins the latest block instead)")
    number, host = latest()
    serving = [i for i in range(len(rpc.urls)) if rpc.serves(i, hex(number))]
    if not serving:
        raise SystemExit(f"refused: no RPC serves the latest block {number:,} either")
    rpc.use(serving)
    return record(host, number, False), f"block {block:,} is not served; the latest block at the first read instead"


class Output:
    """The rows read so far, saved as OUTPUT_STEM parquet parts with OUTPUT_STEM.json beside them."""

    def __init__(self, stem: Path, meta: dict, done: pd.DataFrame | None, probe: bool, rpc: Rpc):
        self.stem, self.meta, self.probe, self.rpc = stem, meta, probe, rpc
        self.meta_path = stem.with_suffix(".json")
        self.done = done if done is not None else pd.DataFrame()
        self.new: list[tuple] = []                  # pass 1: rows read in this run
        self.cols: dict[str, list] | None = None    # pass 2: every row by column, changed in place
        self.calls_before = Counter(meta.get("rpc_calls", {}))
        self.probes_before = Counter(meta.get("probes", {}))
        self.stats: Counter[str] = Counter()
        # pass 2: the probed addresses whose result rests on a call the node aborted at every attempt
        self.aborted: set[str] = set(meta.get("aborted_addresses", []))
        self.todo = self.read = 0

    def add(self, rows: list[tuple]) -> None:
        self.new.extend(rows)
        self.read += len(rows)

    def frame(self) -> pd.DataFrame:
        if not self.probe:  # the layout of the registered reads, built as before
            new = pd.DataFrame(self.new, columns=["address", "code_kind"])
            done = self.done
            allr = pd.concat([done[["address", "code_kind"]], new], ignore_index=True) if not done.empty else new
            allr["account_class"] = allr["code_kind"].map(CLASS)
            return allr.sort_values("address").reset_index(drop=True)
        if self.cols is not None:
            df = pd.DataFrame(self.cols)
        else:
            new = pd.DataFrame(self.new, columns=STORED)
            df = pd.concat([self.done[STORED], new], ignore_index=True) if not self.done.empty else new
        wk = df["wallet_kind"]
        smart = wk.notna() & (wk != "")
        df["account_class"] = df["code_kind"].map(CLASS).where(~smart, "smart_account")
        return df.sort_values("address").reset_index(drop=True)[PROBE_COLUMNS]

    def to_columns(self) -> dict[str, list]:
        """Every row by column in address order, for pass 2."""
        df = self.frame()
        cols = {name: df[name].tolist() for name in STORED}
        for name in ("proxy_kind", "implementation", "wallet_kind"):
            cols[name] = [v if isinstance(v, str) else None for v in cols[name]]
        self.cols, self.new, self.done = cols, [], pd.DataFrame()
        return cols

    def write_meta(self) -> None:
        self.meta_path.parent.mkdir(parents=True, exist_ok=True)
        self.meta_path.write_text(json.dumps(self.meta, indent=2), encoding="utf-8")

    def save(self) -> None:
        df = self.frame()
        if self.probe:
            write_parts(pa.Table.from_pandas(df, schema=PROBE_SCHEMA, preserve_index=False), self.stem)
        else:
            write_parts(df, self.stem)
        m = self.meta
        m["counts"] = df["code_kind"].value_counts().to_dict()
        m["n"] = int(len(df))
        m["counts_account_class"] = df["account_class"].value_counts().to_dict()
        if self.probe:
            wk = df["wallet_kind"]
            m["counts_proxy_kind"] = df["proxy_kind"].value_counts().to_dict()
            m["counts_wallet_kind"] = wk[wk.notna()].value_counts().to_dict()
            m["pending"] = int(wk.isna().sum())
            m["probes"] = dict(self.probes_before + self.stats)
            m["aborted_addresses"] = sorted(self.aborted)
        with self.rpc.lock:
            m["rpc_calls"] = dict(self.calls_before + self.rpc.calls)
        m["complete"] = self.read == self.todo and not m.get("pending", 0)
        m["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.write_meta()


# --- passes -------------------------------------------------------------------------------------

def read_addresses(path: str, column: str, parquet: bool) -> list[str]:
    """The distinct addresses of the input column in input order, as lowercase 0x hex (20-byte binary
    values are converted); any other value is refused."""
    values = read_parts(Path(path), columns=[column])[column] if parquet else pd.read_csv(path)[column]
    out = []
    for v in values.tolist():
        if isinstance(v, (bytes, bytearray, memoryview)) and len(v) == 20:
            v = "0x" + bytes(v).hex()
        out.append(v.lower() if isinstance(v, str) else v)
    bad = [v for v in out if not (isinstance(v, str) and ADDRESS.fullmatch(v))]
    if bad:
        raise SystemExit(f"refused: {len(bad):,} values of column {column!r} are not addresses, e.g. {bad[:3]}")
    return list(dict.fromkeys(out))


def probe_wallets(out: Output, rpc: Rpc, rules: Rules, block_hex: str, workers: int, batch: int) -> None:
    """Pass 2 on every contract not yet probed, at the block of pass 1 (revision sections 4.2 and 4.3)."""
    c = out.to_columns()
    addr = c["address"]
    n = len(addr)

    def stage(fn: Callable[[Any], Any], items: list, apply: Callable[[Any], None], label: str, size: int) -> None:
        if not items:
            return
        count = [0]

        def applied(res: list) -> None:
            apply(res)
            count[0] += len(res)

        def save() -> None:
            out.save()
            print(f"pass 2, {label}: {count[0]:,}/{len(items):,}", flush=True)

        run_ordered(fn, [items[k:k + size] for k in range(0, len(items), size)], workers, applied, save, rpc)
        save()

    def slot_reader(slot: str) -> Callable[[list[tuple[int, str]]], list[tuple[int, int]]]:
        """eth_getStorageAt of ``slot`` for (row, address) items: the low 20 bytes of each word, the address."""
        def read(chunk: list[tuple[int, str]]) -> list[tuple[int, int]]:
            answers = rpc.batch([("eth_getStorageAt", [a, slot, block_hex]) for _, a in chunk],
                                valid=lambda r: storage_value(r) is not None)
            return [(i, storage_value(x["result"]) & ADDRESS_MASK) for (i, _), x in zip(chunk, answers)]
        return read

    # a. ERC-1967 proxies: the implementation slot of every contract whose code holds its constant. A code that
    # also holds the masterCopy() selector and whose slot is empty is a Safe proxy, whose slot 0 is read next.
    slots = [(i, addr[i]) for i in range(n) if c["code_kind"][i] == "contract" and c["proxy_kind"][i] is None]

    def set_slots(res: list[tuple[int, int]]) -> None:
        for i, impl in res:
            kind = proxy_after_slot(bool(impl), c["has_master_copy"][i])
            c["implementation"][i] = f"0x{impl:040x}" if impl else (None if kind == "safe" else "")
            c["proxy_kind"][i] = kind                                # set last: resolved
        out.stats["storage_reads"] += len(res)

    stage(slot_reader(rules.slot_hex), slots, set_slots, "ERC-1967 slots", batch)

    # a2. Safe proxies: the singleton in storage slot 0 (revision section 4.3) is the implementation whose code
    # rule 3(b) examines; a slot 0 that holds no address leaves the proxy's own code examined.
    singletons = [(i, addr[i]) for i in range(n) if c["proxy_kind"][i] == "safe" and c["implementation"][i] is None]

    def set_singletons(res: list[tuple[int, int]]) -> None:
        for i, impl in res:
            c["implementation"][i] = f"0x{impl:040x}" if impl else ""
        out.stats["safe_slots"] += len(res)

    stage(slot_reader(SAFE_SLOT), singletons, set_singletons, "Safe singletons", batch)

    # b. The PUSH4 tests of a proxy examine its implementation's code, read once per implementation.
    by_impl: dict[str, list[int]] = {}
    for i in range(n):
        if (c["wallet_kind"][i] is None and c["proxy_kind"][i] in ("eip1167", "erc1967", "safe")
                and c["implementation"][i]):
            by_impl.setdefault(c["implementation"][i], []).append(i)

    def read_impls(chunk: list[str]) -> list[tuple[str, bool, bool]]:
        answers = rpc.batch([("eth_getCode", [a, block_hex]) for a in chunk])
        res = []
        for a, x in zip(chunk, answers):
            code = hex_bytes(x["result"]) or b""
            res.append((a, has_push4(code, rules.validate_user_op), has_push4(code, rules.validate_paymaster)))
        return res

    def set_impls(res: list[tuple[str, bool, bool]]) -> None:
        for a, vu, pm in res:
            for i in by_impl[a]:
                c["has_validate_userop"][i], c["has_paymaster_selector"][i] = vu, pm
        out.stats["implementations"] += len(res)

    stage(read_impls, sorted(by_impl), set_impls, "implementations", batch)

    # c. The calls (revision section 4.3, Probes). Address by address: ERC-1967 proxies and Safe proxies
    # (the stage of the representatives) and every other address of a code hash whose representative
    # answered getThreshold() with a 32-byte word (the second stage). Every other code hash is probed on
    # its representative, the lowest address, whose results are copied to the rest of the hash.
    def set_result(i: int, result: tuple[int, int, str, str]) -> None:
        c["threshold"][i], c["n_owners"][i], c["entry_point"][i] = result[:3]
        c["wallet_kind"][i] = result[3]                          # set last: the row is then finished

    def single(i: int) -> str | None:
        """The count of a contract probed address by address whatever its code hash, else None."""
        if c["proxy_kind"][i] == "erc1967":
            return "erc1967"
        return "safe_proxies" if c["has_master_copy"][i] else None

    # The other contracts by code hash, each list in address order (the rows are sorted by address).
    groups: dict[str, list[int]] = {}
    for i in range(n):
        if c["code_kind"][i] == "contract" and single(i) is None:
            groups.setdefault(c["code_hash"][i], []).append(i)

    def decision(h: str) -> tuple[str, tuple | None]:
        """How the unprobed addresses of a code hash are typed: 'open' while no address of it has been
        probed (its representative is still to be probed); 'each' if a probed address answered
        getThreshold() with a 32-byte word, so the rest is probed address by address; else 'copy' with
        the results of its lowest probed address, the representative, which hold for the hash."""
        done = [i for i in groups[h] if c["wallet_kind"][i] is not None]
        if not done:
            return "open", None
        if any(c["threshold"][i] >= 0 for i in done):
            return "each", None
        i = done[0]
        return "copy", (c["threshold"][i], c["n_owners"][i], c["entry_point"][i], c["wallet_kind"][i])

    def copy_to_hash(h: str, result: tuple) -> None:
        rows = [i for i in groups[h] if c["wallet_kind"][i] is None]
        for i in rows:
            set_result(i, result)
        out.stats["copied"] += len(rows)

    def jobs_of(targets: list[tuple[str, int]]) -> list[tuple]:
        return [(kind, i, addr[i], c["has_validate_userop"][i], c["has_paymaster_selector"][i])
                for kind, i in sorted(targets, key=lambda t: t[1])]

    def probe(chunk: list[tuple]) -> list[tuple]:
        calls = [("eth_call", [{"to": a, "data": sel}, block_hex]) for _, _, a, _, _ in chunk for sel in rules.calls]
        # A call to a system address runs a precompile, not code: every error it answers is its own failure,
        # except the node's abort at its time limit, which follows the abort rule like that of any call.
        system = [rules.is_system(a) for _, _, a, _, _ in chunk for _ in rules.calls]
        answers = rpc.batch(calls, failed=lambda k, e: (system[k] and not is_aborted_error(e)) or is_call_failure(e),
                            settle=lambda k, e: is_aborted_error(e))
        return [(kind, i, evaluate(answers[3 * k:3 * k + 3], vu, pm, rules),
                 sum(map(is_aborted, answers[3 * k:3 * k + 3]))) for k, (kind, i, _, vu, pm) in enumerate(chunk)]

    def set_probes(res: list[tuple]) -> None:
        for kind, i, result, aborted in res:
            set_result(i, result)
            out.stats[kind] += 1
            if kind == "representatives" and result[0] < 0:   # no 32-byte getThreshold() word: copied
                copy_to_hash(c["code_hash"][i], result)
            if aborted:   # aborted at every attempt: the call failed its test
                out.stats["aborted_calls"] += aborted
                out.aborted.add(addr[i])

    first: list[tuple[str, int]] = []
    for h, rows in groups.items():
        how, result = decision(h)
        if how == "open":
            first.append(("representatives", rows[0]))
        elif how == "copy":   # a representative probed in an earlier run
            copy_to_hash(h, result)
    first += [(kind, i) for i in range(n) if c["wallet_kind"][i] is None and (kind := single(i)) is not None]
    first_jobs = jobs_of(first)
    stage(probe, first_jobs, set_probes, "probes", max(1, batch // 3))

    second = [("threshold_hashes", i) for h, rows in groups.items() if decision(h)[0] == "each"
              for i in rows if c["wallet_kind"][i] is None]
    second_jobs = jobs_of(second)
    stage(probe, second_jobs, set_probes, "probes of getThreshold() hashes", max(1, batch // 3))
    if not first_jobs and not second_jobs:  # copies of earlier results only, or nothing left: record the state
        out.save()


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Account types from eth_getCode and, with --probe-wallets, "
                                             "proxies and smart accounts (docs/revision_contract_graph.md 4.2-4.3)")
    ap.add_argument("input", help="CSV file, or with --input-parquet a parquet part stem")
    ap.add_argument("output_stem")
    ap.add_argument("--column", default="address")
    ap.add_argument("--input-parquet", action="store_true", help="INPUT is a parquet part stem")
    ap.add_argument("--block", type=int, help="read at this block (default: the latest block at the first read)")
    ap.add_argument("--fallback-latest", action="store_true",
                    help="with --block: pin the latest block at the first read if no RPC serves the block")
    ap.add_argument("--rpc", action="extend", nargs="+", metavar="URL",
                    help="RPC URLs in order (default: accounts.rpc_url); with --block or --probe-wallets after "
                         "CONTRACT_REP_RPC_URL")
    ap.add_argument("--workers", type=int, default=WORKERS)
    ap.add_argument("--batch", type=int, default=BATCH, help="JSON-RPC calls per request")
    ap.add_argument("--probe-wallets", action="store_true",
                    help="pass 2: proxies, Safes and ERC-4337 accounts; the calls go address by address to "
                         "ERC-1967 proxies, Safe proxies and every address of a code hash whose representative "
                         "answers getThreshold() with a 32-byte word, and to one representative (the lowest "
                         "address) of every other code hash, whose results are copied to the rest of the hash")
    args = ap.parse_args(argv)
    if args.fallback_latest and args.block is None:
        ap.error("--fallback-latest needs --block")
    if args.block is not None and args.block < 0:
        ap.error("--block must not be negative")
    if args.workers < 1 or args.batch < 1:
        ap.error("--workers and --batch must be at least 1")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    cfg = load_config()
    rules = None
    if args.probe_wallets:
        if "contract_graph" not in cfg:
            raise SystemExit("--probe-wallets reads cfg['contract_graph']: set CONTRACT_REP_VARIANT=contract12m")
        rules = Rules.from_config(cfg["contract_graph"])
    prefix = cfg["accounts"]["delegation_prefix"]
    stem = Path(args.output_stem)
    meta_path = stem.with_suffix(".json")

    addrs = read_addresses(args.input, args.column, args.input_parquet)
    done = read_parts(stem) if part_paths(stem) else None
    if done is not None and list(done.columns) != (PROBE_COLUMNS if rules else BASE_COLUMNS):
        raise SystemExit(f"refused: {stem.name} has the columns {list(done.columns)}; it was not written "
                         f"{'with' if rules else 'without'} --probe-wallets")
    meta = clean_meta(json.loads(meta_path.read_text(encoding="utf-8"))) if meta_path.exists() else {}
    if done is not None and "block_number" not in meta:
        raise SystemExit(f"refused: {stem.name} has parts but {meta_path.name} records no block")
    check_resume(meta, args.block, args.fallback_latest, meta_path.name)
    # The reads of the contract-graph revision (revision sections 4.2 and 4.3), or the resumption of an output
    # they wrote; the registered usage (no --block, no --probe-wallets) keeps its URLs and its resumption.
    revision = (args.probe_wallets or args.block is not None or meta.get("pinned_requested") is not None
                or "resume_key" in meta)
    urls = rpc_urls(args.rpc, cfg, use_env=revision)
    key = resume_key(rules, prefix, addrs) if revision else None
    if key is not None and "block_number" in meta:
        check_key(meta, key, meta_path.name)

    rpc = Rpc(urls)
    try:
        if "block_number" in meta:
            how = "resumed"
            # A requested block (or its fallback) is read only where it is served; the latest block of a
            # read without --block is read as before.
            if args.block is not None or meta.get("pinned_requested") is not None:
                serving = [i for i in range(len(urls)) if rpc.serves(i, meta["block_hex"])]
                if not serving:
                    raise SystemExit(f"refused: no RPC serves block {int(meta['block_number']):,} of {meta_path.name} "
                                     "any more; a run resumes only at the same block")
                rpc.use(serving)
                how = "resumed; served by " + ", ".join(rpc.hosts[i] for i in serving)
                meta["served_by"] = [rpc.hosts[i] for i in serving]
            meta.setdefault("pinned_requested", None)
            meta.setdefault("pinned_served", None)
        else:
            meta, how = pin(rpc, args.block, args.fallback_latest)
            if args.block is not None:   # the reads go only to the endpoints that serve the block
                meta["served_by"] = [rpc.hosts[i] for i in rpc.pool]
            if key is not None:
                meta["resume_key"] = key
                if rules is not None:
                    meta["rules"] = rules.record()
    except RpcError as exc:
        print(f"stopped before any read: {exc}", file=sys.stderr)
        return 1
    block_hex = meta["block_hex"]
    print(f"block {int(meta['block_number']):,}: {how}", flush=True)

    known = set(done["address"]) if done is not None else set()
    todo = [a for a in addrs if a not in known]
    out = Output(stem, meta, done, rules is not None, rpc)
    out.todo = len(todo)
    out.write_meta()

    def read_codes(chunk: list[str]) -> list[tuple]:
        answers = rpc.batch([("eth_getCode", [a, block_hex]) for a in chunk])
        return [code_row(a, x["result"], prefix, rules) for a, x in zip(chunk, answers)]

    def progress() -> None:
        out.save()
        print(f"{out.read:,}/{out.todo:,}", flush=True)

    try:
        run_ordered(read_codes, [todo[k:k + args.batch] for k in range(0, len(todo), args.batch)], args.workers,
                    out.add, progress, rpc)
        out.save()
        if rules is not None:
            probe_wallets(out, rpc, rules, block_hex, args.workers, args.batch)
    except RpcError as exc:
        print(f"stopped: {exc}; the rows read so far are saved, run again to resume", file=sys.stderr)
        return 1
    print(out.meta["counts"])
    if rules is not None:
        print(out.meta["counts_account_class"], out.meta["counts_wallet_kind"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
