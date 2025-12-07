# Учетные данные для подключения

## PostgreSQL

**Host:** localhost (или postgres в Docker сети)  
**Port:** 5432  
**Database:** content_maker  
**Username:** content_admin  
**Password:** ContentMaker2024!Secure

### Строка подключения:
```
postgresql://content_admin:ContentMaker2024!Secure@localhost:5432/content_maker
```

## Airflow

**URL:** http://localhost:8080  
**Username:** admin  
**Password:** admin (измените после первого входа)

## Superset

**URL:** http://localhost:8088  
**Username:** admin  
**Password:** admin (измените после первого входа)

## Web Application

**URL:** http://localhost:8000  
**API Base:** http://localhost:8000/api/

## Redis

**Host:** localhost  
**Port:** 6379  
**URL:** redis://localhost:6379/0

---

⚠️ **ВАЖНО:** Измените все пароли в production окружении!

Для изменения паролей отредактируйте файл `.env` и перезапустите контейнеры.

