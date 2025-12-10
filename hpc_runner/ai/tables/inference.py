"""Batch inference for table structure recognition."""

from typing import Any


async def parse_tables(tables: list[dict]) -> dict[str, dict]:
    """
    Parse structure for all tables in a document.

    Args:
        tables: List of table dictionaries with:
            - id: Table identifier
            - image: Table region image
            - bbox: Bounding box

    Returns:
        Dictionary mapping table IDs to parsed structure

    TODO: Implement batch table parsing
    - Load TableModel
    - Process tables in batches
    - Extract structured data
    - Validate results
    - Return structured mappings
    """
    raise NotImplementedError("Table parsing not yet implemented")


async def parse_single_table(table_image: Any) -> dict:
    """
    Parse a single table structure.

    Args:
        table_image: Table region image

    Returns:
        Parsed table structure

    TODO: Implement single table parsing
    - Run table model inference
    - Extract cells and structure
    - Identify headers
    - Return structured representation
    """
    raise NotImplementedError("Single table parsing not yet implemented")
