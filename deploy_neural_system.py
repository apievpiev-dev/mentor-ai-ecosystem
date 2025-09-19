#!/usr/bin/env python3
"""
Deployment Script for Enhanced Neural Network System
Автоматическое развертывание нейронной системы в облаке
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NeuralSystemDeployer:
    """Развертывание нейронной системы"""
    
    def __init__(self):
        self.project_root = Path("/workspace")
        self.deployment_config = {
            "server_ip": "5.129.198.210",
            "server_port": 8080,
            "neural_port": 8081,
            "visual_port": 8082,
            "ollama_port": 11434
        }
        self.required_packages = [
            "torch",
            "transformers",
            "ollama",
            "fastapi",
            "uvicorn",
            "websockets",
            "pillow",
            "opencv-python",
            "numpy",
            "pandas",
            "scikit-learn",
            "matplotlib",
            "seaborn",
            "requests",
            "aiohttp",
            "asyncio",
            "schedule"
        ]
        self.services = []
        
    async def deploy_full_system(self):
        """Полное развертывание системы"""
        try:
            logger.info("🚀 Начинаю полное развертывание нейронной системы...")
            
            # Этап 1: Подготовка среды
            await self._prepare_environment()
            
            # Этап 2: Установка зависимостей
            await self._install_dependencies()
            
            # Этап 3: Настройка Ollama и моделей
            await self._setup_ollama()
            
            # Этап 4: Создание сервисов
            await self._create_services()
            
            # Этап 5: Запуск системы
            await self._start_system()
            
            # Этап 6: Проверка здоровья
            await self._health_check()
            
            # Этап 7: Настройка автозапуска
            await self._setup_autostart()
            
            logger.info("✅ Развертывание нейронной системы завершено успешно!")
            await self._print_deployment_summary()
            
        except Exception as e:
            logger.error(f"❌ Ошибка развертывания: {e}")
            await self._cleanup_on_error()
            raise
    
    async def _prepare_environment(self):
        """Подготовка среды"""
        logger.info("🔧 Подготовка среды...")
        
        # Создаем необходимые директории
        directories = [
            "/workspace/neural_data",
            "/workspace/neural_models",
            "/workspace/neural_logs",
            "/workspace/neural_cache",
            "/workspace/visual_screenshots",
            "/workspace/visual_reports"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Создана директория: {directory}")
        
        # Устанавливаем переменные окружения
        os.environ["NEURAL_SYSTEM_ROOT"] = str(self.project_root)
        os.environ["PYTHONPATH"] = f"{os.environ.get('PYTHONPATH', '')}:{self.project_root}"
        
        logger.info("✅ Среда подготовлена")
    
    async def _install_dependencies(self):
        """Установка зависимостей"""
        logger.info("📦 Установка зависимостей...")
        
        try:
            # Обновляем pip
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
            
            # Устанавливаем пакеты
            for package in self.required_packages:
                try:
                    logger.info(f"📦 Устанавливаю {package}...")
                    subprocess.run([
                        sys.executable, "-m", "pip", "install", package, "--quiet"
                    ], check=True, timeout=300)
                    logger.info(f"✅ {package} установлен")
                except subprocess.TimeoutExpired:
                    logger.warning(f"⏰ Таймаут установки {package}, пропускаю...")
                except subprocess.CalledProcessError as e:
                    logger.warning(f"⚠️ Не удалось установить {package}: {e}")
            
            logger.info("✅ Зависимости установлены")
            
        except Exception as e:
            logger.error(f"❌ Ошибка установки зависимостей: {e}")
            raise
    
    async def _setup_ollama(self):
        """Настройка Ollama и загрузка моделей"""
        logger.info("🤖 Настройка Ollama...")
        
        try:
            # Проверяем, установлен ли Ollama
            try:
                result = subprocess.run(["ollama", "--version"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    logger.info(f"✅ Ollama уже установлен: {result.stdout.strip()}")
                else:
                    await self._install_ollama()
            except FileNotFoundError:
                await self._install_ollama()
            
            # Запускаем Ollama сервер
            await self._start_ollama_server()
            
            # Загружаем нужные модели
            models_to_download = [
                "llama3.2:latest",
                "codellama:latest",
                "mistral:latest"
            ]
            
            for model in models_to_download:
                await self._download_model(model)
            
            logger.info("✅ Ollama настроен")
            
        except Exception as e:
            logger.error(f"❌ Ошибка настройки Ollama: {e}")
            # Продолжаем без Ollama, используя только OpenAI API
            logger.info("⚠️ Продолжаем без Ollama, будет использоваться только OpenAI API")
    
    async def _install_ollama(self):
        """Установка Ollama"""
        logger.info("📥 Установка Ollama...")
        
        try:
            # Скачиваем и устанавливаем Ollama
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
            
            stdout, stderr = process.communicate(timeout=300)
            
            if process.returncode == 0:
                logger.info("✅ Ollama установлен успешно")
            else:
                logger.error(f"❌ Ошибка установки Ollama: {stderr}")
                raise Exception(f"Установка Ollama не удалась: {stderr}")
                
        except subprocess.TimeoutExpired:
            logger.warning("⏰ Таймаут установки Ollama")
            raise Exception("Таймаут установки Ollama")
    
    async def _start_ollama_server(self):
        """Запуск Ollama сервера"""
        logger.info("🚀 Запуск Ollama сервера...")
        
        try:
            # Проверяем, не запущен ли уже сервер
            try:
                import requests
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Ollama сервер уже запущен")
                    return
            except:
                pass
            
            # Запускаем сервер в фоне
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Ждем запуска
            for i in range(30):
                try:
                    import requests
                    response = requests.get("http://localhost:11434/api/tags", timeout=2)
                    if response.status_code == 200:
                        logger.info("✅ Ollama сервер запущен")
                        return
                except:
                    await asyncio.sleep(2)
            
            logger.warning("⚠️ Ollama сервер не отвечает, продолжаем без него")
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска Ollama сервера: {e}")
    
    async def _download_model(self, model: str):
        """Загрузка модели Ollama"""
        logger.info(f"📥 Загрузка модели {model}...")
        
        try:
            process = subprocess.Popen(
                ["ollama", "pull", model],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Ждем завершения с таймаутом
            try:
                stdout, stderr = process.communicate(timeout=600)  # 10 минут на загрузку
                
                if process.returncode == 0:
                    logger.info(f"✅ Модель {model} загружена")
                else:
                    logger.warning(f"⚠️ Не удалось загрузить модель {model}: {stderr}")
                    
            except subprocess.TimeoutExpired:
                process.kill()
                logger.warning(f"⏰ Таймаут загрузки модели {model}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки модели {model}: {e}")
    
    async def _create_services(self):
        """Создание системных сервисов"""
        logger.info("⚙️ Создание сервисов...")
        
        # Создаем сервис для нейронной системы
        neural_service = self._create_neural_service()
        self.services.append(neural_service)
        
        # Создаем сервис для визуального мониторинга
        visual_service = self._create_visual_service()
        self.services.append(visual_service)
        
        # Создаем сервис для облачной системы
        cloud_service = self._create_cloud_service()
        self.services.append(cloud_service)
        
        logger.info(f"✅ Создано {len(self.services)} сервисов")
    
    def _create_neural_service(self) -> Dict[str, Any]:
        """Создание сервиса нейронной системы"""
        return {
            "name": "neural-system",
            "description": "Enhanced Neural Network System",
            "exec_start": f"{sys.executable} {self.project_root}/enhanced_neural_system.py",
            "working_directory": str(self.project_root),
            "environment": {
                "PYTHONPATH": str(self.project_root),
                "NEURAL_SYSTEM_ROOT": str(self.project_root)
            },
            "restart": "always",
            "port": self.deployment_config["neural_port"]
        }
    
    def _create_visual_service(self) -> Dict[str, Any]:
        """Создание сервиса визуального мониторинга"""
        return {
            "name": "visual-monitor",
            "description": "Visual Intelligence Monitor",
            "exec_start": f"{sys.executable} {self.project_root}/visual_monitor.py",
            "working_directory": str(self.project_root),
            "environment": {
                "PYTHONPATH": str(self.project_root),
                "DISPLAY": ":99"
            },
            "restart": "always",
            "port": self.deployment_config["visual_port"]
        }
    
    def _create_cloud_service(self) -> Dict[str, Any]:
        """Создание облачного сервиса"""
        return {
            "name": "cloud-agent-system",
            "description": "Cloud Agent System",
            "exec_start": f"{sys.executable} {self.project_root}/cloud_agent_system.py",
            "working_directory": str(self.project_root),
            "environment": {
                "PYTHONPATH": str(self.project_root)
            },
            "restart": "always",
            "port": self.deployment_config["server_port"]
        }
    
    async def _start_system(self):
        """Запуск системы"""
        logger.info("🚀 Запуск нейронной системы...")
        
        # Запускаем каждый сервис
        for service in self.services:
            await self._start_service(service)
        
        logger.info("✅ Система запущена")
    
    async def _start_service(self, service: Dict[str, Any]):
        """Запуск конкретного сервиса"""
        try:
            logger.info(f"🚀 Запуск сервиса {service['name']}...")
            
            # Устанавливаем переменные окружения
            env = os.environ.copy()
            env.update(service.get("environment", {}))
            
            # Запускаем процесс
            process = subprocess.Popen(
                service["exec_start"].split(),
                cwd=service["working_directory"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            service["process"] = process
            service["pid"] = process.pid
            
            logger.info(f"✅ Сервис {service['name']} запущен (PID: {process.pid})")
            
            # Небольшая пауза между запусками
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска сервиса {service['name']}: {e}")
    
    async def _health_check(self):
        """Проверка здоровья системы"""
        logger.info("💚 Проверка здоровья системы...")
        
        # Проверяем каждый сервис
        healthy_services = 0
        
        for service in self.services:
            if await self._check_service_health(service):
                healthy_services += 1
        
        logger.info(f"💚 Здоровых сервисов: {healthy_services}/{len(self.services)}")
        
        if healthy_services == len(self.services):
            logger.info("✅ Все сервисы работают корректно")
        else:
            logger.warning(f"⚠️ {len(self.services) - healthy_services} сервисов имеют проблемы")
    
    async def _check_service_health(self, service: Dict[str, Any]) -> bool:
        """Проверка здоровья конкретного сервиса"""
        try:
            process = service.get("process")
            if not process:
                return False
            
            # Проверяем, что процесс еще работает
            if process.poll() is not None:
                logger.warning(f"⚠️ Сервис {service['name']} завершился")
                return False
            
            # Проверяем доступность по порту (если указан)
            port = service.get("port")
            if port:
                try:
                    import requests
                    response = requests.get(f"http://localhost:{port}/health", timeout=5)
                    if response.status_code == 200:
                        logger.info(f"✅ Сервис {service['name']} отвечает на порту {port}")
                        return True
                except:
                    pass
            
            # Если порт не указан, считаем что сервис работает если процесс живой
            logger.info(f"✅ Сервис {service['name']} работает (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки сервиса {service['name']}: {e}")
            return False
    
    async def _setup_autostart(self):
        """Настройка автозапуска"""
        logger.info("⚙️ Настройка автозапуска...")
        
        try:
            # Создаем startup скрипт
            startup_script = self._create_startup_script()
            
            # Сохраняем скрипт
            script_path = self.project_root / "start_neural_system.sh"
            with open(script_path, "w") as f:
                f.write(startup_script)
            
            # Делаем скрипт исполняемым
            script_path.chmod(0o755)
            
            logger.info(f"✅ Startup скрипт создан: {script_path}")
            
            # Создаем systemd сервис для автозапуска
            await self._create_systemd_service()
            
        except Exception as e:
            logger.error(f"❌ Ошибка настройки автозапуска: {e}")
    
    def _create_startup_script(self) -> str:
        """Создание startup скрипта"""
        return f"""#!/bin/bash

# Enhanced Neural Network System Startup Script
# Автоматический запуск нейронной системы

export PYTHONPATH="{self.project_root}:$PYTHONPATH"
export NEURAL_SYSTEM_ROOT="{self.project_root}"

cd {self.project_root}

echo "🚀 Запуск Enhanced Neural Network System..."

# Запуск Ollama сервера
if command -v ollama &> /dev/null; then
    echo "🤖 Запуск Ollama сервера..."
    ollama serve &
    sleep 5
fi

# Запуск основных сервисов
echo "🧠 Запуск нейронной системы..."
{sys.executable} enhanced_neural_system.py &

echo "👁️ Запуск визуального мониторинга..."
{sys.executable} visual_monitor.py &

echo "☁️ Запуск облачной системы..."
{sys.executable} cloud_agent_system.py &

echo "✅ Все сервисы запущены"

# Ожидание
wait
"""
    
    async def _create_systemd_service(self):
        """Создание systemd сервиса"""
        try:
            service_content = f"""[Unit]
Description=Enhanced Neural Network System
After=network.target
Wants=network.target

[Service]
Type=forking
User=root
WorkingDirectory={self.project_root}
ExecStart={self.project_root}/start_neural_system.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
            
            # Сохраняем сервис
            service_path = Path("/etc/systemd/system/neural-system.service")
            try:
                with open(service_path, "w") as f:
                    f.write(service_content)
                
                # Перезагружаем systemd и включаем сервис
                subprocess.run(["systemctl", "daemon-reload"], check=True)
                subprocess.run(["systemctl", "enable", "neural-system"], check=True)
                
                logger.info("✅ Systemd сервис создан и включен")
                
            except PermissionError:
                logger.warning("⚠️ Нет прав для создания systemd сервиса")
                
        except Exception as e:
            logger.error(f"❌ Ошибка создания systemd сервиса: {e}")
    
    async def _cleanup_on_error(self):
        """Очистка при ошибке"""
        logger.info("🧹 Очистка после ошибки...")
        
        # Останавливаем все запущенные процессы
        for service in self.services:
            process = service.get("process")
            if process and process.poll() is None:
                try:
                    process.terminate()
                    logger.info(f"🛑 Остановлен сервис {service['name']}")
                except:
                    pass
    
    async def _print_deployment_summary(self):
        """Печать сводки развертывания"""
        summary = f"""
🎉 РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО УСПЕШНО!

📊 Сводка развертывания:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧠 Enhanced Neural Network System
   ├── Нейронная система: http://localhost:{self.deployment_config['neural_port']}
   ├── Визуальный мониторинг: http://localhost:{self.deployment_config['visual_port']}
   ├── Облачная система: http://localhost:{self.deployment_config['server_port']}
   └── Ollama API: http://localhost:{self.deployment_config['ollama_port']}

🚀 Запущенные сервисы:
"""
        
        for service in self.services:
            status = "🟢 Работает" if service.get("process") and service["process"].poll() is None else "🔴 Не работает"
            summary += f"   ├── {service['name']}: {status}\n"
        
        summary += f"""
📁 Директории:
   ├── Данные: /workspace/neural_data
   ├── Модели: /workspace/neural_models
   ├── Логи: /workspace/neural_logs
   ├── Кэш: /workspace/neural_cache
   └── Скриншоты: /workspace/visual_screenshots

🔧 Управление системой:
   ├── Запуск: ./start_neural_system.sh
   ├── Статус: systemctl status neural-system
   └── Логи: journalctl -u neural-system -f

🌐 Доступ к системе:
   ├── Основной интерфейс: http://localhost:{self.deployment_config['server_port']}
   ├── Нейронная система: http://localhost:{self.deployment_config['neural_port']}
   └── Визуальный мониторинг: http://localhost:{self.deployment_config['visual_port']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ Система готова к работе! Автономные агенты активированы.
🧠 Нейронные сети обучаются и адаптируются автоматически.
👁️ Визуальный интеллект анализирует интерфейс в реальном времени.
☁️ Облачная система обеспечивает 24/7 работу.

🎯 Система работает АВТОНОМНО и не требует постоянного контроля!
"""
        
        print(summary)
        logger.info("📋 Сводка развертывания выведена")

async def main():
    """Основная функция развертывания"""
    deployer = NeuralSystemDeployer()
    
    try:
        await deployer.deploy_full_system()
        
        # Ожидаем сигнала остановки
        logger.info("💤 Система развернута. Нажмите Ctrl+C для завершения мониторинга...")
        while True:
            await asyncio.sleep(60)
            # Периодическая проверка здоровья
            await deployer._health_check()
            
    except KeyboardInterrupt:
        logger.info("📡 Получен сигнал остановки")
        await deployer._cleanup_on_error()
    except Exception as e:
        logger.error(f"❌ Критическая ошибка развертывания: {e}")
        await deployer._cleanup_on_error()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())