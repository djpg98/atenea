#!/usr/bin/env bash
# Regenerates the Bruno collection under bruno/ from the current DRF urlconf.
#
# Pipeline: drf-spectacular (OpenAPI schema) -> bru CLI (OpenAPI -> Bruno .bru)
# -> fix_bruno_urls.py (splits {{baseUrl}}/api/<version>/ into {{url}}/{{version}}/
# to match the vars already defined in the Bruno environment).
set -euo pipefail

API_VERSION="${1:-v1}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$REPO_ROOT/backend"
OUTPUT_DIR="$REPO_ROOT/bruno"
SCHEMA_FILE="$(mktemp -t atenea-openapi-schema).json"

cd "$BACKEND_DIR"
uv run python manage.py spectacular --file "$SCHEMA_FILE" --format openapi-json

rm -rf "$OUTPUT_DIR"
npx --yes @usebruno/cli import openapi \
  --source "$SCHEMA_FILE" \
  --output "$OUTPUT_DIR" \
  --collection-name "Atenea" \
  --collection-format bru

python3 "$REPO_ROOT/scripts/fix_bruno_urls.py" "$OUTPUT_DIR" --api-version "$API_VERSION"

rm -f "$SCHEMA_FILE"

echo "Bruno collection generated at $OUTPUT_DIR"
