#!/usr/bin/env bash
set -e

echo "🔧 Running post-create setup..."

# Wait for db-api to be ready
bash .devcontainer/wait-for-db-api.sh

# Install uv if not already available (backup in case Dockerfile install failed)
if ! command -v uv &>/dev/null; then
	echo "📦 Installing uv..."
	curl -LsSf https://astral.sh/uv/install.sh | sh
	export PATH="$HOME/.local/bin:$PATH"
fi

# Restore .NET packages
if [ -f "app.sln" ]; then
	echo "📦 Restoring .NET packages..."
	dotnet restore
fi

# Dependencies are installed into container-only volumes (see .devcontainer/docker-compose.yml)
# so we do not need to delete host folders.

# Install client dependencies
if [ -d "client" ]; then
	echo "📦 Installing client dependencies..."
	(cd client && npm ci)
fi

# Install workers dependencies
if [ -d "workers" ]; then
	echo "📦 Installing workers dependencies..."
	(cd workers && npm ci)

fi

# Setup Python environment for HPC runner
if [ -d "hpc_runner" ]; then
	echo "📦 Setting up hpc_runner Python environment..."
	(
		cd hpc_runner
		uv python install
		uv sync
	)
fi

echo "✅ Dev container setup complete."
echo ""
echo "Available commands:"
echo "  just dev           - Start all services"
echo "  just dev-server    - Start only server"
echo "  just dev-client    - Start only client"
echo "  just test          - Run all tests"
echo "  just lint          - Run all linters"
echo "  just help          - Show all available commands"
