# Frontend - AutoOffer

Фронтенд приложение для работы с вакансиями на React + TypeScript + Ant Design.

## Технологии

- React 19
- TypeScript
- Vite
- Ant Design
- React Router
- Zustand
- Axios

## Установка

```bash
npm install
```

## Настройка

Создайте файл `.env` в корне проекта (или используйте переменные окружения):

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Запуск

```bash
npm run dev
```

Приложение будет доступно по адресу http://localhost:5173

## Сборка

```bash
npm run build
```

## Структура проекта

```
src/
├── api/              # API клиент и функции
├── components/       # React компоненты
│   └── Layout/      # Layout компоненты
├── pages/           # Страницы приложения
├── stores/          # Zustand stores
├── types/           # TypeScript типы
└── theme/           # Настройки темы Ant Design
```
