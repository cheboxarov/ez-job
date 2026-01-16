# Стелс-окно для Voice Assistant (PTT режим)

## Текущая ситуация

### Основное окно (mainWindow) - СТЕЛС
Расположение: **левый верхний угол**

Свойства для невидимости при трансляции:
```typescript
{
  transparent: true,
  frame: false,
  hasShadow: false,
  backgroundColor: "#00000000",
  skipTaskbar: true,
  type: "panel",
  titleBarStyle: "hidden",
  // ...
}

// После создания:
mainWindow.setContentProtection(true)              // Защита от захвата
mainWindow.setHiddenInMissionControl(true)         // Скрыть в Mission Control
mainWindow.setAlwaysOnTop(true, "screen-saver", 1) // Поверх всех окон
mainWindow.setVisibleOnAllWorkspaces(true)         // На всех workspace
mainWindow.setWindowButtonVisibility(false)
```

### Текущее VoiceWindow - ОБЫЧНОЕ ОКНО
```typescript
{
  width: 500,
  height: 700,
  title: "Voice Assistant",
  alwaysOnTop: true,
  backgroundColor: "#0b0b0b",
  show: true
  // Нет стелс-свойств!
}
```

---

## Задача

Создать **новое стелс-окно** для Push-to-Talk режима:
- Расположение: **правый верхний угол**
- Те же свойства невидимости как у mainWindow
- Компактный UI для PTT режима

---

## План реализации

### 1. Создать функцию `createPTTWindow()` в `electron/main.ts`

```typescript
function createPTTWindow(): void {
  if (state.pttWindow && !state.pttWindow.isDestroyed()) {
    state.pttWindow.focus()
    return
  }

  const primaryDisplay = screen.getPrimaryDisplay()
  const workArea = primaryDisplay.workAreaSize

  // Размеры PTT окна (компактное)
  const pttWidth = 350
  const pttHeight = 200

  // Позиция: правый верхний угол
  const pttX = workArea.width - pttWidth - 20  // 20px отступ от края
  const pttY = 50

  const windowSettings: Electron.BrowserWindowConstructorOptions = {
    width: pttWidth,
    height: pttHeight,
    x: pttX,
    y: pttY,

    // === СТЕЛС СВОЙСТВА (как у mainWindow) ===
    alwaysOnTop: true,
    frame: false,
    transparent: true,
    fullscreenable: false,
    hasShadow: false,
    backgroundColor: "#00000000",
    focusable: true,
    skipTaskbar: true,
    type: "panel",
    titleBarStyle: "hidden",
    movable: true,
    resizable: false,  // Фиксированный размер для PTT

    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: isDev
        ? path.join(__dirname, "../dist-electron/preload.js")
        : path.join(__dirname, "preload.js")
    }
  }

  state.pttWindow = new BrowserWindow(windowSettings)

  // === СТЕЛС НАСТРОЙКИ ПОСЛЕ СОЗДАНИЯ ===
  state.pttWindow.setContentProtection(true)
  state.pttWindow.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true })
  state.pttWindow.setAlwaysOnTop(true, "screen-saver", 1)

  if (process.platform === "darwin") {
    state.pttWindow.setHiddenInMissionControl(true)
    state.pttWindow.setWindowButtonVisibility(false)
    state.pttWindow.setBackgroundColor("#00000000")
    state.pttWindow.setSkipTaskbar(true)
    state.pttWindow.setHasShadow(false)
  }

  // Загрузка страницы PTT
  if (isDev) {
    state.pttWindow.loadURL("http://localhost:54321/#/ptt")
  } else {
    const indexPath = path.join(__dirname, "../dist/index.html")
    state.pttWindow.loadFile(indexPath, { hash: "/ptt" })
  }

  state.pttWindow.on("closed", () => {
    state.pttWindow = null
  })
}
```

### 2. Добавить state для PTT окна

```typescript
const state = {
  mainWindow: null as BrowserWindow | null,
  voiceWindow: null as BrowserWindow | null,
  pttWindow: null as BrowserWindow | null,  // ДОБАВИТЬ
  // ...
}
```

### 3. Функции управления PTT окном

```typescript
// Переменные состояния
let pttWindowVisible = true
let pttWindowPosition: { x: number; y: number } | null = null

function hidePTTWindow(): void {
  if (!state.pttWindow?.isDestroyed()) {
    const bounds = state.pttWindow.getBounds()
    pttWindowPosition = { x: bounds.x, y: bounds.y }
    state.pttWindow.setIgnoreMouseEvents(true, { forward: true })
    state.pttWindow.setOpacity(0)
    pttWindowVisible = false
  }
}

function showPTTWindow(): void {
  if (!state.pttWindow?.isDestroyed()) {
    if (pttWindowPosition) {
      state.pttWindow.setPosition(pttWindowPosition.x, pttWindowPosition.y)
    }
    state.pttWindow.setIgnoreMouseEvents(false)
    state.pttWindow.setOpacity(1)
    pttWindowVisible = true
  }
}

function togglePTTWindow(): void {
  if (state.pttWindow && !state.pttWindow.isDestroyed()) {
    if (pttWindowVisible) {
      hidePTTWindow()
    } else {
      showPTTWindow()
    }
    return
  }
  createPTTWindow()
}
```

### 4. Горячая клавиша для PTT окна

```typescript
// В initializeApp()
globalShortcut.register("CommandOrControl+Shift+P", () => {
  togglePTTWindow()
})
```

### 5. Создать компонент PTT UI

**Файл:** `src/_pages/PushToTalk.tsx`

```tsx
export default function PushToTalk() {
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [response, setResponse] = useState<string | null>(null)

  const handleToggleRecording = async () => {
    if (isRecording) {
      // Остановить и обработать
      setIsRecording(false)
      setIsProcessing(true)

      const result = await window.electronAPI.voice.stopPTTAndProcess()
      setResponse(result.response)
      setIsProcessing(false)
    } else {
      // Начать запись
      await window.electronAPI.voice.startPTTRecording()
      setIsRecording(true)
      setResponse(null)
    }
  }

  return (
    <div className="h-screen w-screen bg-black/80 backdrop-blur-sm rounded-lg p-4
                    flex flex-col items-center justify-center gap-4
                    border border-white/10">
      {/* Drag area */}
      <div className="absolute top-0 left-0 right-0 h-6 -webkit-app-region-drag" />

      {/* Close button */}
      <button
        className="absolute top-2 right-2 text-white/50 hover:text-white"
        onClick={() => window.electronAPI.ptt.hide()}
      >
        ✕
      </button>

      {/* Recording button */}
      <button
        onClick={handleToggleRecording}
        disabled={isProcessing}
        className={`
          w-20 h-20 rounded-full flex items-center justify-center
          transition-all duration-200
          ${isRecording
            ? 'bg-red-500 animate-pulse scale-110'
            : 'bg-white/10 hover:bg-white/20'}
          ${isProcessing ? 'opacity-50' : ''}
        `}
      >
        {isProcessing ? (
          <Spinner />
        ) : isRecording ? (
          <StopIcon />
        ) : (
          <MicIcon />
        )}
      </button>

      {/* Status */}
      <div className="text-sm text-white/60">
        {isProcessing ? 'Processing...' : isRecording ? 'Recording...' : 'Click to record'}
      </div>

      {/* Response (scrollable) */}
      {response && (
        <div className="mt-2 max-h-24 overflow-y-auto text-xs text-white/80
                        bg-white/5 rounded p-2 w-full">
          {response}
        </div>
      )}
    </div>
  )
}
```

### 6. Добавить роут

**Файл:** `src/App.tsx` или роутер

```tsx
<Route path="/ptt" element={<PushToTalk />} />
```

### 7. IPC handlers для PTT

**Файл:** `electron/ipcHandlers.ts`

```typescript
// Начать PTT запись
ipcMain.handle('ptt:start-recording', async () => {
  // Инициализировать запись без разбивки на чанки
  await startPTTCapture()
  return { success: true }
})

// Остановить и обработать
ipcMain.handle('ptt:stop-and-process', async () => {
  // 1. Остановить запись, получить аудио
  const audioBuffer = await stopPTTCapture()

  // 2. Транскрибировать
  const transcription = await transcriptionHelper.transcribe(audioBuffer)

  // 3. Отправить в LLM
  const response = await processWithLLM(transcription.text)

  return { success: true, response }
})

// Скрыть PTT окно
ipcMain.handle('ptt:hide', () => {
  hidePTTWindow()
  return { success: true }
})
```

### 8. Preload для PTT

**Файл:** `electron/preload.ts`

```typescript
ptt: {
  startRecording: () => ipcRenderer.invoke('ptt:start-recording'),
  stopAndProcess: () => ipcRenderer.invoke('ptt:stop-and-process'),
  hide: () => ipcRenderer.invoke('ptt:hide')
}
```

---

## Структура окон

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  ┌─────────────┐                    ┌─────────────┐    │
│  │             │                    │             │    │
│  │  mainWindow │                    │  pttWindow  │    │
│  │  (слева)    │                    │  (справа)   │    │
│  │             │                    │             │    │
│  │  800x600    │                    │  350x200    │    │
│  │             │                    │             │    │
│  └─────────────┘                    └─────────────┘    │
│                                                         │
│                      Screen                             │
└─────────────────────────────────────────────────────────┘
```

---

## Порядок реализации

1. **electron/main.ts** - добавить `pttWindow` в state, создать `createPTTWindow()`, `togglePTTWindow()`
2. **electron/main.ts** - зарегистрировать горячую клавишу `Cmd+Shift+P`
3. **electron/ipcHandlers.ts** - добавить IPC handlers для PTT
4. **electron/preload.ts** - добавить preload API для PTT
5. **src/types/electron.d.ts** - типы для нового API
6. **src/_pages/PushToTalk.tsx** - создать компактный UI
7. **src/App.tsx** - добавить роут `/ptt`
8. **Стили** - добавить стили для прозрачного фона с blur

---

## Ключевые отличия от voiceWindow

| Свойство | voiceWindow (текущий) | pttWindow (новый) |
|----------|----------------------|-------------------|
| Прозрачность | Нет | Да |
| Защита от захвата | Нет | Да |
| Позиция | Центр | Правый верх |
| Размер | 500x700 | 350x200 |
| Frame | Да | Нет |
| Режим | Continuous chunks | Push-to-Talk |
