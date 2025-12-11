#!/usr/bin/env bash
set -euo pipefail

HOST="${1:-db-api}"
PORT="${2:-8787}"

echo "Waiting for Database API Worker at ${HOST}:${PORT}..."
for i in {1..60}; do
  if /bin/bash -c "</dev/tcp/${HOST}/${PORT}" 2>/dev/null; then
    echo "Database API Worker TCP port is open."
    
    # Additional check: verify the health endpoint responds
    sleep 2
    if curl -f http://${HOST}:${PORT}/health &>/dev/null; then
      echo "Database API Worker is healthy and ready."
      exit 0
    fi
  fi
  sleep 2
done

echo "ERROR: Database API Worker did not become ready in time." >&2
exit 1
