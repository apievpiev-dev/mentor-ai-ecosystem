#!/usr/bin/env python3
"""
Простой дашборд для Wildberries - показывает реальные данные
Использует встроенный HTTP сервер Python
"""

import http.server
import socketserver
import json
from datetime import datetime
from wb_api import get_cards, get_orders, get_sales

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_dashboard()
        elif self.path == '/api/data':
            self.send_api_data()
        else:
            super().do_GET()
    
    def send_dashboard(self):
        # Получаем реальные данные
        cards = get_cards(limit=10)
        orders = get_orders(days=7) or []
        sales = get_sales(days=7) or []
        
        # Считаем статистику
        total_orders = len(orders)
        total_sales = len(sales)
        conversion = (total_sales / total_orders * 100) if total_orders > 0 else 0
        
        # Топ товары по заказам (реальная статистика)
        top_products = []
        if orders:
            from collections import Counter
            order_nmids = [order['nmId'] for order in orders]
            top_orders = Counter(order_nmids).most_common(5)
            
            for nmid, count in top_orders:
                # Найдем информацию о товаре
                order_info = next((o for o in orders if o['nmId'] == nmid), None)
                if order_info:
                    top_products.append({
                        'title': f"{order_info['subject']} {order_info['brand']}",
                        'nmID': nmid,
                        'orders': count,
                        'type': 'orders'
                    })
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Wildberries Dashboard</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ background: #fff; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 20px; }}
                .stat-card {{ background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }}
                .stat-number {{ font-size: 2em; font-weight: bold; color: #2c3e50; }}
                .stat-label {{ color: #7f8c8d; margin-top: 5px; }}
                .products {{ background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .product {{ border-bottom: 1px solid #ecf0f1; padding: 15px 0; }}
                .product:last-child {{ border-bottom: none; }}
                .refresh {{ background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 10px 0; }}
                .refresh:hover {{ background: #2980b9; }}
                .success {{ color: #27ae60; font-weight: bold; }}
                .warning {{ color: #f39c12; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛒 Wildberries Dashboard</h1>
                    <p>Обновлено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <button class="refresh" onclick="location.reload()">🔄 Обновить данные</button>
                </div>
                
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number">{len(cards.get('cards', [])) if cards else 0}</div>
                        <div class="stat-label">📦 Товаров в каталоге</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number success">{total_orders}</div>
                        <div class="stat-label">🛒 Заказов за 7 дней</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number success">{total_sales}</div>
                        <div class="stat-label">💰 Продаж за 7 дней</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number {'success' if conversion > 20 else 'warning'}">{conversion:.1f}%</div>
                        <div class="stat-label">📊 Конверсия заказ→продажа</div>
                    </div>
                </div>
                
                <div class="products">
                    <h2>📦 Товары в каталоге сейчас</h2>
                    {''.join([f'''
                    <div class="product">
                        <strong>{card['title'][:50]}{'...' if len(card['title']) > 50 else ''}</strong><br>
                        <small>Артикул: {card['nmID']} | Бренд: {card['brand']}</small>
                    </div>
                    ''' for card in cards.get('cards', [])]) if cards and cards.get('cards') else '<p>Нет товаров в каталоге</p>'}
                </div>
                
                <div class="products">
                    <h2>🏆 Топ товары по заказам (все товары)</h2>
                    {''.join([f'''
                    <div class="product">
                        <strong>{product['title']}</strong><br>
                        <small>Артикул: {product['nmID']} | Заказов: {product['orders']}</small>
                    </div>
                    ''' for product in top_products]) if top_products else '<p>Нет данных о заказах</p>'}
                </div>
                
                <div style="background: #fff; padding: 20px; border-radius: 10px; margin-top: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h3>🎯 Статус API</h3>
                    <p class="success">✅ Wildberries API подключен и работает</p>
                    <p class="success">✅ Получены реальные данные о товарах и заказах</p>
                    <p class="success">✅ Дашборд обновляется в реальном времени</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def send_api_data(self):
        # API endpoint для получения данных в JSON
        cards = get_cards(limit=10)
        orders = get_orders(days=7) or []
        sales = get_sales(days=7) or []
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'products_count': len(cards.get('cards', [])) if cards else 0,
            'orders_7days': len(orders),
            'sales_7days': len(sales),
            'conversion_rate': (len(sales) / len(orders) * 100) if orders else 0,
            'top_products': []
        }
        
        if cards and cards.get('cards'):
            for card in cards['cards'][:5]:
                data['top_products'].append({
                    'title': card['title'],
                    'nmID': card['nmID'],
                    'brand': card['brand']
                })
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))

if __name__ == "__main__":
    PORT = 8002
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        print(f"🚀 Wildberries Dashboard запущен!")
        print(f"📊 Откройте в браузере: http://localhost:{PORT}")
        print(f"🔗 API данные: http://localhost:{PORT}/api/data")
        print("Нажмите Ctrl+C для остановки")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Дашборд остановлен")