"""
Примеры использования AI Manager
"""

import asyncio
import json
from core.task_analyzer import TaskAnalyzer
from core.ai_manager import AIManager
from core.task_executor import TaskExecutor
from models.task import Task, TaskPriority, TaskCategory
from monitoring.logger import logger


async def example_basic_task():
    """Пример выполнения базовой задачи"""
    print("🔧 Пример выполнения базовой задачи")
    
    # Создаем компоненты системы
    task_analyzer = TaskAnalyzer()
    ai_manager = AIManager()
    task_executor = TaskExecutor(ai_manager)
    
    # Создаем задачу
    task = Task(
        description="Напиши краткий отчет о преимуществах искусственного интеллекта",
        priority=TaskPriority.MEDIUM,
        category=TaskCategory.TEXT_PROCESSING
    )
    
    print(f"📝 Задача: {task.description}")
    
    # Анализируем задачу
    analysis = await task_analyzer.analyze_task(task)
    print(f"📊 Анализ: {json.dumps(analysis, ensure_ascii=False, indent=2)}")
    
    # Создаем агента
    agent = await ai_manager.create_agent_for_task(analysis)
    print(f"🤖 Создан агент: {agent.name} (тип: {agent.type})")
    
    # Выполняем задачу
    result = await task_executor.execute_task(task, agent)
    print(f"✅ Результат: {json.dumps(result, ensure_ascii=False, indent=2)}")


async def example_code_generation():
    """Пример генерации кода"""
    print("\n💻 Пример генерации кода")
    
    task_analyzer = TaskAnalyzer()
    ai_manager = AIManager()
    task_executor = TaskExecutor(ai_manager)
    
    task = Task(
        description="Создай функцию на Python для сортировки списка чисел",
        priority=TaskPriority.HIGH,
        category=TaskCategory.CODE_GENERATION
    )
    
    print(f"📝 Задача: {task.description}")
    
    analysis = await task_analyzer.analyze_task(task)
    agent = await ai_manager.create_agent_for_task(analysis)
    result = await task_executor.execute_task(task, agent)
    
    print(f"✅ Результат: {json.dumps(result, ensure_ascii=False, indent=2)}")


async def example_creative_task():
    """Пример творческой задачи"""
    print("\n🎨 Пример творческой задачи")
    
    task_analyzer = TaskAnalyzer()
    ai_manager = AIManager()
    task_executor = TaskExecutor(ai_manager)
    
    task = Task(
        description="Напиши короткое стихотворение о весне",
        priority=TaskPriority.LOW,
        category=TaskCategory.CREATIVE
    )
    
    print(f"📝 Задача: {task.description}")
    
    analysis = await task_analyzer.analyze_task(task)
    agent = await ai_manager.create_agent_for_task(analysis)
    result = await task_executor.execute_task(task, agent)
    
    print(f"✅ Результат: {json.dumps(result, ensure_ascii=False, indent=2)}")


async def example_multiple_tasks():
    """Пример выполнения нескольких задач параллельно"""
    print("\n⚡ Пример параллельного выполнения задач")
    
    task_analyzer = TaskAnalyzer()
    ai_manager = AIManager()
    task_executor = TaskExecutor(ai_manager)
    
    tasks = [
        Task(
            description="Переведи 'Hello, world!' на русский язык",
            priority=TaskPriority.MEDIUM,
            category=TaskCategory.TRANSLATION
        ),
        Task(
            description="Создай краткое резюме текста о машинном обучении",
            priority=TaskPriority.MEDIUM,
            category=TaskCategory.SUMMARIZATION
        ),
        Task(
            description="Напиши функцию для вычисления факториала числа",
            priority=TaskPriority.MEDIUM,
            category=TaskCategory.CODE_GENERATION
        )
    ]
    
    print(f"📝 Запуск {len(tasks)} задач параллельно...")
    
    # Создаем задачи для параллельного выполнения
    async def execute_single_task(task):
        analysis = await task_analyzer.analyze_task(task)
        agent = await ai_manager.create_agent_for_task(analysis)
        return await task_executor.execute_task(task, agent)
    
    # Выполняем все задачи параллельно
    results = await asyncio.gather(*[execute_single_task(task) for task in tasks])
    
    print("✅ Результаты выполнения:")
    for i, result in enumerate(results, 1):
        print(f"  Задача {i}: {result['status']} (время: {result.get('execution_time', 0):.2f}с)")


async def example_system_stats():
    """Пример получения статистики системы"""
    print("\n📊 Пример получения статистики системы")
    
    ai_manager = AIManager()
    task_executor = TaskExecutor(ai_manager)
    
    # Получаем статистику агентов
    agents = await ai_manager.get_active_agents()
    print(f"🤖 Активных агентов: {len(agents)}")
    
    # Получаем общую статистику
    stats = await ai_manager.get_system_stats()
    print(f"📈 Статистика системы: {json.dumps(stats, ensure_ascii=False, indent=2)}")
    
    # Получаем статистику задач
    task_stats = await task_executor.get_system_stats()
    print(f"📋 Статистика задач: {json.dumps(task_stats, ensure_ascii=False, indent=2)}")


async def main():
    """Главная функция с примерами"""
    print("🚀 AI Manager - Примеры использования\n")
    
    try:
        # Базовый пример
        await example_basic_task()
        
        # Генерация кода
        await example_code_generation()
        
        # Творческая задача
        await example_creative_task()
        
        # Параллельные задачи
        await example_multiple_tasks()
        
        # Статистика
        await example_system_stats()
        
        print("\n🎉 Все примеры выполнены успешно!")
        
    except Exception as e:
        logger.logger.error(f"Ошибка в примерах: {e}")
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())
