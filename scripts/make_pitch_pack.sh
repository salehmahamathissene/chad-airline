#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

RUN_ID="pitch_$(date -u +%Y%m%dT%H%M%SZ)"

docker run --rm -v "$PWD/out_demo:/app/out_demo" airline-edition \
  run --out /app/out_demo --run-id "$RUN_ID" --flights 10 --tickets-per-flight 5 --strict

rm -rf pitch_pack
mkdir -p pitch_pack

cp -f "out_demo/$RUN_ID/reports/EXECUTIVE_REPORT.pdf" pitch_pack/
cp -r "out_demo/$RUN_ID/dashboard/images" pitch_pack/images
cp -f "out_demo/$RUN_ID/pipeline.log" pitch_pack/ || true
cp -f README.md pitch_pack/ || true
cp -rf docs pitch_pack/ || true


ZIP="airline-edition-$RUN_ID-pitch.zip"
rm -f "$ZIP"
zip -r "$ZIP" pitch_pack >/dev/null

echo "✅ READY: $ZIP"
