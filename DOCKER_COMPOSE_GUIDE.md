# Docker Compose Guide for Meeting Scheduler

## Overview

This guide explains how to use Docker Compose to run the Meeting Scheduler API in a containerized environment. Docker Compose simplifies the deployment process by managing the container configuration, volumes, and networking.

## Prerequisites

- Docker installed (version 20.10 or higher)
- Docker Compose installed (version 2.0 or higher)

### Check Installation

```bash
docker --version
docker-compose --version
```

---

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd meetingscheduler
```

### 2. Create Environment File

Copy the example environment file and customize it:

```bash
cp .env.example .env
```

Edit `.env` with your preferred settings:

```env
DJANGO_SECRET_KEY=your-super-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
DATABASE_PATH=/data/db.sqlite3
PORT=8000
```

### 3. Build and Start the Service

```bash
docker-compose up -d
```

This command will:
- Build the Docker image
- Create the necessary volumes
- Start the container in detached mode
- Run database migrations automatically
- Start the Django development server

### 4. Verify the Service is Running

```bash
# Check container status
docker-compose ps

# Check logs
docker-compose logs -f web

# Test the API
curl http://localhost:8000/api/meetings/
```

---

## Docker Compose Configuration

### Services

#### web
The main application service running the Django REST API.

**Configuration:**
- **Build Context**: Current directory
- **Container Name**: `meeting-scheduler`
- **Ports**: `8000:8000` (configurable via PORT env var)
- **Volumes**:
  - `meeting-data:/data` - Persistent database storage
  - `.:/app` - Code mounting for development (optional)
- **Health Check**: Polls `/api/meetings/` endpoint every 30 seconds
- **Restart Policy**: `unless-stopped`

### Volumes

#### meeting-data
Named volume for SQLite database persistence.

**Purpose:**
- Ensures database data persists across container restarts
- Prevents data loss when containers are removed
- Provides easy backup and restore capabilities

**Location:** Managed by Docker (typically in `/var/lib/docker/volumes/`)

### Networks

#### meeting-network
Bridge network for service communication.

**Purpose:**
- Isolates the application network
- Allows for future service additions (e.g., Redis, PostgreSQL)

---

## Common Commands

### Start Services

```bash
# Start in foreground (see logs)
docker-compose up

# Start in background (detached mode)
docker-compose up -d

# Rebuild and start
docker-compose up --build
```

### Stop Services

```bash
# Stop containers (keeps volumes)
docker-compose stop

# Stop and remove containers (keeps volumes)
docker-compose down

# Stop, remove containers, and remove volumes (DELETES DATA!)
docker-compose down -v
```

### View Logs

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View logs for specific service
docker-compose logs -f web

# View last 100 lines
docker-compose logs --tail=100
```

### Execute Commands in Container

```bash
# Open shell in container
docker-compose exec web bash

# Run Django management commands
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py shell

# Run tests
docker-compose exec web python manage.py test
```

### Check Service Health

```bash
# View container status and health
docker-compose ps

# Inspect health check details
docker inspect meeting-scheduler | grep -A 10 Health
```

---

## Environment Variables

### Required Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `DJANGO_SECRET_KEY` | Django secret key for cryptographic signing | `dev-secret-key-change-in-production` | `your-random-secret-key-here` |
| `DJANGO_DEBUG` | Enable/disable debug mode | `True` | `False` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `*` | `localhost,127.0.0.1,api.example.com` |
| `DATABASE_PATH` | Path to SQLite database file | `/data/db.sqlite3` | `/data/db.sqlite3` |
| `PORT` | Port to expose the service | `8000` | `8080` |

### Setting Environment Variables

**Option 1: .env File (Recommended)**

Create a `.env` file in the project root:

```env
DJANGO_SECRET_KEY=my-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_PATH=/data/db.sqlite3
PORT=8000
```

**Option 2: Export in Shell**

```bash
export DJANGO_SECRET_KEY=my-secret-key
export DJANGO_DEBUG=False
docker-compose up
```

**Option 3: Inline with Command**

```bash
DJANGO_DEBUG=False PORT=8080 docker-compose up
```

---

## Volume Management

### Backup Database

```bash
# Create backup directory
mkdir -p backups

# Copy database from volume
docker-compose exec web cp /data/db.sqlite3 /app/backups/db_backup_$(date +%Y%m%d_%H%M%S).sqlite3

# Or use docker cp
docker cp meeting-scheduler:/data/db.sqlite3 ./backups/db_backup_$(date +%Y%m%d_%H%M%S).sqlite3
```

### Restore Database

```bash
# Copy backup into container
docker cp ./backups/db_backup.sqlite3 meeting-scheduler:/data/db.sqlite3

# Restart service
docker-compose restart
```

### Inspect Volume

```bash
# List volumes
docker volume ls

# Inspect volume details
docker volume inspect meetingscheduler_meeting-data

# View volume contents (requires root access)
docker run --rm -v meetingscheduler_meeting-data:/data alpine ls -la /data
```

---

## Health Checks

The service includes a health check that:
- Runs every 30 seconds
- Attempts to access the `/api/meetings/` endpoint
- Allows 10 seconds for response
- Retries 3 times before marking as unhealthy
- Waits 40 seconds after container start before first check

### Check Health Status

```bash
# View health status
docker-compose ps

# Detailed health check logs
docker inspect meeting-scheduler --format='{{json .State.Health}}' | jq
```

### Health Check States

- **starting**: Container is starting, health check not yet run
- **healthy**: Health check passed
- **unhealthy**: Health check failed after retries

---

## Development vs Production

### Development Mode

For local development with hot-reloading:

```yaml
# docker-compose.override.yml
version: '3.8'

services:
  web:
    volumes:
      - .:/app  # Mount code for live reloading
    environment:
      - DJANGO_DEBUG=True
    command: python manage.py runserver 0.0.0.0:8000
```

```bash
docker-compose up
```

### Production Mode

For production deployment:

1. **Remove code volume mount** (edit docker-compose.yml)
2. **Set environment variables properly**:
   ```env
   DJANGO_DEBUG=False
   DJANGO_SECRET_KEY=<strong-random-key>
   DJANGO_ALLOWED_HOSTS=yourdomain.com
   ```
3. **Use production server** (e.g., Gunicorn):
   ```yaml
   command: gunicorn meetingscheduler.wsgi:application --bind 0.0.0.0:8000
   ```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs for errors
docker-compose logs web

# Rebuild image
docker-compose build --no-cache
docker-compose up
```

### Database Issues

```bash
# Reset database (WARNING: Deletes all data!)
docker-compose down -v
docker-compose up -d

# Run migrations manually
docker-compose exec web python manage.py migrate
```

### Port Already in Use

```bash
# Change port in .env file
echo "PORT=8080" >> .env
docker-compose up -d

# Or specify inline
PORT=8080 docker-compose up -d
```

### Permission Issues

```bash
# Fix permissions on database directory
docker-compose exec web chown -R $(id -u):$(id -g) /data
```

### Health Check Failing

```bash
# Check if service is actually running
docker-compose exec web curl http://localhost:8000/api/meetings/

# View detailed health check logs
docker inspect meeting-scheduler | grep -A 20 Health

# Temporarily disable health check (edit docker-compose.yml)
# Comment out the healthcheck section
```

---

## Scaling and Advanced Usage

### Multiple Instances

```bash
# Run multiple instances (requires load balancer)
docker-compose up --scale web=3
```

### Custom Network

```yaml
# docker-compose.yml
networks:
  meeting-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16
```

### Resource Limits

```yaml
# docker-compose.yml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy with Docker Compose
        run: |
          docker-compose -f docker-compose.yml up -d --build
```

### GitLab CI Example

```yaml
deploy:
  stage: deploy
  script:
    - docker-compose -f docker-compose.yml up -d --build
  only:
    - main
```

---

## Security Best Practices

1. **Never commit .env files** - Add to .gitignore
2. **Use strong secret keys** - Generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
3. **Disable debug in production** - Set `DJANGO_DEBUG=False`
4. **Restrict allowed hosts** - Set specific domains in `DJANGO_ALLOWED_HOSTS`
5. **Regular backups** - Automate database backups
6. **Update dependencies** - Keep Docker images and Python packages updated
7. **Use HTTPS** - Deploy behind a reverse proxy with SSL/TLS

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Meeting Scheduler API Documentation](./API_TESTING_GUIDE.md)

---

## Support

For issues or questions:
1. Check the logs: `docker-compose logs -f`
2. Review this guide
3. Check the main README.md
4. Open an issue in the repository
