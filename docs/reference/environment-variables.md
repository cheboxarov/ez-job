# Переменные окружения

Полный справочник переменных окружения проекта "Вкатился".

## База данных

### DB_HOST

**Описание:** Хост базы данных PostgreSQL.

**Тип:** string

**Обязательность:** Нет (дефолт: `localhost`)

**Пример:**
```env
DB_HOST=postgres
```

### DB_PORT

**Описание:** Порт базы данных.

**Тип:** integer

**Обязательность:** Нет (дефолт: `5432`)

**Пример:**
```env
DB_PORT=5432
```

### DB_USER

**Описание:** Пользователь базы данных.

**Тип:** string

**Обязательность:** Нет (дефолт: `postgres`)

**Пример:**
```env
DB_USER=postgres
```

### DB_PASSWORD

**Описание:** Пароль базы данных.

**Тип:** string

**Обязательность:** Нет (дефолт: `postgres`)

**Пример:**
```env
DB_PASSWORD=your_secure_password
```

### DB_NAME

**Описание:** Имя базы данных.

**Тип:** string

**Обязательность:** Нет (дефолт: `hh_db`)

**Пример:**
```env
DB_NAME=hh_db
```

### DB_URL

**Описание:** Прямой URL подключения к БД (опционально, вместо отдельных параметров).

**Тип:** string

**Обязательность:** Нет

**Пример:**
```env
DB_URL=postgresql+asyncpg://user:password@host:5432/dbname
```

## JWT и аутентификация

### JWT_SECRET

**Описание:** Секретный ключ для JWT токенов.

**Тип:** string

**Обязательность:** Да (для продакшена)

**Пример:**
```env
JWT_SECRET=your-very-secure-secret-key-here
```

**Генерация:**
```bash
openssl rand -hex 32
```

### JWT_LIFETIME_SECONDS

**Описание:** Время жизни JWT токена в секундах.

**Тип:** integer

**Обязательность:** Нет (дефолт: `7200000`)

**Пример:**
```env
JWT_LIFETIME_SECONDS=7200000
```

### RESET_PASSWORD_TOKEN_SECRET

**Описание:** Секрет для токенов сброса пароля.

**Тип:** string

**Обязательность:** Нет (можно использовать JWT_SECRET)

**Пример:**
```env
RESET_PASSWORD_TOKEN_SECRET=your-reset-secret
```

### VERIFICATION_TOKEN_SECRET

**Описание:** Секрет для токенов верификации email.

**Тип:** string

**Обязательность:** Нет (можно использовать JWT_SECRET)

**Пример:**
```env
VERIFICATION_TOKEN_SECRET=your-verification-secret
```

## OpenAI/BotHub

### OPENAI_API_KEY

**Описание:** API ключ для доступа к LLM.

**Тип:** string

**Обязательность:** Да

**Пример:**
```env
OPENAI_API_KEY=your-api-key
```

### OPENAI_BASE_URL

**Описание:** Базовый URL для LLM API.

**Тип:** string

**Обязательность:** Нет (дефолт: `https://bothub.chat/api/v2/openai/v1`)

**Пример:**
```env
OPENAI_BASE_URL=https://bothub.chat/api/v2/openai/v1
```

### OPENAI_MODEL

**Описание:** Модель LLM для использования.

**Тип:** string

**Обязательность:** Нет (дефолт: `gpt-oss-120b:exacto`)

**Пример:**
```env
OPENAI_MODEL=gpt-oss-120b:exacto
```

### OPENAI_MIN_CONFIDENCE

**Описание:** Минимальный уровень уверенности для ответов LLM.

**Тип:** float

**Обязательность:** Нет (дефолт: `0.0`)

**Пример:**
```env
OPENAI_MIN_CONFIDENCE=0.0
```

## Telegram

### TELEGRAM_BOT_TOKEN

**Описание:** Токен Telegram бота.

**Тип:** string

**Обязательность:** Да (если используется Telegram)

**Пример:**
```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
```

### TELEGRAM_BOT_USERNAME

**Описание:** Username Telegram бота.

**Тип:** string

**Обязательность:** Нет

**Пример:**
```env
TELEGRAM_BOT_USERNAME=your_bot_username
```

### TELEGRAM_LINK_TOKEN_TTL_SECONDS

**Описание:** Время жизни токена для привязки Telegram (в секундах).

**Тип:** integer

**Обязательность:** Нет (дефолт: `600`)

**Пример:**
```env
TELEGRAM_LINK_TOKEN_TTL_SECONDS=600
```

## URLs

### FRONTEND_URL

**Описание:** URL фронтенд приложения.

**Тип:** string

**Обязательность:** Нет (дефолт: `http://localhost:5173`)

**Пример:**
```env
FRONTEND_URL=https://yourdomain.com
```

### BACKEND_URL

**Описание:** URL backend API.

**Тип:** string

**Обязательность:** Нет (дефолт: `http://localhost:8000`)

**Пример:**
```env
BACKEND_URL=https://api.yourdomain.com
```

## HeadHunter

### HH_BASE_URL

**Описание:** Базовый URL HeadHunter API.

**Тип:** string

**Обязательность:** Нет (дефолт: `https://api.hh.ru`)

**Пример:**
```env
HH_BASE_URL=https://api.hh.ru
```

### HH_MAX_VACANCIES

**Описание:** Максимальное количество вакансий для поиска.

**Тип:** integer

**Обязательность:** Нет (дефолт: `50`)

**Пример:**
```env
HH_MAX_VACANCIES=50
```

### HH_DEFAULT_PAGES_DEPTH

**Описание:** Глубина страниц по умолчанию при поиске.

**Тип:** integer

**Обязательность:** Нет (дефолт: `1`)

**Пример:**
```env
HH_DEFAULT_PAGES_DEPTH=1
```

## Окружение

### ENVIRONMENT

**Описание:** Окружение приложения (development/production).

**Тип:** string

**Обязательность:** Нет (дефолт: `development`)

**Пример:**
```env
ENVIRONMENT=production
```

### CORS_ORIGINS

**Описание:** Разрешенные origins для CORS (через запятую).

**Тип:** string

**Обязательность:** Нет (дефолт: `*` для разработки)

**Пример:**
```env
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Логирование

### LOG_LEVEL

**Описание:** Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL).

**Тип:** string

**Обязательность:** Нет (дефолт: `INFO`)

**Пример:**
```env
LOG_LEVEL=INFO
```

## ЮКасса (если интегрирована)

### YOOKASSA_SHOP_ID

**Описание:** ID магазина в ЮКассе.

**Тип:** string

**Обязательность:** Да (если используется)

**Пример:**
```env
YOOKASSA_SHOP_ID=123456
```

### YOOKASSA_SECRET_KEY

**Описание:** Секретный ключ ЮКассы.

**Тип:** string

**Обязательность:** Да (если используется)

**Пример:**
```env
YOOKASSA_SECRET_KEY=your-secret-key
```

### YOOKASSA_TEST_MODE

**Описание:** Тестовый режим ЮКассы.

**Тип:** boolean

**Обязательность:** Нет (дефолт: `true`)

**Пример:**
```env
YOOKASSA_TEST_MODE=false
```

## Примеры конфигураций

### Development

```env
ENVIRONMENT=development
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=hh_db
JWT_SECRET=dev-secret-key
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
LOG_LEVEL=DEBUG
```

### Production

```env
ENVIRONMENT=production
DB_HOST=postgres
DB_PORT=5432
DB_USER=your_db_user
DB_PASSWORD=your_secure_password
DB_NAME=hh_db
JWT_SECRET=your-production-secret-key
FRONTEND_URL=https://yourdomain.com
BACKEND_URL=https://api.yourdomain.com
CORS_ORIGINS=https://yourdomain.com
LOG_LEVEL=INFO
```

## Связанные разделы

- [Deployment: Настройка окружения](../deployment/environment-setup.md) — настройка для деплоя
- [Getting Started: Установка](../getting-started/installation.md) — настройка для разработки
