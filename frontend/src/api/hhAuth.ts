import apiClient from './client';

export interface HhAuthData {
  headers: Record<string, string>;
  cookies: Record<string, string>;
}

export interface HhAuthRequest {
  headers: Record<string, string>;
  cookies: Record<string, string>;
}

export const getHhAuth = async (): Promise<HhAuthData> => {
  const response = await apiClient.get<HhAuthData>('/api/hh-auth');
  return response.data;
};

export const updateHhAuth = async (data: HhAuthRequest): Promise<HhAuthData> => {
  const response = await apiClient.put<HhAuthData>('/api/hh-auth', data);
  return response.data;
};
