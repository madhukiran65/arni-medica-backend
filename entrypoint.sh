#!/bin/bash
set -e

echo "=== Starting Arni eQMS Backend ==="
echo "DATABASE_URL is set: $([ -n \"$DATABASE_URL\" ] && echo 'YES' || echo 'NO')"

echo "=== Running database migrations ==="
python manage.py migrate --noinput -v 2 2>&1 || {
    echo "WARNING: Migration failed, retrying in 5 seconds..."
    sleep 5
    python manage.py migrate --noinput -v 2 2>&1 || echo "ERROR: Migration failed again, continuing anyway..."
}

echo "=== Running seed_eqms ==="
python manage.py seed_eqms 2>&1 || echo "WARNING: seed_eqms failed or already seeded"

echo "=== Starting Gunicorn ==="
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --timeout 120 \
    --log-level info
