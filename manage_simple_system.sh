#!/bin/bash

# Скрипт управления простой автономной системой Multi-AI
# Автор: AI Assistant
# Дата: $(date)

echo "🤖 Управление простой автономной системой Multi-AI"

# Переходим в рабочую директорию
cd /home/mentor

# Активируем виртуальное окружение
source multi_agent_env/bin/activate

case "$1" in
    start)
        echo "🚀 Запуск простой автономной системы..."
        
        # Проверяем, что система не запущена
        if lsof -i:8080 > /dev/null 2>&1; then
            echo "⚠️ Система уже запущена на порту 8080"
            echo "🛑 Остановка существующих процессов..."
            kill $(lsof -t -i:8080) 2>/dev/null
            sleep 5
        fi
        
        # Запускаем простую систему
        nohup python3 simple_working_system.py > simple_system.log 2>&1 &
        
        # Получаем PID процесса
        SIMPLE_PID=$!
        echo "✅ Простая автономная система запущена (PID: $SIMPLE_PID)"
        
        # Сохраняем PID для управления
        echo $SIMPLE_PID > simple_system.pid
        
        # Ждем запуска
        echo "⏳ Ожидание запуска системы..."
        sleep 10
        
        # Проверяем статус
        echo "🔍 Проверка статуса системы..."
        if curl -s http://localhost:8080/api/system/status | grep -q "running"; then
            echo "✅ Система успешно запущена!"
            echo "🌐 Веб-интерфейс: http://5.129.198.210:8080"
            echo "📊 API статуса: http://5.129.198.210:8080/api/system/status"
            echo "📋 Логи: tail -f /home/mentor/simple_system.log"
        else
            echo "❌ Ошибка запуска системы"
            echo "📋 Проверьте логи: tail -f /home/mentor/simple_system.log"
            exit 1
        fi
        
        echo "🎉 Простая автономная система Multi-AI готова к работе!"
        ;;
        
    stop)
        echo "🛑 Остановка простой автономной системы..."
        
        # Останавливаем по PID файлу
        if [ -f simple_system.pid ]; then
            SIMPLE_PID=$(cat simple_system.pid)
            echo "🛑 Остановка основного процесса (PID: $SIMPLE_PID)..."
            kill $SIMPLE_PID 2>/dev/null
            rm -f simple_system.pid
        fi
        
        # Останавливаем все процессы на порту 8080
        echo "🛑 Остановка процессов на порту 8080..."
        if lsof -i:8080 > /dev/null 2>&1; then
            kill $(lsof -t -i:8080) 2>/dev/null
            sleep 3
        fi
        
        # Останавливаем все Python процессы простой системы
        echo "🛑 Остановка процессов простой системы..."
        pkill -f "simple_working_system.py" 2>/dev/null
        
        # Ждем завершения процессов
        sleep 5
        
        # Проверяем, что все остановлено
        if lsof -i:8080 > /dev/null 2>&1; then
            echo "⚠️ Некоторые процессы все еще работают, принудительная остановка..."
            kill -9 $(lsof -t -i:8080) 2>/dev/null
        fi
        
        echo "✅ Простая автономная система остановлена"
        ;;
        
    restart)
        echo "🔄 Перезапуск простой автономной системы..."
        $0 stop
        sleep 5
        $0 start
        ;;
        
    status)
        echo "📊 Статус простой автономной системы:"
        
        if lsof -i:8080 > /dev/null 2>&1; then
            echo "✅ Система запущена на порту 8080"
            
            # Проверяем API
            if curl -s http://localhost:8080/api/system/status > /dev/null 2>&1; then
                echo "✅ API отвечает"
                
                # Получаем детальный статус
                echo "📋 Детальный статус:"
                curl -s http://localhost:8080/api/system/status | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f'  Статус: {data[\"system_status\"]}')
    print(f'  Агентов: {data[\"total_agents\"]}')
    print(f'  Активных: {data[\"active_agents\"]}')
    print(f'  Время работы: {data[\"uptime\"]}')
except:
    print('  Ошибка получения статуса')
"
            else
                echo "❌ API не отвечает"
            fi
        else
            echo "❌ Система не запущена"
        fi
        ;;
        
    logs)
        echo "📋 Логи простой автономной системы:"
        if [ -f simple_system.log ]; then
            tail -50 simple_system.log
        else
            echo "❌ Файл логов не найден"
        fi
        ;;
        
    *)
        echo "Использование: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Команды:"
        echo "  start   - Запустить простую автономную систему"
        echo "  stop    - Остановить простую автономную систему"
        echo "  restart - Перезапустить простую автономную систему"
        echo "  status  - Показать статус системы"
        echo "  logs    - Показать логи системы"
        exit 1
        ;;
esac


