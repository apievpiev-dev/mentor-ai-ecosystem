#!/usr/bin/env python3
"""
Start Neural System - Главный скрипт запуска системы нейросетей
Запускает все компоненты в правильном порядке
"""

import asyncio
import logging
import signal
import sys
import time
import subprocess
import os
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/neural_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NeuralSystemLauncher:
    """Запускатор системы нейросетей"""
    
    def __init__(self):
        self.processes = {}
        self.running = False
        self.base_path = Path("/workspace")
        
    async def check_dependencies(self):
        """Проверка зависимостей"""
        logger.info("🔍 Проверка зависимостей...")
        
        # Проверяем Python модули
        required_modules = [
            "fastapi", "uvicorn", "aiohttp", "asyncio", 
            "requests", "numpy", "pandas", "matplotlib"
        ]
        
        missing_modules = []
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)
        
        if missing_modules:
            logger.error(f"❌ Отсутствуют модули: {', '.join(missing_modules)}")
            logger.info("💡 Установите их командой: pip install " + " ".join(missing_modules))
            return False
        
        # Проверяем Ollama
        try:
            result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✅ Ollama найден")
            else:
                logger.warning("⚠️ Ollama не найден, но система может работать с другими провайдерами")
        except FileNotFoundError:
            logger.warning("⚠️ Ollama не установлен, но система может работать с другими провайдерами")
        
        logger.info("✅ Зависимости проверены")
        return True
    
    async def start_ollama(self):
        """Запуск Ollama"""
        try:
            logger.info("🚀 Запуск Ollama...")
            
            # Проверяем, не запущен ли уже Ollama
            result = subprocess.run(['pgrep', '-f', 'ollama'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✅ Ollama уже запущен")
                return True
            
            # Запускаем Ollama
            process = subprocess.Popen(
                ['ollama', 'serve'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid
            )
            
            self.processes['ollama'] = process
            logger.info(f"✅ Ollama запущен (PID: {process.pid})")
            
            # Ждем запуска
            await asyncio.sleep(5)
            
            # Проверяем доступность
            import requests
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Ollama доступен")
                    return True
                else:
                    logger.warning("⚠️ Ollama запущен, но API недоступен")
                    return False
            except:
                logger.warning("⚠️ Ollama запущен, но API недоступен")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка запуска Ollama: {e}")
            return False
    
    async def start_unified_interface(self):
        """Запуск единого интерфейса"""
        try:
            logger.info("🚀 Запуск Unified Neural Interface...")
            
            process = subprocess.Popen(
                [sys.executable, str(self.base_path / "unified_neural_interface.py")],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid
            )
            
            self.processes['unified_interface'] = process
            logger.info(f"✅ Unified Neural Interface запущен (PID: {process.pid})")
            
            # Ждем запуска
            await asyncio.sleep(10)
            
            # Проверяем доступность
            import requests
            try:
                response = requests.get("http://localhost:8081/api/system/status", timeout=10)
                if response.status_code == 200:
                    logger.info("✅ Unified Neural Interface доступен")
                    return True
                else:
                    logger.warning("⚠️ Unified Neural Interface запущен, но API недоступен")
                    return False
            except:
                logger.warning("⚠️ Unified Neural Interface запущен, но API недоступен")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка запуска Unified Neural Interface: {e}")
            return False
    
    async def start_autonomous_system(self):
        """Запуск автономной системы"""
        try:
            logger.info("🚀 Запуск Autonomous Neural System...")
            
            process = subprocess.Popen(
                [sys.executable, str(self.base_path / "autonomous_neural_system.py")],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid
            )
            
            self.processes['autonomous_system'] = process
            logger.info(f"✅ Autonomous Neural System запущен (PID: {process.pid})")
            
            # Ждем запуска
            await asyncio.sleep(5)
            
            logger.info("✅ Autonomous Neural System запущен")
            return True
                
        except Exception as e:
            logger.error(f"❌ Ошибка запуска Autonomous Neural System: {e}")
            return False
    
    async def monitor_processes(self):
        """Мониторинг процессов"""
        while self.running:
            try:
                for name, process in self.processes.items():
                    if process.poll() is not None:
                        logger.warning(f"⚠️ Процесс {name} завершился неожиданно (PID: {process.pid})")
                        
                        # Перезапускаем процесс
                        if name == 'ollama':
                            await self.start_ollama()
                        elif name == 'unified_interface':
                            await self.start_unified_interface()
                        elif name == 'autonomous_system':
                            await self.start_autonomous_system()
                
                await asyncio.sleep(30)  # Проверяем каждые 30 секунд
                
            except Exception as e:
                logger.error(f"❌ Ошибка мониторинга процессов: {e}")
                await asyncio.sleep(30)
    
    async def start(self):
        """Запуск всей системы"""
        logger.info("🚀 Запуск Neural System...")
        self.running = True
        
        try:
            # 1. Проверяем зависимости
            if not await self.check_dependencies():
                logger.error("❌ Не все зависимости установлены")
                return False
            
            # 2. Запускаем Ollama
            await self.start_ollama()
            
            # 3. Запускаем Unified Neural Interface
            if not await self.start_unified_interface():
                logger.error("❌ Не удалось запустить Unified Neural Interface")
                return False
            
            # 4. Запускаем Autonomous Neural System
            await self.start_autonomous_system()
            
            logger.info("✅ Neural System полностью запущена!")
            logger.info("🌐 Веб-интерфейс: http://localhost:8081")
            logger.info("📊 API статуса: http://localhost:8081/api/system/status")
            logger.info("🤖 Список агентов: http://localhost:8081/api/agents")
            
            # 5. Запускаем мониторинг процессов
            await self.monitor_processes()
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска системы: {e}")
            await self.stop()
    
    async def stop(self):
        """Остановка системы"""
        logger.info("🛑 Остановка Neural System...")
        self.running = False
        
        for name, process in self.processes.items():
            try:
                if process.poll() is None:
                    logger.info(f"🛑 Остановка процесса {name} (PID: {process.pid})")
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    process.wait(timeout=10)
            except Exception as e:
                logger.error(f"❌ Ошибка остановки процесса {name}: {e}")
        
        self.processes.clear()
        logger.info("✅ Neural System остановлена")

def signal_handler(signum, frame):
    """Обработчик сигналов"""
    logger.info(f"📡 Получен сигнал {signum}, завершение работы...")
    asyncio.create_task(launcher.stop())

async def main():
    """Главная функция"""
    global launcher
    launcher = NeuralSystemLauncher()
    
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await launcher.start()
    except KeyboardInterrupt:
        logger.info("📡 Получен сигнал прерывания")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
    finally:
        await launcher.stop()

if __name__ == "__main__":
    print("🧠 Neural System Launcher")
    print("=" * 50)
    print("Запуск автономной системы нейросетей...")
    print("Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    asyncio.run(main())