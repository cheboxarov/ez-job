import apiClient from './client';
import type {
  UserAutomationSettings,
  UpdateUserAutomationSettingsRequest,
} from '../types/api';

export const getAutomationSettings = async (): Promise<UserAutomationSettings> => {
  const response = await apiClient.get<UserAutomationSettings>('/api/settings/automation');
  return response.data;
};

export const updateAutomationSettings = async (
  data: UpdateUserAutomationSettingsRequest
): Promise<UserAutomationSettings> => {
  const response = await apiClient.put<UserAutomationSettings>(
    '/api/settings/automation',
    data
  );
  return response.data;
};
