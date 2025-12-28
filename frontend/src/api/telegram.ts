import apiClient from './client';
import type {
  TelegramNotificationSettings,
  UpdateTelegramNotificationSettingsRequest,
  GenerateTelegramLinkTokenResponse,
  SendTestNotificationResponse,
} from '../types/api';

export const getTelegramSettings = async (): Promise<TelegramNotificationSettings> => {
  const response = await apiClient.get<TelegramNotificationSettings>('/api/telegram/settings');
  return response.data;
};

export const updateTelegramSettings = async (
  data: UpdateTelegramNotificationSettingsRequest
): Promise<TelegramNotificationSettings> => {
  const response = await apiClient.put<TelegramNotificationSettings>(
    '/api/telegram/settings',
    data
  );
  return response.data;
};

export const generateTelegramLinkToken = async (): Promise<GenerateTelegramLinkTokenResponse> => {
  const response = await apiClient.post<GenerateTelegramLinkTokenResponse>(
    '/api/telegram/link-token'
  );
  return response.data;
};

export const unlinkTelegramAccount = async (): Promise<void> => {
  await apiClient.post('/api/telegram/unlink');
};

export const sendTestTelegramNotification = async (): Promise<SendTestNotificationResponse> => {
  const response = await apiClient.post<SendTestNotificationResponse>(
    '/api/telegram/test-notification'
  );
  return response.data;
};
