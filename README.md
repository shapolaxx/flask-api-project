# 🚀 Flask API с тестовой инфраструктурой

Современное REST API на Flask с PostgreSQL, Object Storage (MinIO/S3) и полным CI/CD pipeline. Проект включает тестовую инфраструктуру, автоматизированные тесты и деплой.

## 📋 Задание [Z003] - Настройка тестовой инфраструктуры

**Статус**: ✅ Выполнено  
**Ответственный**: Павел @labradorq  
**Дедлайн**: 12.09.2025  

### Выполненные задачи:
- ✅ Поднят тестовый сервер
- ✅ Настроен CI/CD skeleton  
- ✅ Подключен Object Storage
- ✅ Создана документация

## 🏗️ Архитектура проекта

```
flask-api-project/
├── app/                        # Исходный код приложения
│   ├── __init__.py            # Инициализация Flask приложения
│   ├── config.py              # Конфигурация приложения
│   ├── models.py              # Модели базы данных
│   ├── routes.py              # Основные API маршруты
│   ├── file_routes.py         # Маршруты для работы с файлами
│   └── storage.py             # Модуль работы с Object Storage
├── tests/                      # Тесты приложения
│   ├── test_api.py            # Тесты основного API
│   └── test_storage.py        # Тесты Object Storage
├── .github/workflows/          # GitHub Actions CI/CD
│   └── ci-cd.yml              # Конфигурация pipeline
├── docker-compose.yml          # Продакшн конфигурация
├── docker-compose.dev.yml     # Конфигурация для разработки
├── Dockerfile                  # Docker образ приложения
├── nginx.conf                  # Конфигурация Nginx
├── requirements.txt            # Зависимости Python
├── Makefile                    # Команды для разработки
├── deploy.sh                   # Скрипт деплоя
├── .env.example               # Пример переменных окружения
└── backup_script.sh           # Скрипт бэкапа БД
```

## 🚀 Быстрый старт

### 1. Клонирование и настройка

```bash
git clone https://github.com/ваш-username/flask-api-project.git
cd flask-api-project

# Копируем переменные окружения
cp .env.example .env

# Настраиваем окружение разработки
make dev-setup
```

### 2. Запуск в режиме разработки

```bash
# Локальный запуск (без Docker)
make run

# Или с Docker (включая PostgreSQL и MinIO)
docker-compose -f docker-compose.dev.yml up --build
```

### 3. Запуск в продакшене

```bash
# Автоматический деплой
./deploy.sh production

# Или вручную
docker-compose up --build -d
```

## 🔧 Конфигурация

### Переменные окружения

Скопируйте `.env.example` в `.env` и настройте:

```bash
# База данных
DATABASE_URL=postgresql://user:password@db:5432/flask_db

# Object Storage (MinIO)
STORAGE_ENDPOINT=localhost:9000
STORAGE_ACCESS_KEY=minioadmin
STORAGE_SECRET_KEY=minioadmin
STORAGE_BUCKET=flask-api-bucket

# Для AWS S3
USE_AWS_S3=false
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
```

### GitHub Secrets для CI/CD

Добавьте в настройки репозитория GitHub:

- `DOCKERHUB_USERNAME` - логин DockerHub
- `DOCKERHUB_TOKEN` - токен DockerHub  
- `SERVER_HOST` - IP сервера для деплоя
- `SERVER_USER` - пользователь SSH
- `SERVER_SSH_KEY` - приватный SSH ключ
- `DATABASE_URL` - URL базы данных на сервере

## 📡 API Endpoints

### Основные маршруты
```
GET  /                    # Главная страница
GET  /users               # Получить всех пользователей  
POST /users               # Создать нового пользователя
```

### Работа с файлами
```
POST /files/upload        # Загрузить файл
GET  /files               # Список файлов
GET  /files/{name}/info   # Информация о файле
GET  /files/{name}/download # Скачать файл
DELETE /files/{name}      # Удалить файл
```

### Health Checks
```
GET /health/storage       # Состояние Object Storage
```

## 🧪 Тестирование

```bash
# Запуск всех тестов
make test

# Тесты с покрытием
make test-cov

# Линтинг кода
make lint

# Проверка безопасности
make security

# Полная CI проверка
make ci
```

## 📦 Работа с файлами

### Загрузка файла

```bash
curl -X POST http://localhost:5000/files/upload \
  -F "file=@example.txt" \
  -H "Content-Type: multipart/form-data"
```

### Получение списка файлов

```bash
curl http://localhost:5000/files
curl http://localhost:5000/files?prefix=images/&limit=10
```

### Скачивание файла

```bash
curl http://localhost:5000/files/filename.txt/download
```

## 🔄 CI/CD Pipeline

Pipeline автоматически запускается при:
- Push в ветку `main` или `develop`
- Создании Pull Request в `main`

### Этапы pipeline:

1. **Test** - Запуск тестов и линтинга
2. **Security** - Проверка безопасности зависимостей
3. **Build** - Сборка и публикация Docker образа
4. **Deploy** - Деплой на сервер (только для `main`)
5. **Notify** - Уведомления о результате

## 🐳 Docker

### Разработка

```bash
# Запуск всех сервисов для разработки
docker-compose -f docker-compose.dev.yml up

# Включает:
# - Flask приложение с hot-reload
# - PostgreSQL база данных
# - Redis для кэширования  
# - MinIO для Object Storage
```

### Продакшн

```bash
# Запуск продакшн окружения
docker-compose up -d

# Включает:
# - Flask приложение с Gunicorn
# - PostgreSQL база данных
# - Nginx reverse proxy
```

## 📊 Мониторинг и логи

```bash
# Просмотр логов
docker-compose logs -f web
docker-compose logs -f db

# Статус контейнеров
docker-compose ps

# Использование ресурсов
docker stats
```

## 🔐 Безопасность

- Nginx настроен с security headers
- Rate limiting для API endpoints
- Валидация загружаемых файлов
- Проверка зависимостей на уязвимости
- Presigned URLs для безопасного доступа к файлам

## 🛠️ Разработка

### Полезные команды

```bash
# Установка зависимостей
make install

# Форматирование кода
make format

# Очистка временных файлов
make clean

# Сборка Docker образа
make docker-build

# Остановка Docker контейнеров
make docker-stop
```

### Добавление новых зависимостей

```bash
# Активируем виртуальное окружение
source venv/bin/activate

# Устанавливаем пакет
pip install package-name

# Обновляем requirements.txt
pip freeze > requirements.txt
```

## 📈 Масштабирование

### Горизонтальное масштабирование

```bash
# Увеличиваем количество воркеров
docker-compose up --scale web=3

# Nginx автоматически балансирует нагрузку
```

### Производительность

- Gunicorn с несколькими воркерами
- Nginx для статических файлов и кэширования
- Connection pooling для базы данных
- Presigned URLs для прямого доступа к файлам

## 🚨 Troubleshooting

### Частые проблемы

1. **Порт занят**
   ```bash
   lsof -ti:5000 | xargs kill -9
   ```

2. **Docker контейнеры не запускаются**
   ```bash
   docker-compose down
   docker system prune -f
   docker-compose up --build
   ```

3. **Object Storage недоступен**
   ```bash
   # Проверить статус MinIO
   curl http://localhost:9000/minio/health/live
   
   # Перезапустить контейнеры
   docker-compose restart minio
   ```

4. **База данных недоступна**
   ```bash
   # Проверить подключение
   docker-compose exec db pg_isready -U user
   
   # Восстановить из бэкапа
   docker-compose exec db psql -U user -d flask_db -f /backups/latest.sql
   ```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи: `docker-compose logs`
2. Убедитесь что все сервисы запущены: `docker-compose ps`
3. Проверьте переменные окружения в `.env`
4. Запустите health checks: `curl http://localhost:5000/health/storage`

## 🤝 Контрибьютинг

1. Создайте ветку от `develop`
2. Внесите изменения
3. Запустите тесты: `make test`
4. Создайте Pull Request

---

**Проект готов к использованию!** 🎉

Тестовая инфраструктура полностью настроена и включает:
- ✅ Тестовый сервер на Flask
- ✅ CI/CD pipeline с GitHub Actions
- ✅ Object Storage интеграция (MinIO/S3)
- ✅ Автоматизированные тесты
- ✅ Документация и примеры использования
















