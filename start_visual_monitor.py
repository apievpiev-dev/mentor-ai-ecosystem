#!/usr/bin/env python3
"""
Запуск визуального монитора JARVIS
"""

import asyncio
import logging
from visual_monitor import VisualMonitor

async def main():
    """Основная функция"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("👁️ Запуск JARVIS Visual Monitor")
    print("===============================")
    
    monitor = VisualMonitor()
    
    try:
        print("🚀 Визуальный мониторинг запущен!")
        print("📊 Проверяем страницы каждые 30 секунд")
        print("📸 Скриншоты сохраняются в /home/mentor/visual_screenshots/")
        print("📋 Отчеты в /home/mentor/visual_reports/")
        print("🛑 Нажмите Ctrl+C для остановки")
        print()
        
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки")
        monitor.stop_monitoring()
        print("✅ Визуальный мониторинг остановлен")

if __name__ == "__main__":
    asyncio.run(main())
