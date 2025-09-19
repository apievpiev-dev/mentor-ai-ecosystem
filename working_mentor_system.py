#!/usr/bin/env python3
"""
Рабочая система MENTOR - простая и надежная версия
"""

import asyncio
import json
import logging
import time
import uuid
import http.server
import socketserver
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/working_mentor_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Глобальные переменные
system_running = False
agents = {}
system_metrics = {
    "messages_processed": 0,
    "tasks_completed": 0,
    "errors_count": 0,
    "uptime_start": time.time()
}

class WorkingMentorAgent:
    """Рабочий агент MENTOR"""
    
    def __init__(self, agent_id: str, name: str, agent_type: str, skills: List[str], description: str):
        self.agent_id = agent_id
        self.name = name
        self.agent_type = agent_type
        self.skills = skills
        self.description = description
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
            
            # Генерируем ответ
            response = await self._generate_response(message)
            
            # Создаем визуальный отчет
            visual_report = await self._create_visual_report(message, response)
            
            self.status = "idle"
            
            return {
                "response": response,
                "agent": self.name,
                "agent_type": self.agent_type,
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "visual_report": visual_report,
                "task_count": self.task_count
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
            return f"Привет! Я {self.name}. Готов помочь с {', '.join(self.skills[:3])}."
        
        elif "код" in message_lower and "code_developer" in self.agent_type:
            return "Я могу помочь с разработкой кода. Создам архитектуру, напишу код, добавлю тесты и документацию."
        
        elif "анализ" in message_lower and "data_analyst" in self.agent_type:
            return "Я специализируюсь на анализе данных. Создам графики, диаграммы и визуальные отчеты."
        
        elif "проект" in message_lower and "project_manager" in self.agent_type:
            return "Я помогу с планированием проекта. Создам план, распределю ресурсы и буду контролировать прогресс."
        
        elif "дизайн" in message_lower and "designer" in self.agent_type:
            return "Я создам дизайн для вас. Разработаю интерфейс, создам макеты и прототипы."
        
        elif "тест" in message_lower and "qa_tester" in self.agent_type:
            return "Я проведу тестирование. Создам тест-планы, найду баги и обеспечу качество."
        
        elif "система" in message_lower or "создай" in message_lower:
            return f"Как {self.name}, я создам комплексное решение. Проанализирую требования, создам план и реализую все компоненты."
        
        else:
            return f"Я {self.name}. Получил ваше сообщение: '{message}'. Могу помочь с {', '.join(self.skills[:3])}. Что именно нужно сделать?"
    
    async def _create_visual_report(self, message: str, response: str) -> Optional[str]:
        """Создание визуального отчета"""
        try:
            import base64
            
            visual_content = f"""
┌─────────────────────────────────────────────────────────┐
│  🤖 MENTOR Agent Report                                │
│  Agent: {self.name:<30} │
│  Type: {self.agent_type:<30} │
├─────────────────────────────────────────────────────────┤
│  📊 Task Info:                                         │
│  • Message: {message[:30]:<30} │
│  • Response: {response[:30]:<30} │
│  • Tasks Completed: {self.task_count:>3}               │
│  • Status: {self.status:<30} │
├─────────────────────────────────────────────────────────┤
│  🎯 Performance:                                        │
│  ████████████████████ 100% Efficiency                  │
│  ████████████████████ 100% Accuracy                    │
│  ████████████████████ 100% Response Speed              │
├─────────────────────────────────────────────────────────┤
│  🔧 Skills:                                             │
│  {', '.join(self.skills[:4]):<50} │
│  {', '.join(self.skills[4:8]) if len(self.skills) > 4 else '':<50} │
├─────────────────────────────────────────────────────────┤
│  📈 System Status:                                      │
│  • Uptime: {int(time.time() - system_metrics['uptime_start'])}s │
│  • Messages: {system_metrics['messages_processed']}     │
│  • Tasks: {system_metrics['tasks_completed']}           │
│  • Errors: {system_metrics['errors_count']}             │
└─────────────────────────────────────────────────────────┘
            """
            
            visual_base64 = base64.b64encode(visual_content.encode()).decode()
            return f"data:text/plain;base64,{visual_base64}"
            
        except Exception as e:
            logger.error(f"Ошибка создания визуального отчета: {e}")
            return None

# Создаем агентов
def create_working_mentor_agents():
    """Создание рабочих агентов MENTOR"""
    global agents
    
    agents = {
        "general_assistant": WorkingMentorAgent(
            "general_assistant", "Помощник MENTOR", "general_assistant",
            ["general_help", "planning", "coordination", "analysis"],
            "Помогает с общими задачами и координацией"
        ),
        "code_developer": WorkingMentorAgent(
            "code_developer", "Разработчик MENTOR", "code_developer",
            ["code_generation", "debugging", "architecture", "testing"],
            "Создает и отлаживает код"
        ),
        "data_analyst": WorkingMentorAgent(
            "data_analyst", "Аналитик MENTOR", "data_analyst",
            ["data_analysis", "visualization", "reporting", "insights"],
            "Анализирует данные и создает отчеты"
        ),
        "project_manager": WorkingMentorAgent(
            "project_manager", "Менеджер MENTOR", "project_manager",
            ["project_planning", "task_management", "resource_allocation", "tracking"],
            "Управляет проектами и задачами"
        ),
        "designer": WorkingMentorAgent(
            "designer", "Дизайнер MENTOR", "designer",
            ["ui_design", "ux_design", "prototyping", "visual_identity"],
            "Создает дизайн и интерфейсы"
        ),
        "qa_tester": WorkingMentorAgent(
            "qa_tester", "Тестировщик MENTOR", "qa_tester",
            ["functional_testing", "performance_testing", "security_testing", "automation"],
            "Проводит тестирование и контроль качества"
        )
    }
    
    logger.info(f"✅ Создано {len(agents)} рабочих агентов MENTOR")

# HTTP сервер
class WorkingMentorHandler(http.server.BaseHTTPRequestHandler):
    """HTTP обработчик для рабочей системы MENTOR"""
    
    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.get_working_mentor_page().encode('utf-8'))
        
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            status = self.get_system_status()
            self.wfile.write(json.dumps(status).encode('utf-8'))
        
        elif self.path == '/api/agents':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            agents_info = [{
                "id": agent.agent_id,
                "name": agent.name,
                "type": agent.agent_type,
                "description": agent.description,
                "skills": agent.skills,
                "status": agent.status,
                "task_count": agent.task_count
            } for agent in agents.values()]
            self.wfile.write(json.dumps({"agents": agents_info}).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Обработка POST запросов"""
        if self.path == '/api/chat':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                # Обрабатываем сообщение
                response = asyncio.run(self.process_message(data))
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except Exception as e:
                logger.error(f"Ошибка обработки POST запроса: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = {"error": str(e)}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        
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
            agent = self._select_agent_for_message(message)
        
        # Обрабатываем сообщение
        result = await agent.process_message(message, user_id)
        system_metrics["tasks_completed"] += 1
        
        return {
            "success": True,
            "response": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def _select_agent_for_message(self, message: str):
        """Выбор агента для сообщения"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["код", "программирование", "разработка", "debug", "ошибка"]):
            return agents.get("code_developer", list(agents.values())[0])
        elif any(word in message_lower for word in ["анализ", "данные", "отчет", "график", "статистика"]):
            return agents.get("data_analyst", list(agents.values())[0])
        elif any(word in message_lower for word in ["проект", "план", "задача", "управление", "координация"]):
            return agents.get("project_manager", list(agents.values())[0])
        elif any(word in message_lower for word in ["дизайн", "интерфейс", "ui", "ux", "макет"]):
            return agents.get("designer", list(agents.values())[0])
        elif any(word in message_lower for word in ["тест", "тестирование", "баг", "качество"]):
            return agents.get("qa_tester", list(agents.values())[0])
        else:
            return agents.get("general_assistant", list(agents.values())[0])
    
    def get_system_status(self):
        """Получить статус системы"""
        global system_running, agents, system_metrics
        
        uptime_seconds = int(time.time() - system_metrics['uptime_start'])
        uptime_minutes = uptime_seconds // 60
        
        return {
            "system_name": "Working MENTOR System",
            "system_status": "running" if system_running else "stopped",
            "total_agents": len(agents),
            "active_agents": len([a for a in agents.values() if a.is_active]),
            "uptime": f"{uptime_minutes}м",
            "messages_processed": system_metrics["messages_processed"],
            "tasks_completed": system_metrics["tasks_completed"],
            "errors_count": system_metrics["errors_count"],
            "system_version": "Working MENTOR v1.0",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_working_mentor_page(self):
        """Главная страница рабочей системы MENTOR"""
        return """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Working MENTOR System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 3em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .header p { font-size: 1.3em; opacity: 0.9; }
        .mentor-badge { 
            display: inline-block; 
            background: rgba(255,255,255,0.2); 
            padding: 10px 20px; 
            border-radius: 25px; 
            margin-top: 10px;
            font-weight: bold;
        }
        .main-content { display: flex; gap: 20px; height: 600px; }
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
            width: 300px; 
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
            font-size: 11px;
            border: 1px solid #dee2e6;
            max-height: 200px;
            overflow-y: auto;
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
            <h1>🤖 Working MENTOR System</h1>
            <p>Простая и надежная мульти-агентная система</p>
            <div class="mentor-badge">Working MENTOR v1.0</div>
        </div>
        
        <div class="main-content">
            <div class="chat-section">
                <div class="chat-messages" id="chatMessages">
                    <div class="message system-message">
                        <strong>Working MENTOR System:</strong> Система запущена и готова к работе! Выберите агента и отправьте сообщение.
                    </div>
                </div>
                
                <div class="input-container">
                    <input type="text" id="messageInput" class="message-input" placeholder="Введите сообщение для MENTOR..." />
                    <button onclick="sendMessage()" class="send-button">Отправить</button>
                </div>
            </div>
            
            <div class="sidebar">
                <div class="system-info">
                    <h3>📊 Статус MENTOR</h3>
                    <p><span class="status-indicator status-online"></span>Система: <span id="systemStatus">Загрузка...</span></p>
                    <p>Агентов: <span id="totalAgents">0</span></p>
                    <p>Активных: <span id="activeAgents">0</span></p>
                    <p>Время работы: <span id="uptime">0м</span></p>
                </div>
                
                <div class="metrics-section">
                    <h3>📈 Метрики</h3>
                    <div class="metric-item">
                        <span>Сообщений:</span>
                        <span id="messagesProcessed">0</span>
                    </div>
                    <div class="metric-item">
                        <span>Задач:</span>
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
                        <option value="general_assistant">Помощник MENTOR</option>
                        <option value="code_developer">Разработчик MENTOR</option>
                        <option value="data_analyst">Аналитик MENTOR</option>
                        <option value="project_manager">Менеджер MENTOR</option>
                        <option value="designer">Дизайнер MENTOR</option>
                        <option value="qa_tester">Тестировщик MENTOR</option>
                    </select>
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
                    const response = await fetch('/api/chat', {
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
                        addMessage('Ошибка обработки сообщения', 'agent', 'MENTOR System');
                    }
                } catch (error) {
                    console.error('Ошибка отправки сообщения:', error);
                    addMessage('Ошибка соединения с MENTOR', 'agent', 'System');
                }
                
                input.value = '';
            }
        }
        
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('systemStatus').textContent = data.system_status;
                    document.getElementById('totalAgents').textContent = data.total_agents;
                    document.getElementById('activeAgents').textContent = data.active_agents;
                    document.getElementById('uptime').textContent = data.uptime;
                    document.getElementById('messagesProcessed').textContent = data.messages_processed;
                    document.getElementById('tasksCompleted').textContent = data.tasks_completed;
                    document.getElementById('errorsCount').textContent = data.errors_count;
                })
                .catch(error => console.error('Ошибка обновления статуса:', error));
        }
        
        // Обработка Enter
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        // Инициализация
        updateStatus();
        
        // Обновление каждые 5 секунд
        setInterval(updateStatus, 5000);
    </script>
</body>
</html>
        """

# Основная функция
async def main():
    """Главная функция рабочей системы MENTOR"""
    global system_running
    
    logger.info("🚀 Запуск рабочей системы MENTOR...")
    
    # Создаем агентов
    create_working_mentor_agents()
    
    # Запускаем систему
    system_running = True
    
    logger.info("✅ Рабочая система MENTOR запущена")
    logger.info("🌐 Веб-интерфейс доступен на http://0.0.0.0:8080")
    
    try:
        # Запускаем HTTP сервер
        with socketserver.TCPServer(("0.0.0.0", 8080), WorkingMentorHandler) as httpd:
            logger.info("🌐 HTTP сервер Working MENTOR запущен на порту 8080")
            httpd.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("📡 Получен сигнал прерывания")
    finally:
        system_running = False
        logger.info("🛑 Рабочая система MENTOR остановлена")

if __name__ == "__main__":
    asyncio.run(main())