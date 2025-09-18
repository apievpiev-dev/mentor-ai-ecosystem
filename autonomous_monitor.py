#!/usr/bin/env python3
# Автономный мониторинг системы агентов

import time
import subprocess
import requests
import json
from datetime import datetime

class AutonomousMonitor:
    def __init__(self):
        self.server_ip = '5.129.198.210'
        self.port = 8080
        self.check_interval = 30  # секунд
        
    def check_system_health(self):
        try:
            response = requests.get(f'http://{self.server_ip}:{self.port}/api/system/status', timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ [{datetime.now()}] Система работает: {data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ [{datetime.now()}] Система недоступна: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ [{datetime.now()}] Ошибка проверки: {e}")
            return False
    
    def restart_system_if_needed(self):
        if not self.check_system_health():
            print(f"🔄 [{datetime.now()}] Перезапуск системы...")
            try:
                subprocess.run(['/home/mentor/manage_agents.sh', 'restart'], check=True)
                time.sleep(10)  # Ждем запуска
                if self.check_system_health():
                    print(f"✅ [{datetime.now()}] Система успешно перезапущена")
                else:
                    print(f"❌ [{datetime.now()}] Ошибка перезапуска системы")
            except Exception as e:
                print(f"❌ [{datetime.now()}] Ошибка перезапуска: {e}")
    
    def run(self):
        print(f"🚀 Автономный мониторинг запущен для {self.server_ip}:{self.port}")
        print(f"⏰ Интервал проверки: {self.check_interval} секунд")
        print("🛑 Для остановки нажмите Ctrl+C")
        
        try:
            while True:
                self.restart_system_if_needed()
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            print("\n🛑 Мониторинг остановлен")

if __name__ == '__main__':
    monitor = AutonomousMonitor()
    monitor.run()

