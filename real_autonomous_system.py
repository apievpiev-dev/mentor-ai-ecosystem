#!/usr/bin/env python3
"""
Реальная автономная система агентов с AI
Полноценная система с настоящим искусственным интеллектом
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

# Импортируем AI движок
from ai_engine import OllamaEngine, AIResponse

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/mentor/real_autonomous_system.log'),
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
ai_engine = None

class RealAutonomousAgent:
    """Реальный автономный агент с AI"""
    
    def __init__(self, agent_id: str, name: str, agent_type: str, skills: List[str], ai_engine):
        self.agent_id = agent_id
        self.name = name
        self.agent_type = agent_type
        self.skills = skills
        self.status = "idle"
        self.last_activity = time.time()
        self.task_count = 0
        self.is_active = False
        self.ai_engine = ai_engine
        self.knowledge_base = []
        self.autonomous_thinking = True
        
    async def process_message(self, message: str, user_id: str = "system") -> Dict[str, Any]:
        """Обработка сообщения с использованием AI"""
        try:
            self.last_activity = time.time()
            self.task_count += 1
            self.status = "processing"
            self.is_active = True
            
            # Создаем контекст для AI
            context = f"""
            Ты - {self.name}, специализирующийся на {', '.join(self.skills)}.
            Твоя роль: {self._get_role_description()}
            
            Сообщение пользователя: {message}
            
            Ответь как профессиональный {self.name}, используя свои навыки.
            """
            
            # Получаем ответ от AI с оптимизированными параметрами
            if self.ai_engine:
                try:
                    logger.info(f"🤖 {self.name} обрабатывает сообщение через AI...")
                    
                    # Получаем AI ответ с оптимизированным таймаутом
                    ai_response = await asyncio.wait_for(
                        self.ai_engine.generate_response(
                            context, 
                            max_tokens=50,   # Очень короткие ответы
                            temperature=0.5  # Более предсказуемые ответы
                        ),
                        timeout=180.0  # Увеличенный таймаут для retry механизма
                    )
                    
                    if ai_response.success:
                        response = ai_response.content
                        logger.info(f"✅ {self.name} получил AI ответ: {len(response)} символов")
                    else:
                        response = f"❌ Ошибка AI: {ai_response.error}"
                        logger.error(f"❌ {self.name} ошибка AI: {ai_response.error}")
                        
                except asyncio.TimeoutError:
                    # Принудительный таймаут - возвращаем ошибку
                    response = "⏰ AI не успел ответить за 180 секунд"
                    logger.warning(f"⏰ {self.name} принудительный таймаут 180 сек")
                except Exception as e:
                    # Любая ошибка AI - возвращаем ошибку
                    response = f"❌ Ошибка AI: {str(e)}"
                    if "timeout" in str(e).lower() or "timed out" in str(e).lower():
                        logger.warning(f"⏰ {self.name} AI таймаут")
                    else:
                        logger.error(f"❌ {self.name} ошибка AI: {e}")
            else:
                response = "❌ AI движок недоступен"
                logger.warning(f"⚠️ {self.name} AI движок недоступен")
            
            # Сохраняем в базу знаний
            self.knowledge_base.append({
                "message": message,
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id
            })
            
            self.status = "idle"
            # Агент остается активным для автономной работы
            self.is_active = True
            
            return {
                "response": response,
                "agent": self.name,
                "agent_type": self.agent_type,
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "ai_used": self.ai_engine is not None
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения агентом {self.name}: {e}")
            self.status = "error"
            self.is_active = False
            return {
                "response": f"Ошибка: {str(e)}",
                "agent": self.name,
                "agent_type": self.agent_type,
                "timestamp": datetime.now().isoformat(),
                "success": False
            }
    
    def _get_role_description(self) -> str:
        """Получить описание роли агента"""
        role_descriptions = {
            "general_assistant": "универсальный помощник, который может помочь с любыми вопросами и координировать работу других агентов",
            "code_developer": "эксперт по разработке программного обеспечения, знающий множество языков программирования и технологий",
            "data_analyst": "специалист по анализу данных, статистике, машинному обучению и визуализации данных",
            "project_manager": "опытный менеджер проектов, специализирующийся на планировании, управлении ресурсами и координации команд",
            "designer": "креативный дизайнер с опытом в UI/UX дизайне, создании визуальной идентичности и пользовательских интерфейсов",
            "qa_tester": "эксперт по тестированию программного обеспечения, знающий различные методологии и инструменты тестирования"
        }
        return role_descriptions.get(self.agent_type, "специалист в своей области")
    
    def _get_fallback_response(self, message: str) -> str:
        """Быстрый fallback ответ без AI"""
        if self.agent_type == "general_assistant":
            return f"Привет! Я {self.name}. Получил ваше сообщение: '{message}'. Готов помочь с любыми вопросами!"
        
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
    
    async def autonomous_think(self) -> Optional[str]:
        """Автономное мышление агента"""
        if not self.autonomous_thinking:
            return None
            
        try:
            # Агент сам генерирует идеи и предложения
            thinking_prompts = [
                f"{self.name}: улучшение.",
                f"{self.name}: задача.",
                f"{self.name}: оптимизация.",
                f"{self.name}: идея."
            ]
            
            prompt = thinking_prompts[self.task_count % len(thinking_prompts)]
            
            if self.ai_engine:
                ai_response = await self.ai_engine.generate_response(prompt)
                if ai_response.success:
                    return ai_response.content
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Ошибка автономного мышления агента {self.name}: {e}")
            return None

# Создаем агентов с AI
async def create_ai_agents():
    """Создание агентов с AI"""
    global agents, ai_engine
    
    # Инициализируем AI движок
    ai_engine = OllamaEngine()
    
    agents = {
        "general_assistant": RealAutonomousAgent(
            "general_assistant", "Универсальный Помощник", "general_assistant",
            ["general_help", "planning", "coordination", "user_query"], ai_engine
        ),
        "code_developer": RealAutonomousAgent(
            "code_developer", "Разработчик Кода", "code_developer",
            ["code_generation", "debugging", "code_review", "architecture_design"], ai_engine
        ),
        "data_analyst": RealAutonomousAgent(
            "data_analyst", "Аналитик Данных", "data_analyst",
            ["data_analysis", "reporting", "visualization", "predictive_modeling"], ai_engine
        ),
        "project_manager": RealAutonomousAgent(
            "project_manager", "Менеджер Проектов", "project_manager",
            ["project_planning", "task_management", "resource_allocation", "progress_tracking"], ai_engine
        ),
        "designer": RealAutonomousAgent(
            "designer", "Дизайнер", "designer",
            ["ui_design", "ux_design", "visual_identity"], ai_engine
        ),
        "qa_tester": RealAutonomousAgent(
            "qa_tester", "Тестировщик", "qa_tester",
            ["unit_testing", "integration_testing", "bug_reporting"], ai_engine
        )
    }
    
    logger.info(f"✅ Создано {len(agents)} AI агентов с реальным интеллектом")
    
    # Активируем всех агентов
    for agent in agents.values():
        agent.is_active = True
        agent.status = "active"
    
    logger.info("🚀 Все агенты активированы для автономной работы")

# Автономные задачи с AI
async def ai_autonomous_task_generator():
    """Генератор автономных задач с AI"""
    global autonomous_tasks, task_counter, agents
    
    while system_running:
        try:
            # Создаем задачи каждые 300 секунд для стабильной работы
            await asyncio.sleep(300)
            
            if not system_running:
                break
                
            task_counter += 1
            
            # Выбираем случайного агента для генерации задачи
            if agents:
                agent_id = list(agents.keys())[task_counter % len(agents)]
                agent = agents[agent_id]
                
                # Агент сам генерирует задачу
                autonomous_idea = await agent.autonomous_think()
                
                if autonomous_idea:
                    task = {
                        "id": f"ai_task_{task_counter}",
                        "description": autonomous_idea,
                        "timestamp": datetime.now().isoformat(),
                        "assigned_to": agent.name,
                        "generated_by": "AI",
                        "status": "assigned"
                    }
                    
                    autonomous_tasks.append(task)
                    logger.info(f"🤖 AI агент {agent.name} сгенерировал задачу: {autonomous_idea[:100]}...")
                    
                    # Агент сразу начинает выполнять задачу
                    await agent.process_message(autonomous_idea, "autonomous_ai")
                    task["status"] = "completed"
                    logger.info(f"✅ AI агент {agent.name} выполнил задачу")
            
        except Exception as e:
            logger.error(f"❌ Ошибка в AI генераторе автономных задач: {e}")
            await asyncio.sleep(15)

# FastAPI приложение
app = FastAPI(title="Real Autonomous AI System")

@app.get("/")
async def root():
    """Главная страница с чатом"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Real Autonomous AI System</title>
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
            .ai-message { background: #fff3e0; border-left: 4px solid #ff9800; }
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
            .ai-task { background: #fff3e0; border-left: 3px solid #ff9800; }
            .system-logs { margin-top: 20px; }
            .system-logs h3 { color: #333; margin-bottom: 10px; }
            .logs-container { max-height: 300px; overflow-y: auto; background: #f8f9fa; border-radius: 5px; padding: 10px; }
            .log-entry { margin-bottom: 8px; padding: 8px; border-radius: 3px; font-size: 0.85em; font-family: monospace; }
            .log-info { background: #e3f2fd; border-left: 3px solid #2196f3; }
            .log-warning { background: #fff3e0; border-left: 3px solid #ff9800; }
            .log-error { background: #ffebee; border-left: 3px solid #f44336; }
            .log-timestamp { color: #666; font-size: 0.8em; }
            .log-message { margin-top: 2px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 Real Autonomous AI System</h1>
                <p>Система с настоящим искусственным интеллектом и автономностью</p>
            </div>
            
            <div class="chat-container">
                <div class="chat-messages" id="chatMessages">
                    <div class="message system-message">
                        <strong>Система:</strong> Реальная AI система запущена! Агенты думают автономно и генерируют собственные идеи.
                    </div>
                </div>
                
                <div class="chat-sidebar">
                    <div class="system-info">
                        <h3>📊 Статус AI системы</h3>
                        <p><span class="status-indicator status-online"></span>Система: <span id="systemStatus">Загрузка...</span></p>
                        <p>AI агентов: <span id="totalAgents">0</span></p>
                        <p>Активных: <span id="activeAgents">0</span></p>
                        <p>Время работы: <span id="uptime">0м</span></p>
                        <p>AI задач: <span id="autonomousTasks">0</span></p>
                        <p>AI движок: <span id="aiEngine">Проверка...</span></p>
                    </div>
                    
                    <div class="agent-selector">
                        <label for="agentSelect"><strong>Выберите AI агента:</strong></label>
                        <select id="agentSelect">
                            <option value="">Автоматический выбор</option>
                            <option value="general_assistant">🧠 Универсальный Помощник</option>
                            <option value="code_developer">💻 Разработчик Кода</option>
                            <option value="data_analyst">📊 Аналитик Данных</option>
                            <option value="project_manager">📋 Менеджер Проектов</option>
                            <option value="designer">🎨 Дизайнер</option>
                            <option value="qa_tester">🔍 Тестировщик</option>
                        </select>
                    </div>
                    
                    <div class="autonomous-tasks">
                        <h3>🧠 AI Автономные задачи</h3>
                        <div id="autonomousTasksList">
                            <div class="task-item">AI агенты генерируют собственные идеи...</div>
                        </div>
                    </div>
                    
                    <div class="system-logs">
                        <h3>📋 Единый лог действий</h3>
                        <div class="logs-container" id="systemLogsList">
                            <div class="log-entry log-info">
                                <div class="log-timestamp">Загрузка логов...</div>
                                <div class="log-message">Подключение к системе логов</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="input-container">
                <input type="text" id="messageInput" class="message-input" placeholder="Задайте вопрос AI агенту..." />
                <button onclick="sendMessage()" class="send-button">Отправить</button>
            </div>
        </div>

        <script>
            let ws = null;
            let userId = 'user_' + Math.random().toString(36).substr(2, 9);
            
            function connectWebSocket() {
                ws = new WebSocket(`ws://${window.location.host}/ws/${userId}`);
                
                ws.onopen = function() {
                    console.log('WebSocket подключен к AI системе');
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    addMessage(data.message, 'agent', data.agent, data.ai_used);
                };
                
                ws.onclose = function() {
                    console.log('WebSocket отключен, переподключение...');
                    setTimeout(connectWebSocket, 3000);
                };
            }
            
            function addMessage(message, type, agent = '', ai_used = false) {
                const chatMessages = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                
                if (type === 'user') {
                    messageDiv.className = 'message user-message';
                    messageDiv.innerHTML = `<strong>Вы:</strong> ${message}`;
                } else {
                    messageDiv.className = ai_used ? 'message ai-message' : 'message agent-message';
                    const aiBadge = ai_used ? ' 🧠' : '';
                    messageDiv.innerHTML = `<strong>${agent}${aiBadge}:</strong> ${message}`;
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
                        document.getElementById('aiEngine').textContent = data.ai_engine_status;
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
                            tasksList.innerHTML = '<div class="task-item">AI агенты думают...</div>';
                        } else {
                            data.tasks.slice(-5).forEach(task => {
                                const taskDiv = document.createElement('div');
                                taskDiv.className = task.generated_by === 'AI' ? 'task-item ai-task' : 'task-item';
                                taskDiv.innerHTML = `<strong>${task.description}</strong><br><small>AI: ${task.assigned_to} | Статус: ${task.status}</small>`;
                                tasksList.appendChild(taskDiv);
                            });
                        }
                    })
                    .catch(error => console.error('Ошибка обновления задач:', error));
            }
            
            function updateSystemLogs() {
                fetch('/api/logs')
                    .then(response => response.json())
                    .then(data => {
                        const logsList = document.getElementById('systemLogsList');
                        logsList.innerHTML = '';
                        
                        if (data.logs && data.logs.length > 0) {
                            data.logs.slice(-15).forEach(log => {
                                const logDiv = document.createElement('div');
                                
                                // Определяем класс в зависимости от уровня лога
                                let logClass = 'log-info';
                                if (log.level === 'WARNING') logClass = 'log-warning';
                                if (log.level === 'ERROR') logClass = 'log-error';
                                
                                logDiv.className = `log-entry ${logClass}`;
                                
                                // Форматируем время
                                const time = log.timestamp ? log.timestamp.split(' ')[1] : '';
                                
                                logDiv.innerHTML = `
                                    <div class="log-timestamp">${time} [${log.level}]</div>
                                    <div class="log-message">${log.message}</div>
                                `;
                                
                                logsList.appendChild(logDiv);
                            });
                            
                            // Прокручиваем к последнему логу
                            logsList.scrollTop = logsList.scrollHeight;
                        } else {
                            logsList.innerHTML = '<div class="log-entry log-info"><div class="log-message">Логи загружаются...</div></div>';
                        }
                    })
                    .catch(error => {
                        console.error('Ошибка обновления логов:', error);
                        const logsList = document.getElementById('systemLogsList');
                        logsList.innerHTML = '<div class="log-entry log-error"><div class="log-message">Ошибка загрузки логов</div></div>';
                    });
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
            updateSystemLogs();
            
            // Обновление каждые 5 секунд для снижения нагрузки
            setInterval(updateStatus, 5000);
            setInterval(updateAutonomousTasks, 8000);
            setInterval(updateSystemLogs, 10000);
        </script>
    </body>
    </html>
    """)

@app.get("/api/system/status")
async def get_system_status():
    """Получить статус AI системы"""
    global system_running, agents, active_agents, startup_time, autonomous_tasks, ai_engine
    
    uptime_seconds = int(time.time() - startup_time)
    uptime_minutes = uptime_seconds // 60
    
    # Подсчитываем активных агентов (всегда активны в автономной системе)
    active_count = len(agents) if agents else 0
    
    # Получаем детальный статус AI движка
    ai_health = {}
    if ai_engine:
        ai_health = ai_engine.get_health_status()
    
    return {
        "system_status": "running" if system_running else "stopped",
        "total_agents": len(agents),
        "active_agents": active_count,
        "uptime": f"{uptime_minutes}м",
        "autonomous_tasks": len(autonomous_tasks),
        "ai_engine_status": "connected" if ai_engine and ai_engine.is_available() else "disconnected",
        "ai_health": ai_health,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/autonomous/tasks")
async def get_autonomous_tasks():
    """Получить AI автономные задачи"""
    global autonomous_tasks
    return {"tasks": autonomous_tasks[-10:]}  # Последние 10 задач

@app.get("/api/logs")
async def get_system_logs():
    """Получить единый лог действий системы"""
    try:
        # Читаем последние 100 строк из лога
        with open('/home/mentor/real_autonomous_system.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            recent_logs = lines[-100:] if len(lines) > 100 else lines
        
        # Парсим логи в структурированный формат
        parsed_logs = []
        for line in recent_logs:
            if line.strip():
                # Парсим формат: 2025-09-19 01:36:13,845 - __main__ - INFO - ✅ Универсальный Помощник получил AI ответ: 593 символов
                parts = line.strip().split(' - ', 3)
                if len(parts) >= 4:
                    timestamp = parts[0]
                    module = parts[1]
                    level = parts[2]
                    message = parts[3]
                    
                    parsed_logs.append({
                        "timestamp": timestamp,
                        "module": module,
                        "level": level,
                        "message": message,
                        "raw": line.strip()
                    })
                else:
                    parsed_logs.append({
                        "timestamp": "",
                        "module": "system",
                        "level": "INFO",
                        "message": line.strip(),
                        "raw": line.strip()
                    })
        
        return {
            "logs": parsed_logs,
            "total_count": len(parsed_logs),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Ошибка чтения логов: {e}")
        return {"error": str(e), "logs": []}

@app.post("/api/chat/send")
async def send_message(data: dict):
    """Отправить сообщение AI агенту"""
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
        agent = list(agents.values())[0]
    
    # Обрабатываем сообщение с AI
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
                    "timestamp": result["timestamp"],
                    "ai_used": result.get("ai_used", False)
                }))
            else:
                await websocket.send_text(json.dumps({
                    "message": "Ошибка обработки сообщения",
                    "agent": "System",
                    "timestamp": datetime.now().isoformat(),
                    "ai_used": False
                }))
                
    except WebSocketDisconnect:
        logger.info(f"🔌 Пользователь {user_id} отключился от AI WebSocket")

# Основная функция
async def main():
    """Главная функция"""
    global system_running
    
    logger.info("🧠 Запуск реальной автономной AI системы...")
    
    # Создаем AI агентов
    await create_ai_agents()
    
    # Запускаем систему
    system_running = True
    
    # Запускаем AI генератор автономных задач
    ai_task_generator = asyncio.create_task(ai_autonomous_task_generator())
    
    logger.info("✅ Реальная AI система запущена")
    logger.info("🌐 Веб-интерфейс доступен на http://0.0.0.0:8081")
    
    try:
        # Запускаем веб-сервер
        config = uvicorn.Config(app, host="0.0.0.0", port=8081, log_level="info")
        server = uvicorn.Server(config)
        
        # Запускаем сервер в фоне
        server_task = asyncio.create_task(server.serve())
        
        # Ждем завершения сервера
        await server_task
        
    except KeyboardInterrupt:
        logger.info("📡 Получен сигнал прерывания")
    except Exception as e:
        logger.error(f"❌ Ошибка веб-сервера: {e}")
    finally:
        system_running = False
        ai_task_generator.cancel()
        logger.info("🛑 Реальная AI система остановлена")

if __name__ == "__main__":
    asyncio.run(main())
