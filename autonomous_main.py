#!/usr/bin/env python3
"""
Главный скрипт автономной системы Multi-AI
Запускает все компоненты автономной работы
"""

import asyncio
import subprocess
import logging
import os
import sys
import time
import signal
import requests
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/mentor/autonomous_main.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutonomousMainSystem:
    def __init__(self):
        self.processes = {}
        self.running = False
        self.base_path = Path("/home/mentor")
        
    async def start_main_system(self):
        """Запуск основной системы Multi-AI"""
        logger.info("🚀 Запуск основной системы Multi-AI...")
        try:
            # Запускаем основную систему в фоновом режиме
            cmd = [
                sys.executable, 
                str(self.base_path / "start_multi_agent_system.py"),
                "0.0.0.0", 
                "8080"
            ]
            
            process = subprocess.Popen(
                cmd,
                cwd=str(self.base_path),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid
            )
            
            self.processes['main_system'] = process
            logger.info(f"✅ Основная система запущена (PID: {process.pid})")
            
            # Ждем запуска системы
            await asyncio.sleep(10)
            
            # Проверяем, что система запустилась
            if await self.check_main_system():
                logger.info("✅ Основная система работает корректно")
                return True
            else:
                logger.error("❌ Основная система не запустилась")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка запуска основной системы: {e}")
            return False
    
    async def start_autonomous_monitor(self):
        """Запуск автономного мониторинга"""
        logger.info("🚀 Запуск автономного мониторинга...")
        try:
            process = subprocess.Popen(
                [sys.executable, str(self.base_path / "autonomous_monitor.py")],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid
            )
            
            self.processes['monitor'] = process
            logger.info(f"✅ Автономный мониторинг запущен (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска автономного мониторинга: {e}")
            return False
    
    async def start_autonomous_scheduler(self):
        """Запуск планировщика автономных задач"""
        logger.info("🚀 Запуск планировщика автономных задач...")
        try:
            process = subprocess.Popen(
                [sys.executable, str(self.base_path / "autonomous_task_scheduler.py")],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid
            )
            
            self.processes['scheduler'] = process
            logger.info(f"✅ Планировщик автономных задач запущен (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска планировщика автономных задач: {e}")
            return False
    
    async def start_agent_activator(self):
        """Запуск активатора агентов"""
        logger.info("🚀 Запуск активатора агентов...")
        try:
            process = subprocess.Popen(
                [sys.executable, str(self.base_path / "agent_activator.py")],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid
            )
            
            self.processes['activator'] = process
            logger.info(f"✅ Активатор агентов запущен (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска активатора агентов: {e}")
            return False
    
    async def check_main_system(self):
        """Проверка работы основной системы"""
        try:
            response = requests.get("http://localhost:8080/api/system/status", timeout=5)
            if response.status_code == 200:
                status_data = response.json()
                return status_data.get("system_status") == "running"
            return False
        except:
            return False
    
    async def send_initial_tasks(self):
        """Отправка начальных задач агентам"""
        logger.info("📋 Отправка начальных задач агентам...")
        
        initial_tasks = [
            {
                "message": "Проанализируй текущее состояние системы и создай отчет о производительности",
                "agent_type": "data_analyst"
            },
            {
                "message": "Проверь код на наличие потенциальных улучшений и оптимизаций",
                "agent_type": "code_developer"
            },
            {
                "message": "Создай план развития системы на ближайшие дни",
                "agent_type": "project_manager"
            },
            {
                "message": "Проанализируй пользовательский интерфейс и предложи улучшения",
                "agent_type": "designer"
            },
            {
                "message": "Проведи базовое тестирование всех компонентов системы",
                "agent_type": "qa_tester"
            }
        ]
        
        for task in initial_tasks:
            try:
                response = requests.post(
                    "http://localhost:8080/api/chat/send",
                    json={
                        "message": task["message"],
                        "agent_type": task["agent_type"],
                        "user_id": "autonomous_main"
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Задача отправлена агенту {task['agent_type']}")
                else:
                    logger.warning(f"⚠️ Ошибка отправки задачи агенту {task['agent_type']}: {response.status_code}")
                    
                await asyncio.sleep(2)  # Пауза между задачами
                
            except Exception as e:
                logger.error(f"❌ Ошибка отправки задачи агенту {task['agent_type']}: {e}")
    
    async def monitor_processes(self):
        """Мониторинг процессов"""
        while self.running:
            try:
                for name, process in self.processes.items():
                    if process.poll() is not None:
                        logger.warning(f"⚠️ Процесс {name} завершился неожиданно (PID: {process.pid})")
                        
                        # Перезапускаем процесс
                        if name == 'main_system':
                            await self.start_main_system()
                        elif name == 'monitor':
                            await self.start_autonomous_monitor()
                        elif name == 'scheduler':
                            await self.start_autonomous_scheduler()
                        elif name == 'activator':
                            await self.start_agent_activator()
                
                await asyncio.sleep(30)  # Проверяем каждые 30 секунд
                
            except Exception as e:
                logger.error(f"❌ Ошибка мониторинга процессов: {e}")
                await asyncio.sleep(30)
    
    async def start(self):
        """Запуск всей автономной системы"""
        logger.info("🚀 Запуск автономной системы Multi-AI...")
        self.running = True
        
        try:
            # 1. Запускаем основную систему
            if not await self.start_main_system():
                logger.error("❌ Не удалось запустить основную систему")
                return False
            
            # 2. Ждем полного запуска
            await asyncio.sleep(15)
            
            # 3. Отправляем начальные задачи
            await self.send_initial_tasks()
            
            # 4. Запускаем автономный мониторинг
            await self.start_autonomous_monitor()
            
            # 5. Запускаем планировщик задач
            await self.start_autonomous_scheduler()
            
            # 6. Запускаем активатор агентов
            await self.start_agent_activator()
            
            logger.info("✅ Автономная система Multi-AI полностью запущена!")
            logger.info("🌐 Веб-интерфейс доступен по адресу: http://5.129.198.210:8080")
            logger.info("📊 API статуса: http://5.129.198.210:8080/api/system/status")
            
            # 7. Запускаем мониторинг процессов
            await self.monitor_processes()
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска автономной системы: {e}")
            await self.stop()
    
    async def stop(self):
        """Остановка автономной системы"""
        logger.info("🛑 Остановка автономной системы...")
        self.running = False
        
        for name, process in self.processes.items():
            try:
                if process.poll() is None:
                    logger.info(f"🛑 Остановка процесса {name} (PID: {process.pid})")
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    process.wait(timeout=10)
            except Exception as e:
                logger.error(f"❌ Ошибка остановки процесса {name}: {e}")
        
        self.processes.clear()
        logger.info("✅ Автономная система остановлена")

def signal_handler(signum, frame):
    """Обработчик сигналов для корректного завершения"""
    logger.info(f"📡 Получен сигнал {signum}, завершение работы...")
    asyncio.create_task(autonomous_system.stop())

async def main():
    """Главная функция"""
    global autonomous_system
    autonomous_system = AutonomousMainSystem()
    
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await autonomous_system.start()
    except KeyboardInterrupt:
        logger.info("📡 Получен сигнал прерывания")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
    finally:
        await autonomous_system.stop()

if __name__ == "__main__":
    asyncio.run(main())
