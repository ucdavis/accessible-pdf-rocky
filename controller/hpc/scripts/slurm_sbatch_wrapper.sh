#!/bin/bash
# SLURM sbatch wrapper for restricted SSH command
#
# SECURITY: This script is the ONLY command that can be executed
# by the FastAPI SSH key. It validates that:
# 1. Script path is in allowed directory
# 2. No argument injection is possible
# 3. Only sbatch is executed
#
# INSTALLATION (on HPC login node):
# 1. Copy to: /usr/local/bin/slurm_sbatch_wrapper.sh
# 2. chmod 755 /usr/local/bin/slurm_sbatch_wrapper.sh
# 3. chown root:root /usr/local/bin/slurm_sbatch_wrapper.sh
#
# SSH KEY SETUP:
# In ~slurm_submit/.ssh/authorized_keys:
# command="/usr/local/bin/slurm_sbatch_wrapper.sh",no-agent-forwarding,no-port-forwarding,no-pty ssh-ed25519 AAAA...

set -euo pipefail

# Script path must be first argument
SCRIPT="${1:-}"

if [ -z "$SCRIPT" ]; then
	echo "ERROR: No script path provided" >&2
	exit 1
fi

# Canonicalize path to prevent traversal
SCRIPT_REAL=$(realpath -m "$SCRIPT" 2>/dev/null) || {
	echo "ERROR: Invalid path: $SCRIPT" >&2
	exit 1
}

# Validate script is in allowed directory
# CRITICAL: Only scripts in /home/slurm_submit/jobs/ can be submitted
case "$SCRIPT_REAL" in
/home/slurm_submit/jobs/*.sh)
	# Valid path
	;;
*)
	echo "ERROR: Script not in allowed directory: $SCRIPT_REAL" >&2
	echo "ERROR: Only /home/slurm_submit/jobs/*.sh allowed" >&2
	exit 1
	;;
esac

# Validate script exists
if [ ! -f "$SCRIPT_REAL" ]; then
	echo "ERROR: Script does not exist: $SCRIPT_REAL" >&2
	exit 1
fi

# Validate script is readable
if [ ! -r "$SCRIPT_REAL" ]; then
	echo "ERROR: Script is not readable: $SCRIPT_REAL" >&2
	exit 1
fi

# Execute sbatch with the validated script
# No additional arguments are allowed (prevents injection)
exec /usr/bin/sbatch "$SCRIPT_REAL"
