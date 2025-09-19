#!/bin/bash

# Скрипт запуска системы бесплатных локальных нейросетей
# "Нейросеть, которая создает нейросети" - только бесплатные модели

echo "🧠 Запуск системы бесплатных локальных нейросетей..."
echo "========================================================"

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
if [ ! -d "free_neural_env" ]; then
    echo "📦 Создание виртуального окружения для бесплатных моделей..."
    python3 -m venv free_neural_env
fi

# Активируем виртуальное окружение
echo "🔧 Активация виртуального окружения..."
source free_neural_env/bin/activate

# Устанавливаем только бесплатные зависимости
echo "📚 Установка бесплатных зависимостей..."
pip install --upgrade pip

# Основные пакеты для AI (бесплатные)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install transformers accelerate sentencepiece protobuf
pip install numpy matplotlib seaborn
pip install aiohttp aiohttp-cors
pip install requests

# Проверяем Ollama (бесплатный)
if ! command -v ollama &> /dev/null; then
    echo "📥 Устанавливаем Ollama (бесплатный)..."
    curl -fsSL https://ollama.ai/install.sh | sh
    echo "🔄 Запуск Ollama сервера..."
    ollama serve &
    sleep 5
    echo "📥 Загрузка бесплатных моделей Ollama..."
    ollama pull tinyllama:latest &
    ollama pull orca-mini:latest &
    ollama pull phi3:latest &
    ollama pull mistral:latest &
else
    echo "✅ Ollama уже установлен"
    # Запускаем сервер если не запущен
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "🔄 Запуск Ollama сервера..."
        ollama serve &
        sleep 5
    fi
fi

# Создаем необходимые директории
echo "📁 Создание директорий для бесплатных моделей..."
mkdir -p /workspace/free_models/{ollama,huggingface,transformers,cache,logs,networks,projects,statistics,system_logs}

# Проверяем доступность бесплатных моделей
echo "🔍 Проверка доступности бесплатных моделей..."

# Проверяем Ollama
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama доступен"
else
    echo "⚠️ Ollama недоступен, будут использоваться локальные модели"
fi

# Проверяем Python пакеты
python3 -c "import transformers; print('✅ Hugging Face Transformers доступен')" 2>/dev/null || echo "⚠️ Hugging Face Transformers недоступен"

# Запускаем систему
echo "🚀 Запуск системы бесплатных локальных нейросетей..."
echo "========================================================"
echo "🌐 Веб-интерфейс будет доступен по адресу: http://localhost:8081"
echo "🤖 Система будет работать только с бесплатными моделями:"
echo "   • Ollama - бесплатные языковые модели"
echo "   • Hugging Face - бесплатные трансформеры"  
echo "   • Локальные модели - простые трансформеры"
echo "📊 Все модели устанавливаются локально на сервер"
echo "💰 Никаких платных API или подписок"
echo "========================================================"

# Запускаем главный файл
python3 free_neural_network_creator_main.py

echo "🛑 Система бесплатных локальных нейросетей остановлена."