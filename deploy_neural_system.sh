#!/bin/bash
# Deploy Neural System - Скрипт развертывания системы нейросетей на сервере

set -e

echo "🚀 Развертывание системы нейросетей на сервере..."

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    log_error "Этот скрипт должен быть запущен с правами root"
    exit 1
fi

# Обновление системы
log_info "Обновление системы..."
apt update && apt upgrade -y

# Установка необходимых пакетов
log_info "Установка необходимых пакетов..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    wget \
    git \
    nginx \
    supervisor \
    htop \
    tree \
    unzip \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev

# Создание пользователя для системы
log_info "Создание пользователя neural_system..."
if ! id "neural_system" &>/dev/null; then
    useradd -m -s /bin/bash neural_system
    usermod -aG sudo neural_system
    log_success "Пользователь neural_system создан"
else
    log_warning "Пользователь neural_system уже существует"
fi

# Создание директорий
log_info "Создание директорий системы..."
mkdir -p /opt/neural_system
mkdir -p /opt/neural_system/logs
mkdir -p /opt/neural_system/data
mkdir -p /opt/neural_system/models
mkdir -p /opt/neural_system/screenshots
mkdir -p /opt/neural_system/reports

# Копирование файлов системы
log_info "Копирование файлов системы..."
cp -r /workspace/* /opt/neural_system/
chown -R neural_system:neural_system /opt/neural_system

# Создание виртуального окружения
log_info "Создание виртуального окружения Python..."
cd /opt/neural_system
sudo -u neural_system python3 -m venv venv
sudo -u neural_system ./venv/bin/pip install --upgrade pip

# Установка зависимостей Python
log_info "Установка зависимостей Python..."
sudo -u neural_system ./venv/bin/pip install \
    fastapi \
    uvicorn \
    aiohttp \
    asyncio \
    requests \
    numpy \
    pandas \
    matplotlib \
    seaborn \
    scikit-learn \
    torch \
    transformers \
    openai \
    python-dotenv \
    pydantic \
    websockets \
    jinja2 \
    python-multipart

# Установка Ollama
log_info "Установка Ollama..."
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.ai/install.sh | sh
    log_success "Ollama установлен"
else
    log_warning "Ollama уже установлен"
fi

# Запуск Ollama как сервис
log_info "Настройка Ollama как сервис..."
systemctl enable ollama
systemctl start ollama

# Загрузка моделей Ollama
log_info "Загрузка моделей Ollama..."
sudo -u neural_system ollama pull llama2:7b &
sudo -u neural_system ollama pull codellama:7b &
sudo -u neural_system ollama pull mistral:7b &
wait

log_success "Модели Ollama загружены"

# Создание systemd сервисов
log_info "Создание systemd сервисов..."

# Сервис для основной системы
cat > /etc/systemd/system/neural-system.service << EOF
[Unit]
Description=Neural System - Autonomous AI Agents
After=network.target ollama.service
Requires=ollama.service

[Service]
Type=simple
User=neural_system
Group=neural_system
WorkingDirectory=/opt/neural_system
Environment=PATH=/opt/neural_system/venv/bin
ExecStart=/opt/neural_system/venv/bin/python unified_neural_interface.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Сервис для автономной системы
cat > /etc/systemd/system/autonomous-neural.service << EOF
[Unit]
Description=Autonomous Neural System
After=network.target ollama.service
Requires=ollama.service

[Service]
Type=simple
User=neural_system
Group=neural_system
WorkingDirectory=/opt/neural_system
Environment=PATH=/opt/neural_system/venv/bin
ExecStart=/opt/neural_system/venv/bin/python autonomous_neural_system.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Настройка Nginx
log_info "Настройка Nginx..."
cat > /etc/nginx/sites-available/neural-system << EOF
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /ws {
        proxy_pass http://127.0.0.1:8081;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Активация сайта Nginx
ln -sf /etc/nginx/sites-available/neural-system /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Проверка конфигурации Nginx
nginx -t

# Создание скриптов управления
log_info "Создание скриптов управления..."

# Скрипт запуска
cat > /opt/neural_system/start.sh << 'EOF'
#!/bin/bash
echo "🚀 Запуск системы нейросетей..."
systemctl start ollama
sleep 5
systemctl start neural-system
systemctl start autonomous-neural
systemctl start nginx
echo "✅ Система запущена"
echo "🌐 Веб-интерфейс: http://$(hostname -I | awk '{print $1}')"
EOF

# Скрипт остановки
cat > /opt/neural_system/stop.sh << 'EOF'
#!/bin/bash
echo "🛑 Остановка системы нейросетей..."
systemctl stop neural-system
systemctl stop autonomous-neural
systemctl stop nginx
echo "✅ Система остановлена"
EOF

# Скрипт перезапуска
cat > /opt/neural_system/restart.sh << 'EOF'
#!/bin/bash
echo "🔄 Перезапуск системы нейросетей..."
./stop.sh
sleep 5
./start.sh
EOF

# Скрипт статуса
cat > /opt/neural_system/status.sh << 'EOF'
#!/bin/bash
echo "📊 Статус системы нейросетей:"
echo "================================"
echo "Ollama: $(systemctl is-active ollama)"
echo "Neural System: $(systemctl is-active neural-system)"
echo "Autonomous System: $(systemctl is-active autonomous-neural)"
echo "Nginx: $(systemctl is-active nginx)"
echo "================================"
echo "Логи:"
echo "journalctl -u neural-system -f"
echo "journalctl -u autonomous-neural -f"
EOF

# Скрипт обновления
cat > /opt/neural_system/update.sh << 'EOF'
#!/bin/bash
echo "🔄 Обновление системы нейросетей..."
cd /opt/neural_system
git pull origin main
./venv/bin/pip install -r requirements.txt
systemctl restart neural-system
systemctl restart autonomous-neural
echo "✅ Система обновлена"
EOF

# Делаем скрипты исполняемыми
chmod +x /opt/neural_system/*.sh
chown neural_system:neural_system /opt/neural_system/*.sh

# Создание файла конфигурации
log_info "Создание файла конфигурации..."
cat > /opt/neural_system/.env << EOF
# Neural System Configuration
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama2:7b
HUGGINGFACE_TOKEN=
OPENAI_API_KEY=
SYSTEM_HOST=0.0.0.0
SYSTEM_PORT=8081
AUTONOMOUS_MODE=true
VISUAL_VERIFICATION=true
PERFORMANCE_OPTIMIZATION=true
EOF

chown neural_system:neural_system /opt/neural_system/.env

# Создание файла requirements.txt
log_info "Создание файла requirements.txt..."
cat > /opt/neural_system/requirements.txt << EOF
fastapi==0.104.1
uvicorn==0.24.0
aiohttp==3.9.1
asyncio
requests==2.31.0
numpy==1.24.3
pandas==2.0.3
matplotlib==3.7.2
seaborn==0.12.2
scikit-learn==1.3.0
torch==2.1.0
transformers==4.35.0
openai==1.3.0
python-dotenv==1.0.0
pydantic==2.5.0
websockets==12.0
jinja2==3.1.2
python-multipart==0.0.6
EOF

# Перезагрузка systemd
log_info "Перезагрузка systemd..."
systemctl daemon-reload

# Включение сервисов
log_info "Включение сервисов..."
systemctl enable ollama
systemctl enable neural-system
systemctl enable autonomous-neural
systemctl enable nginx

# Запуск сервисов
log_info "Запуск сервисов..."
systemctl start ollama
sleep 10
systemctl start neural-system
systemctl start autonomous-neural
systemctl start nginx

# Проверка статуса
log_info "Проверка статуса сервисов..."
sleep 5

echo "================================"
echo "📊 Статус развертывания:"
echo "================================"
echo "Ollama: $(systemctl is-active ollama)"
echo "Neural System: $(systemctl is-active neural-system)"
echo "Autonomous System: $(systemctl is-active autonomous-neural)"
echo "Nginx: $(systemctl is-active nginx)"
echo "================================"

# Получение IP адреса
SERVER_IP=$(hostname -I | awk '{print $1}')

log_success "🎉 Система нейросетей успешно развернута!"
echo ""
echo "🌐 Веб-интерфейс: http://$SERVER_IP"
echo "📊 API статуса: http://$SERVER_IP/api/system/status"
echo "🤖 Список агентов: http://$SERVER_IP/api/agents"
echo ""
echo "📁 Директория системы: /opt/neural_system"
echo "📝 Логи: journalctl -u neural-system -f"
echo "🔧 Управление: /opt/neural_system/start.sh, stop.sh, restart.sh, status.sh"
echo ""
echo "🚀 Система готова к работе!"

# Создание файла с информацией о развертывании
cat > /opt/neural_system/DEPLOYMENT_INFO.txt << EOF
Neural System Deployment Information
====================================

Deployment Date: $(date)
Server IP: $SERVER_IP
System Directory: /opt/neural_system
User: neural_system

Services:
- ollama: $(systemctl is-active ollama)
- neural-system: $(systemctl is-active neural-system)
- autonomous-neural: $(systemctl is-active autonomous-neural)
- nginx: $(systemctl is-active nginx)

Web Interface: http://$SERVER_IP
API Status: http://$SERVER_IP/api/system/status
Agents List: http://$SERVER_IP/api/agents

Management Scripts:
- Start: /opt/neural_system/start.sh
- Stop: /opt/neural_system/stop.sh
- Restart: /opt/neural_system/restart.sh
- Status: /opt/neural_system/status.sh
- Update: /opt/neural_system/update.sh

Logs:
- Neural System: journalctl -u neural-system -f
- Autonomous System: journalctl -u autonomous-neural -f
- Ollama: journalctl -u ollama -f

Configuration:
- Environment: /opt/neural_system/.env
- Nginx: /etc/nginx/sites-available/neural-system
- Systemd: /etc/systemd/system/neural-system.service
EOF

chown neural_system:neural_system /opt/neural_system/DEPLOYMENT_INFO.txt

log_success "✅ Развертывание завершено успешно!"