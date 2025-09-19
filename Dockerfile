FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов проекта
COPY requirements.txt .
COPY streamlined_jarvis.py .
COPY enhanced_autonomous_jarvis.py .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Создание директории для логов
RUN mkdir -p /app/logs

# Открытие порта
EXPOSE 8080

# Переменные окружения
ENV PYTHONPATH=/app
ENV JARVIS_ENV=production
ENV JARVIS_LOG_LEVEL=INFO

# Команда запуска
CMD ["python3", "streamlined_jarvis.py"]
