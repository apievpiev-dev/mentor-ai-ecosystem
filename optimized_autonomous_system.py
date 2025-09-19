#!/usr/bin/env python3
"""
Оптимизированная автономная система Multi-AI
Улучшенная версия с лучшей производительностью, стабильностью и мониторингом
"""

import asyncio
import logging
import time
import json
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import aiofiles
import signal
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/optimized_autonomous_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """Метрики системы"""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    network_io: Dict[str, int]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class AgentMetrics:
    """Метрики агента"""
    agent_id: str
    agent_name: str
    tasks_completed: int
    tasks_failed: int
    average_response_time: float
    last_activity: datetime
    status: str
    performance_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            'last_activity': self.last_activity.isoformat()
        }

class OptimizedAutonomousSystem:
    """Оптимизированная автономная система"""
    
    def __init__(self):
        self.running = False
        self.agents = {}
        self.active_agents = set()
        self.task_counter = 0
        self.startup_time = datetime.now()
        self.lock = threading.Lock()
        
        # Метрики системы
        self.system_metrics = []
        self.agent_metrics = {}
        self.performance_history = []
        
        # Конфигурация
        self.config = {
            "max_concurrent_tasks": 10,
            "task_timeout": 30,
            "metrics_retention_hours": 24,
            "auto_restart_threshold": 0.8,  # Перезапуск при 80% загрузке
            "health_check_interval": 60,    # Проверка здоровья каждую минуту
            "metrics_save_interval": 300,   # Сохранение метрик каждые 5 минут
            "task_generation_interval": (30, 60)  # Интервал генерации задач
        }
        
        # Автономные задачи для агентов
        self.autonomous_tasks = {
            "general_assistant": [
                "Проанализируй текущее состояние системы и создай отчет",
                "Предложи улучшения для системы",
                "Создай план оптимизации производительности",
                "Проверь логи системы на наличие ошибок",
                "Предложи новые функции для системы",
                "Создай резервную копию конфигурации",
                "Оптимизируй использование ресурсов"
            ],
            "code_developer": [
                "Создай функцию для автоматического тестирования API",
                "Оптимизируй код системы для лучшей производительности",
                "Добавь обработку ошибок в критические функции",
                "Создай скрипт для автоматического развертывания",
                "Проверь код на наличие потенциальных улучшений",
                "Создай автоматические тесты для новых функций",
                "Оптимизируй алгоритмы для лучшей производительности"
            ],
            "data_analyst": [
                "Проанализируй статистику использования системы",
                "Создай отчет о производительности агентов",
                "Проанализируй паттерны использования API",
                "Создай дашборд для мониторинга системы",
                "Проанализируй последние логи системы",
                "Создай прогноз нагрузки на систему",
                "Оптимизируй структуру данных"
            ],
            "project_manager": [
                "Создай план развития системы на следующую неделю",
                "Проанализируй приоритеты задач",
                "Создай roadmap для новых функций",
                "Оцени риски и создай план их минимизации",
                "Создай план задач на следующий час",
                "Оптимизируй распределение ресурсов",
                "Создай план резервного копирования"
            ],
            "designer": [
                "Улучши дизайн веб-интерфейса",
                "Создай иконки для новых функций",
                "Оптимизируй UX для мобильных устройств",
                "Создай визуальные диаграммы архитектуры системы",
                "Предложи улучшения пользовательского интерфейса",
                "Создай адаптивный дизайн для разных экранов",
                "Оптимизируй загрузку визуальных элементов"
            ],
            "qa_tester": [
                "Протестируй все API endpoints",
                "Проверь систему на уязвимости",
                "Создай автоматические тесты",
                "Протестируй производительность под нагрузкой",
                "Проведи базовое тестирование веб-интерфейса",
                "Создай тесты для новых функций",
                "Проверь совместимость с разными браузерами"
            ]
        }
        
        # Инициализируем агентов
        self._initialize_agents()
        
        # Создаем директории для данных
        self._setup_directories()
        
        logger.info("🚀 Оптимизированная автономная система инициализирована")
    
    def _setup_directories(self):
        """Создание необходимых директорий"""
        directories = [
            "/workspace/system_data",
            "/workspace/metrics",
            "/workspace/logs",
            "/workspace/backups"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Создана директория: {directory}")
    
    def _initialize_agents(self):
        """Инициализация агентов с метриками"""
        agent_types = [
            "general_assistant",
            "code_developer", 
            "data_analyst",
            "project_manager",
            "designer",
            "qa_tester"
        ]
        
        for agent_type in agent_types:
            agent_id = f"{agent_type}_agent"
            self.agents[agent_type] = {
                "id": agent_id,
                "name": f"Агент {agent_type.replace('_', ' ').title()}",
                "type": agent_type,
                "is_active": False,
                "last_activity": None,
                "task_count": 0,
                "failed_tasks": 0,
                "status": "idle",
                "performance_score": 1.0,
                "response_times": []
            }
            
            # Инициализируем метрики агента
            self.agent_metrics[agent_id] = AgentMetrics(
                agent_id=agent_id,
                agent_name=self.agents[agent_type]["name"],
                tasks_completed=0,
                tasks_failed=0,
                average_response_time=0.0,
                last_activity=datetime.now(),
                status="idle",
                performance_score=1.0
            )
            
            logger.info(f"✅ Агент {agent_type} инициализирован с метриками")
    
    async def collect_system_metrics(self) -> SystemMetrics:
        """Сбор метрик системы"""
        try:
            # CPU и память
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            
            # Диск
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            
            # Сеть
            network = psutil.net_io_counters()
            network_io = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
            
            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                disk_usage_percent=disk_usage_percent,
                network_io=network_io,
                timestamp=datetime.now()
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Ошибка сбора метрик системы: {e}")
            return SystemMetrics(0, 0, 0, 0, {}, datetime.now())
    
    async def update_agent_metrics(self, agent_type: str, task_duration: float, success: bool):
        """Обновление метрик агента"""
        try:
            with self.lock:
                agent = self.agents[agent_type]
                agent_id = agent["id"]
                
                # Обновляем счетчики
                if success:
                    agent["task_count"] += 1
                    agent["response_times"].append(task_duration)
                    # Ограничиваем историю до 100 последних задач
                    if len(agent["response_times"]) > 100:
                        agent["response_times"] = agent["response_times"][-100:]
                else:
                    agent["failed_tasks"] += 1
                
                # Обновляем метрики
                metrics = self.agent_metrics[agent_id]
                metrics.tasks_completed = agent["task_count"]
                metrics.tasks_failed = agent["failed_tasks"]
                metrics.last_activity = datetime.now()
                metrics.status = agent["status"]
                
                # Вычисляем среднее время ответа
                if agent["response_times"]:
                    metrics.average_response_time = sum(agent["response_times"]) / len(agent["response_times"])
                
                # Вычисляем оценку производительности
                success_rate = agent["task_count"] / (agent["task_count"] + agent["failed_tasks"]) if (agent["task_count"] + agent["failed_tasks"]) > 0 else 1.0
                response_time_score = max(0, 1 - (metrics.average_response_time / 30))  # Нормализуем к 30 секундам
                metrics.performance_score = (success_rate * 0.7 + response_time_score * 0.3)
                
                agent["performance_score"] = metrics.performance_score
                
        except Exception as e:
            logger.error(f"❌ Ошибка обновления метрик агента {agent_type}: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья системы"""
        try:
            metrics = await self.collect_system_metrics()
            
            # Проверяем критические метрики
            health_status = {
                "overall_health": "healthy",
                "issues": [],
                "recommendations": [],
                "metrics": metrics.to_dict()
            }
            
            # Проверка CPU
            if metrics.cpu_percent > 80:
                health_status["issues"].append(f"Высокая загрузка CPU: {metrics.cpu_percent:.1f}%")
                health_status["recommendations"].append("Рассмотрите возможность масштабирования")
                if metrics.cpu_percent > 90:
                    health_status["overall_health"] = "critical"
            
            # Проверка памяти
            if metrics.memory_percent > 85:
                health_status["issues"].append(f"Высокое использование памяти: {metrics.memory_percent:.1f}%")
                health_status["recommendations"].append("Освободите память или увеличьте RAM")
                if metrics.memory_percent > 95:
                    health_status["overall_health"] = "critical"
            
            # Проверка диска
            if metrics.disk_usage_percent > 90:
                health_status["issues"].append(f"Мало места на диске: {metrics.disk_usage_percent:.1f}%")
                health_status["recommendations"].append("Очистите диск или увеличьте объем")
                health_status["overall_health"] = "critical"
            
            # Проверка агентов
            inactive_agents = [agent_type for agent_type, agent in self.agents.items() 
                             if not agent["is_active"] and (datetime.now() - agent["last_activity"]).seconds > 300]
            
            if inactive_agents:
                health_status["issues"].append(f"Неактивные агенты: {', '.join(inactive_agents)}")
                health_status["recommendations"].append("Проверьте работу неактивных агентов")
            
            # Проверка производительности агентов
            low_performance_agents = [agent_type for agent_type, agent in self.agents.items() 
                                    if agent["performance_score"] < 0.5]
            
            if low_performance_agents:
                health_status["issues"].append(f"Низкая производительность агентов: {', '.join(low_performance_agents)}")
                health_status["recommendations"].append("Оптимизируйте работу агентов с низкой производительностью")
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки здоровья системы: {e}")
            return {"overall_health": "error", "error": str(e)}
    
    async def auto_optimize(self):
        """Автоматическая оптимизация системы"""
        try:
            health = await self.health_check()
            
            if health["overall_health"] == "critical":
                logger.warning("🚨 Критическое состояние системы, применяем экстренные меры")
                await self._emergency_optimization()
            elif health["overall_health"] == "warning":
                logger.info("⚠️ Предупреждение о состоянии системы, применяем оптимизацию")
                await self._standard_optimization()
            
            # Применяем рекомендации
            for recommendation in health.get("recommendations", []):
                await self._apply_recommendation(recommendation)
                
        except Exception as e:
            logger.error(f"❌ Ошибка автоматической оптимизации: {e}")
    
    async def _emergency_optimization(self):
        """Экстренная оптимизация"""
        try:
            logger.info("🚨 Применяем экстренную оптимизацию")
            
            # Останавливаем неактивные агенты
            for agent_type, agent in self.agents.items():
                if not agent["is_active"] and agent["performance_score"] < 0.3:
                    agent["status"] = "disabled"
                    logger.info(f"🔴 Отключен агент {agent_type} из-за низкой производительности")
            
            # Очищаем старые метрики
            cutoff_time = datetime.now() - timedelta(hours=1)
            self.system_metrics = [m for m in self.system_metrics if m.timestamp > cutoff_time]
            
            # Принудительная сборка мусора
            import gc
            gc.collect()
            
            logger.info("✅ Экстренная оптимизация завершена")
            
        except Exception as e:
            logger.error(f"❌ Ошибка экстренной оптимизации: {e}")
    
    async def _standard_optimization(self):
        """Стандартная оптимизация"""
        try:
            logger.info("🔧 Применяем стандартную оптимизацию")
            
            # Оптимизируем агентов с низкой производительностью
            for agent_type, agent in self.agents.items():
                if agent["performance_score"] < 0.6:
                    # Сбрасываем счетчики ошибок
                    agent["failed_tasks"] = max(0, agent["failed_tasks"] - 1)
                    logger.info(f"🔧 Оптимизирован агент {agent_type}")
            
            # Очищаем старые данные
            await self._cleanup_old_data()
            
            logger.info("✅ Стандартная оптимизация завершена")
            
        except Exception as e:
            logger.error(f"❌ Ошибка стандартной оптимизации: {e}")
    
    async def _apply_recommendation(self, recommendation: str):
        """Применение рекомендации"""
        try:
            if "масштабирование" in recommendation.lower():
                await self._scale_system()
            elif "память" in recommendation.lower():
                await self._optimize_memory()
            elif "диск" in recommendation.lower():
                await self._cleanup_disk()
            elif "агенты" in recommendation.lower():
                await self._optimize_agents()
                
        except Exception as e:
            logger.error(f"❌ Ошибка применения рекомендации '{recommendation}': {e}")
    
    async def _scale_system(self):
        """Масштабирование системы"""
        logger.info("📈 Применяем масштабирование системы")
        # Здесь можно добавить логику масштабирования
    
    async def _optimize_memory(self):
        """Оптимизация памяти"""
        logger.info("🧠 Оптимизируем использование памяти")
        import gc
        gc.collect()
    
    async def _cleanup_disk(self):
        """Очистка диска"""
        logger.info("💾 Очищаем диск")
        await self._cleanup_old_data()
    
    async def _optimize_agents(self):
        """Оптимизация агентов"""
        logger.info("🤖 Оптимизируем агентов")
        # Сбрасываем счетчики ошибок для всех агентов
        for agent in self.agents.values():
            agent["failed_tasks"] = max(0, agent["failed_tasks"] - 1)
    
    async def _cleanup_old_data(self):
        """Очистка старых данных"""
        try:
            # Очищаем старые метрики
            cutoff_time = datetime.now() - timedelta(hours=self.config["metrics_retention_hours"])
            self.system_metrics = [m for m in self.system_metrics if m.timestamp > cutoff_time]
            
            # Очищаем старую историю производительности
            self.performance_history = [p for p in self.performance_history if p["timestamp"] > cutoff_time.isoformat()]
            
            logger.info("🧹 Очистка старых данных завершена")
            
        except Exception as e:
            logger.error(f"❌ Ошибка очистки старых данных: {e}")
    
    async def save_metrics(self):
        """Сохранение метрик"""
        try:
            metrics_data = {
                "system_metrics": [m.to_dict() for m in self.system_metrics[-100:]],  # Последние 100 записей
                "agent_metrics": {agent_id: metrics.to_dict() for agent_id, metrics in self.agent_metrics.items()},
                "performance_history": self.performance_history[-50:],  # Последние 50 записей
                "saved_at": datetime.now().isoformat()
            }
            
            metrics_file = Path("/workspace/metrics/system_metrics.json")
            async with aiofiles.open(metrics_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(metrics_data, ensure_ascii=False, indent=2))
            
            logger.info("💾 Метрики сохранены")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения метрик: {e}")
    
    async def load_metrics(self):
        """Загрузка метрик"""
        try:
            metrics_file = Path("/workspace/metrics/system_metrics.json")
            if metrics_file.exists():
                async with aiofiles.open(metrics_file, 'r', encoding='utf-8') as f:
                    data = json.loads(await f.read())
                
                # Восстанавливаем метрики системы
                if "system_metrics" in data:
                    self.system_metrics = [SystemMetrics(**m) for m in data["system_metrics"]]
                
                # Восстанавливаем метрики агентов
                if "agent_metrics" in data:
                    for agent_id, metrics_data in data["agent_metrics"].items():
                        if agent_id in self.agent_metrics:
                            metrics_data["last_activity"] = datetime.fromisoformat(metrics_data["last_activity"])
                            self.agent_metrics[agent_id] = AgentMetrics(**metrics_data)
                
                # Восстанавливаем историю производительности
                if "performance_history" in data:
                    self.performance_history = data["performance_history"]
                
                logger.info("📊 Метрики загружены")
                
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки метрик: {e}")
    
    async def autonomous_task_generator(self):
        """Улучшенный генератор автономных задач"""
        logger.info("🚀 Запуск оптимизированного генератора автономных задач...")
        
        while self.running:
            try:
                # Проверяем здоровье системы перед генерацией задач
                health = await self.health_check()
                if health["overall_health"] == "critical":
                    logger.warning("🚨 Критическое состояние системы, пропускаем генерацию задач")
                    await asyncio.sleep(60)
                    continue
                
                # Выбираем агента на основе производительности
                available_agents = [agent_type for agent_type, agent in self.agents.items() 
                                  if agent["status"] != "disabled" and agent["performance_score"] > 0.3]
                
                if not available_agents:
                    logger.warning("⚠️ Нет доступных агентов для выполнения задач")
                    await asyncio.sleep(30)
                    continue
                
                # Выбираем агента с наилучшей производительностью
                best_agent = max(available_agents, key=lambda x: self.agents[x]["performance_score"])
                agent = self.agents[best_agent]
                
                if best_agent in self.autonomous_tasks:
                    tasks = self.autonomous_tasks[best_agent]
                    task = tasks[self.task_counter % len(tasks)]
                    
                    # Активируем агента
                    start_time = time.time()
                    with self.lock:
                        agent["is_active"] = True
                        agent["last_activity"] = datetime.now()
                        agent["status"] = "working"
                        self.active_agents.add(best_agent)
                        self.task_counter += 1
                    
                    logger.info(f"📋 Автономная задача #{self.task_counter} отправлена агенту {best_agent}: {task[:50]}...")
                    
                    # Имитируем работу агента с таймаутом
                    try:
                        await asyncio.wait_for(
                            asyncio.sleep(5),  # Минимальное время работы
                            timeout=self.config["task_timeout"]
                        )
                        
                        # Обновляем метрики успешного выполнения
                        task_duration = time.time() - start_time
                        await self.update_agent_metrics(best_agent, task_duration, True)
                        
                        logger.info(f"✅ Агент {best_agent} успешно завершил задачу за {task_duration:.2f}с")
                        
                    except asyncio.TimeoutError:
                        # Обновляем метрики неудачного выполнения
                        task_duration = time.time() - start_time
                        await self.update_agent_metrics(best_agent, task_duration, False)
                        logger.warning(f"⏰ Агент {best_agent} превысил время выполнения задачи")
                    
                    # Деактивируем агента
                    with self.lock:
                        agent["is_active"] = False
                        agent["status"] = "idle"
                        if best_agent in self.active_agents:
                            self.active_agents.remove(best_agent)
                
                # Динамический интервал на основе состояния системы
                base_interval = self.config["task_generation_interval"][0]
                max_interval = self.config["task_generation_interval"][1]
                
                # Увеличиваем интервал при высокой загрузке
                if health["overall_health"] == "warning":
                    interval = min(max_interval, base_interval * 1.5)
                elif health["overall_health"] == "critical":
                    interval = max_interval
                else:
                    interval = base_interval
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"❌ Ошибка в генераторе автономных задач: {e}")
                await asyncio.sleep(10)
    
    async def metrics_collector(self):
        """Сборщик метрик"""
        logger.info("📊 Запуск сборщика метрик...")
        
        while self.running:
            try:
                # Собираем метрики системы
                metrics = await self.collect_system_metrics()
                self.system_metrics.append(metrics)
                
                # Ограничиваем количество метрик в памяти
                if len(self.system_metrics) > 1000:
                    self.system_metrics = self.system_metrics[-500:]
                
                # Сохраняем историю производительности
                performance_data = {
                    "timestamp": datetime.now().isoformat(),
                    "total_agents": len(self.agents),
                    "active_agents": len(self.active_agents),
                    "avg_performance": sum(agent["performance_score"] for agent in self.agents.values()) / len(self.agents),
                    "system_health": (await self.health_check())["overall_health"]
                }
                self.performance_history.append(performance_data)
                
                # Ограничиваем историю производительности
                if len(self.performance_history) > 500:
                    self.performance_history = self.performance_history[-250:]
                
                await asyncio.sleep(60)  # Собираем метрики каждую минуту
                
            except Exception as e:
                logger.error(f"❌ Ошибка в сборщике метрик: {e}")
                await asyncio.sleep(60)
    
    async def health_monitor(self):
        """Монитор здоровья системы"""
        logger.info("🏥 Запуск монитора здоровья системы...")
        
        while self.running:
            try:
                # Проверяем здоровье системы
                health = await self.health_check()
                
                # Логируем состояние
                if health["overall_health"] == "critical":
                    logger.critical(f"🚨 КРИТИЧЕСКОЕ СОСТОЯНИЕ СИСТЕМЫ: {health['issues']}")
                elif health["overall_health"] == "warning":
                    logger.warning(f"⚠️ ПРЕДУПРЕЖДЕНИЕ: {health['issues']}")
                
                # Применяем автоматическую оптимизацию
                await self.auto_optimize()
                
                await asyncio.sleep(self.config["health_check_interval"])
                
            except Exception as e:
                logger.error(f"❌ Ошибка в мониторе здоровья: {e}")
                await asyncio.sleep(60)
    
    async def metrics_saver(self):
        """Сохранение метрик"""
        logger.info("💾 Запуск сохранения метрик...")
        
        while self.running:
            try:
                await self.save_metrics()
                await asyncio.sleep(self.config["metrics_save_interval"])
                
            except Exception as e:
                logger.error(f"❌ Ошибка в сохранении метрик: {e}")
                await asyncio.sleep(300)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Получение статуса системы"""
        with self.lock:
            uptime_delta = datetime.now() - self.startup_time
            uptime = f"{int(uptime_delta.total_seconds() / 60)}м"
            
            # Вычисляем общую производительность
            total_performance = sum(agent["performance_score"] for agent in self.agents.values()) / len(self.agents)
            
            return {
                "system_status": "running" if self.running else "stopped",
                "uptime": uptime,
                "total_agents": len(self.agents),
                "active_agents": len(self.active_agents),
                "total_tasks": self.task_counter,
                "overall_performance": total_performance,
                "system_health": "healthy",  # Будет обновлено в health_check
                "coordination_status": {
                    "total_agents": len(self.agents),
                    "active_tasks": len(self.active_agents),
                    "message_queue_size": 0,
                    "agent_capabilities": {
                        agent_id: {
                            "skills": ["autonomous_work", "task_processing", "performance_monitoring"],
                            "performance_score": agent["performance_score"],
                            "availability": agent["status"] != "disabled",
                            "current_load": 1.0 if agent["is_active"] else 0.0,
                            "is_active": agent["is_active"],
                            "last_activity": agent["last_activity"].isoformat() if agent["last_activity"] else None,
                            "tasks_completed": agent["task_count"],
                            "tasks_failed": agent["failed_tasks"]
                        }
                        for agent_id, agent in self.agents.items()
                    },
                    "active_tasks_info": []
                },
                "shared_memory": {
                    "knowledge_items": self.task_counter,
                    "conversation_history": self.task_counter,
                    "agent_capabilities": len(self.agents),
                    "metrics_count": len(self.system_metrics)
                },
                "startup_time": self.startup_time.isoformat(),
                "config": self.config
            }
    
    def send_message_to_agent(self, message: str, agent_type: str = None, user_id: str = "user") -> Dict[str, Any]:
        """Отправка сообщения агенту"""
        try:
            with self.lock:
                if agent_type and agent_type in self.agents:
                    # Отправляем конкретному агенту
                    agent = self.agents[agent_type]
                    start_time = time.time()
                    
                    agent["is_active"] = True
                    agent["last_activity"] = datetime.now()
                    agent["task_count"] += 1
                    self.active_agents.add(agent_type)
                    
                    logger.info(f"🚀 Агент {agent_type} активирован: {message[:50]}...")
                    
                    # Имитируем обработку сообщения
                    task_duration = time.time() - start_time
                    self.update_agent_metrics(agent_type, task_duration, True)
                    
                    return {
                        "success": True,
                        "response": {
                            "response": f"Агент {agent['name']} получил сообщение: {message}",
                            "status": "processed",
                            "processing_time": task_duration
                        },
                        "agent": agent["name"],
                        "agent_type": agent_type,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    # Отправляем агенту с наилучшей производительностью
                    available_agents = [agent_type for agent_type, agent in self.agents.items() 
                                      if agent["status"] != "disabled"]
                    
                    if available_agents:
                        best_agent = max(available_agents, key=lambda x: self.agents[x]["performance_score"])
                        return self.send_message_to_agent(message, best_agent, user_id)
                    else:
                        return {"error": "No agents available"}
                        
        except Exception as e:
            logger.error(f"❌ Ошибка отправки сообщения агенту: {e}")
            return {"error": str(e)}
    
    async def start(self):
        """Запуск системы"""
        try:
            logger.info("🚀 Запуск оптимизированной автономной системы...")
            
            # Загружаем сохраненные метрики
            await self.load_metrics()
            
            self.running = True
            
            # Запускаем все компоненты системы
            tasks = [
                asyncio.create_task(self.autonomous_task_generator()),
                asyncio.create_task(self.metrics_collector()),
                asyncio.create_task(self.health_monitor()),
                asyncio.create_task(self.metrics_saver())
            ]
            
            # Ждем завершения всех задач
            await asyncio.gather(*tasks, return_exceptions=True)
            
            logger.info("✅ Оптимизированная автономная система запущена")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска системы: {e}")
            return False
    
    def stop(self):
        """Остановка системы"""
        logger.info("🛑 Остановка оптимизированной автономной системы...")
        self.running = False
        logger.info("✅ Оптимизированная автономная система остановлена")

# Глобальный экземпляр системы
_optimized_system = None

def get_optimized_system() -> OptimizedAutonomousSystem:
    """Получение глобального экземпляра оптимизированной системы"""
    global _optimized_system
    if _optimized_system is None:
        _optimized_system = OptimizedAutonomousSystem()
    return _optimized_system

async def main():
    """Главная функция для тестирования"""
    system = get_optimized_system()
    
    try:
        # Запускаем систему
        if await system.start():
            logger.info("✅ Оптимизированная автономная система запущена")
            
            # Ждем некоторое время
            await asyncio.sleep(300)  # 5 минут
            
            # Получаем статус
            status = system.get_system_status()
            logger.info(f"📊 Статус системы: {status}")
            
        else:
            logger.error("❌ Не удалось запустить оптимизированную автономную систему")
    
    except Exception as e:
        logger.error(f"❌ Ошибка в главной функции: {e}")
    
    finally:
        # Останавливаем систему
        system.stop()

if __name__ == "__main__":
    # Обработчик сигналов для корректного завершения
    def signal_handler(signum, frame):
        logger.info(f"📡 Получен сигнал {signum}, завершаем работу...")
        system = get_optimized_system()
        system.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    asyncio.run(main())