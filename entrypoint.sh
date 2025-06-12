#!/bin/bash

set -e

echo "Starting Django application..."

# Wait for database to be ready
python /app/wait_for_db.py

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "Creating superuser if needed..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
from django.core.management import execute_from_command_line
import os

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created successfully.")
else:
    print(f"Superuser '{username}' already exists.")
EOF

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Start the application
if [ "$DJANGO_ENV" = "production" ]; then
    echo "Starting production server with Gunicorn..."
    exec gunicorn core.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --worker-class gevent \
        --worker-connections 1000 \
        --max-requests 1000 \
        --max-requests-jitter 50 \
        --timeout 30 \
        --keep-alive 2 \
        --log-level info \
        --access-logfile - \
        --error-logfile - \
        --capture-output
else
    echo "Starting development server..."
    exec python manage.py runserver 0.0.0.0:8000
fi
