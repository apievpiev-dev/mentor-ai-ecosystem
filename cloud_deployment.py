#!/usr/bin/env python3
"""
Cloud Deployment Script for Autonomous JARVIS
Скрипт развертывания автономной системы JARVIS в облаке
"""

import os
import sys
import json
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CloudDeployment:
    """Система развертывания в облаке"""
    
    def __init__(self):
        self.deployment_config = {
            "project_name": "autonomous-jarvis",
            "docker_image": "autonomous-jarvis:latest",
            "port": 8080,
            "environment": "production",
            "auto_restart": True,
            "health_check": True
        }
    
    def create_dockerfile(self):
        """Создание Dockerfile"""
        dockerfile_content = """FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \\
    curl \\
    wget \\
    git \\
    procps \\
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов проекта
COPY requirements.txt .
COPY streamlined_jarvis.py .
COPY enhanced_autonomous_jarvis.py .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Создание директории для логов
RUN mkdir -p /app/logs

# Открытие порта
EXPOSE 8080

# Переменные окружения
ENV PYTHONPATH=/app
ENV JARVIS_ENV=production
ENV JARVIS_LOG_LEVEL=INFO

# Команда запуска
CMD ["python3", "streamlined_jarvis.py"]
"""
        
        with open('/workspace/Dockerfile', 'w') as f:
            f.write(dockerfile_content)
        
        logger.info("✅ Dockerfile создан")
    
    def create_requirements_file(self):
        """Создание requirements.txt"""
        requirements = """fastapi==0.116.2
uvicorn==0.35.0
psutil==7.1.0
pillow==11.3.0
websockets==15.0.1
pydantic==2.11.9
python-multipart==0.0.6
"""
        
        with open('/workspace/requirements.txt', 'w') as f:
            f.write(requirements)
        
        logger.info("✅ requirements.txt создан")
    
    def create_docker_compose(self):
        """Создание docker-compose.yml"""
        compose_content = """version: '3.8'

services:
  jarvis:
    build: .
    container_name: autonomous-jarvis
    ports:
      - "8080:8080"
    environment:
      - JARVIS_ENV=production
      - JARVIS_LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
      - /etc/localtime:/etc/localtime:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/api/status"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  nginx:
    image: nginx:alpine
    container_name: jarvis-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - jarvis
    restart: unless-stopped

volumes:
  jarvis_data:
"""
        
        with open('/workspace/docker-compose.yml', 'w') as f:
            f.write(compose_content)
        
        logger.info("✅ docker-compose.yml создан")
    
    def create_nginx_config(self):
        """Создание конфигурации Nginx"""
        nginx_config = """events {
    worker_connections 1024;
}

http {
    upstream jarvis_backend {
        server jarvis:8080;
    }

    server {
        listen 80;
        server_name _;

        # Redirect HTTP to HTTPS
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name _;

        # SSL Configuration (self-signed for demo)
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

        location / {
            proxy_pass http://jarvis_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Health check endpoint
        location /health {
            proxy_pass http://jarvis_backend/api/status;
            access_log off;
        }
    }
}
"""
        
        with open('/workspace/nginx.conf', 'w') as f:
            f.write(nginx_config)
        
        logger.info("✅ nginx.conf создан")
    
    def create_ssl_certificates(self):
        """Создание самоподписанных SSL сертификатов"""
        ssl_dir = Path('/workspace/ssl')
        ssl_dir.mkdir(exist_ok=True)
        
        # Создаем самоподписанный сертификат
        cmd = [
            'openssl', 'req', '-x509', '-newkey', 'rsa:4096', '-keyout',
            str(ssl_dir / 'key.pem'), '-out', str(ssl_dir / 'cert.pem'),
            '-days', '365', '-nodes', '-subj',
            '/C=US/ST=State/L=City/O=Organization/CN=localhost'
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info("✅ SSL сертификаты созданы")
        except subprocess.CalledProcessError:
            logger.warning("⚠️ OpenSSL недоступен, SSL сертификаты не созданы")
    
    def create_systemd_service(self):
        """Создание systemd сервиса"""
        service_content = f"""[Unit]
Description=Autonomous JARVIS System
After=network.target docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/autonomous-jarvis
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0
User=root

[Install]
WantedBy=multi-user.target
"""
        
        with open('/workspace/jarvis.service', 'w') as f:
            f.write(service_content)
        
        logger.info("✅ Systemd сервис создан")
    
    def create_monitoring_script(self):
        """Создание скрипта мониторинга"""
        monitoring_script = """#!/bin/bash

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
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \\
            -d "chat_id=$TELEGRAM_CHAT_ID" \\
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
"""
        
        with open('/workspace/monitor.sh', 'w') as f:
            f.write(monitoring_script)
        
        # Делаем скрипт исполняемым
        os.chmod('/workspace/monitor.sh', 0o755)
        
        logger.info("✅ Скрипт мониторинга создан")
    
    def create_crontab_entry(self):
        """Создание записи для crontab"""
        crontab_entry = """# Autonomous JARVIS System Monitoring
# Мониторинг каждые 5 минут
*/5 * * * * /opt/autonomous-jarvis/monitor.sh

# Ежедневная очистка логов
0 2 * * * find /var/log -name "jarvis-*.log" -mtime +7 -delete

# Еженедельная проверка обновлений
0 3 * * 0 cd /opt/autonomous-jarvis && git pull && docker-compose build --no-cache && docker-compose up -d
"""
        
        with open('/workspace/crontab.txt', 'w') as f:
            f.write(crontab_entry)
        
        logger.info("✅ Crontab записи созданы")
    
    def create_deployment_script(self):
        """Создание скрипта развертывания"""
        deployment_script = """#!/bin/bash

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
apt-get install -y \\
    docker.io \\
    docker-compose \\
    curl \\
    jq \\
    bc \\
    nginx \\
    openssl \\
    git \\
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
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem \\
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
"""
        
        with open('/workspace/deploy.sh', 'w') as f:
            f.write(deployment_script)
        
        # Делаем скрипт исполняемым
        os.chmod('/workspace/deploy.sh', 0o755)
        
        logger.info("✅ Скрипт развертывания создан")
    
    def create_kubernetes_manifests(self):
        """Создание манифестов Kubernetes"""
        # Deployment
        deployment_yaml = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: autonomous-jarvis
  labels:
    app: jarvis
spec:
  replicas: 2
  selector:
    matchLabels:
      app: jarvis
  template:
    metadata:
      labels:
        app: jarvis
    spec:
      containers:
      - name: jarvis
        image: autonomous-jarvis:latest
        ports:
        - containerPort: 8080
        env:
        - name: JARVIS_ENV
          value: "production"
        - name: JARVIS_LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/status
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/status
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: jarvis-service
spec:
  selector:
    app: jarvis
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: jarvis-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - jarvis.yourdomain.com
    secretName: jarvis-tls
  rules:
  - host: jarvis.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: jarvis-service
            port:
              number: 80
"""
        
        with open('/workspace/k8s-deployment.yaml', 'w') as f:
            f.write(deployment_yaml)
        
        logger.info("✅ Kubernetes манифесты созданы")
    
    def create_terraform_config(self):
        """Создание конфигурации Terraform для облака"""
        terraform_config = """# Terraform configuration for Autonomous JARVIS deployment
# Конфигурация Terraform для развертывания автономной системы JARVIS

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "key_name" {
  description = "AWS Key Pair name"
  type        = string
}

# VPC
resource "aws_vpc" "jarvis_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "jarvis-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "jarvis_igw" {
  vpc_id = aws_vpc.jarvis_vpc.id

  tags = {
    Name = "jarvis-igw"
  }
}

# Subnet
resource "aws_subnet" "jarvis_subnet" {
  vpc_id                  = aws_vpc.jarvis_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name = "jarvis-subnet"
  }
}

# Route Table
resource "aws_route_table" "jarvis_rt" {
  vpc_id = aws_vpc.jarvis_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.jarvis_igw.id
  }

  tags = {
    Name = "jarvis-rt"
  }
}

resource "aws_route_table_association" "jarvis_rta" {
  subnet_id      = aws_subnet.jarvis_subnet.id
  route_table_id = aws_route_table.jarvis_rt.id
}

# Security Group
resource "aws_security_group" "jarvis_sg" {
  name_prefix = "jarvis-sg"
  vpc_id      = aws_vpc.jarvis_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "jarvis-sg"
  }
}

# Data source for availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

# Data source for latest Ubuntu AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# EC2 Instance
resource "aws_instance" "jarvis" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name              = var.key_name
  vpc_security_group_ids = [aws_security_group.jarvis_sg.id]
  subnet_id             = aws_subnet.jarvis_subnet.id

  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    domain = aws_eip.jarvis_eip.public_ip
  }))

  root_block_device {
    volume_type = "gp3"
    volume_size = 20
    encrypted   = true
  }

  tags = {
    Name = "autonomous-jarvis"
  }
}

# Elastic IP
resource "aws_eip" "jarvis_eip" {
  domain = "vpc"
  
  tags = {
    Name = "jarvis-eip"
  }
}

resource "aws_eip_association" "jarvis_eip_assoc" {
  instance_id   = aws_instance.jarvis.id
  allocation_id = aws_eip.jarvis_eip.id
}

# Output
output "jarvis_public_ip" {
  description = "Public IP address of the JARVIS instance"
  value       = aws_eip.jarvis_eip.public_ip
}

output "jarvis_web_url" {
  description = "Web URL for JARVIS"
  value       = "https://${aws_eip.jarvis_eip.public_ip}"
}
"""
        
        with open('/workspace/main.tf', 'w') as f:
            f.write(terraform_config)
        
        # User data script
        user_data_script = """#!/bin/bash
set -e

# Update system
apt-get update && apt-get upgrade -y

# Install dependencies
apt-get install -y \\
    docker.io \\
    docker-compose \\
    curl \\
    jq \\
    bc \\
    nginx \\
    openssl \\
    git \\
    cron \\
    awscli

# Start Docker
systemctl start docker
systemctl enable docker

# Clone repository (replace with your repo)
cd /opt
git clone https://github.com/your-username/autonomous-jarvis.git || \\
  mkdir -p autonomous-jarvis

cd autonomous-jarvis

# Copy deployment files (assuming they're in the repo)
# If not, you can download them from S3 or another source

# Run deployment
./deploy.sh

# Configure domain (if provided)
if [ -n "${domain}" ]; then
    # Update nginx configuration with the domain
    sed -i "s/server_name _;/server_name ${domain};/g" /etc/nginx/sites-available/default
    systemctl reload nginx
fi

echo "🚀 Autonomous JARVIS deployed successfully!"
"""
        
        with open('/workspace/user_data.sh', 'w') as f:
            f.write(user_data_script)
        
        logger.info("✅ Terraform конфигурация создана")
    
    def create_readme(self):
        """Создание README для развертывания"""
        readme_content = """# Autonomous JARVIS Cloud Deployment
# Развертывание автономной системы JARVIS в облаке

## 🚀 Быстрый старт

### Локальное развертывание с Docker

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd autonomous-jarvis
```

2. Запустите систему:
```bash
docker-compose up -d
```

3. Откройте браузер: http://localhost:8080

### Развертывание на сервере

1. Скопируйте файлы на сервер:
```bash
scp -r * user@server:/opt/autonomous-jarvis/
```

2. Запустите скрипт развертывания:
```bash
sudo ./deploy.sh
```

### AWS развертывание с Terraform

1. Настройте AWS CLI:
```bash
aws configure
```

2. Инициализируйте Terraform:
```bash
terraform init
```

3. Создайте инфраструктуру:
```bash
terraform plan
terraform apply
```

## 🛠️ Конфигурация

### Переменные окружения

- `JARVIS_ENV`: Окружение (production/development)
- `JARVIS_LOG_LEVEL`: Уровень логирования (INFO/DEBUG)

### Порты

- 8080: Основное приложение JARVIS
- 80: HTTP (перенаправление на HTTPS)
- 443: HTTPS

## 📊 Мониторинг

### Проверка статуса
```bash
curl http://localhost:8080/api/status
```

### Просмотр логов
```bash
docker-compose logs -f jarvis
```

### Мониторинг ресурсов
```bash
./monitor.sh
```

## 🔧 Управление

### Перезапуск системы
```bash
systemctl restart jarvis
# или
docker-compose restart
```

### Обновление
```bash
git pull
docker-compose build --no-cache
docker-compose up -d
```

### Остановка
```bash
systemctl stop jarvis
# или
docker-compose down
```

## 🎯 Особенности

### Автономная работа
- ✅ Непрерывная работа 24/7
- ✅ Автоматическое восстановление после сбоев
- ✅ Самоисцеление системы
- ✅ Автоматические обновления

### Визуальный интеллект
- ✅ Анализ интерфейса в реальном времени
- ✅ Автоматическое обнаружение проблем
- ✅ Генерация предложений по улучшению
- ✅ Мониторинг пользовательского опыта

### Безопасность
- ✅ HTTPS шифрование
- ✅ Файрвол настроен
- ✅ Безопасные заголовки
- ✅ Регулярные обновления безопасности

## 📱 API Endpoints

### Основные
- `GET /`: Веб-интерфейс
- `GET /api/status`: Статус системы
- `GET /api/vision/status`: Статус визуального анализа

### Управление
- `POST /api/tasks`: Создание задачи
- `POST /api/self-improvement/trigger`: Запуск самоулучшения

### WebSocket
- `WS /ws`: Обновления в реальном времени

## 🚨 Устранение неполадок

### Система не запускается
1. Проверьте логи: `docker-compose logs jarvis`
2. Проверьте порты: `netstat -tlnp | grep 8080`
3. Проверьте Docker: `systemctl status docker`

### Высокая загрузка
1. Проверьте ресурсы: `./monitor.sh`
2. Перезапустите систему: `systemctl restart jarvis`
3. Проверьте логи на ошибки

### Проблемы с SSL
1. Пересоздайте сертификаты: `./create_ssl.sh`
2. Проверьте конфигурацию nginx: `nginx -t`
3. Перезапустите nginx: `systemctl restart nginx`

## 📞 Поддержка

Для получения поддержки:
1. Проверьте логи системы
2. Запустите диагностику: `./monitor.sh`
3. Создайте issue в репозитории

## 🎉 Дополнительные функции

### Telegram уведомления
1. Создайте бота: @BotFather
2. Получите токен и chat_id
3. Обновите monitor.sh с вашими данными

### Автоматические резервные копии
```bash
# Добавьте в crontab
0 4 * * * /opt/autonomous-jarvis/backup.sh
```

### Масштабирование
Для горизонтального масштабирования используйте Kubernetes:
```bash
kubectl apply -f k8s-deployment.yaml
```
"""
        
        with open('/workspace/DEPLOYMENT_README.md', 'w') as f:
            f.write(readme_content)
        
        logger.info("✅ README для развертывания создан")
    
    def deploy_all(self):
        """Создание всех файлов для развертывания"""
        logger.info("🚀 Начало создания файлов для облачного развертывания...")
        
        self.create_dockerfile()
        self.create_requirements_file()
        self.create_docker_compose()
        self.create_nginx_config()
        self.create_ssl_certificates()
        self.create_systemd_service()
        self.create_monitoring_script()
        self.create_crontab_entry()
        self.create_deployment_script()
        self.create_kubernetes_manifests()
        self.create_terraform_config()
        self.create_readme()
        
        logger.info("✅ Все файлы для развертывания созданы!")
        logger.info("📁 Файлы находятся в: /workspace/")
        logger.info("🚀 Для развертывания запустите: sudo ./deploy.sh")
        logger.info("☁️ Для AWS: terraform init && terraform apply")
        logger.info("🐳 Для Docker: docker-compose up -d")

if __name__ == "__main__":
    deployment = CloudDeployment()
    deployment.deploy_all()