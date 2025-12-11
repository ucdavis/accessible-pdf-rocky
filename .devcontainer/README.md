# Dev Container Configuration

This directory contains the configuration for developing accessible-pdf-rocky in a containerized environment using VS Code Dev Containers or GitHub Codespaces.

## What's Included

The dev container provides:

- **Node.js 20** - For client (React/Vite) and workers (Cloudflare Workers)
- **.NET 8.0 SDK** - For the ASP.NET Core server
- **Python 3.12 + uv** - For the HPC runner
- **Git** - Version control
- **Essential VS Code extensions** - C# Dev Kit, ESLint, Prettier, Ruff, etc.

## Services

The dev container runs multiple services:

1. **devcontainer** - Main development environment with all tools
2. **db-api** - Cloudflare Worker (Database API) running on port 8787

## Getting Started

### VS Code

1. Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. Open this project in VS Code
3. Click "Reopen in Container" when prompted (or use Command Palette: `Dev Containers: Reopen in Container`)
4. Wait for the container to build and setup to complete

### GitHub Codespaces

1. Navigate to the repository on GitHub
2. Click the green "Code" button
3. Select "Codespaces" tab
4. Click "Create codespace on [branch]"

## Port Forwarding

The following ports are automatically forwarded:

- **5173** - Vite Dev Server (React client)
- **5165** - ASP.NET HTTP API (server)
- **8787** - Database API Worker

## Development Workflow

Once the container is running, you can use the standard `just` commands:

```bash
# Start all services with Docker Compose
just dev

# Or start services individually for development:
just dev-client    # Start React dev server
just dev-server    # Start .NET server
just dev-workers   # Start workers in dev mode

# Run tests
just test

# Run linters
just lint

# See all available commands
just help
```

## Environment Variables

The dev container automatically sets:

- `ASPNETCORE_ENVIRONMENT=Development`
- `ASPNETCORE_URLS=http://0.0.0.0:5165`
- `DB_API_URL=http://db-api:8787`
- `DB_API_TOKEN=dev-token`

## Customization

- **devcontainer.json** - Main configuration (features, extensions, settings)
- **docker-compose.yml** - Service definitions
- **dev.Dockerfile** - Base image and system dependencies
- **setup.sh** - Post-create setup script
- **wait-for-db-api.sh** - Service readiness check

## Troubleshooting

### Container won't start

- Ensure Docker is running on your host machine
- Check Docker has enough resources allocated (at least 4GB RAM)
- Try rebuilding: Command Palette → `Dev Containers: Rebuild Container`

### Services not accessible

- Verify ports are forwarded in VS Code's "Ports" panel
- Check service logs: `docker compose logs [service-name]`

### Dependencies not installed

- Manually run setup: `bash .devcontainer/setup.sh`
- Check if the db-api service is healthy: `docker compose ps`

### Platform mismatch errors (workerd)

If you see errors like "workerd on another platform than the one you're currently using":

**Cause:** Host `node_modules` (macOS/Windows) conflicting with Linux container binaries.

**Solution:**
```bash
# Stop and remove all devcontainer volumes
docker compose -f .devcontainer/docker-compose.yml down -v

# Rebuild the container
# In VS Code: Command Palette → "Dev Containers: Rebuild Container"
# Or manually:
docker compose -f .devcontainer/docker-compose.yml build --no-cache
```

The devcontainer uses Docker volumes to isolate `node_modules` from the host, so dependencies are always installed fresh in the Linux environment.

### Tools not found (uv, just, etc.)

**VS Code users:** Node.js, .NET, and Python are installed by VS Code when it connects (via "features"). If tools are missing after connecting, try rebuilding.

**Manual testing:** To test the container without VS Code:
```bash
# Start the services
docker compose -f .devcontainer/docker-compose.yml up -d

# Verify tools are installed
docker exec -u vscode devcontainer-devcontainer-1 bash -c "uv --version && just --version"

# Clean up
docker compose -f .devcontainer/docker-compose.yml down
```
