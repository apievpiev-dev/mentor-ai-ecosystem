"""
AI Manager - компонент для создания и управления AI агентами
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from openai import AsyncOpenAI
from models.agent import Agent, AgentType, AgentStatus, AgentCapability
from generators.agent_generators import AgentGeneratorFactory
import logging
import json

logger = logging.getLogger(__name__)


class AIManager:
    """Менеджер AI агентов - создает, управляет и координирует агентов"""
    
    def __init__(self, openai_api_key: str = None):
        self.client = AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None
        self.agents: Dict[str, Agent] = {}
        self.agent_generator_factory = AgentGeneratorFactory()
        self.max_agents = 50  # Максимальное количество активных агентов
        
    async def create_agent_for_task(self, task_analysis: Dict[str, Any]) -> Agent:
        """Создание специализированного агента для задачи"""
        try:
            logger.info(f"Создание агента для задачи категории: {task_analysis.get('category')}")
            
            # Определяем тип агента
            agent_type = AgentType(task_analysis.get('suggested_agent_type', 'general'))
            
            # Получаем генератор для данного типа агента
            generator = self.agent_generator_factory.get_generator(agent_type)
            
            # Создаем агента
            agent = await generator.generate_agent(task_analysis)
            
            # Добавляем агента в пул
            self.agents[agent.id] = agent
            
            logger.info(f"Агент {agent.id} создан успешно")
            return agent
            
        except Exception as e:
            logger.error(f"Ошибка создания агента: {e}")
            # Создаем базового агента в случае ошибки
            return await self._create_fallback_agent(task_analysis)
    
    async def _create_fallback_agent(self, task_analysis: Dict[str, Any]) -> Agent:
        """Создание базового агента в случае ошибки"""
        agent = Agent(
            name=f"Fallback Agent {len(self.agents) + 1}",
            type=AgentType.GENERAL,
            system_prompt=self._get_default_system_prompt(),
            capabilities=[
                AgentCapability(name="general_reasoning", level=0.7, description="Общие рассуждения"),
                AgentCapability(name="text_processing", level=0.6, description="Обработка текста")
            ],
            config={
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 1000
            }
        )
        
        self.agents[agent.id] = agent
        return agent
    
    def _get_default_system_prompt(self) -> str:
        """Базовый системный промпт для агентов"""
        return """Ты - универсальный AI агент, способный решать различные задачи. 
        Твоя цель - качественно выполнять поставленные задачи, предоставляя полезные и точные результаты.
        Всегда анализируй задачу перед выполнением и предоставляй структурированный ответ."""
    
    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Получение агента по ID"""
        return self.agents.get(agent_id)
    
    async def get_active_agents(self) -> List[Agent]:
        """Получение списка активных агентов"""
        return [agent for agent in self.agents.values() 
                if agent.status in [AgentStatus.IDLE, AgentStatus.WORKING, AgentStatus.BUSY]]
    
    async def stop_agent(self, agent_id: str) -> bool:
        """Остановка агента"""
        agent = self.agents.get(agent_id)
        if not agent:
            return False
        
        agent.status = AgentStatus.STOPPED
        agent.current_task_id = None
        agent.last_active = datetime.now()
        
        logger.info(f"Агент {agent_id} остановлен")
        return True
    
    async def update_agent_status(self, agent_id: str, status: AgentStatus, task_id: str = None):
        """Обновление статуса агента"""
        agent = self.agents.get(agent_id)
        if not agent:
            return
        
        agent.status = status
        agent.current_task_id = task_id
        agent.last_active = datetime.now()
        
        logger.debug(f"Статус агента {agent_id} изменен на {status}")
    
    async def complete_task(self, agent_id: str, task_id: str, quality_score: float = None):
        """Отметка завершения задачи агентом"""
        agent = self.agents.get(agent_id)
        if not agent:
            return
        
        agent.tasks_completed += 1
        agent.task_history.append(task_id)
        agent.current_task_id = None
        agent.status = AgentStatus.IDLE
        agent.last_active = datetime.now()
        
        if quality_score is not None:
            # Обновляем средний балл качества
            total_score = agent.average_quality_score * (agent.tasks_completed - 1)
            agent.average_quality_score = (total_score + quality_score) / agent.tasks_completed
        
        logger.info(f"Агент {agent_id} завершил задачу {task_id}")
    
    async def fail_task(self, agent_id: str, task_id: str, error_message: str = None):
        """Отметка неудачного выполнения задачи"""
        agent = self.agents.get(agent_id)
        if not agent:
            return
        
        agent.tasks_failed += 1
        agent.current_task_id = None
        agent.status = AgentStatus.IDLE
        agent.last_active = datetime.now()
        
        logger.warning(f"Агент {agent_id} не смог выполнить задачу {task_id}: {error_message}")
    
    async def get_agent_performance(self, agent_id: str) -> Dict[str, Any]:
        """Получение статистики производительности агента"""
        agent = self.agents.get(agent_id)
        if not agent:
            return {}
        
        total_tasks = agent.tasks_completed + agent.tasks_failed
        success_rate = agent.tasks_completed / total_tasks if total_tasks > 0 else 0
        
        return {
            "agent_id": agent_id,
            "tasks_completed": agent.tasks_completed,
            "tasks_failed": agent.tasks_failed,
            "success_rate": success_rate,
            "average_quality_score": agent.average_quality_score,
            "total_execution_time": agent.total_execution_time,
            "average_execution_time": agent.total_execution_time / agent.tasks_completed if agent.tasks_completed > 0 else 0,
            "status": agent.status,
            "last_active": agent.last_active
        }
    
    async def cleanup_idle_agents(self, max_idle_minutes: int = 30):
        """Очистка неактивных агентов"""
        current_time = datetime.now()
        agents_to_remove = []
        
        for agent_id, agent in self.agents.items():
            if agent.status == AgentStatus.IDLE:
                idle_time = (current_time - agent.last_active).total_seconds() / 60
                if idle_time > max_idle_minutes:
                    agents_to_remove.append(agent_id)
        
        for agent_id in agents_to_remove:
            del self.agents[agent_id]
            logger.info(f"Удален неактивный агент {agent_id}")
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Получение общей статистики системы"""
        active_agents = await self.get_active_agents()
        
        total_tasks_completed = sum(agent.tasks_completed for agent in self.agents.values())
        total_tasks_failed = sum(agent.tasks_failed for agent in self.agents.values())
        
        total_tasks = total_tasks_completed + total_tasks_failed
        overall_success_rate = total_tasks_completed / total_tasks if total_tasks > 0 else 0
        
        avg_quality = sum(agent.average_quality_score for agent in self.agents.values()) / len(self.agents) if self.agents else 0
        
        return {
            "total_agents": len(self.agents),
            "active_agents": len(active_agents),
            "total_tasks_completed": total_tasks_completed,
            "total_tasks_failed": total_tasks_failed,
            "overall_success_rate": overall_success_rate,
            "average_quality_score": avg_quality,
            "agents_by_type": self._get_agents_by_type(),
            "agents_by_status": self._get_agents_by_status()
        }
    
    def _get_agents_by_type(self) -> Dict[str, int]:
        """Статистика агентов по типам"""
        type_counts = {}
        for agent in self.agents.values():
            agent_type = agent.type if isinstance(agent.type, str) else agent.type.value
            type_counts[agent_type] = type_counts.get(agent_type, 0) + 1
        return type_counts
    
    def _get_agents_by_status(self) -> Dict[str, int]:
        """Статистика агентов по статусам"""
        status_counts = {}
        for agent in self.agents.values():
            status = agent.status if isinstance(agent.status, str) else agent.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        return status_counts
    
    async def optimize_agent_pool(self):
        """Оптимизация пула агентов"""
        # Удаляем неактивных агентов
        await self.cleanup_idle_agents()
        
        # Если агентов слишком много, удаляем наименее эффективных
        if len(self.agents) > self.max_agents:
            await self._remove_least_efficient_agents()
    
    async def _remove_least_efficient_agents(self):
        """Удаление наименее эффективных агентов"""
        # Сортируем агентов по эффективности (количество выполненных задач * средний балл качества)
        sorted_agents = sorted(
            self.agents.values(),
            key=lambda a: a.tasks_completed * a.average_quality_score
        )
        
        # Удаляем 20% наименее эффективных агентов
        agents_to_remove = len(self.agents) - int(self.max_agents * 0.8)
        
        for i in range(agents_to_remove):
            agent = sorted_agents[i]
            if agent.status == AgentStatus.IDLE:  # Удаляем только неактивных
                del self.agents[agent.id]
                logger.info(f"Удален неэффективный агент {agent.id}")
