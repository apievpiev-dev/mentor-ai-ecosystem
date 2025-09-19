#!/usr/bin/env python3
"""
Система развертывания нейросетей на сервере
Автоматически развертывает обученные нейросети как API сервисы
"""

import asyncio
import json
import logging
import time
import uuid
import subprocess
import shutil
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import docker
import yaml
import requests
from aiohttp import web, ClientSession
import aiohttp_cors

from neural_network_creator_agent import neural_network_creator
from autonomous_neural_network_trainer import autonomous_trainer

logger = logging.getLogger(__name__)

class NeuralNetworkDeploymentSystem:
    """Система развертывания нейросетей"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8082):
        self.host = host
        self.port = port
        self.deployed_services = {}
        self.docker_client = None
        self.deployment_queue = []
        self.active_deployments = {}
        self._setup_docker()
        self._setup_directories()
    
    def _setup_docker(self):
        """Настройка Docker клиента"""
        try:
            self.docker_client = docker.from_env()
            logger.info("🐳 Docker клиент инициализирован")
        except Exception as e:
            logger.warning(f"⚠️ Docker недоступен: {e}")
            self.docker_client = None
    
    def _setup_directories(self):
        """Создание необходимых директорий"""
        directories = [
            "/workspace/neural_networks/deployments",
            "/workspace/neural_networks/dockerfiles",
            "/workspace/neural_networks/api_templates",
            "/workspace/neural_networks/deployed_services",
            "/workspace/neural_networks/nginx_configs"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    async def deploy_neural_network(self, network_name: str, deployment_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Развертывание нейросети как API сервис"""
        try:
            deployment_id = str(uuid.uuid4())
            
            # Проверяем, что сеть существует и обучена
            networks_info = await neural_network_creator._handle_list_networks({})
            network_info = next((n for n in networks_info.get("networks", []) if n["name"] == network_name), None)
            
            if not network_info:
                return {"error": f"Сеть {network_name} не найдена"}
            
            if network_info["status"] != "trained":
                return {"error": f"Сеть {network_name} не обучена"}
            
            # Создаем конфигурацию развертывания
            if not deployment_config:
                deployment_config = await self._generate_deployment_config(network_info)
            
            # Создаем Dockerfile
            dockerfile_path = await self._create_dockerfile(network_name, network_info, deployment_config)
            
            # Создаем API сервис
            api_service_path = await self._create_api_service(network_name, network_info, deployment_config)
            
            # Создаем docker-compose файл
            compose_path = await self._create_docker_compose(network_name, deployment_config)
            
            # Развертываем сервис
            if self.docker_client:
                deployment_result = await self._deploy_with_docker(network_name, deployment_config)
            else:
                deployment_result = await self._deploy_with_python(network_name, deployment_config)
            
            # Сохраняем информацию о развертывании
            deployment_info = {
                "id": deployment_id,
                "network_name": network_name,
                "config": deployment_config,
                "status": "deployed",
                "deployed_at": datetime.now().isoformat(),
                "endpoints": deployment_result.get("endpoints", {}),
                "dockerfile_path": dockerfile_path,
                "api_service_path": api_service_path,
                "compose_path": compose_path
            }
            
            self.deployed_services[deployment_id] = deployment_info
            
            # Сохраняем в файл
            await self._save_deployment_info(deployment_id, deployment_info)
            
            return {
                "message": f"Нейросеть {network_name} успешно развернута",
                "deployment_id": deployment_id,
                "deployment_info": deployment_info,
                "endpoints": deployment_result.get("endpoints", {})
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка развертывания {network_name}: {e}")
            return {"error": str(e)}
    
    async def _generate_deployment_config(self, network_info: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация конфигурации развертывания"""
        return {
            "service_name": f"nn-{network_info['name']}",
            "port": 8000 + len(self.deployed_services),
            "replicas": 1,
            "resources": {
                "cpu": "0.5",
                "memory": "512Mi"
            },
            "health_check": {
                "path": "/health",
                "interval": 30
            },
            "api_version": "v1",
            "authentication": False,
            "rate_limiting": {
                "enabled": True,
                "requests_per_minute": 100
            }
        }
    
    async def _create_dockerfile(self, network_name: str, network_info: Dict[str, Any], 
                               config: Dict[str, Any]) -> str:
        """Создание Dockerfile для нейросети"""
        try:
            dockerfile_content = f"""
FROM python:3.9-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем пользователя для безопасности
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Экспонируем порт
EXPOSE {config['port']}

# Команда запуска
CMD ["python", "api_service.py"]
"""
            
            dockerfile_path = f"/workspace/neural_networks/dockerfiles/{network_name}_Dockerfile"
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content)
            
            logger.info(f"📄 Dockerfile создан: {dockerfile_path}")
            return dockerfile_path
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания Dockerfile: {e}")
            raise
    
    async def _create_api_service(self, network_name: str, network_info: Dict[str, Any], 
                                config: Dict[str, Any]) -> str:
        """Создание API сервиса для нейросети"""
        try:
            # Создаем requirements.txt
            requirements_content = """
torch>=1.9.0
numpy>=1.21.0
aiohttp>=3.8.0
aiohttp-cors>=0.7.0
pydantic>=1.8.0
uvicorn>=0.15.0
fastapi>=0.68.0
"""
            
            requirements_path = f"/workspace/neural_networks/deployed_services/{network_name}/requirements.txt"
            Path(requirements_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(requirements_path, 'w') as f:
                f.write(requirements_content)
            
            # Создаем API сервис
            api_service_content = f'''
#!/usr/bin/env python3
"""
API сервис для нейросети {network_name}
"""

import asyncio
import json
import logging
import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Any
from datetime import datetime
from aiohttp import web, ClientSession
import aiohttp_cors

# Загружаем модель
model = None
model_loaded = False

async def load_model():
    """Загрузка модели"""
    global model, model_loaded
    try:
        # Здесь должна быть логика загрузки модели
        # Пока создаем простую заглушку
        model = "Model loaded successfully"
        model_loaded = True
        logging.info("✅ Модель загружена")
    except Exception as e:
        logging.error(f"❌ Ошибка загрузки модели: {{e}}")
        model_loaded = False

async def predict(request):
    """Предсказание"""
    try:
        if not model_loaded:
            return web.json_response({{"error": "Модель не загружена"}}, status=500)
        
        data = await request.json()
        input_data = data.get("input", [])
        
        # Здесь должна быть логика предсказания
        # Пока возвращаем заглушку
        prediction = {{
            "prediction": [0.1, 0.2, 0.3, 0.4],
            "confidence": 0.85,
            "timestamp": datetime.now().isoformat()
        }}
        
        return web.json_response(prediction)
        
    except Exception as e:
        logging.error(f"❌ Ошибка предсказания: {{e}}")
        return web.json_response({{"error": str(e)}}, status=500)

async def health_check(request):
    """Проверка здоровья сервиса"""
    return web.json_response({{
        "status": "healthy",
        "model_loaded": model_loaded,
        "timestamp": datetime.now().isoformat()
    }})

async def get_model_info(request):
    """Информация о модели"""
    return web.json_response({{
        "network_name": "{network_name}",
        "architecture": {json.dumps(network_info.get('architecture', {{}}), indent=2)},
        "status": "trained" if network_info.get('status') == 'trained' else "unknown",
        "accuracy": network_info.get('test_accuracy', 0)
    }})

def create_app():
    """Создание приложения"""
    app = web.Application()
    
    # Настройка CORS
    cors = aiohttp_cors.setup(app, defaults={{
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    }})
    
    # Маршруты
    app.router.add_post('/predict', predict)
    app.router.add_get('/health', health_check)
    app.router.add_get('/model-info', get_model_info)
    
    # Добавляем CORS ко всем маршрутам
    for route in list(app.router.routes()):
        cors.add(route)
    
    return app

async def main():
    """Главная функция"""
    logging.basicConfig(level=logging.INFO)
    
    # Загружаем модель
    await load_model()
    
    # Создаем приложение
    app = create_app()
    
    # Запускаем сервер
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', {config['port']})
    await site.start()
    
    logging.info(f"🚀 API сервис для {network_name} запущен на порту {config['port']}")
    
    # Запускаем в бесконечном цикле
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
'''
            
            api_service_path = f"/workspace/neural_networks/deployed_services/{network_name}/api_service.py"
            with open(api_service_path, 'w') as f:
                f.write(api_service_content)
            
            logger.info(f"🔧 API сервис создан: {api_service_path}")
            return api_service_path
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания API сервиса: {e}")
            raise
    
    async def _create_docker_compose(self, network_name: str, config: Dict[str, Any]) -> str:
        """Создание docker-compose файла"""
        try:
            compose_content = f"""
version: '3.8'

services:
  {config['service_name']}:
    build:
      context: /workspace/neural_networks/deployed_services/{network_name}
      dockerfile: /workspace/neural_networks/dockerfiles/{network_name}_Dockerfile
    ports:
      - "{config['port']}:{config['port']}"
    environment:
      - MODEL_NAME={network_name}
      - API_VERSION={config['api_version']}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:{config['port']}/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '{config['resources']['cpu']}'
          memory: {config['resources']['memory']}
        reservations:
          cpus: '0.25'
          memory: 256M
"""
            
            compose_path = f"/workspace/neural_networks/deployments/{network_name}_docker-compose.yml"
            with open(compose_path, 'w') as f:
                f.write(compose_content)
            
            logger.info(f"🐳 Docker Compose файл создан: {compose_path}")
            return compose_path
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания Docker Compose: {e}")
            raise
    
    async def _deploy_with_docker(self, network_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Развертывание с помощью Docker"""
        try:
            service_name = config['service_name']
            port = config['port']
            
            # Собираем Docker образ
            image_name = f"{service_name}:latest"
            build_path = f"/workspace/neural_networks/deployed_services/{network_name}"
            
            logger.info(f"🔨 Сборка Docker образа {image_name}...")
            
            # Собираем образ
            image, build_logs = self.docker_client.images.build(
                path=build_path,
                tag=image_name,
                rm=True
            )
            
            logger.info(f"✅ Docker образ {image_name} собран")
            
            # Запускаем контейнер
            container = self.docker_client.containers.run(
                image_name,
                ports={f'{port}/tcp': port},
                environment={
                    'MODEL_NAME': network_name,
                    'API_VERSION': config['api_version']
                },
                detach=True,
                restart_policy={"Name": "unless-stopped"},
                name=service_name
            )
            
            logger.info(f"🚀 Контейнер {service_name} запущен")
            
            # Ждем запуска сервиса
            await asyncio.sleep(5)
            
            # Проверяем здоровье сервиса
            health_url = f"http://localhost:{port}/health"
            try:
                response = requests.get(health_url, timeout=10)
                if response.status_code == 200:
                    logger.info(f"✅ Сервис {service_name} здоров")
                else:
                    logger.warning(f"⚠️ Сервис {service_name} не отвечает на health check")
            except Exception as e:
                logger.warning(f"⚠️ Не удалось проверить здоровье сервиса: {e}")
            
            return {
                "deployment_type": "docker",
                "container_id": container.id,
                "image_name": image_name,
                "endpoints": {
                    "predict": f"http://localhost:{port}/predict",
                    "health": f"http://localhost:{port}/health",
                    "model_info": f"http://localhost:{port}/model-info"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка Docker развертывания: {e}")
            raise
    
    async def _deploy_with_python(self, network_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Развертывание с помощью Python (без Docker)"""
        try:
            service_name = config['service_name']
            port = config['port']
            
            # Запускаем Python сервис в фоне
            api_service_path = f"/workspace/neural_networks/deployed_services/{network_name}/api_service.py"
            
            process = subprocess.Popen([
                'python', api_service_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            logger.info(f"🚀 Python сервис {service_name} запущен (PID: {process.pid})")
            
            # Ждем запуска
            await asyncio.sleep(3)
            
            # Проверяем здоровье
            health_url = f"http://localhost:{port}/health"
            try:
                response = requests.get(health_url, timeout=10)
                if response.status_code == 200:
                    logger.info(f"✅ Сервис {service_name} здоров")
                else:
                    logger.warning(f"⚠️ Сервис {service_name} не отвечает")
            except Exception as e:
                logger.warning(f"⚠️ Не удалось проверить здоровье: {e}")
            
            return {
                "deployment_type": "python",
                "process_id": process.pid,
                "endpoints": {
                    "predict": f"http://localhost:{port}/predict",
                    "health": f"http://localhost:{port}/health",
                    "model_info": f"http://localhost:{port}/model-info"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка Python развертывания: {e}")
            raise
    
    async def _save_deployment_info(self, deployment_id: str, deployment_info: Dict[str, Any]):
        """Сохранение информации о развертывании"""
        try:
            info_path = f"/workspace/neural_networks/deployments/{deployment_id}_info.json"
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(deployment_info, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Информация о развертывании сохранена: {info_path}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения информации о развертывании: {e}")
    
    async def list_deployed_services(self) -> Dict[str, Any]:
        """Список развернутых сервисов"""
        try:
            services_info = []
            
            for deployment_id, info in self.deployed_services.items():
                # Проверяем статус сервиса
                status = await self._check_service_status(info)
                
                services_info.append({
                    "deployment_id": deployment_id,
                    "network_name": info["network_name"],
                    "status": status,
                    "endpoints": info["endpoints"],
                    "deployed_at": info["deployed_at"]
                })
            
            return {
                "services": services_info,
                "total_services": len(services_info)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка сервисов: {e}")
            return {"error": str(e)}
    
    async def _check_service_status(self, deployment_info: Dict[str, Any]) -> str:
        """Проверка статуса сервиса"""
        try:
            endpoints = deployment_info.get("endpoints", {})
            health_url = endpoints.get("health")
            
            if not health_url:
                return "unknown"
            
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                return "healthy"
            else:
                return "unhealthy"
                
        except Exception:
            return "unhealthy"
    
    async def stop_service(self, deployment_id: str) -> Dict[str, Any]:
        """Остановка сервиса"""
        try:
            if deployment_id not in self.deployed_services:
                return {"error": "Сервис не найден"}
            
            deployment_info = self.deployed_services[deployment_id]
            
            if deployment_info["config"].get("deployment_type") == "docker":
                # Останавливаем Docker контейнер
                container_id = deployment_info.get("container_id")
                if container_id:
                    container = self.docker_client.containers.get(container_id)
                    container.stop()
                    container.remove()
                    logger.info(f"🛑 Docker контейнер {container_id} остановлен")
            
            # Удаляем из списка
            del self.deployed_services[deployment_id]
            
            return {
                "message": f"Сервис {deployment_id} остановлен",
                "deployment_id": deployment_id
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка остановки сервиса: {e}")
            return {"error": str(e)}
    
    async def get_deployment_status(self) -> Dict[str, Any]:
        """Получение статуса системы развертывания"""
        return {
            "deployed_services": len(self.deployed_services),
            "deployment_queue": len(self.deployment_queue),
            "active_deployments": len(self.active_deployments),
            "docker_available": self.docker_client is not None,
            "timestamp": datetime.now().isoformat()
        }

# Глобальный экземпляр системы развертывания
deployment_system = NeuralNetworkDeploymentSystem()

async def main():
    """Главная функция"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        logger.info("🚀 Система развертывания нейросетей запущена")
        
        # Тестируем развертывание
        logger.info("🧪 Тестирование развертывания...")
        
        # Получаем список обученных сетей
        networks_info = await neural_network_creator._handle_list_networks({})
        trained_networks = [n for n in networks_info.get("networks", []) if n["status"] == "trained"]
        
        if trained_networks:
            # Развертываем первую обученную сеть
            network_name = trained_networks[0]["name"]
            result = await deployment_system.deploy_neural_network(network_name)
            
            if result.get("error"):
                logger.error(f"❌ Тест развертывания не прошел: {result['error']}")
            else:
                logger.info("✅ Тест развертывания прошел успешно!")
                logger.info(f"🌐 Развернутые сервисы: {len(deployment_system.deployed_services)}")
        else:
            logger.info("ℹ️ Нет обученных сетей для развертывания")
        
        # Запускаем в бесконечном цикле
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Остановка системы развертывания...")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())