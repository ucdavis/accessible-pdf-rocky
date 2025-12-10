from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import UUID

import httpx
from fastapi import FastAPI, HTTPException

from db.client import close_db_client, get_db_client
from db.models import Job, JobStatus
from metrics import close_metrics_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for cleanup on shutdown."""
    yield
    # Close clients on shutdown
    await close_metrics_client()
    await close_db_client()


app = FastAPI(lifespan=lifespan)


@app.get("/status/{job_id}", response_model=Job)
async def get_status(job_id: UUID) -> Job:
    """Get job status from database.

    Returns job with camelCase field names for frontend compatibility.
    """
    db = get_db_client()

    try:
        job_data = await db.get_job(job_id)
        # Convert timestamps from Unix seconds to datetime
        # Use defensive handling in case timestamps are missing (shouldn't happen in practice)
        now = datetime.now(timezone.utc)
        return Job(
            id=UUID(job_data["id"]),
            slurm_id=job_data.get("slurm_id"),
            status=JobStatus(job_data["status"]),
            r2_key=job_data["r2_key"],
            created_at=(
                datetime.fromtimestamp(job_data["created_at"], tz=timezone.utc)
                if job_data.get("created_at") is not None
                else now
            ),
            updated_at=(
                datetime.fromtimestamp(job_data["updated_at"], tz=timezone.utc)
                if job_data.get("updated_at") is not None
                else now
            ),
            results_url=job_data.get("results_url"),
            user_id=UUID(job_data["user_id"]) if job_data.get("user_id") else None,
            error=None,  # TODO: Add error tracking to database
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Job not found")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503, detail=f"Database service unavailable: {e}"
        )
