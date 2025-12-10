import subprocess
from pathlib import Path


def submit_slurm_job(job_id: str, pdf_path: str) -> str:
    """
    Submit a SLURM job for PDF accessibility analysis.

    Args:
        job_id: Unique job identifier
        pdf_path: Path to the PDF file on the HPC filesystem

    Returns:
        SLURM job ID as a string
    """
    # Get absolute path to job script
    script_path = Path(__file__).parent / "scripts" / "job.sh"

    cmd = [
        "sbatch",
        f"--job-name=wcag-{job_id}",
        f"--export=ALL,JOB_ID={job_id},PDF_PATH={pdf_path}",
        str(script_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    # sbatch output often ends with "Submitted batch job <id>"
    slurm_id = result.stdout.strip().split()[-1]
    return slurm_id
