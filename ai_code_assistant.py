#!/usr/bin/env python3
"""
AI Помощник по коду - реальные полезные функции
Анализ кода, рефакторинг, генерация, оптимизация
"""

import asyncio
import os
import ast
import json
import logging
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AICodeAssistant:
    """AI помощник для работы с кодом"""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "llama3.2:1b"
        
    async def analyze_python_file(self, file_path: str) -> Dict[str, Any]:
        """Анализ Python файла с помощью AI"""
        try:
            if not os.path.exists(file_path):
                return {"error": f"Файл {file_path} не найден"}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Базовый анализ AST
            try:
                tree = ast.parse(code)
                functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                imports = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imports.extend([alias.name for alias in node.names])
                    elif isinstance(node, ast.ImportFrom):
                        imports.append(node.module)
                
            except SyntaxError as e:
                return {"error": f"Синтаксическая ошибка в файле: {e}"}
            
            # AI анализ кода
            ai_prompt = f"""Проанализируй этот Python код и дай краткие рекомендации по улучшению:

{code[:1500]}  # Первые 1500 символов

Ответь кратко на русском языке:
1. Качество кода (1-10)
2. Основные проблемы
3. Рекомендации по улучшению"""

            ai_analysis = await self.get_ai_response(ai_prompt)
            
            return {
                "file_path": file_path,
                "lines_count": len(code.split('\n')),
                "functions": functions,
                "classes": classes,
                "imports": imports,
                "ai_analysis": ai_analysis,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Ошибка анализа файла {file_path}: {e}")
            return {"error": str(e)}
    
    async def optimize_code(self, code: str) -> Dict[str, Any]:
        """Оптимизация кода с помощью AI"""
        try:
            prompt = f"""Оптимизируй этот Python код, сделай его более эффективным и читаемым:

```python
{code[:1000]}
```

Верни только оптимизированный код без объяснений."""

            optimized = await self.get_ai_response(prompt)
            
            return {
                "original_code": code,
                "optimized_code": optimized,
                "status": "success"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def generate_function(self, description: str) -> Dict[str, Any]:
        """Генерация функции по описанию"""
        try:
            prompt = f"""Создай Python функцию по описанию: {description}

Требования:
- Добавь docstring
- Используй type hints
- Добавь обработку ошибок
- Код должен быть готов к использованию

Верни только код функции."""

            function_code = await self.get_ai_response(prompt)
            
            return {
                "description": description,
                "generated_code": function_code,
                "status": "success"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def explain_code(self, code: str) -> str:
        """Объяснение кода"""
        try:
            prompt = f"""Объясни что делает этот код простыми словами на русском языке:

```python
{code[:800]}
```

Ответ должен быть понятен даже новичку."""

            explanation = await self.get_ai_response(prompt)
            return explanation
            
        except Exception as e:
            return f"Ошибка объяснения: {e}"
    
    async def find_bugs(self, code: str) -> List[str]:
        """Поиск потенциальных багов в коде"""
        try:
            prompt = f"""Найди потенциальные баги и проблемы в этом Python коде:

```python
{code[:1200]}
```

Верни список проблем на русском языке, каждую с новой строки."""

            bugs_response = await self.get_ai_response(prompt)
            
            # Разбиваем ответ на строки
            bugs = [bug.strip() for bug in bugs_response.split('\n') if bug.strip()]
            return bugs
            
        except Exception as e:
            return [f"Ошибка анализа багов: {e}"]
    
    async def get_ai_response(self, prompt: str) -> str:
        """Получение ответа от AI"""
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Более детерминированные ответы для кода
                        "top_p": 0.8,
                        "max_tokens": 500
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("response", "").strip()
            else:
                return f"Ошибка AI: {response.status_code}"
                
        except Exception as e:
            return f"Ошибка связи с AI: {e}"

class ProjectAnalyzer:
    """Анализатор всего проекта"""
    
    def __init__(self):
        self.code_assistant = AICodeAssistant()
    
    async def analyze_project(self, project_path: str = "/workspace") -> Dict[str, Any]:
        """Анализ всего проекта"""
        try:
            python_files = []
            
            # Находим все Python файлы
            for root, dirs, files in os.walk(project_path):
                # Исключаем системные директории
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
                
                for file in files:
                    if file.endswith('.py') and not file.startswith('.'):
                        python_files.append(os.path.join(root, file))
            
            # Анализируем каждый файл
            file_analyses = []
            for py_file in python_files[:10]:  # Ограничиваем для производительности
                analysis = await self.code_assistant.analyze_python_file(py_file)
                if analysis.get("status") == "success":
                    file_analyses.append(analysis)
            
            # Общая статистика
            total_lines = sum(analysis.get("lines_count", 0) for analysis in file_analyses)
            total_functions = sum(len(analysis.get("functions", [])) for analysis in file_analyses)
            total_classes = sum(len(analysis.get("classes", [])) for analysis in file_analyses)
            
            # Самые используемые импорты
            all_imports = []
            for analysis in file_analyses:
                all_imports.extend(analysis.get("imports", []))
            
            import_counts = {}
            for imp in all_imports:
                if imp:
                    import_counts[imp] = import_counts.get(imp, 0) + 1
            
            top_imports = sorted(import_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "project_path": project_path,
                "python_files_count": len(python_files),
                "analyzed_files": len(file_analyses),
                "total_lines": total_lines,
                "total_functions": total_functions,
                "total_classes": total_classes,
                "top_imports": top_imports,
                "file_analyses": file_analyses,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Ошибка анализа проекта: {e}")
            return {"error": str(e)}

# Функции для быстрого использования
async def analyze_file(file_path: str):
    """Быстрый анализ файла"""
    assistant = AICodeAssistant()
    return await assistant.analyze_python_file(file_path)

async def optimize_file(file_path: str):
    """Оптимизация файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        assistant = AICodeAssistant()
        result = await assistant.optimize_code(code)
        
        if result.get("status") == "success":
            # Сохраняем оптимизированную версию
            backup_path = f"{file_path}.backup"
            os.rename(file_path, backup_path)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(result["optimized_code"])
            
            return f"Файл оптимизирован. Бэкап: {backup_path}"
        else:
            return f"Ошибка оптимизации: {result.get('error')}"
            
    except Exception as e:
        return f"Ошибка: {e}"

async def main():
    """Демонстрация возможностей"""
    print("🤖 AI Code Assistant - Демонстрация")
    
    # Анализируем текущий файл
    assistant = AICodeAssistant()
    
    # Анализируем один из наших файлов
    result = await assistant.analyze_python_file("/workspace/real_ai_mentor.py")
    
    if result.get("status") == "success":
        print(f"\n📊 Анализ файла real_ai_mentor.py:")
        print(f"Строк кода: {result['lines_count']}")
        print(f"Функций: {len(result['functions'])}")
        print(f"Классов: {len(result['classes'])}")
        print(f"Импортов: {len(result['imports'])}")
        print(f"\nAI анализ: {result['ai_analysis'][:200]}...")
    
    # Генерируем новую функцию
    print("\n🔧 Генерация функции:")
    func_result = await assistant.generate_function("функция для подсчета количества слов в тексте")
    
    if func_result.get("status") == "success":
        print("Сгенерированная функция:")
        print(func_result["generated_code"][:300] + "...")
    
    # Анализируем весь проект
    print("\n📁 Анализ проекта:")
    analyzer = ProjectAnalyzer()
    project_result = await analyzer.analyze_project()
    
    if project_result.get("status") == "success":
        print(f"Python файлов: {project_result['python_files_count']}")
        print(f"Всего строк: {project_result['total_lines']}")
        print(f"Функций: {project_result['total_functions']}")
        print(f"Классов: {project_result['total_classes']}")
        
        if project_result['top_imports']:
            print("Топ импортов:")
            for imp, count in project_result['top_imports'][:5]:
                print(f"  {imp}: {count}")

if __name__ == "__main__":
    asyncio.run(main())