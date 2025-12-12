# System Design

This document covers both:

- the **current implementation** in this repository, and
- the **target system design** (planned) for the full AI-powered PDF accessibility pipeline.

See [ARCHITECTURE.md](./ARCHITECTURE.md) for repository structure and deployment details.
See [DEVELOPMENT.md](./DEVELOPMENT.md) for local development.
See [SECURITY_SETUP.md](./SECURITY_SETUP.md) for secrets and token-based auth.
See [MONITORING_SETUP.md](./MONITORING_SETUP.md) and [METRICS_DEPLOYMENT.md](./METRICS_DEPLOYMENT.md) for metrics.

## Current implementation (what exists today)

Implemented:

- `.NET` server endpoints:
  - `GET /api/job` (list jobs)
  - `GET /api/job/status/{jobId}` (job status)
- `workers/db-api` provides the D1-backed REST API used by the server.
- `workers/metrics-ingest` stores metric points in D1 and exposes `GET /metrics` for Prometheus.

In progress / planned (not end-to-end yet):

- Upload → R2 → Queue → orchestrator/SLURM → results flow.
- Complete the `hpc_runner` processing pipeline and accessible PDF reconstruction (currently scaffold/TODO).
- End-user authentication and UI for review/editing.

## Target Overview (planned)

The target system converts arbitrary PDFs into WCAG 2.1/UA-compliant accessible PDFs through a multi-stage AI-powered pipeline:

1. **PDF Analysis** - Parse structure, detect type (digital/scanned/hybrid)
2. **AI Inference** - Layout detection, role classification, content understanding
3. **Accessibility Enhancement** - Alt-text generation, table structuring, reading order
4. **WCAG Enforcement** - Rule-based validation and repair
5. **PDF Reconstruction** - Build properly tagged accessible PDF

## Processing Pipeline

### Stage 1: PDF Ingestion & Classification

```mermaid
flowchart TD
    A[PDF Upload] --> B[Type Detection]
    B --> C[Preprocessing]
    B --> D{PDF Type}
    D -->|digital| E[Skip OCR]
    D -->|scanned| F[Run OCR]
    D -->|hybrid| F
    E --> G[Continue to Stage 2]
    F --> G
```

**Components:**

- PDF parser ([PyMuPDF](https://pymupdf.readthedocs.io/) or [pdfplumber](https://github.com/jsvine/pdfplumber))
- Type classifier (heuristic-based)
- OCR engine ([Tesseract](https://github.com/tesseract-ocr/tesseract), [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR), or Azure Vision)

### Stage 2: Layout & Structure Analysis

```mermaid
flowchart TD
    A[PDF Pages] --> B[Layout Model<br/>LayoutLMv3]
    B --> C[Structured JSON]
    C --> D[Element Classification]
    D --> E[headings]
    D --> F[paragraphs]
    D --> G[figures]
    D --> H[tables]
    D --> I[lists]
    E --> J[Bounding boxes + metadata]
    F --> J
    G --> J
    H --> J
    I --> J
```

**Primary Model: [LayoutLMv3](https://huggingface.co/docs/transformers/model_doc/layoutlmv3) (Microsoft)**

- Vision + text + spatial understanding
- Designed for document structure
- Fine-tune for:
  - Heading hierarchy (H1/H2/H3/H4/H5/H6)
  - Role classification (paragraph, caption, footnote, header, footer)
  - Figure/table detection
  - Decorative element identification
  - List detection and nesting

**Alternative: [Donut](https://huggingface.co/docs/transformers/model_doc/donut) (Naver Clova)**

- OCR-free document understanding
- Good for forms and structured documents
- Use as inference module (no fine-tuning needed)

**Why Not [BERT](https://huggingface.co/docs/transformers/model_doc/bert)?**
[BERT](https://huggingface.co/docs/transformers/model_doc/bert) lacks spatial awareness—critical for understanding document layout and reading order.

### Stage 3: Reading Order Determination

```mermaid
flowchart LR
    A[Detected Elements] --> B[Reading Order Model<br/>LayoutLMv3 fine-tuned]
    B --> C[Ordered Sequence]
    C --> D[element_1, element_2, element_3, ...]
```

**Approach:** Fine-tune LayoutLMv3 to predict reading order

**Training data format:**

```json
{
  "page_id": "doc1_p1",
  "elements": [
    {"id": "e1", "bbox": [x, y, w, h], "text": "...", "style": {...}},
    {"id": "e2", "bbox": [x, y, w, h], "text": "...", "style": {...}}
  ],
  "reading_order": ["e1", "e2", "e3", ...]
}
```

**Loss function:** Penalize incorrect sequencing and "jumps" (e.g., left column → right column → back to left)

### Stage 4: Content Understanding

#### A. Alt-Text Generation

```mermaid
flowchart LR
    A[Figure/Image] --> B[Vision-Language Model<br/>BLIP-2 / LLaVA]
    B --> C[Descriptive Alt-Text]
    C --> D[factual, concise,<br/>objective description]
```

**Best Models:**

- **[BLIP-2](https://huggingface.co/docs/transformers/model_doc/blip-2)** - Strong captioning, factual descriptions
- **[LLaVA](https://github.com/haotian-liu/LLaVA)-1.6** - High-quality vision understanding
- **[MiniGPT-5](https://github.com/eric-ai-lab/MiniGPT-5)** - Efficient, accurate captions

**Fine-tuning strategy:**

```python
# Training pairs
{
  "image": figure_image,
  "caption": "Bar chart showing revenue growth from 2020 to 2024",
  "negative": "A colorful chart with bars"  # penalize vague descriptions
}
```

**Fine-tune on:**

- Charts (line, bar, scatter, pie)
- Scientific diagrams
- UI screenshots
- Educational materials
- Figure + caption pairs from academic papers

**Training objective:** Minimize hallucination, maximize factual accuracy

#### B. Table Structure Recognition

```mermaid
flowchart LR
    A[Table Region] --> B[Table Model<br/>TAPAS / TaBERT]
    B --> C[Structured Data]
    C --> D{Output Format}
    D --> E[HTML]
    D --> F[JSON]
    D --> G[CSV]
```

**Vision-based approaches:**

- [TableNet](https://github.com/asagar60/TableNet-pytorch)
- [CascadeTabNet](https://github.com/DevashishPrasad/CascadeTabNet)

**Transformer-based approaches:**

- **[TAPAS](https://huggingface.co/docs/transformers/model_doc/tapas) (Google)** - Table parsing to JSON
- **[TaBERT](https://github.com/facebookresearch/TaBERT) (Facebook)** - Table understanding

**Fine-tuning data:**

```json
{
  "table_image": "...",
  "structure": {
    "headers": ["Year", "Revenue", "Profit"],
    "rows": [
      ["2020", "$100M", "$20M"],
      ["2021", "$150M", "$35M"]
    ],
    "header_scope": "col"
  }
}
```

### Stage 5: WCAG Rule Enforcement

```mermaid
flowchart LR
    A[Structured Content] --> B[Rule Engine<br/>WCAG Validator]
    B --> C[Accessibility Fixes]
    C --> D[repair headings]
    C --> E[add structure]
    C --> F[validate]
```

**Deterministic rules:**

- Heading hierarchy validation (no skipped levels)
- List structure enforcement (proper nesting)
- Language attribute on document
- Title metadata
- Alt-text presence on all images
- Table headers (TH vs TD)
- Proper semantic tags
- Color contrast validation (if applicable)

**Implementation:**

```csharp
// Conceptual - WCAG validation happens in hpc_runner (Python)
// .NET API focuses on orchestration, not rule validation
public class WCAGValidator
{
    public bool ValidateHeadingHierarchy(List<Element> elements)
    {
        // Ensure no skipped heading levels (H1 → H3 invalid)
        return true;
    }
    
    public void EnforceListStructure(List<Element> elements)
    {
        // Wrap list items in proper <ul>/<ol> tags
    }
    
    public bool ValidateAltText(List<Image> images)
    {
        // Check all images have alt text or marked decorative
        return true;
    }
    
    public StructureTree BuildStructureTree(List<Element> elements)
    {
        // Create proper tagged PDF structure tree
        return new StructureTree();
    }
}
```

### Stage 6: Accessible PDF Construction

```mermaid
flowchart LR
    A[Validated Content] --> B[PDF Builder<br/>PyMuPDF / iText]
    B --> C[Tagged PDF]
    C --> D[WCAG 2.1 compliant output]
```

**Tools:**

- **[PyMuPDF](https://pymupdf.readthedocs.io/)** - PDF manipulation
- **[iText](https://itextpdf.com/) (Java)** - Commercial-grade PDF tagging
- **[pdfplumber](https://github.com/jsvine/pdfplumber)** - Text extraction for verification

**Output includes:**

- Structure tree with proper tags
- Alt-text embedded in PDF
- Reading order metadata
- Language specification
- Document title and metadata
- Logical structure markers

## AI Model Selection Matrix

| Task | Best Model | Fine-Tune? | Priority |
|------|-----------|------------|----------|
| Layout parsing | [LayoutLMv3](https://huggingface.co/docs/transformers/model_doc/layoutlmv3), [Donut](https://huggingface.co/docs/transformers/model_doc/donut) | Yes | Critical |
| Reading order | [LayoutLMv3](https://huggingface.co/docs/transformers/model_doc/layoutlmv3) | Yes | Critical |
| Alt-text generation | [BLIP-2](https://huggingface.co/docs/transformers/model_doc/blip-2), [LLaVA](https://github.com/haotian-liu/LLaVA) | Yes | High |
| Table structure | [TAPAS](https://huggingface.co/docs/transformers/model_doc/tapas), [TaBERT](https://github.com/facebookresearch/TaBERT) | Yes | High |
| OCR | [Tesseract](https://github.com/tesseract-ocr/tesseract), Google Vision | No | Medium |
| Page understanding | GPT-4 Vision, [Donut](https://huggingface.co/docs/transformers/model_doc/donut) | No | Low |

## Fine-Tuning Priorities

### 1. Heading Classification & Hierarchy (Critical)

**Model:** [LayoutLMv3](https://huggingface.co/docs/transformers/model_doc/layoutlmv3)

**Input:** Text + bounding box + style features (font size, weight, indentation)

**Output:** Role classification (H1/H2/H3/H4/H5/H6, body, caption, footnote, list item)

**Dataset:** 10K+ labeled document pages with annotated heading levels

### 2. Reading Order Prediction (Critical)

**Model:** [LayoutLMv3](https://huggingface.co/docs/transformers/model_doc/layoutlmv3) fine-tuned for sequence prediction

**Input:** Set of document elements with positions

**Output:** Ordered sequence of element IDs

**Loss:** Sequence loss with penalty for incorrect jumps (multi-column handling)

### 3. Alt-Text Generation (High Priority)

**Model:** [BLIP-2](https://huggingface.co/docs/transformers/model_doc/blip-2) or [LLaVA](https://github.com/haotian-liu/LLaVA)

**Training set:**

- 50K+ chart images with objective descriptions
- Scientific diagrams with captions
- UI elements with functional descriptions
- Negative examples to penalize hallucination

**Validation:** Human evaluation + ROUGE/BLEU against expert descriptions

### 4. Table Structure Recognition (High Priority)

**Model:** [TAPAS](https://huggingface.co/docs/transformers/model_doc/tapas)

**Training set:**

- PDF tables → HTML/JSON conversions
- 20K+ tables with header/data cell annotations
- Complex tables (merged cells, multi-level headers)

**Output format:** Structured JSON with semantic roles

## Backend Service Architecture

### Two-Layer Orchestration

**Layer 1: .NET API Server (current + planned)**

Current responsibilities in this repo:

- Provide job APIs for the browser client (`GET /api/job`, `GET /api/job/status/{jobId}`).
- Call `workers/db-api` for job metadata (D1) over HTTP + bearer token.
- Optionally push operational metrics to `workers/metrics-ingest` (if `METRICS_TOKEN` is configured).

Planned responsibilities (not wired end-to-end yet):

- Pull jobs from [Cloudflare Queue](https://developers.cloudflare.com/queues/).
- Download PDFs from [R2](https://developers.cloudflare.com/r2/).
- Submit [SLURM](https://slurm.schedmd.com/) jobs to HPC.
- Monitor job status, upload results to R2, and update the database.

**Layer 2: HPC Runner (ML pipeline on GPU) (scaffold + planned)**

The `hpc_runner/` package contains the intended structure of the ML pipeline (`ai/` and `processors/`). Today, `hpc_runner/runner.py` is still largely a placeholder, but the planned responsibilities are:

- Load GPU models ([LayoutLMv3](https://huggingface.co/docs/transformers/model_doc/layoutlmv3), [BLIP-2](https://huggingface.co/docs/transformers/model_doc/blip-2), [TAPAS](https://huggingface.co/docs/transformers/model_doc/tapas)).
- Run layout detection, reading order, alt-text generation, and table parsing.
- Apply WCAG rules and construct a tagged (accessible) PDF.

### .NET 10 Web API Job Pipeline (Conceptual)

```csharp
// Conceptual (planned). Current server implementation is limited to job status/list + db-api integration.
// Heavy processing happens in hpc_runner (Python)
public async Task<(string outputPdf, Report report)> ProcessPdfJobAsync(
    Guid jobId,
    string pdfPath)
{
    // Orchestrate Cloudflare ↔ HPC ↔ R2 flow
    
    // 1. Generate presigned R2 URLs
    var inputUrl = GeneratePresignedUrl(pdfPath, "get", 3600);
    var outputUrl = GeneratePresignedUrl($"outputs/{jobId}/accessible.pdf", "put", 3600);
    
    // 2. Submit to HPC for heavy ML processing
    var slurmId = await SubmitSlurmJobAsync(jobId, inputUrl, outputUrl);
    
    // 3. Monitor HPC job
    await MonitorSlurmJobAsync(slurmId);
    
    // 4. Update database status
    await _dbClient.UpdateJobAsync(jobId, status: JobStatus.Completed, resultsUrl: null);
    
    // 5. Generate report (from HPC results)
    var report = await GenerateComplianceReportAsync(jobId);
    
    return (outputUrl, report);
}
```

### HPC ML Pipeline (GPU Processing)

```python
# hpc_runner/runner.py
def analyze_pdf(pdf_path: str, job_id: str) -> dict:
    """Heavy ML processing on GPU nodes"""
    
    # 1. Layout detection (LayoutLMv3)
    from ai.layout.inference import run_layout_inference
    layout = await run_layout_inference(pdf_path)
    
    # 2. Reading order prediction
    reading_order = predict_reading_order(layout)
    
    # 3. Alt-text generation (BLIP-2/LLaVA)
    from ai.alt_text.inference import generate_alt_texts
    figures = extract_figures(layout)
    alt_texts = await generate_alt_texts(figures)
    
    # 4. Table parsing (TAPAS)
    from ai.tables.inference import parse_tables
    tables = extract_tables(layout)
    table_data = await parse_tables(tables)
    
    return {
        "layout": layout,
        "reading_order": reading_order,
        "alt_texts": alt_texts,
        "tables": table_data
    }
```

### Service Layer Organization (.NET API Server)

Runs on [.NET Web API](https://learn.microsoft.com/en-us/aspnet/core/web-api/). Today it primarily exposes job APIs and calls `workers/db-api`; orchestration of Cloudflare ↔ HPC ↔ R2 is planned:

```
server/Services/
├── DatabaseApiClient.cs   # HTTP client for Cloudflare D1
├── MetricsClient.cs       # Push metrics to worker
└── (Future: SlurmClient, R2Client, etc.)

server/Controllers/
└── JobController.cs       # Job status endpoints
```

### AI Inference Layer (HPC GPU Nodes)

Intended to run on HPC GPU nodes via [SLURM](https://slurm.schedmd.com/) (planned), performs heavy ML:

```
hpc_runner/
├── runner.py              # Main SLURM entry point (orchestrates ML pipeline)
├── ai/                    # Low-level ML model wrappers
│   ├── layout/
│   │   ├── model.py       # LayoutLMv3 wrapper
│   │   └── inference.py   # Batch inference
│   ├── alt_text/
│   │   ├── model.py       # BLIP-2/LLaVA wrapper
│   │   └── inference.py   # Image captioning
│   └── tables/
│       ├── model.py       # TAPAS wrapper
│       └── inference.py   # Table parsing
└── processors/            # High-level business logic
    ├── layout.py          # Calls ai/layout, adds WCAG validation
    ├── alttext.py         # Calls ai/alt_text, ensures compliance
    ├── ocr.py             # OCR orchestration (external tools)
    ├── wcag.py            # Rule-based validation
    └── tagging.py         # PDF manipulation
```

**Key Distinction:**

- `.NET API server/Services/` = Lightweight orchestration, no heavy ML
- `hpc_runner/` = Heavy GPU-based ML processing

#### HPC Runner Internal Architecture: ai/ vs processors/

The `hpc_runner/` has a two-layer architecture to separate ML concerns from business logic:

**Layer 1: `ai/` - ML Model Layer (Low-Level)**

Direct wrappers around heavy ML models. This is the closest to the metal:

- **Purpose:** Load models, run inference, return raw predictions
- **Responsibilities:**
  - Model loading ([LayoutLMv3](https://huggingface.co/docs/transformers/model_doc/layoutlmv3), [BLIP-2](https://huggingface.co/docs/transformers/model_doc/blip-2), [TAPAS](https://huggingface.co/docs/transformers/model_doc/tapas))
  - GPU memory management
  - Forward passes
  - Batch processing optimization
  - Return raw model outputs (tensors, logits, predictions)

- **Example:**

  ```python
  # ai/layout/model.py
  class LayoutModel:
      def predict_structure(self, pdf_page):
          # Load LayoutLMv3
          # Run inference
          # Return raw predictions (bboxes, labels, confidences)
  
  # ai/layout/inference.py
  async def run_layout_inference(pdf_path):
      model = LayoutModel()
      # Batch all pages, run inference, return raw results
  ```

**Layer 2: `processors/` - Business Logic Layer (High-Level)**

Application logic that **uses** the AI models to accomplish tasks:

- **Purpose:** Add business logic, validation, WCAG compliance
- **Responsibilities:**
  - Call `ai/` layer for ML predictions
  - Validate predictions
  - Apply WCAG-specific rules
  - Clean up and structure results
  - Return application-ready outputs

- **Example:**

  ```python
  # processors/layout.py
  from ai.layout.inference import run_layout_inference
  
  def detect_layout(pdf_path):
      # 1. Get raw ML predictions
      raw_layout = await run_layout_inference(pdf_path)
      
      # 2. Add business logic
      validated = validate_predictions(raw_layout)
      heading_hierarchy = check_heading_hierarchy(validated)
      
      # 3. Add WCAG metadata
      wcag_compliant = add_wcag_metadata(heading_hierarchy)
      
      # 4. Return application-ready structure
      return wcag_compliant
  ```

**Which processors use ai/?**

| Processor | Uses ai/ layer? | Notes |
|-----------|----------------|-------|
| `processors/layout.py` | ✅ Yes | Calls `ai/layout/` for [LayoutLMv3](https://huggingface.co/docs/transformers/model_doc/layoutlmv3) predictions |
| `processors/alttext.py` | ✅ Yes | Calls `ai/alt_text/` for [BLIP-2](https://huggingface.co/docs/transformers/model_doc/blip-2)/[LLaVA](https://github.com/haotian-liu/LLaVA) captions |
| `processors/ocr.py` | ❌ No | Calls external OCR engines ([Tesseract](https://github.com/tesseract-ocr/tesseract), [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)) |
| `processors/wcag.py` | ❌ No | Rule-based validation, no ML |
| `processors/tagging.py` | ❌ No | PDF manipulation with [PyMuPDF](https://pymupdf.readthedocs.io/)/[iText](https://itextpdf.com/) |

**Flow in runner.py:**

```python
# hpc_runner/runner.py
def analyze_pdf(pdf_path, job_id):
    # Step 1: Get raw ML predictions from ai/ layer
    from ai.layout.inference import run_layout_inference
    from ai.alt_text.inference import generate_alt_texts
    from ai.tables.inference import parse_tables
    
    raw_layout = await run_layout_inference(pdf_path)
    raw_alt_texts = await generate_alt_texts(figures)
    raw_tables = await parse_tables(tables)
    
    # Step 2: Process with business logic via processors/
    from processors.layout import analyze_reading_order
    from processors.wcag import check_wcag_compliance
    
    validated_layout = analyze_reading_order(raw_layout)
    wcag_issues = check_wcag_compliance(validated_layout)
    
    # Step 3: Return application-ready results
    return {
        "layout": validated_layout,
        "alt_texts": raw_alt_texts,  # Already validated by processors/alttext
        "tables": raw_tables,
        "wcag_issues": wcag_issues,
    }
```

This separation keeps ML model concerns separate from business logic and makes the codebase more maintainable.

### Separation of concerns: server vs hpc_runner

The server and `hpc_runner/` operate in the same problem domain (OCR, WCAG, tagged PDFs), but they run in different environments and have different responsibilities.

#### Runtime environments

| Layer | Where | Resources | Purpose |
|-------|-------|-----------|---------|
| `server/` | .NET Web API (VM/container) | CPU only, lightweight | API for the client + orchestration glue (planned) |
| `hpc_runner/` | HPC GPU nodes (via SLURM, planned) | GPU/CPU, high memory | Compute-heavy processing and accessible PDF reconstruction |

#### Notes on current repo state

- Today there is no separate OCR/WCAG/PDF processing implementation in `server/`; those concerns live under `hpc_runner/processors/*` (still incomplete/TODO).
- The server currently focuses on job metadata via `workers/db-api` and (optionally) pushing metrics.

#### Complete processing flow (planned)

```mermaid
flowchart TD
    subgraph C1["Controller (Lightweight)"]
        A1["1. Receive job from Queue"]
        A2["2. Generate presigned R2 URLs"]
        A3["3. Submit SLURM job with URLs"]
        A1 --> A2 --> A3
    end
    
    A3 --> B0
    
    subgraph HPC["HPC GPU Nodes (Heavy ML)"]
        B0["4. Download PDF from R2"]
        B1["5. processors/ocr.py<br/><i>Runs Tesseract</i>"]
        B2["6. ai/layout inference<br/><i>LayoutLMv3 on GPU</i>"]
        B3["7. ai/alt_text inference<br/><i>BLIP-2 on GPU</i>"]
        B4["8. processors/wcag<br/><i>Validates predictions</i>"]
        B5["9. processors/tagging<br/><i>Adds semantic tags</i>"]
        B6["10. Upload result to R2"]
        B0 --> B1 --> B2 --> B3 --> B4 --> B5 --> B6
    end
    
    B6 --> C0
    
    subgraph C2["Controller (Lightweight)"]
        C0["11. Update database status"]
    end
    
    style C1 fill:#90ee90,stroke:#228b22,stroke-width:3px,color:#000
    style HPC fill:#ff9999,stroke:#cc0000,stroke-width:3px,color:#000
    style C2 fill:#90ee90,stroke:#228b22,stroke-width:3px,color:#000
```

**Summary:** This diagram describes the target end-to-end flow; it is not fully wired up yet in this repository.

## Frontend Features

### Authentication

Current:

- No end-user authentication yet (client uses CORS to call the server).
- Internal service-to-service calls use bearer tokens (workers).

Planned:

- UC Davis campus account login via EntraID (Microsoft Azure AD).

### Pages / routes

Current routes in `client/src/routes/`:

- `/` - Home
- `/upload` - Upload page (UI stub; not wired end-to-end yet)
- `/jobs` - Job list
- `/jobs/:jobId` - Job details + status polling

Planned pages:

- `/documents/[id]` - Document dashboard
- `/documents/[id]/review` - Accessibility review editor
- `/reports/[id]` - Compliance report viewer

### Key Components (planned)

#### 1. PDF Preview with Structure Overlay

```typescript
// components/PDFViewer.tsx
- React-pdf renderer
- Structure tree visualization
- Element highlighting on hover
- Bounding box overlays
```

#### 2. Structure Tree Inspector

```typescript
// components/StructureTree.tsx
- Hierarchical tag view
- Drag-to-reorder functionality
- Tag type editor
- Reading order visualization
```

#### 3. Alt-Text Editor

```typescript
// components/AltTextEditor.tsx
- AI-generated suggestions
- Manual override
- Mark as decorative
- Context preview
```

#### 4. Reading Order Editor

```typescript
// components/ReadingOrderEditor.tsx
- Visual element sequence
- Drag-and-drop reordering
- Multi-column flow visualization
- Validation warnings
```

#### 5. WCAG Error List

```typescript
// components/WCAGErrors.tsx
- Categorized by severity (A, AA, AAA)
- Click to navigate to issue
- Auto-fix suggestions
- Export compliance report
```

## Database Architecture

### D1 Database with API Worker

The system uses [Cloudflare D1](https://developers.cloudflare.com/d1/) (SQLite) accessed via a dedicated API Worker (`workers/db-api`). .NET 10 Web API controller communicates with the database through HTTP REST API, not direct connections.

**Benefits:**

- No database server to manage
- Cloudflare free tier (5GB storage, 5M reads/day)
- Consistent with metrics infrastructure
- Token-based authentication
- API-based separation of concerns

### Core Tables (MVP)

#### Jobs Table

```sql
CREATE TABLE jobs (
    id TEXT PRIMARY KEY,
    slurm_id TEXT,
    status TEXT NOT NULL DEFAULT 'submitted',
    r2_key TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    results_url TEXT,
    user_id TEXT
);
```

**Indexes:** `slurm_id`, `status`, `r2_key`, `user_id`, `created_at`

#### Users Table

```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    organization TEXT,
    created_at INTEGER NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1
);
```

**Indexes:** `email`

#### Processing Metrics Table

```sql
CREATE TABLE processing_metrics (
    id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    processing_time_seconds REAL,
    pdf_pages INTEGER,
    pdf_size_bytes INTEGER,
    success INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    created_at INTEGER NOT NULL,
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);
```

**Indexes:** `job_id`, `created_at`

### Future Tables (Post-MVP)

For detailed structure analysis and editing features:

#### Documents Table

```sql
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    job_id TEXT,
    title TEXT,
    page_count INTEGER,
    pdf_type TEXT,  -- digital, scanned, hybrid
    language TEXT,
    created_at INTEGER,
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);
```

#### Elements Table

```sql
CREATE TABLE elements (
    id TEXT PRIMARY KEY,
    document_id TEXT,
    page_number INTEGER,
    element_type TEXT,  -- heading, paragraph, figure, table, list
    bbox TEXT,  -- JSON: {x, y, width, height}
    text TEXT,
    reading_order INTEGER,
    ai_confidence REAL,
    human_override INTEGER,
    created_at INTEGER,
    FOREIGN KEY (document_id) REFERENCES documents(id)
);
```

#### Alt-Texts Table

```sql
CREATE TABLE alt_texts (
    id TEXT PRIMARY KEY,
    element_id TEXT,
    alt_text TEXT,
    ai_generated TEXT,
    human_edited INTEGER,
    is_decorative INTEGER,
    created_at INTEGER,
    updated_at INTEGER,
    FOREIGN KEY (element_id) REFERENCES elements(id)
);
```

### Database Access Pattern

.NET API → HTTP API → D1 Worker → D1 Database

```csharp
// server/Services/DatabaseApiClient.cs (actual implementation)
var dbClient = new DatabaseApiClient(httpClient, config, logger);

var job = await dbClient.CreateJobAsync(
    jobId: Guid.NewGuid(),
    r2Key: "uploads/document.pdf",
    slurmId: null,
    userId: null,
    cancellationToken: default
);

// Returns Job object with Status automatically set to "Submitted"
```

See `workers/db-api/README.md` for API documentation.

## Storage Strategy

### Object Storage (R2/S3)

Planned key layout (example):

```
/uploads/{job_id}/original.pdf      # Original upload
/processing/{job_id}/ocr.json       # OCR results
/processing/{job_id}/layout.json    # Layout analysis
/processing/{job_id}/figures/*.png  # Extracted figures
/outputs/{job_id}/accessible.pdf    # Final output
/reports/{job_id}/compliance.json   # WCAG report
```

Current prototype note:

- `workers/api/upload.ts` writes uploads to `raw/{jobId}.pdf` and publishes `{ jobId, r2Key }` to a queue.

### Optional Box Integration

**Future Feature:** Automatic upload of results to user's Box folder

- OAuth integration with Box API
- User grants permission to write to their Box account
- Results automatically saved to `/Accessible PDFs/{job_id}/`
- User maintains full control via Box sharing and permissions
- Falls back to R2 download if Box integration not enabled

## Model Training Pipeline

This section is an outline / example. The `scripts/`, `data/`, and `models/` directories referenced below are not currently tracked in this repository.

### 1. Dataset Preparation

```bash
# scripts/prepare_training_data.py
python scripts/prepare_training_data.py \
  --task layout \
  --input-dir data/raw \
  --output-dir data/processed/layout \
  --format layoutlmv3
```

### 2. Model Fine-Tuning

```bash
# scripts/train_layout.py
python scripts/train_layout.py \
  --model microsoft/layoutlmv3-base \
  --train-data data/processed/layout/train.json \
  --val-data data/processed/layout/val.json \
  --epochs 10 \
  --batch-size 16 \
  --output models/layout-ft
```

### 3. Model Evaluation

```bash
# scripts/benchmark.py
python scripts/benchmark.py \
  --model models/layout-ft \
  --test-data data/processed/layout/test.json \
  --metrics accuracy,f1,precision,recall
```

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Job processing time | < 2 min per page | On GPU worker |
| Layout accuracy | > 95% | F1 score on test set |
| Alt-text quality | > 4.0/5.0 | Human evaluation |
| Reading order accuracy | > 98% | Correct sequence |
| WCAG compliance | 100% | AA level minimum |
| API response time | < 100ms | Status checks |

## Security & Privacy

Current (implemented):

- No end-user authentication yet.
- `workers/db-api` is protected by a bearer token (`DB_AUTH_TOKEN` on the worker; `DB_API_TOKEN` on the server).
- `workers/metrics-ingest` requires a bearer token for `POST /ingest` (`METRICS_AUTH_TOKEN` on the worker; server uses `METRICS_TOKEN`), while `GET /metrics` is public for Prometheus scraping.
- Secrets are provided via environment variables / Worker secrets (not committed).

Planned (target):

- **Authentication**: UC Davis campus account login via EntraID/Azure AD.
- **Authorization**: Users can only access their own jobs and results.
- **PDF sanitization**: Remove embedded scripts, forms, JavaScript.
- **Content isolation**: Each job in a separate container/job allocation.
- **PII detection**: Flag sensitive content (SSN, credit cards).
- **Access control**: Signed URLs with expiration for artifacts.
- **Audit logging**: All AI decisions logged for review.
- **Box integration**: Optional, user-controlled OAuth with write permissions.

## Future Enhancements

### Phase 2

- Math equation accessibility (MathML)
- Multi-language support
- Batch processing API
- Webhooks for job completion

### Phase 3

- Human-in-the-loop review workflow
- Active learning from corrections
- Custom model fine-tuning per organization
- PDF form accessibility

### Phase 4

- Real-time collaborative editing
- Browser extension for instant checking
- PowerPoint/Word conversion support
- Mobile app for on-device processing
