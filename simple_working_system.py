#!/usr/bin/env python3
"""
Простая рабочая автономная система
"""

import asyncio
import logging
import time
import requests
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import threading
import random
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/mentor/simple_working_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# FastAPI приложение
app = FastAPI(title="Simple Working Autonomous System", version="1.0.0")
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
    user_id: str = "user"
    agent_type: Optional[str] = None

# Глобальные переменные
system_running = False
agents = {}
active_agents = set()
task_counter = 0
startup_time = datetime.now()
lock = threading.Lock()

# Автономные задачи для агентов
autonomous_tasks = {
    "general_assistant": [
        "Проанализируй текущее состояние системы и создай отчет",
        "Предложи улучшения для системы",
        "Создай план оптимизации производительности"
    ],
    "code_developer": [
        "Создай функцию для автоматического тестирования API",
        "Оптимизируй код системы для лучшей производительности",
        "Добавь обработку ошибок в критические функции"
    ],
    "data_analyst": [
        "Проанализируй статистику использования системы",
        "Создай отчет о производительности агентов",
        "Проанализируй паттерны использования API"
    ],
    "project_manager": [
        "Создай план развития системы на следующую неделю",
        "Проанализируй приоритеты задач",
        "Создай roadmap для новых функций"
    ],
    "designer": [
        "Улучши дизайн веб-интерфейса",
        "Создай иконки для новых функций",
        "Оптимизируй UX для мобильных устройств"
    ],
    "qa_tester": [
        "Протестируй все API endpoints",
        "Проверь систему на уязвимости",
        "Создай автоматические тесты"
    ]
}

def initialize_agents():
    """Инициализация агентов"""
    global agents
    agent_types = [
        "general_assistant",
        "code_developer", 
        "data_analyst",
        "project_manager",
        "designer",
        "qa_tester"
    ]
    
    for agent_type in agent_types:
        agents[agent_type] = {
            "id": f"{agent_type}_agent",
            "name": f"Агент {agent_type.replace('_', ' ').title()}",
            "type": agent_type,
            "is_active": False,
            "last_activity": None,
            "task_count": 0,
            "status": "idle"
        }
        logger.info(f"✅ Агент {agent_type} инициализирован")

async def get_system_status() -> Dict[str, Any]:
    """Получение статуса системы"""
    global system_running, agents, active_agents, task_counter, startup_time
    
    with lock:
        uptime_delta = datetime.now() - startup_time
        uptime = f"{int(uptime_delta.total_seconds() / 60)}м"
        
        return {
            "system_status": "running" if system_running else "stopped",
            "uptime": uptime,
            "total_agents": len(agents),
            "active_agents": len(active_agents),
            "coordination_status": {
                "total_agents": len(agents),
                "active_tasks": len(active_agents),
                "message_queue_size": 0,
                "agent_capabilities": {
                    agent_id: {
                        "skills": ["autonomous_work", "task_processing"],
                        "performance_score": 1.0,
                        "availability": True,
                        "current_load": 0.0,
                        "is_active": agent["is_active"],
                        "last_activity": agent["last_activity"].isoformat() if agent["last_activity"] else None
                    }
                    for agent_id, agent in agents.items()
                },
                "active_tasks_info": []
            },
            "shared_memory": {
                "knowledge_items": task_counter,
                "conversation_history": task_counter,
                "agent_capabilities": len(agents)
            },
            "startup_time": startup_time.isoformat()
        }

def send_message_to_agent(message: str, agent_type: str = None, user_id: str = "user") -> Dict[str, Any]:
    """Отправка сообщения агенту"""
    global agents, active_agents
    
    try:
        with lock:
            if agent_type and agent_type in agents:
                # Отправляем конкретному агенту
                agent = agents[agent_type]
                agent["is_active"] = True
                agent["last_activity"] = datetime.now()
                agent["task_count"] += 1
                active_agents.add(agent_type)
                
                logger.info(f"🚀 Агент {agent_type} активирован: {message[:50]}...")
                
                return {
                    "success": True,
                    "response": {
                        "response": f"Агент {agent['name']} получил сообщение: {message}",
                        "status": "processed"
                    },
                    "agent": agent["name"],
                    "agent_type": agent_type,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Отправляем первому доступному агенту
                if agents:
                    first_agent_type = list(agents.keys())[0]
                    agent = agents[first_agent_type]
                    agent["is_active"] = True
                    agent["last_activity"] = datetime.now()
                    agent["task_count"] += 1
                    active_agents.add(first_agent_type)
                    
                    logger.info(f"🚀 Агент {first_agent_type} активирован: {message[:50]}...")
                    
                    return {
                        "success": True,
                        "response": {
                            "response": f"Сообщение отправлено агенту {agent['name']}",
                            "status": "processed"
                        },
                        "agent": agent["name"],
                        "agent_type": first_agent_type,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {"error": "No agents available"}
                    
    except Exception as e:
        logger.error(f"❌ Ошибка отправки сообщения агенту: {e}")
        return {"error": str(e)}

async def autonomous_task_generator():
    """Генератор автономных задач"""
    global system_running, agents, active_agents, task_counter
    
    logger.info("🚀 Запуск генератора автономных задач...")
    
    while system_running:
        try:
            # Выбираем случайного агента
            if agents:
                agent_type = random.choice(list(agents.keys()))
                agent = agents[agent_type]
                
                if agent_type in autonomous_tasks:
                    tasks = autonomous_tasks[agent_type]
                    task = random.choice(tasks)
                    
                    # Активируем агента
                    with lock:
                        agent["is_active"] = True
                        agent["last_activity"] = datetime.now()
                        agent["task_count"] += 1
                        agent["status"] = "working"
                        active_agents.add(agent_type)
                        task_counter += 1
                    
                    logger.info(f"📋 Автономная задача #{task_counter} отправлена агенту {agent_type}: {task[:50]}...")
                    
                    # Имитируем работу агента
                    await asyncio.sleep(random.uniform(5, 15))
                    
                    # Деактивируем агента
                    with lock:
                        agent["is_active"] = False
                        agent["status"] = "idle"
                        if agent_type in active_agents:
                            active_agents.remove(agent_type)
                    
                    logger.info(f"✅ Агент {agent_type} завершил задачу")
            
            # Ждем 30-60 секунд перед следующей задачей
            await asyncio.sleep(random.uniform(30, 60))
            
        except Exception as e:
            logger.error(f"❌ Ошибка в генераторе автономных задач: {e}")
            await asyncio.sleep(10)

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    global system_running
    try:
        logger.info("🚀 Запуск простой рабочей системы...")
        
        # Инициализируем агентов
        initialize_agents()
        
        # Запускаем систему
        system_running = True
        
        # Запускаем генератор автономных задач
        asyncio.create_task(autonomous_task_generator())
        
        logger.info("✅ Простая рабочая система запущена")
        
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при завершении"""
    global system_running
    try:
        logger.info("🛑 Остановка простой рабочей системы...")
        system_running = False
        logger.info("✅ Простая рабочая система остановлена")
    except Exception as e:
        logger.error(f"❌ Ошибка остановки: {e}")

@app.get("/")
async def root():
    """Главная страница с чатом"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Multi-AI Chat System</title>
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
                background: #fafafa;
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
                word-wrap: break-word;
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
            .system-message {
                background: #e3f2fd;
                color: #1976d2;
                text-align: center;
                margin: 10px auto;
                max-width: 60%;
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
                <h1>🤖 Multi-AI Chat System</h1>
                <p>Чат с автономными агентами</p>
            </div>
            
            <div class="chat-container">
                <div class="chat-messages" id="chatMessages">
                    <div class="message system-message">
                        <strong>Система:</strong> Добро пожаловать в Multi-AI чат! Агенты работают автономно и готовы к общению.
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
            const chatMessages = document.getElementById('chatMessages');
            const messageInput = document.getElementById('messageInput');
            const agentSelect = document.getElementById('agentSelect');

            function addMessage(message, agent, isUser) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user-message' : 'agent-message'}`;
                messageDiv.innerHTML = `<strong>${agent}:</strong> ${message}`;
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }

            function updateSystemStatus() {
                fetch('/api/system/status')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('systemStatus').textContent = data.system_status === 'running' ? 'Работает' : 'Остановлена';
                        document.getElementById('totalAgents').textContent = data.total_agents || 0;
                        document.getElementById('activeAgents').textContent = data.active_agents || 0;
                        document.getElementById('uptime').textContent = data.uptime || '0м';
                    })
                    .catch(error => {
                        console.error('Ошибка получения статуса:', error);
                        document.getElementById('systemStatus').textContent = 'Ошибка';
                    });
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

            // Обновляем статус каждые 5 секунд
            updateSystemStatus();
            setInterval(updateSystemStatus, 5000);
        </script>
    </body>
    </html>
    """)

@app.post("/api/chat/send")
async def send_chat_message(message: ChatMessage):
    """Отправка сообщения агенту"""
    try:
        if not system_running:
            raise HTTPException(status_code=503, detail="System not running")
        
        # Отправляем сообщение агенту
        result = send_message_to_agent(
            message=message.message,
            agent_type=message.agent_type,
            user_id=message.user_id
        )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"❌ Ошибка отправки сообщения: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/status")
async def get_system_status_endpoint():
    """Получить статус системы"""
    try:
        status = await get_system_status()
        return JSONResponse(content=status)
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения статуса системы: {e}")
        return JSONResponse(content={
            "system_status": "error",
            "error": str(e)
        })

@app.get("/api/health")
async def health_check():
    """Проверка здоровья системы"""
    try:
        if not system_running:
            return JSONResponse(content={"status": "unhealthy", "reason": "System not running"})
        
        return JSONResponse(content={"status": "healthy"})
        
    except Exception as e:
        logger.error(f"❌ Ошибка проверки здоровья: {e}")
        return JSONResponse(content={"status": "unhealthy", "reason": str(e)})

if __name__ == "__main__":
    uvicorn.run(
        "simple_working_system:app",
        host="0.0.0.0",
        port=8080,
        reload=False,
        log_level="info"
    )
