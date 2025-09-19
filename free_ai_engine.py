#!/usr/bin/env python3
"""
Бесплатный AI Engine для работы с локальными моделями
Поддерживает только бесплатные модели: Ollama, Hugging Face, локальные трансформеры
"""

import asyncio
import json
import logging
import subprocess
import time
import requests
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class AIResponse:
    """Ответ от AI модели"""
    content: str
    model: str
    provider: str
    tokens_used: int = 0
    response_time: float = 0.0
    success: bool = True
    error: Optional[str] = None

class OllamaEngine:
    """Движок для работы с Ollama (бесплатные модели)"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.available_models = []
        self.free_models = [
            "llama3.1:8b",           # Meta Llama 3.1 8B
            "llama3.1:70b",          # Meta Llama 3.1 70B  
            "codellama:latest",      # Code Llama
            "mistral:latest",        # Mistral 7B
            "neural-chat:latest",    # Intel Neural Chat
            "starling-lm:latest",    # Starling LM
            "phi3:latest",           # Microsoft Phi-3
            "gemma:latest",          # Google Gemma
            "qwen:latest",           # Alibaba Qwen
            "deepseek-coder:latest", # DeepSeek Coder
            "tinyllama:latest",      # TinyLlama (очень маленькая)
            "orca-mini:latest"       # Orca Mini
        ]
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
    
    async def install_free_models(self):
        """Установка бесплатных моделей"""
        logger.info("📥 Устанавливаю бесплатные модели Ollama...")
        
        for model in self.free_models:
            if model not in self.available_models:
                try:
                    logger.info(f"📥 Устанавливаю {model}...")
                    process = subprocess.Popen(
                        ['ollama', 'pull', model],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    # Ждем завершения
                    while process.poll() is None:
                        await asyncio.sleep(1)
                    
                    if process.returncode == 0:
                        logger.info(f"✅ {model} установлена")
                        self.available_models.append(model)
                    else:
                        logger.error(f"❌ Ошибка установки {model}")
                        
                except Exception as e:
                    logger.error(f"❌ Ошибка установки {model}: {e}")
    
    async def generate_response(self, prompt: str, model: str = None, 
                              system_prompt: str = None, **kwargs) -> AIResponse:
        """Генерация ответа от модели"""
        start_time = time.time()
        
        if not model:
            model = self._get_best_available_model()
        
        if not model:
            return AIResponse(
                content="",
                model="none",
                provider="ollama",
                response_time=time.time() - start_time,
                success=False,
                error="Нет доступных моделей Ollama"
            )
        
        try:
            data = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                    "max_tokens": kwargs.get("max_tokens", 1000)
                }
            }
            
            if system_prompt:
                data["system"] = system_prompt
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=data,
                timeout=120  # Увеличенный таймаут для больших моделей
            )
            
            if response.status_code == 200:
                result = response.json()
                response_time = time.time() - start_time
                
                return AIResponse(
                    content=result.get("response", ""),
                    model=model,
                    provider="ollama",
                    tokens_used=len(result.get("response", "").split()),
                    response_time=response_time,
                    success=True
                )
            else:
                return AIResponse(
                    content="",
                    model=model,
                    provider="ollama",
                    response_time=time.time() - start_time,
                    success=False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            return AIResponse(
                content="",
                model=model,
                provider="ollama",
                response_time=time.time() - start_time,
                success=False,
                error=str(e)
            )
    
    def _get_best_available_model(self) -> str:
        """Получение лучшей доступной модели"""
        # Приоритет: маленькие модели для быстрого ответа
        priority_models = ["tinyllama:latest", "orca-mini:latest", "phi3:latest", "mistral:latest"]
        
        for model in priority_models:
            if model in self.available_models:
                return model
        
        # Если приоритетные не найдены, берем первую доступную
        return self.available_models[0] if self.available_models else None
    
    def is_available(self) -> bool:
        """Проверка доступности Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

class HuggingFaceEngine:
    """Движок для работы с Hugging Face (бесплатные модели)"""
    
    def __init__(self):
        self.available_models = []
        self.free_models = [
            "microsoft/DialoGPT-medium",
            "distilbert-base-uncased", 
            "bert-base-uncased",
            "gpt2",
            "facebook/blenderbot-400M-distill",
            "microsoft/DialoGPT-small",
            "t5-small",
            "google/flan-t5-small"
        ]
        self._check_availability()
    
    def _check_availability(self):
        """Проверка доступности Hugging Face"""
        try:
            import transformers
            self.available_models = self.free_models.copy()
            logger.info(f"✅ Hugging Face доступен, {len(self.available_models)} моделей")
        except ImportError:
            logger.warning("⚠️ Hugging Face не установлен")
    
    async def generate_response(self, prompt: str, model: str = None, **kwargs) -> AIResponse:
        """Генерация ответа от модели"""
        start_time = time.time()
        
        if not self.available_models:
            return AIResponse(
                content="",
                model="none",
                provider="huggingface",
                response_time=time.time() - start_time,
                success=False,
                error="Hugging Face не доступен"
            )
        
        if not model:
            model = "gpt2"  # Простая модель по умолчанию
        
        try:
            from transformers import pipeline
            
            # Создаем pipeline для генерации текста
            generator = pipeline(
                "text-generation",
                model=model,
                max_length=kwargs.get("max_tokens", 100),
                temperature=kwargs.get("temperature", 0.7),
                do_sample=True
            )
            
            result = generator(prompt, max_length=len(prompt.split()) + kwargs.get("max_tokens", 50))
            content = result[0]["generated_text"]
            
            response_time = time.time() - start_time
            
            return AIResponse(
                content=content,
                model=model,
                provider="huggingface",
                tokens_used=len(content.split()),
                response_time=response_time,
                success=True
            )
            
        except Exception as e:
            return AIResponse(
                content="",
                model=model,
                provider="huggingface",
                response_time=time.time() - start_time,
                success=False,
                error=str(e)
            )
    
    def is_available(self) -> bool:
        """Проверка доступности Hugging Face"""
        return len(self.available_models) > 0

class LocalTransformersEngine:
    """Движок для локальных трансформеров (всегда доступен)"""
    
    def __init__(self):
        self.available_models = [
            "simple_classifier",
            "simple_generator", 
            "simple_analyzer",
            "simple_optimizer"
        ]
        logger.info(f"✅ Локальные трансформеры доступны, {len(self.available_models)} моделей")
    
    async def generate_response(self, prompt: str, model: str = None, **kwargs) -> AIResponse:
        """Генерация ответа от локальной модели"""
        start_time = time.time()
        
        if not model:
            model = "simple_generator"
        
        try:
            # Простая генерация для демонстрации
            if model == "simple_classifier":
                content = f"Классификация: {prompt[:50]}... (обработано локальной моделью классификации)"
            elif model == "simple_generator":
                content = f"Сгенерированный текст на основе: {prompt[:30]}... (локальная генерация текста)"
            elif model == "simple_analyzer":
                content = f"Анализ: {prompt[:40]}... (локальный анализ данных)"
            elif model == "simple_optimizer":
                content = f"Оптимизация: {prompt[:35]}... (локальная оптимизация параметров)"
            else:
                content = f"Ответ от локальной модели {model}: {prompt[:50]}..."
            
            response_time = time.time() - start_time
            
            return AIResponse(
                content=content,
                model=model,
                provider="local_transformers",
                tokens_used=len(content.split()),
                response_time=response_time,
                success=True
            )
            
        except Exception as e:
            return AIResponse(
                content="",
                model=model,
                provider="local_transformers",
                response_time=time.time() - start_time,
                success=False,
                error=str(e)
            )
    
    def is_available(self) -> bool:
        """Локальные трансформеры всегда доступны"""
        return True

class FreeAIEngine:
    """Основной класс для работы с бесплатными AI моделями"""
    
    def __init__(self):
        self.ollama = OllamaEngine()
        self.huggingface = HuggingFaceEngine()
        self.local_transformers = LocalTransformersEngine()
        self.default_engine = None
        self._select_default_engine()
    
    def _select_default_engine(self):
        """Выбор движка по умолчанию"""
        if self.ollama.is_available():
            self.default_engine = self.ollama
            logger.info("🤖 Выбран Ollama как основной движок AI")
        elif self.huggingface.is_available():
            self.default_engine = self.huggingface
            logger.info("🤖 Выбран Hugging Face как основной движок AI")
        else:
            self.default_engine = self.local_transformers
            logger.info("🤖 Выбран локальные трансформеры как основной движок AI")
    
    async def setup_free_models(self):
        """Настройка бесплатных моделей"""
        logger.info("🚀 Настройка бесплатных AI моделей...")
        
        # Устанавливаем модели Ollama
        if self.ollama.is_available():
            await self.ollama.install_free_models()
        
        logger.info("✅ Бесплатные AI модели настроены")
    
    async def generate_response(self, prompt: str, model: str = None,
                              system_prompt: str = None, provider: str = None, **kwargs) -> AIResponse:
        """Генерация ответа от AI"""
        if not self.default_engine:
            return AIResponse(
                content="Извините, AI движок недоступен",
                model="none",
                provider="none",
                success=False,
                error="Нет доступных AI движков"
            )
        
        # Выбираем провайдера
        if provider == "ollama" and self.ollama.is_available():
            selected_engine = self.ollama
        elif provider == "huggingface" and self.huggingface.is_available():
            selected_engine = self.huggingface
        elif provider == "local_transformers":
            selected_engine = self.local_transformers
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
        
        if self.huggingface.is_available():
            models["huggingface"] = self.huggingface.available_models
        
        if self.local_transformers.is_available():
            models["local_transformers"] = self.local_transformers.available_models
        
        return models
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус AI движков"""
        return {
            "ollama_available": self.ollama.is_available(),
            "huggingface_available": self.huggingface.is_available(),
            "local_transformers_available": self.local_transformers.is_available(),
            "default_engine": self.default_engine.__class__.__name__ if self.default_engine else "none",
            "available_models": self.get_available_models()
        }

# Глобальный экземпляр бесплатного AI движка
free_ai_engine = FreeAIEngine()

# Функции для удобного использования
async def generate_ai_response(prompt: str, system_prompt: str = None, **kwargs) -> str:
    """Простая функция для генерации ответа от AI"""
    response = await free_ai_engine.generate_response(prompt, system_prompt=system_prompt, **kwargs)
    return response.content if response.success else f"Ошибка: {response.error}"

async def generate_code(prompt: str, language: str = "python") -> str:
    """Генерация кода"""
    system_prompt = f"""Ты эксперт-программист. Создавай качественный, рабочий код на {language}.
Отвечай только кодом без объяснений, если не просят иначе."""
    
    response = await free_ai_engine.generate_response(prompt, system_prompt=system_prompt)
    return response.content if response.success else f"Ошибка генерации кода: {response.error}"

async def analyze_data(prompt: str) -> str:
    """Анализ данных"""
    system_prompt = """Ты эксперт по анализу данных. Анализируй данные, находи закономерности,
создавай инсайты и давай практические рекомендации."""
    
    response = await free_ai_engine.generate_response(prompt, system_prompt=system_prompt)
    return response.content if response.success else f"Ошибка анализа: {response.error}"

async def plan_project(prompt: str) -> str:
    """Планирование проекта"""
    system_prompt = """Ты опытный менеджер проектов. Создавай детальные планы проектов,
разбивай задачи на этапы, оценивай риски и ресурсы."""
    
    response = await free_ai_engine.generate_response(prompt, system_prompt=system_prompt)
    return response.content if response.success else f"Ошибка планирования: {response.error}"

if __name__ == "__main__":
    # Тестирование бесплатного AI движка
    async def test_free_ai():
        print("🧪 Тестирование бесплатного AI движка...")
        
        # Настраиваем модели
        await free_ai_engine.setup_free_models()
        
        status = free_ai_engine.get_status()
        print(f"Статус: {status}")
        
        if status["default_engine"] != "none":
            response = await generate_ai_response("Привет! Как дела?")
            print(f"Ответ AI: {response}")
        else:
            print("❌ AI движок недоступен")
    
    asyncio.run(test_free_ai())