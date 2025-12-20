import apiClient from './client';
import type { UpdateUserRequest } from '../types/api';
import type { User } from '../types/user';

export const getCurrentUser = async (): Promise<User> => {
  const response = await apiClient.get<User>('/users/me');
  return response.data;
};

export const updateUser = async (userId: string, data: UpdateUserRequest): Promise<User> => {
  const response = await apiClient.put<User>(`/api/users/${userId}`, data);
  return response.data;
};


