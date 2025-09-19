#!/usr/bin/env python3
"""
Unified AI Ecosystem - API Gateway
Объединяет все три проекта в единую систему
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import httpx
import asyncio
import logging
from typing import Dict, Any
import uvicorn

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Unified AI Ecosystem",
    description="Объединенная экосистема AI проектов: MENTOR + AI Manager + JARVIS",
    version="1.0.0"
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# URL сервисов
SERVICES = {
    "mentor": "http://localhost:8080",
    "ai_manager": "http://localhost:8000", 
    "jarvis": "http://localhost:8081"  # Изменяем порт JARVIS
}

# Статистика запросов
request_stats = {
    "mentor": 0,
    "ai_manager": 0,
    "jarvis": 0,
    "total": 0
}

@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница с информацией о системе"""
    html_content = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Unified AI Ecosystem</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                text-align: center;
                margin-bottom: 40px;
            }
            .ecosystem-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }
            .service-card {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 30px;
                text-align: center;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: transform 0.3s ease;
            }
            .service-card:hover {
                transform: translateY(-5px);
            }
            .mentor-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
            .ai-manager-card { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
            .jarvis-card { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
            .btn {
                background: rgba(255, 255, 255, 0.2);
                border: none;
                padding: 12px 24px;
                border-radius: 25px;
                color: white;
                cursor: pointer;
                font-size: 16px;
                margin: 10px;
                transition: all 0.3s ease;
            }
            .btn:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: scale(1.05);
            }
            .stats {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 20px;
                margin-top: 20px;
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
            }
            .stat-item {
                text-align: center;
                padding: 15px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌐 Unified AI Ecosystem</h1>
                <p>Объединенная экосистема AI проектов</p>
            </div>
            
            <div class="ecosystem-grid">
                <div class="service-card mentor-card">
                    <h2>🤖 MENTOR</h2>
                    <p>Многоагентная система выполнения задач</p>
                    <p><strong>Порт:</strong> 8080</p>
                    <p><strong>Статус:</strong> <span id="mentor-status">Проверка...</span></p>
                    <button class="btn" onclick="openService('mentor')">Открыть MENTOR</button>
                    <button class="btn" onclick="checkService('mentor')">Проверить статус</button>
                </div>
                
                <div class="service-card ai-manager-card">
                    <h2>🏭 AI MANAGER</h2>
                    <p>Генерация и управление AI агентами</p>
                    <p><strong>Порт:</strong> 8000</p>
                    <p><strong>Статус:</strong> <span id="ai-manager-status">Проверка...</span></p>
                    <button class="btn" onclick="openService('ai_manager')">Открыть AI Manager</button>
                    <button class="btn" onclick="checkService('ai_manager')">Проверить статус</button>
                </div>
                
                <div class="service-card jarvis-card">
                    <h2>🧠 JARVIS DATA</h2>
                    <p>Система знаний и автоматизации</p>
                    <p><strong>Порт:</strong> 8081</p>
                    <p><strong>Статус:</strong> <span id="jarvis-status">Проверка...</span></p>
                    <button class="btn" onclick="openService('jarvis')">Открыть JARVIS</button>
                    <button class="btn" onclick="checkService('jarvis')">Проверить статус</button>
                </div>
            </div>
            
            <div class="stats">
                <h3>📊 Статистика запросов</h3>
                <div class="stats-grid">
                    <div class="stat-item">
                        <h4>MENTOR</h4>
                        <p id="mentor-requests">0</p>
                    </div>
                    <div class="stat-item">
                        <h4>AI Manager</h4>
                        <p id="ai-manager-requests">0</p>
                    </div>
                    <div class="stat-item">
                        <h4>JARVIS</h4>
                        <p id="jarvis-requests">0</p>
                    </div>
                    <div class="stat-item">
                        <h4>Всего</h4>
                        <p id="total-requests">0</p>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            const services = {
                'mentor': 'http://localhost:8080',
                'ai_manager': 'http://localhost:8000',
                'jarvis': 'http://localhost:8081'
            };
            
            function openService(serviceName) {
                const url = services[serviceName];
                window.open(url, '_blank');
            }
            
            async function checkService(serviceName) {
                const statusElement = document.getElementById(serviceName + '-status');
                statusElement.textContent = 'Проверка...';
                
                try {
                    const response = await fetch(`/api/status/${serviceName}`);
                    const data = await response.json();
                    statusElement.textContent = data.status;
                    statusElement.style.color = data.status === 'online' ? '#4CAF50' : '#F44336';
                } catch (error) {
                    statusElement.textContent = 'offline';
                    statusElement.style.color = '#F44336';
                }
            }
            
            async function updateStats() {
                try {
                    const response = await fetch('/api/stats');
                    const stats = await response.json();
                    
                    document.getElementById('mentor-requests').textContent = stats.mentor;
                    document.getElementById('ai-manager-requests').textContent = stats.ai_manager;
                    document.getElementById('jarvis-requests').textContent = stats.jarvis;
                    document.getElementById('total-requests').textContent = stats.total;
                } catch (error) {
                    console.error('Ошибка получения статистики:', error);
                }
            }
            
            // Проверяем статус всех сервисов при загрузке
            document.addEventListener('DOMContentLoaded', function() {
                Object.keys(services).forEach(checkService);
                updateStats();
                
                // Обновляем статистику каждые 5 секунд
                setInterval(updateStats, 5000);
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/status/{service_name}")
async def check_service_status(service_name: str):
    """Проверить статус конкретного сервиса"""
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail="Сервис не найден")
    
    service_url = SERVICES[service_name]
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{service_url}/api/system/status")
            if response.status_code == 200:
                return {"status": "online", "url": service_url}
            else:
                return {"status": "error", "url": service_url}
    except Exception as e:
        logger.error(f"Ошибка проверки сервиса {service_name}: {e}")
        return {"status": "offline", "url": service_url}

@app.get("/api/stats")
async def get_request_stats():
    """Получить статистику запросов"""
    return request_stats

@app.get("/api/services")
async def get_services_info():
    """Получить информацию о всех сервисах"""
    return {
        "services": SERVICES,
        "gateway_port": 9000,
        "description": "Unified AI Ecosystem Gateway"
    }

# Проксирование запросов к MENTOR
@app.api_route("/mentor/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def mentor_proxy(path: str, request: Request):
    """Проксирование запросов к MENTOR"""
    return await proxy_request("mentor", path, request)

# Проксирование запросов к AI Manager
@app.api_route("/ai-manager/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def ai_manager_proxy(path: str, request: Request):
    """Проксирование запросов к AI Manager"""
    return await proxy_request("ai_manager", path, request)

# Проксирование запросов к JARVIS
@app.api_route("/jarvis/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def jarvis_proxy(path: str, request: Request):
    """Проксирование запросов к JARVIS"""
    return await proxy_request("jarvis", path, request)

async def proxy_request(service_name: str, path: str, request: Request):
    """Универсальная функция проксирования"""
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail="Сервис не найден")
    
    service_url = SERVICES[service_name]
    target_url = f"{service_url}/{path}"
    
    # Обновляем статистику
    request_stats[service_name] += 1
    request_stats["total"] += 1
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Получаем заголовки запроса
            headers = dict(request.headers)
            # Удаляем host заголовок, чтобы избежать конфликтов
            headers.pop("host", None)
            
            # Выполняем запрос
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=await request.body(),
                params=request.query_params
            )
            
            # Возвращаем ответ
            return JSONResponse(
                content=response.json() if response.headers.get("content-type", "").startswith("application/json") else {"data": response.text},
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
    except httpx.TimeoutException:
        logger.error(f"Таймаут запроса к {service_name}: {target_url}")
        raise HTTPException(status_code=504, detail="Таймаут сервиса")
    except httpx.ConnectError:
        logger.error(f"Ошибка подключения к {service_name}: {target_url}")
        raise HTTPException(status_code=503, detail="Сервис недоступен")
    except Exception as e:
        logger.error(f"Ошибка проксирования к {service_name}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

# Интеграционные API endpoints
@app.post("/api/integration/create-agent")
async def create_agent_integration(agent_config: Dict[str, Any]):
    """Создать агента через интеграцию сервисов"""
    try:
        # 1. Создаем агента через AI Manager
        async with httpx.AsyncClient() as client:
            ai_manager_response = await client.post(
                f"{SERVICES['ai_manager']}/api/agents/create",
                json=agent_config
            )
            
            if ai_manager_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Ошибка создания агента в AI Manager")
            
            agent_data = ai_manager_response.json()
            
            # 2. Регистрируем агента в MENTOR
            mentor_response = await client.post(
                f"{SERVICES['mentor']}/api/agents/register",
                json=agent_data
            )
            
            if mentor_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Ошибка регистрации агента в MENTOR")
            
            # 3. Сохраняем знания в JARVIS
            jarvis_response = await client.post(
                f"{SERVICES['jarvis']}/api/knowledge/store",
                json={
                    "type": "agent",
                    "data": agent_data,
                    "source": "ai_manager"
                }
            )
            
            return {
                "success": True,
                "agent": agent_data,
                "mentor_registration": mentor_response.json(),
                "jarvis_storage": jarvis_response.json() if jarvis_response.status_code == 200 else None
            }
            
    except Exception as e:
        logger.error(f"Ошибка интеграции создания агента: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/integration/execute-task")
async def execute_task_integration(task_config: Dict[str, Any]):
    """Выполнить задачу через интеграцию всех сервисов"""
    try:
        async with httpx.AsyncClient() as client:
            # 1. Получаем знания из JARVIS
            knowledge_response = await client.get(
                f"{SERVICES['jarvis']}/api/knowledge/search",
                params={"query": task_config.get("description", "")}
            )
            
            knowledge = knowledge_response.json() if knowledge_response.status_code == 200 else {}
            
            # 2. Создаем агента через AI Manager
            agent_config = {
                "task_type": task_config.get("type", "general"),
                "knowledge": knowledge,
                "requirements": task_config.get("requirements", [])
            }
            
            agent_response = await client.post(
                f"{SERVICES['ai_manager']}/api/agents/create-for-task",
                json=agent_config
            )
            
            if agent_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Ошибка создания агента для задачи")
            
            agent_data = agent_response.json()
            
            # 3. Выполняем задачу через MENTOR
            task_response = await client.post(
                f"{SERVICES['mentor']}/api/tasks/execute",
                json={
                    "task": task_config,
                    "agent": agent_data
                }
            )
            
            if task_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Ошибка выполнения задачи")
            
            result = task_response.json()
            
            # 4. Сохраняем результат в JARVIS
            await client.post(
                f"{SERVICES['jarvis']}/api/knowledge/store",
                json={
                    "type": "task_result",
                    "data": result,
                    "source": "mentor"
                }
            )
            
            return {
                "success": True,
                "task": task_config,
                "agent": agent_data,
                "result": result,
                "knowledge_used": knowledge
            }
            
    except Exception as e:
        logger.error(f"Ошибка интеграции выполнения задачи: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("🚀 Запуск Unified AI Ecosystem Gateway...")
    logger.info(f"📡 Сервисы: {SERVICES}")
    logger.info("🌐 Доступ: http://localhost:9000")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=9000,
        reload=True,
        log_level="info"
    )

