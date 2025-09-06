# 🚀 Руководство по деплою

Подробное руководство по деплою тестовой инфраструктуры Flask API.

## 📋 Предварительные требования

### Системные требования
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Docker-совместимая ОС
- **RAM**: Минимум 2GB, рекомендуется 4GB+
- **CPU**: 2+ cores
- **Диск**: Минимум 10GB свободного места
- **Сеть**: Доступ к интернету для загрузки образов

### Установленное ПО
- Docker 20.10+
- Docker Compose 2.0+
- Git
- Curl (для проверок)

## 🛠️ Настройка сервера

### 1. Установка Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Перелогиньтесь для применения изменений
```

### 2. Установка Docker Compose

```bash
# Установка через pip
sudo apt install python3-pip
pip3 install docker-compose

# Или скачать бинарный файл
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. Настройка файрвола (если используется)

```bash
# Открываем необходимые порты
sudo ufw allow 22      # SSH
sudo ufw allow 80      # HTTP
sudo ufw allow 443     # HTTPS
sudo ufw allow 5000    # Flask API (опционально)
sudo ufw enable
```

## 🔧 Конфигурация проекта

### 1. Клонирование репозитория

```bash
git clone https://github.com/ваш-username/flask-api-project.git
cd flask-api-project
```

### 2. Настройка переменных окружения

```bash
# Копируем пример
cp .env.example .env

# Редактируем конфигурацию
nano .env
```

**Основные настройки для продакшена:**

```bash
# База данных
DATABASE_URL=postgresql://user:secure_password@db:5432/flask_db

# Object Storage
STORAGE_ENDPOINT=your-minio-server.com:9000
STORAGE_ACCESS_KEY=your_access_key
STORAGE_SECRET_KEY=your_secret_key
STORAGE_BUCKET=production-bucket
STORAGE_SECURE=true

# Flask
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key

# Для AWS S3 (альтернатива MinIO)
USE_AWS_S3=true
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1
```

### 3. Настройка SSL сертификатов (опционально)

```bash
# Создаем папку для SSL
mkdir -p ssl

# Генерируем самоподписанный сертификат (для тестирования)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/nginx.key \
  -out ssl/nginx.crt

# Или используйте Let's Encrypt для продакшена
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com
```

## 🚀 Варианты деплоя

### Вариант 1: Автоматический деплой (рекомендуется)

```bash
# Делаем скрипт исполняемым
chmod +x deploy.sh

# Запускаем деплой
./deploy.sh production
```

### Вариант 2: Ручной деплой

```bash
# 1. Останавливаем старые контейнеры
docker-compose down

# 2. Собираем образы
docker-compose build --no-cache

# 3. Запускаем сервисы
docker-compose up -d

# 4. Проверяем статус
docker-compose ps
```

### Вариант 3: Деплой через CI/CD

1. **Настройте GitHub Secrets:**
   - `DOCKERHUB_USERNAME`
   - `DOCKERHUB_TOKEN`
   - `SERVER_HOST`
   - `SERVER_USER`
   - `SERVER_SSH_KEY`
   - `DATABASE_URL`

2. **Сделайте push в ветку main:**
   ```bash
   git add .
   git commit -m "Deploy to production"
   git push origin main
   ```

3. **Мониторьте процесс в GitHub Actions**

## ✅ Проверка деплоя

### 1. Проверка статуса контейнеров

```bash
docker-compose ps

# Ожидаемый вывод:
# NAME                COMMAND             SERVICE   STATUS    PORTS
# flask-api-web-1     "gunicorn..."       web       running   0.0.0.0:5000->5000/tcp
# flask-api-db-1      "docker-entrypoint" db        running   5432/tcp
# flask-api-nginx-1   "/docker-entrypoint" nginx     running   0.0.0.0:80->80/tcp
```

### 2. Проверка API endpoints

```bash
# Основной endpoint
curl http://localhost/
# Ответ: {"message":"Hello World!"}

# Health check для storage
curl http://localhost/health/storage

# Список файлов
curl http://localhost/files
```

### 3. Проверка логов

```bash
# Логи приложения
docker-compose logs -f web

# Логи базы данных
docker-compose logs -f db

# Логи Nginx
docker-compose logs -f nginx
```

### 4. Проверка ресурсов

```bash
# Использование ресурсов
docker stats

# Дисковое пространство
df -h
du -sh /var/lib/docker/
```

## 🔄 Обновление приложения

### Автоматическое обновление

```bash
# Запуск скрипта обновления
./deploy.sh production
```

### Ручное обновление

```bash
# 1. Получаем последние изменения
git pull origin main

# 2. Создаем бэкап БД
docker-compose exec db pg_dump -U user flask_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 3. Пересобираем и перезапускаем
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 4. Проверяем работоспособность
curl http://localhost/
```

### Rolling update (без простоя)

```bash
# 1. Масштабируем до 2 экземпляров
docker-compose up --scale web=2 -d

# 2. Обновляем образ
docker-compose build web

# 3. Поочередно перезапускаем контейнеры
docker-compose up --scale web=2 --no-deps -d web

# 4. Возвращаемся к одному экземпляру
docker-compose up --scale web=1 -d
```

## 🛡️ Безопасность

### 1. Настройка файрвола

```bash
# Закрываем прямой доступ к портам сервисов
sudo ufw deny 5000    # Flask
sudo ufw deny 5432    # PostgreSQL
sudo ufw deny 9000    # MinIO

# Оставляем только HTTP/HTTPS и SSH
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
```

### 2. Настройка SSL

Обновите `nginx.conf` для HTTPS:

```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/nginx/ssl/nginx.crt;
    ssl_certificate_key /etc/nginx/ssl/nginx.key;
    
    # SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Остальная конфигурация...
}

# Редирект с HTTP на HTTPS
server {
    listen 80;
    return 301 https://$server_name$request_uri;
}
```

### 3. Регулярные обновления

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Обновление Docker образов
docker-compose pull
docker-compose up -d

# Очистка старых образов
docker image prune -f
```

## 📊 Мониторинг

### 1. Настройка логирования

```bash
# Ротация логов Docker
sudo nano /etc/docker/daemon.json
```

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

### 2. Health checks

```bash
# Создаем скрипт мониторинга
cat > health_check.sh << 'EOF'
#!/bin/bash
set -e

echo "=== Health Check $(date) ==="

# Проверка API
if curl -f http://localhost/ > /dev/null 2>&1; then
    echo "✅ API доступно"
else
    echo "❌ API недоступно"
    exit 1
fi

# Проверка базы данных
if docker-compose exec -T db pg_isready -U user > /dev/null 2>&1; then
    echo "✅ База данных доступна"
else
    echo "❌ База данных недоступна"
    exit 1
fi

# Проверка storage
if curl -f http://localhost/health/storage | grep -q "healthy\|unhealthy"; then
    echo "✅ Storage endpoint доступен"
else
    echo "❌ Storage endpoint недоступен"
    exit 1
fi

echo "=== Health Check завершен ==="
EOF

chmod +x health_check.sh
```

### 3. Автоматический мониторинг

```bash
# Добавляем в crontab
crontab -e

# Проверка каждые 5 минут
*/5 * * * * /path/to/your/project/health_check.sh >> /var/log/health_check.log 2>&1
```

## 🚨 Troubleshooting

### Частые проблемы и решения

#### 1. Контейнеры не запускаются

```bash
# Проверяем логи
docker-compose logs

# Проверяем ресурсы
docker system df
df -h

# Очищаем систему
docker system prune -f
```

#### 2. База данных недоступна

```bash
# Проверяем статус
docker-compose exec db pg_isready -U user

# Проверяем логи
docker-compose logs db

# Перезапускаем контейнер
docker-compose restart db
```

#### 3. Проблемы с SSL

```bash
# Проверяем сертификаты
openssl x509 -in ssl/nginx.crt -text -noout

# Проверяем права доступа
ls -la ssl/
chmod 644 ssl/nginx.crt
chmod 600 ssl/nginx.key
```

#### 4. Высокое использование ресурсов

```bash
# Проверяем использование
docker stats

# Ограничиваем ресурсы в docker-compose.yml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

## 📞 Поддержка

### Логи для диагностики

При обращении в поддержку приложите:

```bash
# Собираем диагностическую информацию
echo "=== System Info ===" > debug_info.txt
uname -a >> debug_info.txt
docker --version >> debug_info.txt
docker-compose --version >> debug_info.txt

echo -e "\n=== Container Status ===" >> debug_info.txt
docker-compose ps >> debug_info.txt

echo -e "\n=== Container Logs ===" >> debug_info.txt
docker-compose logs --tail=50 >> debug_info.txt

echo -e "\n=== System Resources ===" >> debug_info.txt
free -h >> debug_info.txt
df -h >> debug_info.txt
```

### Контакты

- **Email**: support@yourcompany.com
- **Slack**: #infrastructure
- **Documentation**: https://your-docs-site.com

---

**Деплой завершен!** 🎉

Ваша тестовая инфраструктура готова к использованию.