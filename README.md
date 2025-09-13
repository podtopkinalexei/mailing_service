# 🚀 Сервис управления рассылками

Django-приложение для управления email-рассылками с расширенной статистикой, аутентификацией пользователей и системой ролей.

## ✨ Особенности

- **Управление рассылками** - создание, редактирование, отправка и мониторинг email-рассылкок
- **Система клиентов** - управление базой получателей рассылок
- **Детальная статистика** - отслеживание успешных и неудачных отправок
- **Аутентификация** - регистрация, вход, управление профилем
- **Ролевая модель** - разделение прав между пользователями и менеджерами
- **Кэширование** - повышение производительности через Redis кэширование
- **Адаптивный дизайн** - современный интерфейс на Bootstrap 5

## 🛠 Технологический стек

- **Backend**: Django 4.2+
- **Frontend**: Bootstrap 5, HTML5, CSS3
- **База данных**: PostgreSQL / SQLite
- **Кэширование**: Redis
- **Email**: SMTP (Gmail, Yandex, etc.)
- **Деплой**: Docker-ready

## 📦 Установка и запуск

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd mailing_service
```

### 2. Создание виртуального окружения

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка окружения

Создайте файл `.env` в корневой директории:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
REDIS_URL=redis://localhost:6379/1
```

### 5. Миграции и суперпользователь

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py create_managers_group
```

### 6. Запуск сервера

```bash
python manage.py runserver
```

Приложение будет доступно по адресу: http://localhost:8000

## 🏗 Архитектура проекта

```
mailing_service/
├── mailing/          # Основное приложение рассылок
│   ├── models.py     # Модели: Клиент, Сообщение, Рассылка, Попытка
│   ├── views.py      # CBV для всех операций CRUD
│   ├── services.py   # Логика отправки email
│   ├── cache_utils.py # Утилиты кэширования
│   └── management/   # Кастомные команды
├── users/            # Приложение пользователей
│   ├── models.py     # Кастомная модель User
│   ├── forms.py      # Формы регистрации и профиля
│   └── views.py      # Аутентификация и профиль
├── templates/        # Шаблоны HTML
├── static/           # Статические файлы
└── media/            # Загружаемые файлы
```

## 📋 Функциональность

### 🔐 Аутентификация и пользователи
- Регистрация с подтверждением email
- Вход/выход из системы
- Редактирование профиля с аватаром
- Восстановление пароля

### 📧 Управление рассылками
- **Клиенты**: CRUD операции с получателями
- **Сообщения**: Создание шаблонов писем
- **Рассылки**: 
  - Настройка времени отправки
  - Выбор получателей и сообщений
  - Статусы: Создана, Запущена, Завершена
- **Попытки отправки**: 
  - Логирование каждой попытки
  - Статусы: Успешно/Неуспешно
  - Ответы почтового сервера

### 📊 Статистика и отчетность
- Общее количество рассылок
- Активные рассылки
- Уникальные клиенты
- Процент успешных отправок
- Детальная статистика по пользователям

### 👮‍♂️ Ролевая модель
**Обычный пользователь:**
- Управление своими рассылками и клиентами
- Просмотр статистики своих рассылок

**Менеджер:**
- Просмотр всех рассылок и клиентов
- Блокировка пользователей
- Отключение рассылок
- Просмотр системной статистики

## ⚙️ Настройка Email

### Gmail SMTP
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Пароль приложения
```

### Yandex SMTP
```python
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
```

## 🚀 Производительность

### Кэширование
- **Redis**: Кэширование страниц и данных
- **Фрагментарное кэширование**: Кэширование блоков шаблонов
- **Автоинвалидация**: Автоматическая очистка кэша при изменениях

### Оптимизации
- Оптимизированные SQL-запросы
- Пагинация списков
- Селективный prefetch_related

## 🐳 Docker развертывание

```bash
# Сборка и запуск
docker-compose up -d --build

# Миграции
docker-compose exec web python manage.py migrate

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser
```

## 📊 API Endpoints

### Получение статуса рассылки
```http
GET /mailing/api/mailings/{id}/status/
```

Response:
```json
{
    "id": 1,
    "status": "Запущена",
    "total_attempts": 150,
    "successful_attempts": 145,
    "failed_attempts": 5,
    "success_rate": 96.67,
    "last_attempt": "2024-01-15T10:30:45.123456Z"
}
```

## 🎯 Кастомные команды

```bash
# Создание группы менеджеров
python manage.py create_managers_group

# Тестирование email
python manage.py test_email

```

## 🔧 Настройка для Production

1. **Безопасность**:
   ```python
   DEBUG = False
   SECRET_KEY = os.environ['SECRET_KEY']
   ALLOWED_HOSTS = ['your-domain.com']
   CSRF_TRUSTED_ORIGINS = ['https://your-domain.com']
   ```

2. **База данных**:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'mailing_db',
           'USER': 'user',
           'PASSWORD': 'password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

3. **Статические файлы**:
   ```bash
   python manage.py collectstatic
   ```


## 📈 Мониторинг

Приложение поддерживает интеграцию с:
- **Sentry** для отслеживания ошибок
- **Prometheus** для метрик производительности
- **Celery** для асинхронных задач

## 🤝 Разработка

### Code Style
```bash
# Проверка стиля
flake8 .
black --check .

# Автоформатирование
black .
```

### Миграции
```bash
# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate
```

## 📄 Лицензия

MIT License - смотрите файл [LICENSE](LICENSE) для деталей.

## 👥 Разработчики

- Подтопкин Алексей
- Контакты: podtopkinalexei@gmail.com

## 🐛 Поддержка

При обнаружении багов или вопросов создавайте issue в репозитории проекта.

---

**⭐ Если проект вам понравился, поставьте звезду на GitHub!**

