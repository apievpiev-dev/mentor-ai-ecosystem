#!/bin/bash

# Autonomous JARVIS Deployment Script
# Скрипт развертывания автономной системы JARVIS

set -e

INSTALL_DIR="/opt/autonomous-jarvis"
SERVICE_NAME="jarvis"

echo "🚀 Начало развертывания Autonomous JARVIS..."

# Проверяем права root
if [[ $EUID -ne 0 ]]; then
   echo "❌ Этот скрипт должен быть запущен от имени root"
   exit 1
fi

# Обновляем систему
echo "📦 Обновление системы..."
apt-get update && apt-get upgrade -y

# Устанавливаем зависимости
echo "🔧 Установка зависимостей..."
apt-get install -y \
    docker.io \
    docker-compose \
    curl \
    jq \
    bc \
    nginx \
    openssl \
    git \
    cron

# Запускаем Docker
systemctl start docker
systemctl enable docker

# Создаем директорию установки
echo "📁 Создание директории установки..."
mkdir -p $INSTALL_DIR
mkdir -p $INSTALL_DIR/logs
mkdir -p $INSTALL_DIR/ssl

# Копируем файлы
echo "📋 Копирование файлов..."
cp -r /workspace/* $INSTALL_DIR/

# Переходим в директорию установки
cd $INSTALL_DIR

# Создаем SSL сертификаты
echo "🔐 Создание SSL сертификатов..."
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem \
    -days 365 -nodes -subj "/C=US/ST=State/L=City/O=JARVIS/CN=localhost"

# Строим Docker образ
echo "🐳 Сборка Docker образа..."
docker-compose build

# Запускаем службы
echo "▶️ Запуск служб..."
docker-compose up -d

# Устанавливаем systemd сервис
echo "⚙️ Установка systemd сервиса..."
cp jarvis.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable jarvis

# Настраиваем cron
echo "⏰ Настройка cron заданий..."
crontab -l > /tmp/current_crontab 2>/dev/null || true
cat crontab.txt >> /tmp/current_crontab
crontab /tmp/current_crontab
rm /tmp/current_crontab

# Настраиваем firewall
echo "🛡️ Настройка firewall..."
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8080/tcp
ufw --force enable

# Проверяем статус
echo "🔍 Проверка статуса..."
sleep 10

if curl -f http://localhost:8080/api/status > /dev/null 2>&1; then
    echo "✅ JARVIS система успешно развернута и работает!"
    echo "🌐 Веб-интерфейс доступен по адресу: http://$(hostname -I | awk '{print $1}'):8080"
    echo "🔒 HTTPS интерфейс: https://$(hostname -I | awk '{print $1}')"
    
    # Показываем статус
    echo ""
    echo "📊 Текущий статус системы:"
    curl -s http://localhost:8080/api/status | jq -r '
        "Производительность: " + (.system_state.performance_score * 100 | floor | tostring) + "%",
        "Уровень автономности: " + (.system_state.autonomy_level | tostring),
        "Визуальные анализы: " + (.system_state.visual_analysis_count | tostring),
        "Время работы: " + (.uptime / 3600 | floor | tostring) + " часов"
    '
else
    echo "❌ Ошибка развертывания! Проверьте логи:"
    echo "docker-compose logs jarvis"
    exit 1
fi

echo ""
echo "🎯 Развертывание завершено!"
echo "📝 Логи мониторинга: /var/log/jarvis-monitor.log"
echo "🔧 Управление службой: systemctl [start|stop|restart] jarvis"
echo "📊 Мониторинг: /opt/autonomous-jarvis/monitor.sh"
