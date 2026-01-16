# Простой Push-to-Talk режим

## Проблема

Текущий режим Continuous Recording:
- Сложная логика с сегментами по 10 секунд
- WebM файлы нельзя объединять (каждый имеет свой заголовок)
- Баги с получением старых данных

## Новый режим: Простой Push-to-Talk

```
[Нажал REC] → Запись идёт → [Нажал SEND] → Отправка → Ответ
```

**Преимущества:**
- Простая логика: один blob = одна запись
- Нет проблем с объединением WebM
- Пользователь контролирует что записывается

---

## Текущие файлы

| Файл | Что делает |
|------|-----------|
| `src/_pages/PushToTalk.tsx` | UI окна PTT |
| `src/components/Voice/ContinuousRecordingHelper.ts` | Сложный буфер (удалим) |
| `src/components/Voice/PushToTalkCaptureHelper.ts` | Простой захват (используем) |
| `src/contexts/VoiceContext.tsx` | Контекст голоса |

---

## План реализации

### Шаг 1: Обновить PushToTalkCaptureHelper

**Файл:** `src/components/Voice/PushToTalkCaptureHelper.ts`

Убедиться что helper работает правильно:

```typescript
export class PushToTalkCaptureHelper {
  private micStream: MediaStream | null = null
  private systemStream: MediaStream | null = null
  private audioContext: AudioContext | null = null
  private destination: MediaStreamAudioDestinationNode | null = null
  private mediaRecorder: MediaRecorder | null = null
  private chunks: Blob[] = []
  private mimeType: string | undefined
  private isRecording = false

  // Начать запись
  public async startCapture(): Promise<void> {
    if (this.isRecording) return

    this.chunks = []

    // Захват микрофона
    this.micStream = await navigator.mediaDevices.getUserMedia({
      audio: true,
      video: false
    })

    // Попытка захватить системный звук (опционально)
    try {
      await this.startSystemAudioCapture()
    } catch (e) {
      console.warn("System audio not available")
    }

    // Создать AudioContext для микширования
    this.audioContext = new AudioContext({ sampleRate: 16000 })
    this.destination = this.audioContext.createMediaStreamDestination()

    if (this.micStream) {
      const micSource = this.audioContext.createMediaStreamSource(this.micStream)
      micSource.connect(this.destination)
    }

    if (this.systemStream) {
      const sysSource = this.audioContext.createMediaStreamSource(this.systemStream)
      sysSource.connect(this.destination)
    }

    // Создать MediaRecorder
    this.mimeType = this.pickMimeType()
    const options = this.mimeType ? { mimeType: this.mimeType } : undefined
    this.mediaRecorder = new MediaRecorder(this.destination.stream, options)

    this.mediaRecorder.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        this.chunks.push(event.data)
      }
    }

    this.mediaRecorder.start()
    this.isRecording = true
  }

  // Остановить и получить blob
  public async stopCapture(): Promise<{ blob: Blob; mimeType: string }> {
    return new Promise((resolve) => {
      if (!this.mediaRecorder || !this.isRecording) {
        resolve({ blob: new Blob([]), mimeType: "audio/webm" })
        return
      }

      this.mediaRecorder.onstop = () => {
        const blob = new Blob(this.chunks, { type: this.mimeType || "audio/webm" })

        // Очистка ресурсов
        this.cleanup()

        resolve({ blob, mimeType: this.mimeType || "audio/webm" })
      }

      this.mediaRecorder.stop()
      this.isRecording = false
    })
  }

  public isActive(): boolean {
    return this.isRecording
  }

  private cleanup(): void {
    this.micStream?.getTracks().forEach(t => t.stop())
    this.systemStream?.getTracks().forEach(t => t.stop())
    this.destination?.stream.getTracks().forEach(t => t.stop())
    this.audioContext?.close()

    this.micStream = null
    this.systemStream = null
    this.destination = null
    this.audioContext = null
    this.mediaRecorder = null
    this.chunks = []
  }

  private pickMimeType(): string | undefined {
    const candidates = [
      "audio/webm;codecs=opus",
      "audio/webm",
      "audio/ogg;codecs=opus"
    ]
    return candidates.find(t => MediaRecorder.isTypeSupported(t))
  }

  private async startSystemAudioCapture(): Promise<void> {
    // ... существующая логика
  }
}
```

---

### Шаг 2: Обновить VoiceContext

**Файл:** `src/contexts/VoiceContext.tsx`

Добавить/обновить методы для простого PTT:

```typescript
interface VoiceContextType {
  // ... существующие поля

  // Простой PTT
  pttState: {
    isRecording: boolean   // Идёт запись
    isProcessing: boolean  // Обрабатывается (транскрипция/LLM)
    stage: 'idle' | 'recording' | 'transcribing' | 'thinking'
    recordingDuration: number  // Длительность записи в мс
  }

  startSimplePTT: () => Promise<void>     // Начать запись
  stopAndSendPTT: () => Promise<{         // Остановить и отправить
    transcription: string
    response: string
  } | null>
}

// Реализация
const pttCaptureRef = useRef<PushToTalkCaptureHelper | null>(null)
const recordingStartTime = useRef<number>(0)
const durationInterval = useRef<number | null>(null)

const [pttState, setPttState] = useState({
  isRecording: false,
  isProcessing: false,
  stage: 'idle' as const,
  recordingDuration: 0
})

// Начать запись
const startSimplePTT = useCallback(async () => {
  if (pttState.isRecording || pttState.isProcessing) return

  try {
    const capture = new PushToTalkCaptureHelper()
    pttCaptureRef.current = capture
    await capture.startCapture()

    recordingStartTime.current = Date.now()

    // Обновлять длительность каждую секунду
    durationInterval.current = window.setInterval(() => {
      setPttState(prev => ({
        ...prev,
        recordingDuration: Date.now() - recordingStartTime.current
      }))
    }, 100)

    setPttState({
      isRecording: true,
      isProcessing: false,
      stage: 'recording',
      recordingDuration: 0
    })

    setError(null)
  } catch (err) {
    console.error("Failed to start PTT:", err)
    setError("Failed to start recording")
  }
}, [pttState.isRecording, pttState.isProcessing])

// Остановить и отправить
const stopAndSendPTT = useCallback(async () => {
  if (!pttState.isRecording || !pttCaptureRef.current) return null

  // Остановить таймер
  if (durationInterval.current) {
    window.clearInterval(durationInterval.current)
    durationInterval.current = null
  }

  try {
    // Остановить запись
    setPttState(prev => ({
      ...prev,
      isRecording: false,
      isProcessing: true,
      stage: 'transcribing'
    }))

    const { blob, mimeType } = await pttCaptureRef.current.stopCapture()
    pttCaptureRef.current = null

    if (!blob || blob.size === 0) {
      setError("Recording is empty")
      setPttState({ isRecording: false, isProcessing: false, stage: 'idle', recordingDuration: 0 })
      return null
    }

    console.log('[VoiceContext] PTT blob:', { size: blob.size, mimeType })

    // Транскрипция
    const audioBuffer = await blob.arrayBuffer()
    const transcriptionResult = await window.electronAPI.voice.transcribeFull({
      audioData: audioBuffer,
      mimeType
    })

    if (!transcriptionResult?.text?.trim()) {
      setError("Transcription is empty")
      setPttState({ isRecording: false, isProcessing: false, stage: 'idle', recordingDuration: 0 })
      return null
    }

    // LLM
    setPttState(prev => ({ ...prev, stage: 'thinking' }))

    const activeConfig = config || await refreshConfig()
    const llmResult = await window.electronAPI.voice.processQuery({
      chunks: [{ text: transcriptionResult.text, timestamp: Date.now() }],
      question: "",
      systemPrompt: activeConfig?.pttPrompt || undefined
    })

    if (!llmResult?.success) {
      setError(llmResult?.error || "Failed to get response")
      setPttState({ isRecording: false, isProcessing: false, stage: 'idle', recordingDuration: 0 })
      return null
    }

    // Успех
    setPttState({ isRecording: false, isProcessing: false, stage: 'idle', recordingDuration: 0 })

    return {
      transcription: transcriptionResult.text,
      response: llmResult.response || ""
    }
  } catch (err) {
    console.error("Failed to process PTT:", err)
    setError("Failed to process recording")
    setPttState({ isRecording: false, isProcessing: false, stage: 'idle', recordingDuration: 0 })
    return null
  }
}, [pttState.isRecording, config, refreshConfig])
```

---

### Шаг 3: Обновить UI PushToTalk.tsx

**Файл:** `src/_pages/PushToTalk.tsx`

```tsx
function PushToTalkContent() {
  const { t } = useTranslation()
  const {
    pttState,
    startSimplePTT,
    stopAndSendPTT,
    error,
    clearError
  } = useVoice()

  const [response, setResponse] = useState<string | null>(null)

  const dragRegionStyle = { WebkitAppRegion: "drag" } as CSSProperties
  const noDragStyle = { WebkitAppRegion: "no-drag" } as CSSProperties

  // Форматирование времени записи
  const formatDuration = (ms: number) => {
    const seconds = Math.floor(ms / 1000)
    const minutes = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${minutes}:${secs.toString().padStart(2, "0")}`
  }

  // Обработчик кнопки
  const handleButtonClick = async () => {
    if (pttState.isProcessing) return

    if (pttState.isRecording) {
      // Остановить и отправить
      const result = await stopAndSendPTT()
      if (result?.response) {
        setResponse(result.response)
      }
    } else {
      // Начать запись
      setResponse(null)
      await startSimplePTT()
    }
  }

  // Текст статуса
  const statusLabel = useMemo(() => {
    switch (pttState.stage) {
      case 'recording':
        return `Recording ${formatDuration(pttState.recordingDuration)}`
      case 'transcribing':
        return 'Transcribing...'
      case 'thinking':
        return 'Thinking...'
      default:
        return 'Ready'
    }
  }, [pttState.stage, pttState.recordingDuration])

  return (
    <div className="h-screen w-screen bg-transparent text-white">
      <div className="relative flex h-full w-full flex-col items-center gap-3 rounded-xl border border-white/10 bg-black/70 px-4 py-4 backdrop-blur-sm">

        {/* Drag region */}
        <div className="absolute left-0 right-0 top-0 h-6" style={dragRegionStyle} />

        {/* Close button */}
        <button
          type="button"
          onClick={() => window.electronAPI.ptt.hide()}
          className="absolute right-2 top-1 text-xs text-white/50 hover:text-white"
          style={noDragStyle}
        >
          ×
        </button>

        {/* Title */}
        <div className="text-[10px] uppercase tracking-[0.3em] text-white/40">
          Push to Talk
        </div>

        {/* Status */}
        <div className="flex items-center gap-2">
          {pttState.isRecording && (
            <div className="h-3 w-3 animate-pulse rounded-full bg-red-500" />
          )}
          {pttState.isProcessing && (
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
          )}
          <div className="text-sm text-white/70">{statusLabel}</div>
        </div>

        {/* Main Button */}
        <button
          type="button"
          onClick={handleButtonClick}
          disabled={pttState.isProcessing}
          className={`flex h-20 w-20 items-center justify-center rounded-full transition-all ${
            pttState.isProcessing
              ? "cursor-not-allowed bg-white/10"
              : pttState.isRecording
                ? "bg-red-500 hover:bg-red-600 animate-pulse"
                : "bg-blue-500 hover:bg-blue-600"
          }`}
          style={noDragStyle}
        >
          {pttState.isProcessing ? (
            <Spinner />
          ) : pttState.isRecording ? (
            <SendIcon className="h-8 w-8" />
          ) : (
            <MicIcon className="h-8 w-8" />
          )}
        </button>

        {/* Button hint */}
        <div className="text-[11px] text-white/40">
          {pttState.isProcessing
            ? "Processing..."
            : pttState.isRecording
              ? "Click to stop and send"
              : "Click to start recording"}
        </div>

        {/* Response area */}
        <div className="flex w-full flex-1 min-h-0 flex-col">
          <div className="text-[10px] uppercase tracking-[0.2em] text-white/40">
            Response
          </div>
          <div className="mt-1 flex-1 overflow-y-auto rounded-md bg-white/5 p-2 text-xs text-white/80">
            <Markdown content={response || "Response will appear here."} />
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="w-full rounded-md border border-red-500/30 bg-red-500/10 px-2 py-1 text-[11px] text-red-200">
            <div className="flex items-start justify-between gap-2">
              <span>{error}</span>
              <button onClick={clearError} style={noDragStyle}>Dismiss</button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// Иконки
function MicIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="currentColor">
      <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
      <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
    </svg>
  )
}

function SendIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M22 2L11 13" />
      <path d="M22 2L15 22L11 13L2 9L22 2Z" />
    </svg>
  )
}

function Spinner() {
  return (
    <div className="h-6 w-6 animate-spin rounded-full border-2 border-white/30 border-t-white" />
  )
}
```

---

### Шаг 4: Убрать лишнее из useEffect

Убрать автоматический старт `startContinuousRecording` при монтировании:

```tsx
// БЫЛО:
useEffect(() => {
  void startContinuousRecording()
  return () => stopContinuousRecording()
}, [startContinuousRecording, stopContinuousRecording])

// СТАЛО:
// Ничего - пользователь сам нажимает кнопку
```

---

### Шаг 5: Обновить локализацию

**`src/i18n/locales/en.json`:**
```json
{
  "voice": {
    "ptt": {
      "title": "Push to Talk",
      "ready": "Ready",
      "recording": "Recording",
      "transcribing": "Transcribing...",
      "thinking": "Thinking...",
      "clickToRecord": "Click to start recording",
      "clickToSend": "Click to stop and send",
      "processing": "Processing..."
    }
  }
}
```

**`src/i18n/locales/ru.json`:**
```json
{
  "voice": {
    "ptt": {
      "title": "Push to Talk",
      "ready": "Готово",
      "recording": "Запись",
      "transcribing": "Транскрипция...",
      "thinking": "Думаю...",
      "clickToRecord": "Нажми для записи",
      "clickToSend": "Нажми для отправки",
      "processing": "Обработка..."
    }
  }
}
```

---

## Порядок реализации

1. **PushToTalkCaptureHelper** - убедиться что работает правильно
2. **VoiceContext** - добавить `startSimplePTT` и `stopAndSendPTT`
3. **PushToTalk.tsx** - обновить UI на простую кнопку
4. **Убрать useEffect** с автозапуском continuous recording
5. **i18n** - локализация

---

## Схема работы

```
┌─────────────────────────────────────────────────────────┐
│                    Push to Talk Window                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│                   [ Push to Talk ]                      │
│                                                         │
│                      ● Ready                            │
│                                                         │
│                    ┌─────────┐                          │
│                    │   🎤    │  ← Нажми для записи      │
│                    │  (MIC)  │                          │
│                    └─────────┘                          │
│                                                         │
│                Click to start recording                 │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Response                                          │  │
│  │                                                   │  │
│  │ Response will appear here.                        │  │
│  │                                                   │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘

         ↓ Нажал кнопку

┌─────────────────────────────────────────────────────────┐
│                                                         │
│                   ● Recording 0:05                      │
│                   (красный пульсирует)                  │
│                                                         │
│                    ┌─────────┐                          │
│                    │   ➤    │  ← Нажми для отправки     │
│                    │ (SEND)  │     (красная кнопка)     │
│                    └─────────┘                          │
│                                                         │
│                Click to stop and send                   │
│                                                         │
└─────────────────────────────────────────────────────────┘

         ↓ Нажал кнопку

┌─────────────────────────────────────────────────────────┐
│                                                         │
│                   ⟳ Transcribing...                     │
│                                                         │
│                    ┌─────────┐                          │
│                    │   ⟳    │  ← disabled               │
│                    │(spinner)│                          │
│                    └─────────┘                          │
│                                                         │
│                    Processing...                        │
│                                                         │
└─────────────────────────────────────────────────────────┘

         ↓ Готово

┌─────────────────────────────────────────────────────────┐
│                                                         │
│                      ● Ready                            │
│                                                         │
│                    ┌─────────┐                          │
│                    │   🎤    │                          │
│                    └─────────┘                          │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Response                                          │  │
│  │                                                   │  │
│  │ Here is the answer to your question...            │  │
│  │ The algorithm uses a hash map to achieve O(n)...  │  │
│  │                                                   │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Опциональные улучшения

1. **Горячие клавиши** - Space для записи/отправки
2. **Визуализация звука** - показать уровень громкости
3. **Отмена** - кнопка отмены во время записи
4. **История** - сохранять предыдущие ответы
