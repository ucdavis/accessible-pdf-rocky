"""Alt-text generation using BLIP-2, LLaVA, or similar vision-language models."""

from pathlib import Path
from typing import Any


def generate_alt_text(image_path: Path) -> str:
    """
    Generate descriptive alt-text for an image.

    Args:
        image_path: Path to image file

    Returns:
        Generated alt-text description

    TODO: Implement alt-text generation
    - Load BLIP-2 or LLaVA model
    - Process image
    - Generate descriptive caption
    - Ensure WCAG 2.1 AA compliance (meaningful, concise)
    """
    # TODO: Implement alt-text generation
    raise NotImplementedError("Alt-text generation not yet implemented")


def generate_alt_text_for_figure(figure_region: dict, pdf_page: Any) -> str:
    """
    Generate alt-text for a figure detected in PDF.

    Args:
        figure_region: Figure region from layout detection
        pdf_page: PDF page object

    Returns:
        Generated alt-text

    TODO: Implement figure extraction and alt-text generation
    - Extract image from PDF region
    - Generate alt-text using vision model
    - Consider figure context (caption, surrounding text)
    """
    # TODO: Implement figure alt-text generation
    raise NotImplementedError("Figure alt-text generation not yet implemented")
