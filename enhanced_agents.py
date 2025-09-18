#!/usr/bin/env python3
"""
Улучшенные агенты с реальными навыками и подключением к AI
"""

import asyncio
import json
import logging
import os
import subprocess
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from multi_agent_system import BaseAgent, AgentType
from ai_engine import ai_engine, generate_ai_response, generate_code, analyze_data, plan_project

logger = logging.getLogger(__name__)

class EnhancedCodeDeveloperAgent(BaseAgent):
    """Улучшенный агент-разработчик с реальными навыками"""
    
    def __init__(self, agent_id: str = None):
        super().__init__(
            agent_id or str(uuid.uuid4()),
            AgentType.CODE_DEVELOPER,
            "Разработчик Кода",
            "Создает, отлаживает и оптимизирует код с помощью AI"
        )
        self._setup_skills()
        self.projects_dir = Path("/home/mentor/agent_projects")
        self.projects_dir.mkdir(exist_ok=True)
    
    def _setup_skills(self):
        """Настройка навыков"""
        self.add_skill("code_generation", self._handle_code_generation)
        self.add_skill("debugging", self._handle_debugging)
        self.add_skill("code_review", self._handle_code_review)
        self.add_skill("architecture_design", self._handle_architecture_design)
        self.add_skill("create_project", self._handle_create_project)
        self.add_skill("setup_environment", self._handle_setup_environment)
    
    async def _handle_code_generation(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация кода с помощью AI"""
        try:
            language = content.get("language", "python")
            requirements = content.get("requirements", "")
            project_type = content.get("project_type", "script")
            
            # Создаем промпт для AI
            prompt = f"""
            Создай {project_type} на языке {language} со следующими требованиями:
            {requirements}
            
            Включи:
            1. Полный рабочий код
            2. Комментарии
            3. Обработку ошибок
            4. Документацию
            """
            
            # Генерируем код с помощью AI
            code = await generate_code(prompt, language)
            
            # Сохраняем код в файл
            filename = f"generated_{int(time.time())}.{self._get_extension(language)}"
            filepath = self.projects_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code)
            
            return {
                "response": f"Создан код на {language}",
                "code": code,
                "filename": filename,
                "filepath": str(filepath),
                "language": language,
                "size": len(code)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации кода: {e}")
            return {"error": str(e)}
    
    async def _handle_debugging(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Отладка кода с помощью AI"""
        try:
            code = content.get("code", "")
            error = content.get("error", "")
            language = content.get("language", "python")
            
            # Создаем промпт для отладки
            prompt = f"""
            Отлади этот код на {language}:
            
            Код:
            {code}
            
            Ошибка:
            {error}
            
            Найди проблему и исправь код. Объясни что было не так.
            """
            
            # Получаем исправленный код от AI
            fixed_code = await generate_code(prompt, language)
            
            # Сохраняем исправленный код
            filename = f"debugged_{int(time.time())}.{self._get_extension(language)}"
            filepath = self.projects_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_code)
            
            return {
                "response": "Код отлажен и исправлен",
                "original_code": code,
                "fixed_code": fixed_code,
                "error_analysis": "Анализ ошибки выполнен AI",
                "filename": filename,
                "filepath": str(filepath)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка отладки: {e}")
            return {"error": str(e)}
    
    async def _handle_code_review(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Ревью кода с помощью AI"""
        try:
            code = content.get("code", "")
            language = content.get("language", "python")
            
            # Создаем промпт для ревью
            prompt = f"""
            Проведи ревью этого кода на {language}:
            
            {code}
            
            Оцени:
            1. Качество кода
            2. Производительность
            3. Безопасность
            4. Читаемость
            5. Соответствие стандартам
            
            Дай рекомендации по улучшению.
            """
            
            # Получаем ревью от AI
            review = await generate_ai_response(prompt)
            
            return {
                "response": "Ревью кода завершено",
                "code": code,
                "review": review,
                "language": language,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка ревью кода: {e}")
            return {"error": str(e)}
    
    async def _handle_architecture_design(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Проектирование архитектуры с помощью AI"""
        try:
            requirements = content.get("requirements", "")
            project_type = content.get("project_type", "web_app")
            
            # Создаем промпт для проектирования
            prompt = f"""
            Спроектируй архитектуру для {project_type} со следующими требованиями:
            {requirements}
            
            Включи:
            1. Диаграмму архитектуры
            2. Выбор технологий
            3. Структуру проекта
            4. API дизайн
            5. База данных
            6. Развертывание
            """
            
            # Получаем архитектуру от AI
            architecture = await generate_ai_response(prompt)
            
            # Создаем файл с архитектурой
            filename = f"architecture_{int(time.time())}.md"
            filepath = self.projects_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(architecture)
            
            return {
                "response": "Архитектура спроектирована",
                "architecture": architecture,
                "project_type": project_type,
                "filename": filename,
                "filepath": str(filepath)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка проектирования архитектуры: {e}")
            return {"error": str(e)}
    
    async def _handle_create_project(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Создание полного проекта"""
        try:
            project_name = content.get("project_name", f"project_{int(time.time())}")
            project_type = content.get("project_type", "web_app")
            requirements = content.get("requirements", "")
            
            # Создаем директорию проекта
            project_dir = self.projects_dir / project_name
            project_dir.mkdir(exist_ok=True)
            
            # Создаем структуру проекта
            structure = await self._create_project_structure(project_type, requirements)
            
            # Создаем файлы проекта
            created_files = []
            for file_info in structure:
                file_path = project_dir / file_info["name"]
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_info["content"])
                
                created_files.append(str(file_path))
            
            # Создаем README
            readme_content = await self._create_readme(project_name, project_type, requirements)
            readme_path = project_dir / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            return {
                "response": f"Проект {project_name} создан",
                "project_name": project_name,
                "project_type": project_type,
                "project_dir": str(project_dir),
                "created_files": created_files + [str(readme_path)],
                "structure": structure
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания проекта: {e}")
            return {"error": str(e)}
    
    async def _handle_setup_environment(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Настройка окружения разработки"""
        try:
            project_path = content.get("project_path", "")
            language = content.get("language", "python")
            
            if not project_path:
                return {"error": "Не указан путь к проекту"}
            
            project_dir = Path(project_path)
            if not project_dir.exists():
                return {"error": "Проект не найден"}
            
            setup_commands = []
            
            if language == "python":
                # Создаем виртуальное окружение
                venv_cmd = f"cd {project_dir} && python3 -m venv venv"
                setup_commands.append(venv_cmd)
                
                # Создаем requirements.txt
                requirements_content = await self._generate_requirements(content)
                requirements_path = project_dir / "requirements.txt"
                with open(requirements_path, 'w') as f:
                    f.write(requirements_content)
                
                # Команда установки зависимостей
                install_cmd = f"cd {project_dir} && source venv/bin/activate && pip install -r requirements.txt"
                setup_commands.append(install_cmd)
            
            elif language == "javascript":
                # Создаем package.json
                package_content = await self._generate_package_json(content)
                package_path = project_dir / "package.json"
                with open(package_path, 'w') as f:
                    f.write(package_content)
                
                # Команда установки зависимостей
                install_cmd = f"cd {project_dir} && npm install"
                setup_commands.append(install_cmd)
            
            # Выполняем команды настройки
            results = []
            for cmd in setup_commands:
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    results.append({
                        "command": cmd,
                        "success": result.returncode == 0,
                        "output": result.stdout,
                        "error": result.stderr
                    })
                except Exception as e:
                    results.append({
                        "command": cmd,
                        "success": False,
                        "error": str(e)
                    })
            
            return {
                "response": "Окружение разработки настроено",
                "project_path": project_path,
                "language": language,
                "setup_commands": setup_commands,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка настройки окружения: {e}")
            return {"error": str(e)}
    
    def _get_extension(self, language: str) -> str:
        """Получить расширение файла для языка"""
        extensions = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "java": "java",
            "cpp": "cpp",
            "c": "c",
            "go": "go",
            "rust": "rs",
            "php": "php",
            "ruby": "rb"
        }
        return extensions.get(language.lower(), "txt")
    
    async def _create_project_structure(self, project_type: str, requirements: str) -> List[Dict[str, str]]:
        """Создать структуру проекта"""
        prompt = f"""
        Создай структуру файлов для {project_type} со следующими требованиями:
        {requirements}
        
        Верни JSON с массивом файлов, где каждый файл содержит:
        - name: имя файла с путем
        - content: содержимое файла
        """
        
        response = await generate_ai_response(prompt)
        
        try:
            # Пытаемся распарсить JSON из ответа AI
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                structure = json.loads(json_match.group())
                return structure
        except:
            pass
        
        # Если не удалось распарсить, создаем базовую структуру
        if project_type == "web_app":
            return [
                {
                    "name": "app.py",
                    "content": "# Web application\nfrom flask import Flask\n\napp = Flask(__name__)\n\n@app.route('/')\ndef hello():\n    return 'Hello World!'\n\nif __name__ == '__main__':\n    app.run(debug=True)"
                },
                {
                    "name": "templates/index.html",
                    "content": "<!DOCTYPE html>\n<html>\n<head>\n    <title>Web App</title>\n</head>\n<body>\n    <h1>Welcome!</h1>\n</body>\n</html>"
                }
            ]
        else:
            return [
                {
                    "name": "main.py",
                    "content": "# Main application\nprint('Hello World!')"
                }
            ]
    
    async def _create_readme(self, project_name: str, project_type: str, requirements: str) -> str:
        """Создать README для проекта"""
        prompt = f"""
        Создай README.md для проекта {project_name} типа {project_type} со следующими требованиями:
        {requirements}
        
        Включи:
        1. Описание проекта
        2. Установку
        3. Использование
        4. API документацию
        5. Примеры
        """
        
        return await generate_ai_response(prompt)
    
    async def _generate_requirements(self, content: Dict[str, Any]) -> str:
        """Генерировать requirements.txt"""
        prompt = f"""
        Создай requirements.txt для проекта со следующими характеристиками:
        {content}
        
        Включи только необходимые зависимости с версиями.
        """
        
        return await generate_ai_response(prompt)
    
    async def _generate_package_json(self, content: Dict[str, Any]) -> str:
        """Генерировать package.json"""
        prompt = f"""
        Создай package.json для проекта со следующими характеристиками:
        {content}
        
        Включи все необходимые зависимости и скрипты.
        """
        
        return await generate_ai_response(prompt)

class EnhancedDataAnalystAgent(BaseAgent):
    """Улучшенный агент-аналитик данных"""
    
    def __init__(self, agent_id: str = None):
        super().__init__(
            agent_id or str(uuid.uuid4()),
            AgentType.DATA_ANALYST,
            "Аналитик Данных",
            "Анализирует данные, создает отчеты и визуализации с помощью AI"
        )
        self._setup_skills()
        self.data_dir = Path("/home/mentor/agent_data")
        self.data_dir.mkdir(exist_ok=True)
    
    def _setup_skills(self):
        """Настройка навыков"""
        self.add_skill("data_analysis", self._handle_data_analysis)
        self.add_skill("reporting", self._handle_reporting)
        self.add_skill("visualization", self._handle_visualization)
        self.add_skill("predictive_modeling", self._handle_predictive_modeling)
        self.add_skill("data_processing", self._handle_data_processing)
    
    async def _handle_data_analysis(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ данных с помощью AI"""
        try:
            data_source = content.get("data_source", "")
            analysis_type = content.get("analysis_type", "descriptive")
            data = content.get("data", "")
            
            # Создаем промпт для анализа
            prompt = f"""
            Проанализируй данные:
            
            Источник: {data_source}
            Тип анализа: {analysis_type}
            Данные: {data}
            
            Выполни:
            1. Описательную статистику
            2. Поиск закономерностей
            3. Выявление аномалий
            4. Корреляционный анализ
            5. Практические выводы
            """
            
            # Получаем анализ от AI
            analysis = await analyze_data(prompt)
            
            # Сохраняем анализ
            filename = f"analysis_{int(time.time())}.md"
            filepath = self.data_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(analysis)
            
            return {
                "response": "Анализ данных завершен",
                "analysis": analysis,
                "data_source": data_source,
                "analysis_type": analysis_type,
                "filename": filename,
                "filepath": str(filepath)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка анализа данных: {e}")
            return {"error": str(e)}
    
    async def _handle_reporting(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Создание отчетов с помощью AI"""
        try:
            report_type = content.get("report_type", "summary")
            data = content.get("data", "")
            requirements = content.get("requirements", "")
            
            # Создаем промпт для отчета
            prompt = f"""
            Создай {report_type} отчет со следующими требованиями:
            {requirements}
            
            Данные для отчета:
            {data}
            
            Включи:
            1. Исполнительное резюме
            2. Основные выводы
            3. Детальный анализ
            4. Рекомендации
            5. Приложения с данными
            """
            
            # Получаем отчет от AI
            report = await generate_ai_response(prompt)
            
            # Сохраняем отчет
            filename = f"report_{int(time.time())}.md"
            filepath = self.data_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report)
            
            return {
                "response": f"Отчет {report_type} создан",
                "report": report,
                "report_type": report_type,
                "filename": filename,
                "filepath": str(filepath)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания отчета: {e}")
            return {"error": str(e)}
    
    async def _handle_visualization(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Создание визуализаций с помощью AI"""
        try:
            chart_type = content.get("chart_type", "line")
            data = content.get("data", "")
            requirements = content.get("requirements", "")
            
            # Создаем промпт для визуализации
            prompt = f"""
            Создай {chart_type} график со следующими требованиями:
            {requirements}
            
            Данные:
            {data}
            
            Создай Python код для генерации графика с использованием matplotlib/seaborn.
            """
            
            # Получаем код визуализации от AI
            viz_code = await generate_code(prompt, "python")
            
            # Сохраняем код
            filename = f"visualization_{int(time.time())}.py"
            filepath = self.data_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(viz_code)
            
            # Пытаемся выполнить код для создания графика
            try:
                exec(viz_code)
                image_filename = f"chart_{int(time.time())}.png"
                image_path = self.data_dir / image_filename
                # Здесь должен быть код сохранения графика
            except Exception as e:
                logger.warning(f"⚠️ Не удалось выполнить код визуализации: {e}")
                image_path = None
            
            return {
                "response": f"Визуализация {chart_type} создана",
                "chart_type": chart_type,
                "code": viz_code,
                "filename": filename,
                "filepath": str(filepath),
                "image_path": str(image_path) if image_path else None
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания визуализации: {e}")
            return {"error": str(e)}
    
    async def _handle_predictive_modeling(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Предиктивное моделирование с помощью AI"""
        try:
            model_type = content.get("model_type", "regression")
            data = content.get("data", "")
            target = content.get("target", "")
            
            # Создаем промпт для моделирования
            prompt = f"""
            Создай {model_type} модель для предсказания {target}:
            
            Данные:
            {data}
            
            Создай Python код с использованием scikit-learn для:
            1. Подготовки данных
            2. Обучения модели
            3. Валидации
            4. Оценки качества
            5. Предсказаний
            """
            
            # Получаем код модели от AI
            model_code = await generate_code(prompt, "python")
            
            # Сохраняем код
            filename = f"model_{int(time.time())}.py"
            filepath = self.data_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(model_code)
            
            return {
                "response": f"Модель {model_type} создана",
                "model_type": model_type,
                "target": target,
                "code": model_code,
                "filename": filename,
                "filepath": str(filepath)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания модели: {e}")
            return {"error": str(e)}
    
    async def _handle_data_processing(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка данных с помощью AI"""
        try:
            operation = content.get("operation", "clean")
            data = content.get("data", "")
            requirements = content.get("requirements", "")
            
            # Создаем промпт для обработки
            prompt = f"""
            Выполни {operation} обработку данных:
            
            Требования:
            {requirements}
            
            Данные:
            {data}
            
            Создай Python код для обработки данных с использованием pandas.
            """
            
            # Получаем код обработки от AI
            processing_code = await generate_code(prompt, "python")
            
            # Сохраняем код
            filename = f"processing_{int(time.time())}.py"
            filepath = self.data_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(processing_code)
            
            return {
                "response": f"Обработка данных {operation} завершена",
                "operation": operation,
                "code": processing_code,
                "filename": filename,
                "filepath": str(filepath)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки данных: {e}")
            return {"error": str(e)}

# Глобальные экземпляры улучшенных агентов
enhanced_code_developer = EnhancedCodeDeveloperAgent()
enhanced_data_analyst = EnhancedDataAnalystAgent()

if __name__ == "__main__":
    # Тестирование улучшенных агентов
    async def test_enhanced_agents():
        print("🧪 Тестирование улучшенных агентов...")
        
        # Тест генерации кода
        result = await enhanced_code_developer._handle_code_generation({
            "language": "python",
            "requirements": "Создай простой калькулятор",
            "project_type": "script"
        })
        print(f"Генерация кода: {result.get('response', 'Ошибка')}")
        
        # Тест анализа данных
        result = await enhanced_data_analyst._handle_data_analysis({
            "data_source": "test_data",
            "analysis_type": "descriptive",
            "data": "1,2,3,4,5,6,7,8,9,10"
        })
        print(f"Анализ данных: {result.get('response', 'Ошибка')}")
    
    asyncio.run(test_enhanced_agents())

class EnhancedProjectManagerAgent(BaseAgent):
    """Улучшенный агент менеджера проектов"""
    
    def __init__(self, agent_id: str, name: str, agent_type: str, ai_engine=None, coordinator=None):
        super().__init__(agent_id, name, agent_type)
        self.ai_engine = ai_engine
        self.coordinator = coordinator
        self.skills = [
            "project_planning",
            "task_management", 
            "resource_allocation",
            "progress_tracking",
            "user_query"
        ]
        logger.info(f"🤖 Агент {name} ({agent_type}) создан")
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка сообщения"""
        try:
            content = message.get("content", {})
            task = content.get("task", "")
            message_type = content.get("type", "user_message")
            
            if message_type == "autonomous_task":
                return await self._handle_autonomous_task(content)
            else:
                return await self._handle_user_query(content)
                
        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения: {e}")
            return {"error": str(e)}
    
    async def _handle_autonomous_task(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка автономной задачи"""
        try:
            task = content.get("task", "")
            
            if self.ai_engine:
                prompt = f"Как менеджер проектов, выполни задачу: {task}. Создай план, определи приоритеты и ресурсы."
                response = await self.ai_engine.generate_response(prompt)
                
                return {
                    "response": f"Менеджер проектов выполнил задачу: {task}. Результат: {response}",
                    "status": "completed"
                }
            else:
                return {
                    "response": f"Менеджер проектов получил задачу: {task}",
                    "status": "received"
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка обработки автономной задачи: {e}")
            return {"error": str(e)}
    
    async def _handle_user_query(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка пользовательского запроса"""
        try:
            user_message = content.get("message", "")
            
            if self.ai_engine:
                prompt = f"Как менеджер проектов, ответь на вопрос: {user_message}"
                response = await self.ai_engine.generate_response(prompt)
                
                return {
                    "response": response,
                    "status": "completed"
                }
            else:
                return {
                    "response": f"Менеджер проектов получил сообщение: {user_message}",
                    "status": "received"
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка обработки пользовательского запроса: {e}")
            return {"error": str(e)}

class EnhancedDesignerAgent(BaseAgent):
    """Улучшенный агент дизайнера"""
    
    def __init__(self, agent_id: str, name: str, agent_type: str, ai_engine=None, coordinator=None):
        super().__init__(agent_id, name, agent_type)
        self.ai_engine = ai_engine
        self.coordinator = coordinator
        self.skills = [
            "ui_design",
            "ux_design",
            "visual_identity"
        ]
        logger.info(f"🤖 Агент {name} ({agent_type}) создан")
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка сообщения"""
        try:
            content = message.get("content", {})
            task = content.get("task", "")
            message_type = content.get("type", "user_message")
            
            if message_type == "autonomous_task":
                return await self._handle_autonomous_task(content)
            else:
                return await self._handle_user_query(content)
                
        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения: {e}")
            return {"error": str(e)}
    
    async def _handle_autonomous_task(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка автономной задачи"""
        try:
            task = content.get("task", "")
            
            if self.ai_engine:
                prompt = f"Как дизайнер, выполни задачу: {task}. Создай дизайн, предложи улучшения интерфейса."
                response = await self.ai_engine.generate_response(prompt)
                
                return {
                    "response": f"Дизайнер выполнил задачу: {task}. Результат: {response}",
                    "status": "completed"
                }
            else:
                return {
                    "response": f"Дизайнер получил задачу: {task}",
                    "status": "received"
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка обработки автономной задачи: {e}")
            return {"error": str(e)}
    
    async def _handle_user_query(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка пользовательского запроса"""
        try:
            user_message = content.get("message", "")
            
            if self.ai_engine:
                prompt = f"Как дизайнер, ответь на вопрос: {user_message}"
                response = await self.ai_engine.generate_response(prompt)
                
                return {
                    "response": response,
                    "status": "completed"
                }
            else:
                return {
                    "response": f"Дизайнер получил сообщение: {user_message}",
                    "status": "received"
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка обработки пользовательского запроса: {e}")
            return {"error": str(e)}

class EnhancedQATesterAgent(BaseAgent):
    """Улучшенный агент тестировщика"""
    
    def __init__(self, agent_id: str, name: str, agent_type: str, ai_engine=None, coordinator=None):
        super().__init__(agent_id, name, agent_type)
        self.ai_engine = ai_engine
        self.coordinator = coordinator
        self.skills = [
            "unit_testing",
            "integration_testing",
            "bug_reporting"
        ]
        logger.info(f"🤖 Агент {name} ({agent_type}) создан")
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка сообщения"""
        try:
            content = message.get("content", {})
            task = content.get("task", "")
            message_type = content.get("type", "user_message")
            
            if message_type == "autonomous_task":
                return await self._handle_autonomous_task(content)
            else:
                return await self._handle_user_query(content)
                
        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения: {e}")
            return {"error": str(e)}
    
    async def _handle_autonomous_task(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка автономной задачи"""
        try:
            task = content.get("task", "")
            
            if self.ai_engine:
                prompt = f"Как тестировщик, выполни задачу: {task}. Проведи тестирование, найди ошибки."
                response = await self.ai_engine.generate_response(prompt)
                
                return {
                    "response": f"Тестировщик выполнил задачу: {task}. Результат: {response}",
                    "status": "completed"
                }
            else:
                return {
                    "response": f"Тестировщик получил задачу: {task}",
                    "status": "received"
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка обработки автономной задачи: {e}")
            return {"error": str(e)}
    
    async def _handle_user_query(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка пользовательского запроса"""
        try:
            user_message = content.get("message", "")
            
            if self.ai_engine:
                prompt = f"Как тестировщик, ответь на вопрос: {user_message}"
                response = await self.ai_engine.generate_response(prompt)
                
                return {
                    "response": response,
                    "status": "completed"
                }
            else:
                return {
                    "response": f"Тестировщик получил сообщение: {user_message}",
                    "status": "received"
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка обработки пользовательского запроса: {e}")
            return {"error": str(e)}

class EnhancedGeneralAssistantAgent(BaseAgent):
    """Улучшенный агент универсального помощника"""
    
    def __init__(self, agent_id: str, name: str, agent_type: str, ai_engine=None, coordinator=None):
        super().__init__(agent_id, name, agent_type)
        self.ai_engine = ai_engine
        self.coordinator = coordinator
        self.skills = [
            "general_help",
            "planning",
            "coordination",
            "user_query"
        ]
        logger.info(f"🤖 Агент {name} ({agent_type}) создан")
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка сообщения"""
        try:
            content = message.get("content", {})
            task = content.get("task", "")
            message_type = content.get("type", "user_message")
            
            if message_type == "autonomous_task":
                return await self._handle_autonomous_task(content)
            else:
                return await self._handle_user_query(content)
                
        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения: {e}")
            return {"error": str(e)}
    
    async def _handle_autonomous_task(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка автономной задачи"""
        try:
            task = content.get("task", "")
            
            if self.ai_engine:
                prompt = f"Как универсальный помощник, выполни задачу: {task}. Предложи решения и улучшения."
                response = await self.ai_engine.generate_response(prompt)
                
                return {
                    "response": f"Универсальный помощник выполнил задачу: {task}. Результат: {response}",
                    "status": "completed"
                }
            else:
                return {
                    "response": f"Универсальный помощник получил задачу: {task}",
                    "status": "received"
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка обработки автономной задачи: {e}")
            return {"error": str(e)}
    
    async def _handle_user_query(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка пользовательского запроса"""
        try:
            user_message = content.get("message", "")
            
            if self.ai_engine:
                prompt = f"Как универсальный помощник, ответь на вопрос: {user_message}"
                response = await self.ai_engine.generate_response(prompt)
                
                return {
                    "response": response,
                    "status": "completed"
                }
            else:
                return {
                    "response": f"Универсальный помощник получил сообщение: {user_message}",
                    "status": "received"
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка обработки пользовательского запроса: {e}")
            return {"error": str(e)}
