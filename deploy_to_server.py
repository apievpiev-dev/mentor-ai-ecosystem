#!/usr/bin/env python3
"""
Скрипт развертывания системы множественных AI-агентов на сервере
Обеспечивает автономную работу даже при отключении компьютера
"""

import os
import sys
import subprocess
import logging
import time
import json
import requests
from datetime import datetime
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/mentor/deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ServerDeployment:
    """Класс для развертывания системы на сервере"""
    
    def __init__(self):
        self.project_dir = Path("/home/mentor")
        self.service_name = "multi-agent-system"
        self.port = 8080
        self.systemd_service_file = f"/etc/systemd/system/{self.service_name}.service"
        
    def check_system_requirements(self):
        """Проверка системных требований"""
        logger.info("🔍 Проверка системных требований...")
        
        requirements = {
            "python3": self._check_command("python3 --version"),
            "pip": self._check_command("pip --version"),
            "systemd": self._check_command("systemctl --version"),
            "nginx": self._check_command("nginx -v"),
            "ufw": self._check_command("ufw --version")
        }
        
        for req, status in requirements.items():
            if status:
                logger.info(f"✅ {req}: OK")
            else:
                logger.warning(f"⚠️ {req}: НЕ НАЙДЕН")
        
        return all(requirements.values())
    
    def _check_command(self, command):
        """Проверка доступности команды"""
        try:
            result = subprocess.run(command.split(), capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def setup_environment(self):
        """Настройка окружения"""
        logger.info("🔧 Настройка окружения...")
        
        # Создание виртуального окружения
        venv_path = self.project_dir / "multi_agent_env"
        if not venv_path.exists():
            logger.info("📦 Создание виртуального окружения...")
            subprocess.run(["python3", "-m", "venv", str(venv_path)], check=True)
        
        # Активация и установка зависимостей
        pip_path = venv_path / "bin" / "pip"
        requirements_file = self.project_dir / "requirements_multi_agent.txt"
        
        if requirements_file.exists():
            logger.info("📦 Установка зависимостей...")
            subprocess.run([str(pip_path), "install", "-r", str(requirements_file)], check=True)
        
        # Установка дополнительных зависимостей для автономной работы
        additional_packages = [
            "selenium",
            "pillow",
            "requests",
            "psutil",
            "schedule",
            "crontab"
        ]
        
        for package in additional_packages:
            try:
                subprocess.run([str(pip_path), "install", package], check=True)
                logger.info(f"✅ Установлен {package}")
            except subprocess.CalledProcessError:
                logger.warning(f"⚠️ Не удалось установить {package}")
    
    def create_systemd_service(self):
        """Создание systemd сервиса для автономной работы"""
        logger.info("🔧 Создание systemd сервиса...")
        
        service_content = f"""[Unit]
Description=Multi-Agent AI System
After=network.target
Wants=network.target

[Service]
Type=simple
User=mentor
Group=mentor
WorkingDirectory={self.project_dir}
Environment=PATH={self.project_dir}/multi_agent_env/bin
ExecStart={self.project_dir}/multi_agent_env/bin/python {self.project_dir}/start_multi_agent_system.py
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
"""
        
        try:
            with open(self.systemd_service_file, 'w') as f:
                f.write(service_content)
            
            # Перезагрузка systemd и включение сервиса
            subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
            subprocess.run(["sudo", "systemctl", "enable", self.service_name], check=True)
            
            logger.info("✅ Systemd сервис создан и включен")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Ошибка создания systemd сервиса: {e}")
            return False
    
    def setup_nginx_proxy(self):
        """Настройка Nginx как прокси"""
        logger.info("🌐 Настройка Nginx прокси...")
        
        nginx_config = f"""
server {{
    listen 80;
    server_name _;
    
    location / {{
        proxy_pass http://127.0.0.1:{self.port};
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }}
    
    # WebSocket поддержка
    location /ws {{
        proxy_pass http://127.0.0.1:{self.port};
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
        
        try:
            config_file = "/etc/nginx/sites-available/multi-agent-system"
            with open(config_file, 'w') as f:
                f.write(nginx_config)
            
            # Создание символической ссылки
            subprocess.run(["sudo", "ln", "-sf", config_file, "/etc/nginx/sites-enabled/"], check=True)
            
            # Удаление дефолтного сайта
            default_site = "/etc/nginx/sites-enabled/default"
            if os.path.exists(default_site):
                subprocess.run(["sudo", "rm", default_site], check=True)
            
            # Тест и перезагрузка Nginx
            subprocess.run(["sudo", "nginx", "-t"], check=True)
            subprocess.run(["sudo", "systemctl", "reload", "nginx"], check=True)
            
            logger.info("✅ Nginx настроен как прокси")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Ошибка настройки Nginx: {e}")
            return False
    
    def setup_firewall(self):
        """Настройка файрвола"""
        logger.info("🔥 Настройка файрвола...")
        
        try:
            # Включение UFW
            subprocess.run(["sudo", "ufw", "--force", "enable"], check=True)
            
            # Разрешение SSH
            subprocess.run(["sudo", "ufw", "allow", "ssh"], check=True)
            
            # Разрешение HTTP и HTTPS
            subprocess.run(["sudo", "ufw", "allow", "80/tcp"], check=True)
            subprocess.run(["sudo", "ufw", "allow", "443/tcp"], check=True)
            
            # Разрешение локального доступа к порту системы
            subprocess.run(["sudo", "ufw", "allow", "from", "127.0.0.1", "to", "any", "port", str(self.port)], check=True)
            
            logger.info("✅ Файрвол настроен")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Ошибка настройки файрвола: {e}")
            return False
    
    def setup_monitoring(self):
        """Настройка мониторинга системы"""
        logger.info("📊 Настройка мониторинга...")
        
        # Создание скрипта мониторинга
        monitor_script = self.project_dir / "monitor_system.py"
        monitor_content = '''#!/usr/bin/env python3
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
'''
        
        with open(monitor_script, 'w') as f:
            f.write(monitor_content)
        
        # Сделать скрипт исполняемым
        os.chmod(monitor_script, 0o755)
        
        # Создание systemd сервиса для мониторинга
        monitor_service = f"""[Unit]
Description=Multi-Agent System Monitor
After=multi-agent-system.service

[Service]
Type=simple
User=mentor
Group=mentor
WorkingDirectory={self.project_dir}
ExecStart={self.project_dir}/monitor_system.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
"""
        
        with open("/etc/systemd/system/multi-agent-monitor.service", 'w') as f:
            f.write(monitor_service)
        
        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
        subprocess.run(["sudo", "systemctl", "enable", "multi-agent-monitor"], check=True)
        
        logger.info("✅ Мониторинг настроен")
    
    def setup_autonomous_features(self):
        """Настройка автономных функций"""
        logger.info("🤖 Настройка автономных функций...")
        
        # Создание скрипта автономного улучшения
        autonomous_script = self.project_dir / "autonomous_improvement.py"
        autonomous_content = '''#!/usr/bin/env python3
"""
Автономное улучшение системы через агентов
"""

import asyncio
import requests
import logging
from datetime import datetime
from vision_agent import vision_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def autonomous_improvement_cycle():
    """Цикл автономного улучшения"""
    try:
        # Инициализация Vision Agent
        await vision_agent.initialize()
        
        # Анализ текущего состояния
        logger.info("🔍 Анализ текущего состояния системы...")
        improvements = await vision_agent.suggest_improvements()
        
        # Отправка предложений в систему
        if improvements and not improvements.get("error"):
            logger.info("💡 Отправка предложений по улучшению...")
            
            # Отправляем предложения через API
            for suggestion in improvements.get("ui_improvements", []):
                await send_improvement_suggestion(suggestion)
            
            for issue in improvements.get("ui_issues", []):
                await report_issue(issue)
        
        # Проверка здоровья системы
        health_check = await vision_agent.monitor_system_health()
        if health_check.get("web_interface", {}).get("status") != "online":
            logger.warning("🚨 Обнаружена проблема с веб-интерфейсом")
            await request_system_restart()
        
        await vision_agent.cleanup()
        
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

async def report_issue(issue):
    """Сообщение о проблеме"""
    try:
        response = requests.post(
            "http://localhost:8080/api/chat/send",
            json={
                "message": f"Обнаружена проблема: {issue}",
                "user_id": "autonomous_agent"
            },
            timeout=10
        )
        if response.status_code == 200:
            logger.info(f"✅ Проблема зарегистрирована: {issue}")
    except Exception as e:
        logger.error(f"❌ Ошибка регистрации проблемы: {e}")

async def request_system_restart():
    """Запрос перезапуска системы"""
    logger.warning("🔄 Запрос перезапуска системы...")
    # Здесь можно добавить логику автоматического перезапуска

async def main():
    """Основной цикл"""
    while True:
        await autonomous_improvement_cycle()
        await asyncio.sleep(3600)  # Каждый час

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        with open(autonomous_script, 'w') as f:
            f.write(autonomous_content)
        
        os.chmod(autonomous_script, 0o755)
        
        # Создание systemd сервиса для автономного улучшения
        autonomous_service = f"""[Unit]
Description=Autonomous System Improvement
After=multi-agent-system.service

[Service]
Type=simple
User=mentor
Group=mentor
WorkingDirectory={self.project_dir}
Environment=PATH={self.project_dir}/multi_agent_env/bin
ExecStart={self.project_dir}/multi_agent_env/bin/python {self.project_dir}/autonomous_improvement.py
Restart=always
RestartSec=300

[Install]
WantedBy=multi-user.target
"""
        
        with open("/etc/systemd/system/autonomous-improvement.service", 'w') as f:
            f.write(autonomous_service)
        
        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
        subprocess.run(["sudo", "systemctl", "enable", "autonomous-improvement"], check=True)
        
        logger.info("✅ Автономные функции настроены")
    
    def start_services(self):
        """Запуск всех сервисов"""
        logger.info("🚀 Запуск сервисов...")
        
        services = [
            "multi-agent-system",
            "multi-agent-monitor", 
            "autonomous-improvement",
            "nginx"
        ]
        
        for service in services:
            try:
                subprocess.run(["sudo", "systemctl", "start", service], check=True)
                subprocess.run(["sudo", "systemctl", "enable", service], check=True)
                logger.info(f"✅ Сервис {service} запущен")
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Ошибка запуска сервиса {service}: {e}")
    
    def verify_deployment(self):
        """Проверка развертывания"""
        logger.info("🔍 Проверка развертывания...")
        
        # Проверка доступности системы
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"http://localhost:{self.port}/api/system/status", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Система доступна и работает")
                    return True
            except:
                pass
            
            time.sleep(2)
            logger.info(f"⏳ Попытка {attempt + 1}/{max_attempts}...")
        
        logger.error("❌ Система недоступна после развертывания")
        return False
    
    def deploy(self):
        """Основной метод развертывания"""
        logger.info("🚀 Начало развертывания системы множественных AI-агентов...")
        
        try:
            # Проверка требований
            if not self.check_system_requirements():
                logger.error("❌ Не все системные требования выполнены")
                return False
            
            # Настройка окружения
            self.setup_environment()
            
            # Создание systemd сервиса
            if not self.create_systemd_service():
                return False
            
            # Настройка Nginx
            if not self.setup_nginx_proxy():
                return False
            
            # Настройка файрвола
            if not self.setup_firewall():
                return False
            
            # Настройка мониторинга
            self.setup_monitoring()
            
            # Настройка автономных функций
            self.setup_autonomous_features()
            
            # Запуск сервисов
            self.start_services()
            
            # Проверка развертывания
            if self.verify_deployment():
                logger.info("🎉 Развертывание завершено успешно!")
                logger.info(f"🌐 Система доступна по адресу: http://your-server-ip")
                logger.info("🤖 Система будет работать автономно даже при отключении компьютера")
                return True
            else:
                logger.error("❌ Развертывание завершилось с ошибками")
                return False
                
        except Exception as e:
            logger.error(f"❌ Критическая ошибка развертывания: {e}")
            return False

def main():
    """Главная функция"""
    deployment = ServerDeployment()
    success = deployment.deploy()
    
    if success:
        print("\n🎉 РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print("🌐 Система доступна по адресу: http://your-server-ip")
        print("🤖 Система работает автономно")
        print("📊 Мониторинг активен")
        print("🔄 Автономные улучшения включены")
    else:
        print("\n❌ РАЗВЕРТЫВАНИЕ ЗАВЕРШИЛОСЬ С ОШИБКАМИ")
        print("Проверьте логи: /home/mentor/deployment.log")
        sys.exit(1)

if __name__ == "__main__":
    main()

