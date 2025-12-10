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
    
    # NPM audit for frontend and workers
    if [ -d "frontend" ]; then
        echo "Auditing frontend npm packages..."
        cd frontend && npm audit --audit-level=moderate || true && cd ..
        echo ""
    fi
    if [ -d "workers" ]; then
        echo "Auditing workers npm packages..."
        cd workers && npm audit --audit-level=moderate || true && cd ..
        echo ""
    fi
    
    # Python pip-audit for controller and hpc_runner
    if [ -d "controller" ]; then
        echo "Auditing controller Python packages..."
        cd controller && uv pip install --quiet pip-audit && uv run pip-audit || true && cd ..
        echo ""
    fi
    if [ -d "hpc_runner" ]; then
        echo "Auditing hpc_runner Python packages..."
        cd hpc_runner && uv pip install --quiet pip-audit && uv run pip-audit || true && cd ..
        echo ""
    fi
    
    echo "✅ Security audit complete!"

# Build all projects
build: _ensure-npm _ensure-uv
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -d "frontend" ]; then
        echo "Building frontend..."
        cd frontend && npm run build && cd ..
    fi
    if [ -d "workers" ]; then
        echo "Building workers..."
        cd workers && npm run build && cd ..
    fi

# CI simulation: quality checks with comprehensive testing (fast, matches GitHub Actions)
ci: lint test
    @echo "🎯 CI simulation complete!"

# Clean build artifacts
clean:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Cleaning build artifacts..."
    [ -d "frontend/.next" ] && rm -rf frontend/.next
    [ -d "frontend/node_modules" ] && rm -rf frontend/node_modules
    [ -d "workers/node_modules" ] && rm -rf workers/node_modules
    [ -d "controller/.venv" ] && rm -rf controller/.venv
    [ -d "hpc_runner/.venv" ] && rm -rf hpc_runner/.venv
    [ -d "controller/__pycache__" ] && rm -rf controller/__pycache__
    [ -d "hpc_runner/__pycache__" ] && rm -rf hpc_runner/__pycache__
    echo "✅ Clean complete!"

# Pre-commit workflow: comprehensive validation with coverage before committing
# Runs: linting + all tests with coverage reports
commit-check: lint test-coverage
    @echo "🚀 Ready to commit! All checks passed!"

# Start all services with Docker Compose (attached)
dev:
    docker compose up --build

# Start only controller (local)
dev-controller: _ensure-uv
    cd controller && uv run uvicorn main:app --reload

# Stop all Docker services
dev-down:
    docker compose down

# Start only frontend (local)
dev-frontend: _ensure-npm
    cd frontend && npm run dev

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
    @echo "  just lint-code     # Code linting (Python, JavaScript, Shell)"
    @echo "  just lint-docs     # Documentation linting (Markdown, Spelling)"
    @echo "  just lint-config   # Configuration validation (JSON, YAML, Actions)"
    @echo ""
    @echo "Security:"
    @echo "  just audit         # Check for vulnerabilities in dependencies"
    @echo ""
    @echo "Testing:"
    @echo "  just test          # Run all tests"
    @echo "  just test-coverage # Run all tests with coverage reports"
    @echo "  just test-python   # Python tests only"
    @echo "  just test-js       # JavaScript tests only"
    @echo ""
    @echo "Development:"
    @echo "  just dev           # Start all services with Docker Compose"
    @echo "  just dev-up        # Start all services (detached)"
    @echo "  just dev-down      # Stop all services"
    @echo "  just dev-logs      # View logs"
    @echo "  just dev-frontend  # Start only frontend (local)"
    @echo "  just dev-controller # Start only controller (local)"
    @echo "  just dev-workers   # Start only workers (local)"

# JavaScript/TypeScript linting
js-lint: _ensure-npm
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -d "frontend" ]; then
        echo "Linting frontend..."
        cd frontend && npm run lint && cd ..
    fi
    if [ -d "workers" ]; then
        echo "Linting workers..."
        cd workers && npm run lint && cd ..
    fi

# All linting: code + documentation + configuration
lint: lint-code lint-docs lint-config

# Code linting: Python + JavaScript + Shell
lint-code: python-lint js-lint shell-lint

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
    if [ -d "controller" ]; then
        echo "Linting controller..."
        cd controller && uv run ruff check . --fix && uv run ruff format . && uv run mypy . && cd ..
    fi
    if [ -d "hpc_runner" ]; then
        echo "Linting hpc_runner..."
        cd hpc_runner && uv run ruff check . --fix && uv run ruff format . && uv run mypy . && cd ..
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
    for tool in uv node npm docker shellcheck shfmt; do
        if command -v "$tool" &> /dev/null; then
            echo "  ✓ $tool installed"
        else
            echo "  ✗ $tool NOT installed"
            case "$tool" in
                uv)
                    echo "    Install: https://github.com/astral-sh/uv"
                    echo "    macOS: brew install uv"
                    echo "    Linux/WSL: curl -LsSf https://astral.sh/uv/install.sh | sh"
                    ;;
                node|npm) echo "    Install: https://nodejs.org" ;;
                docker)
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
    
    echo ""
    echo "Installing Python environments..."
    
    # Controller setup
    if [ -d "controller" ]; then
        echo "  Setting up controller..."
        cd controller && uv sync && cd ..
    fi
    
    # HPC runner setup
    if [ -d "hpc_runner" ]; then
        echo "  Setting up hpc_runner..."
        cd hpc_runner && uv sync && cd ..
    fi
    
    # Frontend setup
    if [ -d "frontend" ]; then
        echo "  Setting up frontend..."
        cd frontend && npm install && cd ..
    fi
    
    # Workers setup
    if [ -d "workers" ]; then
        echo "  Setting up workers..."
        cd workers && npm install && cd ..
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
test: test-python test-js

# Run tests with coverage
test-coverage: test-python-coverage test-js-coverage

# JavaScript tests
test-js: _ensure-npm
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
        echo "Testing frontend..."
        cd frontend && npm test && cd ..
    fi
    if [ -d "workers" ] && [ -f "workers/package.json" ]; then
        echo "Testing workers..."
        cd workers && npm test && cd ..
    fi

# JavaScript tests with coverage
test-js-coverage: _ensure-npm
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
        echo "Testing frontend with coverage..."
        cd frontend && npm run test:coverage && cd ..
    fi
    if [ -d "workers" ] && [ -f "workers/package.json" ]; then
        echo "Testing workers with coverage..."
        cd workers && npm run test:coverage && cd ..
    fi

# Python tests
test-python: _ensure-uv
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -d "controller" ] && [ -f "controller/pyproject.toml" ]; then
        echo "Testing controller..."
        cd controller && uv run pytest && cd ..
    fi
    if [ -d "hpc_runner" ] && [ -f "hpc_runner/pyproject.toml" ]; then
        echo "Testing hpc_runner..."
        cd hpc_runner && uv run pytest && cd ..
    fi

# Python tests with coverage
test-python-coverage: _ensure-uv
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -d "controller" ] && [ -f "controller/pyproject.toml" ]; then
        echo "Testing controller with coverage..."
        cd controller && uv run pytest --cov=. --cov-report=html --cov-report=term && cd ..
    fi
    if [ -d "hpc_runner" ] && [ -f "hpc_runner/pyproject.toml" ]; then
        echo "Testing hpc_runner with coverage..."
        cd hpc_runner && uv run pytest --cov=. --cov-report=html --cov-report=term && cd ..
    fi

# Type checking
typecheck: _ensure-npm
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -d "frontend" ]; then
        echo "Type checking frontend..."
        cd frontend && npx tsc --noEmit && cd ..
    fi
    if [ -d "workers" ]; then
        echo "Type checking workers..."
        cd workers && npx tsc --noEmit && cd ..
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
