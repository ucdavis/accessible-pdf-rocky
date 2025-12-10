"""Cloudflare R2 download utilities."""

from pathlib import Path


async def download_file(r2_key: str, local_path: Path) -> Path:
    """
    Download a file from Cloudflare R2.

    Args:
        r2_key: R2 object key (source path)
        local_path: Local destination path

    Returns:
        Path to downloaded file

    TODO: Implement R2 download using boto3 or cloudflare SDK
    """
    # TODO: Initialize R2 client with credentials
    # TODO: Download file to local path
    # TODO: Handle download errors and retries
    # TODO: Verify file integrity
    raise NotImplementedError("R2 download not yet implemented")


async def download_pdf(job_id: str, r2_key: str) -> Path:
    """
    Download PDF file for processing.

    Args:
        job_id: Job identifier
        r2_key: R2 object key for PDF

    Returns:
        Path to downloaded PDF

    TODO: Implement PDF download with temporary storage
    """
    local_path = Path(f"/tmp/pdfs/{job_id}.pdf")
    local_path.parent.mkdir(parents=True, exist_ok=True)
    return await download_file(r2_key, local_path)
