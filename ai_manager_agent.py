#!/usr/bin/env python3
"""
Агент-менеджер AI моделей
Может устанавливать, управлять и оптимизировать AI модели
"""

import asyncio
import json
import logging
import subprocess
import time
import requests
import os
import uuid
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

from multi_agent_system import BaseAgent, AgentType
from ai_engine import ai_engine, generate_ai_response

logger = logging.getLogger(__name__)

@dataclass
class ModelInfo:
    """Информация о модели"""
    name: str
    size: str
    status: str  # available, downloading, installed, error
    download_progress: float = 0.0
    last_used: Optional[str] = None
    performance_score: float = 0.0
    memory_usage: float = 0.0

class AIManagerAgent(BaseAgent):
    """Агент-менеджер AI моделей"""
    
    def __init__(self, agent_id: str = None):
        super().__init__(
            agent_id or str(uuid.uuid4()),
            AgentType.SYSTEM_ADMIN,
            "AI Менеджер",
            "Управляет AI моделями, устанавливает новые модели и оптимизирует их работу"
        )
        self.models = {}
        self.installation_queue = []
        self.performance_metrics = {}
        self._setup_skills()
        self._load_models_info()
    
    def _setup_skills(self):
        """Настройка навыков агента"""
        self.add_skill("install_model", self._handle_install_model)
        self.add_skill("list_models", self._handle_list_models)
        self.add_skill("optimize_models", self._handle_optimize_models)
        self.add_skill("monitor_performance", self._handle_monitor_performance)
        self.add_skill("cleanup_models", self._handle_cleanup_models)
        self.add_skill("setup_ai_environment", self._handle_setup_ai_environment)
    
    def _load_models_info(self):
        """Загрузить информацию о моделях"""
        try:
            # Получаем список установленных моделей
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Пропускаем заголовок
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 3:
                            name = parts[0]
                            size = parts[1]
                            self.models[name] = ModelInfo(
                                name=name,
                                size=size,
                                status="installed",
                                last_used=datetime.now().isoformat()
                            )
                logger.info(f"✅ Загружена информация о {len(self.models)} моделях")
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки информации о моделях: {e}")
    
    async def _handle_install_model(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Установка новой модели"""
        model_name = content.get("model_name", "")
        if not model_name:
            return {"error": "Не указано имя модели"}
        
        try:
            # Проверяем, не установлена ли уже модель
            if model_name in self.models:
                return {"message": f"Модель {model_name} уже установлена"}
            
            # Добавляем в очередь установки
            self.installation_queue.append(model_name)
            self.models[model_name] = ModelInfo(
                name=model_name,
                size="unknown",
                status="downloading"
            )
            
            # Запускаем установку в фоне
            asyncio.create_task(self._install_model_async(model_name))
            
            return {
                "message": f"Начинаю установку модели {model_name}",
                "status": "downloading",
                "queue_position": len(self.installation_queue)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка установки модели {model_name}: {e}")
            return {"error": f"Ошибка установки: {str(e)}"}
    
    async def _install_model_async(self, model_name: str):
        """Асинхронная установка модели"""
        try:
            logger.info(f"📥 Устанавливаю модель {model_name}...")
            
            # Запускаем установку
            process = subprocess.Popen(
                ['ollama', 'pull', model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Мониторим прогресс
            while process.poll() is None:
                await asyncio.sleep(1)
                # Здесь можно парсить вывод для отслеживания прогресса
            
            if process.returncode == 0:
                self.models[model_name].status = "installed"
                self.models[model_name].last_used = datetime.now().isoformat()
                logger.info(f"✅ Модель {model_name} успешно установлена")
            else:
                self.models[model_name].status = "error"
                logger.error(f"❌ Ошибка установки модели {model_name}")
            
            # Удаляем из очереди
            if model_name in self.installation_queue:
                self.installation_queue.remove(model_name)
                
        except Exception as e:
            logger.error(f"❌ Ошибка асинхронной установки {model_name}: {e}")
            self.models[model_name].status = "error"
    
    async def _handle_list_models(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Список моделей"""
        try:
            # Обновляем информацию о моделях
            self._load_models_info()
            
            models_info = []
            for model in self.models.values():
                models_info.append({
                    "name": model.name,
                    "size": model.size,
                    "status": model.status,
                    "last_used": model.last_used,
                    "performance_score": model.performance_score
                })
            
            return {
                "models": models_info,
                "total_models": len(models_info),
                "installing": len(self.installation_queue),
                "available_engines": ai_engine.get_status()
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка моделей: {e}")
            return {"error": str(e)}
    
    async def _handle_optimize_models(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Оптимизация моделей"""
        try:
            optimization_results = []
            
            for model_name, model_info in self.models.items():
                if model_info.status == "installed":
                    # Тестируем производительность модели
                    start_time = time.time()
                    response = await ai_engine.generate_response(
                        "Тест производительности",
                        model=model_name,
                        max_tokens=100
                    )
                    response_time = time.time() - start_time
                    
                    # Обновляем метрики
                    model_info.performance_score = 1.0 / max(response_time, 0.1)
                    model_info.last_used = datetime.now().isoformat()
                    
                    optimization_results.append({
                        "model": model_name,
                        "response_time": response_time,
                        "performance_score": model_info.performance_score,
                        "success": response.success
                    })
            
            return {
                "message": "Оптимизация моделей завершена",
                "results": optimization_results
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка оптимизации моделей: {e}")
            return {"error": str(e)}
    
    async def _handle_monitor_performance(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Мониторинг производительности"""
        try:
            performance_data = {
                "timestamp": datetime.now().isoformat(),
                "models": {},
                "system": {
                    "memory_usage": self._get_memory_usage(),
                    "cpu_usage": self._get_cpu_usage(),
                    "disk_usage": self._get_disk_usage()
                }
            }
            
            for model_name, model_info in self.models.items():
                performance_data["models"][model_name] = {
                    "status": model_info.status,
                    "performance_score": model_info.performance_score,
                    "last_used": model_info.last_used,
                    "memory_usage": model_info.memory_usage
                }
            
            return performance_data
            
        except Exception as e:
            logger.error(f"❌ Ошибка мониторинга производительности: {e}")
            return {"error": str(e)}
    
    async def _handle_cleanup_models(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Очистка неиспользуемых моделей"""
        try:
            cleanup_threshold = content.get("days_unused", 30)
            cutoff_date = datetime.now().timestamp() - (cleanup_threshold * 24 * 3600)
            
            models_to_remove = []
            for model_name, model_info in self.models.items():
                if model_info.last_used:
                    last_used_timestamp = datetime.fromisoformat(model_info.last_used).timestamp()
                    if last_used_timestamp < cutoff_date:
                        models_to_remove.append(model_name)
            
            removed_models = []
            for model_name in models_to_remove:
                try:
                    # Удаляем модель
                    subprocess.run(['ollama', 'rm', model_name], check=True)
                    del self.models[model_name]
                    removed_models.append(model_name)
                    logger.info(f"🗑️ Удалена неиспользуемая модель: {model_name}")
                except Exception as e:
                    logger.error(f"❌ Ошибка удаления модели {model_name}: {e}")
            
            return {
                "message": f"Очистка завершена",
                "removed_models": removed_models,
                "models_checked": len(self.models),
                "models_removed": len(removed_models)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка очистки моделей: {e}")
            return {"error": str(e)}
    
    async def _handle_setup_ai_environment(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Настройка AI окружения"""
        try:
            setup_tasks = []
            
            # Устанавливаем популярные модели
            popular_models = [
                "llama3.1:8b",
                "llama3.1:70b", 
                "codellama:latest",
                "mistral:latest",
                "neural-chat:latest",
                "starling-lm:latest",
                "phi3:latest",
                "gemma:latest"
            ]
            
            for model in popular_models:
                if model not in self.models:
                    setup_tasks.append(self._install_model_async(model))
            
            if setup_tasks:
                # Запускаем установку всех моделей параллельно
                await asyncio.gather(*setup_tasks, return_exceptions=True)
            
            # Настраиваем окружение
            self._setup_environment()
            
            return {
                "message": "AI окружение настроено",
                "models_installing": len(setup_tasks),
                "total_models": len(self.models)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка настройки AI окружения: {e}")
            return {"error": str(e)}
    
    def _setup_environment(self):
        """Настройка окружения для AI"""
        try:
            # Создаем директории для AI
            ai_dirs = [
                "/home/mentor/ai_models",
                "/home/mentor/ai_cache",
                "/home/mentor/ai_logs"
            ]
            
            for dir_path in ai_dirs:
                Path(dir_path).mkdir(parents=True, exist_ok=True)
            
            # Настраиваем переменные окружения
            env_vars = {
                "OLLAMA_HOST": "0.0.0.0:11434",
                "OLLAMA_ORIGINS": "*",
                "OLLAMA_MODELS": "/home/mentor/ai_models"
            }
            
            for key, value in env_vars.items():
                os.environ[key] = value
            
            logger.info("✅ AI окружение настроено")
            
        except Exception as e:
            logger.error(f"❌ Ошибка настройки окружения: {e}")
    
    def _get_memory_usage(self) -> float:
        """Получить использование памяти"""
        try:
            result = subprocess.run(['free', '-m'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                mem_line = lines[1].split()
                used = int(mem_line[2])
                total = int(mem_line[1])
                return (used / total) * 100
        except:
            pass
        return 0.0
    
    def _get_cpu_usage(self) -> float:
        """Получить использование CPU"""
        try:
            result = subprocess.run(['top', '-bn1'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Cpu(s)' in line:
                        parts = line.split(',')
                        if len(parts) > 0:
                            cpu_part = parts[0].split()[1]
                            return float(cpu_part.replace('%', ''))
        except:
            pass
        return 0.0
    
    def _get_disk_usage(self) -> float:
        """Получить использование диска"""
        try:
            result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) > 4:
                        usage = parts[4].replace('%', '')
                        return float(usage)
        except:
            pass
        return 0.0
    
    async def auto_install_models(self):
        """Автоматическая установка моделей"""
        try:
            # Получаем список доступных моделей
            available_models = await self._get_available_models()
            
            # Устанавливаем недостающие модели
            for model in available_models:
                if model not in self.models:
                    await self._install_model_async(model)
                    await asyncio.sleep(5)  # Пауза между установками
            
        except Exception as e:
            logger.error(f"❌ Ошибка автоматической установки: {e}")
    
    async def _get_available_models(self) -> List[str]:
        """Получить список доступных моделей"""
        # Список популярных бесплатных моделей
        return [
            "llama3.1:8b",
            "llama3.1:70b",
            "codellama:latest",
            "mistral:latest",
            "neural-chat:latest",
            "starling-lm:latest",
            "phi3:latest",
            "gemma:latest",
            "qwen:latest",
            "deepseek-coder:latest"
        ]

# Глобальный экземпляр агента-менеджера AI
ai_manager = AIManagerAgent()

if __name__ == "__main__":
    # Тестирование агента-менеджера AI
    async def test_ai_manager():
        print("🧪 Тестирование AI менеджера...")
        
        # Список моделей
        result = await ai_manager._handle_list_models({})
        print(f"Модели: {result}")
        
        # Установка модели
        result = await ai_manager._handle_install_model({"model_name": "phi3:latest"})
        print(f"Установка: {result}")
        
        # Мониторинг производительности
        result = await ai_manager._handle_monitor_performance({})
        print(f"Производительность: {result}")
    
    asyncio.run(test_ai_manager())
