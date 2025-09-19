# 🤖 JARVIS - Руководство пользователя
# Как пользоваться автономной системой JARVIS

## 🚀 Быстрый старт

### 1. Откройте веб-интерфейс
```
http://localhost:8080
```

### 2. Что вы увидите
- **Панель статистики** - производительность, агенты, задачи в реальном времени
- **Кнопки управления** - для всех основных функций
- **Логи системы** - что происходит в реальном времени
- **Статус агентов** - кто работает и как

## 🛒 Работа с Wildberries

### Получение данных
- **📦 Карточки товаров** - нажмите кнопку "Карточки товаров"
- **📋 Заказы** - нажмите кнопку "Заказы" 
- **📊 Проверка остатков** - автоматическая проверка складских остатков

### API команды
```bash
# Карточки товаров
curl http://localhost:8080/api/wb/cards

# Заказы за неделю  
curl http://localhost:8080/api/wb/orders

# Проверка остатков
curl -X POST -H "Content-Type: application/json" \
  -d '{"type":"wb_stock_check"}' \
  http://localhost:8080/api/automation/execute
```

## ✍️ Генерация контента

### Через веб-интерфейс
- **📝 Описание товара** - генерирует описание для смартфона
- **🏷️ Название** - создает название для ноутбука
- **🔍 Ключевые слова** - генерирует SEO слова для одежды

### API команды
```bash
# Описание товара
curl -X POST -H "Content-Type: application/json" \
  -d '{"type":"description","topic":"телефон","length":"medium"}' \
  http://localhost:8080/api/content/generate

# Название товара
curl -X POST -H "Content-Type: application/json" \
  -d '{"type":"title","topic":"кроссовки"}' \
  http://localhost:8080/api/content/generate

# Ключевые слова
curl -X POST -H "Content-Type: application/json" \
  -d '{"type":"keywords","topic":"платье"}' \
  http://localhost:8080/api/content/generate
```

## 🤖 Управление агентами

### Доступные агенты
- **Coordinator** - координирует задачи между агентами
- **Analyzer** - анализирует данные и генерирует инсайты
- **Optimizer** - оптимизирует производительность системы

### Команды
```bash
# Статус агентов
curl http://localhost:8080/api/agents/status

# Координация агентов
curl -X POST http://localhost:8080/api/agents/coordinate

# Анализ данных
curl -X POST http://localhost:8080/api/data/analyze
```

## 📊 Бизнес-автоматизация

### Доступные автоматизации
- **wb_stock_check** - проверка остатков WB
- **wb_reports** - генерация отчетов WB
- **sales_analysis** - анализ продаж
- **content_generation** - массовая генерация контента
- **price_monitoring** - мониторинг цен

### Примеры использования
```bash
# Анализ продаж
curl -X POST -H "Content-Type: application/json" \
  -d '{"type":"sales_analysis"}' \
  http://localhost:8080/api/automation/execute

# Генерация отчетов
curl -X POST -H "Content-Type: application/json" \
  -d '{"type":"wb_reports"}' \
  http://localhost:8080/api/automation/execute

# Мониторинг цен
curl -X POST -H "Content-Type: application/json" \
  -d '{"type":"price_monitoring"}' \
  http://localhost:8080/api/automation/execute
```

## 👁️ Визуальный анализ

### Что анализируется
- **HTML структура** - количество элементов, семантика
- **CSS стили** - современность, адаптивность
- **JavaScript** - функциональность, производительность
- **Доступность** - WCAG compliance
- **SEO** - meta теги, заголовки
- **Производительность** - время загрузки

### Команды
```bash
# Статус анализа
curl http://localhost:8080/api/vision/status

# Детальный анализ
curl http://localhost:8080/api/vision/detailed
```

## 🧠 Система обучения

### Что записывается
- Выполнение задач
- Вызовы API
- Генерация контента
- Автоматизация бизнеса
- Визуальный анализ

### Команды
```bash
# Статистика обучения
curl http://localhost:8080/api/learning/status

# Запись события
curl -X POST -H "Content-Type: application/json" \
  -d '{"event_type":"test","context":{"user":"manual"},"outcome":{"result":"ok"},"success":true}' \
  http://localhost:8080/api/learning/record
```

## 🎯 Полезные команды

### Создание задач
```bash
# Самоулучшение
curl -X POST http://localhost:8080/api/self-improvement/trigger

# Оптимизация производительности
curl -X POST -H "Content-Type: application/json" \
  -d '{"type":"performance_optimization","priority":8}' \
  http://localhost:8080/api/tasks

# Улучшение UI
curl -X POST -H "Content-Type: application/json" \
  -d '{"type":"ui_improvement","priority":6}' \
  http://localhost:8080/api/tasks
```

### Мониторинг системы
```bash
# Общий статус
curl http://localhost:8080/api/status

# Все статусы сразу
curl http://localhost:8080/api/status && \
curl http://localhost:8080/api/agents/status && \
curl http://localhost:8080/api/learning/status
```

## 🔄 Автоматические процессы

### Что происходит автоматически
- **Каждые 5 секунд:** Визуальный анализ интерфейса
- **Каждые 10 секунд:** Генерация новых задач
- **Каждые 2 минуты:** Анализ паттернов обучения
- **Непрерывно:** Выполнение задач агентами
- **При каждом действии:** Запись в систему обучения

### Автономное поведение
- Система сама создает задачи оптимизации
- Агенты улучшают свою производительность
- Обнаруживаются проблемы UI и предлагаются решения
- Записываются все действия для обучения

## 🎯 Практические примеры

### Генерация описаний для 10 товаров
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"type":"content_generation","parameters":{"count":10,"type":"description","topics":["смартфон","ноутбук","наушники"]}}' \
  http://localhost:8080/api/automation/execute
```

### Полная проверка WB
```bash
# Сначала карточки
curl http://localhost:8080/api/wb/cards

# Потом заказы
curl http://localhost:8080/api/wb/orders

# Затем остатки
curl -X POST -H "Content-Type: application/json" \
  -d '{"type":"wb_stock_check"}' \
  http://localhost:8080/api/automation/execute
```

### Комплексный анализ
```bash
# Анализ данных
curl -X POST http://localhost:8080/api/data/analyze

# Анализ продаж
curl -X POST -H "Content-Type: application/json" \
  -d '{"type":"sales_analysis"}' \
  http://localhost:8080/api/automation/execute

# Координация агентов
curl -X POST http://localhost:8080/api/agents/coordinate
```

## 🎉 Готово к использованию!

**Система JARVIS полностью функциональна и готова к реальному использованию:**

- ✅ Все API работают
- ✅ Веб-интерфейс доступен
- ✅ Автоматизация активна
- ✅ Агенты координируются
- ✅ Генерация контента работает
- ✅ Система обучается

**Начинайте пользоваться прямо сейчас: http://localhost:8080**