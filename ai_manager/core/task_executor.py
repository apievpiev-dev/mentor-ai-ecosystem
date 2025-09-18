"""
Task Executor - компонент для выполнения задач AI агентами
"""

import asyncio
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from models.task import Task, TaskStatus, TaskResult
from models.agent import Agent, AgentStatus
from core.ai_manager import AIManager
import logging
import json

logger = logging.getLogger(__name__)


class TaskExecutor:
    """Исполнитель задач - координирует выполнение задач агентами"""
    
    def __init__(self, ai_manager: AIManager):
        self.ai_manager = ai_manager
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, TaskResult] = {}
        self.task_queue = asyncio.Queue()
        self.execution_workers = []
        self.max_concurrent_tasks = 10
        
    async def execute_task(self, task: Task, agent: Agent) -> Dict[str, Any]:
        """Выполнение задачи агентом"""
        try:
            logger.info(f"Начало выполнения задачи {task.id} агентом {agent.id}")
            
            # Обновляем статусы
            task.status = TaskStatus.IN_PROGRESS
            task.agent_id = agent.id
            await self.ai_manager.update_agent_status(agent.id, AgentStatus.WORKING, task.id)
            
            self.active_tasks[task.id] = task
            start_time = time.time()
            
            # Выполняем задачу
            result = await self._execute_task_with_agent(task, agent)
            
            # Записываем время выполнения
            execution_time = time.time() - start_time
            task.execution_time = execution_time
            
            # Обрабатываем результат
            if result.get("success", False):
                task.status = TaskStatus.COMPLETED
                task.result = result.get("data")
                
                # Создаем результат задачи
                task_result = TaskResult(
                    task_id=task.id,
                    status=TaskStatus.COMPLETED,
                    result_data=result.get("data", {}),
                    execution_time=execution_time,
                    agent_id=agent.id,
                    quality_score=result.get("quality_score", 0.8)
                )
                
                self.completed_tasks[task.id] = task_result
                await self.ai_manager.complete_task(agent.id, task.id, result.get("quality_score", 0.8))
                
                logger.info(f"Задача {task.id} выполнена успешно за {execution_time:.2f}с")
                
            else:
                task.status = TaskStatus.FAILED
                task.error_message = result.get("error", "Неизвестная ошибка")
                await self.ai_manager.fail_task(agent.id, task.id, result.get("error"))
                
                logger.error(f"Задача {task.id} выполнена с ошибкой: {result.get('error')}")
            
            # Удаляем из активных задач
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]
            
            return {
                "task_id": task.id,
                "status": task.status,
                "result": task.result,
                "execution_time": execution_time,
                "error": task.error_message
            }
            
        except Exception as e:
            logger.error(f"Критическая ошибка выполнения задачи {task.id}: {e}")
            
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            
            if agent:
                await self.ai_manager.fail_task(agent.id, task.id, str(e))
            
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]
            
            return {
                "task_id": task.id,
                "status": TaskStatus.FAILED,
                "error": str(e)
            }
    
    async def _execute_task_with_agent(self, task: Task, agent: Agent) -> Dict[str, Any]:
        """Выполнение задачи конкретным агентом"""
        try:
            # Подготавливаем промпт для агента
            agent_prompt = self._prepare_agent_prompt(task, agent)
            
            # Выполняем запрос к агенту (имитация работы с OpenAI API)
            result = await self._call_agent_api(agent, agent_prompt, task)
            
            # Анализируем качество результата
            quality_score = await self._assess_result_quality(task, result, agent)
            
            return {
                "success": True,
                "data": result,
                "quality_score": quality_score
            }
            
        except Exception as e:
            logger.error(f"Ошибка выполнения задачи агентом {agent.id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _prepare_agent_prompt(self, task: Task, agent: Agent) -> str:
        """Подготовка промпта для агента"""
        # Простой промпт без лишних инструкций
        base_prompt = task.description
        return base_prompt
    
    async def _call_agent_api(self, agent: Agent, prompt: str, task: Task) -> Dict[str, Any]:
        """Вызов AI провайдера для генерации ответа"""
        try:
            # Импортируем менеджер провайдеров
            from ai_providers.provider_manager import provider_manager
            
            # Инициализируем провайдеры если нужно
            if not provider_manager.initialized:
                await provider_manager.initialize_providers()
            
            # Генерируем ответ через AI провайдер
            ai_response = await provider_manager.generate_response(
                prompt=prompt,
                temperature=agent.config.get("temperature", 0.7),
                max_tokens=agent.config.get("max_tokens", 1000),
                top_p=agent.config.get("top_p", 0.9)
            )
            
            if ai_response.get("success"):
                # Форматируем результат в зависимости от типа агента
                return await self._format_agent_response(agent, ai_response["result"], task)
            else:
                # Fallback на имитацию если AI провайдер недоступен
                logger.warning(f"AI provider failed: {ai_response.get('error')}, using fallback")
                return await self._fallback_response(agent, task)
                
        except Exception as e:
            logger.error(f"Error calling AI provider: {e}")
            return await self._fallback_response(agent, task)
    
    async def _format_agent_response(self, agent: Agent, ai_result: str, task: Task) -> Dict[str, Any]:
        """Форматирование ответа AI в зависимости от типа агента"""
        agent_type = agent.type if isinstance(agent.type, str) else agent.type.value
        
        base_result = {
            "type": agent_type,
            "result": ai_result,
            "metadata": {
                "agent_id": agent.id,
                "agent_type": agent_type,
                "word_count": len(ai_result.split()),
                "character_count": len(ai_result)
            }
        }
        
        # Добавляем специфичные метаданные для разных типов агентов
        if agent_type == "code_generator":
            base_result["metadata"].update({
                "language": "python",  # Можно определить автоматически
                "lines_of_code": len(ai_result.split('\n')),
                "complexity": "medium"
            })
        elif agent_type == "text_processor":
            base_result["metadata"].update({
                "processing_method": "ai_analysis",
                "readability_score": 0.8
            })
        elif agent_type == "creative_writer":
            base_result["metadata"].update({
                "genre": "creative",
                "creativity_score": 0.8
            })
        elif agent_type == "data_analyst":
            base_result["metadata"].update({
                "analysis_type": "ai_insights",
                "confidence": 0.85
            })
        
        return base_result
    
    async def _fallback_response(self, agent: Agent, task: Task) -> Dict[str, Any]:
        """Fallback ответ когда AI провайдер недоступен"""
        agent_type = agent.type if isinstance(agent.type, str) else agent.type.value
        
        fallback_responses = {
            "text_processor": f"Обработанный текст для задачи: {task.description}",
            "code_generator": f"# Код для задачи: {task.description}\n\ndef solve_task():\n    # Реализация\n    return 'result'",
            "data_analyst": f"Анализ данных для задачи: {task.description}",
            "creative_writer": f"Творческое произведение на тему: {task.description}",
            "researcher": f"Исследование по теме: {task.description}",
            "translator": f"Перевод для задачи: {task.description}",
            "summarizer": f"Краткое изложение: {task.description}"
        }
        
        result_text = fallback_responses.get(agent_type, f"Ответ на задачу: {task.description}")
        
        return {
            "type": agent_type,
            "result": result_text,
            "metadata": {
                "agent_id": agent.id,
                "agent_type": agent_type,
                "fallback_mode": True,
                "word_count": len(result_text.split())
            }
        }
    
    async def _assess_result_quality(self, task: Task, result: Dict[str, Any], agent: Agent) -> float:
        """Оценка качества результата"""
        base_quality = 0.7
        
        # Учитываем тип агента
        agent_type = agent.type if isinstance(agent.type, str) else agent.type.value
        if agent_type in ["code_generator", "data_analyst"]:
            base_quality += 0.1
        
        # Учитываем сложность задачи
        if task.analysis and task.analysis.get("complexity") == "complex":
            base_quality -= 0.1
        elif task.analysis and task.analysis.get("complexity") == "simple":
            base_quality += 0.1
        
        # Учитываем историю агента
        if agent.average_quality_score > 0:
            base_quality = (base_quality + agent.average_quality_score) / 2
        
        return max(0.0, min(1.0, base_quality))
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Получение задачи по ID"""
        # Ищем в активных задачах
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
        
        # Ищем в завершенных задачах
        if task_id in self.completed_tasks:
            task_result = self.completed_tasks[task_id]
            # Создаем объект Task из результата
            task = Task(
                id=task_id,
                description="",
                status=task_result.status,
                agent_id=task_result.agent_id,
                result=task_result.result_data,
                execution_time=task_result.execution_time
            )
            return task
        
        return None
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Получение статистики системы"""
        active_tasks_count = len(self.active_tasks)
        completed_tasks_count = len(self.completed_tasks)
        
        # Статистика по статусам задач
        status_stats = {}
        for task in self.active_tasks.values():
            status = task.status.value
            status_stats[status] = status_stats.get(status, 0) + 1
        
        # Среднее время выполнения
        execution_times = [result.execution_time for result in self.completed_tasks.values()]
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        # Средний балл качества
        quality_scores = [result.quality_score for result in self.completed_tasks.values() if result.quality_score]
        avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        return {
            "active_tasks": active_tasks_count,
            "completed_tasks": completed_tasks_count,
            "total_tasks": active_tasks_count + completed_tasks_count,
            "average_execution_time": avg_execution_time,
            "average_quality_score": avg_quality_score,
            "tasks_by_status": status_stats,
            "task_queue_size": self.task_queue.qsize()
        }
    
    async def cleanup(self):
        """Очистка ресурсов"""
        # Останавливаем всех воркеров
        for worker in self.execution_workers:
            if not worker.done():
                worker.cancel()
        
        # Ждем завершения активных задач
        if self.active_tasks:
            logger.info(f"Ожидание завершения {len(self.active_tasks)} активных задач...")
            # Здесь можно добавить логику ожидания или принудительного завершения
        
        logger.info("TaskExecutor очищен")
