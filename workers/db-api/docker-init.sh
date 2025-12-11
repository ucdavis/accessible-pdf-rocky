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

WRANGLER_ENTRYPOINT="src/index.ts"
WRANGLER_PORT="8787"
# Wrangler must bind to all interfaces in Docker so other containers (and host port mapping) can reach it.
# Allow override via env var.
ZERO=0
WRANGLER_IP="${WRANGLER_IP:-${ZERO}.${ZERO}.${ZERO}.${ZERO}}"
WRANGLER_VAR_DB_AUTH_TOKEN="DB_AUTH_TOKEN:dev-token"
WRANGLER_PERSIST_DIR=".wrangler/state"

# Build wrangler args as positional parameters so we can safely pass them quoted.
set -- "$WRANGLER_ENTRYPOINT" \
	--port "$WRANGLER_PORT" \
	--ip "$WRANGLER_IP" \
	--var "$WRANGLER_VAR_DB_AUTH_TOKEN" \
	--persist-to "$WRANGLER_PERSIST_DIR"

# Check if schema has been applied marker exists
if [ ! -f ".wrangler/.schema_applied" ]; then
	echo "First run detected - will initialize database schema"

	# Start wrangler in background to let it create the database
	echo "Starting wrangler to create database structure..."
	npx wrangler dev "$@" &
	WRANGLER_PID=$!

	# Wait for wrangler to create the database
	echo "Waiting for database to be created..."
	sleep 10

	# Find all database files (handle missing directory safely)
	if [ -d ".wrangler/state/v3/d1/miniflare-D1DatabaseObject" ]; then
		DB_FILES=$(find .wrangler/state/v3/d1/miniflare-D1DatabaseObject \
			-name "*.sqlite" -not -name "*-shm" -not -name "*-wal")
	else
		DB_FILES=""
	fi

	if [ -n "$DB_FILES" ]; then
		echo "Found database files:"
		echo "$DB_FILES"
		echo "Applying schema..."

		# Stop wrangler temporarily
		kill $WRANGLER_PID || true
		wait $WRANGLER_PID 2>/dev/null || true
		sleep 2

		# Apply schema to all database files using Node.js
		echo "$DB_FILES" | while read -r DB_FILE; do
			if [ -f "$DB_FILE" ]; then
				echo "Applying schema to: $DB_FILE"
				node -e "
                const fs = require('fs');
                const Database = require('better-sqlite3');
                const db = new Database('$DB_FILE');
                const schema = fs.readFileSync('schema.sql', 'utf8');
                db.exec(schema);
                db.close();
                console.log('Schema applied to $DB_FILE');
                "
			fi
		done

		# Mark schema as applied
		touch .wrangler/.schema_applied
		echo "Database initialization complete!"
	else
		echo "Warning: Could not find database files"
	fi
fi

# Start wrangler dev server
echo "Starting wrangler dev server..."
exec npx wrangler dev "$@"
