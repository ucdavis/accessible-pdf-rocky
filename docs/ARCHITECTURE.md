# Architecture

This document outlines the production-grade architecture for the accessible PDF system, integrating Cloudflare Workers, FastAPI, and local HPC with SLURM.

## System Architecture Overview

### 🔵 Cloudflare Layer (edge, fast, cheap)

- **Next.js frontend** on Cloudflare Pages
- **Cloudflare Worker API**:
  - PDF upload → R2
  - Submit jobs → Cloudflare Queue
  - Expose job status
- **R2 Object Storage**:
  - Raw PDFs
  - Intermediate JSON
  - Final WCAG-compliant PDFs
- **Cloudflare Queues**:
  - Routes jobs to GPU inference workers via FastAPI

Cloudflare provides fast ingress, scaling, and routing—not heavy compute.

### 🟢 FastAPI Layer (job controller)

Runs on a publicly accessible host:

- Azure VM
- On-prem login node (NOT compute node)
- Small Kubernetes VM
- Bare-metal host

**Responsibilities:**

- Pull jobs from Cloudflare Queues
- Create SLURM job submissions
- Track job status
- Fetch results from HPC
- Upload outputs to R2
- Update Postgres
- Expose API to frontend

The FastAPI service bridges Cloudflare and the HPC cluster.

### 🔴 Local HPC Cluster (heavy compute)

SLURM manages:

- LayoutLMv3 / Donut / TAPAS inference
- BLIP-2 / LLaVA alt-text generation
- OCR (Tesseract, PaddleOCR, or Azure OCR fallback)
- PDF tagging with iText or PyMuPDF
- WCAG rule enforcement

Workers run on GPU nodes (A100/H100, etc.).

Output flows back to:

- HPC scratch folder → retrieved by FastAPI
- Or directly uploaded to R2 via endpoint

## System Diagram

```text
                    ┌──────────────────────────────────┐
                    │        Next.js Frontend           │
                    │      (Cloudflare Pages)           │
                    └──────────────────▲────────────────┘
                                       │ HTTPS
                                       │
                    ┌──────────────────┴───────────────────┐
                    │         Cloudflare Worker API         │
                    │  - PDF Upload                         │
                    │  - R2 Put                             │
                    │  - Job Submit to Queue                │
                    └───────────────┬──────────────────────┘
                                    │
                          ┌─────────▼──────────┐
                          │   Cloudflare Queue  │
                          │ job messages        │
                          └─────────┬──────────┘
                                    │ dequeues
                    ┌───────────────▼────────────────┐
                    │      FastAPI Controller         │
                    │ - Pull Queue Jobs               │
                    │ - Submit SLURM Jobs             │
                    │ - Monitor SLURM via sacct/squeue│
                    │ - Upload results to R2          │
                    └───────────────┬────────────────┘
                                    │
                          ┌─────────▼───────────────┐
                          │   HPC Cluster (SLURM)    │
                          │   GPU Nodes run heavy ML │
                          │  - Layout detection       │
                          │  - Alt-text models        │
                          │  - WCAG enforcement       │
                          │  - PDF tagging            │
                          └─────────┬────────────────┘
                                    │ output
                    ┌───────────────▼────────────────┐
                    │            R2 Storage           │
                    │ accessible PDFs, reports, JSON  │
                    └─────────────────────────────────┘
```

## Repository Structure

```text
accessible-pdf-rocky/
│
├── frontend/                 # Next.js on Cloudflare Pages
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx
│   │       ├── upload/
│   │       └── layout.tsx
│   └── package.json
│
├── workers/                  # Cloudflare Workers
│   ├── api/
│   │   ├── upload.ts
│   │   ├── submit-job.ts
│   │   └── job-status.ts
│   ├── wrangler.toml
│   └── package.json
│
├── controller/               # FastAPI bridge service
│   ├── main.py
│   ├── queue_listener.py
│   ├── hpc/
│   │   ├── submit.py
│   │   ├── status.py
│   │   └── scripts/
│   │       └── job.sh
│   ├── r2/
│   │   ├── upload.py
│   │   └── download.py
│   ├── db/
│   │   ├── models.py
│   │   └── session.py
│   ├── services/
│   │   └── result_handler.py
│   └── pyproject.toml
│
├── hpc_runner/               # Script executed on HPC compute nodes
│   ├── runner.py
│   ├── processors/
│   └── pyproject.toml
│
└── docs/
    └── ARCHITECTURE.md
```

## Data Flow

### 1. Cloudflare Worker → Queue → FastAPI Controller

#### Worker: submit-job.ts

```typescript
export default {
  async fetch(req, env) {
    const jobId = crypto.randomUUID();
    const body = await req.json();

    // Place job into Cloudflare Queue
    await env.JOB_QUEUE.send({
      jobId,
      r2Key: body.r2Key,
      timestamp: Date.now()
    });

    return new Response(JSON.stringify({ jobId }), {
      headers: { "Content-Type": "application/json" }
    });
  }
};
```

### 2. FastAPI Controller: Queue Listener

#### queue_listener.py

```python
import asyncio
from cloudflare_queue import CloudflareQueueConsumer
from hpc.submit import submit_slurm_job
from db.session import db_session
from db.models import Job

consumer = CloudflareQueueConsumer("JOB_QUEUE")

@consumer.on_message
async def handle_job(message):
    job_id = message["jobId"]
    r2_key = message["r2Key"]

    # Submit SLURM job
    slurm_id = submit_slurm_job(job_id, r2_key)

    # Save slurm_id in DB
    with db_session() as db:
        job = Job(id=job_id, slurm_id=slurm_id, status="submitted")
        db.add(job)
        db.commit()

consumer.run()
```

### 3. SLURM Submission from FastAPI

#### hpc/submit.py

```python
import subprocess
from pathlib import Path

def submit_slurm_job(job_id: str, pdf_path: str) -> str:
    """
    Submit a SLURM job for PDF accessibility analysis.
    
    Args:
        job_id: Unique job identifier
        pdf_path: Path to the PDF file on the HPC filesystem
        
    Returns:
        SLURM job ID as a string
    """
    script_path = Path(__file__).parent / "scripts" / "job.sh"
    
    cmd = [
        "sbatch",
        f"--job-name=wcag-{job_id}",
        f"--export=ALL,JOB_ID={job_id},PDF_PATH={pdf_path}",
        str(script_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    slurm_id = result.stdout.strip().split()[-1]
    return slurm_id
```

### 4. SLURM Batch Script (GPU inference)

#### hpc/scripts/job.sh

```bash
#!/bin/bash
#SBATCH --job-name=${JOB_ID}
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu
#SBATCH --time=02:00:00
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err

# Change to hpc_runner directory
cd $HOME/accessible-pdf-rocky/hpc_runner

# Run using uv
uv run runner.py $PDF_PATH \
  --job-id $JOB_ID \
  --output results/${JOB_ID}.json
```

### 5. HPC ML Runner (Heavy Processing)

#### hpc_runner/runner.py

```python
#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

def analyze_pdf(pdf_path: str, job_id: str) -> dict:
    """
    Analyze a PDF file for accessibility issues.
    
    This is where the heavy ML happens:
    - Layout detection (LayoutLMv3/Donut)
    - Alt-text generation (BLIP-2/LLaVA)
    - Table extraction (TAPAS)
    - OCR (Tesseract/PaddleOCR)
    - WCAG enforcement
    - PDF tagging
    
    Args:
        pdf_path: Path to the PDF file to analyze
        job_id: Unique job identifier
        
    Returns:
        Dictionary containing analysis results
    """
    # TODO: Implement actual PDF analysis
    print(f"Analyzing PDF: {pdf_path}")
    print(f"Job ID: {job_id}")
    
    return {
        "job_id": job_id,
        "pdf_path": pdf_path,
        "status": "completed",
        "issues": []
    }

def main():
    parser = argparse.ArgumentParser(
        description="Analyze PDF accessibility on HPC nodes"
    )
    parser.add_argument("pdf_path", help="Path to PDF file")
    parser.add_argument("--job-id", required=True, help="Job ID")
    parser.add_argument("--output", help="Output JSON path")
    
    args = parser.parse_args()
    
    # Validate PDF exists
    if not Path(args.pdf_path).exists():
        print(f"Error: PDF not found: {args.pdf_path}", file=sys.stderr)
        sys.exit(1)
    
    # Run analysis
    results = analyze_pdf(args.pdf_path, args.job_id)
    
    # Write results
    if args.output:
        import json
        Path(args.output).write_text(json.dumps(results, indent=2))
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### 6. SLURM Status Monitoring

#### hpc/status.py

```python
import subprocess

def get_slurm_status(slurm_id: str) -> str:
    """Query SLURM job status."""
    cmd = ["sacct", "-j", slurm_id, "--format=State", "--noheader"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip().split()[0]
```

### 7. Cloudflare Worker: Job Status API

#### workers/api/job-status.ts

```typescript
export default {
  async fetch(req, env) {
    const jobId = new URL(req.url).searchParams.get("jobId");
    const res = await fetch(`${env.FASTAPI_URL}/status/${jobId}`);
    return res;
  }
};
```

## End-to-End Flow

1. **User uploads PDF** → Cloudflare Worker
2. **Worker saves to R2**
3. **Worker sends Queue message**
4. **FastAPI listener pulls job**
5. **FastAPI submits SLURM job**
6. **SLURM runs ML inference** → produces accessible PDF
7. **Script uploads accessible PDF to R2**
8. **FastAPI updates database**
9. **Frontend polls job status**
10. **User downloads accessible PDF**

## Deployment Considerations

### FastAPI Controller

- Must be accessible from both Cloudflare (public internet) and HPC cluster
- Can run on HPC login node or separate VM
- Needs credentials for:
  - Cloudflare Queues
  - R2 storage
  - Postgres database
  - SLURM submission

### HPC Runner

- Deployed to HPC shared filesystem
- Uses uv for Python environment management
- Requires GPU nodes for inference
- Results stored in shared filesystem or uploaded to R2

### Scaling

- Cloudflare handles edge scaling automatically
- FastAPI can be horizontally scaled behind load balancer
- HPC scales via SLURM job scheduling
- R2 provides unlimited object storage

## Security

- **API Authentication**: Cloudflare Access or API tokens
- **HPC Access**: SSH keys, no passwords
- **R2 Credentials**: Environment variables, never in code
- **Database**: Connection pooling, encrypted at rest
- **PDFs**: Signed URLs for temporary access

## Monitoring

- **Cloudflare**: Analytics dashboard
- **FastAPI**: Prometheus metrics
- **SLURM**: `sacct`, `squeue` for job monitoring
- **R2**: Storage metrics via Cloudflare dashboard
- **Database**: Query performance monitoring

This architecture is production-ready, horizontally scalable, HPC-integrated, and Cloudflare-native.
