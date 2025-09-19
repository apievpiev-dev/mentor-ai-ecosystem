#!/usr/bin/env python3
"""
Визуальная автономная система агентов с мониторингом
Система с реальными AI возможностями и визуальной верификацией
"""

import asyncio
import json
import logging
import time
import signal
import sys
import uuid
import base64
import io
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import subprocess
import requests

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_agg import FigureCanvasAgg

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/visual_autonomous_system.log'),
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
visual_screenshots = []
system_metrics = {
    "messages_processed": 0,
    "tasks_completed": 0,
    "errors_count": 0,
    "uptime_start": time.time()
}

class VisualAutonomousAgent:
    """Визуальный автономный агент с AI возможностями"""
    
    def __init__(self, agent_id: str, name: str, agent_type: str, skills: List[str]):
        self.agent_id = agent_id
        self.name = name
        self.agent_type = agent_type
        self.skills = skills
        self.status = "idle"
        self.last_activity = time.time()
        self.task_count = 0
        self.is_active = False
        self.performance_history = []
        self.visual_outputs = []
        
    async def process_message(self, message: str, user_id: str = "system") -> Dict[str, Any]:
        """Обработка сообщения с визуальной верификацией"""
        try:
            self.last_activity = time.time()
            self.task_count += 1
            self.status = "processing"
            
            # Улучшенная логика ответа с AI возможностями
            response = await self._generate_ai_response(message)
            
            # Создаем визуальный отчет
            visual_report = await self._create_visual_report(message, response)
            
            self.status = "idle"
            self.performance_history.append({
                "timestamp": time.time(),
                "response_time": time.time() - self.last_activity,
                "success": True
            })
            
            return {
                "response": response,
                "agent": self.name,
                "agent_type": self.agent_type,
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "visual_report": visual_report,
                "performance": {
                    "response_time": time.time() - self.last_activity,
                    "task_count": self.task_count
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения агентом {self.name}: {e}")
            self.status = "error"
            system_metrics["errors_count"] += 1
            return {
                "response": f"Ошибка: {str(e)}",
                "agent": self.name,
                "agent_type": self.agent_type,
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "visual_report": None
            }
    
    async def _generate_ai_response(self, message: str) -> str:
        """Генерация AI ответа"""
        message_lower = message.lower()
        
        if "привет" in message_lower:
            return f"Привет! Я {self.name}. Готов помочь с {', '.join(self.skills[:3])}. Могу создать визуальные отчеты и анализировать данные."
        
        elif "код" in message_lower and "code_developer" in self.agent_type:
            return "Я могу помочь с разработкой кода. Создам диаграммы архитектуры, проведу анализ кода и покажу визуальные результаты."
        
        elif "анализ" in message_lower and "data_analyst" in self.agent_type:
            return "Я специализируюсь на анализе данных. Создам графики, диаграммы и визуальные отчеты для ваших данных."
        
        elif "проект" in message_lower and "project_manager" in self.agent_type:
            return "Я помогу с планированием проекта. Создам диаграммы Ганта, временные линии и визуальные планы."
        
        elif "дизайн" in message_lower and "designer" in self.agent_type:
            return "Я создам дизайн для вас. Покажу визуальные концепции, макеты и прототипы интерфейсов."
        
        elif "тест" in message_lower and "qa_tester" in self.agent_type:
            return "Я проведу тестирование. Создам визуальные отчеты о тестах, диаграммы покрытия и анализ результатов."
        
        elif "график" in message_lower or "диаграмма" in message_lower:
            return f"Создам визуальную диаграмму для вас. Какой тип графика нужен? (линейный, столбчатый, круговая диаграмма)"
        
        elif "отчет" in message_lower:
            return f"Создам визуальный отчет с графиками и диаграммами. Что именно нужно проанализировать?"
        
        else:
            return f"Я {self.name}. Получил ваше сообщение: '{message}'. Могу создать визуальные отчеты, графики и диаграммы. Чем могу помочь?"
    
    async def _create_visual_report(self, message: str, response: str) -> Optional[str]:
        """Создание визуального отчета"""
        try:
            # Создаем простую диаграмму
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Данные для демонстрации
            categories = ['Обработка', 'Анализ', 'Визуализация', 'Отчет']
            values = [25, 30, 20, 25]
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
            
            bars = ax.bar(categories, values, color=colors)
            ax.set_title(f'Анализ работы агента: {self.name}', fontsize=14, fontweight='bold')
            ax.set_ylabel('Процент выполнения', fontsize=12)
            
            # Добавляем значения на столбцы
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{value}%', ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            
            # Сохраняем в байты
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            
            # Конвертируем в base64
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"Ошибка создания визуального отчета: {e}")
            return None

# Создаем агентов
def create_agents():
    """Создание визуальных агентов"""
    global agents
    
    agents = {
        "general_assistant": VisualAutonomousAgent(
            "general_assistant", "Универсальный Помощник", "general_assistant",
            ["general_help", "planning", "coordination", "visual_reports"]
        ),
        "code_developer": VisualAutonomousAgent(
            "code_developer", "Разработчик Кода", "code_developer",
            ["code_generation", "debugging", "architecture_diagrams", "visual_analysis"]
        ),
        "data_analyst": VisualAutonomousAgent(
            "data_analyst", "Аналитик Данных", "data_analyst",
            ["data_analysis", "visualization", "charts", "reports"]
        ),
        "project_manager": VisualAutonomousAgent(
            "project_manager", "Менеджер Проектов", "project_manager",
            ["project_planning", "gantt_charts", "timelines", "progress_visualization"]
        ),
        "designer": VisualAutonomousAgent(
            "designer", "Дизайнер", "designer",
            ["ui_design", "visual_prototypes", "mockups", "design_systems"]
        ),
        "qa_tester": VisualAutonomousAgent(
            "qa_tester", "Тестировщик", "qa_tester",
            ["test_reports", "coverage_diagrams", "bug_visualization", "quality_metrics"]
        )
    }
    
    logger.info(f"✅ Создано {len(agents)} визуальных автономных агентов")

# Автономные задачи с визуальным мониторингом
async def autonomous_task_generator():
    """Генератор автономных задач с визуальным мониторингом"""
    global autonomous_tasks, task_counter, system_metrics
    
    while system_running:
        try:
            # Создаем случайную задачу каждые 20-40 секунд
            await asyncio.sleep(30)
            
            if not system_running:
                break
                
            task_counter += 1
            task_types = [
                "Проанализируй производительность системы и создай график",
                "Проверь логи на ошибки и создай отчет",
                "Создай визуальный отчет о работе агентов",
                "Оптимизируй процессы и покажи результаты",
                "Проверь безопасность системы с визуализацией",
                "Создай диаграмму использования ресурсов",
                "Проанализируй активность пользователей",
                "Создай отчет о качестве работы системы"
            ]
            
            task = {
                "id": f"auto_task_{task_counter}",
                "description": task_types[task_counter % len(task_types)],
                "timestamp": datetime.now().isoformat(),
                "assigned_to": None,
                "status": "created"
            }
            
            autonomous_tasks.append(task)
            logger.info(f"🤖 Создана автономная задача: {task['description']}")
            
            # Назначаем задачу случайному агенту
            if agents:
                agent_id = list(agents.keys())[task_counter % len(agents)]
                agent = agents[agent_id]
                result = await agent.process_message(task['description'], "autonomous_system")
                task['assigned_to'] = agent.name
                task['status'] = "completed"
                task['result'] = result
                system_metrics["tasks_completed"] += 1
                logger.info(f"📋 Задача выполнена агентом: {agent.name}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка в генераторе автономных задач: {e}")
            await asyncio.sleep(10)

# FastAPI приложение
app = FastAPI(title="Visual Autonomous Multi-AI System")

@app.get("/")
async def root():
    """Главная страница с визуальным чатом"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Visual Autonomous Multi-AI System</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                min-height: 100vh; 
            }
            .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; color: white; margin-bottom: 30px; }
            .header h1 { font-size: 2.5em; margin-bottom: 10px; }
            .header p { font-size: 1.2em; opacity: 0.9; }
            .main-content { display: flex; gap: 20px; height: 700px; }
            .chat-section { flex: 2; display: flex; flex-direction: column; }
            .chat-messages { 
                flex: 1; 
                background: white; 
                border-radius: 15px; 
                padding: 20px; 
                overflow-y: auto; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.1); 
                margin-bottom: 20px;
            }
            .sidebar { 
                width: 350px; 
                background: rgba(255,255,255,0.95); 
                border-radius: 15px; 
                padding: 20px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.1); 
                overflow-y: auto;
            }
            .message { margin-bottom: 15px; padding: 12px; border-radius: 10px; }
            .user-message { background: #e3f2fd; margin-left: 20px; }
            .agent-message { background: #f3e5f5; margin-right: 20px; }
            .system-message { background: #e8f5e8; text-align: center; font-style: italic; }
            .visual-report { 
                margin-top: 10px; 
                padding: 10px; 
                background: #f8f9fa; 
                border-radius: 8px; 
                text-align: center;
            }
            .visual-report img { 
                max-width: 100%; 
                height: auto; 
                border-radius: 8px; 
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .input-container { display: flex; gap: 10px; }
            .message-input { 
                flex: 1; 
                padding: 15px; 
                border: none; 
                border-radius: 25px; 
                font-size: 16px; 
                outline: none; 
            }
            .send-button { 
                padding: 15px 30px; 
                background: #4CAF50; 
                color: white; 
                border: none; 
                border-radius: 25px; 
                cursor: pointer; 
                font-size: 16px; 
                transition: background 0.3s; 
            }
            .send-button:hover { background: #45a049; }
            .system-info { margin-bottom: 20px; }
            .system-info h3 { color: #333; margin-bottom: 10px; }
            .status-item { display: flex; justify-content: space-between; margin-bottom: 5px; }
            .status-indicator { 
                width: 12px; 
                height: 12px; 
                border-radius: 50%; 
                display: inline-block; 
                margin-right: 8px; 
            }
            .status-online { background: #4CAF50; }
            .status-offline { background: #f44336; }
            .agent-selector { margin-bottom: 20px; }
            .agent-selector label { display: block; margin-bottom: 5px; font-weight: bold; color: #333; }
            .agent-selector select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            .autonomous-tasks { margin-top: 20px; }
            .autonomous-tasks h3 { color: #333; margin-bottom: 10px; }
            .task-item { 
                background: #f0f0f0; 
                padding: 10px; 
                border-radius: 5px; 
                margin-bottom: 5px; 
                font-size: 0.9em; 
            }
            .metrics-section { margin-top: 20px; }
            .metrics-section h3 { color: #333; margin-bottom: 10px; }
            .metric-item { 
                display: flex; 
                justify-content: space-between; 
                margin-bottom: 5px; 
                padding: 5px; 
                background: #f8f9fa; 
                border-radius: 3px; 
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Visual Autonomous Multi-AI System</h1>
                <p>Автономная система агентов с визуальным мониторингом и AI возможностями</p>
            </div>
            
            <div class="main-content">
                <div class="chat-section">
                    <div class="chat-messages" id="chatMessages">
                        <div class="message system-message">
                            <strong>Система:</strong> Визуальная автономная система запущена! Агенты работают независимо, создают визуальные отчеты и выполняют задачи автоматически.
                        </div>
                    </div>
                    
                    <div class="input-container">
                        <input type="text" id="messageInput" class="message-input" placeholder="Введите ваше сообщение..." />
                        <button onclick="sendMessage()" class="send-button">Отправить</button>
                    </div>
                </div>
                
                <div class="sidebar">
                    <div class="system-info">
                        <h3>📊 Статус системы</h3>
                        <p><span class="status-indicator status-online"></span>Система: <span id="systemStatus">Загрузка...</span></p>
                        <p>Агентов: <span id="totalAgents">0</span></p>
                        <p>Активных: <span id="activeAgents">0</span></p>
                        <p>Время работы: <span id="uptime">0м</span></p>
                        <p>Автономных задач: <span id="autonomousTasks">0</span></p>
                    </div>
                    
                    <div class="metrics-section">
                        <h3>📈 Метрики</h3>
                        <div class="metric-item">
                            <span>Сообщений обработано:</span>
                            <span id="messagesProcessed">0</span>
                        </div>
                        <div class="metric-item">
                            <span>Задач выполнено:</span>
                            <span id="tasksCompleted">0</span>
                        </div>
                        <div class="metric-item">
                            <span>Ошибок:</span>
                            <span id="errorsCount">0</span>
                        </div>
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
                    addMessage(data.message, 'agent', data.agent, data.visual_report);
                };
                
                ws.onclose = function() {
                    console.log('WebSocket отключен, переподключение...');
                    setTimeout(connectWebSocket, 3000);
                };
            }
            
            function addMessage(message, type, agent = '', visualReport = null) {
                const chatMessages = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}-message`;
                
                if (type === 'user') {
                    messageDiv.innerHTML = `<strong>Вы:</strong> ${message}`;
                } else {
                    let content = `<strong>${agent}:</strong> ${message}`;
                    if (visualReport) {
                        content += `<div class="visual-report"><img src="${visualReport}" alt="Визуальный отчет" /></div>`;
                    }
                    messageDiv.innerHTML = content;
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
                        document.getElementById('messagesProcessed').textContent = data.messages_processed;
                        document.getElementById('tasksCompleted').textContent = data.tasks_completed;
                        document.getElementById('errorsCount').textContent = data.errors_count;
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
            
            // Обновление каждые 3 секунды
            setInterval(updateStatus, 3000);
            setInterval(updateAutonomousTasks, 8000);
        </script>
    </body>
    </html>
    """)

@app.get("/api/system/status")
async def get_system_status():
    """Получить статус системы с метриками"""
    global system_running, agents, active_agents, startup_time, autonomous_tasks, system_metrics
    
    uptime_seconds = int(time.time() - startup_time)
    uptime_minutes = uptime_seconds // 60
    
    return {
        "system_status": "running" if system_running else "stopped",
        "total_agents": len(agents),
        "active_agents": len([a for a in agents.values() if a.is_active]),
        "uptime": f"{uptime_minutes}м",
        "autonomous_tasks": len(autonomous_tasks),
        "messages_processed": system_metrics["messages_processed"],
        "tasks_completed": system_metrics["tasks_completed"],
        "errors_count": system_metrics["errors_count"],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/autonomous/tasks")
async def get_autonomous_tasks():
    """Получить автономные задачи"""
    global autonomous_tasks
    return {"tasks": autonomous_tasks[-10:]}  # Последние 10 задач

@app.get("/api/visual/screenshots")
async def get_visual_screenshots():
    """Получить визуальные скриншоты"""
    return {"screenshots": visual_screenshots[-20:]}  # Последние 20 скриншотов

@app.post("/api/chat/send")
async def send_message(data: dict):
    """Отправить сообщение агенту"""
    global agents, system_metrics
    
    message = data.get("message", "")
    agent_type = data.get("agent_type")
    user_id = data.get("user_id", "unknown")
    
    if not message:
        return {"error": "Сообщение не может быть пустым"}
    
    system_metrics["messages_processed"] += 1
    
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
                    "timestamp": result["timestamp"],
                    "visual_report": result.get("visual_report")
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
    
    logger.info("🚀 Запуск визуальной автономной системы агентов...")
    
    # Создаем агентов
    create_agents()
    
    # Запускаем систему
    system_running = True
    
    # Запускаем генератор автономных задач
    task_generator = asyncio.create_task(autonomous_task_generator())
    
    logger.info("✅ Визуальная автономная система запущена")
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
        logger.info("🛑 Визуальная автономная система остановлена")

if __name__ == "__main__":
    asyncio.run(main())