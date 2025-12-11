# Push-Based Metrics Deployment Guide

This guide covers deploying the push-based metrics system using Cloudflare Workers and D1.

## Architecture Overview

```mermaid
flowchart TD
    HPC["HPC SLURM Cluster<br/>(Cron Job)<br/>Push Metrics"] -->|HTTPS POST<br/>/ingest| Worker
    
    .NET API[".NET API Controller<br/>Push Metrics"] -->|HTTPS POST<br/>/ingest| Worker
    
    Worker["Cloudflare Worker<br/>Metrics Ingest<br/>• D1 Storage<br/>• Token Auth<br/>• /ingest endpoint<br/>• /metrics endpoint"] --> D1
    
    D1["D1 Database<br/>Metrics Storage<br/>• 7-day retention<br/>• Free tier"]
    
    Worker -->|Prometheus format<br/>/metrics| Monitoring
    
    Monitoring["Prometheus + Grafana<br/>• Scrapes /metrics<br/>• Visualizations<br/>• Alerting"]
    
    style HPC fill:#ff9999,stroke:#cc0000,stroke-width:3px,color:#000
    style .NET API fill:#90ee90,stroke:#228b22,stroke-width:3px,color:#000
    style Worker fill:#80d4ff,stroke:#0066cc,stroke-width:3px,color:#000
    style D1 fill:#80d4ff,stroke:#0066cc,stroke-width:3px,color:#000
    style Monitoring fill:#ffeb99,stroke:#cc9900,stroke-width:3px,color:#000
```

**Key Benefits:**

- ✅ No inbound connections to HPC or .NET API
- ✅ HPC only needs outbound HTTPS (firewall-friendly)
- ✅ Free tier (D1 + Workers)
- ✅ Secure (token-based authentication)
- ✅ Centralized metrics storage

## Prerequisites

- Node.js 18+ and npm
- Cloudflare account (free tier works)
- Wrangler CLI: `npm install -g wrangler`

## Step 1: Deploy Cloudflare Worker

### 1.1 Install Dependencies

```bash
cd workers/metrics-ingest
npm install
```

### 1.2 Create D1 Database

```bash
npm run db:create
```

This outputs something like:

```
✅ Successfully created DB 'metrics-db'!
📋 Database ID: abc123-def456-ghi789
```

Copy the `database_id` and update `wrangler.toml`:

```toml
[[d1_databases]]
binding = "METRICS_DB"
database_name = "metrics-db"
database_id = "abc123-def456-ghi789"  # Paste your ID here
```

### 1.3 Apply Database Schema

```bash
npm run db:migrate
```

### 1.4 Generate and Set Authentication Token

```bash
# Generate a secure random token
openssl rand -base64 32

# Set as secret in Cloudflare
npx wrangler secret put METRICS_AUTH_TOKEN
# Paste the generated token when prompted
```

**IMPORTANT:** Save this token securely - you'll need it for HPC and .NET API configuration.

### 1.5 Deploy Worker

```bash
npm run deploy
```

Output:

```
✨ Published metrics-ingest (1.23s)
   https://metrics-ingest.<your-account>.workers.dev
```

### 1.6 Test the Worker

```bash
# Get the metrics endpoint (should return empty initially)
curl https://metrics-ingest.<your-account>.workers.dev/metrics

# Test ingestion (replace YOUR_TOKEN)
curl -X POST https://metrics-ingest.<your-account>.workers.dev/ingest \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "test",
    "timestamp": '$(date +%s)',
    "metrics": {
      "test_metric": 42
    }
  }'

# Verify it was stored
curl https://metrics-ingest.<your-account>.workers.dev/metrics
```

### 1.7 (Optional) Configure Custom Domain

```bash
# Add route in wrangler.toml
routes = [
  { pattern = "metrics.yourdomain.com/*", zone_name = "yourdomain.com" }
]

# Redeploy
npm run deploy
```

## Step 2: Configure HPC Metrics Push

### 2.1 Update Script Configuration

Edit `.NET server/hpc/scripts/export_slurm_metrics.sh`:

```bash
# Replace these values
METRICS_ENDPOINT="https://metrics-ingest.<your-account>.workers.dev/ingest"
METRICS_TOKEN="<your-token-from-step-1.4>"
```

**Security Best Practice:** Store token in a secure file:

```bash
# On HPC login node
echo "export METRICS_TOKEN='your-token-here'" > ~/.metrics_token
chmod 600 ~/.metrics_token

# Update crontab to source it
crontab -e
# Add:
BASH_ENV=/home/youruser/.metrics_token
* * * * * /usr/local/bin/export_slurm_metrics.sh
```

### 2.2 Install Script on HPC

```bash
# From your local machine
scp .NET server/hpc/scripts/export_slurm_metrics.sh user@hpc-login.ucdavis.edu:/tmp/

# On HPC login node
ssh user@hpc-login.ucdavis.edu
sudo cp /tmp/export_slurm_metrics.sh /usr/local/bin/
sudo chmod 755 /usr/local/bin/export_slurm_metrics.sh
sudo chown root:root /usr/local/bin/export_slurm_metrics.sh
```

### 2.3 Test Script Manually

```bash
# On HPC login node
export METRICS_ENDPOINT="https://metrics-ingest.<your-account>.workers.dev/ingest"
export METRICS_TOKEN="your-token-here"
/usr/local/bin/export_slurm_metrics.sh

# Should output nothing on success
echo $?  # Should print 0
```

### 2.4 Add to Cron

```bash
# On HPC login node
crontab -e

# Add this line (runs every minute):
# Sources token from secure file instead of exposing in crontab
* * * * * . ~/.metrics_token && /usr/local/bin/export_slurm_metrics.sh >> /var/log/slurm_metrics.log 2>&1
```

**Security Note:** This sources the token from `~/.metrics_token` (created in step 2.1) instead of embedding it in the crontab, which would expose it via `ps` or process listings.

**Note:** Check with your HPC admin for proper log directory permissions.

### 2.5 Verify Metrics are Flowing

Wait 1-2 minutes, then:

```bash
# Check if metrics are being pushed
curl https://metrics-ingest.<your-account>.workers.dev/api/sources
# Should show: ["hpc"]

# Get latest HPC metrics
curl "https://metrics-ingest.<your-account>.workers.dev/api/metrics?source=hpc&window=5m"
```

## Step 3: Configure .NET API Controller

### 3.1 Set Environment Variables

For Azure Container Apps:

```bash
az containerapp update \
  --name accessible-pdf-.NET server \
  --resource-group your-rg \
  --set-env-vars \
    METRICS_ENDPOINT="https://metrics-ingest.<your-account>.workers.dev/ingest" \
    METRICS_TOKEN="your-token-here"
```

For local development:

```bash
# In .NET server/.env
METRICS_ENDPOINT=https://metrics-ingest.<your-account>.workers.dev/ingest
METRICS_TOKEN=your-token-here
```

### 3.2 Update pyproject.toml

Ensure `httpx` is in dependencies:

```toml
[project]
dependencies = [
    "fastapi",
    "httpx",  # Add if not present
    # ... other deps
]
```

### 3.3 Install Dependencies

```bash
cd .NET server
uv sync
```

### 3.4 Test Metrics Push

```bash
# Start .NET API locally
cd .NET server
uv run uvicorn main:app --reload

# In another terminal, trigger a metric
python -c "
import asyncio
from metrics import push_metrics

async def test():
    await push_metrics({
        'test_metric': 123.45
    })

asyncio.run(test())
"

# Verify in Cloudflare
curl "https://metrics-ingest.<your-account>.workers.dev/api/metrics?source=fastapi&window=5m"
```

## Step 4: Configure Prometheus & Grafana

### 4.1 Update prometheus.yml

```yaml
global:
  scrape_interval: 30s

scrape_configs:
  - job_name: 'cloudflare-metrics'
    static_configs:
      - targets: ['metrics-ingest.<your-account>.workers.dev']
    scheme: https
    metrics_path: '/metrics'
    scrape_interval: 60s
```

### 4.2 Reload Prometheus

```bash
# Send SIGHUP to reload config
kill -HUP $(pidof prometheus)

# Or restart
systemctl restart prometheus
```

### 4.3 Verify in Prometheus

Visit `http://prometheus:9090/targets` and verify:

- Target is UP
- Last scrape successful

### 4.4 Query Metrics

In Prometheus query interface:

```promql
# See all metrics from HPC
{source="hpc"}

# Job queue depth
slurm_pending_jobs

# Submission latency
slurm_submission_latency_seconds
```

### 4.5 Import Grafana Dashboard

1. Open Grafana → Dashboards → Import
2. Upload `docs/grafana-dashboard.json`
3. Select Prometheus data source
4. Click Import

## Step 5: Monitoring & Maintenance

### 5.1 View Worker Logs

```bash
cd workers/metrics-ingest
npm run tail
```

### 5.2 Check Metrics Volume

```bash
# See which sources are active
curl https://metrics-ingest.<your-account>.workers.dev/api/sources

# Get metrics count (rough estimate)
npx wrangler d1 execute metrics-db --command "SELECT COUNT(*) FROM metrics"
```

### 5.3 Database Cleanup

Metrics older than 7 days should be cleaned up to stay within free tier:

```bash
# Create cleanup script
cat > workers/metrics-ingest/cleanup.sql <<EOF
DELETE FROM metrics 
WHERE timestamp < strftime('%s', 'now', '-7 days');
EOF

# Run via cron (weekly)
npx wrangler d1 execute metrics-db --file=cleanup.sql
```

Or add to Worker as a scheduled job:

```typescript
// In wrangler.toml
[triggers]
crons = ["0 2 * * 0"]  # Every Sunday at 2am

// In src/index.ts
export default {
  async scheduled(event, env, ctx) {
    await env.METRICS_DB.prepare(`
      DELETE FROM metrics 
      WHERE timestamp < strftime('%s', 'now', '-7 days')
    `).run();
  }
}
```

### 5.4 Token Rotation

To rotate the authentication token:

```bash
# Generate new token
NEW_TOKEN=$(openssl rand -base64 32)

# Update Cloudflare secret
npx wrangler secret put METRICS_AUTH_TOKEN
# Paste new token

# Update HPC script (in ~/.metrics_token or crontab)
# Update .NET API environment variables
# Both should continue working during rotation window
```

## Troubleshooting

### HPC metrics not appearing

```bash
# On HPC login node, check last run
tail /var/log/slurm_metrics.log

# Test manually
export METRICS_TOKEN='your-token'
export METRICS_ENDPOINT='https://...'
/usr/local/bin/export_slurm_metrics.sh

# Check if squeue/sacct work
squeue -h | wc -l
```

### .NET API metrics not appearing

```bash
# Check environment variables
az containerapp show --name accessible-pdf-.NET server \
  --resource-group your-rg \
  --query "properties.configuration.secrets" -o json

# Check logs
az containerapp logs tail --name accessible-pdf-.NET server \
  --resource-group your-rg --follow
```

### Worker errors

```bash
# Check Worker logs
cd workers/metrics-ingest
npm run tail

# Check D1 database
npx wrangler d1 execute metrics-db --command "SELECT * FROM metrics LIMIT 10"
```

### Prometheus not scraping

```bash
# Test endpoint manually
curl https://metrics-ingest.<your-account>.workers.dev/metrics

# Check Prometheus logs
journalctl -u prometheus -f

# Verify target in Prometheus UI
# http://prometheus:9090/targets
```

## Security Considerations

1. **Token Storage**
   - Never commit tokens to git
   - Use environment variables or secure vaults
   - Rotate tokens periodically (quarterly)

2. **Network Security**
   - Worker endpoint is public (by design for push-based)
   - Authentication required via Bearer token
   - Rate limiting automatic via Cloudflare

3. **Data Retention**
   - Keep 7 days max to stay in free tier
   - For longer retention, export to external storage

4. **Access Control**
   - Only HPC and .NET API need write access (via token)
   - Prometheus has read-only access (public /metrics)
   - Consider adding IP allowlist if needed

## Cost Estimate

**Cloudflare (D1 + Workers)**

- Storage: 5GB free ≈ millions of metrics
- Reads: 5M/day free ≈ Prometheus scraping every 30s
- Writes: 100K/day free ≈ HPC (1/min) + .NET API (1000/hr)
- **Expected Cost: $0/month**

**Prometheus/Grafana**

- Self-hosted: VM costs (~$20-50/month)
- Managed Grafana Cloud: Free tier available
- Azure Managed Grafana: ~$200/month

## Next Steps

1. Set up alerting rules in Prometheus (see docs/MONITORING_SETUP.md)
2. Create custom Grafana dashboards for your metrics
3. Add more metrics as needed in .NET API .NET server
4. Consider adding Azure metrics if deployed there

## References

- [Cloudflare D1 Documentation](https://developers.cloudflare.com/d1/)
- [Cloudflare Workers](https://developers.cloudflare.com/workers/)
- [Prometheus Documentation](https://prometheus.io/docs/)
