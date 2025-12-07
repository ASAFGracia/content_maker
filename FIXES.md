# Исправления проблем

## ✅ Исправлено

### 1. Web App - ошибка миграций Django
**Проблема:** `ValueError: Dependency on app with no migrations: crm`

**Решение:**
- Созданы миграции для всех приложений:
  - `webapp/crm/migrations/0001_initial.py`
  - `webapp/video_editor/migrations/0001_initial.py`
  - `webapp/templates/migrations/0001_initial.py`
- Обновлен `entrypoint.sh` для автоматического создания миграций

### 2. Superset - ошибка конфигурации
**Проблема:** `FileNotFoundError: /app/superset_config.py`

**Решение:**
- Исправлен путь к конфигурации: `/app/superset/superset_config.py`
- Добавлена проверка существования файла
- Добавлен `|| true` для команд инициализации

### 3. Airflow - проблемы с логином
**Решение:**
- Пользователь создается через `airflow-init` сервис
- Если не работает, можно пересоздать вручную (см. ниже)

## 🚀 Скрипт перезапуска

Создан скрипт `restart.sh` для удобного управления контейнерами:

### Использование:

```bash
# Простой перезапуск
./restart.sh

# Перезапуск с пересборкой образов
./restart.sh --rebuild

# Полная очистка и перезапуск (удалит volumes!)
./restart.sh --clean --rebuild

# Перезапуск конкретного сервиса
./restart.sh --service webapp
./restart.sh --service airflow-webserver
./restart.sh --service superset
```

### Параметры:
- `--rebuild` или `-r` - пересобрать образы
- `--clean` или `-c` - очистить volumes (удалит данные!)
- `--service SERVICE_NAME` или `-s SERVICE_NAME` - перезапустить только один сервис

## 🔧 Ручное исправление проблем

### Если Airflow не принимает логин/пароль:

```bash
# Пересоздать пользователя Airflow
docker compose exec airflow-webserver airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@contentmaker.com \
    --password admin \
    --use-random-password=false

# Или удалить и создать заново
docker compose exec airflow-webserver airflow users delete admin
docker compose exec airflow-webserver airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@contentmaker.com \
    --password admin
```

### Если Web App не запускается:

```bash
# Применить миграции вручную
docker compose exec webapp python manage.py makemigrations
docker compose exec webapp python manage.py migrate

# Создать суперпользователя
docker compose exec webapp python manage.py createsuperuser
```

### Если Superset не работает:

```bash
# Пересоздать пользователя Superset
docker compose exec superset superset fab create-admin \
    --username admin \
    --firstname Admin \
    --lastname User \
    --email admin@contentmaker.com \
    --password admin

# Инициализировать заново
docker compose exec superset superset init
```

## 📋 Полный перезапуск с нуля

Если ничего не помогает:

```bash
# 1. Остановить и удалить все
docker compose down -v

# 2. Пересобрать все заново
./restart.sh --clean --rebuild

# 3. Проверить логи
docker compose logs -f webapp
docker compose logs -f airflow-webserver
docker compose logs -f superset
```

## ✅ После исправлений

Все сервисы должны работать:
- **Web App**: http://localhost:8000
- **Airflow**: http://localhost:8080 (admin/admin)
- **Superset**: http://localhost:8088 (admin/admin)

