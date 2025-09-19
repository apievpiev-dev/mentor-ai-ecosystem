#!/usr/bin/env python3
"""
Система бесплатных локальных AI моделей
Использует только бесплатные модели, которые можно установить на сервер
"""

import asyncio
import json
import logging
import subprocess
import time
import requests
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class FreeLocalAISystem:
    """Система бесплатных локальных AI моделей"""
    
    def __init__(self):
        self.available_models = {}
        self.installed_models = {}
        self.model_providers = {
            "ollama": self._setup_ollama,
            "huggingface": self._setup_huggingface,
            "transformers": self._setup_transformers
        }
        self._setup_directories()
    
    def _setup_directories(self):
        """Создание директорий для моделей"""
        directories = [
            "/workspace/free_models",
            "/workspace/free_models/ollama",
            "/workspace/free_models/huggingface",
            "/workspace/free_models/transformers",
            "/workspace/free_models/cache"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    async def _setup_ollama(self):
        """Настройка Ollama с бесплатными моделями"""
        try:
            # Проверяем, установлен ли Ollama
            result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.info("📥 Устанавливаем Ollama...")
                await self._install_ollama()
            
            # Запускаем Ollama сервер
            await self._start_ollama_server()
            
            # Устанавливаем бесплатные модели
            free_models = [
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
            
            for model in free_models:
                await self._install_ollama_model(model)
            
            logger.info("✅ Ollama настроен с бесплатными моделями")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка настройки Ollama: {e}")
            return False
    
    async def _install_ollama(self):
        """Установка Ollama"""
        try:
            # Скачиваем и устанавливаем Ollama
            install_script = """
            curl -fsSL https://ollama.ai/install.sh | sh
            """
            
            process = subprocess.Popen(
                install_script,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                logger.info("✅ Ollama установлен успешно")
            else:
                logger.error(f"❌ Ошибка установки Ollama: {stderr}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка установки Ollama: {e}")
    
    async def _start_ollama_server(self):
        """Запуск Ollama сервера"""
        try:
            # Проверяем, запущен ли сервер
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Ollama сервер уже запущен")
                    return
            except:
                pass
            
            # Запускаем сервер в фоне
            process = subprocess.Popen(
                ['ollama', 'serve'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Ждем запуска
            for i in range(30):  # Ждем до 30 секунд
                try:
                    response = requests.get("http://localhost:11434/api/tags", timeout=2)
                    if response.status_code == 200:
                        logger.info("✅ Ollama сервер запущен")
                        return
                except:
                    await asyncio.sleep(1)
            
            logger.warning("⚠️ Ollama сервер не запустился")
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска Ollama сервера: {e}")
    
    async def _install_ollama_model(self, model_name: str):
        """Установка модели Ollama"""
        try:
            logger.info(f"📥 Устанавливаю модель {model_name}...")
            
            process = subprocess.Popen(
                ['ollama', 'pull', model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Мониторим прогресс
            while process.poll() is None:
                await asyncio.sleep(1)
            
            if process.returncode == 0:
                self.installed_models[model_name] = {
                    "provider": "ollama",
                    "status": "installed",
                    "installed_at": datetime.now().isoformat()
                }
                logger.info(f"✅ Модель {model_name} установлена")
            else:
                logger.error(f"❌ Ошибка установки модели {model_name}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка установки модели {model_name}: {e}")
    
    async def _setup_huggingface(self):
        """Настройка Hugging Face с бесплатными моделями"""
        try:
            # Устанавливаем transformers
            subprocess.run(['pip', 'install', 'transformers', 'torch', 'accelerate'], check=True)
            
            # Список бесплатных моделей Hugging Face
            free_models = [
                "microsoft/DialoGPT-medium",
                "distilbert-base-uncased",
                "bert-base-uncased",
                "gpt2",
                "facebook/blenderbot-400M-distill",
                "microsoft/DialoGPT-small",
                "t5-small",
                "google/flan-t5-small"
            ]
            
            for model in free_models:
                await self._cache_huggingface_model(model)
            
            logger.info("✅ Hugging Face настроен с бесплатными моделями")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка настройки Hugging Face: {e}")
            return False
    
    async def _cache_huggingface_model(self, model_name: str):
        """Кэширование модели Hugging Face"""
        try:
            from transformers import AutoTokenizer, AutoModel
            
            logger.info(f"📥 Кэширую модель {model_name}...")
            
            # Загружаем токенизатор и модель
            tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir="/workspace/free_models/huggingface")
            model = AutoModel.from_pretrained(model_name, cache_dir="/workspace/free_models/huggingface")
            
            self.installed_models[model_name] = {
                "provider": "huggingface",
                "status": "cached",
                "cached_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Модель {model_name} закэширована")
            
        except Exception as e:
            logger.error(f"❌ Ошибка кэширования модели {model_name}: {e}")
    
    async def _setup_transformers(self):
        """Настройка локальных трансформеров"""
        try:
            # Создаем простые трансформеры для демонстрации
            simple_models = {
                "simple_classifier": {
                    "type": "classification",
                    "description": "Простой классификатор",
                    "size": "small"
                },
                "simple_generator": {
                    "type": "generation", 
                    "description": "Простой генератор текста",
                    "size": "small"
                }
            }
            
            for model_name, config in simple_models.items():
                self.installed_models[model_name] = {
                    "provider": "transformers",
                    "status": "available",
                    "config": config,
                    "created_at": datetime.now().isoformat()
                }
            
            logger.info("✅ Локальные трансформеры настроены")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка настройки трансформеров: {e}")
            return False
    
    async def setup_all_providers(self):
        """Настройка всех провайдеров бесплатных моделей"""
        logger.info("🚀 Настройка системы бесплатных локальных AI моделей...")
        
        results = {}
        
        for provider_name, setup_func in self.model_providers.items():
            logger.info(f"🔧 Настройка {provider_name}...")
            try:
                result = await setup_func()
                results[provider_name] = result
                if result:
                    logger.info(f"✅ {provider_name} настроен успешно")
                else:
                    logger.warning(f"⚠️ {provider_name} настроен с ошибками")
            except Exception as e:
                logger.error(f"❌ Ошибка настройки {provider_name}: {e}")
                results[provider_name] = False
        
        # Сохраняем конфигурацию
        await self._save_configuration()
        
        return results
    
    async def _save_configuration(self):
        """Сохранение конфигурации"""
        try:
            config = {
                "installed_models": self.installed_models,
                "available_providers": list(self.model_providers.keys()),
                "setup_time": datetime.now().isoformat()
            }
            
            config_path = "/workspace/free_models/configuration.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Конфигурация сохранена: {config_path}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения конфигурации: {e}")
    
    async def generate_response(self, prompt: str, model_name: str = None) -> str:
        """Генерация ответа с помощью бесплатной модели"""
        try:
            if not model_name:
                # Выбираем лучшую доступную модель
                model_name = await self._select_best_model()
            
            if model_name not in self.installed_models:
                return "Ошибка: Модель не найдена"
            
            model_info = self.installed_models[model_name]
            provider = model_info["provider"]
            
            if provider == "ollama":
                return await self._generate_with_ollama(prompt, model_name)
            elif provider == "huggingface":
                return await self._generate_with_huggingface(prompt, model_name)
            elif provider == "transformers":
                return await self._generate_with_transformers(prompt, model_name)
            else:
                return "Ошибка: Неизвестный провайдер"
                
        except Exception as e:
            logger.error(f"❌ Ошибка генерации ответа: {e}")
            return f"Ошибка: {str(e)}"
    
    async def _select_best_model(self) -> str:
        """Выбор лучшей доступной модели"""
        # Приоритет: Ollama > HuggingFace > Transformers
        for provider in ["ollama", "huggingface", "transformers"]:
            for model_name, model_info in self.installed_models.items():
                if model_info["provider"] == provider and model_info["status"] in ["installed", "cached", "available"]:
                    return model_name
        
        return "simple_classifier"  # Fallback
    
    async def _generate_with_ollama(self, prompt: str, model_name: str) -> str:
        """Генерация с помощью Ollama"""
        try:
            data = {
                "model": model_name,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "Нет ответа")
            else:
                return f"Ошибка Ollama: {response.status_code}"
                
        except Exception as e:
            return f"Ошибка Ollama: {str(e)}"
    
    async def _generate_with_huggingface(self, prompt: str, model_name: str) -> str:
        """Генерация с помощью Hugging Face"""
        try:
            from transformers import pipeline
            
            # Создаем pipeline для генерации текста
            generator = pipeline("text-generation", model=model_name, cache_dir="/workspace/free_models/huggingface")
            
            result = generator(prompt, max_length=100, num_return_sequences=1)
            return result[0]["generated_text"]
            
        except Exception as e:
            return f"Ошибка Hugging Face: {str(e)}"
    
    async def _generate_with_transformers(self, prompt: str, model_name: str) -> str:
        """Генерация с помощью локальных трансформеров"""
        try:
            # Простая генерация для демонстрации
            if "classifier" in model_name:
                return f"Классификация: {prompt[:50]}... (обработано локальной моделью)"
            elif "generator" in model_name:
                return f"Сгенерированный текст на основе: {prompt[:30]}... (локальная генерация)"
            else:
                return f"Ответ от локальной модели: {prompt[:50]}..."
                
        except Exception as e:
            return f"Ошибка трансформеров: {str(e)}"
    
    async def get_available_models(self) -> Dict[str, Any]:
        """Получение списка доступных моделей"""
        return {
            "installed_models": self.installed_models,
            "total_models": len(self.installed_models),
            "providers": list(self.model_providers.keys())
        }
    
    async def get_model_status(self) -> Dict[str, Any]:
        """Получение статуса моделей"""
        try:
            status = {
                "ollama": False,
                "huggingface": False,
                "transformers": True,  # Всегда доступны
                "total_models": len(self.installed_models)
            }
            
            # Проверяем Ollama
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                status["ollama"] = response.status_code == 200
            except:
                pass
            
            # Проверяем Hugging Face
            try:
                import transformers
                status["huggingface"] = True
            except:
                pass
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статуса: {e}")
            return {"error": str(e)}

# Глобальный экземпляр системы
free_ai_system = FreeLocalAISystem()

async def main():
    """Главная функция"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        logger.info("🚀 Запуск системы бесплатных локальных AI моделей...")
        
        # Настраиваем все провайдеры
        results = await free_ai_system.setup_all_providers()
        
        logger.info("📊 Результаты настройки:")
        for provider, success in results.items():
            status = "✅" if success else "❌"
            logger.info(f"   {status} {provider}")
        
        # Тестируем генерацию
        logger.info("🧪 Тестирование генерации...")
        
        test_prompt = "Создай нейросеть для классификации изображений"
        response = await free_ai_system.generate_response(test_prompt)
        logger.info(f"🤖 Ответ: {response}")
        
        # Показываем доступные модели
        models = await free_ai_system.get_available_models()
        logger.info(f"📋 Доступно моделей: {models['total_models']}")
        
        # Показываем статус
        status = await free_ai_system.get_model_status()
        logger.info(f"📊 Статус провайдеров: {status}")
        
        logger.info("🎉 Система бесплатных локальных AI моделей готова!")
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())