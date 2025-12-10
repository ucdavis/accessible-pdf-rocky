"""Database models for job tracking."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class JobStatus(str, Enum):
    """Job processing status."""

    SUBMITTED = "submitted"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(SQLModel, table=True):
    """Job model for tracking PDF processing."""

    __tablename__ = "jobs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    slurm_id: Optional[str] = Field(default=None, index=True)
    status: JobStatus = Field(default=JobStatus.SUBMITTED, index=True)
    r2_key: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    results_url: Optional[str] = None
    user_id: Optional[UUID] = Field(default=None, foreign_key="users.id")


class User(SQLModel, table=True):
    """User model for authentication and tracking."""

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: Optional[str] = None
    organization: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)


class ProcessingMetrics(SQLModel, table=True):
    """Processing metrics for monitoring and analytics."""

    __tablename__ = "processing_metrics"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    job_id: UUID = Field(foreign_key="jobs.id", index=True)
    processing_time_seconds: Optional[float] = None
    pdf_pages: Optional[int] = None
    pdf_size_bytes: Optional[int] = None
    success: bool = Field(default=False)
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
