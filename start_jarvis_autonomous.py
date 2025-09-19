#!/usr/bin/env python3
"""
Автономный запуск JARVIS
Скрипт для автоматического запуска и поддержания работы JARVIS
"""

import os
import sys
import time
import signal
import subprocess
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/jarvis_autonomous.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class JarvisAutonomousLauncher:
    def __init__(self):
        self.process = None
        self.running = False
        self.base_path = Path("/workspace")
        self.venv_path = self.base_path / "jarvis_env"
        self.jarvis_script = self.base_path / "jarvis_core_fixed.py"
        
    def check_dependencies(self):
        """Проверка зависимостей"""
        logger.info("🔍 Проверка зависимостей...")
        
        # Проверяем виртуальное окружение
        if not self.venv_path.exists():
            logger.error("❌ Виртуальное окружение не найдено")
            return False
        
        # Проверяем скрипт JARVIS
        if not self.jarvis_script.exists():
            logger.error("❌ Скрипт JARVIS не найден")
            return False
        
        logger.info("✅ Все зависимости найдены")
        return True
    
    def start_jarvis(self):
        """Запуск JARVIS"""
        logger.info("🚀 Запуск JARVIS...")
        
        try:
            # Команда для запуска
            cmd = [
                str(self.venv_path / "bin" / "python3"),
                str(self.jarvis_script)
            ]
            
            # Запускаем процесс
            self.process = subprocess.Popen(
                cmd,
                cwd=str(self.base_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )
            
            logger.info(f"✅ JARVIS запущен (PID: {self.process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска JARVIS: {e}")
            return False
    
    def check_jarvis_health(self):
        """Проверка здоровья JARVIS"""
        try:
            import requests
            response = requests.get("http://localhost:8080/api/system/status", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def monitor_jarvis(self):
        """Мониторинг JARVIS"""
        logger.info("👁️ Начинаем мониторинг JARVIS...")
        
        while self.running:
            try:
                # Проверяем, работает ли процесс
                if self.process and self.process.poll() is not None:
                    logger.warning("⚠️ JARVIS завершился неожиданно, перезапускаем...")
                    self.start_jarvis()
                
                # Проверяем здоровье через API
                if not self.check_jarvis_health():
                    logger.warning("⚠️ JARVIS не отвечает на API запросы")
                
                # Ждем 30 секунд
                time.sleep(30)
                
            except KeyboardInterrupt:
                logger.info("📡 Получен сигнал прерывания")
                self.stop()
                break
            except Exception as e:
                logger.error(f"❌ Ошибка мониторинга: {e}")
                time.sleep(10)
    
    def stop(self):
        """Остановка JARVIS"""
        logger.info("🛑 Остановка JARVIS...")
        self.running = False
        
        if self.process:
            try:
                # Отправляем сигнал SIGTERM
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                
                # Ждем завершения
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # Если не завершился, принудительно убиваем
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                    self.process.wait()
                
                logger.info("✅ JARVIS остановлен")
            except Exception as e:
                logger.error(f"❌ Ошибка остановки JARVIS: {e}")
    
    def run(self):
        """Основной цикл"""
        logger.info("🎯 Запуск автономного JARVIS...")
        
        # Проверяем зависимости
        if not self.check_dependencies():
            logger.error("❌ Не удалось запустить из-за отсутствующих зависимостей")
            return False
        
        # Запускаем JARVIS
        if not self.start_jarvis():
            logger.error("❌ Не удалось запустить JARVIS")
            return False
        
        # Ждем запуска
        logger.info("⏳ Ожидаем запуска JARVIS...")
        time.sleep(10)
        
        # Проверяем, что JARVIS запустился
        if self.check_jarvis_health():
            logger.info("✅ JARVIS успешно запущен и работает!")
            logger.info("🌐 Веб-интерфейс доступен: http://localhost:8080")
            logger.info("📊 API статуса: http://localhost:8080/api/system/status")
        else:
            logger.warning("⚠️ JARVIS запущен, но API недоступен")
        
        # Начинаем мониторинг
        self.running = True
        self.monitor_jarvis()
        
        return True

def signal_handler(signum, frame):
    """Обработчик сигналов"""
    logger.info(f"📡 Получен сигнал {signum}")
    if 'launcher' in globals():
        launcher.stop()
    sys.exit(0)

def main():
    """Главная функция"""
    global launcher
    
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Создаем и запускаем лаунчер
    launcher = JarvisAutonomousLauncher()
    
    try:
        launcher.run()
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
    finally:
        launcher.stop()

if __name__ == "__main__":
    main()