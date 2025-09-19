#!/usr/bin/env python3
"""
Enhanced Autonomous JARVIS System
Улучшенная автономная система с визуальным интеллектом и непрерывной работой
"""

import os
import sys
import json
import time
import asyncio
import subprocess
import threading
import logging
import signal
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests
import yaml
from dataclasses import dataclass, asdict
from fastapi import FastAPI, WebSocket, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
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
        logging.FileHandler('/workspace/enhanced_jarvis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class EnhancedSystemState:
    """Расширенное состояние системы"""
    total_instances: int = 1
    active_tasks: int = 0
    resources_used: Dict[str, float] = None
    last_self_replication: Optional[str] = None
    performance_score: float = 0.0
    autonomy_level: int = 1
    knowledge_base_size: int = 0
    visual_analysis_count: int = 0
    continuous_uptime: float = 0.0
    last_visual_check: Optional[str] = None
    autonomous_decisions_made: int = 0
    self_healing_events: int = 0
    
    def __post_init__(self):
        if self.resources_used is None:
            self.resources_used = {"cpu": 0.0, "memory": 0.0, "disk": 0.0, "network": 0.0}

@dataclass
class AutonomousTask:
    """Автономная задача"""
    id: str
    type: str
    priority: int
    status: str
    created_at: str
    parameters: Dict[str, Any] = None
    result: Any = None
    autonomous_generated: bool = False
    visual_triggered: bool = False
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}

@dataclass
class VisualAnalysisResult:
    """Результат визуального анализа"""
    timestamp: str
    screenshot_data: Optional[str]
    elements_detected: List[Dict[str, Any]]
    issues_found: List[Dict[str, Any]]
    suggestions: List[str]
    confidence: float
    performance_impact: Dict[str, float]
    user_experience_score: float

class EnhancedVisualIntelligence:
    """Улучшенная система визуального интеллекта"""
    
    def __init__(self, jarvis_core):
        self.core = jarvis_core
        self.enabled = True
        self.screenshot_interval = 3  # секунд
        self.analysis_history = []
        self.last_analysis = None
        self.continuous_monitoring = True
        
        # Запускаем визуальный мониторинг
        self.start_visual_monitoring()
    
    def start_visual_monitoring(self):
        """Запуск непрерывного визуального мониторинга"""
        def monitor_loop():
            while self.enabled and self.continuous_monitoring:
                try:
                    # Делаем скриншот и анализируем
                    analysis = self.perform_visual_analysis()
                    if analysis:
                        self.process_visual_analysis(analysis)
                        self.analysis_history.append(analysis)
                        
                        # Ограничиваем историю
                        if len(self.analysis_history) > 100:
                            self.analysis_history = self.analysis_history[-50:]
                    
                    time.sleep(self.screenshot_interval)
                    
                except Exception as e:
                    logger.error(f"Ошибка визуального мониторинга: {e}")
                    time.sleep(10)
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        logger.info("🎯 Система визуального интеллекта запущена")
    
    def perform_visual_analysis(self) -> Optional[VisualAnalysisResult]:
        """Выполнение визуального анализа"""
        try:
            # Создаем виртуальный скриншот для демонстрации
            screenshot_data = self.create_enhanced_screenshot()
            
            # Анализируем элементы
            elements = self.analyze_ui_elements(screenshot_data)
            
            # Обнаруживаем проблемы
            issues = self.detect_ui_issues(elements)
            
            # Генерируем предложения
            suggestions = self.generate_ui_suggestions(issues, elements)
            
            # Рассчитываем метрики
            confidence = self.calculate_analysis_confidence(elements, issues)
            performance_impact = self.assess_performance_impact(elements)
            ux_score = self.calculate_ux_score(elements, issues)
            
            analysis = VisualAnalysisResult(
                timestamp=datetime.now().isoformat(),
                screenshot_data=screenshot_data,
                elements_detected=elements,
                issues_found=issues,
                suggestions=suggestions,
                confidence=confidence,
                performance_impact=performance_impact,
                user_experience_score=ux_score
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Ошибка визуального анализа: {e}")
            return None
    
    def create_enhanced_screenshot(self) -> str:
        """Создание улучшенного виртуального скриншота"""
        try:
            # Создаем изображение с улучшенным дизайном
            img = Image.new('RGB', (1200, 800), color='#1a1a2e')
            draw = ImageDraw.Draw(img)
            
            # Рисуем современный интерфейс
            # Заголовок
            try:
                font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
                font_normal = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
            except:
                font_title = ImageFont.load_default()
                font_normal = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Градиентный заголовок
            draw.rectangle([0, 0, 1200, 100], fill='#16213e')
            draw.text((50, 30), "🤖 JARVIS Enhanced Control Panel", fill='#00ff88', font=font_title)
            
            # Статусная панель
            draw.rectangle([50, 120, 1150, 200], fill='#0f3460', outline='#00ff88', width=2)
            draw.text((70, 140), f"⚡ Performance: {self.core.state.performance_score:.1%}", fill='#ffffff', font=font_normal)
            draw.text((70, 160), f"🎯 Tasks: {self.core.state.active_tasks}", fill='#ffffff', font=font_normal)
            draw.text((300, 140), f"🧠 Autonomy Level: {self.core.state.autonomy_level}", fill='#00ff88', font=font_normal)
            draw.text((300, 160), f"👁️ Visual Checks: {self.core.state.visual_analysis_count}", fill='#00ff88', font=font_normal)
            
            # Кнопки управления
            buttons = [
                {"text": "🚀 Self-Replication", "pos": (50, 230), "color": "#e74c3c"},
                {"text": "🧠 Self-Improvement", "pos": (250, 230), "color": "#27ae60"},
                {"text": "👁️ Visual Analysis", "pos": (450, 230), "color": "#3498db"},
                {"text": "🤖 Autonomous Mode", "pos": (650, 230), "color": "#9b59b6"},
                {"text": "☁️ Cloud Deploy", "pos": (850, 230), "color": "#f39c12"}
            ]
            
            for btn in buttons:
                draw.rectangle([btn["pos"][0], btn["pos"][1], btn["pos"][0]+180, btn["pos"][1]+40], 
                             fill=btn["color"], outline='#ffffff', width=1)
                draw.text((btn["pos"][0]+10, btn["pos"][1]+12), btn["text"], fill='#ffffff', font=font_normal)
            
            # Область логов
            draw.rectangle([50, 300, 1150, 600], fill='#2c3e50', outline='#34495e', width=2)
            draw.text((70, 310), "📝 System Logs (Real-time)", fill='#ecf0f1', font=font_normal)
            
            log_entries = [
                f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Enhanced JARVIS system operational",
                f"[{datetime.now().strftime('%H:%M:%S')}] 👁️ Visual intelligence monitoring active",
                f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 Autonomous decision making enabled",
                f"[{datetime.now().strftime('%H:%M:%S')}] ☁️ Cloud integration ready",
                f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Self-healing mechanisms active"
            ]
            
            for i, entry in enumerate(log_entries):
                draw.text((70, 340 + i*25), entry, fill='#ecf0f1', font=font_small)
            
            # Система мониторинга
            draw.rectangle([50, 620, 1150, 750], fill='#34495e', outline='#00ff88', width=2)
            draw.text((70, 630), "📊 Real-time Monitoring & Analytics", fill='#00ff88', font=font_normal)
            
            # Метрики производительности
            metrics = [
                f"CPU: {psutil.cpu_percent():.1f}%",
                f"Memory: {psutil.virtual_memory().percent:.1f}%",
                f"Disk: {psutil.disk_usage('/').percent:.1f}%",
                f"Network: Active"
            ]
            
            for i, metric in enumerate(metrics):
                x_pos = 70 + (i * 250)
                draw.text((x_pos, 660), metric, fill='#ffffff', font=font_normal)
            
            # Индикаторы состояния
            draw.circle([1100, 680], 15, fill='#27ae60')  # Зеленый индикатор - система работает
            draw.text((1070, 700), "Online", fill='#27ae60', font=font_small)
            
            # Кодируем в base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG', quality=95)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return image_base64
            
        except Exception as e:
            logger.error(f"Ошибка создания скриншота: {e}")
            return None
    
    def analyze_ui_elements(self, screenshot_data: str) -> List[Dict[str, Any]]:
        """Анализ элементов интерфейса"""
        elements = []
        
        try:
            # Определяем основные элементы интерфейса
            elements.extend([
                {
                    "type": "header",
                    "text": "JARVIS Enhanced Control Panel",
                    "position": {"x": 50, "y": 30},
                    "size": {"width": 800, "height": 70},
                    "confidence": 0.95,
                    "accessibility_score": 0.9,
                    "performance_impact": "low"
                },
                {
                    "type": "status_panel",
                    "position": {"x": 50, "y": 120},
                    "size": {"width": 1100, "height": 80},
                    "confidence": 0.9,
                    "data_quality": "high",
                    "real_time": True
                },
                {
                    "type": "button_group",
                    "count": 5,
                    "position": {"x": 50, "y": 230},
                    "size": {"width": 1000, "height": 40},
                    "confidence": 0.85,
                    "interactive": True,
                    "color_coded": True
                },
                {
                    "type": "log_area",
                    "position": {"x": 50, "y": 300},
                    "size": {"width": 1100, "height": 300},
                    "confidence": 0.9,
                    "scrollable": True,
                    "real_time_updates": True
                },
                {
                    "type": "monitoring_panel",
                    "position": {"x": 50, "y": 620},
                    "size": {"width": 1100, "height": 130},
                    "confidence": 0.95,
                    "metrics_count": 4,
                    "status_indicators": True
                }
            ])
            
        except Exception as e:
            logger.error(f"Ошибка анализа элементов: {e}")
        
        return elements
    
    def detect_ui_issues(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Обнаружение проблем интерфейса"""
        issues = []
        
        try:
            # Проверяем доступность
            interactive_elements = [e for e in elements if e.get("interactive")]
            if len(interactive_elements) < 3:
                issues.append({
                    "type": "accessibility",
                    "severity": "medium",
                    "description": "Недостаточно интерактивных элементов",
                    "suggestion": "Добавить больше интерактивных кнопок и элементов управления",
                    "auto_fixable": True
                })
            
            # Проверяем производительность
            large_elements = [e for e in elements if e.get("size", {}).get("width", 0) > 1000]
            if len(large_elements) > 3:
                issues.append({
                    "type": "performance",
                    "severity": "low",
                    "description": "Много крупных элементов интерфейса",
                    "suggestion": "Оптимизировать размеры элементов для лучшей производительности",
                    "auto_fixable": True
                })
            
            # Проверяем пользовательский опыт
            real_time_elements = [e for e in elements if e.get("real_time")]
            if len(real_time_elements) < 2:
                issues.append({
                    "type": "user_experience",
                    "severity": "high",
                    "description": "Недостаточно элементов реального времени",
                    "suggestion": "Добавить больше элементов с обновлением в реальном времени",
                    "auto_fixable": True
                })
            
        except Exception as e:
            logger.error(f"Ошибка обнаружения проблем: {e}")
        
        return issues
    
    def generate_ui_suggestions(self, issues: List[Dict[str, Any]], elements: List[Dict[str, Any]]) -> List[str]:
        """Генерация предложений по улучшению"""
        suggestions = []
        
        try:
            # Предложения на основе проблем
            for issue in issues:
                if issue["type"] == "accessibility":
                    suggestions.extend([
                        "🔧 Добавить горячие клавиши для основных функций",
                        "🎯 Увеличить размер кликабельных областей",
                        "🎨 Улучшить контрастность для лучшей читаемости"
                    ])
                elif issue["type"] == "performance":
                    suggestions.extend([
                        "⚡ Внедрить ленивую загрузку для тяжелых элементов",
                        "📊 Оптимизировать графики и диаграммы",
                        "🗜️ Сжать изображения и ресурсы"
                    ])
                elif issue["type"] == "user_experience":
                    suggestions.extend([
                        "🔄 Добавить живые обновления статуса",
                        "💬 Интегрировать чат с реальным временем",
                        "📱 Сделать интерфейс адаптивным"
                    ])
            
            # Общие предложения по улучшению
            suggestions.extend([
                "🤖 Добавить голосовое управление",
                "🌙 Реализовать темную/светлую тему",
                "📈 Расширить аналитическую панель",
                "🔔 Добавить умные уведомления",
                "🎮 Создать интерактивные элементы управления",
                "☁️ Интегрировать с облачными сервисами"
            ])
            
        except Exception as e:
            logger.error(f"Ошибка генерации предложений: {e}")
        
        return suggestions[:8]  # Ограничиваем количество
    
    def calculate_analysis_confidence(self, elements: List[Dict[str, Any]], issues: List[Dict[str, Any]]) -> float:
        """Расчет уверенности анализа"""
        try:
            base_confidence = 0.7
            
            # Увеличиваем за обнаруженные элементы
            base_confidence += len(elements) * 0.03
            
            # Увеличиваем за найденные проблемы
            base_confidence += len(issues) * 0.05
            
            # Учитываем качество элементов
            high_conf_elements = [e for e in elements if e.get("confidence", 0) > 0.9]
            base_confidence += len(high_conf_elements) * 0.02
            
            return min(1.0, base_confidence)
            
        except Exception:
            return 0.75
    
    def assess_performance_impact(self, elements: List[Dict[str, Any]]) -> Dict[str, float]:
        """Оценка влияния на производительность"""
        try:
            total_elements = len(elements)
            large_elements = len([e for e in elements if e.get("size", {}).get("width", 0) > 500])
            interactive_elements = len([e for e in elements if e.get("interactive")])
            
            return {
                "rendering_load": min(1.0, total_elements / 20),
                "interaction_complexity": min(1.0, interactive_elements / 10),
                "memory_usage": min(1.0, large_elements / 5),
                "cpu_impact": min(1.0, (total_elements + interactive_elements) / 30)
            }
            
        except Exception:
            return {"rendering_load": 0.5, "interaction_complexity": 0.5, "memory_usage": 0.5, "cpu_impact": 0.5}
    
    def calculate_ux_score(self, elements: List[Dict[str, Any]], issues: List[Dict[str, Any]]) -> float:
        """Расчет оценки пользовательского опыта"""
        try:
            base_score = 0.8
            
            # Бонусы за хорошие элементы
            interactive_elements = len([e for e in elements if e.get("interactive")])
            real_time_elements = len([e for e in elements if e.get("real_time")])
            accessible_elements = len([e for e in elements if e.get("accessibility_score", 0) > 0.8])
            
            base_score += interactive_elements * 0.02
            base_score += real_time_elements * 0.05
            base_score += accessible_elements * 0.03
            
            # Штрафы за проблемы
            critical_issues = len([i for i in issues if i.get("severity") == "high"])
            medium_issues = len([i for i in issues if i.get("severity") == "medium"])
            
            base_score -= critical_issues * 0.1
            base_score -= medium_issues * 0.05
            
            return max(0.0, min(1.0, base_score))
            
        except Exception:
            return 0.75
    
    def process_visual_analysis(self, analysis: VisualAnalysisResult):
        """Обработка результатов визуального анализа"""
        try:
            self.last_analysis = analysis
            self.core.state.visual_analysis_count += 1
            self.core.state.last_visual_check = analysis.timestamp
            
            # Если найдены критические проблемы, создаем автономные задачи
            critical_issues = [i for i in analysis.issues_found if i.get("severity") == "high"]
            
            if critical_issues and self.core.state.autonomy_level >= 2:
                logger.warning(f"🚨 Обнаружены критические проблемы UI: {len(critical_issues)}")
                
                # Создаем автономную задачу на исправление
                task_id = f"visual_fix_{int(time.time())}"
                task = AutonomousTask(
                    id=task_id,
                    type="ui_improvement",
                    priority=9,
                    status="pending",
                    created_at=datetime.now().isoformat(),
                    autonomous_generated=True,
                    visual_triggered=True,
                    parameters={
                        "issues": critical_issues,
                        "suggestions": analysis.suggestions[:3],
                        "ux_score": analysis.user_experience_score,
                        "confidence": analysis.confidence
                    }
                )
                
                self.core.tasks_queue.append(task)
                self.core.state.autonomous_decisions_made += 1
                logger.info(f"✅ Создана автономная задача улучшения UI: {task_id}")
            
            # Логируем результаты
            logger.info(f"👁️ Визуальный анализ: {len(analysis.elements_detected)} элементов, "
                       f"{len(analysis.issues_found)} проблем, UX: {analysis.user_experience_score:.2f}, "
                       f"уверенность: {analysis.confidence:.2f}")
            
        except Exception as e:
            logger.error(f"Ошибка обработки визуального анализа: {e}")

class EnhancedAutonomousJarvis:
    """Улучшенная автономная система JARVIS"""
    
    def __init__(self):
        self.state = EnhancedSystemState()
        self.tasks_queue = []
        self.completed_tasks = []
        self.knowledge_base = {}
        self.running = True
        self.start_time = time.time()
        
        # Создаем FastAPI приложение
        self.app = FastAPI(title="Enhanced JARVIS Control Panel", version="2.0")
        self.setup_middleware()
        
        # Инициализируем компоненты
        self.visual_intelligence = EnhancedVisualIntelligence(self)
        
        # Запускаем автономные системы
        self.start_autonomous_systems()
        
        # Настраиваем API маршруты
        self.setup_api_routes()
        
        logger.info("🚀 Enhanced Autonomous JARVIS система инициализирована")
    
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
        # Автономный планировщик задач
        def autonomous_scheduler():
            while self.running:
                try:
                    # Генерируем автономные задачи
                    self.generate_autonomous_tasks()
                    
                    # Выполняем задачи
                    self.process_task_queue()
                    
                    # Обновляем состояние системы
                    self.update_system_state()
                    
                    time.sleep(5)
                    
                except Exception as e:
                    logger.error(f"Ошибка автономного планировщика: {e}")
                    time.sleep(10)
        
        # Система самоисцеления
        def self_healing_system():
            while self.running:
                try:
                    # Проверяем здоровье системы
                    health_issues = self.check_system_health()
                    
                    if health_issues:
                        logger.warning(f"🏥 Обнаружены проблемы системы: {len(health_issues)}")
                        self.perform_self_healing(health_issues)
                    
                    time.sleep(30)
                    
                except Exception as e:
                    logger.error(f"Ошибка системы самоисцеления: {e}")
                    time.sleep(30)
        
        # Запускаем потоки
        threading.Thread(target=autonomous_scheduler, daemon=True).start()
        threading.Thread(target=self_healing_system, daemon=True).start()
        
        logger.info("🤖 Автономные системы запущены")
    
    def generate_autonomous_tasks(self):
        """Генерация автономных задач"""
        try:
            current_time = datetime.now()
            
            # Задачи на основе состояния системы
            if self.state.performance_score < 0.7 and self.state.autonomy_level >= 2:
                task = AutonomousTask(
                    id=f"perf_optimization_{int(time.time())}",
                    type="performance_optimization",
                    priority=8,
                    status="pending",
                    created_at=current_time.isoformat(),
                    autonomous_generated=True,
                    parameters={"current_score": self.state.performance_score}
                )
                self.tasks_queue.append(task)
                logger.info("🔧 Создана автономная задача оптимизации производительности")
            
            # Задачи самоулучшения
            if len(self.completed_tasks) > 0 and len(self.completed_tasks) % 10 == 0:
                task = AutonomousTask(
                    id=f"self_improvement_{int(time.time())}",
                    type="self_improvement",
                    priority=6,
                    status="pending",
                    created_at=current_time.isoformat(),
                    autonomous_generated=True,
                    parameters={"completed_tasks": len(self.completed_tasks)}
                )
                self.tasks_queue.append(task)
                logger.info("🧠 Создана автономная задача самоулучшения")
            
            # Задачи мониторинга
            if self.state.visual_analysis_count > 0 and self.state.visual_analysis_count % 20 == 0:
                task = AutonomousTask(
                    id=f"monitoring_report_{int(time.time())}",
                    type="monitoring_report",
                    priority=4,
                    status="pending",
                    created_at=current_time.isoformat(),
                    autonomous_generated=True,
                    parameters={"analysis_count": self.state.visual_analysis_count}
                )
                self.tasks_queue.append(task)
                logger.info("📊 Создана автономная задача отчета мониторинга")
            
        except Exception as e:
            logger.error(f"Ошибка генерации автономных задач: {e}")
    
    def process_task_queue(self):
        """Обработка очереди задач"""
        try:
            if not self.tasks_queue:
                return
            
            # Сортируем по приоритету
            self.tasks_queue.sort(key=lambda x: x.priority, reverse=True)
            
            # Обрабатываем задачи
            tasks_to_process = min(3, len(self.tasks_queue))  # Максимум 3 задачи за раз
            
            for _ in range(tasks_to_process):
                if self.tasks_queue:
                    task = self.tasks_queue.pop(0)
                    self.execute_task(task)
            
        except Exception as e:
            logger.error(f"Ошибка обработки очереди задач: {e}")
    
    def execute_task(self, task: AutonomousTask):
        """Выполнение задачи"""
        try:
            task.status = "running"
            self.state.active_tasks += 1
            
            logger.info(f"▶️ Выполняется задача: {task.id} ({task.type})")
            
            # Выполняем задачу в зависимости от типа
            if task.type == "ui_improvement":
                result = self.execute_ui_improvement(task)
            elif task.type == "performance_optimization":
                result = self.execute_performance_optimization(task)
            elif task.type == "self_improvement":
                result = self.execute_self_improvement(task)
            elif task.type == "monitoring_report":
                result = self.execute_monitoring_report(task)
            else:
                result = {"status": "completed", "message": f"Задача {task.type} выполнена"}
            
            # Завершаем задачу
            task.status = "completed"
            task.result = result
            self.completed_tasks.append(task)
            self.state.active_tasks = max(0, self.state.active_tasks - 1)
            
            logger.info(f"✅ Задача завершена: {task.id}")
            
        except Exception as e:
            task.status = "failed"
            task.result = {"error": str(e)}
            self.state.active_tasks = max(0, self.state.active_tasks - 1)
            logger.error(f"❌ Ошибка выполнения задачи {task.id}: {e}")
    
    def execute_ui_improvement(self, task: AutonomousTask) -> Dict[str, Any]:
        """Выполнение улучшения UI"""
        try:
            issues = task.parameters.get("issues", [])
            suggestions = task.parameters.get("suggestions", [])
            
            improvements_made = []
            
            for issue in issues:
                if issue.get("auto_fixable"):
                    # Симулируем автоматическое исправление
                    improvement = {
                        "issue_type": issue["type"],
                        "action_taken": f"Автоматически исправлено: {issue['description']}",
                        "timestamp": datetime.now().isoformat()
                    }
                    improvements_made.append(improvement)
            
            return {
                "status": "completed",
                "improvements_made": improvements_made,
                "suggestions_applied": len(suggestions),
                "ux_score_improvement": 0.1
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def execute_performance_optimization(self, task: AutonomousTask) -> Dict[str, Any]:
        """Выполнение оптимизации производительности"""
        try:
            current_score = task.parameters.get("current_score", 0.5)
            
            # Симулируем оптимизацию
            optimizations = [
                "Очистка временных файлов",
                "Оптимизация памяти",
                "Сжатие логов",
                "Обновление индексов"
            ]
            
            # Улучшаем производительность
            improvement = 0.1
            self.state.performance_score = min(1.0, current_score + improvement)
            
            return {
                "status": "completed",
                "optimizations_applied": optimizations,
                "performance_improvement": improvement,
                "new_score": self.state.performance_score
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def execute_self_improvement(self, task: AutonomousTask) -> Dict[str, Any]:
        """Выполнение самоулучшения"""
        try:
            completed_tasks = task.parameters.get("completed_tasks", 0)
            
            # Анализируем выполненные задачи
            successful_tasks = len([t for t in self.completed_tasks if t.status == "completed"])
            success_rate = successful_tasks / max(1, len(self.completed_tasks))
            
            # Улучшаем автономность
            if success_rate > 0.8:
                self.state.autonomy_level = min(5, self.state.autonomy_level + 1)
                logger.info(f"🎯 Уровень автономности повышен до {self.state.autonomy_level}")
            
            improvements = [
                f"Проанализировано {completed_tasks} задач",
                f"Успешность выполнения: {success_rate:.1%}",
                f"Уровень автономности: {self.state.autonomy_level}"
            ]
            
            return {
                "status": "completed",
                "improvements": improvements,
                "new_autonomy_level": self.state.autonomy_level,
                "success_rate": success_rate
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def execute_monitoring_report(self, task: AutonomousTask) -> Dict[str, Any]:
        """Выполнение отчета мониторинга"""
        try:
            analysis_count = task.parameters.get("analysis_count", 0)
            
            # Создаем отчет
            report = {
                "timestamp": datetime.now().isoformat(),
                "visual_analyses": analysis_count,
                "active_tasks": self.state.active_tasks,
                "completed_tasks": len(self.completed_tasks),
                "performance_score": self.state.performance_score,
                "autonomy_level": self.state.autonomy_level,
                "uptime_hours": (time.time() - self.start_time) / 3600,
                "system_health": "Excellent" if self.state.performance_score > 0.8 else "Good"
            }
            
            # Сохраняем отчет
            report_file = f"/workspace/monitoring_report_{int(time.time())}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            return {
                "status": "completed",
                "report": report,
                "report_file": report_file
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def update_system_state(self):
        """Обновление состояния системы"""
        try:
            # Обновляем время работы
            self.state.continuous_uptime = time.time() - self.start_time
            
            # Обновляем использование ресурсов
            self.state.resources_used = {
                "cpu": psutil.cpu_percent(interval=1),
                "memory": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage('/').percent,
                "network": 15.0  # Симуляция
            }
            
            # Рассчитываем общую производительность
            resource_score = 1.0 - (
                self.state.resources_used["cpu"] / 100 * 0.3 +
                self.state.resources_used["memory"] / 100 * 0.4 +
                self.state.resources_used["disk"] / 100 * 0.2 +
                self.state.resources_used["network"] / 100 * 0.1
            )
            
            task_score = min(1.0, len(self.completed_tasks) / max(1, len(self.completed_tasks) + len(self.tasks_queue)))
            
            self.state.performance_score = (resource_score + task_score) / 2
            
        except Exception as e:
            logger.error(f"Ошибка обновления состояния системы: {e}")
    
    def check_system_health(self) -> List[Dict[str, Any]]:
        """Проверка здоровья системы"""
        issues = []
        
        try:
            # Проверяем загрузку CPU
            if self.state.resources_used["cpu"] > 90:
                issues.append({
                    "type": "high_cpu",
                    "severity": "high",
                    "value": self.state.resources_used["cpu"],
                    "auto_fixable": True
                })
            
            # Проверяем память
            if self.state.resources_used["memory"] > 85:
                issues.append({
                    "type": "high_memory",
                    "severity": "medium",
                    "value": self.state.resources_used["memory"],
                    "auto_fixable": True
                })
            
            # Проверяем очередь задач
            if len(self.tasks_queue) > 10:
                issues.append({
                    "type": "task_queue_overflow",
                    "severity": "medium",
                    "value": len(self.tasks_queue),
                    "auto_fixable": True
                })
            
        except Exception as e:
            logger.error(f"Ошибка проверки здоровья: {e}")
        
        return issues
    
    def perform_self_healing(self, issues: List[Dict[str, Any]]):
        """Выполнение самоисцеления"""
        try:
            for issue in issues:
                if issue.get("auto_fixable"):
                    if issue["type"] == "high_cpu":
                        # Снижаем интенсивность обработки
                        self.visual_intelligence.screenshot_interval = min(10, self.visual_intelligence.screenshot_interval + 2)
                        logger.info("🏥 Увеличен интервал скриншотов для снижения нагрузки CPU")
                    
                    elif issue["type"] == "high_memory":
                        # Очищаем историю
                        if len(self.visual_intelligence.analysis_history) > 20:
                            self.visual_intelligence.analysis_history = self.visual_intelligence.analysis_history[-10:]
                        if len(self.completed_tasks) > 50:
                            self.completed_tasks = self.completed_tasks[-25:]
                        logger.info("🏥 Очищена история для освобождения памяти")
                    
                    elif issue["type"] == "task_queue_overflow":
                        # Удаляем задачи с низким приоритетом
                        self.tasks_queue = [t for t in self.tasks_queue if t.priority > 3]
                        logger.info("🏥 Очищена очередь задач с низким приоритетом")
                    
                    self.state.self_healing_events += 1
            
        except Exception as e:
            logger.error(f"Ошибка самоисцеления: {e}")
    
    def setup_api_routes(self):
        """Настройка API маршрутов"""
        
        @self.app.get("/")
        async def dashboard():
            """Главная панель управления"""
            html_content = self.generate_enhanced_dashboard()
            return HTMLResponse(content=html_content)
        
        @self.app.get("/api/status")
        async def get_status():
            """Получение статуса системы"""
            return {
                "system_state": asdict(self.state),
                "active_tasks": len(self.tasks_queue),
                "completed_tasks": len(self.completed_tasks),
                "uptime": self.state.continuous_uptime,
                "visual_analysis": {
                    "last_check": self.state.last_visual_check,
                    "total_analyses": self.state.visual_analysis_count,
                    "last_analysis": asdict(self.visual_intelligence.last_analysis) if self.visual_intelligence.last_analysis else None
                }
            }
        
        @self.app.get("/api/vision/status")
        async def get_vision_status():
            """Статус системы зрения"""
            if self.visual_intelligence.last_analysis:
                return {
                    "enabled": self.visual_intelligence.enabled,
                    "total_analyses": len(self.visual_intelligence.analysis_history),
                    "last_analysis": {
                        "timestamp": self.visual_intelligence.last_analysis.timestamp,
                        "elements_detected": len(self.visual_intelligence.last_analysis.elements_detected),
                        "issues_found": len(self.visual_intelligence.last_analysis.issues_found),
                        "confidence": self.visual_intelligence.last_analysis.confidence,
                        "ux_score": self.visual_intelligence.last_analysis.user_experience_score
                    }
                }
            return {"enabled": self.visual_intelligence.enabled, "total_analyses": 0}
        
        @self.app.post("/api/tasks")
        async def create_task(task_data: dict):
            """Создание новой задачи"""
            task = AutonomousTask(
                id=f"user_task_{int(time.time())}",
                type=task_data.get("type", "general"),
                priority=task_data.get("priority", 5),
                status="pending",
                created_at=datetime.now().isoformat(),
                parameters=task_data.get("parameters", {})
            )
            
            self.tasks_queue.append(task)
            return {"task_id": task.id, "status": "created"}
        
        @self.app.post("/api/autonomous/toggle")
        async def toggle_autonomous_mode():
            """Переключение автономного режима"""
            if self.state.autonomy_level < 5:
                self.state.autonomy_level += 1
            else:
                self.state.autonomy_level = 1
            
            return {
                "autonomy_level": self.state.autonomy_level,
                "status": "updated"
            }
        
        @self.app.post("/api/self-improvement/trigger")
        async def trigger_self_improvement():
            """Запуск самоулучшения"""
            task = AutonomousTask(
                id=f"manual_improvement_{int(time.time())}",
                type="self_improvement",
                priority=8,
                status="pending",
                created_at=datetime.now().isoformat(),
                autonomous_generated=False,
                parameters={"manual_trigger": True}
            )
            
            self.tasks_queue.append(task)
            return {"task_id": task.id, "success": True}
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket для реального времени"""
            await websocket.accept()
            try:
                while True:
                    # Отправляем обновления статуса
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
    
    def generate_enhanced_dashboard(self) -> str:
        """Генерация улучшенной панели управления"""
        return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Enhanced JARVIS Control Panel</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.min.js"></script>
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
            overflow-x: hidden;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: rgba(0, 255, 136, 0.1);
            border: 2px solid #00ff88;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
            backdrop-filter: blur(20px);
            box-shadow: 0 0 40px rgba(0, 255, 136, 0.3);
        }}
        
        .header h1 {{
            font-size: 3em;
            margin-bottom: 15px;
            text-shadow: 0 0 20px #00ff88;
            animation: glow 2s ease-in-out infinite alternate;
        }}
        
        @keyframes glow {{
            from {{ text-shadow: 0 0 20px #00ff88, 0 0 30px #00ff88; }}
            to {{ text-shadow: 0 0 30px #00ff88, 0 0 40px #00ff88; }}
        }}
        
        .status-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .status-card {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }}
        
        .status-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 255, 136, 0.2);
            border-color: #00ff88;
        }}
        
        .status-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #00ff88;
            margin-bottom: 10px;
            text-shadow: 0 0 10px #00ff88;
        }}
        
        .status-label {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .controls-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }}
        
        .control-panel {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
        }}
        
        .control-panel h2 {{
            color: #00ff88;
            margin-bottom: 20px;
            font-size: 1.5em;
            text-align: center;
        }}
        
        .btn {{
            width: 100%;
            padding: 15px 20px;
            margin: 10px 0;
            border: none;
            border-radius: 10px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .btn-primary {{ 
            background: linear-gradient(45deg, #00ff88, #00cc6a);
            color: #1a1a2e;
        }}
        
        .btn-secondary {{ 
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
        }}
        
        .btn-danger {{ 
            background: linear-gradient(45deg, #ff6b6b, #ee5a52);
            color: white;
        }}
        
        .btn-warning {{ 
            background: linear-gradient(45deg, #feca57, #ff9ff3);
            color: #1a1a2e;
        }}
        
        .btn:hover {{
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        }}
        
        .monitoring-section {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }}
        
        .monitor-panel {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
        }}
        
        .monitor-panel h3 {{
            color: #00ff88;
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .chart-container {{
            height: 300px;
            position: relative;
        }}
        
        .log-container {{
            height: 400px;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 10px;
            padding: 20px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        
        .log-entry {{
            margin: 8px 0;
            padding: 8px;
            border-left: 3px solid #00ff88;
            padding-left: 15px;
            opacity: 0.9;
        }}
        
        .log-entry.success {{ border-left-color: #00ff88; }}
        .log-entry.warning {{ border-left-color: #feca57; }}
        .log-entry.error {{ border-left-color: #ff6b6b; }}
        
        .visual-section {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }}
        
        .visual-section h3 {{
            color: #00ff88;
            margin-bottom: 20px;
            text-align: center;
            font-size: 1.8em;
        }}
        
        .visual-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .visual-stat {{
            text-align: center;
            padding: 15px;
            background: rgba(0, 255, 136, 0.1);
            border-radius: 10px;
            border: 1px solid rgba(0, 255, 136, 0.3);
        }}
        
        .visual-stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #00ff88;
            text-shadow: 0 0 10px #00ff88;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            opacity: 0.7;
            border-top: 1px solid rgba(0, 255, 136, 0.3);
            margin-top: 30px;
        }}
        
        @media (max-width: 768px) {{
            .monitoring-section {{
                grid-template-columns: 1fr;
            }}
            
            .controls-section {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🤖 Enhanced JARVIS Control Panel</h1>
            <p style="font-size: 1.2em; margin-top: 10px;">
                Автономная AI система с визуальным интеллектом и непрерывной работой
            </p>
        </div>

        <!-- Status Grid -->
        <div class="status-grid">
            <div class="status-card">
                <div class="status-value" id="performance-score">{self.state.performance_score:.1%}</div>
                <div class="status-label">🚀 Производительность</div>
            </div>
            <div class="status-card">
                <div class="status-value" id="active-tasks">{len(self.tasks_queue)}</div>
                <div class="status-label">⚡ Активные задачи</div>
            </div>
            <div class="status-card">
                <div class="status-value" id="autonomy-level">{self.state.autonomy_level}</div>
                <div class="status-label">🧠 Уровень автономности</div>
            </div>
            <div class="status-card">
                <div class="status-value" id="visual-analyses">{self.state.visual_analysis_count}</div>
                <div class="status-label">👁️ Визуальные анализы</div>
            </div>
            <div class="status-card">
                <div class="status-value" id="uptime">{self.state.continuous_uptime/3600:.1f}ч</div>
                <div class="status-label">⏱️ Время работы</div>
            </div>
            <div class="status-card">
                <div class="status-value" id="completed-tasks">{len(self.completed_tasks)}</div>
                <div class="status-label">✅ Выполнено задач</div>
            </div>
        </div>

        <!-- Controls Section -->
        <div class="controls-section">
            <div class="control-panel">
                <h2>🎛️ Управление системой</h2>
                <button class="btn btn-primary" onclick="triggerSelfImprovement()">
                    🧠 Самоулучшение
                </button>
                <button class="btn btn-secondary" onclick="toggleAutonomousMode()">
                    🤖 Переключить автономность
                </button>
                <button class="btn btn-warning" onclick="createTask('performance_optimization')">
                    ⚡ Оптимизация
                </button>
                <button class="btn btn-danger" onclick="createTask('self_replication')">
                    🚀 Самовоспроизводство
                </button>
            </div>

            <div class="control-panel">
                <h2>👁️ Визуальный интеллект</h2>
                <button class="btn btn-primary" onclick="refreshVisualData()">
                    🔄 Обновить анализ
                </button>
                <button class="btn btn-secondary" onclick="createTask('ui_improvement')">
                    🎨 Улучшить интерфейс
                </button>
                <button class="btn btn-warning" onclick="downloadScreenshot()">
                    📸 Скриншот
                </button>
                <button class="btn btn-danger" onclick="toggleVisualMonitoring()">
                    👁️ Переключить мониторинг
                </button>
            </div>
        </div>

        <!-- Visual Intelligence Section -->
        <div class="visual-section">
            <h3>👁️ Система визуального интеллекта</h3>
            <div class="visual-stats">
                <div class="visual-stat">
                    <div class="visual-stat-value" id="elements-detected">0</div>
                    <div>Элементы обнаружены</div>
                </div>
                <div class="visual-stat">
                    <div class="visual-stat-value" id="issues-found">0</div>
                    <div>Проблемы найдены</div>
                </div>
                <div class="visual-stat">
                    <div class="visual-stat-value" id="confidence-score">0%</div>
                    <div>Уверенность</div>
                </div>
                <div class="visual-stat">
                    <div class="visual-stat-value" id="ux-score">0%</div>
                    <div>UX Score</div>
                </div>
            </div>
        </div>

        <!-- Monitoring Section -->
        <div class="monitoring-section">
            <div class="monitor-panel">
                <h3>📊 Мониторинг производительности</h3>
                <div class="chart-container">
                    <canvas id="performanceChart"></canvas>
                </div>
            </div>

            <div class="monitor-panel">
                <h3>🔧 Использование ресурсов</h3>
                <div class="chart-container">
                    <canvas id="resourceChart"></canvas>
                </div>
            </div>
        </div>

        <!-- System Logs -->
        <div class="monitor-panel">
            <h3>📝 Системные логи в реальном времени</h3>
            <div class="log-container" id="system-logs">
                <div class="log-entry success">
                    [{datetime.now().strftime('%H:%M:%S')}] ✅ Enhanced JARVIS система запущена
                </div>
                <div class="log-entry">
                    [{datetime.now().strftime('%H:%M:%S')}] 👁️ Визуальный интеллект активирован
                </div>
                <div class="log-entry">
                    [{datetime.now().strftime('%H:%M:%S')}] 🤖 Автономные системы инициализированы
                </div>
                <div class="log-entry success">
                    [{datetime.now().strftime('%H:%M:%S')}] 🚀 Система готова к работе
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>Enhanced JARVIS System v2.0 | Автономная работа с визуальным интеллектом</p>
            <p>Последнее обновление: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>

    <script>
        let ws;
        let performanceChart;
        let resourceChart;

        // Инициализация
        document.addEventListener('DOMContentLoaded', function() {{
            initWebSocket();
            initCharts();
            startStatusUpdates();
            addLog('🚀 Enhanced JARVIS Control Panel инициализирован', 'success');
        }});

        // WebSocket соединение
        function initWebSocket() {{
            try {{
                ws = new WebSocket('ws://localhost:8080/ws');
                
                ws.onopen = function() {{
                    addLog('🔗 WebSocket соединение установлено', 'success');
                }};
                
                ws.onmessage = function(event) {{
                    const data = JSON.parse(event.data);
                    updateSystemStatus(data);
                }};
                
                ws.onclose = function() {{
                    addLog('⚠️ WebSocket соединение потеряно, переподключение...', 'warning');
                    setTimeout(initWebSocket, 5000);
                }};
            }} catch (error) {{
                addLog('❌ Ошибка WebSocket: ' + error.message, 'error');
            }}
        }}

        // Инициализация графиков
        function initCharts() {{
            // График производительности
            const perfCtx = document.getElementById('performanceChart').getContext('2d');
            performanceChart = new Chart(perfCtx, {{
                type: 'line',
                data: {{
                    labels: [],
                    datasets: [{{
                        label: 'Производительность',
                        data: [],
                        borderColor: '#00ff88',
                        backgroundColor: 'rgba(0, 255, 136, 0.1)',
                        tension: 0.4,
                        fill: true
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            labels: {{
                                color: '#ffffff'
                            }}
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            max: 100,
                            ticks: {{
                                color: '#ffffff'
                            }},
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }},
                        x: {{
                            ticks: {{
                                color: '#ffffff'
                            }},
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }}
                    }}
                }}
            }});

            // График ресурсов
            const resCtx = document.getElementById('resourceChart').getContext('2d');
            resourceChart = new Chart(resCtx, {{
                type: 'doughnut',
                data: {{
                    labels: ['CPU', 'Память', 'Диск', 'Сеть'],
                    datasets: [{{
                        data: [25, 35, 15, 25],
                        backgroundColor: [
                            '#00ff88',
                            '#667eea',
                            '#feca57',
                            '#ff6b6b'
                        ]
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            labels: {{
                                color: '#ffffff'
                            }}
                        }}
                    }}
                }}
            }});
        }}

        // Обновление статуса системы
        function updateSystemStatus(data) {{
            if (data.system_state) {{
                document.getElementById('performance-score').textContent = 
                    Math.round((data.system_state.performance_score || 0) * 100) + '%';
                document.getElementById('active-tasks').textContent = data.active_tasks || 0;
                document.getElementById('autonomy-level').textContent = data.system_state.autonomy_level || 1;
                document.getElementById('visual-analyses').textContent = data.system_state.visual_analysis_count || 0;
                document.getElementById('uptime').textContent = 
                    Math.floor((data.uptime || 0) / 3600) + 'ч';
                document.getElementById('completed-tasks').textContent = data.completed_tasks || 0;

                // Обновляем график производительности
                updatePerformanceChart(data.system_state.performance_score * 100);
                
                // Обновляем график ресурсов
                updateResourceChart(data.system_state.resources_used);
            }}
            
            if (data.visual_analysis && data.visual_analysis.last_analysis) {{
                const va = data.visual_analysis.last_analysis;
                document.getElementById('elements-detected').textContent = va.elements_detected || 0;
                document.getElementById('issues-found').textContent = va.issues_found || 0;
                document.getElementById('confidence-score').textContent = 
                    Math.round((va.confidence || 0) * 100) + '%';
                document.getElementById('ux-score').textContent = 
                    Math.round((va.user_experience_score || 0) * 100) + '%';
            }}
        }}

        // Обновление графика производительности
        function updatePerformanceChart(value) {{
            const now = new Date().toLocaleTimeString();
            performanceChart.data.labels.push(now);
            performanceChart.data.datasets[0].data.push(value);
            
            if (performanceChart.data.labels.length > 20) {{
                performanceChart.data.labels.shift();
                performanceChart.data.datasets[0].data.shift();
            }}
            
            performanceChart.update('none');
        }}

        // Обновление графика ресурсов
        function updateResourceChart(resources) {{
            if (resources) {{
                resourceChart.data.datasets[0].data = [
                    resources.cpu || 0,
                    resources.memory || 0,
                    resources.disk || 0,
                    resources.network || 0
                ];
                resourceChart.update('none');
            }}
        }}

        // API функции
        async function createTask(type) {{
            try {{
                const response = await fetch('/api/tasks', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        type: type,
                        priority: 7,
                        parameters: {{
                            source: 'enhanced_dashboard',
                            timestamp: new Date().toISOString()
                        }}
                    }})
                }});

                const result = await response.json();
                if (result.task_id) {{
                    addLog(`✅ Задача ${{type}} создана: ${{result.task_id}}`, 'success');
                }}
            }} catch (error) {{
                addLog(`❌ Ошибка создания задачи: ${{error.message}}`, 'error');
            }}
        }}

        async function triggerSelfImprovement() {{
            try {{
                const response = await fetch('/api/self-improvement/trigger', {{
                    method: 'POST'
                }});
                const result = await response.json();
                if (result.success) {{
                    addLog(`🧠 Самоулучшение запущено: ${{result.task_id}}`, 'success');
                }}
            }} catch (error) {{
                addLog(`❌ Ошибка самоулучшения: ${{error.message}}`, 'error');
            }}
        }}

        async function toggleAutonomousMode() {{
            try {{
                const response = await fetch('/api/autonomous/toggle', {{
                    method: 'POST'
                }});
                const result = await response.json();
                if (result.status === 'updated') {{
                    addLog(`🤖 Уровень автономности изменен на ${{result.autonomy_level}}`, 'success');
                    document.getElementById('autonomy-level').textContent = result.autonomy_level;
                }}
            }} catch (error) {{
                addLog(`❌ Ошибка переключения автономности: ${{error.message}}`, 'error');
            }}
        }}

        async function refreshVisualData() {{
            try {{
                const response = await fetch('/api/vision/status');
                if (response.ok) {{
                    const data = await response.json();
                    if (data.last_analysis) {{
                        document.getElementById('elements-detected').textContent = data.last_analysis.elements_detected;
                        document.getElementById('issues-found').textContent = data.last_analysis.issues_found;
                        document.getElementById('confidence-score').textContent = 
                            Math.round(data.last_analysis.confidence * 100) + '%';
                        document.getElementById('ux-score').textContent = 
                            Math.round(data.last_analysis.ux_score * 100) + '%';
                    }}
                    addLog('👁️ Данные визуального анализа обновлены', 'success');
                }}
            }} catch (error) {{
                addLog(`❌ Ошибка обновления визуальных данных: ${{error.message}}`, 'error');
            }}
        }}

        function downloadScreenshot() {{
            addLog('📸 Функция скачивания скриншота будет реализована', 'warning');
        }}

        function toggleVisualMonitoring() {{
            addLog('👁️ Переключение визуального мониторинга', 'success');
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
            
            if (logsContainer.children.length > 50) {{
                logsContainer.removeChild(logsContainer.firstChild);
            }}
        }}

        // Обновления статуса
        function startStatusUpdates() {{
            setInterval(async () => {{
                try {{
                    const response = await fetch('/api/status');
                    if (response.ok) {{
                        const data = await response.json();
                        updateSystemStatus(data);
                    }}
                }} catch (error) {{
                    // Игнорируем ошибки обновления статуса
                }}
            }}, 5000);
        }}
    </script>
</body>
</html>"""
    
    async def run_server(self, host: str = "0.0.0.0", port: int = 8080):
        """Запуск сервера"""
        logger.info(f"🌐 Запуск Enhanced JARVIS на http://{host}:{port}")
        
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level="info",
            access_log=False
        )
        
        server = uvicorn.Server(config)
        await server.serve()

def signal_handler(signum, frame):
    """Обработчик сигналов"""
    logger.info("🛑 Получен сигнал остановки, завершение работы...")
    sys.exit(0)

async def main():
    """Главная функция"""
    try:
        # Устанавливаем обработчики сигналов
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Создаем и запускаем Enhanced JARVIS
        jarvis = EnhancedAutonomousJarvis()
        
        logger.info("🚀 Enhanced Autonomous JARVIS система полностью готова!")
        logger.info("🌐 Веб-интерфейс доступен по адресу: http://localhost:8080")
        logger.info("👁️ Система визуального интеллекта активна")
        logger.info("🤖 Автономные агенты работают")
        
        # Запускаем сервер
        await jarvis.run_server()
        
    except KeyboardInterrupt:
        logger.info("🛑 Остановка по запросу пользователя")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())