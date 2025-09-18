#!/usr/bin/env python3
"""
Vision Agent - Агент с визуальными возможностями
Может анализировать веб-интерфейс, делать скриншоты и предлагать улучшения
"""

import asyncio
import logging
import base64
import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import io
from PIL import Image

logger = logging.getLogger(__name__)

class VisionAgent:
    """Агент с визуальными возможностями для анализа веб-интерфейса"""
    
    def __init__(self, agent_id: str = "vision_agent"):
        self.agent_id = agent_id
        self.name = "Vision Agent"
        self.capabilities = [
            "screenshot_analysis",
            "ui_improvement_suggestions", 
            "visual_bug_detection",
            "responsive_design_check",
            "accessibility_analysis"
        ]
        self.driver = None
        self.base_url = "http://localhost:8080"
        
    async def initialize(self):
        """Инициализация веб-драйвера"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("✅ Vision Agent инициализирован")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации Vision Agent: {e}")
            return False
    
    async def take_screenshot(self, url: str = None) -> Optional[str]:
        """Сделать скриншот веб-страницы"""
        try:
            if not self.driver:
                await self.initialize()
            
            target_url = url or self.base_url
            self.driver.get(target_url)
            
            # Ждем загрузки страницы
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Делаем скриншот
            screenshot = self.driver.get_screenshot_as_png()
            
            # Конвертируем в base64
            screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
            
            logger.info(f"📸 Скриншот сделан для {target_url}")
            return screenshot_b64
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания скриншота: {e}")
            return None
    
    async def analyze_ui(self, screenshot_b64: str = None) -> Dict[str, Any]:
        """Анализ пользовательского интерфейса"""
        try:
            if not screenshot_b64:
                screenshot_b64 = await self.take_screenshot()
            
            if not screenshot_b64:
                return {"error": "Не удалось получить скриншот"}
            
            # Анализ через AI (можно использовать Ollama с vision моделью)
            analysis = await self._analyze_with_ai(screenshot_b64)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "analysis": analysis,
                "suggestions": await self._generate_improvements(analysis),
                "issues": await self._detect_issues(analysis)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка анализа UI: {e}")
            return {"error": str(e)}
    
    async def _analyze_with_ai(self, screenshot_b64: str) -> Dict[str, Any]:
        """Анализ скриншота через AI"""
        try:
            # Используем Ollama для анализа изображения
            analysis_prompt = """
            Проанализируй этот скриншот веб-интерфейса системы множественных AI-агентов.
            Оцени:
            1. Общий дизайн и удобство использования
            2. Читаемость текста и контрастность
            3. Расположение элементов интерфейса
            4. Навигацию и доступность функций
            5. Современность дизайна
            
            Дай оценку по 10-балльной шкале и конкретные рекомендации.
            """
            
            # Здесь можно интегрировать с vision моделью Ollama
            # Пока возвращаем базовый анализ
            return {
                "design_score": 7,
                "usability_score": 8,
                "readability_score": 9,
                "navigation_score": 7,
                "modernity_score": 6,
                "overall_score": 7.4,
                "summary": "Интерфейс функционален, но требует улучшения дизайна"
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка AI анализа: {e}")
            return {"error": str(e)}
    
    async def _generate_improvements(self, analysis: Dict[str, Any]) -> List[str]:
        """Генерация предложений по улучшению"""
        suggestions = []
        
        if analysis.get("design_score", 0) < 8:
            suggestions.append("Улучшить цветовую схему и типографику")
            suggestions.append("Добавить современные UI компоненты")
        
        if analysis.get("navigation_score", 0) < 8:
            suggestions.append("Упростить навигацию между агентами")
            suggestions.append("Добавить хлебные крошки")
        
        if analysis.get("modernity_score", 0) < 8:
            suggestions.append("Добавить анимации и переходы")
            suggestions.append("Использовать современные CSS фреймворки")
        
        return suggestions
    
    async def _detect_issues(self, analysis: Dict[str, Any]) -> List[str]:
        """Обнаружение проблем в интерфейсе"""
        issues = []
        
        if analysis.get("readability_score", 0) < 7:
            issues.append("Плохая читаемость текста")
        
        if analysis.get("usability_score", 0) < 7:
            issues.append("Сложность использования")
        
        return issues
    
    async def check_responsive_design(self) -> Dict[str, Any]:
        """Проверка адаптивности дизайна"""
        try:
            results = {}
            screen_sizes = [
                (1920, 1080, "Desktop"),
                (1366, 768, "Laptop"),
                (768, 1024, "Tablet"),
                (375, 667, "Mobile")
            ]
            
            for width, height, device in screen_sizes:
                if self.driver:
                    self.driver.set_window_size(width, height)
                    await asyncio.sleep(1)
                    
                    screenshot = await self.take_screenshot()
                    if screenshot:
                        results[device] = {
                            "size": f"{width}x{height}",
                            "screenshot": screenshot,
                            "responsive": True  # Можно добавить более детальную проверку
                        }
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки адаптивности: {e}")
            return {"error": str(e)}
    
    async def monitor_system_health(self) -> Dict[str, Any]:
        """Мониторинг состояния системы"""
        try:
            health_data = {
                "timestamp": datetime.now().isoformat(),
                "web_interface": await self._check_web_interface(),
                "api_endpoints": await self._check_api_endpoints(),
                "agents_status": await self._check_agents_status()
            }
            
            return health_data
            
        except Exception as e:
            logger.error(f"❌ Ошибка мониторинга: {e}")
            return {"error": str(e)}
    
    async def _check_web_interface(self) -> Dict[str, Any]:
        """Проверка веб-интерфейса"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return {
                "status": "online" if response.status_code == 200 else "offline",
                "response_time": response.elapsed.total_seconds(),
                "status_code": response.status_code
            }
        except Exception as e:
            return {"status": "offline", "error": str(e)}
    
    async def _check_api_endpoints(self) -> Dict[str, Any]:
        """Проверка API endpoints"""
        endpoints = [
            "/api/agents",
            "/api/system/status",
            "/api/chat/send"
        ]
        
        results = {}
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                results[endpoint] = {
                    "status": "online" if response.status_code == 200 else "offline",
                    "status_code": response.status_code
                }
            except Exception as e:
                results[endpoint] = {"status": "offline", "error": str(e)}
        
        return results
    
    async def _check_agents_status(self) -> Dict[str, Any]:
        """Проверка статуса агентов"""
        try:
            response = requests.get(f"{self.base_url}/api/agents", timeout=5)
            if response.status_code == 200:
                agents_data = response.json()
                return {
                    "total_agents": len(agents_data.get("agents", [])),
                    "agents_online": len([a for a in agents_data.get("agents", []) if a.get("status") == "online"]),
                    "status": "healthy"
                }
            else:
                return {"status": "unhealthy", "error": "API недоступен"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def suggest_improvements(self) -> Dict[str, Any]:
        """Предложения по улучшению системы"""
        try:
            # Анализируем текущее состояние
            screenshot = await self.take_screenshot()
            ui_analysis = await self.analyze_ui(screenshot)
            health_check = await self.monitor_system_health()
            
            improvements = {
                "timestamp": datetime.now().isoformat(),
                "ui_improvements": ui_analysis.get("suggestions", []),
                "ui_issues": ui_analysis.get("issues", []),
                "system_improvements": await self._generate_system_improvements(health_check),
                "priority": await self._prioritize_improvements(ui_analysis, health_check)
            }
            
            return improvements
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации предложений: {e}")
            return {"error": str(e)}
    
    async def _generate_system_improvements(self, health_data: Dict[str, Any]) -> List[str]:
        """Генерация предложений по улучшению системы"""
        improvements = []
        
        if health_data.get("web_interface", {}).get("status") != "online":
            improvements.append("Восстановить веб-интерфейс")
        
        api_status = health_data.get("api_endpoints", {})
        offline_endpoints = [ep for ep, status in api_status.items() if status.get("status") != "online"]
        
        if offline_endpoints:
            improvements.append(f"Восстановить API endpoints: {', '.join(offline_endpoints)}")
        
        agents_status = health_data.get("agents_status", {})
        if agents_status.get("status") != "healthy":
            improvements.append("Проверить состояние агентов")
        
        return improvements
    
    async def _prioritize_improvements(self, ui_analysis: Dict[str, Any], health_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Приоритизация улучшений"""
        priorities = []
        
        # Критические проблемы системы
        if health_data.get("web_interface", {}).get("status") != "online":
            priorities.append({
                "priority": "critical",
                "improvement": "Восстановить веб-интерфейс",
                "reason": "Система недоступна"
            })
        
        # Проблемы UI
        ui_score = ui_analysis.get("overall_score", 0)
        if ui_score < 6:
            priorities.append({
                "priority": "high",
                "improvement": "Улучшить дизайн интерфейса",
                "reason": f"Низкий рейтинг UI: {ui_score}/10"
            })
        
        return priorities
    
    async def cleanup(self):
        """Очистка ресурсов"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("✅ Vision Agent очищен")
        except Exception as e:
            logger.error(f"❌ Ошибка очистки Vision Agent: {e}")

# Глобальный экземпляр
vision_agent = VisionAgent()

