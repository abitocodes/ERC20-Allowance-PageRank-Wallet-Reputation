#!/usr/bin/env python3
"""Keep the blockchain data in the public Google Drive folder and in this repository in step.

The data folders are mirrored under one Drive folder that anyone with the link can read:

    contract-reputation/        <- experiments/data
    wallet-reputation-archive/  <- archive/wallet-reputation-experiments/data

GitHub keeps the code, the small records and the published results; the parquet files live
only on Drive. experiments/drive-manifest.json (committed) lists every file on Drive with its
Drive id, size and MD5, so a clone can fetch exactly the files it needs and check them.

    python scripts/drive_sync.py status            # what differs between local and Drive
    python scripts/drive_sync.py push              # upload new local files, refresh the manifest
    python scripts/drive_sync.py pull "*graph-tables-usd/*"   # fetch matching files
    python scripts/drive_sync.py pull --all        # fetch everything (about 10 GB)

push needs rclone with a Google Drive remote (default name phd-gdrive, or DRIVE_SYNC_REMOTE).
pull needs nothing but Python: without rclone it downloads by Drive id over HTTPS, through
www.googleapis.com when GDRIVE_API_KEY is set, otherwise through drive.usercontent.google.com.
push only adds files: it never deletes anything on Drive, and it leaves files already there
untouched unless --allow-overwrite is given, because the dissertation cites these files.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

EXPERIMENTS = Path(__file__).resolve().parents[1]
THESIS = EXPERIMENTS.parent
MANIFEST = EXPERIMENTS / "drive-manifest.json"
DRIVE_README = EXPERIMENTS / "docs" / "drive-data-readme.md"

REMOTE = os.environ.get("DRIVE_SYNC_REMOTE", "phd-gdrive")
DRIVE_ROOT = "phd_works-blockchain-data"
# Drive folder under DRIVE_ROOT -> local folder relative to THESIS.
ROOTS = {
    "contract-reputation": "experiments/data",
    "wallet-reputation-archive": "archive/wallet-reputation-experiments/data",
}
# Scratch and caches that are never published.
EXCLUDE_DIRS = {"_work", "__pycache__", "_chunks", ".pytest_cache"}
EXCLUDE_SUFFIXES = {".log", ".pyc", ".tmp"}
EXCLUDE_NAMES = {".DS_Store", "desktop.ini"}
RCLONE_FILTERS = [
    "--exclude", "_work/**", "--exclude", "__pycache__/**", "--exclude", "_chunks/**",
    "--exclude", ".pytest_cache/**", "--exclude", "*.log", "--exclude", "*.pyc",
    "--exclude", "*.tmp", "--exclude", ".DS_Store", "--exclude", "desktop.ini",
]
CHUNK = 1 << 20


# --- paths and manifest -------------------------------------------------------------------

def local_path(drive_path: str) -> Path:
    top, _, rest = drive_path.partition("/")
    return THESIS / ROOTS[top] / rest


def excluded(rel: Path) -> bool:
    return (any(p in EXCLUDE_DIRS for p in rel.parts[:-1]) or rel.suffix in EXCLUDE_SUFFIXES
            or rel.name in EXCLUDE_NAMES)


def local_files() -> dict[str, Path]:
    """Drive path -> local file, for every publishable file under the data folders."""
    out = {}
    for top, rel_root in ROOTS.items():
        base = THESIS / rel_root
        for p in sorted(base.rglob("*")):
            rel = p.relative_to(base)
            if p.is_file() and not excluded(rel):
                out[f"{top}/{rel.as_posix()}"] = p
    return out


def load_manifest() -> dict:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {"remote_folder": DRIVE_ROOT, "files": []}


def md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        while block := f.read(CHUNK):
            h.update(block)
    return h.hexdigest()


def matches(drive_path: str, patterns: list[str]) -> bool:
    if not patterns:
        return True
    local_rel = local_path(drive_path).relative_to(THESIS).as_posix()
    return any(fnmatch.fnmatch(drive_path, pat) or fnmatch.fnmatch(local_rel, pat) for pat in patterns)


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} GB"


# --- rclone -------------------------------------------------------------------------------

def rclone_bin() -> str | None:
    return os.environ.get("RCLONE") or shutil.which("rclone")


def rclone(*args: str, capture: bool = False) -> str:
    exe = rclone_bin()
    if exe is None:
        raise SystemExit("rclone is not installed (or set RCLONE to its path); push and remote listing need it")
    res = subprocess.run([exe, *args], text=True, encoding="utf-8",
                         stdout=subprocess.PIPE if capture else None)
    if res.returncode != 0:
        # The OAuth app is in Google's "testing" state, so the Drive login lapses after 7 days.
        raise SystemExit(f"rclone {args[0]} failed with exit code {res.returncode}. If the log above "
                         f"says invalid_grant or token expired, log in again with: "
                         f"rclone config reconnect {REMOTE}:")
    return res.stdout or ""


def rclone_remote_ready() -> bool:
    exe = rclone_bin()
    if exe is None:
        return False
    res = subprocess.run([exe, "listremotes"], text=True, capture_output=True)
    return res.returncode == 0 and f"{REMOTE}:" in res.stdout.split()


def remote_listing() -> list[dict]:
    """Every file under DRIVE_ROOT on Drive, as manifest entries."""
    raw = rclone("lsjson", "-R", "--files-only", "--hash", "--hash-type", "md5",
                 f"{REMOTE}:{DRIVE_ROOT}", capture=True)
    files = []
    for item in json.loads(raw):
        if item["Path"].split("/", 1)[0] not in ROOTS:
            continue  # README.md and anything else at the top level
        files.append({"path": item["Path"], "id": item["ID"], "size": item["Size"],
                      "md5": item.get("Hashes", {}).get("md5", "")})
    return sorted(files, key=lambda f: f["path"])


def refresh_manifest(manifest: dict) -> dict:
    manifest["files"] = remote_listing()
    manifest["remote_folder"] = DRIVE_ROOT
    manifest["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    manifest["total_bytes"] = sum(f["size"] for f in manifest["files"])
    MANIFEST.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


# --- commands -----------------------------------------------------------------------------

def compare(manifest: dict, patterns: list[str], use_hash: bool) -> dict[str, list[str]]:
    on_drive = {f["path"]: f for f in manifest["files"] if matches(f["path"], patterns)}
    here = {k: v for k, v in local_files().items() if matches(k, patterns)}
    state = {"same": [], "changed": [], "local_only": [], "drive_only": []}
    for path, p in here.items():
        f = on_drive.get(path)
        if f is None:
            state["local_only"].append(path)
        elif p.stat().st_size != f["size"] or (use_hash and md5(p) != f["md5"]):
            state["changed"].append(path)
        else:
            state["same"].append(path)
    state["drive_only"] = sorted(set(on_drive) - set(here))
    return state


def cmd_status(args) -> int:
    manifest = load_manifest()
    if args.remote:
        manifest = {"files": remote_listing()}
    state = compare(manifest, args.patterns, args.hash)
    size = {f["path"]: f["size"] for f in manifest["files"]}
    files = local_files()
    labels = {
        "local_only": "local only (push uploads these)",
        "changed": "differ from Drive" + ("" if args.hash else " by size; --hash also checks MD5"),
        "drive_only": "on Drive only (pull fetches these)",
    }
    print(f"{len(state['same'])} files match the {'Drive listing' if args.remote else 'manifest'}")
    for key, label in labels.items():
        paths = state[key]
        if not paths:
            continue
        total = sum(size[p] if key == "drive_only" else files[p].stat().st_size for p in paths)
        print(f"\n{len(paths)} {label}, {human(total)}:")
        for p in paths[: args.limit]:
            print(f"  {p}")
        if len(paths) > args.limit:
            print(f"  ... and {len(paths) - args.limit} more (--limit)")
    return 0


def cmd_push(args) -> int:
    if not rclone_remote_ready():
        raise SystemExit(f"rclone remote {REMOTE!r} is not configured; see experiments/README.md")
    manifest = load_manifest()
    if not args.allow_overwrite:
        changed = compare(manifest, [], use_hash=False)["changed"]
        if changed:
            print("Not uploaded: these files differ in size from the Drive copies the dissertation cites.")
            for p in changed:
                print(f"  {p}")
            print("Rename the new files, or rerun with --allow-overwrite to replace the Drive copies.\n")
    # By default files already on Drive are left alone, so nothing cited is replaced by accident.
    mode = ["--checksum"] if args.allow_overwrite else ["--ignore-existing"]
    for top, rel_root in ROOTS.items():
        print(f"== {rel_root} -> {DRIVE_ROOT}/{top}")
        cmd = ["copy", str(THESIS / rel_root), f"{REMOTE}:{DRIVE_ROOT}/{top}", *mode,
               "--transfers", "4", "--stats-one-line", "--stats", "30s", "-v", *RCLONE_FILTERS]
        if args.dry_run:
            cmd.append("--dry-run")
        rclone(*cmd)
    if args.dry_run:
        return 0
    if DRIVE_README.exists():
        rclone("copyto", str(DRIVE_README), f"{REMOTE}:{DRIVE_ROOT}/README.md", "--checksum")
    if not manifest.get("folder_url"):
        # Anyone with the link may read the folder; the files inside inherit it.
        manifest["folder_url"] = rclone("link", f"{REMOTE}:{DRIVE_ROOT}", capture=True).strip()
    manifest = refresh_manifest(manifest)
    print(f"\nmanifest: {len(manifest['files'])} files, {human(manifest['total_bytes'])} -> "
          f"{MANIFEST.relative_to(THESIS).as_posix()}")
    print(f"public folder: {manifest['folder_url']}")
    return 0


def download_http(file_id: str, dest: Path) -> None:
    key = os.environ.get("GDRIVE_API_KEY")
    urls = []
    if key:
        urls.append(f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&key={key}")
    urls.append(f"https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm=t")
    last = None
    for url in urls:
        try:
            with urllib.request.urlopen(url, timeout=120) as r, open(dest, "wb") as out:
                if "text/html" in r.headers.get("Content-Type", ""):
                    raise urllib.error.URLError("Drive answered with a web page, not the file")
                shutil.copyfileobj(r, out, CHUNK)
            return
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last = e
    raise SystemExit(f"download of {file_id} failed: {last}")


def cmd_pull(args) -> int:
    if not args.patterns and not args.all:
        raise SystemExit("name the files to fetch (glob on the Drive or local path), or pass --all")
    manifest = load_manifest()
    wanted = [f for f in manifest["files"] if matches(f["path"], args.patterns)]
    use_rclone = args.method == "rclone" or (args.method == "auto" and rclone_remote_ready())
    todo = []
    for f in wanted:
        dest = local_path(f["path"])
        if dest.exists() and dest.stat().st_size == f["size"] and (not args.hash or md5(dest) == f["md5"]):
            continue
        todo.append(f)
    total = sum(f["size"] for f in todo)
    print(f"{len(wanted)} files match; {len(todo)} to fetch, {human(total)}"
          f" via {'rclone' if use_rclone else 'HTTPS'}")
    if args.dry_run:
        for f in todo:
            print(f"  {f['path']}")
        return 0
    done = 0
    for i, f in enumerate(todo, 1):
        dest = local_path(f["path"])
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_name(dest.name + ".tmp")
        if use_rclone:
            rclone("copyto", f"{REMOTE}:{DRIVE_ROOT}/{f['path']}", str(tmp))
        else:
            download_http(f["id"], tmp)
        got = md5(tmp)
        if got != f["md5"]:
            tmp.unlink()
            raise SystemExit(f"MD5 mismatch for {f['path']}: expected {f['md5']}, got {got}")
        os.replace(tmp, dest)
        done += f["size"]
        print(f"[{i}/{len(todo)}] {human(done)}/{human(total)}  {f['path']}", flush=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="command", required=True)

    st = sub.add_parser("status", help="compare local data with the manifest (or Drive with --remote)")
    st.add_argument("patterns", nargs="*", help="glob on the Drive or local path")
    st.add_argument("--hash", action="store_true", help="also compare MD5 (reads every file)")
    st.add_argument("--remote", action="store_true", help="compare with a fresh Drive listing (rclone)")
    st.add_argument("--limit", type=int, default=20, help="paths listed per group")
    st.set_defaults(func=cmd_status)

    pu = sub.add_parser("push", help="upload local files not yet on Drive, then refresh the manifest")
    pu.add_argument("--dry-run", action="store_true")
    pu.add_argument("--allow-overwrite", action="store_true",
                    help="also replace Drive files whose content differs (MD5) from the local file")
    pu.set_defaults(func=cmd_push)

    pl = sub.add_parser("pull", help="download files listed in the manifest")
    pl.add_argument("patterns", nargs="*", help="glob on the Drive or local path")
    pl.add_argument("--all", action="store_true", help="every file in the manifest")
    pl.add_argument("--hash", action="store_true", help="re-fetch local files whose MD5 differs")
    pl.add_argument("--method", choices=("auto", "rclone", "http"), default="auto")
    pl.add_argument("--dry-run", action="store_true")
    pl.set_defaults(func=cmd_pull)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
