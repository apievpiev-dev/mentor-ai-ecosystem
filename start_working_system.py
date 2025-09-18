#!/usr/bin/env python3
"""
Скрипт запуска рабочей автономной системы
"""

import asyncio
import logging
import signal
import sys
import time
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/mentor/start_working_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WorkingSystemLauncher:
    """Запускатор рабочей системы"""
    
    def __init__(self, host="0.0.0.0", port=8080):
        self.host = host
        self.port = port
        self.running = False
        self.server_process = None
        
    async def start_system(self):
        """Запуск рабочей системы"""
        try:
            logger.info("🚀 Запуск рабочей автономной системы...")
            
            # Импортируем и запускаем рабочий веб-сервер
            import uvicorn
            from working_chat_server import app
            
            # Запускаем сервер
            config = uvicorn.Config(
                app=app,
                host=self.host,
                port=self.port,
                log_level="info",
                access_log=True
            )
            
            server = uvicorn.Server(config)
            
            logger.info(f"🌐 Запуск веб-сервера на {self.host}:{self.port}")
            
            # Запускаем сервер в отдельной задаче
            self.server_process = asyncio.create_task(server.serve())
            
            self.running = True
            logger.info("✅ Рабочая автономная система запущена")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска рабочей системы: {e}")
            return False
    
    async def stop_system(self):
        """Остановка рабочей системы"""
        try:
            logger.info("🛑 Остановка рабочей автономной системы...")
            
            self.running = False
            
            if self.server_process:
                self.server_process.cancel()
                try:
                    await self.server_process
                except asyncio.CancelledError:
                    pass
            
            logger.info("✅ Рабочая автономная система остановлена")
            
        except Exception as e:
            logger.error(f"❌ Ошибка остановки рабочей системы: {e}")
    
    def run(self, host="0.0.0.0", port=8080):
        """Запуск системы"""
        self.host = host
        self.port = port
        
        # Настройка обработчиков сигналов
        def signal_handler(signum, frame):
            logger.info(f"📡 Получен сигнал {signum}")
            asyncio.create_task(self.stop_system())
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Запуск системы
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Запускаем систему
            loop.run_until_complete(self.start_system())
            
            # Держим систему работающей
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("📡 Получен сигнал прерывания")
            loop.run_until_complete(self.stop_system())
        except Exception as e:
            logger.error(f"❌ Ошибка в основном цикле: {e}")
            loop.run_until_complete(self.stop_system())
        finally:
            loop.close()

def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Запуск рабочей автономной системы")
    parser.add_argument("host", nargs="?", default="0.0.0.0", help="Хост для запуска сервера")
    parser.add_argument("port", nargs="?", type=int, default=8080, help="Порт для запуска сервера")
    
    args = parser.parse_args()
    
    launcher = WorkingSystemLauncher(args.host, args.port)
    launcher.run(args.host, args.port)

if __name__ == "__main__":
    main()
