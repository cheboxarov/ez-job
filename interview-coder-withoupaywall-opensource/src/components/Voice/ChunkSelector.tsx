import { Button } from "../ui/button"

interface ChunkSelectorProps {
  onSelectAll: () => void
  onClearSelection: () => void
  onClearAll: () => void
}

export function ChunkSelector({
  onSelectAll,
  onClearSelection,
  onClearAll
}: ChunkSelectorProps) {
  return (
    <div className="flex flex-wrap gap-2">
      <Button
        variant="outline"
        className="border-white/10 text-white"
        onClick={onSelectAll}
      >
        Select All
      </Button>
      <Button
        variant="outline"
        className="border-white/10 text-white"
        onClick={onClearSelection}
      >
        Clear Selection
      </Button>
      <Button
        variant="outline"
        className="border-white/10 text-white"
        onClick={onClearAll}
      >
        Clear All
      </Button>
    </div>
  )
}
