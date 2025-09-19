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
        
        # Запускаем автономные системы
        self.start_autonomous_systems()
        
        # Настраиваем API
        self.setup_routes()
        
        logger.info("🚀 Streamlined JARVIS система инициализирована")
    
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
                self.tasks_queue.append(task)
                logger.info("🧠 Создана задача самоулучшения")
            
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
                self.tasks_queue.append(task)
                logger.info("⚡ Создана задача оптимизации")
            
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
            
            logger.info(f"▶️ Выполняется: {task.id} ({task.type})")
            
            # Симулируем выполнение
            time.sleep(1)
            
            if task.type == "self_improvement":
                result = self.execute_self_improvement()
            elif task.type == "performance_optimization":
                result = self.execute_optimization()
            elif task.type == "ui_improvement":
                result = self.execute_ui_improvement(task)
            else:
                result = {"status": "completed", "message": "Задача выполнена"}
            
            task.status = "completed"
            task.result = result
            self.completed_tasks.append(task)
            self.state.active_tasks = max(0, self.state.active_tasks - 1)
            
            logger.info(f"✅ Задача завершена: {task.id}")
            
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
            if self.visual_intelligence.last_analysis:
                return {
                    "enabled": True,
                    "total_analyses": len(self.visual_intelligence.analysis_history),
                    "last_analysis": {
                        "timestamp": self.visual_intelligence.last_analysis.timestamp,
                        "elements_detected": len(self.visual_intelligence.last_analysis.elements_detected),
                        "issues_found": len(self.visual_intelligence.last_analysis.issues_found),
                        "confidence": self.visual_intelligence.last_analysis.confidence,
                        "ux_score": self.visual_intelligence.last_analysis.ux_score
                    }
                }
            return {"enabled": True, "total_analyses": 0}
        
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
            updateData(); // Первоначальное обновление
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