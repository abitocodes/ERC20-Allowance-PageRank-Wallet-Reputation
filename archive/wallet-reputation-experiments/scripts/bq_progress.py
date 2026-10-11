"""BigQuery extraction progress, checkpoints, and resilient parquet download."""

from __future__ import annotations

import os
import shutil
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import pandas as pd
import pyarrow.parquet as pq
from google.cloud import bigquery
from google.cloud.bigquery import QueryJobConfig
from tqdm import tqdm

from common import load_json, save_json

# Long-running Storage API reads (default 600s is too short for Tier-2 transfers)
BQ_DOWNLOAD_TIMEOUT_SEC = 7200


@dataclass(frozen=True)
class ExtractionStep:
    month: str
    kind: str  # "approvals" | "transfers"

    @property
    def step_id(self) -> str:
        return f"{self.month}/{self.kind}"


def _fmt_count(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)


class StepProgressBar:
    """Overall multi-step extraction progress with live postfix + log lines."""

    def __init__(self, steps: list[ExtractionStep], initial: int = 0) -> None:
        self._pbar = tqdm(
            total=len(steps),
            initial=initial,
            desc="Overall",
            unit="step",
            position=0,
            leave=True,
            dynamic_ncols=True,
            mininterval=0.5,
        )
        self._steps = steps
        self._download_start: float | None = None

    def set_step(self, step: ExtractionStep) -> None:
        self._download_start = None
        self._pbar.set_postfix_str(step.step_id, refresh=True)

    def advance(self, step: ExtractionStep | None = None) -> None:
        if step is not None:
            self._pbar.set_postfix_str(f"{step.step_id} done", refresh=True)
        self._pbar.update(1)

    def log(self, msg: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        tqdm.write(f"[{ts}] {msg}")
        sys.stdout.flush()

    def update_live(
        self,
        step_id: str,
        *,
        rows: int = 0,
        row_total: int | None = None,
        batches: int = 0,
        tmp_mb: float = 0.0,
        phase: str = "",
    ) -> None:
        parts: list[str] = [step_id]
        if row_total is not None and row_total > 0:
            pct = min(100, int(100 * rows / row_total))
            parts.append(f"rows {_fmt_count(rows)}/{_fmt_count(row_total)} ({pct}%)")
        elif rows > 0:
            parts.append(f"rows {_fmt_count(rows)}")
        if tmp_mb > 0:
            parts.append(f"tmp {tmp_mb:.1f}MB")
        if batches > 0:
            parts.append(f"batch {batches}")
        if phase:
            parts.append(phase)
        self._pbar.set_postfix_str(" | ".join(parts), refresh=True)

    def begin_download(self) -> float:
        self._download_start = time.monotonic()
        return self._download_start

    def rows_per_sec(self, rows: int) -> float:
        if self._download_start is None or rows <= 0:
            return 0.0
        elapsed = time.monotonic() - self._download_start
        return rows / elapsed if elapsed > 0 else 0.0

    def close(self) -> None:
        self._pbar.close()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_checkpoint_block(manifest: dict[str, Any], key: str) -> dict[str, Any]:
    block = manifest.get(key) or {}
    checkpoint = block.get("checkpoint")
    if not isinstance(checkpoint, dict):
        checkpoint = {"steps": []}
        block["checkpoint"] = checkpoint
    if "steps" not in checkpoint or not isinstance(checkpoint["steps"], list):
        checkpoint["steps"] = []
    return block


def find_step_record(checkpoint: dict[str, Any], step_id: str) -> dict[str, Any] | None:
    for rec in checkpoint.get("steps", []):
        if rec.get("step_id") == step_id:
            return rec
    return None


def upsert_step_record(
    checkpoint: dict[str, Any],
    step_id: str,
    **fields: Any,
) -> dict[str, Any]:
    steps: list[dict[str, Any]] = checkpoint.setdefault("steps", [])
    rec = find_step_record(checkpoint, step_id)
    if rec is None:
        rec = {"step_id": step_id}
        steps.append(rec)
    rec.update(fields)
    return rec


def step_is_completed(
    step: ExtractionStep,
    out_path: Path,
    checkpoint: dict[str, Any],
) -> bool:
    if out_path.exists() and out_path.stat().st_size > 0:
        return True
    rec = find_step_record(checkpoint, step.step_id)
    return rec is not None and rec.get("status") == "completed"


def count_completed_steps(
    steps: list[ExtractionStep],
    path_for_step: Callable[[ExtractionStep], Path],
    checkpoint: dict[str, Any],
) -> int:
    return sum(
        1 for s in steps if step_is_completed(s, path_for_step(s), checkpoint)
    )


def save_checkpoint(
    manifest_path: Path,
    manifest_key: str,
    manifest: dict[str, Any],
    block_updates: dict[str, Any] | None = None,
) -> None:
    block = get_checkpoint_block(manifest, manifest_key)
    if block_updates:
        block.update(block_updates)
    manifest[manifest_key] = block
    save_json(manifest_path, manifest)


def atomic_replace(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        dst.unlink()
    os.replace(src, dst)


def _chunks_dir(out_path: Path) -> Path:
    return out_path.parent / "_chunks" / out_path.stem


def _chunk_file(chunk_dir: Path, batch_num: int) -> Path:
    return chunk_dir / f"batch_{batch_num:06d}.parquet"


def _chunk_progress_path(chunk_dir: Path) -> Path:
    return chunk_dir / "progress.json"


def _max_contiguous_chunks(chunk_dir: Path) -> int:
    if not chunk_dir.is_dir():
        return 0
    n = 0
    while _chunk_file(chunk_dir, n + 1).exists():
        n += 1
    return n


def _chunks_total_bytes(chunk_dir: Path) -> float:
    if not chunk_dir.is_dir():
        return 0.0
    return sum(p.stat().st_size for p in chunk_dir.glob("batch_*.parquet")) / (1024 * 1024)


def _load_chunk_progress(chunk_dir: Path) -> dict[str, Any]:
    path = _chunk_progress_path(chunk_dir)
    if path.exists():
        return load_json(path)
    return {}


def _save_chunk_progress(
    chunk_dir: Path,
    *,
    job_id: str,
    batches: int,
    rows: int,
) -> None:
    chunk_dir.mkdir(parents=True, exist_ok=True)
    save_json(
        _chunk_progress_path(chunk_dir),
        {
            "job_id": job_id,
            "batches": batches,
            "rows": rows,
            "updated_at": utc_now_iso(),
        },
    )


def _saved_job_id(
    checkpoint: dict[str, Any],
    step_id: str,
    out_path: Path,
) -> str | None:
    rec = find_step_record(checkpoint, step_id)
    if rec and rec.get("job_id"):
        return str(rec["job_id"])
    prog = _load_chunk_progress(_chunks_dir(out_path))
    if prog.get("job_id"):
        return str(prog["job_id"])
    return None


def merge_parquet_paths(paths: list[Path], out_path: Path) -> int:
    """Merge parquet files without loading entire dataset into RAM."""
    writer: pq.ParquetWriter | None = None
    total = 0
    for path in paths:
        if not path.exists():
            continue
        pf = pq.ParquetFile(path)
        for rg in range(pf.num_row_groups):
            table = pf.read_row_group(rg)
            if writer is None:
                out_path.parent.mkdir(parents=True, exist_ok=True)
                writer = pq.ParquetWriter(out_path, table.schema)
            writer.write_table(table)
            total += table.num_rows
    if writer is not None:
        writer.close()
    return total


def _cleanup_chunks(chunk_dir: Path) -> None:
    if chunk_dir.is_dir():
        shutil.rmtree(chunk_dir, ignore_errors=True)


def _write_arrow_batches_chunked(
    batches: Any,
    out_path: Path,
    normalize_fn: Callable[[pd.DataFrame], pd.DataFrame],
    job_id: str,
    resume_after_batch: int,
    on_batch: Callable[[int, int, float], None] | None = None,
    on_checkpoint: Callable[[int, int], None] | None = None,
    reporter: StepProgressBar | None = None,
    step_id: str = "",
) -> int:
    """Write each stream batch to chunk parquet; merge when complete."""
    chunk_dir = _chunks_dir(out_path)
    chunk_dir.mkdir(parents=True, exist_ok=True)
    stale_tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    if stale_tmp.exists():
        stale_tmp.unlink()

    progress = _load_chunk_progress(chunk_dir)
    total_rows = int(progress.get("rows") or 0) if resume_after_batch > 0 else 0

    stream_idx = 0
    try:
        for batch in batches:
            stream_idx += 1
            if stream_idx <= resume_after_batch:
                if (
                    reporter is not None
                    and step_id
                    and (stream_idx == 1 or stream_idx % 50 == 0 or stream_idx == resume_after_batch)
                ):
                    reporter.log(
                        f"{step_id}: skipping stream batch {stream_idx}/{resume_after_batch} "
                        f"(chunk on disk)"
                    )
                continue

            df = batch.to_pandas()
            if df.empty:
                continue
            df = normalize_fn(df)
            if df.empty:
                continue

            chunk_path = _chunk_file(chunk_dir, stream_idx)
            chunk_tmp = chunk_path.with_suffix(chunk_path.suffix + ".tmp")
            df.to_parquet(chunk_tmp, index=False)
            atomic_replace(chunk_tmp, chunk_path)
            total_rows += len(df)

            if on_checkpoint is not None:
                on_checkpoint(stream_idx, total_rows)
            _save_chunk_progress(chunk_dir, job_id=job_id, batches=stream_idx, rows=total_rows)

            if on_batch is not None:
                on_batch(stream_idx, total_rows, _chunks_total_bytes(chunk_dir))

        if stream_idx <= resume_after_batch and resume_after_batch > 0:
            # Iterator ended before new data; still merge existing chunks
            pass
    except KeyboardInterrupt:
        for tmp in chunk_dir.glob("batch_*.parquet.tmp"):
            tmp.unlink(missing_ok=True)
        completed = _max_contiguous_chunks(chunk_dir)
        saved_rows = int(_load_chunk_progress(chunk_dir).get("rows") or 0)
        if completed > 0 and completed == stream_idx:
            saved_rows = total_rows
        if completed > 0:
            _save_chunk_progress(
                chunk_dir,
                job_id=job_id,
                batches=completed,
                rows=saved_rows,
            )
            if on_checkpoint is not None:
                on_checkpoint(completed, saved_rows)
        raise
    except Exception:
        if stream_idx > resume_after_batch:
            _save_chunk_progress(
                chunk_dir,
                job_id=job_id,
                batches=stream_idx,
                rows=total_rows,
            )
        raise

    chunk_files = sorted(chunk_dir.glob("batch_*.parquet"))
    if not chunk_files:
        return 0

    if reporter is not None and step_id:
        reporter.log(f"{step_id}: merging {len(chunk_files)} chunks -> {out_path.name}")

    rows = merge_parquet_paths(chunk_files, out_path)
    _cleanup_chunks(chunk_dir)
    return rows


def write_dataframe_parquet_atomic(df: pd.DataFrame, out_path: Path) -> None:
    tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")
    tmp_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(tmp_path, index=False)
    atomic_replace(tmp_path, out_path)


def _make_bqstorage_client(client: bigquery.Client):
    """BigQuery Storage read client for faster downloads (optional)."""
    try:
        from google.cloud import bigquery_storage

        return bigquery_storage.BigQueryReadClient(
            credentials=client._credentials,
            project=client.project,
        )
    except Exception:
        return None


def _wait_for_job(
    job: bigquery.QueryJob,
    step_id: str,
    reporter: StepProgressBar | None,
    poll_sec: int = 10,
):
    """Poll BQ job with heartbeat logs until complete, then return RowIterator."""
    start = time.monotonic()
    last_log = 0.0
    while not job.done():
        try:
            job.reload()
        except Exception:
            pass
        elapsed = int(time.monotonic() - start)
        if reporter is not None:
            reporter.update_live(step_id, phase=f"BQ {job.state} {elapsed}s")
            if time.monotonic() - last_log >= poll_sec:
                reporter.log(f"{step_id}: BQ {job.state} ... {elapsed}s")
                last_log = time.monotonic()
        time.sleep(1)
    return job.result()


def _download_result_to_parquet(
    job: bigquery.QueryJob,
    client: bigquery.Client,
    out_path: Path,
    normalize_fn: Callable[[pd.DataFrame], pd.DataFrame],
    step_id: str,
    use_storage: bool,
    checkpoint: dict[str, Any],
    on_checkpoint: Callable[[int, int], None] | None = None,
    reporter: StepProgressBar | None = None,
) -> int:
    """Download query results via RowIterator (chunked) with REST fallback."""
    chunk_dir = _chunks_dir(out_path)
    resume_after = _max_contiguous_chunks(chunk_dir)
    progress = _load_chunk_progress(chunk_dir)
    total_rows_resume = int(progress.get("rows") or 0)

    rows_iter = _wait_for_job(job, step_id, reporter)
    row_total = getattr(rows_iter, "total_rows", None)
    if reporter is not None:
        reporter.begin_download()
        if resume_after > 0:
            reporter.log(
                f"{step_id}: resuming download from batch {resume_after} "
                f"({total_rows_resume:,} rows, {_chunks_total_bytes(chunk_dir):.1f} MB on disk)"
            )
        elif row_total:
            reporter.log(f"{step_id}: download started ({row_total:,} rows expected)")
        else:
            reporter.log(f"{step_id}: download started")

    bqstorage = _make_bqstorage_client(client) if use_storage else None

    def on_batch(batch_num: int, total_rows: int, chunks_mb: float) -> None:
        if reporter is None:
            return
        rate = reporter.rows_per_sec(total_rows)
        reporter.update_live(
            step_id,
            rows=total_rows,
            row_total=row_total,
            batches=batch_num,
            tmp_mb=chunks_mb,
            phase="downloading",
        )
        reporter.log(
            f"{step_id}: batch {batch_num} | rows {total_rows:,} | "
            f"chunks {chunks_mb:.1f} MB | {rate:,.0f} rows/s"
        )

    try:
        raw_batches = rows_iter.to_arrow_iterable(
            bqstorage_client=bqstorage,
            timeout=BQ_DOWNLOAD_TIMEOUT_SEC,
        )
        return _write_arrow_batches_chunked(
            raw_batches,
            out_path,
            normalize_fn,
            job_id=job.job_id,
            resume_after_batch=resume_after,
            on_batch=on_batch,
            on_checkpoint=on_checkpoint,
            reporter=reporter,
            step_id=step_id,
        )
    except Exception as arrow_exc:
        if resume_after > 0:
            msg = (
                f"{step_id}: arrow download failed ({arrow_exc}); "
                f"{resume_after} chunks preserved — re-run --resume to continue"
            )
            if reporter is not None:
                reporter.log(msg)
            raise RuntimeError(msg) from arrow_exc
        msg = f"{step_id}: arrow download failed ({arrow_exc}); trying to_dataframe..."
        if reporter is not None:
            reporter.log(msg)
        else:
            tqdm.write(msg)
        df = job.to_dataframe(
            progress_bar_type="tqdm",
            create_bqstorage_client=use_storage,
            timeout=BQ_DOWNLOAD_TIMEOUT_SEC,
        )
        df = normalize_fn(df)
        write_dataframe_parquet_atomic(df, out_path)
        _cleanup_chunks(chunk_dir)
        return len(df)


def try_get_existing_job(
    client: bigquery.Client,
    job_id: str | None,
) -> bigquery.QueryJob | None:
    if not job_id:
        return None
    try:
        job = client.get_job(job_id)
        state = job.state
        if state in ("DONE", "RUNNING", "PENDING"):
            return job
    except Exception:
        return None
    return None


def run_or_resume_query_job(
    client: bigquery.Client,
    sql: str,
    params: list,
    checkpoint: dict[str, Any],
    step_id: str,
    out_path: Path | None = None,
) -> tuple[bigquery.QueryJob, bool]:
    """Return (job, reused). Reuses job_id from checkpoint or chunk progress."""
    saved_id = _saved_job_id(checkpoint, step_id, out_path) if out_path else None
    if saved_id:
        job = try_get_existing_job(client, saved_id)
        if job is not None:
            upsert_step_record(
                checkpoint,
                step_id,
                status="in_progress",
                job_id=job.job_id,
            )
            return job, True
    rec = find_step_record(checkpoint, step_id)
    if rec and rec.get("status") == "in_progress":
        job = try_get_existing_job(client, rec.get("job_id"))
        if job is not None:
            return job, True
    job_config = QueryJobConfig(use_query_cache=False, query_parameters=params)
    job = client.query(sql, job_config=job_config)
    upsert_step_record(
        checkpoint,
        step_id,
        status="in_progress",
        job_id=job.job_id,
        started_at=utc_now_iso(),
    )
    return job, False


def download_query_to_parquet(
    client: bigquery.Client,
    sql: str,
    params: list,
    out_path: Path,
    normalize_fn: Callable[[pd.DataFrame], pd.DataFrame],
    checkpoint: dict[str, Any],
    step_id: str,
    bytes_scanned: int = 0,
    max_retries: int = 4,
    reporter: StepProgressBar | None = None,
    manifest_path: Path | None = None,
    manifest_key: str | None = None,
    manifest: dict[str, Any] | None = None,
    block: dict[str, Any] | None = None,
) -> int:
    """Run/resume BQ query, download with live progress, write parquet atomically."""
    job, reused = run_or_resume_query_job(
        client, sql, params, checkpoint, step_id, out_path=out_path
    )

    def emit(msg: str) -> None:
        if reporter is not None:
            reporter.log(msg)
        else:
            tqdm.write(msg)

    def flush_progress(batches: int, rows: int) -> None:
        upsert_step_record(
            checkpoint,
            step_id,
            status="in_progress",
            job_id=job.job_id,
            batches=batches,
            rows=rows,
            error=None,
        )
        if manifest_path and manifest_key and manifest is not None:
            save_checkpoint(manifest_path, manifest_key, manifest, block)

    if reused:
        emit(f"{step_id}: reusing BQ job {job.job_id} (no re-scan)")
    else:
        resume_batches = _max_contiguous_chunks(_chunks_dir(out_path))
        if resume_batches > 0:
            emit(
                f"{step_id}: WARNING new BQ job (chunks 1..{resume_batches} kept); "
                "stream will fast-skip until new batch"
            )
        emit(f"{step_id}: submitted BQ job {job.job_id}")

    last_exc: Exception | None = None
    for attempt in range(max_retries):
        use_storage = attempt < max_retries - 1
        try:
            emit(
                f"{step_id}: downloading "
                f"(storage={use_storage}, attempt={attempt + 1})..."
            )
            rows = _download_result_to_parquet(
                job,
                client,
                out_path,
                normalize_fn,
                step_id,
                use_storage,
                checkpoint,
                on_checkpoint=flush_progress,
                reporter=reporter,
            )
            upsert_step_record(
                checkpoint,
                step_id,
                status="completed",
                job_id=job.job_id,
                rows=rows,
                bytes_scanned=bytes_scanned,
                finished_at=utc_now_iso(),
                error=None,
            )
            flush_progress(0, rows)
            emit(f"{step_id}: {rows:,} rows -> {out_path.name}")
            return rows
        except KeyboardInterrupt:
            flush_progress(
                _max_contiguous_chunks(_chunks_dir(out_path)),
                int(_load_chunk_progress(_chunks_dir(out_path)).get("rows") or 0),
            )
            raise
        except Exception as exc:
            last_exc = exc
            emit(f"{step_id}: download failed: {exc}")
            upsert_step_record(
                checkpoint,
                step_id,
                status="in_progress",
                job_id=job.job_id,
                batches=_max_contiguous_chunks(_chunks_dir(out_path)),
                rows=_load_chunk_progress(_chunks_dir(out_path)).get("rows"),
                error=str(exc),
            )
            flush_progress(
                _max_contiguous_chunks(_chunks_dir(out_path)),
                int(_load_chunk_progress(_chunks_dir(out_path)).get("rows") or 0),
            )
            if attempt + 1 < max_retries:
                time.sleep(30 * (attempt + 1))
    upsert_step_record(
        checkpoint,
        step_id,
        status="failed",
        job_id=job.job_id,
        error=str(last_exc) if last_exc else "unknown",
        finished_at=utc_now_iso(),
    )
    if manifest_path and manifest_key and manifest is not None:
        save_checkpoint(manifest_path, manifest_key, manifest, block)
    if last_exc is not None:
        raise last_exc
    return 0


def should_skip_dry_run(
    manifest: dict[str, Any],
    wallet_count: int,
    force_dry_run: bool,
    skip_dry_run_flag: bool,
    resume: bool,
    extract: bool = False,
) -> bool:
    if force_dry_run:
        return False
    if skip_dry_run_flag:
        return True
    if not resume and not extract:
        return False
    rep = manifest.get("reputation_extract") or {}
    return (
        rep.get("wallet_count") == wallet_count
        and rep.get("dry_run_bytes_total") is not None
        and bool(rep.get("months"))
    )
