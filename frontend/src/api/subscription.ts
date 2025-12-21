import apiClient from './client';
import type {
  UserSubscriptionResponse,
  DailyResponsesResponse,
  PlansListResponse,
} from '../types/api';

export const getMySubscriptionPlan = async (): Promise<UserSubscriptionResponse> => {
  const response = await apiClient.get<UserSubscriptionResponse>('/api/subscription/my-plan');
  return response.data;
};

export const getDailyResponses = async (): Promise<DailyResponsesResponse> => {
  const response = await apiClient.get<DailyResponsesResponse>('/api/subscription/daily-responses');
  return response.data;
};

export const getAllPlans = async (): Promise<PlansListResponse> => {
  const response = await apiClient.get<PlansListResponse>('/api/subscription/plans');
  return response.data;
};

export const changePlan = async (planName: string): Promise<UserSubscriptionResponse> => {
  const response = await apiClient.post<UserSubscriptionResponse>(
    '/api/subscription/change-plan',
    { plan_name: planName }
  );
  return response.data;
};

