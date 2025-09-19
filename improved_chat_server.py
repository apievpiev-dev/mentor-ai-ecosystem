#!/usr/bin/env python3
"""
Улучшенный веб-сервер для Multi-AI системы
Использует улучшенную интегрированную систему
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os

from improved_integrated_system import get_improved_integrated_system

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/mentor/improved_chat_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Модели данных
class ChatMessage(BaseModel):
    message: str
    user_id: str = "user"
    agent_type: Optional[str] = None

class SystemStats:
    def __init__(self):
        self.active_users = 0
        self.total_messages = 0
        self.start_time = time.time()

# Глобальные переменные
app = FastAPI(title="Improved Multi-AI Chat System", version="2.0.0")
system_stats = SystemStats()
integrated_system = None
connected_clients = set()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_uptime():
    """Получение времени работы"""
    uptime_seconds = int(time.time() - system_stats.start_time)
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    global integrated_system
    try:
        logger.info("🚀 Запуск улучшенного веб-сервера...")
        integrated_system = get_improved_integrated_system()
        
        # Запускаем интегрированную систему
        if await integrated_system.start():
            logger.info("✅ Улучшенная интегрированная система запущена")
        else:
            logger.error("❌ Не удалось запустить улучшенную интегрированную систему")
            
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при завершении"""
    global integrated_system
    try:
        logger.info("🛑 Остановка улучшенного веб-сервера...")
        if integrated_system:
            await integrated_system.stop()
        logger.info("✅ Улучшенный веб-сервер остановлен")
    except Exception as e:
        logger.error(f"❌ Ошибка остановки: {e}")

@app.get("/")
async def root():
    """Главная страница"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Improved Multi-AI Chat System</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            .header h1 {
                margin: 0;
                font-size: 2.5em;
                font-weight: 300;
            }
            .header p {
                margin: 10px 0 0 0;
                opacity: 0.9;
                font-size: 1.1em;
            }
            .chat-container {
                display: flex;
                height: 600px;
            }
            .chat-messages {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
                border-right: 1px solid #eee;
            }
            .chat-sidebar {
                width: 300px;
                padding: 20px;
                background: #f8f9fa;
            }
            .message {
                margin: 15px 0;
                padding: 15px;
                border-radius: 10px;
                max-width: 80%;
            }
            .user-message {
                background: #667eea;
                color: white;
                margin-left: auto;
            }
            .agent-message {
                background: #f1f3f4;
                color: #333;
            }
            .input-container {
                padding: 20px;
                border-top: 1px solid #eee;
                display: flex;
                gap: 10px;
            }
            .message-input {
                flex: 1;
                padding: 15px;
                border: 2px solid #ddd;
                border-radius: 25px;
                font-size: 16px;
                outline: none;
                transition: border-color 0.3s;
            }
            .message-input:focus {
                border-color: #667eea;
            }
            .send-button {
                padding: 15px 30px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                transition: background 0.3s;
            }
            .send-button:hover {
                background: #5a6fd8;
            }
            .agent-selector {
                margin-bottom: 20px;
            }
            .agent-selector select {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
            .status-indicator {
                display: inline-block;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                margin-right: 8px;
            }
            .status-online {
                background: #4CAF50;
            }
            .status-offline {
                background: #f44336;
            }
            .system-info {
                background: #e3f2fd;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            .system-info h3 {
                margin: 0 0 10px 0;
                color: #1976d2;
            }
            .system-info p {
                margin: 5px 0;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Improved Multi-AI Chat System</h1>
                <p>Интеллектуальная система с автономными агентами</p>
            </div>
            
            <div class="chat-container">
                <div class="chat-messages" id="chatMessages">
                    <div class="message agent-message">
                        <strong>Система:</strong> Добро пожаловать в улучшенную Multi-AI систему! Агенты готовы к работе.
                    </div>
                </div>
                
                <div class="chat-sidebar">
                    <div class="system-info">
                        <h3>📊 Статус системы</h3>
                        <p><span class="status-indicator status-online"></span>Система: <span id="systemStatus">Загрузка...</span></p>
                        <p>Агентов: <span id="totalAgents">0</span></p>
                        <p>Активных: <span id="activeAgents">0</span></p>
                        <p>Время работы: <span id="uptime">0м</span></p>
                    </div>
                    
                    <div class="agent-selector">
                        <label for="agentSelect"><strong>Выберите агента:</strong></label>
                        <select id="agentSelect">
                            <option value="">Автоматический выбор</option>
                            <option value="general_assistant">Универсальный Помощник</option>
                            <option value="code_developer">Разработчик Кода</option>
                            <option value="data_analyst">Аналитик Данных</option>
                            <option value="project_manager">Менеджер Проектов</option>
                            <option value="designer">Дизайнер</option>
                            <option value="qa_tester">Тестировщик</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <div class="input-container">
                <input type="text" id="messageInput" class="message-input" placeholder="Введите ваше сообщение..." />
                <button onclick="sendMessage()" class="send-button">Отправить</button>
            </div>
        </div>

        <script>
            const ws = new WebSocket(`ws://${window.location.host}/ws`);
            const chatMessages = document.getElementById('chatMessages');
            const messageInput = document.getElementById('messageInput');
            const agentSelect = document.getElementById('agentSelect');

            ws.onopen = function(event) {
                console.log('WebSocket соединение установлено');
            };

            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                if (data.type === 'message') {
                    addMessage(data.message, data.agent || 'Система', data.isUser);
                } else if (data.type === 'status') {
                    updateSystemStatus(data.status);
                }
            };

            ws.onclose = function(event) {
                console.log('WebSocket соединение закрыто');
            };

            function addMessage(message, agent, isUser) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user-message' : 'agent-message'}`;
                messageDiv.innerHTML = `<strong>${agent}:</strong> ${message}`;
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }

            function updateSystemStatus(status) {
                document.getElementById('systemStatus').textContent = status.system_status === 'running' ? 'Работает' : 'Остановлена';
                document.getElementById('totalAgents').textContent = status.total_agents || 0;
                document.getElementById('activeAgents').textContent = status.active_agents || 0;
                document.getElementById('uptime').textContent = status.uptime || '0м';
            }

            function sendMessage() {
                const message = messageInput.value.trim();
                const agentType = agentSelect.value;
                
                if (message) {
                    addMessage(message, 'Вы', true);
                    
                    fetch('/api/chat/send', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: message,
                            agent_type: agentType || null,
                            user_id: 'web_user'
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            addMessage(data.response.response, data.agent, false);
                        } else {
                            addMessage('Ошибка: ' + (data.error || 'Неизвестная ошибка'), 'Система', false);
                        }
                    })
                    .catch(error => {
                        addMessage('Ошибка соединения: ' + error.message, 'Система', false);
                    });
                    
                    messageInput.value = '';
                }
            }

            messageInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });

            // Обновляем статус системы каждые 5 секунд
            setInterval(() => {
                fetch('/api/system/status')
                    .then(response => response.json())
                    .then(data => updateSystemStatus(data))
                    .catch(error => console.error('Ошибка получения статуса:', error));
            }, 5000);
        </script>
    </body>
    </html>
    """)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket соединение"""
    await websocket.accept()
    connected_clients.add(websocket)
    system_stats.active_users = len(connected_clients)
    
    try:
        while True:
            # Отправляем статус системы
            if integrated_system:
                status = integrated_system.get_system_status()
                await websocket.send_json({
                    "type": "status",
                    "status": status
                })
            
            await asyncio.sleep(5)  # Обновляем каждые 5 секунд
            
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        system_stats.active_users = len(connected_clients)

@app.post("/api/chat/send")
async def send_chat_message(message: ChatMessage):
    """Отправка сообщения агенту"""
    try:
        if not integrated_system:
            raise HTTPException(status_code=503, detail="System not initialized")
        
        if not integrated_system.running:
            raise HTTPException(status_code=503, detail="System not running")
        
        # Отправляем сообщение агенту
        result = integrated_system.send_message_to_agent(
            message=message.message,
            agent_type=message.agent_type,
            user_id=message.user_id
        )
        
        system_stats.total_messages += 1
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"❌ Ошибка отправки сообщения: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/status")
async def get_system_status():
    """Получить статус системы"""
    try:
        if not integrated_system:
            return JSONResponse(content={
                "system_status": "not_initialized",
                "error": "System not initialized"
            })
        
        status = integrated_system.get_system_status()
        status.update({
            "active_users": system_stats.active_users,
            "total_messages": system_stats.total_messages,
            "uptime": get_uptime()
        })
        
        return JSONResponse(content=status)
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения статуса системы: {e}")
        return JSONResponse(content={
            "system_status": "error",
            "error": str(e)
        })

@app.get("/api/agents")
async def get_agents():
    """Получить список агентов"""
    try:
        if not integrated_system:
            return JSONResponse(content={"error": "System not initialized"})
        
        agents = []
        for agent_type, agent in integrated_system.agents.items():
            agents.append({
                "id": agent.agent_id,
                "name": agent.name,
                "type": agent_type,
                "status": "active" if integrated_system.running else "inactive"
            })
        
        return JSONResponse(content={"agents": agents})
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения списка агентов: {e}")
        return JSONResponse(content={"error": str(e)})

@app.get("/api/health")
async def health_check():
    """Проверка здоровья системы"""
    try:
        if not integrated_system:
            return JSONResponse(content={"status": "unhealthy", "reason": "System not initialized"})
        
        if not integrated_system.running:
            return JSONResponse(content={"status": "unhealthy", "reason": "System not running"})
        
        return JSONResponse(content={"status": "healthy"})
        
    except Exception as e:
        logger.error(f"❌ Ошибка проверки здоровья: {e}")
        return JSONResponse(content={"status": "unhealthy", "reason": str(e)})

if __name__ == "__main__":
    uvicorn.run(
        "improved_chat_server:app",
        host="0.0.0.0",
        port=8081,
        reload=False,
        log_level="info"
    )

