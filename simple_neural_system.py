#!/usr/bin/env python3
"""
Simple Neural Network System
Упрощенная автономная нейронная система для демонстрации
"""

import asyncio
import json
import logging
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import os
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SimpleNeuralTask:
    """Простая нейронная задача"""
    id: str
    task_type: str
    priority: int
    input_data: Dict[str, Any]
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    created_at: str = ""
    completed_at: Optional[str] = None
    processing_time: float = 0.0

class SimpleNeuralAgent:
    """Простой нейронный агент"""
    
    def __init__(self):
        self.agent_id = f"neural_agent_{int(time.time())}"
        self.name = "Simple Neural Agent"
        self.status = "idle"
        self.completed_tasks = []
        self.models = {}
        
        logger.info(f"🧠 {self.name} инициализирован")
    
    async def process_task(self, task: SimpleNeuralTask) -> Dict[str, Any]:
        """Обработка задачи"""
        try:
            start_time = time.time()
            task.status = "processing"
            
            logger.info(f"🎯 Обработка задачи {task.id}: {task.task_type}")
            
            # Симуляция обработки в зависимости от типа задачи
            if task.task_type == "data_analysis":
                result = await self._analyze_data(task.input_data)
            elif task.task_type == "pattern_recognition":
                result = await self._recognize_patterns(task.input_data)
            elif task.task_type == "neural_processing":
                result = await self._neural_processing(task.input_data)
            elif task.task_type == "model_training":
                result = await self._train_model(task.input_data)
            else:
                result = {"status": "error", "error": f"Неизвестный тип задачи: {task.task_type}"}
            
            # Обновляем задачу
            task.result = result
            task.processing_time = time.time() - start_time
            task.completed_at = datetime.now().isoformat()
            
            if result.get("status") == "success":
                task.status = "completed"
                logger.info(f"✅ Задача {task.id} выполнена за {task.processing_time:.2f}с")
            else:
                task.status = "failed"
                logger.error(f"❌ Задача {task.id} не выполнена")
            
            self.completed_tasks.append(task)
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки задачи {task.id}: {e}")
            task.status = "failed"
            task.result = {"status": "error", "error": str(e)}
            return task.result
    
    async def _analyze_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ данных"""
        await asyncio.sleep(1)  # Симуляция обработки
        
        input_data = data.get("data", [])
        analysis_type = data.get("analysis_type", "basic")
        
        if not input_data:
            return {"status": "error", "error": "Нет данных для анализа"}
        
        # Простой статистический анализ
        try:
            mean = sum(input_data) / len(input_data)
            minimum = min(input_data)
            maximum = max(input_data)
            data_range = maximum - minimum
            
            return {
                "status": "success",
                "analysis_type": analysis_type,
                "statistics": {
                    "mean": round(mean, 2),
                    "min": minimum,
                    "max": maximum,
                    "range": data_range,
                    "count": len(input_data)
                },
                "insights": [
                    f"Среднее значение: {mean:.2f}",
                    f"Диапазон: {minimum} - {maximum}",
                    f"Размах: {data_range}"
                ]
            }
        except Exception as e:
            return {"status": "error", "error": f"Ошибка анализа: {e}"}
    
    async def _recognize_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Распознавание паттернов"""
        await asyncio.sleep(1.5)  # Симуляция обработки
        
        patterns = data.get("patterns", [])
        
        if not patterns:
            return {"status": "error", "error": "Нет паттернов для анализа"}
        
        # Простое распознавание повторяющихся паттернов
        pattern_counts = {}
        for pattern in patterns:
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        # Находим самый частый паттерн
        most_frequent = max(pattern_counts, key=pattern_counts.get)
        
        return {
            "status": "success",
            "total_patterns": len(patterns),
            "unique_patterns": len(pattern_counts),
            "pattern_counts": pattern_counts,
            "most_frequent_pattern": most_frequent,
            "frequency": pattern_counts[most_frequent],
            "insights": [
                f"Найдено {len(pattern_counts)} уникальных паттернов",
                f"Самый частый паттерн: '{most_frequent}' ({pattern_counts[most_frequent]} раз)",
                f"Общий коэффициент повторения: {sum(pattern_counts.values()) / len(pattern_counts):.2f}"
            ]
        }
    
    async def _neural_processing(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Нейронная обработка"""
        await asyncio.sleep(2)  # Симуляция обработки
        
        input_data = data.get("input_data", {})
        
        # Симуляция нейронной обработки
        processing_result = {
            "processed_data": input_data,
            "neural_score": 0.85,
            "confidence": 0.92,
            "processing_layers": ["input", "hidden1", "hidden2", "output"],
            "activation_function": "ReLU",
            "output_summary": "Данные успешно обработаны нейронной сетью"
        }
        
        return {
            "status": "success",
            "neural_result": processing_result,
            "insights": [
                f"Нейронная обработка завершена с уверенностью {processing_result['confidence']*100:.1f}%",
                f"Оценка качества: {processing_result['neural_score']*100:.1f}%",
                "Использована архитектура с 4 слоями"
            ]
        }
    
    async def _train_model(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Обучение модели"""
        await asyncio.sleep(3)  # Симуляция обучения
        
        model_name = data.get("model_name", "default_model")
        training_data = data.get("training_data", [])
        
        if not training_data:
            return {"status": "error", "error": "Нет данных для обучения"}
        
        # Симуляция обучения
        epochs = 10
        accuracy = 0.75 + (len(training_data) / 100) * 0.2  # Улучшение с количеством данных
        accuracy = min(0.95, accuracy)  # Максимум 95%
        
        # Сохраняем модель
        self.models[model_name] = {
            "name": model_name,
            "accuracy": accuracy,
            "training_samples": len(training_data),
            "epochs": epochs,
            "trained_at": datetime.now().isoformat(),
            "status": "trained"
        }
        
        return {
            "status": "success",
            "model_name": model_name,
            "accuracy": round(accuracy, 3),
            "training_samples": len(training_data),
            "epochs": epochs,
            "insights": [
                f"Модель '{model_name}' обучена с точностью {accuracy*100:.1f}%",
                f"Использовано {len(training_data)} образцов для обучения",
                f"Выполнено {epochs} эпох обучения"
            ]
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус агента"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status,
            "completed_tasks": len(self.completed_tasks),
            "trained_models": len(self.models),
            "models": list(self.models.keys())
        }

class SimpleNeuralSystem:
    """Простая нейронная система"""
    
    def __init__(self):
        self.running = False
        self.agent = SimpleNeuralAgent()
        self.task_queue = []
        self.completed_tasks = []
        self.performance_metrics = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "average_processing_time": 0.0,
            "uptime_start": datetime.now().isoformat()
        }
        
        logger.info("🧠 Simple Neural System инициализирована")
    
    async def start(self):
        """Запуск системы"""
        try:
            logger.info("🚀 Запуск Simple Neural System...")
            self.running = True
            
            # Запускаем основной цикл обработки
            await self._main_processing_loop()
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска: {e}")
            raise
    
    async def _main_processing_loop(self):
        """Основной цикл обработки"""
        logger.info("🔄 Запуск основного цикла обработки")
        
        while self.running:
            try:
                if self.task_queue:
                    task = self.task_queue.pop(0)
                    await self._process_task(task)
                else:
                    # Если нет задач, ждем
                    await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Ошибка в основном цикле: {e}")
                await asyncio.sleep(5)
    
    async def _process_task(self, task: SimpleNeuralTask):
        """Обработка задачи"""
        try:
            result = await self.agent.process_task(task)
            
            self.completed_tasks.append(task)
            self.performance_metrics["total_tasks"] += 1
            
            if result.get("status") == "success":
                self.performance_metrics["successful_tasks"] += 1
            else:
                self.performance_metrics["failed_tasks"] += 1
            
            # Обновляем среднее время обработки
            if self.completed_tasks:
                total_time = sum(t.processing_time for t in self.completed_tasks)
                self.performance_metrics["average_processing_time"] = total_time / len(self.completed_tasks)
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки задачи: {e}")
    
    def add_task(self, task_type: str, input_data: Dict[str, Any], priority: int = 5) -> str:
        """Добавить задачу"""
        task_id = f"task_{int(time.time())}_{len(self.task_queue)}"
        task = SimpleNeuralTask(
            id=task_id,
            task_type=task_type,
            priority=priority,
            input_data=input_data,
            created_at=datetime.now().isoformat()
        )
        
        # Вставляем задачу по приоритету
        inserted = False
        for i, existing_task in enumerate(self.task_queue):
            if task.priority > existing_task.priority:
                self.task_queue.insert(i, task)
                inserted = True
                break
        
        if not inserted:
            self.task_queue.append(task)
        
        logger.info(f"➕ Добавлена задача {task_id}: {task_type} (приоритет: {priority})")
        return task_id
    
    def get_system_status(self) -> Dict[str, Any]:
        """Получить статус системы"""
        return {
            "running": self.running,
            "agent": self.agent.get_status(),
            "task_queue_size": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "performance_metrics": self.performance_metrics
        }
    
    def stop(self):
        """Остановить систему"""
        logger.info("🛑 Остановка Simple Neural System...")
        self.running = False

# Глобальный экземпляр системы
simple_neural_system = SimpleNeuralSystem()

async def demo():
    """Демонстрация работы системы"""
    logger.info("🎯 Запуск демонстрации нейронной системы")
    
    # Добавляем тестовые задачи
    tasks = [
        ("data_analysis", {"data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "analysis_type": "statistical"}, 8),
        ("pattern_recognition", {"patterns": ["ABAB", "CDCD", "EFEF", "ABAB", "GHGH"]}, 7),
        ("neural_processing", {"input_data": {"text": "Анализ нейронной сети", "numbers": [1, 2, 3]}}, 9),
        ("model_training", {"model_name": "demo_model", "training_data": [{"x": 1, "y": 2}, {"x": 2, "y": 4}]}, 6)
    ]
    
    for task_type, input_data, priority in tasks:
        simple_neural_system.add_task(task_type, input_data, priority)
    
    # Запускаем систему в фоне
    system_task = asyncio.create_task(simple_neural_system.start())
    
    # Мониторим выполнение
    start_time = time.time()
    while time.time() - start_time < 30:  # Работаем 30 секунд
        status = simple_neural_system.get_system_status()
        
        logger.info(f"📊 Статус: Очередь={status['task_queue_size']}, "
                   f"Выполнено={status['completed_tasks']}, "
                   f"Успешность={status['performance_metrics']['successful_tasks']}/{status['performance_metrics']['total_tasks']}")
        
        if status['task_queue_size'] == 0 and status['completed_tasks'] >= len(tasks):
            logger.info("✅ Все задачи выполнены!")
            break
        
        await asyncio.sleep(3)
    
    # Останавливаем систему
    simple_neural_system.stop()
    
    # Показываем итоговый отчет
    final_status = simple_neural_system.get_system_status()
    logger.info("📋 Итоговый отчет:")
    logger.info(f"  Всего задач: {final_status['performance_metrics']['total_tasks']}")
    logger.info(f"  Успешных: {final_status['performance_metrics']['successful_tasks']}")
    logger.info(f"  Неуспешных: {final_status['performance_metrics']['failed_tasks']}")
    logger.info(f"  Среднее время: {final_status['performance_metrics']['average_processing_time']:.2f}с")
    logger.info(f"  Обученных моделей: {final_status['agent']['trained_models']}")
    
    if final_status['agent']['models']:
        logger.info(f"  Модели: {', '.join(final_status['agent']['models'])}")
    
    # Показываем результаты последних задач
    logger.info("🔍 Результаты задач:")
    for task in simple_neural_system.completed_tasks[-3:]:  # Последние 3 задачи
        if task.result and task.result.get("status") == "success":
            insights = task.result.get("insights", [])
            logger.info(f"  {task.task_type}: {insights[0] if insights else 'Выполнено'}")

if __name__ == "__main__":
    asyncio.run(demo())