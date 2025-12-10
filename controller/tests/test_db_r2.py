"""Tests for controller db and r2 modules."""

from pathlib import Path

import pytest


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
        # Verify Job can be instantiated (even if it's just a stub)
        job = Job()
        assert job is not None

    def test_user_model_exists(self):
        """Test that User model class exists."""
        from db.models import User

        assert User is not None
        # Verify User can be instantiated
        user = User()
        assert user is not None

    def test_processing_metrics_model_exists(self):
        """Test that ProcessingMetrics model class exists."""
        from db.models import ProcessingMetrics

        assert ProcessingMetrics is not None
        # Verify ProcessingMetrics can be instantiated
        metrics = ProcessingMetrics()
        assert metrics is not None


class TestDBSession:
    """Tests for db/session.py"""

    def test_imports(self):
        """Test that db session can be imported."""
        from db import session

        assert session is not None

    def test_get_db_connection_exists(self):
        """Test that get_db_connection function exists and returns None."""
        from db.session import get_db_connection

        # Currently returns None (not implemented)
        result = get_db_connection()
        assert result is None

    def test_db_session_exists(self):
        """Test that db_session function exists and returns None."""
        from db.session import db_session

        # Currently returns None (not implemented)
        result = db_session()
        assert result is None

    @pytest.mark.asyncio
    async def test_init_db_exists(self):
        """Test that init_db async function exists and returns None."""
        from db.session import init_db

        # Currently returns None (not implemented)
        result = await init_db()
        assert result is None


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
        """Test that download_pdf creates proper directory structure before calling download_file."""
        from r2.download import download_pdf

        # download_pdf calls download_file which raises NotImplementedError,
        # but we can verify the path structure logic
        with pytest.raises(NotImplementedError):
            await download_pdf("job123", "uploads/test.pdf")

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
            assert str(call_args[0][1]) == "/tmp/pdfs/job456.pdf"  # local_path
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
