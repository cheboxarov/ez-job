import { useEffect, useRef } from "react"
import { TranscriptionChunk as Chunk } from "../../types/voice"
import { TranscriptionChunk } from "./TranscriptionChunk"

interface TranscriptionListProps {
  chunks: Chunk[]
  onToggle: (id: string) => void
}

export function TranscriptionList({
  chunks,
  onToggle
}: TranscriptionListProps) {
  const listRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!listRef.current) return
    listRef.current.scrollTop = listRef.current.scrollHeight
  }, [chunks.length])

  if (chunks.length === 0) {
    return (
      <div className="rounded-md border border-dashed border-white/10 bg-black/30 p-6 text-center text-sm text-white/60">
        No transcription chunks yet. Start recording to capture the interview.
      </div>
    )
  }

  return (
    <div
      ref={listRef}
      className="max-h-[320px] space-y-2 overflow-y-auto pr-1"
    >
      {chunks.map((chunk) => (
        <TranscriptionChunk
          key={chunk.id}
          chunk={chunk}
          onToggle={onToggle}
        />
      ))}
    </div>
  )
}
