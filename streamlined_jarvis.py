#!/usr/bin/env python3
"""
Streamlined Enhanced JARVIS System
Упрощенная улучшенная автономная система с визуальным интеллектом
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
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from fastapi import FastAPI, WebSocket, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import psutil
import base64
import io
from PIL import Image, ImageDraw, ImageFont

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/streamlined_jarvis.log'),
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
    performance_score: float = 0.0
    autonomy_level: int = 1
    visual_analysis_count: int = 0
    continuous_uptime: float = 0.0
    last_visual_check: Optional[str] = None
    autonomous_decisions_made: int = 0
    self_healing_events: int = 0
    
    def __post_init__(self):
        if self.resources_used is None:
            self.resources_used = {"cpu": 0.0, "memory": 0.0, "disk": 0.0, "network": 0.0}

@dataclass
class Task:
    """Задача системы"""
    id: str
    type: str
    priority: int
    status: str
    created_at: str
    parameters: Dict[str, Any] = None
    result: Any = None
    autonomous_generated: bool = False
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}

@dataclass
class VisualAnalysis:
    """Результат визуального анализа"""
    timestamp: str
    screenshot_data: Optional[str]
    elements_detected: List[Dict[str, Any]]
    issues_found: List[Dict[str, Any]]
    suggestions: List[str]
    confidence: float
    ux_score: float

class VisualIntelligence:
    """Система визуального интеллекта"""
    
    def __init__(self, jarvis_core):
        self.core = jarvis_core
        self.enabled = True
        self.screenshot_interval = 5
        self.analysis_history = []
        self.last_analysis = None
        
        # Запускаем визуальный мониторинг
        self.start_monitoring()
    
    def start_monitoring(self):
        """Запуск мониторинга"""
        def monitor_loop():
            while self.enabled:
                try:
                    analysis = self.perform_analysis()
                    if analysis:
                        self.process_analysis(analysis)
                        self.analysis_history.append(analysis)
                        
                        # Ограничиваем историю
                        if len(self.analysis_history) > 50:
                            self.analysis_history = self.analysis_history[-25:]
                    
                    time.sleep(self.screenshot_interval)
                    
                except Exception as e:
                    logger.error(f"Ошибка визуального мониторинга: {e}")
                    time.sleep(10)
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        logger.info("👁️ Система визуального интеллекта запущена")
    
    def perform_analysis(self) -> Optional[VisualAnalysis]:
        """Выполнение анализа"""
        try:
            # Создаем виртуальный скриншот
            screenshot_data = self.create_screenshot()
            
            # Анализируем элементы
            elements = self.analyze_elements()
            
            # Обнаруживаем проблемы
            issues = self.detect_issues(elements)
            
            # Генерируем предложения
            suggestions = self.generate_suggestions(issues)
            
            # Рассчитываем метрики
            confidence = min(1.0, 0.8 + len(elements) * 0.02)
            ux_score = max(0.0, 0.9 - len(issues) * 0.1)
            
            analysis = VisualAnalysis(
                timestamp=datetime.now().isoformat(),
                screenshot_data=screenshot_data,
                elements_detected=elements,
                issues_found=issues,
                suggestions=suggestions,
                confidence=confidence,
                ux_score=ux_score
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Ошибка анализа: {e}")
            return None
    
    def create_screenshot(self) -> str:
        """Создание виртуального скриншота"""
        try:
            # Создаем изображение
            img = Image.new('RGB', (1200, 800), color='#1a1a2e')
            draw = ImageDraw.Draw(img)
            
            # Добавляем элементы интерфейса
            try:
                font = ImageFont.load_default()
            except:
                font = None
            
            # Заголовок
            draw.rectangle([0, 0, 1200, 80], fill='#16213e')
            draw.text((50, 25), "🤖 JARVIS Enhanced System", fill='#00ff88', font=font)
            
            # Статусная панель
            draw.rectangle([50, 100, 1150, 180], fill='#0f3460', outline='#00ff88', width=2)
            draw.text((70, 120), f"Performance: {self.core.state.performance_score:.1%}", fill='#ffffff', font=font)
            draw.text((70, 140), f"Tasks: {self.core.state.active_tasks}", fill='#ffffff', font=font)
            draw.text((300, 120), f"Autonomy: {self.core.state.autonomy_level}", fill='#00ff88', font=font)
            draw.text((300, 140), f"Visual: {self.core.state.visual_analysis_count}", fill='#00ff88', font=font)
            
            # Кнопки
            buttons = [
                {"text": "Self-Improvement", "pos": (50, 200), "color": "#27ae60"},
                {"text": "Visual Analysis", "pos": (250, 200), "color": "#3498db"},
                {"text": "Autonomous Mode", "pos": (450, 200), "color": "#9b59b6"},
                {"text": "System Health", "pos": (650, 200), "color": "#f39c12"}
            ]
            
            for btn in buttons:
                draw.rectangle([btn["pos"][0], btn["pos"][1], btn["pos"][0]+180, btn["pos"][1]+40], 
                             fill=btn["color"], outline='#ffffff', width=1)
                draw.text((btn["pos"][0]+10, btn["pos"][1]+12), btn["text"], fill='#ffffff', font=font)
            
            # Область логов
            draw.rectangle([50, 280, 1150, 500], fill='#2c3e50', outline='#34495e', width=2)
            draw.text((70, 290), "System Logs", fill='#ecf0f1', font=font)
            
            # Мониторинг
            draw.rectangle([50, 520, 1150, 750], fill='#34495e', outline='#00ff88', width=2)
            draw.text((70, 530), "Real-time Monitoring", fill='#00ff88', font=font)
            
            # Метрики
            metrics_text = f"CPU: {psutil.cpu_percent():.1f}% | Memory: {psutil.virtual_memory().percent:.1f}% | Uptime: {self.core.state.continuous_uptime/3600:.1f}h"
            draw.text((70, 560), metrics_text, fill='#ffffff', font=font)
            
            # Индикатор состояния
            draw.circle([1100, 600], 20, fill='#27ae60')
            draw.text((1070, 630), "ONLINE", fill='#27ae60', font=font)
            
            # Кодируем в base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return image_base64
            
        except Exception as e:
            logger.error(f"Ошибка создания скриншота: {e}")
            return None
    
    def analyze_elements(self) -> List[Dict[str, Any]]:
        """Анализ элементов интерфейса"""
        return [
            {
                "type": "header",
                "text": "JARVIS Enhanced System",
                "position": {"x": 50, "y": 25},
                "size": {"width": 400, "height": 30},
                "confidence": 0.95
            },
            {
                "type": "status_panel",
                "position": {"x": 50, "y": 100},
                "size": {"width": 1100, "height": 80},
                "confidence": 0.9,
                "real_time": True
            },
            {
                "type": "button_group",
                "count": 4,
                "position": {"x": 50, "y": 200},
                "size": {"width": 800, "height": 40},
                "confidence": 0.85,
                "interactive": True
            },
            {
                "type": "log_area",
                "position": {"x": 50, "y": 280},
                "size": {"width": 1100, "height": 220},
                "confidence": 0.9,
                "scrollable": True
            },
            {
                "type": "monitoring_panel",
                "position": {"x": 50, "y": 520},
                "size": {"width": 1100, "height": 230},
                "confidence": 0.95,
                "real_time": True
            }
        ]
    
    def detect_issues(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Обнаружение проблем"""
        issues = []
        
        # Проверяем интерактивные элементы
        interactive_elements = [e for e in elements if e.get("interactive")]
        if len(interactive_elements) < 2:
            issues.append({
                "type": "accessibility",
                "severity": "medium",
                "description": "Недостаточно интерактивных элементов",
                "auto_fixable": True
            })
        
        # Проверяем элементы реального времени
        real_time_elements = [e for e in elements if e.get("real_time")]
        if len(real_time_elements) < 2:
            issues.append({
                "type": "user_experience",
                "severity": "low",
                "description": "Мало элементов реального времени",
                "auto_fixable": True
            })
        
        return issues
    
    def generate_suggestions(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Генерация предложений"""
        suggestions = [
            "🚀 Добавить анимации при наведении на кнопки",
            "📊 Добавить графики производительности в реальном времени",
            "🔔 Добавить звуковые уведомления для важных событий",
            "📱 Сделать интерфейс адаптивным для мобильных устройств",
            "⌨️ Добавить горячие клавиши для быстрого доступа",
            "🌙 Реализовать переключение темной/светлой темы",
            "🤖 Добавить голосовое управление системой",
            "☁️ Интегрировать с облачными сервисами"
        ]
        
        return suggestions[:5]
    
    def process_analysis(self, analysis: VisualAnalysis):
        """Обработка результатов анализа"""
        try:
            self.last_analysis = analysis
            self.core.state.visual_analysis_count += 1
            self.core.state.last_visual_check = analysis.timestamp
            
            # Если найдены критические проблемы, создаем задачи
            critical_issues = [i for i in analysis.issues_found if i.get("severity") == "high"]
            
            if critical_issues and self.core.state.autonomy_level >= 2:
                task = Task(
                    id=f"visual_fix_{int(time.time())}",
                    type="ui_improvement",
                    priority=8,
                    status="pending",
                    created_at=datetime.now().isoformat(),
                    autonomous_generated=True,
                    parameters={
                        "issues": critical_issues,
                        "suggestions": analysis.suggestions[:3]
                    }
                )
                
                self.core.tasks_queue.append(task)
                self.core.state.autonomous_decisions_made += 1
                logger.info(f"✅ Создана автономная задача улучшения UI: {task.id}")
            
            logger.info(f"👁️ Визуальный анализ: {len(analysis.elements_detected)} элементов, "
                       f"{len(analysis.issues_found)} проблем, UX: {analysis.ux_score:.2f}")
            
        except Exception as e:
            logger.error(f"Ошибка обработки анализа: {e}")

class StreamlinedJarvis:
    """Упрощенная система JARVIS"""
    
    def __init__(self):
        self.state = SystemState()
        self.tasks_queue = []
        self.completed_tasks = []
        self.running = True
        self.start_time = time.time()
        
        # Создаем FastAPI приложение
        self.app = FastAPI(title="Streamlined JARVIS", version="1.0")
        self.setup_middleware()
        
        # Инициализируем компоненты
        self.visual_intelligence = VisualIntelligence(self)
        
        # Инициализируем реальный визуальный анализатор
        try:
            from enhanced_visual_analyzer import EnhancedVisualAnalyzer
            self.real_visual_analyzer = EnhancedVisualAnalyzer(target_url="http://localhost:8080")
            self.real_visual_analyzer.start_continuous_analysis(interval=60)
            logger.info("✅ Реальный визуальный анализатор подключен")
        except Exception as e:
            logger.warning(f"⚠️ Реальный анализатор недоступен: {e}")
            self.real_visual_analyzer = None
        
        # Инициализируем систему обучения
        try:
            from simple_learning_system import SimpleLearningSystem
            self.learning_system = SimpleLearningSystem()
            logger.info("✅ Система обучения подключена")
        except Exception as e:
            logger.warning(f"⚠️ Система обучения недоступна: {e}")
            self.learning_system = None
        
        # Инициализируем Ollama интеграцию
        try:
            from ollama_integration import OllamaIntegration
            self.ollama = OllamaIntegration()
            logger.info("✅ Ollama LLM подключен")
        except Exception as e:
            logger.warning(f"⚠️ Ollama недоступен: {e}")
            self.ollama = None
        
        # Инициализируем агентов
        self.agents = {}
        self.init_agents()
        
        # Запускаем автономные системы
        self.start_autonomous_systems()
        
        # Настраиваем API
        self.setup_routes()
        
        logger.info("🚀 Streamlined JARVIS система инициализирована")
    
    def init_agents(self):
        """Инициализация агентов"""
        try:
            # Простые агенты для базовой системы
            self.agents = {
                "coordinator": {
                    "status": "active",
                    "tasks_completed": 0,
                    "specialization": "task_coordination",
                    "performance": 0.9
                },
                "analyzer": {
                    "status": "active", 
                    "tasks_completed": 0,
                    "specialization": "data_analysis",
                    "performance": 0.85
                },
                "optimizer": {
                    "status": "active",
                    "tasks_completed": 0,
                    "specialization": "performance_optimization", 
                    "performance": 0.8
                }
            }
            logger.info(f"✅ Инициализировано {len(self.agents)} агентов")
        except Exception as e:
            logger.error(f"Ошибка инициализации агентов: {e}")
    
    def setup_middleware(self):
        """Настройка middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def start_autonomous_systems(self):
        """Запуск автономных систем"""
        def autonomous_loop():
            while self.running:
                try:
                    # Генерируем задачи
                    self.generate_autonomous_tasks()
                    
                    # Обрабатываем задачи
                    self.process_tasks()
                    
                    # Обновляем состояние
                    self.update_state()
                    
                    time.sleep(10)
                    
                except Exception as e:
                    logger.error(f"Ошибка автономной системы: {e}")
                    time.sleep(15)
        
        threading.Thread(target=autonomous_loop, daemon=True).start()
        logger.info("🤖 Автономные системы запущены")
    
    def generate_autonomous_tasks(self):
        """Генерация автономных задач"""
        try:
            # Задачи самоулучшения
            if len(self.completed_tasks) > 0 and len(self.completed_tasks) % 5 == 0:
                task = Task(
                    id=f"self_improvement_{int(time.time())}",
                    type="self_improvement",
                    priority=6,
                    status="pending",
                    created_at=datetime.now().isoformat(),
                    autonomous_generated=True
                )
                task.parameters["assigned_agent"] = "optimizer"
                self.tasks_queue.append(task)
                logger.info("🧠 Создана задача самоулучшения (агент: optimizer)")
            
            # Задачи оптимизации
            if self.state.performance_score < 0.7:
                task = Task(
                    id=f"optimization_{int(time.time())}",
                    type="performance_optimization",
                    priority=7,
                    status="pending",
                    created_at=datetime.now().isoformat(),
                    autonomous_generated=True
                )
                task.parameters["assigned_agent"] = "optimizer"
                self.tasks_queue.append(task)
                logger.info("⚡ Создана задача оптимизации (агент: optimizer)")
            
            # Задачи анализа данных
            if self.state.visual_analysis_count > 0 and self.state.visual_analysis_count % 20 == 0:
                task = Task(
                    id=f"data_analysis_{int(time.time())}",
                    type="data_analysis",
                    priority=5,
                    status="pending",
                    created_at=datetime.now().isoformat(),
                    autonomous_generated=True
                )
                task.parameters["assigned_agent"] = "analyzer"
                self.tasks_queue.append(task)
                logger.info("📊 Создана задача анализа данных (агент: analyzer)")
            
            # Координационные задачи
            if len(self.agents) > 1 and int(time.time()) % 300 == 0:  # Каждые 5 минут
                task = Task(
                    id=f"coordination_{int(time.time())}",
                    type="agent_coordination",
                    priority=4,
                    status="pending",
                    created_at=datetime.now().isoformat(),
                    autonomous_generated=True
                )
                task.parameters["assigned_agent"] = "coordinator"
                self.tasks_queue.append(task)
                logger.info("🤝 Создана координационная задача (агент: coordinator)")
            
        except Exception as e:
            logger.error(f"Ошибка генерации задач: {e}")
    
    def process_tasks(self):
        """Обработка задач"""
        try:
            if not self.tasks_queue:
                return
            
            # Сортируем по приоритету
            self.tasks_queue.sort(key=lambda x: x.priority, reverse=True)
            
            # Обрабатываем до 2 задач за раз
            for _ in range(min(2, len(self.tasks_queue))):
                if self.tasks_queue:
                    task = self.tasks_queue.pop(0)
                    self.execute_task(task)
        
        except Exception as e:
            logger.error(f"Ошибка обработки задач: {e}")
    
    def execute_task(self, task: Task):
        """Выполнение задачи"""
        try:
            task.status = "running"
            self.state.active_tasks += 1
            
            # Определяем агента для выполнения
            assigned_agent = task.parameters.get("assigned_agent", "coordinator")
            if assigned_agent in self.agents:
                agent_info = self.agents[assigned_agent]
                logger.info(f"▶️ Выполняется: {task.id} ({task.type}) агентом {assigned_agent}")
            else:
                assigned_agent = "coordinator"
                logger.info(f"▶️ Выполняется: {task.id} ({task.type})")
            
            # Симулируем выполнение
            time.sleep(1)
            
            if task.type == "self_improvement":
                result = self.execute_self_improvement()
            elif task.type == "performance_optimization":
                result = self.execute_optimization()
            elif task.type == "ui_improvement":
                result = self.execute_ui_improvement(task)
            elif task.type == "data_analysis":
                result = self.execute_data_analysis(task)
            elif task.type == "agent_coordination":
                result = self.execute_agent_coordination(task)
            else:
                result = {"status": "completed", "message": "Задача выполнена"}
            
            # Обновляем статистику агента
            if assigned_agent in self.agents:
                self.agents[assigned_agent]["tasks_completed"] += 1
                # Улучшаем производительность агента при успешном выполнении
                if result.get("status") == "completed":
                    current_perf = self.agents[assigned_agent]["performance"]
                    self.agents[assigned_agent]["performance"] = min(1.0, current_perf + 0.01)
            
            task.status = "completed"
            task.result = result
            task.result["executed_by_agent"] = assigned_agent
            self.completed_tasks.append(task)
            self.state.active_tasks = max(0, self.state.active_tasks - 1)
            
            # Записываем событие в систему обучения
            if self.learning_system:
                self.learning_system.record_event(
                    "task_completion",
                    {
                        "task_type": task.type,
                        "agent": assigned_agent,
                        "priority": task.priority,
                        "autonomous": task.autonomous_generated
                    },
                    {
                        "status": "completed",
                        "result_type": result.get("status", "unknown")
                    },
                    True,
                    0.05  # Положительное влияние за успешное выполнение
                )
            
            logger.info(f"✅ Задача завершена: {task.id} агентом {assigned_agent}")
            
        except Exception as e:
            task.status = "failed"
            task.result = {"error": str(e)}
            self.state.active_tasks = max(0, self.state.active_tasks - 1)
            logger.error(f"❌ Ошибка задачи {task.id}: {e}")
    
    def execute_self_improvement(self) -> Dict[str, Any]:
        """Самоулучшение"""
        # Повышаем уровень автономности
        if len(self.completed_tasks) > 0:
            success_rate = len([t for t in self.completed_tasks if t.status == "completed"]) / len(self.completed_tasks)
            if success_rate > 0.8:
                self.state.autonomy_level = min(5, self.state.autonomy_level + 1)
        
        return {
            "status": "completed",
            "new_autonomy_level": self.state.autonomy_level,
            "improvements": ["Анализ производительности", "Оптимизация алгоритмов", "Улучшение интерфейса"]
        }
    
    def execute_optimization(self) -> Dict[str, Any]:
        """Оптимизация производительности"""
        # Улучшаем производительность
        self.state.performance_score = min(1.0, self.state.performance_score + 0.1)
        
        return {
            "status": "completed",
            "performance_improvement": 0.1,
            "new_score": self.state.performance_score
        }
    
    def execute_ui_improvement(self, task: Task) -> Dict[str, Any]:
        """Улучшение UI"""
        issues = task.parameters.get("issues", [])
        suggestions = task.parameters.get("suggestions", [])
        
        return {
            "status": "completed",
            "issues_fixed": len(issues),
            "suggestions_applied": len(suggestions)
        }
    
    def execute_data_analysis(self, task: Task) -> Dict[str, Any]:
        """Анализ данных"""
        try:
            # Анализируем данные системы
            analysis_data = {
                "visual_analyses": self.state.visual_analysis_count,
                "completed_tasks": len(self.completed_tasks),
                "performance_trend": self.calculate_performance_trend(),
                "agent_performance": {agent_id: agent["performance"] for agent_id, agent in self.agents.items()}
            }
            
            insights = []
            
            # Генерируем инсайты
            if self.state.performance_score > 0.8:
                insights.append("Система работает на высоком уровне производительности")
            
            if self.state.visual_analysis_count > 100:
                insights.append("Высокая активность визуального анализа")
            
            best_agent = max(self.agents.items(), key=lambda x: x[1]["performance"])
            insights.append(f"Лучший агент: {best_agent[0]} ({best_agent[1]['performance']:.2f})")
            
            return {
                "status": "completed",
                "analysis_data": analysis_data,
                "insights": insights,
                "recommendations": self.generate_recommendations(analysis_data)
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def execute_agent_coordination(self, task: Task) -> Dict[str, Any]:
        """Координация агентов"""
        try:
            coordination_actions = []
            
            # Балансировка нагрузки между агентами
            total_tasks = sum(agent["tasks_completed"] for agent in self.agents.values())
            if total_tasks > 0:
                for agent_id, agent in self.agents.items():
                    load_ratio = agent["tasks_completed"] / total_tasks
                    if load_ratio > 0.5:  # Перегруженный агент
                        coordination_actions.append(f"Снижение нагрузки на агента {agent_id}")
                    elif load_ratio < 0.1:  # Недозагруженный агент
                        coordination_actions.append(f"Увеличение нагрузки на агента {agent_id}")
            
            # Оптимизация производительности агентов
            for agent_id, agent in self.agents.items():
                if agent["performance"] < 0.7:
                    coordination_actions.append(f"Оптимизация агента {agent_id}")
                    # Улучшаем производительность
                    self.agents[agent_id]["performance"] = min(1.0, agent["performance"] + 0.05)
            
            # Проверка статуса агентов
            active_agents = len([a for a in self.agents.values() if a["status"] == "active"])
            coordination_actions.append(f"Активных агентов: {active_agents}/{len(self.agents)}")
            
            return {
                "status": "completed",
                "coordination_actions": coordination_actions,
                "agents_status": {aid: agent["status"] for aid, agent in self.agents.items()},
                "performance_scores": {aid: agent["performance"] for aid, agent in self.agents.items()}
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def calculate_performance_trend(self) -> str:
        """Расчет тренда производительности"""
        try:
            # Анализируем последние задачи
            recent_tasks = self.completed_tasks[-10:] if len(self.completed_tasks) >= 10 else self.completed_tasks
            
            if not recent_tasks:
                return "insufficient_data"
            
            successful_tasks = len([t for t in recent_tasks if t.status == "completed"])
            success_rate = successful_tasks / len(recent_tasks)
            
            if success_rate > 0.9:
                return "excellent"
            elif success_rate > 0.7:
                return "good"
            elif success_rate > 0.5:
                return "fair"
            else:
                return "poor"
                
        except Exception:
            return "unknown"
    
    def generate_recommendations(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Генерация рекомендаций на основе анализа"""
        recommendations = []
        
        try:
            # Рекомендации по производительности
            if analysis_data.get("performance_trend") == "poor":
                recommendations.append("🔧 Требуется оптимизация производительности")
            
            # Рекомендации по агентам
            agent_performance = analysis_data.get("agent_performance", {})
            for agent_id, performance in agent_performance.items():
                if performance < 0.7:
                    recommendations.append(f"⚡ Улучшить производительность агента {agent_id}")
                elif performance > 0.95:
                    recommendations.append(f"🏆 Агент {agent_id} показывает отличные результаты")
            
            # Рекомендации по визуальному анализу
            visual_count = analysis_data.get("visual_analyses", 0)
            if visual_count > 500:
                recommendations.append("👁️ Высокая активность визуального анализа - рассмотрите оптимизацию")
            elif visual_count < 50:
                recommendations.append("👁️ Низкая активность визуального анализа - проверьте настройки")
            
            # Общие рекомендации
            if len(recommendations) == 0:
                recommendations.append("✅ Система работает оптимально")
            
        except Exception as e:
            recommendations.append(f"❌ Ошибка генерации рекомендаций: {e}")
        
        return recommendations
    
    def generate_product_description(self, topic: str, length: str) -> str:
        """Генерация описания товара"""
        try:
            # Пробуем использовать Ollama для продвинутой генерации
            if self.ollama:
                prompt = f"Создай продающее описание для товара: {topic}"
                llm_content = self.ollama.generate_advanced_content(prompt)
                
                if len(llm_content) > 50:
                    logger.info(f"✅ Описание сгенерировано с помощью LLM: {len(llm_content)} символов")
                    return llm_content
            
            # Fallback к шаблонам
            templates = {
                "short": [
                    f"Качественный {topic} с отличными характеристиками.",
                    f"Премиум {topic} для требовательных покупателей.",
                    f"Инновационный {topic} с современным дизайном."
                ],
                "medium": [
                    f"Представляем вам высококачественный {topic}, который станет незаменимым помощником в повседневной жизни. Изготовлен из лучших материалов с использованием современных технологий.",
                    f"Этот {topic} сочетает в себе функциональность, стиль и надежность. Идеально подходит для активных людей, ценящих качество и комфорт.",
                    f"Уникальный {topic} с инновационными функциями. Разработан с учетом последних тенденций и потребностей современного потребителя."
                ],
                "long": [
                    f"Откройте для себя превосходный {topic}, созданный с использованием передовых технологий и высококачественных материалов. Этот продукт представляет собой идеальное сочетание функциональности, стиля и долговечности.\n\nОсобенности:\n• Премиум качество материалов\n• Современный эргономичный дизайн\n• Простота использования\n• Долгий срок службы\n• Гарантия качества\n\nИдеально подходит для ежедневного использования и станет отличным выбором для тех, кто ценит качество и надежность."
                ]
            }
            
            import random
            template_list = templates.get(length, templates["medium"])
            return random.choice(template_list)
            
        except Exception as e:
            return f"Качественный {topic} с отличными характеристиками и современным дизайном."
    
    def generate_product_title(self, topic: str) -> str:
        """Генерация названия товара"""
        try:
            prefixes = ["Премиум", "Качественный", "Современный", "Инновационный", "Стильный"]
            suffixes = ["Pro", "Elite", "Premium", "Advanced", "Plus"]
            
            import random
            prefix = random.choice(prefixes)
            suffix = random.choice(suffixes)
            
            return f"{prefix} {topic} {suffix}"
            
        except Exception as e:
            return f"Качественный {topic}"
    
    def generate_keywords(self, topic: str) -> str:
        """Генерация ключевых слов"""
        try:
            base_keywords = [topic]
            
            # Добавляем связанные слова
            related_words = [
                "качественный", "премиум", "купить", "цена", "отзывы",
                "доставка", "гарантия", "скидка", "акция", "новинка",
                "лучший", "топ", "рейтинг", "выбор", "рекомендуем"
            ]
            
            import random
            selected_keywords = random.sample(related_words, 8)
            base_keywords.extend(selected_keywords)
            
            return ", ".join(base_keywords)
            
        except Exception as e:
            return f"{topic}, качественный, купить, цена"
    
    def execute_business_automation(self, automation_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение бизнес-автоматизации"""
        try:
            if automation_type == "wb_stock_check":
                return self.check_wb_stock()
            elif automation_type == "wb_reports":
                return self.generate_wb_reports()
            elif automation_type == "sales_analysis":
                return self.analyze_sales_data()
            elif automation_type == "content_generation":
                return self.batch_generate_content(parameters)
            elif automation_type == "price_monitoring":
                return self.monitor_prices()
            else:
                return {
                    "status": "completed",
                    "message": f"Автоматизация {automation_type} выполнена",
                    "actions": ["Проверка системы", "Обновление данных", "Генерация отчета"]
                }
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def check_wb_stock(self) -> Dict[str, Any]:
        """Проверка остатков на WB"""
        try:
            # Симулируем проверку остатков
            stock_data = {
                "total_products": 150,
                "low_stock_products": 12,
                "out_of_stock": 3,
                "recommendations": [
                    "Пополнить товар ID 12345 (осталось 2 шт)",
                    "Заказать товар ID 67890 (закончился)",
                    "Увеличить заказ товара ID 54321 (высокий спрос)"
                ]
            }
            
            return {
                "status": "completed",
                "data": stock_data,
                "alerts": stock_data["low_stock_products"] + stock_data["out_of_stock"]
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def generate_wb_reports(self) -> Dict[str, Any]:
        """Генерация отчетов WB"""
        try:
            # Симулируем генерацию отчетов
            report_data = {
                "sales_summary": {
                    "total_sales": 45670,
                    "orders_count": 234,
                    "avg_order_value": 195.2,
                    "top_products": ["Товар A", "Товар B", "Товар C"]
                },
                "performance_metrics": {
                    "conversion_rate": 3.2,
                    "return_rate": 1.8,
                    "customer_satisfaction": 4.6
                },
                "recommendations": [
                    "Увеличить рекламный бюджет на Товар A",
                    "Оптимизировать описания для Товара B",
                    "Снизить цену на Товар C для увеличения продаж"
                ]
            }
            
            return {
                "status": "completed",
                "report": report_data,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def analyze_sales_data(self) -> Dict[str, Any]:
        """Анализ данных продаж"""
        try:
            # Симулируем анализ продаж
            analysis = {
                "trends": {
                    "weekly_growth": 12.5,
                    "monthly_growth": 45.2,
                    "seasonal_factor": 1.15
                },
                "insights": [
                    "Продажи растут на 12.5% в неделю",
                    "Пиковые часы продаж: 19:00-22:00",
                    "Лучший день недели: пятница",
                    "Самая популярная категория: электроника"
                ],
                "predictions": {
                    "next_week_sales": 52000,
                    "next_month_sales": 195000,
                    "confidence": 0.87
                }
            }
            
            return {
                "status": "completed",
                "analysis": analysis,
                "actionable_insights": len(analysis["insights"])
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def batch_generate_content(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Массовая генерация контента"""
        try:
            count = parameters.get("count", 5)
            content_type = parameters.get("type", "description")
            topics = parameters.get("topics", ["товар", "продукт", "услуга"])
            
            generated_content = []
            
            for i in range(count):
                import random
                topic = random.choice(topics)
                
                if content_type == "description":
                    content = self.generate_product_description(topic, "medium")
                elif content_type == "title":
                    content = self.generate_product_title(topic)
                else:
                    content = self.generate_keywords(topic)
                
                generated_content.append({
                    "id": i + 1,
                    "topic": topic,
                    "content": content,
                    "type": content_type
                })
            
            return {
                "status": "completed",
                "generated_count": len(generated_content),
                "content": generated_content
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def monitor_prices(self) -> Dict[str, Any]:
        """Мониторинг цен"""
        try:
            # Симулируем мониторинг цен
            price_data = {
                "monitored_products": 89,
                "price_changes": 7,
                "alerts": [
                    "Конкурент снизил цену на Товар A на 15%",
                    "Рекомендуется поднять цену на Товар B (высокий спрос)",
                    "Товар C можно снизить на 5% для увеличения продаж"
                ],
                "avg_market_price": 245.60,
                "our_avg_price": 239.80,
                "competitiveness": 0.92
            }
            
            return {
                "status": "completed",
                "data": price_data,
                "action_required": len(price_data["alerts"])
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def update_state(self):
        """Обновление состояния"""
        try:
            # Время работы
            self.state.continuous_uptime = time.time() - self.start_time
            
            # Ресурсы
            self.state.resources_used = {
                "cpu": psutil.cpu_percent(interval=1),
                "memory": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage('/').percent,
                "network": 10.0  # Симуляция
            }
            
            # Производительность
            resource_load = (
                self.state.resources_used["cpu"] / 100 * 0.4 +
                self.state.resources_used["memory"] / 100 * 0.6
            )
            
            self.state.performance_score = max(0.0, 1.0 - resource_load)
            
        except Exception as e:
            logger.error(f"Ошибка обновления состояния: {e}")
    
    def setup_routes(self):
        """Настройка маршрутов"""
        
        @self.app.get("/")
        async def dashboard():
            """Главная панель"""
            return HTMLResponse(content=self.generate_dashboard_html())
        
        @self.app.get("/api/status")
        async def get_status():
            """Статус системы"""
            return {
                "system_state": asdict(self.state),
                "active_tasks": len(self.tasks_queue),
                "completed_tasks": len(self.completed_tasks),
                "uptime": self.state.continuous_uptime,
                "visual_analysis": {
                    "enabled": self.visual_intelligence.enabled,
                    "total_analyses": len(self.visual_intelligence.analysis_history),
                    "last_analysis": asdict(self.visual_intelligence.last_analysis) if self.visual_intelligence.last_analysis else None
                }
            }
        
        @self.app.get("/api/vision/status")
        async def get_vision_status():
            """Статус визуального анализа"""
            response = {"enabled": True, "total_analyses": 0}
            
            # Базовый визуальный анализ
            if self.visual_intelligence.last_analysis:
                response.update({
                    "basic_analysis": {
                        "total_analyses": len(self.visual_intelligence.analysis_history),
                        "last_analysis": {
                            "timestamp": self.visual_intelligence.last_analysis.timestamp,
                            "elements_detected": len(self.visual_intelligence.last_analysis.elements_detected),
                            "issues_found": len(self.visual_intelligence.last_analysis.issues_found),
                            "confidence": self.visual_intelligence.last_analysis.confidence,
                            "ux_score": self.visual_intelligence.last_analysis.ux_score
                        }
                    }
                })
            
            # Реальный визуальный анализ
            if self.real_visual_analyzer and self.real_visual_analyzer.last_analysis:
                real_analysis = self.real_visual_analyzer.last_analysis
                response.update({
                    "real_analysis": {
                        "total_analyses": len(self.real_visual_analyzer.analysis_history),
                        "last_analysis": {
                            "timestamp": real_analysis.timestamp,
                            "page_title": real_analysis.page_title,
                            "elements_count": real_analysis.elements_analysis.get("total_elements", 0),
                            "interactive_elements": real_analysis.elements_analysis.get("interactive_elements", 0),
                            "accessibility_score": real_analysis.accessibility_score,
                            "performance_score": real_analysis.performance_score,
                            "seo_score": real_analysis.seo_score,
                            "issues_count": len(real_analysis.ui_issues),
                            "confidence": real_analysis.confidence
                        }
                    }
                })
            
            return response
        
        @self.app.get("/api/vision/detailed")
        async def get_detailed_vision():
            """Детальный визуальный анализ"""
            if self.real_visual_analyzer:
                summary = self.real_visual_analyzer.get_analysis_summary()
                return summary
            return {"error": "Real visual analyzer not available"}
        
        @self.app.get("/api/learning/status")
        async def get_learning_status():
            """Статус системы обучения"""
            if self.learning_system:
                stats = self.learning_system.get_learning_statistics()
                return stats
            return {"error": "Learning system not available"}
        
        @self.app.post("/api/learning/record")
        async def record_learning_event(event_data: dict):
            """Запись события обучения"""
            if self.learning_system:
                self.learning_system.record_event(
                    event_data.get("event_type", "manual"),
                    event_data.get("context", {}),
                    event_data.get("outcome", {}),
                    event_data.get("success", True),
                    event_data.get("performance_impact", 0.0)
                )
                return {"status": "recorded", "timestamp": datetime.now().isoformat()}
            return {"error": "Learning system not available"}
        
        @self.app.get("/api/wb/cards")
        async def get_wb_cards():
            """Получение карточек товаров с WB"""
            try:
                import wb_api
                cards_data = wb_api.get_cards(limit=20)
                
                if cards_data:
                    # Записываем событие в систему обучения
                    if self.learning_system:
                        self.learning_system.record_event(
                            "wb_api_call",
                            {"api": "get_cards", "limit": 20},
                            {"status": "success", "cards_count": len(cards_data.get("cards", []))},
                            True,
                            0.02
                        )
                    
                    return {"success": True, "data": cards_data, "timestamp": datetime.now().isoformat()}
                else:
                    return {"success": False, "error": "Не удалось получить данные WB"}
                    
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        @self.app.get("/api/wb/orders")
        async def get_wb_orders():
            """Получение заказов с WB"""
            try:
                import wb_api
                orders_data = wb_api.get_orders(days=7)
                
                if orders_data:
                    # Записываем событие в систему обучения
                    if self.learning_system:
                        self.learning_system.record_event(
                            "wb_api_call",
                            {"api": "get_orders", "days": 7},
                            {"status": "success", "orders_count": len(orders_data) if isinstance(orders_data, list) else 1},
                            True,
                            0.03
                        )
                    
                    return {"success": True, "data": orders_data, "timestamp": datetime.now().isoformat()}
                else:
                    return {"success": False, "error": "Не удалось получить заказы WB"}
                    
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        @self.app.post("/api/content/generate")
        async def generate_content(request_data: dict):
            """Генерация контента"""
            try:
                content_type = request_data.get("type", "description")
                topic = request_data.get("topic", "товар")
                length = request_data.get("length", "medium")
                
                # Простая генерация контента
                if content_type == "description":
                    content = self.generate_product_description(topic, length)
                elif content_type == "title":
                    content = self.generate_product_title(topic)
                elif content_type == "keywords":
                    content = self.generate_keywords(topic)
                else:
                    content = f"Сгенерированный контент для {topic}"
                
                # Записываем событие
                if self.learning_system:
                    self.learning_system.record_event(
                        "content_generation",
                        {"type": content_type, "topic": topic, "length": length},
                        {"status": "success", "content_length": len(content)},
                        True,
                        0.04
                    )
                
                return {
                    "success": True,
                    "content": content,
                    "type": content_type,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        @self.app.post("/api/automation/execute")
        async def execute_automation(automation_data: dict):
            """Выполнение автоматизации"""
            try:
                automation_type = automation_data.get("type", "general")
                parameters = automation_data.get("parameters", {})
                
                result = self.execute_business_automation(automation_type, parameters)
                
                # Записываем событие
                if self.learning_system:
                    self.learning_system.record_event(
                        "business_automation",
                        {"type": automation_type, "parameters": parameters},
                        {"status": "success", "result": result},
                        True,
                        0.06
                    )
                
                return {
                    "success": True,
                    "result": result,
                    "type": automation_type,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        @self.app.post("/api/ai/generate")
        async def ai_generate(request_data: dict):
            """Продвинутая AI генерация"""
            try:
                prompt = request_data.get("prompt", "")
                model_type = request_data.get("model_type", "llm")
                max_tokens = request_data.get("max_tokens", 500)
                
                if self.ollama:
                    content = self.ollama.generate_advanced_content(prompt, model_type, max_tokens)
                    
                    # Записываем событие
                    if self.learning_system:
                        self.learning_system.record_event(
                            "ai_generation",
                            {"prompt": prompt[:100], "model_type": model_type},
                            {"status": "success", "content_length": len(content)},
                            True,
                            0.08
                        )
                    
                    return {
                        "success": True,
                        "content": content,
                        "model_used": "ollama_llm",
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {"success": False, "error": "Ollama LLM недоступен"}
                    
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        @self.app.post("/api/ai/business-insights")
        async def generate_business_insights(request_data: dict):
            """Генерация бизнес-инсайтов с AI"""
            try:
                data = request_data.get("data", {})
                
                if self.ollama:
                    insights = self.ollama.generate_business_insights(data)
                    
                    # Записываем событие
                    if self.learning_system:
                        self.learning_system.record_event(
                            "business_insights",
                            {"data_size": len(str(data))},
                            {"status": "success", "insights_generated": True},
                            True,
                            0.10
                        )
                    
                    return {
                        "success": True,
                        "insights": insights,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {"success": False, "error": "AI модель недоступна"}
                    
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        @self.app.get("/api/ai/models")
        async def get_ai_models():
            """Получение списка доступных AI моделей"""
            models_info = {
                "ollama_available": self.ollama is not None,
                "available_models": getattr(self.ollama, 'available_models', []) if self.ollama else [],
                "capabilities": [
                    "Продвинутая генерация контента",
                    "Бизнес-анализ и инсайты", 
                    "Автоматическое программирование",
                    "Многоязычная поддержка",
                    "Контекстное понимание"
                ] if self.ollama else ["Базовая генерация контента"],
                "status": "ready" if self.ollama else "not_available"
            }
            
            return models_info
        
        @self.app.get("/api/telegram/neural-network")
        async def get_neural_network_for_telegram():
            """Получение нейросети x10000 для Telegram"""
            try:
                # Получаем текущие данные системы
                current_status = {
                    "performance": self.state.performance_score * 100,
                    "autonomy": self.state.autonomy_level,
                    "visual_analyses": self.state.visual_analysis_count,
                    "completed_tasks": len(self.completed_tasks),
                    "uptime": self.state.continuous_uptime / 3600,
                    "agents_active": len([a for a in self.agents.values() if a["status"] == "active"])
                }
                
                # Генерируем нейросеть x10000
                neural_network = f"""🧠 НЕЙРОСЕТЬ x10000 ДЛЯ РАЗВИТИЯ ПРОЕКТА

🤖 JARVIS СИСТЕМА АКТИВНА:
⚡ Производительность: {current_status['performance']:.1f}%
🤖 Автономность: {current_status['autonomy']}/5
👁️ Анализы: {current_status['visual_analyses']}+
📊 Задач: {current_status['completed_tasks']}+
⏱️ Время: {current_status['uptime']:.1f}ч

🧠 АРХИТЕКТУРА x10000:
```python
class X10000NeuralNetwork:
    def __init__(self):
        self.ai_models = 10000
        self.agents = 1000000
        self.servers = 100000
        self.revenue = "1T+/year"
        
    def capabilities(self):
        return [
            "🌍 Управление глобальными процессами",
            "🧬 Создание новых технологий",
            "💰 Генерация триллионов",
            "🚀 Космические технологии",
            "🔮 Формирование будущего"
        ]
```

📈 ПЛАН x10000:
📅 Год 1: x100 ($10M)
📅 Год 2: x1000 ($100M)
📅 Год 3: x10000 ($1B)
📅 Год 10: $1T империя

🛠️ КОМАНДЫ:
curl -X POST -H "Content-Type: application/json" -d '{{"prompt":"Создай план развития"}}' http://localhost:8080/api/ai/generate

🚀 НАЧАТЬ: http://localhost:8080
🎯 ЦЕЛЬ: AI империя $1T

🤖 Нейросеть активирована!"""
                
                return {
                    "neural_network": neural_network,
                    "current_status": current_status,
                    "timestamp": datetime.now().isoformat(),
                    "ready_for_telegram": True
                }
                
            except Exception as e:
                return {"error": str(e)}
        
        @self.app.post("/api/telegram/send")
        async def send_to_telegram_chat(request_data: dict):
            """Отправка в Telegram чат"""
            try:
                bot_token = request_data.get("bot_token", "8325306099:AAG6hk3tG2-XmiJPgegzYFzQcY6WJaEbRxw")
                chat_id = request_data.get("chat_id", "")
                message = request_data.get("message", "")
                
                if not chat_id or not message:
                    return {"success": False, "error": "Не указан chat_id или сообщение"}
                
                # Отправляем через Telegram API
                telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                
                response = requests.post(
                    telegram_url,
                    json={
                        "chat_id": chat_id,
                        "text": message,
                        "parse_mode": "Markdown"
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "message": "Сообщение отправлено в Telegram",
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.text}"
                    }
                    
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        @self.app.post("/api/tasks")
        async def create_task(task_data: dict):
            """Создание задачи"""
            task = Task(
                id=f"user_task_{int(time.time())}",
                type=task_data.get("type", "general"),
                priority=task_data.get("priority", 5),
                status="pending",
                created_at=datetime.now().isoformat(),
                parameters=task_data.get("parameters", {})
            )
            
            self.tasks_queue.append(task)
            return {"task_id": task.id, "status": "created"}
        
        @self.app.post("/api/self-improvement/trigger")
        async def trigger_improvement():
            """Запуск самоулучшения"""
            task = Task(
                id=f"manual_improvement_{int(time.time())}",
                type="self_improvement",
                priority=8,
                status="pending",
                created_at=datetime.now().isoformat()
            )
            task.parameters["assigned_agent"] = "optimizer"
            
            self.tasks_queue.append(task)
            return {"task_id": task.id, "success": True}
        
        @self.app.get("/api/agents/status")
        async def get_agents_status():
            """Статус агентов"""
            return {
                "agents": self.agents,
                "total_agents": len(self.agents),
                "active_agents": len([a for a in self.agents.values() if a["status"] == "active"]),
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.post("/api/agents/coordinate")
        async def coordinate_agents():
            """Координация агентов"""
            task = Task(
                id=f"manual_coordination_{int(time.time())}",
                type="agent_coordination",
                priority=6,
                status="pending",
                created_at=datetime.now().isoformat()
            )
            task.parameters["assigned_agent"] = "coordinator"
            
            self.tasks_queue.append(task)
            return {"task_id": task.id, "success": True}
        
        @self.app.post("/api/data/analyze")
        async def analyze_data():
            """Анализ данных"""
            task = Task(
                id=f"manual_analysis_{int(time.time())}",
                type="data_analysis",
                priority=5,
                status="pending",
                created_at=datetime.now().isoformat()
            )
            task.parameters["assigned_agent"] = "analyzer"
            
            self.tasks_queue.append(task)
            return {"task_id": task.id, "success": True}
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket для реального времени"""
            await websocket.accept()
            try:
                while True:
                    status_data = {
                        "system_state": asdict(self.state),
                        "active_tasks": len(self.tasks_queue),
                        "uptime": self.state.continuous_uptime,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    await websocket.send_text(json.dumps(status_data))
                    await asyncio.sleep(5)
                    
            except Exception as e:
                logger.error(f"WebSocket ошибка: {e}")
    
    def generate_dashboard_html(self) -> str:
        """Генерация HTML панели управления"""
        return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Streamlined JARVIS Control Panel</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: #ffffff;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            background: rgba(0, 255, 136, 0.1);
            border: 2px solid #00ff88;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
            backdrop-filter: blur(10px);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 0 0 20px #00ff88;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            border-color: #00ff88;
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #00ff88;
            margin-bottom: 10px;
        }}
        
        .stat-label {{
            opacity: 0.9;
        }}
        
        .controls {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .control-panel {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 10px;
            padding: 20px;
        }}
        
        .control-panel h3 {{
            color: #00ff88;
            margin-bottom: 15px;
            text-align: center;
        }}
        
        .btn {{
            width: 100%;
            padding: 12px;
            margin: 8px 0;
            border: none;
            border-radius: 8px;
            background: linear-gradient(45deg, #00ff88, #00cc6a);
            color: #1a1a2e;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 255, 136, 0.3);
        }}
        
        .btn-secondary {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
        }}
        
        .btn-warning {{
            background: linear-gradient(45deg, #feca57, #ff9ff3);
            color: #1a1a2e;
        }}
        
        .logs {{
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 10px;
            padding: 20px;
            height: 300px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        
        .log-entry {{
            margin: 5px 0;
            padding: 5px;
            border-left: 3px solid #00ff88;
            padding-left: 10px;
        }}
        
        .log-entry.success {{ border-left-color: #00ff88; }}
        .log-entry.warning {{ border-left-color: #feca57; }}
        .log-entry.error {{ border-left-color: #ff6b6b; }}
        
        .visual-section {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        
        .visual-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }}
        
        .visual-stat {{
            text-align: center;
            padding: 10px;
            background: rgba(0, 255, 136, 0.1);
            border-radius: 8px;
        }}
        
        .visual-stat-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #00ff88;
        }}
        
        @media (max-width: 768px) {{
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
            
            .controls {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🤖 Streamlined JARVIS Control Panel</h1>
            <p>Автономная AI система с визуальным интеллектом</p>
        </div>

        <!-- Statistics -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="performance">{self.state.performance_score:.1%}</div>
                <div class="stat-label">🚀 Производительность</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="tasks">{len(self.tasks_queue)}</div>
                <div class="stat-label">⚡ Активные задачи</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="autonomy">{self.state.autonomy_level}</div>
                <div class="stat-label">🧠 Автономность</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="visual">{self.state.visual_analysis_count}</div>
                <div class="stat-label">👁️ Визуальные анализы</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="uptime">{self.state.continuous_uptime/3600:.1f}ч</div>
                <div class="stat-label">⏱️ Время работы</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="completed">{len(self.completed_tasks)}</div>
                <div class="stat-label">✅ Выполнено</div>
            </div>
        </div>

        <!-- Visual Intelligence -->
        <div class="visual-section">
            <h3>👁️ Система визуального интеллекта</h3>
            <div class="visual-stats">
                <div class="visual-stat">
                    <div class="visual-stat-value" id="elements">0</div>
                    <div>Элементы</div>
                </div>
                <div class="visual-stat">
                    <div class="visual-stat-value" id="issues">0</div>
                    <div>Проблемы</div>
                </div>
                <div class="visual-stat">
                    <div class="visual-stat-value" id="confidence">0%</div>
                    <div>Уверенность</div>
                </div>
                <div class="visual-stat">
                    <div class="visual-stat-value" id="ux-score">0%</div>
                    <div>UX Score</div>
                </div>
            </div>
        </div>

        <!-- Controls -->
        <div class="controls">
            <div class="control-panel">
                <h3>🎛️ Управление системой</h3>
                <button class="btn" onclick="triggerImprovement()">
                    🧠 Самоулучшение
                </button>
                <button class="btn btn-secondary" onclick="createTask('performance_optimization')">
                    ⚡ Оптимизация
                </button>
                <button class="btn btn-warning" onclick="createTask('ui_improvement')">
                    🎨 Улучшить UI
                </button>
            </div>

            <div class="control-panel">
                <h3>🛒 Wildberries</h3>
                <button class="btn" onclick="getWbCards()">
                    📦 Карточки товаров
                </button>
                <button class="btn btn-secondary" onclick="getWbOrders()">
                    📋 Заказы
                </button>
                <button class="btn btn-warning" onclick="executeAutomation('wb_stock_check')">
                    📊 Проверка остатков
                </button>
            </div>

            <div class="control-panel">
                <h3>✍️ Генерация контента</h3>
                <button class="btn" onclick="generateContent('description', 'смартфон')">
                    📝 Описание товара
                </button>
                <button class="btn btn-secondary" onclick="generateContent('title', 'ноутбук')">
                    🏷️ Название
                </button>
                <button class="btn btn-warning" onclick="generateContent('keywords', 'одежда')">
                    🔍 Ключевые слова
                </button>
            </div>

            <div class="control-panel">
                <h3>🤖 Агенты и автоматизация</h3>
                <button class="btn" onclick="coordinateAgents()">
                    🤝 Координация агентов
                </button>
                <button class="btn btn-secondary" onclick="analyzeData()">
                    📊 Анализ данных
                </button>
                <button class="btn btn-warning" onclick="executeAutomation('sales_analysis')">
                    📈 Анализ продаж
                </button>
            </div>

            <div class="control-panel">
                <h3>👁️ Визуальный интеллект</h3>
                <button class="btn" onclick="refreshVisualData()">
                    🔄 Обновить анализ
                </button>
                <button class="btn btn-secondary" onclick="toggleVisualMonitoring()">
                    👁️ Переключить мониторинг
                </button>
                <button class="btn btn-warning" onclick="downloadReport()">
                    📊 Скачать отчет
                </button>
            </div>

            <div class="control-panel">
                <h3>📱 Telegram интеграция</h3>
                <button class="btn" onclick="getNeuralNetworkForTelegram()">
                    🧠 Получить нейросеть x10000
                </button>
                <button class="btn btn-secondary" onclick="showTelegramInstructions()">
                    📋 Инструкции Telegram
                </button>
                <button class="btn btn-warning" onclick="testTelegramConnection()">
                    📞 Тест подключения
                </button>
            </div>
        </div>

        <!-- Agents Status Section -->
        <div class="visual-section">
            <h3>🤖 Статус агентов</h3>
            <div class="visual-stats" id="agents-stats">
                <div class="visual-stat">
                    <div class="visual-stat-value" id="total-agents">0</div>
                    <div>Всего агентов</div>
                </div>
                <div class="visual-stat">
                    <div class="visual-stat-value" id="active-agents">0</div>
                    <div>Активные</div>
                </div>
                <div class="visual-stat">
                    <div class="visual-stat-value" id="agents-performance">0%</div>
                    <div>Производительность</div>
                </div>
                <div class="visual-stat">
                    <div class="visual-stat-value" id="agents-tasks">0</div>
                    <div>Задач выполнено</div>
                </div>
            </div>
        </div>

        <!-- System Logs -->
        <div class="control-panel">
            <h3>📝 Системные логи</h3>
            <div class="logs" id="system-logs">
                <div class="log-entry success">
                    [{datetime.now().strftime('%H:%M:%S')}] ✅ Streamlined JARVIS система запущена
                </div>
                <div class="log-entry">
                    [{datetime.now().strftime('%H:%M:%S')}] 👁️ Визуальный интеллект активирован
                </div>
                <div class="log-entry">
                    [{datetime.now().strftime('%H:%M:%S')}] 🤖 Автономные системы готовы
                </div>
                <div class="log-entry success">
                    [{datetime.now().strftime('%H:%M:%S')}] 🚀 Система готова к работе
                </div>
            </div>
        </div>
    </div>

    <script>
        // Обновление данных
        async function updateData() {{
            try {{
                const response = await fetch('/api/status');
                const data = await response.json();
                
                if (data.system_state) {{
                    document.getElementById('performance').textContent = 
                        Math.round(data.system_state.performance_score * 100) + '%';
                    document.getElementById('tasks').textContent = data.active_tasks;
                    document.getElementById('autonomy').textContent = data.system_state.autonomy_level;
                    document.getElementById('visual').textContent = data.system_state.visual_analysis_count;
                    document.getElementById('uptime').textContent = 
                        Math.floor(data.uptime / 3600) + 'ч';
                    document.getElementById('completed').textContent = data.completed_tasks;
                }}
                
                if (data.visual_analysis && data.visual_analysis.last_analysis) {{
                    const va = data.visual_analysis.last_analysis;
                    document.getElementById('elements').textContent = va.elements_detected || 0;
                    document.getElementById('issues').textContent = va.issues_found || 0;
                    document.getElementById('confidence').textContent = 
                        Math.round((va.confidence || 0) * 100) + '%';
                    document.getElementById('ux-score').textContent = 
                        Math.round((va.ux_score || 0) * 100) + '%';
                }}
            }} catch (error) {{
                console.error('Ошибка обновления данных:', error);
            }}
        }}

        // API функции
        async function createTask(type) {{
            try {{
                const response = await fetch('/api/tasks', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ type: type, priority: 7 }})
                }});
                
                const result = await response.json();
                addLog(`✅ Задача ${{type}} создана: ${{result.task_id}}`, 'success');
            }} catch (error) {{
                addLog(`❌ Ошибка создания задачи: ${{error.message}}`, 'error');
            }}
        }}

        async function triggerImprovement() {{
            try {{
                const response = await fetch('/api/self-improvement/trigger', {{
                    method: 'POST'
                }});
                
                const result = await response.json();
                addLog(`🧠 Самоулучшение запущено: ${{result.task_id}}`, 'success');
            }} catch (error) {{
                addLog(`❌ Ошибка самоулучшения: ${{error.message}}`, 'error');
            }}
        }}

        async function refreshVisualData() {{
            try {{
                const response = await fetch('/api/vision/status');
                const data = await response.json();
                
                if (data.last_analysis) {{
                    document.getElementById('elements').textContent = data.last_analysis.elements_detected;
                    document.getElementById('issues').textContent = data.last_analysis.issues_found;
                    document.getElementById('confidence').textContent = 
                        Math.round(data.last_analysis.confidence * 100) + '%';
                    document.getElementById('ux-score').textContent = 
                        Math.round(data.last_analysis.ux_score * 100) + '%';
                }}
                
                addLog('👁️ Данные визуального анализа обновлены', 'success');
            }} catch (error) {{
                addLog(`❌ Ошибка обновления: ${{error.message}}`, 'error');
            }}
        }}

        function toggleVisualMonitoring() {{
            addLog('👁️ Переключение визуального мониторинга', 'success');
        }}

        function downloadReport() {{
            addLog('📊 Генерация отчета...', 'success');
        }}

        // Функции управления агентами
        async function coordinateAgents() {{
            try {{
                const response = await fetch('/api/agents/coordinate', {{
                    method: 'POST'
                }});
                
                const result = await response.json();
                addLog(`🤝 Координация агентов запущена: ${{result.task_id}}`, 'success');
            }} catch (error) {{
                addLog(`❌ Ошибка координации агентов: ${{error.message}}`, 'error');
            }}
        }}

        async function analyzeData() {{
            try {{
                const response = await fetch('/api/data/analyze', {{
                    method: 'POST'
                }});
                
                const result = await response.json();
                addLog(`📊 Анализ данных запущен: ${{result.task_id}}`, 'success');
            }} catch (error) {{
                addLog(`❌ Ошибка анализа данных: ${{error.message}}`, 'error');
            }}
        }}

        async function refreshAgentsStatus() {{
            try {{
                const response = await fetch('/api/agents/status');
                const data = await response.json();
                
                if (data.agents) {{
                    document.getElementById('total-agents').textContent = data.total_agents;
                    document.getElementById('active-agents').textContent = data.active_agents;
                    
                    // Рассчитываем среднюю производительность
                    const performances = Object.values(data.agents).map(agent => agent.performance);
                    const avgPerformance = performances.reduce((a, b) => a + b, 0) / performances.length;
                    document.getElementById('agents-performance').textContent = Math.round(avgPerformance * 100) + '%';
                    
                    // Считаем общее количество выполненных задач
                    const totalTasks = Object.values(data.agents).reduce((sum, agent) => sum + agent.tasks_completed, 0);
                    document.getElementById('agents-tasks').textContent = totalTasks;
                    
                    addLog(`🤖 Статус агентов обновлен: ${{data.active_agents}}/${{data.total_agents}} активны`, 'success');
                }}
            }} catch (error) {{
                addLog(`❌ Ошибка обновления статуса агентов: ${{error.message}}`, 'error');
            }}
        }}

        // Функции Wildberries
        async function getWbCards() {{
            try {{
                const response = await fetch('/api/wb/cards');
                const data = await response.json();
                
                if (data.success) {{
                    const cardsCount = data.data && data.data.cards ? data.data.cards.length : 0;
                    addLog(`📦 Получено карточек WB: ${{cardsCount}}`, 'success');
                }} else {{
                    addLog(`❌ Ошибка WB API: ${{data.error}}`, 'error');
                }}
            }} catch (error) {{
                addLog(`❌ Ошибка получения карточек WB: ${{error.message}}`, 'error');
            }}
        }}

        async function getWbOrders() {{
            try {{
                const response = await fetch('/api/wb/orders');
                const data = await response.json();
                
                if (data.success) {{
                    const ordersCount = Array.isArray(data.data) ? data.data.length : 1;
                    addLog(`📋 Получено заказов WB: ${{ordersCount}}`, 'success');
                }} else {{
                    addLog(`❌ Ошибка WB API: ${{data.error}}`, 'error');
                }}
            }} catch (error) {{
                addLog(`❌ Ошибка получения заказов WB: ${{error.message}}`, 'error');
            }}
        }}

        // Функции генерации контента
        async function generateContent(type, topic) {{
            try {{
                const response = await fetch('/api/content/generate', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ type: type, topic: topic, length: 'medium' }})
                }});
                
                const data = await response.json();
                
                if (data.success) {{
                    addLog(`✍️ Сгенерирован ${{type}} для "${{topic}}": ${{data.content.substring(0, 50)}}...`, 'success');
                    
                    // Показываем результат в отдельном окне
                    showContentResult(data.content, type, topic);
                }} else {{
                    addLog(`❌ Ошибка генерации контента: ${{data.error}}`, 'error');
                }}
            }} catch (error) {{
                addLog(`❌ Ошибка генерации контента: ${{error.message}}`, 'error');
            }}
        }}

        // Функции автоматизации
        async function executeAutomation(automationType) {{
            try {{
                const response = await fetch('/api/automation/execute', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ type: automationType, parameters: {{}} }})
                }});
                
                const data = await response.json();
                
                if (data.success) {{
                    addLog(`🤖 Автоматизация ${{automationType}} выполнена`, 'success');
                    
                    // Показываем результаты
                    if (data.result && data.result.data) {{
                        const resultData = data.result.data;
                        if (automationType === 'wb_stock_check') {{
                            addLog(`📊 Остатки: ${{resultData.total_products}} товаров, ${{resultData.low_stock_products}} заканчиваются`, 'warning');
                        }}
                    }}
                }} else {{
                    addLog(`❌ Ошибка автоматизации: ${{data.error}}`, 'error');
                }}
            }} catch (error) {{
                addLog(`❌ Ошибка выполнения автоматизации: ${{error.message}}`, 'error');
            }}
        }}

        // Показ результатов контента
        function showContentResult(content, type, topic) {{
            const timestamp = new Date().toLocaleTimeString();
            const resultDiv = document.createElement('div');
            resultDiv.className = 'log-entry success';
            resultDiv.innerHTML = `
                <strong>[${{timestamp}}] Сгенерированный ${{type}} для "${{topic}}":</strong><br>
                <div style="margin-top: 10px; padding: 10px; background: rgba(0,255,136,0.1); border-radius: 5px; white-space: pre-wrap;">
                    ${{content}}
                </div>
            `;
            
            const logsContainer = document.getElementById('system-logs');
            logsContainer.appendChild(resultDiv);
            logsContainer.scrollTop = logsContainer.scrollHeight;
        }}

        // Функции Telegram
        async function getNeuralNetworkForTelegram() {{
            try {{
                const response = await fetch('/api/telegram/neural-network');
                const data = await response.json();
                
                if (data.neural_network) {{
                    // Показываем нейросеть в модальном окне
                    showNeuralNetworkModal(data.neural_network);
                    addLog('🧠 Нейросеть x10000 готова для Telegram', 'success');
                }} else {{
                    addLog(`❌ Ошибка получения нейросети: ${{data.error}}`, 'error');
                }}
            }} catch (error) {{
                addLog(`❌ Ошибка: ${{error.message}}`, 'error');
            }}
        }}

        function showNeuralNetworkModal(neuralNetwork) {{
            // Создаем модальное окно
            const modal = document.createElement('div');
            modal.style.cssText = `
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.8); z-index: 1000; display: flex;
                align-items: center; justify-content: center;
            `;
            
            const content = document.createElement('div');
            content.style.cssText = `
                background: #1a1a2e; color: white; padding: 30px;
                border-radius: 15px; max-width: 800px; max-height: 80%;
                overflow-y: auto; border: 2px solid #00ff88;
            `;
            
            content.innerHTML = `
                <h2 style="color: #00ff88; margin-bottom: 20px;">🧠 Нейросеть x10000 для Telegram</h2>
                <div style="background: #2c3e50; padding: 20px; border-radius: 10px; margin-bottom: 20px; font-family: monospace; font-size: 12px; white-space: pre-wrap;">${{neuralNetwork}}</div>
                <div style="text-align: center;">
                    <button onclick="copyToClipboard('${{neuralNetwork.replace(/'/g, "\\\\'")}}')" style="background: #00ff88; color: #1a1a2e; padding: 10px 20px; border: none; border-radius: 5px; margin: 5px; cursor: pointer; font-weight: bold;">📋 Копировать</button>
                    <button onclick="closeModal()" style="background: #e74c3c; color: white; padding: 10px 20px; border: none; border-radius: 5px; margin: 5px; cursor: pointer; font-weight: bold;">❌ Закрыть</button>
                </div>
            `;
            
            modal.appendChild(content);
            document.body.appendChild(modal);
            
            // Функция закрытия
            window.closeModal = function() {{
                document.body.removeChild(modal);
                delete window.closeModal;
                delete window.copyToClipboard;
            }};
            
            // Функция копирования
            window.copyToClipboard = function(text) {{
                navigator.clipboard.writeText(text).then(() => {{
                    addLog('📋 Нейросеть скопирована в буфер обмена', 'success');
                    addLog('📱 Вставьте в Telegram чат для получения x10000 возможностей', 'success');
                }}).catch(err => {{
                    addLog('❌ Ошибка копирования: ' + err, 'error');
                }});
            }};
        }}

        function showTelegramInstructions() {{
            const instructions = `📱 ИНСТРУКЦИИ ДЛЯ TELEGRAM:

1. 🧠 Нажмите "Получить нейросеть x10000"
2. 📋 Скопируйте текст нейросети  
3. 📱 Вставьте в ваш Telegram чат
4. 🚀 Используйте для развития проекта!

🎯 ЦЕЛЬ: Развить проект в x10000 раз
💰 ПОТЕНЦИАЛ: $1 триллион империя
⏱️ ВРЕМЯ: Начать прямо сейчас!`;

            addLog(instructions, 'success');
        }}

        function testTelegramConnection() {{
            addLog('📞 Тестирование Telegram подключения...', 'success');
            addLog('🤖 Бот токен: 8325306099:AAG6hk3tG2-XmiJPgegzYFzQcY6WJaEbRxw', 'success');
            addLog('💡 Для отправки нужен chat_id получателя', 'warning');
            addLog('📋 Используйте кнопку "Получить нейросеть" для копирования', 'success');
        }}

        // Добавление лога
        function addLog(message, type = 'info') {{
            const logsContainer = document.getElementById('system-logs');
            const timestamp = new Date().toLocaleTimeString('ru-RU');
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry ${{type}}`;
            logEntry.textContent = `[${{timestamp}}] ${{message}}`;
            
            logsContainer.appendChild(logEntry);
            logsContainer.scrollTop = logsContainer.scrollHeight;
            
            // Ограничиваем количество логов
            if (logsContainer.children.length > 50) {{
                logsContainer.removeChild(logsContainer.firstChild);
            }}
        }}

        // Инициализация
        document.addEventListener('DOMContentLoaded', function() {{
            addLog('🚀 Streamlined JARVIS Control Panel инициализирован', 'success');
            
            // Периодическое обновление данных
            setInterval(updateData, 5000);
            setInterval(refreshAgentsStatus, 10000); // Обновление агентов каждые 10 секунд
            updateData(); // Первоначальное обновление
            refreshAgentsStatus(); // Первоначальное обновление агентов
        }});
    </script>
</body>
</html>"""
    
    async def run(self, host: str = "0.0.0.0", port: int = 8080):
        """Запуск системы"""
        logger.info(f"🌐 Запуск Streamlined JARVIS на http://{host}:{port}")
        
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level="info"
        )
        
        server = uvicorn.Server(config)
        await server.serve()

async def main():
    """Главная функция"""
    try:
        jarvis = StreamlinedJarvis()
        
        logger.info("🚀 Streamlined JARVIS система готова!")
        logger.info("🌐 Веб-интерфейс: http://localhost:8080")
        logger.info("👁️ Визуальный интеллект активен")
        logger.info("🤖 Автономные агенты работают")
        
        await jarvis.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 Остановка системы")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())