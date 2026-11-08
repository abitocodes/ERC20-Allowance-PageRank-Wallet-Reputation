"""Paths for the tests, and read-only import of the wallet-reputation reference scripts."""

from __future__ import annotations

import importlib.util
import os
import re
import sys
from pathlib import Path

import pytest
import yaml

# Nothing is compiled to __pycache__ next to the scripts or the reference, in
# this process or in the bootstrap's worker processes.
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True

EXPERIMENTS = Path(__file__).resolve().parents[1]
SCRIPTS = EXPERIMENTS / "scripts"
CONFIG_PATH = EXPERIMENTS / "config" / "contract_reputation.yaml"
REFERENCE = EXPERIMENTS.parent / "archive" / "wallet-reputation-experiments" / "scripts"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

# Module names the reference scripts import from their own folder; the new
# scripts folder has a common.py of its own, so these must not leak either way.
_REFERENCE_HELPERS = ("common", "project_paths", "pagerank", "proxy_metrics")
_loaded: dict[str, object] = {}


def load_reference(name: str):
    """The reference module ``name``.py, imported by path; nothing under the reference is written."""
    if name in _loaded:
        return _loaded[name]
    saved = {k: sys.modules.pop(k) for k in _REFERENCE_HELPERS if k in sys.modules}
    sys.path.insert(0, str(REFERENCE))
    try:
        spec = importlib.util.spec_from_file_location(f"reference_{name}", REFERENCE / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(REFERENCE))
        for k in _REFERENCE_HELPERS:
            sys.modules.pop(k, None)
        sys.modules.update(saved)
    _loaded[name] = module
    return module


@pytest.fixture(scope="session")
def config() -> dict:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def params(config) -> dict:
    from scoring import pagerank_params

    return pagerank_params(config)


# Tests that take minutes (the earlier variants' full runs beyond usd12m, the checks on the real data) run only when
# CONTRACT_REP_SLOW_TESTS=1.
slow = pytest.mark.skipif(os.environ.get("CONTRACT_REP_SLOW_TESTS") != "1", reason="set CONTRACT_REP_SLOW_TESTS=1")


def gate_b_amendment_files(text: str) -> tuple[str, ...]:
    """The scripts/*.py files that the gate B amendment of revision section 13 names as the evaluation code: the items
    '- `scripts/<name>.py`: ...' of the list after the sentence 'The evaluation code of this variant' (wrapped lines
    of the sentence and of the items are skipped; the list ends at the first non-blank line indented no deeper than
    its items that is not an item)."""
    lines = text[text.index("## 13. Amendments"):].splitlines()
    start = next((i for i, line in enumerate(lines) if "The evaluation code of this variant" in line), None)
    if start is None:
        raise ValueError("section 13 holds no sentence 'The evaluation code of this variant'")
    item = re.compile(r"^(\s*)- `(scripts/[a-z0-9_]+\.py)`:")
    out, indent = [], None
    for line in lines[start + 1:]:
        m = item.match(line)
        if m and (indent is None or len(m.group(1)) == indent):
            indent = len(m.group(1))
            out.append(m.group(2))
        elif indent is not None and line.strip() and len(line) - len(line.lstrip()) <= indent:
            break
    return tuple(out)
