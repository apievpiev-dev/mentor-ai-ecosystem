"""
Анализатор задач - компонент для анализа входящих задач
"""

import re
from typing import Dict, Any, List
from openai import AsyncOpenAI
from models.task import Task, TaskAnalysis, TaskCategory, TaskPriority
import logging

logger = logging.getLogger(__name__)


class TaskAnalyzer:
    """Анализатор задач для определения стратегии решения"""
    
    def __init__(self, openai_api_key: str = None):
        self.client = AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None
        self.skill_patterns = {
            "text_processing": [
                r"\b(напиши|создай текст|обработай текст|анализ текста|редактирование)\b",
                r"\b(статья|документ|сообщение|письмо|отчет)\b"
            ],
            "code_generation": [
                r"\b(код|программа|функция|алгоритм|скрипт|класс)\b",
                r"\b(python|javascript|java|sql|html|css)\b",
                r"\b(разработай|создай код|напиши программу)\b"
            ],
            "data_analysis": [
                r"\b(анализ данных|статистика|график|диаграмма|отчет)\b",
                r"\b(excel|csv|json|база данных|таблица)\b"
            ],
            "creative": [
                r"\b(творческий|креативный|история|стихотворение|рассказ)\b",
                r"\b(придумай|сочини|воображение)\b"
            ],
            "research": [
                r"\b(исследование|поиск информации|изучение|анализ)\b",
                r"\b(найди|узнай|выясни|изучи)\b"
            ],
            "translation": [
                r"\b(переведи|перевод|язык|английский|русский)\b"
            ],
            "summarization": [
                r"\b(краткое|резюме|суть|сократи|извлеки главное)\b"
            ]
        }
    
    async def analyze_task(self, task: Task) -> Dict[str, Any]:
        """Анализ задачи и определение стратегии решения"""
        try:
            logger.info(f"Анализ задачи: {task.description[:100]}...")
            
            # Определение категории задачи
            category = self._detect_category(task.description)
            
            # Определение сложности
            complexity = self._assess_complexity(task.description)
            
            # Определение необходимых навыков
            required_skills = self._identify_skills(task.description, category)
            
            # Оценка времени выполнения
            estimated_time = self._estimate_execution_time(complexity, category)
            
            # Определение типа агента
            suggested_agent_type = self._suggest_agent_type(category, required_skills)
            
            # Разбиение на подзадачи
            subtasks = await self._break_down_task(task.description, complexity)
            
            # Определение ресурсов
            resources_needed = self._identify_resources(task.description, category)
            
            # Критерии успеха
            success_criteria = self._define_success_criteria(task.description, category)
            
            analysis = {
                "category": category,
                "complexity": complexity,
                "required_skills": required_skills,
                "estimated_time": estimated_time,
                "suggested_agent_type": suggested_agent_type,
                "subtasks": subtasks,
                "resources_needed": resources_needed,
                "success_criteria": success_criteria,
                "priority_adjustment": self._adjust_priority(task.priority, complexity)
            }
            
            logger.info(f"Анализ завершен. Категория: {category}, Сложность: {complexity}")
            return analysis
            
        except Exception as e:
            logger.error(f"Ошибка анализа задачи: {e}")
            # Возвращаем базовый анализ в случае ошибки
            return {
                "category": "general",
                "complexity": "medium",
                "required_skills": ["general_reasoning"],
                "estimated_time": 5.0,
                "suggested_agent_type": "general",
                "subtasks": [task.description],
                "resources_needed": [],
                "success_criteria": ["task_completion"]
            }
    
    def _detect_category(self, description: str) -> str:
        """Определение категории задачи"""
        description_lower = description.lower()
        
        for category, patterns in self.skill_patterns.items():
            for pattern in patterns:
                if re.search(pattern, description_lower):
                    return category
        
        return "general"
    
    def _assess_complexity(self, description: str) -> str:
        """Оценка сложности задачи"""
        # Простые эвристики для определения сложности
        complexity_indicators = {
            "simple": [
                r"\b(простой|легкий|быстро|короткий)\b",
                len(description) < 50
            ],
            "complex": [
                r"\b(сложный|трудный|детальный|многоступенчатый)\b",
                len(description) > 200,
                description.count(",") > 3,
                description.count("и") > 2
            ]
        }
        
        description_lower = description.lower()
        
        for complexity, indicators in complexity_indicators.items():
            for indicator in indicators:
                if isinstance(indicator, str):
                    if re.search(indicator, description_lower):
                        return complexity
                elif isinstance(indicator, bool):
                    if indicator:
                        return complexity
        
        return "medium"
    
    def _identify_skills(self, description: str, category: str) -> List[str]:
        """Определение необходимых навыков"""
        base_skills = ["general_reasoning", "text_understanding"]
        
        skill_mapping = {
            "text_processing": ["text_analysis", "language_processing", "writing"],
            "code_generation": ["programming", "logic", "problem_solving"],
            "data_analysis": ["data_processing", "statistics", "visualization"],
            "creative": ["creativity", "storytelling", "imagination"],
            "research": ["information_retrieval", "analysis", "synthesis"],
            "translation": ["language_translation", "cultural_understanding"],
            "summarization": ["text_compression", "key_point_extraction"]
        }
        
        return base_skills + skill_mapping.get(category, [])
    
    def _estimate_execution_time(self, complexity: str, category: str) -> float:
        """Оценка времени выполнения в минутах"""
        base_times = {
            "simple": 1.0,
            "medium": 3.0,
            "complex": 8.0
        }
        
        category_multipliers = {
            "code_generation": 1.5,
            "data_analysis": 1.3,
            "research": 1.4,
            "creative": 1.2
        }
        
        base_time = base_times.get(complexity, 3.0)
        multiplier = category_multipliers.get(category, 1.0)
        
        return base_time * multiplier
    
    def _suggest_agent_type(self, category: str, skills: List[str]) -> str:
        """Определение рекомендуемого типа агента"""
        type_mapping = {
            "text_processing": "text_processor",
            "code_generation": "code_generator",
            "data_analysis": "data_analyst",
            "creative": "creative_writer",
            "research": "researcher",
            "translation": "translator",
            "summarization": "summarizer",
            "general": "general"
        }
        
        return type_mapping.get(category, "general")
    
    async def _break_down_task(self, description: str, complexity: str) -> List[str]:
        """Разбиение задачи на подзадачи"""
        if complexity == "simple":
            return [description]
        
        # Для сложных задач пытаемся разбить на этапы
        if self.client:
            try:
                response = await self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Разбей задачу на подзадачи. Верни только список подзадач, каждая с новой строки."},
                        {"role": "user", "content": f"Задача: {description}"}
                    ],
                    max_tokens=200
                )
                
                subtasks_text = response.choices[0].message.content
                subtasks = [task.strip() for task in subtasks_text.split("\n") if task.strip()]
                return subtasks if subtasks else [description]
                
            except Exception as e:
                logger.warning(f"Не удалось разбить задачу через OpenAI: {e}")
        
        # Fallback: простое разбиение по ключевым словам
        if "и" in description:
            parts = description.split("и")
            return [part.strip() for part in parts if part.strip()]
        
        return [description]
    
    def _identify_resources(self, description: str, category: str) -> List[str]:
        """Определение необходимых ресурсов"""
        resources = []
        
        if "файл" in description.lower() or "документ" in description.lower():
            resources.append("file_access")
        
        if "интернет" in description.lower() or "поиск" in description.lower():
            resources.append("web_access")
        
        if "база данных" in description.lower() or "данные" in description.lower():
            resources.append("database_access")
        
        return resources
    
    def _define_success_criteria(self, description: str, category: str) -> List[str]:
        """Определение критериев успеха"""
        base_criteria = ["task_completion"]
        
        category_criteria = {
            "text_processing": ["text_quality", "readability"],
            "code_generation": ["code_quality", "functionality"],
            "data_analysis": ["accuracy", "insights"],
            "creative": ["creativity", "engagement"],
            "research": ["accuracy", "completeness"],
            "translation": ["accuracy", "fluency"],
            "summarization": ["completeness", "clarity"]
        }
        
        return base_criteria + category_criteria.get(category, [])
    
    def _adjust_priority(self, original_priority: str, complexity: str) -> str:
        """Корректировка приоритета на основе сложности"""
        if complexity == "complex" and original_priority == "low":
            return "medium"
        elif complexity == "simple" and original_priority == "high":
            return "medium"
        
        return original_priority
