# 🧠 Neural System - Автономная система нейросетей

## 🎯 Обзор проекта

**Neural System** - это полностью автономная система управления множественными AI агентами с визуальной верификацией, интегрированными бесплатными нейросетями и единым веб-интерфейсом. Система работает с минимальным участием пользователя и автоматически решает задачи через специализированных AI агентов.

## ✨ Ключевые возможности

### 🤖 Множественные AI Агенты
- **Универсальный Помощник** - общие задачи и координация
- **Разработчик Кода** - генерация, отладка и оптимизация кода
- **Аналитик Данных** - анализ данных и создание отчетов
- **Менеджер Проектов** - планирование и управление проектами
- **Дизайнер** - UI/UX дизайн и визуализация
- **Тестировщик** - тестирование и контроль качества

### 🆓 Бесплатные нейросети
- **Ollama** - локальные модели (llama2, codellama, mistral)
- **Hugging Face** - бесплатные модели через API
- **Local Provider** - fallback для демонстрации

### 👁️ Визуальная верификация
- Автоматическая проверка результатов генерации кода
- Визуальный мониторинг веб-интерфейсов
- Создание скриншотов и анализ UI
- Автоматическое исправление визуальных проблем

### 🔄 Автономная работа
- Автоматическая генерация и выполнение задач
- Мониторинг здоровья системы
- Оптимизация производительности
- Самостоятельное решение проблем

### 🌐 Единый веб-интерфейс
- Современный responsive дизайн
- Real-time обновления через WebSocket
- Управление всеми компонентами системы
- Визуализация метрик и статуса

## 🏗️ Архитектура системы

```
Neural System
├── 🧠 Enhanced AI Engine - Улучшенный движок AI
│   ├── Ollama Provider - Локальные модели
│   ├── Hugging Face Provider - API модели
│   └── Local Provider - Fallback
├── 🤖 Multi-Agent System - Система множественных агентов
│   ├── General Assistant - Универсальный помощник
│   ├── Code Developer - Разработчик кода
│   ├── Data Analyst - Аналитик данных
│   ├── Project Manager - Менеджер проектов
│   ├── Designer - Дизайнер
│   └── QA Tester - Тестировщик
├── 👁️ Visual Monitor - Визуальный мониторинг
│   ├── Screenshot Capture - Захват скриншотов
│   ├── Visual Analysis - Анализ визуальных данных
│   └── UI Verification - Верификация интерфейсов
├── 🔄 Autonomous System - Автономная система
│   ├── Task Generator - Генератор задач
│   ├── Health Monitor - Мониторинг здоровья
│   ├── Performance Optimizer - Оптимизатор производительности
│   └── Self-Healing - Самовосстановление
└── 🌐 Unified Interface - Единый интерфейс
    ├── Web Interface - Веб-интерфейс
    ├── WebSocket API - Real-time API
    └── REST API - REST API
```

## 🚀 Быстрый старт

### Автоматическое развертывание на сервере

```bash
# Клонируем проект
git clone <repository>
cd neural-system

# Запускаем автоматическое развертывание
sudo ./deploy_neural_system.sh
```

### Ручная установка

```bash
# 1. Установка зависимостей
pip install -r requirements.txt

# 2. Установка Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve

# 3. Загрузка моделей
ollama pull llama2:7b
ollama pull codellama:7b
ollama pull mistral:7b

# 4. Запуск системы
python unified_neural_interface.py
```

## 🌐 Доступ к системе

После развертывания система будет доступна по адресу:
- **Веб-интерфейс**: http://your-server-ip
- **API статуса**: http://your-server-ip/api/system/status
- **Список агентов**: http://your-server-ip/api/agents

## 📊 Компоненты системы

### Enhanced AI Engine (`enhanced_ai_engine.py`)
- Интеграция всех AI провайдеров
- Кэширование ответов
- Визуальная верификация результатов
- Оптимизация производительности

### Multi-Agent System (`multi_agent_system.py`)
- Специализированные AI агенты
- Общая память и контекст
- Координация между агентами
- Автоматический выбор агента

### Visual Monitor (`visual_monitor.py`)
- Захват скриншотов веб-интерфейсов
- Анализ визуальных данных
- Верификация UI компонентов
- Генерация визуальных отчетов

### Autonomous System (`autonomous_neural_system.py`)
- Автоматическая генерация задач
- Мониторинг здоровья системы
- Оптимизация производительности
- Самовосстановление

### Unified Interface (`unified_neural_interface.py`)
- Современный веб-интерфейс
- Real-time обновления
- WebSocket API
- REST API

## 🔧 Управление системой

### Скрипты управления (на сервере)

```bash
# Запуск системы
/opt/neural_system/start.sh

# Остановка системы
/opt/neural_system/stop.sh

# Перезапуск системы
/opt/neural_system/restart.sh

# Проверка статуса
/opt/neural_system/status.sh

# Обновление системы
/opt/neural_system/update.sh
```

### Systemd сервисы

```bash
# Статус сервисов
systemctl status neural-system
systemctl status autonomous-neural
systemctl status ollama

# Логи
journalctl -u neural-system -f
journalctl -u autonomous-neural -f
journalctl -u ollama -f
```

## 📡 API Endpoints

### Основные endpoints

- `GET /` - Веб-интерфейс
- `GET /api/system/status` - Статус системы
- `GET /api/agents` - Список агентов
- `POST /api/chat/send` - Отправка сообщения
- `POST /api/tasks` - Создание задачи
- `GET /api/visual/report` - Визуальный отчет
- `WebSocket /ws` - Real-time обновления

### Примеры использования

```bash
# Получение статуса системы
curl http://localhost:8081/api/system/status

# Отправка сообщения
curl -X POST http://localhost:8081/api/chat/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Создай функцию сортировки", "agent_type": "code_developer"}'

# Получение списка агентов
curl http://localhost:8081/api/agents
```

## 🎯 Типы задач

Система автоматически создает и выполняет следующие типы задач:

- **system_analysis** - Анализ состояния системы
- **performance_optimization** - Оптимизация производительности
- **visual_verification** - Визуальная верификация
- **knowledge_base_update** - Обновление базы знаний
- **security_check** - Проверка безопасности
- **code_generation** - Генерация кода
- **data_analysis** - Анализ данных
- **project_planning** - Планирование проектов

## 📈 Мониторинг и метрики

### Системные метрики
- Количество активных агентов
- Время отклика системы
- Количество выполненных задач
- Использование ресурсов
- Статус здоровья компонентов

### Визуальные метрики
- Качество веб-интерфейсов
- Время загрузки страниц
- Наличие визуальных проблем
- Статус API endpoints

## 🔒 Безопасность

- Изоляция процессов
- Ограничение доступа к API
- Логирование всех операций
- Автоматические проверки безопасности
- Обновление зависимостей

## 🛠️ Конфигурация

### Файл .env

```env
# AI провайдеры
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama2:7b
HUGGINGFACE_TOKEN=your_token_here
OPENAI_API_KEY=your_key_here

# Система
SYSTEM_HOST=0.0.0.0
SYSTEM_PORT=8081
AUTONOMOUS_MODE=true
VISUAL_VERIFICATION=true
PERFORMANCE_OPTIMIZATION=true
```

### Настройка Nginx

```nginx
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /ws {
        proxy_pass http://127.0.0.1:8081;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 📝 Логирование

### Логи системы
- `/opt/neural_system/logs/` - Логи приложения
- `journalctl -u neural-system` - Логи systemd
- `/var/log/nginx/` - Логи веб-сервера

### Мониторинг логов
```bash
# Просмотр логов в реальном времени
tail -f /opt/neural_system/logs/neural_system.log

# Логи systemd
journalctl -u neural-system -f

# Логи Nginx
tail -f /var/log/nginx/access.log
```

## 🔄 Обновление системы

```bash
# Автоматическое обновление
/opt/neural_system/update.sh

# Ручное обновление
cd /opt/neural_system
git pull origin main
./venv/bin/pip install -r requirements.txt
systemctl restart neural-system
```

## 🐛 Устранение неполадок

### Проблемы с Ollama
```bash
# Проверка статуса
systemctl status ollama

# Перезапуск
systemctl restart ollama

# Проверка моделей
ollama list
```

### Проблемы с веб-интерфейсом
```bash
# Проверка Nginx
nginx -t
systemctl status nginx

# Проверка портов
netstat -tlnp | grep :8081
```

### Проблемы с агентами
```bash
# Проверка логов
journalctl -u neural-system -f

# Перезапуск системы
/opt/neural_system/restart.sh
```

## 📚 Дополнительные ресурсы

- [Ollama Documentation](https://ollama.ai/docs)
- [Hugging Face API](https://huggingface.co/docs/api-inference)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [WebSocket Guide](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

## 🤝 Поддержка

При возникновении проблем:

1. Проверьте логи системы
2. Убедитесь в правильности конфигурации
3. Проверьте статус всех сервисов
4. Создайте issue в репозитории проекта

## 🎉 Заключение

**Neural System** представляет собой полноценную автономную платформу для работы с AI агентами, которая:

- ✅ Работает с бесплатными нейросетями
- ✅ Автоматически верифицирует результаты
- ✅ Работает автономно с минимальным участием
- ✅ Предоставляет единый веб-интерфейс
- ✅ Масштабируется под любые нагрузки
- ✅ Самовосстанавливается при проблемах

**Система готова к продуктивному использованию!**

---

**🚀 Начните использовать Neural System прямо сейчас!**