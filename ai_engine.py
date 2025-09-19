#!/usr/bin/env python3
"""
AI Engine для подключения к языковым моделям
Поддерживает Ollama, OpenAI и другие провайдеры
"""

import asyncio
import json
import logging
import requests
import subprocess
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AIResponse:
    """Ответ от AI модели"""
    content: str
    model: str
    tokens_used: int = 0
    response_time: float = 0.0
    success: bool = True
    error: Optional[str] = None

class OllamaEngine:
    """Движок для работы с Ollama"""
    
    def __init__(self, base_url: str = "http://localhost:11434", default_model: str = "llama2:latest"):
        self.base_url = base_url
        self.default_model = default_model
        self.available_models = []
        self.response_cache = {}  # Кэш для быстрых ответов
        self._load_models()
    
    def _load_models(self):
        """Загрузить список доступных моделей"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Пропускаем заголовок
                self.available_models = [line.split()[0] for line in lines if line.strip()]
                logger.info(f"✅ Загружено {len(self.available_models)} моделей Ollama")
            else:
                logger.warning("⚠️ Не удалось получить список моделей Ollama")
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки моделей Ollama: {e}")
    
    async def generate_response(self, prompt: str, model: str = None, 
                              system_prompt: str = None, retry_count: int = 1, **kwargs) -> AIResponse:
        """Генерация ответа от модели с retry механизмом и кэшированием"""
        start_time = time.time()
        model = model or self.default_model
        
        # Проверяем кэш
        cache_key = f"{prompt[:100]}_{model}_{kwargs.get('temperature', 0.7)}_{kwargs.get('max_tokens', 1000)}"
        if cache_key in self.response_cache:
            logger.info("✅ Используем кэшированный ответ")
            cached_response = self.response_cache[cache_key]
            cached_response.response_time = 0.01  # Быстрый ответ из кэша
            return cached_response
        
        for attempt in range(retry_count + 1):
            try:
                response = await self._make_request(prompt, model, system_prompt, start_time, **kwargs)
                # Сохраняем успешный ответ в кэш
                if response.success and response.content:
                    self.response_cache[cache_key] = response
                    logger.info("💾 Ответ сохранен в кэш")
                return response
            except requests.exceptions.Timeout:
                if attempt < retry_count:
                    logger.warning(f"⏰ Попытка {attempt + 1} неудачна, повторяем...")
                    await asyncio.sleep(1)  # Небольшая пауза перед повтором
                    continue
                else:
                    response_time = time.time() - start_time
                    logger.warning(f"⏰ Таймаут AI запроса после {retry_count + 1} попыток ({response_time:.1f} сек)")
                    return AIResponse(
                        content="",
                        model=model,
                        response_time=response_time,
                        success=False,
                        error="AI timeout - используем fallback ответ"
                    )
            except Exception as e:
                if attempt < retry_count:
                    logger.warning(f"❌ Попытка {attempt + 1} неудачна: {e}, повторяем...")
                    await asyncio.sleep(1)
                    continue
                else:
                    logger.error(f"❌ Ошибка генерации ответа после {retry_count + 1} попыток: {e}")
                    return AIResponse(
                        content="",
                        model=model,
                        response_time=time.time() - start_time,
                        success=False,
                        error=str(e)
                    )
    
    async def _make_request(self, prompt: str, model: str, system_prompt: str, start_time: float, **kwargs) -> AIResponse:
        """Выполнение HTTP запроса к Ollama"""
        
        # Подготавливаем данные для запроса с оптимизированными параметрами
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.5),  # Более детерминированные ответы
                "top_p": kwargs.get("top_p", 0.8),  # Ограниченная выборка для скорости
                "top_k": 20,  # Ограничение выбора токенов
                "repeat_penalty": 1.1,  # Предотвращение повторов
                "num_ctx": 1024,  # Уменьшенное контекстное окно
                "num_predict": kwargs.get("max_tokens", 100)  # Ограничение генерации
            }
        }
        
        if system_prompt:
            data["system"] = system_prompt
        
        # Отправляем запрос с оптимизированным таймаутом для AI ответов
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=data,
            timeout=60  # Восстановлен стабильный таймаут
        )
        
        if response.status_code == 200:
            result = response.json()
            response_time = time.time() - start_time
            
            return AIResponse(
                content=result.get("response", ""),
                model=model,
                tokens_used=len(result.get("response", "").split()),
                response_time=response_time,
                success=True
            )
        else:
            return AIResponse(
                content="",
                model=model,
                response_time=time.time() - start_time,
                success=False,
                error=f"HTTP {response.status_code}: {response.text}"
            )
    
    def is_available(self) -> bool:
        """Проверка доступности Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """Получение статуса здоровья AI движка"""
        try:
            # Проверяем доступность
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return {
                    "status": "healthy",
                    "available_models": len(models),
                    "default_model": self.default_model,
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}",
                    "available_models": 0
                }
        except requests.exceptions.Timeout:
            return {
                "status": "timeout",
                "error": "Connection timeout",
                "available_models": 0
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "available_models": 0
            }

class OpenAIEngine:
    """Движок для работы с OpenAI API"""
    
    def __init__(self, api_key: str = None, default_model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or self._get_api_key()
        self.default_model = default_model
        self.base_url = "https://api.openai.com/v1"
    
    def _get_api_key(self) -> Optional[str]:
        """Получить API ключ из переменных окружения"""
        import os
        return os.getenv("OPENAI_API_KEY")
    
    async def generate_response(self, prompt: str, model: str = None,
                              system_prompt: str = None, **kwargs) -> AIResponse:
        """Генерация ответа от OpenAI"""
        if not self.api_key:
            return AIResponse(
                content="",
                model=model or self.default_model,
                success=False,
                error="OpenAI API ключ не найден"
            )
        
        start_time = time.time()
        model = model or self.default_model
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            data = {
                "model": model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 1000),
                "num_ctx": 1024,  # Уменьшенное контекстное окно
                "num_predict": kwargs.get("max_tokens", 1000),  # Ограничение генерации
                "repeat_penalty": 1.1,  # Предотвращение повторов
                "top_k": 20,  # Ограничение выбора токенов
                "top_p": 0.9  # Ядерная выборка
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=150  # Увеличенный таймаут для стабильности
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                response_time = time.time() - start_time
                
                return AIResponse(
                    content=content,
                    model=model,
                    tokens_used=result.get("usage", {}).get("total_tokens", 0),
                    response_time=response_time,
                    success=True
                )
            else:
                return AIResponse(
                    content="",
                    model=model,
                    response_time=time.time() - start_time,
                    success=False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            logger.error(f"❌ Ошибка генерации ответа OpenAI: {e}")
            return AIResponse(
                content="",
                model=model,
                response_time=time.time() - start_time,
                success=False,
                error=str(e)
            )
    
    def is_available(self) -> bool:
        """Проверка доступности OpenAI API"""
        return self.api_key is not None

class AIEngine:
    """Основной класс для работы с AI"""
    
    def __init__(self):
        self.ollama = OllamaEngine()
        self.openai = OpenAIEngine()
        self.default_engine = None
        self._select_default_engine()
    
    def _select_default_engine(self):
        """Выбор движка по умолчанию"""
        if self.ollama.is_available():
            self.default_engine = self.ollama
            logger.info("🤖 Выбран Ollama как основной движок AI")
        elif self.openai.is_available():
            self.default_engine = self.openai
            logger.info("🤖 Выбран OpenAI как основной движок AI")
        else:
            logger.warning("⚠️ Ни один AI движок не доступен")
    
    async def generate_response(self, prompt: str, model: str = None,
                              system_prompt: str = None, engine: str = None, **kwargs) -> AIResponse:
        """Генерация ответа от AI"""
        if not self.default_engine:
            return AIResponse(
                content="Извините, AI движок недоступен",
                model="none",
                success=False,
                error="Нет доступных AI движков"
            )
        
        # Выбираем движок
        if engine == "ollama" and self.ollama.is_available():
            selected_engine = self.ollama
        elif engine == "openai" and self.openai.is_available():
            selected_engine = self.openai
        else:
            selected_engine = self.default_engine
        
        return await selected_engine.generate_response(
            prompt=prompt,
            model=model,
            system_prompt=system_prompt,
            **kwargs
        )
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Получить список доступных моделей"""
        models = {}
        
        if self.ollama.is_available():
            models["ollama"] = self.ollama.available_models
        
        if self.openai.is_available():
            models["openai"] = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
        
        return models
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус AI движков"""
        return {
            "ollama_available": self.ollama.is_available(),
            "openai_available": self.openai.is_available(),
            "default_engine": "ollama" if self.default_engine == self.ollama else "openai" if self.default_engine == self.openai else "none",
            "available_models": self.get_available_models()
        }

# Глобальный экземпляр AI движка
ai_engine = AIEngine()

# Функции для удобного использования
async def generate_ai_response(prompt: str, system_prompt: str = None, **kwargs) -> str:
    """Простая функция для генерации ответа от AI"""
    response = await ai_engine.generate_response(prompt, system_prompt=system_prompt, **kwargs)
    return response.content if response.success else f"Ошибка: {response.error}"

async def generate_code(prompt: str, language: str = "python") -> str:
    """Генерация кода"""
    system_prompt = f"""Ты эксперт-программист. Создавай качественный, рабочий код на {language}.
Отвечай только кодом без объяснений, если не просят иначе."""
    
    response = await ai_engine.generate_response(prompt, system_prompt=system_prompt)
    return response.content if response.success else f"Ошибка генерации кода: {response.error}"

async def analyze_data(prompt: str) -> str:
    """Анализ данных"""
    system_prompt = """Ты эксперт по анализу данных. Анализируй данные, находи закономерности,
создавай инсайты и давай практические рекомендации."""
    
    response = await ai_engine.generate_response(prompt, system_prompt=system_prompt)
    return response.content if response.success else f"Ошибка анализа: {response.error}"

async def plan_project(prompt: str) -> str:
    """Планирование проекта"""
    system_prompt = """Ты опытный менеджер проектов. Создавай детальные планы проектов,
разбивай задачи на этапы, оценивай риски и ресурсы."""
    
    response = await ai_engine.generate_response(prompt, system_prompt=system_prompt)
    return response.content if response.success else f"Ошибка планирования: {response.error}"

if __name__ == "__main__":
    # Тестирование AI движка
    async def test_ai():
        print("🧪 Тестирование AI движка...")
        
        status = ai_engine.get_status()
        print(f"Статус: {status}")
        
        if status["default_engine"] != "none":
            response = await generate_ai_response("Привет! Как дела?")
            print(f"Ответ AI: {response}")
        else:
            print("❌ AI движок недоступен")
    
    asyncio.run(test_ai())
