#!/bin/bash

# Скрипт для настройки ngrok туннелей

echo "🌐 Настройка ngrok туннелей..."

# Проверка наличия ngrok
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok не установлен."
    echo "Установите ngrok:"
    echo "  macOS: brew install ngrok"
    echo "  или скачайте с https://ngrok.com/"
    exit 1
fi

# Проверка авторизации ngrok
if ! ngrok config check &> /dev/null; then
    echo "⚠️  ngrok не авторизован."
    echo "Получите токен на https://dashboard.ngrok.com/get-started/your-authtoken"
    echo "Затем выполните: ngrok config add-authtoken YOUR_TOKEN"
    exit 1
fi

echo ""
echo "Запуск туннелей для сервисов..."
echo ""
echo "📱 Web App (порт 8000):"
ngrok http 8000 --log=stdout &
WEBAPP_PID=$!

echo "📊 Airflow (порт 8080):"
ngrok http 8080 --log=stdout &
AIRFLOW_PID=$!

echo "📈 Superset (порт 8088):"
ngrok http 8088 --log=stdout &
SUPERSET_PID=$!

echo ""
echo "✅ Туннели запущены!"
echo ""
echo "Для просмотра активных туннелей откройте: http://localhost:4040"
echo ""
echo "Для остановки нажмите Ctrl+C"

# Ожидание сигнала завершения
trap "kill $WEBAPP_PID $AIRFLOW_PID $SUPERSET_PID 2>/dev/null; exit" INT TERM

wait

