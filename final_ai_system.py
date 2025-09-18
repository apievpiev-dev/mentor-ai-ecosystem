#!/usr/bin/env python3
"""
Финальная система AI агентов с реальными навыками
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
from ai_engine import ai_engine, generate_ai_response, generate_code
from chat_server import app, manager, system_stats

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/mentor/final_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AIEnhancedAgent:
    """Агент с реальными AI навыками"""
    
    def __init__(self, agent_type: str, name: str, skills: List[str]):
        self.agent_type = agent_type
        self.name = name
        self.skills = skills
        self.status = "idle"
    
    async def process_message(self, message: str, user_id: str = "user") -> Dict[str, Any]:
        """Обработка сообщения с помощью AI"""
        try:
            self.status = "processing"
            
            # Создаем промпт в зависимости от типа агента
            system_prompt = self._get_system_prompt()
            user_prompt = f"Пользователь просит: {message}"
            
            # Получаем ответ от AI
            response = await generate_ai_response(user_prompt, system_prompt)
            
            # Дополнительная обработка в зависимости от навыков
            if "code_generation" in self.skills and any(word in message.lower() for word in ["код", "программирование", "создай", "напиши"]):
                response = await self._enhance_with_code(message, response)
            elif "data_analysis" in self.skills and any(word in message.lower() for word in ["анализ", "данные", "отчет"]):
                response = await self._enhance_with_analysis(message, response)
            elif "project_planning" in self.skills and any(word in message.lower() for word in ["проект", "план", "управление"]):
                response = await self._enhance_with_planning(message, response)
            
            self.status = "idle"
            
            return {
                "response": response,
                "agent": self.name,
                "agent_type": self.agent_type,
                "timestamp": datetime.now().isoformat(),
                "skills_used": self._get_used_skills(message)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения: {e}")
            self.status = "error"
            return {
                "error": str(e),
                "agent": self.name,
                "agent_type": self.agent_type
            }
    
    def _get_system_prompt(self) -> str:
        """Получить системный промпт для агента"""
        prompts = {
            "code_developer": """Ты эксперт-программист. Создавай качественный, рабочий код.
            Отвечай на русском языке, объясняй что делаешь.
            Включай комментарии и обработку ошибок.""",
            
            "data_analyst": """Ты эксперт по анализу данных. Анализируй данные, находи закономерности,
            создавай инсайты и давай практические рекомендации.
            Отвечай на русском языке.""",
            
            "project_manager": """Ты опытный менеджер проектов. Создавай детальные планы проектов,
            разбивай задачи на этапы, оценивай риски и ресурсы.
            Отвечай на русском языке.""",
            
            "general_assistant": """Ты универсальный помощник. Помогай с различными задачами,
            планированием и координацией. Отвечай на русском языке."""
        }
        return prompts.get(self.agent_type, "Ты полезный помощник. Отвечай на русском языке.")
    
    async def _enhance_with_code(self, message: str, base_response: str) -> str:
        """Улучшить ответ с помощью генерации кода"""
        try:
            # Определяем язык программирования
            language = "python"
            if "javascript" in message.lower() or "js" in message.lower():
                language = "javascript"
            elif "html" in message.lower():
                language = "html"
            elif "css" in message.lower():
                language = "css"
            
            # Генерируем код
            code = await generate_code(message, language)
            
            return f"{base_response}\n\nВот код:\n```{language}\n{code}\n```"
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации кода: {e}")
            return base_response
    
    async def _enhance_with_analysis(self, message: str, base_response: str) -> str:
        """Улучшить ответ с помощью анализа данных"""
        try:
            analysis_prompt = f"""
            Дай детальный анализ для запроса: {message}
            
            Включи:
            1. Методологию анализа
            2. Ключевые метрики
            3. Выводы и рекомендации
            4. Визуализации (описание)
            """
            
            analysis = await generate_ai_response(analysis_prompt)
            return f"{base_response}\n\nДетальный анализ:\n{analysis}"
            
        except Exception as e:
            logger.error(f"❌ Ошибка анализа данных: {e}")
            return base_response
    
    async def _enhance_with_planning(self, message: str, base_response: str) -> str:
        """Улучшить ответ с помощью планирования проекта"""
        try:
            planning_prompt = f"""
            Создай детальный план проекта для: {message}
            
            Включи:
            1. Этапы проекта
            2. Временные рамки
            3. Необходимые ресурсы
            4. Риски и митигация
            5. Критерии успеха
            """
            
            plan = await generate_ai_response(planning_prompt)
            return f"{base_response}\n\nДетальный план:\n{plan}"
            
        except Exception as e:
            logger.error(f"❌ Ошибка планирования: {e}")
            return base_response
    
    def _get_used_skills(self, message: str) -> List[str]:
        """Определить какие навыки были использованы"""
        used_skills = []
        
        if "code_generation" in self.skills and any(word in message.lower() for word in ["код", "программирование", "создай", "напиши"]):
            used_skills.append("code_generation")
        
        if "data_analysis" in self.skills and any(word in message.lower() for word in ["анализ", "данные", "отчет"]):
            used_skills.append("data_analysis")
        
        if "project_planning" in self.skills and any(word in message.lower() for word in ["проект", "план", "управление"]):
            used_skills.append("project_planning")
        
        return used_skills

class FinalAISystem:
    """Финальная система AI агентов"""
    
    def __init__(self):
        self.running = False
        self.agents = {}
        self.startup_time = None
        
        # Создаем агентов с реальными навыками
        self._create_agents()
        
        # Настройка обработчиков сигналов
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Обработчик сигналов"""
        logger.info(f"📡 Получен сигнал {signum}, завершаем работу...")
        self.running = False
        sys.exit(0)
    
    def _create_agents(self):
        """Создание агентов"""
        agents_config = [
            {
                "type": "code_developer",
                "name": "Разработчик Кода",
                "skills": ["code_generation", "debugging", "code_review", "architecture_design"]
            },
            {
                "type": "data_analyst", 
                "name": "Аналитик Данных",
                "skills": ["data_analysis", "reporting", "visualization", "predictive_modeling"]
            },
            {
                "type": "project_manager",
                "name": "Менеджер Проектов", 
                "skills": ["project_planning", "task_management", "resource_allocation", "progress_tracking"]
            },
            {
                "type": "general_assistant",
                "name": "Универсальный Помощник",
                "skills": ["general_help", "planning", "coordination"]
            }
        ]
        
        for config in agents_config:
            agent = AIEnhancedAgent(
                config["type"],
                config["name"], 
                config["skills"]
            )
            self.agents[config["type"]] = agent
        
        logger.info(f"✅ Создано {len(self.agents)} AI агентов")
    
    async def start(self):
        """Запуск системы"""
        try:
            logger.info("🚀 Запуск финальной AI системы...")
            
            # Проверяем AI движок
            ai_status = ai_engine.get_status()
            if ai_status.get("default_engine") == "none":
                logger.error("❌ AI движок недоступен")
                return
            
            logger.info(f"✅ AI движок: {ai_status.get('default_engine')}")
            logger.info(f"✅ Доступные модели: {ai_status.get('available_models', {})}")
            
            # Обновляем chat_server
            self._patch_chat_server()
            
            # Запускаем веб-сервер
            self._start_web_server()
            
            self.running = True
            self.startup_time = datetime.now()
            
            logger.info("✅ Финальная AI система запущена")
            
            # Основной цикл
            await self._main_loop()
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска системы: {e}")
            raise
    
    def _patch_chat_server(self):
        """Обновление chat_server"""
        try:
            import chat_server
            
            # Создаем обертку для совместимости
            class AgentSystemWrapper:
                def __init__(self, agents):
                    self.agents = agents
                
                async def process_user_message(self, message: str, user_id: str = "user"):
                    # Выбираем подходящего агента
                    agent = self._select_agent(message)
                    return await agent.process_message(message, user_id)
                
                def _select_agent(self, message: str):
                    """Выбор подходящего агента"""
                    message_lower = message.lower()
                    
                    if any(word in message_lower for word in ["код", "программирование", "разработка", "создай", "напиши"]):
                        return self.agents["code_developer"]
                    elif any(word in message_lower for word in ["анализ", "данные", "отчет", "график"]):
                        return self.agents["data_analyst"]
                    elif any(word in message_lower for word in ["проект", "план", "управление", "координация"]):
                        return self.agents["project_manager"]
                    else:
                        return self.agents["general_assistant"]
                
                def get_system_status(self):
                    return {
                        "total_agents": len(self.agents),
                        "agents": [
                            {
                                "name": agent.name,
                                "type": agent.agent_type,
                                "status": agent.status,
                                "skills": agent.skills
                            }
                            for agent in self.agents.values()
                        ],
                        "system_status": "running"
                    }
            
            # Заменяем multi_agent_system
            chat_server.multi_agent_system = AgentSystemWrapper(self.agents)
            
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
            
            if ai_healthy:
                logger.info("💚 Система здорова")
            else:
                logger.warning("⚠️ AI движок недоступен")
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки здоровья: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус системы"""
        return {
            "running": self.running,
            "startup_time": self.startup_time.isoformat() if self.startup_time else None,
            "total_agents": len(self.agents),
            "ai_status": ai_engine.get_status()
        }

# Глобальный экземпляр
final_ai_system = FinalAISystem()

if __name__ == "__main__":
    # Запуск системы
    async def main():
        try:
            await final_ai_system.start()
        except KeyboardInterrupt:
            logger.info("🛑 Получен сигнал прерывания")
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}")
    
    asyncio.run(main())


