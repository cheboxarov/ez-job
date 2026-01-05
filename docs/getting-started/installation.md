# Установка и настройка окружения

Детальная инструкция по установке всех компонентов системы "Вкатился".

## Требования к системе

### Минимальные требования

- **ОС:** Linux, macOS, или Windows (с WSL2)
- **Python:** 3.11 или выше
- **Node.js:** 20.x или выше
- **PostgreSQL:** 16.x или выше
- **Docker:** 20.10+ (рекомендуется)
- **Docker Compose:** 2.0+ (рекомендуется)
- **RAM:** минимум 4GB
- **Диск:** минимум 10GB свободного места

### Рекомендуемые требования

- **RAM:** 8GB или больше
- **CPU:** 4 ядра или больше
- **Диск:** SSD с 20GB+ свободного места

## Установка зависимостей

### 1. Python и зависимости

#### Установка Python

**macOS:**
```bash
# Используя Homebrew
brew install python@3.11

# Или скачайте с python.org
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**Windows:**
Скачайте установщик с [python.org](https://www.python.org/downloads/)

#### Установка uv (менеджер пакетов)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Установка зависимостей backend

```bash
cd backend
uv pip install -r requirements.txt
```

Или используя стандартный pip:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Node.js и зависимости frontend

#### Установка Node.js

**macOS:**
```bash
brew install node@20
```

**Linux (Ubuntu/Debian):**
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**Windows:**
Скачайте установщик с [nodejs.org](https://nodejs.org/)

#### Установка зависимостей frontend

```bash
cd frontend
npm install
```

### 3. PostgreSQL

#### Вариант 1: Docker (рекомендуется)

```bash
docker run -d \
  --name postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=hh_db \
  -p 5432:5432 \
  postgres:16-alpine
```

#### Вариант 2: Локальная установка

**macOS:**
```bash
brew install postgresql@16
brew services start postgresql@16
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install postgresql-16
sudo systemctl start postgresql
```

**Windows:**
Скачайте установщик с [postgresql.org](https://www.postgresql.org/download/windows/)

### 4. Docker и Docker Compose

#### Установка Docker

**macOS:**
```bash
brew install --cask docker
```

**Linux (Ubuntu/Debian):**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

**Windows:**
Скачайте Docker Desktop с [docker.com](https://www.docker.com/products/docker-desktop)

#### Установка Docker Compose

Обычно устанавливается вместе с Docker Desktop. Для проверки:
```bash
docker compose version
```

## Настройка переменных окружения

### 1. Создание .env файла

Создайте файл `.env` в корне проекта:

```bash
cp .env.example .env  # Если есть пример
# или создайте вручную
```

### 2. Основные переменные окружения

#### Backend переменные

```env
# База данных
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=hh_db

# JWT секреты (сгенерируйте свои!)
JWT_SECRET=your-secret-key-here
RESET_PASSWORD_TOKEN_SECRET=your-reset-secret
VERIFICATION_TOKEN_SECRET=your-verification-secret

# OpenAI/BotHub
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://bothub.chat/api/v2/openai/v1
OPENAI_MODEL=gpt-oss-120b:exacto
OPENAI_MIN_CONFIDENCE=0.0

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_BOT_USERNAME=your_bot_username
TELEGRAM_LINK_TOKEN_TTL_SECONDS=600

# URLs
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000

# HeadHunter
HH_BASE_URL=https://api.hh.ru
HH_MAX_VACANCIES=50
HH_DEFAULT_PAGES_DEPTH=1

# Окружение
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

#### Frontend переменные

Создайте файл `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Генерация секретов

Для генерации безопасных секретов используйте:

```bash
# JWT секрет (32 байта в hex)
openssl rand -hex 32

# Или используйте Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Настройка IDE (опционально)

### VS Code

Рекомендуемые расширения:

- **Python** — поддержка Python
- **Pylance** — языковой сервер для Python
- **ESLint** — линтер для JavaScript/TypeScript
- **Prettier** — форматтер кода
- **Docker** — поддержка Docker

### PyCharm

1. Откройте проект
2. Настройте Python interpreter (File → Settings → Project → Python Interpreter)
3. Установите плагины для Docker и PostgreSQL

## Проверка установки

### 1. Проверка Python

```bash
python3 --version  # Должно быть 3.11+
uv --version  # Проверка uv
```

### 2. Проверка Node.js

```bash
node --version  # Должно быть v20.x+
npm --version
```

### 3. Проверка PostgreSQL

```bash
# Если через Docker
docker ps | grep postgres

# Если локально
psql --version
psql -U postgres -c "SELECT version();"
```

### 4. Проверка Docker

```bash
docker --version
docker compose version
```

### 5. Проверка зависимостей

```bash
# Backend
cd backend
python3 -c "import fastapi; print('FastAPI OK')"

# Frontend
cd frontend
npm list --depth=0
```

## Следующие шаги

После успешной установки:

1. Перейдите к [Первым шагам](first-steps.md) для запуска проекта
2. Изучите [Настройку среды разработки](development-setup.md)

## Проблемы при установке?

Если у вас возникли проблемы:

- Проверьте версии всех компонентов
- Убедитесь, что все зависимости установлены
- См. [Troubleshooting](../troubleshooting/common-issues.md)
