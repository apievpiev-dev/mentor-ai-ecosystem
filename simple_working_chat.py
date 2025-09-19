#!/usr/bin/env python3
"""
Простая рабочая система чата без AI
Быстрые ответы, стабильная работа
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Simple Working Chat")

# Простые агенты без AI
class SimpleAgent:
    def __init__(self, name: str, agent_type: str, skills: List[str]):
        self.name = name
        self.agent_type = agent_type
        self.skills = skills
        self.is_active = True
        self.status = "active"
        self.message_count = 0
        
    def get_response(self, message: str) -> str:
        """Быстрый ответ без AI"""
        self.message_count += 1
        
        if self.agent_type == "general_assistant":
            return f"Привет! Я {self.name}. Получил ваше сообщение: '{message}'. Как я могу помочь?"
        
        elif self.agent_type == "code_developer":
            return f"Я {self.name}, разработчик кода. По поводу '{message}' - могу помочь с программированием на Python, JavaScript, созданием функций и алгоритмов."
        
        elif self.agent_type == "data_analyst":
            return f"Я {self.name}, аналитик данных. По поводу '{message}' - могу помочь с анализом данных, статистикой, визуализацией."
        
        elif self.agent_type == "project_manager":
            return f"Я {self.name}, менеджер проектов. По поводу '{message}' - могу помочь с планированием, управлением задачами, координацией."
        
        elif self.agent_type == "designer":
            return f"Я {self.name}, дизайнер. По поводу '{message}' - могу помочь с UI/UX дизайном, созданием интерфейсов."
        
        elif self.agent_type == "qa_tester":
            return f"Я {self.name}, тестировщик. По поводу '{message}' - могу помочь с тестированием, поиском багов, качеством."
        
        else:
            return f"Я {self.name}. Получил: '{message}'. Готов помочь!"

# Создаем простых агентов
agents = {
    "general_assistant": SimpleAgent("Универсальный Помощник", "general_assistant", ["general_help", "planning"]),
    "code_developer": SimpleAgent("Разработчик Кода", "code_developer", ["programming", "algorithms"]),
    "data_analyst": SimpleAgent("Аналитик Данных", "data_analyst", ["data_analysis", "statistics"]),
    "project_manager": SimpleAgent("Менеджер Проектов", "project_manager", ["project_planning", "management"]),
    "designer": SimpleAgent("Дизайнер", "designer", ["ui_design", "ux_design"]),
    "qa_tester": SimpleAgent("Тестировщик", "qa_tester", ["testing", "quality_assurance"])
}

# Глобальные переменные
system_running = True
startup_time = time.time()
active_connections = set()

@app.get("/")
async def root():
    """Главная страница с чатом"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Simple Working Chat</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: #333; margin: 0; }
            .header p { color: #666; margin: 5px 0; }
            .chat-container { display: flex; gap: 20px; }
            .chat-messages { flex: 1; height: 400px; border: 1px solid #ddd; border-radius: 8px; padding: 15px; overflow-y: auto; background: #fafafa; }
            .message { margin-bottom: 15px; padding: 10px; border-radius: 8px; }
            .user-message { background: #007bff; color: white; margin-left: 20px; }
            .agent-message { background: #28a745; color: white; margin-right: 20px; }
            .system-message { background: #6c757d; color: white; text-align: center; }
            .chat-sidebar { width: 300px; }
            .system-info { background: #e9ecef; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
            .system-info h3 { margin-top: 0; color: #495057; }
            .status-item { margin: 8px 0; }
            .status-label { font-weight: bold; }
            .agent-selector { background: #e9ecef; padding: 15px; border-radius: 8px; }
            .agent-selector label { display: block; margin-bottom: 8px; font-weight: bold; }
            .agent-selector select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            .input-container { display: flex; gap: 10px; margin-top: 20px; }
            .message-input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 16px; }
            .send-button { padding: 12px 24px; background: #007bff; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; }
            .send-button:hover { background: #0056b3; }
            .status-online { color: #28a745; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Simple Working Chat</h1>
                <p>Быстрые ответы, стабильная работа</p>
            </div>
            
            <div class="chat-container">
                <div class="chat-messages" id="chatMessages">
                    <div class="message system-message">
                        <strong>Система:</strong> Добро пожаловать! Все агенты работают быстро и стабильно.
                    </div>
                </div>
                
                <div class="chat-sidebar">
                    <div class="system-info">
                        <h3>📊 Статус системы</h3>
                        <p><span class="status-indicator status-online"></span>Система: <span id="systemStatus">Загрузка...</span></p>
                        <p>Агентов: <span id="totalAgents">6</span></p>
                        <p>Активных: <span id="activeAgents">6</span></p>
                        <p>Время работы: <span id="uptime">0м</span></p>
                        <p>Сообщений: <span id="totalMessages">0</span></p>
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
            let totalMessages = 0;
            
            function addMessage(content, type) {
                const messagesDiv = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}-message`;
                messageDiv.innerHTML = content;
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
            
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const agentSelect = document.getElementById('agentSelect');
                const message = input.value.trim();
                
                if (!message) return;
                
                // Добавляем сообщение пользователя
                addMessage(`<strong>Вы:</strong> ${message}`, 'user');
                input.value = '';
                totalMessages++;
                updateStatus();
                
                // Отправляем запрос
                try {
                    const response = await fetch('/api/chat/send', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            message: message,
                            agent_type: agentSelect.value || null,
                            user_id: 'user_' + Math.random().toString(36).substr(2, 9)
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        addMessage(`<strong>${data.response.agent}:</strong> ${data.response.response}`, 'agent');
                    } else {
                        addMessage(`<strong>Ошибка:</strong> ${data.error}`, 'system');
                    }
                } catch (error) {
                    addMessage(`<strong>Ошибка:</strong> ${error.message}`, 'system');
                }
            }
            
            function updateStatus() {
                document.getElementById('totalMessages').textContent = totalMessages;
                document.getElementById('systemStatus').textContent = 'running';
                document.getElementById('activeAgents').textContent = '6';
                
                const uptime = Math.floor((Date.now() - """ + str(int(startup_time * 1000)) + """) / 60000);
                document.getElementById('uptime').textContent = uptime + 'м';
            }
            
            // Обработка Enter
            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
            
            // Обновляем статус каждые 5 секунд
            setInterval(updateStatus, 5000);
            updateStatus();
        </script>
    </body>
    </html>
    """)

@app.post("/api/chat/send")
async def send_message(request: Dict[str, Any]):
    """Отправка сообщения агенту"""
    try:
        message = request.get("message", "")
        agent_type = request.get("agent_type")
        user_id = request.get("user_id", "anonymous")
        
        if not message:
            return JSONResponse(content={"success": False, "error": "Пустое сообщение"})
        
        # Выбираем агента
        if agent_type and agent_type in agents:
            agent = agents[agent_type]
        else:
            # Автоматический выбор агента
            agent = agents["general_assistant"]
        
        # Получаем ответ
        response = agent.get_response(message)
        
        return JSONResponse(content={
            "success": True,
            "response": {
                "response": response,
                "agent": agent.name,
                "agent_type": agent.agent_type,
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "ai_used": False
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки сообщения: {e}")
        return JSONResponse(content={"success": False, "error": str(e)})

@app.get("/api/system/status")
async def get_system_status():
    """Получить статус системы"""
    try:
        uptime_seconds = int(time.time() - startup_time)
        uptime_minutes = uptime_seconds // 60
        
        total_messages = sum(agent.message_count for agent in agents.values())
        
        return JSONResponse(content={
            "system_status": "running" if system_running else "stopped",
            "total_agents": len(agents),
            "active_agents": len([a for a in agents.values() if a.is_active]),
            "uptime": f"{uptime_minutes}м",
            "total_messages": total_messages,
            "ai_engine_status": "not_used",
            "autonomous_tasks": 0
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения статуса: {e}")
        return JSONResponse(content={"system_status": "error", "error": str(e)})

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket для реального времени"""
    await websocket.accept()
    active_connections.add(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Обрабатываем сообщение
            response = await send_message(message_data)
            await websocket.send_text(json.dumps(response))
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        logger.error(f"❌ Ошибка WebSocket: {e}")
        active_connections.discard(websocket)

if __name__ == "__main__":
    logger.info("🚀 Запуск простой рабочей системы чата...")
    logger.info("✅ Все агенты готовы к работе")
    logger.info("🌐 Веб-интерфейс будет доступен на http://0.0.0.0:8080")
    
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")


