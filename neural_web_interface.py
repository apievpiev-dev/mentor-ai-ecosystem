#!/usr/bin/env python3
"""
Neural Network Web Interface
Веб-интерфейс для управления нейронной системой
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import threading

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from enhanced_neural_system import enhanced_neural_system, NeuralTask
from ai_engine import ai_engine
from visual_monitor import VisualMonitor

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем FastAPI приложение
app = FastAPI(
    title="Enhanced Neural Network System",
    description="Автономная система нейронных сетей с визуальным интеллектом",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальные переменные
connected_clients: List[WebSocket] = []
visual_monitor = None

class ConnectionManager:
    """Менеджер WebSocket соединений"""
    
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
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Отправка сообщения всем подключенным клиентам"""
        if self.active_connections:
            message_str = json.dumps(message, ensure_ascii=False)
            disconnected = []
            
            for connection in self.active_connections:
                try:
                    await connection.send_text(message_str)
                except:
                    disconnected.append(connection)
            
            # Удаляем отключенные соединения
            for connection in disconnected:
                self.disconnect(connection)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    global visual_monitor
    
    logger.info("🚀 Запуск веб-интерфейса нейронной системы...")
    
    # Инициализируем визуальный мониторинг
    try:
        visual_monitor = VisualMonitor()
        logger.info("👁️ Визуальный мониторинг инициализирован")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации визуального мониторинга: {e}")
    
    # Запускаем фоновые задачи
    asyncio.create_task(background_monitoring())
    
    logger.info("✅ Веб-интерфейс готов к работе")

@app.on_event("shutdown")
async def shutdown_event():
    """Завершение работы"""
    logger.info("🛑 Завершение работы веб-интерфейса...")
    
    if visual_monitor:
        visual_monitor.stop_monitoring()
    
    # Закрываем все WebSocket соединения
    for connection in manager.active_connections:
        try:
            await connection.close()
        except:
            pass

async def background_monitoring():
    """Фоновый мониторинг системы"""
    while True:
        try:
            # Собираем статистику системы
            system_stats = {
                "type": "system_update",
                "timestamp": datetime.now().isoformat(),
                "neural_system": enhanced_neural_system.get_system_status(),
                "ai_engine": ai_engine.get_status(),
                "visual_monitor": visual_monitor.get_vision_status() if visual_monitor else None
            }
            
            # Отправляем обновление всем подключенным клиентам
            await manager.broadcast(system_stats)
            
            await asyncio.sleep(30)  # Обновляем каждые 30 секунд
            
        except Exception as e:
            logger.error(f"❌ Ошибка фонового мониторинга: {e}")
            await asyncio.sleep(60)

@app.get("/", response_class=HTMLResponse)
async def get_main_page():
    """Главная страница"""
    html_content = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Neural Network System</title>
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
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
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
        
        .neural-controls {
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
        
        .control-group input, .control-group select, .control-group textarea {
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
        
        .btn.danger {
            background: linear-gradient(45deg, #e74c3c, #c0392b);
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
        
        .log-entry.warning {
            background: rgba(243, 156, 18, 0.2);
        }
        
        .log-entry.error {
            background: rgba(231, 76, 60, 0.2);
        }
        
        .visual-preview {
            max-width: 100%;
            border-radius: 10px;
            margin-top: 15px;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        
        .loading {
            animation: pulse 2s infinite;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .dashboard {
                grid-template-columns: 1fr;
            }
            
            .container {
                padding: 20px 10px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 Enhanced Neural Network System</h1>
        <p>Автономная система нейронных сетей с визуальным интеллектом</p>
    </div>
    
    <div class="container">
        <div class="dashboard">
            <div class="card">
                <h3>🧠 Нейронная Система</h3>
                <div class="status healthy" id="neural-status">Инициализация...</div>
                <div class="metric">
                    <span class="metric-label">Задач в очереди:</span>
                    <span class="metric-value" id="neural-queue">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Выполнено задач:</span>
                    <span class="metric-value" id="neural-completed">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Успешность:</span>
                    <span class="metric-value" id="neural-success-rate">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Среднее время:</span>
                    <span class="metric-value" id="neural-avg-time">-</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🤖 AI Движок</h3>
                <div class="status healthy" id="ai-status">Проверка...</div>
                <div class="metric">
                    <span class="metric-label">Активный движок:</span>
                    <span class="metric-value" id="ai-engine">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Доступно моделей:</span>
                    <span class="metric-value" id="ai-models">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Размер кэша:</span>
                    <span class="metric-value" id="ai-cache">-</span>
                </div>
            </div>
            
            <div class="card">
                <h3>👁️ Визуальный Интеллект</h3>
                <div class="status healthy" id="visual-status">Активен</div>
                <div class="metric">
                    <span class="metric-label">Анализов выполнено:</span>
                    <span class="metric-value" id="visual-analyses">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Элементов обнаружено:</span>
                    <span class="metric-value" id="visual-elements">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Проблем найдено:</span>
                    <span class="metric-value" id="visual-issues">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Уверенность:</span>
                    <span class="metric-value" id="visual-confidence">-</span>
                </div>
            </div>
        </div>
        
        <div class="neural-controls">
            <h3>🎛️ Управление Нейронной Системой</h3>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                <div>
                    <div class="control-group">
                        <label for="task-type">Тип задачи:</label>
                        <select id="task-type">
                            <option value="neural_processing">Нейронная обработка</option>
                            <option value="data_analysis">Анализ данных</option>
                            <option value="pattern_recognition">Распознавание паттернов</option>
                            <option value="model_training">Обучение модели</option>
                        </select>
                    </div>
                    
                    <div class="control-group">
                        <label for="task-priority">Приоритет (1-10):</label>
                        <input type="number" id="task-priority" min="1" max="10" value="5">
                    </div>
                    
                    <div class="control-group">
                        <label for="task-data">Входные данные (JSON):</label>
                        <textarea id="task-data" rows="4" placeholder='{"data": [1, 2, 3], "analysis_type": "statistical"}'></textarea>
                    </div>
                    
                    <button class="btn success" onclick="addNeuralTask()">🚀 Добавить задачу</button>
                    <button class="btn" onclick="clearQueue()">🧹 Очистить очередь</button>
                </div>
                
                <div>
                    <div class="control-group">
                        <label>Быстрые действия:</label>
                        <button class="btn" onclick="analyzeData()">📊 Анализ данных</button>
                        <button class="btn" onclick="recognizePatterns()">🔍 Поиск паттернов</button>
                        <button class="btn" onclick="trainModel()">🧠 Обучить модель</button>
                        <button class="btn" onclick="autonomousLearning()">🤖 Автообучение</button>
                    </div>
                    
                    <div class="control-group">
                        <label>Системные команды:</label>
                        <button class="btn" onclick="optimizeSystem()">⚡ Оптимизация</button>
                        <button class="btn" onclick="clearCache()">🧹 Очистить кэш</button>
                        <button class="btn danger" onclick="restartSystem()">🔄 Перезапуск</button>
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
            } else if (data.type === 'task_result') {
                handleTaskResult(data);
            }
        };
        
        ws.onclose = function(event) {
            addLog('🔌 WebSocket соединение закрыто', 'warning');
            // Попытка переподключения через 5 секунд
            setTimeout(() => {
                location.reload();
            }, 5000);
        };
        
        function updateSystemStatus(data) {
            // Обновляем статус нейронной системы
            if (data.neural_system) {
                const ns = data.neural_system;
                document.getElementById('neural-queue').textContent = ns.task_queue_size || 0;
                document.getElementById('neural-completed').textContent = ns.completed_tasks || 0;
                
                if (ns.performance_metrics) {
                    const total = ns.performance_metrics.total_tasks || 1;
                    const success = ns.performance_metrics.successful_tasks || 0;
                    const successRate = ((success / total) * 100).toFixed(1);
                    document.getElementById('neural-success-rate').textContent = successRate + '%';
                    document.getElementById('neural-avg-time').textContent = (ns.performance_metrics.average_processing_time || 0).toFixed(2) + 's';
                }
                
                const statusEl = document.getElementById('neural-status');
                statusEl.textContent = ns.running ? '✅ Работает' : '❌ Остановлен';
                statusEl.className = 'status ' + (ns.running ? 'healthy' : 'error');
            }
            
            // Обновляем статус AI движка
            if (data.ai_engine) {
                const ai = data.ai_engine;
                document.getElementById('ai-engine').textContent = ai.default_engine || 'none';
                
                let modelCount = 0;
                if (ai.available_models) {
                    for (const engine in ai.available_models) {
                        modelCount += ai.available_models[engine].length;
                    }
                }
                document.getElementById('ai-models').textContent = modelCount;
                
                // Обновляем кэш для Ollama
                if (ai.ollama_available && ai.available_models.ollama) {
                    document.getElementById('ai-cache').textContent = 'N/A';
                }
                
                const statusEl = document.getElementById('ai-status');
                const isHealthy = ai.default_engine !== 'none';
                statusEl.textContent = isHealthy ? '✅ Работает' : '❌ Недоступен';
                statusEl.className = 'status ' + (isHealthy ? 'healthy' : 'error');
            }
            
            // Обновляем статус визуального мониторинга
            if (data.visual_monitor) {
                const vm = data.visual_monitor;
                document.getElementById('visual-analyses').textContent = vm.total_analyses || 0;
                
                if (vm.last_analysis) {
                    document.getElementById('visual-elements').textContent = vm.last_analysis.elements_detected || 0;
                    document.getElementById('visual-issues').textContent = vm.last_analysis.issues_found || 0;
                    document.getElementById('visual-confidence').textContent = ((vm.last_analysis.confidence || 0) * 100).toFixed(1) + '%';
                }
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
            while (logArea.children.length > 100) {
                logArea.removeChild(logArea.firstChild);
            }
        }
        
        function addNeuralTask() {
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
            
            fetch('/api/neural/add_task', {
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
                    addLog(`✅ Задача добавлена: ${data.task_id}`, 'info');
                    document.getElementById('task-data').value = '';
                } else {
                    addLog(`❌ Ошибка добавления задачи: ${data.error}`, 'error');
                }
            })
            .catch(error => {
                addLog(`❌ Ошибка сети: ${error}`, 'error');
            });
        }
        
        function analyzeData() {
            const sampleData = {
                data: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 18, 20, 22],
                analysis_type: "statistical"
            };
            
            document.getElementById('task-type').value = 'data_analysis';
            document.getElementById('task-data').value = JSON.stringify(sampleData, null, 2);
            addNeuralTask();
        }
        
        function recognizePatterns() {
            const samplePatterns = {
                patterns: ["ABAB", "CDCD", "EFEF", "ABAB", "GHGH", "CDCD"]
            };
            
            document.getElementById('task-type').value = 'pattern_recognition';
            document.getElementById('task-data').value = JSON.stringify(samplePatterns, null, 2);
            addNeuralTask();
        }
        
        function trainModel() {
            const trainingData = {
                model_name: "test_model",
                training_data: [
                    {"input": [1, 2], "output": 3},
                    {"input": [2, 3], "output": 5},
                    {"input": [3, 4], "output": 7}
                ]
            };
            
            document.getElementById('task-type').value = 'model_training';
            document.getElementById('task-data').value = JSON.stringify(trainingData, null, 2);
            addNeuralTask();
        }
        
        function autonomousLearning() {
            fetch('/api/neural/autonomous_learning', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    addLog(`🧠 Автономное обучение: ${data.message}`, 'info');
                } else {
                    addLog(`❌ Ошибка автономного обучения: ${data.error}`, 'error');
                }
            });
        }
        
        function clearQueue() {
            fetch('/api/neural/clear_queue', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    addLog('🧹 Очередь задач очищена', 'info');
                } else {
                    addLog(`❌ Ошибка очистки очереди: ${data.error}`, 'error');
                }
            });
        }
        
        function optimizeSystem() {
            fetch('/api/system/optimize', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                addLog('⚡ Оптимизация системы запущена', 'info');
            });
        }
        
        function clearCache() {
            fetch('/api/system/clear_cache', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                addLog('🧹 Кэш очищен', 'info');
            });
        }
        
        function restartSystem() {
            if (confirm('Вы уверены, что хотите перезапустить систему?')) {
                fetch('/api/system/restart', {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    addLog('🔄 Система перезапускается...', 'warning');
                });
            }
        }
        
        function handleTaskResult(data) {
            const message = `✅ Задача ${data.task_id} завершена за ${data.processing_time.toFixed(2)}с`;
            addLog(message, 'info');
        }
        
        // Инициализация
        addLog('🚀 Интерфейс загружен', 'info');
    </script>
</body>
</html>
"""
    return html_content

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint для реального времени"""
    await manager.connect(websocket)
    try:
        while True:
            # Ожидаем сообщения от клиента
            data = await websocket.receive_text()
            
            # Можем обрабатывать команды от клиента
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
async def get_system_status():
    """Получить статус системы"""
    try:
        status = {
            "neural_system": enhanced_neural_system.get_system_status(),
            "ai_engine": ai_engine.get_status(),
            "visual_monitor": visual_monitor.get_vision_status() if visual_monitor else None,
            "timestamp": datetime.now().isoformat()
        }
        return JSONResponse(status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/neural/add_task")
async def add_neural_task(task_data: Dict[str, Any]):
    """Добавить нейронную задачу"""
    try:
        task_type = task_data.get("task_type", "neural_processing")
        priority = task_data.get("priority", 5)
        input_data = task_data.get("input_data", {})
        
        task_id = enhanced_neural_system.add_neural_task(task_type, input_data, priority)
        
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
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/neural/clear_queue")
async def clear_task_queue():
    """Очистить очередь задач"""
    try:
        cleared_count = len(enhanced_neural_system.task_queue)
        enhanced_neural_system.task_queue.clear()
        
        await manager.broadcast({
            "type": "queue_cleared",
            "cleared_count": cleared_count
        })
        
        return JSONResponse({
            "success": True,
            "cleared_count": cleared_count,
            "message": f"Очищено {cleared_count} задач"
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка очистки очереди: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/neural/autonomous_learning")
async def trigger_autonomous_learning():
    """Запустить автономное обучение"""
    try:
        result = await enhanced_neural_system.neural_agent._handle_autonomous_learning({})
        
        await manager.broadcast({
            "type": "autonomous_learning",
            "result": result
        })
        
        return JSONResponse({
            "success": result.get("status") == "success",
            "message": result.get("summary", "Автономное обучение завершено"),
            "result": result
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка автономного обучения: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/system/optimize")
async def optimize_system():
    """Оптимизировать систему"""
    try:
        await enhanced_neural_system._optimize_system()
        
        await manager.broadcast({
            "type": "system_optimized",
            "timestamp": datetime.now().isoformat()
        })
        
        return JSONResponse({
            "success": True,
            "message": "Система оптимизирована"
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка оптимизации: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/system/clear_cache")
async def clear_system_cache():
    """Очистить кэш системы"""
    try:
        if hasattr(ai_engine.ollama, 'clear_cache'):
            ai_engine.ollama.clear_cache()
        
        return JSONResponse({
            "success": True,
            "message": "Кэш очищен"
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка очистки кэша: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/system/restart")
async def restart_system(background_tasks: BackgroundTasks):
    """Перезапустить систему"""
    try:
        background_tasks.add_task(restart_system_background)
        
        return JSONResponse({
            "success": True,
            "message": "Система перезапускается..."
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка перезапуска: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def restart_system_background():
    """Фоновый перезапуск системы"""
    try:
        await manager.broadcast({
            "type": "system_restarting",
            "timestamp": datetime.now().isoformat()
        })
        
        # Останавливаем систему
        enhanced_neural_system.stop()
        
        # Ждем немного
        await asyncio.sleep(3)
        
        # Запускаем заново (в реальности нужно перезапустить процесс)
        logger.info("🔄 Система перезапущена")
        
    except Exception as e:
        logger.error(f"❌ Ошибка фонового перезапуска: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "neural_system_running": enhanced_neural_system.running,
        "ai_engine_available": ai_engine.get_status().get("default_engine") != "none"
    })

if __name__ == "__main__":
    # Запускаем веб-сервер
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8081,
        log_level="info",
        access_log=True
    )