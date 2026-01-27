#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Ensure docker image exists (optional: comment out if you don't want)
# docker build -t airline-edition .

RUN_ID="pitch_$(date -u +%Y%m%dT%H%M%SZ)"
OUT_HOST_DIR="$PWD/out_demo"
OUT_CONT_DIR="/app/out_demo"

echo "🆔 RUN_ID: $RUN_ID"

# Run pipeline inside container
docker run --rm -v "$OUT_HOST_DIR:$OUT_CONT_DIR" airline-edition \
  run --out "$OUT_CONT_DIR" --run-id "$RUN_ID" --flights 10 --tickets-per-flight 5 --strict

RUN_DIR="out_demo/$RUN_ID"
PDF="$RUN_DIR/reports/EXECUTIVE_REPORT.pdf"
IMAGES_DIR="$RUN_DIR/dashboard/images"
LOG="$RUN_DIR/pipeline.log"

# Hard validation (PRO)
test -s "$PDF" || { echo "❌ Missing/empty PDF: $PDF" >&2; exit 2; }
test -d "$IMAGES_DIR" || { echo "❌ Missing images dir: $IMAGES_DIR" >&2; exit 2; }

# Fresh pack
rm -rf pitch_pack
mkdir -p pitch_pack/images pitch_pack/docs

# Core artifacts
cp -f "$PDF" pitch_pack/
cp -r "$IMAGES_DIR/"* pitch_pack/images/

# Optional artifacts (never fail pack if missing)
cp -f "$LOG" pitch_pack/ 2>/dev/null || true
cp -f "$RUN_DIR/RUN_METADATA.txt" pitch_pack/ 2>/dev/null || true
cp -f README.md pitch_pack/ 2>/dev/null || true
cp -rf docs/* pitch_pack/docs/ 2>/dev/null || true

# Manifest + checksums (MUST be created BEFORE zipping)
(
  cd pitch_pack
  # deterministic file order
  find . -type f -print0 | sort -z | xargs -0 ls -lh
) > pitch_pack/MANIFEST.txt

(
  cd pitch_pack
  find . -type f -print0 | sort -z | xargs -0 sha256sum
) > pitch_pack/SHA256SUMS.txt

# Build zip AFTER everything exists
ZIP="airline-edition-$RUN_ID-pitch.zip"
rm -f "$ZIP"
zip -r "$ZIP" pitch_pack >/dev/null

# Stable "latest" alias
cp -f "$ZIP" airline-edition-latest-pitch.zip

echo "✅ READY: $ZIP"
echo "✅ ALSO READY: airline-edition-latest-pitch.zip"

# Quick proof (print file list)
unzip -l "$ZIP" | sed -n '1,200p'
