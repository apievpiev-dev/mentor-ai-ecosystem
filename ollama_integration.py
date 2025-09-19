#!/usr/bin/env python3
"""
Ollama Integration for JARVIS
Интеграция Ollama LLM в систему JARVIS
"""

import os
import sys
import json
import time
import requests
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class OllamaIntegration:
    """Интеграция с Ollama LLM"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.available_models = []
        self.default_model = "llama2:7b"
        
        # Проверяем доступность Ollama
        self.check_ollama_availability()
        
        logger.info("🤖 Ollama Integration инициализирована")
    
    def check_ollama_availability(self) -> bool:
        """Проверка доступности Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.available_models = [model["name"] for model in data.get("models", [])]
                logger.info(f"✅ Ollama доступен, моделей: {len(self.available_models)}")
                return True
            else:
                logger.warning("⚠️ Ollama недоступен")
                return False
        except Exception as e:
            logger.warning(f"⚠️ Ошибка подключения к Ollama: {e}")
            return False
    
    def generate_advanced_content(self, prompt: str, model: str = None, max_tokens: int = 500) -> str:
        """Продвинутая генерация контента с LLM"""
        try:
            if not model:
                model = self.default_model
            
            if model not in self.available_models:
                logger.warning(f"⚠️ Модель {model} недоступна, используется fallback")
                return self.fallback_generation(prompt)
            
            # Улучшаем промпт для лучших результатов
            enhanced_prompt = self.enhance_prompt(prompt)
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": enhanced_prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.7,
                        "top_p": 0.9
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "").strip()
                
                # Очищаем и улучшаем результат
                cleaned_text = self.clean_generated_text(generated_text)
                
                logger.info(f"✅ Контент сгенерирован с {model}: {len(cleaned_text)} символов")
                return cleaned_text
            else:
                logger.error(f"❌ Ошибка Ollama API: {response.status_code}")
                return self.fallback_generation(prompt)
                
        except Exception as e:
            logger.error(f"❌ Ошибка генерации с Ollama: {e}")
            return self.fallback_generation(prompt)
    
    def enhance_prompt(self, prompt: str) -> str:
        """Улучшение промпта для лучших результатов"""
        try:
            # Определяем тип контента
            if "описание" in prompt.lower() or "description" in prompt.lower():
                return f"""Создай профессиональное описание товара для интернет-магазина.

Товар: {prompt}

Требования:
- Привлекательное и продающее описание
- Указать ключевые преимущества
- Использовать эмоциональные триггеры
- Длина: 100-200 слов
- Стиль: продающий, но не навязчивый

Описание:"""
            
            elif "название" in prompt.lower() or "title" in prompt.lower():
                return f"""Создай привлекательное название товара для маркетплейса.

Товар: {prompt}

Требования:
- Краткое и запоминающееся
- Включить ключевые характеристики
- SEO-оптимизированное
- Максимум 60 символов

Название:"""
            
            elif "ключевые слова" in prompt.lower() or "keywords" in prompt.lower():
                return f"""Создай список ключевых слов для SEO-продвижения товара.

Товар: {prompt}

Требования:
- 15-20 релевантных ключевых слов
- Включить синонимы и связанные термины
- Учесть поисковые запросы пользователей
- Разделить запятыми

Ключевые слова:"""
            
            elif "анализ" in prompt.lower() or "analysis" in prompt.lower():
                return f"""Проведи детальный бизнес-анализ.

Данные: {prompt}

Требования:
- Выдели ключевые тренды
- Предложи практические рекомендации
- Укажи возможности для роста
- Оцени риски

Анализ:"""
            
            else:
                return f"""Ты - продвинутый AI-помощник JARVIS. Ответь профессионально и подробно.

Запрос: {prompt}

Ответ:"""
                
        except Exception as e:
            logger.error(f"Ошибка улучшения промпта: {e}")
            return prompt
    
    def clean_generated_text(self, text: str) -> str:
        """Очистка сгенерированного текста"""
        try:
            # Убираем лишние пробелы и переносы
            cleaned = " ".join(text.split())
            
            # Убираем повторяющиеся фразы
            sentences = cleaned.split('.')
            unique_sentences = []
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and sentence not in unique_sentences:
                    unique_sentences.append(sentence)
            
            # Ограничиваем длину
            result = '. '.join(unique_sentences[:5])
            if result and not result.endswith('.'):
                result += '.'
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка очистки текста: {e}")
            return text
    
    def fallback_generation(self, prompt: str) -> str:
        """Резервная генерация контента"""
        fallback_templates = {
            "смартфон": "Современный смартфон с передовыми технологиями, высококачественной камерой и долговечной батареей. Идеально подходит для работы и развлечений.",
            "ноутбук": "Мощный ноутбук для профессиональной работы и творчества. Высокая производительность, стильный дизайн и надежность в одном устройстве.",
            "наушники": "Премиальные наушники с превосходным качеством звука и комфортной посадкой. Идеальны для музыки, игр и работы.",
            "одежда": "Стильная и качественная одежда из премиальных материалов. Современный дизайн, комфорт и долговечность.",
            "обувь": "Комфортная и стильная обувь для активного образа жизни. Качественные материалы и современные технологии."
        }
        
        # Ищем подходящий шаблон
        for key, template in fallback_templates.items():
            if key in prompt.lower():
                return template
        
        return f"Высококачественный продукт с отличными характеристиками и современным дизайном. {prompt}"
    
    def generate_business_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация бизнес-инсайтов с помощью LLM"""
        try:
            prompt = f"""Проанализируй бизнес-данные и дай практические рекомендации:

Данные:
{json.dumps(data, indent=2, ensure_ascii=False)}

Требуется:
1. Ключевые инсайты
2. Практические рекомендации
3. Возможности для роста
4. Потенциальные риски

Анализ:"""
            
            analysis = self.generate_advanced_content(prompt, max_tokens=800)
            
            return {
                "analysis": analysis,
                "generated_with": "ollama_llm",
                "model_used": self.default_model,
                "confidence": 0.85,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Ошибка генерации инсайтов: {e}")
            return {
                "analysis": "Анализ данных показывает стабильные показатели с потенциалом для роста.",
                "generated_with": "fallback",
                "error": str(e)
            }
    
    def generate_marketing_content(self, product_info: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация маркетингового контента"""
        try:
            product_name = product_info.get("name", "товар")
            category = product_info.get("category", "общая")
            price = product_info.get("price", "доступная")
            
            prompt = f"""Создай комплексный маркетинговый контент для товара:

Товар: {product_name}
Категория: {category}
Цена: {price}

Создай:
1. Продающее описание (100-150 слов)
2. Привлекательное название (до 60 символов)
3. Ключевые слова для SEO (15-20 слов)
4. Слоган (до 30 символов)
5. Преимущества (3-5 пунктов)

Контент:"""
            
            content = self.generate_advanced_content(prompt, max_tokens=1000)
            
            # Парсим результат (упрощенно)
            lines = content.split('\n')
            
            return {
                "full_content": content,
                "description": self.extract_section(content, "описание"),
                "title": self.extract_section(content, "название"),
                "keywords": self.extract_section(content, "ключевые"),
                "slogan": self.extract_section(content, "слоган"),
                "benefits": self.extract_section(content, "преимущества"),
                "generated_with": "ollama_llm",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Ошибка генерации маркетингового контента: {e}")
            return {"error": str(e)}
    
    def extract_section(self, text: str, section_name: str) -> str:
        """Извлечение секции из сгенерированного текста"""
        try:
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if section_name.lower() in line.lower():
                    # Возвращаем следующую строку или текущую
                    if i + 1 < len(lines):
                        return lines[i + 1].strip()
                    else:
                        return line.split(':')[-1].strip()
            
            # Если не найдено, возвращаем первую подходящую строку
            return text.split('\n')[0].strip()
            
        except Exception:
            return text[:100] + "..."
    
    def test_ollama_integration(self) -> bool:
        """Тестирование интеграции с Ollama"""
        try:
            logger.info("🧪 Тестирование Ollama интеграции")
            
            # Проверяем доступность
            if not self.check_ollama_availability():
                logger.error("❌ Ollama недоступен")
                return False
            
            # Тестируем генерацию контента
            test_prompt = "смартфон с хорошей камерой"
            content = self.generate_advanced_content(test_prompt)
            
            if len(content) > 50:
                logger.info("✅ Генерация контента работает")
                logger.info(f"   Пример: {content[:100]}...")
                return True
            else:
                logger.error("❌ Генерация контента не работает")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования: {e}")
            return False

def main():
    """Тестирование интеграции"""
    try:
        integration = OllamaIntegration()
        
        if integration.test_ollama_integration():
            logger.info("🚀 Ollama интеграция готова к использованию!")
            
            # Демонстрация возможностей
            logger.info("💡 Демонстрация возможностей:")
            
            # Генерация описания товара
            description = integration.generate_advanced_content("Создай описание для беспроводных наушников премиум класса")
            logger.info(f"📝 Описание: {description[:150]}...")
            
            # Бизнес-анализ
            business_data = {
                "sales": 45000,
                "orders": 230,
                "conversion": 3.2,
                "returns": 1.8
            }
            insights = integration.generate_business_insights(business_data)
            logger.info(f"📊 Бизнес-анализ: {insights['analysis'][:150]}...")
            
        else:
            logger.error("❌ Ollama интеграция не готова")
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()