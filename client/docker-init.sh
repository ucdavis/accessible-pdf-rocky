#!/bin/sh
set -e

# Install dependencies
if [ ! -d "node_modules" ]; then
	echo "Installing dependencies..."
	npm install
else
	echo "Checking dependencies..."
	npm install --no-save
fi

# Start Vite dev server
# Run Vite directly so a Docker stop/Ctrl+C doesn't show up as an npm "error".
echo "Starting Vite dev server..."

VITE_HOST="${VITE_HOST:-0.0.0.0}"

terminated=0
child_pid=""

trap '
	terminated=1
	echo "Stopping Vite..."
	if [ -n "$child_pid" ] && kill -0 "$child_pid" 2>/dev/null; then
		kill -TERM "$child_pid" 2>/dev/null || true
	fi
' INT TERM

./node_modules/.bin/vite --host "$VITE_HOST" &
child_pid=$!

set +e
wait "$child_pid"
exit_code=$?
set -e

# If we were asked to stop (Docker/Compose sends SIGTERM), exit cleanly.
if [ "$terminated" -eq 1 ]; then
	exit 0
fi

exit "$exit_code"
