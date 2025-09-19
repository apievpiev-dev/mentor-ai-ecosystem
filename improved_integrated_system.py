#!/usr/bin/env python3
"""
Улучшенная интегрированная система Multi-AI
Использует улучшенный координатор агентов
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
import threading

from multi_agent_system import MultiAgentSystem, BaseAgent, AgentType
from ai_engine import AIEngine
from improved_agent_coordinator import get_improved_coordinator, ImprovedAgentCoordinator
from enhanced_agents import (
    EnhancedCodeDeveloperAgent,
    EnhancedDataAnalystAgent,
    EnhancedProjectManagerAgent,
    EnhancedDesignerAgent,
    EnhancedQATesterAgent,
    EnhancedGeneralAssistantAgent
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/mentor/improved_integrated_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ImprovedIntegratedAgentSystem:
    """Улучшенная интегрированная система агентов"""
    
    def __init__(self):
        self.running = False
        self.multi_agent_system = None
        self.ai_engine = None
        self.coordinator = None
        self.agents = {}
        self.startup_time = None
        self.lock = threading.Lock()
        
        logger.info("🔧 Инициализация улучшенной интегрированной системы...")
    
    async def initialize_ai_engine(self):
        """Инициализация AI движка"""
        try:
            logger.info("🔧 Инициализация AI движка...")
            self.ai_engine = AIEngine()
            await self.ai_engine.initialize()
            logger.info("✅ AI движок инициализирован")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации AI движка: {e}")
            return False
    
    async def initialize_coordinator(self):
        """Инициализация координатора"""
        try:
            logger.info("🔧 Инициализация улучшенного координатора...")
            self.coordinator = get_improved_coordinator()
            await self.coordinator.start()
            logger.info("✅ Улучшенный координатор инициализирован")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации координатора: {e}")
            return False
    
    async def create_enhanced_agents(self):
        """Создание улучшенных агентов"""
        try:
            logger.info("🔧 Создание улучшенных агентов...")
            
            # Создаем агентов
            agents_data = [
                ("general_assistant", EnhancedGeneralAssistantAgent, ["general_help", "planning", "coordination", "user_query"]),
                ("code_developer", EnhancedCodeDeveloperAgent, ["code_generation", "debugging", "code_review", "architecture_design", "create_project", "setup_environment"]),
                ("data_analyst", EnhancedDataAnalystAgent, ["data_analysis", "reporting", "visualization", "predictive_modeling", "data_processing"]),
                ("project_manager", EnhancedProjectManagerAgent, ["project_planning", "task_management", "resource_allocation", "progress_tracking", "user_query"]),
                ("designer", EnhancedDesignerAgent, ["ui_design", "ux_design", "visual_identity"]),
                ("qa_tester", EnhancedQATesterAgent, ["unit_testing", "integration_testing", "bug_reporting"])
            ]
            
            for agent_type, agent_class, skills in agents_data:
                try:
                    agent = agent_class(
                        agent_id=f"{agent_type}_agent",
                        name=f"Улучшенный {agent_type.replace('_', ' ').title()}",
                        agent_type=agent_type,
                        ai_engine=self.ai_engine,
                        coordinator=self.coordinator
                    )
                    
                    self.agents[agent_type] = agent
                    
                    # Регистрируем агента в координаторе
                    self.coordinator.register_agent(agent.agent_id, agent_type, skills)
                    
                    logger.info(f"✅ Создан агент {agent_type}")
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка создания агента {agent_type}: {e}")
            
            logger.info(f"✅ Создано {len(self.agents)} улучшенных агентов")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания агентов: {e}")
            return False
    
    async def initialize_multi_agent_system(self):
        """Инициализация системы мульти-агентов"""
        try:
            logger.info("🔧 Инициализация системы мульти-агентов...")
            
            self.multi_agent_system = MultiAgentSystem()
            
            # Добавляем агентов в систему
            for agent_type, agent in self.agents.items():
                self.multi_agent_system.add_agent(agent)
                logger.info(f"✅ Агент {agent_type} добавлен в систему")
            
            logger.info("✅ Система мульти-агентов инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации системы мульти-агентов: {e}")
            return False
    
    async def start(self):
        """Запуск улучшенной интегрированной системы"""
        try:
            logger.info("🚀 Запуск улучшенной интегрированной системы...")
            
            with self.lock:
                self.running = True
                self.startup_time = datetime.now()
            
            # 1. Инициализация AI движка
            if not await self.initialize_ai_engine():
                return False
            
            # 2. Инициализация координатора
            if not await self.initialize_coordinator():
                return False
            
            # 3. Создание агентов
            if not await self.create_enhanced_agents():
                return False
            
            # 4. Инициализация системы мульти-агентов
            if not await self.initialize_multi_agent_system():
                return False
            
            logger.info("✅ Улучшенная интегрированная система запущена")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска улучшенной интегрированной системы: {e}")
            return False
    
    async def stop(self):
        """Остановка улучшенной интегрированной системы"""
        try:
            logger.info("🛑 Остановка улучшенной интегрированной системы...")
            
            with self.lock:
                self.running = False
            
            # Останавливаем координатор
            if self.coordinator:
                self.coordinator.stop()
            
            # Останавливаем AI движок
            if self.ai_engine:
                await self.ai_engine.cleanup()
            
            logger.info("✅ Улучшенная интегрированная система остановлена")
            
        except Exception as e:
            logger.error(f"❌ Ошибка остановки улучшенной интегрированной системы: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Получение статуса системы"""
        try:
            with self.lock:
                if not self.running:
                    return {
                        "system_status": "stopped",
                        "uptime": "0м",
                        "total_agents": 0,
                        "active_agents": 0,
                        "coordination_status": {
                            "total_agents": 0,
                            "active_tasks": 0,
                            "message_queue_size": 0,
                            "agent_capabilities": {},
                            "active_tasks_info": []
                        },
                        "shared_memory": {
                            "knowledge_items": 0,
                            "conversation_history": 0,
                            "agent_capabilities": 0
                        },
                        "startup_time": None
                    }
                
                # Получаем статус от координатора
                coordination_status = self.coordinator.get_system_status() if self.coordinator else {}
                
                # Вычисляем время работы
                uptime = "0м"
                if self.startup_time:
                    uptime_delta = datetime.now() - self.startup_time
                    uptime = f"{int(uptime_delta.total_seconds() / 60)}м"
                
                return {
                    "system_status": "running",
                    "uptime": uptime,
                    "total_agents": len(self.agents),
                    "active_agents": coordination_status.get("active_agents", 0),
                    "coordination_status": coordination_status,
                    "shared_memory": {
                        "knowledge_items": len(self.coordinator.shared_memory.knowledge_base) if self.coordinator else 0,
                        "conversation_history": len(self.coordinator.shared_memory.conversation_history) if self.coordinator else 0,
                        "agent_capabilities": len(self.agents)
                    },
                    "startup_time": self.startup_time.isoformat() if self.startup_time else None
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения статуса системы: {e}")
            return {
                "system_status": "error",
                "error": str(e)
            }
    
    def send_message_to_agent(self, message: str, agent_type: str = None, user_id: str = "user") -> Dict[str, Any]:
        """Отправка сообщения агенту"""
        try:
            if not self.running:
                return {"error": "System is not running"}
            
            if agent_type and agent_type in self.agents:
                # Отправляем конкретному агенту
                agent = self.agents[agent_type]
                
                # Отправляем сообщение через координатор
                if self.coordinator:
                    message_id = self.coordinator.send_message(
                        sender_id=user_id,
                        recipient_id=agent.agent_id,
                        content={"message": message, "user_id": user_id},
                        message_type="user_message",
                        priority=1
                    )
                
                return {
                    "success": True,
                    "response": {
                        "response": f"Агент {agent.name} получил сообщение: {message}",
                        "status": "processed"
                    },
                    "agent": agent.name,
                    "agent_type": agent_type,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Отправляем всем агентам или первому доступному
                if self.agents:
                    first_agent = list(self.agents.values())[0]
                    
                    if self.coordinator:
                        message_id = self.coordinator.send_message(
                            sender_id=user_id,
                            recipient_id=first_agent.agent_id,
                            content={"message": message, "user_id": user_id},
                            message_type="user_message",
                            priority=1
                        )
                    
                    return {
                        "success": True,
                        "response": {
                            "response": f"Сообщение отправлено агенту {first_agent.name}",
                            "status": "processed"
                        },
                        "agent": first_agent.name,
                        "agent_type": first_agent.agent_type,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {"error": "No agents available"}
                    
        except Exception as e:
            logger.error(f"❌ Ошибка отправки сообщения агенту: {e}")
            return {"error": str(e)}

# Глобальный экземпляр улучшенной системы
_improved_integrated_system = None

def get_improved_integrated_system() -> ImprovedIntegratedAgentSystem:
    """Получение глобального экземпляра улучшенной интегрированной системы"""
    global _improved_integrated_system
    if _improved_integrated_system is None:
        _improved_integrated_system = ImprovedIntegratedAgentSystem()
    return _improved_integrated_system

async def main():
    """Главная функция для тестирования"""
    system = get_improved_integrated_system()
    
    try:
        # Запускаем систему
        if await system.start():
            logger.info("✅ Улучшенная интегрированная система запущена")
            
            # Ждем некоторое время
            await asyncio.sleep(60)
            
            # Получаем статус
            status = system.get_system_status()
            logger.info(f"📊 Статус системы: {status}")
            
        else:
            logger.error("❌ Не удалось запустить улучшенную интегрированную систему")
    
    except Exception as e:
        logger.error(f"❌ Ошибка в главной функции: {e}")
    
    finally:
        # Останавливаем систему
        await system.stop()

if __name__ == "__main__":
    asyncio.run(main())


