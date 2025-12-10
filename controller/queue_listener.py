"""Cloudflare Queue consumer for processing PDF jobs."""


# TODO: Import presigned URL generation
# from r2.presigned import generate_presigned_url

# TODO: Import database client
# from db.client import get_db_client


async def handle_job(message: dict) -> None:
    """
    Handle a job message from Cloudflare Queue.

    Args:
        message: Job message containing jobId, r2Key, timestamp
    """
    job_id = message.get("jobId")
    r2_key = message.get("r2Key")

    # TODO: Generate presigned URLs for SLURM job
    # input_url = generate_presigned_url(r2_key, operation="get", expires=3600)
    # output_key = f"outputs/{job_id}/accessible.pdf"
    # output_url = generate_presigned_url(output_key, operation="put", expires=3600)

    # TODO: Submit SLURM job with URLs
    # slurm_id = submit_slurm_job(job_id, input_url, output_url)

    # TODO: Save job to database
    # db = get_db_client()
    # await db.create_job(
    #     job_id=job_id,
    #     r2_key=r2_key,
    #     slurm_id=slurm_id,
    #     status="submitted"
    # )

    print(f"TODO: Process job {job_id} with R2 key {r2_key}")


async def start_consumer() -> None:
    """
    Start the Cloudflare Queue consumer.

    TODO: Implement queue consumer setup and main loop
    """
    pass
