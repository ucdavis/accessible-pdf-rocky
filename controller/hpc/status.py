"""SLURM job status monitoring."""

import subprocess


def get_slurm_status(slurm_id: str) -> str:
    """
    Query SLURM job status using sacct.

    Args:
        slurm_id: SLURM job ID

    Returns:
        Job status string (e.g., "RUNNING", "COMPLETED", "FAILED")

    TODO: Implement error handling and status parsing
    """
    # TODO: Add error handling for missing/invalid job IDs
    # TODO: Parse and normalize SLURM status codes
    cmd = ["sacct", "-j", slurm_id, "--format=State", "--noheader"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return result.stdout.strip().split()[0] if result.stdout else "UNKNOWN"


def get_job_output(slurm_id: str) -> str | None:
    """
    Retrieve job output file path.

    Args:
        slurm_id: SLURM job ID

    Returns:
        Path to job output file or None if not found

    TODO: Implement job output retrieval from HPC scratch
    """
    # TODO: Determine output file location from SLURM
    # TODO: Verify file exists and is readable
    pass
