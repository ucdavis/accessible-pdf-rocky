# Accessible PDF AI

Production-grade accessible PDF system with Cloudflare Workers, FastAPI, and HPC/SLURM integration.

## Status

🚧 **Current Phase**: Project Scaffold  
🎯 **Next**: MVP Development ([see roadmap](docs/MVP_ROADMAP.md))

## Repository Structure

- `frontend/` – Next.js UI (Cloudflare Pages)
- `workers/` – Cloudflare Workers (R2 + Queues)
- `controller/` – FastAPI bridge to HPC cluster
- `hpc_runner/` – SLURM job runner (heavy ML + PDF)

## Quick Start

```bash
# Setup all development environments
just setup

# Run linting
just lint

# Start all services with Docker
just dev
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and data flow
- [MVP Roadmap](docs/MVP_ROADMAP.md) - Path to functional prototype
- [Development Guide](docs/DEVELOPMENT.md) - Setup and workflows
- [System Design](docs/SYSTEM_DESIGN.md) - Technical decisions

## MVP Progress

Track development: [MVP v0.1 Milestone](https://github.com/ucdavis/accessible-pdf-rocky/milestone/1)

10 issues across 5 phases:
1. Infrastructure (R2, Queue, Database)
2. Backend (Controller, SLURM)
3. Processing (Mock PDF analysis)
4. Frontend (Upload, Status)
5. Validation (E2E tests)
