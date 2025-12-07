#!/bin/bash

# Скрипт для перезапуска и пересборки контейнеров Content Maker

set -e

echo "🔄 Перезапуск Content Maker..."

# Определение команды docker compose
if command -v docker compose &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Параметры
REBUILD=false
CLEAN=false
SERVICE=""

# Парсинг аргументов
while [[ $# -gt 0 ]]; do
    case $1 in
        --rebuild|-r)
            REBUILD=true
            shift
            ;;
        --clean|-c)
            CLEAN=true
            shift
            ;;
        --service|-s)
            SERVICE="$2"
            shift 2
            ;;
        *)
            echo "Неизвестный параметр: $1"
            echo "Использование: $0 [--rebuild|-r] [--clean|-c] [--service|-s SERVICE_NAME]"
            exit 1
            ;;
    esac
done

# Остановка контейнеров
echo "🛑 Остановка контейнеров..."
if [ -z "$SERVICE" ]; then
    $DOCKER_COMPOSE down
else
    $DOCKER_COMPOSE stop "$SERVICE"
fi

# Очистка (если нужно)
if [ "$CLEAN" = true ]; then
    echo "🧹 Очистка volumes и образов..."
    $DOCKER_COMPOSE down -v
    if [ "$REBUILD" = true ]; then
        echo "🗑️  Удаление образов..."
        $DOCKER_COMPOSE build --no-cache
    fi
fi

# Пересборка (если нужно)
if [ "$REBUILD" = true ]; then
    echo "🔨 Пересборка образов..."
    if [ -z "$SERVICE" ]; then
        $DOCKER_COMPOSE build --no-cache
    else
        $DOCKER_COMPOSE build --no-cache "$SERVICE"
    fi
fi

# Запуск контейнеров
echo "🚀 Запуск контейнеров..."
if [ -z "$SERVICE" ]; then
    $DOCKER_COMPOSE up -d
else
    $DOCKER_COMPOSE up -d --build "$SERVICE"
fi

# Ожидание готовности
echo "⏳ Ожидание готовности сервисов..."
sleep 10

# Проверка статуса
echo ""
echo "📊 Статус сервисов:"
$DOCKER_COMPOSE ps

# Инициализация (если нужно)
if [ -z "$SERVICE" ] || [ "$SERVICE" = "webapp" ]; then
    echo ""
    echo "🔧 Инициализация Django..."
    $DOCKER_COMPOSE exec -T webapp python manage.py makemigrations || true
    $DOCKER_COMPOSE exec -T webapp python manage.py migrate || true
    $DOCKER_COMPOSE exec -T webapp python manage.py init_templates || true
fi

if [ -z "$SERVICE" ] || [ "$SERVICE" = "airflow-webserver" ]; then
    echo ""
    echo "🔧 Проверка Airflow..."
    echo "   Логин: admin"
    echo "   Пароль: admin"
    echo "   Если не работает, выполните:"
    echo "   docker compose exec airflow-webserver airflow users create \\"
    echo "     --username admin --firstname Admin --lastname User \\"
    echo "     --role Admin --email admin@contentmaker.com --password admin"
fi

echo ""
echo "✅ Перезапуск завершен!"
echo ""
echo "📋 Доступ к сервисам:"
echo "   - Web App:      http://localhost:8000"
echo "   - Airflow:      http://localhost:8080 (admin/admin)"
echo "   - Superset:     http://localhost:8088 (admin/admin)"
echo ""
echo "📖 Просмотр логов: $DOCKER_COMPOSE logs -f [service_name]"

