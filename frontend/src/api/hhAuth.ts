import apiClient from './client';
import type { LoginResponse } from '../types/api';

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
): Promise<LoginResponse> => {
  const response = await apiClient.post<LoginResponse>('/api/hh-auth/login-by-code', {
    phone,
    code,
    cookies,
  });
  return response.data;
};
