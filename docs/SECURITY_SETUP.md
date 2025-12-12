# Security Setup Guide

This document describes the security model for the **current** `accessible-pdf-rocky` repository.

The target architecture includes HPC/SLURM integration, but this repo does not yet contain any SSH/SLURM submission code or hardening scripts. Security guidance here focuses on what exists today: the .NET server and Cloudflare Workers.

## Current security model (repo today)

- **End-user authentication/authorization**: not implemented yet.
- **Database access**: protected behind a token-authenticated Worker (`workers/db-api`).
- **Metrics ingestion**: token-authenticated (`workers/metrics-ingest`), but the Prometheus scrape endpoint (`GET /metrics`) is public.
- **Secrets**: expected to be provided via environment variables and Cloudflare Worker secrets (not committed to git).

## Secrets and sensitive configuration

### Database API Worker (`workers/db-api`)

- `DB_AUTH_TOKEN` (Cloudflare Worker secret)
  - Used by: `workers/db-api`
  - Required for: all endpoints except `GET /health`
  - How to set (Cloudflare):

    ```bash
    cd workers/db-api
    npx wrangler secret put DB_AUTH_TOKEN
    ```

- `DB_API_URL` and `DB_API_TOKEN` (server configuration)
  - Used by: `server/` (`DatabaseApiClient`)
  - `DB_API_TOKEN` must match the Worker's `DB_AUTH_TOKEN`.
  - Example (local override): see `server/.env.example`.

### Metrics ingest Worker (`workers/metrics-ingest`)

- `METRICS_AUTH_TOKEN` (Cloudflare Worker secret)
  - Used by: `workers/metrics-ingest`
  - Required for: `POST /ingest`
  - How to set (Cloudflare):

    ```bash
    cd workers/metrics-ingest
    npx wrangler secret put METRICS_AUTH_TOKEN
    ```

- `METRICS_ENDPOINT` and `METRICS_TOKEN` (push clients)
  - Used by: the .NET server's `MetricsClient` (if you wire it into server logic) and any HPC cron script.
  - `METRICS_TOKEN` must match the Worker's `METRICS_AUTH_TOKEN`.
  - Note: if `METRICS_TOKEN` is empty, the .NET `MetricsClient` skips pushing metrics.

### CORS / allowed origins

- `.NET server`:
  - Configure `Cors:AllowedOrigins` (see `server/appsettings.Production.json`).
- Workers (`workers/db-api`, `workers/metrics-ingest`):
  - Optional `ALLOWED_ORIGIN` variable controls `Access-Control-Allow-Origin` (defaults to `*`).
  - In production, set `ALLOWED_ORIGIN` to the specific origin(s) you expect.

## Files that must never be committed

These are already ignored by git (see `../.gitignore`), but treat them as sensitive:

- `.env`, `.env.*`
- `*.pem` and other private keys

Use `server/.env.example` as a starting point for local configuration.

## Local development defaults

Local/dev convenience settings are not production-safe:

- Docker/Dev Container flows commonly use `dev-token`.
- Do not reuse `dev-token` in any real environment.

## Production hardening checklist (before exposure)

1. Replace all dev tokens with strong random tokens (e.g. `openssl rand -base64 32`).
2. Restrict CORS:
   - `.NET server`: set `Cors:AllowedOrigins`.
   - Workers: set `ALLOWED_ORIGIN`.
3. Decide how to protect public endpoints:
   - The `.NET server` is currently unauthenticated.
   - The edge API worker under `workers/api/*` has no auth and must not be treated as production-ready.
4. Consider whether `GET /metrics` should be public:
   - It is public by design for Prometheus scraping.
   - If you need to restrict access, add access control (e.g. Cloudflare Access) or implement auth on the Worker.
5. Rotate tokens periodically and on incident.
6. Use CI security tooling:
   - `just audit` (npm audit + pip-audit)
   - GitHub workflows include CodeQL and Dependabot.

## Incident response (token compromise)

- Rotate the relevant Worker secret and redeploy.
- Update server/HPC environments to use the new token.
- Inspect recent Worker logs (`npm run tail` inside the Worker directory) and D1 tables.

## Future: HPC / SLURM hardening

When HPC/SLURM integration is implemented, follow least-privilege patterns (dedicated user, forced-command SSH keys, allowlisted `sbatch`, no-pty/no-port-forwarding, etc.).

## References

- `workers/db-api/README.md`
- `workers/metrics-ingest/README.md`
- [Metrics Deployment](./METRICS_DEPLOYMENT.md)
