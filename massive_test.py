#!/usr/bin/env python3
"""
Массовое тестирование всех систем MENTOR x1000
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime

async def test_all_systems():
    """Тест всех систем одновременно"""
    print("🚀 ЗАПУСК МАССОВОГО ТЕСТА ВСЕХ СИСТЕМ!")
    print("=" * 60)
    
    systems = {
        "Простая система": "http://localhost:8081",
        "AI система (Llama)": "http://localhost:8082", 
        "Панель управления": "http://localhost:8083",
        "МЕГА-система x1000": "http://localhost:9000"
    }
    
    # Тест 1: Проверка доступности
    print("🔍 ТЕСТ 1: Проверка доступности всех систем")
    async with aiohttp.ClientSession() as session:
        for name, url in systems.items():
            try:
                start = time.time()
                async with session.get(f"{url}/") as response:
                    duration = time.time() - start
                    status = "✅ РАБОТАЕТ" if response.status == 200 else f"❌ {response.status}"
                    print(f"   {name}: {status} ({duration:.3f}с)")
            except Exception as e:
                print(f"   {name}: ❌ НЕДОСТУПНА ({e})")
    
    print()
    
    # Тест 2: API endpoints
    print("🔗 ТЕСТ 2: Проверка API endpoints")
    api_endpoints = [
        ("8081", "/api/system/status", "Простая система API"),
        ("8082", "/api/system/status", "AI система API"),
        ("8083", "/api/dashboard/status", "Панель управления API"),
        ("9000", "/api/mega/status", "МЕГА-система API")
    ]
    
    async with aiohttp.ClientSession() as session:
        for port, endpoint, name in api_endpoints:
            try:
                start = time.time()
                async with session.get(f"http://localhost:{port}{endpoint}") as response:
                    duration = time.time() - start
                    if response.status == 200:
                        data = await response.json()
                        agents = data.get("total_agents", data.get("active_agents", 0))
                        print(f"   {name}: ✅ OK ({agents} агентов, {duration:.3f}с)")
                    else:
                        print(f"   {name}: ❌ {response.status}")
            except Exception as e:
                print(f"   {name}: ❌ Ошибка ({e})")
    
    print()
    
    # Тест 3: Агенты
    print("🤖 ТЕСТ 3: Тестирование агентов")
    agent_tests = [
        ("8081", "Привет простой агент!", "Простые агенты"),
        ("8082", "Привет AI агент с Llama!", "AI агенты"),
        ("9000", {"type": "code", "message": "Тест мега-агента", "priority": "high"}, "МЕГА-агенты")
    ]
    
    async with aiohttp.ClientSession() as session:
        for port, message, name in agent_tests:
            try:
                start = time.time()
                
                if port == "9000":
                    # Мега-система использует другой endpoint
                    async with session.post(
                        f"http://localhost:{port}/api/mega/task",
                        json=message,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        duration = time.time() - start
                        if response.status == 200:
                            data = await response.json()
                            agent_response = data.get("response", "")[:50]
                            print(f"   {name}: ✅ Ответил за {duration:.2f}с - '{agent_response}...'")
                        else:
                            print(f"   {name}: ❌ {response.status}")
                else:
                    # Обычные системы
                    async with session.post(
                        f"http://localhost:{port}/api/chat/send",
                        json={"message": message, "user_id": "test"},
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        duration = time.time() - start
                        if response.status == 200:
                            data = await response.json()
                            agent_response = data["response"]["response"][:50]
                            print(f"   {name}: ✅ Ответил за {duration:.2f}с - '{agent_response}...'")
                        else:
                            print(f"   {name}: ❌ {response.status}")
                            
            except Exception as e:
                print(f"   {name}: ❌ Ошибка ({e})")
    
    print()
    
    # Тест 4: Нагрузочный тест мега-системы
    print("⚡ ТЕСТ 4: НАГРУЗОЧНЫЙ ТЕСТ МЕГА-СИСТЕМЫ")
    print("   Отправляю 20 задач одновременно...")
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        start_time = time.time()
        
        for i in range(20):
            task = session.post(
                "http://localhost:9000/api/mega/task",
                json={
                    "type": "test",
                    "message": f"Нагрузочный тест #{i+1}",
                    "priority": "normal"
                }
            )
            tasks.append(task)
        
        try:
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time
            
            successful = 0
            for response in responses:
                if not isinstance(response, Exception) and hasattr(response, 'status'):
                    if response.status == 200:
                        successful += 1
                    response.close()
            
            print(f"   ✅ Результат: {successful}/20 задач выполнено за {total_time:.2f}с")
            print(f"   📊 Производительность: {20/total_time:.1f} задач/сек")
            
        except Exception as e:
            print(f"   ❌ Ошибка нагрузочного теста: {e}")
    
    print()
    
    # Тест 5: Проверка файлов и логов
    print("📁 ТЕСТ 5: Проверка файлов и логов")
    
    import os
    
    files_to_check = [
        "/workspace/mentor_system.log",
        "/workspace/real_ai_mentor.log", 
        "/workspace/self_improvement.log",
        "/workspace/visual_monitor.log",
        "/workspace/cloud_deployment_report.json"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {os.path.basename(file_path)}: {size:,} байт")
        else:
            print(f"   ❌ {os.path.basename(file_path)}: не найден")
    
    # Проверяем визуальные снимки
    screenshots_dir = "/workspace/visual_screenshots"
    if os.path.exists(screenshots_dir):
        screenshots = [f for f in os.listdir(screenshots_dir) if f.endswith('.png')]
        print(f"   📸 Визуальных снимков: {len(screenshots)}")
    
    print()
    print("🎯 МАССОВЫЙ ТЕСТ ЗАВЕРШЕН!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_all_systems())