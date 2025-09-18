#!/bin/bash
"""
Скрипт остановки оптимизированной AI системы
"""

echo "🛑 Остановка оптимизированной AI системы..."

# Останавливаем основную систему
echo "🤖 Остановка основной AI системы..."
pkill -f "real_autonomous_system.py" 2>/dev/null

# Останавливаем оптимизатор
echo "🔧 Остановка оптимизатора Ollama..."
pkill -f "ollama_optimizer.py" 2>/dev/null

# Ждем завершения процессов
sleep 3

# Проверяем, что процессы остановлены
REMAINING=$(pgrep -f "real_autonomous_system.py\|ollama_optimizer.py" | wc -l)
if [ $REMAINING -eq 0 ]; then
    echo "✅ Все процессы остановлены"
else
    echo "⚠️ Остались процессы: $REMAINING"
    echo "Принудительная остановка..."
    pkill -9 -f "real_autonomous_system.py" 2>/dev/null
    pkill -9 -f "ollama_optimizer.py" 2>/dev/null
fi

echo "✅ Система остановлена"
