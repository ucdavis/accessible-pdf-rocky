import subprocess
from pathlib import Path


def submit_slurm_job(job_id: str, input_url: str, output_url: str) -> str:
    """
    Submit a SLURM job for PDF accessibility analysis.

    Args:
        job_id: Unique job identifier
        input_url: Presigned R2 URL to download input PDF
        output_url: Presigned R2 URL to upload output PDF

    Returns:
        SLURM job ID as a string
    """
    # Get absolute path to job script
    script_path = Path(__file__).parent / "scripts" / "job.sh"

    cmd = [
        "sbatch",
        f"--job-name=wcag-{job_id}",
        f"--export=ALL,JOB_ID={job_id},INPUT_URL={input_url},OUTPUT_URL={output_url}",
        str(script_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    # sbatch output often ends with "Submitted batch job <id>"
    slurm_id = result.stdout.strip().split()[-1]
    return slurm_id
