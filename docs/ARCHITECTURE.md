# Architecture

This document outlines the production-grade architecture for the accessible PDF system, integrating [Cloudflare Workers](https://developers.cloudflare.com/workers/), [.NET 10](https://learn.microsoft.com/en-us/aspnet/core/) on Azure, and local HPC with SLURM.

## System Architecture Overview

### 🔵 Cloudflare Layer (cheap, edge, fast, on-demand, scalable)

- **[React 19](https://react.dev/) + [Vite](https://vite.dev/) frontend** on [Cloudflare Pages](https://developers.cloudflare.com/pages/)
  - Static site deployed to global CDN
  - [TanStack Router](https://tanstack.com/router) for file-based routing
  - [TanStack Query](https://tanstack.com/query) for data fetching and caching
  - Deployed via Azure Pipelines
- **[Cloudflare Worker](https://developers.cloudflare.com/workers/) API**:
  - PDF upload → R2
  - Submit jobs → Cloudflare Queue
  - D1 database operations
- **[R2](https://developers.cloudflare.com/r2/) Object Storage**:
  - Raw PDFs
  - Intermediate JSON
  - Final WCAG-compliant PDFs
- **[Cloudflare Queues](https://developers.cloudflare.com/queues/)**:
  - Routes jobs to GPU inference workers via .NET API

Cloudflare provides fast ingress, scaling, and routing—not heavy compute.

### 🟢 [.NET 10](https://learn.microsoft.com/en-us/aspnet/core/) Layer (job controller)

Runs on [Azure App Service](https://learn.microsoft.com/en-us/azure/app-service/) (Linux):

- ASP.NET Core Web API
- Deployed to Azure via Azure Pipelines

**Responsibilities:**

- Pull jobs from Cloudflare Queues
- Generate presigned R2 URLs for SLURM jobs
- Create [SLURM](https://slurm.schedmd.com/) job submissions
- Track job status
- Update [D1 database](https://developers.cloudflare.com/d1/) via API Worker
- Expose API to frontend

The .NET API service bridges Cloudflare and the HPC cluster.

### 🔴 Local HPC Cluster (heavy compute)

[SLURM](https://slurm.schedmd.com/) manages:

- [LayoutLMv3](https://huggingface.co/docs/transformers/model_doc/layoutlmv3) / Donut / TAPAS inference
- [BLIP-2](https://huggingface.co/docs/transformers/model_doc/blip-2) / LLaVA alt-text generation
- OCR ([Tesseract](https://github.com/tesseract-ocr/tesseract), [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR), or Azure OCR fallback)
- PDF tagging with iText or [PyMuPDF](https://pymupdf.readthedocs.io/)
- WCAG rule enforcement

Workers run on GPU nodes (A100/H100, etc.).

Output flows back to R2:

- SLURM jobs download input PDFs directly from R2
- SLURM jobs upload processed PDFs directly to R2
- No file transfers through .NET API controller

## System Diagram

```mermaid
flowchart TD
    Frontend["React + Vite Frontend<br/>(Cloudflare Pages)"] -->|HTTPS| Workers
    Frontend -->|HTTPS| Controller
    
    Workers["Cloudflare Worker API<br/>• PDF Upload<br/>• R2 Put<br/>• Job Submit to Queue"] --> Queue
    
    Queue["Cloudflare Queue<br/>(job messages)"] -->|dequeues| Controller
    
    Controller[".NET 10 Web API<br/>(Azure App Service)<br/>• Pull Queue Jobs<br/>• Generate R2 URLs<br/>• Submit SLURM Jobs<br/>• Monitor sacct/squeue"] --> HPC
    Controller -->|HTTP API| DBWorker
    
    DBWorker["D1 API Worker<br/>• Job tracking<br/>• User management<br/>• Processing metrics"]
    
    HPC["HPC Cluster SLURM<br/>GPU Nodes run heavy ML<br/>• Layout detection<br/>• Alt-text models<br/>• WCAG enforcement<br/>• PDF tagging"] <-->|download/upload| R2
    
    R2["R2 Storage<br/>accessible PDFs, reports, JSON"]
    
    style Frontend fill:#80d4ff,stroke:#0066cc,stroke-width:3px,color:#000
    style Workers fill:#80d4ff,stroke:#0066cc,stroke-width:3px,color:#000
    style Queue fill:#80d4ff,stroke:#0066cc,stroke-width:3px,color:#000
    style Controller fill:#90ee90,stroke:#228b22,stroke-width:3px,color:#000
    style DBWorker fill:#80d4ff,stroke:#0066cc,stroke-width:3px,color:#000
    style HPC fill:#ff9999,stroke:#cc0000,stroke-width:3px,color:#000
    style R2 fill:#80d4ff,stroke:#0066cc,stroke-width:3px,color:#000
```

## Repository Structure

```text
accessible-pdf-rocky/
│
├── .github/
│   └── workflows/           # CI/CD workflows
│       ├── ci.yml
│       ├── codeql.yml
│       └── security.yml
│
├── client/                   # React 19 + Vite on Cloudflare Pages
│   ├── src/
│   │   ├── main.tsx          # Application entry point
│   │   ├── routes/           # TanStack Router file-based routes
│   │   │   ├── __root.tsx    # Root layout
│   │   │   ├── index.tsx     # Home page
│   │   │   ├── upload.tsx    # PDF upload UI
│   │   │   └── jobs/
│   │   │       ├── index.tsx          # Jobs list
│   │   │       └── $jobId.tsx         # Job details with auto-polling
│   │   ├── components/       # Reusable UI components
│   │   └── lib/
│   │       └── api.ts        # API client for .NET endpoints
│   ├── vite.config.ts        # Vite configuration with API proxy
│   └── package.json
│
├── server/                   # .NET 10 Web API (https://learn.microsoft.com/en-us/aspnet/core/)
│   ├── Program.cs            # Application entry point
│   ├── appsettings.json      # Configuration
│   ├── Controllers/
│   │   └── JobController.cs  # Job status endpoints
│   ├── Services/
│   │   ├── DatabaseApiClient.cs  # Cloudflare D1 API client
│   │   └── MetricsClient.cs      # Metrics push client
│   └── server.csproj
│
├── server.core/              # Domain models and shared logic
│   ├── Domain/
│   │   ├── Job.cs
│   │   ├── User.cs
│   │   ├── ProcessingMetric.cs
│   │   └── JobStatus.cs
│   └── server.core.csproj
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT.md
│   ├── MVP_ROADMAP.md
│   ├── SYSTEM_DESIGN.md
│   ├── TESTING.md
│   └── WHY.md
│
│
├── hpc_runner/               # HPC compute jobs (heavy ML processing)
│   ├── runner.py             # Main SLURM job script
│   ├── ai/                   # Low-level ML model wrappers
│   │   ├── layout/
│   │   │   ├── model.py      # LayoutLMv3 wrapper
│   │   │   └── inference.py  # Batch inference
│   │   ├── alt_text/
│   │   │   ├── model.py      # BLIP-2/LLaVA wrapper
│   │   │   └── inference.py  # Image captioning
│   │   └── tables/
│   │       ├── model.py      # TAPAS wrapper
│   │       └── inference.py  # Table parsing
│   ├── processors/           # High-level business logic
│   │   ├── __init__.py
│   │   ├── layout.py         # Calls ai/layout, adds WCAG validation
│   │   ├── alttext.py        # Calls ai/alt_text, ensures compliance
│   │   ├── ocr.py            # OCR orchestration (external tools)
│   │   ├── wcag.py           # Rule-based validation
│   │   └── tagging.py        # PDF tagging (PyMuPDF/iText)
│   └── pyproject.toml
│
├── workers/                  # Cloudflare Workers (https://developers.cloudflare.com/workers/)
│   ├── api/
│   │   ├── upload.ts         # PDF upload to R2
│   │   ├── submit-job.ts     # Job submission to queue
│   │   └── job-status.ts     # Status query proxy
│   ├── wrangler.toml
│   └── package.json
│
├── tests/                    # .NET xUnit tests
│   ├── JobControllerTests.cs
│   └── tests.csproj
│
├── .gitignore
├── .markdownlint.json
├── app.sln
├── cspell.json
├── docker-compose.yml
├── global.json
├── justfile
└── README.md
```

### Component Clarification: workers/ vs hpc_runner/

**Important**: "workers" refers to [Cloudflare Workers](https://developers.cloudflare.com/workers/), not compute workers!

#### workers/ - [Cloudflare Workers](https://developers.cloudflare.com/workers/) (Edge API)

- **Runtime**: Cloudflare's global edge network
- **Language**: TypeScript
- **Purpose**: Lightweight HTTP endpoints (~10-50ms)
- **Resources**: Minimal CPU/memory, no GPU
- **Responsibilities**:
  - Handle PDF uploads → R2
  - Submit jobs → Cloudflare Queue
  - Proxy status queries → .NET API
  - D1 database operations

#### hpc_runner/ - HPC Compute Jobs (Heavy ML)

- **Runtime**: HPC@UCD cluster via [SLURM](https://slurm.schedmd.com/)
- **Language**: Python
- **Purpose**: GPU-intensive ML processing (minutes to hours)
- **Resources**: GPU nodes (A100/H100), 10s of GB RAM
- **Architecture**: Two-layer separation of concerns
  - `ai/` = Low-level ML model wrappers (loads models, runs inference)
  - `processors/` = High-level business logic (validates, adds WCAG rules)
- **Responsibilities**:
  - Layout detection ([LayoutLMv3](https://huggingface.co/docs/transformers/model_doc/layoutlmv3) - GPU intensive)
  - Alt-text generation ([BLIP-2](https://huggingface.co/docs/transformers/model_doc/blip-2)/LLaVA - GPU intensive)
  - OCR ([Tesseract](https://github.com/tesseract-ocr/tesseract)/[PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR))
  - WCAG compliance checking
  - PDF tagging and remediation

**Internal Flow:**

1. `runner.py` orchestrates the pipeline
2. Calls `ai/*` for raw ML predictions
3. Passes to `processors/*` for validation and business logic
4. Returns application-ready results

**External Flow**: Frontend (Cloudflare Pages) → .NET API (Azure) / Cloudflare Workers → Queue → Controller → SLURM → HPC Runner (heavy ML on GPU) → Results → R2

**Note:** See [SYSTEM_DESIGN.md](./SYSTEM_DESIGN.md) for detailed architecture of the `ai/` vs `processors/` layers.

### Understanding server/Services vs hpc_runner Separation

The .NET API (`server/`) and HPC runner (`hpc_runner/`) have clear separation of concerns.

#### Where They Run

**`server/Services`** - Runs on Azure App Service (.NET Web API)

- **NOT on GPU nodes**
- Orchestrates the overall flow between Cloudflare ↔ HPC ↔ R2
- Does lightweight coordination work
- No heavy ML processing
- Communicates with Cloudflare D1 via HTTP API

**`hpc_runner/`** - Runs on HPC GPU nodes via SLURM

- **ON GPU nodes with A100/H100**
- Does heavy ML processing
- Called by .NET API via SLURM submission

Current architecture focuses on clear separation:

- **`server/Services/DatabaseApiClient.cs`** - HTTP client for Cloudflare D1 database operations
- **`server/Services/MetricsClient.cs`** - Pushes processing metrics to Cloudflare Worker
- **`server/Controllers/JobController.cs`** - Exposes job status endpoints to frontend
- **`hpc_runner/`** - All heavy ML processing (layout detection, OCR, WCAG, PDF tagging)

#### Complete Flow Example

```mermaid
flowchart TD
    A["1. User uploads PDF to R2"] --> B["2. .NET API receives job<br/>from Cloudflare Queue"]
    B --> C["3. .NET API generates<br/>presigned R2 URLs"]
    C --> D["4. .NET API submits<br/>SLURM job with URLs"]
    
    D --> E["5. SLURM job starts:"]
    
    E --> E0["a. Download PDF from R2"]
    E0 --> E1["b. hpc_runner/processors/ocr.py<br/>runs Tesseract (heavy)"]
    E1 --> E2["c. hpc_runner/ai/layout<br/>runs LayoutLMv3 (heavy)"]
    E2 --> E3["d. hpc_runner/processors/wcag<br/>validates predictions"]
    E3 --> E4["e. hpc_runner/processors/tagging<br/>adds semantic tags"]
    E4 --> E5["f. Upload result to R2"]
    
    E5 --> F["6. Job completes"]
    F --> G["7. .NET API updates<br/>database status via D1 Worker"]
    
    style A fill:#80d4ff,stroke:#0066cc,stroke-width:2px,color:#000
    style B fill:#90ee90,stroke:#228b22,stroke-width:2px,color:#000
    style C fill:#90ee90,stroke:#228b22,stroke-width:2px,color:#000
    style D fill:#90ee90,stroke:#228b22,stroke-width:2px,color:#000
    style E fill:#ff9999,stroke:#cc0000,stroke-width:2px,color:#000
    style E0 fill:#ff9999,stroke:#cc0000,stroke-width:2px,color:#000
    style E1 fill:#ff9999,stroke:#cc0000,stroke-width:2px,color:#000
    style E2 fill:#ff9999,stroke:#cc0000,stroke-width:2px,color:#000
    style E3 fill:#ff9999,stroke:#cc0000,stroke-width:2px,color:#000
    style E4 fill:#ff9999,stroke:#cc0000,stroke-width:2px,color:#000
    style E5 fill:#ff9999,stroke:#cc0000,stroke-width:2px,color:#000
    style F fill:#90ee90,stroke:#228b22,stroke-width:2px,color:#000
    style G fill:#90ee90,stroke:#228b22,stroke-width:2px,color:#000
```

**Key Insight:** .NET API generates presigned URLs and orchestrates job submission. HPC jobs download inputs, perform all processing, and upload outputs directly to R2. No file transfers through the API.

## Data Flow

### 1. Cloudflare Worker → Queue → .NET API Controller

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

### 2. .NET API Controller: Queue Listener

#### QueueListener.cs (conceptual)

```csharp
using Server.Services;

public class QueueListener : BackgroundService
{
    private readonly DatabaseApiClient _dbClient;
    private readonly ILogger<QueueListener> _logger;

    public QueueListener(DatabaseApiClient dbClient, ILogger<QueueListener> logger)
    {
        _dbClient = dbClient;
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            // Poll Cloudflare Queue for new messages
            var message = await PollQueueAsync(stoppingToken);
            if (message != null)
            {
                await HandleJobAsync(message, stoppingToken);
            }
            await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken);
        }
    }

    private async Task HandleJobAsync(QueueMessage message, CancellationToken ct)
    {
        var jobId = message.JobId;
        var r2Key = message.R2Key;

        // Generate presigned URLs for SLURM job
        var inputUrl = GeneratePresignedUrl(r2Key, "get", 3600);
        var outputKey = $"outputs/{jobId}/accessible.pdf";
        var outputUrl = GeneratePresignedUrl(outputKey, "put", 3600);

        // Submit SLURM job with URLs
        var slurmId = await SubmitSlurmJobAsync(jobId, inputUrl, outputUrl);

        // Update database via D1 API Worker
        await _dbClient.UpdateJobStatusAsync(jobId, "submitted", slurmId);
    }
}
```

### 3. SLURM Submission from .NET API

#### SlurmSubmitter.cs (conceptual)

```csharp
using System.Diagnostics;

public class SlurmSubmitter
{
    public async Task<string> SubmitSlurmJobAsync(
        string jobId,
        string inputUrl,
        string outputUrl)
    {
        /*
        Submit a SLURM job for PDF accessibility analysis.
        
        Args:
            jobId: Unique job identifier
            inputUrl: Presigned R2 URL to download input PDF
            outputUrl: Presigned R2 URL to upload output PDF
            
        Returns:
            SLURM job ID as a string
        */
        var scriptPath = Path.Combine(AppContext.BaseDirectory, "scripts", "job.sh");
        
        var startInfo = new ProcessStartInfo
        {
            FileName = "sbatch",
            Arguments = $"--job-name=wcag-{jobId} " +
                       $"--export=ALL,JOB_ID={jobId},INPUT_URL={inputUrl},OUTPUT_URL={outputUrl} " +
                       scriptPath,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true
        };
        
        using var process = Process.Start(startInfo);
        var output = await process!.StandardOutput.ReadToEndAsync();
        await process.WaitForExitAsync();
        
        var slurmId = output.Trim().Split(' ').Last();
        return slurmId;
    }
}
```

### 4. SLURM Batch Script (GPU inference)

#### hpc_runner/scripts/job.sh

```bash
#!/bin/bash
#SBATCH --job-name=${JOB_ID}
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu
#SBATCH --time=02:00:00
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err

# Set up temporary working directory
WORK_DIR=$(mktemp -d)
cd $WORK_DIR

# Download PDF from R2 using presigned URL
curl -o input.pdf "$INPUT_URL"

# Change to hpc_runner directory
cd $HOME/accessible-pdf-rocky/hpc_runner

# Run using uv (https://docs.astral.sh/uv/)
uv run runner.py $WORK_DIR/input.pdf \
  --job-id $JOB_ID \
  --output $WORK_DIR/output.pdf

# Upload result to R2 using presigned URL
curl -X PUT --upload-file $WORK_DIR/output.pdf "$OUTPUT_URL"

# Cleanup
rm -rf $WORK_DIR
```

### 5. HPC ML Runner (Heavy Processing)

#### hpc_runner/runner.py

The runner orchestrates both the ML model layer (`ai/`) and business logic layer (`processors/`):

```python
#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

async def analyze_pdf(pdf_path: str, job_id: str) -> dict:
    """
    Analyze a PDF file for accessibility issues using two-layer architecture.
    
    Layer 1 (ai/): Raw ML model inference
    - Layout detection (LayoutLMv3)
    - Alt-text generation (BLIP-2/LLaVA)
    - Table parsing (TAPAS)
    
    Layer 2 (processors/): Business logic and validation
    - WCAG compliance checking
    - Result validation and cleanup
    - PDF tagging and structure
    
    Args:
        pdf_path: Path to the PDF file to analyze
        job_id: Unique job identifier
        
    Returns:
        Dictionary containing analysis results
    """
    # Step 1: Get raw ML predictions from ai/ layer
    from ai.layout.inference import run_layout_inference
    from ai.alt_text.inference import generate_alt_texts
    from ai.tables.inference import parse_tables
    
    raw_layout = await run_layout_inference(pdf_path)
    figures = extract_figures(raw_layout)
    raw_alt_texts = await generate_alt_texts(figures)
    tables = extract_tables(raw_layout)
    raw_tables = await parse_tables(tables)
    
    # Step 2: Process with business logic via processors/
    from processors.layout import analyze_reading_order
    from processors.wcag import check_wcag_compliance
    
    validated_layout = analyze_reading_order(raw_layout)
    wcag_issues = check_wcag_compliance(validated_layout)
    
    # Step 3: Return application-ready results
    return {
        "job_id": job_id,
        "pdf_path": pdf_path,
        "status": "completed",
        "layout": validated_layout,
        "reading_order": validated_layout["reading_order"],
        "alt_texts": raw_alt_texts,
        "tables": raw_tables,
        "wcag_issues": wcag_issues
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
    import asyncio
    results = asyncio.run(analyze_pdf(args.pdf_path, args.job_id))
    
    # Write results
    if args.output:
        import json
        Path(args.output).write_text(json.dumps(results, indent=2))
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### 6. SLURM Status Monitoring

#### hpc_runner/status.py

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
    // Proxy to .NET API running on Azure
    const res = await fetch(`${env.DOTNET_API_URL}/api/job/status/${jobId}`);
    return res;
  }
};
```

## End-to-End Flow

1. **User uploads PDF** → Cloudflare Worker
2. **Worker saves to R2**
3. **Worker sends Queue message**
4. **.NET API listener pulls job**
5. **.NET API generates presigned R2 URLs**
6. **.NET API submits SLURM job with URLs**
7. **SLURM job downloads PDF from R2**
8. **SLURM runs ML inference** → produces accessible PDF
9. **SLURM job uploads result to R2**
10. **.NET API updates database via D1 Worker**
11. **Frontend polls job status**
12. **User downloads accessible PDF from R2**

## Deployment Considerations

### React + Vite Frontend (Cloudflare Pages)

- **Deployment**: Static site build deployed to Cloudflare Pages via Azure Pipelines
- **Build**: `npm run build` produces static assets in `dist/`
- **Routing**: TanStack Router with file-based routing (no SSR required)
- **API Calls**: Direct to .NET API on Azure (CORS configured)
- **Environment Variables**: `.env` for API base URL
- **CDN**: Global edge deployment with automatic scaling

### .NET 10 Web API (Azure App Service)

- **Deployment**: Azure App Service (Linux) via Azure Pipelines
- **Runtime**: .NET 10.0.100+
- **Must be accessible from**: Cloudflare (public internet) and HPC cluster
- **Needs credentials for**:
  - Cloudflare Queues (API token)
  - R2 storage (API credentials)
  - D1 database API (Bearer token)
  - SLURM submission (SSH key and host access)
  - Metrics endpoint (optional, see [Metrics Deployment](METRICS_DEPLOYMENT.md))
- **Configuration**: `appsettings.json` and Azure App Settings for secrets

### HPC Runner

- Deployed to HPC shared filesystem
- Uses [uv](https://docs.astral.sh/uv/) for Python environment management
- Requires GPU nodes for inference
- **Requires internet access** to download/upload from R2
- Uses presigned URLs (no permanent R2 credentials needed on HPC nodes)

### Scaling

- **Cloudflare Pages**: Edge scaling automatic, globally distributed
- **Azure App Service**: Horizontally scalable with Azure scale-out rules
- **.NET API**: Can run multiple instances behind Azure Load Balancer
- **HPC**: Scales via SLURM job scheduling
- **R2**: Unlimited object storage with global replication

## Security

- **API Authentication**: Cloudflare Access or API tokens
- **HPC Access**: SSH keys, no passwords
- **R2 Credentials**: Presigned URLs (time-limited, single-use)
- **Database**: D1 API with Bearer token authentication
- **PDFs**: Presigned URLs for temporary access (1 hour expiry)

## Monitoring

- **Cloudflare Pages**: Build and deployment metrics, analytics dashboard
- **Azure App Service**: Application Insights for .NET API monitoring
- **.NET API**: Push-based metrics to Cloudflare Worker (see [Metrics Deployment](METRICS_DEPLOYMENT.md))
- **HPC**: SLURM metrics export script (see [Monitoring Setup](MONITORING_SETUP.md))
- **Prometheus/Grafana**: Pull metrics from Cloudflare Worker endpoint
- **SLURM**: `sacct`, `squeue` for job monitoring
- **R2**: Storage metrics via Cloudflare dashboard
- **Database**: D1 metrics via Cloudflare dashboard

For detailed setup instructions, see:

- [Monitoring Setup](MONITORING_SETUP.md) - Prometheus and Grafana configuration
- [Metrics Deployment](METRICS_DEPLOYMENT.md) - Cloudflare Worker metrics infrastructure

This architecture is production-ready, horizontally scalable, HPC-integrated, and Cloudflare-native.
