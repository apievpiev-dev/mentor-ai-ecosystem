#!/usr/bin/env python3
"""
API для чата JARVIS
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
import time
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ChatMessage(BaseModel):
    message: str
    user_id: str = "anonymous"

class ChatAPI:
    def __init__(self, jarvis_core):
        self.jarvis = jarvis_core
        self.app = FastAPI(title="JARVIS Chat API")
        self.setup_endpoints()
    
    def setup_endpoints(self):
        @self.app.get("/")
        async def chat_interface():
            """Интерфейс чата"""
            try:
                with open("/home/mentor/jarvis_data/templates/chat.html", "r", encoding="utf-8") as f:
                    return HTMLResponse(f.read())
            except FileNotFoundError:
                return HTMLResponse("<h1>Чат временно недоступен</h1>")
        
        @self.app.post("/api/chat/send")
        async def send_message(message: ChatMessage):
            """Отправка сообщения в чат JARVIS"""
            try:
                if not message.message.strip():
                    raise HTTPException(status_code=400, detail="Сообщение не может быть пустым")
                
                # Создаем задачу для обработки сообщения
                from jarvis_core import Task
                
                task = Task(
                    id=f"chat_{int(time.time())}",
                    type="user_message",
                    parameters={
                        "message": message.message,
                        "user_id": message.user_id,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                self.jarvis.tasks_queue.append(task)
                
                # Ждем обработки (до 10 секунд)
                for _ in range(100):
                    if task.status == "completed":
                        break
                    await asyncio.sleep(0.1)
                
                if task.status == "completed":
                    return task.result
                else:
                    raise HTTPException(status_code=408, detail="Таймаут обработки сообщения")
                    
            except Exception as e:
                logger.error(f"❌ Ошибка отправки сообщения: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/chat/status")
        async def chat_status():
            """Статус чата"""
            try:
                return {
                    "chat_active": True,
                    "websocket_active": False,
                    "messages_processed": len([t for t in self.jarvis.completed_tasks if t.type == "user_message"]),
                    "pending_messages": len([t for t in self.jarvis.tasks_queue if t.type == "user_message"]),
                    "jarvis_status": self.jarvis.state.system_state if hasattr(self.jarvis, 'state') else "unknown"
                }
            except Exception as e:
                logger.error(f"❌ Ошибка получения статуса чата: {e}")
                return {
                    "chat_active": False,
                    "error": str(e)
                }
        
        @self.app.get("/api/chat/history")
        async def chat_history():
            """История сообщений"""
            try:
                history = []
                for task in self.jarvis.completed_tasks[-10:]:  # Последние 10 сообщений
                    if task.type == "user_message" and task.result:
                        history.append({
                            "timestamp": task.parameters.get("timestamp"),
                            "user_message": task.parameters.get("message"),
                            "jarvis_response": task.result.get("message", ""),
                            "user_id": task.parameters.get("user_id")
                        })
                return {"history": history}
            except Exception as e:
                logger.error(f"❌ Ошибка получения истории чата: {e}")
                return {"history": [], "error": str(e)}

# Функция для интеграции с JARVIS
def setup_chat_api(jarvis_core, port=8082):
    """Настройка API чата на отдельном порту"""
    chat_api = ChatAPI(jarvis_core)
    
    import uvicorn
    from threading import Thread
    
    def run_chat_api():
        uvicorn.run(chat_api.app, host="0.0.0.0", port=port, log_level="info")
    
    chat_thread = Thread(target=run_chat_api, daemon=True)
    chat_thread.start()
    
    logger.info(f"💬 Chat API запущен на порту {port}")
    return chat_api

if __name__ == "__main__":
    # Тестовый запуск
    import sys
    sys.path.append('/home/mentor')
    
    from jarvis_core import JarvisCore
    
    jarvis = JarvisCore()
    chat_api = setup_chat_api(jarvis, port=8082)
    
    # Держим программу запущенной
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Chat API остановлен")
