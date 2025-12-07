# Решение проблем

## Проблема: Конфликт зависимостей при сборке Docker

**Ошибка:**
```
ERROR: Cannot install -r requirements.txt (line 13) and -r requirements.txt (line 8) 
because these package versions have conflicting dependencies.
The conflict is caused by:
    openai 1.3.5 depends on httpx<1 and >=0.23.0
    googletrans 4.0.0rc1 depends on httpx==0.13.3
```

**Решение:** ✅ Исправлено
- Заменен `googletrans==4.0.0rc1` на `deep-translator==1.11.4`
- Обновлен код в `video_editor/tasks.py` для использования новой библиотеки
- `deep-translator` не имеет конфликтов с `openai`

## Проблема: Ошибки при установке системных пакетов

**Ошибка:**
```
E: Failed to fetch http://deb.debian.org/debian/...
Unable to connect to deb.debian.org:http
```

**Решение:** ✅ Исправлено
- Добавлен флаг `--fix-missing` в `apt-get update`
- Добавлен `--no-install-recommends` для уменьшения размера образа

**Если проблема сохраняется:**
1. Проверьте интернет-соединение
2. Попробуйте пересобрать: `docker compose build --no-cache webapp`
3. Используйте зеркало репозиториев (если в Китае/РФ)

## Проблема: Сервисы не запускаются

**Решение:**
```bash
# Проверьте статус
docker compose ps

# Посмотрите логи
docker compose logs webapp
docker compose logs airflow-webserver

# Пересоберите и перезапустите
docker compose down
docker compose up -d --build
```

## Проблема: База данных не инициализируется

**Решение:**
```bash
# Остановите все
docker compose down -v

# Запустите заново
./start.sh
```

Флаг `-v` удалит volumes, что пересоздаст базу данных.

## Проблема: Порт уже занят

**Ошибка:**
```
Error: bind: address already in use
```

**Решение:**
```bash
# Найдите процесс, использующий порт
lsof -i :8000
lsof -i :8080
lsof -i :8088

# Остановите процесс или измените порты в docker-compose.yml
```

## Проблема: Airflow не инициализируется

**Решение:**
```bash
# Вручную инициализируйте Airflow
docker compose exec airflow-webserver airflow db init
docker compose exec airflow-webserver airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@contentmaker.com \
    --password admin
```

## Проблема: Django миграции не применяются

**Решение:**
```bash
# Примените миграции вручную
docker compose exec webapp python manage.py migrate

# Создайте суперпользователя
docker compose exec webapp python manage.py createsuperuser
```

## Полезные команды

```bash
# Просмотр логов всех сервисов
docker compose logs -f

# Просмотр логов конкретного сервиса
docker compose logs -f webapp

# Перезапуск конкретного сервиса
docker compose restart webapp

# Полная очистка и перезапуск
docker compose down -v
docker compose up -d --build
```

