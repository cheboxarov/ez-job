# Отправка аудио напрямую в LLM (без транскрипции)

## Цель

Добавить опцию в окно Push-to-Talk (Ctrl+Shift+P) для отправки аудиозаписи напрямую в LLM, минуя этап транскрипции через AssemblyAI.

## Текущее поведение

1. Пользователь нажимает кнопку отправки в PushToTalk окне
2. Извлекается аудио за выбранное время (1/3/5 минут)
3. Аудио отправляется на транскрипцию (AssemblyAI)
4. Текст транскрипции отправляется в LLM
5. Ответ отображается

## Новое поведение (с галочкой "Отправить напрямую")

1. Пользователь включает галочку "Send recording directly"
2. Нажимает кнопку отправки
3. Извлекается аудио за выбранное время
4. **Пропускаем транскрипцию** → аудио (base64) отправляется напрямую в LLM
5. LLM обрабатывает аудио и возвращает ответ

## Преимущества

- Быстрее (нет задержки на транскрипцию)
- Экономия на AssemblyAI API
- LLM может "слышать" интонации, паузы, акценты
- Работает с моделями GPT-4o, Claude, Gemini (которые поддерживают audio input)

---

## План реализации

### 1. Обновить типы (`src/types/voice.ts`)

```typescript
// Добавить в VoiceTranscriptionConfig
export interface VoiceTranscriptionConfig {
  // ... существующие поля
  sendAudioDirectly: boolean  // По умолчанию false
}

// Добавить в PushToTalkState
export interface PushToTalkState {
  // ... существующие поля
  sendDirectly: boolean  // Состояние галочки
}
```

### 2. Обновить ConfigHelper (`electron/ConfigHelper.ts`)

Добавить поле `sendAudioDirectly` в `TranscriptionConfig`:

```typescript
export interface TranscriptionConfig {
  // ... существующие поля
  sendAudioDirectly: boolean
}

// В defaultTranscriptionConfig
const defaultTranscriptionConfig: TranscriptionConfig = {
  // ... существующие поля
  sendAudioDirectly: false
}
```

### 3. Обновить ProcessingHelper (`electron/ProcessingHelper.ts`)

#### 3.1 Расширить тип OpenAIMessage для поддержки аудио

```typescript
type OpenAIMessage =
  | {
      role: "system" | "assistant";
      content: string;
    }
  | {
      role: "user";
      content:
        | string
        | Array<
            | { type: "text"; text: string }
            | { type: "image_url"; image_url: { url: string } }
            | { type: "input_audio"; input_audio: { data: string; format: "wav" | "mp3" | "webm" | "ogg" } }
          >;
    };
```

#### 3.2 Добавить метод processVoiceQueryWithAudio

```typescript
public async processVoiceQueryWithAudio(
  audioBase64: string,
  audioFormat: string,
  systemPromptOverride?: string
): Promise<string> {
  const config = configHelper.loadConfig()
  const languageInstruction = this.getResponseLanguageInstruction(
    config.interfaceLanguage
  )

  const promptHeader = systemPromptOverride?.trim()
    ? systemPromptOverride.trim()
    : "You are an interview assistant.\nThe user is in an interview and needs help answering questions."

  const systemPrompt = `${languageInstruction} ${promptHeader}
Listen to the audio recording below. This is a recording from an interview or meeting.
Please provide a helpful response to the questions or topics discussed in the audio.`

  const messages: OpenAIMessage[] = [
    { role: "system", content: systemPrompt },
    {
      role: "user",
      content: [
        {
          type: "text",
          text: "Please listen to this audio and help me with the question or topic being discussed."
        },
        {
          type: "input_audio",
          input_audio: {
            data: audioBase64,
            format: audioFormat as "wav" | "mp3" | "webm" | "ogg"
          }
        }
      ]
    }
  ]

  return this.callLLM(messages, { maxTokens: 1200, temperature: 0.2 })
}
```

### 4. Добавить IPC handler (`electron/ipcHandlers.ts`)

```typescript
ipcMain.handle("voice:process-audio-directly", async (_event, payload) => {
  if (!deps.processingHelper) {
    return { success: false, error: "Processing helper not available." }
  }
  const { audioData, mimeType, systemPrompt } = payload || {}

  if (!audioData) {
    return { success: false, error: "Missing audio data." }
  }

  try {
    // Конвертируем ArrayBuffer в base64
    const buffer = Buffer.from(audioData)
    const audioBase64 = buffer.toString("base64")

    // Определяем формат из mimeType
    let format = "webm"
    if (mimeType?.includes("wav")) format = "wav"
    else if (mimeType?.includes("mp3")) format = "mp3"
    else if (mimeType?.includes("ogg")) format = "ogg"

    const response = await deps.processingHelper.processVoiceQueryWithAudio(
      audioBase64,
      format,
      systemPrompt
    )
    return { success: true, response }
  } catch (error: any) {
    return {
      success: false,
      error: error?.message || "Failed to process audio directly."
    }
  }
})
```

### 5. Обновить preload.ts

```typescript
voice: {
  // ... существующие методы
  processAudioDirectly: (data: {
    audioData: ArrayBuffer;
    mimeType: string;
    systemPrompt?: string;
  }) => ipcRenderer.invoke("voice:process-audio-directly", data)
}
```

### 6. Обновить типы Electron API (`src/types/electron.d.ts`)

```typescript
voice: {
  // ... существующие методы
  processAudioDirectly: (data: {
    audioData: ArrayBuffer;
    mimeType: string;
    systemPrompt?: string;
  }) => Promise<{ success: boolean; response?: string; error?: string }>;
}
```

### 7. Обновить VoiceContext (`src/contexts/VoiceContext.tsx`)

Добавить состояние и методы для прямой отправки:

```typescript
// Добавить в состояние
const [sendDirectly, setSendDirectly] = useState(false)

// Обновить sendLastMinutes
const sendLastMinutes = useCallback(
  async (minutes: TimeSelection) => {
    if (!continuousRef.current) return null
    const activeConfig = config || (await refreshConfig())
    if (!activeConfig) return null

    setPttState((prev) => ({
      ...prev,
      isProcessing: true,
      stage: "extracting",
      continuousMode: true
    }))
    setError(null)

    try {
      const { blob, mimeType } =
        await continuousRef.current.getLastMinutes(minutes)

      if (!blob || blob.size === 0) {
        setError("Recording buffer is empty.")
        setPttState((prev) => ({
          ...prev,
          isProcessing: false,
          stage: "recording",
          continuousMode: true
        }))
        return null
      }

      const audioBuffer = await blob.arrayBuffer()

      // Если включена опция "отправить напрямую"
      if (sendDirectly) {
        setPttState((prev) => ({
          ...prev,
          stage: "thinking",  // Пропускаем "transcribing"
          continuousMode: true
        }))

        const llmResult = await window.electronAPI.voice.processAudioDirectly({
          audioData: audioBuffer,
          mimeType,
          systemPrompt: activeConfig.pttPrompt || undefined
        })

        if (!llmResult?.success) {
          setError(llmResult?.error || "Failed to process audio directly.")
          setPttState((prev) => ({
            ...prev,
            isProcessing: false,
            stage: "recording",
            continuousMode: true
          }))
          return null
        }

        setPttState((prev) => ({
          ...prev,
          isProcessing: false,
          stage: "recording",
          continuousMode: true
        }))

        return {
          transcription: "[Audio sent directly to LLM]",
          response: llmResult.response || ""
        }
      }

      // Существующая логика с транскрипцией...
      // ...
    } catch (err) {
      // ...
    }
  },
  [config, refreshConfig, sendDirectly]
)

// Добавить в контекст
return (
  <VoiceContext.Provider
    value={{
      // ... существующие значения
      sendDirectly,
      setSendDirectly
    }}
  >
    {children}
  </VoiceContext.Provider>
)
```

### 8. Обновить UI PushToTalk (`src/_pages/PushToTalk.tsx`)

Добавить галочку в интерфейс:

```tsx
function PushToTalkContent() {
  const { t } = useTranslation()
  const {
    pttState,
    startContinuousRecording,
    stopContinuousRecording,
    sendLastMinutes,
    bufferDuration,
    error,
    clearError,
    sendDirectly,      // Новое
    setSendDirectly    // Новое
  } = useVoice()

  // ... существующий код

  return (
    <div className="h-screen w-screen bg-transparent text-white">
      <div className="relative flex h-full w-full flex-col items-center gap-2 rounded-xl border border-white/10 bg-black/70 px-3 py-3 backdrop-blur-sm">
        {/* ... существующий header */}

        {/* Новая галочка */}
        <label
          className="flex items-center gap-2 text-xs text-white/60 cursor-pointer"
          style={noDragStyle}
        >
          <input
            type="checkbox"
            checked={sendDirectly}
            onChange={(e) => setSendDirectly(e.target.checked)}
            className="h-3 w-3 rounded border-white/30 bg-white/10 accent-blue-500"
            disabled={pttState.isProcessing}
          />
          <span>{t("voice.ptt.sendDirectly", "Send audio directly to LLM")}</span>
        </label>

        {/* ... существующие кнопки времени и отправки */}
      </div>
    </div>
  )
}
```

### 9. Обновить локализацию

**`src/i18n/locales/en.json`:**

```json
{
  "voice": {
    "ptt": {
      "sendDirectly": "Send audio directly to LLM",
      "sendDirectlyHint": "Skip transcription, send audio directly (requires model with audio support)"
    }
  }
}
```

**`src/i18n/locales/ru.json`:**

```json
{
  "voice": {
    "ptt": {
      "sendDirectly": "Отправить аудио напрямую в LLM",
      "sendDirectlyHint": "Пропустить транскрипцию, отправить аудио напрямую (требуется модель с поддержкой аудио)"
    }
  }
}
```

---

## Порядок реализации

1. **Types** - обновить `src/types/voice.ts` и `src/types/electron.d.ts`
2. **Config** - добавить поле в `electron/ConfigHelper.ts`
3. **ProcessingHelper** - добавить метод `processVoiceQueryWithAudio`
4. **IPC handlers** - добавить handler `voice:process-audio-directly`
5. **Preload** - обновить `electron/preload.ts`
6. **VoiceContext** - добавить состояние `sendDirectly` и логику
7. **UI** - добавить галочку в `PushToTalk.tsx`
8. **i18n** - локализация

---

## Совместимость моделей

Функция работает с моделями, поддерживающими audio input:
- **OpenAI**: GPT-4o, GPT-4o-mini
- **Anthropic Claude**: Claude 3.5 Sonnet (через API)
- **Google Gemini**: Gemini 1.5 Pro/Flash

Если модель не поддерживает аудио, API вернёт ошибку. Можно добавить fallback на транскрипцию.

---

## Дополнительные улучшения (опционально)

1. **Auto-detect model support** - проверять поддержку audio input для текущей модели
2. **Fallback** - если модель не поддерживает аудио, автоматически использовать транскрипцию
3. **Settings** - сохранять предпочтение `sendDirectly` в конфиге
4. **Visual indicator** - показывать иконку 🎧 когда режим прямой отправки включен
