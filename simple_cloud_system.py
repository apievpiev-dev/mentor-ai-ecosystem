#!/usr/bin/env python3
"""
Упрощенная облачная система агентов
Работает с минимальными ресурсами
"""

import asyncio
import json
import logging
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from multi_agent_system import MultiAgentSystem
from ai_engine import ai_engine, generate_ai_response
from chat_server import app, manager, system_stats

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/mentor/simple_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleCloudSystem:
    """Упрощенная облачная система"""
    
    def __init__(self):
        self.running = False
        self.multi_agent_system = None
        self.startup_time = None
        
        # Настройка обработчиков сигналов
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Обработчик сигналов"""
        logger.info(f"📡 Получен сигнал {signum}, завершаем работу...")
        self.running = False
        sys.exit(0)
    
    async def start(self):
        """Запуск системы"""
        try:
            logger.info("☁️ Запуск упрощенной облачной системы...")
            
            # Создаем систему агентов
            self.multi_agent_system = MultiAgentSystem()
            
            # Обновляем chat_server для использования нашей системы
            self._patch_chat_server()
            
            # Запускаем веб-сервер
            self._start_web_server()
            
            self.running = True
            self.startup_time = datetime.now()
            
            logger.info("✅ Упрощенная облачная система запущена")
            
            # Основной цикл
            await self._main_loop()
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска системы: {e}")
            raise
    
    def _patch_chat_server(self):
        """Обновление chat_server"""
        try:
            import chat_server
            
            # Обновляем multi_agent_system в chat_server
            chat_server.multi_agent_system = self.multi_agent_system
            
            # Обновляем функции обработки сообщений
            async def process_user_message_patched(message: str, user_id: str = "user"):
                return await self.multi_agent_system.process_user_message(message, user_id)
            
            # НЕ заменяем метод, чтобы избежать рекурсии
            # chat_server.multi_agent_system.process_user_message = process_user_message_patched
            
            logger.info("✅ Chat server обновлен")
            
        except Exception as e:
            logger.error(f"❌ Ошибка обновления chat_server: {e}")
    
    def _start_web_server(self):
        """Запуск веб-сервера"""
        try:
            import uvicorn
            import threading
            
            def run_server():
                uvicorn.run(
                    app,
                    host="0.0.0.0",
                    port=8080,
                    log_level="info"
                )
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            logger.info("🌐 Веб-сервер запущен на http://0.0.0.0:8080")
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска веб-сервера: {e}")
    
    async def _main_loop(self):
        """Основной цикл"""
        try:
            while self.running:
                # Проверяем здоровье системы
                await self._health_check()
                
                # Пауза между итерациями
                await asyncio.sleep(30)
                
        except Exception as e:
            logger.error(f"❌ Ошибка в основном цикле: {e}")
    
    async def _health_check(self):
        """Проверка здоровья системы"""
        try:
            # Проверяем AI движок
            ai_status = ai_engine.get_status()
            ai_healthy = ai_status.get("default_engine") != "none"
            
            # Проверяем систему агентов
            system_status = self.multi_agent_system.get_system_status()
            system_healthy = system_status.get("system_status") == "stopped"
            
            if ai_healthy and not system_healthy:
                logger.info("💚 Система здорова")
            else:
                logger.warning("⚠️ Проблемы с системой")
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки здоровья: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус системы"""
        return {
            "running": self.running,
            "startup_time": self.startup_time.isoformat() if self.startup_time else None,
            "system_status": self.multi_agent_system.get_system_status() if self.multi_agent_system else None,
            "ai_status": ai_engine.get_status()
        }

# Глобальный экземпляр
simple_cloud_system = SimpleCloudSystem()

if __name__ == "__main__":
    # Запуск системы
    async def main():
        try:
            await simple_cloud_system.start()
        except KeyboardInterrupt:
            logger.info("🛑 Получен сигнал прерывания")
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}")
    
    asyncio.run(main())
