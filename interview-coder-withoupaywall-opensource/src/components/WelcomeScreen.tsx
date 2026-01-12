import React from 'react';
import { Button } from './ui/button';
import { useTranslation } from 'react-i18next';

interface WelcomeScreenProps {
  onOpenSettings: () => void;
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onOpenSettings }) => {
  const { t } = useTranslation();

  return (
    <div className="bg-black min-h-screen flex flex-col items-center justify-center p-6">
      <div className="max-w-md w-full bg-black border border-white/10 rounded-xl p-6 shadow-lg">
        <h1 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
          <span>{t("app.name")}</span>
          <span className="text-sm font-normal px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded-md">
            {t("app.subtitle")}
          </span>
        </h1>
        
        <div className="mb-8">
          <h2 className="text-lg font-medium text-white mb-3">
            {t("welcome.title")}
          </h2>
          <p className="text-white/70 text-sm mb-4">
            {t("welcome.description")}
          </p>
          <div className="bg-white/5 border border-white/10 rounded-lg p-4 mb-4">
            <h3 className="text-white/90 font-medium mb-2">
              {t("welcome.globalShortcuts")}
            </h3>
            <ul className="space-y-2">
              <li className="flex justify-between text-sm">
                <span className="text-white/70">{t("shortcuts.toggleVisibility")}</span>
                <span className="text-white/90">Ctrl+B / Cmd+B</span>
              </li>
              <li className="flex justify-between text-sm">
                <span className="text-white/70">{t("shortcuts.takeScreenshot")}</span>
                <span className="text-white/90">Ctrl+H / Cmd+H</span>
              </li>
              <li className="flex justify-between text-sm">
                <span className="text-white/70">{t("shortcuts.deleteScreenshot")}</span>
                <span className="text-white/90">Ctrl+L / Cmd+L</span>
              </li>
              <li className="flex justify-between text-sm">
                <span className="text-white/70">{t("shortcuts.processScreenshots")}</span>
                <span className="text-white/90">Ctrl+Enter / Cmd+Enter</span>
              </li>
              <li className="flex justify-between text-sm">
                <span className="text-white/70">{t("shortcuts.resetView")}</span>
                <span className="text-white/90">Ctrl+R / Cmd+R</span>
              </li>
              <li className="flex justify-between text-sm">
                <span className="text-white/70">{t("shortcuts.quitApp")}</span>
                <span className="text-white/90">Ctrl+Q / Cmd+Q</span>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="bg-white/5 border border-white/10 rounded-lg p-4 mb-6">
          <h3 className="text-white/90 font-medium mb-2">
            {t("welcome.gettingStarted")}
          </h3>
          <p className="text-white/70 text-sm mb-3">
            {t("welcome.gettingStartedDescription")}
          </p>
          <Button 
            className="w-full px-4 py-3 bg-white text-black rounded-xl font-medium hover:bg-white/90 transition-colors flex items-center justify-center gap-2"
            onClick={onOpenSettings}
          >
            {t("welcome.openSettings")}
          </Button>
        </div>
        
        <div className="text-white/40 text-xs text-center">
          {t("welcome.startHint")}
        </div>
      </div>
    </div>
  );
};
