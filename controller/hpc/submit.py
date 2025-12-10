"""Submit SLURM jobs via restricted SSH command.

This module uses a secure SSH connection with a forced command wrapper
that only allows sbatch execution. This implements the principle of
least privilege - even if FastAPI is compromised, attackers cannot
run arbitrary commands on the HPC system.
"""

import subprocess
import time
from pathlib import Path

# TODO: Import metrics when ready
# from metrics import submitted_jobs, submission_failures, submission_latency

# Configuration (should come from environment variables in production)
SLURM_HOST = "hpc-login.ucdavis.edu"  # TODO: Set from env
SLURM_USER = "slurm_submit"  # Restricted user
SLURM_KEY_PATH = "/path/to/id_ed25519_slurm_submit"  # TODO: Set from env
REMOTE_SCRIPT_DIR = "/home/slurm_submit/jobs"  # Validated by wrapper


def submit_slurm_job(job_id: str, input_url: str, output_url: str) -> str:
    """
    Submit a SLURM job via restricted SSH.

    Security:
    - SSH key has forced command: /usr/local/bin/slurm_sbatch_wrapper.sh
    - Wrapper validates script path is in allowed directory
    - No shell access, no arbitrary commands, no port forwarding

    Args:
        job_id: Unique job identifier
        input_url: Presigned R2 URL to download input PDF
        output_url: Presigned R2 URL to upload output PDF

    Returns:
        SLURM job ID as a string

    Raises:
        subprocess.CalledProcessError: If SSH or sbatch fails
    """
    start_time = time.time()

    try:
        # 1. Create job script locally
        local_script = _create_job_script(job_id, input_url, output_url)

        # 2. Copy script to HPC via SFTP (using restricted key)
        remote_script = _upload_script(local_script, job_id)

        # 3. Submit via SSH (restricted command wrapper)
        slurm_id = _submit_via_ssh(remote_script)

        # Record success metrics
        # submitted_jobs.labels(status="success").inc()
        # submission_latency.observe(time.time() - start_time)

        return slurm_id

    except subprocess.CalledProcessError as e:
        # Record failure metrics
        # submission_failures.labels(error_type="slurm_error").inc()
        raise RuntimeError(f"SLURM submission failed: {e.stderr}") from e
    except Exception as e:
        # submission_failures.labels(error_type="unknown").inc()
        raise RuntimeError(f"Unexpected error during submission: {e}") from e
    finally:
        # Clean up local script
        if "local_script" in locals():
            Path(local_script).unlink(missing_ok=True)


def _create_job_script(job_id: str, input_url: str, output_url: str) -> str:
    """
    Create a temporary job script with embedded URLs.

    Returns:
        Path to local temporary script
    """
    # Create temporary script with environment variables set
    # In production, this would be more sophisticated
    script_content = f"""#!/bin/bash
#SBATCH --job-name=wcag-{job_id}
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu
#SBATCH --time=02:00:00
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err

export JOB_ID="{job_id}"
export INPUT_URL="{input_url}"
export OUTPUT_URL="{output_url}"

# Source the main job script
source {REMOTE_SCRIPT_DIR}/job_template.sh
"""

    tmp_script = f"/tmp/slurm_job_{job_id}.sh"
    Path(tmp_script).write_text(script_content)
    Path(tmp_script).chmod(0o755)

    return tmp_script


def _upload_script(local_script: str, job_id: str) -> str:
    """
    Upload job script to HPC via SFTP.

    Returns:
        Remote script path
    """
    remote_path = f"{REMOTE_SCRIPT_DIR}/job_{job_id}.sh"

    # TODO: Implement actual SFTP upload
    # Using paramiko or subprocess with sftp
    # Example:
    # sftp -i {SLURM_KEY_PATH} {SLURM_USER}@{SLURM_HOST} <<< "put {local_script} {remote_path}"

    return remote_path


def _submit_via_ssh(remote_script: str) -> str:
    """
    Submit job via SSH with restricted command.

    The SSH key has a forced command, so this will ALWAYS execute:
    /usr/local/bin/slurm_sbatch_wrapper.sh <script>

    Args:
        remote_script: Path to script on HPC system

    Returns:
        SLURM job ID
    """
    cmd = [
        "ssh",
        "-i",
        SLURM_KEY_PATH,
        "-o",
        "StrictHostKeyChecking=yes",
        f"{SLURM_USER}@{SLURM_HOST}",
        remote_script,  # Passed to wrapper as argument
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    # sbatch output: "Submitted batch job <id>"
    slurm_id = result.stdout.strip().split()[-1]
    return slurm_id
