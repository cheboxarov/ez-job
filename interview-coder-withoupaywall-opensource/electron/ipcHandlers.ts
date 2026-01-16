// ipcHandlers.ts

import { app, ipcMain, session, shell, dialog } from "electron"
import fs from "node:fs"
import path from "node:path"
import { randomBytes } from "crypto"
import { IIpcHandlerDeps } from "./main"
import { configHelper } from "./ConfigHelper"
import { TranscriptionHelper } from "./TranscriptionHelper"
import { TranscriptionQueue } from "./TranscriptionQueue"

export function initializeIpcHandlers(deps: IIpcHandlerDeps): void {
  console.log("Initializing IPC handlers")
  const transcriptionHelper = new TranscriptionHelper(() =>
    configHelper.getTranscriptionConfig()
  )
  const transcriptionQueue = new TranscriptionQueue((job) =>
    transcriptionHelper.transcribe(job.buffer, { mimeType: job.mimeType })
  )
  let isRecording = false

  const sendToVoiceWindow = (channel: string, payload: any) => {
    const voiceWindow = deps.getVoiceWindow?.()
    const targetWindow =
      voiceWindow && !voiceWindow.isDestroyed()
        ? voiceWindow
        : deps.getMainWindow()
    if (targetWindow && !targetWindow.isDestroyed()) {
      targetWindow.webContents.send(channel, payload)
    }
  }

  transcriptionQueue.onTranscriptionReady = (payload) => {
    sendToVoiceWindow("voice:transcription-ready", payload)
  }

  transcriptionQueue.onTranscriptionError = (payload) => {
    sendToVoiceWindow("voice:transcription-error", payload)
  }

  // Configuration handlers
  ipcMain.handle("get-config", () => {
    return configHelper.loadConfig();
  })

  ipcMain.handle("update-config", (_event, updates) => {
    return configHelper.updateConfig(updates);
  })

  ipcMain.handle("check-api-key", () => {
    return configHelper.hasApiKey();
  })
  
  ipcMain.handle("validate-api-key", async (_event, payload) => {
    if (!payload || typeof payload !== "object") {
      return { valid: false, error: "Missing API key payload." };
    }

    const { apiKey, baseUrl, model } = payload as {
      apiKey?: string;
      baseUrl?: string;
      model?: string;
    };

    if (!configHelper.isValidApiKeyFormat(apiKey || "")) {
      return { valid: false, error: "API key is required." };
    }

    if (!baseUrl || !baseUrl.trim()) {
      return { valid: false, error: "Base URL is required." };
    }

    const result = await configHelper.testApiKey(apiKey, baseUrl, model);
    return result;
  })

  // Voice recording handlers
  ipcMain.handle("voice:start-recording", () => {
    isRecording = true
    return { success: true }
  })

  ipcMain.handle("voice:stop-recording", () => {
    isRecording = false
    return { success: true }
  })

  ipcMain.handle("voice:get-recording-status", () => {
    return { isRecording }
  })

  ipcMain.handle("voice:enqueue-chunk", async (_event, payload) => {
    // #region agent log
    const logPath = path.join(process.cwd(), '.cursor', 'debug.log');
    try {
      if (!fs.existsSync(path.dirname(logPath))) {
        fs.mkdirSync(path.dirname(logPath), { recursive: true });
      }
      const logEntry = JSON.stringify({location:'ipcHandlers.ts:92',message:'enqueue-chunk handler entry',data:{hasPayload:!!payload,hasAudioData:!!payload?.audioData,audioDataSize:payload?.audioData?.byteLength||0,mimeType:payload?.mimeType},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})+'\n';
      fs.appendFileSync(logPath, logEntry);
    } catch (logErr) {
      console.error('Failed to write log:', logErr);
    }
    // #endregion
    if (!payload || !payload.audioData) {
      // #region agent log
      try {
        const logEntry2 = JSON.stringify({location:'ipcHandlers.ts:96',message:'enqueue-chunk rejected - missing payload',data:{hasPayload:!!payload,hasAudioData:!!payload?.audioData},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})+'\n';
        fs.appendFileSync(logPath, logEntry2);
      } catch (logErr) {
        console.error('Failed to write log:', logErr);
      }
      // #endregion
      return { success: false, error: "Missing audio payload." }
    }
    const timestamp =
      typeof payload.timestamp === "number" ? payload.timestamp : Date.now()
    const mimeType =
      typeof payload.mimeType === "string" ? payload.mimeType : undefined
    const buffer = Buffer.from(payload.audioData)
    // #region agent log
    try {
      const logEntry3 = JSON.stringify({location:'ipcHandlers.ts:103',message:'buffer created and enqueued',data:{bufferLength:buffer.length,originalSize:payload.audioData?.byteLength||0,mimeType:mimeType},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})+'\n';
      fs.appendFileSync(logPath, logEntry3);
    } catch (logErr) {
      console.error('Failed to write log:', logErr);
    }
    // #endregion
    transcriptionQueue.enqueue({ buffer, timestamp, mimeType })
    return { success: true }
  })

  ipcMain.handle("voice:transcribe-chunk", async (_event, payload) => {
    if (!payload || !payload.audioData) {
      return { success: false, error: "Missing audio payload." }
    }
    const buffer = Buffer.from(payload.audioData)
    const mimeType =
      typeof payload.mimeType === "string" ? payload.mimeType : undefined
    return transcriptionHelper.transcribe(buffer, { mimeType })
  })

  ipcMain.handle("voice:transcribe-full", async (_event, payload) => {
    if (!payload || !payload.audioData) {
      return { success: false, error: "Missing audio payload." }
    }
    const buffer = Buffer.from(payload.audioData)
    const mimeType =
      typeof payload.mimeType === "string" ? payload.mimeType : undefined
    const result = await transcriptionHelper.transcribe(buffer, { mimeType })
    return { text: result.text }
  })

  ipcMain.handle("voice:get-config", () => {
    return configHelper.getTranscriptionConfig()
  })

  ipcMain.handle("voice:update-config", async (_event, config) => {
    return configHelper.updateTranscriptionConfig(config || {})
  })

  ipcMain.handle("voice:validate-config", async (_event, config) => {
    const resolvedConfig = config || configHelper.getTranscriptionConfig()
    return transcriptionHelper.validateConfig(resolvedConfig)
  })

  ipcMain.handle("voice:process-query", async (_event, payload) => {
    if (!deps.processingHelper) {
      return { success: false, error: "Processing helper not available." }
    }
    const { chunks, question, systemPrompt } = payload || {}
    try {
      const response = await deps.processingHelper.processVoiceQuery(
        chunks || [],
        question,
        systemPrompt
      )
      return { success: true, response }
    } catch (error: any) {
      return {
        success: false,
        error: error?.message || "Failed to process voice query."
      }
    }
  })

  ipcMain.handle("voice:process-audio-directly", async (_event, payload) => {
    if (!deps.processingHelper) {
      return { success: false, error: "Processing helper not available." }
    }
    const { audioData, mimeType, systemPrompt } = payload || {}

    if (!audioData) {
      return { success: false, error: "Missing audio data." }
    }

    try {
      // Конвертируем ArrayBuffer в base64
      const buffer = Buffer.from(audioData)
      const audioBase64 = buffer.toString("base64")

      // Определяем формат из mimeType
      let format = "webm"
      if (mimeType?.includes("wav")) format = "wav"
      else if (mimeType?.includes("mp3")) format = "mp3"
      else if (mimeType?.includes("ogg")) format = "ogg"

      const response = await deps.processingHelper.processVoiceQueryWithAudio(
        audioBase64,
        format,
        systemPrompt
      )
      return { success: true, response }
    } catch (error: any) {
      return {
        success: false,
        error: error?.message || "Failed to process audio directly."
      }
    }
  })

  // Credits handlers
  ipcMain.handle("set-initial-credits", async (_event, credits: number) => {
    const mainWindow = deps.getMainWindow()
    if (!mainWindow) return

    try {
      // Set the credits in a way that ensures atomicity
      await mainWindow.webContents.executeJavaScript(
        `window.__CREDITS__ = ${credits}`
      )
      mainWindow.webContents.send("credits-updated", credits)
    } catch (error) {
      console.error("Error setting initial credits:", error)
      throw error
    }
  })

  ipcMain.handle("decrement-credits", async () => {
    const mainWindow = deps.getMainWindow()
    if (!mainWindow) return

    try {
      const currentCredits = await mainWindow.webContents.executeJavaScript(
        "window.__CREDITS__"
      )
      if (currentCredits > 0) {
        const newCredits = currentCredits - 1
        await mainWindow.webContents.executeJavaScript(
          `window.__CREDITS__ = ${newCredits}`
        )
        mainWindow.webContents.send("credits-updated", newCredits)
      }
    } catch (error) {
      console.error("Error decrementing credits:", error)
    }
  })

  // Screenshot queue handlers
  ipcMain.handle("get-screenshot-queue", () => {
    return deps.getScreenshotQueue()
  })

  ipcMain.handle("get-extra-screenshot-queue", () => {
    return deps.getExtraScreenshotQueue()
  })

  ipcMain.handle("delete-screenshot", async (event, path: string) => {
    return deps.deleteScreenshot(path)
  })

  ipcMain.handle("get-image-preview", async (event, path: string) => {
    return deps.getImagePreview(path)
  })

  // Screenshot processing handlers
  ipcMain.handle("process-screenshots", async () => {
    // Check for API key before processing
    if (!configHelper.hasApiKey()) {
      const mainWindow = deps.getMainWindow();
      if (mainWindow) {
        mainWindow.webContents.send(deps.PROCESSING_EVENTS.API_KEY_INVALID);
      }
      return;
    }
    
    await deps.processingHelper?.processScreenshots()
  })

  // Window dimension handlers
  ipcMain.handle(
    "update-content-dimensions",
    async (event, { width, height }: { width: number; height: number }) => {
      if (width && height) {
        deps.setWindowDimensions(width, height)
      }
    }
  )

  ipcMain.handle(
    "set-window-dimensions",
    (event, width: number, height: number) => {
      deps.setWindowDimensions(width, height)
    }
  )

  // Screenshot management handlers
  ipcMain.handle("get-screenshots", async () => {
    try {
      let previews = []
      const currentView = deps.getView()

      if (currentView === "queue") {
        const queue = deps.getScreenshotQueue()
        previews = await Promise.all(
          queue.map(async (path) => ({
            path,
            preview: await deps.getImagePreview(path)
          }))
        )
      } else {
        const extraQueue = deps.getExtraScreenshotQueue()
        previews = await Promise.all(
          extraQueue.map(async (path) => ({
            path,
            preview: await deps.getImagePreview(path)
          }))
        )
      }

      return previews
    } catch (error) {
      console.error("Error getting screenshots:", error)
      throw error
    }
  })

  // Screenshot trigger handlers
  ipcMain.handle("trigger-screenshot", async () => {
    const mainWindow = deps.getMainWindow()
    if (mainWindow) {
      try {
        const screenshotPath = await deps.takeScreenshot()
        const preview = await deps.getImagePreview(screenshotPath)
        mainWindow.webContents.send("screenshot-taken", {
          path: screenshotPath,
          preview
        })
        return { success: true }
      } catch (error) {
        console.error("Error triggering screenshot:", error)
        return { error: "Failed to trigger screenshot" }
      }
    }
    return { error: "No main window available" }
  })

  ipcMain.handle("take-screenshot", async () => {
    try {
      const screenshotPath = await deps.takeScreenshot()
      const preview = await deps.getImagePreview(screenshotPath)
      return { path: screenshotPath, preview }
    } catch (error) {
      console.error("Error taking screenshot:", error)
      return { error: "Failed to take screenshot" }
    }
  })

  // Auth-related handlers removed

  ipcMain.handle("open-external-url", (event, url: string) => {
    shell.openExternal(url)
  })
  
  // Open external URL handler
  ipcMain.handle("openLink", (event, url: string) => {
    try {
      console.log(`Opening external URL: ${url}`);
      shell.openExternal(url);
      return { success: true };
    } catch (error) {
      console.error(`Error opening URL ${url}:`, error);
      return { success: false, error: `Failed to open URL: ${error}` };
    }
  })

  // Settings portal handler
  ipcMain.handle("open-settings-portal", () => {
    const mainWindow = deps.getMainWindow();
    if (mainWindow) {
      mainWindow.webContents.send("show-settings-dialog");
      return { success: true };
    }
    return { success: false, error: "Main window not available" };
  })

  // Window management handlers
  ipcMain.handle("toggle-window", () => {
    try {
      deps.toggleMainWindow()
      return { success: true }
    } catch (error) {
      console.error("Error toggling window:", error)
      return { error: "Failed to toggle window" }
    }
  })

  ipcMain.handle("ptt:hide", () => {
    try {
      deps.hidePTTWindow()
      return { success: true }
    } catch (error) {
      console.error("Error hiding ptt window:", error)
      return { success: false, error: "Failed to hide ptt window" }
    }
  })

  ipcMain.handle("reset-queues", async () => {
    try {
      deps.clearQueues()
      return { success: true }
    } catch (error) {
      console.error("Error resetting queues:", error)
      return { error: "Failed to reset queues" }
    }
  })

  ipcMain.handle("reset-app-data", async () => {
    try {
      const defaultSession = session.defaultSession
      if (defaultSession) {
        await defaultSession.clearCache()
        await defaultSession.clearStorageData()
        await defaultSession.clearAuthCache()
      }

      const dataPaths = [
        app.getPath("sessionData"),
        app.getPath("temp"),
        path.join(app.getPath("userData"), "cache")
      ]

      for (const dir of dataPaths) {
        try {
          if (fs.existsSync(dir)) {
            fs.rmSync(dir, { recursive: true, force: true })
          }
          fs.mkdirSync(dir, { recursive: true })
        } catch (error) {
          console.error(`Error clearing data directory ${dir}:`, error)
        }
      }

      deps.clearQueues()
      configHelper.resetConfig()
      return { success: true }
    } catch (error) {
      console.error("Error resetting app data:", error)
      return { success: false, error: "Failed to reset app data" }
    }
  })

  // Process screenshot handlers
  ipcMain.handle("trigger-process-screenshots", async () => {
    try {
      // Check for API key before processing
      if (!configHelper.hasApiKey()) {
        const mainWindow = deps.getMainWindow();
        if (mainWindow) {
          mainWindow.webContents.send(deps.PROCESSING_EVENTS.API_KEY_INVALID);
        }
        return { success: false, error: "API key required" };
      }
      
      await deps.processingHelper?.processScreenshots()
      return { success: true }
    } catch (error) {
      console.error("Error processing screenshots:", error)
      return { error: "Failed to process screenshots" }
    }
  })

  // Reset handlers
  ipcMain.handle("trigger-reset", () => {
    try {
      // First cancel any ongoing requests
      deps.processingHelper?.cancelOngoingRequests()

      // Clear all queues immediately
      deps.clearQueues()

      // Reset view to queue
      deps.setView("queue")

      // Get main window and send reset events
      const mainWindow = deps.getMainWindow()
      if (mainWindow && !mainWindow.isDestroyed()) {
        // Send reset events in sequence
        mainWindow.webContents.send("reset-view")
        mainWindow.webContents.send("reset")
      }

      return { success: true }
    } catch (error) {
      console.error("Error triggering reset:", error)
      return { error: "Failed to trigger reset" }
    }
  })

  // Window movement handlers
  ipcMain.handle("trigger-move-left", () => {
    try {
      deps.moveWindowLeft()
      return { success: true }
    } catch (error) {
      console.error("Error moving window left:", error)
      return { error: "Failed to move window left" }
    }
  })

  ipcMain.handle("trigger-move-right", () => {
    try {
      deps.moveWindowRight()
      return { success: true }
    } catch (error) {
      console.error("Error moving window right:", error)
      return { error: "Failed to move window right" }
    }
  })

  ipcMain.handle("trigger-move-up", () => {
    try {
      deps.moveWindowUp()
      return { success: true }
    } catch (error) {
      console.error("Error moving window up:", error)
      return { error: "Failed to move window up" }
    }
  })

  ipcMain.handle("trigger-move-down", () => {
    try {
      deps.moveWindowDown()
      return { success: true }
    } catch (error) {
      console.error("Error moving window down:", error)
      return { error: "Failed to move window down" }
    }
  })
  
  // Delete last screenshot handler
  ipcMain.handle("delete-last-screenshot", async () => {
    try {
      const queue = deps.getView() === "queue" 
        ? deps.getScreenshotQueue() 
        : deps.getExtraScreenshotQueue()
      
      if (queue.length === 0) {
        return { success: false, error: "No screenshots to delete" }
      }
      
      // Get the last screenshot in the queue
      const lastScreenshot = queue[queue.length - 1]
      
      // Delete it
      const result = await deps.deleteScreenshot(lastScreenshot)
      
      // Notify the renderer about the change
      const mainWindow = deps.getMainWindow()
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send("screenshot-deleted", { path: lastScreenshot })
      }
      
      return result
    } catch (error) {
      console.error("Error deleting last screenshot:", error)
      return { success: false, error: "Failed to delete last screenshot" }
    }
  })

  // Chat message handler
  ipcMain.handle("send-chat-message", async (_event, message: string, solutionData?: string) => {
    try {
      if (!deps.processingHelper) {
        return { success: false, error: "Processing helper not available" }
      }
      return await deps.processingHelper.sendChatMessage(message, solutionData)
    } catch (error) {
      console.error("Error in send-chat-message handler:", error)
      return { 
        success: false, 
        error: error instanceof Error ? error.message : "Failed to send chat message" 
      }
    }
  })
}
