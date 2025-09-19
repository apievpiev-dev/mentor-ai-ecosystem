#!/usr/bin/env python3
"""
Улучшенный дашборд для мониторинга системы Mentor
Предоставляет детальную информацию о состоянии агентов и системы
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import aiofiles

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем FastAPI приложение
app = FastAPI(
    title="Mentor System Dashboard",
    description="Улучшенный дашборд для мониторинга системы Mentor",
    version="2.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DashboardManager:
    """Менеджер дашборда"""
    
    def __init__(self):
        self.connections: List[WebSocket] = []
        self.metrics_data = {}
        self.performance_history = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)
        logger.info(f"📊 Дашборд подключен. Всего соединений: {len(self.connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)
        logger.info(f"📊 Дашборд отключен. Всего соединений: {len(self.connections)}")
    
    async def broadcast(self, data: Dict[str, Any]):
        """Отправка данных всем подключенным клиентам"""
        if not self.connections:
            return
            
        message = json.dumps(data, ensure_ascii=False)
        disconnected = []
        
        for connection in self.connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        
        # Удаляем отключенные соединения
        for connection in disconnected:
            self.disconnect(connection)

# Менеджер дашборда
dashboard_manager = DashboardManager()

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Главная страница дашборда"""
    html_content = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mentor System Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
                color: #333;
            }
            
            .header {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                padding: 20px;
                box-shadow: 0 2px 20px rgba(0,0,0,0.1);
                position: sticky;
                top: 0;
                z-index: 100;
            }
            
            .header h1 {
                text-align: center;
                color: #2c3e50;
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            .header p {
                text-align: center;
                color: #7f8c8d;
                font-size: 1.1em;
            }
            
            .dashboard-container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .metric-card {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            
            .metric-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 12px 40px rgba(0,0,0,0.15);
            }
            
            .metric-card h3 {
                color: #2c3e50;
                margin-bottom: 15px;
                font-size: 1.3em;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .metric-value {
                font-size: 2.5em;
                font-weight: bold;
                color: #3498db;
                margin-bottom: 10px;
            }
            
            .metric-label {
                color: #7f8c8d;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .status-indicator {
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 8px;
            }
            
            .status-healthy { background: #27ae60; }
            .status-warning { background: #f39c12; }
            .status-critical { background: #e74c3c; }
            .status-unknown { background: #95a5a6; }
            
            .charts-section {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .chart-container {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .chart-container h3 {
                color: #2c3e50;
                margin-bottom: 20px;
                text-align: center;
            }
            
            .agents-section {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .agents-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            
            .agent-card {
                background: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                border-left: 4px solid #3498db;
                transition: all 0.3s ease;
            }
            
            .agent-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            
            .agent-card.active {
                border-left-color: #27ae60;
                background: #d5f4e6;
            }
            
            .agent-card.inactive {
                border-left-color: #e74c3c;
                background: #fadbd8;
            }
            
            .agent-name {
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 8px;
            }
            
            .agent-status {
                display: flex;
                align-items: center;
                margin-bottom: 10px;
            }
            
            .agent-metrics {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                font-size: 0.9em;
                color: #7f8c8d;
            }
            
            .performance-bar {
                width: 100%;
                height: 8px;
                background: #ecf0f1;
                border-radius: 4px;
                overflow: hidden;
                margin-top: 10px;
            }
            
            .performance-fill {
                height: 100%;
                background: linear-gradient(90deg, #e74c3c 0%, #f39c12 50%, #27ae60 100%);
                transition: width 0.3s ease;
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
                z-index: 1000;
            }
            
            .refresh-btn:hover {
                background: #2980b9;
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(52, 152, 219, 0.4);
            }
            
            .loading {
                text-align: center;
                padding: 40px;
                color: #7f8c8d;
                font-size: 1.2em;
            }
            
            .error {
                text-align: center;
                padding: 20px;
                color: #e74c3c;
                background: rgba(231, 76, 60, 0.1);
                border-radius: 10px;
                margin: 20px;
            }
            
            @media (max-width: 768px) {
                .charts-section {
                    grid-template-columns: 1fr;
                }
                
                .metrics-grid {
                    grid-template-columns: 1fr;
                }
                
                .agents-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🤖 Mentor System Dashboard</h1>
            <p>Мониторинг автономной системы множественных AI-агентов</p>
        </div>
        
        <div class="dashboard-container">
            <div class="metrics-grid">
                <div class="metric-card">
                    <h3><span class="status-indicator" id="systemStatusIndicator"></span>Статус системы</h3>
                    <div class="metric-value" id="systemStatus">Загрузка...</div>
                    <div class="metric-label">Общее состояние</div>
                </div>
                
                <div class="metric-card">
                    <h3>📊 Всего агентов</h3>
                    <div class="metric-value" id="totalAgents">0</div>
                    <div class="metric-label">Активных агентов</div>
                </div>
                
                <div class="metric-card">
                    <h3>⚡ Производительность</h3>
                    <div class="metric-value" id="overallPerformance">0%</div>
                    <div class="metric-label">Средняя производительность</div>
                </div>
                
                <div class="metric-card">
                    <h3>📈 Выполнено задач</h3>
                    <div class="metric-value" id="totalTasks">0</div>
                    <div class="metric-label">Всего задач</div>
                </div>
                
                <div class="metric-card">
                    <h3>⏱️ Время работы</h3>
                    <div class="metric-value" id="uptime">0м</div>
                    <div class="metric-label">Время работы системы</div>
                </div>
                
                <div class="metric-card">
                    <h3>💾 Использование памяти</h3>
                    <div class="metric-value" id="memoryUsage">0%</div>
                    <div class="metric-label">Загрузка памяти</div>
                </div>
            </div>
            
            <div class="charts-section">
                <div class="chart-container">
                    <h3>📊 Производительность агентов</h3>
                    <canvas id="performanceChart"></canvas>
                </div>
                
                <div class="chart-container">
                    <h3>📈 История активности</h3>
                    <canvas id="activityChart"></canvas>
                </div>
            </div>
            
            <div class="agents-section">
                <h3>🤖 Состояние агентов</h3>
                <div class="agents-grid" id="agentsGrid">
                    <div class="loading">Загрузка информации об агентах...</div>
                </div>
            </div>
        </div>
        
        <button class="refresh-btn" onclick="refreshDashboard()">🔄 Обновить</button>
        
        <script>
            let ws = null;
            let performanceChart = null;
            let activityChart = null;
            let lastUpdateTime = null;
            
            // Инициализация WebSocket соединения
            function initWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws/dashboard`;
                
                ws = new WebSocket(wsUrl);
                
                ws.onopen = function(event) {
                    console.log('WebSocket соединение установлено');
                    refreshDashboard();
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    updateDashboard(data);
                };
                
                ws.onclose = function(event) {
                    console.log('WebSocket соединение закрыто');
                    setTimeout(initWebSocket, 3000);
                };
                
                ws.onerror = function(error) {
                    console.error('WebSocket ошибка:', error);
                };
            }
            
            // Обновление дашборда
            function updateDashboard(data) {
                lastUpdateTime = new Date();
                
                // Обновляем основные метрики
                document.getElementById('systemStatus').textContent = data.system_status || 'unknown';
                document.getElementById('totalAgents').textContent = data.total_agents || 0;
                document.getElementById('overallPerformance').textContent = 
                    Math.round((data.overall_performance || 0) * 100) + '%';
                document.getElementById('totalTasks').textContent = data.total_tasks || 0;
                document.getElementById('uptime').textContent = data.uptime || '0м';
                
                // Обновляем индикатор статуса
                const statusIndicator = document.getElementById('systemStatusIndicator');
                const systemHealth = data.system_health || 'unknown';
                statusIndicator.className = 'status-indicator status-' + systemHealth;
                
                // Обновляем использование памяти
                if (data.coordination_status && data.coordination_status.agent_capabilities) {
                    const agents = Object.values(data.coordination_status.agent_capabilities);
                    const avgMemory = agents.reduce((sum, agent) => sum + (agent.current_load || 0), 0) / agents.length;
                    document.getElementById('memoryUsage').textContent = Math.round(avgMemory * 100) + '%';
                }
                
                // Обновляем агентов
                updateAgents(data.coordination_status?.agent_capabilities || {});
                
                // Обновляем графики
                updateCharts(data);
            }
            
            // Обновление информации об агентах
            function updateAgents(agents) {
                const agentsGrid = document.getElementById('agentsGrid');
                agentsGrid.innerHTML = '';
                
                Object.entries(agents).forEach(([agentId, agent]) => {
                    const agentCard = document.createElement('div');
                    agentCard.className = `agent-card ${agent.is_active ? 'active' : 'inactive'}`;
                    
                    const performancePercent = Math.round((agent.performance_score || 0) * 100);
                    
                    agentCard.innerHTML = `
                        <div class="agent-name">${agentId.replace('_', ' ').toUpperCase()}</div>
                        <div class="agent-status">
                            <span class="status-indicator ${agent.is_active ? 'status-healthy' : 'status-unknown'}"></span>
                            ${agent.is_active ? 'Активен' : 'Неактивен'}
                        </div>
                        <div class="agent-metrics">
                            <div>Задач: ${agent.tasks_completed || 0}</div>
                            <div>Ошибок: ${agent.tasks_failed || 0}</div>
                            <div>Время: ${agent.average_response_time ? agent.average_response_time.toFixed(2) + 'с' : 'N/A'}</div>
                            <div>Произв.: ${performancePercent}%</div>
                        </div>
                        <div class="performance-bar">
                            <div class="performance-fill" style="width: ${performancePercent}%"></div>
                        </div>
                    `;
                    
                    agentsGrid.appendChild(agentCard);
                });
            }
            
            // Обновление графиков
            function updateCharts(data) {
                // График производительности агентов
                if (data.coordination_status && data.coordination_status.agent_capabilities) {
                    const agents = Object.entries(data.coordination_status.agent_capabilities);
                    const labels = agents.map(([id, _]) => id.replace('_', ' ').toUpperCase());
                    const performanceData = agents.map(([_, agent]) => (agent.performance_score || 0) * 100);
                    
                    if (!performanceChart) {
                        const ctx = document.getElementById('performanceChart').getContext('2d');
                        performanceChart = new Chart(ctx, {
                            type: 'bar',
                            data: {
                                labels: labels,
                                datasets: [{
                                    label: 'Производительность (%)',
                                    data: performanceData,
                                    backgroundColor: performanceData.map(score => 
                                        score > 80 ? '#27ae60' : score > 60 ? '#f39c12' : '#e74c3c'
                                    ),
                                    borderColor: '#2c3e50',
                                    borderWidth: 1
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                scales: {
                                    y: {
                                        beginAtZero: true,
                                        max: 100
                                    }
                                }
                            }
                        });
                    } else {
                        performanceChart.data.labels = labels;
                        performanceChart.data.datasets[0].data = performanceData;
                        performanceChart.data.datasets[0].backgroundColor = performanceData.map(score => 
                            score > 80 ? '#27ae60' : score > 60 ? '#f39c12' : '#e74c3c'
                        );
                        performanceChart.update();
                    }
                }
                
                // График активности (заглушка)
                if (!activityChart) {
                    const ctx = document.getElementById('activityChart').getContext('2d');
                    activityChart = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: ['10м', '8м', '6м', '4м', '2м', 'Сейчас'],
                            datasets: [{
                                label: 'Активные агенты',
                                data: [2, 3, 4, 3, 5, data.active_agents || 0],
                                borderColor: '#3498db',
                                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                                tension: 0.4
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                y: {
                                    beginAtZero: true
                                }
                            }
                        }
                    });
                } else {
                    activityChart.data.datasets[0].data.shift();
                    activityChart.data.datasets[0].data.push(data.active_agents || 0);
                    activityChart.update();
                }
            }
            
            // Обновление дашборда
            function refreshDashboard() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({type: 'refresh'}));
                }
            }
            
            // Инициализация при загрузке страницы
            document.addEventListener('DOMContentLoaded', function() {
                initWebSocket();
                
                // Автообновление каждые 30 секунд
                setInterval(refreshDashboard, 30000);
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """WebSocket endpoint для дашборда"""
    await dashboard_manager.connect(websocket)
    
    try:
        while True:
            # Получаем сообщения от клиента
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "refresh":
                # Отправляем текущие данные
                await send_dashboard_data(websocket)
                
    except WebSocketDisconnect:
        dashboard_manager.disconnect(websocket)

async def send_dashboard_data(websocket: WebSocket):
    """Отправка данных дашборда"""
    try:
        # Получаем данные от оптимизированной системы
        from optimized_autonomous_system import get_optimized_system
        system = get_optimized_system()
        
        if system:
            status = system.get_system_status()
            await websocket.send_text(json.dumps(status, ensure_ascii=False))
        else:
            # Fallback к обычной системе
            import requests
            try:
                response = requests.get("http://localhost:8080/api/system/status", timeout=5)
                if response.status_code == 200:
                    await websocket.send_text(response.text)
            except:
                await websocket.send_text(json.dumps({
                    "error": "Система недоступна",
                    "system_status": "error"
                }))
                
    except Exception as e:
        logger.error(f"❌ Ошибка отправки данных дашборда: {e}")
        await websocket.send_text(json.dumps({
            "error": str(e),
            "system_status": "error"
        }))

@app.get("/api/dashboard/metrics")
async def get_dashboard_metrics():
    """Получить метрики для дашборда"""
    try:
        from optimized_autonomous_system import get_optimized_system
        system = get_optimized_system()
        
        if system:
            return JSONResponse(content=system.get_system_status())
        else:
            return JSONResponse(content={"error": "Система недоступна"})
            
    except Exception as e:
        logger.error(f"❌ Ошибка получения метрик: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/health")
async def get_system_health():
    """Получить состояние здоровья системы"""
    try:
        from optimized_autonomous_system import get_optimized_system
        system = get_optimized_system()
        
        if system:
            health = await system.health_check()
            return JSONResponse(content=health)
        else:
            return JSONResponse(content={"overall_health": "error", "error": "Система недоступна"})
            
    except Exception as e:
        logger.error(f"❌ Ошибка получения состояния здоровья: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/performance")
async def get_performance_history():
    """Получить историю производительности"""
    try:
        from optimized_autonomous_system import get_optimized_system
        system = get_optimized_system()
        
        if system:
            return JSONResponse(content={
                "performance_history": system.performance_history,
                "agent_metrics": {agent_id: metrics.to_dict() for agent_id, metrics in system.agent_metrics.items()}
            })
        else:
            return JSONResponse(content={"error": "Система недоступна"})
            
    except Exception as e:
        logger.error(f"❌ Ошибка получения истории производительности: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "enhanced_dashboard:app",
        host="0.0.0.0",
        port=8081,
        reload=True,
        log_level="info"
    )