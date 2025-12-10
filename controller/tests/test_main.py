"""Tests for FastAPI controller."""

import sys
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

# Add parent directory to path to import main
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app, JobStatus


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_read_root(client):
    """Test root endpoint returns correctly."""
    response = client.get("/")
    assert response.status_code == 404  # No root defined yet


def test_get_status(client):
    """Test job status endpoint."""
    response = client.get("/status/test-job-123")
    assert response.status_code == 200
    
    data = response.json()
    assert data["job_id"] == "test-job-123"
    assert data["status"] == "queued"


def test_job_status_model():
    """Test JobStatus model validation."""
    status = JobStatus(job_id="test-123", status="completed")
    assert status.job_id == "test-123"
    assert status.status == "completed"
