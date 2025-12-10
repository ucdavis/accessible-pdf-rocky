"""Cloudflare R2 upload utilities."""

from pathlib import Path


async def upload_file(local_path: Path, r2_key: str) -> str:
    """
    Upload a file to Cloudflare R2.

    Args:
        local_path: Local file path
        r2_key: R2 object key (destination path)

    Returns:
        R2 object URL

    TODO: Implement R2 upload using boto3 or cloudflare SDK
    """
    # TODO: Initialize R2 client with credentials
    # TODO: Upload file with appropriate content-type
    # TODO: Handle upload errors and retries
    # TODO: Return public or signed URL
    raise NotImplementedError("R2 upload not yet implemented")


async def upload_results(job_id: str, results_path: Path) -> str:
    """
    Upload job results to R2.

    Args:
        job_id: Job identifier
        results_path: Path to results file (JSON or PDF)

    Returns:
        R2 object URL

    TODO: Implement results upload with proper naming convention
    """
    r2_key = f"results/{job_id}/{results_path.name}"
    return await upload_file(results_path, r2_key)
