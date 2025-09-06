#!/bin/bash

# Скрипт деплоя приложения
# Использование: ./deploy.sh [environment]

set -e  # Выход при ошибке

ENVIRONMENT=${1:-production}
DOCKER_IMAGE="flask-api"
CONTAINER_NAME="flask-api"

echo "🚀 Начинаем деплой в окружение: $ENVIRONMENT"

# Функция логирования
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Проверка зависимостей
check_dependencies() {
    log "Проверяем зависимости..."
    
    if ! command -v docker &> /dev/null; then
        log "❌ Docker не установлен"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! command -v docker compose &> /dev/null; then
        log "❌ Docker Compose не установлен"
        exit 1
    fi
    
    log "✅ Все зависимости установлены"
}

# Остановка старых контейнеров
stop_old_containers() {
    log "Останавливаем старые контейнеры..."
    
    if [ "$ENVIRONMENT" = "development" ]; then
        docker-compose -f docker-compose.dev.yml down || true
    else
        docker-compose down || true
    fi
    
    log "✅ Старые контейнеры остановлены"
}

# Сборка образов
build_images() {
    log "Собираем Docker образы..."
    
    if [ "$ENVIRONMENT" = "development" ]; then
        docker-compose -f docker-compose.dev.yml build --no-cache
    else
        docker-compose build --no-cache
    fi
    
    log "✅ Образы собраны"
}

# Запуск контейнеров
start_containers() {
    log "Запускаем контейнеры..."
    
    if [ "$ENVIRONMENT" = "development" ]; then
        docker-compose -f docker-compose.dev.yml up -d
    else
        docker-compose up -d
    fi
    
    log "✅ Контейнеры запущены"
}

# Проверка здоровья приложения
health_check() {
    log "Проверяем здоровье приложения..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:5000/ >/dev/null 2>&1; then
            log "✅ Приложение работает корректно"
            return 0
        fi
        
        log "Попытка $attempt/$max_attempts: приложение еще не готово..."
        sleep 5
        ((attempt++))
    done
    
    log "❌ Приложение не отвечает после $max_attempts попыток"
    return 1
}

# Создание бэкапа (для продакшена)
create_backup() {
    if [ "$ENVIRONMENT" = "production" ]; then
        log "Создаем бэкап базы данных..."
        
        # Создаем папку для бэкапов если её нет
        mkdir -p backups
        
        # Запускаем скрипт бэкапа
        docker-compose exec -T db /backup_script.sh || log "⚠️ Не удалось создать бэкап"
        
        log "✅ Бэкап создан"
    fi
}

# Очистка старых образов
cleanup() {
    log "Очищаем неиспользуемые образы..."
    docker image prune -f || true
    log "✅ Очистка завершена"
}

# Главная функция
main() {
    log "🚀 Деплой приложения Flask API"
    log "Окружение: $ENVIRONMENT"
    
    check_dependencies
    create_backup
    stop_old_containers
    build_images
    start_containers
    
    # Ждем немного перед проверкой здоровья
    sleep 10
    
    if health_check; then
        cleanup
        log "🎉 Деплой успешно завершен!"
        
        # Показываем статус контейнеров
        if [ "$ENVIRONMENT" = "development" ]; then
            docker-compose -f docker-compose.dev.yml ps
        else
            docker-compose ps
        fi
        
        log "📱 Приложение доступно по адресу: http://localhost:5000"
    else
        log "❌ Деплой завершился с ошибкой"
        
        # Показываем логи для диагностики
        log "Логи приложения:"
        if [ "$ENVIRONMENT" = "development" ]; then
            docker-compose -f docker-compose.dev.yml logs --tail=50 web
        else
            docker-compose logs --tail=50 web
        fi
        
        exit 1
    fi
}

# Обработка сигналов
trap 'log "⚠️ Деплой прерван пользователем"; exit 1' INT TERM

# Запуск
main "$@"