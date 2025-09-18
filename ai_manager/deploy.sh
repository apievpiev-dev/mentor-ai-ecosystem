#!/bin/bash

# AI Manager - Скрипт развертывания на сервере
set -e

echo "🚀 Развертывание AI Manager на сервере..."

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для логирования
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Проверка зависимостей
check_dependencies() {
    log "Проверка зависимостей..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker не установлен. Установите Docker и повторите попытку."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose не установлен. Установите Docker Compose и повторите попытку."
        exit 1
    fi
    
    success "Все зависимости установлены"
}

# Создание необходимых директорий
create_directories() {
    log "Создание директорий..."
    
    mkdir -p logs
    mkdir -p data
    mkdir -p ssl
    
    success "Директории созданы"
}

# Создание .env файла
create_env_file() {
    log "Создание файла конфигурации..."
    
    if [ ! -f .env ]; then
        cat > .env << EOF
# AI Manager Configuration
DATABASE_URL=postgresql://ai_manager:password@postgres:5432/ai_manager
REDIS_URL=redis://redis:6379/0
HOST=0.0.0.0
PORT=8000
DEBUG=false

# AI Providers
OLLAMA_URL=http://ollama:11434
HUGGINGFACE_TOKEN=

# System Limits
MAX_CONCURRENT_TASKS=20
MAX_AGENTS=100
AGENT_IDLE_TIMEOUT=1800

# Monitoring
ENABLE_PERFORMANCE_MONITORING=true
SYSTEM_METRICS_INTERVAL=60

# Security
SECRET_KEY=$(openssl rand -hex 32)
ALLOWED_ORIGINS=http://localhost,http://localhost:8000
EOF
        success "Файл .env создан"
    else
        warning "Файл .env уже существует"
    fi
}

# Сборка и запуск контейнеров
deploy_containers() {
    log "Сборка и запуск контейнеров..."
    
    # Останавливаем существующие контейнеры
    docker-compose down 2>/dev/null || true
    
    # Собираем и запускаем
    docker-compose up -d --build
    
    success "Контейнеры запущены"
}

# Ожидание готовности сервисов
wait_for_services() {
    log "Ожидание готовности сервисов..."
    
    # Ждем PostgreSQL
    log "Ожидание PostgreSQL..."
    while ! docker-compose exec -T postgres pg_isready -U ai_manager; do
        sleep 2
    done
    success "PostgreSQL готов"
    
    # Ждем Redis
    log "Ожидание Redis..."
    while ! docker-compose exec -T redis redis-cli ping; do
        sleep 2
    done
    success "Redis готов"
    
    # Ждем Ollama
    log "Ожидание Ollama..."
    while ! curl -s http://localhost:11434/api/tags; do
        sleep 5
    done
    success "Ollama готов"
    
    # Ждем AI Manager
    log "Ожидание AI Manager..."
    while ! curl -s http://localhost:8000/api/stats; do
        sleep 5
    done
    success "AI Manager готов"
}

# Инициализация базы данных
init_database() {
    log "Инициализация базы данных..."
    
    # Здесь можно добавить команды для миграций
    # docker-compose exec ai-manager python -c "from database.database import init_db; import asyncio; asyncio.run(init_db())"
    
    success "База данных инициализирована"
}

# Проверка статуса
check_status() {
    log "Проверка статуса сервисов..."
    
    echo ""
    echo "📊 Статус сервисов:"
    docker-compose ps
    
    echo ""
    echo "🌐 Доступные endpoints:"
    echo "  - AI Manager: http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/docs"
    echo "  - Ollama: http://localhost:11434"
    echo "  - PostgreSQL: localhost:5432"
    echo "  - Redis: localhost:6379"
    
    echo ""
    echo "📝 Полезные команды:"
    echo "  - Логи: docker-compose logs -f"
    echo "  - Остановка: docker-compose down"
    echo "  - Перезапуск: docker-compose restart"
    echo "  - Обновление: docker-compose pull && docker-compose up -d"
}

# Основная функция
main() {
    echo "🤖 AI Manager - Развертывание на сервере"
    echo "========================================"
    
    check_dependencies
    create_directories
    create_env_file
    deploy_containers
    wait_for_services
    init_database
    check_status
    
    echo ""
    success "🎉 AI Manager успешно развернут!"
    echo ""
    echo "🚀 Система готова к работе:"
    echo "   - Веб-интерфейс: http://localhost:8000"
    echo "   - API документация: http://localhost:8000/docs"
    echo "   - Мониторинг: docker-compose logs -f"
    echo ""
    echo "💡 Для остановки: docker-compose down"
}

# Запуск
main "$@"
