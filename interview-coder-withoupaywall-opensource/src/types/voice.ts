export interface TranscriptionChunk {
  id: string
  text: string
  timestamp: number
  selected: boolean
}

export type VoiceMode = "continuous" | "push-to-talk"

export type TimeSelection = 1 | 3 | 5

export interface ContinuousRecordingState {
  isRecording: boolean
  isProcessing: boolean
  bufferDuration: number
  stage: "idle" | "recording" | "extracting" | "transcribing" | "thinking"
}

export interface PushToTalkState {
  isRecording: boolean
  isProcessing: boolean
  audioBuffer: Blob | null
  stage: "idle" | "recording" | "extracting" | "transcribing" | "thinking"
  bufferDuration?: number
  continuousMode?: boolean
  sendDirectly: boolean
}

export interface VoiceTranscriptionConfig {
  enabled: boolean
  baseUrl: string
  apiKey: string
  model: string
  language: string
  chunkDurationMs: number
  defaultMode: VoiceMode
  pttPrompt: string
  sendAudioDirectly: boolean
}
