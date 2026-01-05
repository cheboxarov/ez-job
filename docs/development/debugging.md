# Отладка

Инструменты и техники отладки приложения.

## Инструменты отладки

### Python debugger

#### VS Code

Используйте конфигурацию из `.vscode/launch.json`:

```json
{
  "name": "Python: FastAPI",
  "type": "python",
  "request": "launch",
  "program": "${workspaceFolder}/backend/main.py"
}
```

#### PyCharm

1. Создайте Run Configuration
2. Установите breakpoints
3. Запустите в режиме отладки

#### pdb

```python
import pdb; pdb.set_trace()  # Точка останова
```

### React DevTools

Установите расширение для браузера:
- [Chrome](https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi)
- [Firefox](https://addons.mozilla.org/en-US/firefox/addon/react-devtools/)

### Логирование

Используйте loguru для логирования:

```python
from loguru import logger

logger.info("Processing request")
logger.error("Error occurred", exc_info=True)
```

## Типичные проблемы

### Backend не запускается

1. Проверьте логи: `docker-compose logs backend`
2. Проверьте переменные окружения
3. Проверьте подключение к БД

### Frontend не подключается к API

1. Проверьте `VITE_API_BASE_URL`
2. Проверьте CORS настройки
3. Проверьте сетевые запросы в DevTools

## Профилирование

### Python

```python
import cProfile

profiler = cProfile.Profile()
profiler.enable()
# Ваш код
profiler.disable()
profiler.print_stats()
```

## Связанные разделы

- [Troubleshooting](../troubleshooting/common-issues.md) — решение проблем
