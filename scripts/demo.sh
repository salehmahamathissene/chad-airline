#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_DIR="out_demo/${RUN_ID}"

python3 -m venv .venv || true
source .venv/bin/activate

pip install -U pip
pip install -r requirements.txt

PYTHONPATH=. python simulations/run_full_pipeline.py \
  --out "${OUT_DIR}" \
  --run-id "${RUN_ID}" \
  --flights 10 \
  --tickets-per-flight 5

echo
echo "✅ Demo finished."
echo "Run folder: ${OUT_DIR}"
echo "PDF: ${OUT_DIR}/reports/EXECUTIVE_REPORT.pdf"
echo "Images: ${OUT_DIR}/dashboard/images/"
