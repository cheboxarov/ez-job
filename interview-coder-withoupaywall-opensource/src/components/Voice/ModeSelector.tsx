import { Button } from "../ui/button"
import { VoiceMode } from "../../types/voice"
import { useTranslation } from "react-i18next"

interface ModeSelectorProps {
  mode: VoiceMode
  onModeChange: (mode: VoiceMode) => void
}

export function ModeSelector({ mode, onModeChange }: ModeSelectorProps) {
  const { t } = useTranslation()

  return (
    <div className="flex flex-wrap gap-2">
      <Button
        variant={mode === "continuous" ? "default" : "outline"}
        className={mode === "continuous" ? "bg-white text-black" : "border-white/10 text-white"}
        onClick={() => onModeChange("continuous")}
      >
        {t("voice.mode.continuous")}
      </Button>
      <Button
        variant={mode === "push-to-talk" ? "default" : "outline"}
        className={mode === "push-to-talk" ? "bg-white text-black" : "border-white/10 text-white"}
        onClick={() => onModeChange("push-to-talk")}
      >
        {t("voice.mode.pushToTalk")}
      </Button>
    </div>
  )
}
