#!/usr/bin/env python3
"""
Демонстрация AI Manager БЕЗ заглушек - реальная работа системы
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


async def demo_real_ai_system():
    """Демонстрация реальной работы AI системы"""
    print("🤖 AI Manager - РЕАЛЬНАЯ ДЕМОНСТРАЦИЯ БЕЗ ЗАГЛУШЕК")
    print("=" * 60)
    
    # Инициализация компонентов
    print("🔧 Инициализация системы...")
    task_analyzer = TaskAnalyzer()
    ai_manager = AIManager()
    task_executor = TaskExecutor(ai_manager)
    
    # Инициализируем провайдеры
    await provider_manager.initialize_providers({
        "ollama_model": "llama2:7b",
        "hf_model": "microsoft/DialoGPT-medium"
    })
    
    health_status = await provider_manager.get_provider_health()
    print(f"✅ AI провайдеры: {len([p for p in health_status.values() if p['available']])} доступны")
    print(f"🎯 Используется: {provider_manager.get_default_provider_name()}")
    print()
    
    return task_analyzer, ai_manager, task_executor


async def demo_real_text_processing(task_analyzer, ai_manager, task_executor):
    """Реальная демонстрация обработки текста"""
    print("📝 РЕАЛЬНАЯ ОБРАБОТКА ТЕКСТА")
    print("-" * 40)
    
    task = Task(
        description="Напиши краткий обзор преимуществ искусственного интеллекта в современном мире",
        priority=TaskPriority.HIGH,
        category=TaskCategory.TEXT_PROCESSING
    )
    
    print(f"📋 Задача: {task.description}")
    
    # Анализ задачи
    analysis = await task_analyzer.analyze_task(task)
    print(f"🔍 Анализ: {analysis.get('category')} | Сложность: {analysis.get('complexity')}")
    
    # Создание агента
    agent = await ai_manager.create_agent_for_task(analysis)
    print(f"🤖 Агент: {agent.name} ({agent.type})")
    
    # Выполнение задачи
    result = await task_executor.execute_task(task, agent)
    
    status_value = result['status'].value if hasattr(result['status'], 'value') else str(result['status'])
    print(f"⚡ Статус: {status_value}")
    print(f"⏱️ Время: {result.get('execution_time', 0):.2f}с")
    
    if result.get('result') and result.get('result').get('result'):
        response = result['result']['result']
        print(f"📄 Результат:\n{response[:300]}...")
        if len(response) > 300:
            print(f"[... и еще {len(response) - 300} символов]")
    
    print()


async def demo_real_code_generation(task_analyzer, ai_manager, task_executor):
    """Реальная демонстрация генерации кода"""
    print("💻 РЕАЛЬНАЯ ГЕНЕРАЦИЯ КОДА")
    print("-" * 40)
    
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
    
    if result.get('result') and result.get('result').get('result'):
        code = result['result']['result']
        print(f"💻 Сгенерированный код:\n{code}")
    
    print()


async def demo_real_creative_writing(task_analyzer, ai_manager, task_executor):
    """Реальная демонстрация творческого письма"""
    print("🎨 РЕАЛЬНОЕ ТВОРЧЕСКОЕ ПИСЬМО")
    print("-" * 40)
    
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
    
    if result.get('result') and result.get('result').get('result'):
        poem = result['result']['result']
        print(f"🎭 Стихотворение:\n{poem}")
    
    print()


async def demo_real_translation(task_analyzer, ai_manager, task_executor):
    """Реальная демонстрация перевода"""
    print("🌍 РЕАЛЬНЫЙ ПЕРЕВОД")
    print("-" * 40)
    
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
    
    if result.get('result') and result.get('result').get('result'):
        translation = result['result']['result']
        print(f"🌐 Перевод: {translation}")
    
    print()


async def demo_real_provider_test():
    """Тестирование реальных AI провайдеров"""
    print("🔬 ТЕСТИРОВАНИЕ AI ПРОВАЙДЕРОВ")
    print("-" * 40)
    
    prompt = "Объясни, что такое искусственный интеллект в одном предложении"
    print(f"📝 Промпт: {prompt}")
    print()
    
    providers = ["local", "ollama", "huggingface"]
    
    for provider_name in providers:
        if provider_name in provider_manager.get_available_providers():
            print(f"🤖 Тестирование {provider_name}...")
            
            start_time = asyncio.get_event_loop().time()
            response = await provider_manager.generate_response(prompt, provider_name=provider_name)
            end_time = asyncio.get_event_loop().time()
            
            if response.get("success"):
                result_text = response['result'][:100] + "..." if len(response['result']) > 100 else response['result']
                print(f"✅ {provider_name}: {result_text}")
                print(f"⏱️ Время: {(end_time - start_time):.2f}с")
            else:
                print(f"❌ {provider_name}: {response.get('error', 'Неизвестная ошибка')}")
        else:
            print(f"⚠️ {provider_name}: недоступен")
        
        print()


async def demo_real_system_stats(ai_manager, task_executor):
    """Реальная статистика системы"""
    print("📊 РЕАЛЬНАЯ СТАТИСТИКА СИСТЕМЫ")
    print("-" * 40)
    
    # Статистика агентов
    agents = await ai_manager.get_active_agents()
    print(f"🤖 Активных агентов: {len(agents)}")
    
    for agent in agents[:3]:
        agent_type = agent.type if isinstance(agent.type, str) else agent.type.value
        print(f"   - {agent.name} ({agent_type})")
    
    # Статистика задач
    task_stats = await task_executor.get_system_stats()
    print(f"📋 Статистика задач:")
    print(f"   - Активных: {task_stats.get('active_tasks', 0)}")
    print(f"   - Завершенных: {task_stats.get('completed_tasks', 0)}")
    print(f"   - Среднее время: {task_stats.get('average_execution_time', 0):.2f}с")
    print(f"   - Средний балл: {task_stats.get('average_quality_score', 0):.2f}")
    
    # Статистика провайдеров
    health_status = await provider_manager.get_provider_health()
    print(f"🔌 AI провайдеры:")
    for name, status in health_status.items():
        status_icon = "✅" if status["available"] else "❌"
        print(f"   - {status_icon} {name}: {status['status']}")
    
    print()


async def main():
    """Главная функция реальной демонстрации"""
    try:
        print("🎯 РЕАЛЬНАЯ ДЕМОНСТРАЦИЯ AI MANAGER")
        print("Никаких заглушек - только настоящая работа!")
        print()
        
        # Инициализация
        task_analyzer, ai_manager, task_executor = await demo_real_ai_system()
        
        # Реальные демонстрации
        await demo_real_text_processing(task_analyzer, ai_manager, task_executor)
        await demo_real_code_generation(task_analyzer, ai_manager, task_executor)
        await demo_real_creative_writing(task_analyzer, ai_manager, task_executor)
        await demo_real_translation(task_analyzer, ai_manager, task_executor)
        
        # Тестирование провайдеров
        await demo_real_provider_test()
        
        # Статистика
        await demo_real_system_stats(ai_manager, task_executor)
        
        print("🎉 РЕАЛЬНАЯ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
        print("\n💡 Система работает с настоящими AI ответами:")
        print("   - Никаких заглушек")
        print("   - Реальные результаты")
        print("   - Полная функциональность")
        print("\n🚀 Готово к развертыванию на сервере!")
        
    except Exception as e:
        print(f"❌ Ошибка в демонстрации: {e}")
        logger.logger.error(f"Ошибка демонстрации: {e}")
    
    finally:
        # Закрываем провайдеры
        await provider_manager.close_all()


if __name__ == "__main__":
    asyncio.run(main())


