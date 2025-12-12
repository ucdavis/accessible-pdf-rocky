# shellcheck disable=SC2148
# Justfile for accessible-pdf-rocky development workflow
# Install just: https://github.com/casey/just
# Usage: just <command> or just --list

# Use bash with strict error handling for all recipes
set shell := ["bash", "-euo", "pipefail", "-c"]

# Default recipe shows available commands
default:
    @just --list

# Internal helper: ensure npm is installed
_ensure-npm:
    #!/usr/bin/env bash
    set -euo pipefail
    command -v npm >/dev/null || { echo "❌ 'npm' not found. Install Node.js from https://nodejs.org"; exit 1; }

# Internal helper: ensure uv is installed
_ensure-uv:
    #!/usr/bin/env bash
    set -euo pipefail
    command -v uv >/dev/null || { echo "❌ 'uv' not found. See 'just setup' or https://github.com/astral-sh/uv"; exit 1; }

# Internal helper: ensure dotnet is installed
_ensure-dotnet:
    #!/usr/bin/env bash
    set -euo pipefail
    command -v dotnet >/dev/null || { echo "❌ 'dotnet' not found. Install from https://dotnet.microsoft.com/download"; exit 1; }
    # Check for .NET 8 or higher
    version=$(dotnet --version | cut -d. -f1)
    if [ "$version" -lt 8 ]; then
        echo "⚠️  .NET 8+ required but $(dotnet --version) found"
        echo "   Install .NET 8 or later from https://dotnet.microsoft.com/download"
        exit 1
    fi

# GitHub Actions workflow validation
action-lint:
    #!/usr/bin/env bash
    set -euo pipefail
    if ! command -v actionlint >/dev/null; then
        echo "⚠️ 'actionlint' not found, skipping workflow validation"
        echo "   Install: brew install actionlint"
        exit 0
    fi
    files=()
    while IFS= read -r -d '' file; do
        files+=("$file")
    done < <(git ls-files -z '.github/workflows/*.yml' '.github/workflows/*.yaml')
    if [ "${#files[@]}" -gt 0 ]; then
        printf '%s\0' "${files[@]}" | xargs -0 actionlint
    else
        echo "No workflow files found to lint."
    fi

# Security audit: check for vulnerabilities in dependencies
audit: _ensure-npm _ensure-uv
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Running security audits..."
    echo ""
    
    # NPM audit for client and workers
    if [ -d "client" ]; then
        echo "Auditing client npm packages..."
        (
            cd client
            npm audit --audit-level=moderate || true
        )
        echo ""
    fi
    if [ -d "workers" ]; then
        echo "Auditing workers npm packages..."
        (
            cd workers
            npm audit --audit-level=moderate || true
        )
        echo ""
    fi
    
    # Python pip-audit for hpc_runner
    if [ -d "hpc_runner" ]; then
        echo "Auditing hpc_runner Python packages..."
        (
            cd hpc_runner
            # Install pip-audit once if not already available
            if ! uv run pip-audit --version >/dev/null 2>&1; then
                uv pip install --quiet pip-audit
            fi
            uv run pip-audit || true
        )
        echo ""
    fi
    
    echo "✅ Security audit complete!"

# Update JS/Python dependencies and update .NET NuGet packages
update: _ensure-npm _ensure-uv _ensure-dotnet
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Updating JS/Python dependencies and updating NuGet packages..."
    echo ""
    
    # Update NuGet package references (and restore)
    if [ -f "app.sln" ]; then
        echo "Updating NuGet packages..."
        # Add .NET global tools to PATH (needed for dotnet-outdated-tool)
        export PATH="$PATH:$HOME/.dotnet/tools"
        # Install dotnet-outdated-tool if missing
        if ! command -v dotnet-outdated >/dev/null; then
            echo "Installing dotnet-outdated-tool..."
            dotnet tool install -g dotnet-outdated-tool
        fi
        # Upgrade package versions in-place
        dotnet outdated app.sln -u
        echo ""
        echo "Restoring .NET packages..."
        dotnet restore app.sln
        echo ""
    fi
    
    # Update npm packages for client
    if [ -d "client" ]; then
        echo "Updating client npm packages..."
        (
            cd client
            npm update
        )
        echo ""
    fi
    
    # Update npm packages for workers
    # Note: db-api and metrics-ingest are separate npm packages with their own lockfiles.
    if [ -d "workers" ]; then
        echo "Updating workers npm packages..."
        (
            cd workers
            npm update

            for dir in db-api metrics-ingest; do
                if [ -f "$dir/package.json" ]; then
                    echo "Updating workers/$dir npm packages..."
                    (cd "$dir" && npm update)
                fi
            done
        )
        echo ""
    fi
    
    # Update Python packages for hpc_runner
    if [ -d "hpc_runner" ]; then
        echo "Updating hpc_runner Python packages..."
        (
            cd hpc_runner
            uv lock --upgrade
            uv sync
        )
        echo ""
    fi
    
    echo "✅ Dependencies updated (JS/Python + NuGet)."

# Build all projects
build: _ensure-npm _ensure-dotnet
    #!/usr/bin/env bash
    set -euo pipefail
    # Build .NET solution
    if [ -f "app.sln" ]; then
        echo "Building .NET solution..."
        dotnet build app.sln
    fi
    # Build React client
    if [ -d "client" ]; then
        echo "Building client..."
        (
            cd client
            npm run build
        )
    fi
    # Build workers
    if [ -d "workers" ]; then
        echo "Building workers..."
        (
            cd workers
            npm run build
        )
    fi

# CI simulation: quality checks with comprehensive testing (fast, matches GitHub Actions)
ci: lint test
    @echo "🎯 CI simulation complete!"

# Clean build artifacts
clean:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Cleaning build artifacts..."
    # .NET artifacts (scoped to known project directories)
    for dir in server server.core tests/server.tests; do
        if [ -d "$dir" ]; then
            find "$dir" -type d \( -name "bin" -o -name "obj" \) -prune -exec rm -rf {} + 2>/dev/null || true
        fi
    done
    # Node modules and build artifacts
    [ -d "client/node_modules" ] && rm -rf client/node_modules
    [ -d "client/dist" ] && rm -rf client/dist
    [ -d "workers/node_modules" ] && rm -rf workers/node_modules
    [ -d "workers/dist" ] && rm -rf workers/dist
    # Python artifacts
    [ -d "hpc_runner/.venv" ] && rm -rf hpc_runner/.venv
    find hpc_runner -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    echo "✅ Clean complete!"

# Pre-commit workflow: comprehensive validation with coverage before committing
# Runs: linting + all tests with coverage reports
commit-check: lint test-coverage
    @echo "🚀 Ready to commit! All checks passed!"

# Start all services with Docker Compose (attached)
dev:
    docker compose up --build

# Start only server (local)
dev-server: _ensure-dotnet
    dotnet watch --project server/server.csproj

# Stop all Docker services
dev-down:
    docker compose down

# Start only client (local)
dev-client: _ensure-npm
    cd client && npm run dev

# View Docker logs
dev-logs:
    docker compose logs -f

# Restart a specific service
dev-restart service:
    docker compose restart {{service}}

# Start all services with Docker Compose (detached)
dev-up:
    docker compose up --build -d

# Start only workers (local)
dev-workers: _ensure-npm
    cd workers && npm run dev

# Show help with common workflows
help:
    @echo "Common Just workflows:"
    @echo "  just setup         # Setup all development environments"
    @echo "  just ci            # CI simulation (linting + tests, fast)"
    @echo "  just commit-check  # Pre-commit check (linting + tests + coverage)"
    @echo ""
    @echo "Quality Check Groups:"
    @echo "  just lint          # All linting (code + docs + config)"
    @echo "  just lint-code     # Code linting (.NET, Python, JavaScript, TypeScript, Shell)"
    @echo "  just lint-docs     # Documentation linting (Markdown, Spelling)"
    @echo "  just lint-config   # Configuration validation (JSON, YAML, Actions)"
    @echo "  just typecheck     # Type checking (TypeScript)"
    @echo ""
    @echo "Security:"
    @echo "  just audit         # Check for vulnerabilities in dependencies"
    @echo "  just update        # Update all dependencies to latest versions"
    @echo ""
    @echo "Testing:"
    @echo "  just test          # Run all tests"
    @echo "  just test-coverage # Run all tests with coverage reports"
    @echo "  just test-dotnet   # .NET tests only"
    @echo "  just test-python   # Python tests only"
    @echo "  just test-js       # JavaScript tests only"
    @echo ""
    @echo "Development:"
    @echo "  just dev           # Start all services with Docker Compose"
    @echo "  just dev-up        # Start all services (detached)"
    @echo "  just dev-down      # Stop all services"
    @echo "  just dev-logs      # View logs"
    @echo "  just dev-client    # Start only client (local)"
    @echo "  just dev-server    # Start only server (local)"
    @echo "  just dev-workers   # Start only workers (local)"

# .NET linting
dotnet-lint: _ensure-dotnet
    #!/usr/bin/env bash
    set -euo pipefail
    if [ ! -f "app.sln" ]; then
        echo "❌ app.sln not found; expected for .NET linting" >&2
        exit 1
    fi
    echo "Linting .NET projects..."
    dotnet build app.sln /p:TreatWarningsAsErrors=true

# JavaScript/TypeScript linting
js-lint: _ensure-npm
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -d "client" ]; then
        echo "Linting client..."
        (
            cd client
            npm run lint
        )
    fi
    if [ -d "workers" ]; then
        echo "Linting workers..."
        (
            cd workers
            npm run lint
        )
    fi

# All linting: code + documentation + configuration
lint: lint-code lint-docs lint-config

# Code linting + type checking: .NET + Python + JavaScript + TypeScript + Shell
lint-code: dotnet-lint python-lint js-lint typecheck shell-lint

# Configuration validation: JSON, YAML, GitHub Actions workflows
lint-config: validate-json validate-yaml action-lint

# Documentation linting: Markdown + spell checking
lint-docs: markdown-lint spell-check

# Markdown linting
markdown-lint: _ensure-npm
    #!/usr/bin/env bash
    set -euo pipefail
    files=()
    while IFS= read -r -d '' file; do
        files+=("$file")
    done < <(git ls-files -z '*.md')
    if [ "${#files[@]}" -gt 0 ]; then
        printf '%s\0' "${files[@]}" | xargs -0 -n100 npx markdownlint --config .markdownlint.json --fix
    else
        echo "No markdown files found to lint."
    fi

# Python code quality
python-lint: _ensure-uv
    #!/usr/bin/env bash
    set -euo pipefail
    # Only lint hpc_runner (Python still used for HPC processing)
    if [ -d "hpc_runner" ]; then
        echo "Linting hpc_runner..."
        (
            cd hpc_runner
            uv run ruff check . --fix
            uv run ruff format .
            uv run mypy .
        )
    fi

# Shell script linting
shell-lint:
    #!/usr/bin/env bash
    set -euo pipefail
    files=()
    while IFS= read -r -d '' file; do
        files+=("$file")
    done < <(git ls-files -z '*.sh')
    if [ "${#files[@]}" -gt 0 ]; then
        # Format with shfmt if available
        if command -v shfmt &> /dev/null; then
            printf '%s\0' "${files[@]}" | xargs -0 -n1 shfmt -w
        else
            echo "⚠️ shfmt not found, skipping shell formatting (install: brew install shfmt)"
        fi
        # Lint with shellcheck if available
        if command -v shellcheck &> /dev/null; then
            printf '%s\0' "${files[@]}" | xargs -0 -n4 shellcheck -x
        else
            echo "⚠️ shellcheck not found, skipping shell linting (install: brew install shellcheck)"
        fi
    else
        echo "No shell files found to lint."
    fi

# Development setup
setup:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Setting up accessible-pdf-rocky development environment..."
    echo ""
    
    # Check for required tools
    missing_required=0
    for tool in dotnet node npm docker shellcheck shfmt uv; do
        if command -v "$tool" &> /dev/null; then
            echo "  ✓ $tool installed"
        else
            echo "  ✗ $tool NOT installed"
            case "$tool" in
                dotnet)
                    missing_required=1
                    echo "    Install: https://dotnet.microsoft.com/download"
                    echo "    macOS: brew install dotnet"
                    ;;
                uv)
                    missing_required=1
                    echo "    Install: https://github.com/astral-sh/uv"
                    echo "    macOS: brew install uv"
                    echo "    Linux/WSL: curl -LsSf https://astral.sh/uv/install.sh | sh"
                    ;;
                node|npm)
                    missing_required=1
                    echo "    Install: https://nodejs.org"
                    ;;
                docker)
                    missing_required=1
                    echo "    Install: https://www.docker.com/get-started"
                    echo "    macOS: brew install --cask docker"
                    echo "    Linux: https://docs.docker.com/engine/install/"
                    ;;
                shellcheck|shfmt)
                    echo "    Install: brew install $tool"
                    ;;
            esac
        fi
    done
    
    if [ "$missing_required" -ne 0 ]; then
        echo ""
        echo "❌ One or more required tools are missing. Please install them before continuing."
        exit 1
    fi
    
    echo ""
    echo "Installing dependencies..."
    
    # .NET restore
    if [ -f "app.sln" ]; then
        echo "  Restoring .NET packages..."
        dotnet restore
    fi
    
    # HPC runner setup
    if [ -d "hpc_runner" ]; then
        echo "  Setting up hpc_runner..."
        (
            cd hpc_runner
            uv sync
        )
    fi
    
    # Client setup
    if [ -d "client" ]; then
        echo "  Setting up client..."
        (
            cd client
            npm install
        )
    fi
    
    # Workers setup
    if [ -d "workers" ]; then
        echo "  Setting up workers..."
        (
            cd workers
            npm install
        )
    fi
    
    echo ""
    echo "✅ Setup complete! Run 'just help' to see available commands."

# Shell script linting

# Spell checking
spell-check: _ensure-npm
    #!/usr/bin/env bash
    set -euo pipefail
    files=()
    # Use -z for NUL-delimited output to handle filenames with spaces
    while IFS= read -r -d '' status_line; do
        # Extract filename from git status --porcelain -z format
        # Skip deleted files (D in first two characters)
        if [[ "$status_line" =~ ^[^D]D[[:space:]](.*)$ ]] || [[ "$status_line" =~ ^D[^D][[:space:]](.*)$ ]]; then
            continue
        fi
        if [[ "$status_line" =~ ^..[[:space:]](.*)$ ]]; then
            filename="${BASH_REMATCH[1]}"
            # For renames (format: "old -> new"), take the new filename
            if [[ "$filename" == *" -> "* ]]; then
                filename="${filename#* -> }"
            fi
            files+=("$filename")
        fi
    done < <(git status --porcelain -z --ignored=no)
    if [ "${#files[@]}" -gt 0 ]; then
        printf '%s\0' "${files[@]}" | xargs -0 npx cspell lint --config cspell.json --no-progress --gitignore --cache --exclude cspell.json
    else
        echo "No modified files to spell-check."
    fi

# Run all tests
test: test-dotnet test-python test-js

# Run tests with coverage
test-coverage: test-dotnet-coverage test-python-coverage test-js-coverage

# .NET tests
test-dotnet: _ensure-dotnet
    #!/usr/bin/env bash
    set -euo pipefail
    if [ ! -f "app.sln" ]; then
        echo "❌ app.sln not found; expected for .NET tests" >&2
        exit 1
    fi
    echo "Testing .NET projects..."
    dotnet test app.sln

# .NET tests with coverage
test-dotnet-coverage: _ensure-dotnet
    #!/usr/bin/env bash
    set -euo pipefail
    if [ ! -f "app.sln" ]; then
        echo "❌ app.sln not found; expected for .NET tests" >&2
        exit 1
    fi
    echo "Testing .NET projects with coverage..."
    dotnet test app.sln --collect:"XPlat Code Coverage" --results-directory ./coverage
    echo ""
    # Add .NET tools to PATH
    export PATH="$PATH:$HOME/.dotnet/tools"
    # Install reportgenerator if not available
    if ! command -v reportgenerator &> /dev/null; then
        echo "Installing reportgenerator..."
        dotnet tool install -g dotnet-reportgenerator-globaltool || true
    fi
    # Generate text summary for terminal output
    if command -v reportgenerator &> /dev/null; then
        echo ""
        echo "Coverage Summary:"
        reportgenerator "-reports:./coverage/**/coverage.cobertura.xml" \
                        -targetdir:./coverage \
                        -reporttypes:TextSummary > /dev/null 2>&1
        cat ./coverage/Summary.txt
    else
        echo "Coverage report generated in ./coverage directory"
        echo "Install reportgenerator for terminal summary: dotnet tool install -g dotnet-reportgenerator-globaltool"
    fi

# JavaScript tests
test-js: _ensure-npm
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -d "client" ] && [ -f "client/package.json" ]; then
        echo "Testing client..."
        (
            cd client
            npm test
        )
    fi
    if [ -d "workers" ] && [ -f "workers/package.json" ]; then
        echo "Testing workers..."
        (
            cd workers
            npm test
        )
    fi

# JavaScript tests with coverage
test-js-coverage: _ensure-npm
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -d "client" ] && [ -f "client/package.json" ]; then
        echo "Testing client with coverage..."
        (
            cd client
            npm run test:coverage
        )
    fi
    if [ -d "workers" ] && [ -f "workers/package.json" ]; then
        echo "Testing workers with coverage..."
        (
            cd workers
            npm run test:coverage
        )
    fi

# Python tests
test-python: _ensure-uv
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -d "hpc_runner" ] && [ -f "hpc_runner/pyproject.toml" ]; then
        echo "Testing hpc_runner..."
        (
            cd hpc_runner
            uv run pytest
        )
    fi

# Python tests with coverage
test-python-coverage: _ensure-uv
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -d "hpc_runner" ] && [ -f "hpc_runner/pyproject.toml" ]; then
        echo "Testing hpc_runner with coverage..."
        (
            cd hpc_runner
            uv run pytest --cov=. --cov-report=html --cov-report=term
        )
    fi

# Type checking
typecheck: _ensure-npm
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -d "client" ]; then
        echo "Type checking client..."
        (
            cd client
            npx tsc --noEmit
        )
    fi
    if [ -d "workers" ]; then
        echo "Type checking workers..."
        (
            cd workers
            npx tsc --noEmit
        )
    fi

# Validate YAML files
validate-yaml: _ensure-uv
    #!/usr/bin/env bash
    set -euo pipefail
    if ! uv run yamllint --version >/dev/null 2>&1; then
        echo "⚠️ 'yamllint' not found in uv environment, skipping YAML validation"
        echo "   Install: uv tool install yamllint"
        exit 0
    fi
    files=()
    while IFS= read -r -d '' file; do
        files+=("$file")
    done < <(git ls-files -z '*.yml' '*.yaml')
    if [ "${#files[@]}" -gt 0 ]; then
        printf '%s\0' "${files[@]}" | xargs -0 uv run yamllint -c .yamllint.yml
    else
        echo "No YAML files found to validate."
    fi

# Validate JSON files
validate-json:
    #!/usr/bin/env bash
    set -euo pipefail
    files=()
    while IFS= read -r -d '' file; do
        # Skip tsconfig.json files (they use JSONC - JSON with Comments)
        if [[ ! "$file" =~ tsconfig\.json$ ]]; then
            files+=("$file")
        fi
    done < <(git ls-files -z '*.json')
    if [ "${#files[@]}" -gt 0 ]; then
        if command -v jq &> /dev/null; then
            printf '%s\0' "${files[@]}" | xargs -0 -n1 jq empty
        else
            echo "⚠️ 'jq' not found, skipping JSON validation"
            echo "   Install: brew install jq"
        fi
    else
        echo "No JSON files found to validate."
    fi
