import apiClient from './client';
import type {
  AdminUserListResponse,
  AdminUserDetailResponse,
  AdminUserFlagsUpdateRequest,
  AdminChangeUserPlanRequest,
  AdminPlansListResponse,
  AdminPlanUpsertRequest,
  AdminPlan,
  LlmCallListResponse,
  LlmUsageMetricsResponse,
  VacancyResponsesMetricsResponse,
  CombinedMetricsResponse,
  LlmCall,
} from '../types/admin';

export const adminApi = {
  // Users
  getUsers: async (params: {
    page?: number;
    page_size?: number;
    phone?: string;
  }): Promise<AdminUserListResponse> => {
    const response = await apiClient.get<AdminUserListResponse>('/api/admin/users', { params });
    return response.data;
  },

  getUserDetail: async (userId: string): Promise<AdminUserDetailResponse> => {
    const response = await apiClient.get<AdminUserDetailResponse>(`/api/admin/users/${userId}`);
    return response.data;
  },

  updateUserFlags: async (
    userId: string,
    data: AdminUserFlagsUpdateRequest
  ): Promise<void> => {
    await apiClient.patch(`/api/admin/users/${userId}/flags`, data);
  },

  changeUserPlan: async (
    userId: string,
    data: AdminChangeUserPlanRequest
  ): Promise<void> => {
    await apiClient.post(`/api/admin/users/${userId}/change-plan`, data);
  },

  deleteUser: async (userId: string): Promise<void> => {
    await apiClient.delete(`/api/admin/users/${userId}`);
  },

  // Plans
  getPlans: async (params: {
    page?: number;
    page_size?: number;
  }): Promise<AdminPlansListResponse> => {
    const response = await apiClient.get<AdminPlansListResponse>('/api/admin/plans', { params });
    return response.data;
  },

  createPlan: async (data: AdminPlanUpsertRequest): Promise<AdminPlan> => {
    const response = await apiClient.post<AdminPlan>('/api/admin/plans', data);
    return response.data;
  },

  updatePlan: async (planId: string, data: AdminPlanUpsertRequest): Promise<AdminPlan> => {
    const response = await apiClient.put<AdminPlan>(`/api/admin/plans/${planId}`, data);
    return response.data;
  },

  deactivatePlan: async (planId: string): Promise<AdminPlan> => {
    const response = await apiClient.patch<AdminPlan>(`/api/admin/plans/${planId}/deactivate`);
    return response.data;
  },

  // LLM Calls
  getLlmCalls: async (params: {
    page?: number;
    page_size?: number;
    start_date?: string;
    end_date?: string;
    user_id?: string;
    agent_name?: string;
    status?: string;
  }): Promise<LlmCallListResponse> => {
    const response = await apiClient.get<LlmCallListResponse>('/api/admin/llm-calls', { params });
    return response.data;
  },

  getLlmCallDetail: async (callId: string): Promise<LlmCall> => {
    const response = await apiClient.get<LlmCall>(`/api/admin/llm-calls/${callId}`);
    return response.data;
  },

  // Metrics
  getLlmMetrics: async (params: {
    start_date: string;
    end_date: string;
    plan_id?: string;
    time_step?: 'day' | 'week' | 'month';
  }): Promise<LlmUsageMetricsResponse> => {
    const response = await apiClient.get<LlmUsageMetricsResponse>('/api/admin/metrics/llm', {
      params,
    });
    return response.data;
  },

  getResponsesMetrics: async (params: {
    start_date: string;
    end_date: string;
    plan_id?: string;
    time_step?: 'day' | 'week' | 'month';
  }): Promise<VacancyResponsesMetricsResponse> => {
    const response = await apiClient.get<VacancyResponsesMetricsResponse>(
      '/api/admin/metrics/responses',
      { params }
    );
    return response.data;
  },

  getCombinedMetrics: async (params: {
    start_date: string;
    end_date: string;
    plan_id?: string;
    time_step?: 'day' | 'week' | 'month';
  }): Promise<CombinedMetricsResponse> => {
    const response = await apiClient.get<CombinedMetricsResponse>('/api/admin/metrics', {
      params,
    });
    return response.data;
  },
};
