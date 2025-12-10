#!/bin/bash
#SBATCH --job-name=${JOB_ID}
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu
#SBATCH --time=02:00:00
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err

# SLURM job script for PDF accessibility processing
# This script:
# 1. Downloads PDF from R2 using presigned URL
# 2. Processes PDF using hpc_runner
# 3. Uploads result back to R2 using presigned URL

set -e # Exit on error

# Set up temporary working directory
WORK_DIR=$(mktemp -d)
cd "$WORK_DIR"

echo "Job ID: $JOB_ID"
echo "Working directory: $WORK_DIR"

# Download PDF from R2 using presigned URL
echo "Downloading PDF from R2..."
curl -f -o input.pdf "$INPUT_URL"

if [ ! -f input.pdf ]; then
	echo "Error: Failed to download PDF from R2" >&2
	exit 1
fi

# Change to hpc_runner directory
cd "$HOME"/accessible-pdf-rocky/hpc_runner || exit 1

# Run PDF analysis using uv
echo "Running PDF accessibility analysis..."
uv run runner.py "$WORK_DIR"/input.pdf \
	--job-id "$JOB_ID" \
	--output "$WORK_DIR"/output.pdf

if [ ! -f "$WORK_DIR"/output.pdf ]; then
	echo "Error: PDF processing failed - no output file" >&2
	exit 1
fi

# Upload result to R2 using presigned URL
echo "Uploading result to R2..."
curl -f -X PUT --upload-file "$WORK_DIR"/output.pdf "$OUTPUT_URL"

# Cleanup
echo "Cleaning up temporary files..."
rm -rf "$WORK_DIR"

echo "Job completed successfully"
