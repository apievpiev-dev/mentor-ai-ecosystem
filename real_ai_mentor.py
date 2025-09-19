#!/usr/bin/env python3
"""
Настоящая AI система Mentor с Ollama
Реальные нейросети, реальный интеллект, реальные возможности
"""

import asyncio
import json
import logging
import time
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/real_ai_mentor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RealAIAgent:
    """Настоящий AI агент с Ollama"""
    
    def __init__(self, agent_id: str, name: str, agent_type: str, system_prompt: str):
        self.agent_id = agent_id
        self.name = name
        self.agent_type = agent_type
        self.system_prompt = system_prompt
        self.status = "idle"
        self.last_activity = time.time()
        self.task_count = 0
        self.is_active = False
        self.conversation_history = []
        
        logger.info(f"🤖 Создан настоящий AI агент: {self.name}")
    
    async def process_with_real_ai(self, message: str, user_id: str = "user") -> Dict[str, Any]:
        """Обработка сообщения с настоящим AI через Ollama"""
        try:
            self.last_activity = time.time()
            self.task_count += 1
            self.status = "thinking"
            self.is_active = True
            
            # Создаем контекст для AI
            full_prompt = f"{self.system_prompt}\n\nПользователь: {message}\n\nОтветь как {self.name}:"
            
            # Отправляем запрос к Ollama
            start_time = time.time()
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2:1b",
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 200
                    }
                },
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                ai_response = response.json().get("response", "").strip()
                
                # Сохраняем в историю
                self.conversation_history.append({
                    "user_message": message,
                    "ai_response": ai_response,
                    "timestamp": datetime.now().isoformat(),
                    "user_id": user_id,
                    "response_time": response_time
                })
                
                self.status = "idle"
                
                logger.info(f"🧠 {self.name} ответил за {response_time:.2f}с: {ai_response[:50]}...")
                
                return {
                    "response": ai_response,
                    "agent": self.name,
                    "agent_type": self.agent_type,
                    "timestamp": datetime.now().isoformat(),
                    "success": True,
                    "ai_used": True,
                    "response_time": response_time,
                    "model": "llama3.2:1b"
                }
            else:
                raise Exception(f"Ollama error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка AI агента {self.name}: {e}")
            
            # Fallback ответ
            fallback_response = self.get_fallback_response(message)
            
            self.status = "idle"
            
            return {
                "response": fallback_response,
                "agent": self.name,
                "agent_type": self.agent_type,
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "ai_used": False,
                "error": str(e)
            }
    
    def get_fallback_response(self, message: str) -> str:
        """Резервный ответ если AI недоступен"""
        fallbacks = {
            "general_assistant": f"Я {self.name}. Получил ваше сообщение '{message}'. AI временно недоступен, но я готов помочь базовыми функциями.",
            "code_developer": f"Как {self.name}, я вижу запрос о коде: '{message}'. Могу помочь с Python, JavaScript и другими языками программирования.",
            "data_analyst": f"{self.name} здесь. Анализирую ваш запрос '{message}'. Готов помочь с данными, метриками и аналитикой.",
            "project_manager": f"Я {self.name}. Ваш запрос '{message}' принят к рассмотрению. Помогу с планированием и управлением проектом.",
            "designer": f"Как {self.name}, рассматриваю ваш запрос '{message}'. Могу помочь с дизайном интерфейсов и UX.",
            "qa_tester": f"{self.name} на связи. Запрос '{message}' получен. Готов помочь с тестированием и контролем качества."
        }
        
        return fallbacks.get(self.agent_type, f"Агент {self.name} получил: '{message}'. Готов помочь!")

class RealAIMentorSystem:
    """Настоящая AI система Mentor"""
    
    def __init__(self):
        self.agents = {}
        self.system_running = False
        self.startup_time = time.time()
        self.total_requests = 0
        self.ai_requests = 0
        self.fallback_requests = 0
        
        self.create_real_ai_agents()
        
    def create_real_ai_agents(self):
        """Создание настоящих AI агентов с уникальными промптами"""
        
        agent_configs = {
            "general_assistant": {
                "name": "🧠 AI Универсальный Помощник",
                "system_prompt": """Ты опытный AI помощник, который может помочь с любыми вопросами. 
                Ты работаешь в системе Mentor и координируешь работу других агентов.
                Отвечай кратко, по делу, на русском языке. Будь полезным и дружелюбным."""
            },
            "code_developer": {
                "name": "💻 AI Разработчик",
                "system_prompt": """Ты опытный программист-эксперт. Знаешь Python, JavaScript, FastAPI, веб-разработку.
                Помогаешь писать качественный код, находить ошибки, оптимизировать производительность.
                Отвечай конкретно, с примерами кода где нужно. Пиши на русском языке."""
            },
            "data_analyst": {
                "name": "📊 AI Аналитик Данных", 
                "system_prompt": """Ты эксперт по анализу данных и машинному обучению. Разбираешься в статистике,
                визуализации данных, метриках, SQL, pandas, numpy.
                Помогаешь анализировать данные и делать выводы. Отвечай четко, с цифрами где возможно."""
            },
            "project_manager": {
                "name": "📋 AI Менеджер Проектов",
                "system_prompt": """Ты опытный менеджер IT проектов. Знаешь Agile, Scrum, планирование, управление командой.
                Помогаешь планировать задачи, управлять временем, координировать работу.
                Отвечай структурированно, с четким планом действий."""
            },
            "designer": {
                "name": "🎨 AI Дизайнер",
                "system_prompt": """Ты UI/UX дизайнер с большим опытом. Разбираешься в веб-дизайне, пользовательском опыте,
                современных трендах, CSS, адаптивности, типографике, цветах.
                Помогаешь улучшать интерфейсы и пользовательский опыт. Отвечай креативно но практично."""
            },
            "qa_tester": {
                "name": "🔍 AI Тестировщик",
                "system_prompt": """Ты эксперт по тестированию ПО. Знаешь различные виды тестирования, автоматизацию,
                поиск багов, обеспечение качества, тест-кейсы.
                Помогаешь находить проблемы и улучшать качество продукта. Отвечай методично и тщательно."""
            }
        }
        
        for agent_id, config in agent_configs.items():
            self.agents[agent_id] = RealAIAgent(
                agent_id=agent_id,
                name=config["name"],
                agent_type=agent_id,
                system_prompt=config["system_prompt"]
            )
        
        logger.info(f"✅ Создано {len(self.agents)} настоящих AI агентов")

# Создаем систему
mentor_system = RealAIMentorSystem()

# FastAPI приложение
app = FastAPI(title="Real AI Mentor System")

@app.get("/")
async def root():
    """Главная страница с улучшенным интерфейсом"""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Real AI Mentor System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 3em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .header p { font-size: 1.3em; opacity: 0.9; }
        .ai-badge { 
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4); 
            padding: 8px 16px; 
            border-radius: 20px; 
            color: white; 
            font-weight: bold; 
            display: inline-block; 
            margin: 10px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .status-card { background: rgba(255,255,255,0.95); border-radius: 15px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
        .status-card h3 { color: #2c3e50; margin-bottom: 15px; font-size: 1.3em; }
        .metric { display: flex; justify-content: space-between; margin-bottom: 10px; }
        .metric-value { font-weight: bold; color: #667eea; }
        .ai-indicator { color: #ff6b6b; font-weight: bold; }
        .chat-container { display: flex; gap: 20px; height: 500px; }
        .chat-messages { flex: 1; background: white; border-radius: 15px; padding: 20px; overflow-y: auto; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
        .chat-sidebar { width: 350px; background: rgba(255,255,255,0.95); border-radius: 15px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
        .message { margin-bottom: 15px; padding: 15px; border-radius: 12px; }
        .user-message { background: #e3f2fd; margin-left: 30px; border-left: 4px solid #2196f3; }
        .ai-message { background: #fff3e0; margin-right: 30px; border-left: 4px solid #ff9800; }
        .real-ai-message { background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); margin-right: 30px; border-left: 4px solid #ff6b6b; }
        .system-message { background: #e8f5e8; text-align: center; font-style: italic; border-left: 4px solid #4caf50; }
        .input-container { display: flex; gap: 15px; margin-top: 20px; }
        .message-input { flex: 1; padding: 15px; border: none; border-radius: 25px; font-size: 16px; outline: none; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .send-button { 
            padding: 15px 30px; 
            background: linear-gradient(135deg, #ff6b6b, #4ecdc4); 
            color: white; 
            border: none; 
            border-radius: 25px; 
            cursor: pointer; 
            font-size: 16px; 
            transition: transform 0.2s; 
            font-weight: bold;
        }
        .send-button:hover { transform: translateY(-2px); }
        .agent-selector { margin-bottom: 20px; }
        .agent-selector select { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; }
        .ai-stats { margin-top: 20px; }
        .ai-stats h3 { color: #333; margin-bottom: 10px; }
        .stat-item { background: #f8f9fa; padding: 12px; border-radius: 8px; margin-bottom: 8px; font-size: 0.9em; border-left: 3px solid #ff6b6b; }
        .loading { opacity: 0.7; }
        .response-time { font-size: 0.8em; color: #666; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Real AI Mentor System</h1>
            <div class="ai-badge">Powered by Llama 3.2 🧠</div>
            <p>Настоящие нейросети • Реальный интеллект • Живое общение</p>
        </div>
        
        <div class="status-grid">
            <div class="status-card">
                <h3>🤖 AI Статус</h3>
                <div class="metric">
                    <span>AI Модель:</span>
                    <span class="metric-value ai-indicator" id="aiModel">Llama 3.2</span>
                </div>
                <div class="metric">
                    <span>AI Запросов:</span>
                    <span class="metric-value" id="aiRequests">0</span>
                </div>
                <div class="metric">
                    <span>Fallback запросов:</span>
                    <span class="metric-value" id="fallbackRequests">0</span>
                </div>
                <div class="metric">
                    <span>Среднее время AI:</span>
                    <span class="metric-value" id="avgResponseTime">-</span>
                </div>
            </div>
            
            <div class="status-card">
                <h3>📊 Системные Метрики</h3>
                <div class="metric">
                    <span>Статус системы:</span>
                    <span class="metric-value" id="systemStatus">Загрузка...</span>
                </div>
                <div class="metric">
                    <span>AI Агентов:</span>
                    <span class="metric-value" id="activeAgents">0</span>
                </div>
                <div class="metric">
                    <span>Всего запросов:</span>
                    <span class="metric-value" id="totalRequests">0</span>
                </div>
                <div class="metric">
                    <span>Время работы:</span>
                    <span class="metric-value" id="uptime">0с</span>
                </div>
            </div>
            
            <div class="status-card">
                <h3>🧠 AI Агенты</h3>
                <div id="agentStatusList">
                    <div class="stat-item">Загрузка AI агентов...</div>
                </div>
            </div>
        </div>
        
        <div class="chat-container">
            <div class="chat-messages" id="chatMessages">
                <div class="message system-message">
                    <strong>🚀 Система:</strong> Real AI Mentor System запущена! Настоящие нейросети готовы к общению.
                </div>
            </div>
            
            <div class="chat-sidebar">
                <div class="agent-selector">
                    <label for="agentSelect"><strong>Выберите AI агента:</strong></label>
                    <select id="agentSelect">
                        <option value="">Автоматический выбор</option>
                        <option value="general_assistant">🧠 AI Универсальный Помощник</option>
                        <option value="code_developer">💻 AI Разработчик</option>
                        <option value="data_analyst">📊 AI Аналитик Данных</option>
                        <option value="project_manager">📋 AI Менеджер Проектов</option>
                        <option value="designer">🎨 AI Дизайнер</option>
                        <option value="qa_tester">🔍 AI Тестировщик</option>
                    </select>
                </div>
                
                <div class="ai-stats">
                    <h3>📈 AI Статистика</h3>
                    <div id="aiStatsList">
                        <div class="stat-item">Статистика AI загружается...</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="messageInput" class="message-input" placeholder="Напишите сообщение настоящему AI агенту..." />
            <button onclick="sendMessage()" class="send-button">🚀 Отправить AI</button>
        </div>
    </div>

    <script>
        let ws = null;
        let userId = 'user_' + Math.random().toString(36).substr(2, 9);
        let messageCount = 0;
        let responseTimes = [];
        
        function connectWebSocket() {
            ws = new WebSocket(`ws://${window.location.host}/ws/${userId}`);
            
            ws.onopen = function() {
                console.log('WebSocket подключен к Real AI системе');
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                addMessage(data.message, 'ai', data.agent, data.ai_used, data.response_time, data.model);
                
                // Обновляем статистику времени ответа
                if (data.response_time) {
                    responseTimes.push(data.response_time);
                    const avgTime = responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length;
                    document.getElementById('avgResponseTime').textContent = avgTime.toFixed(2) + 'с';
                }
            };
            
            ws.onclose = function() {
                console.log('WebSocket отключен, переподключение...');
                setTimeout(connectWebSocket, 3000);
            };
        }
        
        function addMessage(message, type, agent = '', ai_used = false, response_time = null, model = null) {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            
            if (type === 'user') {
                messageDiv.className = 'message user-message';
                messageDiv.innerHTML = `<strong>Вы:</strong> ${message}`;
            } else {
                messageDiv.className = ai_used ? 'message real-ai-message' : 'message ai-message';
                const badge = ai_used ? ' 🧠 AI' : ' 💬';
                let content = `<strong>${agent}${badge}:</strong> ${message}`;
                
                if (response_time) {
                    content += `<div class="response-time">Время ответа: ${response_time.toFixed(2)}с`;
                    if (model) content += ` • Модель: ${model}`;
                    content += `</div>`;
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
                
                // Показываем индикатор загрузки
                const loadingDiv = document.createElement('div');
                loadingDiv.className = 'message system-message loading';
                loadingDiv.innerHTML = '<strong>AI думает...</strong> 🤔';
                loadingDiv.id = 'loading-indicator';
                document.getElementById('chatMessages').appendChild(loadingDiv);
                
                const payload = {
                    message: message,
                    agent_type: agentType || null,
                    user_id: userId
                };
                
                ws.send(JSON.stringify(payload));
                input.value = '';
                messageCount++;
            }
        }
        
        function updateStatus() {
            fetch('/api/system/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('systemStatus').textContent = data.system_status;
                    document.getElementById('activeAgents').textContent = data.active_agents;
                    document.getElementById('totalRequests').textContent = data.total_requests;
                    document.getElementById('uptime').textContent = data.uptime;
                    document.getElementById('aiRequests').textContent = data.ai_requests;
                    document.getElementById('fallbackRequests').textContent = data.fallback_requests;
                    
                    // Обновляем список агентов
                    const agentsList = document.getElementById('agentStatusList');
                    agentsList.innerHTML = '';
                    
                    if (data.agents) {
                        Object.values(data.agents).forEach(agent => {
                            const agentDiv = document.createElement('div');
                            agentDiv.className = 'stat-item';
                            agentDiv.innerHTML = `${agent.name}: ${agent.task_count} задач`;
                            agentsList.appendChild(agentDiv);
                        });
                    }
                    
                    // Убираем индикатор загрузки если есть
                    const loading = document.getElementById('loading-indicator');
                    if (loading) loading.remove();
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
        connectWebSocket();
        updateStatus();
        
        // Обновление каждые 3 секунды
        setInterval(updateStatus, 3000);
    </script>
</body>
</html>
    """)

@app.get("/api/system/status")
async def get_system_status():
    """Получить статус системы с AI метриками"""
    global mentor_system
    
    uptime_seconds = int(time.time() - mentor_system.startup_time)
    
    agent_data = {}
    for agent_id, agent in mentor_system.agents.items():
        agent_data[agent_id] = {
            "name": agent.name,
            "type": agent.agent_type,
            "status": agent.status,
            "task_count": agent.task_count,
            "is_active": agent.is_active
        }
    
    return {
        "system_status": "running",
        "total_agents": len(mentor_system.agents),
        "active_agents": len(mentor_system.agents),
        "uptime": f"{uptime_seconds}с",
        "total_requests": mentor_system.total_requests,
        "ai_requests": mentor_system.ai_requests,
        "fallback_requests": mentor_system.fallback_requests,
        "agents": agent_data,
        "ai_model": "llama3.2:1b",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/chat/send")
async def send_message(data: dict):
    """Отправить сообщение AI агенту"""
    global mentor_system
    
    message = data.get("message", "")
    agent_type = data.get("agent_type")
    user_id = data.get("user_id", "unknown")
    
    if not message:
        return {"error": "Сообщение не может быть пустым"}
    
    mentor_system.total_requests += 1
    
    # Выбираем агента
    if agent_type and agent_type in mentor_system.agents:
        agent = mentor_system.agents[agent_type]
    else:
        # Автоматический выбор агента
        agent = list(mentor_system.agents.values())[0]
    
    # Обрабатываем сообщение с настоящим AI
    result = await agent.process_with_real_ai(message, user_id)
    
    # Обновляем статистику
    if result.get("ai_used"):
        mentor_system.ai_requests += 1
    else:
        mentor_system.fallback_requests += 1
    
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
                    "ai_used": result.get("ai_used", False),
                    "response_time": result.get("response_time"),
                    "model": result.get("model")
                }))
            else:
                await websocket.send_text(json.dumps({
                    "message": "Ошибка обработки сообщения",
                    "agent": "System",
                    "timestamp": datetime.now().isoformat(),
                    "ai_used": False
                }))
                
    except WebSocketDisconnect:
        logger.info(f"🔌 Пользователь {user_id} отключился от Real AI WebSocket")

# Основная функция
async def main():
    """Главная функция"""
    global mentor_system
    
    logger.info("🤖 Запуск Real AI Mentor System с настоящими нейросетями...")
    
    mentor_system.system_running = True
    
    logger.info("✅ Real AI система запущена")
    logger.info("🧠 Используется модель: llama3.2:1b")
    logger.info("🌐 Веб-интерфейс доступен на http://localhost:8082")
    
    try:
        # Запускаем веб-сервер на другом порту
        config = uvicorn.Config(app, host="0.0.0.0", port=8082, log_level="info")
        server = uvicorn.Server(config)
        
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("📡 Получен сигнал прерывания")
    except Exception as e:
        logger.error(f"❌ Ошибка веб-сервера: {e}")
    finally:
        mentor_system.system_running = False
        logger.info("🛑 Real AI система остановлена")

if __name__ == "__main__":
    asyncio.run(main())