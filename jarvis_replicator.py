#!/usr/bin/env python3
"""
JARVIS Replicator Module
Система самовоспроизводства и автономного масштабирования
"""

import os
import sys
import json
import time
import asyncio
import subprocess
import logging
import docker
import paramiko
import yaml
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import threading
import queue

logger = logging.getLogger(__name__)

@dataclass
class ServerInfo:
    """Информация о сервере"""
    host: str
    port: int = 22
    username: str = "root"
    ssh_key_path: str = ""
    cpu_cores: int = 0
    memory_gb: int = 0
    disk_gb: int = 0
    status: str = "unknown"  # available, busy, offline
    last_check: Optional[str] = None

@dataclass
class ReplicationTarget:
    """Цель для репликации"""
    server: ServerInfo
    priority: int = 5  # 1-10
    resources_needed: Dict[str, float] = None
    deployment_time: Optional[str] = None
    
    def __post_init__(self):
        if self.resources_needed is None:
            self.resources_needed = {"cpu": 2, "memory": 4, "disk": 20}

class JarvisReplicator:
    """Система самовоспроизводства JARVIS"""
    
    def __init__(self, core):
        self.core = core
        self.docker_client = docker.from_env()
        self.known_servers = []
        self.replication_queue = queue.Queue()
        self.active_deployments = {}
        self.replication_history = []
        
        # Загружаем конфигурацию
        self.load_config()
        
        # Инициализируем поиск серверов
        self.init_server_discovery()
        
        # Запускаем фоновые процессы
        self.start_background_processes()
        
    def load_config(self):
        """Загрузка конфигурации репликации"""
        config_path = "/home/mentor/jarvis_data/replication_config.yaml"
        
        default_config = {
            "replication": {
                "enabled": True,
                "max_instances": 10,
                "resource_thresholds": {
                    "cpu_percent": 80,
                    "memory_percent": 85,
                    "active_tasks": 10
                },
                "deployment": {
                    "docker_registry": "localhost:5000",
                    "image_tag": "jarvis:latest",
                    "container_name_prefix": "jarvis_node",
                    "port_range": [8080, 8090]
                },
                "server_discovery": {
                    "enabled": True,
                    "scan_networks": ["192.168.1.0/24", "10.0.0.0/24"],
                    "common_ports": [22, 2222],
                    "ssh_timeout": 10
                }
            },
            "monitoring": {
                "health_check_interval": 300,  # 5 минут
                "performance_check_interval": 60,  # 1 минута
                "auto_cleanup_failed": True,
                "cleanup_interval": 3600  # 1 час
            }
        }
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = default_config
            with open(config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
    
    def init_server_discovery(self):
        """Инициализация поиска серверов"""
        # Загружаем известные серверы из конфигурации
        servers_config = self.config.get("known_servers", [])
        
        for server_config in servers_config:
            server = ServerInfo(
                host=server_config["host"],
                port=server_config.get("port", 22),
                username=server_config.get("username", "root"),
                ssh_key_path=server_config.get("ssh_key_path", "")
            )
            self.known_servers.append(server)
        
        # Добавляем текущий сервер как базовый
        local_server = ServerInfo(
            host="localhost",
            port=22,
            username=os.getenv("USER", "mentor"),
            status="available",
            cpu_cores=8,  # Из анализа системы
            memory_gb=12,
            disk_gb=100
        )
        self.known_servers.append(local_server)
    
    def start_background_processes(self):
        """Запуск фоновых процессов"""
        # Процесс поиска новых серверов
        discovery_thread = threading.Thread(
            target=self.run_server_discovery, 
            daemon=True
        )
        discovery_thread.start()
        
        # Процесс мониторинга развернутых экземпляров
        monitoring_thread = threading.Thread(
            target=self.run_health_monitoring,
            daemon=True
        )
        monitoring_thread.start()
        
        # Процесс очистки неудачных развертываний
        cleanup_thread = threading.Thread(
            target=self.run_cleanup_process,
            daemon=True
        )
        cleanup_thread.start()
        
        logger.info("🔄 Фоновые процессы репликации запущены")
    
    def run_server_discovery(self):
        """Поиск новых серверов"""
        while True:
            try:
                if self.config.get("replication", {}).get("server_discovery", {}).get("enabled", False):
                    self.discover_new_servers()
                time.sleep(3600)  # Каждый час
            except Exception as e:
                logger.error(f"Ошибка поиска серверов: {e}")
                time.sleep(300)
    
    def run_health_monitoring(self):
        """Мониторинг здоровья развернутых экземпляров"""
        while True:
            try:
                self.check_deployed_instances_health()
                time.sleep(self.config["monitoring"]["health_check_interval"])
            except Exception as e:
                logger.error(f"Ошибка мониторинга: {e}")
                time.sleep(60)
    
    def run_cleanup_process(self):
        """Очистка неудачных развертываний"""
        while True:
            try:
                if self.config["monitoring"]["auto_cleanup_failed"]:
                    self.cleanup_failed_deployments()
                time.sleep(self.config["monitoring"]["cleanup_interval"])
            except Exception as e:
                logger.error(f"Ошибка очистки: {e}")
                time.sleep(300)
    
    async def should_replicate(self) -> bool:
        """Проверка необходимости репликации"""
        # Проверяем пороги ресурсов
        cpu_threshold = self.config["replication"]["resource_thresholds"]["cpu_percent"]
        memory_threshold = self.config["replication"]["resource_thresholds"]["memory_percent"]
        tasks_threshold = self.config["replication"]["resource_thresholds"]["active_tasks"]
        
        current_cpu = self.core.state.resources_used.get("cpu", 0)
        current_memory = self.core.state.resources_used.get("memory", 0)
        current_tasks = self.core.state.active_tasks
        
        # Проверяем максимальное количество экземпляров
        max_instances = self.config["replication"]["max_instances"]
        current_instances = self.core.state.total_instances
        
        if current_instances >= max_instances:
            logger.info(f"Достигнуто максимальное количество экземпляров: {max_instances}")
            return False
        
        # Проверяем пороги ресурсов
        if (current_cpu > cpu_threshold or 
            current_memory > memory_threshold or 
            current_tasks > tasks_threshold):
            
            logger.info(f"🚀 Триггер репликации: CPU={current_cpu}%, Memory={current_memory}%, Tasks={current_tasks}")
            return True
        
        return False
    
    async def replicate(self) -> Dict[str, Any]:
        """Основной процесс репликации"""
        try:
            if not await self.should_replicate():
                return {"status": "not_needed", "reason": "Пороги не достигнуты"}
            
            logger.info("🔄 Начинаем процесс самовоспроизводства...")
            
            # 1. Создаем Docker образ
            image = await self.create_deployment_image()
            if not image:
                return {"error": "Не удалось создать Docker образ"}
            
            # 2. Находим доступные серверы
            available_servers = await self.find_available_servers()
            if not available_servers:
                return {"error": "Нет доступных серверов для развертывания"}
            
            # 3. Выбираем лучший сервер
            target_server = self.select_best_server(available_servers)
            if not target_server:
                return {"error": "Не удалось выбрать подходящий сервер"}
            
            # 4. Развертываем на выбранном сервере
            deployment_result = await self.deploy_to_server(target_server, image)
            
            # 5. Обновляем состояние системы
            if deployment_result.get("success"):
                self.core.state.total_instances += 1
                self.core.state.last_self_replication = datetime.now().isoformat()
                
                # Записываем в историю
                self.replication_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "target_server": target_server.server.host,
                    "success": True,
                    "deployment_time": deployment_result.get("deployment_time", 0)
                })
                
                logger.info(f"✅ Репликация успешна на сервер {target_server.server.host}")
            
            return deployment_result
            
        except Exception as e:
            logger.error(f"❌ Ошибка репликации: {e}")
            return {"error": str(e)}
    
    async def create_deployment_image(self) -> Optional[docker.models.images.Image]:
        """Создание Docker образа для развертывания"""
        try:
            logger.info("📦 Создаем Docker образ для развертывания...")
            
            # Создаем временную директорию для сборки
            build_dir = "/home/mentor/jarvis_data/deployment"
            Path(build_dir).mkdir(parents=True, exist_ok=True)
            
            # Создаем Dockerfile
            dockerfile_content = f"""
FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \\
    docker.io \\
    openssh-client \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем код JARVIS
COPY jarvis_core.py .
COPY jarvis_integration.py .
COPY jarvis_replicator.py .

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем конфигурацию
COPY config.yaml .
COPY replication_config.yaml .

# Создаем директории
RUN mkdir -p /app/jarvis_data/knowledge
RUN mkdir -p /app/jarvis_data/logs
RUN mkdir -p /app/jarvis_data/templates

# Копируем шаблоны
COPY templates/ ./templates/

# Устанавливаем права
RUN chmod +x jarvis_core.py

# Экспортируем порт
EXPOSE 8080

# Команда запуска
CMD ["python", "jarvis_core.py"]
"""
            
            with open(f"{build_dir}/Dockerfile", "w") as f:
                f.write(dockerfile_content)
            
            # Создаем requirements.txt
            requirements_content = """
fastapi==0.104.1
uvicorn==0.24.0
docker==6.1.3
paramiko==3.3.1
pyyaml==6.0.1
requests==2.31.0
pandas==2.1.3
websockets==12.0
asyncio
"""
            
            with open(f"{build_dir}/requirements.txt", "w") as f:
                f.write(requirements_content)
            
            # Копируем необходимые файлы
            import shutil
            files_to_copy = [
                "jarvis_core.py",
                "jarvis_integration.py", 
                "jarvis_replicator.py",
                "config.yaml",
                "replication_config.yaml"
            ]
            
            for file in files_to_copy:
                src = f"/home/mentor/jarvis_data/{file}"
                dst = f"{build_dir}/{file}"
                if os.path.exists(src):
                    shutil.copy2(src, dst)
            
            # Копируем шаблоны
            templates_src = "/home/mentor/jarvis_data/templates"
            templates_dst = f"{build_dir}/templates"
            if os.path.exists(templates_src):
                shutil.copytree(templates_src, templates_dst, dirs_exist_ok=True)
            
            # Собираем образ
            image, logs = self.docker_client.images.build(
                path=build_dir,
                tag=self.config["replication"]["deployment"]["image_tag"],
                rm=True
            )
            
            logger.info("✅ Docker образ создан успешно")
            return image
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания Docker образа: {e}")
            return None
    
    async def find_available_servers(self) -> List[ReplicationTarget]:
        """Поиск доступных серверов"""
        available_targets = []
        
        for server in self.known_servers:
            try:
                # Проверяем доступность сервера
                if await self.check_server_availability(server):
                    # Получаем информацию о ресурсах
                    resources = await self.get_server_resources(server)
                    
                    target = ReplicationTarget(
                        server=server,
                        priority=self.calculate_server_priority(server, resources),
                        resources_needed={
                            "cpu": 2,
                            "memory": 4, 
                            "disk": 20
                        }
                    )
                    
                    available_targets.append(target)
                    
            except Exception as e:
                logger.warning(f"Сервер {server.host} недоступен: {e}")
                server.status = "offline"
        
        # Сортируем по приоритету
        available_targets.sort(key=lambda x: x.priority, reverse=True)
        
        return available_targets
    
    async def check_server_availability(self, server: ServerInfo) -> bool:
        """Проверка доступности сервера"""
        try:
            # Проверяем SSH подключение
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            timeout = self.config["replication"]["server_discovery"]["ssh_timeout"]
            ssh.connect(
                hostname=server.host,
                port=server.port,
                username=server.username,
                key_filename=server.ssh_key_path if server.ssh_key_path else None,
                timeout=timeout
            )
            
            ssh.close()
            server.status = "available"
            server.last_check = datetime.now().isoformat()
            return True
            
        except Exception as e:
            server.status = "offline"
            server.last_check = datetime.now().isoformat()
            return False
    
    async def get_server_resources(self, server: ServerInfo) -> Dict[str, Any]:
        """Получение информации о ресурсах сервера"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=server.host,
                port=server.port,
                username=server.username,
                key_filename=server.ssh_key_path if server.ssh_key_path else None,
                timeout=10
            )
            
            # Получаем информацию о CPU
            stdin, stdout, stderr = ssh.exec_command("nproc")
            cpu_cores = int(stdout.read().decode().strip())
            
            # Получаем информацию о памяти
            stdin, stdout, stderr = ssh.exec_command("free -m | awk 'NR==2{printf \"%.1f\", $2/1024}'")
            memory_gb = float(stdout.read().decode().strip())
            
            # Получаем информацию о диске
            stdin, stdout, stderr = ssh.exec_command("df -BG / | awk 'NR==2{print $4}' | sed 's/G//'")
            disk_gb = int(stdout.read().decode().strip())
            
            ssh.close()
            
            # Обновляем информацию о сервере
            server.cpu_cores = cpu_cores
            server.memory_gb = memory_gb
            server.disk_gb = disk_gb
            
            return {
                "cpu_cores": cpu_cores,
                "memory_gb": memory_gb,
                "disk_gb": disk_gb
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения ресурсов сервера {server.host}: {e}")
            return {"cpu_cores": 0, "memory_gb": 0, "disk_gb": 0}
    
    def calculate_server_priority(self, server: ServerInfo, resources: Dict[str, Any]) -> int:
        """Расчет приоритета сервера"""
        priority = 5  # Базовый приоритет
        
        # Учитываем ресурсы
        if resources["cpu_cores"] >= 4:
            priority += 2
        if resources["memory_gb"] >= 8:
            priority += 2
        if resources["disk_gb"] >= 50:
            priority += 1
        
        # Учитываем статус
        if server.status == "available":
            priority += 1
        
        # Учитываем последнюю проверку
        if server.last_check:
            last_check = datetime.fromisoformat(server.last_check)
            if (datetime.now() - last_check).seconds < 300:  # Проверен недавно
                priority += 1
        
        return min(priority, 10)  # Максимум 10
    
    def select_best_server(self, available_targets: List[ReplicationTarget]) -> Optional[ReplicationTarget]:
        """Выбор лучшего сервера для развертывания"""
        if not available_targets:
            return None
        
        # Выбираем сервер с наивысшим приоритетом
        best_target = available_targets[0]
        
        # Проверяем, что ресурсов достаточно
        if (best_target.server.cpu_cores >= best_target.resources_needed["cpu"] and
            best_target.server.memory_gb >= best_target.resources_needed["memory"] and
            best_target.server.disk_gb >= best_target.resources_needed["disk"]):
            
            return best_target
        
        return None
    
    async def deploy_to_server(self, target: ReplicationTarget, image) -> Dict[str, Any]:
        """Развертывание на выбранном сервере"""
        start_time = time.time()
        
        try:
            logger.info(f"🚀 Развертываем JARVIS на сервер {target.server.host}...")
            
            # Подключаемся к серверу
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=target.server.host,
                port=target.server.port,
                username=target.server.username,
                key_filename=target.server.ssh_key_path if target.server.ssh_key_path else None,
                timeout=30
            )
            
            # Проверяем наличие Docker
            stdin, stdout, stderr = ssh.exec_command("docker --version")
            if stdout.channel.recv_exit_status() != 0:
                # Устанавливаем Docker
                logger.info("Устанавливаем Docker на сервере...")
                install_commands = [
                    "curl -fsSL https://get.docker.com -o get-docker.sh",
                    "sh get-docker.sh",
                    "systemctl start docker",
                    "systemctl enable docker"
                ]
                
                for cmd in install_commands:
                    stdin, stdout, stderr = ssh.exec_command(cmd)
                    stdout.channel.recv_exit_status()
            
            # Сохраняем образ в файл
            image_path = "/tmp/jarvis_image.tar"
            with open(image_path, "wb") as f:
                for chunk in image.save():
                    f.write(chunk)
            
            # Копируем образ на сервер
            sftp = ssh.open_sftp()
            remote_image_path = "/tmp/jarvis_image.tar"
            sftp.put(image_path, remote_image_path)
            sftp.close()
            
            # Загружаем образ на сервере
            stdin, stdout, stderr = ssh.exec_command(f"docker load < {remote_image_path}")
            if stdout.channel.recv_exit_status() != 0:
                raise Exception("Не удалось загрузить Docker образ")
            
            # Находим свободный порт
            port = await self.find_free_port(target.server)
            
            # Запускаем контейнер
            container_name = f"{self.config['replication']['deployment']['container_name_prefix']}_{int(time.time())}"
            run_command = f"""
docker run -d \\
    --name {container_name} \\
    -p {port}:8080 \\
    --restart unless-stopped \\
    {self.config['replication']['deployment']['image_tag']}
"""
            
            stdin, stdout, stderr = ssh.exec_command(run_command)
            if stdout.channel.recv_exit_status() != 0:
                raise Exception("Не удалось запустить контейнер")
            
            # Проверяем, что контейнер запустился
            await asyncio.sleep(10)
            stdin, stdout, stderr = ssh.exec_command(f"docker ps | grep {container_name}")
            if stdout.channel.recv_exit_status() != 0:
                raise Exception("Контейнер не запустился")
            
            # Проверяем доступность веб-интерфейса
            health_url = f"http://{target.server.host}:{port}/api/status"
            health_check = await self.check_health_endpoint(health_url)
            
            ssh.close()
            
            deployment_time = time.time() - start_time
            
            if health_check:
                # Добавляем в активные развертывания
                self.active_deployments[container_name] = {
                    "server": target.server.host,
                    "port": port,
                    "container_name": container_name,
                    "deployed_at": datetime.now().isoformat(),
                    "status": "running"
                }
                
                logger.info(f"✅ Развертывание успешно завершено за {deployment_time:.2f}с")
                
                return {
                    "success": True,
                    "server": target.server.host,
                    "port": port,
                    "container_name": container_name,
                    "deployment_time": deployment_time,
                    "health_check": True
                }
            else:
                raise Exception("Health check не прошел")
                
        except Exception as e:
            logger.error(f"❌ Ошибка развертывания на {target.server.host}: {e}")
            return {
                "success": False,
                "error": str(e),
                "server": target.server.host,
                "deployment_time": time.time() - start_time
            }
    
    async def find_free_port(self, server: ServerInfo) -> int:
        """Поиск свободного порта на сервере"""
        port_range = self.config["replication"]["deployment"]["port_range"]
        
        for port in range(port_range[0], port_range[1]):
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(
                    hostname=server.host,
                    port=server.port,
                    username=server.username,
                    key_filename=server.ssh_key_path if server.ssh_key_path else None,
                    timeout=10
                )
                
                stdin, stdout, stderr = ssh.exec_command(f"netstat -tln | grep :{port}")
                if stdout.channel.recv_exit_status() != 0:  # Порт свободен
                    ssh.close()
                    return port
                
                ssh.close()
            except:
                continue
        
        return port_range[0]  # Возвращаем первый порт если ничего не найдено
    
    async def check_health_endpoint(self, url: str) -> bool:
        """Проверка доступности health endpoint"""
        try:
            response = requests.get(url, timeout=30)
            return response.status_code == 200
        except:
            return False
    
    def discover_new_servers(self):
        """Поиск новых серверов в сети"""
        networks = self.config["replication"]["server_discovery"]["scan_networks"]
        ports = self.config["replication"]["server_discovery"]["common_ports"]
        
        for network in networks:
            # Здесь можно добавить сканирование сети
            # Пока заглушка
            logger.info(f"Сканируем сеть {network}...")
    
    def check_deployed_instances_health(self):
        """Проверка здоровья развернутых экземпляров"""
        for container_name, info in list(self.active_deployments.items()):
            try:
                health_url = f"http://{info['server']}:{info['port']}/api/status"
                
                # Проверяем доступность
                response = requests.get(health_url, timeout=10)
                if response.status_code != 200:
                    logger.warning(f"⚠️ Экземпляр {container_name} недоступен")
                    info["status"] = "unhealthy"
                else:
                    info["status"] = "healthy"
                    
            except Exception as e:
                logger.warning(f"⚠️ Ошибка проверки здоровья {container_name}: {e}")
                info["status"] = "unhealthy"
    
    def cleanup_failed_deployments(self):
        """Очистка неудачных развертываний"""
        for container_name, info in list(self.active_deployments.items()):
            if info["status"] == "unhealthy":
                logger.info(f"🧹 Удаляем неудачное развертывание {container_name}")
                del self.active_deployments[container_name]
                
                # Обновляем счетчик экземпляров
                self.core.state.total_instances = max(1, self.core.state.total_instances - 1)
    
    def get_replication_status(self) -> Dict[str, Any]:
        """Получение статуса репликации"""
        return {
            "enabled": self.config["replication"]["enabled"],
            "total_instances": self.core.state.total_instances,
            "known_servers": len(self.known_servers),
            "active_deployments": len(self.active_deployments),
            "deployments": self.active_deployments,
            "replication_history": self.replication_history[-10:],  # Последние 10
            "last_replication": self.core.state.last_self_replication
        }



JARVIS Replicator Module
Система самовоспроизводства и автономного масштабирования
"""

import os
import sys
import json
import time
import asyncio
import subprocess
import logging
import docker
import paramiko
import yaml
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import threading
import queue

logger = logging.getLogger(__name__)

@dataclass
class ServerInfo:
    """Информация о сервере"""
    host: str
    port: int = 22
    username: str = "root"
    ssh_key_path: str = ""
    cpu_cores: int = 0
    memory_gb: int = 0
    disk_gb: int = 0
    status: str = "unknown"  # available, busy, offline
    last_check: Optional[str] = None

@dataclass
class ReplicationTarget:
    """Цель для репликации"""
    server: ServerInfo
    priority: int = 5  # 1-10
    resources_needed: Dict[str, float] = None
    deployment_time: Optional[str] = None
    
    def __post_init__(self):
        if self.resources_needed is None:
            self.resources_needed = {"cpu": 2, "memory": 4, "disk": 20}

class JarvisReplicator:
    """Система самовоспроизводства JARVIS"""
    
    def __init__(self, core):
        self.core = core
        self.docker_client = docker.from_env()
        self.known_servers = []
        self.replication_queue = queue.Queue()
        self.active_deployments = {}
        self.replication_history = []
        
        # Загружаем конфигурацию
        self.load_config()
        
        # Инициализируем поиск серверов
        self.init_server_discovery()
        
        # Запускаем фоновые процессы
        self.start_background_processes()
        
    def load_config(self):
        """Загрузка конфигурации репликации"""
        config_path = "/home/mentor/jarvis_data/replication_config.yaml"
        
        default_config = {
            "replication": {
                "enabled": True,
                "max_instances": 10,
                "resource_thresholds": {
                    "cpu_percent": 80,
                    "memory_percent": 85,
                    "active_tasks": 10
                },
                "deployment": {
                    "docker_registry": "localhost:5000",
                    "image_tag": "jarvis:latest",
                    "container_name_prefix": "jarvis_node",
                    "port_range": [8080, 8090]
                },
                "server_discovery": {
                    "enabled": True,
                    "scan_networks": ["192.168.1.0/24", "10.0.0.0/24"],
                    "common_ports": [22, 2222],
                    "ssh_timeout": 10
                }
            },
            "monitoring": {
                "health_check_interval": 300,  # 5 минут
                "performance_check_interval": 60,  # 1 минута
                "auto_cleanup_failed": True,
                "cleanup_interval": 3600  # 1 час
            }
        }
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = default_config
            with open(config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
    
    def init_server_discovery(self):
        """Инициализация поиска серверов"""
        # Загружаем известные серверы из конфигурации
        servers_config = self.config.get("known_servers", [])
        
        for server_config in servers_config:
            server = ServerInfo(
                host=server_config["host"],
                port=server_config.get("port", 22),
                username=server_config.get("username", "root"),
                ssh_key_path=server_config.get("ssh_key_path", "")
            )
            self.known_servers.append(server)
        
        # Добавляем текущий сервер как базовый
        local_server = ServerInfo(
            host="localhost",
            port=22,
            username=os.getenv("USER", "mentor"),
            status="available",
            cpu_cores=8,  # Из анализа системы
            memory_gb=12,
            disk_gb=100
        )
        self.known_servers.append(local_server)
    
    def start_background_processes(self):
        """Запуск фоновых процессов"""
        # Процесс поиска новых серверов
        discovery_thread = threading.Thread(
            target=self.run_server_discovery, 
            daemon=True
        )
        discovery_thread.start()
        
        # Процесс мониторинга развернутых экземпляров
        monitoring_thread = threading.Thread(
            target=self.run_health_monitoring,
            daemon=True
        )
        monitoring_thread.start()
        
        # Процесс очистки неудачных развертываний
        cleanup_thread = threading.Thread(
            target=self.run_cleanup_process,
            daemon=True
        )
        cleanup_thread.start()
        
        logger.info("🔄 Фоновые процессы репликации запущены")
    
    def run_server_discovery(self):
        """Поиск новых серверов"""
        while True:
            try:
                if self.config.get("replication", {}).get("server_discovery", {}).get("enabled", False):
                    self.discover_new_servers()
                time.sleep(3600)  # Каждый час
            except Exception as e:
                logger.error(f"Ошибка поиска серверов: {e}")
                time.sleep(300)
    
    def run_health_monitoring(self):
        """Мониторинг здоровья развернутых экземпляров"""
        while True:
            try:
                self.check_deployed_instances_health()
                time.sleep(self.config["monitoring"]["health_check_interval"])
            except Exception as e:
                logger.error(f"Ошибка мониторинга: {e}")
                time.sleep(60)
    
    def run_cleanup_process(self):
        """Очистка неудачных развертываний"""
        while True:
            try:
                if self.config["monitoring"]["auto_cleanup_failed"]:
                    self.cleanup_failed_deployments()
                time.sleep(self.config["monitoring"]["cleanup_interval"])
            except Exception as e:
                logger.error(f"Ошибка очистки: {e}")
                time.sleep(300)
    
    async def should_replicate(self) -> bool:
        """Проверка необходимости репликации"""
        # Проверяем пороги ресурсов
        cpu_threshold = self.config["replication"]["resource_thresholds"]["cpu_percent"]
        memory_threshold = self.config["replication"]["resource_thresholds"]["memory_percent"]
        tasks_threshold = self.config["replication"]["resource_thresholds"]["active_tasks"]
        
        current_cpu = self.core.state.resources_used.get("cpu", 0)
        current_memory = self.core.state.resources_used.get("memory", 0)
        current_tasks = self.core.state.active_tasks
        
        # Проверяем максимальное количество экземпляров
        max_instances = self.config["replication"]["max_instances"]
        current_instances = self.core.state.total_instances
        
        if current_instances >= max_instances:
            logger.info(f"Достигнуто максимальное количество экземпляров: {max_instances}")
            return False
        
        # Проверяем пороги ресурсов
        if (current_cpu > cpu_threshold or 
            current_memory > memory_threshold or 
            current_tasks > tasks_threshold):
            
            logger.info(f"🚀 Триггер репликации: CPU={current_cpu}%, Memory={current_memory}%, Tasks={current_tasks}")
            return True
        
        return False
    
    async def replicate(self) -> Dict[str, Any]:
        """Основной процесс репликации"""
        try:
            if not await self.should_replicate():
                return {"status": "not_needed", "reason": "Пороги не достигнуты"}
            
            logger.info("🔄 Начинаем процесс самовоспроизводства...")
            
            # 1. Создаем Docker образ
            image = await self.create_deployment_image()
            if not image:
                return {"error": "Не удалось создать Docker образ"}
            
            # 2. Находим доступные серверы
            available_servers = await self.find_available_servers()
            if not available_servers:
                return {"error": "Нет доступных серверов для развертывания"}
            
            # 3. Выбираем лучший сервер
            target_server = self.select_best_server(available_servers)
            if not target_server:
                return {"error": "Не удалось выбрать подходящий сервер"}
            
            # 4. Развертываем на выбранном сервере
            deployment_result = await self.deploy_to_server(target_server, image)
            
            # 5. Обновляем состояние системы
            if deployment_result.get("success"):
                self.core.state.total_instances += 1
                self.core.state.last_self_replication = datetime.now().isoformat()
                
                # Записываем в историю
                self.replication_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "target_server": target_server.server.host,
                    "success": True,
                    "deployment_time": deployment_result.get("deployment_time", 0)
                })
                
                logger.info(f"✅ Репликация успешна на сервер {target_server.server.host}")
            
            return deployment_result
            
        except Exception as e:
            logger.error(f"❌ Ошибка репликации: {e}")
            return {"error": str(e)}
    
    async def create_deployment_image(self) -> Optional[docker.models.images.Image]:
        """Создание Docker образа для развертывания"""
        try:
            logger.info("📦 Создаем Docker образ для развертывания...")
            
            # Создаем временную директорию для сборки
            build_dir = "/home/mentor/jarvis_data/deployment"
            Path(build_dir).mkdir(parents=True, exist_ok=True)
            
            # Создаем Dockerfile
            dockerfile_content = f"""
FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \\
    docker.io \\
    openssh-client \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем код JARVIS
COPY jarvis_core.py .
COPY jarvis_integration.py .
COPY jarvis_replicator.py .

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем конфигурацию
COPY config.yaml .
COPY replication_config.yaml .

# Создаем директории
RUN mkdir -p /app/jarvis_data/knowledge
RUN mkdir -p /app/jarvis_data/logs
RUN mkdir -p /app/jarvis_data/templates

# Копируем шаблоны
COPY templates/ ./templates/

# Устанавливаем права
RUN chmod +x jarvis_core.py

# Экспортируем порт
EXPOSE 8080

# Команда запуска
CMD ["python", "jarvis_core.py"]
"""
            
            with open(f"{build_dir}/Dockerfile", "w") as f:
                f.write(dockerfile_content)
            
            # Создаем requirements.txt
            requirements_content = """
fastapi==0.104.1
uvicorn==0.24.0
docker==6.1.3
paramiko==3.3.1
pyyaml==6.0.1
requests==2.31.0
pandas==2.1.3
websockets==12.0
asyncio
"""
            
            with open(f"{build_dir}/requirements.txt", "w") as f:
                f.write(requirements_content)
            
            # Копируем необходимые файлы
            import shutil
            files_to_copy = [
                "jarvis_core.py",
                "jarvis_integration.py", 
                "jarvis_replicator.py",
                "config.yaml",
                "replication_config.yaml"
            ]
            
            for file in files_to_copy:
                src = f"/home/mentor/jarvis_data/{file}"
                dst = f"{build_dir}/{file}"
                if os.path.exists(src):
                    shutil.copy2(src, dst)
            
            # Копируем шаблоны
            templates_src = "/home/mentor/jarvis_data/templates"
            templates_dst = f"{build_dir}/templates"
            if os.path.exists(templates_src):
                shutil.copytree(templates_src, templates_dst, dirs_exist_ok=True)
            
            # Собираем образ
            image, logs = self.docker_client.images.build(
                path=build_dir,
                tag=self.config["replication"]["deployment"]["image_tag"],
                rm=True
            )
            
            logger.info("✅ Docker образ создан успешно")
            return image
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания Docker образа: {e}")
            return None
    
    async def find_available_servers(self) -> List[ReplicationTarget]:
        """Поиск доступных серверов"""
        available_targets = []
        
        for server in self.known_servers:
            try:
                # Проверяем доступность сервера
                if await self.check_server_availability(server):
                    # Получаем информацию о ресурсах
                    resources = await self.get_server_resources(server)
                    
                    target = ReplicationTarget(
                        server=server,
                        priority=self.calculate_server_priority(server, resources),
                        resources_needed={
                            "cpu": 2,
                            "memory": 4, 
                            "disk": 20
                        }
                    )
                    
                    available_targets.append(target)
                    
            except Exception as e:
                logger.warning(f"Сервер {server.host} недоступен: {e}")
                server.status = "offline"
        
        # Сортируем по приоритету
        available_targets.sort(key=lambda x: x.priority, reverse=True)
        
        return available_targets
    
    async def check_server_availability(self, server: ServerInfo) -> bool:
        """Проверка доступности сервера"""
        try:
            # Проверяем SSH подключение
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            timeout = self.config["replication"]["server_discovery"]["ssh_timeout"]
            ssh.connect(
                hostname=server.host,
                port=server.port,
                username=server.username,
                key_filename=server.ssh_key_path if server.ssh_key_path else None,
                timeout=timeout
            )
            
            ssh.close()
            server.status = "available"
            server.last_check = datetime.now().isoformat()
            return True
            
        except Exception as e:
            server.status = "offline"
            server.last_check = datetime.now().isoformat()
            return False
    
    async def get_server_resources(self, server: ServerInfo) -> Dict[str, Any]:
        """Получение информации о ресурсах сервера"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=server.host,
                port=server.port,
                username=server.username,
                key_filename=server.ssh_key_path if server.ssh_key_path else None,
                timeout=10
            )
            
            # Получаем информацию о CPU
            stdin, stdout, stderr = ssh.exec_command("nproc")
            cpu_cores = int(stdout.read().decode().strip())
            
            # Получаем информацию о памяти
            stdin, stdout, stderr = ssh.exec_command("free -m | awk 'NR==2{printf \"%.1f\", $2/1024}'")
            memory_gb = float(stdout.read().decode().strip())
            
            # Получаем информацию о диске
            stdin, stdout, stderr = ssh.exec_command("df -BG / | awk 'NR==2{print $4}' | sed 's/G//'")
            disk_gb = int(stdout.read().decode().strip())
            
            ssh.close()
            
            # Обновляем информацию о сервере
            server.cpu_cores = cpu_cores
            server.memory_gb = memory_gb
            server.disk_gb = disk_gb
            
            return {
                "cpu_cores": cpu_cores,
                "memory_gb": memory_gb,
                "disk_gb": disk_gb
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения ресурсов сервера {server.host}: {e}")
            return {"cpu_cores": 0, "memory_gb": 0, "disk_gb": 0}
    
    def calculate_server_priority(self, server: ServerInfo, resources: Dict[str, Any]) -> int:
        """Расчет приоритета сервера"""
        priority = 5  # Базовый приоритет
        
        # Учитываем ресурсы
        if resources["cpu_cores"] >= 4:
            priority += 2
        if resources["memory_gb"] >= 8:
            priority += 2
        if resources["disk_gb"] >= 50:
            priority += 1
        
        # Учитываем статус
        if server.status == "available":
            priority += 1
        
        # Учитываем последнюю проверку
        if server.last_check:
            last_check = datetime.fromisoformat(server.last_check)
            if (datetime.now() - last_check).seconds < 300:  # Проверен недавно
                priority += 1
        
        return min(priority, 10)  # Максимум 10
    
    def select_best_server(self, available_targets: List[ReplicationTarget]) -> Optional[ReplicationTarget]:
        """Выбор лучшего сервера для развертывания"""
        if not available_targets:
            return None
        
        # Выбираем сервер с наивысшим приоритетом
        best_target = available_targets[0]
        
        # Проверяем, что ресурсов достаточно
        if (best_target.server.cpu_cores >= best_target.resources_needed["cpu"] and
            best_target.server.memory_gb >= best_target.resources_needed["memory"] and
            best_target.server.disk_gb >= best_target.resources_needed["disk"]):
            
            return best_target
        
        return None
    
    async def deploy_to_server(self, target: ReplicationTarget, image) -> Dict[str, Any]:
        """Развертывание на выбранном сервере"""
        start_time = time.time()
        
        try:
            logger.info(f"🚀 Развертываем JARVIS на сервер {target.server.host}...")
            
            # Подключаемся к серверу
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=target.server.host,
                port=target.server.port,
                username=target.server.username,
                key_filename=target.server.ssh_key_path if target.server.ssh_key_path else None,
                timeout=30
            )
            
            # Проверяем наличие Docker
            stdin, stdout, stderr = ssh.exec_command("docker --version")
            if stdout.channel.recv_exit_status() != 0:
                # Устанавливаем Docker
                logger.info("Устанавливаем Docker на сервере...")
                install_commands = [
                    "curl -fsSL https://get.docker.com -o get-docker.sh",
                    "sh get-docker.sh",
                    "systemctl start docker",
                    "systemctl enable docker"
                ]
                
                for cmd in install_commands:
                    stdin, stdout, stderr = ssh.exec_command(cmd)
                    stdout.channel.recv_exit_status()
            
            # Сохраняем образ в файл
            image_path = "/tmp/jarvis_image.tar"
            with open(image_path, "wb") as f:
                for chunk in image.save():
                    f.write(chunk)
            
            # Копируем образ на сервер
            sftp = ssh.open_sftp()
            remote_image_path = "/tmp/jarvis_image.tar"
            sftp.put(image_path, remote_image_path)
            sftp.close()
            
            # Загружаем образ на сервере
            stdin, stdout, stderr = ssh.exec_command(f"docker load < {remote_image_path}")
            if stdout.channel.recv_exit_status() != 0:
                raise Exception("Не удалось загрузить Docker образ")
            
            # Находим свободный порт
            port = await self.find_free_port(target.server)
            
            # Запускаем контейнер
            container_name = f"{self.config['replication']['deployment']['container_name_prefix']}_{int(time.time())}"
            run_command = f"""
docker run -d \\
    --name {container_name} \\
    -p {port}:8080 \\
    --restart unless-stopped \\
    {self.config['replication']['deployment']['image_tag']}
"""
            
            stdin, stdout, stderr = ssh.exec_command(run_command)
            if stdout.channel.recv_exit_status() != 0:
                raise Exception("Не удалось запустить контейнер")
            
            # Проверяем, что контейнер запустился
            await asyncio.sleep(10)
            stdin, stdout, stderr = ssh.exec_command(f"docker ps | grep {container_name}")
            if stdout.channel.recv_exit_status() != 0:
                raise Exception("Контейнер не запустился")
            
            # Проверяем доступность веб-интерфейса
            health_url = f"http://{target.server.host}:{port}/api/status"
            health_check = await self.check_health_endpoint(health_url)
            
            ssh.close()
            
            deployment_time = time.time() - start_time
            
            if health_check:
                # Добавляем в активные развертывания
                self.active_deployments[container_name] = {
                    "server": target.server.host,
                    "port": port,
                    "container_name": container_name,
                    "deployed_at": datetime.now().isoformat(),
                    "status": "running"
                }
                
                logger.info(f"✅ Развертывание успешно завершено за {deployment_time:.2f}с")
                
                return {
                    "success": True,
                    "server": target.server.host,
                    "port": port,
                    "container_name": container_name,
                    "deployment_time": deployment_time,
                    "health_check": True
                }
            else:
                raise Exception("Health check не прошел")
                
        except Exception as e:
            logger.error(f"❌ Ошибка развертывания на {target.server.host}: {e}")
            return {
                "success": False,
                "error": str(e),
                "server": target.server.host,
                "deployment_time": time.time() - start_time
            }
    
    async def find_free_port(self, server: ServerInfo) -> int:
        """Поиск свободного порта на сервере"""
        port_range = self.config["replication"]["deployment"]["port_range"]
        
        for port in range(port_range[0], port_range[1]):
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(
                    hostname=server.host,
                    port=server.port,
                    username=server.username,
                    key_filename=server.ssh_key_path if server.ssh_key_path else None,
                    timeout=10
                )
                
                stdin, stdout, stderr = ssh.exec_command(f"netstat -tln | grep :{port}")
                if stdout.channel.recv_exit_status() != 0:  # Порт свободен
                    ssh.close()
                    return port
                
                ssh.close()
            except:
                continue
        
        return port_range[0]  # Возвращаем первый порт если ничего не найдено
    
    async def check_health_endpoint(self, url: str) -> bool:
        """Проверка доступности health endpoint"""
        try:
            response = requests.get(url, timeout=30)
            return response.status_code == 200
        except:
            return False
    
    def discover_new_servers(self):
        """Поиск новых серверов в сети"""
        networks = self.config["replication"]["server_discovery"]["scan_networks"]
        ports = self.config["replication"]["server_discovery"]["common_ports"]
        
        for network in networks:
            # Здесь можно добавить сканирование сети
            # Пока заглушка
            logger.info(f"Сканируем сеть {network}...")
    
    def check_deployed_instances_health(self):
        """Проверка здоровья развернутых экземпляров"""
        for container_name, info in list(self.active_deployments.items()):
            try:
                health_url = f"http://{info['server']}:{info['port']}/api/status"
                
                # Проверяем доступность
                response = requests.get(health_url, timeout=10)
                if response.status_code != 200:
                    logger.warning(f"⚠️ Экземпляр {container_name} недоступен")
                    info["status"] = "unhealthy"
                else:
                    info["status"] = "healthy"
                    
            except Exception as e:
                logger.warning(f"⚠️ Ошибка проверки здоровья {container_name}: {e}")
                info["status"] = "unhealthy"
    
    def cleanup_failed_deployments(self):
        """Очистка неудачных развертываний"""
        for container_name, info in list(self.active_deployments.items()):
            if info["status"] == "unhealthy":
                logger.info(f"🧹 Удаляем неудачное развертывание {container_name}")
                del self.active_deployments[container_name]
                
                # Обновляем счетчик экземпляров
                self.core.state.total_instances = max(1, self.core.state.total_instances - 1)
    
    def get_replication_status(self) -> Dict[str, Any]:
        """Получение статуса репликации"""
        return {
            "enabled": self.config["replication"]["enabled"],
            "total_instances": self.core.state.total_instances,
            "known_servers": len(self.known_servers),
            "active_deployments": len(self.active_deployments),
            "deployments": self.active_deployments,
            "replication_history": self.replication_history[-10:],  # Последние 10
            "last_replication": self.core.state.last_self_replication
        }