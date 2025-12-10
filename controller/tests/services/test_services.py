"""Tests for controller services layer."""

import sys
from pathlib import Path

import pytest

# Add parent directory to path to import services modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestJobRunner:
    """Tests for services/job_runner.py"""

    def test_imports(self):
        """Test that job_runner module can be imported."""
        from services import job_runner

        assert job_runner is not None

    @pytest.mark.asyncio
    async def test_process_pdf_job_not_implemented(self):
        """Test process_pdf_job raises NotImplementedError."""
        from services.job_runner import process_pdf_job

        with pytest.raises(NotImplementedError):
            await process_pdf_job("job123", Path("/tmp/test.pdf"))

    @pytest.mark.asyncio
    async def test_submit_hpc_processing_not_implemented(self):
        """Test submit_hpc_processing raises NotImplementedError."""
        from services.job_runner import submit_hpc_processing

        with pytest.raises(NotImplementedError):
            await submit_hpc_processing("job123", Path("/tmp/test.pdf"))

    @pytest.mark.asyncio
    async def test_process_locally_not_implemented(self):
        """Test process_locally raises NotImplementedError."""
        from services.job_runner import process_locally

        with pytest.raises(NotImplementedError):
            await process_locally("job123", Path("/tmp/test.pdf"))

    def test_cleanup_job_files_not_implemented(self):
        """Test cleanup_job_files raises NotImplementedError."""
        from services.job_runner import cleanup_job_files

        with pytest.raises(NotImplementedError):
            cleanup_job_files("job123")


class TestOcrEngine:
    """Tests for services/ocr_engine.py"""

    def test_imports(self):
        """Test that ocr_engine module can be imported."""
        from services import ocr_engine

        assert ocr_engine is not None

    @pytest.mark.asyncio
    async def test_run_ocr_not_implemented(self):
        """Test run_ocr raises NotImplementedError."""
        from services.ocr_engine import run_ocr

        with pytest.raises(NotImplementedError):
            await run_ocr(Path("/tmp/test.pdf"))

    @pytest.mark.asyncio
    async def test_ocr_page_not_implemented(self):
        """Test ocr_page raises NotImplementedError."""
        from services.ocr_engine import ocr_page

        with pytest.raises(NotImplementedError):
            await ocr_page(Path("/tmp/page.png"))

    @pytest.mark.asyncio
    async def test_ocr_page_with_engine_not_implemented(self):
        """Test ocr_page with specific engine raises NotImplementedError."""
        from services.ocr_engine import ocr_page

        with pytest.raises(NotImplementedError):
            await ocr_page(Path("/tmp/page.png"), engine="paddleocr")

    def test_select_best_ocr_engine_not_implemented(self):
        """Test select_best_ocr_engine raises NotImplementedError."""
        from services.ocr_engine import select_best_ocr_engine

        with pytest.raises(NotImplementedError):
            select_best_ocr_engine("scanned")


class TestPdfBuilder:
    """Tests for services/pdf_builder.py"""

    def test_imports(self):
        """Test that pdf_builder module can be imported."""
        from services import pdf_builder

        assert pdf_builder is not None

    def test_build_tagged_pdf_not_implemented(self):
        """Test build_tagged_pdf raises NotImplementedError."""
        from services.pdf_builder import build_tagged_pdf

        with pytest.raises(NotImplementedError):
            build_tagged_pdf({}, Path("/tmp/test.pdf"))

    def test_add_structure_tags_not_implemented(self):
        """Test add_structure_tags raises NotImplementedError."""
        from services.pdf_builder import add_structure_tags

        with pytest.raises(NotImplementedError):
            add_structure_tags(Path("/tmp/test.pdf"), {})

    def test_embed_alt_texts_not_implemented(self):
        """Test embed_alt_texts raises NotImplementedError."""
        from services.pdf_builder import embed_alt_texts

        with pytest.raises(NotImplementedError):
            embed_alt_texts(Path("/tmp/test.pdf"), {})

    def test_set_pdf_metadata_not_implemented(self):
        """Test set_pdf_metadata raises NotImplementedError."""
        from services.pdf_builder import set_pdf_metadata

        with pytest.raises(NotImplementedError):
            set_pdf_metadata(Path("/tmp/test.pdf"), {})

    def test_validate_output_pdf_not_implemented(self):
        """Test validate_output_pdf raises NotImplementedError."""
        from services.pdf_builder import validate_output_pdf

        with pytest.raises(NotImplementedError):
            validate_output_pdf(Path("/tmp/test.pdf"))


class TestPdfNormalizer:
    """Tests for services/pdf_normalizer.py"""

    def test_imports(self):
        """Test that pdf_normalizer module can be imported."""
        from services import pdf_normalizer

        assert pdf_normalizer is not None

    def test_detect_pdf_type_not_implemented(self):
        """Test detect_pdf_type raises NotImplementedError."""
        from services.pdf_normalizer import detect_pdf_type

        with pytest.raises(NotImplementedError):
            detect_pdf_type(Path("/tmp/test.pdf"))

    def test_normalize_pdf_not_implemented(self):
        """Test normalize_pdf raises NotImplementedError."""
        from services.pdf_normalizer import normalize_pdf

        with pytest.raises(NotImplementedError):
            normalize_pdf(Path("/tmp/test.pdf"), Path("/tmp/output.pdf"))

    def test_preprocess_for_ocr_not_implemented(self):
        """Test preprocess_for_ocr raises NotImplementedError."""
        from services.pdf_normalizer import preprocess_for_ocr

        with pytest.raises(NotImplementedError):
            preprocess_for_ocr(Path("/tmp/test.pdf"))


class TestPdfParser:
    """Tests for services/pdf_parser.py"""

    def test_imports(self):
        """Test that pdf_parser module can be imported."""
        from services import pdf_parser

        assert pdf_parser is not None

    def test_parse_pdf_not_implemented(self):
        """Test parse_pdf raises NotImplementedError."""
        from services.pdf_parser import parse_pdf

        with pytest.raises(NotImplementedError):
            parse_pdf(Path("/tmp/test.pdf"))

    def test_extract_page_images_not_implemented(self):
        """Test extract_page_images raises NotImplementedError."""
        from services.pdf_parser import extract_page_images

        with pytest.raises(NotImplementedError):
            extract_page_images(Path("/tmp/test.pdf"), 0)

    def test_get_pdf_metadata_not_implemented(self):
        """Test get_pdf_metadata raises NotImplementedError."""
        from services.pdf_parser import get_pdf_metadata

        with pytest.raises(NotImplementedError):
            get_pdf_metadata(Path("/tmp/test.pdf"))


class TestResultHandler:
    """Tests for services/result_handler.py"""

    def test_imports(self):
        """Test that result_handler module can be imported."""
        from services import result_handler

        assert result_handler is not None

    @pytest.mark.asyncio
    async def test_process_job_results_not_implemented(self):
        """Test process_job_results raises NotImplementedError."""
        from services.result_handler import process_job_results

        with pytest.raises(NotImplementedError):
            await process_job_results("job123", "slurm456")

    @pytest.mark.asyncio
    async def test_handle_job_failure_does_not_raise(self):
        """Test handle_job_failure can be called without error."""
        from services.result_handler import handle_job_failure

        # Should not raise - currently just passes
        await handle_job_failure("job123", "slurm456", "test error")

    def test_get_job_results_path_returns_path(self):
        """Test get_job_results_path returns expected Path."""
        from services.result_handler import get_job_results_path

        result = get_job_results_path("job123")
        assert isinstance(result, Path)
        assert "job123" in str(result)
        assert "/scratch/accessible-pdf/" in str(result)


class TestWcagEngine:
    """Tests for services/wcag_engine.py"""

    def test_imports(self):
        """Test that wcag_engine module can be imported."""
        from services import wcag_engine

        assert wcag_engine is not None

    def test_validate_and_repair_not_implemented(self):
        """Test validate_and_repair raises NotImplementedError."""
        from services.wcag_engine import validate_and_repair

        with pytest.raises(NotImplementedError):
            validate_and_repair({}, [], {}, {})

    def test_validate_heading_hierarchy_not_implemented(self):
        """Test validate_heading_hierarchy raises NotImplementedError."""
        from services.wcag_engine import validate_heading_hierarchy

        with pytest.raises(NotImplementedError):
            validate_heading_hierarchy([])

    def test_enforce_list_structure_not_implemented(self):
        """Test enforce_list_structure raises NotImplementedError."""
        from services.wcag_engine import enforce_list_structure

        with pytest.raises(NotImplementedError):
            enforce_list_structure([])

    def test_validate_alt_text_presence_not_implemented(self):
        """Test validate_alt_text_presence raises NotImplementedError."""
        from services.wcag_engine import validate_alt_text_presence

        with pytest.raises(NotImplementedError):
            validate_alt_text_presence([], {})

    def test_build_structure_tree_not_implemented(self):
        """Test build_structure_tree raises NotImplementedError."""
        from services.wcag_engine import build_structure_tree

        with pytest.raises(NotImplementedError):
            build_structure_tree([])

    def test_generate_compliance_report_not_implemented(self):
        """Test generate_compliance_report raises NotImplementedError."""
        from services.wcag_engine import generate_compliance_report

        with pytest.raises(NotImplementedError):
            generate_compliance_report({})
