#!/usr/bin/env bash
# Usage: scripts/smoke_test.sh <base-url> [expected-version]
# Retries /health for up to 60s, optionally checks the deployed version, then exercises the API.
set -euo pipefail
BASE_URL="${1:?base url required, e.g. http://localhost:5000}"
EXPECTED_VERSION="${2:-}"

for i in $(seq 1 30); do
  if curl -fsS "$BASE_URL/health" -o /tmp/health.json; then break; fi
  echo "waiting for $BASE_URL ($i/30)..."; sleep 2
  [ "$i" -eq 30 ] && { echo "service never became healthy"; exit 1; }
done
cat /tmp/health.json; echo

if [ -n "$EXPECTED_VERSION" ]; then
  grep -q "\"version\":\"$EXPECTED_VERSION\"" /tmp/health.json \
    || grep -q "\"version\": \"$EXPECTED_VERSION\"" /tmp/health.json \
    || { echo "expected version $EXPECTED_VERSION not deployed"; exit 1; }
fi

curl -fsS -X POST "$BASE_URL/tasks" -H 'Content-Type: application/json' -d '{"title":"smoke"}' >/dev/null
curl -fsS "$BASE_URL/metrics" | grep -q taskflow_http_requests_total
echo "SMOKE TEST PASSED for $BASE_URL"
