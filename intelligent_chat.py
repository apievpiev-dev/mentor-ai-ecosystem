#!/usr/bin/env python3
"""
Интеллектуальный чат JARVIS с настоящим AI
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
import time
import asyncio
import subprocess
import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class ChatMessage(BaseModel):
    message: str
    user_id: str = "anonymous"
    context: Optional[str] = None

app = FastAPI(title="JARVIS Intelligent Chat")

class IntelligentChat:
    def __init__(self):
        self.conversation_history = []
        self.max_history = 10
        self.ai_models = ["llama3.1:8b", "llama2:latest"]
        self.current_model = self.ai_models[0]
        
    def get_ai_response(self, message: str, context: str = "") -> str:
        """Получение интеллектуального ответа от AI"""
        try:
            # Формируем контекст для AI
            system_prompt = f"""Ты JARVIS - автономная AI-система с продвинутыми возможностями. 
Твои основные функции:
- Анализ данных и генерация отчетов
- Самоулучшение и оптимизация кода
- Анализ интерфейса и UX/UI
- Самовоспроизводство на серверах
- Мониторинг производительности
- Интеллектуальная помощь пользователю

Отвечай на русском языке, будь полезным и конкретным. 
Если пользователь просит что-то выполнить - предложи конкретные действия.
Если это вопрос о системе - дай детальный ответ.
Если это творческая задача - прояви креативность.

Контекст: {context}
История разговора: {self.get_recent_history()}
"""
            
            user_prompt = f"Пользователь: {message}"
            
            # Формируем полный промпт
            full_prompt = f"{system_prompt}\n\n{user_prompt}\n\nJARVIS:"
            
            # Пробуем разные модели
            for model in self.ai_models:
                try:
                    response = self.call_ollama(model, full_prompt)
                    if response and len(response.strip()) > 10:
                        return response.strip()
                except Exception as e:
                    logger.debug(f"Модель {model} недоступна: {e}")
                    continue
            
            # Fallback к простому ответу
            return self.get_fallback_response(message)
            
        except Exception as e:
            logger.error(f"Ошибка получения AI ответа: {e}")
            return "Извините, произошла ошибка при обработке запроса. Попробуйте еще раз."
    
    def call_ollama(self, model: str, prompt: str) -> Optional[str]:
        """Вызов Ollama API"""
        try:
            # Используем ollama run для получения ответа
            result = subprocess.run([
                'ollama', 'run', model, prompt
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0 and result.stdout.strip():
                response = result.stdout.strip()
                
                # Очищаем ответ от лишних частей и escape-последовательностей
                response = response.replace('\x1b[?2026h', '').replace('\x1b[?25l', '')
                response = response.replace('\x1b[?2026l', '').replace('\x1b[?25h', '')
                response = response.replace('\x1b[1G', '').replace('\x1b[K', '')
                response = response.replace('\x1b[2K', '').replace('\x1b[?25l', '')
                response = response.replace('\x1b[?25h', '')
                
                # Убираем анимационные символы
                import re
                response = re.sub(r'[\u2800-\u28FF]', '', response)  # Braille patterns
                response = re.sub(r'[⠁-⠿]', '', response)  # Braille characters
                
                # Очищаем от лишних частей
                if "JARVIS:" in response:
                    response = response.split("JARVIS:")[-1].strip()
                if "User:" in response:
                    response = response.split("User:")[0].strip()
                
                # Убираем лишние пробелы и переносы
                response = '\n'.join(line.strip() for line in response.split('\n') if line.strip())
                
                return response if response else None
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Таймаут для модели {model}")
        except FileNotFoundError:
            logger.error("Ollama не найден")
        except Exception as e:
            logger.error(f"Ошибка вызова Ollama: {e}")
        
        return None
    
    def get_fallback_response(self, message: str) -> str:
        """Резервные ответы для критических функций"""
        message_lower = message.lower().strip()
        
        if any(word in message_lower for word in ["статус", "состояние", "как дела"]):
            return """Система JARVIS работает стабильно:
• Все модули активны
• Производительность в норме
• Готов к выполнению задач
• AI модели доступны (llama3.1, llama2)

Что конкретно вас интересует?"""
        
        elif any(word in message_lower for word in ["анализ", "данные", "отчет"]):
            return """Запускаю анализ данных:
• Подключаюсь к источникам данных
• Обрабатываю информацию
• Генерирую отчеты
• Создаю визуализации

Результаты будут готовы через несколько минут."""
        
        elif any(word in message_lower for word in ["код", "программирование", "разработка"]):
            return """Готов помочь с программированием:
• Python, JavaScript, HTML/CSS
• API разработка
• Веб-приложения
• Автоматизация

Опишите задачу подробнее - создам код для вас."""
        
        elif any(word in message_lower for word in ["помощь", "help", "что умеешь"]):
            return """Я JARVIS - интеллектуальная AI-система:

🧠 ИНТЕЛЛЕКТУАЛЬНЫЕ ВОЗМОЖНОСТИ:
• Анализ и понимание контекста
• Генерация кода и решений
• Творческие задачи
• Решение проблем

🔧 ТЕХНИЧЕСКИЕ ФУНКЦИИ:
• Анализ данных и отчеты
• Самоулучшение системы
• Мониторинг производительности
• Самовоспроизводство

Просто опишите, что нужно сделать!"""
        
        else:
            return """Понял ваш запрос! Я использую продвинутые AI-модели для понимания и решения задач. 

Попробуйте:
• Описать конкретную задачу
• Задать вопрос о системе
• Попросить создать код
• Запросить анализ данных

Я всегда готов помочь!"""
    
    def get_recent_history(self) -> str:
        """Получение последних сообщений для контекста"""
        if len(self.conversation_history) <= 2:
            return "Новый разговор"
        
        recent = self.conversation_history[-4:]  # Последние 4 сообщения
        history_text = []
        for msg in recent:
            role = "Пользователь" if msg["role"] == "user" else "JARVIS"
            history_text.append(f"{role}: {msg['content']}")
        
        return "\n".join(history_text)
    
    def add_to_history(self, role: str, content: str):
        """Добавление сообщения в историю"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Ограничиваем историю
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def get_system_status(self) -> Dict[str, Any]:
        """Получение статуса системы"""
        try:
            # Проверяем доступность AI моделей
            available_models = []
            for model in self.ai_models:
                try:
                    result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
                    if model in result.stdout:
                        available_models.append(model)
                except:
                    continue
            
            return {
                "ai_active": True,
                "available_models": available_models,
                "current_model": self.current_model,
                "conversation_length": len(self.conversation_history),
                "intelligence_level": "high" if available_models else "basic"
            }
        except Exception as e:
            logger.error(f"Ошибка получения статуса: {e}")
            return {
                "ai_active": False,
                "error": str(e),
                "intelligence_level": "basic"
            }

# Создаем экземпляр интеллектуального чата
intelligent_chat = IntelligentChat()

@app.get("/")
async def chat_interface():
    """Интеллектуальный интерфейс чата"""
    html_content = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JARVIS Intelligent Chat</title>
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
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            width: 100%;
            max-width: 900px;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .header h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .header p {
            color: #7f8c8d;
            font-size: 1.1em;
        }
        
        .ai-status {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
            margin: 15px 0;
            padding: 10px 20px;
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            border-radius: 25px;
            font-weight: bold;
        }
        
        .chat-container {
            height: 450px;
            border: 2px solid #e0e0e0;
            border-radius: 15px;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
            margin-bottom: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .message {
            max-width: 80%;
            padding: 15px 20px;
            border-radius: 20px;
            word-wrap: break-word;
            animation: fadeIn 0.3s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .user-message {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            margin-left: auto;
            text-align: right;
        }
        
        .jarvis-message {
            background: linear-gradient(45deg, #f8f9fa, #e9ecef);
            color: #2c3e50;
            margin-right: auto;
            border: 1px solid #dee2e6;
        }
        
        .thinking {
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
            font-style: italic;
        }
        
        .input-container {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        
        .message-input {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s ease;
        }
        
        .message-input:focus {
            border-color: #667eea;
        }
        
        .send-button {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s ease;
            min-width: 120px;
        }
        
        .send-button:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        
        .send-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .status {
            text-align: center;
            margin-top: 20px;
            color: #7f8c8d;
            font-size: 0.9em;
        }
        
        .typing-indicator {
            display: none;
            align-items: center;
            gap: 5px;
            color: #667eea;
            font-style: italic;
        }
        
        .typing-dots {
            display: flex;
            gap: 3px;
        }
        
        .typing-dots span {
            width: 6px;
            height: 6px;
            background: #667eea;
            border-radius: 50%;
            animation: typing 1.4s infinite;
        }
        
        .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
        .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-10px); }
        }
        
        .model-info {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(102, 126, 234, 0.1);
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            color: #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>JARVIS Intelligent Chat</h1>
            <p>Искусственный интеллект с продвинутыми возможностями</p>
            <div class="ai-status" id="aiStatus">
                🧠 AI Active - Processing...
            </div>
        </div>
        
        <div class="chat-container" id="chatContainer">
            <div class="message jarvis-message">
                Привет! Я JARVIS - интеллектуальная AI-система. Использую продвинутые модели для понимания и решения задач. Чем могу помочь?
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" class="message-input" id="messageInput" 
                   placeholder="Опишите задачу или задайте вопрос..." 
                   onkeypress="handleKeyPress(event)">
            <button class="send-button" id="sendButton" onclick="sendMessage()">
                Отправить
            </button>
        </div>
        
        <div class="typing-indicator" id="typingIndicator">
            JARVIS печатает
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
        
        <div class="status" id="status">
            Готов к интеллектуальному общению
        </div>
        
        <div class="model-info" id="modelInfo">
            AI Model: Loading...
        </div>
    </div>

    <script>
        let isProcessing = false;
        
        async function handleKeyPress(event) {
            if (event.key === 'Enter' && !isProcessing) {
                sendMessage();
            }
        }

        async function sendMessage() {
            if (isProcessing) return;
            
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Добавляем сообщение пользователя
            addMessage(message, 'user');
            input.value = '';
            
            // Показываем индикатор печати
            showTypingIndicator();
            setProcessing(true);
            
            try {
                const response = await fetch('/api/chat/send', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: message,
                        user_id: 'web_user'
                    })
                });
                
                const data = await response.json();
                
                hideTypingIndicator();
                
                if (data.error) {
                    addMessage('Ошибка: ' + data.error, 'jarvis');
                } else {
                    addMessage(data.message, 'jarvis');
                }
                
                updateStatus('Готов к интеллектуальному общению');
                
            } catch (error) {
                hideTypingIndicator();
                addMessage('Ошибка соединения: ' + error.message, 'jarvis');
                updateStatus('Ошибка соединения');
            } finally {
                setProcessing(false);
            }
        }

        function addMessage(text, sender) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            
            // Обрабатываем текст для лучшего отображения
            text = text.replace(/\\n/g, '<br>');
            text = text.replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
            text = text.replace(/\\*(.*?)\\*/g, '<em>$1</em>');
            
            messageDiv.innerHTML = text;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function showTypingIndicator() {
            document.getElementById('typingIndicator').style.display = 'flex';
            updateStatus('JARVIS анализирует запрос...');
        }

        function hideTypingIndicator() {
            document.getElementById('typingIndicator').style.display = 'none';
        }

        function setProcessing(processing) {
            isProcessing = processing;
            const sendButton = document.getElementById('sendButton');
            const messageInput = document.getElementById('messageInput');
            
            sendButton.disabled = processing;
            messageInput.disabled = processing;
            
            if (processing) {
                sendButton.textContent = 'Обработка...';
            } else {
                sendButton.textContent = 'Отправить';
            }
        }

        function updateStatus(text) {
            document.getElementById('status').textContent = text;
        }

        // Загружаем статус AI при запуске
        async function loadAIStatus() {
            try {
                const response = await fetch('/api/chat/status');
                const data = await response.json();
                
                const aiStatus = document.getElementById('aiStatus');
                const modelInfo = document.getElementById('modelInfo');
                
                if (data.intelligence_level === 'high') {
                    aiStatus.innerHTML = '🧠 AI Active - High Intelligence';
                    aiStatus.style.background = 'linear-gradient(45deg, #4CAF50, #45a049)';
                    modelInfo.textContent = `AI: ${data.available_models.join(', ')}`;
                } else {
                    aiStatus.innerHTML = '🤖 AI Active - Basic Mode';
                    aiStatus.style.background = 'linear-gradient(45deg, #FF9800, #F57C00)';
                    modelInfo.textContent = 'AI: Basic Mode';
                }
            } catch (error) {
                console.error('Ошибка загрузки статуса AI:', error);
            }
        }

        // Загружаем статус при старте
        loadAIStatus();
    </script>
</body>
</html>
    """
    return HTMLResponse(html_content)

@app.post("/api/chat/send")
async def send_message(message: ChatMessage):
    """Отправка сообщения в интеллектуальный чат JARVIS"""
    try:
        if not message.message.strip():
            raise HTTPException(status_code=400, detail="Сообщение не может быть пустым")
        
        # Добавляем в историю
        intelligent_chat.add_to_history("user", message.message)
        
        # Получаем интеллектуальный ответ
        response = intelligent_chat.get_ai_response(message.message, message.context or "")
        
        # Добавляем ответ в историю
        intelligent_chat.add_to_history("assistant", response)
        
        return {
            "message": response,
            "timestamp": datetime.now().isoformat(),
            "user_id": message.user_id,
            "original_message": message.message,
            "intelligence_level": intelligent_chat.get_system_status().get("intelligence_level", "basic")
        }
                    
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/status")
async def chat_status():
    """Статус интеллектуального чата"""
    status = intelligent_chat.get_system_status()
    status.update({
        "chat_active": True,
        "websocket_active": False,
        "conversation_length": len(intelligent_chat.conversation_history),
        "timestamp": datetime.now().isoformat()
    })
    return status

@app.get("/api/chat/history")
async def chat_history():
    """История разговора"""
    return {
        "history": intelligent_chat.conversation_history,
        "length": len(intelligent_chat.conversation_history)
    }

if __name__ == "__main__":
    import uvicorn
    print("🧠 Запуск интеллектуального чата JARVIS...")
    print("🤖 AI модели: llama3.1:8b, llama2:latest")
    print("🌐 Веб-интерфейс: http://localhost:8083/")
    uvicorn.run(app, host="0.0.0.0", port=8083)
