# Настройка среды разработки

Оптимизация рабочего окружения для эффективной разработки.

## Настройка IDE

### VS Code

#### Рекомендуемые расширения

Установите следующие расширения:

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next",
    "ms-azuretools.vscode-docker",
    "ms-python.black-formatter",
    "charliermarsh.ruff"
  ]
}
```

#### Настройки workspace

Создайте `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.organizeImports": true
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

#### Launch configuration для отладки

Создайте `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/backend/main.py",
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      }
    },
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      }
    }
  ]
}
```

### PyCharm

1. **Откройте проект:**
   - File → Open → выберите корневую директорию проекта

2. **Настройте Python interpreter:**
   - File → Settings → Project → Python Interpreter
   - Выберите существующий venv или создайте новый

3. **Настройте структуру проекта:**
   - File → Settings → Project Structure
   - Отметьте `backend` как Sources Root
   - Отметьте `frontend` как Sources Root

4. **Настройте Docker:**
   - File → Settings → Build, Execution, Deployment → Docker
   - Настройте подключение к Docker

## Настройка линтеров и форматтеров

### Python

#### Black (форматтер)

Установка:
```bash
pip install black
```

Использование:
```bash
# Форматирование всех файлов
black backend/

# Проверка без изменений
black --check backend/
```

#### Ruff (линтер)

Установка:
```bash
pip install ruff
```

Использование:
```bash
# Проверка
ruff check backend/

# Автоисправление
ruff check --fix backend/
```

#### Настройка pre-commit

Создайте `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.8
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.56.0
    hooks:
      - id: eslint
        files: \.(js|jsx|ts|tsx)$
        additional_dependencies:
          - eslint@8.56.0
          - '@typescript-eslint/parser@6.19.0'
          - '@typescript-eslint/eslint-plugin@6.19.0'
```

Установка:
```bash
pip install pre-commit
pre-commit install
```

### TypeScript/JavaScript

#### ESLint

Конфигурация уже есть в `frontend/eslint.config.js`.

Запуск:
```bash
cd frontend
npm run lint
```

#### Prettier

Создайте `frontend/.prettierrc`:

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": false,
  "printWidth": 100,
  "tabWidth": 2
}
```

## Настройка отладки

### Backend (Python)

#### VS Code

Используйте конфигурацию из `.vscode/launch.json` (см. выше).

#### PyCharm

1. Создайте Run Configuration:
   - Run → Edit Configurations
   - Добавьте Python configuration
   - Script path: `backend/main.py`
   - Working directory: `backend/`

2. Установите breakpoints и запустите в режиме отладки

#### Отладка через pdb

```python
import pdb; pdb.set_trace()  # Точка останова
```

### Frontend (React)

#### React DevTools

Установите расширение для браузера:
- [Chrome](https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi)
- [Firefox](https://addons.mozilla.org/en-US/firefox/addon/react-devtools/)

#### VS Code Debugger для Chrome

Добавьте в `.vscode/launch.json`:

```json
{
  "name": "Chrome: Frontend",
  "type": "chrome",
  "request": "launch",
  "url": "http://localhost:5173",
  "webRoot": "${workspaceFolder}/frontend"
}
```

## Полезные инструменты

### Database

#### pgAdmin

Установка:
```bash
# macOS
brew install --cask pgadmin4

# Linux
sudo apt install pgadmin4
```

#### DBeaver

Скачайте с [dbeaver.io](https://dbeaver.io/)

### API Testing

#### Postman

Скачайте с [postman.com](https://www.postman.com/)

Импортируйте OpenAPI схему:
- URL: `http://localhost:8000/openapi.json`

#### Insomnia

Скачайте с [insomnia.rest](https://insomnia.rest/)

### Docker

#### Docker Desktop

Включает GUI для управления контейнерами.

### Git

#### GitKraken / SourceTree

GUI клиенты для Git.

## Настройка тестового окружения

### Backend тесты

Создайте `backend/tests/` и настройте pytest:

```bash
pip install pytest pytest-asyncio pytest-cov
```

Создайте `backend/pytest.ini`:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
```

### Frontend тесты

Установите зависимости:

```bash
cd frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom vitest
```

## Полезные команды

### Backend

```bash
# Форматирование кода
black backend/

# Линтинг
ruff check backend/

# Запуск тестов
pytest backend/tests/

# Применение миграций
cd backend && alembic upgrade head
```

### Frontend

```bash
# Линтинг
cd frontend && npm run lint

# Форматирование
cd frontend && npx prettier --write src/

# Запуск тестов
cd frontend && npm test
```

## Следующие шаги

После настройки среды:

1. Изучите [Процесс разработки](../development/README.md)
2. Прочитайте [Стиль кода](../development/code-style.md)
3. Ознакомьтесь с [Git workflow](../development/git-workflow.md)
