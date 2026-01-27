#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 -m venv .venv || true
source .venv/bin/activate

pip install -U pip
pip install -r requirements.txt

# Run the full pipeline demo (your best showcase)
PYTHONPATH=. python simulations/run_full_pipeline.py

echo
echo "✅ Demo finished."
echo "Open: out_demo/demo_001/reports/EXECUTIVE_REPORT.pdf"
echo "And images: out_demo/demo_001/dashboard/images/"
