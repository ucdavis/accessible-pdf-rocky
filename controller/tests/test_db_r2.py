"""Tests for controller db and r2 modules."""

import sys
from pathlib import Path

import pytest

# Add parent directory to path to import db and r2 modules
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestDBModels:
    """Tests for db/models.py"""

    def test_imports(self):
        """Test that db models can be imported."""
        from db import models

        assert models is not None

    def test_job_model_exists(self):
        """Test that Job model class exists."""
        from db.models import Job

        assert Job is not None

    def test_user_model_exists(self):
        """Test that User model class exists."""
        from db.models import User

        assert User is not None

    def test_processing_metrics_model_exists(self):
        """Test that ProcessingMetrics model class exists."""
        from db.models import ProcessingMetrics

        assert ProcessingMetrics is not None

    def test_utc_now_returns_timezone_aware_datetime(self):
        """Test that utc_now() returns timezone-aware datetime in UTC."""
        from datetime import timezone
        from db.models import utc_now

        result = utc_now()

        # Should return a datetime object
        assert result is not None
        # Should be timezone-aware (not naive)
        assert result.tzinfo is not None
        # Should be in UTC timezone
        assert result.tzinfo == timezone.utc

    def test_job_model_fields_and_defaults(self):
        """Test Job model field definitions and default values."""
        from uuid import UUID
        from db.models import Job, JobStatus

        job = Job(r2_key="test/key.pdf")

        # Check types and defaults
        assert isinstance(job.id, UUID)
        assert job.status == JobStatus.SUBMITTED
        assert job.r2_key == "test/key.pdf"
        assert job.slurm_id is None
        assert job.results_url is None
        assert job.user_id is None
        # Timestamps should be auto-populated
        assert job.created_at is not None
        assert job.updated_at is not None
        # Timestamps should be timezone-aware
        assert job.created_at.tzinfo is not None
        assert job.updated_at.tzinfo is not None

    def test_user_model_fields_and_defaults(self):
        """Test User model field definitions and default values."""
        from uuid import UUID
        from db.models import User

        user = User(email="test@example.com")

        # Check types and defaults
        assert isinstance(user.id, UUID)
        assert user.email == "test@example.com"
        assert user.name is None
        assert user.organization is None
        assert user.is_active is True
        # Timestamp should be auto-populated
        assert user.created_at is not None
        # Timestamp should be timezone-aware
        assert user.created_at.tzinfo is not None

    def test_processing_metrics_model_fields_and_defaults(self):
        """Test ProcessingMetrics model field definitions and default values."""
        from uuid import UUID
        from db.models import ProcessingMetrics

        # Need a job_id UUID for the foreign key
        from uuid import uuid4

        job_id = uuid4()

        metrics = ProcessingMetrics(job_id=job_id)

        # Check types and defaults
        assert isinstance(metrics.id, UUID)
        assert metrics.job_id == job_id
        assert metrics.processing_time_seconds is None
        assert metrics.pdf_pages is None
        assert metrics.pdf_size_bytes is None
        assert metrics.success is False
        assert metrics.error_message is None
        # Timestamp should be auto-populated
        assert metrics.created_at is not None
        # Timestamp should be timezone-aware
        assert metrics.created_at.tzinfo is not None


class TestDBClient:
    """Tests for db/client.py"""

    def test_imports(self):
        """Test that db client can be imported."""
        from db import client

        assert client is not None

    def test_get_db_client_exists(self):
        """Test that get_db_client function exists and returns DatabaseClient."""
        from db.client import get_db_client, DatabaseClient

        client = get_db_client()
        assert client is not None
        assert isinstance(client, DatabaseClient)

    def test_database_client_init(self):
        """Test that DatabaseClient can be initialized."""
        from db.client import DatabaseClient

        client = DatabaseClient(base_url="http://test", token="test-token")
        assert client is not None
        assert client.base_url == "http://test"
        assert client.token == "test-token"
        assert "Authorization" in client.headers
        assert client.headers["Authorization"] == "Bearer test-token"


class TestR2Download:
    """Tests for r2/download.py"""

    def test_imports(self):
        """Test that r2 download can be imported."""
        from r2 import download

        assert download is not None

    @pytest.mark.asyncio
    async def test_download_file_not_implemented(self):
        """Test that download_file raises NotImplementedError."""
        from r2.download import download_file

        with pytest.raises(
            NotImplementedError, match="R2 download not yet implemented"
        ):
            await download_file("test/key.pdf", Path("/tmp/test.pdf"))

    @pytest.mark.asyncio
    async def test_download_pdf_creates_directory_structure(self):
        """Test that download_pdf creates /tmp/pdfs/{job_id}.pdf before calling download_file."""
        from unittest.mock import AsyncMock, patch

        from r2.download import download_pdf

        with patch(
            "r2.download.download_file", new_callable=AsyncMock
        ) as mock_download:
            mock_download.return_value = Path("/tmp/pdfs/job123.pdf")
            await download_pdf("job123", "uploads/test.pdf")

        # Verify the local path parent directory is /tmp/pdfs
        local_path = mock_download.call_args[0][1]
        assert local_path.parent == Path("/tmp/pdfs")
        assert local_path.name == "job123.pdf"

    @pytest.mark.asyncio
    async def test_download_pdf_uses_correct_path_pattern(self):
        """Test that download_pdf constructs the expected local path."""
        from unittest.mock import AsyncMock, patch

        # Mock download_file to verify the path it receives
        with patch(
            "r2.download.download_file", new_callable=AsyncMock
        ) as mock_download:
            mock_download.return_value = Path("/tmp/pdfs/job456.pdf")
            from r2.download import download_pdf

            result = await download_pdf("job456", "uploads/test.pdf")

            # Verify download_file was called with correct arguments
            mock_download.assert_called_once()
            call_args = mock_download.call_args
            assert call_args[0][0] == "uploads/test.pdf"  # r2_key
            assert call_args[0][1] == Path("/tmp/pdfs/job456.pdf")  # local_path
            assert result == Path("/tmp/pdfs/job456.pdf")


class TestR2Upload:
    """Tests for r2/upload.py"""

    def test_imports(self):
        """Test that r2 upload can be imported."""
        from r2 import upload

        assert upload is not None

    @pytest.mark.asyncio
    async def test_upload_file_not_implemented(self):
        """Test that upload_file raises NotImplementedError."""
        from r2.upload import upload_file

        with pytest.raises(NotImplementedError, match="R2 upload not yet implemented"):
            await upload_file(Path("/tmp/test.pdf"), "uploads/test.pdf")

    @pytest.mark.asyncio
    async def test_upload_results_constructs_correct_r2_key(self):
        """Test that upload_results constructs the correct R2 key pattern."""
        from unittest.mock import AsyncMock, patch

        # Mock upload_file to verify the r2_key it receives
        with patch("r2.upload.upload_file", new_callable=AsyncMock) as mock_upload:
            mock_upload.return_value = (
                "https://r2.example.com/results/job789/output.pdf"
            )
            from r2.upload import upload_results

            result = await upload_results("job789", Path("/tmp/output.pdf"))

            # Verify upload_file was called with correct arguments
            mock_upload.assert_called_once()
            call_args = mock_upload.call_args
            assert call_args[0][0] == Path("/tmp/output.pdf")  # local_path
            assert call_args[0][1] == "results/job789/output.pdf"  # r2_key
            assert result == "https://r2.example.com/results/job789/output.pdf"

    @pytest.mark.asyncio
    async def test_upload_results_preserves_filename(self):
        """Test that upload_results preserves the original filename in R2 key."""
        from unittest.mock import AsyncMock, patch

        with patch("r2.upload.upload_file", new_callable=AsyncMock) as mock_upload:
            mock_upload.return_value = "https://r2.example.com/results/jobX/report.json"
            from r2.upload import upload_results

            await upload_results("jobX", Path("/tmp/report.json"))

            # Verify the r2_key includes the original filename
            call_args = mock_upload.call_args
            assert call_args[0][1] == "results/jobX/report.json"
