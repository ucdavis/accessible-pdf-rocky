from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from db.models import Job
from db.session import get_session, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)


class JobStatusResponse(BaseModel):
    job_id: str
    status: str


@app.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_status(
    job_id: UUID, session: AsyncSession = Depends(get_session)
) -> JobStatusResponse:
    """Get job status from database."""
    result = await session.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(job_id=str(job.id), status=job.status.value)
