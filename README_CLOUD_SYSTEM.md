# ☁️ ОБЛАЧНАЯ СИСТЕМА МНОЖЕСТВЕННЫХ AI-АГЕНТОВ

Полноценная облачная система с автономным сервером, которая работает онлайн и не зависит от локального компьютера.

## 🚀 Быстрая установка

### Автоматическая установка (рекомендуется)
```bash
sudo ./setup_cloud_system.sh
```

### Ручная установка
```bash
# 1. Установка зависимостей
sudo apt update && sudo apt install -y python3 python3-pip python3-venv curl wget git nginx

# 2. Установка Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 3. Создание виртуального окружения
python3 -m venv multi_agent_env
source multi_agent_env/bin/activate
pip install fastapi uvicorn websockets pydantic python-multipart aiofiles requests schedule

# 4. Установка AI моделей
ollama pull llama3.1:8b
ollama pull codellama:latest
ollama pull mistral:latest

# 5. Настройка systemd сервиса
sudo cp cloud-agent-system.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable cloud-agent-system
sudo systemctl start cloud-agent-system
```

## 🌐 Доступ к системе

После установки система доступна по адресу:
- **Локально**: http://localhost
- **По сети**: http://[IP_СЕРВЕРА]
- **API**: http://[IP_СЕРВЕРА]/api/system/status

## 🤖 Возможности системы

### Автономная работа
- ✅ **Автозапуск** при загрузке сервера
- ✅ **Автовосстановление** при сбоях
- ✅ **Мониторинг здоровья** системы
- ✅ **Автоматические бэкапы**
- ✅ **Оптимизация ресурсов**

### AI Агенты
- 🤖 **Разработчик Кода** - создает проекты и код
- 📊 **Аналитик Данных** - анализирует данные
- 📋 **Менеджер Проектов** - управляет проектами
- 🎨 **Дизайнер** - создает дизайны
- 🧪 **Тестировщик** - тестирует код
- ⚙️ **AI Менеджер** - управляет нейросетями

### Управление AI моделями
- 📥 **Автоустановка** новых моделей
- 🔄 **Автообновление** моделей
- 📊 **Мониторинг производительности**
- 🧹 **Очистка неиспользуемых моделей**
- ⚡ **Оптимизация** работы моделей

## 🛠️ Управление системой

### Статус системы
```bash
# Проверка статуса
systemctl status cloud-agent-system

# Просмотр логов
journalctl -u cloud-agent-system -f

# Статус AI моделей
curl http://localhost/api/system/status
```

### Управление сервисом
```bash
# Запуск
sudo systemctl start cloud-agent-system

# Остановка
sudo systemctl stop cloud-agent-system

# Перезапуск
sudo systemctl restart cloud-agent-system

# Автозапуск
sudo systemctl enable cloud-agent-system
```

### Управление AI моделями
```bash
# Список моделей
ollama list

# Установка новой модели
ollama pull [model_name]

# Удаление модели
ollama rm [model_name]

# Запуск модели
ollama run [model_name]
```

## 📊 Мониторинг

### Системные метрики
- 💾 **Использование памяти**
- 💿 **Использование диска**
- ⚡ **Нагрузка CPU**
- 🌐 **Сетевой трафик**

### AI метрики
- 🤖 **Количество моделей**
- ⏱️ **Время ответа**
- 📈 **Производительность**
- 🔄 **Статус моделей**

### Логи системы
- 📝 **Основные логи**: `/home/mentor/cloud_system.log`
- 📊 **Логи агентов**: `/home/mentor/agent_logs/`
- 🤖 **Логи AI**: `/home/mentor/ai_logs/`

## 🔧 Настройка

### Конфигурация системы
Файл: `/home/mentor/system_state.json`
```json
{
  "timestamp": "2024-01-01T00:00:00",
  "running": true,
  "health_status": "healthy",
  "system_status": {...},
  "ai_status": {...}
}
```

### Переменные окружения
```bash
# Ollama
export OLLAMA_HOST=0.0.0.0:11434
export OLLAMA_ORIGINS=*

# Python
export PYTHONPATH=/home/mentor
```

### Настройка nginx
Файл: `/etc/nginx/sites-available/cloud-agents`
```nginx
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🚨 Устранение неполадок

### Система не запускается
```bash
# Проверка логов
journalctl -u cloud-agent-system -n 50

# Проверка портов
netstat -tlnp | grep :8080

# Проверка процессов
ps aux | grep python
```

### AI модели не работают
```bash
# Проверка Ollama
systemctl status ollama
ollama list

# Перезапуск Ollama
systemctl restart ollama

# Проверка доступности
curl http://localhost:11434/api/tags
```

### Высокое использование ресурсов
```bash
# Мониторинг ресурсов
htop
df -h
free -h

# Очистка системы
sudo systemctl restart cloud-agent-system
```

## 📈 Масштабирование

### Горизонтальное масштабирование
- 🌐 **Load Balancer** для распределения нагрузки
- 🔄 **Кластер серверов** для высокой доступности
- 📊 **Мониторинг кластера** с Prometheus/Grafana

### Вертикальное масштабирование
- 💾 **Увеличение RAM** для больших моделей
- ⚡ **Более мощный CPU** для быстрой обработки
- 💿 **SSD диски** для быстрого доступа к данным

## 🔒 Безопасность

### Настройка файрвола
```bash
# Разрешить только необходимые порты
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### SSL сертификаты
```bash
# Установка Let's Encrypt
sudo apt install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d your-domain.com
```

## 📞 Поддержка

### Полезные команды
```bash
# Полный статус системы
curl http://localhost/api/system/status | jq

# Список агентов
curl http://localhost/api/agents | jq

# История чата
curl http://localhost/api/chat/history | jq

# Перезапуск всех сервисов
sudo systemctl restart cloud-agent-system nginx ollama
```

### Контакты
- 📧 **Логи системы**: `/home/mentor/cloud_system.log`
- 📊 **Мониторинг**: http://localhost/api/system/status
- 🤖 **AI статус**: http://localhost/api/agents

## 🎉 Заключение

Облачная система множественных AI-агентов готова к работе! Система:

- ✅ **Работает автономно** без участия пользователя
- ✅ **Автоматически восстанавливается** при сбоях
- ✅ **Масштабируется** под нагрузку
- ✅ **Мониторит** свое состояние
- ✅ **Создает резервные копии**
- ✅ **Оптимизирует** ресурсы

**Система готова к продуктивному использованию!**
