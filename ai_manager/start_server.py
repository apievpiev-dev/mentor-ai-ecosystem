#!/usr/bin/env python3
"""
Скрипт запуска AI Manager сервера
"""

import asyncio
import uvicorn
import logging
from config import config
from main import app
from monitoring.logger import logger, performance_monitor


async def start_background_tasks():
    """Запуск фоновых задач"""
    if config.ENABLE_PERFORMANCE_MONITORING:
        # Запускаем мониторинг производительности
        async def monitor_system():
            while True:
                try:
                    await performance_monitor.record_system_metrics()
                    await asyncio.sleep(config.SYSTEM_METRICS_INTERVAL)
                except Exception as e:
                    logger.logger.error(f"Ошибка мониторинга системы: {e}")
        
        # Запускаем задачу мониторинга
        asyncio.create_task(monitor_system())
        logger.logger.info("Мониторинг производительности запущен")


def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()
        ]
    )


def main():
    """Главная функция запуска"""
    print("🚀 Запуск AI Manager...")
    
    # Настраиваем логирование
    setup_logging()
    
    # Запускаем фоновые задачи
    asyncio.run(start_background_tasks())
    
    # Запускаем сервер
    logger.logger.info(f"Запуск сервера на {config.HOST}:{config.PORT}")
    
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower(),
        access_log=True
    )


if __name__ == "__main__":
    main()
