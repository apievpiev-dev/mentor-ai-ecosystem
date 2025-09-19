#!/usr/bin/env python3
"""
Агент Neural Network Creator
Создает, обучает и оптимизирует нейросети автоматически
"""

import asyncio
import json
import logging
import subprocess
import time
import uuid
import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

from multi_agent_system import BaseAgent, AgentType
from ai_engine import ai_engine, generate_ai_response

logger = logging.getLogger(__name__)

@dataclass
class NetworkArchitecture:
    """Архитектура нейросети"""
    name: str
    layers: List[Dict[str, Any]]
    input_size: int
    output_size: int
    activation_functions: List[str]
    optimizer: str
    loss_function: str
    learning_rate: float
    batch_size: int
    epochs: int
    created_at: str
    performance_metrics: Dict[str, float] = None

@dataclass
class TrainingData:
    """Данные для обучения"""
    name: str
    data_type: str  # classification, regression, generation
    input_shape: Tuple[int, ...]
    output_shape: Tuple[int, ...]
    samples_count: int
    features: List[str]
    target_column: str
    data_path: str

class NeuralNetworkCreatorAgent(BaseAgent):
    """Агент для создания нейросетей"""
    
    def __init__(self, agent_id: str = None):
        super().__init__(
            agent_id or str(uuid.uuid4()),
            AgentType.SYSTEM_ADMIN,
            "Neural Network Creator",
            "Создает, обучает и оптимизирует нейросети автоматически"
        )
        self.created_networks = {}
        self.training_data = {}
        self.performance_history = []
        self._setup_skills()
        self._setup_directories()
    
    def _setup_skills(self):
        """Настройка навыков агента"""
        self.add_skill("create_network", self._handle_create_network)
        self.add_skill("train_network", self._handle_train_network)
        self.add_skill("optimize_network", self._handle_optimize_network)
        self.add_skill("generate_architecture", self._handle_generate_architecture)
        self.add_skill("evaluate_network", self._handle_evaluate_network)
        self.add_skill("deploy_network", self._handle_deploy_network)
        self.add_skill("list_networks", self._handle_list_networks)
        self.add_skill("create_training_data", self._handle_create_training_data)
        self.add_skill("visualize_network", self._handle_visualize_network)
        self.add_skill("auto_create_network", self._handle_auto_create_network)
    
    def _setup_directories(self):
        """Создание необходимых директорий"""
        directories = [
            "/workspace/neural_networks",
            "/workspace/neural_networks/models",
            "/workspace/neural_networks/data",
            "/workspace/neural_networks/visualizations",
            "/workspace/neural_networks/deployments",
            "/workspace/neural_networks/logs"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    async def _handle_create_network(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Создание новой нейросети"""
        try:
            network_name = content.get("name", f"network_{uuid.uuid4().hex[:8]}")
            network_type = content.get("type", "classification")
            input_size = content.get("input_size", 784)
            output_size = content.get("output_size", 10)
            hidden_layers = content.get("hidden_layers", [128, 64])
            
            # Генерируем архитектуру
            architecture = await self._generate_network_architecture(
                network_name, network_type, input_size, output_size, hidden_layers
            )
            
            # Создаем модель PyTorch
            model = self._create_pytorch_model(architecture)
            
            # Сохраняем архитектуру
            self.created_networks[network_name] = {
                "architecture": architecture,
                "model": model,
                "status": "created",
                "created_at": datetime.now().isoformat(),
                "training_history": []
            }
            
            # Сохраняем в файл
            await self._save_network(network_name)
            
            return {
                "message": f"Нейросеть '{network_name}' успешно создана",
                "network_name": network_name,
                "architecture": asdict(architecture),
                "status": "created"
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания нейросети: {e}")
            return {"error": str(e)}
    
    async def _handle_auto_create_network(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Автоматическое создание нейросети с AI"""
        try:
            task_description = content.get("task", "")
            if not task_description:
                return {"error": "Не указано описание задачи"}
            
            # Используем AI для генерации архитектуры
            ai_prompt = f"""
            Создай архитектуру нейросети для задачи: {task_description}
            
            Верни JSON с полями:
            - name: название сети
            - type: тип задачи (classification/regression/generation)
            - input_size: размер входа
            - output_size: размер выхода
            - hidden_layers: список размеров скрытых слоев
            - activation_functions: список функций активации
            - optimizer: оптимизатор
            - loss_function: функция потерь
            - learning_rate: скорость обучения
            - batch_size: размер батча
            - epochs: количество эпох
            """
            
            ai_response = await generate_ai_response(ai_prompt)
            
            try:
                # Парсим JSON ответ от AI
                network_config = json.loads(ai_response)
            except json.JSONDecodeError:
                # Если AI не вернул валидный JSON, создаем базовую архитектуру
                network_config = {
                    "name": f"auto_network_{uuid.uuid4().hex[:8]}",
                    "type": "classification",
                    "input_size": 784,
                    "output_size": 10,
                    "hidden_layers": [128, 64],
                    "activation_functions": ["relu", "relu"],
                    "optimizer": "adam",
                    "loss_function": "cross_entropy",
                    "learning_rate": 0.001,
                    "batch_size": 32,
                    "epochs": 10
                }
            
            # Создаем нейросеть
            result = await self._handle_create_network(network_config)
            
            return {
                "message": "Автоматическое создание нейросети завершено",
                "ai_suggestion": ai_response,
                "created_network": result
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка автоматического создания: {e}")
            return {"error": str(e)}
    
    async def _generate_network_architecture(self, name: str, network_type: str, 
                                           input_size: int, output_size: int, 
                                           hidden_layers: List[int]) -> NetworkArchitecture:
        """Генерация архитектуры нейросети"""
        
        # Определяем функции активации
        activation_functions = ["relu"] * len(hidden_layers)
        if network_type == "classification":
            activation_functions.append("softmax")
        elif network_type == "regression":
            activation_functions.append("linear")
        
        # Определяем функцию потерь
        if network_type == "classification":
            loss_function = "cross_entropy"
        elif network_type == "regression":
            loss_function = "mse"
        else:
            loss_function = "mse"
        
        # Создаем слои
        layers = []
        prev_size = input_size
        
        for i, layer_size in enumerate(hidden_layers):
            layers.append({
                "type": "linear",
                "input_size": prev_size,
                "output_size": layer_size,
                "activation": activation_functions[i]
            })
            prev_size = layer_size
        
        # Выходной слой
        layers.append({
            "type": "linear",
            "input_size": prev_size,
            "output_size": output_size,
            "activation": activation_functions[-1]
        })
        
        return NetworkArchitecture(
            name=name,
            layers=layers,
            input_size=input_size,
            output_size=output_size,
            activation_functions=activation_functions,
            optimizer="adam",
            loss_function=loss_function,
            learning_rate=0.001,
            batch_size=32,
            epochs=10,
            created_at=datetime.now().isoformat()
        )
    
    def _create_pytorch_model(self, architecture: NetworkArchitecture) -> nn.Module:
        """Создание модели PyTorch"""
        
        class CustomNetwork(nn.Module):
            def __init__(self, arch: NetworkArchitecture):
                super(CustomNetwork, self).__init__()
                self.layers = nn.ModuleList()
                
                for layer_config in arch.layers:
                    if layer_config["type"] == "linear":
                        self.layers.append(
                            nn.Linear(layer_config["input_size"], layer_config["output_size"])
                        )
                
                self.activation_functions = arch.activation_functions
            
            def forward(self, x):
                for i, layer in enumerate(self.layers):
                    x = layer(x)
                    if i < len(self.activation_functions) - 1:  # Не применяем активацию к последнему слою
                        if self.activation_functions[i] == "relu":
                            x = torch.relu(x)
                        elif self.activation_functions[i] == "sigmoid":
                            x = torch.sigmoid(x)
                        elif self.activation_functions[i] == "tanh":
                            x = torch.tanh(x)
                
                # Применяем финальную активацию
                if self.activation_functions[-1] == "softmax":
                    x = torch.softmax(x, dim=1)
                elif self.activation_functions[-1] == "sigmoid":
                    x = torch.sigmoid(x)
                
                return x
        
        return CustomNetwork(architecture)
    
    async def _handle_train_network(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Обучение нейросети"""
        try:
            network_name = content.get("network_name", "")
            if network_name not in self.created_networks:
                return {"error": f"Нейросеть '{network_name}' не найдена"}
            
            # Получаем данные для обучения
            data_name = content.get("data_name", "default")
            if data_name not in self.training_data:
                # Создаем тестовые данные
                await self._create_test_data(data_name)
            
            training_data = self.training_data[data_name]
            network_info = self.created_networks[network_name]
            model = network_info["model"]
            architecture = network_info["architecture"]
            
            # Создаем тестовые данные
            X_train, y_train, X_test, y_test = self._generate_test_data(
                training_data.input_shape, training_data.output_shape, training_data.samples_count
            )
            
            # Настраиваем обучение
            criterion = self._get_loss_function(architecture.loss_function)
            optimizer = self._get_optimizer(model, architecture.optimizer, architecture.learning_rate)
            
            # Обучение
            training_history = []
            model.train()
            
            for epoch in range(architecture.epochs):
                epoch_loss = 0.0
                correct = 0
                total = 0
                
                # Батчи
                for i in range(0, len(X_train), architecture.batch_size):
                    batch_X = X_train[i:i+architecture.batch_size]
                    batch_y = y_train[i:i+architecture.batch_size]
                    
                    optimizer.zero_grad()
                    outputs = model(batch_X)
                    loss = criterion(outputs, batch_y)
                    loss.backward()
                    optimizer.step()
                    
                    epoch_loss += loss.item()
                    _, predicted = torch.max(outputs.data, 1)
                    total += batch_y.size(0)
                    correct += (predicted == batch_y).sum().item()
                
                accuracy = 100 * correct / total
                avg_loss = epoch_loss / (len(X_train) // architecture.batch_size)
                
                training_history.append({
                    "epoch": epoch + 1,
                    "loss": avg_loss,
                    "accuracy": accuracy
                })
                
                logger.info(f"Epoch {epoch+1}/{architecture.epochs}, Loss: {avg_loss:.4f}, Accuracy: {accuracy:.2f}%")
            
            # Тестирование
            model.eval()
            with torch.no_grad():
                test_outputs = model(X_test)
                test_loss = criterion(test_outputs, y_test).item()
                _, predicted = torch.max(test_outputs.data, 1)
                test_accuracy = 100 * (predicted == y_test).sum().item() / y_test.size(0)
            
            # Обновляем информацию о сети
            network_info["training_history"] = training_history
            network_info["status"] = "trained"
            network_info["test_accuracy"] = test_accuracy
            network_info["test_loss"] = test_loss
            
            # Сохраняем обученную модель
            await self._save_trained_model(network_name, model)
            
            return {
                "message": f"Обучение нейросети '{network_name}' завершено",
                "final_accuracy": test_accuracy,
                "final_loss": test_loss,
                "training_history": training_history
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка обучения нейросети: {e}")
            return {"error": str(e)}
    
    def _generate_test_data(self, input_shape: Tuple[int, ...], output_shape: Tuple[int, ...], 
                           samples_count: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """Генерация тестовых данных"""
        
        # Создаем случайные данные
        X = torch.randn(samples_count, input_shape[0])
        
        # Создаем случайные метки
        if len(output_shape) == 1:
            y = torch.randint(0, output_shape[0], (samples_count,))
        else:
            y = torch.randn(samples_count, output_shape[0])
        
        # Разделяем на train/test
        split_idx = int(0.8 * samples_count)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        return X_train, y_train, X_test, y_test
    
    def _get_loss_function(self, loss_name: str):
        """Получение функции потерь"""
        if loss_name == "cross_entropy":
            return nn.CrossEntropyLoss()
        elif loss_name == "mse":
            return nn.MSELoss()
        elif loss_name == "bce":
            return nn.BCELoss()
        else:
            return nn.CrossEntropyLoss()
    
    def _get_optimizer(self, model: nn.Module, optimizer_name: str, learning_rate: float):
        """Получение оптимизатора"""
        if optimizer_name == "adam":
            return optim.Adam(model.parameters(), lr=learning_rate)
        elif optimizer_name == "sgd":
            return optim.SGD(model.parameters(), lr=learning_rate)
        elif optimizer_name == "rmsprop":
            return optim.RMSprop(model.parameters(), lr=learning_rate)
        else:
            return optim.Adam(model.parameters(), lr=learning_rate)
    
    async def _handle_visualize_network(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Визуализация нейросети"""
        try:
            network_name = content.get("network_name", "")
            if network_name not in self.created_networks:
                return {"error": f"Нейросеть '{network_name}' не найдена"}
            
            network_info = self.created_networks[network_name]
            architecture = network_info["architecture"]
            
            # Создаем визуализацию архитектуры
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # График архитектуры
            layer_sizes = [architecture.input_size]
            for layer in architecture.layers:
                layer_sizes.append(layer["output_size"])
            
            ax1.bar(range(len(layer_sizes)), layer_sizes, color='skyblue', alpha=0.7)
            ax1.set_xlabel('Слои')
            ax1.set_ylabel('Количество нейронов')
            ax1.set_title(f'Архитектура сети: {network_name}')
            ax1.set_xticks(range(len(layer_sizes)))
            ax1.set_xticklabels(['Вход'] + [f'Слой {i+1}' for i in range(len(layer_sizes)-2)] + ['Выход'])
            
            # График обучения
            if network_info["training_history"]:
                history = network_info["training_history"]
                epochs = [h["epoch"] for h in history]
                losses = [h["loss"] for h in history]
                accuracies = [h["accuracy"] for h in history]
                
                ax2_twin = ax2.twinx()
                line1 = ax2.plot(epochs, losses, 'b-', label='Потери', linewidth=2)
                line2 = ax2_twin.plot(epochs, accuracies, 'r-', label='Точность', linewidth=2)
                
                ax2.set_xlabel('Эпоха')
                ax2.set_ylabel('Потери', color='b')
                ax2_twin.set_ylabel('Точность (%)', color='r')
                ax2.set_title('Процесс обучения')
                
                # Объединяем легенды
                lines = line1 + line2
                labels = [l.get_label() for l in lines]
                ax2.legend(lines, labels, loc='center right')
            
            plt.tight_layout()
            
            # Сохраняем визуализацию
            viz_path = f"/workspace/neural_networks/visualizations/{network_name}_visualization.png"
            plt.savefig(viz_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                "message": f"Визуализация сети '{network_name}' создана",
                "visualization_path": viz_path,
                "architecture": asdict(architecture)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка визуализации: {e}")
            return {"error": str(e)}
    
    async def _handle_list_networks(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Список созданных нейросетей"""
        try:
            networks_info = []
            
            for name, info in self.created_networks.items():
                networks_info.append({
                    "name": name,
                    "status": info["status"],
                    "created_at": info["created_at"],
                    "architecture": asdict(info["architecture"]),
                    "test_accuracy": info.get("test_accuracy", 0),
                    "test_loss": info.get("test_loss", 0)
                })
            
            return {
                "networks": networks_info,
                "total_networks": len(networks_info)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка сетей: {e}")
            return {"error": str(e)}
    
    async def _save_network(self, network_name: str):
        """Сохранение нейросети"""
        try:
            network_info = self.created_networks[network_name]
            architecture = network_info["architecture"]
            
            # Сохраняем архитектуру
            arch_path = f"/workspace/neural_networks/models/{network_name}_architecture.json"
            with open(arch_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(architecture), f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Архитектура сети '{network_name}' сохранена")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения сети: {e}")
    
    async def _save_trained_model(self, network_name: str, model: nn.Module):
        """Сохранение обученной модели"""
        try:
            model_path = f"/workspace/neural_networks/models/{network_name}_model.pth"
            torch.save(model.state_dict(), model_path)
            logger.info(f"✅ Обученная модель '{network_name}' сохранена")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения модели: {e}")
    
    async def _create_test_data(self, data_name: str):
        """Создание тестовых данных"""
        training_data = TrainingData(
            name=data_name,
            data_type="classification",
            input_shape=(784,),
            output_shape=(10,),
            samples_count=1000,
            features=[f"feature_{i}" for i in range(784)],
            target_column="target",
            data_path=f"/workspace/neural_networks/data/{data_name}.csv"
        )
        
        self.training_data[data_name] = training_data

# Глобальный экземпляр агента
neural_network_creator = NeuralNetworkCreatorAgent()

if __name__ == "__main__":
    # Тестирование агента
    async def test_neural_network_creator():
        print("🧪 Тестирование Neural Network Creator...")
        
        # Создание сети
        result = await neural_network_creator._handle_create_network({
            "name": "test_network",
            "type": "classification",
            "input_size": 784,
            "output_size": 10,
            "hidden_layers": [128, 64]
        })
        print(f"Создание сети: {result}")
        
        # Обучение сети
        result = await neural_network_creator._handle_train_network({
            "network_name": "test_network"
        })
        print(f"Обучение сети: {result}")
        
        # Визуализация
        result = await neural_network_creator._handle_visualize_network({
            "network_name": "test_network"
        })
        print(f"Визуализация: {result}")
    
    asyncio.run(test_neural_network_creator())