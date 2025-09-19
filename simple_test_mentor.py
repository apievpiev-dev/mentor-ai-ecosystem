#!/usr/bin/env python3
"""
Простой тест системы MENTOR без внешних зависимостей
"""

import urllib.request
import urllib.parse
import json
import time

def test_mentor_system():
    """Простой тест системы MENTOR"""
    
    print("🧪 Тестирование системы MENTOR...")
    
    # Проверяем статус системы
    try:
        with urllib.request.urlopen("http://localhost:8080/api/integrated/status", timeout=5) as response:
            if response.status == 200:
                data = response.read().decode('utf-8')
                status = json.loads(data)
                print(f"✅ Система работает: {status['system_name']}")
                print(f"📊 Агентов: {status['total_agents']}")
                print(f"🚀 Параллельная система: {status['parallel_system']['system_name']}")
                print(f"📈 Сообщений обработано: {status['messages_processed']}")
                print(f"🎯 Параллельных задач: {status['parallel_tasks_completed']}")
            else:
                print(f"❌ Ошибка статуса: {response.status}")
                return
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return
    
    # Тестируем агентов
    try:
        with urllib.request.urlopen("http://localhost:8080/api/integrated/agents", timeout=5) as response:
            if response.status == 200:
                data = response.read().decode('utf-8')
                agents_data = json.loads(data)
                print(f"\n🤖 Доступные агенты:")
                for agent in agents_data['agents']:
                    print(f"  - {agent['name']}: {agent['status']}")
                    print(f"    Параллельных задач: {agent['parallel_tasks_created']}")
                    print(f"    Навыки: {', '.join(agent['skills'][:3])}")
            else:
                print(f"❌ Ошибка получения агентов: {response.status}")
    except Exception as e:
        print(f"❌ Ошибка получения агентов: {e}")
    
    # Тестируем параллельную систему
    try:
        with urllib.request.urlopen("http://localhost:8080/api/parallel/status", timeout=5) as response:
            if response.status == 200:
                data = response.read().decode('utf-8')
                parallel_status = json.loads(data)
                print(f"\n🚀 Параллельная система:")
                print(f"  - Агентов: {parallel_status['total_agents']}")
                print(f"  - Максимум воркеров: {parallel_status['max_workers']}")
                print(f"  - Завершенных задач: {parallel_status['completed_tasks']}")
                print(f"  - Ожидающих задач: {parallel_status['pending_tasks']}")
            else:
                print(f"❌ Ошибка параллельной системы: {response.status}")
    except Exception as e:
        print(f"❌ Ошибка параллельной системы: {e}")
    
    print(f"\n🌐 Веб-интерфейс доступен на: http://localhost:8080")
    print(f"📝 Откройте браузер и протестируйте систему вручную!")
    print(f"\n💡 Попробуйте отправить сообщения типа:")
    print(f"   - 'Создай систему для анализа данных'")
    print(f"   - 'Проанализируй производительность'")
    print(f"   - 'Создай план проекта'")

if __name__ == "__main__":
    test_mentor_system()