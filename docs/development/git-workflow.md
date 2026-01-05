# Git workflow

Рабочий процесс с Git в проекте "Вкатился".

## Структура веток

- **main** — продакшн код
- **develop** — разработка (если используется)
- **feature/** — новые фичи
- **fix/** — исправления багов
- **hotfix/** — критические исправления

## Процесс работы

### 1. Создание ветки

```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

### 2. Коммиты

Делайте частые, логичные коммиты:

```bash
git add .
git commit -m "feat: add resume creation endpoint"
```

### 3. Push в удаленный репозиторий

```bash
git push origin feature/your-feature-name
```

### 4. Pull Request

1. Создайте PR на GitHub/GitLab
2. Опишите изменения
3. Дождитесь code review
4. Внесите исправления при необходимости

### 5. Мерж

После одобрения PR выполните мерж в main.

## Соглашения о коммитах

Используйте [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Типы

- `feat` — новая функциональность
- `fix` — исправление бага
- `docs` — изменения в документации
- `style` — форматирование кода
- `refactor` — рефакторинг
- `test` — добавление тестов
- `chore` — обновление зависимостей и т.д.

### Примеры

```
feat(resumes): add resume creation endpoint

fix(auth): fix token expiration handling

docs: update API documentation

refactor(domain): simplify use case logic
```

## Связанные разделы

- [Добавление фич](adding-features.md) — процесс разработки
