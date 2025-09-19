#!/bin/bash

# Скрипт развертывания оптимизированной системы Mentor на сервере
# Автоматически настраивает и запускает систему для непрерывной работы

set -e

echo "🚀 Развертывание оптимизированной системы Mentor..."

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для логирования
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    error "Пожалуйста, запустите скрипт с правами root (sudo)"
    exit 1
fi

# Создание пользователя mentor
log "Создание пользователя mentor..."
if ! id "mentor" &>/dev/null; then
    useradd -m -s /bin/bash mentor
    usermod -aG sudo mentor
    log "Пользователь mentor создан"
else
    info "Пользователь mentor уже существует"
fi

# Создание директорий
log "Создание директорий системы..."
mkdir -p /home/mentor/mentor_system
mkdir -p /home/mentor/mentor_system/logs
mkdir -p /home/mentor/mentor_system/data
mkdir -p /home/mentor/mentor_system/metrics
mkdir -p /home/mentor/mentor_system/backups
mkdir -p /var/log/mentor
chown -R mentor:mentor /home/mentor/mentor_system
chown -R mentor:mentor /var/log/mentor

# Установка зависимостей
log "Установка системных зависимостей..."
apt-get update
apt-get install -y python3 python3-pip python3-venv git curl wget htop

# Создание виртуального окружения
log "Создание виртуального окружения Python..."
cd /home/mentor/mentor_system
sudo -u mentor python3 -m venv mentor_env
sudo -u mentor /home/mentor/mentor_system/mentor_env/bin/pip install --upgrade pip

# Копирование файлов системы
log "Копирование файлов системы..."
cp -r /workspace/* /home/mentor/mentor_system/
chown -R mentor:mentor /home/mentor/mentor_system

# Установка Python зависимостей
log "Установка Python зависимостей..."
sudo -u mentor /home/mentor/mentor_system/mentor_env/bin/pip install -r /home/mentor/mentor_system/requirements.txt
sudo -u mentor /home/mentor/mentor_system/mentor_env/bin/pip install fastapi uvicorn websockets aiofiles psutil

# Создание systemd сервиса
log "Создание systemd сервиса..."
cat > /etc/systemd/system/mentor-system.service << EOF
[Unit]
Description=Mentor Optimized AI System
After=network.target
Wants=network.target

[Service]
Type=simple
User=mentor
Group=mentor
WorkingDirectory=/home/mentor/mentor_system
Environment=PATH=/home/mentor/mentor_system/mentor_env/bin
ExecStart=/home/mentor/mentor_system/mentor_env/bin/python start_optimized_system.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=mentor-system

# Ограничения ресурсов
LimitNOFILE=65536
LimitNPROC=4096

# Переменные окружения
Environment=PYTHONPATH=/home/mentor/mentor_system
Environment=MENTOR_LOG_LEVEL=INFO
Environment=MENTOR_DATA_DIR=/home/mentor/mentor_system/data
Environment=MENTOR_METRICS_DIR=/home/mentor/mentor_system/metrics

[Install]
WantedBy=multi-user.target
EOF

# Создание скрипта мониторинга
log "Создание скрипта мониторинга..."
cat > /home/mentor/mentor_system/monitor_system.sh << 'EOF'
#!/bin/bash

# Скрипт мониторинга системы Mentor
LOG_FILE="/var/log/mentor/monitor.log"
SYSTEM_STATUS_FILE="/home/mentor/mentor_system/data/system_status.json"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

check_system() {
    # Проверяем статус сервиса
    if systemctl is-active --quiet mentor-system; then
        log "Система Mentor работает"
        return 0
    else
        log "Система Mentor не работает, пытаемся перезапустить"
        systemctl restart mentor-system
        sleep 10
        
        if systemctl is-active --quiet mentor-system; then
            log "Система Mentor успешно перезапущена"
            return 0
        else
            log "ОШИБКА: Не удалось перезапустить систему Mentor"
            return 1
        fi
    fi
}

check_resources() {
    # Проверяем использование ресурсов
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')
    DISK_USAGE=$(df /home/mentor/mentor_system | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    
    log "Использование ресурсов - CPU: ${CPU_USAGE}%, RAM: ${MEMORY_USAGE}%, Disk: ${DISK_USAGE}%"
    
    # Предупреждения
    if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
        log "ПРЕДУПРЕЖДЕНИЕ: Высокая загрузка CPU"
    fi
    
    if (( $(echo "$MEMORY_USAGE > 85" | bc -l) )); then
        log "ПРЕДУПРЕЖДЕНИЕ: Высокое использование памяти"
    fi
    
    if [ "$DISK_USAGE" -gt 90 ]; then
        log "ПРЕДУПРЕЖДЕНИЕ: Мало места на диске"
    fi
}

check_ports() {
    # Проверяем доступность портов
    if netstat -tuln | grep -q ":8080 "; then
        log "Порт 8080 (чат) доступен"
    else
        log "ОШИБКА: Порт 8080 (чат) недоступен"
    fi
    
    if netstat -tuln | grep -q ":8081 "; then
        log "Порт 8081 (дашборд) доступен"
    else
        log "ОШИБКА: Порт 8081 (дашборд) недоступен"
    fi
}

# Основной цикл мониторинга
main() {
    log "Запуск мониторинга системы Mentor"
    
    while true; do
        check_system
        check_resources
        check_ports
        
        # Сохраняем статус
        echo "{\"timestamp\": \"$(date -Iseconds)\", \"status\": \"monitoring\"}" > "$SYSTEM_STATUS_FILE"
        
        sleep 60  # Проверяем каждую минуту
    done
}

main
EOF

chmod +x /home/mentor/mentor_system/monitor_system.sh
chown mentor:mentor /home/mentor/mentor_system/monitor_system.sh

# Создание systemd сервиса для мониторинга
log "Создание сервиса мониторинга..."
cat > /etc/systemd/system/mentor-monitor.service << EOF
[Unit]
Description=Mentor System Monitor
After=mentor-system.service
Requires=mentor-system.service

[Service]
Type=simple
User=mentor
Group=mentor
WorkingDirectory=/home/mentor/mentor_system
ExecStart=/home/mentor/mentor_system/monitor_system.sh
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal
SyslogIdentifier=mentor-monitor

[Install]
WantedBy=multi-user.target
EOF

# Создание скрипта резервного копирования
log "Создание скрипта резервного копирования..."
cat > /home/mentor/mentor_system/backup_system.sh << 'EOF'
#!/bin/bash

# Скрипт резервного копирования системы Mentor
BACKUP_DIR="/home/mentor/mentor_system/backups"
DATA_DIR="/home/mentor/mentor_system/data"
METRICS_DIR="/home/mentor/mentor_system/metrics"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="mentor_backup_${DATE}.tar.gz"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

log "Начало резервного копирования системы Mentor"

# Создаем резервную копию
cd /home/mentor/mentor_system
tar -czf "${BACKUP_DIR}/${BACKUP_FILE}" data/ metrics/ logs/ 2>/dev/null

if [ $? -eq 0 ]; then
    log "Резервная копия создана: ${BACKUP_FILE}"
    
    # Удаляем старые копии (старше 7 дней)
    find "$BACKUP_DIR" -name "mentor_backup_*.tar.gz" -mtime +7 -delete
    log "Старые резервные копии удалены"
else
    log "ОШИБКА: Не удалось создать резервную копию"
    exit 1
fi

log "Резервное копирование завершено"
EOF

chmod +x /home/mentor/mentor_system/backup_system.sh
chown mentor:mentor /home/mentor/mentor_system/backup_system.sh

# Создание cron задач
log "Настройка cron задач..."
sudo -u mentor crontab -l 2>/dev/null | { cat; echo "0 2 * * * /home/mentor/mentor_system/backup_system.sh"; } | sudo -u mentor crontab -

# Настройка firewall
log "Настройка firewall..."
if command -v ufw &> /dev/null; then
    ufw allow 8080/tcp
    ufw allow 8081/tcp
    log "Firewall настроен"
else
    warn "UFW не установлен, настройте firewall вручную"
fi

# Перезагрузка systemd
log "Перезагрузка systemd..."
systemctl daemon-reload

# Включение и запуск сервисов
log "Запуск сервисов..."
systemctl enable mentor-system
systemctl enable mentor-monitor
systemctl start mentor-system
systemctl start mentor-monitor

# Ожидание запуска
log "Ожидание запуска системы..."
sleep 10

# Проверка статуса
if systemctl is-active --quiet mentor-system; then
    log "✅ Система Mentor успешно запущена"
else
    error "❌ Ошибка запуска системы Mentor"
    systemctl status mentor-system
    exit 1
fi

# Проверка доступности портов
log "Проверка доступности портов..."
sleep 5

if netstat -tuln | grep -q ":8080 "; then
    log "✅ Порт 8080 (чат) доступен"
else
    warn "⚠️ Порт 8080 (чат) недоступен"
fi

if netstat -tuln | grep -q ":8081 "; then
    log "✅ Порт 8081 (дашборд) доступен"
else
    warn "⚠️ Порт 8081 (дашборд) недоступен"
fi

# Финальная информация
echo ""
echo "🎉 РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!"
echo "=================================="
echo "🌐 Веб-интерфейс чата: http://$(hostname -I | awk '{print $1}'):8080"
echo "📊 Дашборд мониторинга: http://$(hostname -I | awk '{print $1}'):8081"
echo "📈 API статуса: http://$(hostname -I | awk '{print $1}'):8080/api/system/status"
echo ""
echo "🔧 УПРАВЛЕНИЕ СИСТЕМОЙ:"
echo "  Запуск:   sudo systemctl start mentor-system"
echo "  Остановка: sudo systemctl stop mentor-system"
echo "  Перезапуск: sudo systemctl restart mentor-system"
echo "  Статус:   sudo systemctl status mentor-system"
echo "  Логи:     sudo journalctl -u mentor-system -f"
echo ""
echo "📊 МОНИТОРИНГ:"
echo "  Логи мониторинга: /var/log/mentor/monitor.log"
echo "  Резервные копии: /home/mentor/mentor_system/backups/"
echo "  Данные системы: /home/mentor/mentor_system/data/"
echo ""
echo "✅ Система готова к работе!"
echo "=================================="