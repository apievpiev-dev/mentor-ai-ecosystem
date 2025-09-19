#!/usr/bin/env python3
"""
Unified Neural Interface - Единый веб-интерфейс для управления всеми нейросетями
Интегрирует все компоненты системы в единый интерфейс
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Добавляем путь к модулям
sys.path.append('/workspace')

# Импортируем наши компоненты
from enhanced_ai_engine import enhanced_ai_engine, generate_ai_response, generate_code, analyze_data, plan_project
from autonomous_neural_system import autonomous_neural_system
from visual_monitor import visual_monitor
from multi_agent_system import MultiAgentSystem, AgentType

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем FastAPI приложение
app = FastAPI(
    title="Unified Neural Interface",
    description="Единый интерфейс для управления всеми нейросетями",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели данных
class ChatMessage(BaseModel):
    message: str
    agent_type: Optional[str] = None
    user_id: str = "user"

class TaskRequest(BaseModel):
    description: str
    priority: int = 1
    task_type: str = "general"

class SystemConfig(BaseModel):
    auto_mode: bool = True
    visual_verification: bool = True
    performance_optimization: bool = True

# Глобальные переменные
connected_clients: List[WebSocket] = []
system_initialized = False
multi_agent_system = None

# HTML интерфейс
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unified Neural Interface</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            color: #4a5568;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        
        .header p {
            text-align: center;
            color: #718096;
            font-size: 1.1em;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .panel {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .panel h2 {
            color: #4a5568;
            margin-bottom: 15px;
            font-size: 1.5em;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
        }
        
        .chat-container {
            height: 400px;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            overflow-y: auto;
            padding: 15px;
            margin-bottom: 15px;
            background: #f7fafc;
        }
        
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 10px;
            max-width: 80%;
        }
        
        .user-message {
            background: #4299e1;
            color: white;
            margin-left: auto;
        }
        
        .ai-message {
            background: #e2e8f0;
            color: #2d3748;
        }
        
        .system-message {
            background: #48bb78;
            color: white;
            text-align: center;
            margin: 0 auto;
        }
        
        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .input-group input {
            flex: 1;
            padding: 12px;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            font-size: 16px;
        }
        
        .input-group select {
            padding: 12px;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            font-size: 16px;
            background: white;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-primary {
            background: #4299e1;
            color: white;
        }
        
        .btn-primary:hover {
            background: #3182ce;
        }
        
        .btn-success {
            background: #48bb78;
            color: white;
        }
        
        .btn-success:hover {
            background: #38a169;
        }
        
        .btn-warning {
            background: #ed8936;
            color: white;
        }
        
        .btn-warning:hover {
            background: #dd6b20;
        }
        
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .status-card {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        }
        
        .status-card h3 {
            color: #4a5568;
            margin-bottom: 10px;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        
        .status-healthy {
            background: #48bb78;
        }
        
        .status-warning {
            background: #ed8936;
        }
        
        .status-error {
            background: #f56565;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }
        
        .metric-card {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        }
        
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #4299e1;
        }
        
        .metric-label {
            color: #718096;
            font-size: 0.9em;
        }
        
        .agent-list {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .agent-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            margin-bottom: 10px;
            background: #f7fafc;
        }
        
        .agent-info {
            flex: 1;
        }
        
        .agent-name {
            font-weight: bold;
            color: #4a5568;
        }
        
        .agent-type {
            color: #718096;
            font-size: 0.9em;
        }
        
        .agent-status {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .status-idle {
            background: #e2e8f0;
            color: #4a5568;
        }
        
        .status-working {
            background: #4299e1;
            color: white;
        }
        
        .status-busy {
            background: #ed8936;
            color: white;
        }
        
        .footer {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .footer p {
            color: #718096;
            margin-bottom: 10px;
        }
        
        .footer .status {
            font-weight: bold;
            color: #48bb78;
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .status-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Unified Neural Interface</h1>
            <p>Единый интерфейс для управления всеми нейросетями и AI агентами</p>
        </div>
        
        <div class="main-content">
            <div class="panel">
                <h2>💬 Чат с AI</h2>
                <div class="input-group">
                    <select id="agentSelect">
                        <option value="general">Универсальный Помощник</option>
                        <option value="code_developer">Разработчик Кода</option>
                        <option value="data_analyst">Аналитик Данных</option>
                        <option value="project_manager">Менеджер Проектов</option>
                        <option value="designer">Дизайнер</option>
                        <option value="qa_tester">Тестировщик</option>
                    </select>
                </div>
                <div class="chat-container" id="chatContainer">
                    <div class="message system-message">
                        Система инициализирована. Выберите агента и начните общение.
                    </div>
                </div>
                <div class="input-group">
                    <input type="text" id="messageInput" placeholder="Введите ваше сообщение..." maxlength="1000">
                    <button class="btn btn-primary" onclick="sendMessage()">Отправить</button>
                </div>
            </div>
            
            <div class="panel">
                <h2>📊 Статус Системы</h2>
                <div class="status-grid">
                    <div class="status-card">
                        <h3>AI Engine</h3>
                        <span class="status-indicator status-healthy" id="aiEngineStatus"></span>
                        <span id="aiEngineText">Здоров</span>
                    </div>
                    <div class="status-card">
                        <h3>Multi-Agent</h3>
                        <span class="status-indicator status-healthy" id="multiAgentStatus"></span>
                        <span id="multiAgentText">Активен</span>
                    </div>
                    <div class="status-card">
                        <h3>Visual Monitor</h3>
                        <span class="status-indicator status-healthy" id="visualMonitorStatus"></span>
                        <span id="visualMonitorText">Работает</span>
                    </div>
                    <div class="status-card">
                        <h3>Автономный режим</h3>
                        <span class="status-indicator status-healthy" id="autonomousStatus"></span>
                        <span id="autonomousText">Включен</span>
                    </div>
                </div>
                
                <h3>📈 Метрики</h3>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value" id="totalAgents">0</div>
                        <div class="metric-label">Агентов</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="activeTasks">0</div>
                        <div class="metric-label">Задач</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="responseTime">0ms</div>
                        <div class="metric-label">Отклик</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="uptime">0h</div>
                        <div class="metric-label">Время работы</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="panel">
            <h2>🤖 Активные Агенты</h2>
            <div class="agent-list" id="agentList">
                <div class="agent-item">
                    <div class="agent-info">
                        <div class="agent-name">Загрузка...</div>
                        <div class="agent-type">Получение данных</div>
                    </div>
                    <span class="agent-status status-idle">Загрузка</span>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Unified Neural Interface v1.0.0</p>
            <p>Статус: <span class="status" id="systemStatus">Инициализация...</span></p>
            <p>Последнее обновление: <span id="lastUpdate">-</span></p>
        </div>
    </div>

    <script>
        let ws = null;
        let isConnected = false;
        
        // Инициализация WebSocket соединения
        function initWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function(event) {
                isConnected = true;
                updateSystemStatus('Подключено', 'status-healthy');
                addMessage('system', 'WebSocket соединение установлено');
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            };
            
            ws.onclose = function(event) {
                isConnected = false;
                updateSystemStatus('Отключено', 'status-error');
                addMessage('system', 'WebSocket соединение потеряно');
                
                // Попытка переподключения через 3 секунды
                setTimeout(initWebSocket, 3000);
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
                updateSystemStatus('Ошибка', 'status-error');
            };
        }
        
        // Обработка сообщений WebSocket
        function handleWebSocketMessage(data) {
            switch(data.type) {
                case 'system_status':
                    updateSystemMetrics(data.data);
                    break;
                case 'agent_update':
                    updateAgentList(data.data);
                    break;
                case 'chat_response':
                    addMessage('ai', data.data.response, data.data.agent);
                    break;
                case 'system_message':
                    addMessage('system', data.data.message);
                    break;
            }
        }
        
        // Отправка сообщения
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const agentSelect = document.getElementById('agentSelect');
            const message = input.value.trim();
            
            if (!message) return;
            
            if (!isConnected) {
                addMessage('system', 'Ошибка: нет соединения с сервером');
                return;
            }
            
            // Добавляем сообщение пользователя в чат
            addMessage('user', message);
            
            // Отправляем через WebSocket
            ws.send(JSON.stringify({
                type: 'chat_message',
                data: {
                    message: message,
                    agent_type: agentSelect.value,
                    user_id: 'web_user'
                }
            }));
            
            input.value = '';
        }
        
        // Добавление сообщения в чат
        function addMessage(type, content, agent = null) {
            const container = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}-message`;
            
            let messageContent = content;
            if (agent) {
                messageContent = `<strong>${agent}:</strong> ${content}`;
            }
            
            messageDiv.innerHTML = messageContent;
            container.appendChild(messageDiv);
            container.scrollTop = container.scrollHeight;
        }
        
        // Обновление статуса системы
        function updateSystemStatus(text, statusClass) {
            const statusElement = document.getElementById('systemStatus');
            statusElement.textContent = text;
            statusElement.className = statusClass;
        }
        
        // Обновление метрик системы
        function updateSystemMetrics(data) {
            document.getElementById('totalAgents').textContent = data.total_agents || 0;
            document.getElementById('activeTasks').textContent = data.active_tasks || 0;
            document.getElementById('responseTime').textContent = `${Math.round(data.average_response_time || 0)}ms`;
            document.getElementById('uptime').textContent = `${Math.round((data.uptime || 0) / 3600)}h`;
            
            // Обновление статусов компонентов
            updateComponentStatus('aiEngineStatus', 'aiEngineText', data.components?.ai_engine?.healthy);
            updateComponentStatus('multiAgentStatus', 'multiAgentText', data.components?.multi_agent?.system_status === 'running');
            updateComponentStatus('visualMonitorStatus', 'visualMonitorText', data.components?.visual_monitor?.active);
            updateComponentStatus('autonomousStatus', 'autonomousText', data.running);
            
            document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
        }
        
        // Обновление статуса компонента
        function updateComponentStatus(statusId, textId, isHealthy) {
            const statusElement = document.getElementById(statusId);
            const textElement = document.getElementById(textId);
            
            if (isHealthy) {
                statusElement.className = 'status-indicator status-healthy';
                textElement.textContent = 'Здоров';
            } else {
                statusElement.className = 'status-indicator status-error';
                textElement.textContent = 'Ошибка';
            }
        }
        
        // Обновление списка агентов
        function updateAgentList(agents) {
            const container = document.getElementById('agentList');
            container.innerHTML = '';
            
            if (!agents || agents.length === 0) {
                container.innerHTML = '<div class="agent-item"><div class="agent-info"><div class="agent-name">Нет активных агентов</div></div></div>';
                return;
            }
            
            agents.forEach(agent => {
                const agentDiv = document.createElement('div');
                agentDiv.className = 'agent-item';
                
                const statusClass = `status-${agent.status}`;
                const statusText = agent.status === 'idle' ? 'Свободен' : 
                                 agent.status === 'working' ? 'Работает' : 
                                 agent.status === 'busy' ? 'Занят' : 'Неизвестно';
                
                agentDiv.innerHTML = `
                    <div class="agent-info">
                        <div class="agent-name">${agent.name}</div>
                        <div class="agent-type">${agent.type}</div>
                    </div>
                    <span class="agent-status ${statusClass}">${statusText}</span>
                `;
                
                container.appendChild(agentDiv);
            });
        }
        
        // Обработка нажатия Enter в поле ввода
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        // Инициализация при загрузке страницы
        document.addEventListener('DOMContentLoaded', function() {
            initWebSocket();
            
            // Запрос начального статуса
            fetch('/api/system/status')
                .then(response => response.json())
                .then(data => {
                    updateSystemMetrics(data);
                })
                .catch(error => {
                    console.error('Error fetching system status:', error);
                });
        });
    </script>
</body>
</html>
"""

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    global system_initialized, multi_agent_system
    
    try:
        logger.info("🚀 Инициализация Unified Neural Interface...")
        
        # Инициализируем все компоненты
        await enhanced_ai_engine.initialize()
        await autonomous_neural_system.initialize()
        await visual_monitor.initialize()
        
        # Создаем Multi-Agent System
        multi_agent_system = MultiAgentSystem()
        
        system_initialized = True
        logger.info("✅ Unified Neural Interface инициализирован")
        
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации: {e}")

@app.get("/", response_class=HTMLResponse)
async def get_interface():
    """Главная страница интерфейса"""
    return HTML_INTERFACE

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint для реального времени"""
    await websocket.accept()
    connected_clients.append(websocket)
    
    try:
        while True:
            # Получаем сообщение от клиента
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Обрабатываем сообщение
            if message_data.get("type") == "chat_message":
                await handle_chat_message(websocket, message_data["data"])
            elif message_data.get("type") == "system_config":
                await handle_system_config(websocket, message_data["data"])
            
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
    except Exception as e:
        logger.error(f"❌ Ошибка WebSocket: {e}")
        if websocket in connected_clients:
            connected_clients.remove(websocket)

async def handle_chat_message(websocket: WebSocket, data: Dict[str, Any]):
    """Обработка сообщения чата"""
    try:
        message = data.get("message", "")
        agent_type = data.get("agent_type", "general")
        user_id = data.get("user_id", "user")
        
        if not message:
            return
        
        # Обрабатываем сообщение через Multi-Agent System
        if multi_agent_system:
            result = await multi_agent_system.process_user_message(message, user_id)
            
            # Отправляем ответ клиенту
            await websocket.send_text(json.dumps({
                "type": "chat_response",
                "data": {
                    "response": result.get("response", {}).get("response", "Извините, произошла ошибка"),
                    "agent": result.get("agent", "Неизвестный агент"),
                    "agent_type": result.get("agent_type", "general")
                }
            }))
        else:
            # Fallback через Enhanced AI Engine
            response = await generate_ai_response(message)
            await websocket.send_text(json.dumps({
                "type": "chat_response",
                "data": {
                    "response": response,
                    "agent": "AI Assistant",
                    "agent_type": "general"
                }
            }))
    
    except Exception as e:
        logger.error(f"❌ Ошибка обработки сообщения чата: {e}")
        await websocket.send_text(json.dumps({
            "type": "system_message",
            "data": {"message": f"Ошибка: {str(e)}"}
        }))

async def handle_system_config(websocket: WebSocket, data: Dict[str, Any]):
    """Обработка конфигурации системы"""
    try:
        # Здесь можно добавить логику изменения конфигурации
        await websocket.send_text(json.dumps({
            "type": "system_message",
            "data": {"message": "Конфигурация обновлена"}
        }))
    
    except Exception as e:
        logger.error(f"❌ Ошибка обработки конфигурации: {e}")

@app.get("/api/system/status")
async def get_system_status():
    """Получение статуса системы"""
    try:
        if not system_initialized:
            return {"error": "System not initialized"}
        
        # Получаем статус всех компонентов
        ai_status = await enhanced_ai_engine.get_system_status()
        autonomous_status = await autonomous_neural_system.get_system_status()
        visual_status = await visual_monitor.get_status()
        
        # Статус Multi-Agent System
        multi_agent_status = None
        if multi_agent_system:
            multi_agent_status = multi_agent_system.get_system_status()
        
        return {
            "system_initialized": system_initialized,
            "uptime": time.time() - autonomous_status.get("uptime", 0),
            "total_agents": multi_agent_status.get("total_agents", 0) if multi_agent_status else 0,
            "active_tasks": autonomous_status.get("task_queue_size", 0),
            "average_response_time": ai_status.get("performance", {}).get("average_response_time", 0),
            "components": {
                "ai_engine": ai_status,
                "multi_agent": multi_agent_status,
                "visual_monitor": visual_status,
                "autonomous_system": autonomous_status
            },
            "running": autonomous_status.get("running", False)
        }
    
    except Exception as e:
        logger.error(f"❌ Ошибка получения статуса системы: {e}")
        return {"error": str(e)}

@app.get("/api/agents")
async def get_agents():
    """Получение списка агентов"""
    try:
        if not multi_agent_system:
            return {"agents": []}
        
        agents = multi_agent_system.get_available_agents()
        return {"agents": agents}
    
    except Exception as e:
        logger.error(f"❌ Ошибка получения списка агентов: {e}")
        return {"error": str(e)}

@app.post("/api/chat/send")
async def send_chat_message(message: ChatMessage):
    """Отправка сообщения в чат"""
    try:
        if not system_initialized:
            raise HTTPException(status_code=503, detail="System not initialized")
        
        # Обрабатываем сообщение
        if multi_agent_system:
            result = await multi_agent_system.process_user_message(message.message, message.user_id)
        else:
            result = {"response": {"response": await generate_ai_response(message.message)}}
        
        return {
            "success": True,
            "response": result.get("response", {}).get("response", ""),
            "agent": result.get("agent", "AI Assistant"),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"❌ Ошибка отправки сообщения: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tasks")
async def create_task(task: TaskRequest):
    """Создание новой задачи"""
    try:
        if not system_initialized:
            raise HTTPException(status_code=503, detail="System not initialized")
        
        # Здесь можно добавить логику создания задач
        return {
            "success": True,
            "task_id": f"task_{int(time.time())}",
            "message": "Задача создана успешно"
        }
    
    except Exception as e:
        logger.error(f"❌ Ошибка создания задачи: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/visual/report")
async def get_visual_report():
    """Получение визуального отчета"""
    try:
        if not system_initialized:
            raise HTTPException(status_code=503, detail="System not initialized")
        
        report = await visual_monitor.generate_visual_report()
        return report
    
    except Exception as e:
        logger.error(f"❌ Ошибка получения визуального отчета: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Функция для отправки обновлений всем подключенным клиентам
async def broadcast_update(update_type: str, data: Dict[str, Any]):
    """Отправка обновления всем подключенным клиентам"""
    if not connected_clients:
        return
    
    message = json.dumps({
        "type": update_type,
        "data": data
    })
    
    # Отправляем всем подключенным клиентам
    disconnected_clients = []
    for client in connected_clients:
        try:
            await client.send_text(message)
        except:
            disconnected_clients.append(client)
    
    # Удаляем отключенных клиентов
    for client in disconnected_clients:
        connected_clients.remove(client)

# Фоновая задача для отправки обновлений статуса
async def status_broadcast_task():
    """Фоновая задача для отправки обновлений статуса"""
    while True:
        try:
            if connected_clients and system_initialized:
                # Получаем текущий статус
                status = await get_system_status()
                
                # Отправляем обновление
                await broadcast_update("system_status", status)
                
                # Получаем список агентов
                if multi_agent_system:
                    agents = multi_agent_system.get_available_agents()
                    await broadcast_update("agent_update", agents)
            
            await asyncio.sleep(5)  # Обновляем каждые 5 секунд
            
        except Exception as e:
            logger.error(f"❌ Ошибка в задаче broadcast: {e}")
            await asyncio.sleep(10)

# Запуск фоновой задачи при старте
@app.on_event("startup")
async def start_background_tasks():
    """Запуск фоновых задач"""
    asyncio.create_task(status_broadcast_task())

if __name__ == "__main__":
    # Запуск сервера
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8081,
        log_level="info"
    )