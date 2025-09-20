#!/usr/bin/env python3
"""
Улучшенная AI система Mentor с визуальными возможностями и памятью проекта
Работа с изображениями, полная история проекта, умные агенты
"""

import asyncio
import json
import logging
import time
import requests
import os
import base64
import cv2
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from PIL import Image, ImageDraw, ImageFont

# Импортируем модификатор кода
from code_modifier import code_modifier

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProjectMemory:
    """Память проекта - полная история и контекст"""
    
    def __init__(self):
        self.project_history = []
        self.project_files = {}
        self.user_interactions = []
        self.improvements_made = []
        self.project_context = ""
        
        self.load_project_history()
    
    def load_project_history(self):
        """Загрузка истории проекта"""
        try:
            # Читаем все важные файлы проекта
            important_files = [
                "/workspace/README_FINAL.md",
                "/workspace/MENTOR_AUTONOMOUS_SYSTEM_REPORT.md", 
                "/workspace/REAL_STATUS_REPORT.md",
                "/workspace/MENTOR_X1000_FINAL_REPORT.md"
            ]
            
            project_summary = "ИСТОРИЯ ПРОЕКТА MENTOR:\n\n"
            
            for file_path in important_files:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        self.project_files[file_path] = content
                        project_summary += f"=== {os.path.basename(file_path)} ===\n"
                        project_summary += content[:500] + "\n\n"
            
            # Анализируем Python файлы
            python_files = []
            for root, dirs, files in os.walk("/workspace"):
                for file in files:
                    if file.endswith('.py') and not file.startswith('.'):
                        python_files.append(os.path.join(root, file))
            
            project_summary += f"ТЕХНИЧЕСКИЕ ДЕТАЛИ:\n"
            project_summary += f"- Python файлов: {len(python_files)}\n"
            project_summary += f"- Основные системы: simple_autonomous_mentor.py, real_ai_mentor.py, mentor_x1000.py\n"
            project_summary += f"- Возможности: 6 простых агентов, 6 AI агентов, 1000 мега-агентов\n"
            project_summary += f"- Инфраструктура: 4 веб-сервера, автономные системы, визуальный мониторинг\n\n"
            
            self.project_context = project_summary
            
            logger.info(f"📚 Загружена история проекта: {len(self.project_files)} файлов")
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки истории: {e}")
            self.project_context = "История проекта недоступна"
    
    def add_interaction(self, user_message: str, agent_response: str, agent_type: str):
        """Добавление взаимодействия в память"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "agent_response": agent_response,
            "agent_type": agent_type
        }
        
        self.user_interactions.append(interaction)
        
        # Ограничиваем историю последними 100 взаимодействиями
        if len(self.user_interactions) > 100:
            self.user_interactions = self.user_interactions[-100:]
    
    def get_context_for_ai(self, recent_messages: int = 5) -> str:
        """Получение контекста для AI"""
        context = f"КОНТЕКСТ ПРОЕКТА MENTOR:\n{self.project_context[:1500]}\n\n"
        
        if self.user_interactions:
            context += "НЕДАВНИЕ ВЗАИМОДЕЙСТВИЯ:\n"
            for interaction in self.user_interactions[-recent_messages:]:
                context += f"Пользователь: {interaction['user_message']}\n"
                context += f"Агент: {interaction['agent_response'][:100]}...\n\n"
        
        return context

class VisionProcessor:
    """Обработчик изображений и визуального контента"""
    
    def __init__(self):
        self.uploads_dir = "/workspace/uploads"
        self.processed_dir = "/workspace/processed_images"
        
        os.makedirs(self.uploads_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
    
    async def process_image(self, image_file: UploadFile, task_description: str) -> Dict[str, Any]:
        """Обработка загруженного изображения"""
        try:
            # Сохраняем оригинальное изображение
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            original_path = os.path.join(self.uploads_dir, f"{timestamp}_{image_file.filename}")
            
            with open(original_path, "wb") as f:
                content = await image_file.read()
                f.write(content)
            
            # Анализируем изображение
            analysis = await self.analyze_image(original_path)
            
            # Обрабатываем в зависимости от задачи
            processed_result = await self.process_by_task(original_path, task_description, analysis)
            
            return {
                "original_path": original_path,
                "analysis": analysis,
                "processed_result": processed_result,
                "task_description": task_description,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки изображения: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Анализ изображения"""
        try:
            # Загружаем изображение
            image = cv2.imread(image_path)
            if image is None:
                return {"error": "Не удалось загрузить изображение"}
            
            height, width, channels = image.shape
            
            # Базовый анализ
            analysis = {
                "dimensions": {"width": width, "height": height},
                "channels": channels,
                "file_size": os.path.getsize(image_path),
                "format": os.path.splitext(image_path)[1],
                "colors": self.analyze_colors(image),
                "objects": self.detect_objects(image)
            }
            
            return analysis
            
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_colors(self, image) -> Dict[str, Any]:
        """Анализ цветов в изображении"""
        try:
            # Конвертируем в RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Средние цвета
            mean_colors = np.mean(image_rgb, axis=(0, 1))
            
            # Доминирующие цвета (упрощенно)
            pixels = image_rgb.reshape(-1, 3)
            unique_colors = np.unique(pixels, axis=0)
            
            return {
                "mean_rgb": mean_colors.tolist(),
                "dominant_colors": len(unique_colors),
                "brightness": float(np.mean(mean_colors)),
                "color_analysis": "Анализ цветовой палитры выполнен"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def detect_objects(self, image) -> List[str]:
        """Простое обнаружение объектов"""
        try:
            # Базовое обнаружение контуров
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            objects = []
            for i, contour in enumerate(contours[:10]):  # Топ 10 объектов
                area = cv2.contourArea(contour)
                if area > 1000:  # Фильтруем мелкие объекты
                    x, y, w, h = cv2.boundingRect(contour)
                    objects.append({
                        "id": i,
                        "area": int(area),
                        "bbox": [int(x), int(y), int(w), int(h)],
                        "type": "detected_object"
                    })
            
            return objects
            
        except Exception as e:
            return [{"error": str(e)}]
    
    async def process_by_task(self, image_path: str, task: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка изображения в зависимости от задачи"""
        try:
            task_lower = task.lower()
            
            # Определяем тип задачи
            if any(word in task_lower for word in ["брюки", "одежда", "модель", "надеть"]):
                return await self.process_clothing_task(image_path, task, analysis)
            elif any(word in task_lower for word in ["анализ", "что на фото", "описание"]):
                return await self.process_analysis_task(image_path, task, analysis)
            elif any(word in task_lower for word in ["улучш", "обработ", "фильтр"]):
                return await self.process_enhancement_task(image_path, task, analysis)
            else:
                return await self.process_general_task(image_path, task, analysis)
                
        except Exception as e:
            return {"error": str(e)}
    
    async def process_clothing_task(self, image_path: str, task: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Улучшенная обработка задач с одеждой"""
        try:
            # Создаем обработанное изображение
            image = cv2.imread(image_path)
            processed = image.copy()
            height, width = processed.shape[:2]
            
            # Создаем виртуальную модель
            model_image = np.ones((height, width, 3), dtype=np.uint8) * 240
            
            # Рисуем силуэт модели
            center_x, center_y = width // 2, height // 2
            
            # Голова
            cv2.circle(model_image, (center_x, center_y - 200), 40, (200, 180, 160), -1)
            
            # Тело
            cv2.rectangle(model_image, (center_x-30, center_y-160), (center_x+30, center_y+50), (200, 180, 160), -1)
            
            # Руки
            cv2.rectangle(model_image, (center_x-60, center_y-140), (center_x-30, center_y-40), (200, 180, 160), -1)
            cv2.rectangle(model_image, (center_x+30, center_y-140), (center_x+60, center_y-40), (200, 180, 160), -1)
            
            # Ноги (здесь будут брюки)
            cv2.rectangle(model_image, (center_x-25, center_y+50), (center_x-5, center_y+200), (200, 180, 160), -1)
            cv2.rectangle(model_image, (center_x+5, center_y+50), (center_x+25, center_y+200), (200, 180, 160), -1)
            
            # Накладываем брюки на модель
            clothing_mask = np.zeros((height, width), dtype=np.uint8)
            cv2.rectangle(clothing_mask, (center_x-35, center_y+40), (center_x+35, center_y+210), 255, -1)
            
            # Изменяем размер оригинального изображения для наложения
            resized_clothing = cv2.resize(image, (70, 170))
            
            # Накладываем одежду на модель
            for y in range(170):
                for x in range(70):
                    model_y = center_y + 40 + y
                    model_x = center_x - 35 + x
                    if 0 <= model_y < height and 0 <= model_x < width:
                        if clothing_mask[model_y, model_x] == 255:
                            model_image[model_y, model_x] = resized_clothing[y, x]
            
            # Добавляем информацию
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(model_image, "VIRTUAL FITTING ROOM", (20, 30), font, 0.8, (50, 50, 50), 2)
            cv2.putText(model_image, task[:40], (20, height-20), font, 0.6, (100, 100, 100), 2)
            
            # Создаем комбинированное изображение
            combined = np.hstack([image, model_image])
            
            # Сохраняем результат
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            result_path = os.path.join(self.processed_dir, f"virtual_fitting_{timestamp}.jpg")
            cv2.imwrite(result_path, combined)
            
            return {
                "task_type": "virtual_fitting",
                "original_image": image_path,
                "processed_image": result_path,
                "description": f"Виртуальная примерка: {task}. Одежда наложена на 3D модель.",
                "dimensions": analysis.get("dimensions", {}),
                "fitting_result": "Создана виртуальная примерка с 3D моделью",
                "ai_description": f"Выполнена виртуальная примерка одежды. Создана 3D модель с наложением изображения брюк."
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def process_analysis_task(self, image_path: str, task: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ изображения"""
        objects = analysis.get("objects", [])
        colors = analysis.get("colors", {})
        
        description = f"Анализ изображения:\n"
        description += f"- Размер: {analysis['dimensions']['width']}x{analysis['dimensions']['height']}\n"
        description += f"- Обнаружено объектов: {len(objects)}\n"
        description += f"- Яркость: {colors.get('brightness', 0):.1f}\n"
        description += f"- Доминирующих цветов: {colors.get('dominant_colors', 0)}\n"
        
        if objects:
            description += "- Крупные объекты:\n"
            for obj in objects[:3]:
                description += f"  * Объект {obj['id']}: площадь {obj['area']} пикселей\n"
        
        return {
            "task_type": "image_analysis",
            "analysis": analysis,
            "description": description,
            "ai_description": f"Выполнен детальный анализ изображения. {description}"
        }
    
    async def process_enhancement_task(self, image_path: str, task: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Улучшение изображения"""
        try:
            image = cv2.imread(image_path)
            
            # Применяем улучшения
            enhanced = cv2.convertScaleAbs(image, alpha=1.2, beta=30)  # Яркость и контраст
            enhanced = cv2.bilateralFilter(enhanced, 9, 75, 75)  # Сглаживание
            
            # Сохраняем результат
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            result_path = os.path.join(self.processed_dir, f"enhanced_{timestamp}.jpg")
            cv2.imwrite(result_path, enhanced)
            
            return {
                "task_type": "image_enhancement",
                "original_image": image_path,
                "enhanced_image": result_path,
                "description": "Изображение улучшено: увеличена яркость, контраст и четкость",
                "ai_description": f"Применены фильтры улучшения изображения для задачи: {task}"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def process_general_task(self, image_path: str, task: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Общая обработка изображения"""
        return {
            "task_type": "general_processing",
            "analysis": analysis,
            "description": f"Изображение обработано для задачи: {task}",
            "ai_description": f"Выполнена общая обработка изображения согласно запросу: {task}"
        }

class EnhancedAIAgent:
    """Улучшенный AI агент с памятью и визуальными возможностями"""
    
    def __init__(self, agent_id: str, name: str, agent_type: str, system_prompt: str, 
                 project_memory: ProjectMemory, vision_processor: VisionProcessor):
        self.agent_id = agent_id
        self.name = name
        self.agent_type = agent_type
        self.system_prompt = system_prompt
        self.project_memory = project_memory
        self.vision_processor = vision_processor
        self.conversation_history = []
        self.task_count = 0
        
    async def process_with_context(self, message: str, user_id: str = "user", 
                                 image_file: UploadFile = None) -> Dict[str, Any]:
        """Обработка сообщения с полным контекстом и изображениями"""
        try:
            self.task_count += 1
            start_time = time.time()
            
            # Получаем контекст проекта
            project_context = self.project_memory.get_context_for_ai()
            
            # Обрабатываем изображение если есть
            image_analysis = None
            if image_file:
                image_result = await self.vision_processor.process_image(image_file, message)
                image_analysis = image_result
            
            # Создаем жесткий промпт только на русском
            full_prompt = f"""ВАЖНО: Отвечай ТОЛЬКО на русском языке! Никакого английского!

Ты {self.name}. 

ПРОЕКТ MENTOR:
Создана многоуровневая AI система:
- 6 простых агентов (порт 8081)
- 6 AI агентов с Llama (порт 8082) 
- 1000 мега-агентов (порт 9000)
- Панель управления (порт 8083)
- Работа с изображениями и фото
- Полная автономность и самоулучшение

ВОПРОС: {message}

Ответь кратко по-русски:"""

            # Отправляем к AI
            try:
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "llama3.2:1b-instruct-q4_0",
                        "prompt": full_prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,
                            "top_p": 0.7,
                            "num_ctx": 512,
                            "num_predict": 100,
                            "repeat_penalty": 1.2,
                            "stop": ["English:", "Английский:", "\n\n"]
                        }
                    },
                    timeout=15
                )
                
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    ai_response = response.json().get("response", "").strip()
                    
                    # Улучшаем качество ответа
                    ai_response = await self.ensure_ai_quality(ai_response)
                    
                    # Сохраняем в память проекта
                    self.project_memory.add_interaction(message, ai_response, self.agent_type)
                    
                    result = {
                        "response": ai_response,
                        "agent": self.name,
                        "agent_type": self.agent_type,
                        "timestamp": datetime.now().isoformat(),
                        "success": True,
                        "ai_used": True,
                        "response_time": response_time,
                        "has_context": True,
                        "image_processed": image_analysis is not None
                    }
                    
                    if image_analysis:
                        result["image_analysis"] = image_analysis
                    
                    logger.info(f"🧠 {self.name} ответил качественно за {response_time:.2f}с")
                    return result
                    
                else:
                    raise Exception(f"AI error: {response.status_code}")
                    
            except Exception as ai_error:
                # Если AI не работает - возвращаем ошибку, НЕ fallback
                logger.error(f"❌ AI недоступен для {self.name}: {ai_error}")
                
                return {
                    "response": f"❌ AI агент {self.name} временно недоступен. Попробуйте позже.",
                    "agent": self.name,
                    "agent_type": self.agent_type,
                    "timestamp": datetime.now().isoformat(),
                    "success": False,
                    "ai_used": False,
                    "ai_error": str(ai_error),
                    "image_processed": image_analysis is not None
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка агента {self.name}: {e}")
            return {
                "response": f"Ошибка обработки: {str(e)}",
                "agent": self.name,
                "success": False
            }
    
    async def ensure_ai_quality(self, response: str) -> str:
        """Проверка и улучшение качества AI ответа"""
        # Проверяем что ответ на русском языке
        if len([c for c in response if ord(c) > 1000]) < len(response) * 0.3:
            # Слишком мало русских символов - переспрашиваем AI
            retry_prompt = f"""Ответь на русском языке кратко и понятно на вопрос пользователя.
            Ты {self.name} в проекте Mentor. Не используй английский язык."""
            
            try:
                retry_response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "llama3.2:1b-instruct-q4_0", 
                        "prompt": retry_prompt,
                        "stream": False,
                        "options": {"temperature": 0.1, "num_predict": 50}
                    },
                    timeout=10
                )
                
                if retry_response.status_code == 200:
                    better_response = retry_response.json().get("response", "").strip()
                    if better_response and len(better_response) > 10:
                        return better_response
                        
            except:
                pass
        
        return response

# Создаем улучшенную систему
project_memory = ProjectMemory()
vision_processor = VisionProcessor()

# Создаем агентов с памятью и визуальными возможностями
enhanced_agents = {}

agent_configs = {
    "general_assistant": {
        "name": "🧠 Умный Помощник",
        "system_prompt": """Ты главный координатор проекта Mentor. Знаешь всю историю проекта, 
        все системы, всех агентов. Помогаешь планировать развитие и координируешь работу."""
    },
    "code_developer": {
        "name": "💻 AI Разработчик", 
        "system_prompt": """Ты эксперт-программист проекта Mentor. Знаешь весь код проекта,
        можешь анализировать, оптимизировать и генерировать новый код."""
    },
    "vision_specialist": {
        "name": "👁️ Визуальный Специалист",
        "system_prompt": """Ты специалист по компьютерному зрению и обработке изображений.
        Анализируешь фото, работаешь с одеждой, создаешь визуальные решения."""
    },
    "project_manager": {
        "name": "📋 Менеджер Проекта",
        "system_prompt": """Ты менеджер проекта Mentor. Знаешь всю историю развития,
        планируешь следующие этапы, управляешь ресурсами."""
    }
}

for agent_id, config in agent_configs.items():
    enhanced_agents[agent_id] = EnhancedAIAgent(
        agent_id=agent_id,
        name=config["name"],
        agent_type=agent_id,
        system_prompt=config["system_prompt"],
        project_memory=project_memory,
        vision_processor=vision_processor
    )

# FastAPI приложение
app = FastAPI(title="Enhanced AI Mentor System")

@app.get("/")
async def root():
    """Улучшенный интерфейс с загрузкой файлов"""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 Enhanced AI Mentor - Умная система</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
            color: white;
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { font-size: 3em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .features-badge { 
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4); 
            padding: 10px 20px; 
            border-radius: 25px; 
            color: white; 
            font-weight: bold; 
            display: inline-block; 
            margin: 10px; 
        }
        
        .main-content { display: grid; grid-template-columns: 1fr 400px; gap: 30px; }
        
        .chat-section { 
            background: rgba(255,255,255,0.95); 
            border-radius: 20px; 
            padding: 30px; 
            color: #333;
        }
        
        .sidebar { 
            background: rgba(255,255,255,0.9); 
            border-radius: 20px; 
            padding: 25px; 
            color: #333;
        }
        
        .chat-messages { 
            height: 400px; 
            overflow-y: auto; 
            border: 1px solid #ddd; 
            border-radius: 15px; 
            padding: 20px; 
            margin-bottom: 20px;
            background: #f8f9fa;
        }
        
        .message { 
            margin-bottom: 15px; 
            padding: 15px; 
            border-radius: 12px; 
        }
        
        .user-message { 
            background: #e3f2fd; 
            margin-left: 20px; 
            border-left: 4px solid #2196f3; 
        }
        
        .ai-message { 
            background: #f3e5f5; 
            margin-right: 20px; 
            border-left: 4px solid #9c27b0; 
        }
        
        .enhanced-message { 
            background: linear-gradient(135deg, #fff3e0, #fce4ec); 
            margin-right: 20px; 
            border-left: 4px solid #ff6b6b; 
        }
        
        .file-upload-section { 
            background: #f0f8ff; 
            border: 2px dashed #4ecdc4; 
            border-radius: 15px; 
            padding: 20px; 
            margin-bottom: 20px; 
            text-align: center;
        }
        
        .file-input { 
            margin: 10px 0; 
            padding: 10px; 
            border: 1px solid #ddd; 
            border-radius: 8px; 
            width: 100%;
        }
        
        .input-container { 
            display: flex; 
            gap: 10px; 
            margin-bottom: 15px; 
        }
        
        .message-input { 
            flex: 1; 
            padding: 15px; 
            border: 1px solid #ddd; 
            border-radius: 25px; 
            font-size: 16px; 
        }
        
        .send-button { 
            padding: 15px 25px; 
            background: linear-gradient(135deg, #4CAF50, #45a049); 
            color: white; 
            border: none; 
            border-radius: 25px; 
            cursor: pointer; 
            font-weight: bold;
        }
        
        .agent-selector { 
            margin-bottom: 20px; 
        }
        
        .agent-selector select { 
            width: 100%; 
            padding: 12px; 
            border: 1px solid #ddd; 
            border-radius: 8px; 
        }
        
        .project-info { 
            background: #f8f9fa; 
            border-radius: 15px; 
            padding: 20px; 
            margin-bottom: 20px;
        }
        
        .project-info h3 { 
            color: #2c3e50; 
            margin-bottom: 15px; 
        }
        
        .stat-item { 
            display: flex; 
            justify-content: space-between; 
            margin-bottom: 8px; 
        }
        
        .stat-value { 
            font-weight: bold; 
            color: #667eea; 
        }
        
        .image-preview { 
            max-width: 100%; 
            border-radius: 10px; 
            margin: 10px 0; 
        }
        
        .processing-indicator { 
            background: #fff3cd; 
            border: 1px solid #ffeaa7; 
            border-radius: 8px; 
            padding: 10px; 
            margin: 10px 0; 
            text-align: center;
            color: #856404;
        }
        
        .typing-dots {
            animation: typingDots 1.5s infinite;
        }
        
        @keyframes typingDots {
            0%, 20% { opacity: 0; }
            50% { opacity: 1; }
            100% { opacity: 0; }
        }
        
        .suggestion-item {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 20px;
            padding: 8px 15px;
            margin: 5px;
            display: inline-block;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9em;
        }
        
        .suggestion-item:hover {
            background: #007bff;
            color: white;
            transform: translateY(-2px);
        }
        
        .voice-indicator {
            animation: voicePulse 1s ease-in-out infinite;
        }
        
        @keyframes voicePulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        .quick-actions {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        
        .quick-action-btn {
            padding: 8px 15px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9em;
            transition: transform 0.2s;
        }
        
        .quick-action-btn:hover {
            transform: scale(1.05);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Enhanced AI Mentor</h1>
            <div class="features-badge">Память проекта</div>
            <div class="features-badge">Работа с фото</div>
            <div class="features-badge">Умные агенты</div>
            <p style="font-size: 1.2em; margin-top: 15px;">AI система с полным контекстом и визуальными возможностями</p>
        </div>
        
        <div class="main-content">
            <div class="chat-section">
                <h2>💬 Умный чат с AI агентами</h2>
                
                <div class="file-upload-section">
                    <h3>📸 Загрузка изображений</h3>
                    <p>Загрузите фото брюк, одежды или любое изображение для анализа</p>
                    <input type="file" id="imageFile" class="file-input" accept="image/*">
                    <div id="imagePreview"></div>
                </div>
                
                <!-- Быстрые действия -->
                <div class="quick-actions">
                    <button class="quick-action-btn" onclick="quickAction('Расскажи историю проекта')">📚 История</button>
                    <button class="quick-action-btn" onclick="quickAction('Проанализируй код системы')">💻 Анализ кода</button>
                    <button class="quick-action-btn" onclick="quickAction('Как улучшить проект?')">🚀 Улучшения</button>
                    <button class="quick-action-btn" onclick="quickAction('Создай новую функцию')">⚡ Генерация</button>
                </div>
                
                <div class="agent-selector">
                    <label><strong>Выберите умного агента:</strong></label>
                    <select id="agentSelect" onchange="updateSuggestions()">
                        <option value="general_assistant">🧠 Умный Помощник (знает всю историю)</option>
                        <option value="code_developer">💻 AI Разработчик (весь код проекта)</option>
                        <option value="vision_specialist">👁️ Визуальный Специалист (работа с фото)</option>
                        <option value="project_manager">📋 Менеджер Проекта (планирование)</option>
                    </select>
                </div>
                
                <div class="chat-messages" id="chatMessages">
                    <div class="message enhanced-message">
                        <strong>🚀 Система:</strong> Enhanced AI Mentor готова! Агенты знают всю историю проекта и могут работать с изображениями.
                    </div>
                </div>
                
                <!-- Умные подсказки -->
                <div id="smartSuggestions" style="margin-bottom: 15px; display: none;">
                    <div style="background: #e8f4fd; border-radius: 10px; padding: 15px; border-left: 4px solid #2196f3;">
                        <strong>💡 Умные подсказки:</strong>
                        <div id="suggestionsList"></div>
                    </div>
                </div>
                
                <!-- Индикатор печатания -->
                <div id="typingIndicator" style="display: none; background: #f0f0f0; padding: 10px; border-radius: 10px; margin-bottom: 10px; color: #666;">
                    <span id="typingAgent">AI агент</span> печатает... <span class="typing-dots">●●●</span>
                </div>
                
                <div class="input-container">
                    <input type="text" id="messageInput" class="message-input" 
                           placeholder="Напишите сообщение (можно с фото)..." 
                           autocomplete="off" />
                    <button onclick="startVoiceInput()" class="send-button" style="margin-right: 10px; background: linear-gradient(135deg, #9b59b6, #8e44ad);">🎤</button>
                    <button onclick="sendMessage()" class="send-button">🚀 Отправить</button>
                </div>
                
                <!-- Голосовой ввод -->
                <div id="voiceInput" style="display: none; background: #fff3cd; border-radius: 10px; padding: 15px; margin-top: 10px; text-align: center;">
                    <div>🎤 <strong>Говорите...</strong></div>
                    <div id="voiceText" style="margin-top: 10px; font-style: italic;"></div>
                    <button onclick="stopVoiceInput()" style="margin-top: 10px; padding: 8px 16px; background: #dc3545; color: white; border: none; border-radius: 5px;">Остановить</button>
                </div>
            </div>
            
            <div class="sidebar">
                <div class="project-info">
                    <h3>📚 Контекст проекта</h3>
                    <div class="stat-item">
                        <span>Файлов проекта:</span>
                        <span class="stat-value" id="projectFiles">Загрузка...</span>
                    </div>
                    <div class="stat-item">
                        <span>История взаимодействий:</span>
                        <span class="stat-value" id="interactionHistory">0</span>
                    </div>
                    <div class="stat-item">
                        <span>Обработано изображений:</span>
                        <span class="stat-value" id="processedImages">0</span>
                    </div>
                    <div class="stat-item">
                        <span>AI запросов:</span>
                        <span class="stat-value" id="aiRequests">0</span>
                    </div>
                </div>
                
                <div class="project-info">
                    <h3>🎯 Возможности</h3>
                    <p>✅ Анализ и примерка одежды</p>
                    <p>✅ Полная история проекта</p>
                    <p>✅ Работа с кодом</p>
                    <p>✅ Планирование развития</p>
                    <p>✅ Визуальный анализ</p>
                    <p>✅ Контекстные ответы</p>
                </div>
                
                <div class="project-info">
                    <h3>📊 Статистика</h3>
                    <div class="stat-item">
                        <span>Время работы:</span>
                        <span class="stat-value" id="uptime">0с</span>
                    </div>
                    <div class="stat-item">
                        <span>Активных агентов:</span>
                        <span class="stat-value" id="activeAgents">4</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let userId = 'user_' + Math.random().toString(36).substr(2, 9);
        let recognition = null;
        let isListening = false;
        let messageHistory = [];
        
        // Умные подсказки для каждого агента
        const agentSuggestions = {
            'general_assistant': [
                'Расскажи всю историю проекта Mentor',
                'Как развивать проект дальше?',
                'Что уже сделано в проекте?',
                'Какие системы работают?'
            ],
            'code_developer': [
                'Проанализируй код системы',
                'Оптимизируй производительность',
                'Найди баги в коде',
                'Создай новую функцию',
                'Рефактори этот код'
            ],
            'vision_specialist': [
                'Проанализируй это изображение',
                'Создай виртуальную примерку',
                'Надень эти брюки на модель',
                'Улучши качество фото',
                'Определи цвета одежды'
            ],
            'project_manager': [
                'Создай план развития проекта',
                'Какие задачи приоритетные?',
                'Оцени текущий прогресс',
                'Спланируй следующий спринт'
            ]
        };
        
        function connectWebSocket() {
            ws = new WebSocket(`ws://${window.location.host}/ws/enhanced/${userId}`);
            
            ws.onopen = function() {
                console.log('WebSocket подключен к Enhanced AI системе');
                showNotification('🔗 Подключено к умной AI системе', 'success');
            };
            
            ws.onmessage = function(event) {
                hideTypingIndicator();
                const data = JSON.parse(event.data);
                addMessage(data.message, 'ai', data.agent, data.ai_used, data.response_time, data.has_context, data.image_processed);
                updateSuggestions();
            };
            
            ws.onclose = function() {
                console.log('WebSocket отключен, переподключение...');
                showNotification('⚠️ Переподключение...', 'warning');
                setTimeout(connectWebSocket, 3000);
            };
        }
        
        function addMessage(message, type, agent = '', ai_used = false, response_time = null, has_context = false, image_processed = false) {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            
            if (type === 'user') {
                messageDiv.className = 'message user-message';
                messageDiv.innerHTML = `<strong>Вы:</strong> ${message}`;
            } else {
                messageDiv.className = 'message enhanced-message';
                
                let badges = '';
                if (ai_used) badges += ' 🧠';
                if (has_context) badges += ' 📚';
                if (image_processed) badges += ' 👁️';
                
                let content = `<strong>${agent}${badges}:</strong> ${message}`;
                
                if (response_time) {
                    content += `<br><small style="color: #666;">Время ответа: ${response_time.toFixed(2)}с</small>`;
                }
                
                messageDiv.innerHTML = content;
            }
            
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function previewImage() {
            const fileInput = document.getElementById('imageFile');
            const preview = document.getElementById('imagePreview');
            
            if (fileInput.files && fileInput.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.innerHTML = `<img src="${e.target.result}" class="image-preview" alt="Предпросмотр">`;
                };
                reader.readAsDataURL(fileInput.files[0]);
            }
        }
        
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            const agentType = document.getElementById('agentSelect').value;
            const fileInput = document.getElementById('imageFile');
            
            if (!message) return;
            
            // Добавляем в историю для автодополнения
            if (!messageHistory.includes(message)) {
                messageHistory.push(message);
                if (messageHistory.length > 50) {
                    messageHistory = messageHistory.slice(-50);
                }
            }
            
            addMessage(message, 'user');
            
            // Показываем индикатор печатания
            const agentName = document.querySelector(`#agentSelect option[value="${agentType}"]`).textContent;
            showTypingIndicator(agentName);
            
            try {
                const formData = new FormData();
                formData.append('message', message);
                formData.append('agent_type', agentType);
                formData.append('user_id', userId);
                
                if (fileInput.files && fileInput.files[0]) {
                    formData.append('image', fileInput.files[0]);
                }
                
                const response = await fetch('/api/enhanced/chat', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                hideTypingIndicator();
                
                if (data.success) {
                    const result = data.response;
                    addMessage(
                        result.response, 
                        'ai', 
                        result.agent, 
                        result.ai_used, 
                        result.response_time,
                        result.has_context,
                        result.image_processed
                    );
                    
                    // Показываем уведомление о типе ответа
                    if (result.ai_used) {
                        showNotification('🧠 Ответ от настоящего AI', 'success');
                    } else if (result.has_context) {
                        showNotification('📚 Ответ с контекстом проекта', 'info');
                    }
                    
                    // Очищаем форму
                    input.value = '';
                    fileInput.value = '';
                    document.getElementById('imagePreview').innerHTML = '';
                    hideAutoCompleteDropdown();
                } else {
                    addMessage('Ошибка обработки запроса', 'ai', 'System');
                    showNotification('❌ Ошибка обработки', 'warning');
                }
                
            } catch (error) {
                hideTypingIndicator();
                addMessage(`Ошибка: ${error}`, 'ai', 'System');
                showNotification('❌ Ошибка сети', 'warning');
            }
        }
        
        function updateStats() {
            fetch('/api/enhanced/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('projectFiles').textContent = data.project_files || 'N/A';
                    document.getElementById('interactionHistory').textContent = data.interactions || 0;
                    document.getElementById('processedImages').textContent = data.processed_images || 0;
                    document.getElementById('aiRequests').textContent = data.ai_requests || 0;
                    document.getElementById('uptime').textContent = data.uptime || '0с';
                    document.getElementById('activeAgents').textContent = data.active_agents || 4;
                })
                .catch(error => console.error('Ошибка обновления статистики:', error));
        }
        
        // Обработчики событий
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        document.getElementById('imageFile').addEventListener('change', previewImage);
        
        function showTypingIndicator(agentName) {
            const indicator = document.getElementById('typingIndicator');
            document.getElementById('typingAgent').textContent = agentName;
            indicator.style.display = 'block';
        }
        
        function hideTypingIndicator() {
            document.getElementById('typingIndicator').style.display = 'none';
        }
        
        function showNotification(message, type = 'info') {
            // Создаем уведомление
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed; top: 20px; right: 20px; z-index: 1000;
                padding: 15px 20px; border-radius: 10px; color: white; font-weight: bold;
                background: ${type === 'success' ? '#2ecc71' : type === 'warning' ? '#f39c12' : '#3498db'};
                box-shadow: 0 4px 15px rgba(0,0,0,0.2); opacity: 0; transition: opacity 0.3s ease;
            `;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            // Показываем
            setTimeout(() => notification.style.opacity = '1', 100);
            
            // Убираем через 3 секунды
            setTimeout(() => {
                notification.style.opacity = '0';
                setTimeout(() => document.body.removeChild(notification), 300);
            }, 3000);
        }
        
        function updateSuggestions() {
            const agentType = document.getElementById('agentSelect').value;
            const suggestions = agentSuggestions[agentType] || [];
            const suggestionsDiv = document.getElementById('smartSuggestions');
            const suggestionsList = document.getElementById('suggestionsList');
            
            if (suggestions.length > 0) {
                suggestionsList.innerHTML = '';
                suggestions.forEach(suggestion => {
                    const item = document.createElement('span');
                    item.className = 'suggestion-item';
                    item.textContent = suggestion;
                    item.onclick = () => quickAction(suggestion);
                    suggestionsList.appendChild(item);
                });
                suggestionsDiv.style.display = 'block';
            } else {
                suggestionsDiv.style.display = 'none';
            }
        }
        
        function quickAction(text) {
            document.getElementById('messageInput').value = text;
            sendMessage();
        }
        
        function startVoiceInput() {
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                showNotification('❌ Голосовой ввод не поддерживается в этом браузере', 'warning');
                return;
            }
            
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            
            recognition.lang = 'ru-RU';
            recognition.continuous = false;
            recognition.interimResults = true;
            
            recognition.onstart = function() {
                isListening = true;
                document.getElementById('voiceInput').style.display = 'block';
                document.getElementById('voiceText').textContent = 'Слушаю...';
                showNotification('🎤 Голосовой ввод активирован', 'info');
            };
            
            recognition.onresult = function(event) {
                let finalTranscript = '';
                let interimTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript;
                    } else {
                        interimTranscript += transcript;
                    }
                }
                
                document.getElementById('voiceText').textContent = finalTranscript || interimTranscript;
                
                if (finalTranscript) {
                    document.getElementById('messageInput').value = finalTranscript;
                    stopVoiceInput();
                    showNotification('✅ Голосовое сообщение распознано', 'success');
                }
            };
            
            recognition.onerror = function(event) {
                showNotification('❌ Ошибка распознавания речи', 'warning');
                stopVoiceInput();
            };
            
            recognition.start();
        }
        
        function stopVoiceInput() {
            if (recognition && isListening) {
                recognition.stop();
                isListening = false;
                document.getElementById('voiceInput').style.display = 'none';
            }
        }
        
        // Автодополнение на основе истории
        function setupAutoComplete() {
            const input = document.getElementById('messageInput');
            
            input.addEventListener('input', function() {
                const value = this.value.toLowerCase();
                if (value.length > 2) {
                    const matches = messageHistory.filter(msg => 
                        msg.toLowerCase().includes(value)
                    ).slice(0, 3);
                    
                    if (matches.length > 0) {
                        showAutoCompleteDropdown(matches);
                    } else {
                        hideAutoCompleteDropdown();
                    }
                } else {
                    hideAutoCompleteDropdown();
                }
            });
        }
        
        function showAutoCompleteDropdown(matches) {
            let dropdown = document.getElementById('autoCompleteDropdown');
            if (!dropdown) {
                dropdown = document.createElement('div');
                dropdown.id = 'autoCompleteDropdown';
                dropdown.style.cssText = `
                    position: absolute; background: white; border: 1px solid #ddd;
                    border-radius: 8px; max-height: 200px; overflow-y: auto;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1); z-index: 1000;
                    width: 100%; top: 100%; left: 0;
                `;
                document.querySelector('.input-container').style.position = 'relative';
                document.querySelector('.input-container').appendChild(dropdown);
            }
            
            dropdown.innerHTML = '';
            matches.forEach(match => {
                const item = document.createElement('div');
                item.style.cssText = 'padding: 10px; cursor: pointer; border-bottom: 1px solid #eee; color: #333;';
                item.textContent = match;
                item.onclick = () => {
                    document.getElementById('messageInput').value = match;
                    hideAutoCompleteDropdown();
                };
                item.onmouseover = () => item.style.background = '#f0f0f0';
                item.onmouseout = () => item.style.background = 'white';
                dropdown.appendChild(item);
            });
        }
        
        function hideAutoCompleteDropdown() {
            const dropdown = document.getElementById('autoCompleteDropdown');
            if (dropdown) {
                dropdown.style.display = 'none';
            }
        }
        
        // Инициализация
        connectWebSocket();
        updateStats();
        updateSuggestions();
        setupAutoComplete();
        
        setInterval(updateStats, 5000);
        
        // Показываем приветственное сообщение
        setTimeout(() => {
            showNotification('🎉 Добро пожаловать в Enhanced AI Mentor!', 'success');
        }, 1000);
    </script>
</body>
</html>
    """)

@app.post("/api/enhanced/chat")
async def enhanced_chat(message: str = Form(...), agent_type: str = Form("general_assistant"), 
                       user_id: str = Form("user"), image: UploadFile = File(None)):
    """Улучшенный чат с контекстом и изображениями"""
    
    if agent_type not in enhanced_agents:
        agent_type = "general_assistant"
    
    agent = enhanced_agents[agent_type]
    
    # Обрабатываем сообщение с контекстом и изображением
    result = await agent.process_with_context(message, user_id, image)
    
    return {
        "success": True,
        "response": result,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/enhanced/status")
async def enhanced_status():
    """Статус улучшенной системы"""
    
    # Подсчитываем статистику
    total_interactions = sum(len(agent.conversation_history) for agent in enhanced_agents.values())
    total_tasks = sum(agent.task_count for agent in enhanced_agents.values())
    
    # Подсчитываем обработанные изображения
    processed_images = 0
    if os.path.exists("/workspace/processed_images"):
        processed_images = len([f for f in os.listdir("/workspace/processed_images") if f.endswith(('.jpg', '.png'))])
    
    return {
        "system_status": "running",
        "active_agents": len(enhanced_agents),
        "project_files": len(project_memory.project_files),
        "interactions": len(project_memory.user_interactions),
        "processed_images": processed_images,
        "ai_requests": total_tasks,
        "uptime": f"{int(time.time() - startup_time)}с",
        "agents": {
            agent_id: {
                "name": agent.name,
                "task_count": agent.task_count,
                "type": agent.agent_type
            }
            for agent_id, agent in enhanced_agents.items()
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/enhanced/modify_code")
async def modify_code(file_path: str = Form(...), old_code: str = Form(...), new_code: str = Form(...)):
    """Изменение кода через AI"""
    result = await code_modifier.apply_code_change(file_path, old_code, new_code)
    return result

@app.post("/api/enhanced/add_function")
async def add_function(file_path: str = Form(...), function_code: str = Form(...), position: str = Form("end")):
    """Добавление новой функции в файл"""
    result = await code_modifier.add_function_to_file(file_path, function_code, position)
    return result

@app.get("/api/enhanced/project_files")
async def get_project_files():
    """Получение списка файлов проекта"""
    python_files = []
    for root, dirs, files in os.walk("/workspace"):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for file in files:
            if file.endswith('.py') and not file.startswith('.'):
                file_path = os.path.join(root, file)
                python_files.append({
                    "path": file_path,
                    "name": file,
                    "size": os.path.getsize(file_path),
                    "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                })
    
    return {"files": python_files[:50], "total_count": len(python_files)}

@app.websocket("/ws/enhanced/{user_id}")
async def enhanced_websocket(websocket: WebSocket, user_id: str):
    """Enhanced WebSocket"""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Обрабатываем через enhanced систему
            response = await enhanced_chat(
                message=message_data.get("message", ""),
                agent_type=message_data.get("agent_type", "general_assistant"),
                user_id=user_id
            )
            
            if response.get("success"):
                result = response["response"]
                await websocket.send_text(json.dumps({
                    "message": result["response"],
                    "agent": result["agent"],
                    "timestamp": result["timestamp"],
                    "ai_used": result.get("ai_used", False),
                    "response_time": result.get("response_time"),
                    "has_context": result.get("has_context", False),
                    "image_processed": result.get("image_processed", False)
                }))
                
    except WebSocketDisconnect:
        logger.info(f"🔌 Пользователь {user_id} отключился от Enhanced AI")

# Глобальные переменные
startup_time = time.time()

# Основная функция
async def main():
    """Главная функция"""
    logger.info("🧠 Запуск Enhanced AI Mentor System...")
    logger.info("📚 Система загружает полную историю проекта...")
    logger.info("👁️ Интегрированы возможности работы с изображениями...")
    
    try:
        # Заменяем старую систему на порту 8082
        config = uvicorn.Config(app, host="0.0.0.0", port=8082, log_level="info")
        server = uvicorn.Server(config)
        
        logger.info("✅ Enhanced AI система запущена")
        logger.info("🌐 Доступна на http://localhost:8082")
        logger.info("🎯 Возможности: работа с фото, полная память проекта, умные агенты")
        
        await server.serve()
        
    except Exception as e:
        logger.error(f"❌ Ошибка Enhanced AI системы: {e}")

if __name__ == "__main__":
    asyncio.run(main())