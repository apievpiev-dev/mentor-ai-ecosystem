#!/bin/bash

# Скрипт запуска системы Neural Network Creator
# "Нейросеть, которая создает нейросети"

echo "🧠 Запуск системы Neural Network Creator..."
echo "================================================"

# Проверяем Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python3."
    exit 1
fi

# Проверяем pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 не найден. Установите pip3."
    exit 1
fi

# Создаем виртуальное окружение если его нет
if [ ! -d "neural_network_env" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv neural_network_env
fi

# Активируем виртуальное окружение
echo "🔧 Активация виртуального окружения..."
source neural_network_env/bin/activate

# Устанавливаем зависимости
echo "📚 Установка зависимостей..."
pip install --upgrade pip
pip install torch torchvision torchaudio
pip install numpy matplotlib seaborn
pip install aiohttp aiohttp-cors
pip install fastapi uvicorn
pip install pydantic
pip install docker
pip install pyyaml
pip install requests

# Проверяем Ollama
if ! command -v ollama &> /dev/null; then
    echo "⚠️ Ollama не найден. Устанавливаем..."
    curl -fsSL https://ollama.ai/install.sh | sh
    echo "🔄 Запуск Ollama..."
    ollama serve &
    sleep 5
    echo "📥 Загрузка модели neural-chat..."
    ollama pull neural-chat:latest
fi

# Создаем необходимые директории
echo "📁 Создание директорий..."
mkdir -p /workspace/neural_networks/{models,data,visualizations,deployments,logs,architectures,autonomous_training,optimization_results,performance_logs,auto_models,architecture_templates,search_results,performance_db,system_logs,projects,statistics,backups}

# Проверяем Docker (опционально)
if command -v docker &> /dev/null; then
    echo "🐳 Docker найден. Система развертывания будет доступна."
else
    echo "⚠️ Docker не найден. Развертывание будет ограничено."
fi

# Запускаем систему
echo "🚀 Запуск системы Neural Network Creator..."
echo "================================================"
echo "🌐 Веб-интерфейс будет доступен по адресу: http://localhost:8081"
echo "🤖 Система будет работать в автономном режиме"
echo "📊 Все созданные нейросети будут автоматически обучаться и развертываться"
echo "================================================"

# Запускаем главный файл
python3 neural_network_creator_main.py

echo "🛑 Система Neural Network Creator остановлена."