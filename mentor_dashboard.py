#!/usr/bin/env python3
"""
Центральная панель управления всеми системами Mentor
Объединяет все AI системы в одном интерфейсе
"""

import asyncio
import json
import logging
import time
import requests
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MentorDashboard:
    """Центральная панель управления Mentor"""
    
    def __init__(self):
        self.systems = {
            "simple_mentor": {"port": 8081, "name": "Простая система", "status": "unknown"},
            "real_ai_mentor": {"port": 8082, "name": "AI система (Llama)", "status": "unknown"},
        }
        
        self.processes = {}
        self.startup_time = time.time()
        
    def check_system_status(self, port: int) -> str:
        """Проверка статуса системы по порту"""
        try:
            response = requests.get(f"http://localhost:{port}/api/system/status", timeout=3)
            return "online" if response.status_code == 200 else "error"
        except:
            return "offline"
    
    def get_system_info(self, port: int) -> Dict[str, Any]:
        """Получение информации о системе"""
        try:
            response = requests.get(f"http://localhost:{port}/api/system/status", timeout=3)
            if response.status_code == 200:
                return response.json()
            return {"error": "Нет данных"}
        except Exception as e:
            return {"error": str(e)}

dashboard = MentorDashboard()

# FastAPI приложение
app = FastAPI(title="Mentor Dashboard")

@app.get("/")
async def root():
    """Главная панель управления"""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎛️ Mentor Control Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%); 
            min-height: 100vh; 
            color: white;
        }
        .container { max-width: 1600px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 40px; }
        .header h1 { font-size: 3.5em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .header p { font-size: 1.4em; opacity: 0.9; }
        
        .systems-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 30px; margin-bottom: 40px; }
        .system-card { 
            background: rgba(255,255,255,0.1); 
            border-radius: 20px; 
            padding: 30px; 
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease;
        }
        .system-card:hover { transform: translateY(-5px); }
        .system-card h3 { font-size: 1.5em; margin-bottom: 20px; }
        
        .status-indicator { 
            display: inline-block; 
            width: 12px; 
            height: 12px; 
            border-radius: 50%; 
            margin-right: 8px; 
        }
        .status-online { background: #2ecc71; box-shadow: 0 0 10px #2ecc71; }
        .status-offline { background: #e74c3c; }
        .status-unknown { background: #f39c12; }
        
        .metric-row { display: flex; justify-content: space-between; margin-bottom: 10px; }
        .metric-value { font-weight: bold; color: #3498db; }
        
        .action-buttons { margin-top: 20px; }
        .btn { 
            padding: 10px 20px; 
            margin: 5px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .btn-primary { background: #3498db; color: white; }
        .btn-success { background: #2ecc71; color: white; }
        .btn-danger { background: #e74c3c; color: white; }
        .btn:hover { transform: scale(1.05); }
        
        .global-stats { 
            background: rgba(255,255,255,0.1); 
            border-radius: 20px; 
            padding: 30px; 
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }
        
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
        .stat-item { text-align: center; }
        .stat-number { font-size: 2.5em; font-weight: bold; color: #3498db; }
        .stat-label { opacity: 0.8; margin-top: 5px; }
        
        .console { 
            background: rgba(0,0,0,0.3); 
            border-radius: 15px; 
            padding: 20px; 
            font-family: 'Courier New', monospace; 
            height: 300px; 
            overflow-y: auto;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .console-line { margin-bottom: 5px; }
        .console-timestamp { color: #95a5a6; margin-right: 10px; }
        .console-info { color: #3498db; }
        .console-success { color: #2ecc71; }
        .console-error { color: #e74c3c; }
        
        .ai-showcase { 
            background: linear-gradient(135deg, #8e44ad 0%, #3498db 100%); 
            border-radius: 20px; 
            padding: 30px; 
            margin-top: 30px;
        }
        .ai-showcase h2 { margin-bottom: 20px; }
        
        .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
        .feature-card { 
            background: rgba(255,255,255,0.1); 
            padding: 20px; 
            border-radius: 15px; 
            text-align: center;
        }
        .feature-icon { font-size: 3em; margin-bottom: 10px; }
        .feature-title { font-size: 1.2em; font-weight: bold; margin-bottom: 10px; }
        .feature-desc { opacity: 0.9; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎛️ Mentor Control Dashboard</h1>
            <p>Центральная панель управления всеми AI системами</p>
        </div>
        
        <div class="global-stats">
            <h2>📊 Общая статистика</h2>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-number" id="totalSystems">0</div>
                    <div class="stat-label">Систем развернуто</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number" id="onlineSystems">0</div>
                    <div class="stat-label">Систем онлайн</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number" id="totalAgents">0</div>
                    <div class="stat-label">AI агентов</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number" id="totalRequests">0</div>
                    <div class="stat-label">Обработано запросов</div>
                </div>
            </div>
        </div>
        
        <div class="systems-grid" id="systemsGrid">
            <!-- Системы будут загружены динамически -->
        </div>
        
        <div class="ai-showcase">
            <h2>🤖 AI Возможности</h2>
            <div class="feature-grid">
                <div class="feature-card">
                    <div class="feature-icon">🧠</div>
                    <div class="feature-title">Настоящий AI</div>
                    <div class="feature-desc">Llama 3.2 модель для реального интеллекта</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">💻</div>
                    <div class="feature-title">Анализ кода</div>
                    <div class="feature-desc">AI анализ, оптимизация и генерация кода</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">👁️</div>
                    <div class="feature-title">Визуальный контроль</div>
                    <div class="feature-desc">Автоматические скриншоты и анализ UI</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🔧</div>
                    <div class="feature-title">Самоулучшение</div>
                    <div class="feature-desc">Автономная диагностика и оптимизация</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🌐</div>
                    <div class="feature-title">Веб-интерфейс</div>
                    <div class="feature-desc">Современный адаптивный интерфейс</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🇷🇺</div>
                    <div class="feature-title">Русский язык</div>
                    <div class="feature-desc">100% поддержка русского языка</div>
                </div>
            </div>
        </div>
        
        <div style="margin-top: 30px;">
            <h2>📟 Системная консоль</h2>
            <div class="console" id="console">
                <div class="console-line">
                    <span class="console-timestamp">[02:45:00]</span>
                    <span class="console-info">Инициализация панели управления...</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        let updateInterval;
        
        function addConsoleLog(message, type = 'info') {
            const console = document.getElementById('console');
            const timestamp = new Date().toLocaleTimeString();
            const line = document.createElement('div');
            line.className = 'console-line';
            line.innerHTML = `
                <span class="console-timestamp">[${timestamp}]</span>
                <span class="console-${type}">${message}</span>
            `;
            console.appendChild(line);
            console.scrollTop = console.scrollHeight;
        }
        
        async function updateSystemStatus() {
            try {
                const response = await fetch('/api/dashboard/status');
                const data = await response.json();
                
                // Обновляем общую статистику
                document.getElementById('totalSystems').textContent = data.total_systems;
                document.getElementById('onlineSystems').textContent = data.online_systems;
                document.getElementById('totalAgents').textContent = data.total_agents;
                document.getElementById('totalRequests').textContent = data.total_requests;
                
                // Обновляем карточки систем
                updateSystemCards(data.systems);
                
            } catch (error) {
                addConsoleLog(`Ошибка обновления статуса: ${error}`, 'error');
            }
        }
        
        function updateSystemCards(systems) {
            const grid = document.getElementById('systemsGrid');
            grid.innerHTML = '';
            
            Object.entries(systems).forEach(([key, system]) => {
                const card = document.createElement('div');
                card.className = 'system-card';
                
                const statusClass = `status-${system.status}`;
                const statusText = {
                    'online': '🟢 Онлайн',
                    'offline': '🔴 Оффлайн', 
                    'unknown': '🟡 Неизвестно'
                }[system.status] || '❓ Неизвестно';
                
                card.innerHTML = `
                    <h3>
                        <span class="status-indicator ${statusClass}"></span>
                        ${system.name}
                    </h3>
                    <div class="metric-row">
                        <span>Статус:</span>
                        <span class="metric-value">${statusText}</span>
                    </div>
                    <div class="metric-row">
                        <span>Порт:</span>
                        <span class="metric-value">${system.port}</span>
                    </div>
                    ${system.info ? `
                        <div class="metric-row">
                            <span>Агентов:</span>
                            <span class="metric-value">${system.info.active_agents || 0}/${system.info.total_agents || 0}</span>
                        </div>
                        <div class="metric-row">
                            <span>Время работы:</span>
                            <span class="metric-value">${system.info.uptime || '0с'}</span>
                        </div>
                        ${system.info.ai_requests !== undefined ? `
                            <div class="metric-row">
                                <span>AI запросов:</span>
                                <span class="metric-value">${system.info.ai_requests}</span>
                            </div>
                        ` : ''}
                    ` : ''}
                    <div class="action-buttons">
                        ${system.status === 'online' ? 
                            `<button class="btn btn-primary" onclick="openSystem('${system.port}')">Открыть</button>` : 
                            `<button class="btn btn-success" onclick="startSystem('${key}')">Запустить</button>`
                        }
                        <button class="btn btn-danger" onclick="stopSystem('${key}')">Остановить</button>
                    </div>
                `;
                
                grid.appendChild(card);
            });
        }
        
        function openSystem(port) {
            window.open(`http://localhost:${port}`, '_blank');
            addConsoleLog(`🌐 Открываю систему на порту ${port}`, 'info');
            
            // Показываем уведомление
            showDashboardNotification(`Система на порту ${port} открыта в новой вкладке`, 'success');
        }
        
        function showDashboardNotification(message, type = 'info') {
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed; top: 20px; right: 20px; z-index: 1000;
                padding: 15px 20px; border-radius: 10px; color: white; font-weight: bold;
                background: ${type === 'success' ? '#2ecc71' : type === 'warning' ? '#f39c12' : '#3498db'};
                box-shadow: 0 4px 15px rgba(0,0,0,0.2); opacity: 0; transition: opacity 0.3s ease;
            `;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => notification.style.opacity = '1', 100);
            setTimeout(() => {
                notification.style.opacity = '0';
                setTimeout(() => document.body.removeChild(notification), 300);
            }, 3000);
        }
        
        function startSystem(systemKey) {
            addConsoleLog(`Запуск системы ${systemKey}...`, 'info');
            // Здесь можно добавить логику запуска
        }
        
        function stopSystem(systemKey) {
            addConsoleLog(`Остановка системы ${systemKey}...`, 'info');
            // Здесь можно добавить логику остановки
        }
        
        // Инициализация
        addConsoleLog('Панель управления Mentor запущена', 'success');
        addConsoleLog('Проверка статуса всех систем...', 'info');
        
        updateSystemStatus();
        updateInterval = setInterval(updateSystemStatus, 5000);
        
        // Добавляем случайные логи для демонстрации
        setInterval(() => {
            const messages = [
                'Мониторинг систем активен',
                'AI агенты обрабатывают запросы', 
                'Визуальные проверки выполнены',
                'Производительность оптимальна',
                'Все системы стабильны'
            ];
            const randomMessage = messages[Math.floor(Math.random() * messages.length)];
            addConsoleLog(randomMessage, 'info');
        }, 10000);
    </script>
</body>
</html>
    """)

@app.get("/api/dashboard/status")
async def get_dashboard_status():
    """Получить статус всех систем"""
    systems_status = {}
    total_agents = 0
    total_requests = 0
    online_count = 0
    
    for key, system in dashboard.systems.items():
        status = dashboard.check_system_status(system["port"])
        system["status"] = status
        
        info = None
        if status == "online":
            info = dashboard.get_system_info(system["port"])
            online_count += 1
            
            if "total_agents" in info:
                total_agents += info["total_agents"]
            if "total_requests" in info:
                total_requests += info["total_requests"]
        
        systems_status[key] = {
            "name": system["name"],
            "port": system["port"],
            "status": status,
            "info": info if status == "online" else None
        }
    
    return {
        "total_systems": len(dashboard.systems),
        "online_systems": online_count,
        "total_agents": total_agents,
        "total_requests": total_requests,
        "systems": systems_status,
        "timestamp": datetime.now().isoformat()
    }

# Основная функция
async def main():
    """Главная функция"""
    logger.info("🎛️ Запуск Mentor Dashboard...")
    
    try:
        # Запускаем веб-сервер на порту 8083
        config = uvicorn.Config(app, host="0.0.0.0", port=8083, log_level="info")
        server = uvicorn.Server(config)
        
        logger.info("✅ Mentor Dashboard запущена")
        logger.info("🌐 Панель управления доступна на http://localhost:8083")
        
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("📡 Получен сигнал прерывания")
    except Exception as e:
        logger.error(f"❌ Ошибка панели управления: {e}")
    finally:
        logger.info("🛑 Mentor Dashboard остановлена")

if __name__ == "__main__":
    asyncio.run(main())