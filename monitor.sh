#!/bin/bash

# Autonomous JARVIS Monitoring Script
# Скрипт мониторинга автономной системы JARVIS

LOG_FILE="/var/log/jarvis-monitor.log"
HEALTH_URL="http://localhost:8080/api/status"
TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID="YOUR_CHAT_ID"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
}

send_telegram_notification() {
    local message="$1"
    if [[ -n "$TELEGRAM_BOT_TOKEN" && -n "$TELEGRAM_CHAT_ID" ]]; then
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d "chat_id=$TELEGRAM_CHAT_ID" \
            -d "text=🤖 JARVIS Alert: $message"
    fi
}

check_health() {
    local response=$(curl -s -w "%{http_code}" -o /dev/null "$HEALTH_URL")
    
    if [[ "$response" == "200" ]]; then
        log_message "✅ JARVIS система работает нормально"
        return 0
    else
        log_message "❌ JARVIS система недоступна (HTTP: $response)"
        send_telegram_notification "Система JARVIS недоступна! HTTP код: $response"
        return 1
    fi
}

restart_service() {
    log_message "🔄 Перезапуск службы JARVIS..."
    systemctl restart jarvis
    sleep 30
    
    if check_health; then
        log_message "✅ Служба успешно перезапущена"
        send_telegram_notification "Служба JARVIS успешно перезапущена"
    else
        log_message "❌ Ошибка перезапуска службы"
        send_telegram_notification "Критическая ошибка: не удается перезапустить JARVIS!"
    fi
}

check_resources() {
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
    local memory_usage=$(free | grep Mem | awk '{printf "%.1f", ($3/$2) * 100.0}')
    local disk_usage=$(df -h / | awk 'NR==2{printf "%s", $5}' | sed 's/%//')
    
    log_message "📊 Ресурсы: CPU: ${cpu_usage}%, RAM: ${memory_usage}%, Disk: ${disk_usage}%"
    
    # Проверяем критические значения
    if (( $(echo "$cpu_usage > 90" | bc -l) )); then
        send_telegram_notification "⚠️ Высокая загрузка CPU: ${cpu_usage}%"
    fi
    
    if (( $(echo "$memory_usage > 85" | bc -l) )); then
        send_telegram_notification "⚠️ Высокое использование памяти: ${memory_usage}%"
    fi
    
    if (( disk_usage > 90 )); then
        send_telegram_notification "⚠️ Мало места на диске: ${disk_usage}%"
    fi
}

main() {
    log_message "🚀 Запуск мониторинга JARVIS системы"
    
    if ! check_health; then
        restart_service
    fi
    
    check_resources
    
    # Проверяем автономность системы
    local autonomy_level=$(curl -s "$HEALTH_URL" | jq -r '.system_state.autonomy_level // 0')
    local visual_analyses=$(curl -s "$HEALTH_URL" | jq -r '.system_state.visual_analysis_count // 0')
    
    log_message "🧠 Уровень автономности: $autonomy_level, Визуальные анализы: $visual_analyses"
    
    if [[ "$autonomy_level" -lt 2 ]]; then
        log_message "⚠️ Низкий уровень автономности"
    fi
}

# Запуск основной функции
main "$@"
