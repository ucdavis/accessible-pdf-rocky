from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from db.client import get_db_client
from metrics import close_metrics_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize on startup and cleanup on shutdown."""
    yield
    # Close metrics client on shutdown
    await close_metrics_client()


app = FastAPI(lifespan=lifespan)


class JobStatusResponse(BaseModel):
    job_id: str
    status: str


@app.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_status(job_id: UUID) -> JobStatusResponse:
    """Get job status from database."""
    db = get_db_client()

    try:
        job = await db.get_job(job_id)
        return JobStatusResponse(job_id=job["id"], status=job["status"])
    except Exception as e:
        # Handle 404 or other errors
        if "404" in str(e) or "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Job not found")
        raise HTTPException(status_code=500, detail=str(e))
