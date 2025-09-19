#!/usr/bin/env python3
"""
Скрипт развертывания JARVIS на сервере
Автоматически настраивает и запускает JARVIS для непрерывной работы
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JarvisDeployer:
    def __init__(self):
        self.base_path = Path("/workspace")
        self.service_file = self.base_path / "jarvis.service"
        self.systemd_path = Path("/etc/systemd/system/jarvis.service")
    
    def install_systemd_service(self):
        """Установка systemd сервиса"""
        logger.info("🔧 Установка systemd сервиса...")
        
        try:
            # Копируем файл сервиса
            subprocess.run([
                "sudo", "cp", str(self.service_file), str(self.systemd_path)
            ], check=True)
            
            # Перезагружаем systemd
            subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
            
            # Включаем сервис
            subprocess.run(["sudo", "systemctl", "enable", "jarvis"], check=True)
            
            logger.info("✅ Systemd сервис установлен")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Ошибка установки сервиса: {e}")
            return False
    
    def start_jarvis_service(self):
        """Запуск JARVIS через systemd"""
        logger.info("🚀 Запуск JARVIS сервиса...")
        
        try:
            # Запускаем сервис
            subprocess.run(["sudo", "systemctl", "start", "jarvis"], check=True)
            
            # Проверяем статус
            result = subprocess.run([
                "sudo", "systemctl", "is-active", "jarvis"
            ], capture_output=True, text=True)
            
            if result.stdout.strip() == "active":
                logger.info("✅ JARVIS сервис запущен успешно")
                return True
            else:
                logger.error("❌ JARVIS сервис не запустился")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Ошибка запуска сервиса: {e}")
            return False
    
    def check_jarvis_status(self):
        """Проверка статуса JARVIS"""
        logger.info("🔍 Проверка статуса JARVIS...")
        
        try:
            # Проверяем статус сервиса
            result = subprocess.run([
                "sudo", "systemctl", "status", "jarvis", "--no-pager"
            ], capture_output=True, text=True)
            
            logger.info("📊 Статус сервиса:")
            logger.info(result.stdout)
            
            # Проверяем API
            import requests
            response = requests.get("http://localhost:8080/api/system/status", timeout=5)
            if response.status_code == 200:
                logger.info("✅ JARVIS API работает корректно")
                return True
            else:
                logger.warning("⚠️ JARVIS API недоступен")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка проверки статуса: {e}")
            return False
    
    def setup_firewall(self):
        """Настройка файрвола"""
        logger.info("🔥 Настройка файрвола...")
        
        try:
            # Разрешаем порт 8080
            subprocess.run([
                "sudo", "ufw", "allow", "8080"
            ], check=True)
            
            logger.info("✅ Файрвол настроен")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️ Ошибка настройки файрвола: {e}")
            return False
    
    def create_startup_script(self):
        """Создание скрипта автозапуска"""
        logger.info("📝 Создание скрипта автозапуска...")
        
        startup_script = self.base_path / "start_jarvis.sh"
        
        script_content = f"""#!/bin/bash
# JARVIS Startup Script

echo "🚀 Запуск JARVIS..."

# Активируем виртуальное окружение
source {self.base_path}/jarvis_env/bin/activate

# Запускаем JARVIS
cd {self.base_path}
python3 start_jarvis_autonomous.py

echo "✅ JARVIS запущен!"
"""
        
        with open(startup_script, 'w') as f:
            f.write(script_content)
        
        # Делаем скрипт исполняемым
        os.chmod(startup_script, 0o755)
        
        logger.info("✅ Скрипт автозапуска создан")
        return True
    
    def deploy(self):
        """Основной процесс развертывания"""
        logger.info("🎯 Начинаем развертывание JARVIS...")
        
        # 1. Создаем скрипт автозапуска
        if not self.create_startup_script():
            return False
        
        # 2. Настраиваем файрвол
        self.setup_firewall()
        
        # 3. Устанавливаем systemd сервис
        if not self.install_systemd_service():
            return False
        
        # 4. Запускаем сервис
        if not self.start_jarvis_service():
            return False
        
        # 5. Проверяем статус
        time.sleep(5)
        if not self.check_jarvis_status():
            return False
        
        logger.info("🎉 JARVIS успешно развернут!")
        logger.info("🌐 Веб-интерфейс: http://localhost:8080")
        logger.info("📊 API статуса: http://localhost:8080/api/system/status")
        logger.info("🔧 Управление сервисом:")
        logger.info("   sudo systemctl start jarvis    - запустить")
        logger.info("   sudo systemctl stop jarvis     - остановить")
        logger.info("   sudo systemctl status jarvis   - статус")
        logger.info("   sudo systemctl restart jarvis  - перезапустить")
        
        return True

def main():
    """Главная функция"""
    deployer = JarvisDeployer()
    
    try:
        success = deployer.deploy()
        if success:
            logger.info("✅ Развертывание завершено успешно!")
            sys.exit(0)
        else:
            logger.error("❌ Развертывание завершилось с ошибками")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка развертывания: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()