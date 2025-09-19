#!/usr/bin/env python3
"""
Оптимизатор производительности Ollama
Мониторинг и оптимизация AI движка
"""

import asyncio
import logging
import psutil
import requests
import subprocess
import time
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaOptimizer:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.optimization_threshold = 80  # CPU threshold for optimization
        
    def get_ollama_processes(self) -> list:
        """Получение процессов Ollama"""
        ollama_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'cmdline']):
            try:
                if 'ollama' in proc.info['name'].lower():
                    ollama_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return ollama_processes
    
    def check_ollama_health(self) -> Dict[str, Any]:
        """Проверка здоровья Ollama"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return {
                    "status": "healthy",
                    "models_count": len(models),
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def optimize_ollama_performance(self):
        """Оптимизация производительности Ollama"""
        processes = self.get_ollama_processes()
        
        for proc_info in processes:
            if proc_info['cpu_percent'] > self.optimization_threshold:
                logger.warning(f"⚠️ Высокая нагрузка на процесс {proc_info['pid']}: {proc_info['cpu_percent']:.1f}% CPU")
                
                # Проверяем, не завис ли процесс
                if proc_info['cpu_percent'] > 500:  # Аномально высокая нагрузка
                    logger.warning(f"🚨 Аномальная нагрузка на процесс {proc_info['pid']}: {proc_info['cpu_percent']:.1f}% CPU")
                    
                    # Перезапускаем Ollama если он завис
                    self.restart_ollama_if_needed()
    
    def restart_ollama_if_needed(self):
        """Перезапуск Ollama при необходимости"""
        try:
            logger.info("🔄 Перезапуск Ollama для оптимизации...")
            
            # Останавливаем Ollama
            subprocess.run(['pkill', '-f', 'ollama'], check=False)
            time.sleep(2)
            
            # Запускаем Ollama заново
            subprocess.Popen(['ollama', 'serve'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            
            # Ждем запуска
            time.sleep(5)
            
            # Проверяем, что Ollama запустился
            health = self.check_ollama_health()
            if health['status'] == 'healthy':
                logger.info("✅ Ollama успешно перезапущен")
            else:
                logger.error(f"❌ Ошибка перезапуска Ollama: {health}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка перезапуска Ollama: {e}")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Получение статистики системы"""
        processes = self.get_ollama_processes()
        health = self.check_ollama_health()
        
        total_cpu = sum(proc['cpu_percent'] for proc in processes)
        total_memory = sum(proc['memory_percent'] for proc in processes)
        
        return {
            "ollama_processes": len(processes),
            "total_cpu_usage": total_cpu,
            "total_memory_usage": total_memory,
            "health_status": health,
            "processes": processes
        }
    
    async def monitor_and_optimize(self):
        """Мониторинг и оптимизация в реальном времени"""
        logger.info("🚀 Запуск мониторинга Ollama...")
        
        while True:
            try:
                stats = self.get_system_stats()
                
                # Логируем статистику
                logger.info(f"📊 Ollama статистика: {stats['ollama_processes']} процессов, "
                          f"CPU: {stats['total_cpu_usage']:.1f}%, "
                          f"Memory: {stats['total_memory_usage']:.1f}%")
                
                # Оптимизируем при необходимости
                self.optimize_ollama_performance()
                
                # Ждем перед следующей проверкой
                await asyncio.sleep(30)  # Проверяем каждые 30 секунд
                
            except Exception as e:
                logger.error(f"❌ Ошибка мониторинга: {e}")
                await asyncio.sleep(10)

async def main():
    """Главная функция"""
    optimizer = OllamaOptimizer()
    await optimizer.monitor_and_optimize()

if __name__ == "__main__":
    asyncio.run(main())


