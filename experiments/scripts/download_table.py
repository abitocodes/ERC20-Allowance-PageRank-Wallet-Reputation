#!/usr/bin/env python3
"""Download a project BigQuery table into parquet parts below GitHub's size limit.

The BigQuery Storage Read API streams the table; no query is run, so nothing is
billed as scanned bytes. Each part is a separate parquet file
(<stem>.part000.parquet, ...), and <stem>.json records the table, the row count
and the parts.

Usage:
    python scripts/download_table.py contract_rep.spender_candidates data/.../spender_candidates
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from google.cloud import bigquery
from google.cloud import bigquery_storage

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import PartWriter, load_config, part_paths, save_json  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("table", help="dataset.table in the project")
    ap.add_argument("stem")
    args = ap.parse_args()

    cfg = load_config()
    project = cfg["bigquery"]["project_id"]
    client = bigquery.Client(project=project)
    ref = client.get_table(f"{project}.{args.table}")
    bqs = bigquery_storage.BigQueryReadClient()
    rows = client.list_rows(ref)
    stream = rows.to_arrow_iterable(bqstorage_client=bqs)
    writer = None
    for batch in stream:
        if writer is None:
            writer = PartWriter(Path(args.stem), batch.schema)
        writer.write(batch)
        if writer.rows and writer.rows % 5_000_000 < batch.num_rows:
            print(f"{writer.rows:,} rows", flush=True)
    if writer is None:
        print("empty table")
        return 1
    n = writer.close()
    stem = Path(args.stem)
    save_json({
        "table": f"{project}.{args.table}",
        "rows": n,
        "table_rows": int(ref.num_rows or 0),
        "downloaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "parts": [p.name for p in part_paths(stem)],
        "bytes": sum(p.stat().st_size for p in part_paths(stem)),
    }, stem.parent / f"{stem.name}.json")
    print(f"{n:,} rows in {len(part_paths(stem))} parts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
