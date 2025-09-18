"""
AI Manager - Главный модуль системы управления AI агентами
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import uvicorn
import asyncio
from typing import List, Dict, Any

from core.task_analyzer import TaskAnalyzer
from core.ai_manager import AIManager
from core.task_executor import TaskExecutor
from models.task import Task, TaskStatus
from models.agent import Agent, AgentType
from database.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация и очистка ресурсов при запуске/остановке приложения"""
    # Инициализация базы данных
    await init_db()
    
    # Инициализация компонентов системы
    app.state.task_analyzer = TaskAnalyzer()
    app.state.ai_manager = AIManager()
    app.state.task_executor = TaskExecutor()
    
    # Инициализация AI провайдеров
    from ai_providers.provider_manager import provider_manager
    await provider_manager.initialize_providers()
    
    yield
    
    # Очистка ресурсов при остановке
    await app.state.task_executor.cleanup()
    await provider_manager.close_all()


app = FastAPI(
    title="AI Manager",
    description="Система генерации и управления AI агентами",
    version="1.0.0",
    lifespan=lifespan
)

# Подключение статических файлов для веб-интерфейса
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Главная страница веб-интерфейса"""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.post("/api/tasks")
async def create_task(task_data: Dict[str, Any]):
    """Создание новой задачи"""
    try:
        # Создание задачи
        task = Task(
            description=task_data["description"],
            priority=task_data.get("priority", "medium"),
            category=task_data.get("category", "general")
        )
        
        # Анализ задачи
        analysis = await app.state.task_analyzer.analyze_task(task)
        
        # Создание AI агента для задачи
        agent = await app.state.ai_manager.create_agent_for_task(analysis)
        
        # Запуск выполнения задачи
        result = await app.state.task_executor.execute_task(task, agent)
        
        return {
            "task_id": task.id,
            "agent_id": agent.id,
            "status": task.status,
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """Получение информации о задаче"""
    task = await app.state.task_executor.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "id": task.id,
        "description": task.description,
        "status": task.status,
        "created_at": task.created_at,
        "agent_id": task.agent_id,
        "result": task.result
    }


@app.get("/api/agents")
async def get_agents():
    """Получение списка активных агентов"""
    agents = await app.state.ai_manager.get_active_agents()
    return [{"id": agent.id, "type": agent.type, "status": agent.status} for agent in agents]


@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Получение информации об агенте"""
    agent = await app.state.ai_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {
        "id": agent.id,
        "type": agent.type,
        "status": agent.status,
        "created_at": agent.created_at,
        "tasks_completed": agent.tasks_completed
    }


@app.post("/api/agents/{agent_id}/stop")
async def stop_agent(agent_id: str):
    """Остановка агента"""
    success = await app.state.ai_manager.stop_agent(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {"message": "Agent stopped successfully"}


@app.get("/api/stats")
async def get_system_stats():
    """Получение статистики системы"""
    stats = await app.state.task_executor.get_system_stats()
    
    # Добавляем статистику AI провайдеров
    from ai_providers.provider_manager import provider_manager
    provider_stats = await provider_manager.get_provider_health()
    
    stats["ai_providers"] = provider_stats
    stats["default_provider"] = provider_manager.get_default_provider_name()
    
    return stats


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
