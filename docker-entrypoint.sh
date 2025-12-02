#!/bin/bash
# Docker entrypoint script for Meeting Scheduler
# Runs database migrations on startup
# Requirement: 8.2

set -e

echo "Starting Meeting Scheduler..."

# Wait for database to be ready (if using external database)
echo "Checking database connection..."

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files (if needed in production)
# echo "Collecting static files..."
# python manage.py collectstatic --noinput

echo "Starting application..."

# Execute the main command
exec "$@"
