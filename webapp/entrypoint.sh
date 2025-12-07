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
# Сначала пытаемся применить миграции с --fake-initial
if ! python manage.py migrate --noinput --fake-initial 2>/dev/null; then
  # Если миграция падает из-за существующей колонки, помечаем проблемную миграцию как выполненную
  echo "Migration failed, trying to fake problematic migrations..."
  python manage.py migrate video_editor 0002 --fake --noinput 2>/dev/null || true
  # Затем применяем остальные миграции
  python manage.py migrate --noinput || true
fi

echo "Collecting static files..."
python manage.py collectstatic --noinput || true

echo "Initializing templates..."
python manage.py init_templates || true

echo "Starting server..."
exec "$@"

