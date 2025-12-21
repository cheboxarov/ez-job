import apiClient from './client';
import type { ChatListResponse, ChatDetailedResponse } from '../types/api';

export const listChats = async (): Promise<ChatListResponse> => {
  const response = await apiClient.get<ChatListResponse>('/api/chats');
  return response.data;
};

export const getChat = async (chatId: number): Promise<ChatDetailedResponse> => {
  const response = await apiClient.get<ChatDetailedResponse>(`/api/chats/${chatId}`);
  return response.data;
};

