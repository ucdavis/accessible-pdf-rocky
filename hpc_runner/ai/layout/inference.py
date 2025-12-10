"""Batch inference for layout detection."""

from pathlib import Path


async def run_layout_inference(pdf_path: Path) -> dict:
    """
    Run layout detection on entire PDF.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Dictionary containing layout results for all pages:
        - pages: List of page results
        - elements: All detected elements
        - reading_order: Global reading order

    TODO: Implement batch layout inference
    - Load LayoutModel
    - Process each page
    - Aggregate results
    - Determine reading order across pages
    """
    raise NotImplementedError("Layout inference not yet implemented")


async def process_page(page_image: bytes, page_num: int) -> dict:
    """
    Process a single page for layout detection.

    Args:
        page_image: Page image bytes
        page_num: Page number

    Returns:
        Page layout results

    TODO: Implement single-page processing
    - Run layout model inference
    - Extract elements and bounding boxes
    - Return structured results
    """
    raise NotImplementedError("Page processing not yet implemented")
