#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Build once (fast if cached)
docker build -t airline-edition .

RUN_ID="demo_$(date -u +%Y%m%dT%H%M%SZ)"

mkdir -p out_demo

docker run --rm \
  -v "$PWD/out_demo:/app/out_demo" \
  airline-edition \
  run --out /app/out_demo --run-id "$RUN_ID" --flights 10 --tickets-per-flight 5 --strict

echo
echo "✅ Demo finished."
echo "Run folder: out_demo/${RUN_ID}"
echo "PDF: out_demo/${RUN_ID}/reports/EXECUTIVE_REPORT.pdf"
echo "Images: out_demo/${RUN_ID}/dashboard/images/"
echo "Log: out_demo/${RUN_ID}/pipeline.log"
