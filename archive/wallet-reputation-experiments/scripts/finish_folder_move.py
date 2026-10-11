#!/usr/bin/env python3
"""Move what git left behind after the folder renamings of 1 and 7 October 2026.

`git pull` moves every tracked file to its new folder. It cannot move what git
does not track: the virtual environment (.venv), ignored data files over
100 MiB, partial downloads (_chunks), logs, and the checkout of the manuscript
submodule. Those stay in the old folders. This script moves them to the new
folders:

  1 October  A-Skill-Programs/margin_rank/  -> wallet-reputation-experiments/
             (old data folder names translated with project_paths.current_path())
             2-Dissertation-Draft/          -> dissertation/
  7 October  2-Dissertation-Draft-Works/    -> 1-Dissertation-Works/<title>/dissertation/
             1-Proposal/                    -> 1-Dissertation-Works/<title>/proposal/
             4-Graduation/                  -> 2-Graduation/
             5-Roundtable/                  -> 3-Roundtable/

3-Career/ was removed from the repository on 7 October; files git does not
track there are only reported, never moved or deleted.

Run it once, after the pull, from the repository root, with any Python 3.9 or
newer that is not the old .venv (no packages needed):

    python 1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/dissertation/wallet-reputation-experiments/scripts/finish_folder_move.py
    python 1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/dissertation/wallet-reputation-experiments/scripts/finish_folder_move.py --apply

The first command only prints the plan. Nothing is overwritten: a file whose
new place is already taken is reported and left where it is. Python caches
(__pycache__, .pytest_cache) in the old folders are deleted, since they are
rebuilt on the next run, and old folders that end up empty are removed.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from project_paths import REPO_ROOT, ROOT, WORKS_DIR, current_path

OLD_PROJECT = REPO_ROOT / "A-Skill-Programs" / "margin_rank"
OLD_DRAFT = REPO_ROOT / "2-Dissertation-Draft"
OLD_WORKS = REPO_ROOT / "2-Dissertation-Draft-Works"
# (old folder, new folder, translate old data folder names), oldest move first.
MOVES: tuple[tuple[Path, Path, bool], ...] = (
    (OLD_PROJECT, ROOT, True),
    (OLD_DRAFT, WORKS_DIR, False),
    (OLD_WORKS, WORKS_DIR, False),
    (REPO_ROOT / "1-Proposal", WORKS_DIR.parent / "proposal", False),
    (REPO_ROOT / "4-Graduation", REPO_ROOT / "2-Graduation", False),
    (REPO_ROOT / "5-Roundtable", REPO_ROOT / "3-Roundtable", False),
)
OLD_ROOTS = tuple(old for old, _new, _translate in MOVES)
REMOVED = REPO_ROOT / "3-Career"
OLD_SUBMODULES = (OLD_DRAFT / "overleaf-github", OLD_WORKS / "overleaf-github")
NEW_SUBMODULE = WORKS_DIR / "overleaf-github"
CACHE_DIRS = {"__pycache__", ".pytest_cache"}


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(REPO_ROOT), capture_output=True, text=True, check=False)


def _size(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def _mb(n: int) -> str:
    return f"{n / 1e6:,.1f} MB"


def _is_empty_dir(path: Path) -> bool:
    return path.is_dir() and not any(path.iterdir())


def _submodule_gitdir(worktree: Path) -> Path | None:
    """The git directory a submodule checkout points to through its .git file."""
    dot_git = worktree / ".git"
    if not dot_git.is_file():
        return None
    text = dot_git.read_text(encoding="utf-8").strip()
    if not text.startswith("gitdir:"):
        return None
    return (worktree / text[len("gitdir:") :].strip()).resolve()


def plan_submodule() -> tuple[Path, Path] | None:
    old = next((p for p in OLD_SUBMODULES if (p / ".git").exists()), None)
    if old is None:
        return None
    if NEW_SUBMODULE.exists() and not _is_empty_dir(NEW_SUBMODULE):
        print(f"! {NEW_SUBMODULE} is already checked out; {old} is left alone.")
        print("  Commit or copy anything you need from the old one, then delete it by hand.")
        return None
    return old, NEW_SUBMODULE


def move_submodule(old: Path, new: Path) -> bool:
    gitdir = _submodule_gitdir(old)
    try:
        if new.exists():
            new.rmdir()  # the empty folder git created on the pull
        shutil.move(str(old), str(new))
    except OSError as exc:
        print(f"! could not move the submodule checkout: {exc}")
        print("  Close programs that have files open in it (editor, PDF viewer, terminal) and run again.")
        return False
    if gitdir is None:
        return True  # a self-contained checkout (.git is a folder): nothing to reconnect
    rel_gitdir = Path(os.path.relpath(gitdir, new)).as_posix()
    (new / ".git").write_text(f"gitdir: {rel_gitdir}\n", encoding="utf-8")
    rel_worktree = Path(os.path.relpath(new, gitdir)).as_posix()
    result = _git("config", "--file", str(gitdir / "config"), "core.worktree", rel_worktree)
    if result.returncode != 0:
        print(f"! could not set core.worktree in {gitdir / 'config'}: {result.stderr.strip()}")
        return False
    return True


def plan_files(old_root: Path, new_root: Path, translate: bool) -> tuple[list, list, list]:
    """(moves, conflicts, caches) for everything left under old_root."""
    moves: list[tuple[Path, Path]] = []
    conflicts: list[tuple[Path, Path]] = []
    caches: list[Path] = []
    if not old_root.exists():
        return moves, conflicts, caches
    for dirpath, dirnames, filenames in os.walk(old_root):
        here = Path(dirpath)
        if here in OLD_SUBMODULES:
            dirnames[:] = []
            continue
        for name in list(dirnames):
            if name in CACHE_DIRS:
                caches.append(here / name)
                dirnames.remove(name)
            elif name == ".venv":
                # The environment moves as one folder.
                old = here / name
                new = new_root / old.relative_to(old_root)
                (conflicts if new.exists() else moves).append((old, new))
                dirnames.remove(name)
        for name in filenames:
            old = here / name
            rel = old.relative_to(old_root).as_posix()
            new = new_root / (current_path(rel) if translate else rel)
            (conflicts if new.exists() else moves).append((old, new))
    return moves, conflicts, caches


def remove_empty_dirs(root: Path) -> None:
    if not root.exists():
        return
    for dirpath, _dirnames, _filenames in os.walk(root, topdown=False):
        path = Path(dirpath)
        if _is_empty_dir(path):
            path.rmdir()


def remove_old_dirs() -> None:
    for old in OLD_ROOTS:
        remove_empty_dirs(old)
    remove_empty_dirs(REPO_ROOT / "A-Skill-Programs")


def report_removed() -> None:
    """3-Career left the repository; say what is still there, but touch nothing."""
    remove_empty_dirs(REMOVED)
    if REMOVED.exists():
        count = sum(1 for p in REMOVED.rglob("*") if p.is_file())
        print(f"note  {REMOVED.relative_to(REPO_ROOT)} is no longer in the repository but still holds {count} files"
              " git does not track. They are left alone; delete the folder by hand if you do not need them.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true", help="move the files (without it, only print the plan)")
    args = parser.parse_args()

    tracked = _git("ls-files", "--", *(p.relative_to(REPO_ROOT).as_posix() for p in OLD_ROOTS))
    if tracked.returncode != 0:
        print(f"git failed: {tracked.stderr.strip()}")
        return 1
    if tracked.stdout.strip():
        print("Git still tracks files in the old folders. Run `git pull` first, then this script.")
        return 1
    current_prefix = Path(sys.prefix).resolve()

    submodule = plan_submodule()
    moves: list[tuple[Path, Path]] = []
    conflicts: list[tuple[Path, Path]] = []
    caches: list[Path] = []
    for old_root, new_root, translate in MOVES:
        root_moves, root_conflicts, root_caches = plan_files(old_root, new_root, translate)
        moves += root_moves
        conflicts += root_conflicts
        caches += root_caches
    running_from_old_venv = any(o.name == ".venv" and o.resolve() == current_prefix for o, _n in moves)
    if running_from_old_venv:
        moves = [(o, n) for o, n in moves if o.resolve() != current_prefix]
    report_removed()

    if not (submodule or moves or conflicts or caches):
        print("Nothing is left in the old folders.")
        remove_old_dirs()
        return 0

    if submodule:
        print(f"submodule  {submodule[0].relative_to(REPO_ROOT)} -> {submodule[1].relative_to(REPO_ROOT)}")
    total = 0
    for old, new in moves:
        size = _size(old)
        total += size
        print(f"move  {old.relative_to(REPO_ROOT)}\n   -> {new.relative_to(REPO_ROOT)}  ({_mb(size)})")
    for old, new in conflicts:
        print(f"skip  {old.relative_to(REPO_ROOT)}: {new.relative_to(REPO_ROOT)} already exists")
    for path in caches:
        print(f"delete cache  {path.relative_to(REPO_ROOT)}")
    if running_from_old_venv:
        print("! This Python runs from the old .venv, so the .venv stays. Run the script with another Python.")
    print(f"{len(moves)} items to move ({_mb(total)}), {len(conflicts)} left in place, {len(caches)} caches.")

    if not args.apply:
        print("Nothing was changed. Run again with --apply to do it.")
        return 0

    failed = 0
    if submodule and not move_submodule(*submodule):
        failed += 1
    for old, new in moves:
        try:
            new.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(old), str(new))
        except OSError as exc:
            failed += 1
            print(f"! could not move {old}: {exc}")
    for path in caches:
        shutil.rmtree(path, ignore_errors=True)
    remove_old_dirs()
    left = [p for p in OLD_ROOTS if p.exists()]
    print(f"Done: {len(moves) + bool(submodule) - failed} moved, {failed} failed.")
    if left:
        print("Still there (see the messages above): " + ", ".join(str(p.relative_to(REPO_ROOT)) for p in left))
    if any(o.name == ".venv" for o, _ in moves):
        print("The .venv was moved. If `pip` complains about a path, use `python -m pip`, or make the venv again.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
