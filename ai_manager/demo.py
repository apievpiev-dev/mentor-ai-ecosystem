#!/usr/bin/env python3
"""
Демонстрация работы AI Manager
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
from monitoring.logger import logger


async def demo_basic_functionality():
    """Демонстрация базовой функциональности"""
    print("🚀 AI Manager - Демонстрация работы\n")
    print("=" * 60)
    
    # Инициализация компонентов
    print("🔧 Инициализация компонентов системы...")
    task_analyzer = TaskAnalyzer()
    ai_manager = AIManager()
    task_executor = TaskExecutor(ai_manager)
    print("✅ Компоненты инициализированы\n")
    
    # Создание тестовой задачи
    print("📝 Создание тестовой задачи...")
    task = Task(
        description="Напиши краткий обзор преимуществ искусственного интеллекта в современном мире",
        priority=TaskPriority.HIGH,
        category=TaskCategory.TEXT_PROCESSING
    )
    print(f"✅ Задача создана: {task.description[:50]}...\n")
    
    # Анализ задачи
    print("🔍 Анализ задачи...")
    analysis = await task_analyzer.analyze_task(task)
    print(f"📊 Результат анализа:")
    print(f"   - Категория: {analysis.get('category')}")
    print(f"   - Сложность: {analysis.get('complexity')}")
    print(f"   - Предполагаемое время: {analysis.get('estimated_time')} мин")
    print(f"   - Рекомендуемый агент: {analysis.get('suggested_agent_type')}")
    print(f"   - Навыки: {', '.join(analysis.get('required_skills', []))}")
    print()
    
    # Создание агента
    print("🤖 Создание специализированного AI агента...")
    agent = await ai_manager.create_agent_for_task(analysis)
    print(f"✅ Агент создан:")
    print(f"   - ID: {agent.id}")
    print(f"   - Имя: {agent.name}")
    print(f"   - Тип: {agent.type}")
    print(f"   - Способности: {len(agent.capabilities)}")
    for cap in agent.capabilities[:3]:  # Показываем первые 3 способности
        print(f"     • {cap.name} (уровень: {cap.level})")
    print()
    
    # Выполнение задачи
    print("⚡ Выполнение задачи агентом...")
    result = await task_executor.execute_task(task, agent)
    print(f"✅ Задача выполнена:")
    print(f"   - Статус: {result['status']}")
    print(f"   - Время выполнения: {result.get('execution_time', 0):.2f} сек")
    if result.get('result'):
        print(f"   - Результат: {str(result['result'])[:100]}...")
    print()
    
    # Статистика системы
    print("📊 Статистика системы:")
    stats = await ai_manager.get_system_stats()
    print(f"   - Всего агентов: {stats.get('total_agents', 0)}")
    print(f"   - Активных агентов: {stats.get('active_agents', 0)}")
    print(f"   - Выполнено задач: {stats.get('total_tasks_completed', 0)}")
    print(f"   - Процент успеха: {stats.get('overall_success_rate', 0)*100:.1f}%")
    print()
    
    return True


async def demo_multiple_agents():
    """Демонстрация работы с несколькими агентами"""
    print("🔄 Демонстрация множественных агентов")
    print("=" * 60)
    
    task_analyzer = TaskAnalyzer()
    ai_manager = AIManager()
    task_executor = TaskExecutor(ai_manager)
    
    # Создание разных типов задач
    tasks = [
        Task(
            description="Создай функцию Python для сортировки списка чисел по убыванию",
            priority=TaskPriority.MEDIUM,
            category=TaskCategory.CODE_GENERATION
        ),
        Task(
            description="Напиши короткое стихотворение о весне",
            priority=TaskPriority.LOW,
            category=TaskCategory.CREATIVE
        ),
        Task(
            description="Переведи фразу 'Hello, AI Manager!' на русский язык",
            priority=TaskPriority.MEDIUM,
            category=TaskCategory.TRANSLATION
        )
    ]
    
    print(f"📝 Создано {len(tasks)} задач разных типов\n")
    
    # Параллельное выполнение задач
    async def execute_task_with_analysis(task):
        print(f"🔄 Обработка задачи: {task.description[:40]}...")
        analysis = await task_analyzer.analyze_task(task)
        agent = await ai_manager.create_agent_for_task(analysis)
        result = await task_executor.execute_task(task, agent)
        return result
    
    print("⚡ Параллельное выполнение задач...")
    results = await asyncio.gather(*[execute_task_with_analysis(task) for task in tasks])
    
    print("\n📋 Результаты выполнения:")
    for i, result in enumerate(results, 1):
        print(f"   Задача {i}: {result['status']} (время: {result.get('execution_time', 0):.2f}с)")
    
    # Финальная статистика
    print("\n📊 Финальная статистика агентов:")
    agents = await ai_manager.get_active_agents()
    print(f"   - Всего создано агентов: {len(agents)}")
    
    agent_types = {}
    for agent in agents:
        agent_type = agent.type if isinstance(agent.type, str) else agent.type.value
        agent_types[agent_type] = agent_types.get(agent_type, 0) + 1
    
    print("   - Распределение по типам:")
    for agent_type, count in agent_types.items():
        print(f"     • {agent_type}: {count}")
    
    print()


async def demo_system_monitoring():
    """Демонстрация системы мониторинга"""
    print("📈 Демонстрация системы мониторинга")
    print("=" * 60)
    
    ai_manager = AIManager()
    task_executor = TaskExecutor(ai_manager)
    
    # Получение статистики агентов
    print("🤖 Статистика агентов:")
    agents = await ai_manager.get_active_agents()
    for agent in agents[:3]:  # Показываем первые 3 агента
        agent_type = agent.type if isinstance(agent.type, str) else agent.type.value
        agent_status = agent.status if isinstance(agent.status, str) else agent.status.value
        print(f"   - {agent.name} ({agent_type})")
        print(f"     Статус: {agent_status}")
        print(f"     Задач выполнено: {agent.tasks_completed}")
        print(f"     Средний балл: {agent.average_quality_score:.2f}")
        print()
    
    # Статистика задач
    print("📋 Статистика задач:")
    task_stats = await task_executor.get_system_stats()
    print(f"   - Активных задач: {task_stats.get('active_tasks', 0)}")
    print(f"   - Завершенных задач: {task_stats.get('completed_tasks', 0)}")
    print(f"   - Среднее время выполнения: {task_stats.get('average_execution_time', 0):.2f}с")
    print(f"   - Средний балл качества: {task_stats.get('average_quality_score', 0):.2f}")
    print()
    
    # Системная статистика
    print("🖥️ Системная статистика:")
    system_stats = await ai_manager.get_system_stats()
    print(f"   - Общий процент успеха: {system_stats.get('overall_success_rate', 0)*100:.1f}%")
    print(f"   - Агенты по статусам: {system_stats.get('agents_by_status', {})}")
    print(f"   - Агенты по типам: {system_stats.get('agents_by_type', {})}")
    print()


async def main():
    """Главная функция демонстрации"""
    try:
        print("🎯 Запуск демонстрации AI Manager")
        print("Это демонстрационная версия системы управления AI агентами")
        print("В реальной версии потребуется OpenAI API ключ\n")
        
        # Демонстрация базовой функциональности
        await demo_basic_functionality()
        
        # Демонстрация множественных агентов
        await demo_multiple_agents()
        
        # Демонстрация мониторинга
        await demo_system_monitoring()
        
        print("🎉 Демонстрация завершена успешно!")
        print("\n💡 Для полной функциональности:")
        print("   1. Получите OpenAI API ключ на https://platform.openai.com/")
        print("   2. Установите его в переменную окружения OPENAI_API_KEY")
        print("   3. Запустите сервер: python start_server.py")
        print("   4. Откройте веб-интерфейс: http://localhost:8000")
        
    except Exception as e:
        print(f"❌ Ошибка в демонстрации: {e}")
        logger.logger.error(f"Ошибка демонстрации: {e}")


if __name__ == "__main__":
    asyncio.run(main())
