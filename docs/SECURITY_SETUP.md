# Security Setup Guide

This document describes the security hardening for FastAPI → HPC SLURM integration using restricted SSH commands.

## Overview

**Security Goal**: FastAPI should only be able to submit SLURM jobs — nothing else.

Even if FastAPI is compromised, attackers cannot:

- Run arbitrary commands on HPC
- Access user data
- Spawn shells
- Port forward or tunnel
- Access other HPC resources

## Architecture

```
FastAPI Controller → Restricted SSH Key → Forced Command Wrapper → sbatch only
```

## Implementation

### Step 1: Create Restricted User on HPC Login Node

```bash
# On HPC login node (as root)
sudo useradd -m slurm_submit
sudo mkdir -p /home/slurm_submit/jobs
sudo chown slurm_submit:slurm_submit /home/slurm_submit/jobs
sudo chmod 700 /home/slurm_submit/jobs
```

This user:

- Has a home directory
- Has a dedicated jobs directory
- Cannot login interactively (no shell access via normal means)

### Step 2: Install Command Wrapper

```bash
# Copy wrapper script to system location
sudo cp controller/hpc/scripts/slurm_sbatch_wrapper.sh /usr/local/bin/
sudo chmod 755 /usr/local/bin/slurm_sbatch_wrapper.sh
sudo chown root:root /usr/local/bin/slurm_sbatch_wrapper.sh
```

The wrapper script (`/usr/local/bin/slurm_sbatch_wrapper.sh`):

- Validates script path is in `/home/slurm_submit/jobs/`
- Prevents path traversal attacks
- Prevents argument injection
- Only executes `sbatch` — nothing else

### Step 3: Generate SSH Key for FastAPI

```bash
# On FastAPI server (or wherever controller runs)
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_slurm_submit -C "fastapi-slurm-submit"
```

**Important**:

- Use ed25519 (modern, secure, fast)
- Store private key securely
- Set in environment variable: `SLURM_SSH_KEY_PATH=/path/to/id_ed25519_slurm_submit`
- Never commit private key to git

### Step 4: Install Public Key with Forced Command

```bash
# On HPC login node
sudo su - slurm_submit
mkdir -p ~/.ssh
chmod 700 ~/.ssh
touch ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

Add to `~slurm_submit/.ssh/authorized_keys`:

```
command="/usr/local/bin/slurm_sbatch_wrapper.sh",no-agent-forwarding,no-port-forwarding,no-pty,no-X11-forwarding ssh-ed25519 AAAA... fastapi-slurm-submit
```

**Key restrictions:**

- `command=` — Forces execution of wrapper, ignores SSH command
- `no-agent-forwarding` — Prevents SSH agent forwarding
- `no-port-forwarding` — Prevents port tunneling
- `no-pty` — Prevents interactive terminal
- `no-X11-forwarding` — Prevents X11 forwarding

### Step 5: Configure FastAPI Environment

```bash
# On FastAPI server, create .env file
cat >> controller/.env <<EOF
SLURM_HOST=hpc-login.ucdavis.edu
SLURM_USER=slurm_submit
SLURM_SSH_KEY_PATH=/home/controller/.ssh/id_ed25519_slurm_submit
SLURM_REMOTE_SCRIPT_DIR=/home/slurm_submit/jobs
EOF
```

### Step 6: Test the Setup

```bash
# From FastAPI server, test SSH connection
ssh -i ~/.ssh/id_ed25519_slurm_submit slurm_submit@hpc-login.ucdavis.edu /home/slurm_submit/jobs/test.sh
```

Expected behavior:

- ✅ If script exists in `/home/slurm_submit/jobs/`, it submits to SLURM
- ❌ If script is elsewhere, it is rejected
- ❌ Trying to run other commands fails (wrapper always runs)

### Step 7: Create Template Job Script

```bash
# On HPC login node
sudo cp controller/hpc/scripts/job.sh /home/slurm_submit/jobs/job_template.sh
sudo chown slurm_submit:slurm_submit /home/slurm_submit/jobs/job_template.sh
sudo chmod 755 /home/slurm_submit/jobs/job_template.sh
```

FastAPI will:

1. Generate job-specific script with environment variables
2. Upload via SFTP to `/home/slurm_submit/jobs/job_<uuid>.sh`
3. Call wrapper via SSH to submit script
4. Clean up script after submission

## Security Validation

### Test 1: Verify Forced Command

```bash
# Try to run arbitrary command (should fail)
ssh -i ~/.ssh/id_ed25519_slurm_submit slurm_submit@hpc-login.ucdavis.edu "ls -la"
```

Expected: Wrapper rejects with "No script path provided"

### Test 2: Verify Path Validation

```bash
# Try to submit script outside allowed directory
ssh -i ~/.ssh/id_ed25519_slurm_submit slurm_submit@hpc-login.ucdavis.edu /tmp/malicious.sh
```

Expected: "Script not in allowed directory"

### Test 3: Verify No Shell Access

```bash
# Try to get interactive shell
ssh -i ~/.ssh/id_ed25519_slurm_submit slurm_submit@hpc-login.ucdavis.edu
```

Expected: Connection closes immediately (no-pty restriction)

## Monitoring and Alerts

### Failed Authentication Attempts

Monitor `/var/log/auth.log` on HPC login node:

```bash
# Setup alert for failed SSH attempts
tail -f /var/log/auth.log | grep "slurm_submit" | grep "Failed"
```

### Wrapper Script Violations

Monitor wrapper script rejections:

```bash
# Check for path validation failures
sudo journalctl -u sshd | grep "slurm_sbatch_wrapper" | grep "ERROR"
```

### Recommended Alerts

1. **Failed SSH authentication** → Immediate alert
2. **Path validation failures** → Immediate alert
3. **Unusual submission patterns** → Warning (e.g. >100 jobs/minute)

## Key Rotation

Rotate SSH keys every 90 days:

```bash
# 1. Generate new key
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_slurm_submit_new

# 2. Add new key to authorized_keys (keep old key)
# 3. Update FastAPI environment to use new key
# 4. Monitor for 24 hours
# 5. Remove old key from authorized_keys
```

## Incident Response

If FastAPI is compromised:

1. **Immediately revoke SSH key**:

   ```bash
   sudo su - slurm_submit
   # Remove compromised key from ~/.ssh/authorized_keys
   ```

2. **Check for malicious jobs**:

   ```bash
   squeue -u slurm_submit
   sacct -u slurm_submit --starttime now-7days
   ```

3. **Audit submitted scripts**:

   ```bash
   ls -lat /home/slurm_submit/jobs/
   ```

4. **Cancel suspicious jobs**:

   ```bash
   scancel -u slurm_submit
   ```

5. **Generate new key and re-deploy**

## Benefits of This Approach

✅ **Principle of Least Privilege**: FastAPI can only submit jobs, nothing else

✅ **Defense in Depth**: Multiple validation layers (SSH restrictions + wrapper validation)

✅ **Auditability**: All submissions logged via SSH and SLURM

✅ **Isolation**: Dedicated user prevents lateral movement

✅ **Revocable**: Single key can be revoked without affecting other systems

## References

- [OpenSSH authorized_keys](https://man.openbsd.org/sshd.8#AUTHORIZED_KEYS_FILE_FORMAT)
- [SLURM Security Guide](https://slurm.schedmd.com/security.html)
- [SSH Hardening](https://www.ssh.com/academy/ssh/sshd_config)
