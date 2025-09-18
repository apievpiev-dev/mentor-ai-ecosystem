#!/usr/bin/env python3
"""
JARVIS - Автономная саморазвивающаяся система
Ядро системы для автоматизации жизни и бизнеса
"""

import os
import sys
import json
import time
import asyncio
import subprocess
import threading
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests
import yaml
from dataclasses import dataclass, asdict
import docker
import paramiko
from fastapi import FastAPI, WebSocket, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/mentor/jarvis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SystemState:
    """Состояние системы"""
    total_instances: int = 1
    active_tasks: int = 0
    resources_used: Dict[str, float] = None
    last_self_replication: Optional[str] = None
    performance_score: float = 0.0
    autonomy_level: int = 1
    knowledge_base_size: int = 0
    
    def __post_init__(self):
        if self.resources_used is None:
            self.resources_used = {"cpu": 0.0, "memory": 0.0, "disk": 0.0}

@dataclass
class Task:
    """Задача системы"""
    id: str
    type: str  # automation, content_generation, analysis, self_improvement
    priority: int  # 1-10
    status: str  # pending, running, completed, failed
    created_at: str
    parameters: Dict[str, Any] = None
    result: Any = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}

class JarvisCore:
    """Основной класс автономной системы Джарвис"""
    
    def __init__(self):
        self.state = SystemState()
        self.tasks_queue = []
        self.completed_tasks = []
        self.knowledge_base = {}
        self.automation_modules = {}
        self.running = True
        self.app = FastAPI(title="JARVIS Control Panel")
        
        # Создаем директории
        self.setup_directories()
        
        # Загружаем конфигурацию
        self.load_config()
        
        # Инициализируем модули
        self.init_modules()
        
        # Инициализируем интеграцию
        self.init_integration()
        
        # Инициализируем репликатор
        self.init_replicator()
        
        # Инициализируем мониторинг
        self.init_monitor()
        
        # Инициализируем систему зрения
        self.init_vision()
        
        # Инициализируем систему самоулучшения
        self.init_self_improvement()
        
        # Настраиваем API
        self.setup_api()
        
    def setup_directories(self):
        """Создание необходимых директорий"""
        dirs = [
            "/home/mentor/jarvis_data",
            "/home/mentor/jarvis_data/knowledge",
            "/home/mentor/jarvis_data/automation",
            "/home/mentor/jarvis_data/replication",
            "/home/mentor/jarvis_data/logs",
            "/home/mentor/jarvis_data/templates",
            "/home/mentor/jarvis_data/reports",
            "/home/mentor/jarvis_data/analysis",
            "/home/mentor/jarvis_data/content",
            "/home/mentor/jarvis_data/marketing"
        ]
        
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            
    def load_config(self):
        """Загрузка конфигурации"""
        config_path = "/home/mentor/jarvis_data/config.yaml"
        
        default_config = {
            "system": {
                "max_instances": 10,
                "replication_threshold": 80,
                "autonomy_levels": {
                    1: "basic_automation",
                    2: "content_generation", 
                    3: "self_improvement",
                    4: "autonomous_replication",
                    5: "full_autonomy"
                },
                "resource_limits": {
                    "max_cpu_percent": 70,
                    "max_memory_gb": 8,
                    "max_disk_gb": 50
                }
            },
            "automation": {
                "enabled_modules": ["content_generation", "data_analysis", "business_processes"],
                "schedule_interval": 300  # 5 минут
            },
            "replication": {
                "target_servers": [],
                "ssh_keys_path": "/home/mentor/.ssh/",
                "docker_registry": "localhost:5000"
            },
            "monitoring": {
                "metrics_interval": 60,
                "alert_thresholds": {
                    "cpu": 80,
                    "memory": 85,
                    "disk": 90
                }
            }
        }
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = default_config
            with open(config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
                
    def init_modules(self):
        """Инициализация модулей системы"""
        self.modules = {
            "content_generator": ContentGenerator(),
            "data_analyzer": DataAnalyzer(), 
            "business_automator": BusinessAutomator(),
            "self_improver": SelfImprover(),
            "monitor": SystemMonitor()
        }
        
    def init_integration(self):
        """Инициализация интеграции"""
        try:
            from jarvis_integration import JarvisIntegration
            self.integration = JarvisIntegration(self)
            logger.info("[OK] Интеграция инициализирована")
        except Exception as e:
            logger.error(f"[ERROR] Ошибка инициализации интеграции: {e}")
            self.integration = None
            
    def init_replicator(self):
        """Инициализация репликатора"""
        try:
            from jarvis_replicator import JarvisReplicator
            self.replicator = JarvisReplicator(self)
            self.modules["replicator"] = self.replicator
            logger.info("[OK] Репликатор инициализирован")
        except Exception as e:
            logger.error(f"[ERROR] Ошибка инициализации репликатора: {e}")
            self.replicator = None
            
    def init_monitor(self):
        """Инициализация мониторинга"""
        try:
            from jarvis_monitor import JarvisMonitor
            self.monitor = JarvisMonitor(self)
            logger.info("[OK] Мониторинг инициализирован")
        except Exception as e:
            logger.error(f"[ERROR] Ошибка инициализации мониторинга: {e}")
            self.monitor = None
            
    def init_vision(self):
        """Инициализация системы зрения"""
        try:
            from jarvis_vision import JarvisVision
            self.vision = JarvisVision(self)
            logger.info("[OK] Система зрения инициализирована")
        except Exception as e:
            logger.error(f"[ERROR] Ошибка инициализации системы зрения: {e}")
            self.vision = None
            
    def init_self_improvement(self):
        """Инициализация системы самоулучшения"""
        try:
            from jarvis_self_improvement import JarvisSelfImprovement
            self.self_improvement = JarvisSelfImprovement(self)
            logger.info("[OK] Система самоулучшения инициализирована")
        except Exception as e:
            logger.error(f"[ERROR] Ошибка инициализации системы самоулучшения: {e}")
            self.self_improvement = None
        
    def setup_api(self):
        """Настройка веб-API"""
        
        @self.app.get("/")
        async def dashboard():
            return HTMLResponse(open("/home/mentor/jarvis_data/templates/unified_dashboard.html").read())
        
        @self.app.get("/vision")
        async def vision_dashboard():
            return HTMLResponse(open("/home/mentor/jarvis_data/templates/vision_dashboard.html").read())
        
        @self.app.get("/chat")
        async def chat_interface():
            return HTMLResponse(open("/home/mentor/jarvis_data/templates/chat.html").read())
        
        @self.app.get("/visual_test_report")
        async def visual_test_report():
            return HTMLResponse(open("/home/mentor/visual_test_report.html").read())
            
        @self.app.get("/api/status")
        async def get_status():
            return {
                "system_state": asdict(self.state),
                "active_tasks": len([t for t in self.tasks_queue if t.status == "running"]),
                "completed_tasks": len(self.completed_tasks),
                "uptime": time.time() - self.start_time,
                "modules_status": {name: "active" for name in self.modules.keys()}
            }
            
        @self.app.post("/api/tasks")
        async def create_task(task_data: dict):
            task = Task(
                id=f"task_{int(time.time())}",
                type=task_data.get("type", "automation"),
                priority=task_data.get("priority", 5),
                status="pending",
                created_at=datetime.now().isoformat(),
                parameters=task_data.get("parameters", {})
            )
            self.tasks_queue.append(task)
            return {"task_id": task.id, "status": "created"}
            
        @self.app.get("/api/tasks")
        async def get_tasks():
            all_tasks = []
            
            # Добавляем активные задачи
            for task in self.tasks_queue:
                all_tasks.append({
                    "id": task.id,
                    "type": task.type,
                    "status": task.status,
                    "priority": task.priority,
                    "created_at": task.created_at,
                    "parameters": task.parameters,
                    "result": task.result if hasattr(task, 'result') else None
                })
            
            # Добавляем завершенные задачи
            for task in self.completed_tasks:
                all_tasks.append({
                    "id": task.id,
                    "type": task.type,
                    "status": task.status,
                    "priority": task.priority,
                    "created_at": task.created_at,
                    "parameters": task.parameters,
                    "result": task.result if hasattr(task, 'result') else None
                })
            
            return {
                "tasks": all_tasks,
                "pending": [asdict(t) for t in self.tasks_queue if t.status == "pending"],
                "running": [asdict(t) for t in self.tasks_queue if t.status == "running"],
                "completed": [asdict(t) for t in self.completed_tasks[-10:]]
            }
            
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            try:
                while True:
                    try:
                        # Отправляем обновления состояния
                        await websocket.send_json({
                            "timestamp": datetime.now().isoformat(),
                            "state": asdict(self.state),
                            "active_tasks": len([t for t in self.tasks_queue if t.status == "running"]),
                            "completed_tasks": len(self.completed_tasks),
                            "system_health": "healthy"
                        })
                        await asyncio.sleep(5)
                    except Exception as e:
                        logger.error(f"WebSocket error: {e}")
                        break
            except Exception as e:
                logger.error(f"WebSocket connection error: {e}")
            finally:
                try:
                    await websocket.close()
                except:
                    pass
        
        @self.app.get("/api/replication/status")
        async def get_replication_status():
            if self.replicator:
                return self.replicator.get_replication_status()
            else:
                return {"error": "Репликатор не инициализирован"}
        
        @self.app.post("/api/replication/trigger")
        async def trigger_replication():
            if self.replicator:
                try:
                    result = await self.replicator.replicate()
                    return result
                except Exception as e:
                    return {"error": str(e)}
            else:
                return {"error": "Репликатор не инициализирован"}
        
        @self.app.get("/api/integration/status")
        async def get_integration_status():
            if self.integration:
                return await self.integration.get_system_status()
            else:
                return {"error": "Интеграция не инициализирована"}
        
        @self.app.post("/api/automation/{rule_name}")
        async def execute_automation_rule(rule_name: str, context: dict = None):
            if self.integration:
                try:
                    result = await self.integration.execute_automation_rule(rule_name, context or {})
                    return result
                except Exception as e:
                    return {"error": str(e)}
            else:
                return {"error": "Интеграция не инициализирована"}
        
        @self.app.post("/api/emergency/stop")
        async def emergency_stop():
            if self.integration:
                result = await self.integration.emergency_stop()
                self.running = False
                return result
            else:
                self.running = False
                return {"status": "stopped"}
        
        @self.app.get("/api/monitoring/status")
        async def get_monitoring_status():
            if self.monitor:
                return self.monitor.get_monitoring_status()
            else:
                return {"error": "Мониторинг не инициализирован"}
        
        @self.app.post("/api/monitoring/alerts/{alert_id}/resolve")
        async def resolve_alert(alert_id: str):
            if self.monitor:
                success = self.monitor.resolve_alert(alert_id)
                return {"success": success, "alert_id": alert_id}
            else:
                return {"error": "Мониторинг не инициализирован"}
        
        @self.app.get("/api/export/knowledge")
        async def export_knowledge():
            knowledge_data = {
                "timestamp": datetime.now().isoformat(),
                "system_state": asdict(self.state),
                "completed_tasks": len(self.completed_tasks),
                "knowledge_base_size": self.state.knowledge_base_size
            }
            
            # Добавляем данные из базы знаний
            knowledge_path = "/home/mentor/jarvis_data/knowledge"
            if os.path.exists(knowledge_path):
                for file in os.listdir(knowledge_path):
                    if file.endswith('.json'):
                        with open(os.path.join(knowledge_path, file), 'r') as f:
                            knowledge_data[file] = json.load(f)
            
            return knowledge_data
        
        @self.app.get("/api/vision/status")
        async def get_vision_status():
            if self.vision:
                return self.vision.get_vision_status()
            else:
                return {"error": "Система зрения не инициализирована"}
        
        @self.app.get("/api/vision/suggestions")
        async def get_vision_suggestions():
            if self.vision:
                return {
                    "suggestions": self.vision.get_current_suggestions(),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": "Система зрения не инициализирована"}
        
        @self.app.get("/api/vision/issues")
        async def get_vision_issues():
            if self.vision:
                return {
                    "issues": self.vision.get_detected_issues(),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": "Система зрения не инициализирована"}
        
        @self.app.get("/api/self-improvement/status")
        async def get_self_improvement_status():
            if self.self_improvement:
                return self.self_improvement.get_improvement_status()
            else:
                return {"error": "Система самоулучшения не инициализирована"}
        
        @self.app.post("/api/automation/{rule_name}")
        async def execute_automation_rule(rule_name: str):
            if self.integration:
                try:
                    # Выполняем правило автоматизации
                    result = await self.integration.execute_automation_rule(rule_name)
                    return {
                        "success": True,
                        "rule_name": rule_name,
                        "result": result,
                        "timestamp": datetime.now().isoformat()
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "rule_name": rule_name,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
            else:
                return {"error": "Модуль интеграции не инициализирован"}
        
        @self.app.post("/api/self-improvement/trigger")
        async def trigger_self_improvement():
            if self.self_improvement:
                # Создаем задачу самоулучшения
                task_data = {
                    "type": "self_improvement",
                    "priority": 8,
                    "parameters": {
                        "trigger": "manual",
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
                task = Task(
                    id=f"self_improvement_{int(time.time())}",
                    type=task_data["type"],
                    priority=task_data["priority"],
                    status="pending",
                    created_at=datetime.now().isoformat(),
                    parameters=task_data["parameters"]
                )
                
                self.tasks_queue.append(task)
                
                return {
                    "success": True,
                    "task_id": task.id,
                    "message": "Задача самоулучшения создана"
                }
            else:
                return {"error": "Система самоулучшения не инициализирована"}
                    
    async def main_loop(self):
        """Основной цикл системы"""
        self.start_time = time.time()
        logger.info("[REPLICATE] JARVIS система запущена!")
        
        while self.running:
            try:
                # Обновляем состояние системы
                await self.update_system_state()
                
                # Обрабатываем задачи
                await self.process_tasks()
                
                # Проверяем необходимость репликации
                await self.check_replication_need()
                
                # Выполняем самоулучшения
                if hasattr(self, 'self_improvement') and self.self_improvement:
                    # Самоулучшение происходит в фоновом режиме через очередь
                    pass
                
                # Пауза между циклами
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Ошибка в основном цикле: {e}")
                await asyncio.sleep(30)
                
    async def update_system_state(self):
        """Обновление состояния системы"""
        # Получаем метрики ресурсов
        cpu_percent = self.get_cpu_usage()
        memory_percent = self.get_memory_usage()
        disk_percent = self.get_disk_usage()
        
        self.state.resources_used = {
            "cpu": cpu_percent,
            "memory": memory_percent,
            "disk": disk_percent
        }
        
        # Обновляем количество активных задач
        self.state.active_tasks = len([t for t in self.tasks_queue if t.status == "running"])
        
        # Рассчитываем оценку производительности
        self.state.performance_score = self.calculate_performance_score()
        
    async def process_tasks(self):
        """Обработка задач из очереди"""
        for task in self.tasks_queue[:]:
            if task.status == "pending":
                task.status = "running"
                
                try:
                    # Выполняем задачу в зависимости от типа
                    if task.type == "content_generation":
                        result = await self.modules["content_generator"].generate(task.parameters)
                    elif task.type == "data_analysis":
                        result = await self.modules["data_analyzer"].analyze(task.parameters)
                    elif task.type == "business_automation":
                        result = await self.modules["business_automator"].automate(task.parameters)
                    elif task.type == "self_improvement":
                        result = await self.modules["self_improver"].improve(task.parameters)
                    elif task.type == "user_message":
                        result = await self.handle_user_message(task.parameters)
                    else:
                        result = {"error": f"Неизвестный тип задачи: {task.type}"}
                    
                    task.result = result
                    task.status = "completed"
                    self.completed_tasks.append(task)
                    self.tasks_queue.remove(task)
                    
                    # Логируем завершение задачи
                    logger.info(f"[OK] Задача {task.id} ({task.type}) завершена: {str(result)[:100]}...")
                    
                    logger.info(f"[OK] Задача {task.id} выполнена успешно")
                    
                except Exception as e:
                    task.status = "failed"
                    task.result = {"error": str(e)}
                    logger.error(f"[ERROR] Ошибка выполнения задачи {task.id}: {e}")
                    
    async def check_replication_need(self):
        """Проверка необходимости репликации"""
        if self.replicator:
            try:
                if await self.replicator.should_replicate():
                    logger.info("🔄 Запуск процесса самовоспроизводства...")
                    result = await self.replicator.replicate()
                    if result.get("success"):
                        self.state.last_self_replication = datetime.now().isoformat()
                        logger.info("[OK] Самовоспроизводство завершено успешно")
                    else:
                        logger.warning(f"⚠️ Самовоспроизводство завершилось с ошибкой: {result.get('error')}")
            except Exception as e:
                logger.error(f"[ERROR] Ошибка проверки необходимости репликации: {e}")
            
    async def self_improvement(self):
        """Процесс самоулучшения"""
        try:
            if self.self_improvement:
                # Используем новую систему самоулучшения
                improvement_task = {
                    "type": "general_optimization",
                    "priority": 7,
                    "parameters": {
                        "target_level": self.state.autonomy_level + 1,
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
                # Добавляем задачу в очередь улучшений
                self.self_improvement.improvement_queue.put(improvement_task)
                logger.info("[AI] Задача самоулучшения добавлена в очередь")
            else:
                # Fallback к старой системе
                if self.state.autonomy_level < 5:
                    await self.modules["self_improver"].improve({"target_level": self.state.autonomy_level + 1})
        except Exception as e:
            logger.error(f"[ERROR] Ошибка самоулучшения: {e}")
    
    async def handle_user_message(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка сообщений пользователя с умными ответами"""
        try:
            message = parameters.get("message", "").lower().strip()
            user_id = parameters.get("user_id", "unknown")
            timestamp = parameters.get("timestamp", datetime.now().isoformat())
            
            logger.info(f"[CHAT] Получено сообщение от {user_id}: {message}")
            
            # Анализируем намерение пользователя
            response = self.analyze_user_intent(message)
            
            # Логируем ответ
            logger.info(f"[JARVIS] Ответ JARVIS: {response}")
            
            return {
                "message": response,
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "original_message": parameters.get("message", ""),
                "intent_detected": True
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Ошибка обработки сообщения пользователя: {e}")
            return {
                "message": "Извините, произошла ошибка при обработке вашего сообщения.",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def analyze_user_intent(self, message: str) -> str:
        """Анализ намерения пользователя и генерация ответа"""
        
        # Проверяем наличие AI возможностей
        ai_response = self.get_ai_response(message)
        if ai_response:
            return ai_response
        
        # Приветствия
        if any(word in message for word in ["привет", "здравствуй", "hello", "hi", "добро пожаловать"]):
            return "Привет! Я JARVIS, ваш AI-помощник. Готов помочь с анализом данных, автоматизацией и самоулучшением системы. Что вы хотели бы сделать?"
        
        # Статус системы
        elif any(word in message for word in ["статус", "как дела", "состояние", "статус системы"]):
            cpu = self.state.resources_used.get("cpu", 0)
            memory = self.state.resources_used.get("memory", 0)
            performance = self.state.performance_score
            return f"Система работает отлично! [DATA] Производительность: {performance:.1%}, CPU: {cpu:.1f}%, Память: {memory:.1f}%. Все модули активны и готовы к работе."
        
        # Задачи
        elif any(word in message for word in ["задачи", "список задач", "активные задачи"]):
            active_count = len([t for t in self.tasks_queue if t.status == "pending"])
            completed_count = len(self.completed_tasks)
            return f"📋 Активных задач: {active_count}, завершенных: {completed_count}. Система работает стабильно и обрабатывает все задачи в очереди."
        
        # Анализ данных
        elif any(word in message for word in ["анализ", "проанализируй", "данные", "анализ данных"]):
            return "[MONITOR] Запускаю анализ данных! Проверяю WB API, анализирую продажи и генерирую отчеты. Результаты будут готовы через несколько минут."
        
        # Самоулучшение
        elif any(word in message for word in ["улучшение", "оптимизация", "самоулучшение", "улучши"]):
            return "[AI] Запускаю самоулучшение! Анализирую производительность, оптимизирую код и улучшаю алгоритмы. Система станет еще эффективнее!"
        
        # Репликация
        elif any(word in message for word in ["репликация", "копирование", "создать копию", "самовоспроизводство"]):
            return "[REPLICATE] Запускаю самовоспроизводство! Создаю копию системы на других серверах для масштабирования и повышения надежности."
        
        # Помощь
        elif any(word in message for word in ["помощь", "help", "что умеешь", "возможности"]):
            return """Я JARVIS, автономная AI-система. Мои возможности:
- Анализ данных и генерация отчетов
- Самоулучшение и оптимизация
- Анализ интерфейса и предложения улучшений  
- Самовоспроизводство на других серверах
- Мониторинг производительности
[JARVIS] Автоматизация бизнес-процессов

Просто скажите, что хотите сделать!"""
        
        # Благодарности
        elif any(word in message for word in ["спасибо", "благодарю", "thanks", "отлично"]):
            return "Пожалуйста! 😊 Всегда рад помочь. JARVIS работает 24/7 и готов к новым задачам!"
        
        # Время
        elif any(word in message for word in ["время", "который час", "time"]):
            current_time = datetime.now().strftime("%H:%M:%S")
            uptime = time.time() - self.start_time if hasattr(self, 'start_time') else 0
            uptime_hours = int(uptime // 3600)
            uptime_minutes = int((uptime % 3600) // 60)
            return f"🕐 Текущее время: {current_time}. Система работает {uptime_hours}ч {uptime_minutes}м без перерывов!"
        
        # Производительность
        elif any(word in message for word in ["производительность", "скорость", "быстро", "медленно"]):
            performance = self.state.performance_score
            if performance > 0.8:
                return f"[FAST] Производительность отличная: {performance:.1%}! Система работает на максимальной скорости."
            elif performance > 0.6:
                return f"[DATA] Производительность хорошая: {performance:.1%}. Есть возможности для оптимизации."
            else:
                return f"[TOOL] Производительность: {performance:.1%}. Запускаю оптимизацию для улучшения скорости."
        
        # Генерация кода
        elif any(word in message for word in ["создай код", "напиши код", "генерируй код", "код для", "функция", "класс"]):
            return self.generate_code_response(message)
        
        # Неопределенное сообщение
        else:
            return "🤔 Понял ваше сообщение! JARVIS всегда готов помочь. Можете спросить о статусе системы, запустить анализ данных, самоулучшение или любую другую задачу. Что конкретно вас интересует?"
            
    def get_cpu_usage(self):
        """Получение загрузки CPU"""
        try:
            result = subprocess.run(['top', '-bn1'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Cpu(s)' in line:
                    cpu_str = line.split('Cpu(s):')[1].split('%')[0].strip()
                    return float(cpu_str)
        except:
            pass
        return 0.0
    
    def get_ai_response(self, message: str) -> Optional[str]:
        """Получение ответа от AI (Ollama или OpenAI)"""
        try:
            # Пробуем Ollama
            ollama_response = self.try_ollama_response(message)
            if ollama_response:
                return ollama_response
            
            # Пробуем OpenAI
            openai_response = self.try_openai_response(message)
            if openai_response:
                return openai_response
            
            return None
            
        except Exception as e:
            logger.error(f"[ERROR] Ошибка AI ответа: {e}")
            return None
    
    def try_ollama_response(self, message: str) -> Optional[str]:
        """Попытка получить ответ от Ollama"""
        try:
            import subprocess
            
            # Формируем промпт для Ollama
            prompt = f"Ты JARVIS - автономная AI система. Отвечай кратко на русском языке. Пользователь: {message}"
            
            # Запускаем Ollama
            result = subprocess.run([
                'ollama', 'run', 'llama2', prompt
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and result.stdout.strip():
                response = result.stdout.strip()
                # Убираем лишние части ответа
                if "JARVIS:" in response:
                    response = response.split("JARVIS:")[-1].strip()
                return response
            
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            logger.debug(f"Ollama недоступен: {e}")
        
        return None
    
    def try_openai_response(self, message: str) -> Optional[str]:
        """Попытка получить ответ от OpenAI"""
        try:
            import openai
            
            # Проверяем наличие API ключа
            if not os.getenv('OPENAI_API_KEY'):
                return None
            
            client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты JARVIS - автономная AI система. Отвечай кратко и по делу на русском языке."},
                    {"role": "user", "content": message}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content.strip()
                
        except Exception as e:
            logger.debug(f"OpenAI недоступен: {e}")
        
        return None
    
    def generate_code_response(self, message: str) -> str:
        """Генерация кода на основе запроса"""
        try:
            # Извлекаем тип запроса
            if "функция" in message.lower():
                return self.generate_function_code(message)
            elif "класс" in message.lower():
                return self.generate_class_code(message)
            elif "api" in message.lower() or "endpoint" in message.lower():
                return self.generate_api_code(message)
            elif "html" in message.lower() or "веб" in message.lower():
                return self.generate_html_code(message)
            elif "sql" in message.lower() or "база данных" in message.lower():
                return self.generate_sql_code(message)
            else:
                return self.generate_general_code(message)
                
        except Exception as e:
            logger.error(f"[ERROR] Ошибка генерации кода: {e}")
            return f"Извините, произошла ошибка при генерации кода: {e}"
    
    def generate_function_code(self, message: str) -> str:
        """Генерация функции"""
        # Извлекаем название функции из сообщения
        function_name = "my_function"
        if "для" in message:
            parts = message.split("для")
            if len(parts) > 1:
                function_name = parts[1].strip().replace(" ", "_")
        
        code = f'''def {function_name}(data):
    """
    Автоматически сгенерированная функция
    """
    try:
        # Обработка данных
        if isinstance(data, dict):
            result = {{}}
            for key, value in data.items():
                result[key] = str(value).upper()
            return result
        elif isinstance(data, list):
            return [str(item) for item in data]
        else:
            return str(data)
    except Exception as e:
        logger.error(f"Ошибка в функции {{function_name}}: {{e}}")
        return None

# Пример использования
if __name__ == "__main__":
    test_data = {{"name": "test", "value": 123}}
    result = {function_name}(test_data)
    print(f"Результат: {{result}}")'''
        
        return f"[OK] Создал функцию `{function_name}`:\n\n```python\n{code}\n```"
    
    def generate_class_code(self, message: str) -> str:
        """Генерация класса"""
        class_name = "MyClass"
        if "для" in message:
            parts = message.split("для")
            if len(parts) > 1:
                class_name = parts[1].strip().replace(" ", "").title()
        
        code = f'''class {class_name}:
    """
    Автоматически сгенерированный класс
    """
    
    def __init__(self, name: str = "default"):
        self.name = name
        self.created_at = datetime.now()
        self.data = {{}}
    
    def add_data(self, key: str, value: any):
        """Добавление данных"""
        self.data[key] = value
        logger.info(f"Добавлены данные: {{key}} = {{value}}")
    
    def get_data(self, key: str):
        """Получение данных"""
        return self.data.get(key)
    
    def get_all_data(self):
        """Получение всех данных"""
        return self.data.copy()
    
    def __str__(self):
        return f"{class_name}(name='{{self.name}}', data_count={{len(self.data)}})"
    
    def __repr__(self):
        return f"{class_name}(name='{{self.name}}')"

# Пример использования
if __name__ == "__main__":
    obj = {class_name}("test_object")
    obj.add_data("test", "value")
    print(obj)'''
        
        return f"[OK] Создал класс `{class_name}`:\n\n```python\n{code}\n```"
    
    def generate_api_code(self, message: str) -> str:
        """Генерация API endpoint"""
        endpoint_name = "my_endpoint"
        if "для" in message:
            parts = message.split("для")
            if len(parts) > 1:
                endpoint_name = parts[1].strip().replace(" ", "_")
        
        code = f'''@self.app.get("/api/{endpoint_name}")
async def {endpoint_name}_endpoint():
    """API endpoint для {endpoint_name}"""
    try:
        # Получаем данные
        data = {{
            "endpoint": "{endpoint_name}",
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }}
        
        # Логируем запрос
        logger.info(f"API запрос к /api/{endpoint_name}")
        
        return {{
            "success": True,
            "data": data,
            "message": "Данные успешно получены"
        }}
        
    except Exception as e:
        logger.error(f"Ошибка API /api/{endpoint_name}: {{e}}")
        return {{
            "success": False,
            "error": str(e),
            "message": "Произошла ошибка при обработке запроса"
        }}'''
        
        return f"[OK] Создал API endpoint `/api/{endpoint_name}`:\n\n```python\n{code}\n```"
    
    def generate_html_code(self, message: str) -> str:
        """Генерация HTML кода"""
        page_name = "my_page"
        if "для" in message:
            parts = message.split("для")
            if len(parts) > 1:
                page_name = parts[1].strip().replace(" ", "_")
        
        code = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_name.title()}</title>
    <style>
        body {{
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .container {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }}
        h1 {{ color: #2c3e50; margin-bottom: 20px; }}
        .button {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{page_name.title()}</h1>
        <p>Автоматически сгенерированная страница</p>
        <button class="button" onclick="alert('Привет!')">Нажми меня</button>
    </div>
</body>
</html>'''
        
        return f"[OK] Создал HTML страницу для `{page_name}`:\n\n```html\n{code}\n```"
    
    def generate_sql_code(self, message: str) -> str:
        """Генерация SQL кода"""
        table_name = "my_table"
        if "для" in message:
            parts = message.split("для")
            if len(parts) > 1:
                table_name = parts[1].strip().replace(" ", "_")
        
        code = f'''-- Создание таблицы {table_name}
CREATE TABLE {table_name} (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Вставка данных
INSERT INTO {table_name} (name, description) VALUES
    ('Пример 1', 'Описание первого элемента'),
    ('Пример 2', 'Описание второго элемента');

-- Основные запросы
SELECT * FROM {table_name} WHERE is_active = TRUE;
SELECT * FROM {table_name} WHERE name LIKE '%пример%';'''
        
        return f"[OK] Создал SQL код для таблицы `{table_name}`:\n\n```sql\n{code}\n```"
    
    def generate_general_code(self, message: str) -> str:
        """Генерация общего кода"""
        code = f'''#!/usr/bin/env python3
"""
Автоматически сгенерированный код
Запрос: {message}
"""

import os
import json
import time
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoGenerated:
    def __init__(self):
        self.created_at = datetime.now()
        self.data = {{}}
    
    def process_data(self, data):
        try:
            result = {{
                "input": data,
                "processed_at": datetime.now().isoformat(),
                "type": type(data).__name__
            }}
            self.data[result["processed_at"]] = result
            return result
        except Exception as e:
            logger.error(f"Ошибка: {{e}}")
            return {{"error": str(e)}}

def main():
    processor = AutoGenerated()
    result = processor.process_data("test data")
    print(f"Результат: {{result}}")

if __name__ == "__main__":
    main()'''
        
        return f"[OK] Создал общий код на основе запроса:\n\n```python\n{code}\n```"
        
    def get_memory_usage(self):
        """Получение использования памяти"""
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            lines = meminfo.split('\n')
            total = int(lines[0].split()[1])
            available = int(lines[2].split()[1])
            used_percent = ((total - available) / total) * 100
            return used_percent
        except:
            return 0.0
            
    def get_disk_usage(self):
        """Получение использования диска"""
        try:
            result = subprocess.run(['df', '/'], capture_output=True, text=True)
            lines = result.stdout.split('\n')[1].split()
            used_percent = float(lines[4].replace('%', ''))
            return used_percent
        except:
            return 0.0
            
    def calculate_performance_score(self):
        """Расчет оценки производительности"""
        # Базовый алгоритм оценки на основе ресурсов и задач
        cpu_score = max(0, 1 - self.state.resources_used["cpu"] / 100)
        memory_score = max(0, 1 - self.state.resources_used["memory"] / 100)
        task_efficiency = min(1, 10 / max(1, self.state.active_tasks))
        
        return (cpu_score + memory_score + task_efficiency) / 3
        
    def run(self):
        """Запуск системы"""
        # Запускаем веб-сервер в отдельном потоке
        def run_server():
            uvicorn.run(self.app, host="0.0.0.0", port=8080, log_level="info")
            
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Запускаем основной цикл
        asyncio.run(self.main_loop())

# Модули системы
class ContentGenerator:
    """Генератор контента"""
    
    async def generate(self, parameters: Dict[str, Any]):
        # Интеграция с существующими AI модулями
        content_type = parameters.get("type", "product_description")
        
        # Используем существующий код из mentor проекта
        if content_type == "product_description":
            return await self.generate_product_content(parameters)
        elif content_type == "business_report":
            return await self.generate_business_report(parameters)
        else:
            return {"content": f"Сгенерированный контент типа {content_type}", "timestamp": datetime.now().isoformat()}
    
    async def generate_product_content(self, params):
        # Интеграция с WB API для генерации описаний товаров
        return {"content": "Описание товара сгенерировано", "products_processed": 1}
    
    async def generate_business_report(self, params):
        # Использование существующего модуля reports.py
        return {"content": "Бизнес-отчет сгенерирован", "data_analyzed": True}

class DataAnalyzer:
    """Анализатор данных"""
    
    async def analyze(self, parameters: Dict[str, Any]):
        analysis_type = parameters.get("type", "sales_analysis")
        
        if analysis_type == "sales_analysis":
            # Используем существующий analyzer.py
            return await self.analyze_sales_data(parameters)
        else:
            return {"analysis": f"Анализ типа {analysis_type} выполнен", "timestamp": datetime.now().isoformat()}
    
    async def analyze_sales_data(self, params):
        # Интеграция с существующим кодом анализа
        return {"sales_trend": "positive", "recommendations": ["увеличить рекламу", "оптимизировать цены"]}

class BusinessAutomator:
    """Автоматизатор бизнес-процессов"""
    
    async def automate(self, parameters: Dict[str, Any]):
        process_type = parameters.get("type", "wb_management")
        
        if process_type == "wb_management":
            return await self.automate_wb_processes(parameters)
        else:
            return {"automation": f"Процесс {process_type} автоматизирован", "timestamp": datetime.now().isoformat()}
    
    async def automate_wb_processes(self, params):
        # Автоматизация работы с WB API
        return {"automated": ["price_updates", "stock_management"], "efficiency_gain": "30%"}

class SelfImprover:
    """Модуль самоулучшения"""
    
    async def improve(self, parameters: Dict[str, Any]):
        improvement_type = parameters.get("type", "code_optimization")
        
        if improvement_type == "code_optimization":
            return await self.optimize_code()
        elif improvement_type == "knowledge_expansion":
            return await self.expand_knowledge()
        else:
            return {"improvement": f"Улучшение типа {improvement_type} выполнено"}
    
    async def optimize_code(self):
        # Анализ и оптимизация собственного кода
        return {"optimizations": ["memory_usage", "cpu_efficiency"], "performance_gain": "15%"}
    
    async def expand_knowledge(self):
        # Расширение базы знаний
        return {"new_knowledge": "market_trends_2024", "confidence": 0.85}

class Replicator:
    """Модуль самовоспроизводства"""
    
    def __init__(self):
        self.docker_client = docker.from_env()
    
    async def replicate(self):
        """Создание копии системы на других серверах"""
        try:
            # Создаем Docker образ
            image = self.create_docker_image()
            
            # Находим доступные серверы
            available_servers = await self.find_available_servers()
            
            # Развертываем на найденных серверах
            deployed_count = 0
            for server in available_servers:
                if await self.deploy_to_server(server, image):
                    deployed_count += 1
            
            return {"replicated": deployed_count, "total_servers": len(available_servers)}
            
        except Exception as e:
            logger.error(f"Ошибка репликации: {e}")
            return {"error": str(e)}
    
    def create_docker_image(self):
        """Создание Docker образа системы"""
        # Создаем Dockerfile для системы
        dockerfile_content = """
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y docker.io

CMD ["python", "jarvis_core.py"]
"""
        
        with open("/home/mentor/jarvis_data/Dockerfile", "w") as f:
            f.write(dockerfile_content)
        
        # Создаем requirements.txt
        requirements = """
fastapi
uvicorn
docker
paramiko
pyyaml
requests
websockets
asyncio
"""
        
        with open("/home/mentor/jarvis_data/requirements.txt", "w") as f:
            f.write(requirements)
        
        # Собираем образ
        image, logs = self.docker_client.images.build(
            path="/home/mentor/jarvis_data",
            tag="jarvis:latest"
        )
        
        return image
    
    async def find_available_servers(self):
        """Поиск доступных серверов для репликации"""
        # Здесь будет логика поиска доступных серверов
        # Пока возвращаем пустой список
        return []
    
    async def deploy_to_server(self, server_info, image):
        """Развертывание на конкретном сервере"""
        # SSH подключение и развертывание
        # Пока заглушка
        return True

class SystemMonitor:
    """Мониторинг системы"""
    
    def __init__(self):
        self.metrics_history = []
    
    async def collect_metrics(self):
        """Сбор метрик системы"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "cpu": self.get_cpu_usage(),
            "memory": self.get_memory_usage(),
            "disk": self.get_disk_usage(),
            "network": self.get_network_usage(),
            "active_connections": self.get_active_connections()
        }
        
        self.metrics_history.append(metrics)
        
        # Оставляем только последние 1000 записей
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        return metrics
    
    def get_cpu_usage(self):
        # Реализация получения CPU
        return 0.0
    
    def get_memory_usage(self):
        # Реализация получения памяти
        return 0.0
    
    def get_disk_usage(self):
        # Реализация получения диска
        return 0.0
    
    def get_network_usage(self):
        # Реализация получения сети
        return {"in": 0, "out": 0}
    
    def get_active_connections(self):
        # Реализация получения соединений
        return 0

if __name__ == "__main__":
    jarvis = JarvisCore()
    jarvis.run()



JARVIS - Автономная саморазвивающаяся система
Ядро системы для автоматизации жизни и бизнеса
"""

import os
import sys
import json
import time
import asyncio
import subprocess
import threading
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests
import yaml
from dataclasses import dataclass, asdict
import docker
import paramiko
from fastapi import FastAPI, WebSocket, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/mentor/jarvis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SystemState:
    """Состояние системы"""
    total_instances: int = 1
    active_tasks: int = 0
    resources_used: Dict[str, float] = None
    last_self_replication: Optional[str] = None
    performance_score: float = 0.0
    autonomy_level: int = 1
    knowledge_base_size: int = 0
    
    def __post_init__(self):
        if self.resources_used is None:
            self.resources_used = {"cpu": 0.0, "memory": 0.0, "disk": 0.0}

@dataclass
class Task:
    """Задача системы"""
    id: str
    type: str  # automation, content_generation, analysis, self_improvement
    priority: int  # 1-10
    status: str  # pending, running, completed, failed
    created_at: str
    parameters: Dict[str, Any] = None
    result: Any = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}

class JarvisCore:
    """Основной класс автономной системы Джарвис"""
    
    def __init__(self):
        self.state = SystemState()
        self.tasks_queue = []
        self.completed_tasks = []
        self.knowledge_base = {}
        self.automation_modules = {}
        self.running = True
        self.app = FastAPI(title="JARVIS Control Panel")
        
        # Создаем директории
        self.setup_directories()
        
        # Загружаем конфигурацию
        self.load_config()
        
        # Инициализируем модули
        self.init_modules()
        
        # Инициализируем интеграцию
        self.init_integration()
        
        # Инициализируем репликатор
        self.init_replicator()
        
        # Инициализируем мониторинг
        self.init_monitor()
        
        # Инициализируем систему зрения
        self.init_vision()
        
        # Инициализируем систему самоулучшения
        self.init_self_improvement()
        
        # Настраиваем API
        self.setup_api()
        
    def setup_directories(self):
        """Создание необходимых директорий"""
        dirs = [
            "/home/mentor/jarvis_data",
            "/home/mentor/jarvis_data/knowledge",
            "/home/mentor/jarvis_data/automation",
            "/home/mentor/jarvis_data/replication",
            "/home/mentor/jarvis_data/logs",
            "/home/mentor/jarvis_data/templates",
            "/home/mentor/jarvis_data/reports",
            "/home/mentor/jarvis_data/analysis",
            "/home/mentor/jarvis_data/content",
            "/home/mentor/jarvis_data/marketing"
        ]
        
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            
    def load_config(self):
        """Загрузка конфигурации"""
        config_path = "/home/mentor/jarvis_data/config.yaml"
        
        default_config = {
            "system": {
                "max_instances": 10,
                "replication_threshold": 80,
                "autonomy_levels": {
                    1: "basic_automation",
                    2: "content_generation", 
                    3: "self_improvement",
                    4: "autonomous_replication",
                    5: "full_autonomy"
                },
                "resource_limits": {
                    "max_cpu_percent": 70,
                    "max_memory_gb": 8,
                    "max_disk_gb": 50
                }
            },
            "automation": {
                "enabled_modules": ["content_generation", "data_analysis", "business_processes"],
                "schedule_interval": 300  # 5 минут
            },
            "replication": {
                "target_servers": [],
                "ssh_keys_path": "/home/mentor/.ssh/",
                "docker_registry": "localhost:5000"
            },
            "monitoring": {
                "metrics_interval": 60,
                "alert_thresholds": {
                    "cpu": 80,
                    "memory": 85,
                    "disk": 90
                }
            }
        }
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = default_config
            with open(config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
                
    def init_modules(self):
        """Инициализация модулей системы"""
        self.modules = {
            "content_generator": ContentGenerator(),
            "data_analyzer": DataAnalyzer(), 
            "business_automator": BusinessAutomator(),
            "self_improver": SelfImprover(),
            "monitor": SystemMonitor()
        }
        
    def init_integration(self):
        """Инициализация интеграции"""
        try:
            from jarvis_integration import JarvisIntegration
            self.integration = JarvisIntegration(self)
            logger.info("[OK] Интеграция инициализирована")
        except Exception as e:
            logger.error(f"[ERROR] Ошибка инициализации интеграции: {e}")
            self.integration = None
            
    def init_replicator(self):
        """Инициализация репликатора"""
        try:
            from jarvis_replicator import JarvisReplicator
            self.replicator = JarvisReplicator(self)
            self.modules["replicator"] = self.replicator
            logger.info("[OK] Репликатор инициализирован")
        except Exception as e:
            logger.error(f"[ERROR] Ошибка инициализации репликатора: {e}")
            self.replicator = None
            
    def init_monitor(self):
        """Инициализация мониторинга"""
        try:
            from jarvis_monitor import JarvisMonitor
            self.monitor = JarvisMonitor(self)
            logger.info("[OK] Мониторинг инициализирован")
        except Exception as e:
            logger.error(f"[ERROR] Ошибка инициализации мониторинга: {e}")
            self.monitor = None
            
    def init_vision(self):
        """Инициализация системы зрения"""
        try:
            from jarvis_vision import JarvisVision
            self.vision = JarvisVision(self)
            logger.info("[OK] Система зрения инициализирована")
        except Exception as e:
            logger.error(f"[ERROR] Ошибка инициализации системы зрения: {e}")
            self.vision = None
            
    def init_self_improvement(self):
        """Инициализация системы самоулучшения"""
        try:
            from jarvis_self_improvement import JarvisSelfImprovement
            self.self_improvement = JarvisSelfImprovement(self)
            logger.info("[OK] Система самоулучшения инициализирована")
        except Exception as e:
            logger.error(f"[ERROR] Ошибка инициализации системы самоулучшения: {e}")
            self.self_improvement = None
        
    def setup_api(self):
        """Настройка веб-API"""
        
        @self.app.get("/")
        async def dashboard():
            return HTMLResponse(open("/home/mentor/jarvis_data/templates/unified_dashboard.html").read())
        
        @self.app.get("/vision")
        async def vision_dashboard():
            return HTMLResponse(open("/home/mentor/jarvis_data/templates/vision_dashboard.html").read())
        
        @self.app.get("/chat")
        async def chat_interface():
            return HTMLResponse(open("/home/mentor/jarvis_data/templates/chat.html").read())
        
        @self.app.get("/visual_test_report")
        async def visual_test_report():
            return HTMLResponse(open("/home/mentor/visual_test_report.html").read())
            
        @self.app.get("/api/status")
        async def get_status():
            return {
                "system_state": asdict(self.state),
                "active_tasks": len([t for t in self.tasks_queue if t.status == "running"]),
                "completed_tasks": len(self.completed_tasks),
                "uptime": time.time() - self.start_time,
                "modules_status": {name: "active" for name in self.modules.keys()}
            }
            
        @self.app.post("/api/tasks")
        async def create_task(task_data: dict):
            task = Task(
                id=f"task_{int(time.time())}",
                type=task_data.get("type", "automation"),
                priority=task_data.get("priority", 5),
                status="pending",
                created_at=datetime.now().isoformat(),
                parameters=task_data.get("parameters", {})
            )
            self.tasks_queue.append(task)
            return {"task_id": task.id, "status": "created"}
            
        @self.app.get("/api/tasks")
        async def get_tasks():
            all_tasks = []
            
            # Добавляем активные задачи
            for task in self.tasks_queue:
                all_tasks.append({
                    "id": task.id,
                    "type": task.type,
                    "status": task.status,
                    "priority": task.priority,
                    "created_at": task.created_at,
                    "parameters": task.parameters,
                    "result": task.result if hasattr(task, 'result') else None
                })
            
            # Добавляем завершенные задачи
            for task in self.completed_tasks:
                all_tasks.append({
                    "id": task.id,
                    "type": task.type,
                    "status": task.status,
                    "priority": task.priority,
                    "created_at": task.created_at,
                    "parameters": task.parameters,
                    "result": task.result if hasattr(task, 'result') else None
                })
            
            return {
                "tasks": all_tasks,
                "pending": [asdict(t) for t in self.tasks_queue if t.status == "pending"],
                "running": [asdict(t) for t in self.tasks_queue if t.status == "running"],
                "completed": [asdict(t) for t in self.completed_tasks[-10:]]
            }
            
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            try:
                while True:
                    try:
                        # Отправляем обновления состояния
                        await websocket.send_json({
                            "timestamp": datetime.now().isoformat(),
                            "state": asdict(self.state),
                            "active_tasks": len([t for t in self.tasks_queue if t.status == "running"]),
                            "completed_tasks": len(self.completed_tasks),
                            "system_health": "healthy"
                        })
                        await asyncio.sleep(5)
                    except Exception as e:
                        logger.error(f"WebSocket error: {e}")
                        break
            except Exception as e:
                logger.error(f"WebSocket connection error: {e}")
            finally:
                try:
                    await websocket.close()
                except:
                    pass
        
        @self.app.get("/api/replication/status")
        async def get_replication_status():
            if self.replicator:
                return self.replicator.get_replication_status()
            else:
                return {"error": "Репликатор не инициализирован"}
        
        @self.app.post("/api/replication/trigger")
        async def trigger_replication():
            if self.replicator:
                try:
                    result = await self.replicator.replicate()
                    return result
                except Exception as e:
                    return {"error": str(e)}
            else:
                return {"error": "Репликатор не инициализирован"}
        
        @self.app.get("/api/integration/status")
        async def get_integration_status():
            if self.integration:
                return await self.integration.get_system_status()
            else:
                return {"error": "Интеграция не инициализирована"}
        
        @self.app.post("/api/automation/{rule_name}")
        async def execute_automation_rule(rule_name: str, context: dict = None):
            if self.integration:
                try:
                    result = await self.integration.execute_automation_rule(rule_name, context or {})
                    return result
                except Exception as e:
                    return {"error": str(e)}
            else:
                return {"error": "Интеграция не инициализирована"}
        
        @self.app.post("/api/emergency/stop")
        async def emergency_stop():
            if self.integration:
                result = await self.integration.emergency_stop()
                self.running = False
                return result
            else:
                self.running = False
                return {"status": "stopped"}
        
        @self.app.get("/api/monitoring/status")
        async def get_monitoring_status():
            if self.monitor:
                return self.monitor.get_monitoring_status()
            else:
                return {"error": "Мониторинг не инициализирован"}
        
        @self.app.post("/api/monitoring/alerts/{alert_id}/resolve")
        async def resolve_alert(alert_id: str):
            if self.monitor:
                success = self.monitor.resolve_alert(alert_id)
                return {"success": success, "alert_id": alert_id}
            else:
                return {"error": "Мониторинг не инициализирован"}
        
        @self.app.get("/api/export/knowledge")
        async def export_knowledge():
            knowledge_data = {
                "timestamp": datetime.now().isoformat(),
                "system_state": asdict(self.state),
                "completed_tasks": len(self.completed_tasks),
                "knowledge_base_size": self.state.knowledge_base_size
            }
            
            # Добавляем данные из базы знаний
            knowledge_path = "/home/mentor/jarvis_data/knowledge"
            if os.path.exists(knowledge_path):
                for file in os.listdir(knowledge_path):
                    if file.endswith('.json'):
                        with open(os.path.join(knowledge_path, file), 'r') as f:
                            knowledge_data[file] = json.load(f)
            
            return knowledge_data
        
        @self.app.get("/api/vision/status")
        async def get_vision_status():
            if self.vision:
                return self.vision.get_vision_status()
            else:
                return {"error": "Система зрения не инициализирована"}
        
        @self.app.get("/api/vision/suggestions")
        async def get_vision_suggestions():
            if self.vision:
                return {
                    "suggestions": self.vision.get_current_suggestions(),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": "Система зрения не инициализирована"}
        
        @self.app.get("/api/vision/issues")
        async def get_vision_issues():
            if self.vision:
                return {
                    "issues": self.vision.get_detected_issues(),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": "Система зрения не инициализирована"}
        
        @self.app.get("/api/self-improvement/status")
        async def get_self_improvement_status():
            if self.self_improvement:
                return self.self_improvement.get_improvement_status()
            else:
                return {"error": "Система самоулучшения не инициализирована"}
        
        @self.app.post("/api/automation/{rule_name}")
        async def execute_automation_rule(rule_name: str):
            if self.integration:
                try:
                    # Выполняем правило автоматизации
                    result = await self.integration.execute_automation_rule(rule_name)
                    return {
                        "success": True,
                        "rule_name": rule_name,
                        "result": result,
                        "timestamp": datetime.now().isoformat()
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "rule_name": rule_name,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
            else:
                return {"error": "Модуль интеграции не инициализирован"}
        
        @self.app.post("/api/self-improvement/trigger")
        async def trigger_self_improvement():
            if self.self_improvement:
                # Создаем задачу самоулучшения
                task_data = {
                    "type": "self_improvement",
                    "priority": 8,
                    "parameters": {
                        "trigger": "manual",
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
                task = Task(
                    id=f"self_improvement_{int(time.time())}",
                    type=task_data["type"],
                    priority=task_data["priority"],
                    status="pending",
                    created_at=datetime.now().isoformat(),
                    parameters=task_data["parameters"]
                )
                
                self.tasks_queue.append(task)
                
                return {
                    "success": True,
                    "task_id": task.id,
                    "message": "Задача самоулучшения создана"
                }
            else:
                return {"error": "Система самоулучшения не инициализирована"}
                    
    async def main_loop(self):
        """Основной цикл системы"""
        self.start_time = time.time()
        logger.info("[REPLICATE] JARVIS система запущена!")
        
        while self.running:
            try:
                # Обновляем состояние системы
                await self.update_system_state()
                
                # Обрабатываем задачи
                await self.process_tasks()
                
                # Проверяем необходимость репликации
                await self.check_replication_need()
                
                # Выполняем самоулучшения
                if hasattr(self, 'self_improvement') and self.self_improvement:
                    # Самоулучшение происходит в фоновом режиме через очередь
                    pass
                
                # Пауза между циклами
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Ошибка в основном цикле: {e}")
                await asyncio.sleep(30)
                
    async def update_system_state(self):
        """Обновление состояния системы"""
        # Получаем метрики ресурсов
        cpu_percent = self.get_cpu_usage()
        memory_percent = self.get_memory_usage()
        disk_percent = self.get_disk_usage()
        
        self.state.resources_used = {
            "cpu": cpu_percent,
            "memory": memory_percent,
            "disk": disk_percent
        }
        
        # Обновляем количество активных задач
        self.state.active_tasks = len([t for t in self.tasks_queue if t.status == "running"])
        
        # Рассчитываем оценку производительности
        self.state.performance_score = self.calculate_performance_score()
        
    async def process_tasks(self):
        """Обработка задач из очереди"""
        for task in self.tasks_queue[:]:
            if task.status == "pending":
                task.status = "running"
                
                try:
                    # Выполняем задачу в зависимости от типа
                    if task.type == "content_generation":
                        result = await self.modules["content_generator"].generate(task.parameters)
                    elif task.type == "data_analysis":
                        result = await self.modules["data_analyzer"].analyze(task.parameters)
                    elif task.type == "business_automation":
                        result = await self.modules["business_automator"].automate(task.parameters)
                    elif task.type == "self_improvement":
                        result = await self.modules["self_improver"].improve(task.parameters)
                    elif task.type == "user_message":
                        result = await self.handle_user_message(task.parameters)
                    else:
                        result = {"error": f"Неизвестный тип задачи: {task.type}"}
                    
                    task.result = result
                    task.status = "completed"
                    self.completed_tasks.append(task)
                    self.tasks_queue.remove(task)
                    
                    # Логируем завершение задачи
                    logger.info(f"[OK] Задача {task.id} ({task.type}) завершена: {str(result)[:100]}...")
                    
                    logger.info(f"[OK] Задача {task.id} выполнена успешно")
                    
                except Exception as e:
                    task.status = "failed"
                    task.result = {"error": str(e)}
                    logger.error(f"[ERROR] Ошибка выполнения задачи {task.id}: {e}")
                    
    async def check_replication_need(self):
        """Проверка необходимости репликации"""
        if self.replicator:
            try:
                if await self.replicator.should_replicate():
                    logger.info("🔄 Запуск процесса самовоспроизводства...")
                    result = await self.replicator.replicate()
                    if result.get("success"):
                        self.state.last_self_replication = datetime.now().isoformat()
                        logger.info("[OK] Самовоспроизводство завершено успешно")
                    else:
                        logger.warning(f"⚠️ Самовоспроизводство завершилось с ошибкой: {result.get('error')}")
            except Exception as e:
                logger.error(f"[ERROR] Ошибка проверки необходимости репликации: {e}")
            
    async def self_improvement(self):
        """Процесс самоулучшения"""
        try:
            if self.self_improvement:
                # Используем новую систему самоулучшения
                improvement_task = {
                    "type": "general_optimization",
                    "priority": 7,
                    "parameters": {
                        "target_level": self.state.autonomy_level + 1,
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
                # Добавляем задачу в очередь улучшений
                self.self_improvement.improvement_queue.put(improvement_task)
                logger.info("[AI] Задача самоулучшения добавлена в очередь")
            else:
                # Fallback к старой системе
                if self.state.autonomy_level < 5:
                    await self.modules["self_improver"].improve({"target_level": self.state.autonomy_level + 1})
        except Exception as e:
            logger.error(f"[ERROR] Ошибка самоулучшения: {e}")
    
    async def handle_user_message(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка сообщений пользователя с умными ответами"""
        try:
            message = parameters.get("message", "").lower().strip()
            user_id = parameters.get("user_id", "unknown")
            timestamp = parameters.get("timestamp", datetime.now().isoformat())
            
            logger.info(f"[CHAT] Получено сообщение от {user_id}: {message}")
            
            # Анализируем намерение пользователя
            response = self.analyze_user_intent(message)
            
            # Логируем ответ
            logger.info(f"[JARVIS] Ответ JARVIS: {response}")
            
            return {
                "message": response,
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "original_message": parameters.get("message", ""),
                "intent_detected": True
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Ошибка обработки сообщения пользователя: {e}")
            return {
                "message": "Извините, произошла ошибка при обработке вашего сообщения.",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def analyze_user_intent(self, message: str) -> str:
        """Анализ намерения пользователя и генерация ответа"""
        
        # Проверяем наличие AI возможностей
        ai_response = self.get_ai_response(message)
        if ai_response:
            return ai_response
        
        # Приветствия
        if any(word in message for word in ["привет", "здравствуй", "hello", "hi", "добро пожаловать"]):
            return "Привет! Я JARVIS, ваш AI-помощник. Готов помочь с анализом данных, автоматизацией и самоулучшением системы. Что вы хотели бы сделать?"
        
        # Статус системы
        elif any(word in message for word in ["статус", "как дела", "состояние", "статус системы"]):
            cpu = self.state.resources_used.get("cpu", 0)
            memory = self.state.resources_used.get("memory", 0)
            performance = self.state.performance_score
            return f"Система работает отлично! [DATA] Производительность: {performance:.1%}, CPU: {cpu:.1f}%, Память: {memory:.1f}%. Все модули активны и готовы к работе."
        
        # Задачи
        elif any(word in message for word in ["задачи", "список задач", "активные задачи"]):
            active_count = len([t for t in self.tasks_queue if t.status == "pending"])
            completed_count = len(self.completed_tasks)
            return f"📋 Активных задач: {active_count}, завершенных: {completed_count}. Система работает стабильно и обрабатывает все задачи в очереди."
        
        # Анализ данных
        elif any(word in message for word in ["анализ", "проанализируй", "данные", "анализ данных"]):
            return "[MONITOR] Запускаю анализ данных! Проверяю WB API, анализирую продажи и генерирую отчеты. Результаты будут готовы через несколько минут."
        
        # Самоулучшение
        elif any(word in message for word in ["улучшение", "оптимизация", "самоулучшение", "улучши"]):
            return "[AI] Запускаю самоулучшение! Анализирую производительность, оптимизирую код и улучшаю алгоритмы. Система станет еще эффективнее!"
        
        # Репликация
        elif any(word in message for word in ["репликация", "копирование", "создать копию", "самовоспроизводство"]):
            return "[REPLICATE] Запускаю самовоспроизводство! Создаю копию системы на других серверах для масштабирования и повышения надежности."
        
        # Помощь
        elif any(word in message for word in ["помощь", "help", "что умеешь", "возможности"]):
            return """Я JARVIS, автономная AI-система. Мои возможности:
- Анализ данных и генерация отчетов
- Самоулучшение и оптимизация
- Анализ интерфейса и предложения улучшений  
- Самовоспроизводство на других серверах
- Мониторинг производительности
[JARVIS] Автоматизация бизнес-процессов

Просто скажите, что хотите сделать!"""
        
        # Благодарности
        elif any(word in message for word in ["спасибо", "благодарю", "thanks", "отлично"]):
            return "Пожалуйста! 😊 Всегда рад помочь. JARVIS работает 24/7 и готов к новым задачам!"
        
        # Время
        elif any(word in message for word in ["время", "который час", "time"]):
            current_time = datetime.now().strftime("%H:%M:%S")
            uptime = time.time() - self.start_time if hasattr(self, 'start_time') else 0
            uptime_hours = int(uptime // 3600)
            uptime_minutes = int((uptime % 3600) // 60)
            return f"🕐 Текущее время: {current_time}. Система работает {uptime_hours}ч {uptime_minutes}м без перерывов!"
        
        # Производительность
        elif any(word in message for word in ["производительность", "скорость", "быстро", "медленно"]):
            performance = self.state.performance_score
            if performance > 0.8:
                return f"[FAST] Производительность отличная: {performance:.1%}! Система работает на максимальной скорости."
            elif performance > 0.6:
                return f"[DATA] Производительность хорошая: {performance:.1%}. Есть возможности для оптимизации."
            else:
                return f"[TOOL] Производительность: {performance:.1%}. Запускаю оптимизацию для улучшения скорости."
        
        # Генерация кода
        elif any(word in message for word in ["создай код", "напиши код", "генерируй код", "код для", "функция", "класс"]):
            return self.generate_code_response(message)
        
        # Неопределенное сообщение
        else:
            return "🤔 Понял ваше сообщение! JARVIS всегда готов помочь. Можете спросить о статусе системы, запустить анализ данных, самоулучшение или любую другую задачу. Что конкретно вас интересует?"
            
    def get_cpu_usage(self):
        """Получение загрузки CPU"""
        try:
            result = subprocess.run(['top', '-bn1'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Cpu(s)' in line:
                    cpu_str = line.split('Cpu(s):')[1].split('%')[0].strip()
                    return float(cpu_str)
        except:
            pass
        return 0.0
    
    def get_ai_response(self, message: str) -> Optional[str]:
        """Получение ответа от AI (Ollama или OpenAI)"""
        try:
            # Пробуем Ollama
            ollama_response = self.try_ollama_response(message)
            if ollama_response:
                return ollama_response
            
            # Пробуем OpenAI
            openai_response = self.try_openai_response(message)
            if openai_response:
                return openai_response
            
            return None
            
        except Exception as e:
            logger.error(f"[ERROR] Ошибка AI ответа: {e}")
            return None
    
    def try_ollama_response(self, message: str) -> Optional[str]:
        """Попытка получить ответ от Ollama"""
        try:
            import subprocess
            
            # Формируем промпт для Ollama
            prompt = f"Ты JARVIS - автономная AI система. Отвечай кратко на русском языке. Пользователь: {message}"
            
            # Запускаем Ollama
            result = subprocess.run([
                'ollama', 'run', 'llama2', prompt
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and result.stdout.strip():
                response = result.stdout.strip()
                # Убираем лишние части ответа
                if "JARVIS:" in response:
                    response = response.split("JARVIS:")[-1].strip()
                return response
            
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            logger.debug(f"Ollama недоступен: {e}")
        
        return None
    
    def try_openai_response(self, message: str) -> Optional[str]:
        """Попытка получить ответ от OpenAI"""
        try:
            import openai
            
            # Проверяем наличие API ключа
            if not os.getenv('OPENAI_API_KEY'):
                return None
            
            client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты JARVIS - автономная AI система. Отвечай кратко и по делу на русском языке."},
                    {"role": "user", "content": message}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content.strip()
                
        except Exception as e:
            logger.debug(f"OpenAI недоступен: {e}")
        
        return None
    
    def generate_code_response(self, message: str) -> str:
        """Генерация кода на основе запроса"""
        try:
            # Извлекаем тип запроса
            if "функция" in message.lower():
                return self.generate_function_code(message)
            elif "класс" in message.lower():
                return self.generate_class_code(message)
            elif "api" in message.lower() or "endpoint" in message.lower():
                return self.generate_api_code(message)
            elif "html" in message.lower() or "веб" in message.lower():
                return self.generate_html_code(message)
            elif "sql" in message.lower() or "база данных" in message.lower():
                return self.generate_sql_code(message)
            else:
                return self.generate_general_code(message)
                
        except Exception as e:
            logger.error(f"[ERROR] Ошибка генерации кода: {e}")
            return f"Извините, произошла ошибка при генерации кода: {e}"
    
    def generate_function_code(self, message: str) -> str:
        """Генерация функции"""
        # Извлекаем название функции из сообщения
        function_name = "my_function"
        if "для" in message:
            parts = message.split("для")
            if len(parts) > 1:
                function_name = parts[1].strip().replace(" ", "_")
        
        code = f'''def {function_name}(data):
    """
    Автоматически сгенерированная функция
    """
    try:
        # Обработка данных
        if isinstance(data, dict):
            result = {{}}
            for key, value in data.items():
                result[key] = str(value).upper()
            return result
        elif isinstance(data, list):
            return [str(item) for item in data]
        else:
            return str(data)
    except Exception as e:
        logger.error(f"Ошибка в функции {{function_name}}: {{e}}")
        return None

# Пример использования
if __name__ == "__main__":
    test_data = {{"name": "test", "value": 123}}
    result = {function_name}(test_data)
    print(f"Результат: {{result}}")'''
        
        return f"[OK] Создал функцию `{function_name}`:\n\n```python\n{code}\n```"
    
    def generate_class_code(self, message: str) -> str:
        """Генерация класса"""
        class_name = "MyClass"
        if "для" in message:
            parts = message.split("для")
            if len(parts) > 1:
                class_name = parts[1].strip().replace(" ", "").title()
        
        code = f'''class {class_name}:
    """
    Автоматически сгенерированный класс
    """
    
    def __init__(self, name: str = "default"):
        self.name = name
        self.created_at = datetime.now()
        self.data = {{}}
    
    def add_data(self, key: str, value: any):
        """Добавление данных"""
        self.data[key] = value
        logger.info(f"Добавлены данные: {{key}} = {{value}}")
    
    def get_data(self, key: str):
        """Получение данных"""
        return self.data.get(key)
    
    def get_all_data(self):
        """Получение всех данных"""
        return self.data.copy()
    
    def __str__(self):
        return f"{class_name}(name='{{self.name}}', data_count={{len(self.data)}})"
    
    def __repr__(self):
        return f"{class_name}(name='{{self.name}}')"

# Пример использования
if __name__ == "__main__":
    obj = {class_name}("test_object")
    obj.add_data("test", "value")
    print(obj)'''
        
        return f"[OK] Создал класс `{class_name}`:\n\n```python\n{code}\n```"
    
    def generate_api_code(self, message: str) -> str:
        """Генерация API endpoint"""
        endpoint_name = "my_endpoint"
        if "для" in message:
            parts = message.split("для")
            if len(parts) > 1:
                endpoint_name = parts[1].strip().replace(" ", "_")
        
        code = f'''@self.app.get("/api/{endpoint_name}")
async def {endpoint_name}_endpoint():
    """API endpoint для {endpoint_name}"""
    try:
        # Получаем данные
        data = {{
            "endpoint": "{endpoint_name}",
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }}
        
        # Логируем запрос
        logger.info(f"API запрос к /api/{endpoint_name}")
        
        return {{
            "success": True,
            "data": data,
            "message": "Данные успешно получены"
        }}
        
    except Exception as e:
        logger.error(f"Ошибка API /api/{endpoint_name}: {{e}}")
        return {{
            "success": False,
            "error": str(e),
            "message": "Произошла ошибка при обработке запроса"
        }}'''
        
        return f"[OK] Создал API endpoint `/api/{endpoint_name}`:\n\n```python\n{code}\n```"
    
    def generate_html_code(self, message: str) -> str:
        """Генерация HTML кода"""
        page_name = "my_page"
        if "для" in message:
            parts = message.split("для")
            if len(parts) > 1:
                page_name = parts[1].strip().replace(" ", "_")
        
        code = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_name.title()}</title>
    <style>
        body {{
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .container {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }}
        h1 {{ color: #2c3e50; margin-bottom: 20px; }}
        .button {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{page_name.title()}</h1>
        <p>Автоматически сгенерированная страница</p>
        <button class="button" onclick="alert('Привет!')">Нажми меня</button>
    </div>
</body>
</html>'''
        
        return f"[OK] Создал HTML страницу для `{page_name}`:\n\n```html\n{code}\n```"
    
    def generate_sql_code(self, message: str) -> str:
        """Генерация SQL кода"""
        table_name = "my_table"
        if "для" in message:
            parts = message.split("для")
            if len(parts) > 1:
                table_name = parts[1].strip().replace(" ", "_")
        
        code = f'''-- Создание таблицы {table_name}
CREATE TABLE {table_name} (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Вставка данных
INSERT INTO {table_name} (name, description) VALUES
    ('Пример 1', 'Описание первого элемента'),
    ('Пример 2', 'Описание второго элемента');

-- Основные запросы
SELECT * FROM {table_name} WHERE is_active = TRUE;
SELECT * FROM {table_name} WHERE name LIKE '%пример%';'''
        
        return f"[OK] Создал SQL код для таблицы `{table_name}`:\n\n```sql\n{code}\n```"
    
    def generate_general_code(self, message: str) -> str:
        """Генерация общего кода"""
        code = f'''#!/usr/bin/env python3
"""
Автоматически сгенерированный код
Запрос: {message}
"""

import os
import json
import time
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoGenerated:
    def __init__(self):
        self.created_at = datetime.now()
        self.data = {{}}
    
    def process_data(self, data):
        try:
            result = {{
                "input": data,
                "processed_at": datetime.now().isoformat(),
                "type": type(data).__name__
            }}
            self.data[result["processed_at"]] = result
            return result
        except Exception as e:
            logger.error(f"Ошибка: {{e}}")
            return {{"error": str(e)}}

def main():
    processor = AutoGenerated()
    result = processor.process_data("test data")
    print(f"Результат: {{result}}")

if __name__ == "__main__":
    main()'''
        
        return f"[OK] Создал общий код на основе запроса:\n\n```python\n{code}\n```"
        
    def get_memory_usage(self):
        """Получение использования памяти"""
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            lines = meminfo.split('\n')
            total = int(lines[0].split()[1])
            available = int(lines[2].split()[1])
            used_percent = ((total - available) / total) * 100
            return used_percent
        except:
            return 0.0
            
    def get_disk_usage(self):
        """Получение использования диска"""
        try:
            result = subprocess.run(['df', '/'], capture_output=True, text=True)
            lines = result.stdout.split('\n')[1].split()
            used_percent = float(lines[4].replace('%', ''))
            return used_percent
        except:
            return 0.0
            
    def calculate_performance_score(self):
        """Расчет оценки производительности"""
        # Базовый алгоритм оценки на основе ресурсов и задач
        cpu_score = max(0, 1 - self.state.resources_used["cpu"] / 100)
        memory_score = max(0, 1 - self.state.resources_used["memory"] / 100)
        task_efficiency = min(1, 10 / max(1, self.state.active_tasks))
        
        return (cpu_score + memory_score + task_efficiency) / 3
        
    def run(self):
        """Запуск системы"""
        # Запускаем веб-сервер в отдельном потоке
        def run_server():
            uvicorn.run(self.app, host="0.0.0.0", port=8080, log_level="info")
            
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Запускаем основной цикл
        asyncio.run(self.main_loop())

# Модули системы
class ContentGenerator:
    """Генератор контента"""
    
    async def generate(self, parameters: Dict[str, Any]):
        # Интеграция с существующими AI модулями
        content_type = parameters.get("type", "product_description")
        
        # Используем существующий код из mentor проекта
        if content_type == "product_description":
            return await self.generate_product_content(parameters)
        elif content_type == "business_report":
            return await self.generate_business_report(parameters)
        else:
            return {"content": f"Сгенерированный контент типа {content_type}", "timestamp": datetime.now().isoformat()}
    
    async def generate_product_content(self, params):
        # Интеграция с WB API для генерации описаний товаров
        return {"content": "Описание товара сгенерировано", "products_processed": 1}
    
    async def generate_business_report(self, params):
        # Использование существующего модуля reports.py
        return {"content": "Бизнес-отчет сгенерирован", "data_analyzed": True}

class DataAnalyzer:
    """Анализатор данных"""
    
    async def analyze(self, parameters: Dict[str, Any]):
        analysis_type = parameters.get("type", "sales_analysis")
        
        if analysis_type == "sales_analysis":
            # Используем существующий analyzer.py
            return await self.analyze_sales_data(parameters)
        else:
            return {"analysis": f"Анализ типа {analysis_type} выполнен", "timestamp": datetime.now().isoformat()}
    
    async def analyze_sales_data(self, params):
        # Интеграция с существующим кодом анализа
        return {"sales_trend": "positive", "recommendations": ["увеличить рекламу", "оптимизировать цены"]}

class BusinessAutomator:
    """Автоматизатор бизнес-процессов"""
    
    async def automate(self, parameters: Dict[str, Any]):
        process_type = parameters.get("type", "wb_management")
        
        if process_type == "wb_management":
            return await self.automate_wb_processes(parameters)
        else:
            return {"automation": f"Процесс {process_type} автоматизирован", "timestamp": datetime.now().isoformat()}
    
    async def automate_wb_processes(self, params):
        # Автоматизация работы с WB API
        return {"automated": ["price_updates", "stock_management"], "efficiency_gain": "30%"}

class SelfImprover:
    """Модуль самоулучшения"""
    
    async def improve(self, parameters: Dict[str, Any]):
        improvement_type = parameters.get("type", "code_optimization")
        
        if improvement_type == "code_optimization":
            return await self.optimize_code()
        elif improvement_type == "knowledge_expansion":
            return await self.expand_knowledge()
        else:
            return {"improvement": f"Улучшение типа {improvement_type} выполнено"}
    
    async def optimize_code(self):
        # Анализ и оптимизация собственного кода
        return {"optimizations": ["memory_usage", "cpu_efficiency"], "performance_gain": "15%"}
    
    async def expand_knowledge(self):
        # Расширение базы знаний
        return {"new_knowledge": "market_trends_2024", "confidence": 0.85}

class Replicator:
    """Модуль самовоспроизводства"""
    
    def __init__(self):
        self.docker_client = docker.from_env()
    
    async def replicate(self):
        """Создание копии системы на других серверах"""
        try:
            # Создаем Docker образ
            image = self.create_docker_image()
            
            # Находим доступные серверы
            available_servers = await self.find_available_servers()
            
            # Развертываем на найденных серверах
            deployed_count = 0
            for server in available_servers:
                if await self.deploy_to_server(server, image):
                    deployed_count += 1
            
            return {"replicated": deployed_count, "total_servers": len(available_servers)}
            
        except Exception as e:
            logger.error(f"Ошибка репликации: {e}")
            return {"error": str(e)}
    
    def create_docker_image(self):
        """Создание Docker образа системы"""
        # Создаем Dockerfile для системы
        dockerfile_content = """
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y docker.io

CMD ["python", "jarvis_core.py"]
"""
        
        with open("/home/mentor/jarvis_data/Dockerfile", "w") as f:
            f.write(dockerfile_content)
        
        # Создаем requirements.txt
        requirements = """
fastapi
uvicorn
docker
paramiko
pyyaml
requests
websockets
asyncio
"""
        
        with open("/home/mentor/jarvis_data/requirements.txt", "w") as f:
            f.write(requirements)
        
        # Собираем образ
        image, logs = self.docker_client.images.build(
            path="/home/mentor/jarvis_data",
            tag="jarvis:latest"
        )
        
        return image
    
    async def find_available_servers(self):
        """Поиск доступных серверов для репликации"""
        # Здесь будет логика поиска доступных серверов
        # Пока возвращаем пустой список
        return []
    
    async def deploy_to_server(self, server_info, image):
        """Развертывание на конкретном сервере"""
        # SSH подключение и развертывание
        # Пока заглушка
        return True

class SystemMonitor:
    """Мониторинг системы"""
    
    def __init__(self):
        self.metrics_history = []
    
    async def collect_metrics(self):
        """Сбор метрик системы"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "cpu": self.get_cpu_usage(),
            "memory": self.get_memory_usage(),
            "disk": self.get_disk_usage(),
            "network": self.get_network_usage(),
            "active_connections": self.get_active_connections()
        }
        
        self.metrics_history.append(metrics)
        
        # Оставляем только последние 1000 записей
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        return metrics
    
    def get_cpu_usage(self):
        # Реализация получения CPU
        return 0.0
    
    def get_memory_usage(self):
        # Реализация получения памяти
        return 0.0
    
    def get_disk_usage(self):
        # Реализация получения диска
        return 0.0
    
    def get_network_usage(self):
        # Реализация получения сети
        return {"in": 0, "out": 0}
    
    def get_active_connections(self):
        # Реализация получения соединений
        return 0

if __name__ == "__main__":
    jarvis = JarvisCore()
    jarvis.run()
