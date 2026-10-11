"""Shared helpers for the wallet-reputation-experiments scripts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from eth_utils import keccak, to_hex

from project_paths import CONFIG_DIR, DATA_DIR, PROCESSED_DIR, RAW_DIR, ROOT, SQL_DIR  # noqa: F401

CONFIG_PATH = CONFIG_DIR / "margin_config.yaml"


def _resolve_path(p: str | Path) -> Path:
    path = Path(p)
    return path if path.is_absolute() else ROOT / path


def load_config(path: Path | None = None) -> dict[str, Any]:
    cfg_path = path or CONFIG_PATH
    with cfg_path.open(encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    _enrich_config(cfg)
    for key, val in cfg.get("paths", {}).items():
        if isinstance(val, str):
            cfg["paths"][key] = str(_resolve_path(val))
    rep = cfg.get("reputation", {})
    for key, val in rep.get("paths", {}).items():
        if isinstance(val, str):
            rep["paths"][key] = str(_resolve_path(val))
    bench = cfg.get("benchmark", {})
    for key in ("supplemental_path", "wallet_set_path"):
        val = bench.get(key)
        if isinstance(val, str):
            bench[key] = str(_resolve_path(val))
    tier2 = bench.get("tier2_paths") or {}
    for key, val in tier2.items():
        if isinstance(val, str):
            tier2[key] = str(_resolve_path(val))
    return cfg


def _enrich_config(cfg: dict[str, Any]) -> None:
    events = cfg.setdefault("events", {})
    if not events.get("event_log1_topic0"):
        events["event_log1_topic0"] = event_log1_topic0()
    for key in ("position_increase", "position_decrease"):
        name = events[key]
        events[f"{key}_hash"] = event_name_hash(name)


def read_sql(name: str) -> str:
    return (SQL_DIR / name).read_text(encoding="utf-8")


def parse_token_amount(val) -> float:
    """Parse ERC-20 uint256 amounts (string or numeric) to float for graph weights."""
    import math

    if val is None:
        return 0.0
    if isinstance(val, float) and math.isnan(val):
        return 0.0
    try:
        return float(val)
    except (ValueError, TypeError):
        pass
    try:
        return float(int(str(val).strip()))
    except (ValueError, OverflowError):
        return 0.0


def normalize_address(addr: str | None) -> str | None:
    if addr is None:
        return None
    s = str(addr).strip().lower()
    if not s:
        return None
    if not s.startswith("0x"):
        s = "0x" + s
    if len(s) == 66:
        s = "0x" + s[-40:]
    return s


def parse_topic_address(topic: str | None) -> str | None:
    return normalize_address(topic)


def event_name_hash(name: str) -> str:
    """Indexed string topic = keccak256(bytes(name))."""
    return to_hex(keccak(text=name))


def event_log1_topic0() -> str:
    """Topic0 for EventLog1 — EventLogData tuple type from GMX EventUtils."""
    key_value = "(string,address)"
    array_kv = "(string,address[])"
    uint_kv = "(string,uint256)"
    uint_akv = "(string,uint256[])"
    int_kv = "(string,int256)"
    int_akv = "(string,int256[])"
    bool_kv = "(string,bool)"
    bool_akv = "(string,bool[])"
    b32_kv = "(string,bytes32)"
    b32_akv = "(string,bytes32[])"
    bytes_kv = "(string,bytes)"
    bytes_akv = "(string,bytes[])"
    str_kv = "(string,string)"
    str_akv = "(string,string[])"

    addr_items = f"(({key_value}[]),({array_kv}[]))"
    uint_items = f"(({uint_kv}[]),({uint_akv}[]))"
    int_items = f"(({int_kv}[]),({int_akv}[]))"
    bool_items = f"(({bool_kv}[]),({bool_akv}[]))"
    b32_items = f"(({b32_kv}[]),({b32_akv}[]))"
    bytes_items = f"(({bytes_kv}[]),({bytes_akv}[]))"
    str_items = f"(({str_kv}[]),({str_akv}[]))"
    event_log_data = (
        f"({addr_items},{uint_items},{int_items},{bool_items},"
        f"{b32_items},{bytes_items},{str_items})"
    )
    sig = f"EventLog1(address,string,string,bytes32,{event_log_data})"
    return to_hex(keccak(text=sig))


def format_bytes(n: int) -> str:
    if n >= 1024**3:
        return f"{n / 1024**3:.2f} GiB"
    if n >= 1024**2:
        return f"{n / 1024**2:.2f} MiB"
    return f"{n} B"


def load_raw_parquet_dir(raw_dir: Path, combined_name: str | None = None) -> pd.DataFrame:
    """Load raw parquet frames; prefer combined *_arbitrum.parquet when present."""
    if combined_name:
        combined = raw_dir / combined_name
        if combined.exists():
            return pd.read_parquet(combined)
    paths = sorted(p for p in raw_dir.glob("*.parquet") if "synthetic" not in p.name)
    if not paths:
        paths = sorted(raw_dir.glob("*.parquet"))
    if not paths:
        raise FileNotFoundError(f"No parquet files in {raw_dir}")
    return pd.concat([pd.read_parquet(p) for p in paths], ignore_index=True)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def bq_table_fqn(cfg: dict[str, Any], table: str) -> str:
    bq = cfg["bigquery"]
    return f"`{bq['dataset']}.{table}`"


def seeded_benchmark_address(seed: str, index: int) -> str:
    """Deterministic address from SHA256(seed:index); used to pad benchmark pool offline."""
    digest = hashlib.sha256(f"{seed}:{index}".encode()).hexdigest()
    return "0x" + digest[-40:]


def merge_extraction_wallets(
    gmx_wallets: list[str],
    config: dict[str, Any],
    supplemental_path: Path | None = None,
    *,
    include_benchmark: bool = True,
) -> tuple[list[str], dict[str, Any]]:
    """Union GMX-qualified wallets with benchmark seed addresses up to target_wallets."""
    gmx_sorted = sorted({w.lower() for w in gmx_wallets})
    bench = config.get("benchmark") or {}
    target = int(bench.get("target_wallets", 0)) if include_benchmark else 0
    meta: dict[str, Any] = {
        "gmx_wallet_count": len(gmx_sorted),
        "target_wallets": target,
        "benchmark_seed": bench.get("seed"),
    }

    if not include_benchmark or target <= 0 or len(gmx_sorted) >= target:
        meta["extraction_wallet_count"] = len(gmx_sorted)
        meta["supplemental_source"] = "none"
        meta["supplemental_count"] = 0
        return gmx_sorted, meta

    merged_set = set(gmx_sorted)
    supplemental_source = ""

    path = supplemental_path
    if path is None and bench.get("supplemental_path"):
        path = Path(bench["supplemental_path"])

    if path and Path(path).exists():
        supplemental_source = str(path)
        df = pd.read_parquet(path)
        if "wallet" not in df.columns:
            raise ValueError(f"Missing wallet column in {path}")
        for wallet in df["wallet"].astype(str).str.lower():
            if len(merged_set) >= target:
                break
            merged_set.add(wallet)
    else:
        seed = str(bench.get("seed", "endorserank-benchmark-v1"))
        supplemental_source = f"sha256:{seed}"
        i = 0
        while len(merged_set) < target:
            merged_set.add(seeded_benchmark_address(seed, i))
            i += 1

    merged = sorted(merged_set)[:target]
    meta["supplemental_source"] = supplemental_source
    meta["supplemental_count"] = max(0, len(merged) - len(gmx_sorted))
    meta["extraction_wallet_count"] = len(merged)
    return merged, meta


def save_extraction_wallet_set(wallets: list[str], config: dict[str, Any]) -> Path | None:
    bench = config.get("benchmark") or {}
    out = bench.get("wallet_set_path")
    if not out:
        return None
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"wallet": wallets}).to_parquet(path, index=False)
    return path


def derive_wallets_from_reputation_parquet(
    allowances: pd.DataFrame,
    transfers: pd.DataFrame,
) -> list[str]:
    """Unique wallet addresses appearing in Tier-1 reputation parquet (includes 1-hop neighbors)."""
    wallets: set[str] = set()
    if not transfers.empty:
        wallets |= set(transfers["from_address"].astype(str).str.lower())
        wallets |= set(transfers["to_address"].astype(str).str.lower())
    if not allowances.empty:
        wallets |= set(allowances["owner"].astype(str).str.lower())
        wallets |= set(allowances["spender"].astype(str).str.lower())
    return sorted(w for w in wallets if w and w.startswith("0x"))


def rank_wallets_by_activity(
    wallets: list[str],
    transfers: pd.DataFrame,
    allowances: pd.DataFrame,
) -> list[str]:
    """Order wallets by inbound+outbound transfer event count (descending)."""
    scores: dict[str, int] = {w.lower(): 0 for w in wallets}
    if not transfers.empty:
        for col in ("from_address", "to_address"):
            counts = transfers[col].astype(str).str.lower().value_counts()
            for w, c in counts.items():
                if w in scores:
                    scores[w] += int(c)
    if not allowances.empty:
        for col in ("owner", "spender"):
            counts = allowances[col].astype(str).str.lower().value_counts()
            for w, c in counts.items():
                if w in scores:
                    scores[w] += int(c)
    return sorted(scores.keys(), key=lambda w: (-scores[w], w))


def build_tier2_wallet_pool(
    gmx_wallets: list[str],
    allowances: pd.DataFrame,
    transfers: pd.DataFrame,
    config: dict[str, Any],
    supplemental_path: Path | None = None,
) -> tuple[list[str], dict[str, Any]]:
    """Union GMX wallets with supplemental/active pool up to target_wallets."""
    bench = config.get("benchmark") or {}
    target = int(bench.get("target_wallets", 100000))
    gmx_sorted = sorted({w.lower() for w in gmx_wallets})

    path = supplemental_path
    if path is None and bench.get("supplemental_path"):
        path = Path(bench["supplemental_path"])

    merged_set = set(gmx_sorted)
    supplemental_source = "reputation_parquet"

    if path and Path(path).exists():
        supplemental_source = str(path)
        df = pd.read_parquet(path)
        if "wallet" not in df.columns:
            raise ValueError(f"Missing wallet column in {path}")
        for wallet in df["wallet"].astype(str).str.lower():
            if len(merged_set) >= target:
                break
            merged_set.add(wallet)
    else:
        derived = derive_wallets_from_reputation_parquet(allowances, transfers)
        ranked = rank_wallets_by_activity(derived, transfers, allowances)
        for wallet in ranked:
            if len(merged_set) >= target:
                break
            merged_set.add(wallet)

    merged = sorted(merged_set)[:target]
    meta = {
        "gmx_wallet_count": len(gmx_sorted),
        "target_wallets": target,
        "extraction_wallet_count": len(merged),
        "supplemental_source": supplemental_source,
        "supplemental_count": max(0, len(merged) - len(gmx_sorted)),
    }
    return merged, meta


def tier2_reputation_paths(config: dict[str, Any]) -> dict[str, str]:
    """Return processed reputation paths preferring Tier-2 parquet when present."""
    bench = config.get("benchmark") or {}
    tier2 = bench.get("tier2_paths") or {}
    rep = config["reputation"]["paths"]
    out = dict(rep)
    for key in ("latest_allowances", "transfer_events"):
        tier2_path = tier2.get(key)
        if tier2_path and Path(tier2_path).exists():
            out[key] = tier2_path
    return out
