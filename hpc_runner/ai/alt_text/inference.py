"""Batch inference for alt-text generation."""

from typing import Any


async def generate_alt_texts(figures: list[dict]) -> dict[str, str]:
    """
    Generate alt-text for all figures in a document.

    Args:
        figures: List of figure dictionaries with:
            - id: Figure identifier
            - image: Image data
            - context: Surrounding text

    Returns:
        Dictionary mapping figure IDs to generated alt-text

    TODO: Implement batch alt-text generation
    - Load AltTextModel
    - Process figures in batches for efficiency
    - Include context when available
    - Validate quality
    - Return alt-text mappings
    """
    raise NotImplementedError("Alt-text generation not yet implemented")


async def generate_single_alt_text(image: Any, context: str | None = None) -> str:
    """
    Generate alt-text for a single image.

    Args:
        image: Image data
        context: Optional surrounding text

    Returns:
        Generated alt-text

    TODO: Implement single image captioning
    - Preprocess image
    - Run vision-language model
    - Post-process caption
    - Ensure WCAG compliance
    """
    raise NotImplementedError("Single alt-text generation not yet implemented")
