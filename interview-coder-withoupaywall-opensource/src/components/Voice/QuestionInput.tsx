import { useState, type FormEvent } from "react"
import { TranscriptionChunk } from "../../types/voice"
import { Button } from "../ui/button"
import { Input } from "../ui/input"

interface QuestionInputProps {
  onSubmit: (question: string, chunks: TranscriptionChunk[]) => void
  selectedChunks: TranscriptionChunk[]
  disabled?: boolean
}

export function QuestionInput({
  onSubmit,
  selectedChunks,
  disabled
}: QuestionInputProps) {
  const [question, setQuestion] = useState("")

  const canSubmit = !disabled && selectedChunks.length > 0

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
    if (!canSubmit) return
    onSubmit(question.trim(), selectedChunks)
    setQuestion("")
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="space-y-1">
        <label className="text-sm text-white/80" htmlFor="voice-question">
          Optional follow-up question
        </label>
        <Input
          id="voice-question"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask the assistant to refine the answer..."
          className="bg-black/50 border-white/10 text-white"
          disabled={disabled}
        />
      </div>
      <Button
        type="submit"
        className="w-full bg-white text-black hover:bg-white/90"
        disabled={!canSubmit}
      >
        Send to Assistant
      </Button>
    </form>
  )
}
