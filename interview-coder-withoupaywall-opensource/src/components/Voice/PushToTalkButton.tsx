import { Button } from "../ui/button"
import { PushToTalkState } from "../../types/voice"
import { useTranslation } from "react-i18next"

interface PushToTalkButtonProps {
  state: PushToTalkState
  onStart: () => void
  onStop: () => void
}

export function PushToTalkButton({
  state,
  onStart,
  onStop
}: PushToTalkButtonProps) {
  const { t } = useTranslation()
  const { isRecording, isProcessing } = state

  if (isProcessing) {
    return (
      <Button className="w-full bg-white/10 text-white" disabled>
        {t("voice.ptt.processing")}
      </Button>
    )
  }

  return (
    <Button
      onClick={isRecording ? onStop : onStart}
      className={`w-full ${
        isRecording ? "bg-red-500 text-white animate-pulse" : "bg-white text-black"
      }`}
    >
      {isRecording ? t("voice.ptt.stopAndProcess") : t("voice.ptt.startRecording")}
    </Button>
  )
}
