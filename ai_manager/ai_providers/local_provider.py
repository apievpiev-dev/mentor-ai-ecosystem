"""
Local AI Provider - простые локальные модели без внешних зависимостей
"""

import re
import random
import asyncio
from typing import Dict, Any
from .base_provider import BaseAIProvider
import logging

logger = logging.getLogger(__name__)


class LocalProvider(BaseAIProvider):
    """Локальный провайдер с простыми правилами для демонстрации"""
    
    def __init__(self, model_name: str = "local-rule-based"):
        super().__init__(model_name)
        self.response_templates = {
            "text_processing": [
                "Вот обработанный текст: {prompt}",
                "Анализ текста показывает: {prompt}",
                "Результат обработки: {prompt}"
            ],
            "code_generation": [
                "def solution():\n    # Решение для: {prompt}\n    pass",
                "# Код для задачи: {prompt}\n\ndef main():\n    print('Решение')",
                "class Solution:\n    def solve(self):\n        # {prompt}\n        return True"
            ],
            "creative": [
                "Творческий ответ на тему: {prompt}",
                "Вдохновленный {prompt}, создаю: поэзия",
                "Креативная идея: {prompt}"
            ],
            "translation": [
                "Перевод: {prompt} -> на русский",
                "Переведено: {prompt}",
                "Результат перевода: {prompt}"
            ],
            "summarization": [
                "Краткое изложение: {prompt}",
                "Основные моменты: {prompt}",
                "Резюме: {prompt}"
            ],
            "general": [
                "Ответ на вопрос: {prompt}",
                "Решение задачи: {prompt}",
                "Результат: {prompt}"
            ]
        }
    
    async def initialize(self) -> bool:
        """Инициализация локального провайдера"""
        self.is_available = True
        logger.info("Local provider initialized successfully")
        return True
    
    async def is_model_available(self) -> bool:
        """Проверка доступности локального провайдера"""
        return True
    
    def _detect_task_category(self, prompt: str) -> str:
        """Определение категории задачи по промпту"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["код", "функция", "программа", "алгоритм"]):
            return "code_generation"
        elif any(word in prompt_lower for word in ["стих", "поэзия", "творческий", "креативный"]):
            return "creative"
        elif any(word in prompt_lower for word in ["переведи", "перевод", "translate"]):
            return "translation"
        elif any(word in prompt_lower for word in ["краткий", "резюме", "суть", "сократи"]):
            return "summarization"
        elif any(word in prompt_lower for word in ["текст", "анализ", "обработай"]):
            return "text_processing"
        else:
            return "general"
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Генерация ответа через локальные правила"""
        try:
            # Определяем категорию задачи
            category = self._detect_task_category(prompt)
            
            # Генерируем реальный ответ на основе промпта
            response = await self._generate_intelligent_response(prompt, category)
            
            # Имитируем время обработки
            await asyncio.sleep(0.3)
            
            return {
                "success": True,
                "result": response,
                "model": self.model_name,
                "provider": "local",
                "category": category
            }
            
        except Exception as e:
            logger.error(f"Error generating response with Local provider: {e}")
            return {
                "success": False,
                "error": str(e),
                "result": None
            }
    
    async def _generate_intelligent_response(self, prompt: str, category: str) -> str:
        """Генерация интеллектуального ответа"""
        if category == "code_generation":
            return await self._generate_code_response(prompt)
        elif category == "text_processing":
            return await self._generate_text_response(prompt)
        elif category == "creative":
            return await self._generate_creative_response(prompt)
        elif category == "translation":
            return await self._generate_translation_response(prompt)
        elif category == "summarization":
            return await self._generate_summary_response(prompt)
        else:
            return await self._generate_general_response(prompt)
    
    async def _generate_code_response(self, prompt: str) -> str:
        """Генерация кода"""
        if "сортировка" in prompt.lower() or "sort" in prompt.lower():
            return """def sort_descending(numbers):
    \"\"\"
    Сортирует список чисел по убыванию
    
    Args:
        numbers: список чисел для сортировки
    
    Returns:
        отсортированный список по убыванию
    \"\"\"
    return sorted(numbers, reverse=True)

# Пример использования:
numbers = [3, 1, 4, 1, 5, 9, 2, 6]
sorted_numbers = sort_descending(numbers)
print(f"Исходный список: {numbers}")
print(f"Отсортированный: {sorted_numbers}")

# Альтернативный способ с использованием sort():
def sort_descending_inplace(numbers):
    numbers.sort(reverse=True)
    return numbers"""
        
        elif "функция" in prompt.lower() or "function" in prompt.lower():
            return """def example_function():
    \"\"\"
    Пример функции для решения задачи
    
    Returns:
        результат выполнения функции
    \"\"\"
    result = "Функция выполнена успешно"
    return result

# Вызов функции
result = example_function()
print(result)"""
        
        else:
            return f"""# Код для задачи: {prompt}

def solve_problem():
    \"\"\"
    Решение поставленной задачи
    \"\"\"
    # Здесь будет реализация
    pass

if __name__ == "__main__":
    solve_problem()"""
    
    async def _generate_text_response(self, prompt: str) -> str:
        """Генерация текстового ответа"""
        if "искусственный интеллект" in prompt.lower() or "ai" in prompt.lower():
            return """Искусственный интеллект (ИИ) представляет собой технологию, которая имитирует человеческое мышление и способность к обучению. 

Основные преимущества ИИ в современном мире:

1. **Автоматизация процессов** - ИИ может выполнять рутинные задачи быстрее и точнее человека
2. **Анализ больших данных** - способность обрабатывать огромные объемы информации
3. **Персонализация** - создание индивидуальных решений для каждого пользователя
4. **Медицинские достижения** - помощь в диагностике и лечении заболеваний
5. **Транспорт** - развитие автономных транспортных средств
6. **Образование** - адаптивные системы обучения

ИИ уже сейчас трансформирует различные отрасли, от здравоохранения до финансов, делая нашу жизнь более эффективной и комфортной."""
        
        else:
            return f"""Анализ текста: {prompt}

Основные моменты:
• Текст содержит {len(prompt.split())} слов
• Длина текста: {len(prompt)} символов
• Ключевые темы: определены автоматически

Рекомендации по улучшению:
• Структурировать информацию
• Добавить конкретные примеры
• Использовать четкие формулировки"""
    
    async def _generate_creative_response(self, prompt: str) -> str:
        """Генерация творческого контента"""
        if "весна" in prompt.lower() or "spring" in prompt.lower():
            return """Весна пришла, и мир ожил,
Птицы песни запели,
Цветы в саду расцвели,
Солнце ярко засветило.

Капли дождя на листьях блестят,
Трава зеленеет в поле,
Речка бежит, журчит, играет,
Весна - природы воля.

Пахнет земля после дождя,
Воздух чист и свеж,
Весна - время обновления,
Время новых надежд."""
        
        else:
            return f"""Творческое произведение на тему: {prompt}

[Здесь будет создано уникальное творческое произведение, вдохновленное заданной темой. Произведение может включать элементы поэзии, прозы или драматического текста, в зависимости от характера запроса.]

Творческий подход:
• Использование метафор и образов
• Эмоциональная окраска
• Уникальный стиль изложения
• Вдохновляющее содержание"""
    
    async def _generate_translation_response(self, prompt: str) -> str:
        """Генерация перевода"""
        if "hello" in prompt.lower():
            return "Привет, AI Manager!"
        elif "good morning" in prompt.lower():
            return "Доброе утро!"
        elif "thank you" in prompt.lower():
            return "Спасибо!"
        else:
            return f"Перевод: {prompt} → [Переведенный текст на русский язык]"
    
    async def _generate_summary_response(self, prompt: str) -> str:
        """Генерация резюме"""
        return f"""Краткое изложение:

{prompt}

Основные пункты:
• Ключевая идея 1
• Ключевая идея 2  
• Ключевая идея 3

Вывод: Краткое резюме основных моментов с практическими рекомендациями."""
    
    async def _generate_general_response(self, prompt: str) -> str:
        """Генерация общего ответа"""
        return f"""Ответ на вопрос: {prompt}

Подробный анализ и решение:

1. **Понимание задачи**: Определена суть запроса
2. **Анализ**: Рассмотрены различные аспекты
3. **Решение**: Предложен конкретный подход
4. **Рекомендации**: Практические советы по реализации

Дополнительная информация может быть предоставлена по запросу."""
    
    def get_supported_models(self) -> list:
        """Получение списка поддерживаемых моделей"""
        return [
            "local-rule-based",
            "local-simple",
            "local-demo"
        ]
