#!/usr/bin/env python3
"""
Автономный планировщик задач для агентов
Создает задачи и распределяет их между агентами автоматически
"""

import asyncio
import json
import logging
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
import requests

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutonomousTaskScheduler:
    """Автономный планировщик задач"""
    
    def __init__(self, server_url="http://5.129.198.210:8080"):
        self.server_url = server_url
        self.running = False
        self.task_interval = 60  # секунд между задачами
        self.agents = {
            "general_assistant": "Универсальный Помощник",
            "code_developer": "Разработчик Кода", 
            "data_analyst": "Аналитик Данных",
            "project_manager": "Менеджер Проектов",
            "designer": "Дизайнер",
            "qa_tester": "Тестировщик"
        }
        
        # Автономные задачи для каждого агента
        self.autonomous_tasks = {
            "general_assistant": [
                "Проанализируй текущее состояние системы и предложи улучшения",
                "Создай план оптимизации производительности",
                "Проверь логи системы на наличие ошибок",
                "Предложи новые функции для системы"
            ],
            "code_developer": [
                "Создай функцию для автоматического тестирования API",
                "Оптимизируй код системы для лучшей производительности", 
                "Создай скрипт для автоматического развертывания",
                "Добавь обработку ошибок в критические функции"
            ],
            "data_analyst": [
                "Проанализируй статистику использования системы",
                "Создай отчет о производительности агентов",
                "Проанализируй паттерны использования API",
                "Создай дашборд для мониторинга системы"
            ],
            "project_manager": [
                "Создай план развития системы на следующую неделю",
                "Проанализируй приоритеты задач",
                "Создай roadmap для новых функций",
                "Оцени риски и создай план их минимизации"
            ],
            "designer": [
                "Улучши дизайн веб-интерфейса",
                "Создай иконки для новых функций",
                "Оптимизируй UX для мобильных устройств",
                "Создай визуальные диаграммы архитектуры системы"
            ],
            "qa_tester": [
                "Протестируй все API endpoints",
                "Проверь систему на уязвимости",
                "Создай автоматические тесты",
                "Протестируй производительность под нагрузкой"
            ]
        }
    
    async def start(self):
        """Запуск автономного планировщика"""
        logger.info("🚀 Запуск автономного планировщика задач...")
        self.running = True
        
        while self.running:
            try:
                await self._create_autonomous_task()
                await asyncio.sleep(self.task_interval)
            except Exception as e:
                logger.error(f"❌ Ошибка в планировщике: {e}")
                await asyncio.sleep(10)
    
    async def _create_autonomous_task(self):
        """Создание автономной задачи"""
        try:
            # Выбираем случайного агента
            agent_type = random.choice(list(self.agents.keys()))
            agent_name = self.agents[agent_type]
            
            # Выбираем случайную задачу для агента
            task = random.choice(self.autonomous_tasks[agent_type])
            
            logger.info(f"📋 Создаю автономную задачу для {agent_name}: {task}")
            
            # Отправляем задачу агенту
            await self._send_task_to_agent(agent_type, task)
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания задачи: {e}")
    
    async def _send_task_to_agent(self, agent_type: str, task: str):
        """Отправка задачи агенту"""
        try:
            url = f"{self.server_url}/api/chat/send"
            data = {
                "message": task,
                "user_id": "autonomous_scheduler",
                "agent_type": agent_type
            }
            
            response = requests.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Задача отправлена {self.agents[agent_type]}: {result.get('success', False)}")
            else:
                logger.error(f"❌ Ошибка отправки задачи: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка отправки задачи агенту: {e}")
    
    def stop(self):
        """Остановка планировщика"""
        logger.info("🛑 Остановка автономного планировщика...")
        self.running = False

async def main():
    """Главная функция"""
    scheduler = AutonomousTaskScheduler()
    
    try:
        await scheduler.start()
    except KeyboardInterrupt:
        logger.info("📡 Получен сигнал прерывания")
        scheduler.stop()

if __name__ == "__main__":
    asyncio.run(main())



