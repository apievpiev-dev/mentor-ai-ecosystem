"""
Hugging Face AI Provider - бесплатные модели через API
"""

import aiohttp
import json
from typing import Dict, Any, Optional
from .base_provider import BaseAIProvider
import logging

logger = logging.getLogger(__name__)


class HuggingFaceProvider(BaseAIProvider):
    """Провайдер для Hugging Face - бесплатные модели через API"""
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium", api_token: str = None):
        super().__init__(model_name)
        self.api_token = api_token
        self.api_url = "https://api-inference.huggingface.co/models"
        self.session = None
    
    async def initialize(self) -> bool:
        """Инициализация Hugging Face провайдера"""
        try:
            self.session = aiohttp.ClientSession()
            self.is_available = await self.is_model_available()
            if self.is_available:
                logger.info(f"HuggingFace provider initialized with model: {self.model_name}")
            else:
                logger.warning(f"HuggingFace model {self.model_name} not available")
            return self.is_available
        except Exception as e:
            logger.error(f"Failed to initialize HuggingFace provider: {e}")
            self.is_available = False
            return False
    
    async def is_model_available(self) -> bool:
        """Проверка доступности модели Hugging Face"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            headers = {}
            if self.api_token:
                headers["Authorization"] = f"Bearer {self.api_token}"
            
            async with self.session.get(
                f"{self.api_url}/{self.model_name}",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Error checking HuggingFace model availability: {e}")
            return False
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Генерация ответа через Hugging Face"""
        if not self.is_available:
            return {
                "success": False,
                "error": "HuggingFace provider not available",
                "result": None
            }
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            headers = {"Content-Type": "application/json"}
            if self.api_token:
                headers["Authorization"] = f"Bearer {self.api_token}"
            
            # Параметры для генерации
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": kwargs.get("max_tokens", 100),
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            async with self.session.post(
                f"{self.api_url}/{self.model_name}",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Извлекаем текст ответа
                    if isinstance(data, list) and len(data) > 0:
                        result_text = data[0].get("generated_text", "")
                    elif isinstance(data, dict):
                        result_text = data.get("generated_text", "")
                    else:
                        result_text = str(data)
                    
                    return {
                        "success": True,
                        "result": result_text.strip(),
                        "model": self.model_name,
                        "provider": "huggingface"
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"HuggingFace API error: {response.status} - {error_text}",
                        "result": None
                    }
                    
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "HuggingFace request timeout",
                "result": None
            }
        except Exception as e:
            logger.error(f"Error generating response with HuggingFace: {e}")
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
            "microsoft/DialoGPT-medium",
            "microsoft/DialoGPT-small",
            "gpt2",
            "gpt2-medium",
            "distilgpt2",
            "facebook/blenderbot-400M-distill",
            "microsoft/DialoGPT-large",
            "EleutherAI/gpt-neo-125M",
            "EleutherAI/gpt-neo-1.3B",
            "microsoft/DialoGPT-small",
            "sshleifer/tiny-gpt2",
            "distilbert-base-uncased",
            "bert-base-uncased"
        ]
