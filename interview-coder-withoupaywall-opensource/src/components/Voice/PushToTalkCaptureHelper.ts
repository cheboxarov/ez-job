export class PushToTalkCaptureHelper {
  private micStream: MediaStream | null = null
  private systemStream: MediaStream | null = null
  private mediaRecorder: MediaRecorder | null = null
  private audioContext: AudioContext | null = null
  private destination: MediaStreamAudioDestinationNode | null = null
  private audioChunks: Blob[] = []
  private mimeType: string | undefined

  public async startCapture(): Promise<void> {
    this.audioChunks = []
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

    this.mimeType = this.pickMimeType()
    const options = this.mimeType ? { mimeType: this.mimeType } : undefined
    this.mediaRecorder = new MediaRecorder(this.destination.stream, options)

    this.mediaRecorder.addEventListener("dataavailable", (event) => {
      if (event.data && event.data.size > 0) {
        this.audioChunks.push(event.data)
      }
    })

    this.mediaRecorder.start()
  }

  public async stopCapture(): Promise<{
    blob: Blob
    mimeType: string | undefined
  }> {
    const recorder = this.mediaRecorder
    if (!recorder || recorder.state === "inactive") {
      return { blob: new Blob([], { type: this.mimeType }), mimeType: this.mimeType }
    }

    const stopPromise = new Promise<void>((resolve) => {
      recorder.addEventListener(
        "stop",
        () => {
          resolve()
        },
        { once: true }
      )
    })

    recorder.stop()
    await stopPromise

    const blob = new Blob(this.audioChunks, { type: this.mimeType })

    this.cleanup()

    return { blob, mimeType: this.mimeType }
  }

  private cleanup(): void {
    this.micStream?.getTracks().forEach((track) => track.stop())
    this.systemStream?.getTracks().forEach((track) => track.stop())
    this.destination?.stream.getTracks().forEach((track) => track.stop())
    this.audioContext?.close()

    this.mediaRecorder = null
    this.micStream = null
    this.systemStream = null
    this.destination = null
    this.audioContext = null
    this.audioChunks = []
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
