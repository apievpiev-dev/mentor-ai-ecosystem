#!/usr/bin/env python3
"""
Multi-Agent Autonomous JARVIS System
Многоагентная автономная система JARVIS с координацией специализированных агентов
"""

import os
import sys
import json
import time
import asyncio
import threading
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from abc import ABC, abstractmethod

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/multi_agent_jarvis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Типы агентов"""
    COORDINATOR = "coordinator"
    VISUAL_INTELLIGENCE = "visual_intelligence"
    TASK_EXECUTOR = "task_executor"
    MONITORING = "monitoring"
    SELF_IMPROVEMENT = "self_improvement"
    COMMUNICATION = "communication"
    SECURITY = "security"

class MessageType(Enum):
    """Типы сообщений между агентами"""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    STATUS_UPDATE = "status_update"
    COORDINATION = "coordination"
    ALERT = "alert"
    DATA_SHARING = "data_sharing"

@dataclass
class AgentMessage:
    """Сообщение между агентами"""
    id: str
    sender_id: str
    recipient_id: Optional[str]  # None для broadcast
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: str
    priority: int = 5
    requires_response: bool = False

@dataclass
class AgentCapability:
    """Способность агента"""
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    performance_score: float = 0.0

@dataclass
class AgentStatus:
    """Статус агента"""
    agent_id: str
    agent_type: AgentType
    status: str  # active, busy, idle, error
    last_activity: str
    tasks_completed: int
    performance_score: float
    capabilities: List[AgentCapability]
    current_task: Optional[str] = None

class MessageBus:
    """Шина сообщений для межагентного взаимодействия"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[callable]] = {}
        self.message_history: List[AgentMessage] = []
        self.lock = threading.Lock()
    
    def subscribe(self, agent_id: str, callback: callable):
        """Подписка агента на сообщения"""
        with self.lock:
            if agent_id not in self.subscribers:
                self.subscribers[agent_id] = []
            self.subscribers[agent_id].append(callback)
    
    def publish(self, message: AgentMessage):
        """Отправка сообщения"""
        with self.lock:
            self.message_history.append(message)
            
            # Ограничиваем историю
            if len(self.message_history) > 1000:
                self.message_history = self.message_history[-500:]
            
            # Доставляем сообщение
            if message.recipient_id:
                # Личное сообщение
                if message.recipient_id in self.subscribers:
                    for callback in self.subscribers[message.recipient_id]:
                        try:
                            callback(message)
                        except Exception as e:
                            logger.error(f"Ошибка доставки сообщения {message.id}: {e}")
            else:
                # Broadcast сообщение
                for agent_id, callbacks in self.subscribers.items():
                    if agent_id != message.sender_id:  # Не отправляем отправителю
                        for callback in callbacks:
                            try:
                                callback(message)
                            except Exception as e:
                                logger.error(f"Ошибка broadcast {message.id} для {agent_id}: {e}")
    
    def get_message_history(self, agent_id: Optional[str] = None) -> List[AgentMessage]:
        """Получение истории сообщений"""
        with self.lock:
            if agent_id:
                return [msg for msg in self.message_history 
                       if msg.sender_id == agent_id or msg.recipient_id == agent_id]
            return self.message_history.copy()

class BaseAgent(ABC):
    """Базовый класс агента"""
    
    def __init__(self, agent_id: str, agent_type: AgentType, message_bus: MessageBus):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.message_bus = message_bus
        self.status = AgentStatus(
            agent_id=agent_id,
            agent_type=agent_type,
            status="idle",
            last_activity=datetime.now().isoformat(),
            tasks_completed=0,
            performance_score=1.0,
            capabilities=self.get_capabilities()
        )
        self.running = True
        self.task_queue = []
        
        # Подписываемся на сообщения
        self.message_bus.subscribe(agent_id, self.handle_message)
        
        # Запускаем основной цикл агента
        self.start_agent_loop()
        
        logger.info(f"🤖 Агент {self.agent_id} ({self.agent_type.value}) инициализирован")
    
    @abstractmethod
    def get_capabilities(self) -> List[AgentCapability]:
        """Получение списка способностей агента"""
        pass
    
    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка задачи"""
        pass
    
    def start_agent_loop(self):
        """Запуск основного цикла агента"""
        def agent_loop():
            while self.running:
                try:
                    # Обрабатываем задачи
                    if self.task_queue:
                        task = self.task_queue.pop(0)
                        asyncio.run(self.execute_task(task))
                    
                    # Обновляем статус
                    self.update_status()
                    
                    # Отправляем периодические обновления статуса
                    if int(time.time()) % 30 == 0:  # Каждые 30 секунд
                        self.send_status_update()
                    
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Ошибка в цикле агента {self.agent_id}: {e}")
                    time.sleep(5)
        
        thread = threading.Thread(target=agent_loop, daemon=True)
        thread.start()
    
    async def execute_task(self, task: Dict[str, Any]):
        """Выполнение задачи"""
        try:
            self.status.status = "busy"
            self.status.current_task = task.get("id", "unknown")
            
            # Обрабатываем задачу
            result = await self.process_task(task)
            
            # Отправляем результат
            if task.get("sender_id"):
                response = AgentMessage(
                    id=str(uuid.uuid4()),
                    sender_id=self.agent_id,
                    recipient_id=task["sender_id"],
                    message_type=MessageType.TASK_RESPONSE,
                    content={
                        "task_id": task.get("id"),
                        "result": result,
                        "status": "completed"
                    },
                    timestamp=datetime.now().isoformat()
                )
                self.message_bus.publish(response)
            
            self.status.tasks_completed += 1
            self.status.status = "idle"
            self.status.current_task = None
            
            logger.info(f"✅ Агент {self.agent_id} завершил задачу {task.get('id')}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка выполнения задачи {task.get('id')} агентом {self.agent_id}: {e}")
            self.status.status = "error"
    
    def handle_message(self, message: AgentMessage):
        """Обработка входящего сообщения"""
        try:
            if message.message_type == MessageType.TASK_REQUEST:
                self.task_queue.append(message.content)
            elif message.message_type == MessageType.COORDINATION:
                self.handle_coordination_message(message)
            elif message.message_type == MessageType.ALERT:
                self.handle_alert_message(message)
            
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения {message.id} агентом {self.agent_id}: {e}")
    
    def handle_coordination_message(self, message: AgentMessage):
        """Обработка координационного сообщения"""
        content = message.content
        
        if content.get("action") == "capability_request":
            # Отправляем информацию о способностях
            response = AgentMessage(
                id=str(uuid.uuid4()),
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type=MessageType.COORDINATION,
                content={
                    "action": "capability_response",
                    "capabilities": [asdict(cap) for cap in self.status.capabilities],
                    "status": asdict(self.status)
                },
                timestamp=datetime.now().isoformat()
            )
            self.message_bus.publish(response)
    
    def handle_alert_message(self, message: AgentMessage):
        """Обработка алертов"""
        logger.warning(f"🚨 Алерт для агента {self.agent_id}: {message.content.get('message', 'Unknown alert')}")
    
    def send_status_update(self):
        """Отправка обновления статуса"""
        message = AgentMessage(
            id=str(uuid.uuid4()),
            sender_id=self.agent_id,
            recipient_id=None,  # Broadcast
            message_type=MessageType.STATUS_UPDATE,
            content=asdict(self.status),
            timestamp=datetime.now().isoformat()
        )
        self.message_bus.publish(message)
    
    def update_status(self):
        """Обновление статуса агента"""
        self.status.last_activity = datetime.now().isoformat()
        
        # Обновляем производительность на основе выполненных задач
        if self.status.tasks_completed > 0:
            self.status.performance_score = min(1.0, 0.5 + (self.status.tasks_completed * 0.01))

class CoordinatorAgent(BaseAgent):
    """Агент-координатор"""
    
    def __init__(self, message_bus: MessageBus):
        self.agents_registry: Dict[str, AgentStatus] = {}
        self.task_assignments: Dict[str, str] = {}  # task_id -> agent_id
        super().__init__("coordinator", AgentType.COORDINATOR, message_bus)
    
    def get_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="task_coordination",
                description="Координация задач между агентами",
                input_types=["task_request", "agent_status"],
                output_types=["task_assignment", "coordination_command"]
            ),
            AgentCapability(
                name="agent_management",
                description="Управление агентами",
                input_types=["agent_registration", "status_update"],
                output_types=["agent_command", "capability_request"]
            )
        ]
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка задачи координации"""
        task_type = task.get("type", "unknown")
        
        if task_type == "coordinate_task":
            return await self.coordinate_task(task)
        elif task_type == "manage_agents":
            return await self.manage_agents(task)
        elif task_type == "optimize_performance":
            return await self.optimize_performance(task)
        
        return {"status": "unknown_task_type", "type": task_type}
    
    async def coordinate_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Координация выполнения задачи"""
        try:
            target_task = task.get("target_task", {})
            required_capabilities = task.get("required_capabilities", [])
            
            # Находим подходящего агента
            best_agent = self.find_best_agent(required_capabilities)
            
            if best_agent:
                # Отправляем задачу агенту
                task_message = AgentMessage(
                    id=str(uuid.uuid4()),
                    sender_id=self.agent_id,
                    recipient_id=best_agent,
                    message_type=MessageType.TASK_REQUEST,
                    content=target_task,
                    timestamp=datetime.now().isoformat(),
                    priority=task.get("priority", 5)
                )
                
                self.message_bus.publish(task_message)
                self.task_assignments[task_message.id] = best_agent
                
                return {
                    "status": "assigned",
                    "agent_id": best_agent,
                    "task_id": task_message.id
                }
            else:
                return {
                    "status": "no_suitable_agent",
                    "required_capabilities": required_capabilities
                }
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def find_best_agent(self, required_capabilities: List[str]) -> Optional[str]:
        """Поиск лучшего агента для задачи"""
        best_agent = None
        best_score = 0.0
        
        for agent_id, agent_status in self.agents_registry.items():
            if agent_status.status in ["idle", "active"]:
                # Проверяем соответствие способностей
                agent_capabilities = [cap.name for cap in agent_status.capabilities]
                matches = len(set(required_capabilities) & set(agent_capabilities))
                
                if matches > 0:
                    # Рассчитываем оценку
                    score = matches / len(required_capabilities) * agent_status.performance_score
                    
                    if score > best_score:
                        best_score = score
                        best_agent = agent_id
        
        return best_agent
    
    async def manage_agents(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Управление агентами"""
        action = task.get("action", "status")
        
        if action == "status":
            return {
                "agents_count": len(self.agents_registry),
                "agents": {aid: asdict(status) for aid, status in self.agents_registry.items()}
            }
        elif action == "restart_agent":
            agent_id = task.get("agent_id")
            if agent_id in self.agents_registry:
                # Отправляем команду перезапуска
                restart_message = AgentMessage(
                    id=str(uuid.uuid4()),
                    sender_id=self.agent_id,
                    recipient_id=agent_id,
                    message_type=MessageType.COORDINATION,
                    content={"action": "restart"},
                    timestamp=datetime.now().isoformat()
                )
                self.message_bus.publish(restart_message)
                return {"status": "restart_sent", "agent_id": agent_id}
        
        return {"status": "unknown_action", "action": action}
    
    async def optimize_performance(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Оптимизация производительности системы"""
        try:
            # Анализируем производительность агентов
            low_performance_agents = [
                agent_id for agent_id, status in self.agents_registry.items()
                if status.performance_score < 0.7
            ]
            
            # Перераспределяем нагрузку
            rebalanced_tasks = 0
            for agent_id in low_performance_agents:
                # Отправляем команду оптимизации
                optimize_message = AgentMessage(
                    id=str(uuid.uuid4()),
                    sender_id=self.agent_id,
                    recipient_id=agent_id,
                    message_type=MessageType.COORDINATION,
                    content={"action": "optimize_performance"},
                    timestamp=datetime.now().isoformat()
                )
                self.message_bus.publish(optimize_message)
                rebalanced_tasks += 1
            
            return {
                "status": "optimization_sent",
                "agents_optimized": rebalanced_tasks,
                "low_performance_agents": low_performance_agents
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def handle_message(self, message: AgentMessage):
        """Обработка сообщений для координатора"""
        super().handle_message(message)
        
        # Обновляем реестр агентов при получении статусов
        if message.message_type == MessageType.STATUS_UPDATE:
            agent_status_data = message.content
            agent_status = AgentStatus(**agent_status_data)
            self.agents_registry[message.sender_id] = agent_status

class VisualIntelligenceAgent(BaseAgent):
    """Агент визуального интеллекта"""
    
    def __init__(self, message_bus: MessageBus):
        super().__init__("visual_intelligence", AgentType.VISUAL_INTELLIGENCE, message_bus)
        self.analysis_history = []
    
    def get_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="screenshot_analysis",
                description="Анализ скриншотов интерфейса",
                input_types=["image_data", "ui_state"],
                output_types=["analysis_result", "ui_issues"]
            ),
            AgentCapability(
                name="ui_optimization",
                description="Оптимизация пользовательского интерфейса",
                input_types=["ui_issues", "user_feedback"],
                output_types=["ui_improvements", "optimization_plan"]
            )
        ]
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка задачи визуального анализа"""
        task_type = task.get("type", "unknown")
        
        if task_type == "analyze_interface":
            return await self.analyze_interface(task)
        elif task_type == "optimize_ui":
            return await self.optimize_ui(task)
        elif task_type == "detect_issues":
            return await self.detect_issues(task)
        
        return {"status": "unknown_task_type", "type": task_type}
    
    async def analyze_interface(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ интерфейса"""
        try:
            # Симулируем анализ интерфейса
            interface_data = task.get("interface_data", {})
            
            analysis_result = {
                "timestamp": datetime.now().isoformat(),
                "elements_detected": 5,
                "issues_found": [
                    {
                        "type": "accessibility",
                        "severity": "medium",
                        "description": "Недостаточный контраст текста",
                        "location": {"x": 100, "y": 200}
                    }
                ],
                "suggestions": [
                    "Увеличить контрастность текста",
                    "Добавить альтернативный текст для изображений",
                    "Улучшить навигацию с клавиатуры"
                ],
                "ux_score": 0.85,
                "performance_impact": {
                    "loading_time": 1.2,
                    "responsiveness": 0.9
                }
            }
            
            self.analysis_history.append(analysis_result)
            
            # Если найдены критические проблемы, отправляем алерт
            critical_issues = [i for i in analysis_result["issues_found"] if i["severity"] == "high"]
            if critical_issues:
                alert = AgentMessage(
                    id=str(uuid.uuid4()),
                    sender_id=self.agent_id,
                    recipient_id=None,  # Broadcast
                    message_type=MessageType.ALERT,
                    content={
                        "type": "critical_ui_issues",
                        "issues": critical_issues,
                        "requires_immediate_action": True
                    },
                    timestamp=datetime.now().isoformat(),
                    priority=9
                )
                self.message_bus.publish(alert)
            
            return {
                "status": "completed",
                "analysis": analysis_result
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def optimize_ui(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Оптимизация UI"""
        try:
            issues = task.get("issues", [])
            
            optimizations = []
            for issue in issues:
                if issue["type"] == "accessibility":
                    optimizations.append({
                        "type": "contrast_improvement",
                        "action": "Увеличить контрастность до 4.5:1",
                        "priority": "high"
                    })
                elif issue["type"] == "performance":
                    optimizations.append({
                        "type": "resource_optimization",
                        "action": "Сжать изображения и CSS",
                        "priority": "medium"
                    })
            
            return {
                "status": "completed",
                "optimizations": optimizations,
                "estimated_improvement": 0.15
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def detect_issues(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Обнаружение проблем"""
        try:
            # Анализируем последние результаты
            recent_analyses = self.analysis_history[-5:] if self.analysis_history else []
            
            patterns = []
            if len(recent_analyses) >= 3:
                # Ищем повторяющиеся проблемы
                all_issues = []
                for analysis in recent_analyses:
                    all_issues.extend(analysis.get("issues_found", []))
                
                issue_types = {}
                for issue in all_issues:
                    issue_type = issue["type"]
                    issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
                
                for issue_type, count in issue_types.items():
                    if count >= 2:
                        patterns.append({
                            "type": issue_type,
                            "frequency": count,
                            "recommendation": f"Системная проблема с {issue_type}, требует внимания"
                        })
            
            return {
                "status": "completed",
                "patterns_detected": patterns,
                "analysis_count": len(recent_analyses)
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}

class TaskExecutorAgent(BaseAgent):
    """Агент выполнения задач"""
    
    def __init__(self, message_bus: MessageBus):
        super().__init__("task_executor", AgentType.TASK_EXECUTOR, message_bus)
    
    def get_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="general_task_execution",
                description="Выполнение общих задач",
                input_types=["task_definition", "parameters"],
                output_types=["task_result", "execution_log"]
            ),
            AgentCapability(
                name="automation_tasks",
                description="Автоматизация процессов",
                input_types=["automation_script", "schedule"],
                output_types=["automation_result", "status_report"]
            )
        ]
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка задачи"""
        task_type = task.get("type", "unknown")
        
        if task_type == "execute_script":
            return await self.execute_script(task)
        elif task_type == "data_processing":
            return await self.process_data(task)
        elif task_type == "file_operation":
            return await self.file_operation(task)
        
        return {"status": "unknown_task_type", "type": task_type}
    
    async def execute_script(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение скрипта"""
        try:
            script_content = task.get("script", "")
            parameters = task.get("parameters", {})
            
            # Симулируем выполнение скрипта
            result = {
                "status": "completed",
                "output": f"Script executed with parameters: {parameters}",
                "execution_time": 0.5,
                "exit_code": 0
            }
            
            return result
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def process_data(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка данных"""
        try:
            data = task.get("data", [])
            operation = task.get("operation", "analyze")
            
            if operation == "analyze":
                result = {
                    "status": "completed",
                    "analysis": {
                        "records_processed": len(data) if isinstance(data, list) else 1,
                        "processing_time": 0.3,
                        "insights": ["Data processed successfully"]
                    }
                }
            elif operation == "transform":
                result = {
                    "status": "completed",
                    "transformed_data": f"Transformed {len(data) if isinstance(data, list) else 1} records",
                    "transformation_rules_applied": 3
                }
            else:
                result = {"status": "unknown_operation", "operation": operation}
            
            return result
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def file_operation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Операции с файлами"""
        try:
            operation = task.get("operation", "read")
            file_path = task.get("file_path", "")
            
            if operation == "read":
                result = {
                    "status": "completed",
                    "content": f"Content of {file_path}",
                    "file_size": 1024
                }
            elif operation == "write":
                content = task.get("content", "")
                result = {
                    "status": "completed",
                    "bytes_written": len(content),
                    "file_path": file_path
                }
            elif operation == "delete":
                result = {
                    "status": "completed",
                    "deleted": True,
                    "file_path": file_path
                }
            else:
                result = {"status": "unknown_operation", "operation": operation}
            
            return result
            
        except Exception as e:
            return {"status": "error", "error": str(e)}

class MultiAgentJarvis:
    """Главная система многоагентного JARVIS"""
    
    def __init__(self):
        self.message_bus = MessageBus()
        self.agents: Dict[str, BaseAgent] = {}
        self.system_stats = {
            "start_time": time.time(),
            "messages_processed": 0,
            "tasks_completed": 0,
            "agents_active": 0
        }
        
        # Инициализируем агентов
        self.initialize_agents()
        
        # Запускаем систему мониторинга
        self.start_monitoring()
        
        logger.info("🚀 Multi-Agent JARVIS система инициализирована")
    
    def initialize_agents(self):
        """Инициализация агентов"""
        try:
            # Создаем базовых агентов
            self.agents["coordinator"] = CoordinatorAgent(self.message_bus)
            self.agents["visual_intelligence"] = VisualIntelligenceAgent(self.message_bus)
            self.agents["task_executor"] = TaskExecutorAgent(self.message_bus)
            
            logger.info(f"✅ Инициализировано {len(self.agents)} агентов")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации агентов: {e}")
    
    def start_monitoring(self):
        """Запуск системы мониторинга"""
        def monitoring_loop():
            while True:
                try:
                    # Обновляем статистику
                    self.update_system_stats()
                    
                    # Проверяем здоровье агентов
                    self.check_agents_health()
                    
                    # Логируем статистику каждые 60 секунд
                    if int(time.time()) % 60 == 0:
                        self.log_system_stats()
                    
                    time.sleep(10)
                    
                except Exception as e:
                    logger.error(f"Ошибка мониторинга: {e}")
                    time.sleep(30)
        
        thread = threading.Thread(target=monitoring_loop, daemon=True)
        thread.start()
        logger.info("📊 Система мониторинга запущена")
    
    def update_system_stats(self):
        """Обновление статистики системы"""
        try:
            self.system_stats["messages_processed"] = len(self.message_bus.message_history)
            self.system_stats["agents_active"] = len([
                agent for agent in self.agents.values() 
                if agent.status.status in ["active", "busy", "idle"]
            ])
            self.system_stats["tasks_completed"] = sum(
                agent.status.tasks_completed for agent in self.agents.values()
            )
            
        except Exception as e:
            logger.error(f"Ошибка обновления статистики: {e}")
    
    def check_agents_health(self):
        """Проверка здоровья агентов"""
        try:
            for agent_id, agent in self.agents.items():
                # Проверяем последнюю активность
                last_activity = datetime.fromisoformat(agent.status.last_activity)
                time_since_activity = (datetime.now() - last_activity).total_seconds()
                
                if time_since_activity > 300:  # 5 минут без активности
                    logger.warning(f"⚠️ Агент {agent_id} неактивен {time_since_activity:.0f} секунд")
                    
                    # Отправляем ping
                    ping_message = AgentMessage(
                        id=str(uuid.uuid4()),
                        sender_id="system",
                        recipient_id=agent_id,
                        message_type=MessageType.COORDINATION,
                        content={"action": "ping"},
                        timestamp=datetime.now().isoformat()
                    )
                    self.message_bus.publish(ping_message)
                
        except Exception as e:
            logger.error(f"Ошибка проверки здоровья агентов: {e}")
    
    def log_system_stats(self):
        """Логирование статистики системы"""
        uptime = time.time() - self.system_stats["start_time"]
        logger.info(
            f"📊 Статистика системы: "
            f"Время работы: {uptime/3600:.1f}ч, "
            f"Агенты: {self.system_stats['agents_active']}, "
            f"Сообщения: {self.system_stats['messages_processed']}, "
            f"Задачи: {self.system_stats['tasks_completed']}"
        )
    
    async def submit_task(self, task_type: str, parameters: Dict[str, Any], priority: int = 5) -> str:
        """Отправка задачи в систему"""
        try:
            # Создаем задачу координации
            coordination_task = {
                "id": str(uuid.uuid4()),
                "type": "coordinate_task",
                "target_task": {
                    "id": str(uuid.uuid4()),
                    "type": task_type,
                    "parameters": parameters,
                    "priority": priority
                },
                "required_capabilities": self.get_required_capabilities(task_type),
                "sender_id": "system"
            }
            
            # Отправляем координатору
            message = AgentMessage(
                id=str(uuid.uuid4()),
                sender_id="system",
                recipient_id="coordinator",
                message_type=MessageType.TASK_REQUEST,
                content=coordination_task,
                timestamp=datetime.now().isoformat(),
                priority=priority
            )
            
            self.message_bus.publish(message)
            
            logger.info(f"📤 Задача {task_type} отправлена в систему")
            return coordination_task["target_task"]["id"]
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки задачи: {e}")
            return ""
    
    def get_required_capabilities(self, task_type: str) -> List[str]:
        """Получение требуемых способностей для типа задачи"""
        capability_map = {
            "analyze_interface": ["screenshot_analysis", "ui_optimization"],
            "execute_script": ["general_task_execution"],
            "data_processing": ["general_task_execution"],
            "optimize_ui": ["ui_optimization", "screenshot_analysis"],
            "file_operation": ["general_task_execution"]
        }
        
        return capability_map.get(task_type, ["general_task_execution"])
    
    def get_system_status(self) -> Dict[str, Any]:
        """Получение статуса системы"""
        return {
            "system_stats": self.system_stats,
            "agents": {
                agent_id: asdict(agent.status) 
                for agent_id, agent in self.agents.items()
            },
            "message_bus": {
                "total_messages": len(self.message_bus.message_history),
                "subscribers": len(self.message_bus.subscribers)
            },
            "timestamp": datetime.now().isoformat()
        }

async def main():
    """Главная функция"""
    try:
        # Создаем многоагентную систему
        jarvis = MultiAgentJarvis()
        
        logger.info("🚀 Multi-Agent JARVIS система готова!")
        
        # Демонстрируем работу системы
        await demo_multi_agent_system(jarvis)
        
        # Ожидаем
        while True:
            await asyncio.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("🛑 Остановка системы")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

async def demo_multi_agent_system(jarvis: MultiAgentJarvis):
    """Демонстрация работы многоагентной системы"""
    try:
        logger.info("🎯 Начало демонстрации многоагентной системы")
        
        # Отправляем различные задачи
        tasks = [
            ("analyze_interface", {"interface_data": {"url": "localhost:8080"}}),
            ("execute_script", {"script": "echo 'Hello from agent'", "parameters": {"env": "production"}}),
            ("data_processing", {"data": [1, 2, 3, 4, 5], "operation": "analyze"}),
            ("optimize_ui", {"issues": [{"type": "accessibility", "severity": "medium"}]})
        ]
        
        task_ids = []
        for task_type, parameters in tasks:
            task_id = await jarvis.submit_task(task_type, parameters, priority=7)
            task_ids.append(task_id)
            await asyncio.sleep(2)
        
        # Ждем выполнения задач
        logger.info("⏳ Ожидание выполнения задач...")
        await asyncio.sleep(10)
        
        # Показываем статус системы
        status = jarvis.get_system_status()
        logger.info(f"📊 Статус системы: {json.dumps(status, indent=2, ensure_ascii=False)}")
        
        logger.info("✅ Демонстрация завершена")
        
    except Exception as e:
        logger.error(f"❌ Ошибка демонстрации: {e}")

if __name__ == "__main__":
    asyncio.run(main())