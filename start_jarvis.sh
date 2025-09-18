#!/bin/bash

# JARVIS Startup Script
# Скрипт запуска автономной системы Джарвис

echo "🚀 Запуск системы JARVIS..."

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Устанавливаем..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не найден. Устанавливаем..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Создаем виртуальное окружение если его нет
if [ ! -d "jarvis_env" ]; then
    echo "📦 Создаем виртуальное окружение..."
    python3 -m venv jarvis_env
fi

# Активируем виртуальное окружение
source jarvis_env/bin/activate

# Проверяем установлены ли зависимости
echo "📥 Проверяем зависимости..."
if ! python3 -c "import fastapi, uvicorn, docker, paramiko" 2>/dev/null; then
    echo "📥 Устанавливаем зависимости..."
    pip install -r jarvis_data/requirements.txt
    pip install tabulate matplotlib
else
    echo "✅ Зависимости уже установлены"
fi

# Создаем необходимые директории
echo "📁 Создаем директории..."
mkdir -p jarvis_data/knowledge
mkdir -p jarvis_data/logs
mkdir -p jarvis_data/templates
mkdir -p jarvis_data/automation
mkdir -p jarvis_data/replication

# Проверяем права доступа
echo "🔐 Настраиваем права доступа..."
chmod +x jarvis_core.py
chmod +x jarvis_integration.py
chmod +x jarvis_replicator.py

# Копируем файлы в jarvis_data
cp jarvis_core.py jarvis_integration.py jarvis_replicator.py jarvis_data/

# Запускаем систему
echo "🎯 Запускаем JARVIS..."
python3 jarvis_core.py

echo "✅ JARVIS запущен! Доступен по адресу: http://localhost:8080"



# JARVIS Startup Script
# Скрипт запуска автономной системы Джарвис

echo "🚀 Запуск системы JARVIS..."

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Устанавливаем..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не найден. Устанавливаем..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Создаем виртуальное окружение если его нет
if [ ! -d "jarvis_env" ]; then
    echo "📦 Создаем виртуальное окружение..."
    python3 -m venv jarvis_env
fi

# Активируем виртуальное окружение
source jarvis_env/bin/activate

# Проверяем установлены ли зависимости
echo "📥 Проверяем зависимости..."
if ! python3 -c "import fastapi, uvicorn, docker, paramiko" 2>/dev/null; then
    echo "📥 Устанавливаем зависимости..."
    pip install -r jarvis_data/requirements.txt
    pip install tabulate matplotlib
else
    echo "✅ Зависимости уже установлены"
fi

# Создаем необходимые директории
echo "📁 Создаем директории..."
mkdir -p jarvis_data/knowledge
mkdir -p jarvis_data/logs
mkdir -p jarvis_data/templates
mkdir -p jarvis_data/automation
mkdir -p jarvis_data/replication

# Проверяем права доступа
echo "🔐 Настраиваем права доступа..."
chmod +x jarvis_core.py
chmod +x jarvis_integration.py
chmod +x jarvis_replicator.py

# Копируем файлы в jarvis_data
cp jarvis_core.py jarvis_integration.py jarvis_replicator.py jarvis_data/

# Запускаем систему
echo "🎯 Запускаем JARVIS..."
python3 jarvis_core.py

echo "✅ JARVIS запущен! Доступен по адресу: http://localhost:8080"