"""Submit SLURM jobs via restricted SSH command.

This module uses a secure SSH connection with a forced command wrapper
that only allows sbatch execution. This implements the principle of
least privilege - even if FastAPI is compromised, attackers cannot
run arbitrary commands on the HPC system.
"""

import os
import re
import shlex
import subprocess
import time
from pathlib import Path

# TODO: Import metrics when ready
# from metrics import submitted_jobs, submission_failures, submission_latency

# Regex pattern for parsing SLURM job ID from sbatch output
SLURM_JOB_ID_PATTERN = re.compile(r"Submitted batch job (\d+)")

# Configuration from environment variables
SLURM_HOST = os.environ.get("SLURM_HOST", "")
SLURM_USER = os.environ.get("SLURM_USER", "slurm_submit")
SLURM_KEY_PATH = os.environ.get("SLURM_KEY_PATH", "")
REMOTE_SCRIPT_DIR = os.environ.get("REMOTE_SCRIPT_DIR", "/home/slurm_submit/jobs")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")

# Validate required configuration in production
if ENVIRONMENT == "production":
    if not SLURM_HOST:
        raise RuntimeError(
            "SLURM_HOST must be set in production environment. "
            "Set the SLURM_HOST environment variable."
        )
    if not SLURM_KEY_PATH:
        raise RuntimeError(
            "SLURM_KEY_PATH must be set in production environment. "
            "Set the SLURM_KEY_PATH environment variable."
        )


def _sanitize_job_name(job_id: str) -> str:
    """Sanitize job_id for use in SBATCH job-name directive.

    SBATCH directives are parsed by SLURM, not bash, so they should not
    contain shell quotes. This function ensures only safe characters are used.

    Args:
        job_id: Job identifier

    Returns:
        Sanitized job name with only alphanumeric, hyphen, and underscore characters
    """
    return re.sub(r"[^a-zA-Z0-9_-]", "_", job_id)


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
    start_time = time.time()  # noqa: F841 - Used in commented metrics code
    local_script = None

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
        if local_script is not None:
            Path(local_script).unlink(missing_ok=True)


def _create_job_script(job_id: str, input_url: str, output_url: str) -> str:
    """
    Create a temporary job script with embedded URLs.

    Security: Uses shlex.quote() to prevent shell injection.

    Returns:
        Path to local temporary script
    """
    # Create temporary script with environment variables set
    # Note: SBATCH directives are parsed by SLURM, not bash, so use sanitization not quoting
    # Use shlex.quote() for bash variables to prevent shell injection via URLs
    script_content = f"""#!/bin/bash
#SBATCH --job-name=wcag-{_sanitize_job_name(job_id)}
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu
#SBATCH --time=02:00:00
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err

export JOB_ID={shlex.quote(job_id)}
export INPUT_URL={shlex.quote(input_url)}
export OUTPUT_URL={shlex.quote(output_url)}

# Source the main job script
source {shlex.quote(f"{REMOTE_SCRIPT_DIR}/job_template.sh")}
"""

    tmp_script = f"/tmp/slurm_job_{job_id}.sh"
    Path(tmp_script).write_text(script_content)
    Path(tmp_script).chmod(0o755)

    return tmp_script


def _upload_script(local_script: str, job_id: str) -> str:
    """
    Upload job script to HPC via SCP.

    Security: Uses the same restricted SSH key as job submission.

    Args:
        local_script: Path to local script file
        job_id: Job identifier for naming remote file

    Returns:
        Remote script path

    Raises:
        subprocess.CalledProcessError: If SCP upload fails
    """
    remote_path = f"{REMOTE_SCRIPT_DIR}/job_{job_id}.sh"
    remote_target = f"{SLURM_USER}@{SLURM_HOST}:{remote_path}"

    cmd = [
        "scp",
        "-i",
        SLURM_KEY_PATH,
        "-o",
        "StrictHostKeyChecking=yes",
        local_script,
        remote_target,
    ]

    subprocess.run(cmd, capture_output=True, text=True, check=True)

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
    # Use regex for robust parsing in case of warnings or format changes
    match = SLURM_JOB_ID_PATTERN.search(result.stdout)
    if not match:
        raise RuntimeError(
            f"Failed to parse SLURM job ID from sbatch output: {result.stdout}"
        )
    slurm_id = match.group(1)
    return slurm_id
