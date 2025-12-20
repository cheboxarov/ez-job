import apiClient from './client';
import type {
  VacancyRequest,
  VacanciesResponse,
  VacanciesListRequest,
  VacanciesListResponse,
  VacancyResponsesListResponse,
} from '../types/api';

export const getRelevantVacancies = async (request: VacancyRequest): Promise<VacanciesResponse> => {
  const response = await apiClient.post<VacanciesResponse>('/api/vacancies/relevant', request);
  return response.data;
};

export const getRelevantVacancyList = async (request: VacanciesListRequest): Promise<VacanciesListResponse> => {
  const response = await apiClient.post<VacanciesListResponse>('/api/vacancies/relevant-list', request);
  return response.data;
};

export interface VacancyRespondRequest {
  vacancy_id: number;
  resume_id: string;
  letter?: string;
}

export const respondToVacancy = async (request: VacancyRespondRequest): Promise<Record<string, string>> => {
  const response = await apiClient.post<Record<string, string>>('/api/vacancies/respond', request);
  return response.data;
};

export interface GetVacancyResponsesParams {
  resume_hash: string;
  offset?: number;
  limit?: number;
}

export const getVacancyResponses = async (
  params: GetVacancyResponsesParams
): Promise<VacancyResponsesListResponse> => {
  const queryParams = new URLSearchParams({
    resume_hash: params.resume_hash,
    ...(params.offset !== undefined && { offset: params.offset.toString() }),
    ...(params.limit !== undefined && { limit: params.limit.toString() }),
  });
  const response = await apiClient.get<VacancyResponsesListResponse>(
    `/api/vacancies/responses?${queryParams.toString()}`
  );
  return response.data;
};


