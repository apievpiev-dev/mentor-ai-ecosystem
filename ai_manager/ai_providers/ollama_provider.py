"""
Ollama AI Provider - бесплатные локальные модели
"""

import aiohttp
import json
from typing import Dict, Any, Optional
from .base_provider import BaseAIProvider
import logging

logger = logging.getLogger(__name__)


class OllamaProvider(BaseAIProvider):
    """Провайдер для Ollama - бесплатные локальные модели"""
    
    def __init__(self, model_name: str = "llama2", base_url: str = "http://localhost:11434"):
        super().__init__(model_name)
        self.base_url = base_url.rstrip('/')
        self.session = None
    
    async def initialize(self) -> bool:
        """Инициализация Ollama провайдера"""
        try:
            self.session = aiohttp.ClientSession()
            self.is_available = await self.is_model_available()
            if self.is_available:
                logger.info(f"Ollama provider initialized with model: {self.model_name}")
            else:
                logger.warning(f"Ollama model {self.model_name} not available")
            return self.is_available
        except Exception as e:
            logger.error(f"Failed to initialize Ollama provider: {e}")
            self.is_available = False
            return False
    
    async def is_model_available(self) -> bool:
        """Проверка доступности модели Ollama"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Проверяем список доступных моделей
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = [model["name"] for model in data.get("models", [])]
                    
                    # Проверяем, есть ли наша модель
                    if self.model_name in models:
                        return True
                    
                    # Если модели нет, пытаемся загрузить её
                    return await self._pull_model()
                return False
        except Exception as e:
            logger.error(f"Error checking Ollama model availability: {e}")
            return False
    
    async def _pull_model(self) -> bool:
        """Загрузка модели Ollama"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Пытаемся загрузить модель
            async with self.session.post(
                f"{self.base_url}/api/pull",
                json={"name": self.model_name}
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Error pulling Ollama model: {e}")
            return False
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Генерация ответа через Ollama"""
        if not self.is_available:
            return {
                "success": False,
                "error": "Ollama provider not available",
                "result": None
            }
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Параметры для генерации
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                    "max_tokens": kwargs.get("max_tokens", 1000)
                }
            }
            
            async with self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "result": data.get("response", ""),
                        "model": self.model_name,
                        "provider": "ollama"
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"Ollama API error: {response.status} - {error_text}",
                        "result": None
                    }
                    
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Ollama request timeout",
                "result": None
            }
        except Exception as e:
            logger.error(f"Error generating response with Ollama: {e}")
            return {
                "success": False,
                "error": str(e),
                "result": None
            }
    
    async def close(self):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()
    
    def get_supported_models(self) -> list:
        """Получение списка поддерживаемых моделей"""
        return [
            "llama2",
            "llama2:7b",
            "llama2:13b",
            "codellama",
            "codellama:7b",
            "codellama:13b",
            "mistral",
            "mistral:7b",
            "neural-chat",
            "orca-mini",
            "orca-mini:3b",
            "orca-mini:7b",
            "phi",
            "phi:3b",
            "starling-lm",
            "gemma",
            "gemma:2b",
            "gemma:7b"
        ]
