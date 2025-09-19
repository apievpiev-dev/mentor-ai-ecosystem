#!/usr/bin/env python3
"""
Autonomous JARVIS Startup Script
Скрипт запуска автономной системы JARVIS
"""

import os
import sys
import time
import asyncio
import logging
import argparse
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_banner():
    """Вывод баннера системы"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🤖 AUTONOMOUS JARVIS SYSTEM v2.0 🤖                  ║
║                                                              ║
║     Автономная AI система с визуальным интеллектом          ║
║            и непрерывным обучением                           ║
║                                                              ║
║  ✅ Автономная работа 24/7                                  ║
║  ✅ Визуальный интеллект                                     ║
║  ✅ Многоагентная координация                               ║
║  ✅ Непрерывное обучение                                     ║
║  ✅ Самоисцеление и оптимизация                             ║
║  ✅ Облачное развертывание                                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def check_dependencies():
    """Проверка зависимостей"""
    logger.info("🔍 Проверка зависимостей...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'psutil', 'pillow', 'websockets'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"  ✅ {package}")
        except ImportError:
            logger.error(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"❌ Отсутствующие пакеты: {missing_packages}")
        logger.info("💡 Установите их командой: pip install --break-system-packages " + " ".join(missing_packages))
        return False
    
    logger.info("✅ Все зависимости установлены")
    return True

def check_system_files():
    """Проверка системных файлов"""
    logger.info("📁 Проверка системных файлов...")
    
    required_files = [
        'streamlined_jarvis.py',
        'multi_agent_jarvis.py', 
        'continuous_learning_jarvis.py',
        'unified_autonomous_jarvis.py'
    ]
    
    missing_files = []
    
    for file_name in required_files:
        file_path = Path(file_name)
        if file_path.exists():
            logger.info(f"  ✅ {file_name}")
        else:
            logger.error(f"  ❌ {file_name}")
            missing_files.append(file_name)
    
    if missing_files:
        logger.error(f"❌ Отсутствующие файлы: {missing_files}")
        return False
    
    logger.info("✅ Все системные файлы найдены")
    return True

async def start_streamlined_system():
    """Запуск упрощенной системы"""
    try:
        logger.info("🚀 Запуск Streamlined JARVIS...")
        
        # Импортируем и запускаем
        from streamlined_jarvis import StreamlinedJarvis
        
        jarvis = StreamlinedJarvis()
        logger.info("✅ Streamlined JARVIS запущен")
        logger.info("🌐 Веб-интерфейс: http://localhost:8080")
        
        # Запускаем сервер
        await jarvis.run(host="0.0.0.0", port=8080)
        
    except ImportError as e:
        logger.error(f"❌ Ошибка импорта: {e}")
        logger.info("💡 Убедитесь, что все файлы системы находятся в текущей директории")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска: {e}")

async def start_multi_agent_system():
    """Запуск многоагентной системы"""
    try:
        logger.info("🤖 Запуск Multi-Agent JARVIS...")
        
        from multi_agent_jarvis import MultiAgentJarvis
        
        jarvis = MultiAgentJarvis()
        logger.info("✅ Multi-Agent JARVIS запущен")
        
        # Демонстрация работы
        await asyncio.sleep(5)
        
        # Отправляем тестовые задачи
        await jarvis.submit_task("analyze_interface", {"target": "system"})
        await jarvis.submit_task("optimize_performance", {"level": "medium"})
        
        # Основной цикл
        while True:
            await asyncio.sleep(60)
            
    except ImportError as e:
        logger.error(f"❌ Ошибка импорта: {e}")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска: {e}")

async def start_learning_system():
    """Запуск системы обучения"""
    try:
        logger.info("🧠 Запуск Continuous Learning JARVIS...")
        
        from continuous_learning_jarvis import ContinuousLearningSystem
        
        learning = ContinuousLearningSystem()
        logger.info("✅ Continuous Learning JARVIS запущен")
        
        # Демонстрация обучения
        learning.record_learning_event(
            "system_startup",
            {"component": "learning_system", "mode": "demo"},
            {"status": "successful"},
            True,
            0.05
        )
        
        # Основной цикл
        while True:
            await asyncio.sleep(300)  # Каждые 5 минут
            stats = learning.get_learning_statistics()
            logger.info(f"📊 Статистика обучения: {stats.get('events_24h', 0)} событий, {stats.get('total_patterns', 0)} паттернов")
            
    except ImportError as e:
        logger.error(f"❌ Ошибка импорта: {e}")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска: {e}")

async def start_unified_system():
    """Запуск объединенной системы"""
    try:
        logger.info("🎯 Запуск Unified Autonomous JARVIS...")
        
        from unified_autonomous_jarvis import UnifiedAutonomousJarvis
        
        jarvis = UnifiedAutonomousJarvis()
        logger.info("✅ Unified Autonomous JARVIS запущен")
        logger.info("🎯 Все компоненты интегрированы и работают автономно")
        
        # Демонстрация работы
        await asyncio.sleep(5)
        
        # Отправляем комплексные задачи
        await jarvis.submit_unified_task("full_system_analysis", {"depth": "comprehensive"})
        await jarvis.submit_unified_task("autonomous_optimization", {"target": "all_components"})
        
        # Основной цикл с периодической отчетностью
        while True:
            status = jarvis.get_unified_status()
            health = status.get('system_health', 'unknown')
            
            if health in ['excellent', 'good']:
                logger.info(f"💚 Система работает отлично: {health}")
            elif health == 'fair':
                logger.warning(f"💛 Система работает удовлетворительно: {health}")
            else:
                logger.error(f"❤️ Проблемы в работе системы: {health}")
            
            await asyncio.sleep(300)  # Каждые 5 минут
            
    except ImportError as e:
        logger.error(f"❌ Ошибка импорта: {e}")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска: {e}")

def run_system_tests():
    """Запуск системных тестов"""
    logger.info("🧪 Запуск системных тестов...")
    
    tests_passed = 0
    total_tests = 4
    
    # Тест 1: Проверка зависимостей
    if check_dependencies():
        tests_passed += 1
        logger.info("✅ Тест зависимостей пройден")
    else:
        logger.error("❌ Тест зависимостей провален")
    
    # Тест 2: Проверка файлов
    if check_system_files():
        tests_passed += 1
        logger.info("✅ Тест файлов пройден")
    else:
        logger.error("❌ Тест файлов провален")
    
    # Тест 3: Проверка импортов
    try:
        import streamlined_jarvis
        tests_passed += 1
        logger.info("✅ Тест импорта основной системы пройден")
    except ImportError:
        logger.error("❌ Тест импорта основной системы провален")
    
    # Тест 4: Проверка портов
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8080))
        sock.close()
        
        if result != 0:
            tests_passed += 1
            logger.info("✅ Порт 8080 свободен")
        else:
            logger.warning("⚠️ Порт 8080 занят")
    except Exception:
        logger.error("❌ Тест портов провален")
    
    # Результат
    success_rate = tests_passed / total_tests
    logger.info(f"📊 Тесты завершены: {tests_passed}/{total_tests} ({success_rate:.1%})")
    
    if success_rate >= 0.75:
        logger.info("✅ Система готова к запуску")
        return True
    else:
        logger.error("❌ Система не готова к запуску")
        return False

async def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description='Autonomous JARVIS Startup Script')
    parser.add_argument('--mode', choices=['streamlined', 'multi-agent', 'learning', 'unified', 'test'], 
                       default='streamlined', help='Режим запуска системы')
    parser.add_argument('--skip-tests', action='store_true', help='Пропустить системные тесты')
    
    args = parser.parse_args()
    
    print_banner()
    
    # Системные тесты
    if not args.skip_tests:
        if not run_system_tests():
            logger.error("❌ Системные тесты не пройдены. Используйте --skip-tests для принудительного запуска")
            return
    
    logger.info(f"🎯 Режим запуска: {args.mode}")
    
    try:
        if args.mode == 'streamlined':
            await start_streamlined_system()
        elif args.mode == 'multi-agent':
            await start_multi_agent_system()
        elif args.mode == 'learning':
            await start_learning_system()
        elif args.mode == 'unified':
            await start_unified_system()
        elif args.mode == 'test':
            logger.info("✅ Тесты завершены")
            return
            
    except KeyboardInterrupt:
        logger.info("🛑 Остановка системы по запросу пользователя")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())