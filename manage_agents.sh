#!/bin/bash
# Скрипт управления агентами системы мульти AI

case "$1" in
    start)
        echo "🚀 Запуск системы агентов..."
        cd /home/mentor
        source multi_agent_env/bin/activate
        nohup python3 start_multi_agent_system.py 0.0.0.0 8080 > system.log 2>&1 &
        echo "✅ Система запущена"
        ;;
    stop)
        echo "🛑 Остановка системы агентов..."
        pkill -f "start_multi_agent_system.py"
        echo "✅ Система остановлена"
        ;;
    restart)
        echo "🔄 Перезапуск системы агентов..."
        $0 stop
        sleep 2
        $0 start
        ;;
    status)
        echo "📊 Статус системы агентов:"
        if ss -tlnp | grep -q ':8080'; then
            echo "✅ Система запущена на порту 8080"
            echo "🌐 Веб-интерфейс: http://5.129.198.210:8080"
        else
            echo "❌ Система не запущена"
        fi
        ;;
    logs)
        echo "📝 Логи системы:"
        tail -f /home/mentor/system.log
        ;;
    *)
        echo "Использование: $0 {start|stop|restart|status|logs}"
        echo "  start   - Запустить систему"
        echo "  stop    - Остановить систему"
        echo "  restart - Перезапустить систему"
        echo "  status  - Показать статус"
        echo "  logs    - Показать логи"
        exit 1
        ;;
esac



