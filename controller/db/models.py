"""Type definitions and enums for database models.

Note: These are kept for type hints and compatibility, but the actual
database operations are now handled via HTTP API to D1 worker.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    """Return current UTC time with timezone info."""
    return datetime.now(timezone.utc)


class JobStatus(str, Enum):
    """Job processing status."""

    SUBMITTED = "submitted"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(BaseModel):
    """Job model for tracking PDF processing."""

    id: UUID = Field(default_factory=uuid4)
    slurm_id: Optional[str] = None
    status: JobStatus = JobStatus.SUBMITTED
    r2_key: str
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    results_url: Optional[str] = None
    user_id: Optional[UUID] = None


class User(BaseModel):
    """User model for authentication and tracking."""

    id: UUID = Field(default_factory=uuid4)
    email: str
    name: Optional[str] = None
    organization: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)
    is_active: bool = True


class ProcessingMetrics(BaseModel):
    """Processing metrics for monitoring and analytics."""

    id: UUID = Field(default_factory=uuid4)
    job_id: UUID
    processing_time_seconds: Optional[float] = None
    pdf_pages: Optional[int] = None
    pdf_size_bytes: Optional[int] = None
    success: bool = False
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)
