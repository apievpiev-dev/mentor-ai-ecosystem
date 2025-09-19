#!/usr/bin/env python3
"""
Автономный менеджер системы
Управляет системой, мониторит состояние и принимает решения
"""

import asyncio
import json
import logging
import time
import subprocess
import requests
from datetime import datetime
from typing import Dict, Any

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutonomousSystemManager:
    """Автономный менеджер системы"""
    
    def __init__(self, server_url="http://5.129.198.210:8080"):
        self.server_url = server_url
        self.running = False
        self.check_interval = 30  # секунд
        self.last_health_check = None
        self.consecutive_failures = 0
        self.max_failures = 3
        
    async def start(self):
        """Запуск автономного менеджера"""
        logger.info("🚀 Запуск автономного менеджера системы...")
        self.running = True
        
        while self.running:
            try:
                await self._health_check()
                await self._monitor_system()
                await self._make_autonomous_decisions()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"❌ Ошибка в менеджере: {e}")
                await asyncio.sleep(10)
    
    async def _health_check(self):
        """Проверка здоровья системы"""
        try:
            response = requests.get(f"{self.server_url}/api/system/status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('system_status', 'unknown')
                
                if status == 'running':
                    self.consecutive_failures = 0
                    logger.info(f"✅ Система здорова: {status}")
                else:
                    self.consecutive_failures += 1
                    logger.warning(f"⚠️ Система не в порядке: {status}")
                    
                self.last_health_check = datetime.now()
                
            else:
                self.consecutive_failures += 1
                logger.error(f"❌ Ошибка проверки здоровья: {response.status_code}")
                
        except Exception as e:
            self.consecutive_failures += 1
            logger.error(f"❌ Ошибка проверки здоровья: {e}")
    
    async def _monitor_system(self):
        """Мониторинг системы"""
        try:
            # Проверяем использование ресурсов
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            if 'start_multi_agent_system.py' in result.stdout:
                logger.info("✅ Процесс системы запущен")
            else:
                logger.error("❌ Процесс системы не найден")
                await self._restart_system()
            
            # Проверяем порт
            result = subprocess.run(['ss', '-tlnp'], capture_output=True, text=True)
            if ':8080' in result.stdout:
                logger.info("✅ Порт 8080 активен")
            else:
                logger.error("❌ Порт 8080 не активен")
                await self._restart_system()
                
        except Exception as e:
            logger.error(f"❌ Ошибка мониторинга: {e}")
    
    async def _make_autonomous_decisions(self):
        """Принятие автономных решений"""
        try:
            # Если система падает несколько раз подряд - перезапускаем
            if self.consecutive_failures >= self.max_failures:
                logger.warning(f"🔄 Система падает {self.consecutive_failures} раз подряд, перезапускаем...")
                await self._restart_system()
                self.consecutive_failures = 0
            
            # Проверяем, нужно ли обновить систему
            await self._check_for_updates()
            
            # Проверяем, нужно ли очистить логи
            await self._cleanup_logs()
            
        except Exception as e:
            logger.error(f"❌ Ошибка принятия решений: {e}")
    
    async def _restart_system(self):
        """Перезапуск системы"""
        try:
            logger.info("🔄 Автономный перезапуск системы...")
            
            # Останавливаем систему
            subprocess.run(['/home/mentor/manage_agents.sh', 'stop'], check=True)
            await asyncio.sleep(5)
            
            # Запускаем систему
            subprocess.run(['/home/mentor/manage_agents.sh', 'start'], check=True)
            await asyncio.sleep(10)
            
            logger.info("✅ Система перезапущена автономно")
            
        except Exception as e:
            logger.error(f"❌ Ошибка перезапуска: {e}")
    
    async def _check_for_updates(self):
        """Проверка обновлений"""
        try:
            # Проверяем, есть ли новые коммиты в git
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                 capture_output=True, text=True, cwd='/home/mentor')
            
            if result.stdout.strip():
                logger.info("📝 Обнаружены изменения в коде")
                # Здесь можно добавить автономное обновление
                
        except Exception as e:
            logger.debug(f"Git не доступен: {e}")
    
    async def _cleanup_logs(self):
        """Очистка логов"""
        try:
            # Очищаем старые логи (старше 7 дней)
            subprocess.run(['find', '/home/mentor', '-name', '*.log', 
                          '-mtime', '+7', '-delete'], check=True)
            logger.info("🧹 Старые логи очищены")
            
        except Exception as e:
            logger.debug(f"Очистка логов: {e}")
    
    def stop(self):
        """Остановка менеджера"""
        logger.info("🛑 Остановка автономного менеджера...")
        self.running = False

async def main():
    """Главная функция"""
    manager = AutonomousSystemManager()
    
    try:
        await manager.start()
    except KeyboardInterrupt:
        logger.info("📡 Получен сигнал прерывания")
        manager.stop()

if __name__ == "__main__":
    asyncio.run(main())



