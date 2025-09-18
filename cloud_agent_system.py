#!/usr/bin/env python3
"""
Облачная система агентов для работы онлайн
Автономный сервер с автозапуском и сохранением состояния
"""

import asyncio
import json
import logging
import os
import signal
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import threading
import schedule

from integrated_agent_system import integrated_system
from ai_engine import ai_engine
from ai_manager_agent import ai_manager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/mentor/cloud_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CloudAgentSystem:
    """Облачная система агентов"""
    
    def __init__(self):
        self.running = False
        self.auto_restart = True
        self.health_check_interval = 300  # 5 минут
        self.backup_interval = 3600  # 1 час
        self.system_state_file = Path("/home/mentor/system_state.json")
        self.pid_file = Path("/home/mentor/cloud_system.pid")
        self.health_status = "unknown"
        self.last_health_check = None
        self.startup_time = None
        
        # Настройка обработчиков сигналов
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGHUP, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Обработчик сигналов для корректного завершения"""
        logger.info(f"📡 Получен сигнал {signum}, завершаем работу...")
        self.running = False
        self._save_system_state()
        sys.exit(0)
    
    async def start(self):
        """Запуск облачной системы"""
        try:
            logger.info("☁️ Запуск облачной системы агентов...")
            
            # Создаем PID файл
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
            
            # Загружаем состояние системы
            await self._load_system_state()
            
            # Запускаем интегрированную систему
            await integrated_system.start()
            
            # Запускаем AI менеджер
            await self._start_ai_manager()
            
            # Запускаем мониторинг
            self._start_monitoring()
            
            # Запускаем планировщик задач
            self._start_scheduler()
            
            self.running = True
            self.startup_time = datetime.now()
            self.health_status = "healthy"
            
            logger.info("✅ Облачная система агентов запущена")
            
            # Основной цикл
            await self._main_loop()
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска облачной системы: {e}")
            raise
    
    async def _start_ai_manager(self):
        """Запуск AI менеджера"""
        try:
            # Регистрируем AI менеджера в системе
            integrated_system.multi_agent_system.agents[ai_manager.agent_id] = ai_manager
            ai_manager.set_shared_memory(integrated_system.shared_memory)
            integrated_system.coordinator.register_agent(ai_manager)
            
            # Автоматически устанавливаем модели
            await ai_manager.auto_install_models()
            
            logger.info("✅ AI менеджер запущен")
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска AI менеджера: {e}")
    
    def _start_monitoring(self):
        """Запуск мониторинга системы"""
        def monitor_loop():
            while self.running:
                try:
                    self._health_check()
                    time.sleep(self.health_check_interval)
                except Exception as e:
                    logger.error(f"❌ Ошибка мониторинга: {e}")
                    time.sleep(60)  # Пауза при ошибке
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        logger.info("📊 Мониторинг системы запущен")
    
    def _start_scheduler(self):
        """Запуск планировщика задач"""
        def scheduler_loop():
            while self.running:
                try:
                    schedule.run_pending()
                    time.sleep(60)
                except Exception as e:
                    logger.error(f"❌ Ошибка планировщика: {e}")
                    time.sleep(60)
        
        # Настраиваем расписание
        schedule.every().hour.do(self._backup_system)
        schedule.every().day.at("02:00").do(self._cleanup_logs)
        schedule.every().day.at("03:00").do(self._optimize_models)
        
        scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        scheduler_thread.start()
        logger.info("⏰ Планировщик задач запущен")
    
    async def _main_loop(self):
        """Основной цикл системы"""
        try:
            while self.running:
                # Проверяем здоровье системы
                if self.health_status != "healthy":
                    await self._recover_system()
                
                # Обновляем состояние
                await self._update_system_state()
                
                # Пауза между итерациями
                await asyncio.sleep(30)
                
        except Exception as e:
            logger.error(f"❌ Ошибка в основном цикле: {e}")
            if self.auto_restart:
                logger.info("🔄 Перезапуск системы...")
                await self._restart_system()
    
    def _health_check(self):
        """Проверка здоровья системы"""
        try:
            # Проверяем доступность AI движка
            ai_status = ai_engine.get_status()
            ai_healthy = ai_status.get("default_engine") != "none"
            
            # Проверяем доступность интегрированной системы
            system_status = integrated_system.get_system_status()
            system_healthy = system_status.get("system_status") == "running"
            
            # Проверяем использование ресурсов
            memory_usage = self._get_memory_usage()
            disk_usage = self._get_disk_usage()
            
            # Определяем общее состояние
            if ai_healthy and system_healthy and memory_usage < 90 and disk_usage < 90:
                self.health_status = "healthy"
            elif memory_usage > 95 or disk_usage > 95:
                self.health_status = "critical"
            else:
                self.health_status = "warning"
            
            self.last_health_check = datetime.now()
            
            logger.info(f"💚 Проверка здоровья: {self.health_status} (память: {memory_usage}%, диск: {disk_usage}%)")
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки здоровья: {e}")
            self.health_status = "error"
    
    async def _recover_system(self):
        """Восстановление системы"""
        try:
            logger.info("🔧 Восстановление системы...")
            
            if self.health_status == "critical":
                # Критическое состояние - перезапуск
                await self._restart_system()
            elif self.health_status == "warning":
                # Предупреждение - оптимизация
                await self._optimize_system()
            elif self.health_status == "error":
                # Ошибка - полный перезапуск
                await self._full_restart()
            
        except Exception as e:
            logger.error(f"❌ Ошибка восстановления системы: {e}")
    
    async def _restart_system(self):
        """Перезапуск системы"""
        try:
            logger.info("🔄 Перезапуск системы...")
            
            # Останавливаем систему
            await integrated_system.stop()
            
            # Ждем немного
            await asyncio.sleep(5)
            
            # Запускаем заново
            await integrated_system.start()
            
            self.health_status = "healthy"
            logger.info("✅ Система перезапущена")
            
        except Exception as e:
            logger.error(f"❌ Ошибка перезапуска: {e}")
    
    async def _optimize_system(self):
        """Оптимизация системы"""
        try:
            logger.info("⚡ Оптимизация системы...")
            
            # Очистка памяти
            await self._cleanup_memory()
            
            # Оптимизация моделей
            await self._optimize_models()
            
            self.health_status = "healthy"
            logger.info("✅ Система оптимизирована")
            
        except Exception as e:
            logger.error(f"❌ Ошибка оптимизации: {e}")
    
    async def _full_restart(self):
        """Полный перезапуск системы"""
        try:
            logger.info("🔄 Полный перезапуск системы...")
            
            # Сохраняем состояние
            self._save_system_state()
            
            # Останавливаем все
            await integrated_system.stop()
            
            # Ждем
            await asyncio.sleep(10)
            
            # Запускаем заново
            await self.start()
            
        except Exception as e:
            logger.error(f"❌ Ошибка полного перезапуска: {e}")
    
    async def _cleanup_memory(self):
        """Очистка памяти"""
        try:
            # Очистка кэша AI
            if hasattr(ai_engine, 'clear_cache'):
                ai_engine.clear_cache()
            
            # Очистка логов
            self._cleanup_logs()
            
            logger.info("🧹 Память очищена")
            
        except Exception as e:
            logger.error(f"❌ Ошибка очистки памяти: {e}")
    
    def _cleanup_logs(self):
        """Очистка старых логов"""
        try:
            log_dir = Path("/home/mentor")
            for log_file in log_dir.glob("*.log"):
                if log_file.stat().st_size > 100 * 1024 * 1024:  # 100MB
                    # Ротируем лог
                    backup_name = f"{log_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                    log_file.rename(log_dir / backup_name)
                    
                    # Создаем новый пустой лог
                    log_file.touch()
            
            logger.info("📝 Логи очищены")
            
        except Exception as e:
            logger.error(f"❌ Ошибка очистки логов: {e}")
    
    async def _optimize_models(self):
        """Оптимизация AI моделей"""
        try:
            if ai_manager:
                result = await ai_manager._handle_optimize_models({})
                logger.info(f"🤖 Модели оптимизированы: {result.get('message', '')}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка оптимизации моделей: {e}")
    
    def _backup_system(self):
        """Резервное копирование системы"""
        try:
            backup_dir = Path("/home/mentor/backups")
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"system_backup_{timestamp}.json"
            
            # Сохраняем состояние системы
            state = {
                "timestamp": timestamp,
                "system_status": integrated_system.get_system_status(),
                "ai_status": ai_engine.get_status(),
                "health_status": self.health_status,
                "startup_time": self.startup_time.isoformat() if self.startup_time else None
            }
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            
            # Удаляем старые бэкапы (оставляем последние 10)
            backups = sorted(backup_dir.glob("system_backup_*.json"))
            for old_backup in backups[:-10]:
                old_backup.unlink()
            
            logger.info(f"💾 Резервная копия создана: {backup_file}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания резервной копии: {e}")
    
    async def _update_system_state(self):
        """Обновление состояния системы"""
        try:
            state = {
                "timestamp": datetime.now().isoformat(),
                "running": self.running,
                "health_status": self.health_status,
                "startup_time": self.startup_time.isoformat() if self.startup_time else None,
                "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
                "system_status": integrated_system.get_system_status(),
                "ai_status": ai_engine.get_status()
            }
            
            with open(self.system_state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"❌ Ошибка обновления состояния: {e}")
    
    async def _load_system_state(self):
        """Загрузка состояния системы"""
        try:
            if self.system_state_file.exists():
                with open(self.system_state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                
                logger.info(f"📂 Состояние системы загружено: {state.get('timestamp', 'unknown')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки состояния: {e}")
    
    def _save_system_state(self):
        """Сохранение состояния системы"""
        try:
            state = {
                "timestamp": datetime.now().isoformat(),
                "running": False,
                "health_status": self.health_status,
                "shutdown_time": datetime.now().isoformat()
            }
            
            with open(self.system_state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            
            # Удаляем PID файл
            if self.pid_file.exists():
                self.pid_file.unlink()
            
            logger.info("💾 Состояние системы сохранено")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения состояния: {e}")
    
    def _get_memory_usage(self) -> float:
        """Получить использование памяти"""
        try:
            result = subprocess.run(['free', '-m'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                mem_line = lines[1].split()
                used = int(mem_line[2])
                total = int(mem_line[1])
                return (used / total) * 100
        except:
            pass
        return 0.0
    
    def _get_disk_usage(self) -> float:
        """Получить использование диска"""
        try:
            result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) > 4:
                        usage = parts[4].replace('%', '')
                        return float(usage)
        except:
            pass
        return 0.0
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус облачной системы"""
        return {
            "running": self.running,
            "health_status": self.health_status,
            "startup_time": self.startup_time.isoformat() if self.startup_time else None,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "memory_usage": self._get_memory_usage(),
            "disk_usage": self._get_disk_usage(),
            "auto_restart": self.auto_restart,
            "system_status": integrated_system.get_system_status() if integrated_system else None
        }

# Глобальный экземпляр облачной системы
cloud_system = CloudAgentSystem()

if __name__ == "__main__":
    # Запуск облачной системы
    async def main():
        try:
            await cloud_system.start()
        except KeyboardInterrupt:
            logger.info("🛑 Получен сигнал прерывания")
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}")
        finally:
            cloud_system._save_system_state()
    
    asyncio.run(main())
