import apiClient from './client';
import type { LoginResponse } from '../types/api';

export interface CaptchaData {
  isBot: boolean;
  captchaState: string;
  captchaError: boolean;
}

export interface GenerateOtpResponse {
  result: {
    hhcaptcha?: CaptchaData;
    [key: string]: any;
  };
  cookies: Record<string, string>;
}

export interface CaptchaKeyResponse {
  captchaKey: string;
  cookies: Record<string, string>;
}

export interface CaptchaPictureResponse {
  contentType: string;
  imageBase64: string;
  cookies: Record<string, string>;
}

export const generateOtp = async (
  phone: string,
  cookies?: Record<string, string>,
  captcha?: {
    captchaText: string;
    captchaKey: string;
    captchaState: string;
  }
): Promise<GenerateOtpResponse> => {
  const response = await apiClient.post<GenerateOtpResponse>('/api/hh-auth/generate-otp', {
    phone,
    cookies: cookies || undefined,
    captcha: captcha || undefined,
  });
  return response.data;
};

export const getCaptchaKey = async (cookies: Record<string, string>): Promise<CaptchaKeyResponse> => {
  const response = await apiClient.post<CaptchaKeyResponse>('/api/hh-auth/captcha/key', {
    cookies,
    lang: 'RU',
  });
  return response.data;
};

export const getCaptchaPicture = async (
  captchaKey: string,
  cookies: Record<string, string>
): Promise<CaptchaPictureResponse> => {
  const response = await apiClient.post<CaptchaPictureResponse>('/api/hh-auth/captcha/picture', {
    captchaKey,
    cookies,
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
