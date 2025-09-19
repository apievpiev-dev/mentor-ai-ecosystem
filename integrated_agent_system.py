#!/usr/bin/env python3
"""
Интегрированная система множественных AI-агентов
Объединяет все компоненты в единую рабочую систему
"""

import asyncio
import json
import logging
import time
import signal
import sys
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Импортируем наши модули
from multi_agent_system import (
    MultiAgentSystem, BaseAgent, GeneralAssistantAgent, 
    CodeDeveloperAgent, DataAnalystAgent, ProjectManagerAgent,
    AgentType, SharedMemory
)
from enhanced_agents import (
    EnhancedCodeDeveloperAgent, EnhancedDataAnalystAgent
)
from ai_engine import generate_ai_response
from agent_coordinator import (
    AgentCoordinator, EnhancedSharedMemory, KnowledgeGraph,
    TaskComplexity, CoordinationStrategy, initialize_coordinator
)
from chat_server import app, manager, system_stats
from enhanced_agents import EnhancedCodeDeveloperAgent, EnhancedDataAnalystAgent
from ai_manager_agent import AIManagerAgent
from ai_engine import ai_engine

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('integrated_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IntegratedAgentSystem:
    """Интегрированная система агентов"""
    
    def __init__(self):
        self.running = True
        self.shared_memory = None
        self.multi_agent_system = None
        self.coordinator = None
        self.startup_time = None
        
        # Создаем директории
        self._setup_directories()
        
        logger.info("🚀 Интегрированная система агентов инициализирована")
    
    def _setup_directories(self):
        """Создание необходимых директорий"""
        directories = [
            "agent_data",
            "agent_logs",
            "agent_knowledge",
            "agent_projects"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Создана директория: {directory}")
    
    async def initialize(self):
        """Инициализация системы"""
        try:
            logger.info("🔧 Инициализация интегрированной системы...")
            
            # Создаем расширенную общую память
            self.shared_memory = EnhancedSharedMemory()
            logger.info("✅ Расширенная общая память создана")
            
            # Создаем систему множественных агентов с улучшенными агентами
            self.multi_agent_system = self._create_enhanced_agent_system()
            
            # Заменяем обычную память на расширенную
            for agent in self.multi_agent_system.agents.values():
                agent.set_shared_memory(self.shared_memory)
            
            logger.info("✅ Система множественных агентов создана")
            
            # Создаем координатор
            self.coordinator = initialize_coordinator(self.shared_memory)
            
            # Регистрируем агентов в координаторе
            for agent in self.multi_agent_system.agents.values():
                self.coordinator.register_agent(agent)
            
            logger.info("✅ Координатор агентов создан")
            
            # Запускаем координацию
            self.coordinator.start_coordination()
            logger.info("✅ Система координации запущена")
            
            # Инициализируем дополнительные агенты
            await self._create_additional_agents()
            
            # Загружаем сохраненные знания
            await self._load_saved_knowledge()
            
            self.startup_time = datetime.now()
            logger.info("🎉 Интегрированная система успешно инициализирована")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации системы: {e}")
            raise
    
    def _create_enhanced_agent_system(self):
        """Создание системы с улучшенными агентами"""
        try:
            # Создаем базовую систему
            system = MultiAgentSystem()
            
            # Заменяем агентов на улучшенных
            enhanced_agents = {}
            
            # Создаем улучшенного помощника
            for agent_id, agent in system.agents.items():
                if agent.agent_type == AgentType.GENERAL_ASSISTANT:
                    enhanced_agent = self._create_enhanced_assistant(agent_id)
                    enhanced_agents[agent_id] = enhanced_agent
                elif agent.agent_type == AgentType.CODE_DEVELOPER:
                    # Заменяем на улучшенного разработчика
                    enhanced_agent = EnhancedCodeDeveloperAgent(agent_id)
                    enhanced_agents[agent_id] = enhanced_agent
                elif agent.agent_type == AgentType.DATA_ANALYST:
                    # Заменяем на улучшенного аналитика
                    enhanced_agent = EnhancedDataAnalystAgent(agent_id)
                    enhanced_agents[agent_id] = enhanced_agent
                elif agent.agent_type == AgentType.PROJECT_MANAGER:
                    # Создаем улучшенного менеджера проектов
                    enhanced_agent = self._create_enhanced_project_manager(agent_id)
                    enhanced_agents[agent_id] = enhanced_agent
                else:
                    # Оставляем остальных как есть
                    enhanced_agents[agent_id] = agent
            
            # Обновляем агентов в системе
            system.agents = enhanced_agents
            
            logger.info("✅ Создана система с улучшенными агентами")
            return system
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания улучшенной системы: {e}")
            # Возвращаем базовую систему в случае ошибки
            return MultiAgentSystem()
    
    def _create_enhanced_assistant(self, agent_id: str):
        """Создание улучшенного помощника с AI"""
        class EnhancedGeneralAssistant(GeneralAssistantAgent):
            def __init__(self, agent_id: str, parent_system):
                super().__init__(agent_id)
                # Добавляем обработчик для user_query
                self.add_skill("user_query", self._handle_user_query)
                # Сохраняем ссылку на родительский класс для доступа к методам
                self.parent_system = parent_system
            
            async def _handle_user_query(self, content: Dict[str, Any]) -> Dict[str, Any]:
                """Обработка пользовательских запросов с AI"""
                try:
                    message = content.get("message", "").lower().strip()
                    user_id = content.get("user_id", "user")
                    
                    # Быстрые ответы для простых запросов
                    quick_responses = {
                        "привет": "Привет! Как дела? Чем могу помочь?",
                        "hello": "Hello! How can I help you today?",
                        "как дела": "Отлично! Готов помочь с любыми задачами.",
                        "спасибо": "Пожалуйста! Рад был помочь.",
                        "пока": "До свидания! Обращайтесь, если понадобится помощь.",
                        "bye": "Goodbye! Feel free to ask if you need help.",
                        "история проекта": self.parent_system._get_project_history(),
                        "что такое mentor": self.parent_system._get_project_overview(),
                        "архитектура системы": self.parent_system._get_system_architecture(),
                        "агенты системы": self.parent_system._get_agents_info()
                    }
                    
                    if message in quick_responses:
                        return {
                            "response": quick_responses[message],
                            "suggestions": [
                                "Планирование задач",
                                "Поиск информации", 
                                "Координация с другими агентами",
                                "Анализ данных"
                            ]
                        }
                    
                    # Для сложных запросов используем AI
                    ai_response = await generate_ai_response(
                        message, 
                        context=f"Ты универсальный помощник. Помоги пользователю с запросом: {message}",
                        user_id=user_id
                    )
                    
                    return {
                        "response": ai_response,
                        "suggestions": [
                            "Планирование задач",
                            "Поиск информации", 
                            "Координация с другими агентами",
                            "Анализ данных"
                        ]
                    }
                except Exception as e:
                    logger.error(f"❌ Ошибка AI обработки: {e}")
                    return {
                        "response": f"Извините, произошла ошибка при обработке запроса: {e}",
                        "error": str(e)
                    }
            
            async def _handle_general_help(self, content: Dict[str, Any]) -> Dict[str, Any]:
                """Обработка общих запросов с AI"""
                try:
                    message = content.get("message", "")
                    user_id = content.get("user_id", "user")
                    
                    # Используем AI для генерации ответа
                    ai_response = await generate_ai_response(
                        message, 
                        context=f"Ты универсальный помощник. Помоги пользователю с запросом: {message}",
                        user_id=user_id
                    )
                    
                    return {
                        "response": ai_response,
                        "suggestions": [
                            "Планирование задач",
                            "Поиск информации", 
                            "Координация с другими агентами",
                            "Анализ данных"
                        ]
                    }
                except Exception as e:
                    logger.error(f"❌ Ошибка AI обработки: {e}")
                    return {
                        "response": f"Извините, произошла ошибка при обработке запроса: {e}",
                        "error": str(e)
                    }
            
            async def _handle_planning(self, content: Dict[str, Any]) -> Dict[str, Any]:
                """Обработка планирования с AI"""
                try:
                    message = content.get("message", "")
                    user_id = content.get("user_id", "user")
                    
                    ai_response = await generate_ai_response(
                        message,
                        context="Ты эксперт по планированию. Создай детальный план для достижения цели.",
                        user_id=user_id
                    )
                    
                    return {
                        "response": ai_response,
                        "plan_type": "AI-generated"
                    }
                except Exception as e:
                    logger.error(f"❌ Ошибка AI планирования: {e}")
                    return {
                        "response": f"Ошибка при создании плана: {e}",
                        "error": str(e)
                    }
        
        return EnhancedGeneralAssistant(agent_id, self)
    
    def _get_project_history(self):
        """Получить историю проекта"""
        return """📚 ИСТОРИЯ ПРОЕКТА MENTOR:

🎯 Mentor Project - система множественных AI-агентов с автономными возможностями.

🏗️ ЭВОЛЮЦИЯ:
• Фаза 1: Базовая система агентов
• Фаза 2: AI интеграция с Ollama
• Фаза 3: Улучшенные агенты с AI
• Фаза 4: Оптимизация и исправление ошибок

🐛 РЕШЕННЫЕ ПРОБЛЕМЫ:
• Рекурсия (maximum recursion depth exceeded)
• ImportError при запуске
• KeyError в WebSocket
• Таймауты AI (60→30 сек)
• WebSocket 403 ошибки

✅ ТЕКУЩЕЕ СОСТОЯНИЕ:
• 6 агентов с AI интеграцией
• Веб-интерфейс на порту 8080
• Быстрые ответы + AI для сложных задач
• Стабильная работа системы"""
    
    def _get_project_overview(self):
        """Получить обзор проекта"""
        return """🎯 MENTOR PROJECT - ОБЗОР:

Это комплексная система множественных AI-агентов с:
• 6 специализированными агентами
• AI интеграцией (Ollama + OpenAI)
• Веб-интерфейсом с WebSocket
• Координацией между агентами
• Общей памятью и знаниями

🤖 АГЕНТЫ:
• Универсальный Помощник
• Разработчик Кода  
• Аналитик Данных
• Менеджер Проектов
• Дизайнер
• Тестировщик

🚀 ВОЗМОЖНОСТИ:
• Мгновенные ответы на простые вопросы
• AI-генерированные ответы для сложных задач
• Координация между агентами
• Веб-интерфейс в реальном времени"""
    
    def _get_system_architecture(self):
        """Получить архитектуру системы"""
        return """🏗️ АРХИТЕКТУРА СИСТЕМЫ MENTOR:

🔧 КОМПОНЕНТЫ:
• Multi-Agent System (ядро)
• AI Engine (Ollama + OpenAI)
• Agent Coordinator (координация)
• Web Interface (FastAPI + WebSocket)
• Shared Memory (общая память)
• Enhanced Agents (улучшенные агенты)

📊 ТЕХНИЧЕСКИЙ СТЕК:
• Backend: Python 3.12, FastAPI, asyncio
• AI: Ollama (llama3.1:8b, llama2, mistral)
• Frontend: HTML/CSS/JS, WebSocket
• Infrastructure: Linux, Docker-ready

🔄 ПОТОК ДАННЫХ:
Пользователь → Web Interface → Agent Coordinator → 
Выбор агента → AI Engine → Ответ → Пользователь"""
    
    def _get_agents_info(self):
        """Получить информацию об агентах"""
        return """🤖 АГЕНТЫ СИСТЕМЫ MENTOR:

1️⃣ УНИВЕРСАЛЬНЫЙ ПОМОЩНИК
• Навыки: общие вопросы, координация
• AI: ✅ Полная интеграция
• Особенности: быстрые ответы + AI

2️⃣ РАЗРАБОТЧИК КОДА  
• Навыки: программирование, создание проектов
• AI: ✅ EnhancedCodeDeveloperAgent
• Особенности: генерация кода, отладка

3️⃣ АНАЛИТИК ДАННЫХ
• Навыки: анализ, отчеты, визуализация  
• AI: ✅ EnhancedDataAnalystAgent
• Особенности: обработка данных

4️⃣ МЕНЕДЖЕР ПРОЕКТОВ
• Навыки: планирование, управление задачами
• AI: ✅ EnhancedProjectManager
• Особенности: создание планов

5️⃣ ДИЗАЙНЕР
• Навыки: UI/UX, визуальные решения
• AI: ⚠️ Базовая (требует улучшения)

6️⃣ ТЕСТИРОВЩИК
• Навыки: тестирование, поиск багов
• AI: ⚠️ Базовая (требует улучшения)"""
    
    def _create_enhanced_project_manager(self, agent_id: str):
        """Создание улучшенного менеджера проектов с AI"""
        class EnhancedProjectManager(ProjectManagerAgent):
            def __init__(self, agent_id: str):
                super().__init__(agent_id)
                # Добавляем обработчик для user_query
                self.add_skill("user_query", self._handle_user_query)
            
            async def _handle_user_query(self, content: Dict[str, Any]) -> Dict[str, Any]:
                """Обработка пользовательских запросов с AI"""
                try:
                    message = content.get("message", "").lower().strip()
                    user_id = content.get("user_id", "user")
                    
                    # Быстрые ответы для простых запросов
                    quick_responses = {
                        "план": "Создам детальный план проекта. Какой тип проекта вас интересует?",
                        "проект": "Помогу спланировать и организовать ваш проект. Расскажите подробнее.",
                        "задачи": "Составлю список задач и назначу ответственных. Что нужно сделать?",
                        "время": "Создам временную шкалу проекта. Какие у вас сроки?",
                        "ресурсы": "Помогу распределить ресурсы и бюджет. Какие ресурсы доступны?"
                    }
                    
                    if any(keyword in message for keyword in quick_responses.keys()):
                        for keyword, response in quick_responses.items():
                            if keyword in message:
                                return {
                                    "response": response,
                                    "project_phase": "planning",
                                    "suggestions": [
                                        "Создать план проекта",
                                        "Назначить задачи",
                                        "Определить ресурсы",
                                        "Установить сроки"
                                    ]
                                }
                    
                    # Для сложных запросов используем AI
                    ai_response = await generate_ai_response(
                        message, 
                        context="Ты эксперт по управлению проектами. Создай детальный план и рекомендации.",
                        user_id=user_id
                    )
                    
                    return {
                        "response": ai_response,
                        "project_phase": "ai_analysis",
                        "suggestions": [
                            "Создать план проекта",
                            "Назначить задачи",
                            "Определить ресурсы",
                            "Установить сроки"
                        ]
                    }
                except Exception as e:
                    logger.error(f"❌ Ошибка AI обработки менеджера проектов: {e}")
                    return {
                        "response": f"Ошибка при планировании проекта: {e}",
                        "error": str(e)
                    }
        
        return EnhancedProjectManager(agent_id)
    
    async def _create_additional_agents(self):
        """Создание дополнительных агентов"""
        try:
            # Создаем агента-дизайнера
            from multi_agent_system import BaseAgent
            
            class DesignerAgent(BaseAgent):
                def __init__(self, agent_id: str = None):
                    super().__init__(
                        agent_id or str(uuid.uuid4()),
                        AgentType.DESIGNER,
                        "Дизайнер",
                        "Создает дизайны, макеты и визуальные решения"
                    )
                    self._setup_skills()
                
                def _setup_skills(self):
                    self.add_skill("ui_design", self._handle_ui_design)
                    self.add_skill("ux_design", self._handle_ux_design)
                    self.add_skill("visual_identity", self._handle_visual_identity)
                
                async def _handle_ui_design(self, content: Dict[str, Any]) -> Dict[str, Any]:
                    return {
                        "response": "Создаю дизайн пользовательского интерфейса",
                        "design_elements": ["Кнопки", "Формы", "Навигация", "Цветовая схема"]
                    }
                
                async def _handle_ux_design(self, content: Dict[str, Any]) -> Dict[str, Any]:
                    return {
                        "response": "Проектирую пользовательский опыт",
                        "ux_principles": ["Простота", "Интуитивность", "Доступность", "Эффективность"]
                    }
                
                async def _handle_visual_identity(self, content: Dict[str, Any]) -> Dict[str, Any]:
                    return {
                        "response": "Создаю визуальную идентичность",
                        "elements": ["Логотип", "Цвета", "Типографика", "Стиль"]
                    }
            
            # Создаем агента-тестировщика
            class QATesterAgent(BaseAgent):
                def __init__(self, agent_id: str = None):
                    super().__init__(
                        agent_id or str(uuid.uuid4()),
                        AgentType.QA_TESTER,
                        "Тестировщик",
                        "Тестирует приложения и находит ошибки"
                    )
                    self._setup_skills()
                
                def _setup_skills(self):
                    self.add_skill("unit_testing", self._handle_unit_testing)
                    self.add_skill("integration_testing", self._handle_integration_testing)
                    self.add_skill("bug_reporting", self._handle_bug_reporting)
                
                async def _handle_unit_testing(self, content: Dict[str, Any]) -> Dict[str, Any]:
                    return {
                        "response": "Создаю unit тесты",
                        "test_cases": ["Позитивные сценарии", "Негативные сценарии", "Граничные случаи"]
                    }
                
                async def _handle_integration_testing(self, content: Dict[str, Any]) -> Dict[str, Any]:
                    return {
                        "response": "Выполняю интеграционное тестирование",
                        "test_areas": ["API", "База данных", "Внешние сервисы"]
                    }
                
                async def _handle_bug_reporting(self, content: Dict[str, Any]) -> Dict[str, Any]:
                    return {
                        "response": "Создаю отчет об ошибке",
                        "bug_info": ["Шаги воспроизведения", "Ожидаемый результат", "Фактический результат"]
                    }
            
            # Добавляем новых агентов в систему
            designer = DesignerAgent()
            tester = QATesterAgent()
            
            self.multi_agent_system.agents[designer.agent_id] = designer
            self.multi_agent_system.agents[tester.agent_id] = tester
            
            # Устанавливаем общую память
            designer.set_shared_memory(self.shared_memory)
            tester.set_shared_memory(self.shared_memory)
            
            # Регистрируем в координаторе
            self.coordinator.register_agent(designer)
            self.coordinator.register_agent(tester)
            
            logger.info("✅ Дополнительные агенты созданы")
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания дополнительных агентов: {e}")
    
    async def _load_saved_knowledge(self):
        """Загрузка сохраненных знаний"""
        try:
            knowledge_file = Path("agent_knowledge/saved_knowledge.json")
            
            if knowledge_file.exists():
                with open(knowledge_file, 'r', encoding='utf-8') as f:
                    saved_knowledge = json.load(f)
                
                # Восстанавливаем знания
                for key, items in saved_knowledge.get("knowledge_base", {}).items():
                    for item in items:
                        self.shared_memory.store_knowledge(
                            key, item["value"], item["agent_id"], 
                            item.get("keywords", []), item.get("metadata", {})
                        )
                
                logger.info(f"✅ Загружено {len(saved_knowledge.get('knowledge_base', {}))} знаний")
            else:
                logger.info("📝 Файл сохраненных знаний не найден, создаем новый")
                
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки сохраненных знаний: {e}")
    
    async def save_knowledge(self):
        """Сохранение знаний"""
        try:
            knowledge_file = Path("agent_knowledge/saved_knowledge.json")
            
            # Сохраняем знания
            saved_data = {
                "knowledge_base": self.shared_memory.knowledge_base,
                "conversation_history": list(self.shared_memory.conversation_history),
                "agent_capabilities": {
                    agent_id: {
                        "skills": cap.skills,
                        "performance_score": cap.performance_score,
                        "specialization_areas": cap.specialization_areas
                    }
                    for agent_id, cap in self.shared_memory.agent_capabilities.items()
                },
                "saved_at": datetime.now().isoformat()
            }
            
            with open(knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(saved_data, f, ensure_ascii=False, indent=2)
            
            logger.info("💾 Знания сохранены")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения знаний: {e}")
    
    async def process_user_message(self, message: str, user_id: str = "user") -> Dict[str, Any]:
        """Обработка сообщения пользователя"""
        try:
            # Обрабатываем через систему агентов
            result = await self.multi_agent_system.process_user_message(message, user_id)
            
            # Сохраняем в общей памяти
            self.shared_memory.add_conversation({
                "user_id": user_id,
                "message": message,
                "agent_response": result,
                "timestamp": datetime.now().isoformat()
            })
            
            # Если задача сложная, создаем задачу координации
            if self._is_complex_task(message):
                await self._create_coordination_task(message, user_id)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения пользователя: {e}")
            return {"error": str(e)}
    
    def _is_complex_task(self, message: str) -> bool:
        """Определение сложности задачи"""
        complex_keywords = [
            "создать проект", "разработать приложение", "создать систему",
            "комплексное решение", "многоэтапная задача", "большой проект"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in complex_keywords)
    
    async def _create_coordination_task(self, message: str, user_id: str):
        """Создание задачи координации"""
        try:
            # Определяем необходимые навыки
            required_skills = self._extract_required_skills(message)
            
            # Создаем задачу
            task = await self.coordinator.create_coordination_task(
                title=f"Задача от пользователя {user_id}",
                description=message,
                required_skills=required_skills,
                complexity=TaskComplexity.COMPLEX,
                priority=7
            )
            
            logger.info(f"📋 Создана задача координации: {task.title}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания задачи координации: {e}")
    
    def _extract_required_skills(self, message: str) -> List[str]:
        """Извлечение необходимых навыков из сообщения"""
        skills_mapping = {
            "код": ["code_generation", "debugging"],
            "разработка": ["code_generation", "architecture_design"],
            "анализ": ["data_analysis", "reporting"],
            "данные": ["data_analysis", "visualization"],
            "дизайн": ["ui_design", "ux_design"],
            "тестирование": ["unit_testing", "integration_testing"],
            "проект": ["project_planning", "task_management"]
        }
        
        message_lower = message.lower()
        required_skills = []
        
        for keyword, skills in skills_mapping.items():
            if keyword in message_lower:
                required_skills.extend(skills)
        
        return list(set(required_skills)) if required_skills else ["general_help"]
    
    def get_system_status(self) -> Dict[str, Any]:
        """Получить статус системы"""
        try:
            uptime = datetime.now() - self.startup_time if self.startup_time else None
            
            return {
                "system_status": "running" if self.running else "stopped",
                "uptime": str(uptime) if uptime else "0:00:00",
                "total_agents": len(self.multi_agent_system.agents),
                "active_agents": len([a for a in self.multi_agent_system.agents.values() if a.status != "idle"]),
                "coordination_status": self.coordinator.get_coordination_status() if self.coordinator else {},
                "shared_memory": {
                    "knowledge_items": len(self.shared_memory.knowledge_base),
                    "conversation_history": len(self.shared_memory.conversation_history),
                    "agent_capabilities": len(self.shared_memory.agent_capabilities)
                },
                "startup_time": self.startup_time.isoformat() if self.startup_time else None
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статуса системы: {e}")
            return {"error": str(e)}
    
    def get_available_agents(self) -> List[Dict[str, Any]]:
        """Получить список доступных агентов"""
        try:
            return [
                {
                    "id": agent.agent_id,
                    "name": agent.name,
                    "type": agent.agent_type.value,
                    "description": agent.description,
                    "skills": agent.skills,
                    "status": agent.status,
                    "performance_score": getattr(
                        self.shared_memory.agent_capabilities.get(agent.agent_id), 
                        "performance_score", 1.0
                    ) if self.shared_memory.agent_capabilities.get(agent.agent_id) else 1.0
                }
                for agent in self.multi_agent_system.agents.values()
            ]
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка агентов: {e}")
            return []
    
    async def start(self):
        """Запуск системы"""
        try:
            logger.info("🚀 Запуск интегрированной системы агентов...")
            
            await self.initialize()
            self.running = True
            logger.info(f"🔧 Статус установлен в running: {self.running}")
            
            # Настраиваем периодическое сохранение знаний
            asyncio.create_task(self._periodic_save())
            
            logger.info("✅ Интегрированная система агентов запущена")
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска системы: {e}")
            raise
    
    async def stop(self):
        """Остановка системы"""
        try:
            logger.info("🛑 Остановка интегрированной системы агентов...")
            
            self.running = False
            logger.info(f"🔧 Статус установлен в stopped: {self.running}")
            
            # Сохраняем знания
            await self.save_knowledge()
            
            # Останавливаем координатор
            if self.coordinator:
                self.coordinator.stop_coordination()
            
            logger.info("✅ Интегрированная система агентов остановлена")
            
        except Exception as e:
            logger.error(f"❌ Ошибка остановки системы: {e}")
    
    async def _periodic_save(self):
        """Периодическое сохранение знаний"""
        while self.running:
            try:
                await asyncio.sleep(300)  # Сохраняем каждые 5 минут
                if self.running:
                    await self.save_knowledge()
            except Exception as e:
                logger.error(f"❌ Ошибка периодического сохранения: {e}")

# Глобальный экземпляр системы (создается лениво)
integrated_system = None

def get_integrated_system():
    """Получить экземпляр интегрированной системы (ленивая инициализация)"""
    global integrated_system
    if integrated_system is None:
        integrated_system = IntegratedAgentSystem()
    return integrated_system

# Обновляем chat_server для использования интегрированной системы
async def process_user_message_integrated(message: str, user_id: str = "user") -> Dict[str, Any]:
    """Обработка сообщения пользователя через интегрированную систему"""
    system = get_integrated_system()
    return await system.process_user_message(message, user_id)

def get_available_agents_integrated() -> List[Dict[str, Any]]:
    """Получить список агентов через интегрированную систему"""
    system = get_integrated_system()
    return system.get_available_agents()

def get_system_status_integrated() -> Dict[str, Any]:
    """Получить статус системы через интегрированную систему"""
    system = get_integrated_system()
    return system.get_system_status()

# Обработчики сигналов для корректного завершения
def signal_handler(signum, frame):
    """Обработчик сигналов для корректного завершения"""
    logger.info(f"📡 Получен сигнал {signum}, завершаем работу...")
    system = get_integrated_system()
    asyncio.create_task(system.stop())
    sys.exit(0)

# Регистрируем обработчики сигналов
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    # Запуск интегрированной системы
    async def main():
        system = get_integrated_system()
        try:
            await system.start()
            
            # Держим систему запущенной
            while system.running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("🛑 Получен сигнал прерывания")
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}")
        finally:
            await system.stop()
    
    # Запуск
    asyncio.run(main())
