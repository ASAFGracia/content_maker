#!/bin/bash
set -e

# Ожидание PostgreSQL
echo "Waiting for postgres..."
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

# Инициализация базы данных Airflow (только если нужно)
if [ ! -f /opt/airflow/airflow.db ]; then
    echo "Initializing Airflow database..."
    airflow db init
fi

# Создание пользователя (только если не существует)
echo "Creating Airflow admin user..."
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@contentmaker.com \
    --password admin \
    || echo "User already exists"

exec "$@"

