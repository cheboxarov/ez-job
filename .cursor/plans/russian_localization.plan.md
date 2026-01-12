# План: Добавление русского языка в Interview Coder

## Цель

1. **Локализация интерфейса** - возможность переключить весь UI на русский язык
2. **Ответы LLM на русском** - нейросеть отвечает на выбранном языке

## Текущее состояние

- **Нет системы локализации** - все ~100 текстовых строк hardcoded на английском
- Тексты разбросаны по 15+ компонентам
- Нет файлов переводов

---

## План реализации

### Шаг 1: Установить i18next

**Установить зависимости:**

```bash
npm install i18next react-i18next i18next-browser-languagedetector
```

**Почему i18next:**

- Самая популярная библиотека для React
- Поддержка namespace, интерполяции, pluralization
- Легкая интеграция с Electron

### Шаг 2: Создать структуру локализации

**Создать папку и файлы:**

```
src/
├── i18n/
│   ├── index.ts          # Конфигурация i18next
│   └── locales/
│       ├── en.json       # Английские тексты
│       └── ru.json       # Русские тексты
```

**src/i18n/index.ts:**

```typescript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import en from './locales/en.json';
import ru from './locales/ru.json';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      ru: { translation: ru }
    },
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
```

### Шаг 3: Создать файлы переводов

**src/i18n/locales/en.json:**

```json
{
  "app": {
    "name": "Interview Coder",
    "subtitle": "Unlocked Edition"
  },
  "welcome": {
    "title": "Welcome to Interview Coder",
    "globalShortcuts": "Global Shortcuts",
    "gettingStarted": "Getting Started"
  },
  "header": {
    "language": "Language:",
    "settings": "Settings",
    "logOut": "Log Out"
  },
  "queue": {
    "takeScreenshot": "Take Screenshot",
    "solve": "Solve",
    "deleteLastScreenshot": "Delete Last Screenshot",
    "keyboardShortcuts": "Keyboard Shortcuts",
    "toggleWindow": "Toggle Window"
  },
  "solutions": {
    "problemStatement": "Problem Statement",
    "myThoughts": "My Thoughts",
    "solution": "Solution",
    "complexity": "Complexity",
    "time": "Time:",
    "space": "Space:",
    "extracting": "Extracting problem statement...",
    "loading": "Loading solutions...",
    "generating": "Generating solutions...",
    "calculating": "Calculating complexity...",
    "notAvailable": "Complexity not available"
  },
  "debug": {
    "whatIChanged": "What I Changed",
    "originalCode": "Original Code",
    "analysisImprovements": "Analysis & Improvements",
    "loadingDebug": "Loading debug analysis..."
  },
  "settings": {
    "title": "Settings",
    "baseUrl": "Base URL",
    "model": "Model",
    "apiKey": "API Key",
    "interfaceLanguage": "Interface Language",
    "testConnection": "Test Connection",
    "save": "Save Settings"
  },
  "update": {
    "readyToInstall": "Update Ready to Install",
    "newVersionAvailable": "A New Version is Available",
    "restartAndInstall": "Restart and Install",
    "download": "Download Update",
    "downloading": "Downloading..."
  },
  "errors": {
    "apiConfigInvalid": "API Configuration Invalid",
    "failedToSaveApiKey": "Failed to save API key",
    "processingFailed": "Processing Failed",
    "failedToTakeScreenshot": "Failed to take screenshot",
    "failedToDeleteScreenshot": "Failed to delete the screenshot",
    "noScreenshots": "There are no screenshots to delete",
    "failedToProcess": "Failed to process screenshots",
    "failedToToggleWindow": "Failed to toggle window",
    "missingInfo": "Please fill in Base URL, Model, and API Key",
    "connectionFailed": "Unable to validate credentials"
  },
  "success": {
    "apiKeySaved": "API key saved successfully",
    "settingsSaved": "Settings saved successfully"
  },
  "shortcuts": {
    "toggleVisibility": "Toggle Visibility",
    "takeScreenshot": "Take Screenshot",
    "deleteScreenshot": "Delete Last Screenshot",
    "processScreenshots": "Process Screenshots",
    "startDebug": "Start Debug",
    "scrollUp": "Scroll Up",
    "scrollDown": "Scroll Down",
    "resetScroll": "Reset Scroll"
  }
}
```

**src/i18n/locales/ru.json:**

```json
{
  "app": {
    "name": "Interview Coder",
    "subtitle": "Разблокированная версия"
  },
  "welcome": {
    "title": "Добро пожаловать в Interview Coder",
    "globalShortcuts": "Глобальные горячие клавиши",
    "gettingStarted": "Начало работы"
  },
  "header": {
    "language": "Язык:",
    "settings": "Настройки",
    "logOut": "Выход"
  },
  "queue": {
    "takeScreenshot": "Сделать скриншот",
    "solve": "Решить",
    "deleteLastScreenshot": "Удалить последний скриншот",
    "keyboardShortcuts": "Горячие клавиши",
    "toggleWindow": "Показать/скрыть окно"
  },
  "solutions": {
    "problemStatement": "Условие задачи",
    "myThoughts": "Мои мысли",
    "solution": "Решение",
    "complexity": "Сложность",
    "time": "Время:",
    "space": "Память:",
    "extracting": "Извлекаю условие задачи...",
    "loading": "Загрузка решений...",
    "generating": "Генерация решений...",
    "calculating": "Расчёт сложности...",
    "notAvailable": "Сложность недоступна"
  },
  "debug": {
    "whatIChanged": "Что я изменил",
    "originalCode": "Исходный код",
    "analysisImprovements": "Анализ и улучшения",
    "loadingDebug": "Загрузка анализа отладки..."
  },
  "settings": {
    "title": "Настройки",
    "baseUrl": "URL сервера",
    "model": "Модель",
    "apiKey": "API ключ",
    "interfaceLanguage": "Язык интерфейса",
    "testConnection": "Проверить подключение",
    "save": "Сохранить настройки"
  },
  "update": {
    "readyToInstall": "Обновление готово к установке",
    "newVersionAvailable": "Доступна новая версия",
    "restartAndInstall": "Перезапустить и установить",
    "download": "Скачать обновление",
    "downloading": "Загрузка..."
  },
  "errors": {
    "apiConfigInvalid": "Неверная конфигурация API",
    "failedToSaveApiKey": "Не удалось сохранить API ключ",
    "processingFailed": "Ошибка обработки",
    "failedToTakeScreenshot": "Не удалось сделать скриншот",
    "failedToDeleteScreenshot": "Не удалось удалить скриншот",
    "noScreenshots": "Нет скриншотов для удаления",
    "failedToProcess": "Не удалось обработать скриншоты",
    "failedToToggleWindow": "Не удалось переключить окно",
    "missingInfo": "Пожалуйста, заполните URL сервера, Модель и API ключ",
    "connectionFailed": "Не удалось проверить подключение"
  },
  "success": {
    "apiKeySaved": "API ключ сохранён",
    "settingsSaved": "Настройки сохранены"
  },
  "shortcuts": {
    "toggleVisibility": "Показать/скрыть",
    "takeScreenshot": "Сделать скриншот",
    "deleteScreenshot": "Удалить последний скриншот",
    "processScreenshots": "Обработать скриншоты",
    "startDebug": "Начать отладку",
    "scrollUp": "Прокрутить вверх",
    "scrollDown": "Прокрутить вниз",
    "resetScroll": "Сбросить прокрутку"
  }
}
```

### Шаг 4: Добавить настройку языка интерфейса в Config

**Обновить ConfigHelper.ts:**

```typescript
interface Config {
  apiKey: string;
  baseUrl: string;
  model: string;
  language: string;           // Язык программирования
  interfaceLanguage: string;  // НОВОЕ: 'en' | 'ru'
  opacity: number;
}

defaultConfig = {
  // ...
  interfaceLanguage: 'en'
}
```

### Шаг 5: Инициализировать i18n в приложении

**Обновить src/main.tsx:**

```typescript
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './i18n';  // Добавить импорт

ReactDOM.createRoot(...).render(<App />);
```

### Шаг 6: Обновить компоненты для использования переводов

**Паттерн замены:**

```typescript
// Было:
<h1>Problem Statement</h1>

// Станет:
import { useTranslation } from 'react-i18next';

const { t } = useTranslation();
<h1>{t('solutions.problemStatement')}</h1>
```

**Компоненты для обновления:**

| Компонент | Количество строк |

|-----------|------------------|

| WelcomeScreen.tsx | ~15 строк |

| Header.tsx | ~5 строк |

| QueueCommands.tsx | ~20 строк |

| Solutions.tsx | ~15 строк |

| Debug.tsx | ~5 строк |

| SettingsDialog.tsx | ~10 строк |

| UpdateNotification.tsx | ~5 строк |

| SolutionCommands.tsx | ~10 строк |

| App.tsx (toast сообщения) | ~15 строк |

### Шаг 7: Добавить переключатель языка в настройки

**В SettingsDialog.tsx добавить:**

```tsx
import { useTranslation } from 'react-i18next';

const { t, i18n } = useTranslation();

// UI для выбора языка интерфейса
<div>
  <label>{t('settings.interfaceLanguage')}</label>
  <select
    value={interfaceLanguage}
    onChange={e => {
      setInterfaceLanguage(e.target.value);
      i18n.changeLanguage(e.target.value);
    }}
  >
    <option value="en">English</option>
    <option value="ru">Русский</option>
  </select>
</div>
```

### Шаг 8: Синхронизировать язык при загрузке

**В App.tsx при инициализации:**

```typescript
import { useTranslation } from 'react-i18next';

useEffect(() => {
  const loadLanguage = async () => {
    const config = await window.electronAPI.getConfig();
    i18n.changeLanguage(config.interfaceLanguage);
  };
  loadLanguage();
}, []);
```

### Шаг 9: Настроить LLM для ответов на русском

**В ProcessingHelper.ts добавить инструкцию в промпт:**

```typescript
const config = configHelper.loadConfig();

// Добавить в системный промпт или в начало user message:
const languageInstruction = config.interfaceLanguage === 'ru'
  ? 'IMPORTANT: Respond in Russian language. All explanations, thoughts, and descriptions must be in Russian.'
  : '';

const systemPrompt = `${languageInstruction}
You are a coding interview assistant...`;
```

**Обновить промпты для всех типов обработки:**

1. **Problem Extraction** - извлечение условия на выбранном языке
2. **Solution Generation** - мысли и объяснения на выбранном языке
3. **Debug Processing** - анализ и рекомендации на выбранном языке

**Пример для Solution Generation:**

```typescript
// ru
`Ответь на русском языке. Объясни свой ход мыслей и решение на русском.`

// en
`Respond in English. Explain your thought process and solution in English.`
```

---

## Файлы для изменения

| Файл | Действие |

|------|----------|

| `package.json` | Добавить i18next зависимости |

| `src/i18n/index.ts` | СОЗДАТЬ - конфигурация i18n |

| `src/i18n/locales/en.json` | СОЗДАТЬ - английские переводы |

| `src/i18n/locales/ru.json` | СОЗДАТЬ - русские переводы |

| `src/main.tsx` | Импортировать i18n |

| `electron/ConfigHelper.ts` | Добавить interfaceLanguage |

| `electron/ProcessingHelper.ts` | Добавить языковую инструкцию в промпты |

| `src/App.tsx` | Инициализация языка + заменить тексты |

| `src/components/WelcomeScreen.tsx` | Заменить hardcoded тексты |

| `src/components/Header/Header.tsx` | Заменить hardcoded тексты |

| `src/components/Queue/QueueCommands.tsx` | Заменить hardcoded тексты |

| `src/components/Solutions/SolutionCommands.tsx` | Заменить hardcoded тексты |

| `src/components/Settings/SettingsDialog.tsx` | Добавить выбор языка + заменить тексты |

| `src/components/UpdateNotification.tsx` | Заменить hardcoded тексты |

| `src/_pages/Solutions.tsx` | Заменить hardcoded тексты |

| `src/_pages/Debug.tsx` | Заменить hardcoded тексты |

---

## Порядок реализации

1. **Установка зависимостей** - npm install
2. **Создать i18n конфигурацию и файлы переводов**
3. **Обновить ConfigHelper.ts** - добавить interfaceLanguage
4. **Обновить main.tsx** - импортировать i18n
5. **Обновить App.tsx** - синхронизация языка при загрузке
6. **Обновить SettingsDialog.tsx** - добавить переключатель языка
7. **Обновить ProcessingHelper.ts** - языковая инструкция для LLM
8. **Заменить тексты в компонентах** - по одному компоненту

---

## UI переключателя языка

```
┌─────────────────────────────────────┐
│ Settings                            │
├─────────────────────────────────────┤
│ Base URL:                           │
│ [https://api.example.com/v1     ]   │
│                                     │
│ Model:                              │
│ [gpt-4o                         ]   │
│                                     │
│ API Key:                            │
│ [••••••••••••••••               ]   │
│                                     │
│ Interface Language:                 │
│ [English ▼]                         │
│   ├── English                       │
│   └── Русский                       │
│                                     │
│ [Test Connection]  [Save Settings]  │
└─────────────────────────────────────┘
```

---

## Примеры переводов в коде

### До:

```tsx
// Solutions.tsx
<h2 className="...">Problem Statement</h2>
<span>Extracting problem statement...</span>
showToast("Processing Failed", error, "error");
```

### После:

```tsx
// Solutions.tsx
import { useTranslation } from 'react-i18next';

const { t } = useTranslation();

<h2 className="...">{t('solutions.problemStatement')}</h2>
<span>{t('solutions.extracting')}</span>
showToast(t('errors.processingFailed'), error, "error");
```

---

## Добавление новых языков в будущем

Для добавления нового языка (например, испанского):

1. Создать `src/i18n/locales/es.json`
2. Импортировать в `src/i18n/index.ts`
3. Добавить опцию в SettingsDialog.tsx
```typescript
// i18n/index.ts
import es from './locales/es.json';

resources: {
  en: { translation: en },
  ru: { translation: ru },
  es: { translation: es }  // Добавить
}
```