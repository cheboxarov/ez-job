export interface AudioSegment {
  blob: Blob
  startTime: number
  endTime: number
  mimeType: string
}

export class ContinuousRecordingHelper {
  private micStream: MediaStream | null = null
  private systemStream: MediaStream | null = null
  private audioContext: AudioContext | null = null
  private destination: MediaStreamAudioDestinationNode | null = null
  private mediaRecorder: MediaRecorder | null = null
  private isRecording = false
  private mimeType: string | undefined
  private segments: AudioSegment[] = []
  private currentSegmentStartTime = 0
  private segmentTimer: number | null = null

  private readonly SEGMENT_DURATION_MS = 10_000
  private readonly MAX_BUFFER_DURATION_MS = 5 * 60 * 1000

  public async startCapture(): Promise<void> {
    if (this.isRecording) return

    this.segments = []
    this.currentSegmentStartTime = 0

    await this.startMicrophoneCapture()
    try {
      await this.startSystemAudioCapture()
    } catch (error) {
      console.warn("System audio capture failed, using microphone only.", error)
    }

    this.audioContext = new AudioContext({ sampleRate: 16000 })
    this.destination = this.audioContext.createMediaStreamDestination()

    if (this.micStream) {
      const micSource = this.audioContext.createMediaStreamSource(this.micStream)
      micSource.connect(this.destination)
    }

    if (this.systemStream) {
      const systemSource = this.audioContext.createMediaStreamSource(
        this.systemStream
      )
      systemSource.connect(this.destination)
    }

    this.isRecording = true
    this.startRecorderCycle()
  }

  public stopCapture(): void {
    this.isRecording = false

    if (this.segmentTimer) {
      window.clearTimeout(this.segmentTimer)
      this.segmentTimer = null
    }

    if (this.mediaRecorder && this.mediaRecorder.state !== "inactive") {
      this.mediaRecorder.stop()
    }

    this.micStream?.getTracks().forEach((track) => track.stop())
    this.systemStream?.getTracks().forEach((track) => track.stop())
    this.destination?.stream.getTracks().forEach((track) => track.stop())
    this.audioContext?.close()

    this.mediaRecorder = null
    this.micStream = null
    this.systemStream = null
    this.destination = null
    this.audioContext = null
    this.mimeType = undefined
    this.segments = []
    this.currentSegmentStartTime = 0
  }

  public async getLastMinutes(
    minutes: number
  ): Promise<{ blob: Blob; mimeType: string | undefined }> {
    await this.flushSegment()

    const targetDuration = minutes * 60 * 1000
    const now = Date.now()
    const cutoffTime = now - targetDuration

    this.rotateBuffer()

    const relevantSegments = this.segments.filter(
      (segment) => segment.endTime > cutoffTime
    )

    if (relevantSegments.length === 0) {
      return {
        blob: new Blob([], { type: this.mimeType }),
        mimeType: this.mimeType
      }
    }

    const mimeType = relevantSegments[0]?.mimeType || this.mimeType

    // ВАЖНО: WebM файлы нельзя просто конкатенировать - каждый имеет свой заголовок.
    // При объединении нескольких WebM блобов, только первый будет корректно читаться.
    // Для полного объединения нужен remuxer (ffmpeg.wasm), но это сложно.
    //
    // ТЕКУЩЕЕ РЕШЕНИЕ: возвращаем только ПОСЛЕДНИЙ сегмент (самый свежий).
    // Это гарантирует, что каждый раз возвращается новые данные.
    const lastSegment = relevantSegments[relevantSegments.length - 1]

    console.log('[ContinuousRecordingHelper] getLastMinutes:', {
      requestedMinutes: minutes,
      totalSegments: this.segments.length,
      relevantSegmentsCount: relevantSegments.length,
      returnedSegmentSize: lastSegment.blob.size,
      allSegmentSizes: relevantSegments.map(s => s.blob.size),
      segmentTimes: relevantSegments.map(s => ({
        start: new Date(s.startTime).toISOString(),
        end: new Date(s.endTime).toISOString(),
        durationMs: s.endTime - s.startTime
      }))
    })

    // Если сегментов несколько, логируем предупреждение
    if (relevantSegments.length > 1) {
      console.warn('[ContinuousRecordingHelper] Multiple segments found, but only returning the last one due to WebM concatenation issues. Consider using longer segments or ffmpeg.wasm for proper merging.')
    }

    return { blob: lastSegment.blob, mimeType }
  }

  public getBufferDuration(): number {
    if (this.segments.length === 0) {
      if (!this.isRecording || !this.currentSegmentStartTime) {
        return 0
      }
      return Math.min(
        Date.now() - this.currentSegmentStartTime,
        this.MAX_BUFFER_DURATION_MS
      )
    }

    const startTime = this.segments[0].startTime
    const lastSegment = this.segments[this.segments.length - 1]
    const endTime = this.isRecording ? Date.now() : lastSegment?.endTime
    if (!endTime) return 0
    return Math.min(endTime - startTime, this.MAX_BUFFER_DURATION_MS)
  }

  public isActive(): boolean {
    return this.isRecording
  }

  private rotateBuffer(): void {
    const cutoffTime = Date.now() - this.MAX_BUFFER_DURATION_MS
    this.segments = this.segments.filter(
      (segment) => segment.endTime > cutoffTime
    )
  }

  private startRecorderCycle(): void {
    if (!this.destination || !this.isRecording) return

    if (this.segmentTimer) {
      window.clearTimeout(this.segmentTimer)
      this.segmentTimer = null
    }

    this.mimeType = this.mimeType || this.pickMimeType()
    const options = this.mimeType ? { mimeType: this.mimeType } : undefined
    const recorder = new MediaRecorder(this.destination.stream, options)
    this.mediaRecorder = recorder
    this.currentSegmentStartTime = Date.now()

    recorder.addEventListener("dataavailable", (event) => {
      console.log('[ContinuousRecordingHelper] dataavailable:', {
        hasData: !!event.data,
        dataSize: event.data?.size || 0,
        currentSegmentStartTime: this.currentSegmentStartTime,
        segmentsCountBefore: this.segments.length
      })

      if (!event.data || event.data.size === 0) {
        console.log('[ContinuousRecordingHelper] dataavailable: empty data, skipping')
        return
      }

      const endTime = Date.now()
      const segmentMimeType = this.mimeType || event.data.type || "audio/webm"

      this.segments.push({
        blob: event.data,
        startTime: this.currentSegmentStartTime || endTime,
        endTime,
        mimeType: segmentMimeType
      })

      console.log('[ContinuousRecordingHelper] segment added:', {
        segmentSize: event.data.size,
        startTime: new Date(this.currentSegmentStartTime || endTime).toISOString(),
        endTime: new Date(endTime).toISOString(),
        totalSegments: this.segments.length
      })

      this.rotateBuffer()
    })

    recorder.addEventListener("stop", () => {
      if (!this.isRecording) return
      this.startRecorderCycle()
    })

    recorder.start()
    this.segmentTimer = window.setTimeout(() => {
      if (recorder.state === "recording") {
        recorder.stop()
      }
    }, this.SEGMENT_DURATION_MS)
  }

  private async flushSegment(): Promise<void> {
    const recorder = this.mediaRecorder
    console.log('[ContinuousRecordingHelper] flushSegment called:', {
      hasRecorder: !!recorder,
      recorderState: recorder?.state,
      segmentsCountBefore: this.segments.length
    })

    if (!recorder || recorder.state !== "recording") {
      console.log('[ContinuousRecordingHelper] flushSegment: no active recorder, returning')
      return
    }

    if (this.segmentTimer) {
      window.clearTimeout(this.segmentTimer)
      this.segmentTimer = null
    }

    await new Promise<void>((resolve) => {
      recorder.addEventListener(
        "stop",
        () => {
          console.log('[ContinuousRecordingHelper] flushSegment: recorder stopped, segments:', this.segments.length)
          resolve()
        },
        { once: true }
      )
      recorder.stop()
    })
  }

  private async startMicrophoneCapture(): Promise<void> {
    this.micStream = await navigator.mediaDevices.getUserMedia({
      audio: true,
      video: false
    })
  }

  private async startSystemAudioCapture(): Promise<void> {
    const sources = await window.electronAPI.voice.getDesktopSources()
    const screenSource = sources?.[0]
    if (!screenSource) {
      return
    }

    const constraints = {
      audio: {
        mandatory: {
          chromeMediaSource: "desktop",
          chromeMediaSourceId: screenSource.id
        }
      },
      video: {
        mandatory: {
          chromeMediaSource: "desktop",
          chromeMediaSourceId: screenSource.id
        }
      }
    } as unknown as MediaStreamConstraints

    const stream = await navigator.mediaDevices.getUserMedia(constraints)
    const audioTracks = stream.getAudioTracks()
    this.systemStream = new MediaStream(audioTracks)
    stream.getVideoTracks().forEach((track) => track.stop())
  }

  private pickMimeType(): string | undefined {
    const candidates = [
      "audio/webm;codecs=opus",
      "audio/webm",
      "audio/ogg;codecs=opus"
    ]

    return candidates.find((type) => MediaRecorder.isTypeSupported(type))
  }
}
