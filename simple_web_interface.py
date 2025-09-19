#!/usr/bin/env python3
"""
Simple Web Interface for Neural Network System
Простой веб-интерфейс для нейронной системы
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
import threading
import time

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from simple_neural_system import simple_neural_system

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем FastAPI приложение
app = FastAPI(
    title="Simple Neural Network System",
    description="Простая автономная система нейронных сетей",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Менеджер WebSocket соединений
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"🔌 Новое WebSocket соединение. Всего: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"🔌 WebSocket соединение закрыто. Осталось: {len(self.active_connections)}")
    
    async def broadcast(self, message: Dict[str, Any]):
        if self.active_connections:
            message_str = json.dumps(message, ensure_ascii=False)
            disconnected = []
            
            for connection in self.active_connections:
                try:
                    await connection.send_text(message_str)
                except:
                    disconnected.append(connection)
            
            for connection in disconnected:
                self.disconnect(connection)

manager = ConnectionManager()

# Запуск нейронной системы в фоне
neural_system_task = None
neural_system_running = False

async def start_neural_system():
    """Запуск нейронной системы в фоне"""
    global neural_system_running
    neural_system_running = True
    
    try:
        await simple_neural_system.start()
    except Exception as e:
        logger.error(f"❌ Ошибка нейронной системы: {e}")
        neural_system_running = False

async def background_monitoring():
    """Фоновый мониторинг системы"""
    while True:
        try:
            if neural_system_running:
                # Собираем статистику системы
                system_stats = {
                    "type": "system_update",
                    "timestamp": datetime.now().isoformat(),
                    "neural_system": simple_neural_system.get_system_status()
                }
                
                # Отправляем обновление всем подключенным клиентам
                await manager.broadcast(system_stats)
            
            await asyncio.sleep(5)  # Обновляем каждые 5 секунд
            
        except Exception as e:
            logger.error(f"❌ Ошибка фонового мониторинга: {e}")
            await asyncio.sleep(10)

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    global neural_system_task
    
    logger.info("🚀 Запуск веб-интерфейса нейронной системы...")
    
    # Запускаем нейронную систему в фоне
    neural_system_task = asyncio.create_task(start_neural_system())
    
    # Запускаем фоновые задачи
    asyncio.create_task(background_monitoring())
    
    logger.info("✅ Веб-интерфейс готов к работе")

@app.on_event("shutdown")
async def shutdown_event():
    """Завершение работы"""
    logger.info("🛑 Завершение работы веб-интерфейса...")
    
    simple_neural_system.stop()
    
    # Закрываем все WebSocket соединения
    for connection in manager.active_connections:
        try:
            await connection.close()
        except:
            pass

@app.get("/", response_class=HTMLResponse)
async def get_main_page():
    """Главная страница"""
    html_content = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 Simple Neural Network System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        
        .header {
            background: rgba(0, 0, 0, 0.3);
            padding: 20px;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 30px 20px;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card h3 {
            font-size: 1.5rem;
            margin-bottom: 15px;
            color: #fff;
        }
        
        .status {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: bold;
            margin-bottom: 15px;
        }
        
        .status.healthy {
            background: #27ae60;
        }
        
        .status.warning {
            background: #f39c12;
        }
        
        .status.error {
            background: #e74c3c;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-label {
            opacity: 0.8;
        }
        
        .metric-value {
            font-weight: bold;
        }
        
        .controls {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
        }
        
        .control-group {
            margin-bottom: 20px;
        }
        
        .control-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        
        .control-group select, .control-group textarea, .control-group input {
            width: 100%;
            padding: 10px;
            border: none;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            font-size: 1rem;
        }
        
        .control-group input::placeholder, .control-group textarea::placeholder {
            color: rgba(255, 255, 255, 0.7);
        }
        
        .btn {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-right: 10px;
            margin-bottom: 10px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        
        .btn.success {
            background: linear-gradient(45deg, #27ae60, #2ecc71);
        }
        
        .log-area {
            background: rgba(0, 0, 0, 0.5);
            border-radius: 10px;
            padding: 20px;
            height: 300px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            line-height: 1.4;
        }
        
        .log-entry {
            margin-bottom: 5px;
            padding: 5px;
            border-radius: 3px;
        }
        
        .log-entry.info {
            background: rgba(52, 152, 219, 0.2);
        }
        
        .log-entry.success {
            background: rgba(39, 174, 96, 0.2);
        }
        
        .log-entry.error {
            background: rgba(231, 76, 60, 0.2);
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        
        .loading {
            animation: pulse 2s infinite;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 Simple Neural Network System</h1>
        <p>Автономная система нейронных сетей - Работает 24/7</p>
    </div>
    
    <div class="container">
        <div class="dashboard">
            <div class="card">
                <h3>🧠 Нейронная Система</h3>
                <div class="status healthy" id="system-status">Активна</div>
                <div class="metric">
                    <span class="metric-label">Задач в очереди:</span>
                    <span class="metric-value" id="queue-size">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Выполнено задач:</span>
                    <span class="metric-value" id="completed-tasks">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Успешность:</span>
                    <span class="metric-value" id="success-rate">100%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Среднее время:</span>
                    <span class="metric-value" id="avg-time">0.0с</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🤖 Нейронный Агент</h3>
                <div class="status healthy" id="agent-status">Готов</div>
                <div class="metric">
                    <span class="metric-label">Статус агента:</span>
                    <span class="metric-value" id="agent-state">idle</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Обученных моделей:</span>
                    <span class="metric-value" id="trained-models">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Последняя активность:</span>
                    <span class="metric-value" id="last-activity">-</span>
                </div>
            </div>
        </div>
        
        <div class="controls">
            <h3>🎛️ Управление Нейронной Системой</h3>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                <div>
                    <div class="control-group">
                        <label for="task-type">Тип задачи:</label>
                        <select id="task-type">
                            <option value="data_analysis">Анализ данных</option>
                            <option value="pattern_recognition">Распознавание паттернов</option>
                            <option value="neural_processing">Нейронная обработка</option>
                            <option value="model_training">Обучение модели</option>
                        </select>
                    </div>
                    
                    <div class="control-group">
                        <label for="task-priority">Приоритет (1-10):</label>
                        <input type="number" id="task-priority" min="1" max="10" value="5">
                    </div>
                    
                    <div class="control-group">
                        <label for="task-data">Данные (JSON):</label>
                        <textarea id="task-data" rows="4" placeholder='{"data": [1, 2, 3], "analysis_type": "statistical"}'></textarea>
                    </div>
                    
                    <button class="btn success" onclick="addTask()">🚀 Добавить задачу</button>
                </div>
                
                <div>
                    <div class="control-group">
                        <label>Быстрые задачи:</label>
                        <button class="btn" onclick="quickDataAnalysis()">📊 Анализ данных</button>
                        <button class="btn" onclick="quickPatternRecognition()">🔍 Поиск паттернов</button>
                        <button class="btn" onclick="quickNeuralProcessing()">🧠 Нейронная обработка</button>
                        <button class="btn" onclick="quickModelTraining()">🎯 Обучение модели</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>📋 Системные Логи</h3>
            <div class="log-area" id="system-logs">
                <div class="log-entry info">🚀 Система инициализируется...</div>
            </div>
        </div>
    </div>
    
    <script>
        // WebSocket соединение
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        
        ws.onopen = function(event) {
            addLog('🔌 WebSocket соединение установлено', 'info');
        };
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            if (data.type === 'system_update') {
                updateSystemStatus(data);
            } else if (data.type === 'log') {
                addLog(data.message, data.level);
            }
        };
        
        ws.onclose = function(event) {
            addLog('🔌 WebSocket соединение закрыто', 'error');
        };
        
        function updateSystemStatus(data) {
            if (data.neural_system) {
                const ns = data.neural_system;
                
                // Обновляем метрики
                document.getElementById('queue-size').textContent = ns.task_queue_size || 0;
                document.getElementById('completed-tasks').textContent = ns.completed_tasks || 0;
                
                // Обновляем успешность
                if (ns.performance_metrics) {
                    const total = ns.performance_metrics.total_tasks || 1;
                    const success = ns.performance_metrics.successful_tasks || 0;
                    const successRate = ((success / total) * 100).toFixed(1);
                    document.getElementById('success-rate').textContent = successRate + '%';
                    document.getElementById('avg-time').textContent = (ns.performance_metrics.average_processing_time || 0).toFixed(2) + 's';
                }
                
                // Обновляем статус системы
                const systemStatus = document.getElementById('system-status');
                systemStatus.textContent = ns.running ? '✅ Работает' : '❌ Остановлена';
                systemStatus.className = 'status ' + (ns.running ? 'healthy' : 'error');
                
                // Обновляем информацию об агенте
                if (ns.agent) {
                    document.getElementById('agent-state').textContent = ns.agent.status || 'idle';
                    document.getElementById('trained-models').textContent = ns.agent.trained_models || 0;
                    
                    const agentStatus = document.getElementById('agent-status');
                    agentStatus.textContent = ns.agent.status === 'idle' ? '✅ Готов' : '🔄 Работает';
                    agentStatus.className = 'status healthy';
                }
                
                document.getElementById('last-activity').textContent = new Date().toLocaleTimeString();
            }
        }
        
        function addLog(message, level = 'info') {
            const logArea = document.getElementById('system-logs');
            const timestamp = new Date().toLocaleTimeString();
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry ${level}`;
            logEntry.textContent = `[${timestamp}] ${message}`;
            
            logArea.appendChild(logEntry);
            logArea.scrollTop = logArea.scrollHeight;
            
            // Ограничиваем количество логов
            while (logArea.children.length > 50) {
                logArea.removeChild(logArea.firstChild);
            }
        }
        
        function addTask() {
            const taskType = document.getElementById('task-type').value;
            const priority = parseInt(document.getElementById('task-priority').value);
            const taskDataStr = document.getElementById('task-data').value;
            
            let taskData;
            try {
                taskData = JSON.parse(taskDataStr || '{}');
            } catch (e) {
                addLog('❌ Ошибка парсинга JSON данных', 'error');
                return;
            }
            
            fetch('/api/add_task', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    task_type: taskType,
                    priority: priority,
                    input_data: taskData
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    addLog(`✅ Задача добавлена: ${data.task_id}`, 'success');
                    document.getElementById('task-data').value = '';
                } else {
                    addLog(`❌ Ошибка: ${data.error}`, 'error');
                }
            })
            .catch(error => {
                addLog(`❌ Ошибка сети: ${error}`, 'error');
            });
        }
        
        function quickDataAnalysis() {
            document.getElementById('task-type').value = 'data_analysis';
            document.getElementById('task-data').value = JSON.stringify({
                data: [1, 5, 3, 9, 2, 8, 4, 7, 6, 10],
                analysis_type: "statistical"
            }, null, 2);
            addTask();
        }
        
        function quickPatternRecognition() {
            document.getElementById('task-type').value = 'pattern_recognition';
            document.getElementById('task-data').value = JSON.stringify({
                patterns: ["ABAB", "CDCD", "ABAB", "EFEF", "ABAB", "CDCD"]
            }, null, 2);
            addTask();
        }
        
        function quickNeuralProcessing() {
            document.getElementById('task-type').value = 'neural_processing';
            document.getElementById('task-data').value = JSON.stringify({
                input_data: {
                    text: "Тестовая нейронная обработка",
                    numbers: [1, 2, 3, 4, 5]
                }
            }, null, 2);
            addTask();
        }
        
        function quickModelTraining() {
            document.getElementById('task-type').value = 'model_training';
            document.getElementById('task-data').value = JSON.stringify({
                model_name: "test_model_" + Date.now(),
                training_data: [
                    {"input": [1, 2], "output": 3},
                    {"input": [2, 3], "output": 5},
                    {"input": [3, 4], "output": 7},
                    {"input": [4, 5], "output": 9}
                ]
            }, null, 2);
            addTask();
        }
        
        // Инициализация
        addLog('🚀 Веб-интерфейс загружен', 'info');
        addLog('🧠 Нейронная система готова к работе', 'info');
    </script>
</body>
</html>
"""
    return html_content

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Обрабатываем ping/pong
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }))
            except:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/status")
async def get_status():
    """Получить статус системы"""
    return JSONResponse(simple_neural_system.get_system_status())

@app.post("/api/add_task")
async def add_task(task_data: Dict[str, Any]):
    """Добавить задачу"""
    try:
        task_type = task_data.get("task_type", "neural_processing")
        priority = task_data.get("priority", 5)
        input_data = task_data.get("input_data", {})
        
        task_id = simple_neural_system.add_task(task_type, input_data, priority)
        
        # Уведомляем всех клиентов
        await manager.broadcast({
            "type": "task_added",
            "task_id": task_id,
            "task_type": task_type,
            "priority": priority
        })
        
        return JSONResponse({
            "success": True,
            "task_id": task_id,
            "message": "Задача добавлена в очередь"
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка добавления задачи: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e)
        })

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "neural_system_running": neural_system_running
    })

if __name__ == "__main__":
    # Запускаем веб-сервер
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8081,
        log_level="info"
    )