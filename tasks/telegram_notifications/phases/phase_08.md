# Этап 8: Frontend

## Описание
Создание страницы настроек с разделом Telegram на фронтенде.

## Подзадачи

1. **Создание API клиента**
   - Файл: `frontend/src/api/telegram.ts`
   - Функции: getTelegramSettings, updateTelegramSettings, generateTelegramLink, unlinkTelegram, sendTestNotification

2. **Расширение типов**
   - Файл: `frontend/src/types/api.ts`
   - Интерфейсы: TelegramNotificationSettings, TelegramLinkResponse

3. **Создание страницы настроек**
   - Файл: `frontend/src/pages/SettingsPage.tsx`
   - Раздел Telegram:
     - Состояние "Не привязан": кнопка привязки
     - Состояние "Привязан": username, глобальный switch, чекбоксы по типам, кнопка отвязки
     - Кнопка "Отправить тестовое"
   - Polling статуса привязки

4. **Обновление навигации**
   - Файл: `frontend/src/components/Layout/MainLayout.tsx`
   - Добавить пункт "Настройки" в меню

5. **Добавление роута**
   - Файл: `frontend/src/App.tsx`
   - Роут `/settings` → SettingsPage

## Зависимости
- Этап 6: API endpoints (API должен быть готов)

## Критерии завершения
- [ ] Страница настроек доступна из меню
- [ ] Привязка Telegram работает
- [ ] Настройки уведомлений сохраняются
- [ ] Отвязка работает
- [ ] Тестовое уведомление отправляется
- [ ] UI соответствует дизайну приложения

## Deliverables
- `frontend/src/api/telegram.ts`
- `frontend/src/pages/SettingsPage.tsx`
- Обновлённый `frontend/src/types/api.ts`
- Обновлённый `frontend/src/components/Layout/MainLayout.tsx`
- Обновлённый `frontend/src/App.tsx`
