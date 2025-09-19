#!/usr/bin/env python3
"""
Скрипт запуска системы множественных AI-агентов
Запускает интегрированную систему с веб-интерфейсом
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
sys.path.append('/home/mentor')

# Импортируем наши модули
from integrated_agent_system import get_integrated_system
from chat_server import app, manager, system_stats

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('multi_agent_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MultiAgentSystemLauncher:
    """Запускатор системы множественных агентов"""
    
    def __init__(self):
        self.running = False
        self.server_thread = None
        self.system_thread = None
        
    async def start_system(self):
        """Запуск системы агентов"""
        try:
            logger.info("🚀 Запуск системы множественных AI-агентов...")
            
            # Запускаем интегрированную систему
            integrated_system = get_integrated_system()
            await integrated_system.start()
            
            # Принудительно устанавливаем статус running
            integrated_system.running = True
            
            # Обновляем функции в chat_server для использования интегрированной системы
            self._patch_chat_server(integrated_system)
            
            logger.info("✅ Система агентов запущена")
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска системы агентов: {e}")
            raise
    
    def _patch_chat_server(self, integrated_system):
        """Обновление chat_server для использования интегрированной системы"""
        try:
            # Заменяем функции в chat_server
            import chat_server
            
            # Обновляем multi_agent_system в chat_server
            chat_server.multi_agent_system = integrated_system.multi_agent_system
            
            # Обновляем функции обработки сообщений в chat_server
            async def process_user_message_patched(message: str, user_id: str = "user"):
                return await integrated_system.process_user_message(message, user_id)
            
            # Заменяем функцию в chat_server, а не в multi_agent_system
            chat_server.process_user_message = process_user_message_patched
            
            logger.info("✅ Chat server обновлен для работы с интегрированной системой")
            
        except Exception as e:
            logger.error(f"❌ Ошибка обновления chat_server: {e}")
    
    def start_web_server(self, host="0.0.0.0", port=8080):
        """Запуск веб-сервера"""
        try:
            logger.info(f"🌐 Запуск веб-сервера на {host}:{port}")
            
            # Запускаем сервер в отдельном потоке
            def run_server():
                uvicorn.run(
                    app,
                    host=host,
                    port=port,
                    log_level="info",
                    access_log=True
                )
            
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            
            logger.info(f"✅ Веб-сервер запущен на http://{host}:{port}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска веб-сервера: {e}")
            raise
    
    async def stop_system(self):
        """Остановка системы"""
        try:
            logger.info("🛑 Остановка системы множественных агентов...")
            
            self.running = False
            
            # Останавливаем интегрированную систему
            integrated_system = get_integrated_system()
            await integrated_system.stop()
            
            logger.info("✅ Система остановлена")
            
        except Exception as e:
            logger.error(f"❌ Ошибка остановки системы: {e}")
    
    def run(self, host="0.0.0.0", port=8080):
        """Запуск всей системы"""
        try:
            logger.info("🎯 Запуск системы множественных AI-агентов")
            logger.info("=" * 60)
            
            # Создаем event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Запускаем систему агентов
            loop.run_until_complete(self.start_system())
            
            # Запускаем веб-сервер
            self.start_web_server(host, port)
            
            self.running = True
            
            # Выводим информацию о системе
            self._print_system_info(host, port)
            
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
    
    def _print_system_info(self, host, port):
        """Вывод информации о системе"""
        print("\n" + "=" * 60)
        print("🎉 СИСТЕМА МНОЖЕСТВЕННЫХ AI-АГЕНТОВ ЗАПУЩЕНА!")
        print("=" * 60)
        print(f"🌐 Веб-интерфейс: http://{host}:{port}")
        print(f"📊 API статуса: http://{host}:{port}/api/system/status")
        print(f"🤖 Список агентов: http://{host}:{port}/api/agents")
        print("=" * 60)
        print("📋 ДОСТУПНЫЕ АГЕНТЫ:")
        
        try:
            integrated_system = get_integrated_system()
            agents = integrated_system.get_available_agents()
            for agent in agents:
                print(f"  🤖 {agent['name']} ({agent['type']})")
                print(f"     Навыки: {', '.join(agent['skills'])}")
                print(f"     Статус: {agent['status']}")
                print()
        except Exception as e:
            print(f"  ❌ Ошибка получения списка агентов: {e}")
        
        print("=" * 60)
        print("💡 КАК ИСПОЛЬЗОВАТЬ:")
        print("1. Откройте браузер и перейдите по адресу выше")
        print("2. Выберите агента из боковой панели")
        print("3. Начните общение в чате")
        print("4. Каждый агент имеет свою специализацию")
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
    launcher = MultiAgentSystemLauncher()
    
    try:
        # Получаем параметры из командной строки
        host = "0.0.0.0"
        port = 8080
        
        if len(sys.argv) > 1:
            host = sys.argv[1]
        if len(sys.argv) > 2:
            port = int(sys.argv[2])
        
        # Запускаем систему
        launcher.run(host, port)
        
    except KeyboardInterrupt:
        logger.info("🛑 Система остановлена пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
