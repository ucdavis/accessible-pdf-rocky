# Accessible PDF AI

Production-grade accessible PDF system with [Cloudflare Workers](https://developers.cloudflare.com/workers/), [FastAPI](https://fastapi.tiangolo.com/), and HPC/SLURM integration.

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

- `controller/` – [FastAPI](https://fastapi.tiangolo.com/) bridge to HPC cluster
- `frontend/` – Next.js UI (Cloudflare Pages)
- `hpc_runner/` – SLURM job runner (heavy ML + PDF)
- `workers/` – [Cloudflare Workers](https://developers.cloudflare.com/workers/) (R2 + Queues)

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

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and data flow
- [Development Guide](docs/DEVELOPMENT.md) - Setup and workflows
- [MVP Roadmap](docs/MVP_ROADMAP.md) - Path to functional prototype
- [System Design](docs/SYSTEM_DESIGN.md) - Technical decisions
- [Testing Strategy](docs/TESTING.md) - Test coverage and approach
- [Why This Project?](docs/WHY.md) - Problem statement and rationale

## MVP Progress

Track development: [MVP v0.1 Milestone](https://github.com/ucdavis/accessible-pdf-rocky/milestone/1)

10 issues across 5 phases:

1. Infrastructure (R2, Queue, Database)
2. Backend (Controller, SLURM)
3. Processing (Mock PDF analysis)
4. Frontend (Upload, Status)
5. Validation (E2E tests)
