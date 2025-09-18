# 🆓 AI Manager - Настройка бесплатных AI провайдеров

## 🎯 Обзор

AI Manager теперь поддерживает **бесплатные AI провайдеры**! Больше не нужны платные API ключи OpenAI - система работает с локальными и бесплатными моделями.

## 🔌 Поддерживаемые провайдеры

### 1. 🤖 Ollama (Рекомендуется)
**Локальные модели на вашем сервере**

- ✅ **Полностью бесплатно**
- ✅ **Приватность данных**
- ✅ **Быстрая работа**
- ✅ **Много моделей**

**Популярные модели:**
- `llama2:7b` - универсальная модель
- `codellama:7b` - для генерации кода
- `mistral:7b` - быстрая и качественная
- `orca-mini:3b` - легкая модель

### 2. 🌐 Hugging Face (API)
**Бесплатные модели через API**

- ✅ **Бесплатно** (с ограничениями)
- ✅ **Много моделей**
- ✅ **Простая настройка**

**Популярные модели:**
- `microsoft/DialoGPT-medium`
- `gpt2-medium`
- `distilgpt2`

### 3. 🏠 Local Provider
**Простая имитация для демонстрации**

- ✅ **Всегда работает**
- ✅ **Не требует интернета**
- ✅ **Быстрый отклик**

## 🚀 Быстрая установка

### Вариант 1: Docker (Рекомендуется)

```bash
# Клонируем проект
git clone <repository>
cd ai_manager

# Запускаем одной командой
./deploy.sh
```

### Вариант 2: Локальная установка

```bash
# 1. Устанавливаем Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Запускаем Ollama
ollama serve

# 3. Загружаем модель
ollama pull llama2:7b

# 4. Устанавливаем зависимости
pip install -r requirements.txt

# 5. Запускаем AI Manager
python start_server.py
```

## ⚙️ Конфигурация

### Файл .env

```env
# Ollama настройки
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama2:7b

# Hugging Face (опционально)
HUGGINGFACE_TOKEN=your_token_here
HUGGINGFACE_MODEL=microsoft/DialoGPT-medium

# OpenAI (опционально, если есть)
OPENAI_API_KEY=your_key_here
```

### Приоритет провайдеров

Система автоматически выбирает лучший доступный провайдер:

1. **Ollama** (если доступен)
2. **Hugging Face** (если настроен)
3. **Local Provider** (fallback)

## 🧪 Тестирование

### Демонстрация бесплатных провайдеров

```bash
python demo_free.py
```

### Проверка статуса провайдеров

```bash
curl http://localhost:8000/api/stats
```

## 📊 Сравнение провайдеров

| Провайдер | Скорость | Качество | Приватность | Стоимость |
|-----------|----------|----------|-------------|-----------|
| Ollama | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 🆓 |
| Hugging Face | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | 🆓 |
| OpenAI | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | 💰 |
| Local | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | 🆓 |

## 🛠️ Устранение неполадок

### Ollama не запускается

```bash
# Проверяем статус
ollama list

# Перезапускаем
sudo systemctl restart ollama

# Проверяем логи
journalctl -u ollama -f
```

### Hugging Face API ошибки

```bash
# Проверяем токен
curl -H "Authorization: Bearer YOUR_TOKEN" https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium
```

### Низкая производительность

```bash
# Используем более легкую модель Ollama
ollama pull orca-mini:3b

# Или настраиваем в .env
OLLAMA_MODEL=orca-mini:3b
```

## 🎯 Рекомендации

### Для разработки
- Используйте `orca-mini:3b` - быстрая и легкая
- Настройте Local Provider как fallback

### Для продакшена
- Используйте `llama2:7b` или `mistral:7b`
- Настройте Redis для кэширования
- Используйте PostgreSQL вместо SQLite

### Для высокой нагрузки
- Настройте несколько экземпляров Ollama
- Используйте балансировщик нагрузки
- Настройте мониторинг производительности

## 🔧 Дополнительные настройки

### Оптимизация Ollama

```bash
# Настройки в ~/.ollama/config.json
{
  "gpu_layers": 35,
  "num_ctx": 2048,
  "num_thread": 8
}
```

### Мониторинг ресурсов

```bash
# Проверяем использование GPU
nvidia-smi

# Проверяем память
free -h

# Проверяем CPU
htop
```

## 🎉 Готово!

Теперь у вас есть полностью бесплатная система AI агентов:

- 🆓 **Без платных API**
- 🚀 **Быстрая работа**
- 🔒 **Приватность данных**
- 📈 **Масштабируемость**

**Запускайте и наслаждайтесь!**

```bash
./deploy.sh
# Откройте http://localhost:8000
```


