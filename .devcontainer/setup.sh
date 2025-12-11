#!/usr/bin/env bash
set -e

echo "🔧 Running post-create setup..."

# Wait for db-api to be ready
bash .devcontainer/wait-for-db-api.sh

# Install uv if not already available (backup in case Dockerfile install failed)
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Restore .NET packages
if [ -f "app.sln" ]; then
    echo "📦 Restoring .NET packages..."
    dotnet restore
fi

# Clean host node_modules and Python venv to prevent platform conflicts
echo "🧹 Cleaning host node_modules and Python venv..."
for dir in client workers; do
    if [ -d "$dir/node_modules" ]; then
        rm -rf "$dir/node_modules"
    fi
done

# Clean Python virtual environment if it exists
if [ -d "hpc_runner/.venv" ]; then
    rm -rf "hpc_runner/.venv"
fi

# Install client dependencies
if [ -d "client" ]; then
    echo "📦 Installing client dependencies..."
    (cd client && npm install)
fi

# Install workers dependencies
if [ -d "workers" ]; then
    echo "📦 Installing workers dependencies..."
    (cd workers && npm install)
fi

# Setup Python environment for HPC runner
if [ -d "hpc_runner" ]; then
    echo "📦 Setting up hpc_runner Python environment..."
    (cd hpc_runner && uv sync)
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
