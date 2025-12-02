# Docker Deployment Guide

## Overview

This guide explains how to build and run the Meeting Scheduler API using Docker.

## Requirements

- Docker 20.10 or higher
- Docker Compose 2.0 or higher (optional, for docker-compose setup)

## Quick Start

### 1. Build the Docker Image

```bash
docker build -t meeting-scheduler:latest .
```

### 2. Run the Container

```bash
docker run -d \
  --name meeting-scheduler \
  -p 8000:8000 \
  -v meeting-data:/data \
  meeting-scheduler:latest
```

### 3. Access the API

The API will be available at: `http://localhost:8000/api/`

## Configuration

### Environment Variables

The following environment variables can be configured:

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key for security | (required) |
| `DJANGO_DEBUG` | Enable debug mode | `False` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `localhost,127.0.0.1` |
| `DATABASE_PATH` | Path to SQLite database file | `/data/db.sqlite3` |
| `PORT` | Port to run the server on | `8000` |

### Using Environment Variables

**Option 1: Command Line**

```bash
docker run -d \
  --name meeting-scheduler \
  -p 8000:8000 \
  -e DJANGO_SECRET_KEY="your-secret-key" \
  -e DJANGO_DEBUG="False" \
  -e DJANGO_ALLOWED_HOSTS="localhost,yourdomain.com" \
  -v meeting-data:/data \
  meeting-scheduler:latest
```

**Option 2: Environment File**

Create a `.env` file:

```bash
cp .env.example .env
# Edit .env with your values
```

Run with env file:

```bash
docker run -d \
  --name meeting-scheduler \
  -p 8000:8000 \
  --env-file .env \
  -v meeting-data:/data \
  meeting-scheduler:latest
```

## Docker Image Details

### Multi-Stage Build

The Dockerfile uses a multi-stage build to optimize image size:

1. **Builder Stage**: Installs build dependencies and Python packages
2. **Runtime Stage**: Copies only necessary files and runtime dependencies

This results in a smaller final image (~200MB vs ~500MB).

### Base Image

- **Base**: `python:3.11-slim`
- **Python Version**: 3.11
- **OS**: Debian-based slim image

### Exposed Ports

- **8000**: HTTP API server

### Volumes

- **/data**: Database storage directory
  - Contains `db.sqlite3` file
  - Should be mounted as a volume for data persistence

## Database Migrations

Database migrations run automatically on container startup via the entrypoint script.

To run migrations manually:

```bash
docker exec meeting-scheduler python manage.py migrate
```

## Container Management

### Start Container

```bash
docker start meeting-scheduler
```

### Stop Container

```bash
docker stop meeting-scheduler
```

### View Logs

```bash
docker logs meeting-scheduler

# Follow logs
docker logs -f meeting-scheduler
```

### Access Container Shell

```bash
docker exec -it meeting-scheduler bash
```

### Remove Container

```bash
docker stop meeting-scheduler
docker rm meeting-scheduler
```

## Data Persistence

### Using Named Volumes (Recommended)

```bash
# Create named volume
docker volume create meeting-data

# Run container with named volume
docker run -d \
  --name meeting-scheduler \
  -p 8000:8000 \
  -v meeting-data:/data \
  meeting-scheduler:latest

# Backup volume
docker run --rm \
  -v meeting-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/meeting-data-backup.tar.gz -C /data .

# Restore volume
docker run --rm \
  -v meeting-data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/meeting-data-backup.tar.gz -C /data
```

### Using Bind Mounts

```bash
# Create local directory
mkdir -p ./data

# Run container with bind mount
docker run -d \
  --name meeting-scheduler \
  -p 8000:8000 \
  -v $(pwd)/data:/data \
  meeting-scheduler:latest
```

## Production Deployment

### Security Considerations

1. **Secret Key**: Always use a strong, random secret key
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **Debug Mode**: Set `DJANGO_DEBUG=False` in production

3. **Allowed Hosts**: Configure `DJANGO_ALLOWED_HOSTS` with your domain

4. **HTTPS**: Use a reverse proxy (nginx, traefik) for HTTPS

### Recommended Production Setup

```bash
docker run -d \
  --name meeting-scheduler \
  --restart unless-stopped \
  -p 8000:8000 \
  -e DJANGO_SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" \
  -e DJANGO_DEBUG="False" \
  -e DJANGO_ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com" \
  -v meeting-data:/data \
  meeting-scheduler:latest
```

### Using with Reverse Proxy (nginx)

Example nginx configuration:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Health Checks

Check if the container is running:

```bash
docker ps | grep meeting-scheduler
```

Check API health:

```bash
curl http://localhost:8000/api/meetings/
```

## Troubleshooting

### Container Won't Start

Check logs:
```bash
docker logs meeting-scheduler
```

### Database Issues

Reset database:
```bash
docker exec meeting-scheduler rm /data/db.sqlite3
docker restart meeting-scheduler
```

### Permission Issues

Ensure the data directory has proper permissions:
```bash
docker exec meeting-scheduler ls -la /data
```

### Port Already in Use

Change the host port:
```bash
docker run -d \
  --name meeting-scheduler \
  -p 8080:8000 \
  -v meeting-data:/data \
  meeting-scheduler:latest
```

## Building for Different Architectures

### Build for ARM64 (Apple Silicon, Raspberry Pi)

```bash
docker buildx build --platform linux/arm64 -t meeting-scheduler:arm64 .
```

### Build for AMD64 (Intel/AMD)

```bash
docker buildx build --platform linux/amd64 -t meeting-scheduler:amd64 .
```

### Multi-Architecture Build

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t meeting-scheduler:latest \
  --push \
  .
```

## Image Size Optimization

The multi-stage build reduces image size by:

1. Using `python:3.11-slim` instead of full Python image
2. Installing only runtime dependencies in final stage
3. Removing build tools and cache files
4. Using `.dockerignore` to exclude unnecessary files

Expected image size: ~200-250MB

## Development vs Production

### Development

```bash
docker run -d \
  --name meeting-scheduler-dev \
  -p 8000:8000 \
  -e DJANGO_DEBUG="True" \
  -v $(pwd):/app \
  -v meeting-data:/data \
  meeting-scheduler:latest
```

### Production

```bash
docker run -d \
  --name meeting-scheduler-prod \
  --restart unless-stopped \
  -p 8000:8000 \
  -e DJANGO_DEBUG="False" \
  -e DJANGO_SECRET_KEY="your-production-secret" \
  -v meeting-data:/data \
  meeting-scheduler:latest
```

## Next Steps

- See `DOCKER_COMPOSE_GUIDE.md` for docker-compose setup (Task 11)
- See `API_TESTING_GUIDE.md` for API documentation
- See `QUICK_TEST_COMMANDS.md` for testing the API

## Support

For issues or questions, please refer to the main README.md or open an issue.
