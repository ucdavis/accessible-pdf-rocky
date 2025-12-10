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
    """Create test client."""
    from main import app

    with TestClient(app) as test_client:
        yield test_client


def test_read_root(client):
    """Test root endpoint returns correctly."""
    response = client.get("/")
    assert response.status_code == 404  # No root defined yet


def test_get_status_not_found():
    """Test job status endpoint returns 404 for non-existent job."""
    from unittest.mock import patch
    from fastapi.testclient import TestClient
    import httpx

    # Mock the HTTP client to raise 404
    async def mock_get_job(*args, **kwargs):
        raise httpx.HTTPStatusError(
            "404 Not Found",
            request=httpx.Request("GET", "http://test"),
            response=httpx.Response(404),
        )

    with patch("db.client.DatabaseClient.get_job", new=mock_get_job):
        from main import app

        with TestClient(app, raise_server_exceptions=False) as client:
            job_id = uuid4()
            response = client.get(f"/status/{job_id}")
            assert response.status_code == 404
            assert response.json()["detail"] == "Job not found"


def test_job_status_enum():
    """Test JobStatus enum values."""
    assert JobStatus.SUBMITTED.value == "submitted"
    assert JobStatus.RUNNING.value == "running"
    assert JobStatus.COMPLETED.value == "completed"
    assert JobStatus.FAILED.value == "failed"
