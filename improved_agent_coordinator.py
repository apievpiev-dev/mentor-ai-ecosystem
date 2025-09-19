#!/usr/bin/env python3
"""
Улучшенная система координации агентов
Заставляет агентов работать и отслеживает их активность
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from collections import defaultdict, deque
import hashlib

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskComplexity(Enum):
    """Сложность задач"""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    MULTI_AGENT = "multi_agent"

class CoordinationStrategy(Enum):
    """Стратегии координации"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    COLLABORATIVE = "collaborative"
    HIERARCHICAL = "hierarchical"

@dataclass
class AgentCapability:
    """Возможности агента"""
    agent_id: str
    skills: List[str]
    performance_score: float
    availability: bool
    current_load: float
    specialization_areas: List[str]
    collaboration_history: Dict[str, int]
    is_active: bool = False
    last_activity: Optional[datetime] = None

@dataclass
class CoordinationTask:
    """Задача для координации"""
    task_id: str
    description: str
    complexity: TaskComplexity
    required_skills: List[str]
    assigned_agents: List[str]
    status: str
    created_at: datetime
    deadline: Optional[datetime] = None
    priority: int = 1
    dependencies: List[str] = None

@dataclass
class AgentMessage:
    """Сообщение между агентами"""
    message_id: str
    sender_id: str
    recipient_id: str
    content: Dict[str, Any]
    timestamp: datetime
    message_type: str
    priority: int = 1

class KnowledgeGraph:
    """Граф знаний для хранения связей между концепциями"""
    
    def __init__(self):
        self.nodes = {}  # concept_id -> concept_data
        self.edges = defaultdict(list)  # concept_id -> [related_concept_ids]
        self.weights = {}  # (concept1, concept2) -> weight
    
    def add_concept(self, concept_id: str, concept_data: Dict[str, Any]):
        """Добавление концепции"""
        self.nodes[concept_id] = concept_data
    
    def add_relation(self, concept1: str, concept2: str, weight: float = 1.0):
        """Добавление связи между концепциями"""
        if concept1 not in self.edges:
            self.edges[concept1] = []
        if concept2 not in self.edges:
            self.edges[concept2] = []
        
        if concept2 not in self.edges[concept1]:
            self.edges[concept1].append(concept2)
        if concept1 not in self.edges[concept2]:
            self.edges[concept2].append(concept1)
        
        self.weights[(concept1, concept2)] = weight
        self.weights[(concept2, concept1)] = weight
    
    def get_related_concepts(self, concept_id: str, max_depth: int = 2) -> List[str]:
        """Получение связанных концепций"""
        if concept_id not in self.nodes:
            return []
        
        visited = set()
        queue = [(concept_id, 0)]
        related = []
        
        while queue:
            current, depth = queue.pop(0)
            if current in visited or depth > max_depth:
                continue
            
            visited.add(current)
            if current != concept_id:
                related.append(current)
            
            for neighbor in self.edges.get(current, []):
                if neighbor not in visited:
                    queue.append((neighbor, depth + 1))
        
        return related

class ImprovedAgentCoordinator:
    """Улучшенный координатор агентов"""
    
    def __init__(self):
        self.agents = {}
        self.tasks = {}
        self.message_queue = deque()
        self.shared_memory = ImprovedSharedMemory()
        self.running = False
        self.lock = threading.Lock()
        self.active_agents = set()
        self.agent_activity = defaultdict(lambda: {"last_seen": None, "task_count": 0})
        
        # Автономные задачи для агентов
        self.autonomous_tasks = {
            "general_assistant": [
                "Проанализируй текущее состояние системы и создай отчет",
                "Предложи улучшения для системы",
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
    
    def register_agent(self, agent_id: str, agent_type: str, skills: List[str]):
        """Регистрация агента"""
        with self.lock:
            capability = AgentCapability(
                agent_id=agent_id,
                skills=skills,
                performance_score=1.0,
                availability=True,
                current_load=0.0,
                specialization_areas=[agent_type],
                collaboration_history={},
                is_active=False,
                last_activity=None
            )
            self.agents[agent_id] = capability
            logger.info(f"✅ Агент {agent_id} ({agent_type}) зарегистрирован")
    
    def send_message(self, sender_id: str, recipient_id: str, content: Dict[str, Any], 
                    message_type: str = "task", priority: int = 1):
        """Отправка сообщения агенту"""
        message = AgentMessage(
            message_id=str(uuid.uuid4()),
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content,
            timestamp=datetime.now(),
            message_type=message_type,
            priority=priority
        )
        
        with self.lock:
            self.message_queue.append(message)
            
            # Активируем агента
            if recipient_id in self.agents:
                self.agents[recipient_id].is_active = True
                self.agents[recipient_id].last_activity = datetime.now()
                self.active_agents.add(recipient_id)
                self.agent_activity[recipient_id]["last_seen"] = datetime.now()
                self.agent_activity[recipient_id]["task_count"] += 1
                
                logger.info(f"🚀 Агент {recipient_id} активирован")
        
        return message.message_id
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Получение статуса агента"""
        with self.lock:
            if agent_id not in self.agents:
                return {"error": "Agent not found"}
            
            agent = self.agents[agent_id]
            activity = self.agent_activity[agent_id]
            
            return {
                "agent_id": agent_id,
                "is_active": agent.is_active,
                "last_activity": agent.last_activity.isoformat() if agent.last_activity else None,
                "current_load": agent.current_load,
                "availability": agent.availability,
                "performance_score": agent.performance_score,
                "task_count": activity["task_count"],
                "last_seen": activity["last_seen"].isoformat() if activity["last_seen"] else None
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Получение статуса системы"""
        with self.lock:
            total_agents = len(self.agents)
            active_agents = len(self.active_agents)
            active_tasks = len([t for t in self.tasks.values() if t.status == "in_progress"])
            message_queue_size = len(self.message_queue)
            
            agent_capabilities = {}
            for agent_id, agent in self.agents.items():
                agent_capabilities[agent_id] = {
                    "skills": agent.skills,
                    "performance_score": agent.performance_score,
                    "availability": agent.availability,
                    "current_load": agent.current_load,
                    "is_active": agent.is_active,
                    "last_activity": agent.last_activity.isoformat() if agent.last_activity else None
                }
            
            return {
                "total_agents": total_agents,
                "active_agents": active_agents,
                "active_tasks": active_tasks,
                "message_queue_size": message_queue_size,
                "agent_capabilities": agent_capabilities,
                "active_tasks_info": []
            }
    
    async def autonomous_task_generator(self):
        """Генератор автономных задач"""
        logger.info("🚀 Запуск генератора автономных задач...")
        
        task_counter = 0
        
        while self.running:
            try:
                # Выбираем случайного агента
                if self.agents:
                    agent_id = list(self.agents.keys())[task_counter % len(self.agents)]
                    agent = self.agents[agent_id]
                    
                    if agent.specialization_areas:
                        agent_type = agent.specialization_areas[0]
                        if agent_type in self.autonomous_tasks:
                            tasks = self.autonomous_tasks[agent_type]
                            task = tasks[task_counter % len(tasks)]
                            
                            # Отправляем задачу агенту
                            self.send_message(
                                sender_id="coordinator",
                                recipient_id=agent_id,
                                content={"task": task, "type": "autonomous"},
                                message_type="autonomous_task",
                                priority=1
                            )
                            
                            logger.info(f"📋 Автономная задача отправлена агенту {agent_id}: {task[:50]}...")
                
                task_counter += 1
                
                # Ждем 30 секунд перед следующей задачей
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Ошибка в генераторе автономных задач: {e}")
                await asyncio.sleep(10)
    
    async def start(self):
        """Запуск координатора"""
        logger.info("🚀 Запуск улучшенного координатора агентов...")
        self.running = True
        
        # Запускаем генератор автономных задач
        asyncio.create_task(self.autonomous_task_generator())
        
        logger.info("✅ Улучшенный координатор агентов запущен")
    
    def stop(self):
        """Остановка координатора"""
        logger.info("🛑 Остановка улучшенного координатора агентов...")
        self.running = False

class ImprovedSharedMemory:
    """Улучшенная общая память"""
    
    def __init__(self):
        self.knowledge_base = {}
        self.project_context = {}
        self.user_preferences = {}
        self.conversation_history = []
        self.shared_resources = {}
        self.knowledge_graph = KnowledgeGraph()
        self.agent_capabilities = {}
        self.task_history = []
        self.collaboration_patterns = defaultdict(int)
        self.lock = threading.Lock()
    
    def store_knowledge(self, key: str, value: Any, metadata: Dict[str, Any] = None):
        """Сохранение знаний"""
        with self.lock:
            self.knowledge_base[key] = {
                "value": value,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat()
            }
    
    def get_knowledge(self, key: str) -> Any:
        """Получение знаний"""
        with self.lock:
            return self.knowledge_base.get(key, {}).get("value")
    
    def add_conversation(self, conversation: Dict[str, Any]):
        """Добавление разговора"""
        with self.lock:
            self.conversation_history.append(conversation)
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Получение последних разговоров"""
        with self.lock:
            return self.conversation_history[-limit:]

# Глобальный экземпляр координатора
_improved_coordinator = None

def get_improved_coordinator() -> ImprovedAgentCoordinator:
    """Получение глобального экземпляра координатора"""
    global _improved_coordinator
    if _improved_coordinator is None:
        _improved_coordinator = ImprovedAgentCoordinator()
    return _improved_coordinator

async def main():
    """Главная функция для тестирования"""
    coordinator = get_improved_coordinator()
    
    # Регистрируем тестовых агентов
    coordinator.register_agent("test_agent_1", "general_assistant", ["general_help", "planning"])
    coordinator.register_agent("test_agent_2", "code_developer", ["code_generation", "debugging"])
    
    # Запускаем координатор
    await coordinator.start()
    
    # Ждем некоторое время
    await asyncio.sleep(60)
    
    # Останавливаем координатор
    coordinator.stop()

if __name__ == "__main__":
    asyncio.run(main())


