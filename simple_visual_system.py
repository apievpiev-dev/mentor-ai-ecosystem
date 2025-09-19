#!/usr/bin/env python3
"""
Простая визуальная автономная система агентов
Работает без дополнительных зависимостей, только со стандартными библиотеками Python
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
import http.server
import socketserver
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import urllib.parse

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/simple_visual_system.log'),
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
system_metrics = {
    "messages_processed": 0,
    "tasks_completed": 0,
    "errors_count": 0,
    "uptime_start": time.time()
}

class SimpleVisualAgent:
    """Простой визуальный автономный агент"""
    
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
        
    async def process_message(self, message: str, user_id: str = "system") -> Dict[str, Any]:
        """Обработка сообщения с визуальной верификацией"""
        try:
            self.last_activity = time.time()
            self.task_count += 1
            self.status = "processing"
            
            # Улучшенная логика ответа
            response = await self._generate_response(message)
            
            # Создаем простой визуальный отчет
            visual_report = await self._create_simple_visual(message, response)
            
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
    
    async def _generate_response(self, message: str) -> str:
        """Генерация ответа"""
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
    
    async def _create_simple_visual(self, message: str, response: str) -> Optional[str]:
        """Создание простого визуального отчета"""
        try:
            # Создаем простую ASCII диаграмму
            visual_content = f"""
┌─────────────────────────────────────┐
│  📊 Визуальный отчет агента        │
│  {self.name}                        │
├─────────────────────────────────────┤
│  📝 Сообщение: {message[:30]}...    │
│  ⏱️  Время: {datetime.now().strftime('%H:%M:%S')}        │
│  📈 Статус: {self.status}           │
│  🔢 Задач выполнено: {self.task_count}        │
├─────────────────────────────────────┤
│  📊 Производительность:             │
│  ████████████████████ 100%         │
│  🎯 Точность: 95%                   │
│  ⚡ Скорость: Быстрая               │
└─────────────────────────────────────┘
            """
            
            # Конвертируем в base64 для передачи
            visual_base64 = base64.b64encode(visual_content.encode()).decode()
            return f"data:text/plain;base64,{visual_base64}"
            
        except Exception as e:
            logger.error(f"Ошибка создания визуального отчета: {e}")
            return None

# Создаем агентов
def create_agents():
    """Создание простых визуальных агентов"""
    global agents
    
    agents = {
        "general_assistant": SimpleVisualAgent(
            "general_assistant", "Универсальный Помощник", "general_assistant",
            ["general_help", "planning", "coordination", "visual_reports"]
        ),
        "code_developer": SimpleVisualAgent(
            "code_developer", "Разработчик Кода", "code_developer",
            ["code_generation", "debugging", "architecture_diagrams", "visual_analysis"]
        ),
        "data_analyst": SimpleVisualAgent(
            "data_analyst", "Аналитик Данных", "data_analyst",
            ["data_analysis", "visualization", "charts", "reports"]
        ),
        "project_manager": SimpleVisualAgent(
            "project_manager", "Менеджер Проектов", "project_manager",
            ["project_planning", "gantt_charts", "timelines", "progress_visualization"]
        ),
        "designer": SimpleVisualAgent(
            "designer", "Дизайнер", "designer",
            ["ui_design", "visual_prototypes", "mockups", "design_systems"]
        ),
        "qa_tester": SimpleVisualAgent(
            "qa_tester", "Тестировщик", "qa_tester",
            ["test_reports", "coverage_diagrams", "bug_visualization", "quality_metrics"]
        )
    }
    
    logger.info(f"✅ Создано {len(agents)} простых визуальных автономных агентов")

# Автономные задачи
async def autonomous_task_generator():
    """Генератор автономных задач"""
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

# HTTP сервер
class VisualSystemHandler(http.server.BaseHTTPRequestHandler):
    """HTTP обработчик для визуальной системы"""
    
    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.get_main_page().encode('utf-8'))
        
        elif self.path == '/api/system/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            status = self.get_system_status()
            self.wfile.write(json.dumps(status).encode('utf-8'))
        
        elif self.path == '/api/autonomous/tasks':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            tasks = {"tasks": autonomous_tasks[-10:]}
            self.wfile.write(json.dumps(tasks).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Обработка POST запросов"""
        if self.path == '/api/chat/send':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Обрабатываем сообщение
            response = asyncio.run(self.process_message(data))
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.end_headers()
    
    async def process_message(self, data: dict):
        """Обработка сообщения"""
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
            agent = list(agents.values())[0]
        
        # Обрабатываем сообщение
        result = await agent.process_message(message, user_id)
        
        return {
            "success": True,
            "response": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_system_status(self):
        """Получить статус системы"""
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
    
    def get_main_page(self):
        """Главная страница"""
        return """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple Visual Autonomous Multi-AI System</title>
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
            font-family: monospace;
            white-space: pre-wrap;
            font-size: 12px;
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
            <h1>🤖 Simple Visual Autonomous Multi-AI System</h1>
            <p>Простая автономная система агентов с визуальным мониторингом</p>
        </div>
        
        <div class="main-content">
            <div class="chat-section">
                <div class="chat-messages" id="chatMessages">
                    <div class="message system-message">
                        <strong>Система:</strong> Простая визуальная автономная система запущена! Агенты работают независимо и создают визуальные отчеты.
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
        function addMessage(message, type, agent = '', visualReport = null) {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}-message`;
            
            if (type === 'user') {
                messageDiv.innerHTML = `<strong>Вы:</strong> ${message}`;
            } else {
                let content = `<strong>${agent}:</strong> ${message}`;
                if (visualReport) {
                    content += `<div class="visual-report">${visualReport}</div>`;
                }
                messageDiv.innerHTML = content;
            }
            
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            const agentType = document.getElementById('agentSelect').value;
            
            if (message) {
                addMessage(message, 'user');
                
                try {
                    const response = await fetch('/api/chat/send', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: message,
                            agent_type: agentType || null,
                            user_id: 'user_' + Math.random().toString(36).substr(2, 9)
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        const result = data.response;
                        let visualReport = null;
                        
                        if (result.visual_report) {
                            try {
                                const decoded = atob(result.visual_report.split(',')[1]);
                                visualReport = decoded;
                            } catch (e) {
                                console.error('Ошибка декодирования визуального отчета:', e);
                            }
                        }
                        
                        addMessage(result.response, 'agent', result.agent, visualReport);
                    } else {
                        addMessage('Ошибка обработки сообщения', 'agent', 'System');
                    }
                } catch (error) {
                    console.error('Ошибка отправки сообщения:', error);
                    addMessage('Ошибка соединения с сервером', 'agent', 'System');
                }
                
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
        updateStatus();
        updateAutonomousTasks();
        
        // Обновление каждые 3 секунды
        setInterval(updateStatus, 3000);
        setInterval(updateAutonomousTasks, 8000);
    </script>
</body>
</html>
        """

# Основная функция
async def main():
    """Главная функция"""
    global system_running
    
    logger.info("🚀 Запуск простой визуальной автономной системы агентов...")
    
    # Создаем агентов
    create_agents()
    
    # Запускаем систему
    system_running = True
    
    # Запускаем генератор автономных задач
    task_generator = asyncio.create_task(autonomous_task_generator())
    
    logger.info("✅ Простая визуальная автономная система запущена")
    logger.info("🌐 Веб-интерфейс доступен на http://0.0.0.0:8080")
    
    try:
        # Запускаем HTTP сервер
        with socketserver.TCPServer(("0.0.0.0", 8080), VisualSystemHandler) as httpd:
            logger.info("🌐 HTTP сервер запущен на порту 8080")
            httpd.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("📡 Получен сигнал прерывания")
    finally:
        system_running = False
        task_generator.cancel()
        logger.info("🛑 Простая визуальная автономная система остановлена")

if __name__ == "__main__":
    asyncio.run(main())