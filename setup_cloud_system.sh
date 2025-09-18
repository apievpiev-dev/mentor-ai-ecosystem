#!/bin/bash

# Скрипт установки и настройки облачной системы агентов

echo "☁️ Установка облачной системы агентов..."
echo "=============================================="

# Проверяем права root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Запустите скрипт с правами root: sudo ./setup_cloud_system.sh"
    exit 1
fi

# Обновляем систему
echo "📦 Обновление системы..."
apt update && apt upgrade -y

# Устанавливаем необходимые пакеты
echo "📦 Установка зависимостей..."
apt install -y python3 python3-pip python3-venv curl wget git htop nginx ufw

# Создаем пользователя mentor если не существует
if ! id "mentor" &>/dev/null; then
    echo "👤 Создание пользователя mentor..."
    useradd -m -s /bin/bash mentor
    usermod -aG sudo mentor
fi

# Переключаемся на пользователя mentor
echo "👤 Настройка окружения для пользователя mentor..."
sudo -u mentor bash << 'EOF'

# Переходим в домашнюю директорию
cd /home/mentor

# Создаем виртуальное окружение если не существует
if [ ! -d "multi_agent_env" ]; then
    echo "🐍 Создание виртуального окружения..."
    python3 -m venv multi_agent_env
fi

# Активируем виртуальное окружение
source multi_agent_env/bin/activate

# Устанавливаем зависимости
echo "📚 Установка Python зависимостей..."
pip install --upgrade pip
pip install fastapi uvicorn websockets pydantic python-multipart aiofiles requests schedule

# Устанавливаем Ollama если не установлен
if ! command -v ollama &> /dev/null; then
    echo "🤖 Установка Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi

# Запускаем Ollama сервис
echo "🚀 Запуск Ollama сервиса..."
systemctl --user enable ollama
systemctl --user start ollama

# Ждем запуска Ollama
sleep 10

# Устанавливаем базовые модели
echo "📥 Установка базовых AI моделей..."
ollama pull llama3.1:8b &
ollama pull codellama:latest &
ollama pull mistral:latest &
ollama pull neural-chat:latest &

# Ждем завершения установки моделей
wait

echo "✅ Установка завершена для пользователя mentor"
EOF

# Настраиваем systemd сервис
echo "⚙️ Настройка systemd сервиса..."
cp /home/mentor/cloud-agent-system.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable cloud-agent-system

# Настраиваем nginx для проксирования
echo "🌐 Настройка nginx..."
cat > /etc/nginx/sites-available/cloud-agents << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /ws/ {
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

# Активируем сайт nginx
ln -sf /etc/nginx/sites-available/cloud-agents /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# Настраиваем файрвол
echo "🔥 Настройка файрвола..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Создаем директории для системы
echo "📁 Создание директорий..."
mkdir -p /home/mentor/agent_data
mkdir -p /home/mentor/agent_logs
mkdir -p /home/mentor/agent_knowledge
mkdir -p /home/mentor/agent_projects
mkdir -p /home/mentor/backups
mkdir -p /home/mentor/ai_models
mkdir -p /home/mentor/ai_cache

# Устанавливаем права доступа
chown -R mentor:mentor /home/mentor
chmod -R 755 /home/mentor

# Запускаем сервисы
echo "🚀 Запуск сервисов..."
systemctl start cloud-agent-system
systemctl start nginx

# Проверяем статус
echo "📊 Проверка статуса сервисов..."
sleep 5

if systemctl is-active --quiet cloud-agent-system; then
    echo "✅ Cloud Agent System запущен"
else
    echo "❌ Ошибка запуска Cloud Agent System"
    systemctl status cloud-agent-system
fi

if systemctl is-active --quiet nginx; then
    echo "✅ Nginx запущен"
else
    echo "❌ Ошибка запуска Nginx"
    systemctl status nginx
fi

# Получаем IP адрес
IP=$(hostname -I | awk '{print $1}')

echo ""
echo "🎉 УСТАНОВКА ЗАВЕРШЕНА!"
echo "=============================================="
echo "🌐 Система доступна по адресу:"
echo "   http://$IP"
echo "   http://localhost"
echo ""
echo "📊 Статус системы:"
echo "   systemctl status cloud-agent-system"
echo ""
echo "📝 Логи системы:"
echo "   journalctl -u cloud-agent-system -f"
echo ""
echo "🛑 Остановка системы:"
echo "   systemctl stop cloud-agent-system"
echo ""
echo "🔄 Перезапуск системы:"
echo "   systemctl restart cloud-agent-system"
echo ""
echo "=============================================="
echo "🤖 Система агентов готова к работе!"
echo "=============================================="
