import React, { useEffect, useState } from "react"
import { Dialog, DialogContent } from "./ui/dialog"
import { Button } from "./ui/button"
import { useToast } from "../contexts/toast"
import { useTranslation } from "react-i18next"

export const UpdateNotification: React.FC = () => {
  const [updateAvailable, setUpdateAvailable] = useState(false)
  const [updateDownloaded, setUpdateDownloaded] = useState(false)
  const [isDownloading, setIsDownloading] = useState(false)
  const { showToast } = useToast()
  const { t } = useTranslation()

  useEffect(() => {
    console.log("UpdateNotification: Setting up event listeners")

    const unsubscribeAvailable = window.electronAPI.onUpdateAvailable(
      (info) => {
        console.log("UpdateNotification: Update available received", info)
        setUpdateAvailable(true)
      }
    )

    const unsubscribeDownloaded = window.electronAPI.onUpdateDownloaded(
      (info) => {
        console.log("UpdateNotification: Update downloaded received", info)
        setUpdateDownloaded(true)
        setIsDownloading(false)
      }
    )

    return () => {
      console.log("UpdateNotification: Cleaning up event listeners")
      unsubscribeAvailable()
      unsubscribeDownloaded()
    }
  }, [])

  const handleStartUpdate = async () => {
    console.log("UpdateNotification: Starting update download")
    setIsDownloading(true)
    const result = await window.electronAPI.startUpdate()
    console.log("UpdateNotification: Update download result", result)
    if (!result.success) {
      setIsDownloading(false)
      showToast(
        t("common.errorTitle"),
        t("errors.failedToDownloadUpdate"),
        "error"
      )
    }
  }

  const handleInstallUpdate = () => {
    console.log("UpdateNotification: Installing update")
    window.electronAPI.installUpdate()
  }

  console.log("UpdateNotification: Render state", {
    updateAvailable,
    updateDownloaded,
    isDownloading
  })
  if (!updateAvailable && !updateDownloaded) return null

  return (
    <Dialog open={true}>
      <DialogContent
        className="bg-black/90 text-white border-white/20"
        onPointerDownOutside={(e) => e.preventDefault()}
      >
        <div className="p-4">
          <h2 className="text-lg font-semibold mb-4">
            {updateDownloaded
              ? t("update.readyToInstall")
              : t("update.newVersionAvailable")}
          </h2>
          <p className="text-sm text-white/70 mb-6">
            {updateDownloaded
              ? t("update.downloadedDescription")
              : t("update.availableDescription")}
          </p>
          <div className="flex justify-end gap-2">
            {updateDownloaded ? (
              <Button
                variant="outline"
                onClick={handleInstallUpdate}
                className="border-white/20 hover:bg-white/10"
              >
                {t("update.restartAndInstall")}
              </Button>
            ) : (
              <Button
                variant="outline"
                onClick={handleStartUpdate}
                disabled={isDownloading}
                className="border-white/20 hover:bg-white/10"
              >
                {isDownloading ? t("update.downloading") : t("update.download")}
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
