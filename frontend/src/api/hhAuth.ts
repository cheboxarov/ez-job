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

export interface GenerateOtpResponse {
  result: Record<string, any>;
  cookies: Record<string, string>;
}

export const generateOtp = async (phone: string): Promise<GenerateOtpResponse> => {
  const response = await apiClient.post<GenerateOtpResponse>('/api/hh-auth/generate-otp', {
    phone,
  });
  return response.data;
};

export const loginByCode = async (
  phone: string,
  code: string,
  cookies: Record<string, string>,
): Promise<HhAuthData> => {
  const response = await apiClient.post<HhAuthData>('/api/hh-auth/login-by-code', {
    phone,
    code,
    cookies,
  });
  return response.data;
};

export const deleteHhAuth = async (): Promise<void> => {
  await apiClient.delete('/api/hh-auth');
};
