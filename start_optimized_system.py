#!/usr/bin/env python3
"""
Скрипт запуска оптимизированной системы Mentor
Запускает улучшенную систему с дашбордом мониторинга
"""

import asyncio
import logging
import sys
import time
import signal
import threading
from pathlib import Path
import uvicorn
from fastapi import FastAPI

# Добавляем путь к модулям
sys.path.append('/workspace')

# Импортируем наши модули
from optimized_autonomous_system import get_optimized_system
from enhanced_dashboard import app as dashboard_app
from chat_server import app as chat_app

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/optimized_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OptimizedSystemLauncher:
    """Запускатор оптимизированной системы"""
    
    def __init__(self):
        self.running = False
        self.dashboard_thread = None
        self.chat_thread = None
        self.system_task = None
        
    async def start_optimized_system(self):
        """Запуск оптимизированной системы агентов"""
        try:
            logger.info("🚀 Запуск оптимизированной системы агентов...")
            
            # Запускаем оптимизированную систему
            system = get_optimized_system()
            self.system_task = asyncio.create_task(system.start())
            
            logger.info("✅ Оптимизированная система агентов запущена")
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска оптимизированной системы: {e}")
            raise
    
    def start_dashboard_server(self, host="0.0.0.0", port=8081):
        """Запуск сервера дашборда"""
        try:
            logger.info(f"📊 Запуск дашборда на {host}:{port}")
            
            def run_dashboard():
                uvicorn.run(
                    dashboard_app,
                    host=host,
                    port=port,
                    log_level="info",
                    access_log=True
                )
            
            self.dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
            self.dashboard_thread.start()
            
            logger.info(f"✅ Дашборд запущен на http://{host}:{port}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска дашборда: {e}")
            raise
    
    def start_chat_server(self, host="0.0.0.0", port=8080):
        """Запуск сервера чата"""
        try:
            logger.info(f"💬 Запуск чата на {host}:{port}")
            
            def run_chat():
                uvicorn.run(
                    chat_app,
                    host=host,
                    port=port,
                    log_level="info",
                    access_log=True
                )
            
            self.chat_thread = threading.Thread(target=run_chat, daemon=True)
            self.chat_thread.start()
            
            logger.info(f"✅ Чат запущен на http://{host}:{port}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска чата: {e}")
            raise
    
    async def stop_system(self):
        """Остановка системы"""
        try:
            logger.info("🛑 Остановка оптимизированной системы...")
            
            self.running = False
            
            # Останавливаем оптимизированную систему
            if self.system_task:
                self.system_task.cancel()
                try:
                    await self.system_task
                except asyncio.CancelledError:
                    pass
            
            system = get_optimized_system()
            system.stop()
            
            logger.info("✅ Оптимизированная система остановлена")
            
        except Exception as e:
            logger.error(f"❌ Ошибка остановки системы: {e}")
    
    def run(self, chat_host="0.0.0.0", chat_port=8080, dashboard_host="0.0.0.0", dashboard_port=8081):
        """Запуск всей системы"""
        try:
            logger.info("🎯 Запуск оптимизированной системы Mentor")
            logger.info("=" * 60)
            
            # Создаем event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Запускаем оптимизированную систему агентов
            loop.run_until_complete(self.start_optimized_system())
            
            # Запускаем серверы
            self.start_chat_server(chat_host, chat_port)
            self.start_dashboard_server(dashboard_host, dashboard_port)
            
            self.running = True
            
            # Выводим информацию о системе
            self._print_system_info(chat_host, chat_port, dashboard_host, dashboard_port)
            
            # Держим систему запущенной
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("📡 Получен сигнал прерывания")
                loop.run_until_complete(self.stop_system())
            except Exception as e:
                logger.error(f"❌ Ошибка в основном цикле: {e}")
                loop.run_until_complete(self.stop_system())
                
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}")
            raise
    
    def _print_system_info(self, chat_host, chat_port, dashboard_host, dashboard_port):
        """Вывод информации о системе"""
        print("\n" + "=" * 60)
        print("🎉 ОПТИМИЗИРОВАННАЯ СИСТЕМА MENTOR ЗАПУЩЕНА!")
        print("=" * 60)
        print(f"💬 Веб-интерфейс чата: http://{chat_host}:{chat_port}")
        print(f"📊 Дашборд мониторинга: http://{dashboard_host}:{dashboard_port}")
        print(f"📈 API статуса: http://{chat_host}:{chat_port}/api/system/status")
        print(f"🤖 Список агентов: http://{chat_host}:{chat_port}/api/agents")
        print("=" * 60)
        print("🚀 НОВЫЕ ВОЗМОЖНОСТИ:")
        print("  📊 Детальный мониторинг производительности")
        print("  🏥 Автоматическая проверка здоровья системы")
        print("  ⚡ Оптимизация на основе метрик")
        print("  📈 Графики и аналитика в реальном времени")
        print("  🔧 Автоматическое восстановление при сбоях")
        print("  💾 Сохранение и анализ истории производительности")
        print("=" * 60)
        print("💡 КАК ИСПОЛЬЗОВАТЬ:")
        print("1. Откройте дашборд для мониторинга системы")
        print("2. Используйте чат для взаимодействия с агентами")
        print("3. Система автоматически оптимизирует свою работу")
        print("4. Все метрики сохраняются и анализируются")
        print("=" * 60)
        print("🛑 Для остановки нажмите Ctrl+C")
        print("=" * 60 + "\n")

def signal_handler(signum, frame):
    """Обработчик сигналов"""
    logger.info(f"📡 Получен сигнал {signum}")
    global launcher
    launcher.running = False

# Регистрируем обработчики сигналов
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    # Создаем и запускаем систему
    launcher = OptimizedSystemLauncher()
    
    try:
        # Получаем параметры из командной строки
        chat_host = "0.0.0.0"
        chat_port = 8080
        dashboard_host = "0.0.0.0"
        dashboard_port = 8081
        
        if len(sys.argv) > 1:
            chat_host = sys.argv[1]
        if len(sys.argv) > 2:
            chat_port = int(sys.argv[2])
        if len(sys.argv) > 3:
            dashboard_host = sys.argv[3]
        if len(sys.argv) > 4:
            dashboard_port = int(sys.argv[4])
        
        # Запускаем систему
        launcher.run(chat_host, chat_port, dashboard_host, dashboard_port)
        
    except KeyboardInterrupt:
        logger.info("🛑 Система остановлена пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)