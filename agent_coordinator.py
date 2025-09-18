#!/usr/bin/env python3
"""
Система координации между агентами
Обеспечивает взаимодействие, общую память и интеллектуальное распределение задач
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
    SEQUENTIAL = "sequential"  # Последовательное выполнение
    PARALLEL = "parallel"      # Параллельное выполнение
    COLLABORATIVE = "collaborative"  # Совместная работа
    HIERARCHICAL = "hierarchical"    # Иерархическая координация

@dataclass
class AgentCapability:
    """Возможности агента"""
    agent_id: str
    skills: List[str]
    performance_score: float
    availability: bool
    current_load: float
    specialization_areas: List[str]
    collaboration_history: Dict[str, int]  # agent_id -> успешных коллабораций

@dataclass
class CoordinationTask:
    """Задача для координации"""
    id: str
    title: str
    description: str
    complexity: TaskComplexity
    required_skills: List[str]
    priority: int
    deadline: Optional[str]
    dependencies: List[str]
    assigned_agents: List[str]
    status: str
    created_at: str
    progress: float = 0.0
    results: Dict[str, Any] = None

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
    requires_response: bool = False
    response_deadline: Optional[str] = None

class KnowledgeGraph:
    """Граф знаний для хранения связей между концепциями"""
    
    def __init__(self):
        self.nodes = {}  # concept_id -> concept_data
        self.edges = {}  # (concept1, concept2) -> relationship_data
        self.concept_index = defaultdict(set)  # keyword -> concept_ids
        self.lock = threading.Lock()
    
    def add_concept(self, concept_id: str, name: str, description: str, 
                   keywords: List[str], agent_id: str, metadata: Dict[str, Any] = None):
        """Добавить концепцию в граф"""
        with self.lock:
            self.nodes[concept_id] = {
                "id": concept_id,
                "name": name,
                "description": description,
                "keywords": keywords,
                "created_by": agent_id,
                "created_at": datetime.now().isoformat(),
                "metadata": metadata or {},
                "usage_count": 0
            }
            
            # Индексируем по ключевым словам
            for keyword in keywords:
                self.concept_index[keyword.lower()].add(concept_id)
    
    def add_relationship(self, concept1_id: str, concept2_id: str, 
                        relationship_type: str, strength: float = 1.0):
        """Добавить связь между концепциями"""
        with self.lock:
            edge_key = tuple(sorted([concept1_id, concept2_id]))
            self.edges[edge_key] = {
                "concept1": concept1_id,
                "concept2": concept2_id,
                "type": relationship_type,
                "strength": strength,
                "created_at": datetime.now().isoformat()
            }
    
    def find_related_concepts(self, concept_id: str, max_depth: int = 2) -> List[str]:
        """Найти связанные концепции"""
        with self.lock:
            related = set()
            to_explore = [(concept_id, 0)]
            
            while to_explore:
                current_id, depth = to_explore.pop(0)
                if depth >= max_depth:
                    continue
                
                for edge_key, edge_data in self.edges.items():
                    if current_id in edge_key:
                        other_id = edge_key[0] if edge_key[1] == current_id else edge_key[1]
                        if other_id not in related:
                            related.add(other_id)
                            to_explore.append((other_id, depth + 1))
            
            return list(related)
    
    def search_concepts(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Поиск концепций по запросу"""
        with self.lock:
            query_lower = query.lower()
            results = []
            
            # Поиск по ключевым словам
            for keyword, concept_ids in self.concept_index.items():
                if query_lower in keyword:
                    for concept_id in concept_ids:
                        if concept_id in self.nodes:
                            concept = self.nodes[concept_id].copy()
                            concept["relevance_score"] = 1.0
                            results.append(concept)
            
            # Сортировка по релевантности и использованию
            results.sort(key=lambda x: (x["relevance_score"], x["usage_count"]), reverse=True)
            return results[:limit]

class EnhancedSharedMemory:
    """Расширенная общая память с графом знаний"""
    
    def __init__(self):
        self.knowledge_base = {}
        self.project_context = {}
        self.user_preferences = {}
        self.conversation_history = deque(maxlen=1000)
        self.shared_resources = {}
        self.knowledge_graph = KnowledgeGraph()
        self.agent_capabilities = {}
        self.task_history = []
        self.collaboration_patterns = defaultdict(int)
        self.lock = threading.Lock()
    
    def store_knowledge(self, key: str, value: Any, agent_id: str, 
                       keywords: List[str] = None, metadata: Dict[str, Any] = None):
        """Сохранить знание в общей памяти"""
        with self.lock:
            if key not in self.knowledge_base:
                self.knowledge_base[key] = []
            
            knowledge_item = {
                "value": value,
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat(),
                "keywords": keywords or [],
                "metadata": metadata or {}
            }
            
            self.knowledge_base[key].append(knowledge_item)
            
            # Добавляем в граф знаний
            concept_id = hashlib.md5(key.encode()).hexdigest()
            self.knowledge_graph.add_concept(
                concept_id, key, str(value), keywords or [], agent_id, metadata
            )
    
    def get_knowledge(self, key: str) -> List[Any]:
        """Получить знания по ключу"""
        with self.lock:
            return self.knowledge_base.get(key, [])
    
    def search_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """Поиск знаний по запросу"""
        with self.lock:
            # Поиск в графе знаний
            concepts = self.knowledge_graph.search_concepts(query)
            
            # Поиск в базе знаний
            results = []
            query_lower = query.lower()
            
            for key, items in self.knowledge_base.items():
                if query_lower in key.lower():
                    for item in items:
                        if any(query_lower in str(kw).lower() for kw in item.get("keywords", [])):
                            results.append({
                                "key": key,
                                "value": item["value"],
                                "agent_id": item["agent_id"],
                                "timestamp": item["timestamp"],
                                "relevance": 1.0
                            })
            
            return results + concepts
    
    def add_conversation(self, message: Dict[str, Any]):
        """Добавить сообщение в историю разговора"""
        with self.lock:
            self.conversation_history.append(message)
    
    def get_recent_context(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Получить последний контекст разговора"""
        with self.lock:
            return list(self.conversation_history)[-limit:]
    
    def update_agent_capability(self, agent_id: str, capability: AgentCapability):
        """Обновить возможности агента"""
        with self.lock:
            self.agent_capabilities[agent_id] = capability
    
    def get_agent_capabilities(self) -> Dict[str, AgentCapability]:
        """Получить возможности всех агентов"""
        with self.lock:
            return self.agent_capabilities.copy()
    
    def record_collaboration(self, agent1_id: str, agent2_id: str, success: bool):
        """Записать результат коллаборации"""
        with self.lock:
            key = tuple(sorted([agent1_id, agent2_id]))
            if success:
                self.collaboration_patterns[key] += 1
    
    def get_collaboration_score(self, agent1_id: str, agent2_id: str) -> int:
        """Получить оценку коллаборации между агентами"""
        with self.lock:
            key = tuple(sorted([agent1_id, agent2_id]))
            return self.collaboration_patterns.get(key, 0)

class AgentCoordinator:
    """Координатор агентов"""
    
    def __init__(self, shared_memory: EnhancedSharedMemory):
        self.shared_memory = shared_memory
        self.agents = {}
        self.active_tasks = {}
        self.message_queue = deque()
        self.coordination_strategies = {}
        self.task_assignments = {}
        self.running = False
        self.coordinator_thread = None
        
        # Настройка стратегий координации
        self._setup_coordination_strategies()
        
        logger.info("🎯 Координатор агентов инициализирован")
    
    def _setup_coordination_strategies(self):
        """Настройка стратегий координации"""
        self.coordination_strategies = {
            TaskComplexity.SIMPLE: CoordinationStrategy.SEQUENTIAL,
            TaskComplexity.MEDIUM: CoordinationStrategy.PARALLEL,
            TaskComplexity.COMPLEX: CoordinationStrategy.COLLABORATIVE,
            TaskComplexity.MULTI_AGENT: CoordinationStrategy.HIERARCHICAL
        }
    
    def register_agent(self, agent):
        """Регистрация агента в системе координации"""
        self.agents[agent.agent_id] = agent
        
        # Создаем профиль возможностей агента
        capability = AgentCapability(
            agent_id=agent.agent_id,
            skills=agent.skills,
            performance_score=1.0,
            availability=True,
            current_load=0.0,
            specialization_areas=agent.skills,
            collaboration_history={}
        )
        
        self.shared_memory.update_agent_capability(agent.agent_id, capability)
        
        logger.info(f"📝 Агент {agent.name} зарегистрирован в координаторе")
    
    def start_coordination(self):
        """Запуск системы координации"""
        self.running = True
        self.coordinator_thread = threading.Thread(target=self._coordination_loop, daemon=True)
        self.coordinator_thread.start()
        logger.info("🚀 Система координации запущена")
    
    def stop_coordination(self):
        """Остановка системы координации"""
        self.running = False
        if self.coordinator_thread:
            self.coordinator_thread.join(timeout=5)
        logger.info("🛑 Система координации остановлена")
    
    def _coordination_loop(self):
        """Основной цикл координации"""
        while self.running:
            try:
                # Обработка очереди сообщений
                self._process_message_queue()
                
                # Мониторинг активных задач
                self._monitor_active_tasks()
                
                # Оптимизация распределения ресурсов
                self._optimize_resource_allocation()
                
                # Обновление возможностей агентов
                self._update_agent_capabilities()
                
                time.sleep(1)  # Пауза между итерациями
                
            except Exception as e:
                logger.error(f"❌ Ошибка в цикле координации: {e}")
                time.sleep(5)
    
    def _process_message_queue(self):
        """Обработка очереди сообщений"""
        while self.message_queue:
            try:
                message = self.message_queue.popleft()
                self._route_message(message)
            except Exception as e:
                logger.error(f"❌ Ошибка обработки сообщения: {e}")
    
    def _route_message(self, message: AgentMessage):
        """Маршрутизация сообщения между агентами"""
        if message.recipient_id in self.agents:
            agent = self.agents[message.recipient_id]
            # Асинхронная обработка сообщения
            asyncio.create_task(agent.process_message(message))
        else:
            logger.warning(f"⚠️ Агент {message.recipient_id} не найден")
    
    def _monitor_active_tasks(self):
        """Мониторинг активных задач"""
        for task_id, task in list(self.active_tasks.items()):
            if task.status == "completed":
                self._handle_task_completion(task)
            elif task.status == "failed":
                self._handle_task_failure(task)
            elif self._is_task_overdue(task):
                self._handle_overdue_task(task)
    
    def _handle_task_completion(self, task: CoordinationTask):
        """Обработка завершения задачи"""
        logger.info(f"✅ Задача {task.title} завершена")
        
        # Обновляем статистику агентов
        for agent_id in task.assigned_agents:
            if agent_id in self.shared_memory.agent_capabilities:
                capability = self.shared_memory.agent_capabilities[agent_id]
                capability.performance_score = min(1.0, capability.performance_score + 0.1)
                capability.current_load = max(0.0, capability.current_load - 0.2)
                self.shared_memory.update_agent_capability(agent_id, capability)
        
        # Записываем успешную коллаборацию
        if len(task.assigned_agents) > 1:
            for i, agent1 in enumerate(task.assigned_agents):
                for agent2 in task.assigned_agents[i+1:]:
                    self.shared_memory.record_collaboration(agent1, agent2, True)
        
        # Удаляем из активных задач
        del self.active_tasks[task.id]
    
    def _handle_task_failure(self, task: CoordinationTask):
        """Обработка неудачи задачи"""
        logger.warning(f"❌ Задача {task.title} провалена")
        
        # Обновляем статистику агентов
        for agent_id in task.assigned_agents:
            if agent_id in self.shared_memory.agent_capabilities:
                capability = self.shared_memory.agent_capabilities[agent_id]
                capability.performance_score = max(0.1, capability.performance_score - 0.05)
                self.shared_memory.update_agent_capability(agent_id, capability)
        
        # Записываем неудачную коллаборацию
        if len(task.assigned_agents) > 1:
            for i, agent1 in enumerate(task.assigned_agents):
                for agent2 in task.assigned_agents[i+1:]:
                    self.shared_memory.record_collaboration(agent1, agent2, False)
        
        # Удаляем из активных задач
        del self.active_tasks[task.id]
    
    def _is_task_overdue(self, task: CoordinationTask) -> bool:
        """Проверка просрочки задачи"""
        if not task.deadline:
            return False
        
        deadline = datetime.fromisoformat(task.deadline)
        return datetime.now() > deadline
    
    def _handle_overdue_task(self, task: CoordinationTask):
        """Обработка просроченной задачи"""
        logger.warning(f"⏰ Задача {task.title} просрочена")
        
        # Перераспределяем задачу
        self._redistribute_task(task)
    
    def _redistribute_task(self, task: CoordinationTask):
        """Перераспределение задачи"""
        # Находим более подходящих агентов
        new_agents = self._select_agents_for_task(task)
        
        if new_agents:
            task.assigned_agents = new_agents
            task.status = "in_progress"
            logger.info(f"🔄 Задача {task.title} перераспределена")
        else:
            task.status = "failed"
            logger.error(f"❌ Не удалось перераспределить задачу {task.title}")
    
    def _optimize_resource_allocation(self):
        """Оптимизация распределения ресурсов"""
        # Анализируем загрузку агентов
        capabilities = self.shared_memory.get_agent_capabilities()
        
        for agent_id, capability in capabilities.items():
            if capability.current_load > 0.8:  # Высокая загрузка
                # Ищем задачи для перераспределения
                self._balance_agent_load(agent_id, capability)
    
    def _balance_agent_load(self, agent_id: str, capability: AgentCapability):
        """Балансировка загрузки агента"""
        # Находим менее загруженных агентов с похожими навыками
        other_capabilities = {
            aid: cap for aid, cap in self.shared_memory.get_agent_capabilities().items()
            if aid != agent_id and cap.current_load < 0.5
        }
        
        # Ищем агентов с пересекающимися навыками
        for other_id, other_cap in other_capabilities.items():
            common_skills = set(capability.skills) & set(other_cap.skills)
            if common_skills:
                # Можем перераспределить некоторые задачи
                logger.info(f"⚖️ Балансировка загрузки между {agent_id} и {other_id}")
                break
    
    def _update_agent_capabilities(self):
        """Обновление возможностей агентов"""
        for agent_id, agent in self.agents.items():
            if hasattr(agent, 'get_status'):
                status = agent.get_status()
                
                capability = self.shared_memory.agent_capabilities.get(agent_id)
                if capability:
                    capability.availability = status.get("status") != "error"
                    capability.current_load = len(agent.task_queue) / 10.0  # Нормализация
                    self.shared_memory.update_agent_capability(agent_id, capability)
    
    async def create_coordination_task(self, title: str, description: str, 
                                     required_skills: List[str], 
                                     complexity: TaskComplexity = TaskComplexity.MEDIUM,
                                     priority: int = 5,
                                     deadline: Optional[str] = None) -> CoordinationTask:
        """Создать задачу для координации"""
        task = CoordinationTask(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            complexity=complexity,
            required_skills=required_skills,
            priority=priority,
            deadline=deadline,
            dependencies=[],
            assigned_agents=[],
            status="pending",
            created_at=datetime.now().isoformat()
        )
        
        # Выбираем агентов для задачи
        selected_agents = self._select_agents_for_task(task)
        task.assigned_agents = selected_agents
        
        if selected_agents:
            task.status = "in_progress"
            self.active_tasks[task.id] = task
            
            # Создаем сообщения для агентов
            await self._notify_agents_about_task(task)
            
            logger.info(f"📋 Создана задача координации: {task.title}")
        else:
            task.status = "failed"
            logger.error(f"❌ Не удалось назначить агентов для задачи: {task.title}")
        
        return task
    
    def _select_agents_for_task(self, task: CoordinationTask) -> List[str]:
        """Выбор агентов для задачи"""
        capabilities = self.shared_memory.get_agent_capabilities()
        suitable_agents = []
        
        # Фильтруем агентов по навыкам и доступности
        for agent_id, capability in capabilities.items():
            if not capability.availability:
                continue
            
            # Проверяем наличие необходимых навыков
            has_skills = any(skill in capability.skills for skill in task.required_skills)
            if not has_skills:
                continue
            
            # Проверяем загрузку
            if capability.current_load > 0.8:
                continue
            
            suitable_agents.append((agent_id, capability))
        
        # Сортируем по производительности и загрузке
        suitable_agents.sort(
            key=lambda x: (x[1].performance_score, -x[1].current_load),
            reverse=True
        )
        
        # Выбираем количество агентов в зависимости от сложности
        if task.complexity == TaskComplexity.SIMPLE:
            return [suitable_agents[0][0]] if suitable_agents else []
        elif task.complexity == TaskComplexity.MEDIUM:
            return [agent[0] for agent in suitable_agents[:2]]
        elif task.complexity == TaskComplexity.COMPLEX:
            return [agent[0] for agent in suitable_agents[:3]]
        else:  # MULTI_AGENT
            return [agent[0] for agent in suitable_agents[:5]]
    
    async def _notify_agents_about_task(self, task: CoordinationTask):
        """Уведомление агентов о новой задаче"""
        for agent_id in task.assigned_agents:
            message = AgentMessage(
                id=str(uuid.uuid4()),
                sender_id="coordinator",
                recipient_id=agent_id,
                message_type="new_task",
                content={
                    "task_id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "required_skills": task.required_skills,
                    "priority": task.priority,
                    "deadline": task.deadline
                },
                timestamp=datetime.now().isoformat(),
                priority=task.priority
            )
            
            self.message_queue.append(message)
    
    def send_message_to_agent(self, sender_id: str, recipient_id: str, 
                            message_type: str, content: Dict[str, Any],
                            priority: int = 1, requires_response: bool = False):
        """Отправить сообщение агенту"""
        message = AgentMessage(
            id=str(uuid.uuid4()),
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=message_type,
            content=content,
            timestamp=datetime.now().isoformat(),
            priority=priority,
            requires_response=requires_response
        )
        
        self.message_queue.append(message)
    
    def get_coordination_status(self) -> Dict[str, Any]:
        """Получить статус координации"""
        capabilities = self.shared_memory.get_agent_capabilities()
        
        return {
            "total_agents": len(self.agents),
            "active_tasks": len(self.active_tasks),
            "message_queue_size": len(self.message_queue),
            "agent_capabilities": {
                agent_id: {
                    "skills": cap.skills,
                    "performance_score": cap.performance_score,
                    "availability": cap.availability,
                    "current_load": cap.current_load
                }
                for agent_id, cap in capabilities.items()
            },
            "active_tasks_info": [
                {
                    "id": task.id,
                    "title": task.title,
                    "status": task.status,
                    "assigned_agents": task.assigned_agents,
                    "progress": task.progress
                }
                for task in self.active_tasks.values()
            ]
        }

# Глобальный экземпляр координатора
coordinator = None

def initialize_coordinator(shared_memory: EnhancedSharedMemory) -> AgentCoordinator:
    """Инициализация координатора"""
    global coordinator
    coordinator = AgentCoordinator(shared_memory)
    return coordinator

if __name__ == "__main__":
    # Тестирование системы координации
    async def test_coordination():
        shared_memory = EnhancedSharedMemory()
        coordinator = initialize_coordinator(shared_memory)
        
        # Создаем тестовую задачу
        task = await coordinator.create_coordination_task(
            title="Разработка веб-приложения",
            description="Создать полнофункциональное веб-приложение",
            required_skills=["code_generation", "architecture_design"],
            complexity=TaskComplexity.COMPLEX,
            priority=8
        )
        
        print(f"Создана задача: {task.title}")
        print(f"Назначенные агенты: {task.assigned_agents}")
        
        # Получаем статус координации
        status = coordinator.get_coordination_status()
        print(f"Статус координации: {status}")
    
    # Запуск тестов
    asyncio.run(test_coordination())
