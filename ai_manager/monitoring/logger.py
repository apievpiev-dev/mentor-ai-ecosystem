"""
Система мониторинга и логирования для AI Manager
"""

import logging
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from database.database import db_manager
import sys
import traceback


class AIManagerLogger:
    """Централизованный логгер для AI Manager"""
    
    def __init__(self, name: str = "ai_manager"):
        self.logger = logging.getLogger(name)
        self.setup_logging()
    
    def setup_logging(self):
        """Настройка системы логирования"""
        # Создаем форматтер
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Настройка консольного вывода
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        # Настройка файлового вывода
        file_handler = logging.FileHandler('ai_manager.log')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        
        # Добавляем обработчики к логгеру
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)
        
        # Предотвращаем дублирование логов
        self.logger.propagate = False
    
    async def log_task_event(self, task_id: str, event_type: str, message: str, metadata: Dict[str, Any] = None):
        """Логирование событий задач"""
        log_message = f"[TASK:{task_id}] {event_type}: {message}"
        
        if event_type in ["ERROR", "CRITICAL"]:
            self.logger.error(log_message, extra={"metadata": metadata or {}})
            level = "ERROR"
        elif event_type in ["WARNING"]:
            self.logger.warning(log_message, extra={"metadata": metadata or {}})
            level = "WARNING"
        else:
            self.logger.info(log_message, extra={"metadata": metadata or {}})
            level = "INFO"
        
        # Сохраняем в базу данных
        await db_manager.log_system_event(
            level=level,
            message=log_message,
            component="task_executor",
            metadata=metadata or {}
        )
    
    async def log_agent_event(self, agent_id: str, event_type: str, message: str, metadata: Dict[str, Any] = None):
        """Логирование событий агентов"""
        log_message = f"[AGENT:{agent_id}] {event_type}: {message}"
        
        if event_type in ["ERROR", "CRITICAL"]:
            self.logger.error(log_message, extra={"metadata": metadata or {}})
            level = "ERROR"
        elif event_type in ["WARNING"]:
            self.logger.warning(log_message, extra={"metadata": metadata or {}})
            level = "WARNING"
        else:
            self.logger.info(log_message, extra={"metadata": metadata or {}})
            level = "INFO"
        
        # Сохраняем в базу данных
        await db_manager.log_system_event(
            level=level,
            message=log_message,
            component="ai_manager",
            metadata=metadata or {}
        )
    
    async def log_system_event(self, component: str, event_type: str, message: str, metadata: Dict[str, Any] = None):
        """Логирование системных событий"""
        log_message = f"[SYSTEM:{component}] {event_type}: {message}"
        
        if event_type in ["ERROR", "CRITICAL"]:
            self.logger.error(log_message, extra={"metadata": metadata or {}})
            level = "ERROR"
        elif event_type in ["WARNING"]:
            self.logger.warning(log_message, extra={"metadata": metadata or {}})
            level = "WARNING"
        else:
            self.logger.info(log_message, extra={"metadata": metadata or {}})
            level = "INFO"
        
        # Сохраняем в базу данных
        await db_manager.log_system_event(
            level=level,
            message=log_message,
            component=component,
            metadata=metadata or {}
        )
    
    async def log_performance_metric(self, metric_name: str, value: float, metadata: Dict[str, Any] = None):
        """Логирование метрик производительности"""
        log_message = f"PERFORMANCE: {metric_name} = {value}"
        self.logger.info(log_message, extra={"metadata": metadata or {}})
        
        # Сохраняем в базу данных
        await db_manager.log_system_event(
            level="INFO",
            message=log_message,
            component="performance_monitor",
            metadata={"metric_name": metric_name, "value": value, **(metadata or {})}
        )
    
    def log_exception(self, component: str, exception: Exception, context: Dict[str, Any] = None):
        """Логирование исключений"""
        error_message = f"EXCEPTION in {component}: {str(exception)}"
        self.logger.error(error_message, exc_info=True, extra={"context": context or {}})
        
        # Асинхронно сохраняем в базу данных
        asyncio.create_task(
            db_manager.log_system_event(
                level="ERROR",
                message=error_message,
                component=component,
                metadata={
                    "exception_type": type(exception).__name__,
                    "exception_message": str(exception),
                    "traceback": traceback.format_exc(),
                    **(context or {})
                }
            )
        )


class PerformanceMonitor:
    """Монитор производительности системы"""
    
    def __init__(self):
        self.metrics = {}
        self.logger = AIManagerLogger("performance_monitor")
    
    async def record_task_execution_time(self, task_id: str, execution_time: float):
        """Запись времени выполнения задачи"""
        await self.logger.log_performance_metric(
            "task_execution_time",
            execution_time,
            {"task_id": task_id}
        )
        
        # Обновляем внутренние метрики
        if "task_execution_times" not in self.metrics:
            self.metrics["task_execution_times"] = []
        
        self.metrics["task_execution_times"].append({
            "task_id": task_id,
            "execution_time": execution_time,
            "timestamp": datetime.now()
        })
        
        # Ограничиваем размер списка
        if len(self.metrics["task_execution_times"]) > 1000:
            self.metrics["task_execution_times"] = self.metrics["task_execution_times"][-500:]
    
    async def record_agent_performance(self, agent_id: str, task_id: str, quality_score: float, execution_time: float):
        """Запись производительности агента"""
        await self.logger.log_performance_metric(
            "agent_performance",
            quality_score,
            {
                "agent_id": agent_id,
                "task_id": task_id,
                "execution_time": execution_time
            }
        )
        
        # Обновляем внутренние метрики
        if "agent_performance" not in self.metrics:
            self.metrics["agent_performance"] = {}
        
        if agent_id not in self.metrics["agent_performance"]:
            self.metrics["agent_performance"][agent_id] = []
        
        self.metrics["agent_performance"][agent_id].append({
            "task_id": task_id,
            "quality_score": quality_score,
            "execution_time": execution_time,
            "timestamp": datetime.now()
        })
    
    async def record_system_metrics(self):
        """Запись системных метрик"""
        import psutil
        
        # CPU использование
        cpu_percent = psutil.cpu_percent()
        await self.logger.log_performance_metric("cpu_usage", cpu_percent)
        
        # Использование памяти
        memory = psutil.virtual_memory()
        await self.logger.log_performance_metric("memory_usage", memory.percent)
        
        # Использование диска
        disk = psutil.disk_usage('/')
        await self.logger.log_performance_metric("disk_usage", (disk.used / disk.total) * 100)
        
        # Обновляем внутренние метрики
        if "system_metrics" not in self.metrics:
            self.metrics["system_metrics"] = []
        
        self.metrics["system_metrics"].append({
            "cpu_usage": cpu_percent,
            "memory_usage": memory.percent,
            "disk_usage": (disk.used / disk.total) * 100,
            "timestamp": datetime.now()
        })
        
        # Ограничиваем размер списка
        if len(self.metrics["system_metrics"]) > 100:
            self.metrics["system_metrics"] = self.metrics["system_metrics"][-50:]
    
    def get_average_execution_time(self) -> float:
        """Получение среднего времени выполнения задач"""
        if "task_execution_times" not in self.metrics or not self.metrics["task_execution_times"]:
            return 0.0
        
        times = [m["execution_time"] for m in self.metrics["task_execution_times"]]
        return sum(times) / len(times)
    
    def get_average_quality_score(self) -> float:
        """Получение среднего балла качества"""
        if "agent_performance" not in self.metrics:
            return 0.0
        
        all_scores = []
        for agent_scores in self.metrics["agent_performance"].values():
            all_scores.extend([s["quality_score"] for s in agent_scores])
        
        if not all_scores:
            return 0.0
        
        return sum(all_scores) / len(all_scores)
    
    def get_agent_performance_summary(self, agent_id: str) -> Dict[str, Any]:
        """Получение сводки производительности агента"""
        if "agent_performance" not in self.metrics or agent_id not in self.metrics["agent_performance"]:
            return {"tasks_completed": 0, "average_quality": 0.0, "average_time": 0.0}
        
        agent_data = self.metrics["agent_performance"][agent_id]
        
        if not agent_data:
            return {"tasks_completed": 0, "average_quality": 0.0, "average_time": 0.0}
        
        quality_scores = [d["quality_score"] for d in agent_data]
        execution_times = [d["execution_time"] for d in agent_data]
        
        return {
            "tasks_completed": len(agent_data),
            "average_quality": sum(quality_scores) / len(quality_scores),
            "average_time": sum(execution_times) / len(execution_times),
            "last_activity": max([d["timestamp"] for d in agent_data])
        }
    
    def get_system_health_status(self) -> Dict[str, Any]:
        """Получение статуса здоровья системы"""
        if "system_metrics" not in self.metrics or not self.metrics["system_metrics"]:
            return {"status": "unknown", "metrics": {}}
        
        latest_metrics = self.metrics["system_metrics"][-1]
        
        # Определяем статус на основе метрик
        status = "healthy"
        if latest_metrics["cpu_usage"] > 80 or latest_metrics["memory_usage"] > 80:
            status = "warning"
        if latest_metrics["cpu_usage"] > 95 or latest_metrics["memory_usage"] > 95:
            status = "critical"
        
        return {
            "status": status,
            "metrics": latest_metrics,
            "timestamp": latest_metrics["timestamp"]
        }


# Глобальные экземпляры
logger = AIManagerLogger()
performance_monitor = PerformanceMonitor()
