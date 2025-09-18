#!/usr/bin/env python3
"""
JARVIS Visual Monitor
Автоматическая система визуального мониторинга веб-интерфейса
"""

import asyncio
import aiohttp
import base64
import time
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import subprocess
from PIL import Image, ImageDraw, ImageFont
import io

logger = logging.getLogger(__name__)

class VisualMonitor:
    """Система визуального мониторинга JARVIS"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.screenshots_dir = "/home/mentor/visual_screenshots"
        self.reports_dir = "/home/mentor/visual_reports"
        
        # Создаем директории
        os.makedirs(self.screenshots_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Страницы для мониторинга
        self.pages = {
            "main_dashboard": "/",
            "chat": "/chat", 
            "vision": "/vision",
            "visual_report": "/visual_test_report"
        }
        
        self.monitoring_active = False
        self.last_check_time = None
        self.check_results = {}
        
        logger.info("👁️ Visual Monitor инициализирован")
    
    async def start_monitoring(self):
        """Запуск визуального мониторинга"""
        self.monitoring_active = True
        logger.info("🚀 Запуск визуального мониторинга")
        
        while self.monitoring_active:
            try:
                await self.check_all_pages()
                await self.generate_visual_report()
                await asyncio.sleep(30)  # Проверяем каждые 30 секунд
            except Exception as e:
                logger.error(f"❌ Ошибка мониторинга: {e}")
                await asyncio.sleep(60)
    
    async def check_all_pages(self):
        """Проверка всех страниц"""
        logger.info("🔍 Проверка всех страниц...")
        
        for page_name, endpoint in self.pages.items():
            try:
                result = await self.check_page(page_name, endpoint)
                self.check_results[page_name] = result
                logger.info(f"✅ {page_name}: {result['status']} ({result['response_time']:.3f}s)")
            except Exception as e:
                logger.error(f"❌ Ошибка проверки {page_name}: {e}")
                self.check_results[page_name] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        self.last_check_time = datetime.now()
    
    async def check_page(self, page_name: str, endpoint: str) -> Dict[str, Any]:
        """Проверка конкретной страницы"""
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}{endpoint}") as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        content = await response.text()
                        size = len(content.encode('utf-8'))
                        
                        # Создаем визуальный скриншот страницы
                        screenshot_path = await self.create_page_screenshot(page_name, content, response_time)
                        
                        return {
                            "status": "ok",
                            "status_code": response.status,
                            "response_time": response_time,
                            "size": size,
                            "screenshot": screenshot_path,
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "status": "error",
                            "status_code": response.status,
                            "response_time": response_time,
                            "timestamp": datetime.now().isoformat()
                        }
                        
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "response_time": time.time() - start_time,
                    "timestamp": datetime.now().isoformat()
                }
    
    async def create_page_screenshot(self, page_name: str, content: str, response_time: float) -> str:
        """Создание визуального скриншота страницы"""
        try:
            # Создаем изображение страницы
            img = Image.new('RGB', (1200, 800), color='#f8f9fa')
            draw = ImageDraw.Draw(img)
            
            # Заголовок
            try:
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
                font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Заголовок страницы
            title = f"JARVIS - {page_name.replace('_', ' ').title()}"
            draw.text((50, 30), title, fill='#2c3e50', font=font_large)
            
            # Статус
            draw.text((50, 70), f"Status: 200 OK | Response Time: {response_time:.3f}s", fill='#27ae60', font=font_medium)
            
            # Размер контента
            content_size = len(content.encode('utf-8'))
            draw.text((50, 100), f"Content Size: {content_size:,} bytes", fill='#3498db', font=font_medium)
            
            # Время проверки
            draw.text((50, 130), f"Checked: {datetime.now().strftime('%H:%M:%S')}", fill='#7f8c8d', font=font_medium)
            
            # Превью контента
            draw.rectangle([50, 170, 1150, 750], outline='#bdc3c7', width=2)
            
            # Извлекаем ключевую информацию из HTML
            lines = content.split('\n')
            y_pos = 190
            
            for i, line in enumerate(lines[:30]):  # Показываем первые 30 строк
                if y_pos > 720:
                    break
                    
                # Очищаем HTML теги для превью
                clean_line = line.strip()
                if clean_line.startswith('<title>'):
                    title_text = clean_line.replace('<title>', '').replace('</title>', '')
                    draw.text((60, y_pos), f"Title: {title_text}", fill='#2c3e50', font=font_medium)
                    y_pos += 25
                elif clean_line.startswith('<h1>') or clean_line.startswith('<h2>'):
                    header_text = clean_line.replace('<h1>', '').replace('<h2>', '').replace('</h1>', '').replace('</h2>', '')
                    draw.text((60, y_pos), f"Header: {header_text[:50]}...", fill='#34495e', font=font_small)
                    y_pos += 20
                elif 'class=' in clean_line and ('btn' in clean_line or 'card' in clean_line):
                    draw.text((60, y_pos), f"UI Element: {clean_line[:60]}...", fill='#8e44ad', font=font_small)
                    y_pos += 18
                elif clean_line.startswith('<script>') or clean_line.startswith('function'):
                    draw.text((60, y_pos), f"JS: {clean_line[:60]}...", fill='#e67e22', font=font_small)
                    y_pos += 18
                elif clean_line and not clean_line.startswith('<') and len(clean_line) > 10:
                    draw.text((60, y_pos), f"Content: {clean_line[:60]}...", fill='#7f8c8d', font=font_small)
                    y_pos += 18
            
            # Сохраняем скриншот
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{page_name}_{timestamp}.png"
            filepath = os.path.join(self.screenshots_dir, filename)
            
            img.save(filepath)
            logger.info(f"📸 Скриншот создан: {filepath}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания скриншота: {e}")
            return None
    
    async def generate_visual_report(self):
        """Генерация визуального отчета"""
        try:
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "last_check": self.last_check_time.isoformat() if self.last_check_time else None,
                "pages": self.check_results,
                "summary": self.generate_summary()
            }
            
            # Сохраняем JSON отчет
            report_file = os.path.join(self.reports_dir, f"visual_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            # Создаем HTML отчет
            html_report = await self.create_html_report(report_data)
            html_file = os.path.join(self.reports_dir, f"visual_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_report)
            
            logger.info(f"📊 Визуальный отчет создан: {html_file}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации отчета: {e}")
    
    def generate_summary(self) -> Dict[str, Any]:
        """Генерация сводки"""
        total_pages = len(self.check_results)
        working_pages = len([r for r in self.check_results.values() if r.get('status') == 'ok'])
        error_pages = total_pages - working_pages
        
        avg_response_time = 0
        if working_pages > 0:
            response_times = [r.get('response_time', 0) for r in self.check_results.values() if r.get('status') == 'ok']
            avg_response_time = sum(response_times) / len(response_times)
        
        return {
            "total_pages": total_pages,
            "working_pages": working_pages,
            "error_pages": error_pages,
            "success_rate": (working_pages / total_pages * 100) if total_pages > 0 else 0,
            "avg_response_time": avg_response_time
        }
    
    async def create_html_report(self, report_data: Dict[str, Any]) -> str:
        """Создание HTML отчета"""
        summary = report_data['summary']
        
        html = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JARVIS Visual Monitor Report</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #f8f9fa; margin: 0; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .header h1 {{ color: #2c3e50; font-size: 2.5em; margin-bottom: 10px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric {{ background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .metric-label {{ color: #7f8c8d; margin-top: 5px; }}
        .pages {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .page-card {{ background: #f8f9fa; padding: 20px; border-radius: 10px; }}
        .page-card h3 {{ color: #2c3e50; margin-bottom: 15px; }}
        .status {{ padding: 5px 15px; border-radius: 20px; font-size: 0.9em; font-weight: bold; }}
        .status-ok {{ background: #d5f4e6; color: #27ae60; }}
        .status-error {{ background: #fadbd8; color: #e74c3c; }}
        .screenshot {{ margin-top: 15px; }}
        .screenshot img {{ max-width: 100%; border-radius: 5px; border: 1px solid #ddd; }}
        .timestamp {{ color: #7f8c8d; font-size: 0.9em; margin-top: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>👁️ JARVIS Visual Monitor Report</h1>
            <p>Автоматический отчет о состоянии веб-интерфейса</p>
            <p class="timestamp">Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="summary">
            <div class="metric">
                <div class="metric-value">{summary['total_pages']}</div>
                <div class="metric-label">Всего страниц</div>
            </div>
            <div class="metric">
                <div class="metric-value">{summary['working_pages']}</div>
                <div class="metric-label">Работают</div>
            </div>
            <div class="metric">
                <div class="metric-value">{summary['success_rate']:.1f}%</div>
                <div class="metric-label">Успешность</div>
            </div>
            <div class="metric">
                <div class="metric-value">{summary['avg_response_time']:.3f}s</div>
                <div class="metric-label">Средний отклик</div>
            </div>
        </div>
        
        <div class="pages">
"""
        
        for page_name, result in report_data['pages'].items():
            status_class = 'status-ok' if result.get('status') == 'ok' else 'status-error'
            status_text = '✅ OK' if result.get('status') == 'ok' else '❌ Error'
            
            html += f"""
            <div class="page-card">
                <h3>{page_name.replace('_', ' ').title()}</h3>
                <span class="status {status_class}">{status_text}</span>
                <p><strong>Response Time:</strong> {result.get('response_time', 0):.3f}s</p>
                <p><strong>Size:</strong> {result.get('size', 0):,} bytes</p>
"""
            
            if result.get('screenshot'):
                screenshot_name = os.path.basename(result['screenshot'])
                html += f"""
                <div class="screenshot">
                    <img src="../visual_screenshots/{screenshot_name}" alt="Screenshot of {page_name}">
                </div>
"""
            
            html += f"""
                <p class="timestamp">Проверено: {result.get('timestamp', 'N/A')}</p>
            </div>
"""
        
        html += """
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    def stop_monitoring(self):
        """Остановка мониторинга"""
        self.monitoring_active = False
        logger.info("🛑 Визуальный мониторинг остановлен")

async def main():
    """Основная функция"""
    logging.basicConfig(level=logging.INFO)
    
    monitor = VisualMonitor()
    
    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
        monitor.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
