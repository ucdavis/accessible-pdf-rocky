# System Design

This document describes the AI-powered PDF accessibility conversion pipeline, model selection, and processing architecture.

See [ARCHITECTURE.md](./ARCHITECTURE.md) for infrastructure and deployment details.

## Overview

The system converts arbitrary PDFs into WCAG 2.1/UA-compliant accessible PDFs through a multi-stage AI-powered pipeline:

1. **PDF Analysis** - Parse structure, detect type (digital/scanned/hybrid)
2. **AI Inference** - Layout detection, role classification, content understanding
3. **Accessibility Enhancement** - Alt-text generation, table structuring, reading order
4. **WCAG Enforcement** - Rule-based validation and repair
5. **PDF Reconstruction** - Build properly tagged accessible PDF

## Processing Pipeline

### Stage 1: PDF Ingestion & Classification

```
PDF Upload → Type Detection → Preprocessing
                ↓
         [digital | scanned | hybrid]
                ↓
         OCR if needed
```

**Components:**

- PDF parser (PyMuPDF or pdfplumber)
- Type classifier (heuristic-based)
- OCR engine (Tesseract, PaddleOCR, or Azure Vision)

### Stage 2: Layout & Structure Analysis

```
PDF Pages → Layout Model → Structured JSON
              ↓
    [headings, paragraphs, figures, tables, lists]
              ↓
         Bounding boxes + metadata
```

**Primary Model: LayoutLMv3 (Microsoft)**

- Vision + text + spatial understanding
- Designed for document structure
- Fine-tune for:
  - Heading hierarchy (H1/H2/H3/H4/H5/H6)
  - Role classification (paragraph, caption, footnote, header, footer)
  - Figure/table detection
  - Decorative element identification
  - List detection and nesting

**Alternative: Donut (Naver Clova)**

- OCR-free document understanding
- Good for forms and structured documents
- Use as inference module (no fine-tuning needed)

**Why Not BERT?**
BERT lacks spatial awareness—critical for understanding document layout and reading order.

### Stage 3: Reading Order Determination

```
Detected Elements → Reading Order Model → Ordered Sequence
                         ↓
              [element_1, element_2, ...]
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

```
Figure/Image → Vision-Language Model → Descriptive Alt-Text
                       ↓
         [factual, concise, objective description]
```

**Best Models:**

- **BLIP-2** - Strong captioning, factual descriptions
- **LLaVA-1.6** - High-quality vision understanding
- **MiniGPT-5** - Efficient, accurate captions

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

```
Table Region → Table Model → Structured Data
                   ↓
            [HTML | JSON | CSV]
```

**Vision-based approaches:**

- TableNet
- CascadeTabNet

**Transformer-based approaches:**

- **TAPAS (Google)** - Table parsing to JSON
- **TaBERT (Facebook)** - Table understanding

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

```
Structured Content → Rule Engine → Accessibility Fixes
                         ↓
         [repair headings, add structure, validate]
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

```python
# services/wcag_engine.py
class WCAGValidator:
    def validate_heading_hierarchy(self, elements):
        """Ensure no skipped heading levels (H1 → H3 invalid)"""
        pass
    
    def enforce_list_structure(self, elements):
        """Wrap list items in proper <ul>/<ol> tags"""
        pass
    
    def validate_alt_text(self, images):
        """Check all images have alt text or marked decorative"""
        pass
    
    def build_structure_tree(self, elements):
        """Create proper tagged PDF structure tree"""
        pass
```

### Stage 6: Accessible PDF Construction

```
Validated Content → PDF Builder → Tagged PDF
                         ↓
              [WCAG 2.1 compliant output]
```

**Tools:**

- **PyMuPDF** - PDF manipulation
- **iText (Java)** - Commercial-grade PDF tagging
- **pdfplumber** - Text extraction for verification

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
| Layout parsing | LayoutLMv3, Donut | Yes | Critical |
| Reading order | LayoutLMv3 | Yes | Critical |
| Alt-text generation | BLIP-2, LLaVA | Yes | High |
| Table structure | TAPAS, TaBERT | Yes | High |
| OCR | Tesseract, Google Vision | No | Medium |
| Page understanding | GPT-4 Vision, Donut | No | Low |

## Fine-Tuning Priorities

### 1. Heading Classification & Hierarchy (Critical)

**Model:** LayoutLMv3

**Input:** Text + bounding box + style features (font size, weight, indentation)

**Output:** Role classification (H1/H2/H3/H4/H5/H6, body, caption, footnote, list item)

**Dataset:** 10K+ labeled document pages with annotated heading levels

### 2. Reading Order Prediction (Critical)

**Model:** LayoutLMv3 fine-tuned for sequence prediction

**Input:** Set of document elements with positions

**Output:** Ordered sequence of element IDs

**Loss:** Sequence loss with penalty for incorrect jumps (multi-column handling)

### 3. Alt-Text Generation (High Priority)

**Model:** BLIP-2 or LLaVA

**Training set:**

- 50K+ chart images with objective descriptions
- Scientific diagrams with captions
- UI elements with functional descriptions
- Negative examples to penalize hallucination

**Validation:** Human evaluation + ROUGE/BLEU against expert descriptions

### 4. Table Structure Recognition (High Priority)

**Model:** TAPAS

**Training set:**

- PDF tables → HTML/JSON conversions
- 20K+ tables with header/data cell annotations
- Complex tables (merged cells, multi-level headers)

**Output format:** Structured JSON with semantic roles

## Backend Service Architecture

### FastAPI Job Pipeline

```python
# services/job_runner.py
async def process_pdf_job(job_id: str, pdf_path: str):
    """Main async job processing pipeline"""
    
    # 1. Upload & classify
    pdf_type = detect_pdf_type(pdf_path)
    
    # 2. OCR if needed
    if pdf_type in ["scanned", "hybrid"]:
        ocr_result = await run_ocr(pdf_path)
    
    # 3. Layout analysis
    layout = await run_layout_model(pdf_path)
    
    # 4. Reading order
    reading_order = await predict_reading_order(layout)
    
    # 5. Alt-text for figures
    figures = extract_figures(layout)
    alt_texts = await generate_alt_texts(figures)
    
    # 6. Table structure
    tables = extract_tables(layout)
    table_data = await parse_tables(tables)
    
    # 7. WCAG validation & repair
    validated = wcag_engine.validate_and_repair(
        layout, reading_order, alt_texts, table_data
    )
    
    # 8. Build accessible PDF
    output_pdf = build_tagged_pdf(validated, pdf_path)
    
    # 9. Generate report
    report = generate_compliance_report(validated)
    
    return output_pdf, report
```

### Service Layer Organization

```
backend/services/
├── pdf_parser.py          # PyMuPDF/pdfplumber extraction
├── pdf_normalizer.py      # Type detection, preprocessing
├── ocr_engine.py          # Tesseract/Azure OCR
├── wcag_engine.py         # Rule-based validation
├── pdf_builder.py         # Tagged PDF construction
└── job_runner.py          # Orchestration
```

### AI Inference Layer

```
backend/ai/
├── layout/
│   ├── model.py           # LayoutLMv3 wrapper
│   └── inference.py       # Batch inference
├── alt_text/
│   ├── model.py           # BLIP-2/LLaVA wrapper
│   └── inference.py       # Image captioning
├── tables/
│   ├── model.py           # TAPAS wrapper
│   └── inference.py       # Table parsing
└── prompts/
    └── vision_prompts.py  # GPT-4V system prompts
```

## Frontend Features

### Pages

- `/upload` - PDF upload with drag-and-drop
- `/documents/[id]` - Document dashboard
- `/documents/[id]/review` - Accessibility review editor
- `/reports/[id]` - Compliance report viewer

### Key Components

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

## Database Schema

### Jobs Table

```sql
CREATE TABLE jobs (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    status VARCHAR(50),  -- pending, processing, completed, failed
    pdf_key VARCHAR(255),
    output_key VARCHAR(255),
    created_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);
```

### Documents Table

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    job_id UUID REFERENCES jobs(id),
    title VARCHAR(255),
    page_count INTEGER,
    pdf_type VARCHAR(50),  -- digital, scanned, hybrid
    language VARCHAR(10),
    created_at TIMESTAMP
);
```

### Elements Table

```sql
CREATE TABLE elements (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(id),
    page_number INTEGER,
    element_type VARCHAR(50),  -- heading, paragraph, figure, table, list
    bbox JSONB,  -- {x, y, width, height}
    text TEXT,
    reading_order INTEGER,
    ai_confidence FLOAT,
    human_override BOOLEAN,
    created_at TIMESTAMP
);
```

### Alt-Texts Table

```sql
CREATE TABLE alt_texts (
    id UUID PRIMARY KEY,
    element_id UUID REFERENCES elements(id),
    alt_text TEXT,
    ai_generated TEXT,
    human_edited BOOLEAN,
    is_decorative BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## Storage Strategy

### Object Storage (R2/S3)

```
/uploads/{job_id}/original.pdf      # Original upload
/processing/{job_id}/ocr.json       # OCR results
/processing/{job_id}/layout.json    # Layout analysis
/processing/{job_id}/figures/*.png  # Extracted figures
/outputs/{job_id}/accessible.pdf    # Final output
/reports/{job_id}/compliance.json   # WCAG report
```

## Model Training Pipeline

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

- **PDF sanitization** - Remove embedded scripts, forms, JavaScript
- **Content isolation** - Each job in separate container
- **PII detection** - Flag sensitive content (SSN, credit cards)
- **Access control** - Signed URLs with expiration
- **Audit logging** - All AI decisions logged for review

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
