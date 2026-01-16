export interface ElectronAPI {
  // Original methods
  openSubscriptionPortal: (authData: {
    id: string
    email: string
  }) => Promise<{ success: boolean; error?: string }>
  updateContentDimensions: (dimensions: {
    width: number
    height: number
  }) => Promise<void>
  clearStore: () => Promise<{ success: boolean; error?: string }>
  getScreenshots: () => Promise<{
    success: boolean
    previews?: Array<{ path: string; preview: string }> | null
    error?: string
  }>
  deleteScreenshot: (
    path: string
  ) => Promise<{ success: boolean; error?: string }>
  onScreenshotTaken: (
    callback: (data: { path: string; preview: string }) => void
  ) => () => void
  onResetView: (callback: () => void) => () => void
  onSolutionStart: (callback: () => void) => () => void
  onDebugStart: (callback: () => void) => () => void
  onDebugSuccess: (callback: (data: any) => void) => () => void
  onSolutionError: (callback: (error: string) => void) => () => void
  onProcessingNoScreenshots: (callback: () => void) => () => void
  onProblemExtracted: (callback: (data: any) => void) => () => void
  onSolutionSuccess: (callback: (data: any) => void) => () => void
  onUnauthorized: (callback: () => void) => () => void
  onDebugError: (callback: (error: string) => void) => () => void
  openExternal: (url: string) => void
  toggleMainWindow: () => Promise<{ success: boolean; error?: string }>
  triggerScreenshot: () => Promise<{ success: boolean; error?: string }>
  triggerProcessScreenshots: () => Promise<{ success: boolean; error?: string }>
  triggerReset: () => Promise<{ success: boolean; error?: string }>
  triggerMoveLeft: () => Promise<{ success: boolean; error?: string }>
  triggerMoveRight: () => Promise<{ success: boolean; error?: string }>
  triggerMoveUp: () => Promise<{ success: boolean; error?: string }>
  triggerMoveDown: () => Promise<{ success: boolean; error?: string }>
  onSubscriptionUpdated: (callback: () => void) => () => void
  onSubscriptionPortalClosed: (callback: () => void) => () => void
  startUpdate: () => Promise<{ success: boolean; error?: string }>
  installUpdate: () => void
  onUpdateAvailable: (callback: (info: any) => void) => () => void
  onUpdateDownloaded: (callback: (info: any) => void) => () => void

  decrementCredits: () => Promise<void>
  setInitialCredits: (credits: number) => Promise<void>
  onCreditsUpdated: (callback: (credits: number) => void) => () => void
  onOutOfCredits: (callback: () => void) => () => void
  openSettingsPortal: () => Promise<void>
  getPlatform: () => string
  
  // New methods for API integration
  getConfig: () => Promise<{
    apiKey: string;
    baseUrl: string;
    model: string;
    language: string;
    interfaceLanguage: string;
    opacity: number;
    transcription: {
      enabled: boolean;
      baseUrl: string;
      apiKey: string;
      model: string;
      language: string;
      chunkDurationMs: number;
      defaultMode: "continuous" | "push-to-talk";
      pttPrompt: string;
    };
  }>
  updateConfig: (config: {
    apiKey?: string;
    baseUrl?: string;
    model?: string;
    language?: string;
    interfaceLanguage?: string;
    opacity?: number;
    transcription?: {
      enabled?: boolean;
      baseUrl?: string;
      apiKey?: string;
      model?: string;
      language?: string;
      chunkDurationMs?: number;
      defaultMode?: "continuous" | "push-to-talk";
      pttPrompt?: string;
    };
  }) => Promise<{
    apiKey: string;
    baseUrl: string;
    model: string;
    language: string;
    interfaceLanguage: string;
    opacity: number;
    transcription: {
      enabled: boolean;
      baseUrl: string;
      apiKey: string;
      model: string;
      language: string;
      chunkDurationMs: number;
      defaultMode: "continuous" | "push-to-talk";
      pttPrompt: string;
    };
  }>
  checkApiKey: () => Promise<boolean>
  validateApiKey: (config: {
    apiKey: string;
    baseUrl: string;
    model?: string;
  }) => Promise<{ valid: boolean; error?: string }>
  resetAppData: () => Promise<{ success: boolean; error?: string }>
  openLink: (url: string) => void
  onApiKeyInvalid: (callback: () => void) => () => void
  removeListener: (eventName: string, callback: (...args: any[]) => void) => void
  sendChatMessage: (message: string, solutionData?: string) => Promise<{ success: boolean; response?: string; error?: string }>
  ptt: {
    hide: () => Promise<{ success: boolean; error?: string }>
  }
  voice: {
    startRecording: () => Promise<{ success: boolean }>
    stopRecording: () => Promise<{ success: boolean }>
    getRecordingStatus: () => Promise<{ isRecording: boolean }>
    enqueueChunk: (payload: {
      audioData: ArrayBuffer
      timestamp: number
      mimeType?: string
    }) => Promise<{ success: boolean; error?: string }>
    transcribeChunk: (payload: {
      audioData: ArrayBuffer
      mimeType?: string
    }) => Promise<any>
    processQuery: (payload: {
      chunks: Array<{ text: string; timestamp: number }>
      question?: string
      systemPrompt?: string
    }) => Promise<{ success: boolean; response?: string; error?: string }>
    getConfig: () => Promise<{
      enabled: boolean
      baseUrl: string
      apiKey: string
      model: string
      language: string
      chunkDurationMs: number
      defaultMode: "continuous" | "push-to-talk"
      pttPrompt: string
    }>
    updateConfig: (config: {
      enabled?: boolean
      baseUrl?: string
      apiKey?: string
      model?: string
      language?: string
      chunkDurationMs?: number
      defaultMode?: "continuous" | "push-to-talk"
      pttPrompt?: string
    }) => Promise<{
      enabled: boolean
      baseUrl: string
      apiKey: string
      model: string
      language: string
      chunkDurationMs: number
      defaultMode: "continuous" | "push-to-talk"
      pttPrompt: string
    }>
    validateConfig: (config: {
      enabled: boolean
      baseUrl: string
      apiKey: string
      model: string
      language: string
      chunkDurationMs: number
      defaultMode: "continuous" | "push-to-talk"
      pttPrompt: string
    }) => Promise<{ valid: boolean; error?: string }>
    getDesktopSources: () => Promise<Array<{ id: string; name: string }>>
    onTranscriptionReady: (callback: (data: any) => void) => () => void
    onTranscriptionError: (callback: (data: any) => void) => () => void
    transcribeFull: (payload: {
      audioData: ArrayBuffer
      mimeType?: string
    }) => Promise<{ text: string }>
    processAudioDirectly: (data: {
      audioData: ArrayBuffer
      mimeType: string
      systemPrompt?: string
    }) => Promise<{ success: boolean; response?: string; error?: string }>
  }
}

declare global {
  interface Window {
    electronAPI: ElectronAPI
    electron: {
      ipcRenderer: {
        on: (channel: string, func: (...args: any[]) => void) => void
        removeListener: (
          channel: string,
          func: (...args: any[]) => void
        ) => void
      }
    }
    __CREDITS__: number
    __LANGUAGE__: string
    __IS_INITIALIZED__: boolean
    __AUTH_TOKEN__?: string | null
  }
}
