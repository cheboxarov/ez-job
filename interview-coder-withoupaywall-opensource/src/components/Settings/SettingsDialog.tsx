import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "../ui/dialog";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import { useToast } from "../../contexts/toast";
import { useTranslation } from "react-i18next";

interface SettingsDialogProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}

export function SettingsDialog({ open: externalOpen, onOpenChange }: SettingsDialogProps) {
  const [open, setOpen] = useState(externalOpen || false);
  const [apiKey, setApiKey] = useState("");
  const [baseUrl, setBaseUrl] = useState("");
  const [model, setModel] = useState("");
  const [interfaceLanguage, setInterfaceLanguage] = useState("en");
  const [transcriptionEnabled, setTranscriptionEnabled] = useState(false);
  const [transcriptionBaseUrl, setTranscriptionBaseUrl] = useState("");
  const [transcriptionApiKey, setTranscriptionApiKey] = useState("");
  const [transcriptionModel, setTranscriptionModel] = useState("");
  const [transcriptionLanguage, setTranscriptionLanguage] = useState("ru");
  const [transcriptionChunkDurationMs, setTranscriptionChunkDurationMs] = useState(10000);
  const [transcriptionDefaultMode, setTranscriptionDefaultMode] = useState<"continuous" | "push-to-talk">("continuous");
  const [transcriptionPttPrompt, setTranscriptionPttPrompt] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [isTestingTranscription, setIsTestingTranscription] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const { showToast } = useToast();
  const { t, i18n } = useTranslation();

  // Sync with external open state
  useEffect(() => {
    if (externalOpen !== undefined) {
      setOpen(externalOpen);
    }
  }, [externalOpen]);

  // Handle open state changes
  const handleOpenChange = (newOpen: boolean) => {
    setOpen(newOpen);
    // Only call onOpenChange when there's actually a change
    if (onOpenChange && newOpen !== externalOpen) {
      onOpenChange(newOpen);
    }
  };

  // Load current config on dialog open
  useEffect(() => {
    if (open) {
      setIsLoading(true);
      interface Config {
        apiKey?: string;
        baseUrl?: string;
        model?: string;
        interfaceLanguage?: string;
        transcription?: {
          enabled?: boolean;
          baseUrl?: string;
          apiKey?: string;
          model?: string;
          language?: string;
          chunkDurationMs?: number;
          defaultMode?: "continuous" | "push-to-talk";
          pttPrompt?: string;
        };
      }

      window.electronAPI
        .getConfig()
        .then((config: Config) => {
          setApiKey(config.apiKey || "");
          setBaseUrl(config.baseUrl || "https://api.openai.com/v1");
          setModel(config.model || "gpt-4o");
          setInterfaceLanguage(config.interfaceLanguage || "en");
          setTranscriptionEnabled(!!config.transcription?.enabled);
          setTranscriptionBaseUrl(
            config.transcription?.baseUrl || "https://api.openai.com/v1"
          );
          setTranscriptionApiKey(config.transcription?.apiKey || "");
          setTranscriptionModel(config.transcription?.model || "whisper-1");
          setTranscriptionLanguage(config.transcription?.language || "ru");
          setTranscriptionChunkDurationMs(
            config.transcription?.chunkDurationMs || 10000
          );
          setTranscriptionDefaultMode(
            config.transcription?.defaultMode === "push-to-talk"
              ? "push-to-talk"
              : "continuous"
          );
          setTranscriptionPttPrompt(config.transcription?.pttPrompt || "");
        })
        .catch((error: unknown) => {
          console.error("Failed to load config:", error);
          showToast("Error", "Failed to load settings", "error");
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, [open, showToast]);

  const handleSave = async () => {
    setIsLoading(true);
    try {
      if (transcriptionEnabled) {
        if (
          !transcriptionBaseUrl.trim() ||
          !transcriptionApiKey.trim() ||
          !transcriptionModel.trim() ||
          !transcriptionLanguage.trim()
        ) {
          showToast(
            t("errors.missingInfoTitle"),
            t("errors.missingInfo"),
            "error"
          );
          setIsLoading(false);
          return;
        }
      }

      const rawDuration = Number.isFinite(transcriptionChunkDurationMs)
        ? transcriptionChunkDurationMs
        : 10000;
      const normalizedChunkDuration = Math.min(
        30000,
        Math.max(5000, Math.round(rawDuration))
      );

      const result = await window.electronAPI.updateConfig({
        apiKey,
        baseUrl,
        model,
        interfaceLanguage,
        transcription: {
          enabled: transcriptionEnabled,
          baseUrl: transcriptionBaseUrl,
          apiKey: transcriptionApiKey,
          model: transcriptionModel,
          language: transcriptionLanguage,
          chunkDurationMs: normalizedChunkDuration,
          defaultMode: transcriptionDefaultMode,
          pttPrompt: transcriptionPttPrompt
        }
      });

      if (result) {
        showToast(
          t("common.successTitle"),
          t("success.settingsSaved"),
          "success"
        );
        handleOpenChange(false);

        // Force reload the app to apply the API key
        setTimeout(() => {
          window.location.reload();
        }, 1500);
      }
    } catch (error) {
      console.error("Failed to save settings:", error);
      showToast(
        t("common.errorTitle"),
        t("errors.failedToSaveSettings"),
        "error"
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleTestConnection = async () => {
    if (!apiKey.trim() || !baseUrl.trim() || !model.trim()) {
      showToast(
        t("errors.missingInfoTitle"),
        t("errors.missingInfo"),
        "error"
      );
      return;
    }

    setIsTesting(true);
    try {
      const result = await window.electronAPI.validateApiKey({ apiKey, baseUrl, model });
      if (result.valid) {
        showToast(
          t("common.successTitle"),
          t("success.connectionVerified"),
          "success"
        );
      } else {
        showToast(
          t("errors.connectionFailedTitle"),
          result.error || t("errors.connectionFailed"),
          "error"
        );
      }
    } catch (error) {
      console.error("Failed to validate API key:", error);
      showToast(
        t("common.errorTitle"),
        t("errors.connectionFailed"),
        "error"
      );
    } finally {
      setIsTesting(false);
    }
  };

  const handleTestTranscription = async () => {
    if (
      !transcriptionBaseUrl.trim() ||
      !transcriptionApiKey.trim() ||
      !transcriptionModel.trim() ||
      !transcriptionLanguage.trim()
    ) {
      showToast(
        t("errors.missingInfoTitle"),
        t("errors.missingInfo"),
        "error"
      );
      return;
    }

    setIsTestingTranscription(true);
    try {
      const rawDuration = Number.isFinite(transcriptionChunkDurationMs)
        ? transcriptionChunkDurationMs
        : 10000;
      const normalizedChunkDuration = Math.min(
        30000,
        Math.max(5000, Math.round(rawDuration))
      );
      const result = await window.electronAPI.voice.validateConfig({
        enabled: transcriptionEnabled,
        baseUrl: transcriptionBaseUrl,
        apiKey: transcriptionApiKey,
        model: transcriptionModel,
        language: transcriptionLanguage,
        chunkDurationMs: normalizedChunkDuration,
        defaultMode: transcriptionDefaultMode,
        pttPrompt: transcriptionPttPrompt
      });
      if (result.valid) {
        showToast(
          t("common.successTitle"),
          t("success.transcriptionConnectionVerified"),
          "success"
        );
      } else {
        showToast(
          t("errors.connectionFailedTitle"),
          result.error || t("errors.connectionFailed"),
          "error"
        );
      }
    } catch (error) {
      console.error("Failed to validate transcription config:", error);
      showToast(
        t("common.errorTitle"),
        t("errors.connectionFailed"),
        "error"
      );
    } finally {
      setIsTestingTranscription(false);
    }
  };

  const handleResetAppData = async () => {
    const confirmed = window.confirm(t("settings.resetAppDataConfirm"));
    if (!confirmed) {
      return;
    }

    setIsResetting(true);
    try {
      const result = await window.electronAPI.resetAppData();
      if (result?.success) {
        showToast(
          t("common.successTitle"),
          t("success.resetAppData"),
          "success"
        );
        setTimeout(() => {
          window.location.reload();
        }, 1200);
      } else {
        showToast(
          t("common.errorTitle"),
          result?.error || t("errors.resetAppDataFailed"),
          "error"
        );
      }
    } catch (error) {
      console.error("Failed to reset app data:", error);
      showToast(
        t("common.errorTitle"),
        t("errors.resetAppDataFailed"),
        "error"
      );
    } finally {
      setIsResetting(false);
    }
  };

  // Mask API key for display
  const maskApiKey = (key: string) => {
    if (!key || key.length < 10) return "";
    return `${key.substring(0, 4)}...${key.substring(key.length - 4)}`;
  };

  const canSubmit = !!apiKey.trim() && !!baseUrl.trim() && !!model.trim();

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent
        className="sm:max-w-md bg-black border border-white/10 text-white settings-dialog"
        style={{
          position: "fixed",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: "min(450px, 90vw)",
          height: "auto",
          minHeight: "400px",
          maxHeight: "90vh",
          overflowY: "auto",
          zIndex: 9999,
          margin: 0,
          padding: "20px",
          transition: "opacity 0.25s ease, transform 0.25s ease",
          animation: "fadeIn 0.25s ease forwards",
          opacity: 0.98
        }}
      >
        <DialogHeader>
          <DialogTitle>{t("settings.title")}</DialogTitle>
          <DialogDescription className="text-white/70">
            {t("settings.description")}
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-white" htmlFor="baseUrl">
              {t("settings.baseUrl")}
            </label>
            <Input
              id="baseUrl"
              type="text"
              value={baseUrl}
              onChange={(e) => setBaseUrl(e.target.value)}
              placeholder="https://api.openai.com/v1"
              className="bg-black/50 border-white/10 text-white"
            />
            <p className="text-xs text-white/50">
              {t("settings.baseUrlHint")}
            </p>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-white" htmlFor="model">
              {t("settings.model")}
            </label>
            <Input
              id="model"
              type="text"
              value={model}
              onChange={(e) => setModel(e.target.value)}
              placeholder="gpt-4o"
              className="bg-black/50 border-white/10 text-white"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-white" htmlFor="apiKey">
              {t("settings.apiKey")}
            </label>
            <Input
              id="apiKey"
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder={t("settings.apiKeyPlaceholder")}
              className="bg-black/50 border-white/10 text-white"
            />
            {apiKey && (
              <p className="text-xs text-white/50">
                {t("settings.currentKey")} {maskApiKey(apiKey)}
              </p>
            )}
            <p className="text-xs text-white/50">
              {t("settings.apiKeyStoredNote")}
            </p>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-white" htmlFor="interfaceLanguage">
              {t("settings.interfaceLanguage")}
            </label>
            <select
              id="interfaceLanguage"
              value={interfaceLanguage}
              onChange={(e) => {
                const value = e.target.value;
                setInterfaceLanguage(value);
                i18n.changeLanguage(value);
              }}
              className="bg-black/50 border border-white/10 text-white rounded-md px-3 py-2 text-sm outline-none focus:border-white/20 w-full"
            >
              <option value="en" className="bg-black text-white">English</option>
              <option value="ru" className="bg-black text-white">Русский</option>
            </select>
          </div>

          <div className="space-y-2 mt-4">
            <label className="text-sm font-medium text-white mb-2 block">
              {t("settings.transcription.title")}
            </label>
            <div className="bg-black/30 border border-white/10 rounded-lg p-4 space-y-4">
              <label className="flex items-center gap-2 text-sm text-white">
                <input
                  type="checkbox"
                  checked={transcriptionEnabled}
                  onChange={(event) => setTranscriptionEnabled(event.target.checked)}
                  className="h-4 w-4 accent-white/90"
                />
                {t("settings.transcription.enabled")}
              </label>

              <div className="space-y-2">
                <label className="text-xs text-white/70" htmlFor="transcriptionBaseUrl">
                  {t("settings.transcription.baseUrl")}
                </label>
                <Input
                  id="transcriptionBaseUrl"
                  type="text"
                  value={transcriptionBaseUrl}
                  onChange={(e) => setTranscriptionBaseUrl(e.target.value)}
                  placeholder="https://api.openai.com/v1"
                  className="bg-black/50 border-white/10 text-white"
                  disabled={!transcriptionEnabled}
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs text-white/70" htmlFor="transcriptionModel">
                  {t("settings.transcription.model")}
                </label>
                <Input
                  id="transcriptionModel"
                  type="text"
                  value={transcriptionModel}
                  onChange={(e) => setTranscriptionModel(e.target.value)}
                  placeholder="whisper-1"
                  className="bg-black/50 border-white/10 text-white"
                  disabled={!transcriptionEnabled}
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs text-white/70" htmlFor="transcriptionLanguage">
                  {t("settings.transcription.language")}
                </label>
                <Input
                  id="transcriptionLanguage"
                  type="text"
                  value={transcriptionLanguage}
                  onChange={(e) => setTranscriptionLanguage(e.target.value)}
                  placeholder="ru"
                  className="bg-black/50 border-white/10 text-white"
                  disabled={!transcriptionEnabled}
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs text-white/70" htmlFor="transcriptionApiKey">
                  {t("settings.transcription.apiKey")}
                </label>
                <Input
                  id="transcriptionApiKey"
                  type="password"
                  value={transcriptionApiKey}
                  onChange={(e) => setTranscriptionApiKey(e.target.value)}
                  placeholder={t("settings.apiKeyPlaceholder")}
                  className="bg-black/50 border-white/10 text-white"
                  disabled={!transcriptionEnabled}
                />
                {transcriptionApiKey && (
                  <p className="text-xs text-white/50">
                    {t("settings.currentKey")} {maskApiKey(transcriptionApiKey)}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-xs text-white/70" htmlFor="transcriptionDefaultMode">
                  {t("settings.transcription.defaultMode")}
                </label>
                <select
                  id="transcriptionDefaultMode"
                  value={transcriptionDefaultMode}
                  onChange={(e) =>
                    setTranscriptionDefaultMode(
                      e.target.value === "push-to-talk" ? "push-to-talk" : "continuous"
                    )
                  }
                  className="bg-black/50 border border-white/10 text-white rounded-md px-3 py-2 text-sm outline-none focus:border-white/20 w-full"
                  disabled={!transcriptionEnabled}
                >
                  <option value="continuous" className="bg-black text-white">
                    {t("voice.mode.continuous")}
                  </option>
                  <option value="push-to-talk" className="bg-black text-white">
                    {t("voice.mode.pushToTalk")}
                  </option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-xs text-white/70" htmlFor="transcriptionPttPrompt">
                  {t("settings.transcription.pttPrompt")}
                </label>
                <textarea
                  id="transcriptionPttPrompt"
                  value={transcriptionPttPrompt}
                  onChange={(e) => setTranscriptionPttPrompt(e.target.value)}
                  placeholder={t("settings.transcription.pttPromptPlaceholder")}
                  className="min-h-[90px] w-full rounded-md border border-white/10 bg-black/50 px-3 py-2 text-sm text-white outline-none focus:border-white/20"
                  disabled={!transcriptionEnabled}
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs text-white/70" htmlFor="transcriptionChunkDuration">
                  {t("settings.transcription.chunkDuration")}
                </label>
                <Input
                  id="transcriptionChunkDuration"
                  type="number"
                  value={transcriptionChunkDurationMs}
                  min={5000}
                  max={30000}
                  step={1000}
                  onChange={(e) => {
                    const value = Number(e.target.value)
                    setTranscriptionChunkDurationMs(Number.isFinite(value) ? value : 0)
                  }}
                  className="bg-black/50 border-white/10 text-white"
                  disabled={!transcriptionEnabled}
                />
                <p className="text-xs text-white/50">
                  {t("settings.transcription.chunkDurationHint")}
                </p>
              </div>

              <Button
                variant="outline"
                onClick={handleTestTranscription}
                className="w-full border-white/10 text-white"
                disabled={!transcriptionEnabled || isTestingTranscription}
              >
                {isTestingTranscription
                  ? t("settings.testing")
                  : t("settings.transcription.testConnection")}
              </Button>
            </div>
          </div>

          <div className="space-y-2 mt-4">
            <label className="text-sm font-medium text-white mb-2 block">
              {t("settings.maintenance")}
            </label>
            <div className="bg-black/30 border border-white/10 rounded-lg p-3 space-y-2">
              <p className="text-xs text-white/60">
                {t("settings.resetAppDataDescription")}
              </p>
              <Button
                variant="destructive"
                onClick={handleResetAppData}
                className="w-full"
                disabled={isLoading || isResetting}
              >
                {isResetting ? t("settings.resetting") : t("settings.resetAppData")}
              </Button>
            </div>
          </div>

          <div className="space-y-2 mt-4">
            <label className="text-sm font-medium text-white mb-2 block">
              {t("settings.keyboardShortcuts")}
            </label>
            <div className="bg-black/30 border border-white/10 rounded-lg p-3">
              <div className="grid grid-cols-2 gap-y-2 text-xs">
                <div className="text-white/70">{t("shortcuts.toggleVisibility")}</div>
                <div className="text-white/90 font-mono">Ctrl+B / Cmd+B</div>

                <div className="text-white/70">{t("shortcuts.takeScreenshot")}</div>
                <div className="text-white/90 font-mono">Ctrl+H / Cmd+H</div>

                <div className="text-white/70">{t("shortcuts.processScreenshots")}</div>
                <div className="text-white/90 font-mono">Ctrl+Enter / Cmd+Enter</div>

                <div className="text-white/70">{t("shortcuts.deleteScreenshot")}</div>
                <div className="text-white/90 font-mono">Ctrl+L / Cmd+L</div>

                <div className="text-white/70">{t("shortcuts.resetView")}</div>
                <div className="text-white/90 font-mono">Ctrl+R / Cmd+R</div>

                <div className="text-white/70">{t("shortcuts.voiceAssistant")}</div>
                <div className="text-white/90 font-mono">Ctrl+Shift+V / Cmd+Shift+V</div>

                <div className="text-white/70">{t("shortcuts.quitApp")}</div>
                <div className="text-white/90 font-mono">Ctrl+Q / Cmd+Q</div>

                <div className="text-white/70">{t("shortcuts.moveWindow")}</div>
                <div className="text-white/90 font-mono">Ctrl+Arrow Keys</div>

                <div className="text-white/70">{t("shortcuts.decreaseOpacity")}</div>
                <div className="text-white/90 font-mono">Ctrl+[ / Cmd+[</div>

                <div className="text-white/70">{t("shortcuts.increaseOpacity")}</div>
                <div className="text-white/90 font-mono">Ctrl+] / Cmd+]</div>

                <div className="text-white/70">{t("shortcuts.zoomOut")}</div>
                <div className="text-white/90 font-mono">Ctrl+- / Cmd+-</div>

                <div className="text-white/70">{t("shortcuts.resetZoom")}</div>
                <div className="text-white/90 font-mono">Ctrl+0 / Cmd+0</div>

                <div className="text-white/70">{t("shortcuts.zoomIn")}</div>
                <div className="text-white/90 font-mono">Ctrl+= / Cmd+=</div>
              </div>
            </div>
          </div>
        </div>
        <DialogFooter className="flex justify-between sm:justify-between gap-2">
          <Button
            variant="outline"
            onClick={() => handleOpenChange(false)}
            className="border-white/10 hover:bg-white/5 text-white"
          >
            {t("settings.cancel")}
          </Button>
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={handleTestConnection}
              className="border-white/10 hover:bg-white/5 text-white"
              disabled={isLoading || isTesting || !canSubmit}
            >
              {isTesting ? t("settings.testing") : t("settings.testConnection")}
            </Button>
            <Button
              className="px-4 py-3 bg-white text-black rounded-xl font-medium hover:bg-white/90 transition-colors"
              onClick={handleSave}
              disabled={isLoading || !canSubmit}
            >
              {isLoading ? t("settings.saving") : t("settings.save")}
            </Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
