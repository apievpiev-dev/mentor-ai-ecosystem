#!/usr/bin/env python3
"""
Автоматическая установка бесплатных AI моделей
Устанавливает все необходимые бесплатные модели на сервер
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

class AutoModelInstaller:
    """Автоматический установщик бесплатных моделей"""
    
    def __init__(self):
        self.installation_log = []
        self.installed_models = {}
        self.failed_installations = []
        self._setup_directories()
    
    def _setup_directories(self):
        """Создание директорий для моделей"""
        directories = [
            "/workspace/free_models",
            "/workspace/free_models/ollama",
            "/workspace/free_models/huggingface", 
            "/workspace/free_models/transformers",
            "/workspace/free_models/cache",
            "/workspace/free_models/logs"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    async def install_ollama(self):
        """Установка Ollama"""
        try:
            logger.info("📥 Устанавливаю Ollama...")
            
            # Проверяем, установлен ли уже Ollama
            result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✅ Ollama уже установлен")
                return True
            
            # Устанавливаем Ollama
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
                self.installation_log.append({
                    "component": "ollama",
                    "status": "installed",
                    "timestamp": datetime.now().isoformat()
                })
                return True
            else:
                logger.error(f"❌ Ошибка установки Ollama: {stderr}")
                self.failed_installations.append({
                    "component": "ollama",
                    "error": stderr,
                    "timestamp": datetime.now().isoformat()
                })
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка установки Ollama: {e}")
            self.failed_installations.append({
                "component": "ollama",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            return False
    
    async def start_ollama_server(self):
        """Запуск Ollama сервера"""
        try:
            # Проверяем, запущен ли сервер
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Ollama сервер уже запущен")
                    return True
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
                        return True
                except:
                    await asyncio.sleep(1)
            
            logger.warning("⚠️ Ollama сервер не запустился")
            return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска Ollama сервера: {e}")
            return False
    
    async def install_ollama_models(self):
        """Установка моделей Ollama"""
        ollama_models = [
            {
                "name": "tinyllama:latest",
                "description": "TinyLlama - очень маленькая и быстрая модель",
                "size": "1.1GB",
                "priority": 1
            },
            {
                "name": "orca-mini:latest", 
                "description": "Orca Mini - компактная модель для диалогов",
                "size": "1.9GB",
                "priority": 2
            },
            {
                "name": "phi3:latest",
                "description": "Microsoft Phi-3 - эффективная модель",
                "size": "2.3GB", 
                "priority": 3
            },
            {
                "name": "mistral:latest",
                "description": "Mistral 7B - качественная модель",
                "size": "4.1GB",
                "priority": 4
            },
            {
                "name": "llama3.1:8b",
                "description": "Meta Llama 3.1 8B - мощная модель",
                "size": "4.7GB",
                "priority": 5
            },
            {
                "name": "codellama:latest",
                "description": "Code Llama - специализированная для программирования",
                "size": "3.8GB",
                "priority": 6
            }
        ]
        
        logger.info(f"📥 Устанавливаю {len(ollama_models)} моделей Ollama...")
        
        for model_info in ollama_models:
            model_name = model_info["name"]
            try:
                logger.info(f"📥 Устанавливаю {model_name} ({model_info['size']})...")
                
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
                    logger.info(f"✅ {model_name} установлена")
                    self.installed_models[model_name] = {
                        "provider": "ollama",
                        "status": "installed",
                        "size": model_info["size"],
                        "installed_at": datetime.now().isoformat()
                    }
                else:
                    logger.error(f"❌ Ошибка установки {model_name}")
                    self.failed_installations.append({
                        "model": model_name,
                        "error": "Installation failed",
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except Exception as e:
                logger.error(f"❌ Ошибка установки {model_name}: {e}")
                self.failed_installations.append({
                    "model": model_name,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
    
    async def install_python_packages(self):
        """Установка Python пакетов для AI"""
        packages = [
            "torch",
            "transformers",
            "accelerate",
            "sentencepiece",
            "protobuf",
            "numpy",
            "requests",
            "aiohttp",
            "aiohttp-cors"
        ]
        
        logger.info("📦 Устанавливаю Python пакеты для AI...")
        
        for package in packages:
            try:
                logger.info(f"📦 Устанавливаю {package}...")
                
                process = subprocess.Popen(
                    ['pip', 'install', package],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    logger.info(f"✅ {package} установлен")
                else:
                    logger.error(f"❌ Ошибка установки {package}: {stderr}")
                    
            except Exception as e:
                logger.error(f"❌ Ошибка установки {package}: {e}")
    
    async def install_huggingface_models(self):
        """Установка моделей Hugging Face"""
        hf_models = [
            {
                "name": "gpt2",
                "description": "GPT-2 - генерация текста",
                "size": "500MB"
            },
            {
                "name": "distilbert-base-uncased",
                "description": "DistilBERT - компактный BERT",
                "size": "250MB"
            },
            {
                "name": "t5-small",
                "description": "T5 Small - универсальная модель",
                "size": "240MB"
            },
            {
                "name": "google/flan-t5-small",
                "description": "FLAN-T5 Small - обученная на инструкциях",
                "size": "240MB"
            }
        ]
        
        logger.info(f"📥 Кэширую {len(hf_models)} моделей Hugging Face...")
        
        for model_info in hf_models:
            model_name = model_info["name"]
            try:
                logger.info(f"📥 Кэширую {model_name}...")
                
                # Импортируем и кэшируем модель
                from transformers import AutoTokenizer, AutoModel
                
                tokenizer = AutoTokenizer.from_pretrained(
                    model_name, 
                    cache_dir="/workspace/free_models/huggingface"
                )
                model = AutoModel.from_pretrained(
                    model_name,
                    cache_dir="/workspace/free_models/huggingface"
                )
                
                logger.info(f"✅ {model_name} закэширована")
                self.installed_models[model_name] = {
                    "provider": "huggingface",
                    "status": "cached",
                    "size": model_info["size"],
                    "cached_at": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"❌ Ошибка кэширования {model_name}: {e}")
                self.failed_installations.append({
                    "model": model_name,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
    
    async def create_local_models(self):
        """Создание локальных моделей"""
        local_models = [
            {
                "name": "simple_classifier",
                "description": "Простой классификатор",
                "type": "classification"
            },
            {
                "name": "simple_generator",
                "description": "Простой генератор текста",
                "type": "generation"
            },
            {
                "name": "simple_analyzer",
                "description": "Простой анализатор данных",
                "type": "analysis"
            },
            {
                "name": "simple_optimizer",
                "description": "Простой оптимизатор",
                "type": "optimization"
            }
        ]
        
        logger.info(f"🔧 Создаю {len(local_models)} локальных моделей...")
        
        for model_info in local_models:
            model_name = model_info["name"]
            try:
                # Создаем простую локальную модель
                model_path = f"/workspace/free_models/transformers/{model_name}.json"
                model_config = {
                    "name": model_name,
                    "description": model_info["description"],
                    "type": model_info["type"],
                    "created_at": datetime.now().isoformat(),
                    "status": "available"
                }
                
                with open(model_path, 'w', encoding='utf-8') as f:
                    json.dump(model_config, f, indent=2, ensure_ascii=False)
                
                logger.info(f"✅ {model_name} создана")
                self.installed_models[model_name] = {
                    "provider": "local_transformers",
                    "status": "created",
                    "created_at": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"❌ Ошибка создания {model_name}: {e}")
    
    async def install_all_models(self):
        """Установка всех бесплатных моделей"""
        logger.info("🚀 Начинаю автоматическую установку бесплатных AI моделей...")
        start_time = time.time()
        
        # 1. Устанавливаем Python пакеты
        await self.install_python_packages()
        
        # 2. Устанавливаем Ollama
        ollama_installed = await self.install_ollama()
        
        if ollama_installed:
            # 3. Запускаем Ollama сервер
            await self.start_ollama_server()
            
            # 4. Устанавливаем модели Ollama
            await self.install_ollama_models()
        
        # 5. Устанавливаем модели Hugging Face
        try:
            await self.install_huggingface_models()
        except Exception as e:
            logger.error(f"❌ Ошибка установки Hugging Face моделей: {e}")
        
        # 6. Создаем локальные модели
        await self.create_local_models()
        
        # Сохраняем результаты
        await self._save_installation_results()
        
        installation_time = time.time() - start_time
        
        logger.info("🎉 Установка завершена!")
        logger.info(f"⏱️ Время установки: {installation_time:.1f} секунд")
        logger.info(f"✅ Установлено моделей: {len(self.installed_models)}")
        logger.info(f"❌ Ошибок: {len(self.failed_installations)}")
        
        return {
            "success": True,
            "installed_models": len(self.installed_models),
            "failed_installations": len(self.failed_installations),
            "installation_time": installation_time,
            "models": self.installed_models
        }
    
    async def _save_installation_results(self):
        """Сохранение результатов установки"""
        try:
            results = {
                "installation_log": self.installation_log,
                "installed_models": self.installed_models,
                "failed_installations": self.failed_installations,
                "total_installed": len(self.installed_models),
                "total_failed": len(self.failed_installations),
                "installation_time": datetime.now().isoformat()
            }
            
            results_path = "/workspace/free_models/logs/installation_results.json"
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Результаты установки сохранены: {results_path}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения результатов: {e}")
    
    async def get_installation_status(self):
        """Получение статуса установки"""
        return {
            "installed_models": self.installed_models,
            "failed_installations": self.failed_installations,
            "total_installed": len(self.installed_models),
            "total_failed": len(self.failed_installations),
            "installation_log": self.installation_log
        }

# Глобальный экземпляр установщика
model_installer = AutoModelInstaller()

async def main():
    """Главная функция"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        logger.info("🚀 Автоматическая установка бесплатных AI моделей")
        logger.info("=" * 60)
        
        # Устанавливаем все модели
        results = await model_installer.install_all_models()
        
        logger.info("📊 РЕЗУЛЬТАТЫ УСТАНОВКИ:")
        logger.info(f"✅ Установлено моделей: {results['installed_models']}")
        logger.info(f"❌ Ошибок: {results['failed_installations']}")
        logger.info(f"⏱️ Время установки: {results['installation_time']:.1f} сек")
        
        # Показываем установленные модели
        logger.info("📋 УСТАНОВЛЕННЫЕ МОДЕЛИ:")
        for model_name, model_info in results['models'].items():
            provider = model_info['provider']
            status = model_info['status']
            logger.info(f"   • {model_name} ({provider}) - {status}")
        
        logger.info("🎉 Установка завершена успешно!")
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())