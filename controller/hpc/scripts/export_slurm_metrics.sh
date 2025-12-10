#!/bin/bash
# Push SLURM metrics to Cloudflare Worker (D1 database)
#
# INSTALLATION (on HPC login node):
# 1. Copy to: /usr/local/bin/export_slurm_metrics.sh
# 2. chmod 755 /usr/local/bin/export_slurm_metrics.sh
# 3. Set environment variables (or edit script):
#    export METRICS_ENDPOINT="https://metrics.your-domain.workers.dev/ingest"
#    export METRICS_TOKEN="your-secure-token-here"
# 4. Add to crontab to run every minute:
#    * * * * * /usr/local/bin/export_slurm_metrics.sh
#
# SECURITY:
# - Store METRICS_TOKEN in a secure file with restricted permissions
# - Or use environment variables in crontab
# - No inbound connections required to HPC (push-based)

set -euo pipefail

# Configuration (can be overridden by environment variables)
METRICS_ENDPOINT="${METRICS_ENDPOINT:-https://metrics.your-domain.workers.dev/ingest}"
METRICS_TOKEN="${METRICS_TOKEN:-}"

# Validate configuration
if [ -z "$METRICS_TOKEN" ]; then
	echo "ERROR: METRICS_TOKEN not set" >&2
	exit 1
fi

# Collect SLURM metrics
PENDING=$(squeue -t PENDING -h 2>/dev/null | wc -l || echo 0)
RUNNING=$(squeue -t RUNNING -h 2>/dev/null | wc -l || echo 0)
COMPLETED=$(sacct -s COMPLETED -n --starttime=now-1hour 2>/dev/null | wc -l || echo 0)
FAILED=$(sacct -s FAILED -n --starttime=now-1hour 2>/dev/null | wc -l || echo 0)

# Get partition-specific metrics (optional)
GPU_PENDING=$(squeue -t PENDING -p gpu -h 2>/dev/null | wc -l || echo 0)
GPU_RUNNING=$(squeue -t RUNNING -p gpu -h 2>/dev/null | wc -l || echo 0)

# Get node availability (optional)
NODES_IDLE=$(sinfo -t idle -h 2>/dev/null | wc -l || echo 0)
NODES_ALLOC=$(sinfo -t alloc -h 2>/dev/null | wc -l || echo 0)
NODES_DOWN=$(sinfo -t down -h 2>/dev/null | wc -l || echo 0)

# Build JSON payload
TIMESTAMP=$(date +%s)
PAYLOAD=$(
	cat <<EOF
{
  "source": "hpc",
  "timestamp": ${TIMESTAMP},
  "metrics": {
    "slurm_pending_jobs": ${PENDING},
    "slurm_running_jobs": ${RUNNING},
    "slurm_completed_jobs_1h": ${COMPLETED},
    "slurm_failed_jobs_1h": ${FAILED},
    "slurm_gpu_pending_jobs": ${GPU_PENDING},
    "slurm_gpu_running_jobs": ${GPU_RUNNING},
    "slurm_nodes_idle": ${NODES_IDLE},
    "slurm_nodes_allocated": ${NODES_ALLOC},
    "slurm_nodes_down": ${NODES_DOWN}
  }
}
EOF
)

# Push metrics to Cloudflare Worker
RESPONSE=$(curl -X POST "${METRICS_ENDPOINT}" \
	-H "Authorization: Bearer ${METRICS_TOKEN}" \
	-H "Content-Type: application/json" \
	-d "${PAYLOAD}" \
	--max-time 10 \
	--silent \
	--show-error \
	--write-out "\nHTTP_CODE:%{http_code}" 2>&1)

# Check response
HTTP_CODE=$(echo "$RESPONSE" | grep -o "HTTP_CODE:[0-9]*" | cut -d: -f2)
if [ "${HTTP_CODE:-000}" -ne 200 ]; then
	echo "ERROR: Failed to push metrics (HTTP ${HTTP_CODE})" >&2
	echo "$RESPONSE" >&2
	exit 1
fi

# Optional: Log for debugging
# echo "$(date): Successfully pushed SLURM metrics" >> /var/log/slurm_metrics_export.log
