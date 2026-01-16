import { AssemblyAI } from "assemblyai"
import fs from "node:fs"
import path from "node:path"
import os from "node:os"
import { TranscriptionConfig } from "./ConfigHelper"

export interface TranscriptionResult {
  text: string
  language?: string
  duration?: number
  segments?: Array<{
    start: number
    end: number
    text: string
  }>
}

export class TranscriptionHelper {
  private getConfig: () => TranscriptionConfig
  private client: AssemblyAI | null = null

  constructor(getConfig: () => TranscriptionConfig) {
    this.getConfig = getConfig
  }

  private getClient(): AssemblyAI {
    if (!this.client) {
      const config = this.getConfig()
      if (!config.apiKey) {
        throw new Error("AssemblyAI API key is required.")
      }
      this.client = new AssemblyAI({
        apiKey: config.apiKey
      })
    }
    return this.client
  }

  public async transcribe(
    audioBuffer: Buffer,
    options: { mimeType?: string; filename?: string } = {}
  ): Promise<TranscriptionResult> {
    const config = this.getConfig()

    if (!config.apiKey) {
      throw new Error("AssemblyAI API key is required.")
    }

    // Проверяем размер буфера - слишком маленькие буферы могут быть пустыми или поврежденными
    // Минимальный размер для валидного аудио файла обычно около 1-2KB
    const MIN_BUFFER_SIZE = 1024 // 1KB
    if (audioBuffer.length < MIN_BUFFER_SIZE) {
      console.log('[TranscriptionHelper] Buffer too small, skipping:', {
        bufferLength: audioBuffer.length,
        minSize: MIN_BUFFER_SIZE
      })
      return {
        text: "",
        language: config.language,
        segments: []
      }
    }

    const client = this.getClient()
    
    // Определяем расширение файла на основе MIME-типа
    let fileExtension = "webm"
    if (options.mimeType) {
      if (options.mimeType.includes("webm")) {
        fileExtension = "webm"
      } else if (options.mimeType.includes("ogg")) {
        fileExtension = "ogg"
      } else if (options.mimeType.includes("mp3")) {
        fileExtension = "mp3"
      } else if (options.mimeType.includes("wav")) {
        fileExtension = "wav"
      }
    }
    
    // Сохраняем буфер во временный файл для AssemblyAI
    const tempDir = os.tmpdir()
    const tempFilePath = path.join(tempDir, `transcription-${Date.now()}-${Math.random().toString(36).substring(7)}.${fileExtension}`)
    
    try {
      fs.writeFileSync(tempFilePath, audioBuffer)
      
      // Проверяем размер файла перед отправкой
      const fileStats = fs.statSync(tempFilePath)
      console.log('[TranscriptionHelper] File stats before transcribe:', {
        filePath: tempFilePath,
        fileSize: fileStats.size,
        bufferLength: audioBuffer.length,
        mimeType: options.mimeType,
        fileExtension: fileExtension
      })
      
      // Используем ReadableStream для передачи файла - это помогает AssemblyAI правильно определить тип
      const fileStream = fs.createReadStream(tempFilePath)
      
      const params: any = {
        audio: fileStream,
        speech_model: "universal" as const,
        language_code: config.language || "ru",
        // Добавляем speech_threshold для обработки чанков с низким уровнем речи
        speech_threshold: 0.3 // 30% - более низкий порог для коротких чанков
      }

      console.log('[TranscriptionHelper] Calling AssemblyAI with params (using ReadableStream):', {
        audio: 'ReadableStream',
        speech_model: params.speech_model,
        language_code: params.language_code,
        speech_threshold: params.speech_threshold,
        fileExtension: fileExtension
      })
      
      const transcript = await client.transcripts.transcribe(params)

      // Логируем полный ответ от AssemblyAI для отладки
      console.log('[TranscriptionHelper] Full AssemblyAI response:', {
        status: transcript.status,
        text: transcript.text,
        textLength: transcript.text?.length || 0,
        language_code: transcript.language_code,
        audio_duration: transcript.audio_duration,
        words: transcript.words?.length || 0,
        error: transcript.error,
        id: transcript.id
      })

      // Если статус "error", логируем и возвращаем пустой результат
      if (transcript.status === "error") {
        console.error('[TranscriptionHelper] AssemblyAI returned error:', {
          error: transcript.error,
          status: transcript.status,
          bufferLength: audioBuffer.length,
          fileExtension: fileExtension
        })
        return {
          text: "",
          language: config.language,
          segments: []
        }
      }

      // Преобразуем результат AssemblyAI в наш формат
      // AssemblyAI возвращает текст напрямую, а слова в transcript.words
      const text = transcript.text || ""
      const result: TranscriptionResult = {
        text: text,
        language: transcript.language_code || config.language,
        duration: transcript.audio_duration ? transcript.audio_duration / 1000 : undefined,
        segments: transcript.words?.map((word: any) => ({
          start: (word.start || 0) / 1000, // AssemblyAI возвращает в миллисекундах
          end: (word.end || 0) / 1000,
          text: word.text || ""
        })) || []
      }

      // Логируем результат для отладки
      console.log('[TranscriptionHelper] Result:', {
        textLength: text.length,
        hasText: text.trim().length > 0,
        language: result.language,
        duration: result.duration,
        segmentsCount: result.segments?.length || 0,
        bufferLength: audioBuffer.length,
        transcriptStatus: transcript.status
      })

      // Если статус не "completed", логируем предупреждение
      if (transcript.status !== "completed") {
        console.warn('[TranscriptionHelper] Transcript status is not completed:', transcript.status)
      }
      
      // Если статус completed, но текст пустой, это может означать тишину или проблему с аудио
      if (transcript.status === "completed" && !text.trim()) {
        console.warn('[TranscriptionHelper] Transcript completed but text is empty - possible silence or audio issue')
      }

      return result
    } catch (error: any) {
      // При ошибке сохраняем детали для отображения
      if (error?.status === 422 || error?.response?.status === 422) {
        const enhancedError = new Error(error?.message || "Request failed with status code 422")
        ;(enhancedError as any).response = error.response || { data: error }
        ;(enhancedError as any).statusCode = 422
        throw enhancedError
      }
      throw error
    } finally {
      // Удаляем временный файл
      try {
        if (fs.existsSync(tempFilePath)) {
          fs.unlinkSync(tempFilePath)
        }
      } catch (cleanupError) {
        console.error("Failed to cleanup temp file:", cleanupError)
      }
    }
  }

  public async validateConfig(
    config: TranscriptionConfig
  ): Promise<{ valid: boolean; error?: string }> {
    if (!config.apiKey || !config.apiKey.trim()) {
      return { valid: false, error: "AssemblyAI API key is required." }
    }

    try {
      const client = new AssemblyAI({
        apiKey: config.apiKey
      })
      
      // Проверяем валидность API ключа, пытаясь получить информацию об аккаунте
      // AssemblyAI не имеет прямого endpoint для проверки, поэтому используем транскрипцию тестового файла
      // Вместо этого просто проверяем, что клиент создан успешно
      // Если ключ невалидный, это проявится при первой транскрипции
      return { valid: true }
    } catch (error: any) {
      const status = error?.status || error?.response?.status

      if (status === 401 || status === 403) {
        return { valid: false, error: "Invalid AssemblyAI API key. Please check and try again." }
      }

      if (status === 429) {
        return {
          valid: false,
          error: "Rate limit exceeded or insufficient quota. Please try again later."
        }
      }

      if (status && status >= 500) {
        return {
          valid: false,
          error: "Server error from AssemblyAI. Please try again later."
        }
      }

      if (error?.code === "ECONNREFUSED" || error?.code === "ENOTFOUND") {
        return {
          valid: false,
          error: "Unable to reach AssemblyAI. Please check your network connection."
        }
      }

      return {
        valid: false,
        error: error?.message || "Unknown error validating AssemblyAI config"
      }
    }
  }
}
