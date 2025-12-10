"""OCR engine service orchestrating Tesseract, PaddleOCR, and Azure OCR."""

from pathlib import Path


async def run_ocr(pdf_path: Path) -> dict:
    """
    Run OCR on a PDF file.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Dictionary containing OCR results:
        - text: Extracted text
        - confidence: OCR confidence scores
        - page_results: Per-page OCR data

    TODO: Implement OCR orchestration
    - Try Tesseract first (local, free)
    - Fall back to PaddleOCR for better accuracy
    - Fall back to Azure OCR if needed (API quota)
    - Handle multi-language documents
    - Preserve text structure/layout
    """
    raise NotImplementedError("OCR orchestration not yet implemented")


async def ocr_page(image_path: Path, engine: str = "tesseract") -> dict:
    """
    Run OCR on a single page image.

    Args:
        image_path: Path to page image
        engine: OCR engine to use ("tesseract", "paddleocr", "azure")

    Returns:
        Dictionary containing page OCR results

    TODO: Implement single-page OCR
    - Support multiple OCR engines
    - Return structured results with bounding boxes
    - Include confidence scores
    """
    raise NotImplementedError("Single-page OCR not yet implemented")


def select_best_ocr_engine(pdf_type: str, language: str = "eng") -> str:
    """
    Select the best OCR engine for a given PDF.

    Args:
        pdf_type: PDF type ("scanned", "hybrid", "digital")
        language: Document language code

    Returns:
        OCR engine name

    TODO: Implement engine selection logic
    - Consider language support
    - Consider accuracy requirements
    - Consider API quotas/costs
    - Consider processing time
    """
    raise NotImplementedError("OCR engine selection not yet implemented")
