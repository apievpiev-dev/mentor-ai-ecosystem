#!/bin/bash
# filepath: reset_mentor_project.sh

# 1. Остановить все контейнеры Docker
docker compose down || docker-compose down

# 2. Удалить все контейнеры, образы и тома Docker
docker system prune -a --volumes -f

# 3. Удалить директорию проекта (замените путь, если нужно)
rm -rf ~/mentor-coder100
rm -rf ~/MentorCoder100
rm -rf ~/workspace
rm -rf ~/ollama
rm -rf ~/qdrant
rm -rf ~/redis
rm -rf ~/.cache/ollama ~/.ollama ~/.docker

# 4. (Опционально) Очистить логи и временные файлы
rm -rf /tmp/*

echo "Сервер очищен. Можно начинать новый проект."