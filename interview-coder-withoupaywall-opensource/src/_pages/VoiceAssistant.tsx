import { useEffect, useState, useRef } from "react"
import { AudioControls } from "../components/Voice/AudioControls"
import { ChunkSelector } from "../components/Voice/ChunkSelector"
import { ModeSelector } from "../components/Voice/ModeSelector"
import { PushToTalkButton } from "../components/Voice/PushToTalkButton"
import { QuestionInput } from "../components/Voice/QuestionInput"
import { TranscriptionList } from "../components/Voice/TranscriptionList"
import { SettingsDialog } from "../components/Settings/SettingsDialog"
import { Button } from "../components/ui/button"
import { VoiceProvider, useVoice } from "../contexts/VoiceContext"
import { TranscriptionChunk } from "../types/voice"
import { useTranslation } from "react-i18next"
import { Markdown } from "../components/Markdown"

function VoiceAssistantContent() {
  const {
    mode,
    isRecording,
    pttState,
    chunks,
    selectedChunks,
    error,
    setMode,
    startRecording,
    stopRecording,
    startPTTRecording,
    stopPTTRecording,
    toggleChunkSelection,
    selectAllChunks,
    clearSelection,
    clearAllChunks,
    refreshConfig,
    clearError
  } = useVoice()
  const { t } = useTranslation()
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)
  const [response, setResponse] = useState<string | null>(null)
  const [isSending, setIsSending] = useState(false)
  const [pttTranscription, setPttTranscription] = useState<string | null>(null)
  const [recordingDuration, setRecordingDuration] = useState(0)
  const recordingStartTimeRef = useRef<number | null>(null)

  useEffect(() => {
    if (!isSettingsOpen) {
      refreshConfig()
    }
  }, [isSettingsOpen, refreshConfig])

  useEffect(() => {
    if (mode === "continuous") {
      setPttTranscription(null)
      setRecordingDuration(0)
      recordingStartTimeRef.current = null
    }
  }, [mode])

  // Таймер записи для PTT режима
  useEffect(() => {
    if (pttState.isRecording && pttState.stage === "recording") {
      if (!recordingStartTimeRef.current) {
        recordingStartTimeRef.current = Date.now()
      }
      const interval = setInterval(() => {
        if (recordingStartTimeRef.current) {
          const elapsed = Date.now() - recordingStartTimeRef.current
          setRecordingDuration(elapsed)
        }
      }, 100)
      return () => clearInterval(interval)
    } else {
      recordingStartTimeRef.current = null
      setRecordingDuration(0)
    }
  }, [pttState.isRecording, pttState.stage])

  const formatDuration = (ms: number) => {
    const totalSeconds = Math.floor(ms / 1000)
    const minutes = Math.floor(totalSeconds / 60)
    const seconds = totalSeconds % 60
    const milliseconds = Math.floor((ms % 1000) / 100)
    if (minutes > 0) {
      return `${minutes}:${seconds.toString().padStart(2, "0")}.${milliseconds}`
    }
    return `${seconds}.${milliseconds}`
  }

  const handleSubmit = async (
    question: string,
    selected: TranscriptionChunk[]
  ) => {
    setIsSending(true)
    try {
      const result = await window.electronAPI.voice.processQuery({
        chunks: selected.map((chunk) => ({
          text: chunk.text,
          timestamp: chunk.timestamp
        })),
        question
      })
      if (result?.success) {
        setResponse(result.response || "")
      } else {
        setResponse(null)
        throw new Error(result?.error || "Failed to process voice query.")
      }
    } catch (err: any) {
      setResponse(err?.message || "Failed to process voice query.")
      console.error("Voice query failed:", err)
    } finally {
      setIsSending(false)
    }
  }

  const handleStopPTT = async () => {
    const result = await stopPTTRecording()
    if (result?.response) {
      setResponse(result.response)
      setPttTranscription(result.transcription)
    }
  }

  const pttStatusLabel = (() => {
    switch (pttState.stage) {
      case "recording":
        return `${t("voice.ptt.recording")} ${recordingDuration > 0 ? `(${formatDuration(recordingDuration)})` : ""}`
      case "transcribing":
        return t("voice.ptt.transcribing")
      case "thinking":
        return t("voice.ptt.thinking")
      default:
        return t("voice.ptt.idle")
    }
  })()

  const getStageProgress = () => {
    switch (pttState.stage) {
      case "recording":
        return { label: t("voice.ptt.recording"), progress: 25 }
      case "transcribing":
        return { label: t("voice.ptt.transcribing"), progress: 50 }
      case "thinking":
        return { label: t("voice.ptt.thinking"), progress: 75 }
      default:
        return { label: t("voice.ptt.idle"), progress: 0 }
    }
  }

  const stageProgress = getStageProgress()

  const isBusy = mode === "continuous" ? isSending : pttState.isProcessing

  return (
    <div className="min-h-screen bg-black text-white">
      <div className="mx-auto flex w-full max-w-2xl flex-col gap-6 px-6 py-8">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-semibold">Voice Assistant</h1>
            <p className="text-sm text-white/60">
              Capture the interview and send selected chunks to the LLM.
            </p>
          </div>
          <Button
            variant="outline"
            className="border-white/10 text-white"
            onClick={() => setIsSettingsOpen(true)}
          >
            Settings
          </Button>
        </div>

        <ModeSelector mode={mode} onModeChange={setMode} />

        {mode === "continuous" ? (
          <>
            <div className="rounded-lg border border-white/10 bg-black/40 p-4">
              <div className="flex flex-col gap-4">
                <AudioControls
                  isRecording={isRecording}
                  onStart={startRecording}
                  onStop={stopRecording}
                />
                <div className="text-xs text-white/60">
                  Chunks captured: {chunks.length} • Selected:{" "}
                  {selectedChunks.length}
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <h2 className="text-lg font-semibold">Transcription</h2>
              <TranscriptionList chunks={chunks} onToggle={toggleChunkSelection} />
            </div>

            <ChunkSelector
              onSelectAll={selectAllChunks}
              onClearSelection={clearSelection}
              onClearAll={clearAllChunks}
            />

            <QuestionInput
              onSubmit={handleSubmit}
              selectedChunks={selectedChunks}
              disabled={isSending}
            />
          </>
        ) : (
          <>
            <div className="rounded-lg border border-white/10 bg-black/40 p-4 space-y-4">
              <PushToTalkButton
                state={pttState}
                onStart={startPTTRecording}
                onStop={handleStopPTT}
              />
              <div className="space-y-2">
                <div className="text-xs text-white/60">{pttStatusLabel}</div>
                {pttState.isProcessing && (
                  <div className="space-y-1">
                    <div className="flex items-center justify-between text-xs text-white/50">
                      <span>{stageProgress.label}</span>
                      <span>{stageProgress.progress}%</span>
                    </div>
                    <div className="h-1 w-full bg-white/10 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-white/30 transition-all duration-300 ease-out"
                        style={{ width: `${stageProgress.progress}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>

            {pttTranscription ? (
              <div className="rounded-lg border border-white/10 bg-black/40 p-4">
                <div className="text-xs uppercase tracking-wide text-white/50">
                  {t("voice.ptt.transcription")}
                </div>
                <div className="mt-2 whitespace-pre-wrap text-sm text-white/80">
                  {pttTranscription}
                </div>
              </div>
            ) : null}
          </>
        )}

        {error ? (
          <div className="rounded-md border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-200">
            <div className="flex flex-col gap-2">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 whitespace-pre-wrap break-words">{error}</div>
                <button
                  onClick={clearError}
                  className="text-xs uppercase tracking-wide text-red-200/70 flex-shrink-0"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        ) : null}

        <div className="rounded-lg border border-white/10 bg-black/40 p-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Assistant Response</h2>
            {isBusy ? (
              <span className="text-xs text-white/50">{t("voice.ptt.thinking")}</span>
            ) : null}
          </div>
          <div className="mt-3 text-sm text-white/80">
            <Markdown
              content={response || "Response will appear here after processing."}
            />
          </div>
        </div>
      </div>

      <SettingsDialog
        open={isSettingsOpen}
        onOpenChange={setIsSettingsOpen}
      />
    </div>
  )
}

export default function VoiceAssistant() {
  return (
    <VoiceProvider>
      <VoiceAssistantContent />
    </VoiceProvider>
  )
}
