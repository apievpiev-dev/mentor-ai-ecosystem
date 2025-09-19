#!/usr/bin/env python3
"""
Демонстрация работы нейронной системы
"""

import requests
import json
import time
from datetime import datetime

def show_system_status():
    """Показать статус системы"""
    print("🧠 ENHANCED NEURAL NETWORK SYSTEM")
    print("=" * 50)
    
    try:
        # Проверяем здоровье системы
        health = requests.get("http://localhost:8081/health", timeout=5)
        if health.status_code == 200:
            health_data = health.json()
            print(f"✅ Система здорова: {health_data['status']}")
            print(f"📅 Время проверки: {health_data['timestamp']}")
        else:
            print("❌ Система недоступна")
            return
        
        # Получаем статус
        status = requests.get("http://localhost:8081/api/status", timeout=5)
        if status.status_code == 200:
            data = status.json()
            
            print(f"\n📊 СТАТИСТИКА:")
            print(f"   🔄 Статус: {'✅ Работает' if data['running'] else '❌ Остановлена'}")
            print(f"   📋 Задач в очереди: {data['task_queue_size']}")
            print(f"   ✅ Выполнено задач: {data['completed_tasks']}")
            
            if 'performance_metrics' in data:
                metrics = data['performance_metrics']
                total = metrics.get('total_tasks', 0)
                success = metrics.get('successful_tasks', 0)
                failed = metrics.get('failed_tasks', 0)
                avg_time = metrics.get('average_processing_time', 0)
                
                print(f"\n⚡ ПРОИЗВОДИТЕЛЬНОСТЬ:")
                print(f"   📈 Всего задач: {total}")
                print(f"   ✅ Успешных: {success}")
                print(f"   ❌ Неуспешных: {failed}")
                print(f"   📊 Успешность: {(success/max(total,1)*100):.1f}%")
                print(f"   ⏱️  Среднее время: {avg_time:.2f} сек")
                print(f"   🕐 Работает с: {metrics.get('uptime_start', 'N/A')}")
            
            if 'agent' in data:
                agent = data['agent']
                print(f"\n🤖 НЕЙРОННЫЙ АГЕНТ:")
                print(f"   🆔 ID: {agent.get('agent_id', 'N/A')}")
                print(f"   📛 Имя: {agent.get('name', 'N/A')}")
                print(f"   🔄 Статус: {agent.get('status', 'N/A')}")
                print(f"   ✅ Выполненных задач: {agent.get('completed_tasks', 0)}")
                print(f"   🧠 Обученных моделей: {agent.get('trained_models', 0)}")
        
        print(f"\n🌐 ДОСТУП:")
        print(f"   Веб-интерфейс: http://localhost:8081")
        print(f"   API статус: http://localhost:8081/api/status")
        print(f"   Health check: http://localhost:8081/health")
        
        print(f"\n📄 ФАЙЛЫ:")
        print(f"   Статус HTML: /workspace/neural_system_status.html")
        print(f"   Отчеты: /workspace/visual_reports/")
        print(f"   Скриншоты: /workspace/visual_screenshots/")
        
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к системе")
        print("   Проверьте, запущен ли веб-интерфейс на порту 8081")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def demo_task():
    """Демонстрационная задача"""
    print(f"\n🎯 ДЕМОНСТРАЦИЯ РАБОТЫ:")
    print("   Добавляем тестовую задачу анализа данных...")
    
    try:
        task_data = {
            "task_type": "data_analysis",
            "priority": 8,
            "input_data": {
                "data": [10, 25, 15, 30, 45, 35, 20, 40],
                "analysis_type": "live_demo"
            }
        }
        
        response = requests.post(
            "http://localhost:8081/api/add_task",
            json=task_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"   ✅ Задача добавлена: {result['task_id']}")
                print("   ⏳ Ожидаем выполнения...")
                
                # Ждем выполнения
                time.sleep(3)
                
                # Проверяем статус
                status = requests.get("http://localhost:8081/api/status", timeout=5)
                if status.status_code == 200:
                    data = status.json()
                    print(f"   📊 Обновленная статистика:")
                    print(f"      Выполнено задач: {data['completed_tasks']}")
                    if 'performance_metrics' in data:
                        metrics = data['performance_metrics']
                        success_rate = (metrics.get('successful_tasks', 0) / max(metrics.get('total_tasks', 1), 1)) * 100
                        print(f"      Успешность: {success_rate:.1f}%")
                
            else:
                print(f"   ❌ Ошибка: {result.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ HTTP ошибка: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Ошибка демонстрации: {e}")

if __name__ == "__main__":
    show_system_status()
    demo_task()
    
    print(f"\n🎉 СИСТЕМА РАБОТАЕТ АВТОНОМНО!")
    print("   Нейронная система обрабатывает задачи 24/7")
    print("   Откройте neural_system_status.html в браузере для просмотра")