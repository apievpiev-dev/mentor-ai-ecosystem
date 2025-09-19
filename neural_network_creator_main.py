#!/usr/bin/env python3
"""
Главный файл системы "Нейросеть, которая создает нейросети"
Объединяет все компоненты в единую автономную систему
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# Импортируем все компоненты системы
from neural_network_creator_agent import neural_network_creator
from neural_network_web_interface import web_interface
from integrated_neural_network_system import integrated_system
from autonomous_neural_network_trainer import autonomous_trainer
from neural_network_deployment_system import deployment_system
from neural_architecture_generator import architecture_generator
from ai_engine import ai_engine, generate_ai_response

logger = logging.getLogger(__name__)

class NeuralNetworkCreatorSystem:
    """Главная система создания нейросетей"""
    
    def __init__(self):
        self.system_id = str(uuid.uuid4())
        self.system_name = "Neural Network Creator"
        self.version = "1.0.0"
        self.status = "initializing"
        self.components = {}
        self.active_projects = {}
        self.statistics = {
            "networks_created": 0,
            "networks_trained": 0,
            "networks_deployed": 0,
            "total_projects": 0,
            "uptime_start": datetime.now().isoformat()
        }
        self._setup_components()
        self._setup_directories()
    
    def _setup_components(self):
        """Настройка всех компонентов системы"""
        self.components = {
            "neural_network_creator": neural_network_creator,
            "web_interface": web_interface,
            "integrated_system": integrated_system,
            "autonomous_trainer": autonomous_trainer,
            "deployment_system": deployment_system,
            "architecture_generator": architecture_generator,
            "ai_engine": ai_engine
        }
        
        logger.info(f"✅ Инициализировано {len(self.components)} компонентов")
    
    def _setup_directories(self):
        """Создание необходимых директорий"""
        directories = [
            "/workspace/neural_networks",
            "/workspace/neural_networks/system_logs",
            "/workspace/neural_networks/projects",
            "/workspace/neural_networks/statistics",
            "/workspace/neural_networks/backups"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    async def start_system(self):
        """Запуск всей системы"""
        try:
            self.status = "starting"
            logger.info("🚀 Запуск системы Neural Network Creator...")
            
            # Запускаем веб-интерфейс
            logger.info("🌐 Запуск веб-интерфейса...")
            web_runner = await web_interface.start_server()
            
            # Инициализируем AI движок
            logger.info("🤖 Инициализация AI движка...")
            ai_status = ai_engine.get_status()
            logger.info(f"AI движок: {ai_status}")
            
            # Запускаем автономный тренер
            logger.info("🎓 Запуск автономного тренера...")
            asyncio.create_task(autonomous_trainer.start_autonomous_training())
            
            # Инициализируем систему развертывания
            logger.info("🚀 Инициализация системы развертывания...")
            deployment_status = await deployment_system.get_deployment_status()
            logger.info(f"Система развертывания: {deployment_status}")
            
            self.status = "running"
            
            # Сохраняем статистику запуска
            await self._save_system_statistics()
            
            logger.info("🎉 Система Neural Network Creator успешно запущена!")
            logger.info("=" * 60)
            logger.info("🧠 NEURAL NETWORK CREATOR - СИСТЕМА ГОТОВА К РАБОТЕ")
            logger.info("=" * 60)
            logger.info("🌐 Веб-интерфейс: http://localhost:8081")
            logger.info("🤖 AI движок: активен")
            logger.info("🎓 Автономный тренер: активен")
            logger.info("🚀 Система развертывания: активна")
            logger.info("🧠 Генератор архитектур: активен")
            logger.info("=" * 60)
            logger.info("📋 Доступные функции:")
            logger.info("   - Создание нейросетей с помощью ИИ")
            logger.info("   - Автоматическое обучение и оптимизация")
            logger.info("   - Развертывание как API сервисы")
            logger.info("   - Визуализация архитектур")
            logger.info("   - Автономная работа без участия человека")
            logger.info("=" * 60)
            
            return web_runner
            
        except Exception as e:
            self.status = "error"
            logger.error(f"❌ Ошибка запуска системы: {e}")
            raise
    
    async def create_neural_network_project(self, task_description: str, 
                                          project_name: str = None) -> Dict[str, Any]:
        """Создание полного проекта нейросети"""
        try:
            project_id = str(uuid.uuid4())
            project_name = project_name or f"project_{project_id[:8]}"
            
            logger.info(f"🎯 Создание проекта: {project_name}")
            logger.info(f"📝 Описание: {task_description}")
            
            # Создаем проект
            project = {
                "id": project_id,
                "name": project_name,
                "description": task_description,
                "status": "creating",
                "created_at": datetime.now().isoformat(),
                "components_used": [],
                "results": {}
            }
            
            self.active_projects[project_id] = project
            
            # Этап 1: Генерация архитектуры
            logger.info("🧠 Этап 1: Генерация архитектуры...")
            architecture = await architecture_generator.generate_architecture(task_description)
            project["results"]["architecture"] = asdict(architecture)
            project["components_used"].append("architecture_generator")
            
            # Этап 2: Создание нейросети
            logger.info("🔧 Этап 2: Создание нейросети...")
            network_result = await neural_network_creator._handle_create_network({
                "name": f"{project_name}_network",
                "type": architecture.layers[-1].get("activation", "classification"),
                "input_size": architecture.input_size,
                "output_size": architecture.output_size,
                "hidden_layers": [layer["output_size"] for layer in architecture.layers[:-1]]
            })
            project["results"]["network_creation"] = network_result
            project["components_used"].append("neural_network_creator")
            
            # Этап 3: Обучение
            logger.info("🎓 Этап 3: Обучение нейросети...")
            training_result = await neural_network_creator._handle_train_network({
                "network_name": network_result["network_name"]
            })
            project["results"]["training"] = training_result
            project["components_used"].append("autonomous_trainer")
            
            # Этап 4: Визуализация
            logger.info("📊 Этап 4: Создание визуализации...")
            visualization_result = await neural_network_creator._handle_visualize_network({
                "network_name": network_result["network_name"]
            })
            project["results"]["visualization"] = visualization_result
            
            # Этап 5: Развертывание
            logger.info("🚀 Этап 5: Развертывание нейросети...")
            deployment_result = await deployment_system.deploy_neural_network(
                network_result["network_name"]
            )
            project["results"]["deployment"] = deployment_result
            project["components_used"].append("deployment_system")
            
            project["status"] = "completed"
            project["completed_at"] = datetime.now().isoformat()
            
            # Обновляем статистику
            self.statistics["networks_created"] += 1
            self.statistics["networks_trained"] += 1
            self.statistics["networks_deployed"] += 1
            self.statistics["total_projects"] += 1
            
            # Сохраняем проект
            await self._save_project(project)
            
            logger.info(f"✅ Проект {project_name} успешно завершен!")
            logger.info(f"🌐 API доступен по адресам: {deployment_result.get('endpoints', {})}")
            
            return {
                "message": f"Проект '{project_name}' успешно завершен",
                "project": project,
                "statistics": self.statistics
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания проекта: {e}")
            if project_id in self.active_projects:
                self.active_projects[project_id]["status"] = "error"
                self.active_projects[project_id]["error"] = str(e)
            return {"error": str(e)}
    
    async def auto_create_network_with_ai(self, task_description: str) -> Dict[str, Any]:
        """Автоматическое создание нейросети с использованием всех AI компонентов"""
        try:
            logger.info(f"🤖 Автоматическое создание нейросети с ИИ: {task_description}")
            
            # Используем интегрированную систему
            result = await integrated_system.auto_create_network_with_ai(task_description)
            
            if result.get("error"):
                return result
            
            # Обновляем статистику
            self.statistics["networks_created"] += 1
            self.statistics["networks_trained"] += 1
            self.statistics["total_projects"] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка автоматического создания: {e}")
            return {"error": str(e)}
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Получение статуса всей системы"""
        try:
            # Статус компонентов
            components_status = {}
            
            # Статус AI движка
            ai_status = ai_engine.get_status()
            components_status["ai_engine"] = ai_status
            
            # Статус нейросетей
            networks_status = await neural_network_creator._handle_list_networks({})
            components_status["neural_networks"] = networks_status
            
            # Статус автономного тренера
            trainer_status = await autonomous_trainer.get_training_status()
            components_status["autonomous_trainer"] = trainer_status
            
            # Статус системы развертывания
            deployment_status = await deployment_system.get_deployment_status()
            components_status["deployment_system"] = deployment_status
            
            # Статус интегрированной системы
            integrated_status = await integrated_system.get_system_status()
            components_status["integrated_system"] = integrated_status
            
            return {
                "system_id": self.system_id,
                "system_name": self.system_name,
                "version": self.version,
                "status": self.status,
                "uptime": self._get_uptime(),
                "statistics": self.statistics,
                "active_projects": len(self.active_projects),
                "components": components_status,
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
    
    async def _save_project(self, project: Dict[str, Any]):
        """Сохранение проекта"""
        try:
            project_path = f"/workspace/neural_networks/projects/{project['id']}_project.json"
            with open(project_path, 'w', encoding='utf-8') as f:
                json.dump(project, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Проект сохранен: {project_path}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения проекта: {e}")
    
    async def _save_system_statistics(self):
        """Сохранение статистики системы"""
        try:
            stats_path = f"/workspace/neural_networks/statistics/system_stats_{int(time.time())}.json"
            with open(stats_path, 'w', encoding='utf-8') as f:
                json.dump(self.statistics, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Статистика сохранена: {stats_path}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения статистики: {e}")
    
    async def demo_creation(self):
        """Демонстрация создания нейросети"""
        try:
            logger.info("🎬 Запуск демонстрации создания нейросети...")
            
            # Создаем демо-проект
            demo_result = await self.create_neural_network_project(
                "Создай нейросеть для классификации изображений рукописных цифр (MNIST)",
                "demo_mnist_classifier"
            )
            
            if demo_result.get("error"):
                logger.error(f"❌ Демо не удалось: {demo_result['error']}")
            else:
                logger.info("✅ Демонстрация завершена успешно!")
                logger.info(f"📊 Создано проектов: {self.statistics['total_projects']}")
                logger.info(f"🧠 Создано нейросетей: {self.statistics['networks_created']}")
                logger.info(f"🎓 Обучено нейросетей: {self.statistics['networks_trained']}")
                logger.info(f"🚀 Развернуто сервисов: {self.statistics['networks_deployed']}")
            
            return demo_result
            
        except Exception as e:
            logger.error(f"❌ Ошибка демонстрации: {e}")
            return {"error": str(e)}

# Глобальный экземпляр системы
neural_network_creator_system = NeuralNetworkCreatorSystem()

async def main():
    """Главная функция"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Запускаем систему
        runner = await neural_network_creator_system.start_system()
        
        # Запускаем демонстрацию
        logger.info("🎬 Запуск демонстрации...")
        demo_result = await neural_network_creator_system.demo_creation()
        
        if not demo_result.get("error"):
            logger.info("🎉 Демонстрация прошла успешно!")
        
        # Показываем статус системы
        status = await neural_network_creator_system.get_system_status()
        logger.info(f"📊 Статус системы: {status['status']}")
        logger.info(f"⏱️ Время работы: {status['uptime']}")
        logger.info(f"📈 Статистика: {status['statistics']}")
        
        # Запускаем в бесконечном цикле
        logger.info("🔄 Система работает в автономном режиме...")
        while True:
            await asyncio.sleep(60)  # Обновляем каждую минуту
            
            # Периодически показываем статистику
            if int(time.time()) % 300 == 0:  # Каждые 5 минут
                status = await neural_network_creator_system.get_system_status()
                logger.info(f"📊 Активных проектов: {status['active_projects']}")
                logger.info(f"🧠 Всего нейросетей: {status['statistics']['networks_created']}")
            
    except KeyboardInterrupt:
        logger.info("🛑 Остановка системы Neural Network Creator...")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())