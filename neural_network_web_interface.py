#!/usr/bin/env python3
"""
Веб-интерфейс для Neural Network Creator
Позволяет создавать, обучать и визуализировать нейросети через веб-интерфейс
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

from neural_network_creator_agent import neural_network_creator

logger = logging.getLogger(__name__)

class NeuralNetworkWebInterface:
    """Веб-интерфейс для управления нейросетями"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8081):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.setup_routes()
        self.setup_cors()
        self.connected_clients = set()
    
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
        
        # Добавляем CORS ко всем маршрутам
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    def setup_routes(self):
        """Настройка маршрутов"""
        # Статические файлы
        self.app.router.add_static('/static', '/workspace/neural_networks/visualizations')
        
        # API маршруты
        self.app.router.add_get('/', self.index_handler)
        self.app.router.add_get('/api/networks', self.get_networks_handler)
        self.app.router.add_post('/api/networks/create', self.create_network_handler)
        self.app.router.add_post('/api/networks/train', self.train_network_handler)
        self.app.router.add_post('/api/networks/visualize', self.visualize_network_handler)
        self.app.router.add_post('/api/networks/auto-create', self.auto_create_network_handler)
        self.app.router.add_get('/api/networks/{network_name}/status', self.get_network_status_handler)
        self.app.router.add_websocket('/ws', self.websocket_handler)
    
    async def index_handler(self, request):
        """Главная страница"""
        html_content = """
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Neural Network Creator</title>
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
                
                .network-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 10px;
                }
                
                .network-name {
                    font-weight: 600;
                    color: #333;
                    font-size: 1.1em;
                }
                
                .network-status {
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                }
                
                .status-created {
                    background: #e3f2fd;
                    color: #1976d2;
                }
                
                .status-trained {
                    background: #e8f5e8;
                    color: #388e3c;
                }
                
                .status-training {
                    background: #fff3e0;
                    color: #f57c00;
                }
                
                .network-details {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 10px;
                    font-size: 14px;
                    color: #666;
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
                
                .visualization {
                    text-align: center;
                    margin-top: 20px;
                }
                
                .visualization img {
                    max-width: 100%;
                    border-radius: 10px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
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
                    <h1>🧠 Neural Network Creator</h1>
                    <p>Создавайте, обучайте и визуализируйте нейросети с помощью ИИ</p>
                </div>
                
                <div class="alert alert-success" id="successAlert"></div>
                <div class="alert alert-error" id="errorAlert"></div>
                
                <div class="dashboard">
                    <div class="card">
                        <h3>🚀 Создать новую нейросеть</h3>
                        <form id="createNetworkForm">
                            <div class="form-group">
                                <label for="networkName">Название сети:</label>
                                <input type="text" id="networkName" name="name" placeholder="my_neural_network" required>
                            </div>
                            <div class="form-group">
                                <label for="networkType">Тип задачи:</label>
                                <select id="networkType" name="type" required>
                                    <option value="classification">Классификация</option>
                                    <option value="regression">Регрессия</option>
                                    <option value="generation">Генерация</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="inputSize">Размер входа:</label>
                                <input type="number" id="inputSize" name="input_size" value="784" required>
                            </div>
                            <div class="form-group">
                                <label for="outputSize">Размер выхода:</label>
                                <input type="number" id="outputSize" name="output_size" value="10" required>
                            </div>
                            <div class="form-group">
                                <label for="hiddenLayers">Скрытые слои (через запятую):</label>
                                <input type="text" id="hiddenLayers" name="hidden_layers" value="128,64" placeholder="128,64,32">
                            </div>
                            <button type="submit" class="btn btn-success">Создать нейросеть</button>
                        </form>
                    </div>
                    
                    <div class="card">
                        <h3>🤖 Автоматическое создание с ИИ</h3>
                        <form id="autoCreateForm">
                            <div class="form-group">
                                <label for="taskDescription">Описание задачи:</label>
                                <textarea id="taskDescription" name="task" rows="4" placeholder="Создай нейросеть для классификации изображений кошек и собак..." required></textarea>
                            </div>
                            <button type="submit" class="btn btn-info">Создать с помощью ИИ</button>
                        </form>
                    </div>
                </div>
                
                <div class="networks-list">
                    <h3>📊 Созданные нейросети</h3>
                    <div class="loading" id="loading">
                        <div class="spinner"></div>
                        <p>Загрузка...</p>
                    </div>
                    <div id="networksList"></div>
                </div>
                
                <div class="visualization" id="visualization"></div>
            </div>
            
            <script>
                let currentNetworks = [];
                
                // Инициализация
                document.addEventListener('DOMContentLoaded', function() {
                    loadNetworks();
                    setupEventListeners();
                });
                
                function setupEventListeners() {
                    document.getElementById('createNetworkForm').addEventListener('submit', handleCreateNetwork);
                    document.getElementById('autoCreateForm').addEventListener('submit', handleAutoCreate);
                }
                
                async function handleCreateNetwork(e) {
                    e.preventDefault();
                    const formData = new FormData(e.target);
                    const data = Object.fromEntries(formData);
                    
                    // Парсим скрытые слои
                    data.hidden_layers = data.hidden_layers.split(',').map(x => parseInt(x.trim()));
                    data.input_size = parseInt(data.input_size);
                    data.output_size = parseInt(data.output_size);
                    
                    showLoading(true);
                    try {
                        const response = await fetch('/api/networks/create', {
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
                            showSuccess(result.message);
                            loadNetworks();
                        }
                    } catch (error) {
                        showError('Ошибка создания нейросети: ' + error.message);
                    } finally {
                        showLoading(false);
                    }
                }
                
                async function handleAutoCreate(e) {
                    e.preventDefault();
                    const formData = new FormData(e.target);
                    const data = Object.fromEntries(formData);
                    
                    showLoading(true);
                    try {
                        const response = await fetch('/api/networks/auto-create', {
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
                            showSuccess(result.message);
                            loadNetworks();
                        }
                    } catch (error) {
                        showError('Ошибка автоматического создания: ' + error.message);
                    } finally {
                        showLoading(false);
                    }
                }
                
                async function loadNetworks() {
                    showLoading(true);
                    try {
                        const response = await fetch('/api/networks');
                        const result = await response.json();
                        
                        if (result.error) {
                            showError(result.error);
                        } else {
                            currentNetworks = result.networks;
                            displayNetworks(result.networks);
                        }
                    } catch (error) {
                        showError('Ошибка загрузки сетей: ' + error.message);
                    } finally {
                        showLoading(false);
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
                            <div class="network-header">
                                <div class="network-name">${network.name}</div>
                                <div class="network-status status-${network.status}">${getStatusText(network.status)}</div>
                            </div>
                            <div class="network-details">
                                <div><strong>Тип:</strong> ${network.architecture.type || 'Не указан'}</div>
                                <div><strong>Вход:</strong> ${network.architecture.input_size}</div>
                                <div><strong>Выход:</strong> ${network.architecture.output_size}</div>
                                <div><strong>Слои:</strong> ${network.architecture.layers ? network.architecture.layers.length : 0}</div>
                                <div><strong>Создана:</strong> ${new Date(network.created_at).toLocaleString()}</div>
                                ${network.test_accuracy ? `<div><strong>Точность:</strong> ${network.test_accuracy.toFixed(2)}%</div>` : ''}
                            </div>
                            <div style="margin-top: 15px;">
                                ${network.status === 'created' ? `
                                    <button class="btn btn-warning" onclick="trainNetwork('${network.name}')">Обучить</button>
                                ` : ''}
                                <button class="btn btn-info" onclick="visualizeNetwork('${network.name}')">Визуализировать</button>
                                <button class="btn" onclick="showNetworkDetails('${network.name}')">Детали</button>
                            </div>
                        </div>
                    `).join('');
                }
                
                function getStatusText(status) {
                    const statusMap = {
                        'created': 'Создана',
                        'trained': 'Обучена',
                        'training': 'Обучение...',
                        'error': 'Ошибка'
                    };
                    return statusMap[status] || status;
                }
                
                async function trainNetwork(networkName) {
                    showLoading(true);
                    try {
                        const response = await fetch('/api/networks/train', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ network_name: networkName })
                        });
                        
                        const result = await response.json();
                        
                        if (result.error) {
                            showError(result.error);
                        } else {
                            showSuccess(result.message);
                            loadNetworks();
                        }
                    } catch (error) {
                        showError('Ошибка обучения: ' + error.message);
                    } finally {
                        showLoading(false);
                    }
                }
                
                async function visualizeNetwork(networkName) {
                    showLoading(true);
                    try {
                        const response = await fetch('/api/networks/visualize', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ network_name: networkName })
                        });
                        
                        const result = await response.json();
                        
                        if (result.error) {
                            showError(result.error);
                        } else {
                            showSuccess(result.message);
                            showVisualization(result.visualization_path);
                        }
                    } catch (error) {
                        showError('Ошибка визуализации: ' + error.message);
                    } finally {
                        showLoading(false);
                    }
                }
                
                function showVisualization(imagePath) {
                    const container = document.getElementById('visualization');
                    container.innerHTML = `
                        <h3>Визуализация нейросети</h3>
                        <img src="${imagePath}" alt="Визуализация нейросети">
                    `;
                }
                
                function showNetworkDetails(networkName) {
                    const network = currentNetworks.find(n => n.name === networkName);
                    if (network) {
                        alert(`Детали сети "${networkName}":\\n\\n` +
                              `Архитектура: ${JSON.stringify(network.architecture, null, 2)}`);
                    }
                }
                
                function showLoading(show) {
                    document.getElementById('loading').style.display = show ? 'block' : 'none';
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
    
    async def get_networks_handler(self, request):
        """Получение списка нейросетей"""
        try:
            result = await neural_network_creator._handle_list_networks({})
            return web.json_response(result)
        except Exception as e:
            logger.error(f"❌ Ошибка получения сетей: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def create_network_handler(self, request):
        """Создание новой нейросети"""
        try:
            data = await request.json()
            result = await neural_network_creator._handle_create_network(data)
            return web.json_response(result)
        except Exception as e:
            logger.error(f"❌ Ошибка создания сети: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def train_network_handler(self, request):
        """Обучение нейросети"""
        try:
            data = await request.json()
            result = await neural_network_creator._handle_train_network(data)
            return web.json_response(result)
        except Exception as e:
            logger.error(f"❌ Ошибка обучения сети: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def visualize_network_handler(self, request):
        """Визуализация нейросети"""
        try:
            data = await request.json()
            result = await neural_network_creator._handle_visualize_network(data)
            return web.json_response(result)
        except Exception as e:
            logger.error(f"❌ Ошибка визуализации: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def auto_create_network_handler(self, request):
        """Автоматическое создание нейросети"""
        try:
            data = await request.json()
            result = await neural_network_creator._handle_auto_create_network(data)
            return web.json_response(result)
        except Exception as e:
            logger.error(f"❌ Ошибка автоматического создания: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def get_network_status_handler(self, request):
        """Получение статуса нейросети"""
        try:
            network_name = request.match_info['network_name']
            networks = await neural_network_creator._handle_list_networks({})
            
            network = next((n for n in networks.get('networks', []) if n['name'] == network_name), None)
            if network:
                return web.json_response(network)
            else:
                return web.json_response({"error": "Сеть не найдена"}, status=404)
        except Exception as e:
            logger.error(f"❌ Ошибка получения статуса: {e}")
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
                # Подписка на обновления
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
    
    async def broadcast_update(self, message):
        """Отправка обновления всем подключенным клиентам"""
        if self.connected_clients:
            message_str = json.dumps(message)
            disconnected = set()
            
            for ws in self.connected_clients:
                try:
                    await ws.send_str(message_str)
                except Exception as e:
                    logger.error(f"❌ Ошибка отправки WebSocket сообщения: {e}")
                    disconnected.add(ws)
            
            # Удаляем отключенные соединения
            self.connected_clients -= disconnected
    
    async def start_server(self):
        """Запуск веб-сервера"""
        try:
            runner = web.AppRunner(self.app)
            await runner.setup()
            site = web.TCPSite(runner, self.host, self.port)
            await site.start()
            
            logger.info(f"🌐 Neural Network Creator веб-интерфейс запущен на http://{self.host}:{self.port}")
            logger.info(f"📊 Доступные функции:")
            logger.info(f"   - Создание нейросетей")
            logger.info(f"   - Автоматическое создание с ИИ")
            logger.info(f"   - Обучение нейросетей")
            logger.info(f"   - Визуализация архитектуры")
            logger.info(f"   - Real-time обновления")
            
            return runner
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска веб-сервера: {e}")
            raise

# Глобальный экземпляр веб-интерфейса
web_interface = NeuralNetworkWebInterface()

async def main():
    """Главная функция"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        runner = await web_interface.start_server()
        
        # Запускаем в бесконечном цикле
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Остановка веб-интерфейса...")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())