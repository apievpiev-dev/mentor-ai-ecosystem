"""
Базовый провайдер AI для различных моделей
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio
import json


class BaseAIProvider(ABC):
    """Базовый класс для AI провайдеров"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name
        self.is_available = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Инициализация провайдера"""
        pass
    
    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Генерация ответа на основе промпта"""
        pass
    
    @abstractmethod
    async def is_model_available(self) -> bool:
        """Проверка доступности модели"""
        pass
    
    def get_provider_name(self) -> str:
        """Получение имени провайдера"""
        return self.__class__.__name__
    
    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья провайдера"""
        return {
            "provider": self.get_provider_name(),
            "model": self.model_name,
            "available": await self.is_model_available(),
            "status": "healthy" if self.is_available else "unavailable"
        }
