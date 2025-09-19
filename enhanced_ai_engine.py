#!/usr/bin/env python3
"""
Enhanced AI Engine - Улучшенный движок для работы с нейросетями
Интегрирует все провайдеры, визуальную верификацию и автономную работу
"""

import asyncio
import json
import logging
import time
import base64
import io
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import aiohttp
import requests
from pathlib import Path
import subprocess
import os
import sys

# Добавляем путь к ai_manager
sys.path.append('/workspace/ai_manager')

try:
    from ai_providers.provider_manager import AIProviderManager
    from ai_providers.ollama_provider import OllamaProvider
    from ai_providers.huggingface_provider import HuggingFaceProvider
    from ai_providers.local_provider import LocalProvider
except ImportError:
    print("⚠️ AI Manager провайдеры не найдены, используем базовую реализацию")

logger = logging.getLogger(__name__)

@dataclass
class AIResponse:
    """Улучшенный ответ от AI модели"""
    content: str
    model: str
    provider: str
    tokens_used: int = 0
    response_time: float = 0.0
    success: bool = True
    error: Optional[str] = None
    visual_verified: bool = False
    quality_score: float = 0.0
    metadata: Dict[str, Any] = None

@dataclass
class VisualVerification:
    """Результат визуальной верификации"""
    verified: bool
    confidence: float
    issues: List[str]
    suggestions: List[str]
    screenshot_path: Optional[str] = None

class VisualIntelligence:
    """Система визуальной верификации результатов"""
    
    def __init__(self):
        self.screenshots_dir = Path("/workspace/visual_screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        self.verification_history = []
    
    async def verify_code_result(self, code: str, expected_output: str = None) -> VisualVerification:
        """Верификация результата генерации кода"""
        try:
            # Сохраняем код во временный файл
            temp_file = Path("/tmp/test_code.py")
            temp_file.write_text(code)
            
            # Выполняем код и проверяем результат
            result = subprocess.run([sys.executable, str(temp_file)], 
                                  capture_output=True, text=True, timeout=10)
            
            issues = []
            suggestions = []
            confidence = 1.0
            
            if result.returncode != 0:
                issues.append(f"Код содержит ошибки: {result.stderr}")
                confidence = 0.0
                suggestions.append("Исправить синтаксические ошибки")
            else:
                if expected_output and expected_output not in result.stdout:
                    issues.append("Результат не соответствует ожиданиям")
                    confidence = 0.5
                    suggestions.append("Проверить логику кода")
            
            # Создаем скриншот (если это веб-приложение)
            screenshot_path = None
            if "flask" in code.lower() or "fastapi" in code.lower() or "streamlit" in code.lower():
                screenshot_path = await self._capture_web_screenshot(code)
            
            return VisualVerification(
                verified=len(issues) == 0,
                confidence=confidence,
                issues=issues,
                suggestions=suggestions,
                screenshot_path=screenshot_path
            )
            
        except Exception as e:
            logger.error(f"Ошибка визуальной верификации: {e}")
            return VisualVerification(
                verified=False,
                confidence=0.0,
                issues=[f"Ошибка верификации: {str(e)}"],
                suggestions=["Проверить код вручную"]
            )
    
    async def _capture_web_screenshot(self, code: str) -> Optional[str]:
        """Создание скриншота веб-приложения"""
        try:
            # Простая реализация - в реальности можно использовать Selenium
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = self.screenshots_dir / f"web_app_{timestamp}.png"
            
            # Создаем заглушку скриншота
            screenshot_path.write_bytes(b"")
            
            return str(screenshot_path)
        except Exception as e:
            logger.error(f"Ошибка создания скриншота: {e}")
            return None
    
    async def verify_text_result(self, text: str, context: str = None) -> VisualVerification:
        """Верификация текстового результата"""
        issues = []
        suggestions = []
        confidence = 1.0
        
        # Проверяем качество текста
        if len(text.strip()) < 10:
            issues.append("Текст слишком короткий")
            confidence = 0.3
            suggestions.append("Расширить ответ")
        
        if not text.strip():
            issues.append("Пустой ответ")
            confidence = 0.0
            suggestions.append("Повторить запрос")
        
        # Проверяем на наличие ошибок
        if "ошибка" in text.lower() or "error" in text.lower():
            issues.append("Ответ содержит упоминание об ошибке")
            confidence = 0.5
            suggestions.append("Проверить корректность ответа")
        
        return VisualVerification(
            verified=len(issues) == 0,
            confidence=confidence,
            issues=issues,
            suggestions=suggestions
        )

class EnhancedAIEngine:
    """Улучшенный AI движок с поддержкой всех провайдеров"""
    
    def __init__(self):
        self.provider_manager = None
        self.visual_intelligence = VisualIntelligence()
        self.response_cache = {}
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "average_response_time": 0.0,
            "cache_hits": 0
        }
        self.initialized = False
        
    async def initialize(self):
        """Инициализация движка"""
        if self.initialized:
            return
        
        try:
            # Инициализируем провайдеры
            self.provider_manager = AIProviderManager()
            await self.provider_manager.initialize_providers({
                "ollama_model": "llama2:7b",
                "hf_model": "microsoft/DialoGPT-medium",
                "hf_token": os.getenv("HUGGINGFACE_TOKEN")
            })
            
            self.initialized = True
            logger.info("✅ Enhanced AI Engine инициализирован")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации Enhanced AI Engine: {e}")
            # Создаем fallback провайдер
            self._create_fallback_providers()
    
    def _create_fallback_providers(self):
        """Создание fallback провайдеров"""
        try:
            from ai_providers.local_provider import LocalProvider
            self.provider_manager = AIProviderManager()
            self.provider_manager.providers["local"] = LocalProvider("fallback")
            self.provider_manager.default_provider = self.provider_manager.providers["local"]
            self.initialized = True
            logger.info("✅ Fallback провайдеры созданы")
        except Exception as e:
            logger.error(f"❌ Ошибка создания fallback провайдеров: {e}")
    
    async def generate_response(self, prompt: str, 
                              system_prompt: str = None,
                              provider: str = None,
                              enable_visual_verification: bool = True,
                              **kwargs) -> AIResponse:
        """Генерация ответа с визуальной верификацией"""
        
        if not self.initialized:
            await self.initialize()
        
        start_time = time.time()
        self.performance_metrics["total_requests"] += 1
        
        # Проверяем кэш
        cache_key = self._generate_cache_key(prompt, provider, kwargs)
        if cache_key in self.response_cache:
            self.performance_metrics["cache_hits"] += 1
            cached_response = self.response_cache[cache_key]
            cached_response.response_time = 0.01
            return cached_response
        
        try:
            # Генерируем ответ через провайдер
            if self.provider_manager:
                result = await self.provider_manager.generate_response(
                    prompt, provider_name=provider, **kwargs
                )
            else:
                result = {"success": False, "error": "No providers available"}
            
            response_time = time.time() - start_time
            
            if result.get("success"):
                content = result.get("result", "")
                model = result.get("model", "unknown")
                provider_name = result.get("provider", "unknown")
                
                # Визуальная верификация
                visual_verification = None
                if enable_visual_verification:
                    if self._is_code_prompt(prompt):
                        visual_verification = await self.visual_intelligence.verify_code_result(content)
                    else:
                        visual_verification = await self.visual_intelligence.verify_text_result(content, prompt)
                
                # Создаем ответ
                ai_response = AIResponse(
                    content=content,
                    model=model,
                    provider=provider_name,
                    response_time=response_time,
                    success=True,
                    visual_verified=visual_verification.verified if visual_verification else False,
                    quality_score=visual_verification.confidence if visual_verification else 1.0,
                    metadata={
                        "visual_verification": asdict(visual_verification) if visual_verification else None,
                        "cache_key": cache_key
                    }
                )
                
                # Сохраняем в кэш
                self.response_cache[cache_key] = ai_response
                self.performance_metrics["successful_requests"] += 1
                
                return ai_response
            else:
                return AIResponse(
                    content="",
                    model="unknown",
                    provider="unknown",
                    response_time=response_time,
                    success=False,
                    error=result.get("error", "Unknown error")
                )
                
        except Exception as e:
            logger.error(f"❌ Ошибка генерации ответа: {e}")
            return AIResponse(
                content="",
                model="unknown",
                provider="unknown",
                response_time=time.time() - start_time,
                success=False,
                error=str(e)
            )
    
    def _generate_cache_key(self, prompt: str, provider: str, kwargs: Dict) -> str:
        """Генерация ключа кэша"""
        key_data = {
            "prompt": prompt[:100],
            "provider": provider,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000)
        }
        return base64.b64encode(json.dumps(key_data, sort_keys=True).encode()).decode()[:50]
    
    def _is_code_prompt(self, prompt: str) -> bool:
        """Определение, является ли промпт запросом на генерацию кода"""
        code_keywords = ["код", "code", "функция", "function", "класс", "class", 
                        "программа", "program", "скрипт", "script", "алгоритм", "algorithm"]
        return any(keyword in prompt.lower() for keyword in code_keywords)
    
    async def get_available_models(self) -> Dict[str, List[str]]:
        """Получение списка доступных моделей"""
        if not self.initialized:
            await self.initialize()
        
        models = {}
        if self.provider_manager:
            for name, provider in self.provider_manager.providers.items():
                if hasattr(provider, 'get_supported_models'):
                    models[name] = provider.get_supported_models()
        
        return models
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Получение статуса системы"""
        if not self.initialized:
            await self.initialize()
        
        status = {
            "initialized": self.initialized,
            "providers": {},
            "performance": self.performance_metrics.copy(),
            "cache_size": len(self.response_cache)
        }
        
        if self.provider_manager:
            status["providers"] = await self.provider_manager.get_provider_health()
        
        return status
    
    async def optimize_performance(self):
        """Оптимизация производительности"""
        # Очистка старых записей кэша
        if len(self.response_cache) > 1000:
            # Оставляем только последние 500 записей
            cache_items = list(self.response_cache.items())
            self.response_cache = dict(cache_items[-500:])
            logger.info("🧹 Кэш оптимизирован")
        
        # Обновление метрик производительности
        if self.performance_metrics["total_requests"] > 0:
            success_rate = self.performance_metrics["successful_requests"] / self.performance_metrics["total_requests"]
            cache_hit_rate = self.performance_metrics["cache_hits"] / self.performance_metrics["total_requests"]
            
            logger.info(f"📊 Производительность: успешность {success_rate:.2%}, кэш {cache_hit_rate:.2%}")

# Глобальный экземпляр улучшенного движка
enhanced_ai_engine = EnhancedAIEngine()

# Удобные функции для использования
async def generate_ai_response(prompt: str, system_prompt: str = None, **kwargs) -> str:
    """Простая функция для генерации ответа"""
    response = await enhanced_ai_engine.generate_response(prompt, system_prompt, **kwargs)
    return response.content if response.success else f"Ошибка: {response.error}"

async def generate_code(prompt: str, language: str = "python") -> str:
    """Генерация кода с визуальной верификацией"""
    system_prompt = f"""Ты эксперт-программист. Создавай качественный, рабочий код на {language}.
    Отвечай только кодом без объяснений, если не просят иначе.
    Код должен быть готов к выполнению."""
    
    response = await enhanced_ai_engine.generate_response(
        prompt, 
        system_prompt=system_prompt,
        enable_visual_verification=True
    )
    
    if response.success and response.visual_verified:
        return response.content
    elif response.success:
        logger.warning(f"⚠️ Код сгенерирован, но есть проблемы: {response.metadata.get('visual_verification', {}).get('issues', [])}")
        return response.content
    else:
        return f"Ошибка генерации кода: {response.error}"

async def analyze_data(prompt: str) -> str:
    """Анализ данных"""
    system_prompt = """Ты эксперт по анализу данных. Анализируй данные, находи закономерности,
    создавай инсайты и давай практические рекомендации."""
    
    response = await enhanced_ai_engine.generate_response(prompt, system_prompt=system_prompt)
    return response.content if response.success else f"Ошибка анализа: {response.error}"

async def plan_project(prompt: str) -> str:
    """Планирование проекта"""
    system_prompt = """Ты опытный менеджер проектов. Создавай детальные планы проектов,
    разбивай задачи на этапы, оценивай риски и ресурсы."""
    
    response = await enhanced_ai_engine.generate_response(prompt, system_prompt=system_prompt)
    return response.content if response.success else f"Ошибка планирования: {response.error}"

if __name__ == "__main__":
    # Тестирование улучшенного AI движка
    async def test_enhanced_ai():
        print("🧪 Тестирование Enhanced AI Engine...")
        
        # Инициализация
        await enhanced_ai_engine.initialize()
        
        # Статус системы
        status = await enhanced_ai_engine.get_system_status()
        print(f"Статус: {status}")
        
        # Тестовые запросы
        test_prompts = [
            "Привет! Как дела?",
            "Напиши функцию для сортировки списка чисел",
            "Проанализируй эти данные: [1, 2, 3, 4, 5]",
            "Создай план разработки веб-приложения"
        ]
        
        for prompt in test_prompts:
            print(f"\n👤 Запрос: {prompt}")
            response = await enhanced_ai_engine.generate_response(prompt)
            print(f"🤖 Ответ: {response.content[:100]}...")
            print(f"📊 Качество: {response.quality_score:.2f}, Верифицировано: {response.visual_verified}")
        
        # Оптимизация
        await enhanced_ai_engine.optimize_performance()
    
    asyncio.run(test_enhanced_ai())