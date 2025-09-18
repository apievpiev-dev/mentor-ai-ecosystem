#!/usr/bin/env python3
"""
Сервер чата для системы множественных AI-агентов
Предоставляет веб-интерфейс и API для взаимодействия с агентами
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from pathlib import Path

# Импортируем нашу систему агентов
from multi_agent_system import MultiAgentSystem, AgentType
from vision_agent import vision_agent

# Создаем экземпляр системы
multi_agent_system = MultiAgentSystem()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция обработки сообщений (будет заменена при запуске)
async def process_user_message(message: str, user_id: str = "user") -> Dict[str, Any]:
    """Обработка сообщения пользователя (базовая реализация)"""
    return await multi_agent_system.process_user_message(message, user_id)

# Модели данных
class ChatMessage(BaseModel):
    message: str
    user_id: str = "anonymous"
    agent_type: Optional[str] = None

class AgentRequest(BaseModel):
    agent_id: str
    message: str
    user_id: str = "anonymous"

class SystemStatus(BaseModel):
    total_agents: int
    active_agents: int
    total_messages: int
    system_uptime: str

# Класс для управления WebSocket соединениями
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str = "anonymous"):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_connections[user_id] = websocket
        logger.info(f"🔌 Пользователь {user_id} подключился к чату")
    
    def disconnect(self, websocket: WebSocket, user_id: str = "anonymous"):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if user_id in self.user_connections:
            del self.user_connections[user_id]
        logger.info(f"🔌 Пользователь {user_id} отключился от чата")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Удаляем неактивные соединения
                self.active_connections.remove(connection)

# Создаем FastAPI приложение
app = FastAPI(
    title="Multi-Agent Chat System",
    description="Система чата с множественными AI-агентами",
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

# Менеджер соединений
manager = ConnectionManager()

# Статистика системы
system_stats = {
    "start_time": datetime.now(),
    "total_messages": 0,
    "active_users": 0
}

@app.get("/status", response_class=HTMLResponse)
async def get_status_page():
    """Страница статуса системы"""
    html_content = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Multi-AI System Status</title>
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
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            
            .header {
                background: #2c3e50;
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            .header p {
                font-size: 1.2em;
                opacity: 0.8;
            }
            
            .status-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                padding: 30px;
            }
            
            .status-card {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 25px;
                border-left: 5px solid #3498db;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            
            .status-card h3 {
                color: #2c3e50;
                margin-bottom: 15px;
                font-size: 1.3em;
            }
            
            .status-item {
                display: flex;
                justify-content: space-between;
                margin: 10px 0;
                padding: 8px 0;
                border-bottom: 1px solid #ecf0f1;
            }
            
            .status-item:last-child {
                border-bottom: none;
            }
            
            .status-label {
                font-weight: 600;
                color: #34495e;
            }
            
            .status-value {
                color: #27ae60;
                font-weight: bold;
            }
            
            .status-value.error {
                color: #e74c3c;
            }
            
            .status-value.warning {
                color: #f39c12;
            }
            
            .agent-list {
                margin-top: 15px;
            }
            
            .agent-item {
                background: white;
                margin: 8px 0;
                padding: 12px;
                border-radius: 8px;
                border-left: 3px solid #3498db;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .agent-item.active {
                border-left-color: #27ae60;
                background: #d5f4e6;
            }
            
            .agent-item.inactive {
                border-left-color: #e74c3c;
                background: #fadbd8;
            }
            
            .agent-name {
                font-weight: 600;
                color: #2c3e50;
            }
            
            .agent-status {
                font-size: 0.9em;
                padding: 4px 8px;
                border-radius: 12px;
                font-weight: bold;
            }
            
            .agent-status.active {
                background: #27ae60;
                color: white;
            }
            
            .agent-status.inactive {
                background: #e74c3c;
                color: white;
            }
            
            .refresh-btn {
                position: fixed;
                bottom: 30px;
                right: 30px;
                background: #3498db;
                color: white;
                border: none;
                border-radius: 50px;
                padding: 15px 25px;
                font-size: 1.1em;
                cursor: pointer;
                box-shadow: 0 5px 15px rgba(52, 152, 219, 0.3);
                transition: all 0.3s ease;
            }
            
            .refresh-btn:hover {
                background: #2980b9;
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(52, 152, 219, 0.4);
            }
            
            .back-btn {
                position: fixed;
                bottom: 30px;
                left: 30px;
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 50px;
                padding: 15px 25px;
                font-size: 1.1em;
                cursor: pointer;
                box-shadow: 0 5px 15px rgba(39, 174, 96, 0.3);
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
            }
            
            .back-btn:hover {
                background: #229954;
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(39, 174, 96, 0.4);
            }
            
            .loading {
                text-align: center;
                padding: 20px;
                color: #7f8c8d;
            }
            
            .error {
                text-align: center;
                padding: 20px;
                color: #e74c3c;
                background: #fadbd8;
                border-radius: 10px;
                margin: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Multi-AI System Status</h1>
                <p>Мониторинг автономной системы агентов</p>
            </div>
            
            <div class="status-grid">
                <div class="status-card">
                    <h3>📊 Общий статус</h3>
                    <div class="status-item">
                        <span class="status-label">Статус системы:</span>
                        <span class="status-value" id="systemStatus">Загрузка...</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Время работы:</span>
                        <span class="status-value" id="uptime">0м</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Активных пользователей:</span>
                        <span class="status-value" id="activeUsers">0</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Всего сообщений:</span>
                        <span class="status-value" id="totalMessages">0</span>
                    </div>
                </div>
                
                <div class="status-card">
                    <h3>🤖 Агенты</h3>
                    <div class="status-item">
                        <span class="status-label">Всего агентов:</span>
                        <span class="status-value" id="totalAgents">0</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Активных агентов:</span>
                        <span class="status-value" id="activeAgents">0</span>
                    </div>
                    <div class="agent-list" id="agentList">
                        <div class="loading">Загрузка списка агентов...</div>
                    </div>
                </div>
                
                <div class="status-card">
                    <h3>🔧 Система</h3>
                    <div class="status-item">
                        <span class="status-label">Версия API:</span>
                        <span class="status-value">v1.0</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Порт:</span>
                        <span class="status-value">8080</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Протокол:</span>
                        <span class="status-value">HTTP/WebSocket</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Последнее обновление:</span>
                        <span class="status-value" id="lastUpdate">-</span>
                    </div>
                </div>
            </div>
        </div>
        
        <button class="refresh-btn" onclick="refreshStatus()">🔄 Обновить</button>
        <a href="/" class="back-btn">← К чату</a>
        
        <script>
            let statusInterval;
            
            async function fetchStatus() {
                try {
                    const response = await fetch('/api/system/status');
                    const data = await response.json();
                    
                    // Обновляем общий статус
                    document.getElementById('systemStatus').textContent = data.system_status || 'unknown';
                    document.getElementById('systemStatus').className = 'status-value ' + (data.system_status === 'running' ? '' : 'error');
                    
                    document.getElementById('uptime').textContent = data.uptime || '0м';
                    document.getElementById('activeUsers').textContent = data.active_users || '0';
                    document.getElementById('totalMessages').textContent = data.total_messages || '0';
                    
                    // Обновляем агентов
                    document.getElementById('totalAgents').textContent = data.total_agents || '0';
                    document.getElementById('activeAgents').textContent = data.active_agents || '0';
                    
                    // Обновляем список агентов
                    const agentList = document.getElementById('agentList');
                    if (data.agents && data.agents.length > 0) {
                        agentList.innerHTML = data.agents.map(agent => `
                            <div class="agent-item ${agent.status === 'active' ? 'active' : 'inactive'}">
                                <span class="agent-name">${agent.name}</span>
                                <span class="agent-status ${agent.status === 'active' ? 'active' : 'inactive'}">
                                    ${agent.status === 'active' ? 'Активен' : 'Неактивен'}
                                </span>
                            </div>
                        `).join('');
                    } else {
                        agentList.innerHTML = '<div class="loading">Агенты не найдены</div>';
                    }
                    
                    // Обновляем время последнего обновления
                    document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
                    
                } catch (error) {
                    console.error('Ошибка получения статуса:', error);
                    document.getElementById('systemStatus').textContent = 'Ошибка';
                    document.getElementById('systemStatus').className = 'status-value error';
                }
            }
            
            function refreshStatus() {
                fetchStatus();
            }
            
            // Автообновление каждые 5 секунд
            function startAutoRefresh() {
                statusInterval = setInterval(fetchStatus, 5000);
            }
            
            function stopAutoRefresh() {
                if (statusInterval) {
                    clearInterval(statusInterval);
                }
            }
            
            // Запускаем при загрузке страницы
            document.addEventListener('DOMContentLoaded', function() {
                fetchStatus();
                startAutoRefresh();
            });
            
            // Останавливаем при уходе со страницы
            window.addEventListener('beforeunload', stopAutoRefresh);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/", response_class=HTMLResponse)
async def get_chat_interface():
    """Главная страница чата"""
    html_content = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Multi-Agent Chat System</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            .chat-container {
                width: 90%;
                max-width: 1200px;
                height: 90vh;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                display: flex;
                overflow: hidden;
            }
            
            .sidebar {
                width: 300px;
                background: #2c3e50;
                color: white;
                padding: 20px;
                overflow-y: auto;
            }
            
            .sidebar h2 {
                margin-bottom: 20px;
                color: #ecf0f1;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }
            
            .agent-list {
                margin-bottom: 30px;
            }
            
            .agent-item {
                background: #34495e;
                margin: 10px 0;
                padding: 15px;
                border-radius: 10px;
                cursor: pointer;
                transition: all 0.3s ease;
                border-left: 4px solid #3498db;
            }
            
            .agent-item:hover {
                background: #3498db;
                transform: translateX(5px);
            }
            
            .agent-item.active {
                background: #e74c3c;
                border-left-color: #c0392b;
            }
            
            .agent-name {
                font-weight: bold;
                margin-bottom: 5px;
            }
            
            .agent-type {
                font-size: 0.9em;
                opacity: 0.8;
            }
            
            .agent-skills {
                font-size: 0.8em;
                margin-top: 5px;
                opacity: 0.7;
            }
            
            .system-status {
                background: #27ae60;
                padding: 15px;
                border-radius: 10px;
                margin-top: 20px;
            }
            
            .status-item {
                display: flex;
                justify-content: space-between;
                margin: 5px 0;
            }
            
            .status-link {
                color: #3498db;
                text-decoration: none;
                font-weight: 600;
                padding: 8px 12px;
                border-radius: 6px;
                background: rgba(52, 152, 219, 0.1);
                transition: all 0.3s ease;
                display: inline-block;
                width: 100%;
                text-align: center;
            }
            
            .status-link:hover {
                background: #3498db;
                color: white;
                transform: translateY(-1px);
            }
            
            .chat-area {
                flex: 1;
                display: flex;
                flex-direction: column;
            }
            
            .chat-header {
                background: #34495e;
                color: white;
                padding: 20px;
                text-align: center;
            }
            
            .chat-header h1 {
                margin: 0;
                font-size: 1.5em;
            }
            
            .messages-container {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
                background: #f8f9fa;
            }
            
            .message {
                margin: 15px 0;
                display: flex;
                align-items: flex-start;
            }
            
            .message.user {
                justify-content: flex-end;
            }
            
            .message.agent {
                justify-content: flex-start;
            }
            
            .message-content {
                max-width: 70%;
                padding: 15px 20px;
                border-radius: 20px;
                position: relative;
            }
            
            .message.user .message-content {
                background: #3498db;
                color: white;
                border-bottom-right-radius: 5px;
            }
            
            .message.agent .message-content {
                background: white;
                color: #2c3e50;
                border: 1px solid #e0e0e0;
                border-bottom-left-radius: 5px;
            }
            
            .message-meta {
                font-size: 0.8em;
                opacity: 0.7;
                margin-top: 5px;
            }
            
            .agent-avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: #3498db;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 10px;
                font-weight: bold;
                color: white;
            }
            
            .input-area {
                padding: 20px;
                background: white;
                border-top: 1px solid #e0e0e0;
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
                transition: border-color 0.3s ease;
            }
            
            .message-input:focus {
                border-color: #3498db;
            }
            
            .send-button {
                padding: 15px 25px;
                background: #3498db;
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                transition: background 0.3s ease;
            }
            
            .send-button:hover {
                background: #2980b9;
            }
            
            .send-button:disabled {
                background: #bdc3c7;
                cursor: not-allowed;
            }
            
            .typing-indicator {
                display: none;
                padding: 10px 20px;
                color: #7f8c8d;
                font-style: italic;
            }
            
            .typing-indicator.show {
                display: block;
            }
            
            .welcome-message {
                text-align: center;
                color: #7f8c8d;
                margin: 50px 0;
                font-size: 1.2em;
            }
            
            .welcome-message h3 {
                margin-bottom: 10px;
                color: #2c3e50;
            }
            
            @media (max-width: 768px) {
                .chat-container {
                    width: 100%;
                    height: 100vh;
                    border-radius: 0;
                }
                
                .sidebar {
                    width: 250px;
                }
                
                .message-content {
                    max-width: 85%;
                }
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="sidebar">
                <h2>🤖 AI Агенты</h2>
                <div class="agent-list" id="agentList">
                    <!-- Агенты будут загружены динамически -->
                </div>
                
                <div class="system-status">
                    <h3>📊 Статус системы</h3>
                    <div class="status-item">
                        <span>Агентов:</span>
                        <span id="totalAgents">0</span>
                    </div>
                    <div class="status-item">
                        <span>Активных:</span>
                        <span id="activeAgents">0</span>
                    </div>
                    <div class="status-item">
                        <span>Сообщений:</span>
                        <span id="totalMessages">0</span>
                    </div>
                    <div class="status-item">
                        <span>Время работы:</span>
                        <span id="uptime">0м</span>
                    </div>
                    <div class="status-item">
                        <a href="/status" class="status-link" target="_blank">
                            📈 Подробный статус
                        </a>
                    </div>
                </div>
            </div>
            
            <div class="chat-area">
                <div class="chat-header">
                    <h1>💬 Multi-Agent Chat System</h1>
                </div>
                
                <div class="messages-container" id="messagesContainer">
                    <div class="welcome-message">
                        <h3>👋 Добро пожаловать!</h3>
                        <p>Выберите агента и начните общение</p>
                        <p>Каждый агент имеет свою специализацию и может помочь в разных задачах</p>
                    </div>
                </div>
                
                <div class="typing-indicator" id="typingIndicator">
                    Агент печатает...
                </div>
                
                <div class="input-area">
                    <div class="input-container">
                        <input type="text" class="message-input" id="messageInput" 
                               placeholder="Введите ваше сообщение..." maxlength="1000">
                        <button class="send-button" id="sendButton" onclick="sendMessage()">
                            Отправить
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let ws = null;
            let currentAgent = null;
            let userId = 'user_' + Math.random().toString(36).substr(2, 9);
            
            // Инициализация WebSocket соединения
            function initWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws/${userId}`;
                
                ws = new WebSocket(wsUrl);
                
                ws.onopen = function(event) {
                    console.log('WebSocket соединение установлено');
                    loadAgents();
                    updateSystemStatus();
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    handleMessage(data);
                };
                
                ws.onclose = function(event) {
                    console.log('WebSocket соединение закрыто');
                    setTimeout(initWebSocket, 3000); // Переподключение через 3 секунды
                };
                
                ws.onerror = function(error) {
                    console.error('WebSocket ошибка:', error);
                };
            }
            
            // Загрузка списка агентов
            async function loadAgents() {
                try {
                    const response = await fetch('/api/agents');
                    const agents = await response.json();
                    
                    const agentList = document.getElementById('agentList');
                    agentList.innerHTML = '';
                    
                    agents.forEach(agent => {
                        const agentItem = document.createElement('div');
                        agentItem.className = 'agent-item';
                        agentItem.onclick = () => selectAgent(agent.id);
                        
                        agentItem.innerHTML = `
                            <div class="agent-name">${agent.name}</div>
                            <div class="agent-type">${agent.type}</div>
                            <div class="agent-skills">${agent.skills.join(', ')}</div>
                        `;
                        
                        agentList.appendChild(agentItem);
                    });
                } catch (error) {
                    console.error('Ошибка загрузки агентов:', error);
                }
            }
            
            // Выбор агента
            function selectAgent(agentId) {
                // Убираем активный класс с предыдущего агента
                document.querySelectorAll('.agent-item').forEach(item => {
                    item.classList.remove('active');
                });
                
                // Добавляем активный класс к выбранному агенту
                event.target.closest('.agent-item').classList.add('active');
                
                currentAgent = agentId;
                
                // Показываем сообщение о выборе агента
                addMessage('system', `Выбран агент: ${event.target.closest('.agent-item').querySelector('.agent-name').textContent}`);
            }
            
            // Отправка сообщения
            function sendMessage() {
                const messageInput = document.getElementById('messageInput');
                const message = messageInput.value.trim();
                
                if (!message) return;
                
                if (!currentAgent) {
                    alert('Пожалуйста, выберите агента для общения');
                    return;
                }
                
                // Отправляем сообщение через WebSocket
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({
                        type: 'user_message',
                        message: message,
                        agent_id: currentAgent,
                        user_id: userId
                    }));
                    
                    // Добавляем сообщение пользователя в чат
                    addMessage('user', message);
                    
                    // Очищаем поле ввода
                    messageInput.value = '';
                    
                    // Показываем индикатор печати
                    showTypingIndicator();
                }
            }
            
            // Обработка входящих сообщений
            function handleMessage(data) {
                hideTypingIndicator();
                
                switch (data.type) {
                    case 'agent_response':
                        addMessage('agent', data.response, data.agent_name);
                        break;
                    case 'system_status':
                        updateSystemStatus(data);
                        break;
                    case 'error':
                        addMessage('system', `Ошибка: ${data.message}`);
                        break;
                }
            }
            
            // Добавление сообщения в чат
            function addMessage(sender, content, agentName = null) {
                const messagesContainer = document.getElementById('messagesContainer');
                
                // Убираем приветственное сообщение если оно есть
                const welcomeMessage = messagesContainer.querySelector('.welcome-message');
                if (welcomeMessage) {
                    welcomeMessage.remove();
                }
                
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}`;
                
                const timestamp = new Date().toLocaleTimeString();
                
                if (sender === 'user') {
                    messageDiv.innerHTML = `
                        <div class="message-content">
                            ${content}
                            <div class="message-meta">${timestamp}</div>
                        </div>
                    `;
                } else if (sender === 'agent') {
                    const avatar = agentName ? agentName.charAt(0).toUpperCase() : '🤖';
                    messageDiv.innerHTML = `
                        <div class="agent-avatar">${avatar}</div>
                        <div class="message-content">
                            ${content}
                            <div class="message-meta">${agentName || 'Агент'} • ${timestamp}</div>
                        </div>
                    `;
                } else if (sender === 'system') {
                    messageDiv.innerHTML = `
                        <div class="message-content" style="background: #f39c12; color: white; text-align: center; margin: 0 auto;">
                            ${content}
                        </div>
                    `;
                }
                
                messagesContainer.appendChild(messageDiv);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
            
            // Показать индикатор печати
            function showTypingIndicator() {
                document.getElementById('typingIndicator').classList.add('show');
            }
            
            // Скрыть индикатор печати
            function hideTypingIndicator() {
                document.getElementById('typingIndicator').classList.remove('show');
            }
            
            // Обновление статуса системы
            function updateSystemStatus(data = null) {
                if (data) {
                    document.getElementById('totalAgents').textContent = data.total_agents || 0;
                    document.getElementById('activeAgents').textContent = data.active_agents || 0;
                    document.getElementById('totalMessages').textContent = data.total_messages || 0;
                    document.getElementById('uptime').textContent = data.uptime || '0м';
                }
            }
            
            // Обработка нажатия Enter
            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
            
            // Инициализация при загрузке страницы
            document.addEventListener('DOMContentLoaded', function() {
                initWebSocket();
                
                // Обновление статуса каждые 30 секунд
                setInterval(updateSystemStatus, 30000);
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.websocket("/ws")
async def websocket_endpoint_general(websocket: WebSocket):
    """WebSocket endpoint для чата (общий)"""
    # Генерируем случайный user_id
    import uuid
    user_id = f"user_{uuid.uuid4().hex[:10]}"
    await websocket_endpoint(websocket, user_id)

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint для чата"""
    await manager.connect(websocket, user_id)
    system_stats["active_users"] = len(manager.active_connections)
    
    try:
        while True:
            # Получаем сообщение от клиента
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data["type"] == "user_message":
                # Обрабатываем сообщение пользователя
                result = await process_user_message(
                    message_data["message"], 
                    user_id
                )
                
                system_stats["total_messages"] += 1
                
                # Отправляем ответ агенту
                response_text = ""
                if isinstance(result["response"], dict):
                    response_text = result["response"].get("response", str(result["response"]))
                else:
                    response_text = str(result["response"])
                
                response = {
                    "type": "agent_response",
                    "response": response_text,
                    "agent_name": result.get("agent", "Unknown"),
                    "agent_type": result.get("agent_type", "Unknown"),
                    "timestamp": result.get("timestamp", datetime.now().isoformat())
                }
                
                await manager.send_personal_message(json.dumps(response), websocket)
                
                # Отправляем обновленный статус системы
                status_update = {
                    "type": "system_status",
                    "total_agents": len(multi_agent_system.agents),
                    "active_agents": len([a for a in multi_agent_system.agents.values() if a.status != "idle"]),
                    "total_messages": system_stats["total_messages"],
                    "uptime": get_uptime()
                }
                
                await manager.send_personal_message(json.dumps(status_update), websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        system_stats["active_users"] = len(manager.active_connections)

@app.get("/api/agents")
async def get_agents():
    """Получить список доступных агентов"""
    try:
        agents = multi_agent_system.get_available_agents()
        return JSONResponse(content=agents)
    except Exception as e:
        logger.error(f"❌ Ошибка получения списка агентов: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/send")
async def send_message(message: ChatMessage):
    """Отправить сообщение агенту через REST API"""
    try:
        result = await process_user_message(
            message.message, 
            message.user_id
        )
        
        system_stats["total_messages"] += 1
        
        return JSONResponse(content={
            "success": True,
            "response": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка отправки сообщения: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/status")
async def get_system_status():
    """Получить статус системы"""
    try:
        # Используем интегрированную систему вместо старой
        from integrated_agent_system import get_integrated_system
        integrated_system = get_integrated_system()
        status = integrated_system.get_system_status()
        status.update({
            "active_users": system_stats["active_users"],
            "total_messages": system_stats["total_messages"],
            "uptime": get_uptime()
        })
        
        return JSONResponse(content=status)
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения статуса системы: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/history")
async def get_chat_history(limit: int = 50):
    """Получить историю чата"""
    try:
        history = multi_agent_system.shared_memory.get_recent_context(limit)
        return JSONResponse(content={"history": history})
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения истории чата: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Vision Agent API endpoints
@app.get("/api/vision/suggestions")
async def get_vision_suggestions():
    """Получить предложения по улучшению от Vision Agent"""
    try:
        suggestions = await vision_agent.suggest_improvements()
        return {"success": True, "suggestions": suggestions}
    except Exception as e:
        logger.error(f"❌ Ошибка получения предложений: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/vision/issues")
async def get_vision_issues():
    """Получить обнаруженные проблемы от Vision Agent"""
    try:
        screenshot = await vision_agent.take_screenshot()
        if screenshot:
            analysis = await vision_agent.analyze_ui(screenshot)
            return {"success": True, "issues": analysis.get("issues", [])}
        else:
            return {"success": False, "error": "Не удалось получить скриншот"}
    except Exception as e:
        logger.error(f"❌ Ошибка получения проблем: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/vision/analyze")
async def analyze_ui():
    """Анализ пользовательского интерфейса"""
    try:
        screenshot = await vision_agent.take_screenshot()
        if screenshot:
            analysis = await vision_agent.analyze_ui(screenshot)
            return {"success": True, "analysis": analysis}
        else:
            return {"success": False, "error": "Не удалось получить скриншот"}
    except Exception as e:
        logger.error(f"❌ Ошибка анализа UI: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/vision/health")
async def get_vision_health():
    """Получить состояние Vision Agent"""
    try:
        health = await vision_agent.monitor_system_health()
        return {"success": True, "health": health}
    except Exception as e:
        logger.error(f"❌ Ошибка получения состояния: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def get_uptime() -> str:
    """Получить время работы системы"""
    uptime = datetime.now() - system_stats["start_time"]
    minutes = int(uptime.total_seconds() / 60)
    hours = minutes // 60
    minutes = minutes % 60
    
    if hours > 0:
        return f"{hours}ч {minutes}м"
    else:
        return f"{minutes}м"

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    logger.info("🚀 Multi-Agent Chat Server запущен")
    logger.info(f"📊 Создано агентов: {len(multi_agent_system.agents)}")
    
    # Выводим информацию об агентах
    for agent in multi_agent_system.agents.values():
        logger.info(f"  🤖 {agent.name} ({agent.agent_type.value})")

@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при остановке"""
    logger.info("🛑 Multi-Agent Chat Server остановлен")

if __name__ == "__main__":
    # Запуск сервера
    uvicorn.run(
        "chat_server:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
