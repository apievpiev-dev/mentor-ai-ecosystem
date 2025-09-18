#!/usr/bin/env python3
"""
Демонстрация AI Manager с бесплатными AI провайдерами
"""

import asyncio
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.task import Task, TaskPriority, TaskCategory
from models.agent import Agent, AgentType
from core.task_analyzer import TaskAnalyzer
from core.ai_manager import AIManager
from core.task_executor import TaskExecutor
from ai_providers.provider_manager import provider_manager
from monitoring.logger import logger


async def demo_free_ai_providers():
    """Демонстрация бесплатных AI провайдеров"""
    print("🤖 AI Manager - Демонстрация с бесплатными AI провайдерами\n")
    print("=" * 70)
    
    # Инициализация компонентов
    print("🔧 Инициализация AI провайдеров...")
    
    # Инициализируем провайдеры
    await provider_manager.initialize_providers({
        "ollama_model": "llama2:7b",
        "hf_model": "microsoft/DialoGPT-medium",
        "hf_token": None  # Можно оставить пустым для бесплатного использования
    })
    
    # Проверяем статус провайдеров
    health_status = await provider_manager.get_provider_health()
    print("\n📊 Статус AI провайдеров:")
    for name, status in health_status.items():
        status_icon = "✅" if status["available"] else "❌"
        print(f"  {status_icon} {name}: {status['model']} - {status['status']}")
    
    print(f"\n🎯 Используется провайдер: {provider_manager.get_default_provider_name()}")
    print()
    
    # Создание компонентов системы
    print("🔧 Инициализация компонентов системы...")
    task_analyzer = TaskAnalyzer()
    ai_manager = AIManager()
    task_executor = TaskExecutor(ai_manager)
    print("✅ Компоненты инициализированы\n")
    
    return task_analyzer, ai_manager, task_executor


async def demo_text_processing_with_ai(task_analyzer, ai_manager, task_executor):
    """Демонстрация обработки текста с AI"""
    print("📝 Демонстрация обработки текста с AI")
    print("-" * 50)
    
    task = Task(
        description="Напиши краткий обзор преимуществ искусственного интеллекта в современном мире",
        priority=TaskPriority.HIGH,
        category=TaskCategory.TEXT_PROCESSING
    )
    
    print(f"📋 Задача: {task.description}")
    
    # Анализ задачи
    analysis = await task_analyzer.analyze_task(task)
    print(f"🔍 Анализ: категория={analysis.get('category')}, сложность={analysis.get('complexity')}")
    
    # Создание агента
    agent = await ai_manager.create_agent_for_task(analysis)
    print(f"🤖 Создан агент: {agent.name} ({agent.type})")
    
    # Выполнение задачи
    result = await task_executor.execute_task(task, agent)
    status_value = result['status'].value if hasattr(result['status'], 'value') else str(result['status'])
    print(f"⚡ Статус: {status_value}")
    print(f"⏱️ Время: {result.get('execution_time', 0):.2f}с")
    
    if result.get('result'):
        print(f"📄 Результат: {str(result['result'])[:200]}...")
    
    print()


async def demo_code_generation_with_ai(task_analyzer, ai_manager, task_executor):
    """Демонстрация генерации кода с AI"""
    print("💻 Демонстрация генерации кода с AI")
    print("-" * 50)
    
    task = Task(
        description="Создай функцию Python для сортировки списка чисел по убыванию",
        priority=TaskPriority.MEDIUM,
        category=TaskCategory.CODE_GENERATION
    )
    
    print(f"📋 Задача: {task.description}")
    
    # Анализ и выполнение
    analysis = await task_analyzer.analyze_task(task)
    agent = await ai_manager.create_agent_for_task(analysis)
    result = await task_executor.execute_task(task, agent)
    
    status_value = result['status'].value if hasattr(result['status'], 'value') else str(result['status'])
    print(f"⚡ Статус: {status_value}")
    print(f"⏱️ Время: {result.get('execution_time', 0):.2f}с")
    
    if result.get('result'):
        print(f"💻 Код:\n{str(result['result'])[:300]}...")
    
    print()


async def demo_creative_writing_with_ai(task_analyzer, ai_manager, task_executor):
    """Демонстрация творческого письма с AI"""
    print("🎨 Демонстрация творческого письма с AI")
    print("-" * 50)
    
    task = Task(
        description="Напиши короткое стихотворение о весне",
        priority=TaskPriority.LOW,
        category=TaskCategory.CREATIVE
    )
    
    print(f"📋 Задача: {task.description}")
    
    # Анализ и выполнение
    analysis = await task_analyzer.analyze_task(task)
    agent = await ai_manager.create_agent_for_task(analysis)
    result = await task_executor.execute_task(task, agent)
    
    status_value = result['status'].value if hasattr(result['status'], 'value') else str(result['status'])
    print(f"⚡ Статус: {status_value}")
    print(f"⏱️ Время: {result.get('execution_time', 0):.2f}с")
    
    if result.get('result'):
        print(f"🎭 Стихотворение:\n{str(result['result'])[:400]}...")
    
    print()


async def demo_translation_with_ai(task_analyzer, ai_manager, task_executor):
    """Демонстрация перевода с AI"""
    print("🌍 Демонстрация перевода с AI")
    print("-" * 50)
    
    task = Task(
        description="Переведи фразу 'Hello, AI Manager!' на русский язык",
        priority=TaskPriority.MEDIUM,
        category=TaskCategory.TRANSLATION
    )
    
    print(f"📋 Задача: {task.description}")
    
    # Анализ и выполнение
    analysis = await task_analyzer.analyze_task(task)
    agent = await ai_manager.create_agent_for_task(analysis)
    result = await task_executor.execute_task(task, agent)
    
    status_value = result['status'].value if hasattr(result['status'], 'value') else str(result['status'])
    print(f"⚡ Статус: {status_value}")
    print(f"⏱️ Время: {result.get('execution_time', 0):.2f}с")
    
    if result.get('result'):
        print(f"🌐 Перевод: {str(result['result'])[:200]}...")
    
    print()


async def demo_provider_comparison():
    """Демонстрация сравнения разных AI провайдеров"""
    print("🔄 Сравнение AI провайдеров")
    print("-" * 50)
    
    prompt = "Объясни, что такое искусственный интеллект в одном предложении"
    
    print(f"📝 Промпт: {prompt}")
    print()
    
    # Тестируем разные провайдеры
    providers = ["local", "ollama", "huggingface"]
    
    for provider_name in providers:
        if provider_name in provider_manager.get_available_providers():
            print(f"🤖 Тестирование {provider_name}...")
            
            start_time = asyncio.get_event_loop().time()
            response = await provider_manager.generate_response(prompt, provider_name=provider_name)
            end_time = asyncio.get_event_loop().time()
            
            if response.get("success"):
                print(f"✅ {provider_name}: {response['result'][:100]}...")
                print(f"⏱️ Время: {(end_time - start_time):.2f}с")
            else:
                print(f"❌ {provider_name}: {response.get('error', 'Неизвестная ошибка')}")
        else:
            print(f"⚠️ {provider_name}: недоступен")
        
        print()


async def demo_system_stats(ai_manager, task_executor):
    """Демонстрация статистики системы"""
    print("📊 Статистика системы")
    print("-" * 50)
    
    # Статистика агентов
    agents = await ai_manager.get_active_agents()
    print(f"🤖 Активных агентов: {len(agents)}")
    
    # Статистика задач
    task_stats = await task_executor.get_system_stats()
    print(f"📋 Статистика задач:")
    print(f"   - Активных: {task_stats.get('active_tasks', 0)}")
    print(f"   - Завершенных: {task_stats.get('completed_tasks', 0)}")
    print(f"   - Среднее время: {task_stats.get('average_execution_time', 0):.2f}с")
    
    # Статистика провайдеров
    health_status = await provider_manager.get_provider_health()
    print(f"🔌 AI провайдеры:")
    for name, status in health_status.items():
        status_icon = "✅" if status["available"] else "❌"
        print(f"   - {status_icon} {name}: {status['status']}")
    
    print()


async def main():
    """Главная функция демонстрации"""
    try:
        print("🎯 Запуск демонстрации AI Manager с бесплатными AI провайдерами")
        print("Система использует Ollama, Hugging Face и локальные модели")
        print()
        
        # Инициализация
        task_analyzer, ai_manager, task_executor = await demo_free_ai_providers()
        
        # Демонстрации разных типов задач
        await demo_text_processing_with_ai(task_analyzer, ai_manager, task_executor)
        await demo_code_generation_with_ai(task_analyzer, ai_manager, task_executor)
        await demo_creative_writing_with_ai(task_analyzer, ai_manager, task_executor)
        await demo_translation_with_ai(task_analyzer, ai_manager, task_executor)
        
        # Сравнение провайдеров
        await demo_provider_comparison()
        
        # Статистика
        await demo_system_stats(ai_manager, task_executor)
        
        print("🎉 Демонстрация завершена успешно!")
        print("\n💡 Для развертывания на сервере:")
        print("   1. Запустите: ./deploy.sh")
        print("   2. Откройте: http://localhost:8000")
        print("   3. Наслаждайтесь бесплатными AI агентами!")
        
    except Exception as e:
        print(f"❌ Ошибка в демонстрации: {e}")
        logger.logger.error(f"Ошибка демонстрации: {e}")
    
    finally:
        # Закрываем провайдеры
        await provider_manager.close_all()


if __name__ == "__main__":
    asyncio.run(main())
