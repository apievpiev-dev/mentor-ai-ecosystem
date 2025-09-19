#!/usr/bin/env python3
"""
Тестовый скрипт для интегрированной системы MENTOR
"""

import asyncio
import json
import requests
import time
from datetime import datetime

async def test_integrated_mentor():
    """Тестирование интегрированной системы MENTOR"""
    
    print("🧪 Тестирование интегрированной системы MENTOR...")
    
    # Проверяем статус системы
    try:
        response = requests.get("http://localhost:8080/api/integrated/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Система работает: {status['system_name']}")
            print(f"📊 Агентов: {status['total_agents']}")
            print(f"🚀 Параллельная система: {status['parallel_system']['system_name']}")
        else:
            print(f"❌ Ошибка статуса: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return
    
    # Тестируем агентов
    try:
        response = requests.get("http://localhost:8080/api/integrated/agents", timeout=5)
        if response.status_code == 200:
            agents_data = response.json()
            print(f"\n🤖 Доступные агенты:")
            for agent in agents_data['agents']:
                print(f"  - {agent['name']}: {agent['status']} (Параллельных задач: {agent['parallel_tasks_created']})")
        else:
            print(f"❌ Ошибка получения агентов: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка получения агентов: {e}")
    
    # Тестируем параллельную систему
    try:
        response = requests.get("http://localhost:8080/api/parallel/status", timeout=5)
        if response.status_code == 200:
            parallel_status = response.json()
            print(f"\n🚀 Параллельная система:")
            print(f"  - Агентов: {parallel_status['total_agents']}")
            print(f"  - Максимум воркеров: {parallel_status['max_workers']}")
            print(f"  - Завершенных задач: {parallel_status['completed_tasks']}")
        else:
            print(f"❌ Ошибка параллельной системы: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка параллельной системы: {e}")
    
    print(f"\n🌐 Веб-интерфейс доступен на: http://localhost:8080")
    print(f"📝 Откройте браузер и протестируйте систему вручную!")

if __name__ == "__main__":
    asyncio.run(test_integrated_mentor())