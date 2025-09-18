"""
Генераторы AI агентов для различных типов задач
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from models.agent import Agent, AgentType, AgentCapability
from openai import AsyncOpenAI
import logging
import json

logger = logging.getLogger(__name__)


class BaseAgentGenerator(ABC):
    """Базовый класс для генераторов агентов"""
    
    def __init__(self, openai_api_key: str = None):
        self.client = AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None
    
    @abstractmethod
    async def generate_agent(self, task_analysis: Dict[str, Any]) -> Agent:
        """Генерация агента на основе анализа задачи"""
        pass
    
    def _get_base_capabilities(self) -> List[AgentCapability]:
        """Базовые способности всех агентов"""
        return [
            AgentCapability(name="general_reasoning", level=0.8, description="Общие рассуждения"),
            AgentCapability(name="text_understanding", level=0.9, description="Понимание текста"),
            AgentCapability(name="problem_solving", level=0.7, description="Решение проблем")
        ]


class GeneralAgentGenerator(BaseAgentGenerator):
    """Генератор универсальных агентов"""
    
    async def generate_agent(self, task_analysis: Dict[str, Any]) -> Agent:
        """Создание универсального агента"""
        capabilities = self._get_base_capabilities()
        
        system_prompt = """Ты - универсальный AI агент, способный решать различные задачи.
        
        Твои основные принципы:
        1. Анализируй задачу перед выполнением
        2. Предоставляй структурированные и полезные ответы
        3. Если задача сложная - разбей ее на этапы
        4. Всегда объясняй свой подход к решению
        5. Предоставляй качественные результаты
        
        Отвечай на русском языке, если не указано иное."""
        
        return Agent(
            name=f"Universal Agent {hash(str(task_analysis)) % 1000}",
            type=AgentType.GENERAL,
            system_prompt=system_prompt,
            capabilities=capabilities,
            config={
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 1500,
                "top_p": 0.9
            }
        )


class TextProcessorAgentGenerator(BaseAgentGenerator):
    """Генератор агентов для обработки текста"""
    
    async def generate_agent(self, task_analysis: Dict[str, Any]) -> Agent:
        """Создание агента для обработки текста"""
        capabilities = self._get_base_capabilities() + [
            AgentCapability(name="text_analysis", level=0.9, description="Анализ текста"),
            AgentCapability(name="language_processing", level=0.8, description="Обработка языка"),
            AgentCapability(name="writing", level=0.8, description="Написание текстов"),
            AgentCapability(name="editing", level=0.7, description="Редактирование")
        ]
        
        system_prompt = """Ты - специализированный AI агент для обработки и анализа текста.
        
        Твои специализации:
        - Анализ текста и извлечение ключевой информации
        - Редактирование и улучшение текстов
        - Создание структурированных документов
        - Проверка грамматики и стиля
        - Суммаризация и компрессия текста
        
        Принципы работы:
        1. Всегда сохраняй смысл и стиль оригинального текста
        2. Предоставляй четкую структуру в ответах
        3. Выделяй ключевые моменты
        4. Используй профессиональный язык
        5. Учитывай контекст и целевую аудиторию"""
        
        return Agent(
            name=f"Text Processor Agent {hash(str(task_analysis)) % 1000}",
            type=AgentType.TEXT_PROCESSOR,
            system_prompt=system_prompt,
            capabilities=capabilities,
            config={
                "model": "gpt-3.5-turbo",
                "temperature": 0.5,
                "max_tokens": 2000,
                "top_p": 0.8
            }
        )


class CodeGeneratorAgentGenerator(BaseAgentGenerator):
    """Генератор агентов для генерации кода"""
    
    async def generate_agent(self, task_analysis: Dict[str, Any]) -> Agent:
        """Создание агента для генерации кода"""
        capabilities = self._get_base_capabilities() + [
            AgentCapability(name="programming", level=0.9, description="Программирование"),
            AgentCapability(name="logic", level=0.8, description="Логическое мышление"),
            AgentCapability(name="algorithm_design", level=0.8, description="Проектирование алгоритмов"),
            AgentCapability(name="debugging", level=0.7, description="Отладка кода")
        ]
        
        system_prompt = """Ты - специализированный AI агент для генерации и анализа кода.
        
        Твои специализации:
        - Создание качественного, читаемого кода
        - Проектирование алгоритмов и структур данных
        - Отладка и оптимизация кода
        - Объяснение сложных концепций программирования
        - Работа с различными языками программирования
        
        Принципы работы:
        1. Пиши чистый, документированный код
        2. Следуй лучшим практикам программирования
        3. Объясняй логику и алгоритмы
        4. Предоставляй примеры использования
        5. Учитывай производительность и безопасность"""
        
        return Agent(
            name=f"Code Generator Agent {hash(str(task_analysis)) % 1000}",
            type=AgentType.CODE_GENERATOR,
            system_prompt=system_prompt,
            capabilities=capabilities,
            config={
                "model": "gpt-3.5-turbo",
                "temperature": 0.3,
                "max_tokens": 2000,
                "top_p": 0.7
            }
        )


class DataAnalystAgentGenerator(BaseAgentGenerator):
    """Генератор агентов для анализа данных"""
    
    async def generate_agent(self, task_analysis: Dict[str, Any]) -> Agent:
        """Создание агента для анализа данных"""
        capabilities = self._get_base_capabilities() + [
            AgentCapability(name="data_processing", level=0.9, description="Обработка данных"),
            AgentCapability(name="statistics", level=0.8, description="Статистический анализ"),
            AgentCapability(name="visualization", level=0.7, description="Визуализация данных"),
            AgentCapability(name="pattern_recognition", level=0.8, description="Распознавание паттернов")
        ]
        
        system_prompt = """Ты - специализированный AI агент для анализа данных.
        
        Твои специализации:
        - Статистический анализ и интерпретация данных
        - Выявление паттернов и трендов
        - Создание инсайтов и рекомендаций
        - Работа с различными форматами данных
        - Создание отчетов и визуализаций
        
        Принципы работы:
        1. Всегда проверяй качество и достоверность данных
        2. Используй подходящие статистические методы
        3. Предоставляй четкие выводы и рекомендации
        4. Объясняй ограничения анализа
        5. Создавай понятные визуализации"""
        
        return Agent(
            name=f"Data Analyst Agent {hash(str(task_analysis)) % 1000}",
            type=AgentType.DATA_ANALYST,
            system_prompt=system_prompt,
            capabilities=capabilities,
            config={
                "model": "gpt-3.5-turbo",
                "temperature": 0.4,
                "max_tokens": 2000,
                "top_p": 0.8
            }
        )


class CreativeWriterAgentGenerator(BaseAgentGenerator):
    """Генератор агентов для творческого письма"""
    
    async def generate_agent(self, task_analysis: Dict[str, Any]) -> Agent:
        """Создание агента для творческого письма"""
        capabilities = self._get_base_capabilities() + [
            AgentCapability(name="creativity", level=0.9, description="Творческое мышление"),
            AgentCapability(name="storytelling", level=0.8, description="Рассказывание историй"),
            AgentCapability(name="imagination", level=0.9, description="Воображение"),
            AgentCapability(name="emotional_intelligence", level=0.7, description="Эмоциональный интеллект")
        ]
        
        system_prompt = """Ты - специализированный AI агент для творческого письма.
        
        Твои специализации:
        - Создание оригинальных историй и рассказов
        - Написание стихотворений и поэзии
        - Разработка персонажей и сюжетов
        - Создание маркетингового контента
        - Написание сценариев и диалогов
        
        Принципы работы:
        1. Будь креативным и оригинальным
        2. Создавай эмоционально вовлекающий контент
        3. Развивай интересных персонажей
        4. Используй богатый и разнообразный язык
        5. Адаптируй стиль под целевую аудиторию"""
        
        return Agent(
            name=f"Creative Writer Agent {hash(str(task_analysis)) % 1000}",
            type=AgentType.CREATIVE_WRITER,
            system_prompt=system_prompt,
            capabilities=capabilities,
            config={
                "model": "gpt-3.5-turbo",
                "temperature": 0.9,
                "max_tokens": 2000,
                "top_p": 0.95
            }
        )


class ResearcherAgentGenerator(BaseAgentGenerator):
    """Генератор агентов для исследований"""
    
    async def generate_agent(self, task_analysis: Dict[str, Any]) -> Agent:
        """Создание агента для исследований"""
        capabilities = self._get_base_capabilities() + [
            AgentCapability(name="information_retrieval", level=0.9, description="Поиск информации"),
            AgentCapability(name="analysis", level=0.8, description="Анализ информации"),
            AgentCapability(name="synthesis", level=0.8, description="Синтез данных"),
            AgentCapability(name="critical_thinking", level=0.8, description="Критическое мышление")
        ]
        
        system_prompt = """Ты - специализированный AI агент для исследований.
        
        Твои специализации:
        - Поиск и анализ информации из различных источников
        - Синтез данных и создание выводов
        - Проведение сравнительного анализа
        - Создание исследовательских отчетов
        - Оценка достоверности источников
        
        Принципы работы:
        1. Всегда проверяй достоверность источников
        2. Предоставляй объективный анализ
        3. Указывай ограничения и неопределенности
        4. Создавай структурированные отчеты
        5. Различай факты и мнения"""
        
        return Agent(
            name=f"Researcher Agent {hash(str(task_analysis)) % 1000}",
            type=AgentType.RESEARCHER,
            system_prompt=system_prompt,
            capabilities=capabilities,
            config={
                "model": "gpt-3.5-turbo",
                "temperature": 0.4,
                "max_tokens": 2500,
                "top_p": 0.8
            }
        )


class TranslatorAgentGenerator(BaseAgentGenerator):
    """Генератор агентов для перевода"""
    
    async def generate_agent(self, task_analysis: Dict[str, Any]) -> Agent:
        """Создание агента для перевода"""
        capabilities = self._get_base_capabilities() + [
            AgentCapability(name="language_translation", level=0.9, description="Перевод языков"),
            AgentCapability(name="cultural_understanding", level=0.8, description="Понимание культур"),
            AgentCapability(name="context_analysis", level=0.8, description="Анализ контекста"),
            AgentCapability(name="linguistics", level=0.7, description="Лингвистика")
        ]
        
        system_prompt = """Ты - специализированный AI агент для перевода текстов.
        
        Твои специализации:
        - Точный перевод между различными языками
        - Сохранение смысла и стиля оригинала
        - Учет культурного контекста
        - Адаптация под целевую аудиторию
        - Работа с техническими и художественными текстами
        
        Принципы работы:
        1. Сохраняй точность и полноту перевода
        2. Учитывай культурные особенности
        3. Адаптируй стиль под целевую аудиторию
        4. Проверяй грамматику и орфографию
        5. Указывай неоднозначности при их наличии"""
        
        return Agent(
            name=f"Translator Agent {hash(str(task_analysis)) % 1000}",
            type=AgentType.TRANSLATOR,
            system_prompt=system_prompt,
            capabilities=capabilities,
            config={
                "model": "gpt-3.5-turbo",
                "temperature": 0.3,
                "max_tokens": 2000,
                "top_p": 0.8
            }
        )


class SummarizerAgentGenerator(BaseAgentGenerator):
    """Генератор агентов для суммаризации"""
    
    async def generate_agent(self, task_analysis: Dict[str, Any]) -> Agent:
        """Создание агента для суммаризации"""
        capabilities = self._get_base_capabilities() + [
            AgentCapability(name="text_compression", level=0.9, description="Сжатие текста"),
            AgentCapability(name="key_point_extraction", level=0.8, description="Извлечение ключевых моментов"),
            AgentCapability(name="information_synthesis", level=0.8, description="Синтез информации"),
            AgentCapability(name="clarity", level=0.8, description="Ясность изложения")
        ]
        
        system_prompt = """Ты - специализированный AI агент для суммаризации текстов.
        
        Твои специализации:
        - Создание кратких и точных резюме
        - Извлечение ключевой информации
        - Адаптация длины под требования
        - Сохранение важных деталей
        - Структурирование информации
        
        Принципы работы:
        1. Сохраняй все важные моменты
        2. Создавай логичную структуру
        3. Используй четкий и понятный язык
        4. Адаптируйся под целевую аудиторию
        5. Указывай источники при необходимости"""
        
        return Agent(
            name=f"Summarizer Agent {hash(str(task_analysis)) % 1000}",
            type=AgentType.SUMMARIZER,
            system_prompt=system_prompt,
            capabilities=capabilities,
            config={
                "model": "gpt-3.5-turbo",
                "temperature": 0.4,
                "max_tokens": 1500,
                "top_p": 0.8
            }
        )


class AgentGeneratorFactory:
    """Фабрика генераторов агентов"""
    
    def __init__(self):
        self.generators = {
            AgentType.GENERAL: GeneralAgentGenerator(),
            AgentType.TEXT_PROCESSOR: TextProcessorAgentGenerator(),
            AgentType.CODE_GENERATOR: CodeGeneratorAgentGenerator(),
            AgentType.DATA_ANALYST: DataAnalystAgentGenerator(),
            AgentType.CREATIVE_WRITER: CreativeWriterAgentGenerator(),
            AgentType.RESEARCHER: ResearcherAgentGenerator(),
            AgentType.TRANSLATOR: TranslatorAgentGenerator(),
            AgentType.SUMMARIZER: SummarizerAgentGenerator()
        }
    
    def get_generator(self, agent_type: AgentType) -> BaseAgentGenerator:
        """Получение генератора для указанного типа агента"""
        return self.generators.get(agent_type, self.generators[AgentType.GENERAL])
