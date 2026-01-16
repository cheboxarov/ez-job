# Continuous Recording Mode (Режим постоянной записи)

## Текущее поведение (Push-to-Talk)

1. Пользователь нажимает кнопку → начинается запись
2. Пользователь нажимает снова → запись останавливается
3. Аудио транскрибируется и отправляется в LLM
4. Отображается ответ

**Проблема:** Пользователь должен заранее знать, когда начнётся важная информация.

---

## Новое поведение (Continuous Recording)

1. **Запись идёт постоянно** с момента открытия окна
2. Аудио хранится в **кольцевом буфере** (последние 5 минут)
3. Пользователь выбирает временной отрезок: **1 мин / 3 мин / 5 мин**
4. При нажатии кнопки отправляется соответствующий отрезок
5. Происходит транскрипция → LLM → ответ

**Преимущество:** Можно "отмотать назад" и получить ответ на то, что уже прозвучало.

---

## Архитектура изменений

### 1. Новый AudioCapture helper с кольцевым буфером

**Файл:** `src/components/Voice/ContinuousRecordingHelper.ts`

```typescript
export interface AudioSegment {
  blob: Blob
  startTime: number
  endTime: number
  mimeType: string
}

export class ContinuousRecordingHelper {
  private micStream: MediaStream | null = null
  private systemStream: MediaStream | null = null
  private audioContext: AudioContext | null = null
  private destination: MediaStreamAudioDestinationNode | null = null
  private mediaRecorder: MediaRecorder | null = null
  private isRecording = false
  private mimeType: string | undefined

  // Кольцевой буфер - хранит сегменты аудио
  private segments: AudioSegment[] = []
  private currentSegmentChunks: Blob[] = []
  private currentSegmentStartTime: number = 0

  // Настройки буфера
  private readonly SEGMENT_DURATION_MS = 10_000  // 10 секунд на сегмент
  private readonly MAX_BUFFER_DURATION_MS = 5 * 60 * 1000  // 5 минут

  private segmentTimer: number | null = null

  public async startCapture(): Promise<void> {
    // Инициализация микрофона и системного аудио
    // Запуск MediaRecorder с сегментацией каждые 10 секунд
    // При получении сегмента - добавляем в кольцевой буфер
    // Удаляем старые сегменты (>5 минут)
  }

  public stopCapture(): void {
    // Остановка записи и очистка ресурсов
  }

  public getLastMinutes(minutes: number): Promise<{ blob: Blob; mimeType: string }> {
    // Извлекает последние N минут из буфера
    // Объединяет сегменты в один Blob
    const targetDuration = minutes * 60 * 1000
    const now = Date.now()
    const cutoffTime = now - targetDuration

    const relevantSegments = this.segments.filter(s => s.endTime > cutoffTime)
    // Объединить Blob-ы и вернуть
  }

  public getBufferDuration(): number {
    // Возвращает текущую длительность буфера в мс
  }

  public isActive(): boolean {
    return this.isRecording
  }

  private rotateBuffer(): void {
    // Удаляет сегменты старше MAX_BUFFER_DURATION_MS
    const cutoffTime = Date.now() - this.MAX_BUFFER_DURATION_MS
    this.segments = this.segments.filter(s => s.endTime > cutoffTime)
  }
}
```

### 2. Обновить типы

**Файл:** `src/types/voice.ts`

```typescript
// Добавить новые типы
export type TimeSelection = 1 | 3 | 5  // минуты

export interface ContinuousRecordingState {
  isRecording: boolean      // Запись активна
  isProcessing: boolean     // Идёт транскрипция/LLM
  bufferDuration: number    // Текущая длительность буфера (мс)
  stage: 'idle' | 'recording' | 'extracting' | 'transcribing' | 'thinking'
}

// Обновить PushToTalkState для обратной совместимости
export interface PushToTalkState {
  isRecording: boolean
  isProcessing: boolean
  audioBuffer: Blob | null
  stage: 'idle' | 'recording' | 'transcribing' | 'thinking'
  // Новые поля для continuous режима
  bufferDuration?: number
  continuousMode?: boolean
}
```

### 3. Обновить VoiceContext

**Файл:** `src/contexts/VoiceContext.tsx`

Добавить новые методы и состояние:

```typescript
interface VoiceContextType {
  // ... существующие поля

  // Новые методы для continuous recording
  startContinuousRecording: () => Promise<void>
  stopContinuousRecording: () => void
  sendLastMinutes: (minutes: TimeSelection) => Promise<{
    transcription: string
    response: string
  } | null>
  bufferDuration: number  // Текущая длительность буфера
}

// В VoiceProvider
const continuousRef = useRef<ContinuousRecordingHelper | null>(null)
const [bufferDuration, setBufferDuration] = useState(0)

// Обновление длительности буфера каждую секунду
useEffect(() => {
  if (!pttState.isRecording || !continuousRef.current) return

  const interval = setInterval(() => {
    const duration = continuousRef.current?.getBufferDuration() || 0
    setBufferDuration(duration)
  }, 1000)

  return () => clearInterval(interval)
}, [pttState.isRecording])

const startContinuousRecording = useCallback(async () => {
  // Проверка конфига
  // Создание ContinuousRecordingHelper
  // Запуск записи
  // Обновление состояния
}, [])

const stopContinuousRecording = useCallback(() => {
  continuousRef.current?.stopCapture()
  continuousRef.current = null
  setPttState(prev => ({ ...prev, isRecording: false, stage: 'idle' }))
}, [])

const sendLastMinutes = useCallback(async (minutes: TimeSelection) => {
  if (!continuousRef.current) return null

  setPttState(prev => ({ ...prev, isProcessing: true, stage: 'extracting' }))

  try {
    // 1. Извлечь аудио из буфера
    const { blob, mimeType } = await continuousRef.current.getLastMinutes(minutes)

    if (blob.size === 0) {
      setError('Буфер записи пуст')
      return null
    }

    // 2. Транскрипция
    setPttState(prev => ({ ...prev, stage: 'transcribing' }))
    const audioBuffer = await blob.arrayBuffer()
    const transcriptionResult = await window.electronAPI.voice.transcribeFull({
      audioData: audioBuffer,
      mimeType
    })

    if (!transcriptionResult?.text?.trim()) {
      setError('Транскрипция пуста')
      return null
    }

    // 3. LLM
    setPttState(prev => ({ ...prev, stage: 'thinking' }))
    const llmResult = await window.electronAPI.voice.processQuery({
      chunks: [{ text: transcriptionResult.text, timestamp: Date.now() }],
      question: '',
      systemPrompt: config?.pttPrompt
    })

    if (!llmResult?.success) {
      setError(llmResult?.error || 'Ошибка LLM')
      return null
    }

    setPttState(prev => ({ ...prev, isProcessing: false, stage: 'recording' }))

    return {
      transcription: transcriptionResult.text,
      response: llmResult.response || ''
    }
  } catch (err) {
    setError('Ошибка обработки')
    setPttState(prev => ({ ...prev, isProcessing: false, stage: 'recording' }))
    return null
  }
}, [config])
```

### 4. Обновить UI компонент PushToTalk

**Файл:** `src/_pages/PushToTalk.tsx`

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
    clearError
  } = useVoice()

  const [response, setResponse] = useState<string | null>(null)
  const [selectedTime, setSelectedTime] = useState<TimeSelection>(1)

  // Автозапуск записи при монтировании
  useEffect(() => {
    startContinuousRecording()
    return () => stopContinuousRecording()
  }, [])

  // Форматирование длительности буфера
  const formatDuration = (ms: number) => {
    const seconds = Math.floor(ms / 1000)
    const minutes = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${minutes}:${secs.toString().padStart(2, '0')}`
  }

  // Доступные варианты времени (в зависимости от буфера)
  const availableTimes: TimeSelection[] = useMemo(() => {
    const times: TimeSelection[] = []
    if (bufferDuration >= 60_000) times.push(1)
    if (bufferDuration >= 180_000) times.push(3)
    if (bufferDuration >= 300_000) times.push(5)
    return times.length > 0 ? times : [1]
  }, [bufferDuration])

  const handleSend = async () => {
    if (pttState.isProcessing) return
    const result = await sendLastMinutes(selectedTime)
    if (result?.response) {
      setResponse(result.response)
    }
  }

  const statusLabel = useMemo(() => {
    switch (pttState.stage) {
      case 'recording':
        return `${t('voice.ptt.recording')} (${formatDuration(bufferDuration)})`
      case 'extracting':
        return t('voice.ptt.extracting')
      case 'transcribing':
        return t('voice.ptt.transcribing')
      case 'thinking':
        return t('voice.ptt.thinking')
      default:
        return t('voice.ptt.idle')
    }
  }, [pttState.stage, bufferDuration, t])

  return (
    <div className="h-screen w-screen bg-transparent text-white">
      <div className="relative flex h-full w-full flex-col items-center gap-2 rounded-xl border border-white/10 bg-black/70 px-3 py-3 backdrop-blur-sm">
        {/* Заголовок */}
        <div className="absolute left-0 right-0 top-0 h-6" style={dragRegionStyle} />
        <button
          type="button"
          onClick={() => window.electronAPI.ptt.hide()}
          className="absolute right-2 top-1 text-xs text-white/50 hover:text-white"
        >
          x
        </button>

        <div className="text-[10px] uppercase tracking-[0.3em] text-white/40">
          Continuous Recording
        </div>

        {/* Индикатор записи */}
        <div className="flex items-center gap-2">
          {pttState.isRecording && (
            <div className="h-3 w-3 rounded-full bg-red-500 animate-pulse" />
          )}
          <div className="text-xs text-white/60">{statusLabel}</div>
        </div>

        {/* Выбор временного интервала */}
        <div className="flex gap-2 mt-2">
          {([1, 3, 5] as TimeSelection[]).map((time) => (
            <button
              key={time}
              type="button"
              disabled={!availableTimes.includes(time) || pttState.isProcessing}
              onClick={() => setSelectedTime(time)}
              className={`px-3 py-1.5 rounded-md text-xs transition ${
                selectedTime === time
                  ? 'bg-blue-500 text-white'
                  : availableTimes.includes(time)
                    ? 'bg-white/10 text-white hover:bg-white/20'
                    : 'bg-white/5 text-white/30 cursor-not-allowed'
              }`}
            >
              {time} мин
            </button>
          ))}
        </div>

        {/* Кнопка отправки */}
        <button
          type="button"
          onClick={handleSend}
          disabled={pttState.isProcessing || bufferDuration < 1000}
          className={`mt-2 flex h-14 w-14 items-center justify-center rounded-full transition ${
            pttState.isProcessing
              ? 'bg-white/10 cursor-not-allowed'
              : 'bg-blue-500 text-white hover:bg-blue-600'
          }`}
        >
          {pttState.isProcessing ? (
            <Spinner />
          ) : (
            <SendIcon className="h-6 w-6" />
          )}
        </button>

        <div className="text-[10px] text-white/40">
          {pttState.isProcessing
            ? 'Обрабатывается...'
            : `Отправить последние ${selectedTime} мин`
          }
        </div>

        {/* Ответ */}
        <div className="flex w-full flex-1 min-h-0 flex-col mt-2">
          <div className="text-[10px] uppercase tracking-[0.2em] text-white/40">
            Response
          </div>
          <div className="mt-1 flex-1 overflow-y-auto rounded-md bg-white/5 p-2 text-xs text-white/80">
            <Markdown content={response || "Response will appear here."} />
          </div>
        </div>

        {/* Ошибки */}
        {error && (
          <div className="w-full rounded-md border border-red-500/30 bg-red-500/10 px-2 py-1 text-[11px] text-red-200">
            <div className="flex items-start justify-between gap-2">
              <span>{error}</span>
              <button type="button" onClick={clearError}>Dismiss</button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
```

### 5. Добавить иконку отправки

**В файле:** `src/_pages/PushToTalk.tsx`

```tsx
function SendIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      className={className}
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M22 2L11 13" />
      <path d="M22 2L15 22L11 13L2 9L22 2Z" />
    </svg>
  )
}
```

### 6. Обновить локализацию

**Файл:** `src/i18n/locales/en.json`

```json
{
  "voice": {
    "ptt": {
      "recording": "Recording",
      "extracting": "Extracting audio...",
      "transcribing": "Transcribing...",
      "thinking": "Thinking...",
      "idle": "Ready",
      "sendLast": "Send last {{minutes}} min",
      "processing": "Processing..."
    }
  }
}
```

**Файл:** `src/i18n/locales/ru.json`

```json
{
  "voice": {
    "ptt": {
      "recording": "Запись",
      "extracting": "Извлечение аудио...",
      "transcribing": "Транскрипция...",
      "thinking": "Генерация ответа...",
      "idle": "Готов",
      "sendLast": "Отправить последние {{minutes}} мин",
      "processing": "Обрабатывается..."
    }
  }
}
```

---

## Порядок реализации

### Фаза 1: Backend (ContinuousRecordingHelper)
1. [ ] Создать `src/components/Voice/ContinuousRecordingHelper.ts`
2. [ ] Реализовать кольцевой буфер с сегментами по 10 секунд
3. [ ] Реализовать метод `getLastMinutes()`
4. [ ] Добавить метод `getBufferDuration()`

### Фаза 2: Context
5. [ ] Обновить типы в `src/types/voice.ts`
6. [ ] Добавить `ContinuousRecordingState` в VoiceContext
7. [ ] Реализовать `startContinuousRecording()`
8. [ ] Реализовать `stopContinuousRecording()`
9. [ ] Реализовать `sendLastMinutes()`
10. [ ] Добавить периодическое обновление `bufferDuration`

### Фаза 3: UI
11. [ ] Обновить `PushToTalk.tsx` с новым дизайном
12. [ ] Добавить кнопки выбора времени (1/3/5 мин)
13. [ ] Добавить индикатор длительности буфера
14. [ ] Автозапуск записи при открытии окна
15. [ ] Добавить иконку отправки

### Фаза 4: Локализация
16. [ ] Обновить `en.json`
17. [ ] Обновить `ru.json`

### Фаза 5: Тестирование
18. [ ] Проверить запись с микрофона
19. [ ] Проверить запись системного аудио
20. [ ] Проверить работу кольцевого буфера (не превышает 5 минут)
21. [ ] Проверить извлечение различных временных отрезков
22. [ ] Проверить транскрипцию и LLM ответы

---

## Технические детали

### Кольцевой буфер

- Аудио разбивается на сегменты по 10 секунд
- Каждый сегмент хранится как отдельный Blob с метаданными (startTime, endTime)
- Максимальная длительность буфера: 5 минут (30 сегментов)
- При превышении лимита - старые сегменты удаляются
- При извлечении - сегменты объединяются в один Blob

### Оптимизация памяти

- Сегменты по 10 секунд минимизируют фрагментацию
- Регулярная ротация буфера предотвращает утечки памяти
- При закрытии окна все ресурсы освобождаются

### UX соображения

- Запись начинается автоматически при открытии окна
- Кнопки времени становятся активными по мере накопления буфера
- Индикатор записи показывает текущую длительность
- При обработке кнопки блокируются, но запись продолжается

---

## Возможные улучшения (future)

1. **Настраиваемые интервалы** - пользователь может выбрать свои временные интервалы
2. **Визуализация аудио** - волновая форма текущего буфера
3. **Горячие клавиши** - быстрая отправка по Cmd+1/2/3
4. **История запросов** - сохранение предыдущих транскрипций и ответов
5. **Автоопределение речи** - автоматическая отправка при паузе в разговоре
