# MVP Roadmap

## Overview

This document outlines the path from current scaffold to a functional MVP.

## Current Status: Project Scaffold ✅

We have:
- Complete monorepo structure
- Development tooling (justfile, linting, type checking)
- Comprehensive documentation
- Placeholder implementations for all components

## MVP Goal

A working end-to-end flow where:
1. User uploads PDF via frontend
2. PDF stored in R2
3. Job queued and processed on HPC
4. Results available via API
5. User sees status and downloads result

## MVP Issues

All MVP work is tracked in GitHub Issues with the `MVP v0.1` milestone:

- **Issue #1**: Frontend PDF upload UI
- **Issue #2**: Cloudflare R2 storage integration
- **Issue #3**: Cloudflare Queue for job submission
- **Issue #4**: Database setup (Postgres)
- **Issue #5**: FastAPI controller queue listener
- **Issue #6**: SLURM job submission from controller
- **Issue #7**: Basic PDF analysis (mock implementation)
- **Issue #8**: Job status API endpoint
- **Issue #9**: Frontend status polling and results display
- **Issue #10**: End-to-end integration test

View milestone: https://github.com/ucdavis/accessible-pdf-rocky/milestone/1

## Recommended Implementation Order

### Phase 1: Infrastructure (Issues #2, #3, #4)
1. Set up R2 bucket
2. Configure Cloudflare Queue
3. Deploy Postgres database

### Phase 2: Backend Foundation (Issues #5, #6, #8)
4. Implement queue listener in controller
5. SLURM job submission
6. Status API endpoint

### Phase 3: Processing (Issue #7)
7. Mock PDF analysis in hpc_runner

### Phase 4: Frontend (Issues #1, #9)
8. Upload UI
9. Status polling and results

### Phase 5: Validation (Issue #10)
10. End-to-end integration test

## GitHub Project Board

To track progress visually, create a GitHub Project board:

1. Go to: https://github.com/orgs/ucdavis/projects
2. Click "New project"
3. Title: "MVP Development"
4. Template: "Board"
5. Add all MVP issues to the project

## Definition of Done

MVP is complete when:
- [ ] User can upload a PDF
- [ ] System processes the PDF (even with mock analysis)
- [ ] User receives results
- [ ] End-to-end test passes
- [ ] All 10 MVP issues closed

## Post-MVP Work

After MVP completion, focus shifts to:
- Real ML models (LayoutLMv3, BLIP-2, etc.)
- WCAG compliance checking
- PDF remediation
- Performance optimization
- Production deployment
