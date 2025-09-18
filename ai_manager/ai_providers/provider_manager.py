"""
Менеджер AI провайдеров - управляет различными бесплатными AI моделями
"""

from typing import Dict, Any, List, Optional
import asyncio
import logging
from .base_provider import BaseAIProvider
from .ollama_provider import OllamaProvider
from .huggingface_provider import HuggingFaceProvider
from .local_provider import LocalProvider

logger = logging.getLogger(__name__)


class AIProviderManager:
    """Менеджер AI провайдеров"""
    
    def __init__(self):
        self.providers: Dict[str, BaseAIProvider] = {}
        self.default_provider = None
        self.initialized = False
    
    async def initialize_providers(self, config: Dict[str, Any] = None):
        """Инициализация всех доступных провайдеров"""
        if self.initialized:
            return
        
        config = config or {}
        logger.info("Initializing AI providers...")
        
        # Инициализируем провайдеры в порядке приоритета
        providers_to_init = [
            ("ollama", OllamaProvider(config.get("ollama_model", "llama2"))),
            ("huggingface", HuggingFaceProvider(
                config.get("hf_model", "microsoft/DialoGPT-medium"),
                config.get("hf_token")
            )),
            ("local", LocalProvider("local-rule-based"))
        ]
        
        for name, provider in providers_to_init:
            try:
                if await provider.initialize():
                    self.providers[name] = provider
                    if not self.default_provider:
                        self.default_provider = provider
                    logger.info(f"Provider {name} initialized successfully")
                else:
                    logger.warning(f"Provider {name} failed to initialize")
            except Exception as e:
                logger.error(f"Error initializing provider {name}: {e}")
        
        # Устанавливаем локальный провайдер как fallback
        if not self.default_provider and "local" in self.providers:
            self.default_provider = self.providers["local"]
        
        self.initialized = True
        logger.info(f"AI Provider Manager initialized with {len(self.providers)} providers")
    
    async def generate_response(self, prompt: str, provider_name: str = None, **kwargs) -> Dict[str, Any]:
        """Генерация ответа через указанный или лучший доступный провайдер"""
        if not self.initialized:
            await self.initialize_providers()
        
        # Выбираем провайдер
        if provider_name and provider_name in self.providers:
            provider = self.providers[provider_name]
        elif self.default_provider:
            provider = self.default_provider
        else:
            return {
                "success": False,
                "error": "No AI providers available",
                "result": None
            }
        
        # Генерируем ответ
        try:
            result = await provider.generate_response(prompt, **kwargs)
            
            # Если первый провайдер не сработал, пробуем другие
            if not result.get("success") and len(self.providers) > 1:
                for fallback_provider in self.providers.values():
                    if fallback_provider != provider:
                        logger.info(f"Trying fallback provider: {fallback_provider.get_provider_name()}")
                        result = await fallback_provider.generate_response(prompt, **kwargs)
                        if result.get("success"):
                            break
            
            return result
            
        except Exception as e:
            logger.error(f"Error in generate_response: {e}")
            return {
                "success": False,
                "error": str(e),
                "result": None
            }
    
    async def get_provider_health(self) -> Dict[str, Any]:
        """Получение статуса всех провайдеров"""
        if not self.initialized:
            await self.initialize_providers()
        
        health_status = {}
        for name, provider in self.providers.items():
            try:
                health_status[name] = await provider.health_check()
            except Exception as e:
                health_status[name] = {
                    "provider": provider.get_provider_name(),
                    "model": provider.model_name,
                    "available": False,
                    "status": f"error: {str(e)}"
                }
        
        return health_status
    
    def get_available_providers(self) -> List[str]:
        """Получение списка доступных провайдеров"""
        return list(self.providers.keys())
    
    def get_default_provider_name(self) -> str:
        """Получение имени провайдера по умолчанию"""
        if self.default_provider:
            for name, provider in self.providers.items():
                if provider == self.default_provider:
                    return name
        return "none"
    
    async def close_all(self):
        """Закрытие всех провайдеров"""
        for provider in self.providers.values():
            try:
                if hasattr(provider, 'close'):
                    await provider.close()
            except Exception as e:
                logger.error(f"Error closing provider {provider.get_provider_name()}: {e}")
        
        self.providers.clear()
        self.default_provider = None
        self.initialized = False
        logger.info("All AI providers closed")


# Глобальный экземпляр менеджера
provider_manager = AIProviderManager()
