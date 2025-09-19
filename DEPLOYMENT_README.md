# Autonomous JARVIS Cloud Deployment
# Развертывание автономной системы JARVIS в облаке

## 🚀 Быстрый старт

### Локальное развертывание с Docker

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd autonomous-jarvis
```

2. Запустите систему:
```bash
docker-compose up -d
```

3. Откройте браузер: http://localhost:8080

### Развертывание на сервере

1. Скопируйте файлы на сервер:
```bash
scp -r * user@server:/opt/autonomous-jarvis/
```

2. Запустите скрипт развертывания:
```bash
sudo ./deploy.sh
```

### AWS развертывание с Terraform

1. Настройте AWS CLI:
```bash
aws configure
```

2. Инициализируйте Terraform:
```bash
terraform init
```

3. Создайте инфраструктуру:
```bash
terraform plan
terraform apply
```

## 🛠️ Конфигурация

### Переменные окружения

- `JARVIS_ENV`: Окружение (production/development)
- `JARVIS_LOG_LEVEL`: Уровень логирования (INFO/DEBUG)

### Порты

- 8080: Основное приложение JARVIS
- 80: HTTP (перенаправление на HTTPS)
- 443: HTTPS

## 📊 Мониторинг

### Проверка статуса
```bash
curl http://localhost:8080/api/status
```

### Просмотр логов
```bash
docker-compose logs -f jarvis
```

### Мониторинг ресурсов
```bash
./monitor.sh
```

## 🔧 Управление

### Перезапуск системы
```bash
systemctl restart jarvis
# или
docker-compose restart
```

### Обновление
```bash
git pull
docker-compose build --no-cache
docker-compose up -d
```

### Остановка
```bash
systemctl stop jarvis
# или
docker-compose down
```

## 🎯 Особенности

### Автономная работа
- ✅ Непрерывная работа 24/7
- ✅ Автоматическое восстановление после сбоев
- ✅ Самоисцеление системы
- ✅ Автоматические обновления

### Визуальный интеллект
- ✅ Анализ интерфейса в реальном времени
- ✅ Автоматическое обнаружение проблем
- ✅ Генерация предложений по улучшению
- ✅ Мониторинг пользовательского опыта

### Безопасность
- ✅ HTTPS шифрование
- ✅ Файрвол настроен
- ✅ Безопасные заголовки
- ✅ Регулярные обновления безопасности

## 📱 API Endpoints

### Основные
- `GET /`: Веб-интерфейс
- `GET /api/status`: Статус системы
- `GET /api/vision/status`: Статус визуального анализа

### Управление
- `POST /api/tasks`: Создание задачи
- `POST /api/self-improvement/trigger`: Запуск самоулучшения

### WebSocket
- `WS /ws`: Обновления в реальном времени

## 🚨 Устранение неполадок

### Система не запускается
1. Проверьте логи: `docker-compose logs jarvis`
2. Проверьте порты: `netstat -tlnp | grep 8080`
3. Проверьте Docker: `systemctl status docker`

### Высокая загрузка
1. Проверьте ресурсы: `./monitor.sh`
2. Перезапустите систему: `systemctl restart jarvis`
3. Проверьте логи на ошибки

### Проблемы с SSL
1. Пересоздайте сертификаты: `./create_ssl.sh`
2. Проверьте конфигурацию nginx: `nginx -t`
3. Перезапустите nginx: `systemctl restart nginx`

## 📞 Поддержка

Для получения поддержки:
1. Проверьте логи системы
2. Запустите диагностику: `./monitor.sh`
3. Создайте issue в репозитории

## 🎉 Дополнительные функции

### Telegram уведомления
1. Создайте бота: @BotFather
2. Получите токен и chat_id
3. Обновите monitor.sh с вашими данными

### Автоматические резервные копии
```bash
# Добавьте в crontab
0 4 * * * /opt/autonomous-jarvis/backup.sh
```

### Масштабирование
Для горизонтального масштабирования используйте Kubernetes:
```bash
kubectl apply -f k8s-deployment.yaml
```
