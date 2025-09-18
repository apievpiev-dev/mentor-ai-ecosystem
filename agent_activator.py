#!/usr/bin/env python3
"""
Активатор агентов - заставляет агентов работать автономно
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

class AgentActivator:
    """Активатор агентов для автономной работы"""
    
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
        
        # Задачи для активации агентов
        self.activation_tasks = {
            "general_assistant": [
                "Проанализируй текущее состояние системы и создай краткий отчет",
                "Предложи 3 улучшения для системы",
                "Создай план оптимизации производительности"
            ],
            "code_developer": [
                "Создай функцию для автоматического тестирования API",
                "Оптимизируй код системы для лучшей производительности",
                "Добавь обработку ошибок в критические функции"
            ],
            "data_analyst": [
                "Проанализируй статистику использования системы",
                "Создай отчет о производительности агентов",
                "Проанализируй паттерны использования API"
            ],
            "project_manager": [
                "Создай план развития системы на следующую неделю",
                "Проанализируй приоритеты задач",
                "Создай roadmap для новых функций"
            ],
            "designer": [
                "Улучши дизайн веб-интерфейса",
                "Создай иконки для новых функций",
                "Оптимизируй UX для мобильных устройств"
            ],
            "qa_tester": [
                "Протестируй все API endpoints",
                "Проверь систему на уязвимости",
                "Создай автоматические тесты"
            ]
        }
    
    async def activate_agent(self, agent_type: str, task: str):
        """Активация конкретного агента"""
        try:
            url = f"{self.server_url}/api/chat/send"
            data = {
                "message": task,
                "user_id": "agent_activator",
                "agent_type": agent_type
            }
            
            logger.info(f"🚀 Активация агента {agent_type}: {task[:50]}...")
            
            response = requests.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Агент {agent_type} активирован: {result.get('success', False)}")
                return True
            else:
                logger.error(f"❌ Ошибка активации агента {agent_type}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка активации агента {agent_type}: {e}")
            return False
    
    async def activate_all_agents(self):
        """Активация всех агентов"""
        logger.info("🚀 Активация всех агентов...")
        
        for agent_type in self.agents:
            if agent_type in self.activation_tasks:
                task = self.activation_tasks[agent_type][0]  # Берем первую задачу
                await self.activate_agent(agent_type, task)
                await asyncio.sleep(2)  # Пауза между активациями
    
    async def continuous_activation(self):
        """Непрерывная активация агентов"""
        logger.info("🔄 Запуск непрерывной активации агентов...")
        
        task_counter = 0
        
        while self.running:
            try:
                # Выбираем случайного агента
                agent_type = self.agents[task_counter % len(self.agents)]
                
                if agent_type in self.activation_tasks:
                    tasks = self.activation_tasks[agent_type]
                    task = tasks[task_counter % len(tasks)]
                    
                    await self.activate_agent(agent_type, task)
                
                task_counter += 1
                
                # Ждем 30 секунд перед следующей активацией
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Ошибка в непрерывной активации: {e}")
                await asyncio.sleep(10)
    
    async def start(self):
        """Запуск активатора агентов"""
        logger.info("🚀 Запуск активатора агентов...")
        self.running = True
        
        # Сначала активируем всех агентов
        await self.activate_all_agents()
        
        # Затем запускаем непрерывную активацию
        await self.continuous_activation()
    
    def stop(self):
        """Остановка активатора"""
        logger.info("🛑 Остановка активатора агентов...")
        self.running = False

async def main():
    """Главная функция"""
    activator = AgentActivator()
    
    try:
        await activator.start()
    except KeyboardInterrupt:
        logger.info("📡 Получен сигнал прерывания")
        activator.stop()

if __name__ == "__main__":
    asyncio.run(main())
