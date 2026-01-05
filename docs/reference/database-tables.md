# Таблицы базы данных

Справочник по структуре таблиц базы данных.

## users

**Назначение:** Пользователи системы.

**Поля:**
- `id` (UUID, PK)
- `email` (VARCHAR, UNIQUE)
- `hashed_password` (VARCHAR)
- `is_active` (BOOLEAN)
- `is_superuser` (BOOLEAN)
- `is_verified` (BOOLEAN)
- `resume_id` (VARCHAR)
- `area` (VARCHAR)
- `salary` (VARCHAR)
- `hh_user_id` (VARCHAR)
- `hh_headers` (JSONB)
- `hh_cookies` (JSONB)
- `hh_cookies_updated_at` (TIMESTAMP)
- `phone` (VARCHAR)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

**Индексы:**
- `ix_users_email` на `email`

## resumes

**Назначение:** Резюме пользователей.

**Поля:**
- `id` (UUID, PK)
- `user_id` (UUID, FK → users.id)
- `content` (TEXT)
- `user_parameters` (TEXT)
- `external_id` (VARCHAR)
- `headhunter_hash` (VARCHAR)
- `is_auto_reply` (BOOLEAN)
- `autolike_threshold` (INTEGER)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

**Индексы:**
- `ix_resumes_user_id` на `user_id`

## subscription_plans

**Назначение:** Тарифные планы подписки.

**Поля:**
- `id` (UUID, PK)
- `name` (VARCHAR, UNIQUE)
- `response_limit` (INTEGER)
- `reset_period_seconds` (INTEGER)
- `duration_days` (INTEGER)
- `price` (NUMERIC(10,2))
- `is_active` (BOOLEAN)

**Индексы:**
- `ix_subscription_plans_name` на `name`

## user_subscriptions

**Назначение:** Подписки пользователей.

**Поля:**
- `user_id` (UUID, PK, FK → users.id)
- `subscription_plan_id` (UUID, FK → subscription_plans.id)
- `responses_count` (INTEGER)
- `period_started_at` (TIMESTAMP)
- `started_at` (TIMESTAMP)
- `expires_at` (TIMESTAMP)

**Индексы:**
- `ix_user_subscriptions_subscription_plan_id` на `subscription_plan_id`

## vacancy_responses

**Назначение:** Отклики на вакансии.

**Поля:**
- `id` (UUID, PK)
- `user_id` (UUID, FK → users.id)
- `resume_id` (UUID, FK → resumes.id)
- `vacancy_id` (VARCHAR)
- `vacancy_name` (VARCHAR)
- `vacancy_url` (VARCHAR)
- `cover_letter` (TEXT)
- `resume_hash` (VARCHAR)
- `created_at` (TIMESTAMP)

**Индексы:**
- `ix_vacancy_responses_user_id` на `user_id`
- `ix_vacancy_responses_resume_id` на `resume_id`
- `ix_vacancy_responses_vacancy_id` на `vacancy_id`

## resume_to_vacancy_matches

**Назначение:** Совпадения резюме с вакансиями.

**Поля:**
- `id` (UUID, PK)
- `resume_id` (UUID, FK → resumes.id)
- `vacancy_id` (VARCHAR)
- `match_score` (INTEGER)
- `created_at` (TIMESTAMP)

**Индексы:**
- `ix_resume_to_vacancy_matches_resume_id` на `resume_id`

## agent_actions

**Назначение:** Действия, предложенные AI агентом.

**Поля:**
- `id` (UUID, PK)
- `user_id` (UUID, FK → users.id)
- `entity_type` (VARCHAR)
- `entity_id` (BIGINT)
- `action_type` (VARCHAR)
- `action_data` (JSONB)
- `is_read` (BOOLEAN)
- `created_at` (TIMESTAMP)

**Индексы:**
- `ix_agent_actions_user_id` на `user_id`
- `ix_agent_actions_is_read` на `is_read`

## resume_filter_settings

**Назначение:** Настройки фильтрации для резюме.

**Поля:**
- `id` (UUID, PK)
- `resume_id` (UUID, FK → resumes.id, UNIQUE)
- `salary_min` (INTEGER)
- `area` (VARCHAR)
- `keywords` (TEXT)
- `stop_words` (TEXT)
- `excluded_companies` (TEXT)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

## telegram_notification_settings

**Назначение:** Настройки Telegram уведомлений.

**Поля:**
- `id` (UUID, PK)
- `user_id` (UUID, FK → users.id, UNIQUE)
- `telegram_chat_id` (BIGINT)
- `telegram_username` (VARCHAR)
- `is_enabled` (BOOLEAN)
- `notify_new_messages` (BOOLEAN)
- `notify_invitations` (BOOLEAN)
- `notify_rejections` (BOOLEAN)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

## telegram_link_tokens

**Назначение:** Временные токены для привязки Telegram.

**Поля:**
- `id` (UUID, PK)
- `user_id` (UUID, FK → users.id)
- `token` (VARCHAR, UNIQUE)
- `expires_at` (TIMESTAMP)
- `created_at` (TIMESTAMP)

**Индексы:**
- `ix_telegram_link_tokens_token` на `token`

## Примеры запросов

### Получение пользователя с подпиской

```sql
SELECT u.*, us.responses_count, sp.name as plan_name
FROM users u
LEFT JOIN user_subscriptions us ON u.id = us.user_id
LEFT JOIN subscription_plans sp ON us.subscription_plan_id = sp.id
WHERE u.id = '550e8400-e29b-41d4-a716-446655440000';
```

### Статистика откликов по пользователю

```sql
SELECT COUNT(*) as total_responses
FROM vacancy_responses
WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'
AND created_at >= NOW() - INTERVAL '30 days';
```

## Связанные разделы

- [Архитектура: Схема БД](../architecture/database-schema.md) — детальная схема
- [Reference: Глоссарий](glossary.md) — определения терминов
