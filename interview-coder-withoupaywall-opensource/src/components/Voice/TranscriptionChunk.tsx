import { TranscriptionChunk as Chunk } from "../../types/voice"

interface TranscriptionChunkProps {
  chunk: Chunk
  onToggle: (id: string) => void
}

function formatTimestamp(timestamp: number): string {
  const date = new Date(timestamp)
  const hours = String(date.getHours()).padStart(2, "0")
  const minutes = String(date.getMinutes()).padStart(2, "0")
  const seconds = String(date.getSeconds()).padStart(2, "0")
  return `${hours}:${minutes}:${seconds}`
}

export function TranscriptionChunk({
  chunk,
  onToggle
}: TranscriptionChunkProps) {
  return (
    <label className="flex items-start gap-3 rounded-md border border-white/10 bg-black/40 px-3 py-2 text-white/90">
      <input
        type="checkbox"
        checked={chunk.selected}
        onChange={() => onToggle(chunk.id)}
        className="mt-1 h-4 w-4 accent-white/90"
      />
      <div className="flex-1">
        <div className="text-xs text-white/50">
          {formatTimestamp(chunk.timestamp)}
        </div>
        <div className="text-sm text-white/90">{chunk.text}</div>
      </div>
    </label>
  )
}
