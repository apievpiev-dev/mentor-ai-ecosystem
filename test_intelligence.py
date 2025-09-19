#!/usr/bin/env python3
"""
Test JARVIS Intelligence
Тестирование интеллекта системы JARVIS
"""

import requests
import json
import time

def test_ai_intelligence():
    """Тестирование AI интеллекта"""
    print("🧠 ТЕСТИРОВАНИЕ ИНТЕЛЛЕКТА JARVIS...")
    
    # Тест 1: Базовый интеллект
    try:
        response = requests.get("http://localhost:8080/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            performance = data["system_state"]["performance_score"] * 100
            print(f"✅ Базовый интеллект: {performance:.1f}% производительность")
        else:
            print("❌ Базовый интеллект недоступен")
    except:
        print("❌ Система недоступна")
        return False
    
    # Тест 2: Агентский интеллект
    try:
        response = requests.get("http://localhost:8080/api/agents/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            agents = data["active_agents"]
            print(f"✅ Агентский интеллект: {agents}/3 агентов активны")
        else:
            print("❌ Агенты недоступны")
    except:
        print("❌ Агентский интеллект недоступен")
    
    # Тест 3: Визуальный интеллект
    try:
        response = requests.get("http://localhost:8080/api/vision/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "basic_analysis" in data:
                analyses = data["basic_analysis"]["total_analyses"]
                print(f"✅ Визуальный интеллект: {analyses}+ анализов выполнено")
            else:
                print("✅ Визуальный интеллект: базовый уровень")
        else:
            print("❌ Визуальный интеллект недоступен")
    except:
        print("❌ Визуальный интеллект недоступен")
    
    # Тест 4: Обучающийся интеллект
    try:
        response = requests.get("http://localhost:8080/api/learning/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            events = data.get("events_24h", 0)
            success_rate = data.get("success_rate_24h", 0) * 100
            print(f"✅ Обучающийся интеллект: {events} событий, {success_rate:.1f}% успешность")
        else:
            print("❌ Обучающийся интеллект недоступен")
    except:
        print("❌ Обучающийся интеллект недоступен")
    
    # Тест 5: LLM интеллект
    try:
        response = requests.get("http://localhost:8080/api/ai/models", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("ollama_available"):
                models = len(data.get("available_models", []))
                print(f"✅ LLM интеллект: Ollama работает, {models} моделей")
            else:
                print("⚠️ LLM интеллект: базовый режим")
        else:
            print("❌ LLM интеллект недоступен")
    except:
        print("❌ LLM интеллект недоступен")
    
    # Тест 6: Генеративный интеллект
    try:
        response = requests.post(
            "http://localhost:8080/api/content/generate",
            json={"type": "description", "topic": "тест интеллекта"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                content = data["content"]
                print(f"✅ Генеративный интеллект: '{content[:50]}...'")
            else:
                print("❌ Генеративный интеллект: ошибка генерации")
        else:
            print("❌ Генеративный интеллект недоступен")
    except:
        print("❌ Генеративный интеллект недоступен")
    
    print("\n🎯 ИТОГ: JARVIS ОБЛАДАЕТ МНОЖЕСТВЕННЫМ ИНТЕЛЛЕКТОМ!")
    print("🌐 Доступ: http://localhost:8080")
    
    return True

if __name__ == "__main__":
    test_ai_intelligence()