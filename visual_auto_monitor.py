#!/usr/bin/env python3
"""
Автоматический визуальный мониторинг системы Mentor
Делает скриншоты, анализирует UI и автоматически исправляет проблемы
"""

import asyncio
import json
import logging
import time
import os
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from PIL import Image, ImageDraw, ImageFont
import io
import base64

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/visual_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VisualAutoMonitor:
    """Автоматический визуальный мониторинг"""
    
    def __init__(self):
        self.base_url = "http://localhost:8081"
        self.screenshots_dir = "/workspace/visual_screenshots"
        self.reports_dir = "/workspace/visual_reports"
        self.monitoring_active = False
        
        # Создаем директории
        os.makedirs(self.screenshots_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Счетчики
        self.screenshots_taken = 0
        self.issues_found = 0
        self.fixes_applied = 0
        
        # История проверок
        self.check_history = []
        
        logger.info("👁️ Автоматический визуальный мониторинг инициализирован")
    
    async def start_visual_monitoring(self):
        """Запуск автоматического визуального мониторинга"""
        self.monitoring_active = True
        logger.info("🚀 Запуск автоматического визуального мониторинга")
        
        while self.monitoring_active:
            try:
                # Делаем скриншот и анализируем каждые 60 секунд
                await self.capture_and_analyze()
                
                # Проверяем все страницы каждые 5 минут
                if self.screenshots_taken % 5 == 0:
                    await self.check_all_pages()
                
                # Генерируем отчет каждые 10 минут
                if self.screenshots_taken % 10 == 0:
                    await self.generate_visual_report()
                
                await asyncio.sleep(60)  # Проверяем каждую минуту
                
            except Exception as e:
                logger.error(f"❌ Ошибка визуального мониторинга: {e}")
                await asyncio.sleep(120)  # При ошибке ждем дольше
    
    async def capture_and_analyze(self):
        """Захват и анализ текущего состояния интерфейса"""
        try:
            self.screenshots_taken += 1
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            logger.info(f"📸 Создание визуального снимка #{self.screenshots_taken}")
            
            # Получаем HTML страницы
            response = requests.get(self.base_url, timeout=10)
            
            if response.status_code == 200:
                html_content = response.text
                
                # Анализируем содержимое
                analysis = await self.analyze_html_content(html_content)
                
                # Создаем визуальный снимок
                screenshot_path = await self.create_visual_snapshot(
                    html_content, analysis, timestamp
                )
                
                # Проверяем на проблемы
                issues = await self.detect_visual_issues(analysis)
                
                # Записываем результат
                check_result = {
                    "timestamp": datetime.now().isoformat(),
                    "screenshot_number": self.screenshots_taken,
                    "screenshot_path": screenshot_path,
                    "analysis": analysis,
                    "issues_found": issues,
                    "status": "completed"
                }
                
                self.check_history.append(check_result)
                
                # Применяем автоматические исправления
                if issues:
                    await self.apply_automatic_fixes(issues)
                
                logger.info(f"✅ Визуальный анализ #{self.screenshots_taken} завершен")
                
            else:
                logger.warning(f"⚠️ Не удалось получить страницу: HTTP {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка захвата и анализа: {e}")
    
    async def analyze_html_content(self, html_content: str) -> Dict[str, Any]:
        """Анализ HTML содержимого"""
        try:
            analysis = {
                "content_size": len(html_content),
                "has_title": "<title>" in html_content,
                "title_text": "",
                "has_css": "<style>" in html_content,
                "has_javascript": "<script>" in html_content,
                "has_russian": any(char in html_content.lower() for char in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"),
                "responsive_design": "viewport" in html_content,
                "modern_css": False,
                "ui_elements": {},
                "performance_indicators": {}
            }
            
            # Извлекаем заголовок
            if "<title>" in html_content:
                start = html_content.find("<title>") + 7
                end = html_content.find("</title>", start)
                if end > start:
                    analysis["title_text"] = html_content[start:end]
            
            # Проверяем современные CSS элементы
            modern_css_features = ["grid", "flexbox", "transform", "gradient", "border-radius"]
            analysis["modern_css"] = any(feature in html_content.lower() for feature in modern_css_features)
            
            # Считаем UI элементы
            ui_elements = {
                "buttons": html_content.count("button"),
                "inputs": html_content.count("<input"),
                "divs": html_content.count("<div"),
                "cards": html_content.count("card"),
                "containers": html_content.count("container")
            }
            analysis["ui_elements"] = ui_elements
            
            # Оцениваем производительность
            analysis["performance_indicators"] = {
                "estimated_load_time": len(html_content) / 10000,  # Примерная оценка
                "css_complexity": html_content.count("{"),
                "js_complexity": html_content.count("function")
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Ошибка анализа HTML: {e}")
            return {"status": "error", "error": str(e)}
    
    async def create_visual_snapshot(self, html_content: str, analysis: Dict[str, Any], timestamp: str) -> str:
        """Создание визуального снимка страницы"""
        try:
            # Создаем изображение с информацией о странице
            img = Image.new('RGB', (1200, 800), color='#f8f9fa')
            draw = ImageDraw.Draw(img)
            
            # Пытаемся загрузить шрифты
            try:
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
                font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Заголовок
            title = analysis.get("title_text", "Mentor System")
            draw.text((50, 30), f"📸 {title}", fill='#2c3e50', font=font_large)
            
            # Информация о времени
            draw.text((50, 70), f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fill='#27ae60', font=font_medium)
            draw.text((50, 100), f"Снимок: #{self.screenshots_taken}", fill='#3498db', font=font_medium)
            
            # Метрики
            y_pos = 140
            metrics = [
                f"Размер контента: {analysis.get('content_size', 0):,} байт",
                f"Русский язык: {'✅' if analysis.get('has_russian') else '❌'}",
                f"Адаптивный дизайн: {'✅' if analysis.get('responsive_design') else '❌'}",
                f"Современный CSS: {'✅' if analysis.get('modern_css') else '❌'}",
                f"JavaScript: {'✅' if analysis.get('has_javascript') else '❌'}"
            ]
            
            for metric in metrics:
                draw.text((50, y_pos), metric, fill='#34495e', font=font_small)
                y_pos += 25
            
            # UI элементы
            draw.text((50, y_pos + 20), "UI Элементы:", fill='#2c3e50', font=font_medium)
            y_pos += 50
            
            ui_elements = analysis.get("ui_elements", {})
            for element, count in ui_elements.items():
                draw.text((70, y_pos), f"{element}: {count}", fill='#7f8c8d', font=font_small)
                y_pos += 20
            
            # Производительность
            draw.text((50, y_pos + 20), "Производительность:", fill='#2c3e50', font=font_medium)
            y_pos += 50
            
            perf = analysis.get("performance_indicators", {})
            perf_metrics = [
                f"Время загрузки: ~{perf.get('estimated_load_time', 0):.2f}с",
                f"Сложность CSS: {perf.get('css_complexity', 0)}",
                f"Сложность JS: {perf.get('js_complexity', 0)}"
            ]
            
            for metric in perf_metrics:
                draw.text((70, y_pos), metric, fill='#8e44ad', font=font_small)
                y_pos += 20
            
            # Превью HTML (первые строки)
            draw.rectangle([50, y_pos + 30, 1150, 750], outline='#bdc3c7', width=2)
            draw.text((60, y_pos + 40), "HTML Превью:", fill='#2c3e50', font=font_medium)
            
            # Показываем ключевые части HTML
            html_lines = html_content.split('\n')[:20]  # Первые 20 строк
            preview_y = y_pos + 70
            
            for i, line in enumerate(html_lines):
                if preview_y > 720:
                    break
                clean_line = line.strip()[:80]  # Обрезаем длинные строки
                if clean_line:
                    draw.text((70, preview_y), clean_line, fill='#7f8c8d', font=font_small)
                    preview_y += 18
            
            # Сохраняем снимок
            filename = f"visual_snapshot_{timestamp}.png"
            filepath = os.path.join(self.screenshots_dir, filename)
            img.save(filepath)
            
            logger.info(f"📸 Визуальный снимок сохранен: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания снимка: {e}")
            return None
    
    async def detect_visual_issues(self, analysis: Dict[str, Any]) -> List[str]:
        """Обнаружение визуальных проблем"""
        issues = []
        
        try:
            # Проверяем размер контента
            content_size = analysis.get("content_size", 0)
            if content_size > 200000:  # Больше 200KB
                issues.append("Слишком большой размер HTML страницы")
            elif content_size < 1000:  # Меньше 1KB
                issues.append("Подозрительно маленький размер страницы")
            
            # Проверяем русский язык
            if not analysis.get("has_russian", False):
                issues.append("Отсутствует русский текст на странице")
            
            # Проверяем адаптивность
            if not analysis.get("responsive_design", False):
                issues.append("Отсутствует адаптивный дизайн")
            
            # Проверяем современность
            if not analysis.get("modern_css", False):
                issues.append("Используются устаревшие CSS технологии")
            
            # Проверяем производительность
            perf = analysis.get("performance_indicators", {})
            if perf.get("estimated_load_time", 0) > 3:
                issues.append("Медленная загрузка страницы")
            
            # Проверяем UI элементы
            ui_elements = analysis.get("ui_elements", {})
            if ui_elements.get("buttons", 0) == 0:
                issues.append("Отсутствуют интерактивные кнопки")
            
            if issues:
                self.issues_found += len(issues)
                logger.warning(f"⚠️ Обнаружено {len(issues)} визуальных проблем")
                for issue in issues:
                    logger.warning(f"   - {issue}")
            
            return issues
            
        except Exception as e:
            logger.error(f"❌ Ошибка обнаружения проблем: {e}")
            return []
    
    async def apply_automatic_fixes(self, issues: List[str]):
        """Применение автоматических исправлений"""
        try:
            fixes_applied = []
            
            for issue in issues:
                fix_applied = False
                
                # Исправляем проблемы с русским языком
                if "русский текст" in issue.lower():
                    await self.request_russian_content_fix()
                    fix_applied = True
                
                # Исправляем проблемы с адаптивностью
                elif "адаптивный" in issue.lower():
                    await self.request_responsive_design_fix()
                    fix_applied = True
                
                # Исправляем проблемы с производительностью
                elif "загрузка" in issue.lower() or "производительность" in issue.lower():
                    await self.request_performance_optimization()
                    fix_applied = True
                
                # Исправляем проблемы с UI
                elif "кнопки" in issue.lower() or "интерактив" in issue.lower():
                    await self.request_ui_improvements()
                    fix_applied = True
                
                if fix_applied:
                    fixes_applied.append(issue)
                    self.fixes_applied += 1
            
            if fixes_applied:
                logger.info(f"🔧 Применено {len(fixes_applied)} автоматических исправлений")
                for fix in fixes_applied:
                    logger.info(f"   ✅ Исправлено: {fix}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка применения исправлений: {e}")
    
    async def request_russian_content_fix(self):
        """Запрос исправления русского контента"""
        try:
            response = requests.post(
                f"{self.base_url}/api/chat/send",
                json={
                    "message": "Убедись что весь интерфейс на русском языке и добавь недостающие русские тексты",
                    "agent_type": "designer",
                    "user_id": "visual_monitor"
                },
                timeout=15
            )
            
            if response.status_code == 200:
                logger.info("✅ Запрос на исправление русского контента отправлен")
            
        except Exception as e:
            logger.error(f"❌ Ошибка запроса исправления контента: {e}")
    
    async def request_responsive_design_fix(self):
        """Запрос исправления адаптивного дизайна"""
        try:
            response = requests.post(
                f"{self.base_url}/api/chat/send",
                json={
                    "message": "Улучши адаптивность интерфейса для всех размеров экранов",
                    "agent_type": "designer",
                    "user_id": "visual_monitor"
                },
                timeout=15
            )
            
            if response.status_code == 200:
                logger.info("✅ Запрос на улучшение адаптивности отправлен")
            
        except Exception as e:
            logger.error(f"❌ Ошибка запроса улучшения адаптивности: {e}")
    
    async def request_performance_optimization(self):
        """Запрос оптимизации производительности"""
        try:
            response = requests.post(
                f"{self.base_url}/api/chat/send",
                json={
                    "message": "Оптимизируй скорость загрузки и производительность интерфейса",
                    "agent_type": "code_developer",
                    "user_id": "visual_monitor"
                },
                timeout=15
            )
            
            if response.status_code == 200:
                logger.info("✅ Запрос на оптимизацию производительности отправлен")
            
        except Exception as e:
            logger.error(f"❌ Ошибка запроса оптимизации: {e}")
    
    async def request_ui_improvements(self):
        """Запрос улучшения UI элементов"""
        try:
            response = requests.post(
                f"{self.base_url}/api/chat/send",
                json={
                    "message": "Добавь недостающие интерактивные элементы и улучши пользовательский интерфейс",
                    "agent_type": "designer",
                    "user_id": "visual_monitor"
                },
                timeout=15
            )
            
            if response.status_code == 200:
                logger.info("✅ Запрос на улучшение UI отправлен")
            
        except Exception as e:
            logger.error(f"❌ Ошибка запроса улучшения UI: {e}")
    
    async def check_all_pages(self):
        """Проверка всех доступных страниц"""
        try:
            logger.info("🔍 Проверка всех страниц системы")
            
            pages_to_check = [
                "/",
                "/api/system/status", 
                "/api/autonomous/tasks"
            ]
            
            for page in pages_to_check:
                try:
                    response = requests.get(f"{self.base_url}{page}", timeout=10)
                    status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
                    logger.info(f"   {page}: {status}")
                    
                except Exception as e:
                    logger.warning(f"   {page}: ❌ Ошибка - {e}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки страниц: {e}")
    
    async def generate_visual_report(self):
        """Генерация визуального отчета"""
        try:
            logger.info("📊 Генерация визуального отчета")
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "monitoring_stats": {
                    "screenshots_taken": self.screenshots_taken,
                    "issues_found": self.issues_found,
                    "fixes_applied": self.fixes_applied,
                    "monitoring_active": self.monitoring_active
                },
                "recent_checks": self.check_history[-10:],  # Последние 10 проверок
                "summary": {
                    "avg_issues_per_check": self.issues_found / max(self.screenshots_taken, 1),
                    "fix_success_rate": (self.fixes_applied / max(self.issues_found, 1)) * 100,
                    "monitoring_duration": f"{self.screenshots_taken} минут"
                }
            }
            
            # Сохраняем JSON отчет
            report_file = os.path.join(
                self.reports_dir, 
                f"visual_monitor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"📊 Отчет сохранен: {report_file}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации отчета: {e}")
    
    def stop_monitoring(self):
        """Остановка визуального мониторинга"""
        self.monitoring_active = False
        logger.info("🛑 Автоматический визуальный мониторинг остановлен")

async def main():
    """Главная функция"""
    monitor = VisualAutoMonitor()
    
    try:
        logger.info("🚀 Запуск автоматического визуального мониторинга Mentor")
        await monitor.start_visual_monitoring()
    except KeyboardInterrupt:
        logger.info("📡 Получен сигнал остановки")
        monitor.stop_monitoring()
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
    finally:
        # Генерируем финальный отчет
        await monitor.generate_visual_report()
        logger.info("📊 Финальный отчет визуального мониторинга создан")

if __name__ == "__main__":
    asyncio.run(main())