#!/bin/bash

# Скрипт для ПОЛНОГО перезапуска проекта с очисткой всего
# Используйте этот скрипт когда нужно полностью пересоздать все сервисы

set -e

echo "🔄 ПОЛНЫЙ ПЕРЕЗАПУСК Content Maker..."
echo "⚠️  ВНИМАНИЕ: Это удалит все данные (volumes, базы данных, образы)"
echo ""
read -p "Продолжить? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Отменено"
    exit 1
fi

# Определение команды docker compose
if command -v docker compose &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# 1. Полная остановка и удаление
echo ""
echo "🛑 Шаг 1: Остановка всех контейнеров..."
$DOCKER_COMPOSE down -v --remove-orphans

# 2. Удаление образов
echo ""
echo "🗑️  Шаг 2: Удаление образов..."
$DOCKER_COMPOSE down --rmi all --volumes --remove-orphans 2>/dev/null || true

# 3. Очистка volumes
echo ""
echo "🧹 Шаг 3: Очистка volumes..."
docker volume prune -f 2>/dev/null || true

# 4. Очистка сети (если нужно)
echo ""
echo "🌐 Шаг 4: Очистка сетей..."
docker network prune -f 2>/dev/null || true

# 5. Пересборка образов
echo ""
echo "🔨 Шаг 5: Пересборка образов с нуля..."
$DOCKER_COMPOSE build --no-cache --pull

# 6. Запуск сервисов
echo ""
echo "🚀 Шаг 6: Запуск всех сервисов..."
$DOCKER_COMPOSE up -d

# 7. Ожидание готовности базовых сервисов
echo ""
echo "⏳ Шаг 7: Ожидание готовности PostgreSQL и Redis..."
sleep 15

# Проверка готовности PostgreSQL
echo "   Проверка PostgreSQL..."
for i in {1..30}; do
    if docker compose exec -T postgres pg_isready -U content_admin > /dev/null 2>&1; then
        echo "   ✅ PostgreSQL готов"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ❌ PostgreSQL не готов после 30 попыток"
        exit 1
    fi
    sleep 1
done

# Проверка готовности Redis
echo "   Проверка Redis..."
for i in {1..30}; do
    if docker compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        echo "   ✅ Redis готов"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ❌ Redis не готов после 30 попыток"
        exit 1
    fi
    sleep 1
done

# 8. Инициализация Airflow
echo ""
echo "🔧 Шаг 8: Инициализация Airflow..."
sleep 5
$DOCKER_COMPOSE exec -T airflow-webserver airflow db init || true
$DOCKER_COMPOSE exec -T airflow-webserver airflow users delete admin || true
$DOCKER_COMPOSE exec -T airflow-webserver airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@contentmaker.com \
    --password admin \
    --use-random-password=false || true

# 9. Инициализация Django
echo ""
echo "🔧 Шаг 9: Инициализация Django..."
sleep 5
$DOCKER_COMPOSE exec -T webapp python manage.py makemigrations || true
$DOCKER_COMPOSE exec -T webapp python manage.py migrate --fake-initial || \
    $DOCKER_COMPOSE exec -T webapp python manage.py migrate || true
$DOCKER_COMPOSE exec -T webapp python manage.py init_templates || true

# 10. Инициализация Superset
echo ""
echo "🔧 Шаг 10: Инициализация Superset..."
sleep 5
$DOCKER_COMPOSE exec -T superset pip install psycopg2-binary || true
$DOCKER_COMPOSE exec -T superset superset db upgrade || true
$DOCKER_COMPOSE exec -T superset superset fab delete-user admin || true
$DOCKER_COMPOSE exec -T superset superset fab create-admin \
    --username admin \
    --firstname Admin \
    --lastname User \
    --email admin@contentmaker.com \
    --password admin || true
$DOCKER_COMPOSE exec -T superset superset init || true

# 11. Проверка статуса
echo ""
echo "📊 Шаг 11: Проверка статуса сервисов..."
sleep 5
$DOCKER_COMPOSE ps

# 12. Финальная проверка
echo ""
echo "🔍 Шаг 12: Финальная проверка доступности..."
sleep 5

# Проверка Web App
if curl -s http://localhost:8000 > /dev/null 2>&1; then
    echo "   ✅ Web App доступен на http://localhost:8000"
else
    echo "   ⚠️  Web App не отвечает (может быть еще запускается)"
fi

# Проверка Airflow
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "   ✅ Airflow доступен на http://localhost:8080"
else
    echo "   ⚠️  Airflow не отвечает (может быть еще запускается)"
fi

# Проверка Superset
if curl -s http://localhost:8088 > /dev/null 2>&1; then
    echo "   ✅ Superset доступен на http://localhost:8088"
else
    echo "   ⚠️  Superset не отвечает (может быть еще запускается)"
fi

echo ""
echo "✅ ПОЛНЫЙ ПЕРЕЗАПУСК ЗАВЕРШЕН!"
echo ""
echo "📋 Доступ к сервисам:"
echo "   - Web App:      http://localhost:8000"
echo "   - Airflow:      http://localhost:8080"
echo "     Логин: admin"
echo "     Пароль: admin"
echo "   - Superset:     http://localhost:8088"
echo "     Логин: admin"
echo "     Пароль: admin"
echo ""
echo "📖 Просмотр логов:"
echo "   $DOCKER_COMPOSE logs -f webapp"
echo "   $DOCKER_COMPOSE logs -f airflow-webserver"
echo "   $DOCKER_COMPOSE logs -f superset"
echo ""
echo "💡 Если сервисы не работают, подождите еще 1-2 минуты и проверьте логи"

