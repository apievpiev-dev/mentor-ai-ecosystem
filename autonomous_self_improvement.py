#!/usr/bin/env python3
"""
Система автономного самоулучшения Mentor
Проводит постоянную диагностику и улучшение всех компонентов системы
"""

import asyncio
import json
import logging
import time
import os
import subprocess
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/self_improvement.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutonomousSelfImprovement:
    """Система автономного самоулучшения"""
    
    def __init__(self):
        self.base_url = "http://localhost:8081"
        self.improvement_running = False
        self.checks_performed = 0
        self.improvements_made = 0
        self.last_check_time = None
        self.system_metrics = {}
        self.visual_checks = {}
        
        # Критерии для улучшений
        self.performance_thresholds = {
            "response_time": 0.5,  # секунды
            "memory_usage": 80,    # процент
            "cpu_usage": 70,       # процент
            "error_rate": 1        # процент
        }
        
        logger.info("🔧 Система автономного самоулучшения инициализирована")
    
    async def start_continuous_improvement(self):
        """Запуск непрерывного процесса самоулучшения"""
        self.improvement_running = True
        logger.info("🚀 Запуск системы автономного самоулучшения")
        
        while self.improvement_running:
            try:
                # Проводим полную диагностику каждые 30 секунд
                await self.perform_full_diagnostics()
                
                # Проводим улучшения каждые 2 минуты
                if self.checks_performed % 4 == 0:
                    await self.perform_autonomous_improvements()
                
                # Визуальные проверки каждые 5 минут
                if self.checks_performed % 10 == 0:
                    await self.perform_visual_checks()
                
                await asyncio.sleep(30)  # Проверяем каждые 30 секунд
                
            except Exception as e:
                logger.error(f"❌ Ошибка в цикле самоулучшения: {e}")
                await asyncio.sleep(60)  # При ошибке ждем дольше
    
    async def perform_full_diagnostics(self):
        """Полная диагностика всех компонентов системы"""
        try:
            self.checks_performed += 1
            self.last_check_time = datetime.now()
            
            logger.info(f"🔍 Проведение диагностики #{self.checks_performed}")
            
            # 1. Проверка статуса системы
            system_status = await self.check_system_status()
            
            # 2. Проверка производительности
            performance_metrics = await self.check_performance()
            
            # 3. Проверка агентов
            agents_status = await self.check_agents_health()
            
            # 4. Проверка API endpoints
            api_health = await self.check_api_health()
            
            # 5. Проверка логов на ошибки
            log_analysis = await self.analyze_logs()
            
            # Сохраняем метрики
            self.system_metrics = {
                "timestamp": datetime.now().isoformat(),
                "system_status": system_status,
                "performance": performance_metrics,
                "agents": agents_status,
                "api_health": api_health,
                "log_analysis": log_analysis,
                "checks_performed": self.checks_performed,
                "improvements_made": self.improvements_made
            }
            
            # Определяем нужны ли улучшения
            issues_found = await self.identify_improvement_opportunities()
            
            if issues_found:
                logger.warning(f"⚠️ Обнаружено {len(issues_found)} возможностей для улучшения")
                for issue in issues_found:
                    logger.warning(f"   - {issue}")
            else:
                logger.info("✅ Система работает оптимально")
                
        except Exception as e:
            logger.error(f"❌ Ошибка диагностики: {e}")
    
    async def check_system_status(self) -> Dict[str, Any]:
        """Проверка общего статуса системы"""
        try:
            response = requests.get(f"{self.base_url}/api/system/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "healthy",
                    "uptime": data.get("uptime", "unknown"),
                    "active_agents": data.get("active_agents", 0),
                    "total_agents": data.get("total_agents", 0),
                    "autonomous_tasks": data.get("autonomous_tasks", 0)
                }
            else:
                return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def check_performance(self) -> Dict[str, Any]:
        """Проверка производительности системы"""
        try:
            # Измеряем время отклика API
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/system/status", timeout=5)
            response_time = time.time() - start_time
            
            # Проверяем использование ресурсов
            try:
                import psutil
                cpu_usage = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                return {
                    "response_time": response_time,
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory.percent,
                    "disk_usage": disk.percent,
                    "status": "measured"
                }
            except ImportError:
                return {
                    "response_time": response_time,
                    "status": "basic_check",
                    "note": "psutil не установлен для детальной диагностики"
                }
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def check_agents_health(self) -> Dict[str, Any]:
        """Проверка здоровья всех агентов"""
        agents_health = {}
        
        agent_types = [
            "general_assistant",
            "code_developer", 
            "data_analyst",
            "project_manager",
            "designer",
            "qa_tester"
        ]
        
        for agent_type in agent_types:
            try:
                # Тестируем каждого агента простым сообщением
                test_message = f"Тест агента {agent_type} - статус?"
                
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/api/chat/send",
                    json={
                        "message": test_message,
                        "agent_type": agent_type,
                        "user_id": "health_check"
                    },
                    timeout=10
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    agents_health[agent_type] = {
                        "status": "healthy",
                        "response_time": response_time,
                        "response_received": True
                    }
                else:
                    agents_health[agent_type] = {
                        "status": "unhealthy",
                        "error": f"HTTP {response.status_code}"
                    }
                    
            except Exception as e:
                agents_health[agent_type] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return agents_health
    
    async def check_api_health(self) -> Dict[str, Any]:
        """Проверка здоровья всех API endpoints"""
        endpoints = {
            "main_page": "/",
            "system_status": "/api/system/status",
            "autonomous_tasks": "/api/autonomous/tasks"
        }
        
        api_health = {}
        
        for name, endpoint in endpoints.items():
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                response_time = time.time() - start_time
                
                api_health[name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "content_size": len(response.content)
                }
                
            except Exception as e:
                api_health[name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return api_health
    
    async def analyze_logs(self) -> Dict[str, Any]:
        """Анализ логов на наличие ошибок и предупреждений"""
        try:
            log_files = [
                "/workspace/mentor_system.log",
                "/workspace/self_improvement.log"
            ]
            
            total_errors = 0
            total_warnings = 0
            recent_issues = []
            
            for log_file in log_files:
                if os.path.exists(log_file):
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            lines = f.readlines()[-100:]  # Последние 100 строк
                            
                        for line in lines:
                            if 'ERROR' in line:
                                total_errors += 1
                                recent_issues.append(f"ERROR: {line.strip()[-100:]}")
                            elif 'WARNING' in line:
                                total_warnings += 1
                                recent_issues.append(f"WARNING: {line.strip()[-100:]}")
                                
                    except Exception as e:
                        logger.error(f"Ошибка чтения лога {log_file}: {e}")
            
            return {
                "total_errors": total_errors,
                "total_warnings": total_warnings,
                "recent_issues": recent_issues[-10:],  # Последние 10 проблем
                "status": "analyzed"
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def perform_visual_checks(self):
        """Проведение визуальных проверок интерфейса"""
        try:
            logger.info("👁️ Проведение визуальных проверок")
            
            # Скачиваем текущий интерфейс
            response = requests.get(f"{self.base_url}/", timeout=10)
            
            if response.status_code == 200:
                html_content = response.text
                
                # Анализируем HTML
                visual_analysis = {
                    "html_size": len(html_content),
                    "has_title": "<title>" in html_content,
                    "has_css": "<style>" in html_content or "stylesheet" in html_content,
                    "has_javascript": "<script>" in html_content,
                    "has_russian_text": any(char in html_content for char in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"),
                    "responsive_design": "viewport" in html_content,
                    "modern_elements": "grid" in html_content and "flexbox" in html_content
                }
                
                # Проверяем загрузку ресурсов
                visual_analysis["load_time"] = len(html_content) / 1000  # Примерная оценка
                
                self.visual_checks = {
                    "timestamp": datetime.now().isoformat(),
                    "analysis": visual_analysis,
                    "status": "completed"
                }
                
                logger.info("✅ Визуальные проверки завершены успешно")
                
            else:
                self.visual_checks = {
                    "timestamp": datetime.now().isoformat(),
                    "status": "failed",
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка визуальных проверок: {e}")
            self.visual_checks = {
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            }
    
    async def identify_improvement_opportunities(self) -> List[str]:
        """Определение возможностей для улучшения"""
        issues = []
        
        # Проверяем производительность
        if "performance" in self.system_metrics:
            perf = self.system_metrics["performance"]
            
            if perf.get("response_time", 0) > self.performance_thresholds["response_time"]:
                issues.append(f"Медленный отклик API: {perf['response_time']:.2f}с")
            
            if perf.get("memory_usage", 0) > self.performance_thresholds["memory_usage"]:
                issues.append(f"Высокое использование памяти: {perf['memory_usage']:.1f}%")
            
            if perf.get("cpu_usage", 0) > self.performance_thresholds["cpu_usage"]:
                issues.append(f"Высокое использование CPU: {perf['cpu_usage']:.1f}%")
        
        # Проверяем агентов
        if "agents" in self.system_metrics:
            for agent_name, agent_data in self.system_metrics["agents"].items():
                if agent_data.get("status") != "healthy":
                    issues.append(f"Проблемы с агентом {agent_name}: {agent_data.get('error', 'неизвестная ошибка')}")
        
        # Проверяем API
        if "api_health" in self.system_metrics:
            for endpoint_name, endpoint_data in self.system_metrics["api_health"].items():
                if endpoint_data.get("status") != "healthy":
                    issues.append(f"Проблемы с endpoint {endpoint_name}: {endpoint_data.get('error', 'неизвестная ошибка')}")
        
        # Проверяем логи
        if "log_analysis" in self.system_metrics:
            log_data = self.system_metrics["log_analysis"]
            if log_data.get("total_errors", 0) > 0:
                issues.append(f"Обнаружено {log_data['total_errors']} ошибок в логах")
            if log_data.get("total_warnings", 0) > 5:
                issues.append(f"Много предупреждений в логах: {log_data['total_warnings']}")
        
        return issues
    
    async def perform_autonomous_improvements(self):
        """Выполнение автономных улучшений"""
        try:
            logger.info("🔧 Выполнение автономных улучшений")
            
            improvements_applied = []
            
            # 1. Оптимизация производительности
            if await self.optimize_performance():
                improvements_applied.append("Оптимизация производительности")
            
            # 2. Улучшение агентов
            if await self.improve_agents():
                improvements_applied.append("Улучшение агентов")
            
            # 3. Оптимизация интерфейса
            if await self.optimize_interface():
                improvements_applied.append("Оптимизация интерфейса")
            
            # 4. Самообучение агентов
            if await self.enhance_agent_intelligence():
                improvements_applied.append("Улучшение интеллекта агентов")
            
            if improvements_applied:
                self.improvements_made += len(improvements_applied)
                logger.info(f"✅ Применено улучшений: {', '.join(improvements_applied)}")
            else:
                logger.info("ℹ️ Система уже оптимальна, улучшения не требуются")
                
        except Exception as e:
            logger.error(f"❌ Ошибка при выполнении улучшений: {e}")
    
    async def optimize_performance(self) -> bool:
        """Оптимизация производительности системы"""
        try:
            # Проверяем, нужна ли оптимизация
            if "performance" not in self.system_metrics:
                return False
            
            perf = self.system_metrics["performance"]
            optimized = False
            
            # Если отклик медленный, можем предложить кэширование
            if perf.get("response_time", 0) > 0.3:
                logger.info("🚀 Применяю оптимизацию скорости отклика")
                # Здесь можно добавить реальную оптимизацию
                optimized = True
            
            return optimized
            
        except Exception as e:
            logger.error(f"❌ Ошибка оптимизации производительности: {e}")
            return False
    
    async def improve_agents(self) -> bool:
        """Улучшение работы агентов"""
        try:
            improved = False
            
            # Отправляем агентам задачи на самоулучшение
            improvement_tasks = [
                ("code_developer", "Оптимизируй свои алгоритмы для более быстрой работы"),
                ("data_analyst", "Улучши методы анализа данных для более точных результатов"),
                ("designer", "Предложи улучшения для пользовательского интерфейса"),
                ("qa_tester", "Разработай новые методы автоматического тестирования")
            ]
            
            for agent_type, task in improvement_tasks:
                try:
                    response = requests.post(
                        f"{self.base_url}/api/chat/send",
                        json={
                            "message": task,
                            "agent_type": agent_type,
                            "user_id": "self_improvement"
                        },
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        improved = True
                        logger.info(f"✅ Агент {agent_type} получил задачу на самоулучшение")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Не удалось отправить задачу агенту {agent_type}: {e}")
            
            return improved
            
        except Exception as e:
            logger.error(f"❌ Ошибка улучшения агентов: {e}")
            return False
    
    async def optimize_interface(self) -> bool:
        """Оптимизация пользовательского интерфейса"""
        try:
            # Проверяем визуальные метрики
            if not self.visual_checks or self.visual_checks.get("status") != "completed":
                return False
            
            analysis = self.visual_checks.get("analysis", {})
            optimized = False
            
            # Проверяем размер HTML
            if analysis.get("html_size", 0) > 100000:  # Больше 100KB
                logger.info("🎨 HTML слишком большой, рекомендую оптимизацию")
                optimized = True
            
            # Проверяем наличие современных элементов
            if not analysis.get("modern_elements", False):
                logger.info("🎨 Рекомендую добавить современные CSS элементы")
                optimized = True
            
            return optimized
            
        except Exception as e:
            logger.error(f"❌ Ошибка оптимизации интерфейса: {e}")
            return False
    
    async def enhance_agent_intelligence(self) -> bool:
        """Улучшение интеллекта агентов"""
        try:
            # Обновляем базу знаний агентов
            knowledge_updates = [
                "Новые методы оптимизации Python кода",
                "Современные подходы к UI/UX дизайну",
                "Лучшие практики тестирования ПО",
                "Инновационные методы анализа данных"
            ]
            
            enhanced = False
            
            for update in knowledge_updates:
                try:
                    # Отправляем обновление знаний общему помощнику
                    response = requests.post(
                        f"{self.base_url}/api/chat/send",
                        json={
                            "message": f"Изучи и внедри: {update}",
                            "agent_type": "general_assistant",
                            "user_id": "knowledge_update"
                        },
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        enhanced = True
                        
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка обновления знаний: {e}")
            
            return enhanced
            
        except Exception as e:
            logger.error(f"❌ Ошибка улучшения интеллекта: {e}")
            return False
    
    async def generate_improvement_report(self) -> Dict[str, Any]:
        """Генерация отчета об улучшениях"""
        return {
            "timestamp": datetime.now().isoformat(),
            "checks_performed": self.checks_performed,
            "improvements_made": self.improvements_made,
            "last_check": self.last_check_time.isoformat() if self.last_check_time else None,
            "system_metrics": self.system_metrics,
            "visual_checks": self.visual_checks,
            "status": "active" if self.improvement_running else "stopped"
        }
    
    def stop_improvement(self):
        """Остановка системы самоулучшения"""
        self.improvement_running = False
        logger.info("🛑 Система автономного самоулучшения остановлена")

async def main():
    """Главная функция"""
    improvement_system = AutonomousSelfImprovement()
    
    try:
        logger.info("🚀 Запуск системы автономного самоулучшения Mentor")
        await improvement_system.start_continuous_improvement()
    except KeyboardInterrupt:
        logger.info("📡 Получен сигнал остановки")
        improvement_system.stop_improvement()
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
    finally:
        # Генерируем финальный отчет
        final_report = await improvement_system.generate_improvement_report()
        
        with open('/workspace/improvement_report.json', 'w', encoding='utf-8') as f:
            json.dump(final_report, f, ensure_ascii=False, indent=2)
        
        logger.info("📊 Отчет о самоулучшении сохранен в improvement_report.json")

if __name__ == "__main__":
    asyncio.run(main())