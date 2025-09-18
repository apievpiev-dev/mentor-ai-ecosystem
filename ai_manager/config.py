"""
Конфигурация AI Manager
"""

import os
from typing import List
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


class Config:
    """Основная конфигурация приложения"""
    
    # AI Providers
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2:7b")
    HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
    HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "microsoft/DialoGPT-medium")
    
    # База данных
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_manager.db")
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Сервер
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # Лимиты системы
    MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", 10))
    MAX_AGENTS = int(os.getenv("MAX_AGENTS", 50))
    AGENT_IDLE_TIMEOUT = int(os.getenv("AGENT_IDLE_TIMEOUT", 1800))  # 30 минут
    
    # Логирование
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "ai_manager.log")
    
    # Мониторинг
    ENABLE_PERFORMANCE_MONITORING = os.getenv("ENABLE_PERFORMANCE_MONITORING", "true").lower() == "true"
    SYSTEM_METRICS_INTERVAL = int(os.getenv("SYSTEM_METRICS_INTERVAL", 60))  # секунды
    
    # Безопасность
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    
    # Настройки AI агентов
    DEFAULT_AI_MODEL = os.getenv("DEFAULT_AI_MODEL", "gpt-3.5-turbo")
    DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
    DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "1500"))
    
    # Настройки задач
    DEFAULT_TASK_PRIORITY = os.getenv("DEFAULT_TASK_PRIORITY", "medium")
    DEFAULT_TASK_CATEGORY = os.getenv("DEFAULT_TASK_CATEGORY", "general")
    
    # Настройки производительности
    TASK_TIMEOUT = int(os.getenv("TASK_TIMEOUT", 300))  # 5 минут
    AGENT_RESPONSE_TIMEOUT = int(os.getenv("AGENT_RESPONSE_TIMEOUT", 60))  # 1 минута
    
    @classmethod
    def validate_config(cls):
        """Валидация конфигурации"""
        errors = []
        
        # Проверяем наличие хотя бы одного AI провайдера
        has_ai_provider = (
            cls.OPENAI_API_KEY or 
            cls.OLLAMA_URL or 
            cls.HUGGINGFACE_TOKEN
        )
        
        if not has_ai_provider:
            errors.append("Необходимо настроить хотя бы один AI провайдер (OpenAI, Ollama или HuggingFace)")
        
        if cls.MAX_CONCURRENT_TASKS < 1:
            errors.append("MAX_CONCURRENT_TASKS должен быть больше 0")
        
        if cls.MAX_AGENTS < 1:
            errors.append("MAX_AGENTS должен быть больше 0")
        
        if cls.PORT < 1 or cls.PORT > 65535:
            errors.append("PORT должен быть в диапазоне 1-65535")
        
        if errors:
            raise ValueError(f"Ошибки конфигурации: {', '.join(errors)}")
        
        return True


# Создаем экземпляр конфигурации
config = Config()

# Валидируем конфигурацию при импорте
try:
    config.validate_config()
except ValueError as e:
    print(f"Предупреждение: {e}")
    print("Некоторые функции могут работать некорректно без правильной конфигурации.")
