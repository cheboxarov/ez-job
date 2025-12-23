import apiClient from './client';
import type {
  AgentActionsListResponse,
  AgentActionsUnreadCountResponse,
} from '../types/api';

export interface GetAgentActionsParams {
  type?: string;
  entity_type?: string;
  entity_id?: number;
}

export const getAgentActions = async (
  params?: GetAgentActionsParams
): Promise<AgentActionsListResponse> => {
  const queryParams = new URLSearchParams();
  if (params?.type) {
    queryParams.append('type', params.type);
  }
  if (params?.entity_type) {
    queryParams.append('entity_type', params.entity_type);
  }
  if (params?.entity_id !== undefined) {
    queryParams.append('entity_id', params.entity_id.toString());
  }

  const queryString = queryParams.toString();
  const url = `/api/agent-actions${queryString ? `?${queryString}` : ''}`;
  
  const response = await apiClient.get<AgentActionsListResponse>(url);
  return response.data;
};

export const getAgentActionsUnreadCount = async (): Promise<number> => {
  const response = await apiClient.get<AgentActionsUnreadCountResponse>(
    '/api/agent-actions/unread/count',
  );
  return response.data.unread_count;
};

export const markAllAgentActionsAsRead = async (): Promise<void> => {
  await apiClient.post('/api/agent-actions/read-all');
};

