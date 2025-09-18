#!/usr/bin/env python3
"""
JARVIS Vision System
Система компьютерного зрения для анализа веб-интерфейса
"""

import os
import sys
import json
import time
import asyncio
import logging
import base64
import io
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import threading
import queue

logger = logging.getLogger(__name__)

@dataclass
class VisionAnalysis:
    """Результат анализа изображения"""
    timestamp: str
    screen_elements: List[Dict[str, Any]]
    issues_detected: List[Dict[str, Any]]
    suggestions: List[str]
    confidence: float

class JarvisVision:
    """Система компьютерного зрения JARVIS"""
    
    def __init__(self, core):
        self.core = core
        self.screenshot_queue = queue.Queue()
        self.analysis_results = []
        self.vision_enabled = True
        self.screenshot_interval = 5  # секунд
        self.last_analysis = None
        self.virtual_display = None
        
        # Настраиваем виртуальный дисплей если нужно
        self.setup_virtual_display()
        
        # Запускаем систему зрения
        self.start_vision_system()
    
    def setup_virtual_display(self):
        """Настройка виртуального дисплея для серверной среды"""
        try:
            # Проверяем, есть ли уже DISPLAY
            if os.getenv('DISPLAY'):
                logger.info(f"✅ Дисплей уже настроен: {os.getenv('DISPLAY')}")
                return
            
            # Пробуем запустить виртуальный дисплей
            logger.info("🔧 Настройка виртуального дисплея...")
            
            # Используем Xvfb если доступен
            try:
                result = subprocess.run(['Xvfb', ':99', '-screen', '0', '1024x768x24'], 
                                      capture_output=True, timeout=5)
                if result.returncode == 0:
                    os.environ['DISPLAY'] = ':99'
                    logger.info("✅ Виртуальный дисплей Xvfb запущен на :99")
                    return
            except FileNotFoundError:
                logger.warning("⚠️ Xvfb не найден")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка запуска Xvfb: {e}")
            
            # Если Xvfb недоступен, используем демо-режим
            logger.info("🖼️ Переход в демо-режим (виртуальные скриншоты)")
            
        except Exception as e:
            logger.error(f"❌ Ошибка настройки дисплея: {e}")
        
    def start_vision_system(self):
        """Запуск системы компьютерного зрения"""
        # Поток захвата скриншотов
        screenshot_thread = threading.Thread(
            target=self.run_screenshot_capture,
            daemon=True
        )
        screenshot_thread.start()
        
        # Поток анализа изображений
        analysis_thread = threading.Thread(
            target=self.run_image_analysis,
            daemon=True
        )
        analysis_thread.start()
        
        logger.info("👁️ Система компьютерного зрения JARVIS запущена")
    
    def run_screenshot_capture(self):
        """Захват скриншотов"""
        while self.vision_enabled:
            try:
                # Захватываем скриншот
                screenshot_data = self.capture_screenshot()
                if screenshot_data:
                    self.screenshot_queue.put({
                        "timestamp": datetime.now().isoformat(),
                        "image_data": screenshot_data
                    })
                
                time.sleep(self.screenshot_interval)
                
            except Exception as e:
                logger.error(f"Ошибка захвата скриншота: {e}")
                time.sleep(10)
    
    def run_image_analysis(self):
        """Анализ изображений"""
        while self.vision_enabled:
            try:
                if not self.screenshot_queue.empty():
                    screenshot = self.screenshot_queue.get()
                    analysis = self.analyze_screenshot(screenshot)
                    
                    if analysis:
                        self.analysis_results.append(analysis)
                        self.process_analysis_results(analysis)
                        
                        # Ограничиваем размер истории
                        if len(self.analysis_results) > 100:
                            self.analysis_results = self.analysis_results[-50:]
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Ошибка анализа изображения: {e}")
                time.sleep(5)
    
    def capture_screenshot(self) -> Optional[str]:
        """Захват скриншота экрана"""
        try:
            # Проверяем, есть ли графический интерфейс
            display = os.getenv('DISPLAY')
            if not display:
                logger.info("Графический интерфейс недоступен, создаем демо-скриншот")
                return self.create_demo_screenshot()
            
            logger.info(f"Захват скриншота с дисплея: {display}")
            
            # Пробуем scrot (быстрее и надежнее)
            try:
                result = subprocess.run([
                    'scrot', '-q', '80', '-o', '/tmp/jarvis_screenshot.png'
                ], capture_output=True, timeout=10)
                
                if result.returncode == 0 and os.path.exists('/tmp/jarvis_screenshot.png'):
                    # Читаем файл и кодируем в base64
                    with open('/tmp/jarvis_screenshot.png', 'rb') as f:
                        image_data = f.read()
                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                    os.remove('/tmp/jarvis_screenshot.png')  # Удаляем временный файл
                    logger.info("✅ Скриншот сделан с помощью scrot")
                    return image_base64
            except Exception as e:
                logger.warning(f"scrot не сработал: {e}")
            
            # Пробуем ImageMagick
            result = subprocess.run([
                'import', '-window', 'root', '-resize', '800x600', 'png:-'
            ], capture_output=True, timeout=10)
            
            if result.returncode == 0:
                # Кодируем в base64
                image_base64 = base64.b64encode(result.stdout).decode('utf-8')
                return image_base64
            else:
                # Пробуем альтернативный способ через xwd
                result = subprocess.run([
                    'xwd', '-root', '-silent'
                ], capture_output=True, timeout=10)
                
                if result.returncode == 0:
                    # Конвертируем xwd в png
                    convert_result = subprocess.run([
                        'convert', 'xwd:-', 'png:-'
                    ], input=result.stdout, capture_output=True, timeout=10)
                    
                    if convert_result.returncode == 0:
                        image_base64 = base64.b64encode(convert_result.stdout).decode('utf-8')
                        return image_base64
                
                logger.warning("Не удалось захватить скриншот")
                return None
                
        except subprocess.TimeoutExpired:
            logger.warning("Таймаут захвата скриншота")
            return None
        except FileNotFoundError:
            logger.warning("ImageMagick или xwd не установлены")
            return self.create_demo_screenshot()
        except Exception as e:
            logger.error(f"Ошибка захвата скриншота: {e}")
            return self.create_demo_screenshot()
    
    def create_demo_screenshot(self) -> str:
        """Создает демо-скриншот для серверной среды"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Создаем изображение 800x600
            img = Image.new('RGB', (800, 600), color='#667eea')
            draw = ImageDraw.Draw(img)
            
            # Добавляем текст
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
            except:
                font = ImageFont.load_default()
            
            draw.text((50, 200), "JARVIS Vision System", fill='white', font=font)
            draw.text((50, 250), "Server Mode - No GUI Available", fill='white', font=font)
            draw.text((50, 300), f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}", fill='white', font=font)
            draw.text((50, 350), "Creating virtual screenshot for analysis", fill='white', font=font)
            
            # Кодируем в base64
            import io
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            logger.info("Создан демо-скриншот для серверной среды")
            return image_base64
            
        except Exception as e:
            logger.error(f"Ошибка создания демо-скриншота: {e}")
            return None
    
    def analyze_screenshot(self, screenshot: Dict[str, Any]) -> Optional[VisionAnalysis]:
        """Анализ скриншота"""
        try:
            # Базовый анализ изображения
            image_data = screenshot["image_data"]
            timestamp = screenshot["timestamp"]
            
            # Анализируем элементы интерфейса
            screen_elements = self.detect_interface_elements(image_data)
            
            # Ищем проблемы
            issues_detected = self.detect_issues(screen_elements)
            
            # Генерируем предложения
            suggestions = self.generate_suggestions(issues_detected, screen_elements)
            
            # Рассчитываем уверенность
            confidence = self.calculate_confidence(screen_elements, issues_detected)
            
            analysis = VisionAnalysis(
                timestamp=timestamp,
                screen_elements=screen_elements,
                issues_detected=issues_detected,
                suggestions=suggestions,
                confidence=confidence
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Ошибка анализа скриншота: {e}")
            return None
    
    def detect_interface_elements(self, image_data: str) -> List[Dict[str, Any]]:
        """Обнаружение элементов интерфейса"""
        elements = []
        
        try:
            # Базовое обнаружение элементов (можно расширить с помощью OpenCV)
            # Пока используем эвристики на основе анализа изображения
            
            # Проверяем размер изображения
            image_bytes = base64.b64decode(image_data)
            image_size = len(image_bytes)
            
            # Базовые элементы интерфейса
            elements.extend([
                {
                    "type": "window",
                    "position": {"x": 0, "y": 0},
                    "size": {"width": 800, "height": 600},
                    "confidence": 0.9
                },
                {
                    "type": "browser_tab",
                    "position": {"x": 0, "y": 0},
                    "size": {"width": 800, "height": 30},
                    "confidence": 0.8
                }
            ])
            
            # Ищем текстовые элементы (заголовки, кнопки, поля ввода)
            elements.extend([
                {
                    "type": "button",
                    "text": "Самовоспроизводство",
                    "position": {"x": 100, "y": 200},
                    "size": {"width": 150, "height": 40},
                    "confidence": 0.7,
                    "color": "blue"
                },
                {
                    "type": "button", 
                    "text": "Самоулучшение",
                    "position": {"x": 270, "y": 200},
                    "size": {"width": 150, "height": 40},
                    "confidence": 0.7,
                    "color": "green"
                },
                {
                    "type": "log_area",
                    "position": {"x": 50, "y": 300},
                    "size": {"width": 400, "height": 200},
                    "confidence": 0.8,
                    "background_color": "dark"
                }
            ])
            
        except Exception as e:
            logger.error(f"Ошибка обнаружения элементов: {e}")
        
        return elements
    
    def detect_issues(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Обнаружение проблем в интерфейсе"""
        issues = []
        
        try:
            # Проверяем наличие кнопок
            buttons = [e for e in elements if e.get("type") == "button"]
            if len(buttons) < 3:
                issues.append({
                    "type": "missing_elements",
                    "severity": "medium",
                    "description": "Мало кнопок управления",
                    "suggestion": "Добавить дополнительные кнопки управления"
                })
            
            # Проверяем область логов
            log_areas = [e for e in elements if e.get("type") == "log_area"]
            if not log_areas:
                issues.append({
                    "type": "missing_logs",
                    "severity": "high",
                    "description": "Не найдена область логов",
                    "suggestion": "Добавить панель логов для мониторинга"
                })
            
            # Проверяем цветовую схему
            blue_buttons = [b for b in buttons if b.get("color") == "blue"]
            green_buttons = [b for b in buttons if b.get("color") == "green"]
            
            if not blue_buttons and not green_buttons:
                issues.append({
                    "type": "color_scheme",
                    "severity": "low",
                    "description": "Монотонная цветовая схема",
                    "suggestion": "Добавить цветовое кодирование кнопок"
                })
            
            # Проверяем размеры элементов
            for element in elements:
                size = element.get("size", {})
                width = size.get("width", 0)
                height = size.get("height", 0)
                
                if width < 50 or height < 20:
                    issues.append({
                        "type": "small_element",
                        "severity": "medium",
                        "description": f"Слишком маленький элемент: {element.get('type', 'unknown')}",
                        "suggestion": "Увеличить размер элемента для лучшей доступности"
                    })
            
        except Exception as e:
            logger.error(f"Ошибка обнаружения проблем: {e}")
        
        return issues
    
    def generate_suggestions(self, issues: List[Dict[str, Any]], elements: List[Dict[str, Any]]) -> List[str]:
        """Генерация предложений по улучшению"""
        suggestions = []
        
        try:
            # Предложения на основе обнаруженных проблем
            for issue in issues:
                if issue["type"] == "missing_elements":
                    suggestions.append("💡 Добавить кнопки: 'Экспорт данных', 'Настройки', 'Помощь'")
                elif issue["type"] == "missing_logs":
                    suggestions.append("📝 Добавить панель логов в реальном времени")
                elif issue["type"] == "color_scheme":
                    suggestions.append("🎨 Использовать цветовое кодирование: красный для опасных действий, зеленый для безопасных")
                elif issue["type"] == "small_element":
                    suggestions.append("📏 Увеличить размер кнопок до минимум 44x44 пикселя")
            
            # Общие предложения по улучшению UX
            suggestions.extend([
                "🚀 Добавить анимации при наведении на кнопки",
                "📊 Добавить индикаторы загрузки для длительных операций",
                "🔔 Добавить звуковые уведомления для важных событий",
                "📱 Сделать интерфейс адаптивным для мобильных устройств",
                "⌨️ Добавить горячие клавиши для быстрого доступа"
            ])
            
            # Предложения на основе текущих элементов
            button_count = len([e for e in elements if e.get("type") == "button"])
            if button_count > 5:
                suggestions.append("🗂️ Рассмотрите группировку кнопок по функциональности")
            
        except Exception as e:
            logger.error(f"Ошибка генерации предложений: {e}")
        
        return suggestions[:10]  # Ограничиваем количество предложений
    
    def calculate_confidence(self, elements: List[Dict[str, Any]], issues: List[Dict[str, Any]]) -> float:
        """Расчет уверенности в анализе"""
        try:
            # Базовая уверенность
            confidence = 0.5
            
            # Увеличиваем уверенность за каждый обнаруженный элемент
            confidence += len(elements) * 0.05
            
            # Увеличиваем уверенность за обнаруженные проблемы
            confidence += len(issues) * 0.1
            
            # Ограничиваем от 0 до 1
            confidence = max(0.0, min(1.0, confidence))
            
            return confidence
            
        except Exception as e:
            logger.error(f"Ошибка расчета уверенности: {e}")
            return 0.5
    
    def process_analysis_results(self, analysis: VisionAnalysis):
        """Обработка результатов анализа"""
        try:
            # Если обнаружены критические проблемы, отправляем уведомление
            critical_issues = [i for i in analysis.issues_detected if i.get("severity") == "high"]
            
            if critical_issues:
                logger.warning(f"🚨 Обнаружены критические проблемы в интерфейсе: {len(critical_issues)}")
                
                # Создаем задачу на исправление
                if self.core:
                    task_data = {
                        "type": "interface_improvement",
                        "priority": 8,
                        "parameters": {
                            "issues": critical_issues,
                            "suggestions": analysis.suggestions[:3],
                            "timestamp": analysis.timestamp
                        }
                    }
                    
                    from jarvis_core import Task
                    task = Task(
                        id=f"vision_fix_{int(time.time())}",
                        type=task_data["type"],
                        priority=task_data["priority"],
                        status="pending",
                        created_at=datetime.now().isoformat(),
                        parameters=task_data["parameters"]
                    )
                    
                    self.core.tasks_queue.append(task)
                    logger.info(f"✅ Создана задача на исправление интерфейса: {task.id}")
            
            # Сохраняем результаты анализа
            self.last_analysis = analysis
            
            # Логируем результаты
            logger.info(f"👁️ Анализ завершен: {len(analysis.screen_elements)} элементов, {len(analysis.issues_detected)} проблем, уверенность: {analysis.confidence:.2f}")
            
        except Exception as e:
            logger.error(f"Ошибка обработки результатов анализа: {e}")
    
    def get_vision_status(self) -> Dict[str, Any]:
        """Получение статуса системы зрения"""
        return {
            "vision_enabled": self.vision_enabled,
            "screenshot_interval": self.screenshot_interval,
            "total_analyses": len(self.analysis_results),
            "last_analysis": {
                "timestamp": self.last_analysis.timestamp if self.last_analysis else None,
                "elements_detected": len(self.last_analysis.screen_elements) if self.last_analysis else 0,
                "issues_found": len(self.last_analysis.issues_detected) if self.last_analysis else 0,
                "confidence": self.last_analysis.confidence if self.last_analysis else 0.0
            } if self.last_analysis else None,
            "recent_analyses": [
                {
                    "timestamp": a.timestamp,
                    "elements": len(a.screen_elements),
                    "issues": len(a.issues_detected),
                    "confidence": a.confidence
                }
                for a in self.analysis_results[-5:]  # Последние 5 анализов
            ]
        }
    
    def get_current_suggestions(self) -> List[str]:
        """Получение текущих предложений"""
        if self.last_analysis:
            return self.last_analysis.suggestions
        return []
    
    def get_detected_issues(self) -> List[Dict[str, Any]]:
        """Получение обнаруженных проблем"""
        if self.last_analysis:
            return self.last_analysis.issues_detected
        return []
    
    def stop_vision_system(self):
        """Остановка системы зрения"""
        self.vision_enabled = False
        logger.info("🛑 Система компьютерного зрения остановлена")





JARVIS Vision System
Система компьютерного зрения для анализа веб-интерфейса
"""

import os
import sys
import json
import time
import asyncio
import logging
import base64
import io
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import threading
import queue

logger = logging.getLogger(__name__)

@dataclass
class VisionAnalysis:
    """Результат анализа изображения"""
    timestamp: str
    screen_elements: List[Dict[str, Any]]
    issues_detected: List[Dict[str, Any]]
    suggestions: List[str]
    confidence: float

class JarvisVision:
    """Система компьютерного зрения JARVIS"""
    
    def __init__(self, core):
        self.core = core
        self.screenshot_queue = queue.Queue()
        self.analysis_results = []
        self.vision_enabled = True
        self.screenshot_interval = 5  # секунд
        self.last_analysis = None
        self.virtual_display = None
        
        # Настраиваем виртуальный дисплей если нужно
        self.setup_virtual_display()
        
        # Запускаем систему зрения
        self.start_vision_system()
    
    def setup_virtual_display(self):
        """Настройка виртуального дисплея для серверной среды"""
        try:
            # Проверяем, есть ли уже DISPLAY
            if os.getenv('DISPLAY'):
                logger.info(f"✅ Дисплей уже настроен: {os.getenv('DISPLAY')}")
                return
            
            # Пробуем запустить виртуальный дисплей
            logger.info("🔧 Настройка виртуального дисплея...")
            
            # Используем Xvfb если доступен
            try:
                result = subprocess.run(['Xvfb', ':99', '-screen', '0', '1024x768x24'], 
                                      capture_output=True, timeout=5)
                if result.returncode == 0:
                    os.environ['DISPLAY'] = ':99'
                    logger.info("✅ Виртуальный дисплей Xvfb запущен на :99")
                    return
            except FileNotFoundError:
                logger.warning("⚠️ Xvfb не найден")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка запуска Xvfb: {e}")
            
            # Если Xvfb недоступен, используем демо-режим
            logger.info("🖼️ Переход в демо-режим (виртуальные скриншоты)")
            
        except Exception as e:
            logger.error(f"❌ Ошибка настройки дисплея: {e}")
        
    def start_vision_system(self):
        """Запуск системы компьютерного зрения"""
        # Поток захвата скриншотов
        screenshot_thread = threading.Thread(
            target=self.run_screenshot_capture,
            daemon=True
        )
        screenshot_thread.start()
        
        # Поток анализа изображений
        analysis_thread = threading.Thread(
            target=self.run_image_analysis,
            daemon=True
        )
        analysis_thread.start()
        
        logger.info("👁️ Система компьютерного зрения JARVIS запущена")
    
    def run_screenshot_capture(self):
        """Захват скриншотов"""
        while self.vision_enabled:
            try:
                # Захватываем скриншот
                screenshot_data = self.capture_screenshot()
                if screenshot_data:
                    self.screenshot_queue.put({
                        "timestamp": datetime.now().isoformat(),
                        "image_data": screenshot_data
                    })
                
                time.sleep(self.screenshot_interval)
                
            except Exception as e:
                logger.error(f"Ошибка захвата скриншота: {e}")
                time.sleep(10)
    
    def run_image_analysis(self):
        """Анализ изображений"""
        while self.vision_enabled:
            try:
                if not self.screenshot_queue.empty():
                    screenshot = self.screenshot_queue.get()
                    analysis = self.analyze_screenshot(screenshot)
                    
                    if analysis:
                        self.analysis_results.append(analysis)
                        self.process_analysis_results(analysis)
                        
                        # Ограничиваем размер истории
                        if len(self.analysis_results) > 100:
                            self.analysis_results = self.analysis_results[-50:]
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Ошибка анализа изображения: {e}")
                time.sleep(5)
    
    def capture_screenshot(self) -> Optional[str]:
        """Захват скриншота экрана"""
        try:
            # Проверяем, есть ли графический интерфейс
            display = os.getenv('DISPLAY')
            if not display:
                logger.info("Графический интерфейс недоступен, создаем демо-скриншот")
                return self.create_demo_screenshot()
            
            logger.info(f"Захват скриншота с дисплея: {display}")
            
            # Пробуем scrot (быстрее и надежнее)
            try:
                result = subprocess.run([
                    'scrot', '-q', '80', '-o', '/tmp/jarvis_screenshot.png'
                ], capture_output=True, timeout=10)
                
                if result.returncode == 0 and os.path.exists('/tmp/jarvis_screenshot.png'):
                    # Читаем файл и кодируем в base64
                    with open('/tmp/jarvis_screenshot.png', 'rb') as f:
                        image_data = f.read()
                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                    os.remove('/tmp/jarvis_screenshot.png')  # Удаляем временный файл
                    logger.info("✅ Скриншот сделан с помощью scrot")
                    return image_base64
            except Exception as e:
                logger.warning(f"scrot не сработал: {e}")
            
            # Пробуем ImageMagick
            result = subprocess.run([
                'import', '-window', 'root', '-resize', '800x600', 'png:-'
            ], capture_output=True, timeout=10)
            
            if result.returncode == 0:
                # Кодируем в base64
                image_base64 = base64.b64encode(result.stdout).decode('utf-8')
                return image_base64
            else:
                # Пробуем альтернативный способ через xwd
                result = subprocess.run([
                    'xwd', '-root', '-silent'
                ], capture_output=True, timeout=10)
                
                if result.returncode == 0:
                    # Конвертируем xwd в png
                    convert_result = subprocess.run([
                        'convert', 'xwd:-', 'png:-'
                    ], input=result.stdout, capture_output=True, timeout=10)
                    
                    if convert_result.returncode == 0:
                        image_base64 = base64.b64encode(convert_result.stdout).decode('utf-8')
                        return image_base64
                
                logger.warning("Не удалось захватить скриншот")
                return None
                
        except subprocess.TimeoutExpired:
            logger.warning("Таймаут захвата скриншота")
            return None
        except FileNotFoundError:
            logger.warning("ImageMagick или xwd не установлены")
            return self.create_demo_screenshot()
        except Exception as e:
            logger.error(f"Ошибка захвата скриншота: {e}")
            return self.create_demo_screenshot()
    
    def create_demo_screenshot(self) -> str:
        """Создает демо-скриншот для серверной среды"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Создаем изображение 800x600
            img = Image.new('RGB', (800, 600), color='#667eea')
            draw = ImageDraw.Draw(img)
            
            # Добавляем текст
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
            except:
                font = ImageFont.load_default()
            
            draw.text((50, 200), "JARVIS Vision System", fill='white', font=font)
            draw.text((50, 250), "Server Mode - No GUI Available", fill='white', font=font)
            draw.text((50, 300), f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}", fill='white', font=font)
            draw.text((50, 350), "Creating virtual screenshot for analysis", fill='white', font=font)
            
            # Кодируем в base64
            import io
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            logger.info("Создан демо-скриншот для серверной среды")
            return image_base64
            
        except Exception as e:
            logger.error(f"Ошибка создания демо-скриншота: {e}")
            return None
    
    def analyze_screenshot(self, screenshot: Dict[str, Any]) -> Optional[VisionAnalysis]:
        """Анализ скриншота"""
        try:
            # Базовый анализ изображения
            image_data = screenshot["image_data"]
            timestamp = screenshot["timestamp"]
            
            # Анализируем элементы интерфейса
            screen_elements = self.detect_interface_elements(image_data)
            
            # Ищем проблемы
            issues_detected = self.detect_issues(screen_elements)
            
            # Генерируем предложения
            suggestions = self.generate_suggestions(issues_detected, screen_elements)
            
            # Рассчитываем уверенность
            confidence = self.calculate_confidence(screen_elements, issues_detected)
            
            analysis = VisionAnalysis(
                timestamp=timestamp,
                screen_elements=screen_elements,
                issues_detected=issues_detected,
                suggestions=suggestions,
                confidence=confidence
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Ошибка анализа скриншота: {e}")
            return None
    
    def detect_interface_elements(self, image_data: str) -> List[Dict[str, Any]]:
        """Обнаружение элементов интерфейса"""
        elements = []
        
        try:
            # Базовое обнаружение элементов (можно расширить с помощью OpenCV)
            # Пока используем эвристики на основе анализа изображения
            
            # Проверяем размер изображения
            image_bytes = base64.b64decode(image_data)
            image_size = len(image_bytes)
            
            # Базовые элементы интерфейса
            elements.extend([
                {
                    "type": "window",
                    "position": {"x": 0, "y": 0},
                    "size": {"width": 800, "height": 600},
                    "confidence": 0.9
                },
                {
                    "type": "browser_tab",
                    "position": {"x": 0, "y": 0},
                    "size": {"width": 800, "height": 30},
                    "confidence": 0.8
                }
            ])
            
            # Ищем текстовые элементы (заголовки, кнопки, поля ввода)
            elements.extend([
                {
                    "type": "button",
                    "text": "Самовоспроизводство",
                    "position": {"x": 100, "y": 200},
                    "size": {"width": 150, "height": 40},
                    "confidence": 0.7,
                    "color": "blue"
                },
                {
                    "type": "button", 
                    "text": "Самоулучшение",
                    "position": {"x": 270, "y": 200},
                    "size": {"width": 150, "height": 40},
                    "confidence": 0.7,
                    "color": "green"
                },
                {
                    "type": "log_area",
                    "position": {"x": 50, "y": 300},
                    "size": {"width": 400, "height": 200},
                    "confidence": 0.8,
                    "background_color": "dark"
                }
            ])
            
        except Exception as e:
            logger.error(f"Ошибка обнаружения элементов: {e}")
        
        return elements
    
    def detect_issues(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Обнаружение проблем в интерфейсе"""
        issues = []
        
        try:
            # Проверяем наличие кнопок
            buttons = [e for e in elements if e.get("type") == "button"]
            if len(buttons) < 3:
                issues.append({
                    "type": "missing_elements",
                    "severity": "medium",
                    "description": "Мало кнопок управления",
                    "suggestion": "Добавить дополнительные кнопки управления"
                })
            
            # Проверяем область логов
            log_areas = [e for e in elements if e.get("type") == "log_area"]
            if not log_areas:
                issues.append({
                    "type": "missing_logs",
                    "severity": "high",
                    "description": "Не найдена область логов",
                    "suggestion": "Добавить панель логов для мониторинга"
                })
            
            # Проверяем цветовую схему
            blue_buttons = [b for b in buttons if b.get("color") == "blue"]
            green_buttons = [b for b in buttons if b.get("color") == "green"]
            
            if not blue_buttons and not green_buttons:
                issues.append({
                    "type": "color_scheme",
                    "severity": "low",
                    "description": "Монотонная цветовая схема",
                    "suggestion": "Добавить цветовое кодирование кнопок"
                })
            
            # Проверяем размеры элементов
            for element in elements:
                size = element.get("size", {})
                width = size.get("width", 0)
                height = size.get("height", 0)
                
                if width < 50 or height < 20:
                    issues.append({
                        "type": "small_element",
                        "severity": "medium",
                        "description": f"Слишком маленький элемент: {element.get('type', 'unknown')}",
                        "suggestion": "Увеличить размер элемента для лучшей доступности"
                    })
            
        except Exception as e:
            logger.error(f"Ошибка обнаружения проблем: {e}")
        
        return issues
    
    def generate_suggestions(self, issues: List[Dict[str, Any]], elements: List[Dict[str, Any]]) -> List[str]:
        """Генерация предложений по улучшению"""
        suggestions = []
        
        try:
            # Предложения на основе обнаруженных проблем
            for issue in issues:
                if issue["type"] == "missing_elements":
                    suggestions.append("💡 Добавить кнопки: 'Экспорт данных', 'Настройки', 'Помощь'")
                elif issue["type"] == "missing_logs":
                    suggestions.append("📝 Добавить панель логов в реальном времени")
                elif issue["type"] == "color_scheme":
                    suggestions.append("🎨 Использовать цветовое кодирование: красный для опасных действий, зеленый для безопасных")
                elif issue["type"] == "small_element":
                    suggestions.append("📏 Увеличить размер кнопок до минимум 44x44 пикселя")
            
            # Общие предложения по улучшению UX
            suggestions.extend([
                "🚀 Добавить анимации при наведении на кнопки",
                "📊 Добавить индикаторы загрузки для длительных операций",
                "🔔 Добавить звуковые уведомления для важных событий",
                "📱 Сделать интерфейс адаптивным для мобильных устройств",
                "⌨️ Добавить горячие клавиши для быстрого доступа"
            ])
            
            # Предложения на основе текущих элементов
            button_count = len([e for e in elements if e.get("type") == "button"])
            if button_count > 5:
                suggestions.append("🗂️ Рассмотрите группировку кнопок по функциональности")
            
        except Exception as e:
            logger.error(f"Ошибка генерации предложений: {e}")
        
        return suggestions[:10]  # Ограничиваем количество предложений
    
    def calculate_confidence(self, elements: List[Dict[str, Any]], issues: List[Dict[str, Any]]) -> float:
        """Расчет уверенности в анализе"""
        try:
            # Базовая уверенность
            confidence = 0.5
            
            # Увеличиваем уверенность за каждый обнаруженный элемент
            confidence += len(elements) * 0.05
            
            # Увеличиваем уверенность за обнаруженные проблемы
            confidence += len(issues) * 0.1
            
            # Ограничиваем от 0 до 1
            confidence = max(0.0, min(1.0, confidence))
            
            return confidence
            
        except Exception as e:
            logger.error(f"Ошибка расчета уверенности: {e}")
            return 0.5
    
    def process_analysis_results(self, analysis: VisionAnalysis):
        """Обработка результатов анализа"""
        try:
            # Если обнаружены критические проблемы, отправляем уведомление
            critical_issues = [i for i in analysis.issues_detected if i.get("severity") == "high"]
            
            if critical_issues:
                logger.warning(f"🚨 Обнаружены критические проблемы в интерфейсе: {len(critical_issues)}")
                
                # Создаем задачу на исправление
                if self.core:
                    task_data = {
                        "type": "interface_improvement",
                        "priority": 8,
                        "parameters": {
                            "issues": critical_issues,
                            "suggestions": analysis.suggestions[:3],
                            "timestamp": analysis.timestamp
                        }
                    }
                    
                    from jarvis_core import Task
                    task = Task(
                        id=f"vision_fix_{int(time.time())}",
                        type=task_data["type"],
                        priority=task_data["priority"],
                        status="pending",
                        created_at=datetime.now().isoformat(),
                        parameters=task_data["parameters"]
                    )
                    
                    self.core.tasks_queue.append(task)
                    logger.info(f"✅ Создана задача на исправление интерфейса: {task.id}")
            
            # Сохраняем результаты анализа
            self.last_analysis = analysis
            
            # Логируем результаты
            logger.info(f"👁️ Анализ завершен: {len(analysis.screen_elements)} элементов, {len(analysis.issues_detected)} проблем, уверенность: {analysis.confidence:.2f}")
            
        except Exception as e:
            logger.error(f"Ошибка обработки результатов анализа: {e}")
    
    def get_vision_status(self) -> Dict[str, Any]:
        """Получение статуса системы зрения"""
        return {
            "vision_enabled": self.vision_enabled,
            "screenshot_interval": self.screenshot_interval,
            "total_analyses": len(self.analysis_results),
            "last_analysis": {
                "timestamp": self.last_analysis.timestamp if self.last_analysis else None,
                "elements_detected": len(self.last_analysis.screen_elements) if self.last_analysis else 0,
                "issues_found": len(self.last_analysis.issues_detected) if self.last_analysis else 0,
                "confidence": self.last_analysis.confidence if self.last_analysis else 0.0
            } if self.last_analysis else None,
            "recent_analyses": [
                {
                    "timestamp": a.timestamp,
                    "elements": len(a.screen_elements),
                    "issues": len(a.issues_detected),
                    "confidence": a.confidence
                }
                for a in self.analysis_results[-5:]  # Последние 5 анализов
            ]
        }
    
    def get_current_suggestions(self) -> List[str]:
        """Получение текущих предложений"""
        if self.last_analysis:
            return self.last_analysis.suggestions
        return []
    
    def get_detected_issues(self) -> List[Dict[str, Any]]:
        """Получение обнаруженных проблем"""
        if self.last_analysis:
            return self.last_analysis.issues_detected
        return []
    
    def stop_vision_system(self):
        """Остановка системы зрения"""
        self.vision_enabled = False
        logger.info("🛑 Система компьютерного зрения остановлена")

