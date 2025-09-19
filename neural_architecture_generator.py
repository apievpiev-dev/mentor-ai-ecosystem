#!/usr/bin/env python3
"""
Генератор архитектур нейросетей
Автоматически генерирует оптимальные архитектуры для различных задач
"""

import asyncio
import json
import logging
import time
import uuid
import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import random
from pathlib import Path

from ai_engine import generate_ai_response
from neural_network_creator_agent import NetworkArchitecture

logger = logging.getLogger(__name__)

@dataclass
class ArchitectureTemplate:
    """Шаблон архитектуры"""
    name: str
    description: str
    task_type: str  # classification, regression, generation, vision, nlp
    input_size: int
    output_size: int
    layers: List[Dict[str, Any]]
    activation_functions: List[str]
    optimizer: str
    loss_function: str
    learning_rate: float
    batch_size: int
    epochs: int
    complexity_score: float  # 1-10
    performance_estimate: float  # 0-1

@dataclass
class ArchitectureSearchResult:
    """Результат поиска архитектуры"""
    best_architecture: NetworkArchitecture
    search_time: float
    iterations: int
    tested_architectures: List[NetworkArchitecture]
    performance_ranking: List[Tuple[NetworkArchitecture, float]]

class NeuralArchitectureGenerator:
    """Генератор архитектур нейросетей"""
    
    def __init__(self):
        self.architecture_templates = {}
        self.performance_database = {}
        self.search_history = []
        self._setup_templates()
        self._setup_directories()
    
    def _setup_directories(self):
        """Создание необходимых директорий"""
        directories = [
            "/workspace/neural_networks/architectures",
            "/workspace/neural_networks/architecture_templates",
            "/workspace/neural_networks/search_results",
            "/workspace/neural_networks/performance_db"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _setup_templates(self):
        """Настройка шаблонов архитектур"""
        # Классификация
        self.architecture_templates["simple_classifier"] = ArchitectureTemplate(
            name="Simple Classifier",
            description="Простая архитектура для классификации",
            task_type="classification",
            input_size=784,
            output_size=10,
            layers=[
                {"type": "linear", "input_size": 784, "output_size": 128, "activation": "relu"},
                {"type": "linear", "input_size": 128, "output_size": 64, "activation": "relu"},
                {"type": "linear", "input_size": 64, "output_size": 10, "activation": "softmax"}
            ],
            activation_functions=["relu", "relu", "softmax"],
            optimizer="adam",
            loss_function="cross_entropy",
            learning_rate=0.001,
            batch_size=32,
            epochs=20,
            complexity_score=3.0,
            performance_estimate=0.85
        )
        
        # Регрессия
        self.architecture_templates["regression_net"] = ArchitectureTemplate(
            name="Regression Network",
            description="Архитектура для регрессии",
            task_type="regression",
            input_size=100,
            output_size=1,
            layers=[
                {"type": "linear", "input_size": 100, "output_size": 64, "activation": "relu"},
                {"type": "linear", "input_size": 64, "output_size": 32, "activation": "relu"},
                {"type": "linear", "input_size": 32, "output_size": 1, "activation": "linear"}
            ],
            activation_functions=["relu", "relu", "linear"],
            optimizer="adam",
            loss_function="mse",
            learning_rate=0.001,
            batch_size=32,
            epochs=50,
            complexity_score=2.5,
            performance_estimate=0.80
        )
        
        # Генерация
        self.architecture_templates["generator_net"] = ArchitectureTemplate(
            name="Generator Network",
            description="Архитектура для генерации данных",
            task_type="generation",
            input_size=100,
            output_size=784,
            layers=[
                {"type": "linear", "input_size": 100, "output_size": 256, "activation": "relu"},
                {"type": "linear", "input_size": 256, "output_size": 512, "activation": "relu"},
                {"type": "linear", "input_size": 512, "output_size": 784, "activation": "sigmoid"}
            ],
            activation_functions=["relu", "relu", "sigmoid"],
            optimizer="adam",
            loss_function="bce",
            learning_rate=0.0002,
            batch_size=64,
            epochs=100,
            complexity_score=4.0,
            performance_estimate=0.75
        )
        
        # Компьютерное зрение
        self.architecture_templates["cnn_classifier"] = ArchitectureTemplate(
            name="CNN Classifier",
            description="Сверточная сеть для классификации изображений",
            task_type="vision",
            input_size=3072,  # 32x32x3
            output_size=10,
            layers=[
                {"type": "conv2d", "in_channels": 3, "out_channels": 32, "kernel_size": 3, "activation": "relu"},
                {"type": "maxpool2d", "kernel_size": 2},
                {"type": "conv2d", "in_channels": 32, "out_channels": 64, "kernel_size": 3, "activation": "relu"},
                {"type": "maxpool2d", "kernel_size": 2},
                {"type": "linear", "input_size": 64*6*6, "output_size": 128, "activation": "relu"},
                {"type": "linear", "input_size": 128, "output_size": 10, "activation": "softmax"}
            ],
            activation_functions=["relu", "relu", "relu", "softmax"],
            optimizer="adam",
            loss_function="cross_entropy",
            learning_rate=0.001,
            batch_size=32,
            epochs=30,
            complexity_score=6.0,
            performance_estimate=0.90
        )
        
        # NLP
        self.architecture_templates["rnn_classifier"] = ArchitectureTemplate(
            name="RNN Classifier",
            description="Рекуррентная сеть для обработки текста",
            task_type="nlp",
            input_size=1000,
            output_size=5,
            layers=[
                {"type": "embedding", "vocab_size": 10000, "embedding_dim": 128},
                {"type": "lstm", "input_size": 128, "hidden_size": 64, "num_layers": 2},
                {"type": "linear", "input_size": 64, "output_size": 32, "activation": "relu"},
                {"type": "linear", "input_size": 32, "output_size": 5, "activation": "softmax"}
            ],
            activation_functions=["relu", "softmax"],
            optimizer="adam",
            loss_function="cross_entropy",
            learning_rate=0.001,
            batch_size=16,
            epochs=25,
            complexity_score=7.0,
            performance_estimate=0.88
        )
        
        logger.info(f"✅ Загружено {len(self.architecture_templates)} шаблонов архитектур")
    
    async def generate_architecture(self, task_description: str, 
                                 task_type: str = None,
                                 input_size: int = None,
                                 output_size: int = None,
                                 complexity: str = "medium") -> NetworkArchitecture:
        """Генерация архитектуры нейросети"""
        try:
            logger.info(f"🧠 Генерация архитектуры для: {task_description}")
            
            # Определяем тип задачи
            if not task_type:
                task_type = await self._detect_task_type(task_description)
            
            # Определяем размеры входа и выхода
            if not input_size or not output_size:
                input_size, output_size = await self._estimate_io_sizes(task_description, task_type)
            
            # Выбираем базовый шаблон
            base_template = await self._select_base_template(task_type, complexity)
            
            # Адаптируем шаблон под задачу
            adapted_architecture = await self._adapt_template(base_template, task_description, 
                                                           input_size, output_size, complexity)
            
            # Используем AI для улучшения архитектуры
            improved_architecture = await self._improve_with_ai(adapted_architecture, task_description)
            
            # Сохраняем результат
            await self._save_architecture(improved_architecture)
            
            logger.info(f"✅ Архитектура сгенерирована: {improved_architecture.name}")
            return improved_architecture
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации архитектуры: {e}")
            raise
    
    async def _detect_task_type(self, task_description: str) -> str:
        """Определение типа задачи"""
        try:
            # Используем AI для определения типа задачи
            ai_prompt = f"""
            Определи тип задачи машинного обучения на основе описания:
            "{task_description}"
            
            Верни только одно слово из списка:
            - classification (классификация)
            - regression (регрессия) 
            - generation (генерация)
            - vision (компьютерное зрение)
            - nlp (обработка естественного языка)
            """
            
            ai_response = await generate_ai_response(ai_prompt)
            task_type = ai_response.strip().lower()
            
            # Проверяем валидность
            valid_types = ["classification", "regression", "generation", "vision", "nlp"]
            if task_type not in valid_types:
                task_type = "classification"  # По умолчанию
            
            logger.info(f"🎯 Определен тип задачи: {task_type}")
            return task_type
            
        except Exception as e:
            logger.error(f"❌ Ошибка определения типа задачи: {e}")
            return "classification"
    
    async def _estimate_io_sizes(self, task_description: str, task_type: str) -> Tuple[int, int]:
        """Оценка размеров входа и выхода"""
        try:
            # Используем AI для оценки размеров
            ai_prompt = f"""
            Оцени размеры входа и выхода для задачи:
            "{task_description}"
            Тип задачи: {task_type}
            
            Верни JSON с полями:
            - input_size: размер входных данных (число)
            - output_size: размер выходных данных (число)
            
            Примеры:
            - Классификация изображений 28x28: input_size=784, output_size=10
            - Регрессия с 50 признаками: input_size=50, output_size=1
            - Генерация текста: input_size=100, output_size=1000
            """
            
            ai_response = await generate_ai_response(ai_prompt)
            
            try:
                sizes = json.loads(ai_response)
                input_size = sizes.get("input_size", 784)
                output_size = sizes.get("output_size", 10)
            except json.JSONDecodeError:
                # Fallback значения
                if task_type == "classification":
                    input_size, output_size = 784, 10
                elif task_type == "regression":
                    input_size, output_size = 100, 1
                elif task_type == "generation":
                    input_size, output_size = 100, 784
                elif task_type == "vision":
                    input_size, output_size = 3072, 10
                elif task_type == "nlp":
                    input_size, output_size = 1000, 5
                else:
                    input_size, output_size = 784, 10
            
            logger.info(f"📏 Оценены размеры: вход={input_size}, выход={output_size}")
            return input_size, output_size
            
        except Exception as e:
            logger.error(f"❌ Ошибка оценки размеров: {e}")
            return 784, 10
    
    async def _select_base_template(self, task_type: str, complexity: str) -> ArchitectureTemplate:
        """Выбор базового шаблона"""
        try:
            # Фильтруем шаблоны по типу задачи
            suitable_templates = [
                template for template in self.architecture_templates.values()
                if template.task_type == task_type
            ]
            
            if not suitable_templates:
                # Если нет подходящих шаблонов, берем простой классификатор
                suitable_templates = [self.architecture_templates["simple_classifier"]]
            
            # Выбираем по сложности
            if complexity == "simple":
                selected = min(suitable_templates, key=lambda t: t.complexity_score)
            elif complexity == "complex":
                selected = max(suitable_templates, key=lambda t: t.complexity_score)
            else:  # medium
                selected = suitable_templates[len(suitable_templates) // 2]
            
            logger.info(f"📋 Выбран шаблон: {selected.name}")
            return selected
            
        except Exception as e:
            logger.error(f"❌ Ошибка выбора шаблона: {e}")
            return self.architecture_templates["simple_classifier"]
    
    async def _adapt_template(self, template: ArchitectureTemplate, task_description: str,
                            input_size: int, output_size: int, complexity: str) -> NetworkArchitecture:
        """Адаптация шаблона под задачу"""
        try:
            # Адаптируем размеры слоев
            adapted_layers = []
            prev_size = input_size
            
            for i, layer in enumerate(template.layers):
                if layer["type"] == "linear":
                    # Адаптируем размеры
                    if i == len(template.layers) - 1:  # Последний слой
                        layer_size = output_size
                    else:
                        # Масштабируем скрытые слои
                        original_size = layer["output_size"]
                        scale_factor = input_size / template.input_size
                        layer_size = max(int(original_size * scale_factor), 32)
                    
                    adapted_layers.append({
                        "type": "linear",
                        "input_size": prev_size,
                        "output_size": layer_size,
                        "activation": layer["activation"]
                    })
                    prev_size = layer_size
                else:
                    # Копируем другие типы слоев как есть
                    adapted_layers.append(layer.copy())
            
            # Адаптируем гиперпараметры
            learning_rate = template.learning_rate
            batch_size = template.batch_size
            epochs = template.epochs
            
            if complexity == "simple":
                learning_rate *= 1.5
                batch_size = min(batch_size * 2, 128)
                epochs = max(epochs // 2, 10)
            elif complexity == "complex":
                learning_rate *= 0.5
                batch_size = max(batch_size // 2, 16)
                epochs = min(epochs * 2, 200)
            
            # Создаем архитектуру
            architecture = NetworkArchitecture(
                name=f"generated_{uuid.uuid4().hex[:8]}",
                layers=adapted_layers,
                input_size=input_size,
                output_size=output_size,
                activation_functions=template.activation_functions,
                optimizer=template.optimizer,
                loss_function=template.loss_function,
                learning_rate=learning_rate,
                batch_size=batch_size,
                epochs=epochs,
                created_at=datetime.now().isoformat()
            )
            
            logger.info(f"🔧 Шаблон адаптирован под задачу")
            return architecture
            
        except Exception as e:
            logger.error(f"❌ Ошибка адаптации шаблона: {e}")
            raise
    
    async def _improve_with_ai(self, architecture: NetworkArchitecture, 
                             task_description: str) -> NetworkArchitecture:
        """Улучшение архитектуры с помощью AI"""
        try:
            # Используем AI для улучшения архитектуры
            ai_prompt = f"""
            Улучши архитектуру нейросети для задачи: {task_description}
            
            Текущая архитектура:
            {json.dumps(asdict(architecture), indent=2)}
            
            Предложи улучшения и верни новую архитектуру в JSON формате:
            - name: название архитектуры
            - layers: список слоев
            - input_size: размер входа
            - output_size: размер выхода
            - activation_functions: функции активации
            - optimizer: оптимизатор
            - loss_function: функция потерь
            - learning_rate: скорость обучения
            - batch_size: размер батча
            - epochs: количество эпох
            - created_at: время создания
            
            Учти:
            - Производительность
            - Скорость обучения
            - Стабильность
            - Регуляризацию
            """
            
            ai_response = await generate_ai_response(ai_prompt)
            
            try:
                # Парсим улучшенную архитектуру
                improved_data = json.loads(ai_response)
                improved_architecture = NetworkArchitecture(**improved_data)
                
                logger.info("🤖 Архитектура улучшена с помощью AI")
                return improved_architecture
                
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"⚠️ Не удалось парсить AI улучшения: {e}")
                return architecture
                
        except Exception as e:
            logger.error(f"❌ Ошибка улучшения с AI: {e}")
            return architecture
    
    async def search_optimal_architecture(self, task_description: str, 
                                        search_iterations: int = 10) -> ArchitectureSearchResult:
        """Поиск оптимальной архитектуры"""
        try:
            logger.info(f"🔍 Поиск оптимальной архитектуры (итераций: {search_iterations})")
            
            start_time = time.time()
            tested_architectures = []
            performance_scores = []
            
            # Генерируем различные архитектуры
            for i in range(search_iterations):
                try:
                    # Генерируем архитектуру
                    complexity = random.choice(["simple", "medium", "complex"])
                    architecture = await self.generate_architecture(
                        task_description, complexity=complexity
                    )
                    
                    # Тестируем производительность (симуляция)
                    performance = await self._simulate_performance(architecture, task_description)
                    
                    tested_architectures.append(architecture)
                    performance_scores.append(performance)
                    
                    logger.info(f"📊 Итерация {i+1}/{search_iterations}: производительность {performance:.3f}")
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка в итерации {i+1}: {e}")
                    continue
            
            # Находим лучшую архитектуру
            if tested_architectures:
                best_idx = np.argmax(performance_scores)
                best_architecture = tested_architectures[best_idx]
                best_performance = performance_scores[best_idx]
                
                # Создаем рейтинг
                performance_ranking = list(zip(tested_architectures, performance_scores))
                performance_ranking.sort(key=lambda x: x[1], reverse=True)
                
                search_time = time.time() - start_time
                
                result = ArchitectureSearchResult(
                    best_architecture=best_architecture,
                    search_time=search_time,
                    iterations=len(tested_architectures),
                    tested_architectures=tested_architectures,
                    performance_ranking=performance_ranking
                )
                
                # Сохраняем результат
                await self._save_search_result(result)
                
                logger.info(f"🏆 Найдена оптимальная архитектура: производительность {best_performance:.3f}")
                return result
            else:
                raise Exception("Не удалось сгенерировать ни одной архитектуры")
                
        except Exception as e:
            logger.error(f"❌ Ошибка поиска оптимальной архитектуры: {e}")
            raise
    
    async def _simulate_performance(self, architecture: NetworkArchitecture, 
                                  task_description: str) -> float:
        """Симуляция производительности архитектуры"""
        try:
            # Простая эвристика для оценки производительности
            base_score = 0.5
            
            # Оценка по количеству слоев
            layer_count = len(architecture.layers)
            if 2 <= layer_count <= 5:
                base_score += 0.1
            elif layer_count > 5:
                base_score += 0.05
            
            # Оценка по размеру слоев
            total_neurons = sum(layer.get("output_size", 0) for layer in architecture.layers)
            if 100 <= total_neurons <= 1000:
                base_score += 0.1
            elif total_neurons > 1000:
                base_score += 0.05
            
            # Оценка по гиперпараметрам
            if 0.0001 <= architecture.learning_rate <= 0.01:
                base_score += 0.1
            
            if 16 <= architecture.batch_size <= 128:
                base_score += 0.1
            
            # Добавляем случайность для разнообразия
            random_factor = random.uniform(-0.1, 0.1)
            final_score = min(max(base_score + random_factor, 0.0), 1.0)
            
            return final_score
            
        except Exception as e:
            logger.error(f"❌ Ошибка симуляции производительности: {e}")
            return 0.5
    
    async def _save_architecture(self, architecture: NetworkArchitecture):
        """Сохранение архитектуры"""
        try:
            arch_path = f"/workspace/neural_networks/architectures/{architecture.name}_architecture.json"
            with open(arch_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(architecture), f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Архитектура сохранена: {arch_path}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения архитектуры: {e}")
    
    async def _save_search_result(self, result: ArchitectureSearchResult):
        """Сохранение результата поиска"""
        try:
            result_data = {
                "best_architecture": asdict(result.best_architecture),
                "search_time": result.search_time,
                "iterations": result.iterations,
                "tested_architectures": [asdict(arch) for arch in result.tested_architectures],
                "performance_ranking": [
                    {"architecture": asdict(arch), "performance": perf}
                    for arch, perf in result.performance_ranking
                ],
                "timestamp": datetime.now().isoformat()
            }
            
            result_path = f"/workspace/neural_networks/search_results/search_{int(time.time())}.json"
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Результат поиска сохранен: {result_path}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения результата поиска: {e}")
    
    async def get_available_templates(self) -> Dict[str, Any]:
        """Получение доступных шаблонов"""
        try:
            templates_info = []
            
            for name, template in self.architecture_templates.items():
                templates_info.append({
                    "name": template.name,
                    "description": template.description,
                    "task_type": template.task_type,
                    "complexity_score": template.complexity_score,
                    "performance_estimate": template.performance_estimate
                })
            
            return {
                "templates": templates_info,
                "total_templates": len(templates_info)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения шаблонов: {e}")
            return {"error": str(e)}

# Глобальный экземпляр генератора архитектур
architecture_generator = NeuralArchitectureGenerator()

async def main():
    """Главная функция"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        logger.info("🧠 Генератор архитектур нейросетей запущен")
        
        # Тестируем генерацию
        logger.info("🧪 Тестирование генерации архитектур...")
        
        # Генерируем архитектуру для классификации
        architecture = await architecture_generator.generate_architecture(
            "Классификация изображений рукописных цифр MNIST",
            complexity="medium"
        )
        
        logger.info(f"✅ Сгенерирована архитектура: {architecture.name}")
        logger.info(f"📊 Слоев: {len(architecture.layers)}")
        logger.info(f"🎯 Вход: {architecture.input_size}, Выход: {architecture.output_size}")
        
        # Тестируем поиск оптимальной архитектуры
        logger.info("🔍 Тестирование поиска оптимальной архитектуры...")
        
        search_result = await architecture_generator.search_optimal_architecture(
            "Регрессия для предсказания цен на недвижимость",
            search_iterations=5
        )
        
        logger.info(f"🏆 Найдена оптимальная архитектура: {search_result.best_architecture.name}")
        logger.info(f"⏱️ Время поиска: {search_result.search_time:.2f} сек")
        logger.info(f"🔄 Протестировано архитектур: {search_result.iterations}")
        
        # Запускаем в бесконечном цикле
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Остановка генератора архитектур...")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())