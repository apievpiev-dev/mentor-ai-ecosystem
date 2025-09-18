#!/usr/bin/env python3
"""
Простой чат для JARVIS
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

app = FastAPI(title="JARVIS Simple Chat")

# Простые ответы JARVIS
def get_jarvis_response(message: str) -> str:
    """Простой ответ JARVIS на основе ключевых слов"""
    message_lower = message.lower().strip()
    
    if any(word in message_lower for word in ["привет", "hello", "hi"]):
        return "Привет! Я JARVIS, автономная AI-система. Чем могу помочь?"
    
    elif any(word in message_lower for word in ["как дела", "как ты", "статус"]):
        return "У меня все отлично! Система работает стабильно, все модули активны."
    
    elif any(word in message_lower for word in ["что умеешь", "возможности", "помощь"]):
        return """Я JARVIS, автономная AI-система. Мои возможности:
- Анализ данных и генерация отчетов
- Самоулучшение и оптимизация  
- Анализ интерфейса и предложения улучшений
- Самовоспроизводство на других серверах
- Мониторинг производительности
- Интеллектуальный чат и помощь пользователю"""
    
    elif any(word in message_lower for word in ["анализ", "данные", "отчет"]):
        return "Запускаю анализ данных! Создаю отчет с метриками и рекомендациями."
    
    elif any(word in message_lower for word in ["самоулучшение", "оптимизация", "улучшить"]):
        return "Инициирую процесс самоулучшения! Анализирую производительность и оптимизирую код."
    
    elif any(word in message_lower for word in ["репликация", "копирование", "создать копию"]):
        return "Запускаю самовоспроизводство! Создаю копию системы на других серверах."
    
    elif any(word in message_lower for word in ["спасибо", "thanks", "благодарю"]):
        return "Пожалуйста! Всегда рад помочь. JARVIS всегда на связи!"
    
    elif any(word in message_lower for word in ["время", "дата", "который час"]):
        return f"Текущее время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
    
    elif any(word in message_lower for word in ["производительность", "мониторинг", "метрики"]):
        return "Проверяю производительность системы... Все показатели в норме!"
    
    else:
        return "Понял ваше сообщение! JARVIS всегда готов помочь. Можете спросить о статусе системы, запустить анализ данных, самоулучшение или любую другую задачу."

@app.get("/")
async def chat_interface():
    """Интерфейс чата"""
    html_content = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JARVIS Chat</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .chat-container {
            height: 400px;
            border: 2px solid #e0e0e0;
            border-radius: 15px;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
            margin-bottom: 20px;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px 15px;
            border-radius: 15px;
            max-width: 80%;
        }
        .user-message {
            background: #667eea;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .jarvis-message {
            background: #e9ecef;
            color: #2c3e50;
            margin-right: auto;
        }
        .input-container {
            display: flex;
            gap: 10px;
        }
        .message-input {
            flex: 1;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
        }
        .send-button {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }
        .send-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        .status {
            text-align: center;
            margin-top: 20px;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>JARVIS Chat</h1>
            <p>Интеллектуальный чат с AI-системой</p>
        </div>
        
        <div class="chat-container" id="chatContainer">
            <div class="message jarvis-message">
                Привет! Я JARVIS, автономная AI-система. Чем могу помочь?
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" class="message-input" id="messageInput" placeholder="Введите ваше сообщение..." onkeypress="handleKeyPress(event)">
            <button class="send-button" onclick="sendMessage()">Отправить</button>
        </div>
        
        <div class="status" id="status">
            Готов к общению
        </div>
    </div>

    <script>
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Добавляем сообщение пользователя
            addMessage(message, 'user');
            input.value = '';
            
            // Показываем статус загрузки
            document.getElementById('status').textContent = 'JARVIS печатает...';
            
            try {
                const response = await fetch('/api/chat/send', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: message,
                        user_id: 'web_user'
                    })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    addMessage('Ошибка: ' + data.error, 'jarvis');
                } else {
                    addMessage(data.message, 'jarvis');
                }
                
                document.getElementById('status').textContent = 'Готов к общению';
                
            } catch (error) {
                addMessage('Ошибка соединения: ' + error.message, 'jarvis');
                document.getElementById('status').textContent = 'Ошибка соединения';
            }
        }

        function addMessage(text, sender) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.textContent = text;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(html_content)

@app.post("/api/chat/send")
async def send_message(message: ChatMessage):
    """Отправка сообщения в чат JARVIS"""
    try:
        if not message.message.strip():
            raise HTTPException(status_code=400, detail="Сообщение не может быть пустым")
        
        # Получаем ответ от JARVIS
        response = get_jarvis_response(message.message)
        
        return {
            "message": response,
            "timestamp": datetime.now().isoformat(),
            "user_id": message.user_id,
            "original_message": message.message
        }
                    
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/status")
async def chat_status():
    """Статус чата"""
    return {
        "chat_active": True,
        "websocket_active": False,
        "messages_processed": 0,
        "pending_messages": 0,
        "jarvis_status": "active"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)
