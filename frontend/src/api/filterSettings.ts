import apiClient from './client';
import type { UserFilterSettings, UserFilterSettingsUpdate, SuggestedUserFilterSettings } from '../types/api';

export const getUserFilterSettings = async (): Promise<UserFilterSettings> => {
  const response = await apiClient.get<UserFilterSettings>('/api/users/me/filter-settings');
  return response.data;
};

export const updateUserFilterSettings = async (
  data: UserFilterSettingsUpdate,
): Promise<UserFilterSettings> => {
  const response = await apiClient.put<UserFilterSettings>(
    '/api/users/me/filter-settings',
    data,
  );
  return response.data;
};

export const suggestUserFilterSettings = async (): Promise<SuggestedUserFilterSettings> => {
  const response = await apiClient.post<SuggestedUserFilterSettings>(
    '/api/users/me/filter-settings/suggest',
    {},
  );
  return response.data;
};
