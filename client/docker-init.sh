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
echo "Starting Vite dev server..."
exec npm run dev -- --host 0.0.0.0
