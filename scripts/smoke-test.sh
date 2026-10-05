#!/usr/bin/env sh
set -eu

API_URL="${API_URL:-http://localhost:8000}"
WEB_URL="${WEB_URL:-http://localhost:8080}"

echo "Checking API liveness..."
curl --fail --silent "${API_URL}/health"
echo

echo "Checking API readiness..."
curl --fail --silent "${API_URL}/ready"
echo

echo "Checking web application..."
curl --fail --silent --output /dev/null "${WEB_URL}/"

echo "Smoke test passed."
