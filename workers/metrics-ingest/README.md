# Metrics Ingestion Worker

Cloudflare Worker that receives metrics from HPC and the .NET server, stores them in D1, and exposes a Prometheus-compatible endpoint.

## Quick Start

```bash
# Install dependencies
npm install

# Login to Cloudflare
npx wrangler login

# Create D1 database
npm run db:create
# Copy the database_id and update wrangler.toml

# Apply schema
npm run db:migrate

# Set authentication token
npx wrangler secret put METRICS_AUTH_TOKEN

# Deploy
npm run deploy
```

## API Endpoints

### `POST /ingest`

Receive metrics from sources (HPC, .NET server).

**Authentication:** Bearer token required

**Request:**

```json
{
  "source": "hpc",
  "timestamp": 1702345678,
  "metrics": {
    "slurm_pending_jobs": 42,
    "slurm_running_jobs": 10
  }
}
```

**Validation:**

- `timestamp` must be a Unix timestamp (seconds) within acceptable range:
  - Not more than 1 year in the past
  - Not more than 1 hour in the future

**Response:**

```json
{
  "status": "ok",
  "inserted": 2
}
```

### `GET /metrics`

Prometheus-compatible metrics export.

**Response:** Prometheus text format

```
# HELP slurm_pending_jobs Metric from hpc
# TYPE slurm_pending_jobs gauge
slurm_pending_jobs{source="hpc"} 42 1702345678000
```

### `GET /api/metrics?source=hpc&window=1h&metric=slurm_pending_jobs`

JSON API for custom dashboards.

**Query Parameters:**

- `source` (optional): Filter by source (hpc, server)
- `window` (optional): Time window (1m, 5m, 1h, 1d) - default 1h
- `metric` (optional): Filter by metric name
- `limit` (optional): Maximum rows to return (1-50000, default 10000)

**Response:**

```json
[
  {
    "source": "hpc",
    "timestamp": 1702345678,
    "metric_name": "slurm_pending_jobs",
    "metric_value": 42
  }
]
```

### `GET /api/sources`

List active metric sources.

**Response:**

```json
["hpc", "server"]
```

## Development

```bash
# Run locally
npm run dev

# Test locally
curl http://localhost:8787/metrics

# View logs
npm run tail
```

## Database

### Schema

```sql
CREATE TABLE metrics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,
  timestamp INTEGER NOT NULL,
  metric_name TEXT NOT NULL,
  metric_value REAL NOT NULL,
  created_at INTEGER DEFAULT (strftime('%s', 'now'))
);
```

### Management

```bash
# Query database
npm run db:query "SELECT * FROM metrics LIMIT 10"

# Local development database
npm run db:migrate:local
npm run db:query:local "SELECT COUNT(*) FROM metrics"
```

## Configuration

### Environment Variables

Set via Wrangler secrets:

- `METRICS_AUTH_TOKEN` - Bearer token for authentication

Optional variables (set in `wrangler.toml` under `[vars]`):

- `METRICS_RETENTION_DAYS` - Number of days to retain metrics (default: 7)
- `ALLOWED_ORIGIN` - CORS Access-Control-Allow-Origin header (default: '*')

### Data Retention

The worker automatically cleans up old metrics using a Cron Trigger:

- **Schedule:** Daily at 2 AM UTC
- **Default retention:** 7 days
- **Configurable:** Set `METRICS_RETENTION_DAYS` in wrangler.toml

Example:

```toml
[vars]
METRICS_RETENTION_DAYS = "30"  # Keep metrics for 30 days
```

Manual cleanup:

```bash
# Delete metrics older than 7 days
npm run db:query "DELETE FROM metrics WHERE timestamp < strftime('%s', 'now', '-7 days')"
```

### Wrangler.toml

```toml
name = "metrics-ingest"
main = "src/index.ts"

[[d1_databases]]
binding = "METRICS_DB"
database_name = "metrics-db"
database_id = "YOUR_DATABASE_ID"
```

## Deployment

See [METRICS_DEPLOYMENT.md](../../docs/METRICS_DEPLOYMENT.md) for complete setup instructions.

## Monitoring

- **Cloudflare Dashboard:** View request metrics, errors
- **Worker Logs:** `npm run tail`
- **D1 Usage:** Cloudflare Dashboard → D1 → metrics-db

## Free Tier Limits

- **D1:**
  - 5GB storage
  - 5M reads/day
  - 100K writes/day
- **Workers:**
  - 100K requests/day
  - 10ms CPU time/request

**Estimated usage:**

- HPC: 1,440 writes/day (1/min)
- FastAPI: ~10,000 writes/day
- Prometheus: ~2,880 reads/day (1/30s)
- **Total: Well within free tier**

## License

Same as parent project.
