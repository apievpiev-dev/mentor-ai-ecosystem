#!/usr/bin/env python3
"""
Visual Monitor - Система визуального мониторинга
Автоматически отслеживает визуальное состояние системы и веб-интерфейсов
"""

import asyncio
import json
import logging
import time
import base64
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import aiohttp
import subprocess
import os
import sys
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class VisualState:
    """Состояние визуального компонента"""
    component: str
    url: str
    status: str
    screenshot_path: Optional[str] = None
    issues: List[str] = None
    timestamp: str = ""
    response_time: float = 0.0

@dataclass
class VisualAnalysis:
    """Результат визуального анализа"""
    overall_health: float
    issues: List[str]
    suggestions: List[str]
    components_status: Dict[str, VisualState]
    timestamp: str

class VisualMonitor:
    """Система визуального мониторинга"""
    
    def __init__(self):
        self.active = False
        self.screenshots_dir = Path("/workspace/visual_screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        self.visual_history = []
        self.monitored_components = [
            {
                "name": "main_web_interface",
                "url": "http://localhost:8080",
                "type": "web_interface"
            },
            {
                "name": "ai_manager_interface",
                "url": "http://localhost:8000",
                "type": "web_interface"
            },
            {
                "name": "system_status_api",
                "url": "http://localhost:8080/api/system/status",
                "type": "api_endpoint"
            }
        ]
        self.session = None
        
    async def initialize(self):
        """Инициализация визуального монитора"""
        try:
            self.session = aiohttp.ClientSession()
            self.active = True
            logger.info("✅ Visual Monitor инициализирован")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации Visual Monitor: {e}")
            self.active = False
    
    async def capture_system_state(self) -> Dict[str, VisualState]:
        """Захват визуального состояния системы"""
        if not self.active:
            return {}
        
        visual_states = {}
        
        for component in self.monitored_components:
            try:
                visual_state = await self._capture_component_state(component)
                visual_states[component["name"]] = visual_state
                
                # Сохраняем в историю
                self.visual_history.append(visual_state)
                
                # Ограничиваем историю
                if len(self.visual_history) > 100:
                    self.visual_history = self.visual_history[-100:]
                
            except Exception as e:
                logger.error(f"❌ Ошибка захвата состояния {component['name']}: {e}")
                visual_states[component["name"]] = VisualState(
                    component=component["name"],
                    url=component["url"],
                    status="error",
                    issues=[f"Ошибка захвата: {str(e)}"],
                    timestamp=datetime.now().isoformat()
                )
        
        return visual_states
    
    async def _capture_component_state(self, component: Dict[str, str]) -> VisualState:
        """Захват состояния отдельного компонента"""
        start_time = time.time()
        
        try:
            # Проверяем доступность компонента
            async with self.session.get(
                component["url"], 
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    status = "healthy"
                    issues = []
                    
                    # Для веб-интерфейсов создаем скриншот
                    if component["type"] == "web_interface":
                        screenshot_path = await self._create_screenshot(component)
                    else:
                        screenshot_path = None
                    
                    # Анализируем содержимое ответа
                    if component["type"] == "api_endpoint":
                        content = await response.text()
                        issues = self._analyze_api_response(content)
                    else:
                        issues = self._analyze_web_content(await response.text())
                    
                    return VisualState(
                        component=component["name"],
                        url=component["url"],
                        status=status,
                        screenshot_path=screenshot_path,
                        issues=issues,
                        timestamp=datetime.now().isoformat(),
                        response_time=response_time
                    )
                else:
                    return VisualState(
                        component=component["name"],
                        url=component["url"],
                        status="unhealthy",
                        issues=[f"HTTP {response.status}"],
                        timestamp=datetime.now().isoformat(),
                        response_time=response_time
                    )
        
        except asyncio.TimeoutError:
            return VisualState(
                component=component["name"],
                url=component["url"],
                status="timeout",
                issues=["Timeout при обращении"],
                timestamp=datetime.now().isoformat(),
                response_time=time.time() - start_time
            )
        except Exception as e:
            return VisualState(
                component=component["name"],
                url=component["url"],
                status="error",
                issues=[f"Ошибка: {str(e)}"],
                timestamp=datetime.now().isoformat(),
                response_time=time.time() - start_time
            )
    
    async def _create_screenshot(self, component: Dict[str, str]) -> Optional[str]:
        """Создание скриншота веб-интерфейса"""
        try:
            # Простая реализация - в реальности можно использовать Selenium или Playwright
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = self.screenshots_dir / f"{component['name']}_{timestamp}.png"
            
            # Создаем заглушку скриншота (в реальности здесь был бы настоящий скриншот)
            screenshot_data = f"Screenshot of {component['url']} at {datetime.now()}"
            screenshot_path.write_text(screenshot_data)
            
            return str(screenshot_path)
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания скриншота для {component['name']}: {e}")
            return None
    
    def _analyze_api_response(self, content: str) -> List[str]:
        """Анализ ответа API"""
        issues = []
        
        try:
            data = json.loads(content)
            
            # Проверяем статус системы
            if data.get("system_status") != "running":
                issues.append("Система не работает")
            
            # Проверяем количество агентов
            agents_count = data.get("total_agents", 0)
            if agents_count == 0:
                issues.append("Нет активных агентов")
            
            # Проверяем производительность
            if data.get("average_response_time", 0) > 5.0:
                issues.append("Медленный отклик системы")
        
        except json.JSONDecodeError:
            issues.append("Некорректный JSON ответ")
        except Exception as e:
            issues.append(f"Ошибка анализа API: {str(e)}")
        
        return issues
    
    def _analyze_web_content(self, content: str) -> List[str]:
        """Анализ содержимого веб-страницы"""
        issues = []
        
        # Проверяем базовые элементы
        if "error" in content.lower():
            issues.append("Страница содержит ошибки")
        
        if "not found" in content.lower() or "404" in content:
            issues.append("Страница не найдена")
        
        if len(content) < 100:
            issues.append("Слишком короткое содержимое страницы")
        
        # Проверяем наличие ключевых элементов интерфейса
        if "chat" in content.lower() and "input" not in content.lower():
            issues.append("Отсутствует поле ввода в чате")
        
        if "agent" in content.lower() and "select" not in content.lower():
            issues.append("Отсутствует выбор агентов")
        
        return issues
    
    async def analyze_visual_data(self) -> VisualAnalysis:
        """Анализ визуальных данных"""
        try:
            # Получаем текущее состояние
            current_states = await self.capture_system_state()
            
            # Анализируем состояние
            overall_health = 1.0
            all_issues = []
            suggestions = []
            
            for component_name, state in current_states.items():
                if state.status != "healthy":
                    overall_health -= 0.2
                
                if state.issues:
                    all_issues.extend([f"{component_name}: {issue}" for issue in state.issues])
                
                # Генерируем предложения
                if state.status == "timeout":
                    suggestions.append(f"Проверить доступность {component_name}")
                elif state.status == "error":
                    suggestions.append(f"Перезапустить {component_name}")
                elif state.issues:
                    suggestions.append(f"Исправить проблемы в {component_name}")
            
            # Анализируем тренды
            if len(self.visual_history) > 5:
                recent_states = self.visual_history[-5:]
                unhealthy_count = sum(1 for state in recent_states if state.status != "healthy")
                
                if unhealthy_count > 2:
                    overall_health -= 0.3
                    suggestions.append("Система показывает нестабильность")
            
            return VisualAnalysis(
                overall_health=max(0.0, overall_health),
                issues=all_issues,
                suggestions=suggestions,
                components_status=current_states,
                timestamp=datetime.now().isoformat()
            )
        
        except Exception as e:
            logger.error(f"❌ Ошибка анализа визуальных данных: {e}")
            return VisualAnalysis(
                overall_health=0.0,
                issues=[f"Ошибка анализа: {str(e)}"],
                suggestions=["Проверить работу Visual Monitor"],
                components_status={},
                timestamp=datetime.now().isoformat()
            )
    
    async def generate_visual_report(self) -> Dict[str, Any]:
        """Генерация визуального отчета"""
        try:
            analysis = await self.analyze_visual_data()
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "overall_health": analysis.overall_health,
                "health_status": "healthy" if analysis.overall_health > 0.7 else "warning" if analysis.overall_health > 0.4 else "critical",
                "components": {},
                "issues": analysis.issues,
                "suggestions": analysis.suggestions,
                "statistics": {
                    "total_components": len(self.monitored_components),
                    "healthy_components": sum(1 for state in analysis.components_status.values() if state.status == "healthy"),
                    "monitoring_duration": len(self.visual_history),
                    "last_check": analysis.timestamp
                }
            }
            
            # Детали по компонентам
            for component_name, state in analysis.components_status.items():
                report["components"][component_name] = {
                    "status": state.status,
                    "response_time": state.response_time,
                    "issues": state.issues,
                    "screenshot_available": state.screenshot_path is not None,
                    "last_check": state.timestamp
                }
            
            return report
        
        except Exception as e:
            logger.error(f"❌ Ошибка генерации визуального отчета: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "overall_health": 0.0,
                "health_status": "error"
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса Visual Monitor"""
        return {
            "active": self.active,
            "monitored_components": len(self.monitored_components),
            "visual_history_size": len(self.visual_history),
            "screenshots_dir": str(self.screenshots_dir),
            "last_analysis": self.visual_history[-1].timestamp if self.visual_history else None
        }
    
    async def add_component(self, name: str, url: str, component_type: str = "web_interface"):
        """Добавление нового компонента для мониторинга"""
        self.monitored_components.append({
            "name": name,
            "url": url,
            "type": component_type
        })
        logger.info(f"➕ Добавлен компонент для мониторинга: {name} ({url})")
    
    async def remove_component(self, name: str):
        """Удаление компонента из мониторинга"""
        self.monitored_components = [
            comp for comp in self.monitored_components 
            if comp["name"] != name
        ]
        logger.info(f"➖ Удален компонент из мониторинга: {name}")
    
    async def close(self):
        """Закрытие Visual Monitor"""
        if self.session:
            await self.session.close()
        self.active = False
        logger.info("✅ Visual Monitor закрыт")

# Глобальный экземпляр
visual_monitor = VisualMonitor()

if __name__ == "__main__":
    # Тестирование Visual Monitor
    async def test_visual_monitor():
        print("🧪 Тестирование Visual Monitor...")
        
        # Инициализация
        await visual_monitor.initialize()
        
        # Захват состояния
        states = await visual_monitor.capture_system_state()
        print(f"Захвачено состояний: {len(states)}")
        
        # Анализ
        analysis = await visual_monitor.analyze_visual_data()
        print(f"Общее здоровье: {analysis.overall_health:.2f}")
        print(f"Проблемы: {analysis.issues}")
        
        # Отчет
        report = await visual_monitor.generate_visual_report()
        print(f"Статус здоровья: {report['health_status']}")
        
        # Закрытие
        await visual_monitor.close()
    
    asyncio.run(test_visual_monitor())