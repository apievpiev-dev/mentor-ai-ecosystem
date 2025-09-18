#!/usr/bin/env python3
"""
Тестовый скрипт для системы множественных AI-агентов
Проверяет работоспособность всех компонентов
"""

import asyncio
import sys
import time
import logging
from pathlib import Path

# Добавляем путь к модулям
sys.path.append('/home/mentor')

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_multi_agent_system():
    """Тест основной системы агентов"""
    try:
        logger.info("🧪 Тестирование системы множественных агентов...")
        
        from multi_agent_system import MultiAgentSystem
        
        # Создаем систему
        system = MultiAgentSystem()
        
        # Проверяем создание агентов
        assert len(system.agents) > 0, "Агенты не созданы"
        logger.info(f"✅ Создано {len(system.agents)} агентов")
        
        # Тестируем обработку сообщений
        test_messages = [
            "Помоги мне создать веб-приложение",
            "Проанализируй эти данные",
            "Создай план проекта",
            "Как дела?"
        ]
        
        for message in test_messages:
            result = await system.process_user_message(message)
            assert "response" in result, f"Нет ответа на сообщение: {message}"
            logger.info(f"✅ Обработано сообщение: {message[:30]}...")
        
        # Проверяем статус системы
        status = system.get_system_status()
        assert "total_agents" in status, "Нет информации о количестве агентов"
        logger.info(f"✅ Статус системы: {status['total_agents']} агентов")
        
        logger.info("✅ Тест системы множественных агентов пройден")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования системы агентов: {e}")
        return False

async def test_agent_coordinator():
    """Тест координатора агентов"""
    try:
        logger.info("🧪 Тестирование координатора агентов...")
        
        from agent_coordinator import EnhancedSharedMemory, AgentCoordinator, TaskComplexity
        
        # Создаем общую память
        shared_memory = EnhancedSharedMemory()
        
        # Создаем координатор
        coordinator = AgentCoordinator(shared_memory)
        
        # Тестируем создание задачи
        task = await coordinator.create_coordination_task(
            title="Тестовая задача",
            description="Тестовая задача для проверки координации",
            required_skills=["general_help"],
            complexity=TaskComplexity.SIMPLE,
            priority=5
        )
        
        assert task.id is not None, "Задача не создана"
        logger.info(f"✅ Создана задача: {task.title}")
        
        # Проверяем статус координации
        status = coordinator.get_coordination_status()
        assert "total_agents" in status, "Нет информации о координации"
        logger.info(f"✅ Статус координации получен")
        
        logger.info("✅ Тест координатора агентов пройден")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования координатора: {e}")
        return False

async def test_integrated_system():
    """Тест интегрированной системы"""
    try:
        logger.info("🧪 Тестирование интегрированной системы...")
        
        from integrated_agent_system import IntegratedAgentSystem
        
        # Создаем интегрированную систему
        system = IntegratedAgentSystem()
        
        # Инициализируем систему
        await system.initialize()
        
        # Проверяем инициализацию
        assert system.shared_memory is not None, "Общая память не создана"
        assert system.multi_agent_system is not None, "Система агентов не создана"
        assert system.coordinator is not None, "Координатор не создан"
        
        logger.info("✅ Интегрированная система инициализирована")
        
        # Тестируем обработку сообщений
        result = await system.process_user_message("Тестовое сообщение")
        assert "response" in result, "Нет ответа на тестовое сообщение"
        logger.info("✅ Обработка сообщений работает")
        
        # Проверяем статус системы
        status = system.get_system_status()
        assert "system_status" in status, "Нет статуса системы"
        logger.info(f"✅ Статус системы: {status['system_status']}")
        
        # Останавливаем систему
        await system.stop()
        
        logger.info("✅ Тест интегрированной системы пройден")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования интегрированной системы: {e}")
        return False

def test_file_structure():
    """Тест структуры файлов"""
    try:
        logger.info("🧪 Тестирование структуры файлов...")
        
        required_files = [
            "/home/mentor/multi_agent_system.py",
            "/home/mentor/agent_coordinator.py",
            "/home/mentor/chat_server.py",
            "/home/mentor/integrated_agent_system.py",
            "/home/mentor/start_multi_agent_system.py",
            "/home/mentor/requirements.txt",
            "/home/mentor/README_MULTI_AGENT.md"
        ]
        
        for file_path in required_files:
            assert Path(file_path).exists(), f"Файл не найден: {file_path}"
            logger.info(f"✅ Файл найден: {Path(file_path).name}")
        
        # Проверяем создание директорий
        required_dirs = [
            "/home/mentor/agent_data",
            "/home/mentor/agent_logs",
            "/home/mentor/agent_knowledge",
            "/home/mentor/agent_projects"
        ]
        
        for dir_path in required_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            assert Path(dir_path).exists(), f"Директория не создана: {dir_path}"
            logger.info(f"✅ Директория создана: {Path(dir_path).name}")
        
        logger.info("✅ Тест структуры файлов пройден")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования структуры файлов: {e}")
        return False

def test_imports():
    """Тест импортов"""
    try:
        logger.info("🧪 Тестирование импортов...")
        
        # Тестируем основные импорты
        import fastapi
        import uvicorn
        import asyncio
        import json
        import logging
        import threading
        import uuid
        from datetime import datetime
        from typing import Dict, List, Any, Optional
        from dataclasses import dataclass
        from enum import Enum
        from pathlib import Path
        
        logger.info("✅ Основные импорты работают")
        
        # Тестируем импорты наших модулей
        from multi_agent_system import MultiAgentSystem, BaseAgent, AgentType
        from agent_coordinator import AgentCoordinator, EnhancedSharedMemory
        from integrated_agent_system import IntegratedAgentSystem
        
        logger.info("✅ Импорты наших модулей работают")
        
        logger.info("✅ Тест импортов пройден")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования импортов: {e}")
        return False

async def run_all_tests():
    """Запуск всех тестов"""
    logger.info("🚀 Запуск тестов системы множественных AI-агентов")
    logger.info("=" * 60)
    
    tests = [
        ("Структура файлов", test_file_structure),
        ("Импорты", test_imports),
        ("Система агентов", test_multi_agent_system),
        ("Координатор", test_agent_coordinator),
        ("Интегрированная система", test_integrated_system)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Запуск теста: {test_name}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                logger.info(f"✅ Тест '{test_name}' пройден")
            else:
                logger.error(f"❌ Тест '{test_name}' провален")
        except Exception as e:
            logger.error(f"❌ Ошибка в тесте '{test_name}': {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    logger.info(f"✅ Пройдено: {passed}/{total}")
    logger.info(f"❌ Провалено: {total - passed}/{total}")
    
    if passed == total:
        logger.info("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Система готова к работе!")
        return True
    else:
        logger.error("❌ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ! Проверьте ошибки выше.")
        return False

if __name__ == "__main__":
    try:
        # Запускаем все тесты
        result = asyncio.run(run_all_tests())
        
        if result:
            print("\n🎉 СИСТЕМА ГОТОВА К ЗАПУСКУ!")
            print("Для запуска выполните:")
            print("python start_multi_agent_system.py")
            sys.exit(0)
        else:
            print("\n❌ СИСТЕМА НЕ ГОТОВА! Исправьте ошибки и повторите тесты.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Тестирование прервано пользователем")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка тестирования: {e}")
        sys.exit(1)
