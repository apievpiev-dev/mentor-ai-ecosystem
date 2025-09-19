#!/usr/bin/env python3
"""
Главный файл системы бесплатных локальных нейросетей
"Нейросеть, которая создает нейросети" - только бесплатные модели
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# Импортируем компоненты системы бесплатных моделей
from free_ai_engine import free_ai_engine, generate_ai_response
from free_local_ai_system import free_ai_system
from auto_install_free_models import model_installer
from free_neural_network_web_interface import free_web_interface

logger = logging.getLogger(__name__)

class FreeNeuralNetworkCreatorSystem:
    """Главная система создания нейросетей с бесплатными моделями"""
    
    def __init__(self):
        self.system_id = str(uuid.uuid4())
        self.system_name = "Free Neural Network Creator"
        self.version = "1.0.0"
        self.status = "initializing"
        self.components = {}
        self.created_networks = {}
        self.statistics = {
            "networks_created": 0,
            "models_installed": 0,
            "ai_responses_generated": 0,
            "total_projects": 0,
            "uptime_start": datetime.now().isoformat()
        }
        self._setup_components()
        self._setup_directories()
    
    def _setup_components(self):
        """Настройка всех компонентов системы"""
        self.components = {
            "free_ai_engine": free_ai_engine,
            "free_ai_system": free_ai_system,
            "model_installer": model_installer,
            "web_interface": free_web_interface
        }
        
        logger.info(f"✅ Инициализировано {len(self.components)} компонентов")
    
    def _setup_directories(self):
        """Создание необходимых директорий"""
        directories = [
            "/workspace/free_models",
            "/workspace/free_models/system_logs",
            "/workspace/free_models/projects",
            "/workspace/free_models/statistics",
            "/workspace/free_models/networks"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    async def start_system(self):
        """Запуск всей системы"""
        try:
            self.status = "starting"
            logger.info("🚀 Запуск системы бесплатных локальных нейросетей...")
            
            # 1. Устанавливаем бесплатные модели
            logger.info("📥 Установка бесплатных AI моделей...")
            await self.setup_free_models()
            
            # 2. Настраиваем AI движок
            logger.info("🤖 Настройка AI движка...")
            await free_ai_engine.setup_free_models()
            
            # 3. Запускаем веб-интерфейс
            logger.info("🌐 Запуск веб-интерфейса...")
            web_runner = await free_web_interface.start_server()
            
            self.status = "running"
            
            # Сохраняем статистику запуска
            await self._save_system_statistics()
            
            logger.info("🎉 Система бесплатных локальных нейросетей запущена!")
            logger.info("=" * 70)
            logger.info("🧠 FREE NEURAL NETWORK CREATOR - СИСТЕМА ГОТОВА К РАБОТЕ")
            logger.info("=" * 70)
            logger.info("🌐 Веб-интерфейс: http://localhost:8081")
            logger.info("🤖 AI движок: бесплатные локальные модели")
            logger.info("📥 Поддерживаемые провайдеры:")
            logger.info("   • Ollama - бесплатные языковые модели")
            logger.info("   • Hugging Face - бесплатные трансформеры")
            logger.info("   • Локальные модели - простые трансформеры")
            logger.info("=" * 70)
            logger.info("📋 Доступные функции:")
            logger.info("   - Автоматическая установка бесплатных моделей")
            logger.info("   - Создание нейросетей с помощью ИИ")
            logger.info("   - Работа полностью офлайн")
            logger.info("   - Никаких платных API")
            logger.info("   - Все модели локально на сервере")
            logger.info("=" * 70)
            
            return web_runner
            
        except Exception as e:
            self.status = "error"
            logger.error(f"❌ Ошибка запуска системы: {e}")
            raise
    
    async def setup_free_models(self):
        """Настройка бесплатных моделей"""
        try:
            logger.info("🔧 Настройка бесплатных AI моделей...")
            
            # Устанавливаем все бесплатные модели
            results = await model_installer.install_all_models()
            
            if results["success"]:
                self.statistics["models_installed"] = results["installed_models"]
                logger.info(f"✅ Установлено {results['installed_models']} бесплатных моделей")
            else:
                logger.warning(f"⚠️ Установка завершена с ошибками: {results['failed_installations']} ошибок")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Ошибка настройки бесплатных моделей: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_neural_network_with_ai(self, task_description: str, 
                                          provider: str = "auto") -> Dict[str, Any]:
        """Создание нейросети с помощью бесплатного AI"""
        try:
            network_id = str(uuid.uuid4())[:8]
            network_name = f"free_network_{network_id}"
            
            logger.info(f"🧠 Создание нейросети: {task_description}")
            
            # Генерируем архитектуру с помощью AI
            ai_prompt = f"""
            Создай архитектуру нейросети для задачи: {task_description}
            
            Верни JSON с полями:
            - name: название сети
            - type: тип задачи (classification/regression/generation)
            - input_size: размер входа
            - output_size: размер выхода
            - hidden_layers: список размеров скрытых слоев
            - activation_functions: функции активации
            - optimizer: оптимизатор
            - loss_function: функция потерь
            - learning_rate: скорость обучения
            - batch_size: размер батча
            - epochs: количество эпох
            - description: описание архитектуры
            """
            
            # Генерируем ответ с помощью бесплатного AI
            ai_response = await free_ai_engine.generate_response(
                ai_prompt,
                provider=provider if provider != "auto" else None
            )
            
            if not ai_response.success:
                raise Exception(f"Ошибка AI: {ai_response.error}")
            
            self.statistics["ai_responses_generated"] += 1
            
            try:
                # Парсим JSON ответ от AI
                network_config = json.loads(ai_response.content)
            except json.JSONDecodeError:
                # Fallback конфигурация
                network_config = {
                    "name": network_name,
                    "type": "classification",
                    "input_size": 784,
                    "output_size": 10,
                    "hidden_layers": [128, 64],
                    "activation_functions": ["relu", "relu"],
                    "optimizer": "adam",
                    "loss_function": "cross_entropy",
                    "learning_rate": 0.001,
                    "batch_size": 32,
                    "epochs": 20,
                    "description": f"Нейросеть для задачи: {task_description}"
                }
            
            # Создаем нейросеть
            network = {
                "id": network_id,
                "name": network_config["name"],
                "task": task_description,
                "provider": ai_response.provider,
                "model_used": ai_response.model,
                "config": network_config,
                "ai_response": ai_response.content,
                "status": "created",
                "created_at": datetime.now().isoformat(),
                "response_time": ai_response.response_time
            }
            
            self.created_networks[network_id] = network
            self.statistics["networks_created"] += 1
            self.statistics["total_projects"] += 1
            
            # Сохраняем нейросеть
            await self._save_network(network)
            
            logger.info(f"✅ Нейросеть создана: {network_name}")
            logger.info(f"🤖 Использована модель: {ai_response.model} ({ai_response.provider})")
            logger.info(f"⏱️ Время генерации: {ai_response.response_time:.2f} сек")
            
            return {
                "message": f"Нейросеть '{network_name}' создана успешно",
                "network": network,
                "ai_provider": ai_response.provider,
                "ai_model": ai_response.model,
                "response_time": ai_response.response_time
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания нейросети: {e}")
            return {"error": str(e)}
    
    async def get_available_models(self) -> Dict[str, Any]:
        """Получение списка доступных бесплатных моделей"""
        try:
            models = free_ai_engine.get_available_models()
            status = free_ai_engine.get_status()
            
            return {
                "models": models,
                "status": status,
                "total_models": sum(len(model_list) for model_list in models.values()),
                "providers": list(models.keys())
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения моделей: {e}")
            return {"error": str(e)}
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Получение статуса всей системы"""
        try:
            # Статус AI движка
            ai_status = free_ai_engine.get_status()
            
            # Статус установщика моделей
            installer_status = await model_installer.get_installation_status()
            
            return {
                "system_id": self.system_id,
                "system_name": self.system_name,
                "version": self.version,
                "status": self.status,
                "uptime": self._get_uptime(),
                "statistics": self.statistics,
                "created_networks": len(self.created_networks),
                "ai_engine": ai_status,
                "model_installer": installer_status,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статуса системы: {e}")
            return {"error": str(e)}
    
    def _get_uptime(self) -> str:
        """Получение времени работы системы"""
        try:
            start_time = datetime.fromisoformat(self.statistics["uptime_start"])
            uptime = datetime.now() - start_time
            return str(uptime)
        except:
            return "unknown"
    
    async def _save_network(self, network: Dict[str, Any]):
        """Сохранение нейросети"""
        try:
            network_path = f"/workspace/free_models/networks/{network['id']}_network.json"
            with open(network_path, 'w', encoding='utf-8') as f:
                json.dump(network, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Нейросеть сохранена: {network_path}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения нейросети: {e}")
    
    async def _save_system_statistics(self):
        """Сохранение статистики системы"""
        try:
            stats_path = f"/workspace/free_models/statistics/system_stats_{int(time.time())}.json"
            with open(stats_path, 'w', encoding='utf-8') as f:
                json.dump(self.statistics, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Статистика сохранена: {stats_path}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения статистики: {e}")
    
    async def demo_creation(self):
        """Демонстрация создания нейросети"""
        try:
            logger.info("🎬 Запуск демонстрации создания нейросети...")
            
            # Создаем демо-нейросеть
            demo_result = await self.create_neural_network_with_ai(
                "Создай нейросеть для классификации изображений рукописных цифр MNIST",
                provider="auto"
            )
            
            if demo_result.get("error"):
                logger.error(f"❌ Демо не удалось: {demo_result['error']}")
            else:
                logger.info("✅ Демонстрация завершена успешно!")
                logger.info(f"📊 Создано нейросетей: {self.statistics['networks_created']}")
                logger.info(f"🤖 AI ответов сгенерировано: {self.statistics['ai_responses_generated']}")
                logger.info(f"📥 Моделей установлено: {self.statistics['models_installed']}")
            
            return demo_result
            
        except Exception as e:
            logger.error(f"❌ Ошибка демонстрации: {e}")
            return {"error": str(e)}

# Глобальный экземпляр системы
free_neural_network_creator_system = FreeNeuralNetworkCreatorSystem()

async def main():
    """Главная функция"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Запускаем систему
        runner = await free_neural_network_creator_system.start_system()
        
        # Запускаем демонстрацию
        logger.info("🎬 Запуск демонстрации...")
        demo_result = await free_neural_network_creator_system.demo_creation()
        
        if not demo_result.get("error"):
            logger.info("🎉 Демонстрация прошла успешно!")
        
        # Показываем статус системы
        status = await free_neural_network_creator_system.get_system_status()
        logger.info(f"📊 Статус системы: {status['status']}")
        logger.info(f"⏱️ Время работы: {status['uptime']}")
        logger.info(f"📈 Статистика: {status['statistics']}")
        
        # Показываем доступные модели
        models = await free_neural_network_creator_system.get_available_models()
        logger.info(f"🤖 Доступно моделей: {models.get('total_models', 0)}")
        logger.info(f"📋 Провайдеры: {models.get('providers', [])}")
        
        # Запускаем в бесконечном цикле
        logger.info("🔄 Система работает в автономном режиме...")
        while True:
            await asyncio.sleep(60)  # Обновляем каждую минуту
            
            # Периодически показываем статистику
            if int(time.time()) % 300 == 0:  # Каждые 5 минут
                status = await free_neural_network_creator_system.get_system_status()
                logger.info(f"📊 Создано нейросетей: {status['statistics']['networks_created']}")
                logger.info(f"🤖 AI ответов: {status['statistics']['ai_responses_generated']}")
            
    except KeyboardInterrupt:
        logger.info("🛑 Остановка системы бесплатных нейросетей...")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())