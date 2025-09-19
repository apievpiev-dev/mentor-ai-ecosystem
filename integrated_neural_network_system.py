#!/usr/bin/env python3
"""
Интегрированная система Neural Network Creator
Объединяет все AI агенты для создания нейросетей
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from multi_agent_system import BaseAgent, AgentType, AgentCoordinator
from ai_engine import ai_engine, generate_ai_response
from ai_manager_agent import ai_manager
from neural_network_creator_agent import neural_network_creator
from neural_network_web_interface import web_interface

logger = logging.getLogger(__name__)

class IntegratedNeuralNetworkSystem:
    """Интегрированная система для создания нейросетей"""
    
    def __init__(self):
        self.system_id = str(uuid.uuid4())
        self.coordinator = AgentCoordinator()
        self.agents = {}
        self.active_projects = {}
        self.system_status = "initializing"
        self._setup_agents()
        self._setup_coordination()
    
    def _setup_agents(self):
        """Настройка всех агентов"""
        # Добавляем агентов в систему
        self.agents = {
            "ai_manager": ai_manager,
            "neural_network_creator": neural_network_creator,
            "coordinator": self.coordinator
        }
        
        # Регистрируем агентов в координаторе
        for agent_id, agent in self.agents.items():
            self.coordinator.register_agent(agent)
        
        logger.info(f"✅ Зарегистрировано {len(self.agents)} агентов")
    
    def _setup_coordination(self):
        """Настройка координации между агентами"""
        # Настраиваем связи между агентами
        self.coordinator.add_agent_connection(
            "neural_network_creator", 
            "ai_manager",
            "model_management"
        )
        
        self.coordinator.add_agent_connection(
            "ai_manager",
            "neural_network_creator", 
            "ai_optimization"
        )
        
        logger.info("🔗 Координация между агентами настроена")
    
    async def create_neural_network_project(self, project_description: str, 
                                          project_name: str = None) -> Dict[str, Any]:
        """Создание проекта нейросети с координацией всех агентов"""
        try:
            project_id = str(uuid.uuid4())
            project_name = project_name or f"project_{project_id[:8]}"
            
            # Создаем проект
            project = {
                "id": project_id,
                "name": project_name,
                "description": project_description,
                "status": "planning",
                "created_at": datetime.now().isoformat(),
                "agents_involved": [],
                "tasks": [],
                "results": {}
            }
            
            self.active_projects[project_id] = project
            
            # Этап 1: Планирование с AI Manager
            logger.info("📋 Этап 1: Планирование проекта...")
            planning_result = await self._plan_project(project_description)
            project["results"]["planning"] = planning_result
            project["agents_involved"].append("ai_manager")
            
            # Этап 2: Создание нейросети
            logger.info("🧠 Этап 2: Создание нейросети...")
            network_result = await self._create_network_for_project(planning_result)
            project["results"]["network_creation"] = network_result
            project["agents_involved"].append("neural_network_creator")
            
            # Этап 3: Оптимизация с AI Manager
            logger.info("⚡ Этап 3: Оптимизация...")
            optimization_result = await self._optimize_network(network_result)
            project["results"]["optimization"] = optimization_result
            
            # Этап 4: Обучение
            logger.info("🎓 Этап 4: Обучение нейросети...")
            training_result = await self._train_network_for_project(network_result)
            project["results"]["training"] = training_result
            
            # Этап 5: Визуализация
            logger.info("📊 Этап 5: Создание визуализации...")
            visualization_result = await self._create_visualization(network_result)
            project["results"]["visualization"] = visualization_result
            
            project["status"] = "completed"
            project["completed_at"] = datetime.now().isoformat()
            
            # Уведомляем веб-интерфейс
            await self._notify_web_interface(project)
            
            return {
                "message": f"Проект '{project_name}' успешно завершен",
                "project_id": project_id,
                "project": project
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания проекта: {e}")
            if project_id in self.active_projects:
                self.active_projects[project_id]["status"] = "error"
                self.active_projects[project_id]["error"] = str(e)
            return {"error": str(e)}
    
    async def _plan_project(self, description: str) -> Dict[str, Any]:
        """Планирование проекта с помощью AI Manager"""
        try:
            # Используем AI для планирования
            planning_prompt = f"""
            Создай детальный план для проекта нейросети: {description}
            
            Верни JSON с полями:
            - network_type: тип нейросети (classification/regression/generation)
            - input_size: размер входа
            - output_size: размер выхода
            - hidden_layers: список размеров скрытых слоев
            - activation_functions: функции активации
            - optimizer: оптимизатор
            - loss_function: функция потерь
            - learning_rate: скорость обучения
            - batch_size: размер батча
            - epochs: количество эпох
            - data_requirements: требования к данным
            - performance_targets: целевые показатели производительности
            """
            
            ai_response = await generate_ai_response(planning_prompt)
            
            try:
                plan = json.loads(ai_response)
            except json.JSONDecodeError:
                # Fallback план
                plan = {
                    "network_type": "classification",
                    "input_size": 784,
                    "output_size": 10,
                    "hidden_layers": [128, 64],
                    "activation_functions": ["relu", "relu"],
                    "optimizer": "adam",
                    "loss_function": "cross_entropy",
                    "learning_rate": 0.001,
                    "batch_size": 32,
                    "epochs": 10,
                    "data_requirements": "Нужны данные для обучения",
                    "performance_targets": "Точность > 90%"
                }
            
            # Проверяем доступность AI моделей
            ai_status = await ai_manager._handle_list_models({})
            plan["ai_models_available"] = ai_status.get("total_models", 0)
            
            return {
                "plan": plan,
                "ai_suggestion": ai_response,
                "planning_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка планирования: {e}")
            return {"error": str(e)}
    
    async def _create_network_for_project(self, planning_result: Dict[str, Any]) -> Dict[str, Any]:
        """Создание нейросети на основе плана"""
        try:
            plan = planning_result.get("plan", {})
            
            # Создаем нейросеть
            network_config = {
                "name": f"project_network_{uuid.uuid4().hex[:8]}",
                "type": plan.get("network_type", "classification"),
                "input_size": plan.get("input_size", 784),
                "output_size": plan.get("output_size", 10),
                "hidden_layers": plan.get("hidden_layers", [128, 64])
            }
            
            result = await neural_network_creator._handle_create_network(network_config)
            
            if result.get("error"):
                raise Exception(result["error"])
            
            return {
                "network_creation": result,
                "network_name": result["network_name"],
                "creation_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания сети: {e}")
            return {"error": str(e)}
    
    async def _optimize_network(self, network_result: Dict[str, Any]) -> Dict[str, Any]:
        """Оптимизация нейросети"""
        try:
            # Оптимизируем AI модели
            optimization_result = await ai_manager._handle_optimize_models({})
            
            # Получаем метрики производительности
            performance_result = await ai_manager._handle_monitor_performance({})
            
            return {
                "ai_optimization": optimization_result,
                "performance_metrics": performance_result,
                "optimization_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка оптимизации: {e}")
            return {"error": str(e)}
    
    async def _train_network_for_project(self, network_result: Dict[str, Any]) -> Dict[str, Any]:
        """Обучение нейросети"""
        try:
            network_name = network_result.get("network_name")
            if not network_name:
                raise Exception("Имя сети не найдено")
            
            # Обучаем нейросеть
            training_result = await neural_network_creator._handle_train_network({
                "network_name": network_name
            })
            
            if training_result.get("error"):
                raise Exception(training_result["error"])
            
            return {
                "training": training_result,
                "training_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка обучения: {e}")
            return {"error": str(e)}
    
    async def _create_visualization(self, network_result: Dict[str, Any]) -> Dict[str, Any]:
        """Создание визуализации"""
        try:
            network_name = network_result.get("network_name")
            if not network_name:
                raise Exception("Имя сети не найдено")
            
            # Создаем визуализацию
            viz_result = await neural_network_creator._handle_visualize_network({
                "network_name": network_name
            })
            
            if viz_result.get("error"):
                raise Exception(viz_result["error"])
            
            return {
                "visualization": viz_result,
                "visualization_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка визуализации: {e}")
            return {"error": str(e)}
    
    async def _notify_web_interface(self, project: Dict[str, Any]):
        """Уведомление веб-интерфейса о завершении проекта"""
        try:
            if hasattr(web_interface, 'broadcast_update'):
                await web_interface.broadcast_update({
                    "type": "project_completed",
                    "project": project
                })
        except Exception as e:
            logger.error(f"❌ Ошибка уведомления веб-интерфейса: {e}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Получение статуса системы"""
        try:
            # Статус AI Manager
            ai_status = await ai_manager._handle_list_models({})
            
            # Статус Neural Network Creator
            networks_status = await neural_network_creator._handle_list_networks({})
            
            # Статус координатора
            coordinator_status = self.coordinator.get_status()
            
            return {
                "system_id": self.system_id,
                "status": self.system_status,
                "agents": {
                    "ai_manager": {
                        "status": "active",
                        "models_count": ai_status.get("total_models", 0)
                    },
                    "neural_network_creator": {
                        "status": "active", 
                        "networks_count": networks_status.get("total_networks", 0)
                    },
                    "coordinator": coordinator_status
                },
                "active_projects": len(self.active_projects),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статуса: {e}")
            return {"error": str(e)}
    
    async def auto_create_network_with_ai(self, task_description: str) -> Dict[str, Any]:
        """Автоматическое создание нейросети с использованием всех AI агентов"""
        try:
            logger.info(f"🚀 Запуск автоматического создания нейросети для: {task_description}")
            
            # Создаем проект
            result = await self.create_neural_network_project(task_description)
            
            if result.get("error"):
                return result
            
            # Дополнительная оптимизация с AI
            project = result["project"]
            network_name = project["results"]["network_creation"]["network_name"]
            
            # Используем AI для дополнительной оптимизации
            optimization_prompt = f"""
            Проанализируй созданную нейросеть и предложи улучшения:
            Задача: {task_description}
            Архитектура: {json.dumps(project['results']['network_creation']['architecture'], indent=2)}
            Результаты обучения: {json.dumps(project['results']['training'], indent=2)}
            
            Предложи конкретные улучшения архитектуры, гиперпараметров или методов обучения.
            """
            
            ai_suggestions = await generate_ai_response(optimization_prompt)
            
            return {
                "message": "Автоматическое создание нейросети завершено",
                "project": project,
                "ai_suggestions": ai_suggestions,
                "total_agents_used": len(project["agents_involved"])
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка автоматического создания: {e}")
            return {"error": str(e)}
    
    async def start_system(self):
        """Запуск интегрированной системы"""
        try:
            self.system_status = "starting"
            
            # Запускаем веб-интерфейс
            web_runner = await web_interface.start_server()
            
            # Инициализируем AI Manager
            await ai_manager._handle_setup_ai_environment({})
            
            self.system_status = "running"
            
            logger.info("🎉 Интегрированная система Neural Network Creator запущена!")
            logger.info("🌐 Веб-интерфейс: http://localhost:8081")
            logger.info("🤖 AI агенты активны и готовы к работе")
            
            return web_runner
            
        except Exception as e:
            self.system_status = "error"
            logger.error(f"❌ Ошибка запуска системы: {e}")
            raise

# Глобальный экземпляр системы
integrated_system = IntegratedNeuralNetworkSystem()

async def main():
    """Главная функция"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Запускаем систему
        runner = await integrated_system.start_system()
        
        # Тестируем систему
        logger.info("🧪 Тестирование системы...")
        
        # Создаем тестовую нейросеть
        test_result = await integrated_system.auto_create_network_with_ai(
            "Создай нейросеть для классификации изображений рукописных цифр (MNIST)"
        )
        
        if test_result.get("error"):
            logger.error(f"❌ Тест не прошел: {test_result['error']}")
        else:
            logger.info("✅ Тест прошел успешно!")
            logger.info(f"📊 Создано проектов: {len(integrated_system.active_projects)}")
        
        # Запускаем в бесконечном цикле
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Остановка системы...")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())