#!/usr/bin/env python3
"""
Простая система MENTOR - максимально упрощенная версия
"""

import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

class SimpleMentorHandler(BaseHTTPRequestHandler):
    """Простой обработчик для системы MENTOR"""
    
    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.get_main_page().encode('utf-8'))
        
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            status = {
                "system_name": "Simple MENTOR System",
                "status": "running",
                "agents": 6,
                "uptime": "0m",
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(status).encode('utf-8'))
        
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
                
                message = data.get("message", "")
                agent_type = data.get("agent_type", "general_assistant")
                
                # Простой ответ
                response = self.generate_response(message, agent_type)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                result = {
                    "success": True,
                    "response": {
                        "response": response,
                        "agent": f"MENTOR {agent_type}",
                        "timestamp": datetime.now().isoformat()
                    }
                }
                self.wfile.write(json.dumps(result).encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = {"error": str(e)}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def generate_response(self, message, agent_type):
        """Генерация простого ответа"""
        message_lower = message.lower()
        
        if "привет" in message_lower:
            return f"Привет! Я MENTOR {agent_type}. Готов помочь!"
        elif "код" in message_lower:
            return "Я могу помочь с разработкой кода. Создам архитектуру и напишу код."
        elif "анализ" in message_lower:
            return "Я проанализирую данные и создам отчеты с графиками."
        elif "проект" in message_lower:
            return "Я создам план проекта и буду управлять задачами."
        elif "дизайн" in message_lower:
            return "Я создам дизайн интерфейса и прототипы."
        elif "тест" in message_lower:
            return "Я проведу тестирование и найду баги."
        else:
            return f"Я MENTOR {agent_type}. Получил сообщение: '{message}'. Чем могу помочь?"
    
    def get_main_page(self):
        """Главная страница"""
        return """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple MENTOR System</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            margin: 0; 
            padding: 20px; 
            min-height: 100vh; 
        }
        .container { 
            max-width: 1000px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 15px; 
            padding: 30px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.1); 
        }
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
        }
        .header h1 { 
            color: #333; 
            font-size: 2.5em; 
            margin-bottom: 10px; 
        }
        .header p { 
            color: #666; 
            font-size: 1.2em; 
        }
        .chat-container { 
            display: flex; 
            gap: 20px; 
            height: 500px; 
        }
        .chat-messages { 
            flex: 2; 
            border: 1px solid #ddd; 
            border-radius: 10px; 
            padding: 20px; 
            overflow-y: auto; 
            background: #f9f9f9; 
        }
        .sidebar { 
            width: 300px; 
            border: 1px solid #ddd; 
            border-radius: 10px; 
            padding: 20px; 
            background: #f0f0f0; 
        }
        .message { 
            margin-bottom: 15px; 
            padding: 10px; 
            border-radius: 8px; 
        }
        .user-message { 
            background: #e3f2fd; 
            margin-left: 20px; 
        }
        .agent-message { 
            background: #f3e5f5; 
            margin-right: 20px; 
        }
        .system-message { 
            background: #e8f5e8; 
            text-align: center; 
            font-style: italic; 
        }
        .input-container { 
            display: flex; 
            gap: 10px; 
            margin-top: 20px; 
        }
        .message-input { 
            flex: 1; 
            padding: 15px; 
            border: 1px solid #ddd; 
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
        }
        .send-button:hover { 
            background: #45a049; 
        }
        .agent-selector { 
            margin-bottom: 20px; 
        }
        .agent-selector select { 
            width: 100%; 
            padding: 10px; 
            border: 1px solid #ddd; 
            border-radius: 5px; 
        }
        .status { 
            background: #d4edda; 
            padding: 10px; 
            border-radius: 5px; 
            margin-bottom: 20px; 
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Simple MENTOR System</h1>
            <p>Простая мульти-агентная система</p>
        </div>
        
        <div class="chat-container">
            <div class="chat-messages" id="chatMessages">
                <div class="message system-message">
                    <strong>Simple MENTOR System:</strong> Система запущена и готова к работе!
                </div>
            </div>
            
            <div class="sidebar">
                <div class="status">
                    <h3>📊 Статус</h3>
                    <p>Система: <span id="systemStatus">Загрузка...</span></p>
                    <p>Агентов: <span id="totalAgents">6</span></p>
                </div>
                
                <div class="agent-selector">
                    <label><strong>Выберите агента:</strong></label>
                    <select id="agentSelect">
                        <option value="general_assistant">Помощник</option>
                        <option value="code_developer">Разработчик</option>
                        <option value="data_analyst">Аналитик</option>
                        <option value="project_manager">Менеджер</option>
                        <option value="designer">Дизайнер</option>
                        <option value="qa_tester">Тестировщик</option>
                    </select>
                </div>
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="messageInput" class="message-input" placeholder="Введите сообщение..." />
            <button onclick="sendMessage()" class="send-button">Отправить</button>
        </div>
    </div>

    <script>
        function addMessage(message, type, agent = '') {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}-message`;
            
            if (type === 'user') {
                messageDiv.innerHTML = `<strong>Вы:</strong> ${message}`;
            } else {
                messageDiv.innerHTML = `<strong>${agent}:</strong> ${message}`;
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
                            agent_type: agentType
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        const result = data.response;
                        addMessage(result.response, 'agent', result.agent);
                    } else {
                        addMessage('Ошибка обработки сообщения', 'agent', 'MENTOR System');
                    }
                } catch (error) {
                    console.error('Ошибка:', error);
                    addMessage('Ошибка соединения', 'agent', 'System');
                }
                
                input.value = '';
            }
        }
        
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('systemStatus').textContent = data.status;
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
        setInterval(updateStatus, 5000);
    </script>
</body>
</html>
        """

def main():
    """Главная функция"""
    print("🚀 Запуск Simple MENTOR System...")
    
    server = HTTPServer(('0.0.0.0', 8080), SimpleMentorHandler)
    print("✅ Simple MENTOR System запущена")
    print("🌐 Веб-интерфейс доступен на http://0.0.0.0:8080")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("🛑 Simple MENTOR System остановлена")
        server.shutdown()

if __name__ == "__main__":
    main()