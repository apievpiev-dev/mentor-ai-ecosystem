#!/bin/bash

echo "🚀 Запуск визуальной автономной системы агентов..."

# Проверяем Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Устанавливаем..."
    apt-get update && apt-get install -y python3 python3-pip
fi

# Устанавливаем зависимости
echo "📦 Устанавливаем зависимости..."
pip3 install -r requirements_visual.txt

# Создаем директории для логов
mkdir -p /workspace/logs
mkdir -p /workspace/visual_screenshots

# Запускаем систему
echo "🤖 Запускаем визуальную автономную систему..."
python3 visual_autonomous_system.py