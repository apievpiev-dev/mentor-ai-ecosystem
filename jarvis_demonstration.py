#!/usr/bin/env python3
"""
JARVIS System Demonstration
Демонстрация возможностей системы JARVIS
"""

import os
import sys
import json
import time
import asyncio
import requests
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JarvisDemo:
    """Демонстратор системы JARVIS"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def print_banner(self):
        """Вывод баннера"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           🤖 JARVIS SYSTEM DEMONSTRATION 🤖                 ║
║                                                              ║
║        Демонстрация автономной AI системы                   ║
║     с визуальным интеллектом и обучением                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
        print(banner)
    
    def check_system_availability(self) -> bool:
        """Проверка доступности системы"""
        try:
            response = self.session.get(f"{self.base_url}/api/status", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Система JARVIS доступна")
                return True
            else:
                logger.error(f"❌ Система недоступна: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Ошибка подключения: {e}")
            return False
    
    def demonstrate_basic_functionality(self):
        """Демонстрация базовой функциональности"""
        logger.info("🎯 Демонстрация базовой функциональности")
        
        try:
            # Получаем статус системы
            response = self.session.get(f"{self.base_url}/api/status")
            status = response.json()
            
            system_state = status["system_state"]
            logger.info(f"📊 Производительность: {system_state['performance_score']*100:.1f}%")
            logger.info(f"🤖 Уровень автономности: {system_state['autonomy_level']}")
            logger.info(f"👁️ Визуальные анализы: {system_state['visual_analysis_count']}")
            logger.info(f"⏱️ Время работы: {status['uptime']/3600:.1f} часов")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка демонстрации базовой функциональности: {e}")
            return False
    
    def demonstrate_agents(self):
        """Демонстрация работы агентов"""
        logger.info("🤖 Демонстрация многоагентной системы")
        
        try:
            # Получаем статус агентов
            response = self.session.get(f"{self.base_url}/api/agents/status")
            agents_data = response.json()
            
            logger.info(f"👥 Всего агентов: {agents_data['total_agents']}")
            logger.info(f"✅ Активных агентов: {agents_data['active_agents']}")
            
            for agent_id, agent_info in agents_data['agents'].items():
                logger.info(f"  🤖 {agent_id}: {agent_info['specialization']}, "
                           f"производительность: {agent_info['performance']:.2f}, "
                           f"задач: {agent_info['tasks_completed']}")
            
            # Тестируем координацию агентов
            logger.info("🤝 Тестирование координации агентов...")
            coord_response = self.session.post(f"{self.base_url}/api/agents/coordinate")
            if coord_response.status_code == 200:
                result = coord_response.json()
                logger.info(f"✅ Координация запущена: {result['task_id']}")
            
            # Тестируем анализ данных
            logger.info("📊 Тестирование анализа данных...")
            analysis_response = self.session.post(f"{self.base_url}/api/data/analyze")
            if analysis_response.status_code == 200:
                result = analysis_response.json()
                logger.info(f"✅ Анализ данных запущен: {result['task_id']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка демонстрации агентов: {e}")
            return False
    
    def demonstrate_visual_intelligence(self):
        """Демонстрация визуального интеллекта"""
        logger.info("👁️ Демонстрация визуального интеллекта")
        
        try:
            # Получаем статус визуального анализа
            response = self.session.get(f"{self.base_url}/api/vision/status")
            vision_data = response.json()
            
            logger.info("📊 Базовый визуальный анализ:")
            if "basic_analysis" in vision_data:
                basic = vision_data["basic_analysis"]["last_analysis"]
                logger.info(f"  🔍 Элементов обнаружено: {basic['elements_detected']}")
                logger.info(f"  🚨 Проблем найдено: {basic['issues_found']}")
                logger.info(f"  🎯 UX Score: {basic['ux_score']:.2f}")
                logger.info(f"  📈 Уверенность: {basic['confidence']:.2f}")
            
            # Проверяем реальный анализ
            if "real_analysis" in vision_data:
                logger.info("🔍 Реальный визуальный анализ:")
                real = vision_data["real_analysis"]["last_analysis"]
                logger.info(f"  📄 Страница: {real['page_title']}")
                logger.info(f"  🔢 HTML элементов: {real['elements_count']}")
                logger.info(f"  🖱️ Интерактивных: {real['interactive_elements']}")
                logger.info(f"  ♿ Доступность: {real['accessibility_score']:.2f}")
                logger.info(f"  ⚡ Производительность: {real['performance_score']:.2f}")
                logger.info(f"  🔍 SEO: {real['seo_score']:.2f}")
            
            # Получаем детальный анализ
            detailed_response = self.session.get(f"{self.base_url}/api/vision/detailed")
            if detailed_response.status_code == 200:
                detailed = detailed_response.json()
                if "latest_analysis" in detailed:
                    latest = detailed["latest_analysis"]
                    logger.info("📈 Детальный анализ:")
                    logger.info(f"  📊 Всего анализов: {detailed['total_analyses']}")
                    logger.info(f"  💡 Предложений: {latest['suggestions_count']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка демонстрации визуального интеллекта: {e}")
            return False
    
    def demonstrate_learning_system(self):
        """Демонстрация системы обучения"""
        logger.info("🧠 Демонстрация системы обучения")
        
        try:
            # Записываем тестовое событие
            test_event = {
                "event_type": "demo_event",
                "context": {"demo": True, "timestamp": datetime.now().isoformat()},
                "outcome": {"result": "successful_demo"},
                "success": True,
                "performance_impact": 0.03
            }
            
            record_response = self.session.post(
                f"{self.base_url}/api/learning/record",
                json=test_event
            )
            
            if record_response.status_code == 200:
                logger.info("✅ Тестовое событие записано в систему обучения")
            
            # Получаем статистику обучения
            learning_response = self.session.get(f"{self.base_url}/api/learning/status")
            learning_data = learning_response.json()
            
            logger.info("📚 Статистика обучения:")
            logger.info(f"  📊 События за 24ч: {learning_data.get('events_24h', 0)}")
            logger.info(f"  ✅ Успешность: {learning_data.get('success_rate_24h', 0)*100:.1f}%")
            logger.info(f"  📈 Влияние на производительность: {learning_data.get('avg_performance_impact', 0):+.3f}")
            logger.info(f"  🎯 Всего паттернов: {learning_data.get('total_patterns', 0)}")
            logger.info(f"  🔄 Обучение активно: {learning_data.get('learning_enabled', False)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка демонстрации системы обучения: {e}")
            return False
    
    def demonstrate_autonomous_behavior(self):
        """Демонстрация автономного поведения"""
        logger.info("🤖 Демонстрация автономного поведения")
        
        try:
            # Запускаем самоулучшение
            improvement_response = self.session.post(f"{self.base_url}/api/self-improvement/trigger")
            if improvement_response.status_code == 200:
                result = improvement_response.json()
                logger.info(f"🧠 Самоулучшение запущено: {result['task_id']}")
            
            # Ждем выполнения
            time.sleep(3)
            
            # Создаем несколько задач для демонстрации автономности
            task_types = ["performance_optimization", "ui_improvement", "data_analysis"]
            
            for task_type in task_types:
                task_data = {
                    "type": task_type,
                    "priority": 6,
                    "parameters": {"demo": True, "automated": True}
                }
                
                task_response = self.session.post(
                    f"{self.base_url}/api/tasks",
                    json=task_data
                )
                
                if task_response.status_code == 200:
                    result = task_response.json()
                    logger.info(f"📋 Задача {task_type} создана: {result['task_id']}")
            
            # Ждем обработки задач
            logger.info("⏳ Ожидание автономной обработки задач...")
            time.sleep(8)
            
            # Проверяем обновленный статус
            status_response = self.session.get(f"{self.base_url}/api/status")
            status = status_response.json()
            
            logger.info("📊 Результаты автономной работы:")
            logger.info(f"  ⚡ Производительность: {status['system_state']['performance_score']*100:.1f}%")
            logger.info(f"  📋 Выполнено задач: {status['completed_tasks']}")
            logger.info(f"  🔄 Активных задач: {status['active_tasks']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка демонстрации автономного поведения: {e}")
            return False
    
    def demonstrate_real_time_updates(self):
        """Демонстрация обновлений в реальном времени"""
        logger.info("🔄 Демонстрация обновлений в реальном времени")
        
        try:
            # Мониторим изменения в течение 30 секунд
            start_time = time.time()
            last_visual_count = 0
            last_completed_tasks = 0
            
            while time.time() - start_time < 30:
                response = self.session.get(f"{self.base_url}/api/status")
                status = response.json()
                
                visual_count = status["system_state"]["visual_analysis_count"]
                completed_tasks = status["completed_tasks"]
                
                if visual_count != last_visual_count:
                    logger.info(f"👁️ Новый визуальный анализ: {visual_count} (было {last_visual_count})")
                    last_visual_count = visual_count
                
                if completed_tasks != last_completed_tasks:
                    logger.info(f"✅ Задача завершена: {completed_tasks} (было {last_completed_tasks})")
                    last_completed_tasks = completed_tasks
                
                time.sleep(5)
            
            logger.info("🎯 Мониторинг реального времени завершен")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка мониторинга реального времени: {e}")
            return False
    
    def run_full_demonstration(self):
        """Запуск полной демонстрации"""
        self.print_banner()
        
        logger.info("🚀 Начало полной демонстрации системы JARVIS")
        
        # Проверяем доступность
        if not self.check_system_availability():
            logger.error("❌ Система недоступна. Убедитесь, что JARVIS запущен на localhost:8080")
            return False
        
        success_count = 0
        total_tests = 5
        
        # Тест 1: Базовая функциональность
        if self.demonstrate_basic_functionality():
            success_count += 1
            logger.info("✅ Тест 1/5: Базовая функциональность - ПРОЙДЕН")
        else:
            logger.error("❌ Тест 1/5: Базовая функциональность - ПРОВАЛЕН")
        
        time.sleep(2)
        
        # Тест 2: Агенты
        if self.demonstrate_agents():
            success_count += 1
            logger.info("✅ Тест 2/5: Многоагентная система - ПРОЙДЕН")
        else:
            logger.error("❌ Тест 2/5: Многоагентная система - ПРОВАЛЕН")
        
        time.sleep(2)
        
        # Тест 3: Визуальный интеллект
        if self.demonstrate_visual_intelligence():
            success_count += 1
            logger.info("✅ Тест 3/5: Визуальный интеллект - ПРОЙДЕН")
        else:
            logger.error("❌ Тест 3/5: Визуальный интеллект - ПРОВАЛЕН")
        
        time.sleep(2)
        
        # Тест 4: Система обучения
        if self.demonstrate_learning_system():
            success_count += 1
            logger.info("✅ Тест 4/5: Система обучения - ПРОЙДЕН")
        else:
            logger.error("❌ Тест 4/5: Система обучения - ПРОВАЛЕН")
        
        time.sleep(2)
        
        # Тест 5: Автономное поведение
        if self.demonstrate_autonomous_behavior():
            success_count += 1
            logger.info("✅ Тест 5/5: Автономное поведение - ПРОЙДЕН")
        else:
            logger.error("❌ Тест 5/5: Автономное поведение - ПРОВАЛЕН")
        
        # Финальные результаты
        success_rate = success_count / total_tests
        logger.info("")
        logger.info("=" * 60)
        logger.info(f"🎯 РЕЗУЛЬТАТЫ ДЕМОНСТРАЦИИ: {success_count}/{total_tests} ({success_rate:.1%})")
        
        if success_rate >= 0.8:
            logger.info("🏆 ОТЛИЧНЫЙ РЕЗУЛЬТАТ! Система JARVIS работает превосходно")
        elif success_rate >= 0.6:
            logger.info("✅ ХОРОШИЙ РЕЗУЛЬТАТ! Система JARVIS работает хорошо")
        else:
            logger.warning("⚠️ УДОВЛЕТВОРИТЕЛЬНЫЙ РЕЗУЛЬТАТ. Система работает, но есть проблемы")
        
        # Дополнительная демонстрация реального времени
        logger.info("")
        logger.info("🔄 Дополнительная демонстрация: мониторинг в реальном времени")
        self.demonstrate_real_time_updates()
        
        logger.info("")
        logger.info("🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
        logger.info("🌐 Веб-интерфейс доступен: http://localhost:8080")
        
        return success_rate >= 0.6

def main():
    """Главная функция"""
    try:
        demo = JarvisDemo()
        success = demo.run_full_demonstration()
        
        if success:
            print("\n🎯 Система JARVIS готова к использованию!")
        else:
            print("\n⚠️ Обнаружены проблемы в работе системы")
        
    except KeyboardInterrupt:
        logger.info("🛑 Демонстрация прервана пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка демонстрации: {e}")

if __name__ == "__main__":
    main()