#!/bin/bash

# Скрипт развертывания системы множественных AI-агентов на сервере
# Обеспечивает автономную работу даже при отключении компьютера

echo "🚀 РАЗВЕРТЫВАНИЕ СИСТЕМЫ МНОЖЕСТВЕННЫХ AI-АГЕНТОВ"
echo "=================================================="

# Проверка прав sudo
if [ "$EUID" -ne 0 ]; then
    echo "❌ Запустите скрипт с правами sudo: sudo ./start_deployment.sh"
    exit 1
fi

# Переход в директорию проекта
cd /home/mentor

echo "📦 Установка системных зависимостей..."

# Обновление системы
apt update && apt upgrade -y

# Установка необходимых пакетов
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    ufw \
    curl \
    wget \
    git \
    chromium-browser \
    chromium-chromedriver \
    systemd \
    cron \
    htop \
    netstat-nat

echo "🔧 Настройка Python окружения..."

# Создание виртуального окружения
python3 -m venv multi_agent_env
source multi_agent_env/bin/activate

# Установка зависимостей
pip install --upgrade pip
pip install -r requirements_multi_agent.txt

# Дополнительные пакеты для автономной работы
pip install \
    selenium \
    pillow \
    requests \
    psutil \
    schedule \
    python-crontab \
    fastapi \
    uvicorn \
    websockets

echo "🌐 Настройка Nginx..."

# Создание конфигурации Nginx
cat > /etc/nginx/sites-available/multi-agent-system << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }
    
    # WebSocket поддержка
    location /ws {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Активация конфигурации
ln -sf /etc/nginx/sites-available/multi-agent-system /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Тест и перезагрузка Nginx
nginx -t && systemctl reload nginx

echo "🔥 Настройка файрвола..."

# Настройка UFW
ufw --force enable
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow from 127.0.0.1 to any port 8080

echo "🤖 Создание systemd сервисов..."

# Основной сервис системы
cat > /etc/systemd/system/multi-agent-system.service << 'EOF'
[Unit]
Description=Multi-Agent AI System
After=network.target
Wants=network.target

[Service]
Type=simple
User=mentor
Group=mentor
WorkingDirectory=/home/mentor
Environment=PATH=/home/mentor/multi_agent_env/bin
ExecStart=/home/mentor/multi_agent_env/bin/python /home/mentor/start_multi_agent_system.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Автоматический перезапуск при сбоях
Restart=on-failure
RestartSec=5
StartLimitInterval=60s
StartLimitBurst=3

# Ограничения ресурсов
MemoryLimit=2G
CPUQuota=200%

[Install]
WantedBy=multi-user.target
EOF

# Сервис мониторинга
cat > /etc/systemd/system/multi-agent-monitor.service << 'EOF'
[Unit]
Description=Multi-Agent System Monitor
After=multi-agent-system.service

[Service]
Type=simple
User=mentor
Group=mentor
WorkingDirectory=/home/mentor
ExecStart=/home/mentor/multi_agent_env/bin/python /home/mentor/monitor_system.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

# Сервис автономного улучшения
cat > /etc/systemd/system/autonomous-improvement.service << 'EOF'
[Unit]
Description=Autonomous System Improvement
After=multi-agent-system.service

[Service]
Type=simple
User=mentor
Group=mentor
WorkingDirectory=/home/mentor
Environment=PATH=/home/mentor/multi_agent_env/bin
ExecStart=/home/mentor/multi_agent_env/bin/python /home/mentor/autonomous_improvement.py
Restart=always
RestartSec=300

[Install]
WantedBy=multi-user.target
EOF

echo "📊 Создание скриптов мониторинга и автономного улучшения..."

# Скрипт мониторинга
cat > /home/mentor/monitor_system.py << 'EOF'
#!/usr/bin/env python3
"""
Скрипт мониторинга системы множественных AI-агентов
"""

import requests
import time
import logging
import subprocess
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_system_health():
    """Проверка состояния системы"""
    try:
        response = requests.get("http://localhost:8080/api/system/status", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Система работает нормально")
            return True
        else:
            logger.warning(f"⚠️ Система отвечает с кодом {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Система недоступна: {e}")
        return False

def restart_system():
    """Перезапуск системы"""
    try:
        subprocess.run(["sudo", "systemctl", "restart", "multi-agent-system"], check=True)
        logger.info("🔄 Система перезапущена")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка перезапуска: {e}")
        return False

def main():
    """Основной цикл мониторинга"""
    consecutive_failures = 0
    max_failures = 3
    
    while True:
        if check_system_health():
            consecutive_failures = 0
        else:
            consecutive_failures += 1
            if consecutive_failures >= max_failures:
                logger.warning("🚨 Критическое количество сбоев, перезапуск системы...")
                restart_system()
                consecutive_failures = 0
        
        time.sleep(60)  # Проверка каждую минуту

if __name__ == "__main__":
    main()
EOF

# Скрипт автономного улучшения
cat > /home/mentor/autonomous_improvement.py << 'EOF'
#!/usr/bin/env python3
"""
Автономное улучшение системы через агентов
"""

import asyncio
import requests
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def autonomous_improvement_cycle():
    """Цикл автономного улучшения"""
    try:
        # Проверка состояния системы
        response = requests.get("http://localhost:8080/api/system/status", timeout=5)
        if response.status_code != 200:
            logger.warning("⚠️ Система недоступна для анализа")
            return
        
        # Отправка запроса на анализ UI
        try:
            analysis_response = requests.post("http://localhost:8080/api/vision/analyze", timeout=30)
            if analysis_response.status_code == 200:
                analysis = analysis_response.json()
                logger.info("🔍 Анализ UI завершен")
                
                # Отправка предложений в систему
                if analysis.get("success") and analysis.get("analysis"):
                    suggestions = analysis["analysis"].get("suggestions", [])
                    for suggestion in suggestions:
                        await send_improvement_suggestion(suggestion)
                
        except Exception as e:
            logger.error(f"❌ Ошибка анализа UI: {e}")
        
        # Проверка здоровья системы
        try:
            health_response = requests.get("http://localhost:8080/api/vision/health", timeout=10)
            if health_response.status_code == 200:
                health = health_response.json()
                if health.get("success"):
                    web_status = health["health"].get("web_interface", {}).get("status")
                    if web_status != "online":
                        logger.warning("🚨 Обнаружена проблема с веб-интерфейсом")
                        await request_system_restart()
        except Exception as e:
            logger.error(f"❌ Ошибка проверки здоровья: {e}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в цикле автономного улучшения: {e}")

async def send_improvement_suggestion(suggestion):
    """Отправка предложения по улучшению"""
    try:
        response = requests.post(
            "http://localhost:8080/api/chat/send",
            json={
                "message": f"Предложение по улучшению: {suggestion}",
                "user_id": "autonomous_agent"
            },
            timeout=10
        )
        if response.status_code == 200:
            logger.info(f"✅ Предложение отправлено: {suggestion}")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки предложения: {e}")

async def request_system_restart():
    """Запрос перезапуска системы"""
    logger.warning("🔄 Запрос перезапуска системы...")
    try:
        subprocess.run(["sudo", "systemctl", "restart", "multi-agent-system"], check=True)
        logger.info("✅ Система перезапущена")
    except Exception as e:
        logger.error(f"❌ Ошибка перезапуска: {e}")

async def main():
    """Основной цикл"""
    while True:
        await autonomous_improvement_cycle()
        await asyncio.sleep(3600)  # Каждый час

if __name__ == "__main__":
    asyncio.run(main())
EOF

# Делаем скрипты исполняемыми
chmod +x /home/mentor/monitor_system.py
chmod +x /home/mentor/autonomous_improvement.py

echo "🔄 Перезагрузка systemd и запуск сервисов..."

# Перезагрузка systemd
systemctl daemon-reload

# Включение и запуск сервисов
systemctl enable multi-agent-system
systemctl enable multi-agent-monitor
systemctl enable autonomous-improvement
systemctl enable nginx

systemctl start multi-agent-system
systemctl start multi-agent-monitor
systemctl start autonomous-improvement
systemctl start nginx

echo "⏳ Ожидание запуска системы..."

# Ожидание запуска системы
for i in {1..30}; do
    if curl -s http://localhost:8080/api/system/status > /dev/null; then
        echo "✅ Система запущена и доступна!"
        break
    fi
    echo "⏳ Попытка $i/30..."
    sleep 2
done

echo ""
echo "🎉 РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО УСПЕШНО!"
echo "=================================="
echo "🌐 Система доступна по адресу: http://$(hostname -I | awk '{print $1}')"
echo "🤖 Система работает автономно"
echo "📊 Мониторинг активен"
echo "🔄 Автономные улучшения включены"
echo ""
echo "📋 Управление сервисами:"
echo "  sudo systemctl status multi-agent-system"
echo "  sudo systemctl restart multi-agent-system"
echo "  sudo systemctl logs multi-agent-system -f"
echo ""
echo "🔍 Проверка состояния:"
echo "  curl http://localhost:8080/api/system/status"
echo "  curl http://localhost:8080/api/vision/health"
echo ""
echo "📝 Логи:"
echo "  journalctl -u multi-agent-system -f"
echo "  journalctl -u multi-agent-monitor -f"
echo "  journalctl -u autonomous-improvement -f"

