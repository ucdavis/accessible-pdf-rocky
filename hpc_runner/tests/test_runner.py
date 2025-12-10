"""Tests for HPC runner."""

import json
import sys
import pytest
from pathlib import Path

# Add parent directory to path to import runner
sys.path.insert(0, str(Path(__file__).parent.parent))

from runner import analyze_pdf, main


def test_analyze_pdf():
    """Test PDF analysis function."""
    result = analyze_pdf("/fake/path.pdf", "job-123")
    
    assert result["job_id"] == "job-123"
    assert result["pdf_path"] == "/fake/path.pdf"
    assert result["status"] == "completed"
    assert "issues" in result
    assert isinstance(result["issues"], list)


def test_analyze_pdf_returns_dict():
    """Test that analyze_pdf returns a dictionary."""
    result = analyze_pdf("test.pdf", "test-job")
    assert isinstance(result, dict)
    assert all(key in result for key in ["job_id", "pdf_path", "status", "issues"])


def test_main_missing_pdf(monkeypatch, capsys):
    """Test main function with missing PDF file."""
    # Mock sys.argv
    monkeypatch.setattr(
        "sys.argv",
        ["runner.py", "/nonexistent/file.pdf", "--job-id", "test-123"]
    )
    
    # Should exit with code 1
    with pytest.raises(SystemExit) as exc_info:
        main()
    
    assert exc_info.value.code == 1
    
    captured = capsys.readouterr()
    assert "Error: PDF file not found" in captured.err


def test_main_with_output_file(monkeypatch, tmp_path):
    """Test main function writes output to file."""
    # Create a temporary PDF file
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_text("fake pdf content")
    
    # Create output path
    output_file = tmp_path / "output.json"
    
    # Mock sys.argv
    monkeypatch.setattr(
        "sys.argv",
        [
            "runner.py",
            str(pdf_file),
            "--job-id",
            "test-123",
            "--output",
            str(output_file),
        ]
    )
    
    # Run main
    exit_code = main()
    
    assert exit_code == 0
    assert output_file.exists()
    
    # Verify output JSON
    with open(output_file) as f:
        data = json.load(f)
    
    assert data["job_id"] == "test-123"
    assert data["pdf_path"] == str(pdf_file)
