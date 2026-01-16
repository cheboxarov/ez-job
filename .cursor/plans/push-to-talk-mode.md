# Push-to-Talk Mode для Voice Assistant

## Текущее поведение

Сейчас голосовой помощник работает в режиме **Continuous Recording**:
1. Нажимаем Start Recording - начинается непрерывная запись
2. Аудио автоматически разбивается на чанки по таймеру (`chunkDurationMs`)
3. Каждый чанк немедленно отправляется на транскрипцию (AssemblyAI)
4. Транскрипции появляются в списке
5. Пользователь вручную выбирает нужные чанки
6. Пользователь пишет вопрос и отправляет в LLM

## Новый режим: Push-to-Talk

Новый режим работы:
1. **Нажимаем кнопку** → начинается запись (без автоматической отправки на транскрипцию)
2. **Ждем/говорим** → аудио накапливается в буфер
3. **Нажимаем кнопку снова** → запись останавливается
4. **Автоматически** → вся запись отправляется на транскрипцию
5. **Автоматически** → транскрипция отправляется в LLM
6. **Получаем ответ** → отображается в интерфейсе

---

## План реализации

### 1. Обновить типы (`src/types/voice.ts`)

```typescript
// Добавить новые типы
export type VoiceMode = 'continuous' | 'push-to-talk'

export interface PushToTalkState {
  isRecording: boolean
  isProcessing: boolean  // транскрипция + LLM
  audioBuffer: Blob | null
}
```

### 2. Создать новый AudioCapture helper для PTT режима

**Файл:** `src/components/Voice/PushToTalkCaptureHelper.ts`

Отличия от `AudioCaptureHelper`:
- Не разбивает на чанки по таймеру
- Накапливает всё аудио в один буфер
- При остановке возвращает полный Blob

```typescript
export class PushToTalkCaptureHelper {
  private audioChunks: Blob[] = []

  public async startCapture(): Promise<void> { ... }

  public stopCapture(): Blob {
    // Объединяет все чанки в один Blob и возвращает
  }
}
```

### 3. Обновить VoiceContext (`src/contexts/VoiceContext.tsx`)

Добавить:
- `mode: VoiceMode` - текущий режим
- `setMode(mode: VoiceMode)` - переключение режима
- `pttState: PushToTalkState` - состояние PTT режима
- `startPTTRecording()` - начать PTT запись
- `stopPTTRecording()` - остановить и обработать

```typescript
const stopPTTRecording = useCallback(async () => {
  // 1. Остановить запись, получить audioBlob
  const audioBlob = pttCaptureRef.current?.stopCapture()

  // 2. Отправить на транскрипцию
  setPttState(prev => ({ ...prev, isProcessing: true }))
  const transcription = await window.electronAPI.voice.transcribeFull(audioBlob)

  // 3. Отправить в LLM
  const response = await window.electronAPI.voice.processQuery({
    chunks: [{ text: transcription, timestamp: Date.now() }],
    question: '' // Пустой вопрос = просто обработать транскрипцию
  })

  // 4. Показать результат
  setResponse(response)
  setPttState(prev => ({ ...prev, isProcessing: false }))
}, [])
```

### 4. Добавить IPC handler для полной транскрипции

**Файл:** `electron/ipcHandlers.ts`

```typescript
ipcMain.handle('voice:transcribe-full', async (_event, { audioData, mimeType }) => {
  const buffer = Buffer.from(audioData)
  const result = await transcriptionHelper.transcribe(buffer, { mimeType })
  return result.text
})
```

**Файл:** `electron/preload.ts`

```typescript
voice: {
  // ... существующие методы
  transcribeFull: (data: { audioData: ArrayBuffer, mimeType: string }) =>
    ipcRenderer.invoke('voice:transcribe-full', data)
}
```

### 5. Обновить UI компоненты

#### 5.1 Переключатель режима

**Файл:** `src/components/Voice/ModeSelector.tsx`

```tsx
export function ModeSelector({ mode, onModeChange }: Props) {
  return (
    <div className="flex gap-2">
      <Button
        variant={mode === 'continuous' ? 'default' : 'outline'}
        onClick={() => onModeChange('continuous')}
      >
        Continuous
      </Button>
      <Button
        variant={mode === 'push-to-talk' ? 'default' : 'outline'}
        onClick={() => onModeChange('push-to-talk')}
      >
        Push-to-Talk
      </Button>
    </div>
  )
}
```

#### 5.2 PTT кнопка записи

**Файл:** `src/components/Voice/PushToTalkButton.tsx`

```tsx
export function PushToTalkButton({ state, onStart, onStop }: Props) {
  const { isRecording, isProcessing } = state

  if (isProcessing) {
    return <Button disabled>Processing...</Button>
  }

  return (
    <Button
      onClick={isRecording ? onStop : onStart}
      className={isRecording ? 'bg-red-500 animate-pulse' : ''}
    >
      {isRecording ? 'Stop & Process' : 'Start Recording'}
    </Button>
  )
}
```

#### 5.3 Обновить VoiceAssistant.tsx

```tsx
function VoiceAssistantContent() {
  const { mode, setMode, pttState, startPTTRecording, stopPTTRecording, ... } = useVoice()

  return (
    <div>
      <ModeSelector mode={mode} onModeChange={setMode} />

      {mode === 'continuous' ? (
        // Текущий UI с чанками
        <>
          <AudioControls ... />
          <TranscriptionList ... />
          <ChunkSelector ... />
          <QuestionInput ... />
        </>
      ) : (
        // Новый PTT UI
        <>
          <PushToTalkButton
            state={pttState}
            onStart={startPTTRecording}
            onStop={stopPTTRecording}
          />
          {pttState.isProcessing && <ProcessingIndicator />}
        </>
      )}

      <ResponseDisplay response={response} />
    </div>
  )
}
```

### 6. Добавить настройку для PTT режима

**Файл:** `electron/ConfigHelper.ts` (обновить `TranscriptionConfig`)

```typescript
export interface TranscriptionConfig {
  // ... существующие поля
  defaultMode: 'continuous' | 'push-to-talk'
  pttPrompt: string  // Системный промпт для PTT режима
}
```

### 7. Обновить локализацию

**Файлы:** `src/i18n/locales/en.json`, `ru.json`

```json
{
  "voice": {
    "mode": {
      "continuous": "Continuous Recording",
      "pushToTalk": "Push-to-Talk"
    },
    "ptt": {
      "startRecording": "Start Recording",
      "stopAndProcess": "Stop & Process",
      "processing": "Processing...",
      "transcribing": "Transcribing...",
      "thinking": "Thinking..."
    }
  }
}
```

---

## Порядок реализации

1. **Types** - обновить типы
2. **Backend** - добавить IPC handler для полной транскрипции
3. **PushToTalkCaptureHelper** - создать helper для записи без чанков
4. **VoiceContext** - добавить PTT логику
5. **UI компоненты** - создать ModeSelector, PushToTalkButton
6. **VoiceAssistant** - интегрировать новый режим
7. **Settings** - добавить настройки PTT
8. **i18n** - локализация

---

## Примечания

- В PTT режиме не нужен список чанков и их выбор
- Транскрипция всей записи может занять больше времени (зависит от длины)
- Нужно добавить индикатор прогресса для этапов: Recording → Transcribing → Thinking → Done
- Можно добавить таймер записи для визуального фидбека
