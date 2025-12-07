#!/bin/bash

# Скрипт запуска Content Maker

set -e

echo "🚀 Запуск Content Maker..."

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и попробуйте снова."
    exit 1
fi

if ! command -v docker compose &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose и попробуйте снова."
    exit 1
fi

# Определение команды docker compose
if command -v docker compose &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Создание .env файла если его нет
if [ ! -f .env ]; then
    echo "📝 Создание .env файла..."
    cp .env.example .env
    
    # Генерация ключа для Airflow
    if command -v python3 &> /dev/null; then
        FERNET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" 2>/dev/null || echo "")
        if [ ! -z "$FERNET_KEY" ]; then
            echo "AIRFLOW_FERNET_KEY=$FERNET_KEY" >> .env
            echo "✅ Сгенерирован ключ для Airflow"
        fi
    fi
fi

# Создание директорий
echo "📁 Создание необходимых директорий..."
mkdir -p media/uploads media/processed media/thumbnails media/tts
mkdir -p airflow/logs airflow/plugins airflow/config
mkdir -p webapp/staticfiles

# Остановка старых контейнеров если есть
echo "🛑 Остановка старых контейнеров..."
$DOCKER_COMPOSE down 2>/dev/null || true

# Запуск контейнеров
echo "🐳 Запуск Docker контейнеров..."
$DOCKER_COMPOSE up -d --build

# Ожидание готовности сервисов
echo "⏳ Ожидание готовности сервисов..."
sleep 15

# Проверка статуса
echo "📊 Статус сервисов:"
$DOCKER_COMPOSE ps

echo ""
echo "✅ Content Maker запущен!"
echo ""
echo "📋 Доступ к сервисам:"
echo "   - Web App:      http://localhost:8000"
echo "   - Airflow:      http://localhost:8080 (admin/admin)"
echo "   - Superset:     http://localhost:8088 (admin/admin)"
echo ""
echo "📖 Учетные данные: см. CREDENTIALS.md"
echo ""
echo "Для просмотра логов: $DOCKER_COMPOSE logs -f [service_name]"
echo "Для остановки: $DOCKER_COMPOSE down"

