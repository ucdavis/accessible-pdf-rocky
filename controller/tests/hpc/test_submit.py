"""Tests for HPC SLURM submission."""

from pathlib import Path


def test_submit_placeholder():
    """Placeholder test for SLURM submission.

    TODO: Implement once hpc/submit.py has actual implementation.
    """
    # For now, just verify the script exists
    script_path = Path(__file__).parent.parent.parent / "hpc" / "scripts" / "job.sh"
    assert script_path.exists()
    assert script_path.is_file()


def test_slurm_script_executable():
    """Test that SLURM job script is executable."""
    script_path = Path(__file__).parent.parent.parent / "hpc" / "scripts" / "job.sh"
    assert script_path.stat().st_mode & 0o111  # Check any execute bit is set
