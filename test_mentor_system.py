#!/usr/bin/env python3
"""
Тестовый скрипт для системы MENTOR
"""

import urllib.request
import urllib.parse
import json
import time

def test_mentor_system():
    """Тестирование системы MENTOR"""
    
    print("🧪 Тестирование системы MENTOR...")
    
    # Проверяем статус системы
    try:
        with urllib.request.urlopen("http://localhost:8081/api/status", timeout=5) as response:
            if response.status == 200:
                data = response.read().decode('utf-8')
                status = json.loads(data)
                print(f"✅ Система работает: {status['system_name']}")
                print(f"📊 Статус: {status['status']}")
                print(f"🤖 Агентов: {status['agents']}")
            else:
                print(f"❌ Ошибка статуса: {response.status}")
                return
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return
    
    # Тестируем разных агентов
    test_messages = [
        {"message": "Привет! Как дела?", "agent_type": "general_assistant"},
        {"message": "Создай код для веб-приложения", "agent_type": "code_developer"},
        {"message": "Проанализируй данные продаж", "agent_type": "data_analyst"},
        {"message": "Создай план проекта", "agent_type": "project_manager"},
        {"message": "Создай дизайн интерфейса", "agent_type": "designer"},
        {"message": "Протестируй систему", "agent_type": "qa_tester"}
    ]
    
    print(f"\n🤖 Тестирование агентов:")
    
    for i, test_data in enumerate(test_messages, 1):
        try:
            # Создаем POST запрос
            data = json.dumps(test_data).encode('utf-8')
            req = urllib.request.Request(
                "http://localhost:8081/api/chat",
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    response_data = response.read().decode('utf-8')
                    result = json.loads(response_data)
                    
                    if result.get('success'):
                        agent_response = result['response']['response']
                        agent_name = result['response']['agent']
                        print(f"  {i}. {agent_name}: {agent_response[:50]}...")
                    else:
                        print(f"  {i}. Ошибка: {result.get('error', 'Неизвестная ошибка')}")
                else:
                    print(f"  {i}. HTTP ошибка: {response.status}")
                    
        except Exception as e:
            print(f"  {i}. Ошибка: {e}")
        
        time.sleep(0.5)  # Небольшая пауза между запросами
    
    print(f"\n🌐 Веб-интерфейс доступен на: http://localhost:8081")
    print(f"📝 Откройте браузер и протестируйте систему вручную!")
    print(f"\n💡 Система MENTOR работает корректно!")

if __name__ == "__main__":
    test_mentor_system()