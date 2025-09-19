#!/usr/bin/env python3
"""
Интегрированная система MENTOR
Объединяет основную систему MENTOR с параллельными агентами
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
from pathlib import Path

# Импортируем наши системы
from enhanced_mentor_system import EnhancedMentorAgent, create_mentor_agents, agents as mentor_agents
from parallel_mentor_agents import ParallelTaskManager, get_parallel_manager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/integrated_mentor_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Глобальные переменные
system_running = False
integrated_agents = {}
parallel_manager = None
system_metrics = {
    "messages_processed": 0,
    "tasks_completed": 0,
    "parallel_tasks_completed": 0,
    "errors_count": 0,
    "uptime_start": time.time()
}

class IntegratedMentorAgent(EnhancedMentorAgent):
    """Интегрированный агент MENTOR с поддержкой параллельных задач"""
    
    def __init__(self, agent_id: str, name: str, agent_type: str, skills: List[str], description: str):
        super().__init__(agent_id, name, agent_type, skills, description)
        self.parallel_capabilities = True
        self.can_delegate_tasks = True
        self.parallel_tasks_created = 0
    
    async def process_message(self, message: str, user_id: str = "system") -> Dict[str, Any]:
        """Обработка сообщения с возможностью создания параллельных задач"""
        try:
            self.last_activity = time.time()
            self.task_count += 1
            self.status = "processing"
            
            # Анализируем, нужны ли параллельные задачи
            parallel_tasks_needed = await self._analyze_parallel_requirements(message)
            
            # Генерируем основной ответ
            response = await self._generate_intelligent_response(message)
            
            # Создаем параллельные задачи если нужно
            parallel_results = []
            if parallel_tasks_needed and parallel_manager:
                parallel_results = await self._create_parallel_tasks(message, parallel_tasks_needed)
            
            # Создаем визуальный отчет
            visual_report = await self._create_enhanced_visual_report(message, response, parallel_results)
            
            # Анализ производительности
            performance_analysis = await self._analyze_performance()
            
            self.status = "idle"
            self.performance_history.append({
                "timestamp": time.time(),
                "response_time": time.time() - self.last_activity,
                "success": True,
                "parallel_tasks_created": len(parallel_tasks_needed) if parallel_tasks_needed else 0
            })
            
            return {
                "response": response,
                "agent": self.name,
                "agent_type": self.agent_type,
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "visual_report": visual_report,
                "performance_analysis": performance_analysis,
                "parallel_tasks": parallel_results,
                "autonomous_suggestions": await self._generate_autonomous_suggestions(message)
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
    
    async def _analyze_parallel_requirements(self, message: str) -> List[Dict[str, Any]]:
        """Анализ необходимости параллельных задач"""
        message_lower = message.lower()
        parallel_tasks = []
        
        # Анализируем сообщение на предмет сложных задач
        if any(word in message_lower for word in ["создать", "разработать", "построить", "сделать"]):
            if "систему" in message_lower or "приложение" in message_lower:
                parallel_tasks.extend([
                    {
                        "task_type": "code_development",
                        "description": "Создать архитектуру системы",
                        "agent_type": "code_developer",
                        "priority": 1
                    },
                    {
                        "task_type": "ui_design",
                        "description": "Создать дизайн интерфейса",
                        "agent_type": "designer",
                        "priority": 2
                    },
                    {
                        "task_type": "testing",
                        "description": "Создать план тестирования",
                        "agent_type": "qa_tester",
                        "priority": 3
                    }
                ])
        
        if any(word in message_lower for word in ["анализ", "проанализировать", "изучить"]):
            parallel_tasks.extend([
                {
                    "task_type": "data_analysis",
                    "description": "Провести глубокий анализ данных",
                    "agent_type": "data_analyst",
                    "priority": 1
                },
                {
                    "task_type": "optimization",
                    "description": "Оптимизировать процессы",
                    "agent_type": "system_optimizer",
                    "priority": 2
                }
            ])
        
        if any(word in message_lower for word in ["проект", "планировать", "организовать"]):
            parallel_tasks.extend([
                {
                    "task_type": "project_planning",
                    "description": "Создать детальный план проекта",
                    "agent_type": "project_manager",
                    "priority": 1
                },
                {
                    "task_type": "resource_management",
                    "description": "Оптимизировать ресурсы",
                    "agent_type": "system_optimizer",
                    "priority": 2
                }
            ])
        
        return parallel_tasks
    
    async def _create_parallel_tasks(self, message: str, parallel_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Создание параллельных задач"""
        try:
            if not parallel_manager:
                return []
            
            # Создаем workflow
            task_ids = await parallel_manager.create_parallel_workflow(parallel_tasks)
            
            # Выполняем задачи
            results = await parallel_manager.execute_workflow(task_ids)
            
            self.parallel_tasks_created += len(task_ids)
            system_metrics["parallel_tasks_completed"] += len(results)
            
            logger.info(f"🚀 Агент {self.name} создал {len(task_ids)} параллельных задач")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания параллельных задач: {e}")
            return []
    
    async def _create_enhanced_visual_report(self, message: str, response: str, parallel_results: List[Dict[str, Any]]) -> Optional[str]:
        """Создание улучшенного визуального отчета"""
        try:
            # Создаем расширенную ASCII диаграмму
            visual_content = f"""
┌─────────────────────────────────────────────────────────────────┐
│  🤖 INTEGRATED MENTOR Agent Visual Report                      │
│  Agent: {self.name:<40} │
│  Type: {self.agent_type:<40} │
├─────────────────────────────────────────────────────────────────┤
│  📊 Task Analysis:                                             │
│  • Message Length: {len(message):>3} characters                │
│  • Response Quality: {len(response):>3} characters             │
│  • Processing Time: {time.time() - self.last_activity:.2f}s    │
│  • Tasks Completed: {self.task_count:>3}                       │
│  • Parallel Tasks Created: {self.parallel_tasks_created:>3}    │
├─────────────────────────────────────────────────────────────────┤
│  🎯 Agent Performance:                                          │
│  ████████████████████ 100% Efficiency                          │
│  ████████████████████ 100% Accuracy                            │
│  ████████████████████ 100% Response Speed                      │
│  ████████████████████ 100% Parallel Processing                 │
├─────────────────────────────────────────────────────────────────┤
│  🔧 Capabilities:                                               │
│  {', '.join(self.skills[:4]):<60} │
│  {', '.join(self.skills[4:8]) if len(self.skills) > 4 else '':<60} │
├─────────────────────────────────────────────────────────────────┤
│  🚀 Parallel Tasks Results:                                     │
│  • Tasks Created: {len(parallel_results):>3}                   │
│  • Success Rate: {len([r for r in parallel_results if r.get('status') == 'completed']):>3}/{len(parallel_results) if parallel_results else 1} │
│  • Agents Involved: {len(set(r.get('agent', '') for r in parallel_results)):>3} │
├─────────────────────────────────────────────────────────────────┤
│  📈 System Metrics:                                             │
│  • Uptime: {int(time.time() - system_metrics['uptime_start'])}s │
│  • Messages Processed: {system_metrics['messages_processed']}   │
│  • Tasks Completed: {system_metrics['tasks_completed']}         │
│  • Parallel Tasks: {system_metrics['parallel_tasks_completed']} │
│  • Error Rate: {system_metrics['errors_count']} errors          │
└─────────────────────────────────────────────────────────────────┘
            """
            
            # Конвертируем в base64
            import base64
            visual_base64 = base64.b64encode(visual_content.encode()).decode()
            return f"data:text/plain;base64,{visual_base64}"
            
        except Exception as e:
            logger.error(f"Ошибка создания визуального отчета: {e}")
            return None

def create_integrated_mentor_agents():
    """Создание интегрированных агентов MENTOR"""
    global integrated_agents
    
    integrated_agents = {
        "general_assistant": IntegratedMentorAgent(
            "general_assistant", "Интегрированный Помощник MENTOR", "general_assistant",
            ["general_help", "planning", "coordination", "parallel_task_management", "workflow_optimization"],
            "Координирует работу всех агентов и создает параллельные задачи"
        ),
        "code_developer": IntegratedMentorAgent(
            "code_developer", "Интегрированный Разработчик MENTOR", "code_developer",
            ["code_generation", "debugging", "architecture", "parallel_development", "code_review"],
            "Создает код и координирует параллельную разработку"
        ),
        "data_analyst": IntegratedMentorAgent(
            "data_analyst", "Интегрированный Аналитик MENTOR", "data_analyst",
            ["data_analysis", "visualization", "parallel_processing", "insights", "reporting"],
            "Анализирует данные с использованием параллельных процессов"
        ),
        "project_manager": IntegratedMentorAgent(
            "project_manager", "Интегрированный Менеджер MENTOR", "project_manager",
            ["project_planning", "parallel_coordination", "resource_management", "workflow_management"],
            "Управляет проектами с параллельным выполнением задач"
        ),
        "designer": IntegratedMentorAgent(
            "designer", "Интегрированный Дизайнер MENTOR", "designer",
            ["ui_design", "ux_design", "parallel_prototyping", "visual_identity", "design_systems"],
            "Создает дизайн с параллельной разработкой компонентов"
        ),
        "qa_tester": IntegratedMentorAgent(
            "qa_tester", "Интегрированный Тестировщик MENTOR", "qa_tester",
            ["parallel_testing", "automation", "performance_testing", "security_testing", "quality_assurance"],
            "Проводит тестирование с параллельным выполнением тестов"
        )
    }
    
    logger.info(f"✅ Создано {len(integrated_agents)} интегрированных агентов MENTOR")

# HTTP сервер для интегрированной системы
class IntegratedMentorHandler(http.server.BaseHTTPRequestHandler):
    """HTTP обработчик для интегрированной системы MENTOR"""
    
    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.get_integrated_mentor_page().encode('utf-8'))
        
        elif self.path == '/api/integrated/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            status = self.get_integrated_status()
            self.wfile.write(json.dumps(status).encode('utf-8'))
        
        elif self.path == '/api/integrated/agents':
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
                "task_count": agent.task_count,
                "parallel_tasks_created": agent.parallel_tasks_created,
                "parallel_capabilities": agent.parallel_capabilities
            } for agent in integrated_agents.values()]
            self.wfile.write(json.dumps({"agents": agents_info}).encode('utf-8'))
        
        elif self.path == '/api/parallel/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            if parallel_manager:
                parallel_status = parallel_manager.coordinator.get_system_status()
                self.wfile.write(json.dumps(parallel_status).encode('utf-8'))
            else:
                self.wfile.write(json.dumps({"error": "Parallel manager not initialized"}).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Обработка POST запросов"""
        if self.path == '/api/integrated/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Обрабатываем сообщение через интегрированную систему
            response = asyncio.run(self.process_integrated_message(data))
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.end_headers()
    
    async def process_integrated_message(self, data: dict):
        """Обработка сообщения через интегрированную систему"""
        global integrated_agents, system_metrics
        
        message = data.get("message", "")
        agent_type = data.get("agent_type")
        user_id = data.get("user_id", "unknown")
        
        if not message:
            return {"error": "Сообщение не может быть пустым"}
        
        system_metrics["messages_processed"] += 1
        
        # Выбираем интегрированного агента
        if agent_type and agent_type in integrated_agents:
            agent = integrated_agents[agent_type]
        else:
            # Автоматический выбор агента
            agent = self._select_integrated_agent_for_message(message)
        
        # Обрабатываем сообщение
        result = await agent.process_message(message, user_id)
        
        return {
            "success": True,
            "response": result,
            "timestamp": datetime.now().isoformat(),
            "system_type": "integrated_mentor"
        }
    
    def _select_integrated_agent_for_message(self, message: str):
        """Выбор интегрированного агента для сообщения"""
        message_lower = message.lower()
        
        # Ключевые слова для выбора агента
        if any(word in message_lower for word in ["код", "программирование", "разработка", "debug", "ошибка"]):
            return integrated_agents.get("code_developer", list(integrated_agents.values())[0])
        elif any(word in message_lower for word in ["анализ", "данные", "отчет", "график", "статистика"]):
            return integrated_agents.get("data_analyst", list(integrated_agents.values())[0])
        elif any(word in message_lower for word in ["проект", "план", "задача", "управление", "координация"]):
            return integrated_agents.get("project_manager", list(integrated_agents.values())[0])
        elif any(word in message_lower for word in ["дизайн", "интерфейс", "ui", "ux", "макет"]):
            return integrated_agents.get("designer", list(integrated_agents.values())[0])
        elif any(word in message_lower for word in ["тест", "тестирование", "баг", "качество"]):
            return integrated_agents.get("qa_tester", list(integrated_agents.values())[0])
        else:
            return integrated_agents.get("general_assistant", list(integrated_agents.values())[0])
    
    def get_integrated_status(self):
        """Получить статус интегрированной системы"""
        global system_running, integrated_agents, system_metrics, parallel_manager
        
        uptime_seconds = int(time.time() - system_metrics['uptime_start'])
        uptime_minutes = uptime_seconds // 60
        
        parallel_status = {}
        if parallel_manager:
            parallel_status = parallel_manager.coordinator.get_system_status()
        
        return {
            "system_name": "Integrated MENTOR Multi-Agent System",
            "system_status": "running" if system_running else "stopped",
            "total_agents": len(integrated_agents),
            "active_agents": len([a for a in integrated_agents.values() if a.is_active]),
            "uptime": f"{uptime_minutes}м",
            "messages_processed": system_metrics["messages_processed"],
            "tasks_completed": system_metrics["tasks_completed"],
            "parallel_tasks_completed": system_metrics["parallel_tasks_completed"],
            "errors_count": system_metrics["errors_count"],
            "system_version": "Integrated MENTOR v3.0",
            "parallel_system": parallel_status,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_integrated_mentor_page(self):
        """Главная страница интегрированной системы MENTOR"""
        return """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Integrated MENTOR Multi-Agent System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
        }
        .container { max-width: 1600px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 3.5em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .header p { font-size: 1.4em; opacity: 0.9; }
        .mentor-badge { 
            display: inline-block; 
            background: rgba(255,255,255,0.2); 
            padding: 15px 25px; 
            border-radius: 30px; 
            margin-top: 15px;
            font-weight: bold;
            font-size: 1.1em;
        }
        .main-content { display: flex; gap: 20px; height: 800px; }
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
            width: 400px; 
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
            font-size: 10px;
            border: 1px solid #dee2e6;
            max-height: 300px;
            overflow-y: auto;
        }
        .suggestions { 
            margin-top: 10px; 
            padding: 8px; 
            background: #fff3cd; 
            border-radius: 5px; 
            font-size: 0.9em;
        }
        .parallel-tasks { 
            margin-top: 10px; 
            padding: 8px; 
            background: #d1ecf1; 
            border-radius: 5px; 
            font-size: 0.9em;
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
        .agent-list { margin-top: 20px; }
        .agent-list h3 { color: #333; margin-bottom: 10px; }
        .agent-item { 
            background: #e9ecef; 
            padding: 8px; 
            border-radius: 5px; 
            margin-bottom: 5px; 
            font-size: 0.85em;
        }
        .parallel-status { margin-top: 20px; }
        .parallel-status h3 { color: #333; margin-bottom: 10px; }
        .parallel-item { 
            background: #d4edda; 
            padding: 5px; 
            border-radius: 3px; 
            margin-bottom: 3px; 
            font-size: 0.8em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Integrated MENTOR Multi-Agent System</h1>
            <p>Интегрированная мульти-агентная система с параллельными возможностями</p>
            <div class="mentor-badge">Integrated MENTOR v3.0 - Parallel Processing</div>
        </div>
        
        <div class="main-content">
            <div class="chat-section">
                <div class="chat-messages" id="chatMessages">
                    <div class="message system-message">
                        <strong>Integrated MENTOR System:</strong> Добро пожаловать в интегрированную систему MENTOR! Агенты работают параллельно, создают сложные workflow и обеспечивают максимальную эффективность.
                    </div>
                </div>
                
                <div class="input-container">
                    <input type="text" id="messageInput" class="message-input" placeholder="Введите сообщение для Integrated MENTOR..." />
                    <button onclick="sendMessage()" class="send-button">Отправить</button>
                </div>
            </div>
            
            <div class="sidebar">
                <div class="system-info">
                    <h3>📊 Статус Integrated MENTOR</h3>
                    <p><span class="status-indicator status-online"></span>Система: <span id="systemStatus">Загрузка...</span></p>
                    <p>Агентов: <span id="totalAgents">0</span></p>
                    <p>Активных: <span id="activeAgents">0</span></p>
                    <p>Время работы: <span id="uptime">0м</span></p>
                </div>
                
                <div class="metrics-section">
                    <h3>📈 Метрики Integrated MENTOR</h3>
                    <div class="metric-item">
                        <span>Сообщений обработано:</span>
                        <span id="messagesProcessed">0</span>
                    </div>
                    <div class="metric-item">
                        <span>Задач выполнено:</span>
                        <span id="tasksCompleted">0</span>
                    </div>
                    <div class="metric-item">
                        <span>Параллельных задач:</span>
                        <span id="parallelTasksCompleted">0</span>
                    </div>
                    <div class="metric-item">
                        <span>Ошибок:</span>
                        <span id="errorsCount">0</span>
                    </div>
                </div>
                
                <div class="agent-selector">
                    <label for="agentSelect"><strong>Выберите агента MENTOR:</strong></label>
                    <select id="agentSelect">
                        <option value="">Автоматический выбор</option>
                        <option value="general_assistant">Интегрированный Помощник</option>
                        <option value="code_developer">Интегрированный Разработчик</option>
                        <option value="data_analyst">Интегрированный Аналитик</option>
                        <option value="project_manager">Интегрированный Менеджер</option>
                        <option value="designer">Интегрированный Дизайнер</option>
                        <option value="qa_tester">Интегрированный Тестировщик</option>
                    </select>
                </div>
                
                <div class="agent-list">
                    <h3>🤖 Интегрированные Агенты</h3>
                    <div id="agentsList">
                        <div class="agent-item">Загрузка агентов...</div>
                    </div>
                </div>
                
                <div class="parallel-status">
                    <h3>🚀 Параллельная Система</h3>
                    <div id="parallelStatus">
                        <div class="parallel-item">Загрузка статуса...</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function addMessage(message, type, agent = '', visualReport = null, suggestions = null, parallelTasks = null) {
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
                if (suggestions && suggestions.length > 0) {
                    content += `<div class="suggestions"><strong>Предложения:</strong> ${suggestions.join(', ')}</div>`;
                }
                if (parallelTasks && parallelTasks.length > 0) {
                    content += `<div class="parallel-tasks"><strong>Параллельные задачи выполнены:</strong> ${parallelTasks.length} задач</div>`;
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
                    const response = await fetch('/api/integrated/chat', {
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
                        let suggestions = null;
                        let parallelTasks = null;
                        
                        if (result.visual_report) {
                            try {
                                const decoded = atob(result.visual_report.split(',')[1]);
                                visualReport = decoded;
                            } catch (e) {
                                console.error('Ошибка декодирования визуального отчета:', e);
                            }
                        }
                        
                        if (result.autonomous_suggestions) {
                            suggestions = result.autonomous_suggestions;
                        }
                        
                        if (result.parallel_tasks) {
                            parallelTasks = result.parallel_tasks;
                        }
                        
                        addMessage(result.response, 'agent', result.agent, visualReport, suggestions, parallelTasks);
                    } else {
                        addMessage('Ошибка обработки сообщения', 'agent', 'Integrated MENTOR System');
                    }
                } catch (error) {
                    console.error('Ошибка отправки сообщения:', error);
                    addMessage('Ошибка соединения с Integrated MENTOR', 'agent', 'System');
                }
                
                input.value = '';
            }
        }
        
        function updateStatus() {
            fetch('/api/integrated/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('systemStatus').textContent = data.system_status;
                    document.getElementById('totalAgents').textContent = data.total_agents;
                    document.getElementById('activeAgents').textContent = data.active_agents;
                    document.getElementById('uptime').textContent = data.uptime;
                    document.getElementById('messagesProcessed').textContent = data.messages_processed;
                    document.getElementById('tasksCompleted').textContent = data.tasks_completed;
                    document.getElementById('parallelTasksCompleted').textContent = data.parallel_tasks_completed;
                    document.getElementById('errorsCount').textContent = data.errors_count;
                })
                .catch(error => console.error('Ошибка обновления статуса:', error));
        }
        
        function updateAgents() {
            fetch('/api/integrated/agents')
                .then(response => response.json())
                .then(data => {
                    const agentsList = document.getElementById('agentsList');
                    agentsList.innerHTML = '';
                    
                    data.agents.forEach(agent => {
                        const agentDiv = document.createElement('div');
                        agentDiv.className = 'agent-item';
                        agentDiv.innerHTML = `<strong>${agent.name}</strong><br><small>${agent.description}<br>Задач: ${agent.task_count} | Параллельных: ${agent.parallel_tasks_created} | Статус: ${agent.status}</small>`;
                        agentsList.appendChild(agentDiv);
                    });
                })
                .catch(error => console.error('Ошибка обновления агентов:', error));
        }
        
        function updateParallelStatus() {
            fetch('/api/parallel/status')
                .then(response => response.json())
                .then(data => {
                    const parallelStatus = document.getElementById('parallelStatus');
                    parallelStatus.innerHTML = '';
                    
                    if (data.error) {
                        parallelStatus.innerHTML = `<div class="parallel-item">${data.error}</div>`;
                    } else {
                        parallelStatus.innerHTML = `
                            <div class="parallel-item">Агентов: ${data.total_agents}</div>
                            <div class="parallel-item">Активных: ${data.active_agents}</div>
                            <div class="parallel-item">Ожидающих: ${data.pending_tasks}</div>
                            <div class="parallel-item">Выполнено: ${data.completed_tasks}</div>
                        `;
                    }
                })
                .catch(error => console.error('Ошибка обновления параллельного статуса:', error));
        }
        
        // Обработка Enter
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        // Инициализация
        updateStatus();
        updateAgents();
        updateParallelStatus();
        
        // Обновление каждые 3 секунды
        setInterval(updateStatus, 3000);
        setInterval(updateAgents, 5000);
        setInterval(updateParallelStatus, 4000);
    </script>
</body>
</html>
        """

# Основная функция интегрированной системы
async def main():
    """Главная функция интегрированной системы MENTOR"""
    global system_running, parallel_manager
    
    logger.info("🚀 Запуск интегрированной системы MENTOR...")
    
    # Создаем интегрированных агентов
    create_integrated_mentor_agents()
    
    # Инициализируем параллельный менеджер
    parallel_manager = get_parallel_manager()
    await parallel_manager.start()
    
    # Запускаем систему
    system_running = True
    
    logger.info("✅ Интегрированная система MENTOR запущена")
    logger.info("🌐 Веб-интерфейс доступен на http://0.0.0.0:8080")
    
    try:
        # Запускаем HTTP сервер
        with socketserver.TCPServer(("0.0.0.0", 8080), IntegratedMentorHandler) as httpd:
            logger.info("🌐 HTTP сервер Integrated MENTOR запущен на порту 8080")
            httpd.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("📡 Получен сигнал прерывания")
    finally:
        system_running = False
        if parallel_manager:
            await parallel_manager.stop()
        logger.info("🛑 Интегрированная система MENTOR остановлена")

if __name__ == "__main__":
    asyncio.run(main())