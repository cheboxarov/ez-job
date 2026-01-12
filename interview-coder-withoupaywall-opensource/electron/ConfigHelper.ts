// ConfigHelper.ts
import fs from "node:fs"
import path from "node:path"
import { app } from "electron"
import { EventEmitter } from "events"
import axios from "axios"

interface Config {
  apiKey: string;
  baseUrl: string;
  model: string;
  language: string;
  interfaceLanguage: string;
  opacity: number;
}

export class ConfigHelper extends EventEmitter {
  private configPath: string;
  private defaultConfig: Config = {
    apiKey: "",
    baseUrl: "https://api.openai.com/v1",
    model: "gpt-4o",
    language: "python",
    interfaceLanguage: "en",
    opacity: 1.0
  };

  constructor() {
    super();
    // Use the app's user data directory to store the config
    try {
      this.configPath = path.join(app.getPath('userData'), 'config.json');
      console.log('Config path:', this.configPath);
    } catch (err) {
      console.warn('Could not access user data path, using fallback');
      this.configPath = path.join(process.cwd(), 'config.json');
    }

    // Ensure the initial config file exists
    this.ensureConfigExists();
  }

  /**
   * Ensure config file exists
   */
  private ensureConfigExists(): void {
    try {
      if (!fs.existsSync(this.configPath)) {
        this.saveConfig(this.defaultConfig);
      }
    } catch (err) {
      console.error("Error ensuring config exists:", err);
    }
  }

  private normalizeBaseUrl(baseUrl: string): string {
    const trimmed = baseUrl.trim();
    if (!trimmed) {
      return this.defaultConfig.baseUrl;
    }
    return trimmed.replace(/\/+$/, "");
  }

  private normalizeConfig(raw: Partial<Config> & Record<string, unknown>): Config {
    const legacyModel = [
      raw.model,
      raw.solutionModel,
      raw.extractionModel,
      raw.debuggingModel
    ].find((value) => typeof value === "string" && value.trim().length > 0) as
      | string
      | undefined;

    const model = legacyModel ? legacyModel.trim() : this.defaultConfig.model;
    const baseUrlValue = typeof raw.baseUrl === "string" ? raw.baseUrl : "";
    const interfaceLanguageValue =
      typeof raw.interfaceLanguage === "string" ? raw.interfaceLanguage.trim() : "";
    const interfaceLanguage =
      interfaceLanguageValue === "ru" ? "ru" : this.defaultConfig.interfaceLanguage;

    return {
      apiKey: typeof raw.apiKey === "string" ? raw.apiKey : this.defaultConfig.apiKey,
      baseUrl: this.normalizeBaseUrl(baseUrlValue || this.defaultConfig.baseUrl),
      model,
      language: typeof raw.language === "string" && raw.language.trim()
        ? raw.language
        : this.defaultConfig.language,
      interfaceLanguage,
      opacity: typeof raw.opacity === "number" ? raw.opacity : this.defaultConfig.opacity
    };
  }

  private getCurrentConfigPath(): string {
    try {
      return path.join(app.getPath('userData'), 'config.json');
    } catch (err) {
      console.warn("Could not resolve current userData path:", err);
      return this.configPath;
    }
  }

  private buildApiUrl(baseUrl: string, pathFragment: string): string {
    const normalizedBaseUrl = this.normalizeBaseUrl(baseUrl);
    const normalizedPath = pathFragment.startsWith("/")
      ? pathFragment
      : `/${pathFragment}`;
    return `${normalizedBaseUrl}${normalizedPath}`;
  }

  public loadConfig(): Config {
    try {
      if (fs.existsSync(this.configPath)) {
        const configData = fs.readFileSync(this.configPath, 'utf8');
        const config = JSON.parse(configData);
        const normalized = this.normalizeConfig(config);

        if (
          !config.baseUrl ||
          !config.model ||
          !config.interfaceLanguage ||
          config.apiProvider ||
          config.extractionModel ||
          config.solutionModel ||
          config.debuggingModel
        ) {
          this.saveConfig(normalized);
        }

        return normalized;
      }

      // If no config exists, create a default one
      this.saveConfig(this.defaultConfig);
      return this.defaultConfig;
    } catch (err) {
      console.error("Error loading config:", err);
      return this.defaultConfig;
    }
  }

  /**
   * Save configuration to disk
   */
  public saveConfig(config: Config): void {
    try {
      // Ensure the directory exists
      const configDir = path.dirname(this.configPath);
      if (!fs.existsSync(configDir)) {
        fs.mkdirSync(configDir, { recursive: true });
      }
      // Write the config file
      fs.writeFileSync(this.configPath, JSON.stringify(config, null, 2));
    } catch (err) {
      console.error("Error saving config:", err);
    }
  }

  /**
   * Update specific configuration values
   */
  public updateConfig(updates: Partial<Config>): Config {
    try {
      const currentConfig = this.loadConfig();
      const mergedConfig = { ...currentConfig, ...updates };
      const normalizedConfig = this.normalizeConfig(mergedConfig);
      this.saveConfig(normalizedConfig);

      // Only emit update event for changes other than opacity
      // This prevents re-initializing the AI client when only opacity changes
      if (
        updates.apiKey !== undefined ||
        updates.baseUrl !== undefined ||
        updates.model !== undefined ||
        updates.language !== undefined ||
        updates.interfaceLanguage !== undefined
      ) {
        this.emit('config-updated', normalizedConfig);
      }

      return normalizedConfig;
    } catch (error) {
      console.error('Error updating config:', error);
      return this.defaultConfig;
    }
  }

  /**
   * Reset configuration to defaults and remove any legacy config files.
   */
  public resetConfig(): Config {
    try {
      const currentPath = this.getCurrentConfigPath();
      const pathsToRemove = new Set([this.configPath, currentPath]);

      for (const configPath of pathsToRemove) {
        try {
          if (fs.existsSync(configPath)) {
            fs.rmSync(configPath, { force: true });
          }
        } catch (error) {
          console.error(`Error deleting config at ${configPath}:`, error);
        }
      }

      this.configPath = currentPath;
      const freshConfig = { ...this.defaultConfig };
      this.saveConfig(freshConfig);
      this.emit('config-updated', freshConfig);
      return freshConfig;
    } catch (error) {
      console.error("Error resetting config:", error);
      return this.defaultConfig;
    }
  }

  /**
   * Check if the API key is configured
   */
  public hasApiKey(): boolean {
    const config = this.loadConfig();
    return !!config.apiKey && config.apiKey.trim().length > 0;
  }

  /**
   * Validate the API key format
   */
  public isValidApiKeyFormat(apiKey: string): boolean {
    return !!apiKey && apiKey.trim().length > 0;
  }

  /**
   * Get the stored opacity value
   */
  public getOpacity(): number {
    const config = this.loadConfig();
    return config.opacity !== undefined ? config.opacity : 1.0;
  }

  /**
   * Set the window opacity value
   */
  public setOpacity(opacity: number): void {
    // Ensure opacity is between 0.1 and 1.0
    const validOpacity = Math.min(1.0, Math.max(0.1, opacity));
    this.updateConfig({ opacity: validOpacity });
  }

  /**
   * Get the preferred programming language
   */
  public getLanguage(): string {
    const config = this.loadConfig();
    return config.language || "python";
  }

  /**
   * Set the preferred programming language
   */
  public setLanguage(language: string): void {
    this.updateConfig({ language });
  }

  /**
   * Test API key with the selected provider
   */
  public async testApiKey(
    apiKey: string,
    baseUrl: string,
    model?: string
  ): Promise<{ valid: boolean; error?: string }> {
    if (!this.isValidApiKeyFormat(apiKey)) {
      return { valid: false, error: "API key is required." };
    }

    if (!baseUrl || !baseUrl.trim()) {
      return { valid: false, error: "Base URL is required." };
    }

    const headers = {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json'
    };

    try {
      const modelsUrl = this.buildApiUrl(baseUrl, "/models");
      await axios.get(modelsUrl, { headers, timeout: 10000 });
      return { valid: true };
    } catch (error: any) {
      const status = error?.response?.status;

      if (status === 401 || status === 403) {
        return { valid: false, error: "Invalid API key. Please check and try again." };
      }

      if (status === 404 && model) {
        try {
          const chatUrl = this.buildApiUrl(baseUrl, "/chat/completions");
          await axios.post(
            chatUrl,
            {
              model,
              messages: [{ role: "user", content: "ping" }],
              max_tokens: 1,
              temperature: 0
            },
            { headers, timeout: 10000 }
          );
          return { valid: true };
        } catch (fallbackError: any) {
          const fallbackStatus = fallbackError?.response?.status;
          if (fallbackStatus === 401 || fallbackStatus === 403) {
            return {
              valid: false,
              error: "Invalid API key. Please check and try again."
            };
          }
          if (fallbackStatus === 404) {
            return {
              valid: false,
              error: "Base URL did not respond to OpenAI-compatible endpoints. Ensure it includes /v1."
            };
          }
        }
      }

      if (status === 404) {
        return {
          valid: false,
          error: "Base URL did not respond to OpenAI-compatible endpoints. Ensure it includes /v1."
        };
      }

      if (status === 429) {
        return {
          valid: false,
          error: "Rate limit exceeded or insufficient quota. Please try again later."
        };
      }

      if (status && status >= 500) {
        return {
          valid: false,
          error: "Server error from the API provider. Please try again later."
        };
      }

      if (error?.code === 'ECONNREFUSED' || error?.code === 'ENOTFOUND') {
        return {
          valid: false,
          error: "Unable to reach the base URL. Please check the URL and your network connection."
        };
      }

      return {
        valid: false,
        error: error?.message || "Unknown error validating API key"
      };
    }
  }
}

// Export a singleton instance
export const configHelper = new ConfigHelper();
