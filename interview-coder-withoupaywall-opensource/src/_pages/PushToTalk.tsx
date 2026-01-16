import { useEffect, useMemo, useState, useRef } from "react"
import type { CSSProperties } from "react"
import { useTranslation } from "react-i18next"
import { VoiceProvider, useVoice } from "../contexts/VoiceContext"
import { Markdown } from "../components/Markdown"

function Spinner() {
  return (
    <div className="h-5 w-5 animate-spin rounded-full border-2 border-white/30 border-t-white" />
  )
}

function PushToTalkContent() {
  const { t } = useTranslation()
  const {
    pttState,
    startPTTRecording,
    stopPTTRecording,
    error,
    clearError
  } = useVoice()
  const [response, setResponse] = useState<string | null>(null)
  const [transcription, setTranscription] = useState<string | null>(null)
  const [recordingDuration, setRecordingDuration] = useState(0)
  const recordingStartTimeRef = useRef<number | null>(null)
  const dragRegionStyle = { WebkitAppRegion: "drag" } as CSSProperties
  const noDragStyle = { WebkitAppRegion: "no-drag" } as CSSProperties

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

  const handleToggleRecording = async () => {
    if (pttState.isRecording) {
      const result = await stopPTTRecording()
      if (result?.response) {
        setResponse(result.response)
      }
      if (result?.transcription) {
        setTranscription(result.transcription)
      }
    } else {
      setResponse(null)
      setTranscription(null)
      await startPTTRecording()
    }
  }

  const statusLabel = useMemo(() => {
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
  }, [recordingDuration, pttState.stage, t])

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

  return (
    <div className="h-screen w-screen bg-transparent text-white">
      <div className="relative flex h-full w-full flex-col items-center gap-2 rounded-xl border border-white/10 bg-black/70 px-3 py-3 backdrop-blur-sm">
        <div
          className="absolute left-0 right-0 top-0 h-6"
          style={dragRegionStyle}
        />
        <button
          type="button"
          aria-label="Hide push to talk window"
          onClick={() => window.electronAPI.ptt.hide()}
          className="absolute right-2 top-1 text-xs text-white/50 transition hover:text-white"
          style={noDragStyle}
        >
          x
        </button>

        <div className="text-[10px] uppercase tracking-[0.3em] text-white/40">
          Push-to-Talk
        </div>

        <div className="flex items-center gap-2">
          {pttState.isRecording ? (
            <div className="h-3 w-3 animate-pulse rounded-full bg-red-500" />
          ) : null}
          <div className="text-xs text-white/60">{statusLabel}</div>
        </div>

        <button
          type="button"
          onClick={handleToggleRecording}
          disabled={pttState.isProcessing}
          className={`mt-2 flex h-16 w-16 items-center justify-center rounded-full transition ${
            pttState.isProcessing
              ? "cursor-not-allowed bg-white/10"
              : pttState.isRecording
                ? "bg-red-500 text-white hover:bg-red-600 animate-pulse"
                : "bg-blue-500 text-white hover:bg-blue-600"
          }`}
          style={noDragStyle}
        >
          {pttState.isProcessing ? (
            <Spinner />
          ) : pttState.isRecording ? (
            <div className="h-6 w-6 rounded-sm bg-white" />
          ) : (
            <div className="h-6 w-6 rounded-full border-2 border-white" />
          )}
        </button>

        <div className="text-[10px] text-white/40">
          {pttState.isProcessing
            ? t("voice.ptt.processing")
            : pttState.isRecording
              ? t("voice.ptt.stopAndProcess")
              : t("voice.ptt.startRecording")}
        </div>

        {pttState.isProcessing && (
          <div className="w-full space-y-1 px-2">
            <div className="flex items-center justify-between text-[10px] text-white/50">
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

        <div className="flex w-full flex-1 min-h-0 flex-col">
          <div className="text-[10px] uppercase tracking-[0.2em] text-white/40">
            Response
          </div>
          <div className="mt-1 flex-1 overflow-y-auto rounded-md bg-white/5 p-2 text-xs text-white/80">
            <Markdown content={response || "Response will appear here."} />
          </div>
        </div>

        {transcription && transcription !== "[Audio sent directly to LLM]" ? (
          <div className="flex w-full flex-col">
            <div className="text-[10px] uppercase tracking-[0.2em] text-white/40">
              {t("voice.ptt.transcription", "Transcription")}
            </div>
            <div className="mt-1 max-h-32 overflow-y-auto rounded-md bg-white/5 p-2 text-xs text-white/80">
              <div className="whitespace-pre-wrap">{transcription}</div>
            </div>
          </div>
        ) : null}

        {error ? (
          <div className="w-full rounded-md border border-red-500/30 bg-red-500/10 px-2 py-1 text-[11px] text-red-200">
            <div className="flex items-start justify-between gap-2">
              <span className="flex-1 whitespace-pre-wrap">{error}</span>
              <button
                type="button"
                className="text-[10px] uppercase tracking-wide text-red-200/70"
                onClick={clearError}
                style={noDragStyle}
              >
                Dismiss
              </button>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  )
}

export default function PushToTalk() {
  return (
    <VoiceProvider>
      <PushToTalkContent />
    </VoiceProvider>
  )
}
