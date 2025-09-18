#!/bin/bash

# Скрипт быстрого запуска облачной системы агентов

echo "☁️ Запуск облачной системы агентов..."
echo "=============================================="

# Проверяем, запущена ли система
if systemctl is-active --quiet cloud-agent-system; then
    echo "✅ Система уже запущена"
    echo "🌐 Доступна по адресу: http://$(hostname -I | awk '{print $1}')"
    echo ""
    echo "📊 Статус:"
    systemctl status cloud-agent-system --no-pager
    exit 0
fi

# Проверяем права
if [ "$EUID" -eq 0 ]; then
    echo "⚠️ Запуск с правами root. Переключаемся на пользователя mentor..."
    sudo -u mentor bash -c "cd /home/mentor && source multi_agent_env/bin/activate && python cloud_agent_system.py" &
    sleep 5
    echo "✅ Система запущена в фоне"
else
    # Запуск от пользователя mentor
    cd /home/mentor
    source multi_agent_env/bin/activate
    python cloud_agent_system.py
fi
