import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState
} from "react"
import { AudioCaptureHelper } from "../components/Voice/AudioCaptureHelper"
import { ContinuousRecordingHelper } from "../components/Voice/ContinuousRecordingHelper"
import { PushToTalkCaptureHelper } from "../components/Voice/PushToTalkCaptureHelper"
import {
  PushToTalkState,
  TimeSelection,
  TranscriptionChunk,
  VoiceMode,
  VoiceTranscriptionConfig
} from "../types/voice"

interface VoiceContextType {
  mode: VoiceMode
  isRecording: boolean
  pttState: PushToTalkState
  chunks: TranscriptionChunk[]
  selectedChunks: TranscriptionChunk[]
  config: VoiceTranscriptionConfig | null
  error: string | null
  sendDirectly: boolean
  setSendDirectly: (value: boolean) => void
  setMode: (mode: VoiceMode) => void
  startRecording: () => Promise<void>
  stopRecording: () => Promise<void>
  startPTTRecording: () => Promise<void>
  stopPTTRecording: () => Promise<{
    transcription: string
    response: string
  } | null>
  startContinuousRecording: () => Promise<void>
  stopContinuousRecording: () => void
  sendLastMinutes: (minutes: TimeSelection, context?: string) => Promise<{
    transcription: string
    response: string
  } | null>
  bufferDuration: number
  toggleChunkSelection: (id: string) => void
  selectAllChunks: () => void
  clearSelection: () => void
  clearAllChunks: () => void
  refreshConfig: () => Promise<VoiceTranscriptionConfig | null>
  clearError: () => void
}

const VoiceContext = createContext<VoiceContextType | undefined>(undefined)

const MAX_CHUNKS = 50

export const VoiceProvider: React.FC<{ children: React.ReactNode }> = ({
  children
}) => {
  const [mode, setModeState] = useState<VoiceMode>("continuous")
  const [isRecording, setIsRecording] = useState(false)
  const [pttState, setPttState] = useState<PushToTalkState>({
    isRecording: false,
    isProcessing: false,
    audioBuffer: null,
    stage: "idle",
    continuousMode: false,
    sendDirectly: false
  })
  const [sendDirectly, setSendDirectly] = useState(false)
  const [chunks, setChunks] = useState<TranscriptionChunk[]>([])
  const [config, setConfig] = useState<VoiceTranscriptionConfig | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [bufferDuration, setBufferDuration] = useState(0)
  const configRef = useRef<VoiceTranscriptionConfig | null>(null)
  const captureRef = useRef<AudioCaptureHelper | null>(null)
  const pttCaptureRef = useRef<PushToTalkCaptureHelper | null>(null)
  const continuousRef = useRef<ContinuousRecordingHelper | null>(null)
  const modeInitializedRef = useRef(false)

  const refreshConfig = useCallback(async () => {
    try {
      const nextConfig = await window.electronAPI.voice.getConfig()
      setConfig(nextConfig)
      return nextConfig
    } catch (err) {
      console.error("Failed to load transcription config:", err)
      setError("Failed to load transcription config.")
      return null
    }
  }, [])

  useEffect(() => {
    refreshConfig()
  }, [refreshConfig])

  useEffect(() => {
    configRef.current = config
  }, [config])

  useEffect(() => {
    if (config && !modeInitializedRef.current) {
      setModeState(
        config.defaultMode === "push-to-talk" ? "push-to-talk" : "continuous"
      )
      modeInitializedRef.current = true
    }
  }, [config])

  useEffect(() => {
    const unsubscribeReady = window.electronAPI.voice.onTranscriptionReady(
      (data: { id: string; text: string; timestamp: number }) => {
        // Используем функциональное обновление состояния для получения актуального isRecording
        setChunks((prev) => {
          const currentIsRecording = isRecording
          console.log('[VoiceContext] Transcription ready received:', {
            id: data.id,
            textLength: data.text?.length || 0,
            isRecording: currentIsRecording,
            captureExists: !!captureRef.current,
            chunksCount: prev.length
          })
          
          // Проверяем, что запись все еще активна
          if (!currentIsRecording) {
            console.warn('[VoiceContext] Received transcription but recording is not active!')
          }
          
          const next = [
            ...prev,
            {
              id: data.id,
              text: data.text,
              timestamp: data.timestamp,
              selected: false
            }
          ]
          if (next.length > MAX_CHUNKS) {
            return next.slice(next.length - MAX_CHUNKS)
          }
          return next
        })
      }
    )

    const unsubscribeError = window.electronAPI.voice.onTranscriptionError(
      (data: { error?: string; responseBody?: any; statusCode?: number }) => {
        console.error('[VoiceContext] Transcription error:', {
          error: data?.error,
          statusCode: data?.statusCode,
          isRecording: isRecording,
          captureExists: !!captureRef.current
        })
        
        let errorMessage = data?.error || "Transcription failed."
        
        // При ошибке 422 форматируем тело ответа для отображения
        if (data?.statusCode === 422 && data?.responseBody) {
          const bodyText = typeof data.responseBody === 'string' 
            ? data.responseBody 
            : JSON.stringify(data.responseBody, null, 2)
          errorMessage = `${errorMessage}\n\nТело ответа сервера:\n${bodyText}`
        }
        
        // Ошибка транскрипции не должна останавливать запись
        setError(errorMessage)
      }
    )

    return () => {
      unsubscribeReady()
      unsubscribeError()
    }
  }, [isRecording])

  useEffect(() => {
    return () => {
      captureRef.current?.stopCapture()
      captureRef.current = null
      if (pttCaptureRef.current) {
        void pttCaptureRef.current.stopCapture()
        pttCaptureRef.current = null
      }
      continuousRef.current?.stopCapture()
      continuousRef.current = null
    }
  }, [])

  const resetPTTState = useCallback(() => {
    setPttState({
      isRecording: false,
      isProcessing: false,
      audioBuffer: null,
      stage: "idle",
      continuousMode: false,
      sendDirectly: false
    })
  }, [])

  useEffect(() => {
    if (!pttState.isRecording || !continuousRef.current) return

    const interval = window.setInterval(() => {
      const duration = continuousRef.current?.getBufferDuration() || 0
      setBufferDuration(duration)
    }, 1000)

    return () => window.clearInterval(interval)
  }, [pttState.isRecording])


  const startRecording = useCallback(async () => {
    if (isRecording) return
    const activeConfig = config || (await refreshConfig())
    if (!activeConfig) return

    if (!activeConfig.enabled) {
      setError("Transcription is disabled in settings.")
      return
    }

    if (
      !activeConfig.apiKey?.trim()
    ) {
      setError("Transcription API settings are incomplete.")
      return
    }

    try {
      await window.electronAPI.voice.startRecording()
      const capture = new AudioCaptureHelper(activeConfig.chunkDurationMs)
      capture.onChunkReady = async (chunk, timestamp) => {
        try {
          console.log('[VoiceContext] Chunk ready from AudioCaptureHelper:', {
            chunkSize: chunk.size,
            chunkType: chunk.type,
            isRecording: isRecording,
            captureExists: !!captureRef.current
          })
          
          const buffer = await chunk.arrayBuffer()
          console.log('[VoiceContext] Buffer created, enqueueing:', {
            bufferSize: buffer.byteLength,
            isRecording: isRecording
          })
          
          await window.electronAPI.voice.enqueueChunk({
            audioData: buffer,
            timestamp,
            mimeType: chunk.type
          })
          
          console.log('[VoiceContext] Chunk enqueued successfully, isRecording:', isRecording)
        } catch (err) {
          console.error("[VoiceContext] Failed to enqueue audio chunk:", err, {
            isRecording: isRecording,
            captureExists: !!captureRef.current
          })
        }
      }
      captureRef.current = capture
      await capture.startCombinedCapture()
      setIsRecording(true)
      setError(null)
    } catch (err) {
      console.error("Failed to start recording:", err)
      setError("Failed to start recording.")
    }
  }, [config, isRecording, refreshConfig])

  const stopRecording = useCallback(async () => {
    if (!isRecording) return
    captureRef.current?.stopCapture()
    captureRef.current = null
    await window.electronAPI.voice.stopRecording()
    setIsRecording(false)
  }, [isRecording])

  const setMode = useCallback(
    (nextMode: VoiceMode) => {
      if (nextMode === mode) return
      if (mode === "continuous" && isRecording) {
        void stopRecording()
      }
      if (mode === "push-to-talk" && pttState.isRecording) {
        if (pttCaptureRef.current) {
          void pttCaptureRef.current.stopCapture()
          pttCaptureRef.current = null
        }
        resetPTTState()
      }
      setModeState(nextMode)
    },
    [isRecording, mode, pttState.isRecording, resetPTTState, stopRecording]
  )

  const startPTTRecording = useCallback(async () => {
    if (pttState.isRecording) return
    const activeConfig = config || (await refreshConfig())
    if (!activeConfig) return

    if (!activeConfig.enabled) {
      setError("Transcription is disabled in settings.")
      return
    }

    if (!activeConfig.apiKey?.trim()) {
      setError("Transcription API settings are incomplete.")
      return
    }

    try {
      await window.electronAPI.voice.startRecording()
      const capture = new PushToTalkCaptureHelper()
      pttCaptureRef.current = capture
      await capture.startCapture()
      setPttState({
        isRecording: true,
        isProcessing: false,
        audioBuffer: null,
        stage: "recording",
        continuousMode: false,
        sendDirectly: false
      })
      setError(null)
    } catch (err) {
      console.error("Failed to start push-to-talk recording:", err)
      setError("Failed to start push-to-talk recording.")
    }
  }, [config, refreshConfig])

  const stopPTTRecording = useCallback(async () => {
    if (!pttState.isRecording) return null
    const activeConfig = config || (await refreshConfig())
    if (!activeConfig) return null

      setPttState((prev) => ({
        ...prev,
        isRecording: false,
        isProcessing: true,
        stage: "transcribing",
        continuousMode: false
      }))

    const capture = pttCaptureRef.current
    pttCaptureRef.current = null

    try {
      const result = await capture?.stopCapture()
      await window.electronAPI.voice.stopRecording()

      if (!result?.blob || result.blob.size === 0) {
        resetPTTState()
        setError("Recorded audio is empty.")
        return null
      }

      setPttState((prev) => ({
        ...prev,
        audioBuffer: result.blob
      }))

      const audioBuffer = await result.blob.arrayBuffer()
      const transcriptionResult = await window.electronAPI.voice.transcribeFull({
        audioData: audioBuffer,
        mimeType: result.mimeType
      })
      const transcription = transcriptionResult?.text || ""

      if (!transcription.trim()) {
        resetPTTState()
        setError("Transcription is empty.")
        return null
      }

      setPttState((prev) => ({
        ...prev,
        stage: "thinking"
      }))

      const llmResult = await window.electronAPI.voice.processQuery({
        chunks: [{ text: transcription, timestamp: Date.now() }],
        question: "",
        systemPrompt: activeConfig.pttPrompt || undefined
      })

      if (!llmResult?.success) {
        resetPTTState()
        setError(llmResult?.error || "Failed to process voice query.")
        return null
      }

      setPttState((prev) => ({
        ...prev,
        isProcessing: false,
        stage: "idle",
        continuousMode: false,
        sendDirectly: false
      }))

      return {
        transcription,
        response: llmResult.response || ""
      }
    } catch (err) {
      console.error("Failed to process push-to-talk recording:", err)
      resetPTTState()
      setError("Failed to process push-to-talk recording.")
      return null
    }
  }, [config, pttState.isRecording, refreshConfig, resetPTTState])

  const startContinuousRecording = useCallback(async () => {
    if (continuousRef.current) return
    const activeConfig = configRef.current || (await refreshConfig())
    if (!activeConfig) return

    if (!activeConfig.enabled) {
      setError("Transcription is disabled in settings.")
      return
    }

    if (!activeConfig.apiKey?.trim()) {
      setError("Transcription API settings are incomplete.")
      return
    }

    try {
      await window.electronAPI.voice.startRecording()
      const capture = new ContinuousRecordingHelper()
      continuousRef.current = capture
      await capture.startCapture()
      setPttState((prev) => ({
        ...prev,
        isRecording: true,
        isProcessing: false,
        audioBuffer: null,
        stage: "recording",
        continuousMode: true,
        sendDirectly: false
      }))
      setError(null)
    } catch (err) {
      console.error("Failed to start continuous recording:", err)
      setError("Failed to start continuous recording.")
    }
  }, [refreshConfig])

  const stopContinuousRecording = useCallback(() => {
    continuousRef.current?.stopCapture()
    continuousRef.current = null
    void window.electronAPI.voice.stopRecording()
    setBufferDuration(0)
    setPttState((prev) => ({
      ...prev,
      isRecording: false,
      isProcessing: false,
      audioBuffer: null,
      stage: "idle",
      continuousMode: false,
      sendDirectly: false
    }))
  }, [])

  const sendLastMinutes = useCallback(
    async (minutes: TimeSelection, context?: string) => {
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

        // Используем переданный контекст, если он есть, иначе используем pttPrompt из конфига
        const systemPrompt = context?.trim() || activeConfig.pttPrompt || undefined

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
            systemPrompt
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

        // Существующая логика с транскрипцией
        setPttState((prev) => ({
          ...prev,
          stage: "transcribing",
          continuousMode: true
        }))
        const transcriptionResult = await window.electronAPI.voice.transcribeFull({
          audioData: audioBuffer,
          mimeType
        })

        if (!transcriptionResult?.text?.trim()) {
          setError("Transcription is empty.")
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
          stage: "thinking",
          continuousMode: true
        }))
        const llmResult = await window.electronAPI.voice.processQuery({
          chunks: [{ text: transcriptionResult.text, timestamp: Date.now() }],
          question: "",
          systemPrompt
        })

        if (!llmResult?.success) {
          setError(llmResult?.error || "Failed to process voice query.")
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
          transcription: transcriptionResult.text,
          response: llmResult.response || ""
        }
      } catch (err) {
        console.error("Failed to process continuous recording:", err)
        setError("Failed to process continuous recording.")
        setPttState((prev) => ({
          ...prev,
          isProcessing: false,
          stage: "recording",
          continuousMode: true
        }))
        return null
      }
    },
    [config, refreshConfig, sendDirectly]
  )

  const toggleChunkSelection = useCallback((id: string) => {
    setChunks((prev) =>
      prev.map((chunk) =>
        chunk.id === id ? { ...chunk, selected: !chunk.selected } : chunk
      )
    )
  }, [])

  const selectAllChunks = useCallback(() => {
    setChunks((prev) => prev.map((chunk) => ({ ...chunk, selected: true })))
  }, [])

  const clearSelection = useCallback(() => {
    setChunks((prev) => prev.map((chunk) => ({ ...chunk, selected: false })))
  }, [])

  const clearAllChunks = useCallback(() => {
    setChunks([])
  }, [])

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  const selectedChunks = useMemo(
    () => chunks.filter((chunk) => chunk.selected),
    [chunks]
  )

  return (
    <VoiceContext.Provider
      value={{
        mode,
        isRecording,
        pttState,
        chunks,
        selectedChunks,
        config,
        error,
        sendDirectly,
        setSendDirectly,
        setMode,
        startRecording,
        stopRecording,
        startPTTRecording,
        stopPTTRecording,
        startContinuousRecording,
        stopContinuousRecording,
        sendLastMinutes,
        bufferDuration,
        toggleChunkSelection,
        selectAllChunks,
        clearSelection,
        clearAllChunks,
        refreshConfig,
        clearError
      }}
    >
      {children}
    </VoiceContext.Provider>
  )
}

export const useVoice = (): VoiceContextType => {
  const context = useContext(VoiceContext)
  if (!context) {
    throw new Error("useVoice must be used within a VoiceProvider")
  }
  return context
}
