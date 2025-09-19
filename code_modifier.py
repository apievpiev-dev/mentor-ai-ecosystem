#!/usr/bin/env python3
"""
Модуль для реального изменения кода через AI
"""

import ast
import os
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional

class CodeModifier:
    """Класс для безопасного изменения кода"""
    
    def __init__(self):
        self.backup_dir = "/workspace/code_backups"
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self, file_path: str) -> str:
        """Создание резервной копии файла"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{os.path.basename(file_path)}.backup_{timestamp}"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def validate_python_syntax(self, code: str) -> bool:
        """Проверка синтаксиса Python кода"""
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False
    
    async def apply_code_change(self, file_path: str, old_code: str, new_code: str) -> Dict[str, Any]:
        """Применение изменения кода с проверками"""
        try:
            # Проверяем существование файла
            if not os.path.exists(file_path):
                return {"error": f"Файл {file_path} не найден", "success": False}
            
            # Читаем текущий код
            with open(file_path, 'r', encoding='utf-8') as f:
                current_code = f.read()
            
            # Проверяем что старый код есть в файле
            if old_code not in current_code:
                return {"error": "Указанный код не найден в файле", "success": False}
            
            # Создаем резервную копию
            backup_path = self.create_backup(file_path)
            
            # Применяем изменение
            modified_code = current_code.replace(old_code, new_code)
            
            # Проверяем синтаксис
            if not self.validate_python_syntax(modified_code):
                return {"error": "Новый код содержит синтаксические ошибки", "success": False}
            
            # Сохраняем изменения
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_code)
            
            return {
                "success": True,
                "file_path": file_path,
                "backup_path": backup_path,
                "changes_applied": True,
                "description": f"Код успешно изменен. Резервная копия: {backup_path}"
            }
            
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def add_function_to_file(self, file_path: str, function_code: str, position: str = "end") -> Dict[str, Any]:
        """Добавление новой функции в файл"""
        try:
            # Создаем резервную копию
            backup_path = self.create_backup(file_path)
            
            # Читаем файл
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем синтаксис новой функции
            if not self.validate_python_syntax(function_code):
                return {"error": "Функция содержит синтаксические ошибки", "success": False}
            
            # Добавляем функцию
            if position == "end":
                modified_content = content + "\n\n" + function_code
            else:
                # Добавляем в начало (после импортов)
                lines = content.split('\n')
                import_end = 0
                for i, line in enumerate(lines):
                    if line.strip() and not (line.startswith('import') or line.startswith('from') or line.startswith('#')):
                        import_end = i
                        break
                
                lines.insert(import_end, function_code + "\n")
                modified_content = '\n'.join(lines)
            
            # Проверяем синтаксис итогового файла
            if not self.validate_python_syntax(modified_content):
                return {"error": "Итоговый файл содержит синтаксические ошибки", "success": False}
            
            # Сохраняем
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            return {
                "success": True,
                "file_path": file_path,
                "backup_path": backup_path,
                "function_added": True,
                "description": f"Функция добавлена в {position} файла. Резервная копия: {backup_path}"
            }
            
        except Exception as e:
            return {"error": str(e), "success": False}

# Глобальный экземпляр
code_modifier = CodeModifier()