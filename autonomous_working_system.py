#!/usr/bin/env python3
"""
Автономная рабочая система агентов
Простая, но стабильная система с реальной автономностью
"""

import asyncio
import json
import logging
import time
import signal
import sys
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/mentor/autonomous_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Глобальные переменные системы
system_running = False
agents = {}
active_agents = set()
task_counter = 0
startup_time = time.time()
autonomous_tasks = []

class AutonomousAgent:
    """Простой автономный агент"""
    
    def __init__(self, agent_id: str, name: str, agent_type: str, skills: List[str]):
        self.agent_id = agent_id
        self.name = name
        self.agent_type = agent_type
        self.skills = skills
        self.status = "idle"
        self.last_activity = time.time()
        self.task_count = 0
        self.is_active = False
        
    async def process_message(self, message: str, user_id: str = "system") -> Dict[str, Any]:
        """Обработка сообщения"""
        try:
            self.last_activity = time.time()
            self.task_count += 1
            self.status = "processing"
            
            # Простая логика ответа
            if "привет" in message.lower():
                response = f"Привет! Я {self.name}. Готов помочь с {', '.join(self.skills[:3])}."
            elif "код" in message.lower() and "code_developer" in self.agent_type:
                response = "Я могу помочь с разработкой кода. Какой язык программирования вас интересует?"
            elif "анализ" in message.lower() and "data_analyst" in self.agent_type:
                response = "Я специализируюсь на анализе данных. Какие данные нужно проанализировать?"
            elif "проект" in message.lower() and "project_manager" in self.agent_type:
                response = "Я помогу с планированием проекта. Расскажите о ваших целях."
            elif "дизайн" in message.lower() and "designer" in self.agent_type:
                response = "Я создам дизайн для вас. Какой стиль предпочитаете?"
            elif "тест" in message.lower() and "qa_tester" in self.agent_type:
                response = "Я проведу тестирование. Что нужно протестировать?"
            else:
                response = f"Я {self.name}. Получил ваше сообщение: '{message}'. Чем могу помочь?"
            
            self.status = "idle"
            return {
                "response": response,
                "agent": self.name,
                "agent_type": self.agent_type,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения агентом {self.name}: {e}")
            self.status = "error"
            return {
                "response": f"Ошибка: {str(e)}",
                "agent": self.name,
                "agent_type": self.agent_type,
                "timestamp": datetime.now().isoformat(),
                "success": False
            }

# Создаем агентов
def create_agents():
    """Создание агентов"""
    global agents
    
    agents = {
        "general_assistant": AutonomousAgent(
            "general_assistant", "Универсальный Помощник", "general_assistant",
            ["general_help", "planning", "coordination", "user_query"]
        ),
        "code_developer": AutonomousAgent(
            "code_developer", "Разработчик Кода", "code_developer",
            ["code_generation", "debugging", "code_review", "architecture_design"]
        ),
        "data_analyst": AutonomousAgent(
            "data_analyst", "Аналитик Данных", "data_analyst",
            ["data_analysis", "reporting", "visualization", "predictive_modeling"]
        ),
        "project_manager": AutonomousAgent(
            "project_manager", "Менеджер Проектов", "project_manager",
            ["project_planning", "task_management", "resource_allocation", "progress_tracking"]
        ),
        "designer": AutonomousAgent(
            "designer", "Дизайнер", "designer",
            ["ui_design", "ux_design", "visual_identity"]
        ),
        "qa_tester": AutonomousAgent(
            "qa_tester", "Тестировщик", "qa_tester",
            ["unit_testing", "integration_testing", "bug_reporting"]
        )
    }
    
    logger.info(f"✅ Создано {len(agents)} автономных агентов")

# Автономные задачи
async def autonomous_task_generator():
    """Генератор автономных задач"""
    global autonomous_tasks, task_counter
    
    while system_running:
        try:
            # Создаем случайную задачу каждые 30-60 секунд
            await asyncio.sleep(30)
            
            if not system_running:
                break
                
            task_counter += 1
            task_types = [
                "Проанализируй производительность системы",
                "Проверь логи на ошибки",
                "Создай отчет о работе агентов",
                "Оптимизируй процессы",
                "Проверь безопасность системы"
            ]
            
            task = {
                "id": f"auto_task_{task_counter}",
                "description": task_types[task_counter % len(task_types)],
                "timestamp": datetime.now().isoformat(),
                "assigned_to": None
            }
            
            autonomous_tasks.append(task)
            logger.info(f"🤖 Создана автономная задача: {task['description']}")
            
            # Назначаем задачу случайному агенту
            if agents:
                agent_id = list(agents.keys())[task_counter % len(agents)]
                agent = agents[agent_id]
                await agent.process_message(task['description'], "autonomous_system")
                task['assigned_to'] = agent.name
                logger.info(f"📋 Задача назначена агенту: {agent.name}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка в генераторе автономных задач: {e}")
            await asyncio.sleep(10)

# FastAPI приложение
app = FastAPI(title="Autonomous Multi-AI System")

@app.get("/")
async def root():
    """Главная страница с чатом"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Autonomous Multi-AI System</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; color: white; margin-bottom: 30px; }
            .header h1 { font-size: 2.5em; margin-bottom: 10px; }
            .header p { font-size: 1.2em; opacity: 0.9; }
            .chat-container { display: flex; gap: 20px; height: 600px; }
            .chat-messages { flex: 1; background: white; border-radius: 15px; padding: 20px; overflow-y: auto; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
            .chat-sidebar { width: 300px; background: rgba(255,255,255,0.95); border-radius: 15px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
            .message { margin-bottom: 15px; padding: 12px; border-radius: 10px; }
            .user-message { background: #e3f2fd; margin-left: 20px; }
            .agent-message { background: #f3e5f5; margin-right: 20px; }
            .system-message { background: #e8f5e8; text-align: center; font-style: italic; }
            .input-container { display: flex; gap: 10px; margin-top: 20px; }
            .message-input { flex: 1; padding: 15px; border: none; border-radius: 25px; font-size: 16px; outline: none; }
            .send-button { padding: 15px 30px; background: #4CAF50; color: white; border: none; border-radius: 25px; cursor: pointer; font-size: 16px; transition: background 0.3s; }
            .send-button:hover { background: #45a049; }
            .system-info { margin-bottom: 20px; }
            .system-info h3 { color: #333; margin-bottom: 10px; }
            .status-item { display: flex; justify-content: space-between; margin-bottom: 5px; }
            .status-indicator { width: 12px; height: 12px; border-radius: 50%; display: inline-block; margin-right: 8px; }
            .status-online { background: #4CAF50; }
            .status-offline { background: #f44336; }
            .agent-selector { margin-bottom: 20px; }
            .agent-selector label { display: block; margin-bottom: 5px; font-weight: bold; color: #333; }
            .agent-selector select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            .autonomous-tasks { margin-top: 20px; }
            .autonomous-tasks h3 { color: #333; margin-bottom: 10px; }
            .task-item { background: #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 5px; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Autonomous Multi-AI System</h1>
                <p>Автономная система агентов с реальной автономностью</p>
            </div>
            
            <div class="chat-container">
                <div class="chat-messages" id="chatMessages">
                    <div class="message system-message">
                        <strong>Система:</strong> Автономная система запущена! Агенты работают независимо и выполняют задачи автоматически.
                    </div>
                </div>
                
                <div class="chat-sidebar">
                    <div class="system-info">
                        <h3>📊 Статус системы</h3>
                        <p><span class="status-indicator status-online"></span>Система: <span id="systemStatus">Загрузка...</span></p>
                        <p>Агентов: <span id="totalAgents">0</span></p>
                        <p>Активных: <span id="activeAgents">0</span></p>
                        <p>Время работы: <span id="uptime">0м</span></p>
                        <p>Автономных задач: <span id="autonomousTasks">0</span></p>
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
                    
                    <div class="autonomous-tasks">
                        <h3>🤖 Автономные задачи</h3>
                        <div id="autonomousTasksList">
                            <div class="task-item">Система генерирует задачи автоматически...</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="input-container">
                <input type="text" id="messageInput" class="message-input" placeholder="Введите ваше сообщение..." />
                <button onclick="sendMessage()" class="send-button">Отправить</button>
            </div>
        </div>

        <script>
            let ws = null;
            let userId = 'user_' + Math.random().toString(36).substr(2, 9);
            
            function connectWebSocket() {
                ws = new WebSocket(`ws://${window.location.host}/ws/${userId}`);
                
                ws.onopen = function() {
                    console.log('WebSocket подключен');
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    addMessage(data.message, 'agent', data.agent);
                };
                
                ws.onclose = function() {
                    console.log('WebSocket отключен, переподключение...');
                    setTimeout(connectWebSocket, 3000);
                };
            }
            
            function addMessage(message, type, agent = '') {
                const chatMessages = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}-message`;
                
                if (type === 'user') {
                    messageDiv.innerHTML = `<strong>Вы:</strong> ${message}`;
                } else {
                    messageDiv.innerHTML = `<strong>${agent}:</strong> ${message}`;
                }
                
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                const agentType = document.getElementById('agentSelect').value;
                
                if (message && ws) {
                    addMessage(message, 'user');
                    
                    const payload = {
                        message: message,
                        agent_type: agentType || null,
                        user_id: userId
                    };
                    
                    ws.send(JSON.stringify(payload));
                    input.value = '';
                }
            }
            
            function updateStatus() {
                fetch('/api/system/status')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('systemStatus').textContent = data.system_status;
                        document.getElementById('totalAgents').textContent = data.total_agents;
                        document.getElementById('activeAgents').textContent = data.active_agents;
                        document.getElementById('uptime').textContent = data.uptime;
                        document.getElementById('autonomousTasks').textContent = data.autonomous_tasks;
                    })
                    .catch(error => console.error('Ошибка обновления статуса:', error));
            }
            
            function updateAutonomousTasks() {
                fetch('/api/autonomous/tasks')
                    .then(response => response.json())
                    .then(data => {
                        const tasksList = document.getElementById('autonomousTasksList');
                        tasksList.innerHTML = '';
                        
                        if (data.tasks.length === 0) {
                            tasksList.innerHTML = '<div class="task-item">Нет активных задач</div>';
                        } else {
                            data.tasks.slice(-5).forEach(task => {
                                const taskDiv = document.createElement('div');
                                taskDiv.className = 'task-item';
                                taskDiv.innerHTML = `<strong>${task.description}</strong><br><small>Агент: ${task.assigned_to || 'Не назначен'}</small>`;
                                tasksList.appendChild(taskDiv);
                            });
                        }
                    })
                    .catch(error => console.error('Ошибка обновления задач:', error));
            }
            
            // Обработка Enter
            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
            
            // Инициализация
            connectWebSocket();
            updateStatus();
            updateAutonomousTasks();
            
            // Обновление каждые 5 секунд
            setInterval(updateStatus, 5000);
            setInterval(updateAutonomousTasks, 10000);
        </script>
    </body>
    </html>
    """)

@app.get("/api/system/status")
async def get_system_status():
    """Получить статус системы"""
    global system_running, agents, active_agents, startup_time, autonomous_tasks
    
    uptime_seconds = int(time.time() - startup_time)
    uptime_minutes = uptime_seconds // 60
    
    return {
        "system_status": "running" if system_running else "stopped",
        "total_agents": len(agents),
        "active_agents": len([a for a in agents.values() if a.is_active]),
        "uptime": f"{uptime_minutes}м",
        "autonomous_tasks": len(autonomous_tasks),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/autonomous/tasks")
async def get_autonomous_tasks():
    """Получить автономные задачи"""
    global autonomous_tasks
    return {"tasks": autonomous_tasks[-10:]}  # Последние 10 задач

@app.post("/api/chat/send")
async def send_message(data: dict):
    """Отправить сообщение агенту"""
    global agents
    
    message = data.get("message", "")
    agent_type = data.get("agent_type")
    user_id = data.get("user_id", "unknown")
    
    if not message:
        return {"error": "Сообщение не может быть пустым"}
    
    # Выбираем агента
    if agent_type and agent_type in agents:
        agent = agents[agent_type]
    else:
        # Автоматический выбор агента
        agent = list(agents.values())[0]  # Простой выбор
    
    # Обрабатываем сообщение
    result = await agent.process_message(message, user_id)
    
    return {
        "success": True,
        "response": result,
        "timestamp": datetime.now().isoformat()
    }

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket для реального времени"""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Обрабатываем сообщение
            response = await send_message(message_data)
            
            if response.get("success"):
                result = response["response"]
                await websocket.send_text(json.dumps({
                    "message": result["response"],
                    "agent": result["agent"],
                    "timestamp": result["timestamp"]
                }))
            else:
                await websocket.send_text(json.dumps({
                    "message": "Ошибка обработки сообщения",
                    "agent": "System",
                    "timestamp": datetime.now().isoformat()
                }))
                
    except WebSocketDisconnect:
        logger.info(f"🔌 Пользователь {user_id} отключился от WebSocket")

# Основная функция
async def main():
    """Главная функция"""
    global system_running
    
    logger.info("🚀 Запуск автономной системы агентов...")
    
    # Создаем агентов
    create_agents()
    
    # Запускаем систему
    system_running = True
    
    # Запускаем генератор автономных задач
    task_generator = asyncio.create_task(autonomous_task_generator())
    
    logger.info("✅ Автономная система запущена")
    logger.info("🌐 Веб-интерфейс доступен на http://0.0.0.0:8080")
    
    try:
        # Запускаем веб-сервер
        config = uvicorn.Config(app, host="0.0.0.0", port=8080, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("📡 Получен сигнал прерывания")
    finally:
        system_running = False
        task_generator.cancel()
        logger.info("🛑 Автономная система остановлена")

if __name__ == "__main__":
    asyncio.run(main())


