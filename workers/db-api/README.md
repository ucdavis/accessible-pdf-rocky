# Database API Worker

Cloudflare Worker that provides a REST API for D1 database operations. The FastAPI controller calls this worker for all database interactions.

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Create D1 Database

```bash
npm run db:create
```

Copy the `database_id` from the output and update it in `wrangler.toml`.

### 3. Apply Database Schema

```bash
npm run db:migrate
```

### 4. Set Authentication Token

```bash
# Generate a secure token
openssl rand -base64 32

# Set as secret
npx wrangler secret put DB_AUTH_TOKEN
# Paste the token when prompted
```

Save this token - you'll need to set it as `DB_API_TOKEN` in the FastAPI controller environment.

### 5. Deploy

```bash
npm run deploy
```

## API Endpoints

All endpoints require Bearer token authentication via `Authorization` header.

### Jobs

- `POST /jobs` - Create a new job
- `GET /jobs` - List jobs (supports `?status=`, `?user_id=`, `?limit=` query params)
- `GET /jobs/:id` - Get job by ID
- `PUT /jobs/:id` - Update job (status, slurm_id, results_url)
- `DELETE /jobs/:id` - Delete job

### Users

- `POST /users` - Create a new user
- `GET /users/:id` - Get user by ID

### Processing Metrics

- `POST /metrics` - Create processing metrics for a job

## Example Usage

```bash
# Create a job
curl -X POST https://db-api.your-account.workers.dev/jobs \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "r2_key": "uploads/example.pdf",
    "status": "submitted"
  }'

# Get job by ID
curl https://db-api.your-account.workers.dev/jobs/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_TOKEN"

# Update job status
curl -X PUT https://db-api.your-account.workers.dev/jobs/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "results_url": "https://r2.example.com/results/output.pdf"
  }'

# List jobs with filters
curl https://db-api.your-account.workers.dev/jobs?status=running&limit=10 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Development

### Local Development

```bash
# Start local dev server
npm run dev

# Apply schema to local database
npm run db:migrate:local

# Query local database
npm run db:query:local "SELECT * FROM jobs"
```

### View Logs

```bash
npm run tail
```

## Database Schema

See `schema.sql` for the complete database schema. Tables:

- `jobs` - Job tracking
- `users` - User management
- `processing_metrics` - Processing analytics

## Security

- All endpoints require Bearer token authentication
- Token is stored as a Cloudflare Workers secret
- CORS enabled for all origins (can be restricted if needed)
- D1 database is not directly accessible from the internet
