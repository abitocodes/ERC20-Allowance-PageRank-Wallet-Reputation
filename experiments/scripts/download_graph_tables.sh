#!/usr/bin/env bash
# Download the tables the local evaluation reads into data/1-raw-blockchain-extracts/graph-tables/
# (parquet parts below 90 MB). Run from experiments/ after sql/04-08 have run.
set -euo pipefail
OUT=data/1-raw-blockchain-extracts/graph-tables
bq query --use_legacy_sql=false --quiet \
  "CREATE OR REPLACE TABLE \`dissertation-bq.contract_rep.x_nodes\` AS SELECT id, address, is_cohort FROM \`dissertation-bq.contract_rep.nodes\`" >/dev/null
python scripts/download_table.py contract_rep.x_nodes $OUT/nodes
for t in tobs t1; do
  python scripts/download_table.py contract_rep.x_allow_pairs_$t $OUT/allow_pairs_$t
  python scripts/download_table.py contract_rep.x_transfer_pairs_$t $OUT/transfer_pairs_$t
done
python scripts/download_table.py contract_rep.proxies_tobs $OUT/proxies_tobs
python scripts/download_table.py contract_rep.labels_w0 $OUT/labels_w0
