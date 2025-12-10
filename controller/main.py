from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class JobStatus(BaseModel):
    job_id: str
    status: str


# TODO: read from Postgres
@app.get("/status/{job_id}", response_model=JobStatus)
async def get_status(job_id: str):
    # placeholder
    return JobStatus(job_id=job_id, status="queued")
