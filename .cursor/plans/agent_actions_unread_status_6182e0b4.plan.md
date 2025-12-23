---
name: Agent Actions Unread Status
overview: Implement read/unread status for Agent Actions, including database schema changes, backend API endpoints for counting and resetting unread actions, and frontend integration with a badge in the navigation menu.
todos:
  - id: migration
    content: Создать миграцию Alembic для поля is_read
    status: completed
  - id: backend-models
    content: Обновить AgentAction entity и model
    status: completed
    dependencies:
      - migration
  - id: backend-interfaces
    content: Обновить интерфейсы репозитория и сервиса
    status: completed
    dependencies:
      - backend-models
  - id: backend-repo
    content: Реализовать методы репозитория (get_unread_count, mark_all_as_read)
    status: completed
    dependencies:
      - backend-interfaces
  - id: backend-service-api
    content: Реализовать методы сервиса и добавить API endpoints
    status: completed
    dependencies:
      - backend-repo
  - id: frontend-store-api
    content: Создать agentActionsStore и обновить API клиент на фронтенде
    status: in_progress
  - id: frontend-ui
    content: Добавить бейдж в MainLayout и логику прочтения в EventsPage
    status: completed
    dependencies:
      - frontend-store-api
---

