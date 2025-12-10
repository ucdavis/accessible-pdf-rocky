"""Tests for FastAPI controller."""

import sys
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

# Add parent directory to path to import main
sys.path.insert(0, str(Path(__file__).parent.parent))

from uuid import uuid4

from db.models import JobStatus


@pytest.fixture
def client():
    """Create test client with mocked database."""
    from unittest.mock import AsyncMock, patch

    # Mock init_db before importing app
    with patch("db.session.init_db", new_callable=AsyncMock):
        from main import app

        with TestClient(app) as test_client:
            yield test_client


def test_read_root(client):
    """Test root endpoint returns correctly."""
    response = client.get("/")
    assert response.status_code == 404  # No root defined yet


def test_get_status_not_found():
    """Test job status endpoint returns 404 for non-existent job."""
    from unittest.mock import AsyncMock, patch
    from fastapi.testclient import TestClient

    # Mock the database session
    mock_session = AsyncMock()
    # Mock session.get() to return None (job not found)
    mock_session.get.return_value = None

    # Override the get_session dependency
    async def mock_get_session():
        yield mock_session

    # Mock init_db to avoid actual database connection
    with patch("db.session.init_db", new_callable=AsyncMock):
        from main import app
        from db.session import get_session

        app.dependency_overrides[get_session] = mock_get_session

        try:
            with TestClient(app, raise_server_exceptions=False) as client:
                job_id = uuid4()
                response = client.get(f"/status/{job_id}")
                assert response.status_code == 404
                assert response.json()["detail"] == "Job not found"
        finally:
            app.dependency_overrides.clear()


def test_job_status_response_model():
    """Test JobStatusResponse model validation."""
    from main import JobStatusResponse

    status = JobStatusResponse(job_id="test-123", status="completed")
    assert status.job_id == "test-123"
    assert status.status == "completed"


def test_job_status_enum():
    """Test JobStatus enum values."""
    assert JobStatus.SUBMITTED.value == "submitted"
    assert JobStatus.RUNNING.value == "running"
    assert JobStatus.COMPLETED.value == "completed"
    assert JobStatus.FAILED.value == "failed"
