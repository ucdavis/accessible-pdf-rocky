"""OCR processing using Tesseract, PaddleOCR, or Azure OCR.

Note: This module directly calls OCR engines (no ai/ layer dependency).
OCR engines are external tools, not ML models we wrap.
"""

from pathlib import Path


def extract_text_ocr(image_or_pdf: Path) -> str:
    """
    Extract text from image or scanned PDF using OCR.

    Args:
        image_or_pdf: Path to image or PDF file

    Returns:
        Extracted text

    TODO: Implement OCR
    - Try Tesseract first (local, free)
    - Fall back to PaddleOCR for better accuracy
    - Fall back to Azure OCR if needed (API quota)
    - Handle multi-language documents
    - Preserve text structure/layout
    """
    # TODO: Implement OCR extraction
    raise NotImplementedError("OCR extraction not yet implemented")


def is_scanned_pdf(pdf_path: Path) -> bool:
    """
    Detect if PDF is scanned (image-based) vs. text-based.

    Args:
        pdf_path: Path to PDF file

    Returns:
        True if PDF is scanned, False otherwise

    TODO: Implement scan detection
    - Check if PDF contains searchable text
    - Analyze page content (images vs text)
    - Return whether OCR is needed
    """
    # TODO: Implement scan detection
    raise NotImplementedError("Scan detection not yet implemented")
