#!/usr/bin/env python3
"""
Система множественных AI-агентов
Каждый агент имеет свою специализацию и может работать автономно
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Типы агентов"""
    GENERAL_ASSISTANT = "general_assistant"
    CODE_DEVELOPER = "code_developer"
    DATA_ANALYST = "data_analyst"
    PROJECT_MANAGER = "project_manager"
    CREATIVE_WRITER = "creative_writer"
    RESEARCHER = "researcher"
    SYSTEM_ADMIN = "system_admin"
    BUSINESS_CONSULTANT = "business_consultant"
    DESIGNER = "designer"
    QA_TESTER = "qa_tester"

class TaskStatus(Enum):
    """Статусы задач"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AgentMessage:
    """Сообщение между агентами"""
    id: str
    sender_id: str
    recipient_id: str
    message_type: str
    content: Dict[str, Any]
    timestamp: str
    priority: int = 1

@dataclass
class Task:
    """Задача для агента"""
    id: str
    agent_id: str
    title: str
    description: str
    task_type: str
    status: TaskStatus
    priority: int
    created_at: str
    parameters: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class SharedMemory:
    """Общая память для всех агентов"""
    
    def __init__(self):
        self.knowledge_base = {}
        self.project_context = {}
        self.user_preferences = {}
        self.conversation_history = []
        self.shared_resources = {}
        self.lock = threading.Lock()
    
    def store_knowledge(self, key: str, value: Any, agent_id: str):
        """Сохранить знание в общей памяти"""
        with self.lock:
            if key not in self.knowledge_base:
                self.knowledge_base[key] = []
            self.knowledge_base[key].append({
                "value": value,
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            })
    
    def get_knowledge(self, key: str) -> List[Any]:
        """Получить знания по ключу"""
        with self.lock:
            return self.knowledge_base.get(key, [])
    
    def add_conversation(self, message: Dict[str, Any]):
        """Добавить сообщение в историю разговора"""
        with self.lock:
            self.conversation_history.append(message)
            # Ограничиваем историю последними 1000 сообщениями
            if len(self.conversation_history) > 1000:
                self.conversation_history = self.conversation_history[-1000:]
    
    def get_recent_context(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Получить последний контекст разговора"""
        with self.lock:
            return self.conversation_history[-limit:]

class BaseAgent:
    """Базовый класс для всех агентов"""
    
    def __init__(self, agent_id: str, agent_type: AgentType, name: str, description: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.name = name
        self.description = description
        self.status = "idle"
        self.current_task = None
        self.task_queue = []
        self.completed_tasks = []
        self.skills = []
        self.personality = {}
        self.memory = {}
        self.created_at = datetime.now().isoformat()
        self.last_activity = datetime.now().isoformat()
        
        # Связь с общей памятью
        self.shared_memory = None
        
        # Обработчики сообщений
        self.message_handlers = {}
        
        logger.info(f"🤖 Агент {self.name} ({self.agent_type.value}) создан")
    
    def set_shared_memory(self, shared_memory: SharedMemory):
        """Установить связь с общей памятью"""
        self.shared_memory = shared_memory
    
    def add_skill(self, skill: str, handler: Callable):
        """Добавить навык агенту"""
        self.skills.append(skill)
        self.message_handlers[skill] = handler
        logger.info(f"🔧 Агент {self.name} получил навык: {skill}")
    
    async def process_message(self, message: AgentMessage) -> Dict[str, Any]:
        """Обработать входящее сообщение"""
        try:
            self.status = "processing"
            self.last_activity = datetime.now().isoformat()
            
            # Сохраняем сообщение в общей памяти
            if self.shared_memory:
                self.shared_memory.add_conversation({
                    "agent_id": self.agent_id,
                    "message_type": message.message_type,
                    "content": message.content,
                    "timestamp": message.timestamp
                })
            
            # Обрабатываем сообщение
            if message.message_type in self.message_handlers:
                result = await self.message_handlers[message.message_type](message.content)
            else:
                result = await self._default_handler(message.content)
            
            self.status = "idle"
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения агентом {self.name}: {e}")
            self.status = "error"
            return {"error": str(e)}
    
    async def _default_handler(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Обработчик по умолчанию"""
        return {
            "response": f"Агент {self.name} получил сообщение: {content}",
            "status": "processed"
        }
    
    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Выполнить задачу"""
        try:
            self.status = "working"
            self.current_task = task
            task.status = TaskStatus.IN_PROGRESS
            self.last_activity = datetime.now().isoformat()
            
            logger.info(f"🎯 Агент {self.name} выполняет задачу: {task.title}")
            
            # Выполняем задачу в зависимости от типа
            result = await self._execute_task_by_type(task)
            
            task.status = TaskStatus.COMPLETED
            task.result = result
            self.completed_tasks.append(task)
            self.current_task = None
            self.status = "idle"
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка выполнения задачи агентом {self.name}: {e}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            self.status = "error"
            return {"error": str(e)}
    
    async def _execute_task_by_type(self, task: Task) -> Dict[str, Any]:
        """Выполнить задачу по типу"""
        # Базовая реализация - переопределяется в наследниках
        return {
            "message": f"Задача '{task.title}' выполнена агентом {self.name}",
            "task_id": task.id,
            "agent_id": self.agent_id
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус агента"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "type": self.agent_type.value,
            "status": self.status,
            "skills": self.skills,
            "current_task": self.current_task.title if self.current_task else None,
            "tasks_completed": len(self.completed_tasks),
            "tasks_pending": len(self.task_queue),
            "last_activity": self.last_activity
        }

class GeneralAssistantAgent(BaseAgent):
    """Универсальный помощник"""
    
    def __init__(self, agent_id: str = None):
        super().__init__(
            agent_id or str(uuid.uuid4()),
            AgentType.GENERAL_ASSISTANT,
            "Универсальный Помощник",
            "Помогает с общими задачами, планированием и координацией"
        )
        self._setup_skills()
    
    def _setup_skills(self):
        """Настройка навыков"""
        self.add_skill("general_help", self._handle_general_help)
        self.add_skill("planning", self._handle_planning)
        self.add_skill("coordination", self._handle_coordination)
    
    async def _handle_general_help(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка общих запросов"""
        query = content.get("query", "")
        return {
            "response": f"Я помогу вам с запросом: {query}. Что именно вас интересует?",
            "suggestions": [
                "Планирование задач",
                "Поиск информации",
                "Координация с другими агентами",
                "Анализ данных"
            ]
        }
    
    async def _handle_planning(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка планирования"""
        goal = content.get("goal", "")
        return {
            "response": f"Создаю план для достижения цели: {goal}",
            "plan": [
                "1. Анализ текущей ситуации",
                "2. Определение ресурсов",
                "3. Создание временной шкалы",
                "4. Назначение ответственных",
                "5. Мониторинг прогресса"
            ]
        }
    
    async def _handle_coordination(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка координации"""
        return {
            "response": "Координирую работу с другими агентами",
            "coordination_plan": "Связываюсь с соответствующими специалистами"
        }

class CodeDeveloperAgent(BaseAgent):
    """Агент-разработчик"""
    
    def __init__(self, agent_id: str = None):
        super().__init__(
            agent_id or str(uuid.uuid4()),
            AgentType.CODE_DEVELOPER,
            "Разработчик Кода",
            "Создает, отлаживает и оптимизирует код"
        )
        self._setup_skills()
    
    def _setup_skills(self):
        """Настройка навыков"""
        self.add_skill("code_generation", self._handle_code_generation)
        self.add_skill("debugging", self._handle_debugging)
        self.add_skill("code_review", self._handle_code_review)
        self.add_skill("architecture_design", self._handle_architecture_design)
    
    async def _handle_code_generation(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация кода"""
        language = content.get("language", "python")
        requirements = content.get("requirements", "")
        
        return {
            "response": f"Создаю код на {language} для: {requirements}",
            "code": f"# Код на {language}\n# Требования: {requirements}\n# TODO: Реализовать функциональность",
            "suggestions": [
                "Добавить обработку ошибок",
                "Написать тесты",
                "Добавить документацию",
                "Оптимизировать производительность"
            ]
        }
    
    async def _handle_debugging(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Отладка кода"""
        error = content.get("error", "")
        code = content.get("code", "")
        
        return {
            "response": f"Анализирую ошибку: {error}",
            "analysis": "Проверяю код на наличие проблем",
            "suggestions": [
                "Проверить синтаксис",
                "Проверить логику",
                "Добавить логирование",
                "Протестировать с разными данными"
            ]
        }
    
    async def _handle_code_review(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Ревью кода"""
        code = content.get("code", "")
        
        return {
            "response": "Провожу ревью кода",
            "review": {
                "style": "Проверяю соответствие стандартам",
                "performance": "Анализирую производительность",
                "security": "Проверяю безопасность",
                "maintainability": "Оцениваю поддерживаемость"
            }
        }
    
    async def _handle_architecture_design(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Проектирование архитектуры"""
        requirements = content.get("requirements", "")
        
        return {
            "response": f"Проектирую архитектуру для: {requirements}",
            "architecture": {
                "components": ["Frontend", "Backend", "Database", "API"],
                "patterns": ["MVC", "Repository", "Factory"],
                "technologies": ["Python", "FastAPI", "PostgreSQL", "Redis"]
            }
        }

class DataAnalystAgent(BaseAgent):
    """Агент-аналитик данных"""
    
    def __init__(self, agent_id: str = None):
        super().__init__(
            agent_id or str(uuid.uuid4()),
            AgentType.DATA_ANALYST,
            "Аналитик Данных",
            "Анализирует данные, создает отчеты и визуализации"
        )
        self._setup_skills()
    
    def _setup_skills(self):
        """Настройка навыков"""
        self.add_skill("data_analysis", self._handle_data_analysis)
        self.add_skill("reporting", self._handle_reporting)
        self.add_skill("visualization", self._handle_visualization)
        self.add_skill("predictive_modeling", self._handle_predictive_modeling)
    
    async def _handle_data_analysis(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ данных"""
        data_source = content.get("data_source", "")
        analysis_type = content.get("analysis_type", "descriptive")
        
        return {
            "response": f"Анализирую данные из {data_source}",
            "analysis": {
                "type": analysis_type,
                "summary": "Выполняю статистический анализ",
                "insights": ["Тренд 1", "Паттерн 2", "Аномалия 3"]
            }
        }
    
    async def _handle_reporting(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Создание отчетов"""
        report_type = content.get("report_type", "summary")
        
        return {
            "response": f"Создаю отчет типа: {report_type}",
            "report": {
                "title": "Аналитический отчет",
                "sections": ["Введение", "Методология", "Результаты", "Выводы"],
                "recommendations": ["Рекомендация 1", "Рекомендация 2"]
            }
        }
    
    async def _handle_visualization(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Создание визуализаций"""
        chart_type = content.get("chart_type", "line")
        
        return {
            "response": f"Создаю {chart_type} график",
            "visualization": {
                "type": chart_type,
                "data_points": 100,
                "format": "interactive"
            }
        }
    
    async def _handle_predictive_modeling(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Предиктивное моделирование"""
        model_type = content.get("model_type", "regression")
        
        return {
            "response": f"Создаю модель {model_type}",
            "model": {
                "type": model_type,
                "accuracy": "85%",
                "features": ["feature1", "feature2", "feature3"]
            }
        }

class ProjectManagerAgent(BaseAgent):
    """Агент-менеджер проектов"""
    
    def __init__(self, agent_id: str = None):
        super().__init__(
            agent_id or str(uuid.uuid4()),
            AgentType.PROJECT_MANAGER,
            "Менеджер Проектов",
            "Управляет проектами, планирует задачи и координирует команду"
        )
        self._setup_skills()
    
    def _setup_skills(self):
        """Настройка навыков"""
        self.add_skill("project_planning", self._handle_project_planning)
        self.add_skill("task_management", self._handle_task_management)
        self.add_skill("resource_allocation", self._handle_resource_allocation)
        self.add_skill("progress_tracking", self._handle_progress_tracking)
    
    async def _handle_project_planning(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Планирование проекта"""
        project_name = content.get("project_name", "")
        requirements = content.get("requirements", [])
        
        return {
            "response": f"Планирую проект: {project_name}",
            "project_plan": {
                "phases": ["Инициация", "Планирование", "Выполнение", "Завершение"],
                "timeline": "4 недели",
                "resources": ["Разработчик", "Дизайнер", "Тестировщик"],
                "milestones": ["MVP", "Beta", "Release"]
            }
        }
    
    async def _handle_task_management(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Управление задачами"""
        tasks = content.get("tasks", [])
        
        return {
            "response": "Управляю задачами проекта",
            "task_plan": {
                "total_tasks": len(tasks),
                "priority_order": "По важности и срочности",
                "assignments": "Назначаю агентам по специализации"
            }
        }
    
    async def _handle_resource_allocation(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Распределение ресурсов"""
        return {
            "response": "Распределяю ресурсы между агентами",
            "allocation": {
                "developers": 2,
                "analysts": 1,
                "designers": 1,
                "testers": 1
            }
        }
    
    async def _handle_progress_tracking(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Отслеживание прогресса"""
        return {
            "response": "Отслеживаю прогресс проекта",
            "progress": {
                "completed": "60%",
                "in_progress": "30%",
                "pending": "10%",
                "blockers": []
            }
        }

class MultiAgentSystem:
    """Система управления множественными агентами"""
    
    def __init__(self):
        self.agents = {}
        self.shared_memory = SharedMemory()
        self.message_queue = []
        self.running = False
        self.coordinator = None
        
        # Создаем агентов
        self._create_agents()
        
        logger.info("🚀 Система множественных агентов инициализирована")
    
    def _create_agents(self):
        """Создание агентов"""
        # Универсальный помощник
        general_agent = GeneralAssistantAgent()
        self.agents[general_agent.agent_id] = general_agent
        
        # Разработчик
        dev_agent = CodeDeveloperAgent()
        self.agents[dev_agent.agent_id] = dev_agent
        
        # Аналитик данных
        analyst_agent = DataAnalystAgent()
        self.agents[analyst_agent.agent_id] = analyst_agent
        
        # Менеджер проектов
        pm_agent = ProjectManagerAgent()
        self.agents[pm_agent.agent_id] = pm_agent
        
        # Устанавливаем общую память для всех агентов
        for agent in self.agents.values():
            agent.set_shared_memory(self.shared_memory)
        
        logger.info(f"✅ Создано {len(self.agents)} агентов")
    
    async def process_user_message(self, message: str, user_id: str = "user") -> Dict[str, Any]:
        """Обработать сообщение пользователя"""
        try:
            # Определяем подходящего агента
            agent = self._select_agent_for_message(message)
            
            # Создаем сообщение
            agent_message = AgentMessage(
                id=str(uuid.uuid4()),
                sender_id=user_id,
                recipient_id=agent.agent_id,
                message_type="user_query",
                content={"message": message, "user_id": user_id},
                timestamp=datetime.now().isoformat()
            )
            
            # Обрабатываем сообщение
            result = await agent.process_message(agent_message)
            
            # Сохраняем в общей памяти
            self.shared_memory.add_conversation({
                "user_id": user_id,
                "message": message,
                "agent_response": result,
                "agent_id": agent.agent_id,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "response": result,
                "agent": agent.name,
                "agent_type": agent.agent_type.value,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения пользователя: {e}")
            return {"error": str(e)}
    
    def _select_agent_for_message(self, message: str) -> BaseAgent:
        """Выбрать подходящего агента для сообщения"""
        message_lower = message.lower()
        
        # Ключевые слова для определения типа агента
        if any(word in message_lower for word in ["код", "программирование", "разработка", "debug", "ошибка"]):
            return self._get_agent_by_type(AgentType.CODE_DEVELOPER)
        elif any(word in message_lower for word in ["анализ", "данные", "отчет", "график", "статистика"]):
            return self._get_agent_by_type(AgentType.DATA_ANALYST)
        elif any(word in message_lower for word in ["проект", "план", "задача", "управление", "координация"]):
            return self._get_agent_by_type(AgentType.PROJECT_MANAGER)
        else:
            return self._get_agent_by_type(AgentType.GENERAL_ASSISTANT)
    
    def _get_agent_by_type(self, agent_type: AgentType) -> BaseAgent:
        """Получить агента по типу"""
        for agent in self.agents.values():
            if agent.agent_type == agent_type:
                return agent
        # Если не найден, возвращаем универсального помощника
        return self._get_agent_by_type(AgentType.GENERAL_ASSISTANT)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Получить статус системы"""
        return {
            "total_agents": len(self.agents),
            "agents": [agent.get_status() for agent in self.agents.values()],
            "shared_memory": {
                "knowledge_items": len(self.shared_memory.knowledge_base),
                "conversation_history": len(self.shared_memory.conversation_history)
            },
            "system_status": "running" if self.running else "stopped"
        }
    
    def get_available_agents(self) -> List[Dict[str, Any]]:
        """Получить список доступных агентов"""
        return [
            {
                "id": agent.agent_id,
                "name": agent.name,
                "type": agent.agent_type.value,
                "description": agent.description,
                "skills": agent.skills,
                "status": agent.status
            }
            for agent in self.agents.values()
        ]

# Глобальный экземпляр системы
# multi_agent_system = MultiAgentSystem()  # Закомментировано для избежания ошибок при импорте

if __name__ == "__main__":
    # Тестирование системы
    async def test_system():
        system = MultiAgentSystem()
        
        # Тестовые сообщения
        test_messages = [
            "Помоги мне создать веб-приложение",
            "Проанализируй эти данные",
            "Создай план проекта",
            "Как дела?"
        ]
        
        for message in test_messages:
            print(f"\n👤 Пользователь: {message}")
            result = await system.process_user_message(message)
            print(f"🤖 {result['agent']}: {result['response']}")
        
        # Статус системы
        print(f"\n📊 Статус системы:")
        status = system.get_system_status()
        print(f"Агентов: {status['total_agents']}")
        for agent in status['agents']:
            print(f"  - {agent['name']}: {agent['status']}")
    
    # Запуск тестов
    asyncio.run(test_system())
