import { randomUUID } from "crypto"
import fs from "node:fs"
import { TranscriptionResult } from "./TranscriptionHelper"

export interface TranscriptionJob {
  buffer: Buffer
  timestamp: number
  mimeType?: string
}

export interface TranscriptionReadyPayload {
  id: string
  text: string
  timestamp: number
  segments?: TranscriptionResult["segments"]
}

export interface TranscriptionErrorPayload {
  id: string
  error: string
  timestamp: number
  responseBody?: any
  statusCode?: number
}

export class TranscriptionQueue {
  private queue: TranscriptionJob[] = []
  private isProcessing = false
  private transcribe: (
    job: TranscriptionJob
  ) => Promise<TranscriptionResult>

  public onTranscriptionReady?: (payload: TranscriptionReadyPayload) => void
  public onTranscriptionError?: (payload: TranscriptionErrorPayload) => void

  constructor(
    transcribe: (job: TranscriptionJob) => Promise<TranscriptionResult>
  ) {
    this.transcribe = transcribe
  }

  public enqueue(job: TranscriptionJob): void {
    this.queue.push(job)
    void this.processQueue()
  }

  private async processQueue(): Promise<void> {
    if (this.isProcessing) return
    this.isProcessing = true

    while (this.queue.length > 0) {
      const job = this.queue.shift()
      if (!job) continue
      const id = randomUUID()
      // #region agent log
      const logPath = '/Users/apple/dev/hh/.cursor/debug.log';
      try {
        const logData = {location:'TranscriptionQueue.ts:54',message:'processing transcription job',data:{jobId:id,bufferLength:job.buffer.length,mimeType:job.mimeType},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'};
        console.log('[DEBUG]', logData);
        const logEntry = JSON.stringify(logData)+'\n';
        fs.appendFileSync(logPath, logEntry, { flag: 'a' });
      } catch (logErr) {
        console.error('Failed to write log:', logErr);
      }
      // #endregion
      try {
        const result = await this.transcribe(job)
        // #region agent log
        try {
          const logData = {location:'TranscriptionQueue.ts:67',message:'transcription result',data:{jobId:id,bufferLength:job.buffer.length,resultText:result.text,resultTextLength:result.text?.length||0,hasText:!!result.text&&result.text.trim().length>0},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'};
          console.log('[DEBUG RESULT]', logData);
          const logEntry = JSON.stringify(logData)+'\n';
          fs.appendFileSync(logPath, logEntry, { flag: 'a' });
        } catch (logErr) {
          console.error('Failed to write log:', logErr);
        }
        // #endregion
        
        // Пропускаем чанки с пустым текстом (тишина, слишком короткие и т.д.)
        if (result.text && result.text.trim().length > 0) {
          if (this.onTranscriptionReady) {
            this.onTranscriptionReady({
              id,
              text: result.text,
              timestamp: job.timestamp,
              segments: result.segments
            })
          }
        } else {
          // #region agent log
          try {
            const logData = {location:'TranscriptionQueue.ts:85',message:'skipping empty transcription',data:{jobId:id,bufferLength:job.buffer.length},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'};
            console.log('[DEBUG SKIP EMPTY]', logData);
            const logEntry = JSON.stringify(logData)+'\n';
            fs.appendFileSync(logPath, logEntry, { flag: 'a' });
          } catch (logErr) {
            console.error('Failed to write log:', logErr);
          }
          // #endregion
        }
      } catch (error: any) {
        if (this.onTranscriptionError) {
          const statusCode = error?.response?.status
          const responseBody = error?.response?.data
          
          this.onTranscriptionError({
            id,
            error: error?.message || "Failed to transcribe audio.",
            timestamp: job.timestamp,
            responseBody: statusCode === 422 ? responseBody : undefined,
            statusCode
          })
        }
      }
    }

    this.isProcessing = false
  }
}
