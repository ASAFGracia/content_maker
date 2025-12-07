# Инструкция по деплою в GitHub

## Подготовка к коммиту

1. Убедитесь, что все файлы созданы:
```bash
git status
```

2. Добавьте файлы в git:
```bash
git add .
```

3. Создайте первый коммит:
```bash
git commit -m "Initial commit: Content Maker - система для создания и управления видеоконтентом"
```

4. Добавьте remote репозиторий:
```bash
git remote add origin https://github.com/ASAFGracia/content_maker.git
```

5. Запушьте код:
```bash
git branch -M main
git push -u origin main
```

## Структура проекта

```
content_maker/
├── airflow/              # Airflow DAG'и и конфигурация
│   ├── dags/            # DAG файлы
│   ├── logs/            # Логи Airflow
│   ├── plugins/         # Плагины Airflow
│   └── config/          # Конфигурация
├── webapp/              # Django приложение
│   ├── contentmaker/    # Основные настройки Django
│   ├── crm/             # CRM приложение
│   ├── video_editor/    # Видео редактор
│   ├── templates/       # Шаблоны обработки видео
│   ├── static/          # Статические файлы (CSS, JS)
│   └── templates/       # HTML шаблоны
├── superset/            # Конфигурация Superset
├── media/               # Медиа файлы (создается автоматически)
├── docker-compose.yml   # Docker Compose конфигурация
├── init_db.sql          # SQL скрипт инициализации БД
├── start.sh             # Скрипт запуска
├── setup_ngrok.sh       # Скрипт настройки ngrok
├── README.md            # Основная документация
├── QUICKSTART.md        # Быстрый старт
├── CREDENTIALS.md       # Учетные данные
└── .env.example         # Пример файла окружения
```

## Важные замечания

1. **НЕ коммитьте** файл `.env` - он содержит секретные ключи
2. **НЕ коммитьте** директорию `media/` - она содержит загруженные файлы
3. Убедитесь, что `.gitignore` настроен правильно

## После деплоя

После успешного пуша в GitHub:

1. Клонируйте репозиторий на сервере:
```bash
git clone https://github.com/ASAFGracia/content_maker.git
cd content_maker
```

2. Создайте `.env` файл с реальными ключами

3. Запустите систему:
```bash
./start.sh
```

## Обновление кода

Для обновления кода на сервере:

```bash
git pull origin main
docker-compose down
docker-compose up -d --build
```

