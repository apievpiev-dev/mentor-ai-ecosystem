#!/usr/bin/env python3
"""
Веб-интерфейс для системы бесплатных локальных нейросетей
Работает только с бесплатными моделями: Ollama, Hugging Face, локальные трансформеры
"""

import asyncio
import json
import logging
from typing import Dict, List, Any
from datetime import datetime
import aiohttp
from aiohttp import web, WSMsgType
import aiohttp_cors
from pathlib import Path

from free_ai_engine import free_ai_engine, generate_ai_response
from auto_install_free_models import model_installer

logger = logging.getLogger(__name__)

class FreeNeuralNetworkWebInterface:
    """Веб-интерфейс для бесплатных локальных нейросетей"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8081):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.setup_routes()
        self.setup_cors()
        self.connected_clients = set()
        self.created_networks = {}
    
    def setup_cors(self):
        """Настройка CORS"""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    def setup_routes(self):
        """Настройка маршрутов"""
        # Статические файлы
        self.app.router.add_static('/static', '/workspace/free_models')
        
        # API маршруты
        self.app.router.add_get('/', self.index_handler)
        self.app.router.add_get('/api/models', self.get_models_handler)
        self.app.router.add_get('/api/status', self.get_status_handler)
        self.app.router.add_post('/api/install-models', self.install_models_handler)
        self.app.router.add_post('/api/create-network', self.create_network_handler)
        self.app.router.add_post('/api/generate-response', self.generate_response_handler)
        self.app.router.add_get('/api/networks', self.get_networks_handler)
        self.app.router.add_websocket('/ws', self.websocket_handler)
    
    async def index_handler(self, request):
        """Главная страница"""
        html_content = """
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Бесплатные Локальные Нейросети</title>
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
                
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                
                .header {
                    text-align: center;
                    color: white;
                    margin-bottom: 30px;
                }
                
                .header h1 {
                    font-size: 2.5em;
                    margin-bottom: 10px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }
                
                .header p {
                    font-size: 1.2em;
                    opacity: 0.9;
                }
                
                .dashboard {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    margin-bottom: 30px;
                }
                
                .card {
                    background: white;
                    border-radius: 15px;
                    padding: 25px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    transition: transform 0.3s ease;
                }
                
                .card:hover {
                    transform: translateY(-5px);
                }
                
                .card h3 {
                    color: #667eea;
                    margin-bottom: 15px;
                    font-size: 1.3em;
                }
                
                .form-group {
                    margin-bottom: 15px;
                }
                
                .form-group label {
                    display: block;
                    margin-bottom: 5px;
                    font-weight: 600;
                    color: #555;
                }
                
                .form-group input, .form-group select, .form-group textarea {
                    width: 100%;
                    padding: 12px;
                    border: 2px solid #e1e5e9;
                    border-radius: 8px;
                    font-size: 14px;
                    transition: border-color 0.3s ease;
                }
                
                .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
                    outline: none;
                    border-color: #667eea;
                }
                
                .btn {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    padding: 12px 25px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 600;
                    transition: transform 0.2s ease;
                    margin-right: 10px;
                    margin-bottom: 10px;
                }
                
                .btn:hover {
                    transform: scale(1.05);
                }
                
                .btn:disabled {
                    opacity: 0.6;
                    cursor: not-allowed;
                    transform: none;
                }
                
                .btn-success {
                    background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
                }
                
                .btn-warning {
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                }
                
                .btn-info {
                    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                }
                
                .models-list {
                    background: white;
                    border-radius: 15px;
                    padding: 25px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                }
                
                .model-item {
                    border: 1px solid #e1e5e9;
                    border-radius: 10px;
                    padding: 15px;
                    margin-bottom: 15px;
                    transition: all 0.3s ease;
                }
                
                .model-item:hover {
                    border-color: #667eea;
                    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.1);
                }
                
                .model-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 10px;
                }
                
                .model-name {
                    font-weight: 600;
                    color: #333;
                    font-size: 1.1em;
                }
                
                .model-provider {
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                }
                
                .provider-ollama {
                    background: #e3f2fd;
                    color: #1976d2;
                }
                
                .provider-huggingface {
                    background: #e8f5e8;
                    color: #388e3c;
                }
                
                .provider-local {
                    background: #fff3e0;
                    color: #f57c00;
                }
                
                .model-details {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 10px;
                    font-size: 14px;
                    color: #666;
                }
                
                .networks-list {
                    background: white;
                    border-radius: 15px;
                    padding: 25px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                }
                
                .network-item {
                    border: 1px solid #e1e5e9;
                    border-radius: 10px;
                    padding: 15px;
                    margin-bottom: 15px;
                    transition: all 0.3s ease;
                }
                
                .network-item:hover {
                    border-color: #667eea;
                    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.1);
                }
                
                .loading {
                    display: none;
                    text-align: center;
                    padding: 20px;
                }
                
                .spinner {
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid #667eea;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 10px;
                }
                
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                
                .alert {
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    display: none;
                }
                
                .alert-success {
                    background: #d4edda;
                    color: #155724;
                    border: 1px solid #c3e6cb;
                }
                
                .alert-error {
                    background: #f8d7da;
                    color: #721c24;
                    border: 1px solid #f5c6cb;
                }
                
                .status-indicator {
                    display: inline-block;
                    width: 10px;
                    height: 10px;
                    border-radius: 50%;
                    margin-right: 8px;
                }
                
                .status-online {
                    background: #28a745;
                }
                
                .status-offline {
                    background: #dc3545;
                }
                
                .status-unknown {
                    background: #ffc107;
                }
                
                @media (max-width: 768px) {
                    .dashboard {
                        grid-template-columns: 1fr;
                    }
                    
                    .container {
                        padding: 10px;
                    }
                    
                    .header h1 {
                        font-size: 2em;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧠 Бесплатные Локальные Нейросети</h1>
                    <p>Создавайте нейросети с помощью бесплатных локальных AI моделей</p>
                </div>
                
                <div class="alert alert-success" id="successAlert"></div>
                <div class="alert alert-error" id="errorAlert"></div>
                
                <div class="dashboard">
                    <div class="card">
                        <h3>🚀 Установить бесплатные модели</h3>
                        <p>Автоматически установить все бесплатные AI модели на сервер</p>
                        <button class="btn btn-success" onclick="installModels()">Установить модели</button>
                        <button class="btn btn-info" onclick="checkStatus()">Проверить статус</button>
                    </div>
                    
                    <div class="card">
                        <h3>🤖 Создать нейросеть с ИИ</h3>
                        <form id="createNetworkForm">
                            <div class="form-group">
                                <label for="taskDescription">Описание задачи:</label>
                                <textarea id="taskDescription" name="task" rows="3" placeholder="Создай нейросеть для классификации изображений..." required></textarea>
                            </div>
                            <div class="form-group">
                                <label for="modelProvider">Провайдер AI:</label>
                                <select id="modelProvider" name="provider">
                                    <option value="auto">Автоматический выбор</option>
                                    <option value="ollama">Ollama</option>
                                    <option value="huggingface">Hugging Face</option>
                                    <option value="local_transformers">Локальные модели</option>
                                </select>
                            </div>
                            <button type="submit" class="btn btn-success">Создать нейросеть</button>
                        </form>
                    </div>
                </div>
                
                <div class="models-list">
                    <h3>📋 Доступные AI модели</h3>
                    <div class="loading" id="modelsLoading">
                        <div class="spinner"></div>
                        <p>Загрузка моделей...</p>
                    </div>
                    <div id="modelsList"></div>
                </div>
                
                <div class="networks-list">
                    <h3>🧠 Созданные нейросети</h3>
                    <div class="loading" id="networksLoading">
                        <div class="spinner"></div>
                        <p>Загрузка нейросетей...</p>
                    </div>
                    <div id="networksList"></div>
                </div>
            </div>
            
            <script>
                let availableModels = [];
                let createdNetworks = [];
                
                // Инициализация
                document.addEventListener('DOMContentLoaded', function() {
                    loadModels();
                    loadNetworks();
                    setupEventListeners();
                });
                
                function setupEventListeners() {
                    document.getElementById('createNetworkForm').addEventListener('submit', handleCreateNetwork);
                }
                
                async function installModels() {
                    showLoading('modelsLoading', true);
                    try {
                        const response = await fetch('/api/install-models', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            }
                        });
                        
                        const result = await response.json();
                        
                        if (result.error) {
                            showError(result.error);
                        } else {
                            showSuccess('Модели установлены успешно!');
                            loadModels();
                        }
                    } catch (error) {
                        showError('Ошибка установки моделей: ' + error.message);
                    } finally {
                        showLoading('modelsLoading', false);
                    }
                }
                
                async function checkStatus() {
                    try {
                        const response = await fetch('/api/status');
                        const result = await response.json();
                        
                        if (result.error) {
                            showError(result.error);
                        } else {
                            showSuccess('Статус системы: ' + JSON.stringify(result, null, 2));
                        }
                    } catch (error) {
                        showError('Ошибка проверки статуса: ' + error.message);
                    }
                }
                
                async function handleCreateNetwork(e) {
                    e.preventDefault();
                    const formData = new FormData(e.target);
                    const data = Object.fromEntries(formData);
                    
                    showLoading('networksLoading', true);
                    try {
                        const response = await fetch('/api/create-network', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify(data)
                        });
                        
                        const result = await response.json();
                        
                        if (result.error) {
                            showError(result.error);
                        } else {
                            showSuccess('Нейросеть создана успешно!');
                            loadNetworks();
                        }
                    } catch (error) {
                        showError('Ошибка создания нейросети: ' + error.message);
                    } finally {
                        showLoading('networksLoading', false);
                    }
                }
                
                async function loadModels() {
                    showLoading('modelsLoading', true);
                    try {
                        const response = await fetch('/api/models');
                        const result = await response.json();
                        
                        if (result.error) {
                            showError(result.error);
                        } else {
                            availableModels = result.models;
                            displayModels(result.models);
                        }
                    } catch (error) {
                        showError('Ошибка загрузки моделей: ' + error.message);
                    } finally {
                        showLoading('modelsLoading', false);
                    }
                }
                
                function displayModels(models) {
                    const container = document.getElementById('modelsList');
                    
                    if (Object.keys(models).length === 0) {
                        container.innerHTML = '<p style="text-align: center; color: #666; padding: 20px;">Нет доступных моделей</p>';
                        return;
                    }
                    
                    let html = '';
                    for (const [provider, modelList] of Object.entries(models)) {
                        html += `<h4 style="margin: 20px 0 10px 0; color: #667eea;">${getProviderName(provider)}</h4>`;
                        
                        if (modelList.length === 0) {
                            html += '<p style="color: #666; margin-left: 20px;">Нет моделей</p>';
                        } else {
                            for (const model of modelList) {
                                html += `
                                    <div class="model-item">
                                        <div class="model-header">
                                            <div class="model-name">${model}</div>
                                            <div class="model-provider provider-${provider}">${getProviderName(provider)}</div>
                                        </div>
                                        <div class="model-details">
                                            <div><strong>Провайдер:</strong> ${getProviderName(provider)}</div>
                                            <div><strong>Статус:</strong> <span class="status-indicator status-online"></span>Доступна</div>
                                        </div>
                                    </div>
                                `;
                            }
                        }
                    }
                    
                    container.innerHTML = html;
                }
                
                async function loadNetworks() {
                    showLoading('networksLoading', true);
                    try {
                        const response = await fetch('/api/networks');
                        const result = await response.json();
                        
                        if (result.error) {
                            showError(result.error);
                        } else {
                            createdNetworks = result.networks;
                            displayNetworks(result.networks);
                        }
                    } catch (error) {
                        showError('Ошибка загрузки нейросетей: ' + error.message);
                    } finally {
                        showLoading('networksLoading', false);
                    }
                }
                
                function displayNetworks(networks) {
                    const container = document.getElementById('networksList');
                    
                    if (networks.length === 0) {
                        container.innerHTML = '<p style="text-align: center; color: #666; padding: 20px;">Нет созданных нейросетей</p>';
                        return;
                    }
                    
                    container.innerHTML = networks.map(network => `
                        <div class="network-item">
                            <div class="model-header">
                                <div class="model-name">${network.name}</div>
                                <div class="model-provider provider-${network.provider}">${getProviderName(network.provider)}</div>
                            </div>
                            <div class="model-details">
                                <div><strong>Задача:</strong> ${network.task}</div>
                                <div><strong>Создана:</strong> ${new Date(network.created_at).toLocaleString()}</div>
                                <div><strong>Статус:</strong> <span class="status-indicator status-online"></span>${network.status}</div>
                            </div>
                        </div>
                    `).join('');
                }
                
                function getProviderName(provider) {
                    const names = {
                        'ollama': 'Ollama',
                        'huggingface': 'Hugging Face',
                        'local_transformers': 'Локальные'
                    };
                    return names[provider] || provider;
                }
                
                function showLoading(elementId, show) {
                    document.getElementById(elementId).style.display = show ? 'block' : 'none';
                }
                
                function showSuccess(message) {
                    const alert = document.getElementById('successAlert');
                    alert.textContent = message;
                    alert.style.display = 'block';
                    setTimeout(() => alert.style.display = 'none', 5000);
                }
                
                function showError(message) {
                    const alert = document.getElementById('errorAlert');
                    alert.textContent = message;
                    alert.style.display = 'block';
                    setTimeout(() => alert.style.display = 'none', 5000);
                }
            </script>
        </body>
        </html>
        """
        return web.Response(text=html_content, content_type='text/html')
    
    async def get_models_handler(self, request):
        """Получение списка доступных моделей"""
        try:
            models = free_ai_engine.get_available_models()
            return web.json_response({"models": models})
        except Exception as e:
            logger.error(f"❌ Ошибка получения моделей: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def get_status_handler(self, request):
        """Получение статуса системы"""
        try:
            status = free_ai_engine.get_status()
            return web.json_response(status)
        except Exception as e:
            logger.error(f"❌ Ошибка получения статуса: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def install_models_handler(self, request):
        """Установка бесплатных моделей"""
        try:
            results = await model_installer.install_all_models()
            return web.json_response(results)
        except Exception as e:
            logger.error(f"❌ Ошибка установки моделей: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def create_network_handler(self, request):
        """Создание нейросети"""
        try:
            data = await request.json()
            task = data.get("task", "")
            provider = data.get("provider", "auto")
            
            if not task:
                return web.json_response({"error": "Не указано описание задачи"}, status=400)
            
            # Генерируем нейросеть с помощью AI
            ai_prompt = f"""
            Создай архитектуру нейросети для задачи: {task}
            
            Верни JSON с полями:
            - name: название сети
            - type: тип задачи (classification/regression/generation)
            - input_size: размер входа
            - output_size: размер выхода
            - hidden_layers: список размеров скрытых слоев
            - description: описание архитектуры
            """
            
            response = await free_ai_engine.generate_response(
                ai_prompt, 
                provider=provider if provider != "auto" else None
            )
            
            if not response.success:
                return web.json_response({"error": f"Ошибка AI: {response.error}"}, status=500)
            
            try:
                network_config = json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback конфигурация
                network_config = {
                    "name": f"network_{int(time.time())}",
                    "type": "classification",
                    "input_size": 784,
                    "output_size": 10,
                    "hidden_layers": [128, 64],
                    "description": f"Нейросеть для задачи: {task}"
                }
            
            # Сохраняем нейросеть
            network_id = str(int(time.time()))
            network = {
                "id": network_id,
                "name": network_config["name"],
                "task": task,
                "provider": response.provider,
                "config": network_config,
                "status": "created",
                "created_at": datetime.now().isoformat()
            }
            
            self.created_networks[network_id] = network
            
            return web.json_response({
                "message": "Нейросеть создана успешно",
                "network": network,
                "ai_response": response.content
            })
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания нейросети: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def generate_response_handler(self, request):
        """Генерация ответа от AI"""
        try:
            data = await request.json()
            prompt = data.get("prompt", "")
            provider = data.get("provider", "auto")
            
            if not prompt:
                return web.json_response({"error": "Не указан промпт"}, status=400)
            
            response = await free_ai_engine.generate_response(
                prompt,
                provider=provider if provider != "auto" else None
            )
            
            return web.json_response({
                "response": response.content,
                "model": response.model,
                "provider": response.provider,
                "response_time": response.response_time,
                "success": response.success
            })
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации ответа: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def get_networks_handler(self, request):
        """Получение списка созданных нейросетей"""
        try:
            networks = list(self.created_networks.values())
            return web.json_response({"networks": networks})
        except Exception as e:
            logger.error(f"❌ Ошибка получения нейросетей: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def websocket_handler(self, request):
        """WebSocket для real-time обновлений"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.connected_clients.add(ws)
        logger.info(f"🔌 WebSocket подключен. Всего клиентов: {len(self.connected_clients)}")
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    await self.handle_websocket_message(ws, data)
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f'WebSocket ошибка: {ws.exception()}')
        finally:
            self.connected_clients.discard(ws)
            logger.info(f"🔌 WebSocket отключен. Осталось клиентов: {len(self.connected_clients)}")
        
        return ws
    
    async def handle_websocket_message(self, ws, data):
        """Обработка WebSocket сообщений"""
        try:
            message_type = data.get('type')
            
            if message_type == 'ping':
                await ws.send_str(json.dumps({'type': 'pong'}))
            elif message_type == 'subscribe':
                await ws.send_str(json.dumps({
                    'type': 'subscribed',
                    'message': 'Подписка на обновления активна'
                }))
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки WebSocket сообщения: {e}")
            await ws.send_str(json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def start_server(self):
        """Запуск веб-сервера"""
        try:
            runner = web.AppRunner(self.app)
            await runner.setup()
            site = web.TCPSite(runner, self.host, self.port)
            await site.start()
            
            logger.info(f"🌐 Веб-интерфейс бесплатных нейросетей запущен на http://{self.host}:{self.port}")
            logger.info(f"📊 Доступные функции:")
            logger.info(f"   - Установка бесплатных AI моделей")
            logger.info(f"   - Создание нейросетей с помощью ИИ")
            logger.info(f"   - Работа с Ollama, Hugging Face, локальными моделями")
            logger.info(f"   - Real-time обновления")
            
            return runner
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска веб-сервера: {e}")
            raise

# Глобальный экземпляр веб-интерфейса
free_web_interface = FreeNeuralNetworkWebInterface()

async def main():
    """Главная функция"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        runner = await free_web_interface.start_server()
        
        # Запускаем в бесконечном цикле
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Остановка веб-интерфейса...")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())