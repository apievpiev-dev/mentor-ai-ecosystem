#!/usr/bin/env python3
"""
Автономный тренер нейросетей
Автоматически обучает, оптимизирует и улучшает нейросети
"""

import asyncio
import json
import logging
import time
import uuid
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from neural_network_creator_agent import neural_network_creator, NetworkArchitecture
from ai_engine import generate_ai_response

logger = logging.getLogger(__name__)

@dataclass
class TrainingConfig:
    """Конфигурация обучения"""
    learning_rate: float
    batch_size: int
    epochs: int
    optimizer: str
    loss_function: str
    early_stopping_patience: int = 10
    learning_rate_decay: float = 0.95
    weight_decay: float = 1e-4
    dropout_rate: float = 0.2

@dataclass
class OptimizationResult:
    """Результат оптимизации"""
    best_config: TrainingConfig
    best_accuracy: float
    best_loss: float
    optimization_time: float
    iterations: int
    improvements: List[Dict[str, Any]]

class AutonomousNeuralNetworkTrainer:
    """Автономный тренер нейросетей"""
    
    def __init__(self):
        self.training_queue = []
        self.active_training = {}
        self.optimization_history = []
        self.performance_metrics = {}
        self.auto_optimization_enabled = True
        self.continuous_learning = True
        self._setup_directories()
    
    def _setup_directories(self):
        """Создание необходимых директорий"""
        directories = [
            "/workspace/neural_networks/autonomous_training",
            "/workspace/neural_networks/optimization_results",
            "/workspace/neural_networks/performance_logs",
            "/workspace/neural_networks/auto_models"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    async def start_autonomous_training(self):
        """Запуск автономного обучения"""
        logger.info("🚀 Запуск автономного обучения нейросетей...")
        
        while self.continuous_learning:
            try:
                # Проверяем очередь обучения
                if self.training_queue:
                    task = self.training_queue.pop(0)
                    await self._process_training_task(task)
                
                # Автоматическая оптимизация
                if self.auto_optimization_enabled:
                    await self._auto_optimize_networks()
                
                # Очистка старых данных
                await self._cleanup_old_data()
                
                # Пауза между циклами
                await asyncio.sleep(30)  # 30 секунд между циклами
                
            except Exception as e:
                logger.error(f"❌ Ошибка в автономном обучении: {e}")
                await asyncio.sleep(60)  # Пауза при ошибке
    
    async def add_training_task(self, network_name: str, task_type: str = "train", 
                              config: TrainingConfig = None) -> str:
        """Добавление задачи в очередь обучения"""
        task_id = str(uuid.uuid4())
        
        task = {
            "id": task_id,
            "network_name": network_name,
            "task_type": task_type,
            "config": config,
            "created_at": datetime.now().isoformat(),
            "status": "queued",
            "priority": 1
        }
        
        self.training_queue.append(task)
        logger.info(f"📝 Добавлена задача обучения: {task_id} для сети {network_name}")
        
        return task_id
    
    async def _process_training_task(self, task: Dict[str, Any]):
        """Обработка задачи обучения"""
        try:
            task_id = task["id"]
            network_name = task["network_name"]
            task_type = task["task_type"]
            
            logger.info(f"🎯 Обработка задачи {task_id}: {task_type} для {network_name}")
            
            # Обновляем статус
            task["status"] = "processing"
            self.active_training[task_id] = task
            
            if task_type == "train":
                await self._train_network_autonomous(network_name, task.get("config"))
            elif task_type == "optimize":
                await self._optimize_network_autonomous(network_name)
            elif task_type == "evaluate":
                await self._evaluate_network_autonomous(network_name)
            
            # Завершаем задачу
            task["status"] = "completed"
            task["completed_at"] = datetime.now().isoformat()
            del self.active_training[task_id]
            
            logger.info(f"✅ Задача {task_id} завершена")
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки задачи {task_id}: {e}")
            task["status"] = "error"
            task["error"] = str(e)
            if task_id in self.active_training:
                del self.active_training[task_id]
    
    async def _train_network_autonomous(self, network_name: str, config: TrainingConfig = None):
        """Автономное обучение нейросети"""
        try:
            # Получаем информацию о сети
            networks_info = await neural_network_creator._handle_list_networks({})
            network_info = next((n for n in networks_info.get("networks", []) if n["name"] == network_name), None)
            
            if not network_info:
                raise Exception(f"Сеть {network_name} не найдена")
            
            # Создаем конфигурацию обучения
            if not config:
                config = await self._generate_optimal_config(network_info)
            
            # Обучаем сеть
            training_result = await neural_network_creator._handle_train_network({
                "network_name": network_name,
                "config": config.__dict__
            })
            
            # Сохраняем результаты
            await self._save_training_results(network_name, training_result, config)
            
            # Обновляем метрики производительности
            await self._update_performance_metrics(network_name, training_result)
            
            logger.info(f"🎓 Автономное обучение сети {network_name} завершено")
            
        except Exception as e:
            logger.error(f"❌ Ошибка автономного обучения {network_name}: {e}")
            raise
    
    async def _optimize_network_autonomous(self, network_name: str):
        """Автономная оптимизация нейросети"""
        try:
            logger.info(f"⚡ Начинаю автономную оптимизацию сети {network_name}")
            
            # Получаем текущую производительность
            current_metrics = self.performance_metrics.get(network_name, {})
            baseline_accuracy = current_metrics.get("accuracy", 0.0)
            
            # Генерируем варианты оптимизации
            optimization_configs = await self._generate_optimization_configs(network_name)
            
            best_result = None
            best_accuracy = baseline_accuracy
            improvements = []
            
            # Тестируем каждый вариант
            for i, config in enumerate(optimization_configs):
                try:
                    logger.info(f"🧪 Тестирую конфигурацию {i+1}/{len(optimization_configs)}")
                    
                    # Обучаем с новой конфигурацией
                    training_result = await neural_network_creator._handle_train_network({
                        "network_name": f"{network_name}_opt_{i}",
                        "config": config.__dict__
                    })
                    
                    if training_result.get("error"):
                        continue
                    
                    accuracy = training_result.get("final_accuracy", 0.0)
                    
                    improvement = {
                        "config": config.__dict__,
                        "accuracy": accuracy,
                        "improvement": accuracy - baseline_accuracy,
                        "timestamp": datetime.now().isoformat()
                    }
                    improvements.append(improvement)
                    
                    # Проверяем, лучше ли результат
                    if accuracy > best_accuracy:
                        best_accuracy = accuracy
                        best_result = {
                            "config": config,
                            "accuracy": accuracy,
                            "training_result": training_result
                        }
                    
                    logger.info(f"📊 Конфигурация {i+1}: точность {accuracy:.2f}% (улучшение: {accuracy - baseline_accuracy:.2f}%)")
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка тестирования конфигурации {i+1}: {e}")
                    continue
            
            # Сохраняем результаты оптимизации
            if best_result:
                optimization_result = OptimizationResult(
                    best_config=best_result["config"],
                    best_accuracy=best_result["accuracy"],
                    best_loss=best_result["training_result"].get("final_loss", 0.0),
                    optimization_time=time.time(),
                    iterations=len(optimization_configs),
                    improvements=improvements
                )
                
                await self._save_optimization_results(network_name, optimization_result)
                
                # Применяем лучшую конфигурацию к основной сети
                await self._apply_best_config(network_name, best_result["config"])
                
                logger.info(f"🏆 Оптимизация завершена! Лучшая точность: {best_accuracy:.2f}%")
            else:
                logger.warning(f"⚠️ Не удалось улучшить производительность сети {network_name}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка автономной оптимизации {network_name}: {e}")
            raise
    
    async def _generate_optimal_config(self, network_info: Dict[str, Any]) -> TrainingConfig:
        """Генерация оптимальной конфигурации обучения"""
        try:
            # Используем AI для генерации конфигурации
            ai_prompt = f"""
            Создай оптимальную конфигурацию обучения для нейросети:
            Архитектура: {json.dumps(network_info.get('architecture', {}), indent=2)}
            Текущая точность: {network_info.get('test_accuracy', 0)}%
            
            Верни JSON с полями:
            - learning_rate: скорость обучения (0.001-0.1)
            - batch_size: размер батча (16, 32, 64, 128)
            - epochs: количество эпох (10-100)
            - optimizer: оптимизатор (adam, sgd, rmsprop)
            - loss_function: функция потерь
            - early_stopping_patience: терпение early stopping (5-20)
            - learning_rate_decay: затухание скорости обучения (0.9-0.99)
            - weight_decay: регуляризация весов (1e-5 до 1e-3)
            - dropout_rate: коэффициент dropout (0.1-0.5)
            """
            
            ai_response = await generate_ai_response(ai_prompt)
            
            try:
                config_data = json.loads(ai_response)
                return TrainingConfig(**config_data)
            except (json.JSONDecodeError, TypeError):
                # Fallback конфигурация
                return TrainingConfig(
                    learning_rate=0.001,
                    batch_size=32,
                    epochs=20,
                    optimizer="adam",
                    loss_function="cross_entropy",
                    early_stopping_patience=10,
                    learning_rate_decay=0.95,
                    weight_decay=1e-4,
                    dropout_rate=0.2
                )
                
        except Exception as e:
            logger.error(f"❌ Ошибка генерации конфигурации: {e}")
            # Возвращаем базовую конфигурацию
            return TrainingConfig(
                learning_rate=0.001,
                batch_size=32,
                epochs=20,
                optimizer="adam",
                loss_function="cross_entropy"
            )
    
    async def _generate_optimization_configs(self, network_name: str) -> List[TrainingConfig]:
        """Генерация вариантов конфигурации для оптимизации"""
        configs = []
        
        # Базовые варианты
        base_configs = [
            {"learning_rate": 0.001, "batch_size": 32, "optimizer": "adam"},
            {"learning_rate": 0.01, "batch_size": 64, "optimizer": "sgd"},
            {"learning_rate": 0.0001, "batch_size": 16, "optimizer": "rmsprop"},
            {"learning_rate": 0.005, "batch_size": 128, "optimizer": "adam"},
        ]
        
        for base in base_configs:
            config = TrainingConfig(
                learning_rate=base["learning_rate"],
                batch_size=base["batch_size"],
                epochs=15,
                optimizer=base["optimizer"],
                loss_function="cross_entropy",
                early_stopping_patience=8,
                learning_rate_decay=0.9,
                weight_decay=1e-4,
                dropout_rate=0.3
            )
            configs.append(config)
        
        # Используем AI для генерации дополнительных вариантов
        try:
            ai_prompt = f"""
            Создай 3 дополнительных варианта конфигурации обучения для оптимизации нейросети {network_name}.
            Каждый вариант должен быть JSON объектом с полями:
            - learning_rate, batch_size, epochs, optimizer, loss_function, early_stopping_patience, learning_rate_decay, weight_decay, dropout_rate
            
            Верни массив из 3 JSON объектов.
            """
            
            ai_response = await generate_ai_response(ai_prompt)
            
            try:
                ai_configs = json.loads(ai_response)
                for config_data in ai_configs:
                    config = TrainingConfig(**config_data)
                    configs.append(config)
            except (json.JSONDecodeError, TypeError):
                logger.warning("⚠️ Не удалось парсить AI конфигурации")
                
        except Exception as e:
            logger.error(f"❌ Ошибка генерации AI конфигураций: {e}")
        
        return configs
    
    async def _auto_optimize_networks(self):
        """Автоматическая оптимизация всех сетей"""
        try:
            # Получаем список всех сетей
            networks_info = await neural_network_creator._handle_list_networks({})
            networks = networks_info.get("networks", [])
            
            for network in networks:
                network_name = network["name"]
                
                # Проверяем, нужна ли оптимизация
                if await self._needs_optimization(network_name):
                    logger.info(f"🔄 Автоматическая оптимизация сети {network_name}")
                    await self.add_training_task(network_name, "optimize")
                    
        except Exception as e:
            logger.error(f"❌ Ошибка автоматической оптимизации: {e}")
    
    async def _needs_optimization(self, network_name: str) -> bool:
        """Проверка, нужна ли оптимизация сети"""
        try:
            # Проверяем последнюю оптимизацию
            last_optimization = self.optimization_history[-1] if self.optimization_history else None
            
            if not last_optimization:
                return True
            
            # Проверяем время последней оптимизации
            last_time = datetime.fromisoformat(last_optimization.get("timestamp", ""))
            if datetime.now() - last_time > timedelta(hours=1):  # Оптимизируем каждый час
                return True
            
            # Проверяем производительность
            current_metrics = self.performance_metrics.get(network_name, {})
            accuracy = current_metrics.get("accuracy", 0.0)
            
            if accuracy < 0.8:  # Если точность меньше 80%
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки необходимости оптимизации: {e}")
            return False
    
    async def _save_training_results(self, network_name: str, training_result: Dict[str, Any], 
                                   config: TrainingConfig):
        """Сохранение результатов обучения"""
        try:
            results = {
                "network_name": network_name,
                "config": config.__dict__,
                "training_result": training_result,
                "timestamp": datetime.now().isoformat()
            }
            
            results_path = f"/workspace/neural_networks/autonomous_training/{network_name}_training_{int(time.time())}.json"
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Результаты обучения сохранены: {results_path}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения результатов обучения: {e}")
    
    async def _save_optimization_results(self, network_name: str, result: OptimizationResult):
        """Сохранение результатов оптимизации"""
        try:
            optimization_data = {
                "network_name": network_name,
                "best_config": result.best_config.__dict__,
                "best_accuracy": result.best_accuracy,
                "best_loss": result.best_loss,
                "optimization_time": result.optimization_time,
                "iterations": result.iterations,
                "improvements": result.improvements,
                "timestamp": datetime.now().isoformat()
            }
            
            results_path = f"/workspace/neural_networks/optimization_results/{network_name}_optimization_{int(time.time())}.json"
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump(optimization_data, f, indent=2, ensure_ascii=False)
            
            # Добавляем в историю
            self.optimization_history.append(optimization_data)
            
            logger.info(f"💾 Результаты оптимизации сохранены: {results_path}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения результатов оптимизации: {e}")
    
    async def _update_performance_metrics(self, network_name: str, training_result: Dict[str, Any]):
        """Обновление метрик производительности"""
        try:
            if network_name not in self.performance_metrics:
                self.performance_metrics[network_name] = {}
            
            self.performance_metrics[network_name].update({
                "accuracy": training_result.get("final_accuracy", 0.0),
                "loss": training_result.get("final_loss", 0.0),
                "last_training": datetime.now().isoformat(),
                "training_history": training_result.get("training_history", [])
            })
            
            # Сохраняем метрики
            metrics_path = f"/workspace/neural_networks/performance_logs/{network_name}_metrics.json"
            with open(metrics_path, 'w', encoding='utf-8') as f:
                json.dump(self.performance_metrics[network_name], f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"❌ Ошибка обновления метрик: {e}")
    
    async def _apply_best_config(self, network_name: str, config: TrainingConfig):
        """Применение лучшей конфигурации к сети"""
        try:
            # Здесь можно применить лучшую конфигурацию к основной сети
            # Пока просто логируем
            logger.info(f"🎯 Применяю лучшую конфигурацию к сети {network_name}: {config.__dict__}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка применения конфигурации: {e}")
    
    async def _cleanup_old_data(self):
        """Очистка старых данных"""
        try:
            # Очищаем старые результаты оптимизации (старше 7 дней)
            cutoff_date = datetime.now() - timedelta(days=7)
            
            old_optimizations = [
                opt for opt in self.optimization_history
                if datetime.fromisoformat(opt.get("timestamp", "")) < cutoff_date
            ]
            
            for opt in old_optimizations:
                self.optimization_history.remove(opt)
            
            if old_optimizations:
                logger.info(f"🧹 Очищено {len(old_optimizations)} старых результатов оптимизации")
            
        except Exception as e:
            logger.error(f"❌ Ошибка очистки данных: {e}")
    
    async def get_training_status(self) -> Dict[str, Any]:
        """Получение статуса обучения"""
        return {
            "training_queue": len(self.training_queue),
            "active_training": len(self.active_training),
            "optimization_history": len(self.optimization_history),
            "performance_metrics": len(self.performance_metrics),
            "auto_optimization_enabled": self.auto_optimization_enabled,
            "continuous_learning": self.continuous_learning,
            "timestamp": datetime.now().isoformat()
        }

# Глобальный экземпляр автономного тренера
autonomous_trainer = AutonomousNeuralNetworkTrainer()

async def main():
    """Главная функция"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        logger.info("🚀 Запуск автономного тренера нейросетей...")
        
        # Запускаем автономное обучение
        await autonomous_trainer.start_autonomous_training()
        
    except KeyboardInterrupt:
        logger.info("🛑 Остановка автономного тренера...")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())