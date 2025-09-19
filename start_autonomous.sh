#!/bin/bash

# Скрипт запуска автономной системы Multi-AI
# Автор: AI Assistant
# Дата: $(date)

echo "🚀 Запуск автономной системы Multi-AI..."

# Переходим в рабочую директорию
cd /home/mentor

# Активируем виртуальное окружение
echo "🔧 Активация виртуального окружения..."
source multi_agent_env/bin/activate

# Проверяем, что система не запущена
if lsof -i:8080 > /dev/null 2>&1; then
    echo "⚠️ Система уже запущена на порту 8080"
    echo "🛑 Остановка существующих процессов..."
    kill $(lsof -t -i:8080) 2>/dev/null
    sleep 5
fi

# Запускаем автономную систему
echo "🚀 Запуск автономной системы..."
nohup python3 autonomous_main.py > autonomous_system.log 2>&1 &

# Получаем PID процесса
AUTONOMOUS_PID=$!
echo "✅ Автономная система запущена (PID: $AUTONOMOUS_PID)"

# Сохраняем PID для управления
echo $AUTONOMOUS_PID > autonomous_system.pid

# Ждем запуска
echo "⏳ Ожидание запуска системы..."
sleep 15

# Проверяем статус
echo "🔍 Проверка статуса системы..."
if curl -s http://localhost:8080/api/system/status | grep -q "running"; then
    echo "✅ Система успешно запущена!"
    echo "🌐 Веб-интерфейс: http://5.129.198.210:8080"
    echo "📊 API статуса: http://5.129.198.210:8080/api/system/status"
    echo "📋 Логи: tail -f /home/mentor/autonomous_system.log"
else
    echo "❌ Ошибка запуска системы"
    echo "📋 Проверьте логи: tail -f /home/mentor/autonomous_system.log"
    exit 1
fi

echo "🎉 Автономная система Multi-AI готова к работе!"


