
FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    docker.io \
    openssh-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем код JARVIS
COPY jarvis_core.py .
COPY jarvis_integration.py .
COPY jarvis_replicator.py .

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем конфигурацию
COPY config.yaml .
COPY replication_config.yaml .

# Создаем директории
RUN mkdir -p /app/jarvis_data/knowledge
RUN mkdir -p /app/jarvis_data/logs
RUN mkdir -p /app/jarvis_data/templates

# Копируем шаблоны
COPY templates/ ./templates/

# Устанавливаем права
RUN chmod +x jarvis_core.py

# Экспортируем порт
EXPOSE 8080

# Команда запуска
CMD ["python", "jarvis_core.py"]
