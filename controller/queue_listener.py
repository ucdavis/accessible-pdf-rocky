"""Cloudflare Queue consumer for processing PDF jobs."""

# TODO: Implement Cloudflare Queue consumer
# This module will:
# - Connect to Cloudflare Queue
# - Listen for job messages
# - Submit SLURM jobs via hpc.submit
# - Update job status in database


async def handle_job(message: dict) -> None:
    """
    Handle a job message from Cloudflare Queue.

    Args:
        message: Job message containing jobId, r2Key, timestamp

    TODO: Implement job handling logic
    """
    _job_id = message.get("jobId")
    _r2_key = message.get("r2Key")

    # TODO: Submit SLURM job
    # TODO: Save to database
    pass


async def start_consumer() -> None:
    """
    Start the Cloudflare Queue consumer.

    TODO: Implement queue consumer setup and main loop
    """
    pass
