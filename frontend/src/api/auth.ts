import apiClient from './client';
import type { LoginResponse, RegisterRequest } from '../types/api';
import type { User } from '../types/user';

export const login = async (email: string, password: string): Promise<LoginResponse> => {
  // FastAPI Users использует OAuth2PasswordRequestForm, который ожидает FormData
  // Требуется grant_type: "password"
  const formData = new URLSearchParams();
  formData.append('grant_type', 'password');
  formData.append('username', email);
  formData.append('password', password);
  
  // FastAPI Users создает путь на основе префикса роутера + /login
  // Роутер подключен с префиксом /auth, поэтому путь /auth/login
  const response = await apiClient.post<LoginResponse>('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  return response.data;
};

export const register = async (data: RegisterRequest): Promise<User> => {
  const response = await apiClient.post<User>('/auth/register', data);
  return response.data;
};


