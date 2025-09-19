#!/bin/bash
"""
Скрипт запуска оптимизированной AI системы
"""

echo "🚀 Запуск оптимизированной AI системы..."

# Останавливаем старые процессы
echo "🛑 Остановка старых процессов..."
pkill -f "real_autonomous_system.py" 2>/dev/null
pkill -f "ollama_optimizer.py" 2>/dev/null
sleep 2

# Активируем виртуальное окружение
echo "📦 Активация виртуального окружения..."
cd /home/mentor
source multi_agent_env/bin/activate

# Запускаем оптимизатор Ollama в фоне
echo "🔧 Запуск оптимизатора Ollama..."
nohup python3 ollama_optimizer.py > ollama_optimizer.log 2>&1 &
OPTIMIZER_PID=$!
echo "✅ Оптимизатор запущен (PID: $OPTIMIZER_PID)"

# Ждем немного для стабилизации
sleep 3

# Запускаем основную систему
echo "🤖 Запуск основной AI системы..."
nohup python3 real_autonomous_system.py > real_ai_system.log 2>&1 &
SYSTEM_PID=$!
echo "✅ Основная система запущена (PID: $SYSTEM_PID)"

# Ждем запуска системы
sleep 5

# Проверяем статус
echo "📊 Проверка статуса системы..."
curl -s http://localhost:8080/api/system/status | jq .

echo "✅ Оптимизированная AI система запущена!"
echo "🌐 Веб-интерфейс: http://localhost:8080"
echo "📊 API статуса: http://localhost:8080/api/system/status"
echo "📝 Логи системы: tail -f real_ai_system.log"
echo "🔧 Логи оптимизатора: tail -f ollama_optimizer.log"


