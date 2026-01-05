# Настройка окружения

Подготовка окружения для деплоя проекта "Вкатился".

## Установка Docker и Docker Compose

### Ubuntu/Debian

```bash
# Обновление пакетов
sudo apt update
sudo apt upgrade -y

# Установка зависимостей
sudo apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Добавление официального GPG ключа Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Добавление репозитория Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установка Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Проверка установки
docker --version
docker compose version
```

### macOS

```bash
# Используя Homebrew
brew install --cask docker
```

Затем откройте Docker Desktop и дождитесь запуска.

## Настройка переменных окружения для продакшена

### Создание .env файла

Создайте файл `.env` в корне проекта:

```bash
cp .env.example .env
nano .env  # или используйте ваш редактор
```

### Обязательные переменные

```env
# База данных
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=hh_db
DB_PORT=5432

# JWT секреты (ОБЯЗАТЕЛЬНО сгенерируйте свои!)
JWT_SECRET=your-very-secure-secret-key-here
RESET_PASSWORD_TOKEN_SECRET=your-reset-secret
VERIFICATION_TOKEN_SECRET=your-verification-secret

# OpenAI/BotHub
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://bothub.chat/api/v2/openai/v1
OPENAI_MODEL=gpt-oss-120b:exacto

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_BOT_USERNAME=your_bot_username

# URLs (замените на ваши домены)
FRONTEND_URL=https://yourdomain.com
BACKEND_URL=https://api.yourdomain.com

# Окружение
ENVIRONMENT=production
CORS_ORIGINS=https://yourdomain.com

# ЮКасса (если интегрирована)
YOOKASSA_SHOP_ID=your-shop-id
YOOKASSA_SECRET_KEY=your-secret-key
YOOKASSA_TEST_MODE=false
```

### Генерация секретов

```bash
# JWT секрет
openssl rand -hex 32

# Или через Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Настройка БД

### Создание пользователя БД

```bash
# Подключение к PostgreSQL
sudo -u postgres psql

# Создание пользователя и БД
CREATE USER your_db_user WITH PASSWORD 'your_secure_password';
CREATE DATABASE hh_db OWNER your_db_user;
GRANT ALL PRIVILEGES ON DATABASE hh_db TO your_db_user;
\q
```

## Настройка внешних сервисов

### HeadHunter

1. Зарегистрируйте приложение в HeadHunter
2. Получите Client ID и Client Secret
3. Настройте redirect URI

### Telegram Bot

1. Создайте бота через [@BotFather](https://t.me/botfather)
2. Получите токен бота
3. Настройте webhook (если используется)

### ЮКасса

1. Зарегистрируйтесь в [ЮКассе](https://yookassa.ru/)
2. Получите Shop ID и Secret Key
3. Настройте webhook URL в личном кабинете

## Проверка настроек

```bash
# Проверка переменных окружения
cat .env | grep -v "^#" | grep -v "^$"

# Проверка подключения к БД
docker-compose exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT version();"
```

## Следующие шаги

1. [Деплой через Docker](docker-deployment.md)
2. [Настройка SSL](ssl-certificates.md)
