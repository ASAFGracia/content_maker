#!/bin/bash
set -e

echo "Waiting for postgres..."
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

echo "Waiting for redis..."
while ! nc -z redis 6379; do
  sleep 0.1
done
echo "Redis started"

echo "Creating migrations..."
python manage.py makemigrations --noinput || true

echo "Running migrations..."
# Используем --fake-initial для пропуска уже существующих таблиц
python manage.py migrate --noinput --fake-initial 2>/dev/null || \
python manage.py migrate --noinput || true

echo "Collecting static files..."
python manage.py collectstatic --noinput || true

echo "Initializing templates..."
python manage.py init_templates || true

echo "Starting server..."
exec "$@"

