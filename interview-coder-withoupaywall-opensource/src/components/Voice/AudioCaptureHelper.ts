export class AudioCaptureHelper {
  private micStream: MediaStream | null = null
  private systemStream: MediaStream | null = null
  private mediaRecorder: MediaRecorder | null = null
  private audioContext: AudioContext | null = null
  private destination: MediaStreamAudioDestinationNode | null = null
  private chunkDurationMs: number
  private isCapturing = false
  private chunkTimer: number | null = null
  private currentMimeType: string | undefined

  public onChunkReady?: (chunk: Blob, timestamp: number) => void

  constructor(chunkDurationMs: number) {
    this.chunkDurationMs = chunkDurationMs
  }

  public async startMicrophoneCapture(): Promise<void> {
    this.micStream = await navigator.mediaDevices.getUserMedia({
      audio: true,
      video: false
    })
  }

  public async startSystemAudioCapture(): Promise<void> {
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

  public async startCombinedCapture(): Promise<void> {
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

    this.currentMimeType = this.pickMimeType()
    this.isCapturing = true
    this.startRecorderCycle()
  }

  public stopCapture(): void {
    this.isCapturing = false
    if (this.chunkTimer) {
      window.clearTimeout(this.chunkTimer)
      this.chunkTimer = null
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
    this.currentMimeType = undefined
  }

  private pickMimeType(): string | undefined {
    const candidates = [
      "audio/webm;codecs=opus",
      "audio/webm",
      "audio/ogg;codecs=opus"
    ]

    return candidates.find((type) => MediaRecorder.isTypeSupported(type))
  }

  private startRecorderCycle(): void {
    if (!this.destination || !this.isCapturing) return

    const options = this.currentMimeType ? { mimeType: this.currentMimeType } : undefined
    const recorder = new MediaRecorder(this.destination.stream, options)
    this.mediaRecorder = recorder

    recorder.addEventListener("dataavailable", (event) => {
      console.log("[AudioCaptureHelper] dataavailable event:", {
        hasData: !!event.data,
        size: event.data?.size || 0,
        recorderState: recorder.state,
        mimeType: this.currentMimeType
      })

      if (event.data && event.data.size > 0) {
        console.log("[AudioCaptureHelper] Calling onChunkReady:", {
          size: event.data.size,
          recorderState: recorder.state
        })
        this.onChunkReady?.(event.data, Date.now())
      } else {
        console.warn("[AudioCaptureHelper] Chunk rejected - empty or zero size:", {
          hasData: !!event.data,
          size: event.data?.size || 0
        })
      }
    })

    recorder.addEventListener("stop", () => {
      if (!this.isCapturing) return
      this.startRecorderCycle()
    })

    recorder.addEventListener("start", () => {
      console.log("[AudioCaptureHelper] MediaRecorder started")
    })

    recorder.addEventListener("pause", () => {
      console.warn("[AudioCaptureHelper] MediaRecorder paused!")
    })

    recorder.addEventListener("resume", () => {
      console.log("[AudioCaptureHelper] MediaRecorder resumed")
    })

    recorder.start()
    this.chunkTimer = window.setTimeout(() => {
      if (recorder.state === "recording") {
        recorder.stop()
      }
    }, this.chunkDurationMs)
  }
}
