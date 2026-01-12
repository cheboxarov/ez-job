# План: Замена LLM провайдеров на кастомный провайдер

## Цель

Заменить три существующих LLM провайдера (OpenAI, Gemini, Anthropic) на один кастомный провайдер с настраиваемыми параметрами:

- **Custom URL** - базовый URL API
- **Model** - название модели
- **API Key** - ключ авторизации

## Текущая архитектура

### Ключевые файлы:

1. `electron/ConfigHelper.ts` - управление конфигурацией
2. `electron/ProcessingHelper.ts` - API вызовы к LLM
3. `src/components/Settings/SettingsDialog.tsx` - UI настроек

### Текущая структура конфига:

```typescript
interface Config {
  apiKey: string;
  apiProvider: "openai" | "gemini" | "anthropic";
  extractionModel: string;
  solutionModel: string;
  debuggingModel: string;
  language: string;
  opacity: number;
}
```

---

## План реализации

### Шаг 1: Обновить ConfigHelper.ts

**Изменения в интерфейсе Config:**

```typescript
interface Config {
  apiKey: string;
  baseUrl: string;        // НОВОЕ: кастомный URL (например: https://api.example.com/v1)
  model: string;          // НОВОЕ: одна модель для всех задач
  language: string;
  opacity: number;
}
```

**Удалить:**

- `apiProvider` поле
- `extractionModel`, `solutionModel`, `debuggingModel` (заменить на `model`)
- Логику автоопределения провайдера по API ключу
- Функцию `sanitizeModelSelection()`
- Провайдер-специфичную валидацию ключей

**Обновить defaultConfig:**

```typescript
defaultConfig = {
  apiKey: "",
  baseUrl: "https://api.openai.com/v1",  // По умолчанию OpenAI-совместимый
  model: "gpt-4o",
  language: "python",
  opacity: 1.0
}
```

**Упростить валидацию:**

- `isValidApiKeyFormat()` - просто проверять что ключ не пустой
- `testApiKey()` - сделать тестовый запрос к указанному URL

### Шаг 2: Обновить ProcessingHelper.ts

**Удалить:**

- `openaiClient`, `anthropicClient`, `geminiApiKey` поля
- Три отдельных метода для каждого провайдера
- Импорты OpenAI, Anthropic SDK

**Добавить:**

- Один универсальный HTTP клиент (axios или fetch)
- Использовать **OpenAI-совместимый формат API** (стандарт для большинства LLM)

**Новая структура API вызова:**

```typescript
async callLLM(messages: Message[], options: {maxTokens?: number, temperature?: number}) {
  const config = configHelper.loadConfig();

  const response = await axios.post(
    `${config.baseUrl}/chat/completions`,
    {
      model: config.model,
      messages: messages,
      max_tokens: options.maxTokens || 4000,
      temperature: options.temperature || 0.2
    },
    {
      headers: {
        'Authorization': `Bearer ${config.apiKey}`,
        'Content-Type': 'application/json'
      },
      timeout: 60000
    }
  );

  return response.data.choices[0].message.content;
}
```

**Формат сообщений с изображениями (OpenAI Vision формат):**

```typescript
{
  role: "user",
  content: [
    { type: "text", text: "..." },
    {
      type: "image_url",
      image_url: { url: `data:image/png;base64,${base64Data}` }
    }
  ]
}
```

**Обновить методы:**

- `processScreenshots()` - использовать `callLLM()`
- `generateSolution()` - использовать `callLLM()`
- `processDebug()` - использовать `callLLM()`

### Шаг 3: Обновить SettingsDialog.tsx

**Удалить:**

- Выбор провайдера (radio buttons OpenAI/Gemini/Anthropic)
- Списки моделей для каждого провайдера
- Инструкции по получению ключей для разных провайдеров

**Добавить поля:**

```tsx
// Base URL
<input
  type="text"
  placeholder="https://api.openai.com/v1"
  value={baseUrl}
  onChange={e => setBaseUrl(e.target.value)}
/>

// Model name
<input
  type="text"
  placeholder="gpt-4o"
  value={model}
  onChange={e => setModel(e.target.value)}
/>

// API Key (уже есть)
<input
  type="password"
  value={apiKey}
  onChange={e => setApiKey(e.target.value)}
/>
```

**UI структура:**

```
┌─────────────────────────────────────┐
│ Settings                            │
├─────────────────────────────────────┤
│ Base URL:                           │
│ [https://api.openai.com/v1      ]   │
│                                     │
│ Model:                              │
│ [gpt-4o                         ]   │
│                                     │
│ API Key:                            │
│ [••••••••••••••••               ]   │
│                                     │
│ Language: [Python ▼]                │
│                                     │
│ [Test Connection]  [Save Settings]  │
└─────────────────────────────────────┘
```

### Шаг 4: Обновить IPC handlers (ipcHandlers.ts)

**Обновить:**

- `validate-api-key` - тестировать подключение к кастомному URL
- Убрать провайдер-специфичную логику

### Шаг 5: Обновить типы (env.d.ts / types)

**Обновить TypeScript типы:**

```typescript
interface Config {
  apiKey: string;
  baseUrl: string;
  model: string;
  language: string;
  opacity: number;
}
```

### Шаг 6: Очистка

**Удалить зависимости из package.json:**

- `openai` (если не нужен SDK)
- `@anthropic-ai/sdk`

**Оставить:**

- `axios` для HTTP запросов

---

## Файлы для изменения

| Файл | Действие |

|------|----------|

| `electron/ConfigHelper.ts` | Упростить конфиг, убрать провайдеры |

| `electron/ProcessingHelper.ts` | Заменить 3 клиента на 1 универсальный |

| `electron/ipcHandlers.ts` | Обновить валидацию |

| `electron/preload.ts` | Минимальные изменения (если нужно) |

| `src/components/Settings/SettingsDialog.tsx` | Новый UI |

| `package.json` | Удалить ненужные SDK |

---

## Порядок реализации

1. **ConfigHelper.ts** - основа, от неё зависит всё остальное
2. **ProcessingHelper.ts** - ядро функционала
3. **SettingsDialog.tsx** - UI
4. **ipcHandlers.ts** - связующее звено
5. **package.json** - очистка зависимостей
6. **Тестирование** - проверить работу с кастомным URL

---

## Совместимость

Новая реализация будет совместима с любым OpenAI-совместимым API:

- OpenAI
- Azure OpenAI
- OpenRouter
- LocalAI
- Ollama (с OpenAI-совместимым endpoint)
- vLLM
- LiteLLM
- Любой кастомный прокси

---

## Риски и ограничения

1. **Vision API** - не все провайдеры поддерживают изображения в том же формате

   - Решение: документировать требования к провайдеру

2. **Формат ответов** - разные провайдеры могут возвращать данные по-разному

   - Решение: использовать стандартный OpenAI формат

3. **Таймауты** - разные провайдеры имеют разные лимиты

   - Решение: сделать таймаут настраиваемым (опционально)