#!/bin/bash

# Скрипт остановки автономной системы Multi-AI
# Автор: AI Assistant
# Дата: $(date)

echo "🛑 Остановка автономной системы Multi-AI..."

# Переходим в рабочую директорию
cd /home/mentor

# Останавливаем по PID файлу
if [ -f autonomous_system.pid ]; then
    AUTONOMOUS_PID=$(cat autonomous_system.pid)
    echo "🛑 Остановка основного процесса (PID: $AUTONOMOUS_PID)..."
    kill $AUTONOMOUS_PID 2>/dev/null
    rm -f autonomous_system.pid
fi

# Останавливаем все процессы на порту 8080
echo "🛑 Остановка процессов на порту 8080..."
if lsof -i:8080 > /dev/null 2>&1; then
    kill $(lsof -t -i:8080) 2>/dev/null
    sleep 3
fi

# Останавливаем все Python процессы автономной системы
echo "🛑 Остановка автономных процессов..."
pkill -f "autonomous_main.py" 2>/dev/null
pkill -f "autonomous_monitor.py" 2>/dev/null
pkill -f "autonomous_task_scheduler.py" 2>/dev/null
pkill -f "start_multi_agent_system.py" 2>/dev/null

# Ждем завершения процессов
sleep 5

# Проверяем, что все остановлено
if lsof -i:8080 > /dev/null 2>&1; then
    echo "⚠️ Некоторые процессы все еще работают, принудительная остановка..."
    kill -9 $(lsof -t -i:8080) 2>/dev/null
fi

echo "✅ Автономная система остановлена"
