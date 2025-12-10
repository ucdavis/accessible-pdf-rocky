#!/bin/bash
#SBATCH --job-name=${JOB_ID}
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu
#SBATCH --time=02:00:00
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err

# Change to hpc_runner directory
cd "$HOME"/accessible-pdf-rocky/hpc_runner || exit 1

# Run using uv
uv run runner.py "$PDF_PATH" \
	--job-id "$JOB_ID" \
	--output results/"${JOB_ID}".json
