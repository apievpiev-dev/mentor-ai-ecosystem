#!/usr/bin/env python3
"""
Скрипт для установки дополнительных AI моделей в JARVIS
"""

import subprocess
import sys
import time
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIModelInstaller:
    def __init__(self):
        self.available_models = {
            "llama3.2:3b": {
                "name": "Llama 3.2 3B",
                "size": "2GB",
                "description": "Основная модель для общих задач"
            },
            "gemma2:2b": {
                "name": "Gemma 2 2B", 
                "size": "1.6GB",
                "description": "Быстрая модель для простых задач"
            },
            "codellama:7b": {
                "name": "CodeLlama 7B",
                "size": "4GB", 
                "description": "Специализированная модель для программирования"
            },
            "mistral:7b": {
                "name": "Mistral 7B",
                "size": "4GB",
                "description": "Альтернативная модель высокого качества"
            },
            "llama3.1:8b": {
                "name": "Llama 3.1 8B",
                "size": "5GB",
                "description": "Мощная модель для сложных задач"
            },
            "phi3:3.8b": {
                "name": "Phi-3 3.8B",
                "size": "2.3GB",
                "description": "Компактная модель Microsoft"
            }
        }
    
    def check_ollama(self):
        """Проверка доступности Ollama"""
        try:
            result = subprocess.run(["ollama", "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info("✅ Ollama установлен")
                return True
            else:
                logger.error("❌ Ollama не найден")
                return False
        except Exception as e:
            logger.error(f"❌ Ошибка проверки Ollama: {e}")
            return False
    
    def get_installed_models(self):
        """Получение списка установленных моделей"""
        try:
            result = subprocess.run(["ollama", "list"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                models = []
                lines = result.stdout.strip().split('\n')[1:]  # Пропускаем заголовок
                for line in lines:
                    if line.strip():
                        model_name = line.split()[0]
                        models.append(model_name)
                return models
            else:
                logger.error("❌ Не удалось получить список моделей")
                return []
        except Exception as e:
            logger.error(f"❌ Ошибка получения моделей: {e}")
            return []
    
    def install_model(self, model_name):
        """Установка модели"""
        if model_name not in self.available_models:
            logger.error(f"❌ Модель {model_name} не найдена в списке доступных")
            return False
        
        model_info = self.available_models[model_name]
        logger.info(f"📥 Устанавливаем {model_info['name']} ({model_info['size']})...")
        logger.info(f"📝 {model_info['description']}")
        
        try:
            # Запускаем установку
            process = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Выводим прогресс
            for line in process.stdout:
                if "pulling" in line or "downloading" in line:
                    print(f"\r{line.strip()}", end="", flush=True)
            
            process.wait()
            
            if process.returncode == 0:
                logger.info(f"\n✅ Модель {model_name} установлена успешно!")
                return True
            else:
                logger.error(f"\n❌ Ошибка установки модели {model_name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка установки {model_name}: {e}")
            return False
    
    def test_model(self, model_name):
        """Тестирование модели"""
        logger.info(f"🧪 Тестируем модель {model_name}...")
        
        try:
            result = subprocess.run(
                ["ollama", "run", model_name, "Привет! Как дела?"],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                response = result.stdout.strip()
                logger.info(f"✅ Модель отвечает: {response[:100]}...")
                return True
            else:
                logger.error(f"❌ Модель не отвечает: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Таймаут при тестировании модели")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования: {e}")
            return False
    
    def show_menu(self):
        """Показать меню выбора моделей"""
        installed_models = self.get_installed_models()
        
        print("\n🤖 Установщик AI моделей для JARVIS")
        print("=" * 50)
        
        print("\n📋 Доступные модели:")
        for i, (model_id, info) in enumerate(self.available_models.items(), 1):
            status = "✅ Установлена" if model_id in installed_models else "❌ Не установлена"
            print(f"{i}. {info['name']} ({info['size']}) - {status}")
            print(f"   {info['description']}")
            print()
        
        print("0. Выход")
        print("a. Установить все модели")
        print("t. Тестировать все установленные модели")
        
        return input("\nВыберите номер модели для установки: ").strip()
    
    def install_all_models(self):
        """Установка всех моделей"""
        logger.info("🚀 Устанавливаем все доступные модели...")
        
        installed_count = 0
        total_count = len(self.available_models)
        
        for model_id, info in self.available_models.items():
            logger.info(f"\n📥 Устанавливаем {info['name']}...")
            if self.install_model(model_id):
                installed_count += 1
                # Тестируем модель
                self.test_model(model_id)
            else:
                logger.warning(f"⚠️ Не удалось установить {model_id}")
        
        logger.info(f"\n📊 Результат: {installed_count}/{total_count} моделей установлено")
    
    def test_all_models(self):
        """Тестирование всех установленных моделей"""
        installed_models = self.get_installed_models()
        
        if not installed_models:
            logger.warning("⚠️ Нет установленных моделей для тестирования")
            return
        
        logger.info(f"🧪 Тестируем {len(installed_models)} установленных моделей...")
        
        for model in installed_models:
            self.test_model(model)
            print()
    
    def run(self):
        """Основной цикл"""
        logger.info("🚀 Запуск установщика AI моделей...")
        
        # Проверяем Ollama
        if not self.check_ollama():
            logger.error("❌ Ollama не установлен. Установите Ollama сначала.")
            return False
        
        while True:
            choice = self.show_menu()
            
            if choice == "0":
                logger.info("👋 До свидания!")
                break
            elif choice == "a":
                self.install_all_models()
            elif choice == "t":
                self.test_all_models()
            elif choice.isdigit():
                model_index = int(choice) - 1
                model_ids = list(self.available_models.keys())
                
                if 0 <= model_index < len(model_ids):
                    model_id = model_ids[model_index]
                    self.install_model(model_id)
                    self.test_model(model_id)
                else:
                    logger.error("❌ Неверный номер модели")
            else:
                logger.error("❌ Неверный выбор")
            
            input("\nНажмите Enter для продолжения...")

def main():
    """Главная функция"""
    installer = AIModelInstaller()
    
    try:
        installer.run()
    except KeyboardInterrupt:
        logger.info("\n👋 Установка прервана пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    main()