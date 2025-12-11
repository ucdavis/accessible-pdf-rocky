# Accessible PDF AI

Production-grade accessible PDF system with [Cloudflare Workers](https://developers.cloudflare.com/workers/), [.NET 8](https://dotnet.microsoft.com/), and HPC/SLURM integration.

[![CI](https://github.com/ucdavis/accessible-pdf-rocky/actions/workflows/ci.yml/badge.svg)](https://github.com/ucdavis/accessible-pdf-rocky/actions/workflows/ci.yml)
[![CodeQL](https://github.com/ucdavis/accessible-pdf-rocky/actions/workflows/codeql.yml/badge.svg)](https://github.com/ucdavis/accessible-pdf-rocky/actions/workflows/codeql.yml)
[![Security Audit](https://github.com/ucdavis/accessible-pdf-rocky/actions/workflows/security.yml/badge.svg)](https://github.com/ucdavis/accessible-pdf-rocky/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/ucdavis/accessible-pdf-rocky/graph/badge.svg?token=2NJXW8VPKO)](https://codecov.io/gh/ucdavis/accessible-pdf-rocky)

## Status

🚧 **Current Phase**: Project Scaffold  
🎯 **Next**: MVP Development ([see roadmap](docs/MVP_ROADMAP.md))

## Why Use This?

This project aims to automate PDF accessibility remediation using modern AI models.

- **Batch Processing**: Enable processing of large document collections without manual review
- **Cost Efficient**: Leverage existing HPC infrastructure for cost-effective processing
- **Deployment Flexibility**: Cloud, hybrid, or fully on-premise with HPC integration
- **Modern AI**: Uses LayoutLMv3, BLIP-2, and other state-of-the-art models for document understanding and alt-text generation
- **WCAG 2.1 AA Compliance**: Automated enforcement, not just checking. Easily upgrade compliance standards.

Designed for UC Davis document remediation needs.

**[Learn more about the rationale →](docs/WHY.md)**

## Repository Structure

- `client/` – [React 19](https://react.dev/) + [Vite](https://vite.dev/) frontend with [TanStack Router](https://tanstack.com/router) and [Query](https://tanstack.com/query)
- `hpc_runner/` – SLURM job runner (heavy ML + PDF, Python)
- `server/` – [.NET 8](https://dotnet.microsoft.com/) Web API bridge to HPC cluster
- `server.core/` – Domain models and shared logic
- `tests/` – .NET test project with xUnit
- `workers/` – [Cloudflare Workers](https://developers.cloudflare.com/workers/) (R2 + Queues, TypeScript)

## Quick Start

```bash
# Copy environment template
cp .env.example .env

# Setup all development environments
just setup

# Run CI checks (linting + tests)
just ci

# Start all services with Docker
just dev

# Before committing (includes coverage)
just commit-check

# See all available commands
just help
```

## Dev Container

For a consistent development environment, use the provided Dev Container configuration:

**VS Code:**
1. Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. Open this project in VS Code
3. Click "Reopen in Container" when prompted

**GitHub Codespaces:**
1. Click the green "Code" button on GitHub
2. Select the "Codespaces" tab
3. Click "Create codespace on [branch]"

The dev container includes Node.js, .NET SDK, Python/uv, and all required VS Code extensions. See [.devcontainer/README.md](.devcontainer/README.md) for details.

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and data flow
- [Development Guide](docs/DEVELOPMENT.md) - Setup and workflows
- [MVP Roadmap](docs/MVP_ROADMAP.md) - Path to functional prototype
- [System Design](docs/SYSTEM_DESIGN.md) - Technical decisions
- [Testing Strategy](docs/TESTING.md) - Test coverage and approach
- [Why This Project?](docs/WHY.md) - Problem statement and rationale

### Operations

- [Monitoring Setup](docs/MONITORING_SETUP.md) - Prometheus and Grafana configuration
- [Metrics Deployment](docs/METRICS_DEPLOYMENT.md) - Cloudflare Worker metrics infrastructure
- [Security Setup](docs/SECURITY_SETUP.md) - Authentication and secure configuration

## MVP Progress

Track development: [MVP v0.1 Milestone](https://github.com/ucdavis/accessible-pdf-rocky/milestone/1)

10 issues across 5 phases:

1. Infrastructure (R2, Queue, Database)
2. Backend (Controller, SLURM)
3. Processing (Mock PDF analysis)
4. Frontend (Upload, Status)
5. Validation (E2E tests)
