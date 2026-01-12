import apiClient from './client';
import type {
  AgentActionsListResponse,
  AgentActionsUnreadCountResponse,
  AgentAction,
  EventStatus,
} from '../types/api';

export interface GetAgentActionsParams {
  types?: string[];
  exclude_types?: string[];
  event_types?: string[];
  exclude_event_types?: string[];
  statuses?: EventStatus[];
  entity_type?: string;
  entity_id?: number;
}

export const getAgentActions = async (
  params?: GetAgentActionsParams
): Promise<AgentActionsListResponse> => {
  const queryParams = new URLSearchParams();
  const appendListParam = (key: string, values?: string[]) => {
    if (!values || values.length === 0) {
      return;
    }
    values.forEach((value) => {
      queryParams.append(key, value);
    });
  };

  appendListParam('types', params?.types);
  appendListParam('exclude_types', params?.exclude_types);
  appendListParam('event_types', params?.event_types);
  appendListParam('exclude_event_types', params?.exclude_event_types);
  appendListParam('statuses', params?.statuses);
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

export const executeAgentAction = async (actionId: string): Promise<AgentAction> => {
  const response = await apiClient.post<AgentAction>(
    `/api/agent-actions/${actionId}/execute`
  );
  return response.data;
};

export const updateAgentActionStatus = async (
  actionId: string,
  status: EventStatus
): Promise<AgentAction> => {
  const response = await apiClient.patch<AgentAction>(
    `/api/agent-actions/${actionId}/status`,
    { status }
  );
  return response.data;
};
