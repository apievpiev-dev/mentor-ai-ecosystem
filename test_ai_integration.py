#!/usr/bin/env python3
"""
Тест интеграции AI с JARVIS
"""

import requests
import json

def test_ollama_direct():
    """Прямой тест Ollama"""
    print("🧪 Тестируем Ollama напрямую...")
    
    try:
        # Проверяем доступность Ollama
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            print(f"✅ Ollama работает, доступные модели: {models}")
            
            # Тестируем генерацию
            payload = {
                "model": "llama3.2:3b",
                "prompt": "Привет! Как дела?",
                "stream": False
            }
            
            response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Ollama отвечает: {data.get('response', '')[:100]}...")
                return True
            else:
                print(f"❌ Ollama не отвечает: {response.status_code}")
                return False
        else:
            print(f"❌ Ollama недоступен: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования Ollama: {e}")
        return False

def test_jarvis_api():
    """Тест API JARVIS"""
    print("\n🧪 Тестируем API JARVIS...")
    
    try:
        # Проверяем статус
        response = requests.get("http://localhost:8000/api/system/status", timeout=5)
        if response.status_code == 200:
            print("✅ JARVIS API работает")
        else:
            print(f"❌ JARVIS API недоступен: {response.status_code}")
            return False
        
        # Проверяем модели
        response = requests.get("http://localhost:8000/api/ai/models", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                print(f"❌ Ошибка получения моделей: {data['error']}")
            else:
                print(f"✅ Модели получены: {data.get('available_models', [])}")
        else:
            print(f"❌ Не удалось получить модели: {response.status_code}")
        
        # Тестируем чат
        response = requests.post(
            "http://localhost:8000/api/chat",
            json={"message": "Привет!"},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ JARVIS отвечает: {data.get('response', '')[:100]}...")
            return True
        else:
            print(f"❌ JARVIS не отвечает: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования JARVIS: {e}")
        return False

def main():
    """Главная функция тестирования"""
    print("🚀 Запуск тестов интеграции AI...")
    
    ollama_ok = test_ollama_direct()
    jarvis_ok = test_jarvis_api()
    
    print(f"\n📊 Результаты тестирования:")
    print(f"Ollama: {'✅' if ollama_ok else '❌'}")
    print(f"JARVIS: {'✅' if jarvis_ok else '❌'}")
    
    if ollama_ok and jarvis_ok:
        print("\n🎉 Все тесты пройдены! AI интеграция работает!")
    else:
        print("\n⚠️ Есть проблемы с интеграцией AI")

if __name__ == "__main__":
    main()