import { Button } from "../ui/button"

interface AudioControlsProps {
  isRecording: boolean
  onStart: () => void
  onStop: () => void
}

export function AudioControls({
  isRecording,
  onStart,
  onStop
}: AudioControlsProps) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex items-center gap-2 text-sm text-white/80">
        <span
          className={`h-2.5 w-2.5 rounded-full ${
            isRecording ? "bg-red-500 animate-pulse" : "bg-white/30"
          }`}
        />
        {isRecording ? "Recording" : "Idle"}
      </div>
      <Button
        variant="outline"
        className="border-white/10 text-white"
        onClick={onStart}
        disabled={isRecording}
      >
        Start
      </Button>
      <Button
        variant="outline"
        className="border-white/10 text-white"
        onClick={onStop}
        disabled={!isRecording}
      >
        Stop
      </Button>
    </div>
  )
}
