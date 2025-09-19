#!/usr/bin/env python3
"""
Enhanced Visual Analyzer for JARVIS
Улучшенный визуальный анализатор с реальным анализом HTML/CSS
"""

import os
import sys
import json
import time
import re
import subprocess
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import base64
from urllib.parse import urljoin, urlparse
import threading

logger = logging.getLogger(__name__)

@dataclass
class EnhancedVisualAnalysis:
    """Улучшенный результат визуального анализа"""
    timestamp: str
    url: str
    html_content: str
    page_title: str
    elements_analysis: Dict[str, Any]
    css_analysis: Dict[str, Any]
    javascript_analysis: Dict[str, Any]
    accessibility_score: float
    performance_score: float
    seo_score: float
    ui_issues: List[Dict[str, Any]]
    suggestions: List[str]
    confidence: float

class EnhancedVisualAnalyzer:
    """Улучшенный визуальный анализатор"""
    
    def __init__(self, target_url: str = "http://localhost:8080"):
        self.target_url = target_url
        self.analysis_history = []
        self.enabled = True
        self.last_analysis = None
        
        logger.info("🔍 Enhanced Visual Analyzer инициализирован")
    
    def fetch_page_content(self) -> Optional[Dict[str, Any]]:
        """Получение содержимого страницы"""
        try:
            # Получаем HTML
            html_result = subprocess.run([
                'curl', '-s', '-L', '--max-time', '10', 
                '-H', 'User-Agent: JARVIS-Visual-Analyzer/1.0',
                self.target_url
            ], capture_output=True, text=True, timeout=15)
            
            if html_result.returncode != 0:
                logger.warning(f"⚠️ Ошибка получения HTML: {html_result.stderr}")
                return None
            
            html_content = html_result.stdout
            
            # Получаем заголовки HTTP
            headers_result = subprocess.run([
                'curl', '-s', '-I', '--max-time', '5', self.target_url
            ], capture_output=True, text=True, timeout=10)
            
            headers = headers_result.stdout if headers_result.returncode == 0 else ""
            
            # Измеряем время отклика
            time_result = subprocess.run([
                'curl', '-s', '-o', '/dev/null', '-w', '%{time_total}', 
                '--max-time', '10', self.target_url
            ], capture_output=True, text=True, timeout=15)
            
            response_time = float(time_result.stdout) if time_result.returncode == 0 else 1.0
            
            return {
                "html_content": html_content,
                "headers": headers,
                "response_time": response_time,
                "content_length": len(html_content)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения содержимого: {e}")
            return None
    
    def analyze_html_structure(self, html_content: str) -> Dict[str, Any]:
        """Анализ HTML структуры"""
        try:
            analysis = {
                "total_elements": 0,
                "semantic_elements": 0,
                "interactive_elements": 0,
                "form_elements": 0,
                "media_elements": 0,
                "accessibility_features": 0,
                "structure_score": 0.0
            }
            
            # Подсчитываем различные типы элементов
            semantic_tags = ['header', 'nav', 'main', 'section', 'article', 'aside', 'footer']
            interactive_tags = ['button', 'input', 'select', 'textarea', 'a']
            form_tags = ['form', 'input', 'select', 'textarea', 'label']
            media_tags = ['img', 'video', 'audio', 'canvas', 'svg']
            
            # Считаем общее количество элементов
            total_tags = len(re.findall(r'<\w+', html_content))
            analysis["total_elements"] = total_tags
            
            # Семантические элементы
            for tag in semantic_tags:
                count = len(re.findall(f'<{tag}[^>]*>', html_content, re.IGNORECASE))
                analysis["semantic_elements"] += count
            
            # Интерактивные элементы
            for tag in interactive_tags:
                count = len(re.findall(f'<{tag}[^>]*>', html_content, re.IGNORECASE))
                analysis["interactive_elements"] += count
            
            # Элементы форм
            for tag in form_tags:
                count = len(re.findall(f'<{tag}[^>]*>', html_content, re.IGNORECASE))
                analysis["form_elements"] += count
            
            # Медиа элементы
            for tag in media_tags:
                count = len(re.findall(f'<{tag}[^>]*>', html_content, re.IGNORECASE))
                analysis["media_elements"] += count
            
            # Проверяем доступность
            accessibility_features = 0
            if 'alt=' in html_content:
                accessibility_features += 1
            if 'aria-' in html_content:
                accessibility_features += 1
            if 'role=' in html_content:
                accessibility_features += 1
            if '<label' in html_content.lower():
                accessibility_features += 1
            
            analysis["accessibility_features"] = accessibility_features
            
            # Рассчитываем оценку структуры
            if total_tags > 0:
                semantic_ratio = analysis["semantic_elements"] / total_tags
                interactive_ratio = analysis["interactive_elements"] / total_tags
                accessibility_ratio = accessibility_features / 4  # Максимум 4 функции
                
                analysis["structure_score"] = (semantic_ratio * 0.4 + 
                                             interactive_ratio * 0.4 + 
                                             accessibility_ratio * 0.2)
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Ошибка анализа HTML: {e}")
            return {"total_elements": 0, "structure_score": 0.0}
    
    def analyze_css_styles(self, html_content: str) -> Dict[str, Any]:
        """Анализ CSS стилей"""
        try:
            analysis = {
                "has_external_css": False,
                "has_inline_styles": False,
                "responsive_design": False,
                "modern_css_features": 0,
                "css_score": 0.0
            }
            
            # Проверяем наличие CSS
            analysis["has_external_css"] = '<link' in html_content and 'stylesheet' in html_content
            analysis["has_inline_styles"] = '<style' in html_content
            
            # Проверяем адаптивный дизайн
            analysis["responsive_design"] = (
                'viewport' in html_content and 
                ('media' in html_content or '@media' in html_content)
            )
            
            # Проверяем современные CSS функции
            modern_features = 0
            css_features = [
                'grid', 'flexbox', 'flex', 'transform', 'transition',
                'border-radius', 'box-shadow', 'gradient', 'backdrop-filter'
            ]
            
            for feature in css_features:
                if feature in html_content.lower():
                    modern_features += 1
            
            analysis["modern_css_features"] = modern_features
            
            # Рассчитываем CSS оценку
            css_score = 0.0
            if analysis["has_external_css"] or analysis["has_inline_styles"]:
                css_score += 0.3
            if analysis["responsive_design"]:
                css_score += 0.4
            css_score += min(0.3, modern_features / len(css_features) * 0.3)
            
            analysis["css_score"] = css_score
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Ошибка анализа CSS: {e}")
            return {"css_score": 0.0}
    
    def analyze_javascript(self, html_content: str) -> Dict[str, Any]:
        """Анализ JavaScript"""
        try:
            analysis = {
                "has_external_js": False,
                "has_inline_js": False,
                "modern_js_features": 0,
                "framework_detected": None,
                "js_score": 0.0
            }
            
            # Проверяем наличие JavaScript
            analysis["has_external_js"] = '<script src=' in html_content
            analysis["has_inline_js"] = '<script>' in html_content or '<script type=' in html_content
            
            # Проверяем современные JS функции
            modern_features = 0
            js_features = [
                'async', 'await', 'fetch', 'const', 'let', 'arrow function',
                'addEventListener', 'querySelector', 'JSON.parse'
            ]
            
            for feature in js_features:
                if feature in html_content or (feature == 'arrow function' and '=>' in html_content):
                    modern_features += 1
            
            analysis["modern_js_features"] = modern_features
            
            # Определяем фреймворки
            if 'chart.js' in html_content.lower():
                analysis["framework_detected"] = "Chart.js"
            elif 'react' in html_content.lower():
                analysis["framework_detected"] = "React"
            elif 'vue' in html_content.lower():
                analysis["framework_detected"] = "Vue.js"
            
            # Рассчитываем JS оценку
            js_score = 0.0
            if analysis["has_external_js"] or analysis["has_inline_js"]:
                js_score += 0.4
            js_score += min(0.4, modern_features / len(js_features) * 0.4)
            if analysis["framework_detected"]:
                js_score += 0.2
            
            analysis["js_score"] = js_score
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Ошибка анализа JavaScript: {e}")
            return {"js_score": 0.0}
    
    def calculate_accessibility_score(self, html_content: str, elements_analysis: Dict[str, Any]) -> float:
        """Расчет оценки доступности"""
        try:
            score = 0.0
            max_score = 10.0
            
            # Проверяем lang атрибут
            if 'lang=' in html_content:
                score += 1.0
            
            # Проверяем alt теги для изображений
            img_count = html_content.count('<img')
            alt_count = html_content.count('alt=')
            if img_count > 0 and alt_count >= img_count * 0.8:
                score += 2.0
            elif alt_count > 0:
                score += 1.0
            
            # Проверяем ARIA атрибуты
            if 'aria-' in html_content:
                score += 1.5
            
            # Проверяем role атрибуты
            if 'role=' in html_content:
                score += 1.0
            
            # Проверяем label для форм
            form_elements = elements_analysis.get("form_elements", 0)
            label_count = html_content.count('<label')
            if form_elements > 0 and label_count >= form_elements * 0.5:
                score += 1.5
            
            # Проверяем заголовки
            h1_count = html_content.count('<h1')
            h2_count = html_content.count('<h2')
            h3_count = html_content.count('<h3')
            if h1_count >= 1 and (h2_count > 0 or h3_count > 0):
                score += 1.0
            
            # Проверяем контрастность (упрощенно)
            if 'color:' in html_content and 'background' in html_content:
                score += 1.0
            
            # Проверяем навигацию с клавиатуры
            if 'tabindex' in html_content or 'focus' in html_content:
                score += 1.0
            
            return min(1.0, score / max_score)
            
        except Exception as e:
            logger.error(f"❌ Ошибка расчета доступности: {e}")
            return 0.5
    
    def calculate_seo_score(self, html_content: str) -> float:
        """Расчет SEO оценки"""
        try:
            score = 0.0
            max_score = 8.0
            
            # Проверяем title
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
            if title_match and len(title_match.group(1).strip()) > 10:
                score += 2.0
            elif title_match:
                score += 1.0
            
            # Проверяем meta description
            if 'meta name="description"' in html_content.lower():
                score += 1.5
            
            # Проверяем meta keywords
            if 'meta name="keywords"' in html_content.lower():
                score += 0.5
            
            # Проверяем заголовки H1-H3
            if '<h1' in html_content.lower():
                score += 1.0
            if '<h2' in html_content.lower():
                score += 0.5
            if '<h3' in html_content.lower():
                score += 0.5
            
            # Проверяем структурированные данные
            if 'schema.org' in html_content or 'application/ld+json' in html_content:
                score += 1.0
            
            # Проверяем Open Graph
            if 'og:' in html_content:
                score += 1.0
            
            return min(1.0, score / max_score)
            
        except Exception as e:
            logger.error(f"❌ Ошибка расчета SEO: {e}")
            return 0.5
    
    def detect_ui_issues(self, html_analysis: Dict[str, Any], css_analysis: Dict[str, Any], 
                        js_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Обнаружение проблем UI"""
        issues = []
        
        try:
            # Проблемы HTML структуры
            if html_analysis.get("total_elements", 0) < 10:
                issues.append({
                    "type": "insufficient_content",
                    "severity": "medium",
                    "description": "Мало HTML элементов на странице",
                    "recommendation": "Добавить больше контента и элементов"
                })
            
            if html_analysis.get("interactive_elements", 0) < 3:
                issues.append({
                    "type": "low_interactivity",
                    "severity": "high",
                    "description": "Недостаточно интерактивных элементов",
                    "recommendation": "Добавить больше кнопок, ссылок и элементов управления"
                })
            
            # Проблемы CSS
            if not css_analysis.get("responsive_design", False):
                issues.append({
                    "type": "no_responsive_design",
                    "severity": "high",
                    "description": "Отсутствует адаптивный дизайн",
                    "recommendation": "Добавить CSS медиа-запросы для мобильных устройств"
                })
            
            if css_analysis.get("modern_css_features", 0) < 3:
                issues.append({
                    "type": "outdated_css",
                    "severity": "medium",
                    "description": "Используются устаревшие CSS техники",
                    "recommendation": "Обновить CSS с современными функциями (Grid, Flexbox, etc.)"
                })
            
            # Проблемы JavaScript
            if not js_analysis.get("has_external_js", False) and not js_analysis.get("has_inline_js", False):
                issues.append({
                    "type": "no_javascript",
                    "severity": "medium",
                    "description": "Отсутствует JavaScript функциональность",
                    "recommendation": "Добавить интерактивность с помощью JavaScript"
                })
            
            if js_analysis.get("modern_js_features", 0) < 4:
                issues.append({
                    "type": "outdated_javascript",
                    "severity": "low",
                    "description": "Используется устаревший JavaScript",
                    "recommendation": "Обновить JavaScript код с современными функциями"
                })
            
        except Exception as e:
            logger.error(f"❌ Ошибка обнаружения проблем: {e}")
        
        return issues
    
    def generate_actionable_suggestions(self, issues: List[Dict[str, Any]], 
                                      html_analysis: Dict[str, Any]) -> List[str]:
        """Генерация практических предложений"""
        suggestions = []
        
        try:
            # Предложения на основе проблем
            for issue in issues:
                if issue["severity"] == "high":
                    suggestions.append(f"🚨 КРИТИЧНО: {issue['recommendation']}")
                elif issue["severity"] == "medium":
                    suggestions.append(f"⚠️ ВАЖНО: {issue['recommendation']}")
                else:
                    suggestions.append(f"💡 Рекомендация: {issue['recommendation']}")
            
            # Дополнительные предложения
            interactive_count = html_analysis.get("interactive_elements", 0)
            
            if interactive_count > 10:
                suggestions.append("🗂️ Группировать элементы управления для лучшей навигации")
            elif interactive_count < 5:
                suggestions.append("➕ Добавить больше интерактивных элементов")
            
            # Предложения по производительности
            total_elements = html_analysis.get("total_elements", 0)
            if total_elements > 100:
                suggestions.append("⚡ Оптимизировать DOM - слишком много элементов")
            
            # Предложения по UX
            suggestions.extend([
                "🎨 Добавить анимации для улучшения пользовательского опыта",
                "📊 Реализовать прогрессивную загрузку для больших данных",
                "🔔 Добавить уведомления о статусе операций",
                "⌨️ Улучшить поддержку навигации с клавиатуры",
                "🌙 Добавить переключение темной/светлой темы"
            ])
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации предложений: {e}")
        
        return suggestions[:8]  # Ограничиваем количество
    
    def perform_enhanced_analysis(self) -> Optional[EnhancedVisualAnalysis]:
        """Выполнение улучшенного анализа"""
        try:
            logger.info(f"🔍 Начало анализа: {self.target_url}")
            
            # Получаем содержимое страницы
            content_data = self.fetch_page_content()
            
            if not content_data:
                logger.warning("⚠️ Не удалось получить содержимое страницы")
                return None
            
            html_content = content_data["html_content"]
            
            # Извлекаем заголовок страницы
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
            page_title = title_match.group(1).strip() if title_match else "Без заголовка"
            
            # Выполняем различные виды анализа
            html_analysis = self.analyze_html_structure(html_content)
            css_analysis = self.analyze_css_styles(html_content)
            js_analysis = self.analyze_javascript(html_content)
            
            # Рассчитываем оценки
            accessibility_score = self.calculate_accessibility_score(html_content, html_analysis)
            seo_score = self.calculate_seo_score(html_content)
            
            # Рассчитываем производительность
            performance_score = self.calculate_performance_score(content_data, html_analysis)
            
            # Обнаруживаем проблемы
            ui_issues = self.detect_ui_issues(html_analysis, css_analysis, js_analysis)
            
            # Генерируем предложения
            suggestions = self.generate_actionable_suggestions(ui_issues, html_analysis)
            
            # Рассчитываем уверенность
            confidence = self.calculate_analysis_confidence(html_analysis, css_analysis, js_analysis)
            
            analysis = EnhancedVisualAnalysis(
                timestamp=datetime.now().isoformat(),
                url=self.target_url,
                html_content=html_content[:1000] + "..." if len(html_content) > 1000 else html_content,
                page_title=page_title,
                elements_analysis=html_analysis,
                css_analysis=css_analysis,
                javascript_analysis=js_analysis,
                accessibility_score=accessibility_score,
                performance_score=performance_score,
                seo_score=seo_score,
                ui_issues=ui_issues,
                suggestions=suggestions,
                confidence=confidence
            )
            
            self.last_analysis = analysis
            self.analysis_history.append(analysis)
            
            # Ограничиваем историю
            if len(self.analysis_history) > 50:
                self.analysis_history = self.analysis_history[-25:]
            
            logger.info(f"✅ Улучшенный анализ завершен: "
                       f"Элементы: {html_analysis.get('total_elements', 0)}, "
                       f"Проблемы: {len(ui_issues)}, "
                       f"Доступность: {accessibility_score:.2f}, "
                       f"Производительность: {performance_score:.2f}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Ошибка улучшенного анализа: {e}")
            return None
    
    def calculate_performance_score(self, content_data: Dict[str, Any], html_analysis: Dict[str, Any]) -> float:
        """Расчет оценки производительности"""
        try:
            score = 1.0
            
            # Время отклика
            response_time = content_data.get("response_time", 1.0)
            if response_time > 2.0:
                score -= 0.3
            elif response_time > 1.0:
                score -= 0.1
            
            # Размер контента
            content_length = content_data.get("content_length", 0)
            if content_length > 100000:  # Больше 100KB
                score -= 0.2
            elif content_length > 50000:  # Больше 50KB
                score -= 0.1
            
            # Количество элементов
            total_elements = html_analysis.get("total_elements", 0)
            if total_elements > 200:
                score -= 0.2
            elif total_elements > 100:
                score -= 0.1
            
            return max(0.0, score)
            
        except Exception as e:
            logger.error(f"❌ Ошибка расчета производительности: {e}")
            return 0.7
    
    def calculate_analysis_confidence(self, html_analysis: Dict[str, Any], 
                                    css_analysis: Dict[str, Any], js_analysis: Dict[str, Any]) -> float:
        """Расчет уверенности анализа"""
        try:
            confidence = 0.6  # Базовая уверенность
            
            # Увеличиваем за успешный анализ HTML
            if html_analysis.get("total_elements", 0) > 0:
                confidence += 0.2
            
            # Увеличиваем за анализ CSS
            if css_analysis.get("css_score", 0) > 0:
                confidence += 0.1
            
            # Увеличиваем за анализ JavaScript
            if js_analysis.get("js_score", 0) > 0:
                confidence += 0.1
            
            return min(1.0, confidence)
            
        except Exception:
            return 0.7
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Получение сводки анализов"""
        try:
            if not self.analysis_history:
                return {"total_analyses": 0, "status": "no_data"}
            
            latest = self.analysis_history[-1]
            
            return {
                "total_analyses": len(self.analysis_history),
                "latest_analysis": {
                    "timestamp": latest.timestamp,
                    "page_title": latest.page_title,
                    "elements_count": latest.elements_analysis.get("total_elements", 0),
                    "interactive_elements": latest.elements_analysis.get("interactive_elements", 0),
                    "accessibility_score": latest.accessibility_score,
                    "performance_score": latest.performance_score,
                    "seo_score": latest.seo_score,
                    "issues_count": len(latest.ui_issues),
                    "suggestions_count": len(latest.suggestions),
                    "confidence": latest.confidence
                },
                "trends": {
                    "avg_accessibility": sum(a.accessibility_score for a in self.analysis_history) / len(self.analysis_history),
                    "avg_performance": sum(a.performance_score for a in self.analysis_history) / len(self.analysis_history),
                    "avg_issues": sum(len(a.ui_issues) for a in self.analysis_history) / len(self.analysis_history)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения сводки: {e}")
            return {"error": str(e)}
    
    def start_continuous_analysis(self, interval: int = 30):
        """Запуск непрерывного анализа"""
        def analysis_loop():
            while self.enabled:
                try:
                    analysis = self.perform_enhanced_analysis()
                    if analysis:
                        # Проверяем критические проблемы
                        critical_issues = [i for i in analysis.ui_issues if i.get("severity") == "high"]
                        if critical_issues:
                            logger.warning(f"🚨 Обнаружены критические проблемы UI: {len(critical_issues)}")
                            for issue in critical_issues:
                                logger.warning(f"  - {issue['description']}")
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка в цикле анализа: {e}")
                    time.sleep(interval * 2)
        
        thread = threading.Thread(target=analysis_loop, daemon=True)
        thread.start()
        logger.info(f"🔄 Непрерывный анализ запущен (интервал: {interval}с)")

def test_enhanced_analyzer():
    """Тестирование улучшенного анализатора"""
    try:
        logger.info("🧪 Тестирование Enhanced Visual Analyzer")
        
        # Создаем анализатор
        analyzer = EnhancedVisualAnalyzer()
        
        # Выполняем анализ
        analysis = analyzer.perform_enhanced_analysis()
        
        if analysis:
            logger.info("✅ Улучшенный анализ выполнен")
            logger.info(f"  📄 Страница: {analysis.page_title}")
            logger.info(f"  🔢 Элементов: {analysis.elements_analysis.get('total_elements', 0)}")
            logger.info(f"  🖱️ Интерактивных: {analysis.elements_analysis.get('interactive_elements', 0)}")
            logger.info(f"  ♿ Доступность: {analysis.accessibility_score:.2f}")
            logger.info(f"  ⚡ Производительность: {analysis.performance_score:.2f}")
            logger.info(f"  🔍 SEO: {analysis.seo_score:.2f}")
            logger.info(f"  🚨 Проблем: {len(analysis.ui_issues)}")
            logger.info(f"  💡 Предложений: {len(analysis.suggestions)}")
            logger.info(f"  🎯 Уверенность: {analysis.confidence:.2f}")
            
            # Показываем критические проблемы
            critical_issues = [i for i in analysis.ui_issues if i.get("severity") == "high"]
            if critical_issues:
                logger.warning("🚨 Критические проблемы:")
                for issue in critical_issues:
                    logger.warning(f"  - {issue['description']}")
            
            # Показываем топ предложения
            logger.info("💡 Топ предложения:")
            for suggestion in analysis.suggestions[:3]:
                logger.info(f"  - {suggestion}")
            
            return True
        else:
            logger.error("❌ Анализ не выполнен")
            return False
            
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_enhanced_analyzer()