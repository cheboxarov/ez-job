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

export interface SendChatMessageRequest {
  text: string;
  idempotency_key?: string;
  hhtm_source?: string;
  hhtm_source_label?: string;
}

export interface SendChatMessageResponse {
  success: boolean;
  data?: Record<string, unknown>;
}

export const sendChatMessage = async (
  chatId: number,
  text: string
): Promise<SendChatMessageResponse> => {
  const response = await apiClient.post<SendChatMessageResponse>(
    `/api/chats/${chatId}/send`,
    { text }
  );
  return response.data;
};

