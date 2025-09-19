#!/usr/bin/env python3
"""
Принудительная активация агентов - заставляет агентов работать
"""

import asyncio
import requests
import logging
import time
import json
from typing import Dict, List, Any

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ForceAgentWork:
    """Принудительная активация агентов"""
    
    def __init__(self, server_url="http://localhost:8080"):
        self.server_url = server_url
        self.running = False
        self.agents = [
            "general_assistant",
            "code_developer", 
            "data_analyst",
            "project_manager",
            "designer",
            "qa_tester"
        ]
        
        # Простые задачи для принудительной активации
        self.force_tasks = {
            "general_assistant": "Создай краткий отчет о состоянии системы",
            "code_developer": "Проверь код на наличие ошибок",
            "data_analyst": "Проанализируй статистику системы",
            "project_manager": "Создай план задач на сегодня",
            "designer": "Предложи улучшения интерфейса",
            "qa_tester": "Проверь работоспособность API"
        }
    
    async def force_agent_work(self, agent_type: str):
        """Принудительная активация агента"""
        try:
            task = self.force_tasks.get(agent_type, "Выполни задачу")
            
            # Отправляем задачу
            url = f"{self.server_url}/api/chat/send"
            data = {
                "message": task,
                "user_id": "force_worker",
                "agent_type": agent_type
            }
            
            logger.info(f"🚀 Принудительная активация агента {agent_type}")
            
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Агент {agent_type} активирован: {result.get('success', False)}")
                
                # Ждем немного и проверяем статус
                await asyncio.sleep(5)
                
                # Проверяем, стал ли агент активным
                status_response = requests.get(f"{self.server_url}/api/system/status", timeout=5)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    active_agents = status_data.get("active_agents", 0)
                    logger.info(f"📊 Активных агентов: {active_agents}")
                
                return True
            else:
                logger.error(f"❌ Ошибка активации агента {agent_type}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка принудительной активации агента {agent_type}: {e}")
            return False
    
    async def force_all_agents(self):
        """Принудительная активация всех агентов"""
        logger.info("🚀 Принудительная активация всех агентов...")
        
        for agent_type in self.agents:
            await self.force_agent_work(agent_type)
            await asyncio.sleep(3)  # Пауза между активациями
    
    async def continuous_force_work(self):
        """Непрерывная принудительная активация"""
        logger.info("🔄 Запуск непрерывной принудительной активации...")
        
        cycle = 0
        
        while self.running:
            try:
                cycle += 1
                logger.info(f"🔄 Цикл принудительной активации #{cycle}")
                
                # Активируем всех агентов
                await self.force_all_agents()
                
                # Проверяем статус системы
                try:
                    status_response = requests.get(f"{self.server_url}/api/system/status", timeout=5)
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        active_agents = status_data.get("active_agents", 0)
                        active_tasks = status_data.get("coordination_status", {}).get("active_tasks", 0)
                        logger.info(f"📊 Статус: {active_agents} активных агентов, {active_tasks} активных задач")
                except Exception as e:
                    logger.error(f"❌ Ошибка проверки статуса: {e}")
                
                # Ждем 2 минуты перед следующим циклом
                await asyncio.sleep(120)
                
            except Exception as e:
                logger.error(f"❌ Ошибка в непрерывной активации: {e}")
                await asyncio.sleep(30)
    
    async def start(self):
        """Запуск принудительной активации"""
        logger.info("🚀 Запуск принудительной активации агентов...")
        self.running = True
        
        # Сначала принудительно активируем всех агентов
        await self.force_all_agents()
        
        # Затем запускаем непрерывную активацию
        await self.continuous_force_work()
    
    def stop(self):
        """Остановка принудительной активации"""
        logger.info("🛑 Остановка принудительной активации агентов...")
        self.running = False

async def main():
    """Главная функция"""
    force_worker = ForceAgentWork()
    
    try:
        await force_worker.start()
    except KeyboardInterrupt:
        logger.info("📡 Получен сигнал прерывания")
        force_worker.stop()

if __name__ == "__main__":
    asyncio.run(main())


