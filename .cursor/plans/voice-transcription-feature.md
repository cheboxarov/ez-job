# План реализации: Голосовая транскрипция для интервью

## Обзор

Добавление функционала прослушивания и транскрипции голоса во время собеседования. Система будет:
- Захватывать аудио с микрофона (голос пользователя)
- Захватывать системный звук (голос собеседника из Zoom, браузера и т.д.)
- Транскрибировать аудио через конфигурируемый API (OpenAI Whisper-совместимый)
- Отображать транскрипцию в виде чанков (реплик)
- Позволять выбирать чанки и отправлять их в LLM для получения ответа

## Архитектура

### Новые компоненты

```
interview-coder-withoupaywall-opensource/
├── electron/
│   ├── AudioCaptureHelper.ts      # Захват аудио (микрофон + система)
│   ├── TranscriptionHelper.ts     # Отправка аудио на транскрипцию
│   └── ipcHandlers.ts             # + новые IPC handlers для аудио
│
├── src/
│   ├── _pages/
│   │   └── VoiceAssistant.tsx     # Новая страница (отдельное окно)
│   │
│   ├── components/
│   │   └── Voice/
│   │       ├── TranscriptionChunk.tsx    # Компонент одного чанка
│   │       ├── TranscriptionList.tsx     # Список чанков
│   │       ├── AudioControls.tsx         # Кнопки старт/стоп записи
│   │       ├── ChunkSelector.tsx         # Выбор чанков
│   │       └── QuestionInput.tsx         # Ввод вопроса по чанкам
│   │
│   └── contexts/
│       └── VoiceContext.tsx              # Контекст для состояния записи
```

---

## Этап 1: Конфигурация транскрипции

### 1.1 Расширить ConfigHelper.ts

**Файл:** `electron/ConfigHelper.ts`

Добавить поля конфигурации:

```typescript
interface TranscriptionConfig {
  enabled: boolean;
  baseUrl: string;           // URL API транскрипции (default: https://api.openai.com/v1)
  apiKey: string;            // API ключ
  model: string;             // Модель (default: whisper-1)
  language: string;          // Язык (default: ru)
  chunkDurationMs: number;   // Длительность чанка в мс (default: 10000)
}

interface Config {
  // ... существующие поля
  transcription: TranscriptionConfig;
}
```

### 1.2 Добавить UI настроек транскрипции

**Файл:** `src/_pages/Settings.tsx` (или где находятся настройки)

Добавить секцию:
- Base URL для транскрипции
- API Key
- Модель (whisper-1, whisper-large-v3 и т.д.)
- Язык
- Длительность чанка (5-30 секунд)

---

## Этап 2: Захват аудио (Electron main process)

### 2.1 Создать AudioCaptureHelper.ts

**Файл:** `electron/AudioCaptureHelper.ts`

```typescript
import { desktopCapturer } from 'electron';

class AudioCaptureHelper {
  private micStream: MediaStream | null = null;
  private systemStream: MediaStream | null = null;
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private chunkDuration: number = 10000; // 10 секунд

  // Начать захват микрофона
  async startMicrophoneCapture(): Promise<void>

  // Начать захват системного звука
  async startSystemAudioCapture(): Promise<void>

  // Объединить потоки (микрофон + система)
  async startCombinedCapture(): Promise<void>

  // Остановить захват
  stopCapture(): void

  // Получить текущий чанк как WAV/WebM blob
  getCurrentChunk(): Promise<Blob>

  // Callback при готовности чанка
  onChunkReady: (chunk: Blob, timestamp: number) => void
}
```

### 2.2 Захват системного звука

**Для macOS:**
- Использовать `desktopCapturer.getSources({ types: ['screen'] })` с `audio: true`
- Или интегрировать BlackHole/Soundflower для loopback audio
- Альтернатива: использовать `node-audio-capture` или `@nickverlinden/audio-capture`

**Для Windows:**
- Использовать WASAPI loopback через `node-audio-capture`
- Или `desktopCapturer` с аудио от экрана

**Для Linux:**
- PulseAudio monitor через `node-audio-capture`

### 2.3 Формат аудио

- Формат: WAV или WebM (opus)
- Sample rate: 16000 Hz (рекомендуется для Whisper)
- Channels: mono (1 канал)
- Битность: 16-bit PCM

---

## Этап 3: Сервис транскрипции

### 3.1 Создать TranscriptionHelper.ts

**Файл:** `electron/TranscriptionHelper.ts`

```typescript
import FormData from 'form-data';
import axios from 'axios';

interface TranscriptionResult {
  text: string;
  language: string;
  duration: number;
  segments?: Array<{
    start: number;
    end: number;
    text: string;
  }>;
}

class TranscriptionHelper {
  private config: TranscriptionConfig;

  constructor(config: TranscriptionConfig) {
    this.config = config;
  }

  // Транскрибировать аудио чанк
  async transcribe(audioBlob: Blob): Promise<TranscriptionResult> {
    const formData = new FormData();
    formData.append('file', audioBlob, 'audio.wav');
    formData.append('model', this.config.model);
    formData.append('language', this.config.language);
    formData.append('response_format', 'verbose_json');

    const response = await axios.post(
      `${this.config.baseUrl}/audio/transcriptions`,
      formData,
      {
        headers: {
          'Authorization': `Bearer ${this.config.apiKey}`,
          ...formData.getHeaders(),
        },
      }
    );

    return response.data;
  }

  // Валидация конфигурации
  async validateConfig(): Promise<{ valid: boolean; error?: string }>
}
```

### 3.2 Очередь транскрипции

Создать систему очереди для обработки чанков:

```typescript
class TranscriptionQueue {
  private queue: Array<{ blob: Blob; timestamp: number }> = [];
  private isProcessing: boolean = false;

  // Добавить чанк в очередь
  enqueue(blob: Blob, timestamp: number): void

  // Обработать очередь
  async processQueue(): Promise<void>

  // Callback при готовности транскрипции
  onTranscriptionReady: (text: string, timestamp: number) => void
}
```

---

## Этап 4: IPC Handlers

### 4.1 Добавить IPC handlers в ipcHandlers.ts

**Файл:** `electron/ipcHandlers.ts`

```typescript
// Управление записью
ipcMain.handle('voice:start-recording', async () => {
  await audioCaptureHelper.startCombinedCapture();
  return { success: true };
});

ipcMain.handle('voice:stop-recording', async () => {
  audioCaptureHelper.stopCapture();
  return { success: true };
});

ipcMain.handle('voice:get-recording-status', () => {
  return audioCaptureHelper.isRecording();
});

// Транскрипция
ipcMain.handle('voice:transcribe-chunk', async (_, audioData: ArrayBuffer) => {
  const blob = new Blob([audioData], { type: 'audio/wav' });
  return await transcriptionHelper.transcribe(blob);
});

// Конфигурация
ipcMain.handle('voice:get-config', () => {
  return configHelper.getTranscriptionConfig();
});

ipcMain.handle('voice:update-config', async (_, config: TranscriptionConfig) => {
  await configHelper.updateTranscriptionConfig(config);
  return { success: true };
});

ipcMain.handle('voice:validate-config', async (_, config: TranscriptionConfig) => {
  return await transcriptionHelper.validateConfig(config);
});

// События от main к renderer
// При готовности нового чанка транскрипции
mainWindow.webContents.send('voice:transcription-ready', { text, timestamp, id });
```

### 4.2 Обновить preload.ts

```typescript
contextBridge.exposeInMainWorld('electronAPI', {
  // ... существующие методы

  // Voice API
  voice: {
    startRecording: () => ipcRenderer.invoke('voice:start-recording'),
    stopRecording: () => ipcRenderer.invoke('voice:stop-recording'),
    getRecordingStatus: () => ipcRenderer.invoke('voice:get-recording-status'),
    getConfig: () => ipcRenderer.invoke('voice:get-config'),
    updateConfig: (config) => ipcRenderer.invoke('voice:update-config', config),
    validateConfig: (config) => ipcRenderer.invoke('voice:validate-config', config),

    // Listeners
    onTranscriptionReady: (callback) => {
      ipcRenderer.on('voice:transcription-ready', (_, data) => callback(data));
      return () => ipcRenderer.removeAllListeners('voice:transcription-ready');
    },
  },
});
```

---

## Этап 5: Frontend компоненты

### 5.1 VoiceContext.tsx

**Файл:** `src/contexts/VoiceContext.tsx`

```typescript
interface TranscriptionChunk {
  id: string;
  text: string;
  timestamp: number;
  selected: boolean;
}

interface VoiceContextType {
  isRecording: boolean;
  chunks: TranscriptionChunk[];
  selectedChunks: TranscriptionChunk[];

  startRecording: () => Promise<void>;
  stopRecording: () => Promise<void>;
  toggleChunkSelection: (id: string) => void;
  selectAllChunks: () => void;
  clearSelection: () => void;
  clearAllChunks: () => void;
}
```

### 5.2 VoiceAssistant.tsx (главная страница)

**Файл:** `src/_pages/VoiceAssistant.tsx`

Структура страницы:

```
┌─────────────────────────────────────────────────────────┐
│  [🔴 Recording]  [⏹ Stop]  [⚙ Settings]                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ [✓] 10:23:15 - "Расскажите о своем опыте..."    │   │
│  │ [✓] 10:23:25 - "Я работал над проектом..."      │   │
│  │ [ ] 10:23:35 - "Какие технологии использовали?" │   │
│  │ [ ] 10:23:45 - "Мы использовали React и..."     │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  [Select All] [Clear Selection] [Clear All]             │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────┐   │
│  │ Дополнительный вопрос (опционально):            │   │
│  │ [                                            ]   │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  [🚀 Отправить в LLM]                                   │
├─────────────────────────────────────────────────────────┤
│  Response from LLM:                                     │
│  ┌─────────────────────────────────────────────────┐   │
│  │ ... ответ от нейросети ...                      │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 5.3 Компоненты

**TranscriptionChunk.tsx:**
```typescript
interface Props {
  chunk: TranscriptionChunk;
  onToggle: (id: string) => void;
}

// Отображает один чанк с чекбоксом, временем и текстом
```

**TranscriptionList.tsx:**
```typescript
interface Props {
  chunks: TranscriptionChunk[];
  onToggle: (id: string) => void;
}

// Список чанков с автоскроллом к новым
```

**AudioControls.tsx:**
```typescript
interface Props {
  isRecording: boolean;
  onStart: () => void;
  onStop: () => void;
}

// Кнопки управления записью + индикатор статуса
```

**QuestionInput.tsx:**
```typescript
interface Props {
  onSubmit: (question: string, chunks: TranscriptionChunk[]) => void;
  selectedChunks: TranscriptionChunk[];
  disabled: boolean;
}

// Поле ввода вопроса + кнопка отправки
```

---

## Этап 6: Интеграция с LLM

### 6.1 Обработка выбранных чанков

**Файл:** `electron/ProcessingHelper.ts` (расширить)

```typescript
async processVoiceQuery(
  chunks: TranscriptionChunk[],
  question?: string
): Promise<string> {
  const context = chunks
    .map(c => `[${formatTime(c.timestamp)}] ${c.text}`)
    .join('\n');

  const systemPrompt = `You are an interview assistant.
The user is in an interview and needs help answering questions.
Below is the transcription of the conversation.

Transcription:
${context}

${question ? `User's question: ${question}` : 'Please provide a helpful response to the latest question in the conversation.'}`;

  const messages = [
    { role: 'system', content: systemPrompt },
    { role: 'user', content: question || 'Please help me answer this.' },
  ];

  return await this.callLLM(messages);
}
```

### 6.2 IPC для обработки

```typescript
ipcMain.handle('voice:process-query', async (_, { chunks, question }) => {
  return await processingHelper.processVoiceQuery(chunks, question);
});
```

---

## Этап 7: Отдельное окно

### 7.1 Создание второго окна

**Файл:** `electron/main.ts`

```typescript
let voiceWindow: BrowserWindow | null = null;

function createVoiceWindow() {
  voiceWindow = new BrowserWindow({
    width: 500,
    height: 700,
    title: 'Voice Assistant',
    webPreferences: {
      preload: join(__dirname, 'preload.js'),
      contextIsolation: true,
    },
    // Опционально: always on top
    alwaysOnTop: true,
  });

  voiceWindow.loadURL(`${RENDERER_URL}/#/voice`);
}

// Горячая клавиша для открытия/закрытия окна голосового помощника
globalShortcut.register('CommandOrControl+Shift+V', () => {
  if (voiceWindow && !voiceWindow.isDestroyed()) {
    voiceWindow.isVisible() ? voiceWindow.hide() : voiceWindow.show();
  } else {
    createVoiceWindow();
  }
});
```

### 7.2 Роутинг

**Файл:** `src/App.tsx`

```typescript
<Routes>
  {/* ... существующие роуты */}
  <Route path="/voice" element={<VoiceAssistant />} />
</Routes>
```

---

## Этап 8: Зависимости

### 8.1 npm packages

```bash
npm install --save \
  @nickverlinden/audio-capture  # Для захвата системного звука
  audiobuffer-to-wav            # Конвертация в WAV
  form-data                     # Для отправки multipart/form-data
```

### 8.2 Опциональные зависимости для macOS

Для захвата системного звука на macOS может потребоваться:
- BlackHole (виртуальное аудио устройство) - https://existential.audio/blackhole/
- Или использовать Screen Capture API с аудио

---

## Порядок реализации

### Фаза 1: Базовая инфраструктура
1. [ ] Расширить ConfigHelper.ts для хранения настроек транскрипции
2. [ ] Создать TranscriptionHelper.ts для работы с API
3. [ ] Добавить IPC handlers для конфигурации
4. [ ] Создать UI настроек транскрипции

### Фаза 2: Захват аудио
5. [ ] Создать AudioCaptureHelper.ts
6. [ ] Реализовать захват микрофона
7. [ ] Реализовать захват системного звука (platform-specific)
8. [ ] Добавить IPC handlers для управления записью

### Фаза 3: Frontend
9. [ ] Создать VoiceContext.tsx
10. [ ] Создать компоненты Voice/*
11. [ ] Создать страницу VoiceAssistant.tsx
12. [ ] Настроить роутинг

### Фаза 4: Интеграция
13. [ ] Интегрировать с ProcessingHelper для отправки в LLM
14. [ ] Создать отдельное окно для голосового помощника
15. [ ] Добавить глобальную горячую клавишу

### Фаза 5: Тестирование и полировка
16. [ ] Тестирование на разных платформах (macOS, Windows)
17. [ ] Обработка ошибок и edge cases
18. [ ] Оптимизация производительности

---

## Технические заметки

### Whisper API совместимость

OpenAI Whisper API endpoint: `POST /v1/audio/transcriptions`

Параметры:
- `file` (required): аудио файл (wav, mp3, m4a, webm, ...)
- `model` (required): модель (whisper-1)
- `language` (optional): язык (ru, en, ...)
- `response_format` (optional): json, verbose_json, text, srt, vtt

Совместимые альтернативы:
- Groq Whisper API
- LocalAI с Whisper
- Собственный сервер с faster-whisper

### Обработка тишины

- Детектировать тишину и не отправлять пустые чанки
- Использовать VAD (Voice Activity Detection) для оптимизации
- Можно использовать WebRTC VAD или простой threshold по громкости

### Память и производительность

- Ограничить количество хранимых чанков (например, последние 50)
- Очищать старые чанки автоматически
- Использовать виртуализацию списка при большом количестве чанков
