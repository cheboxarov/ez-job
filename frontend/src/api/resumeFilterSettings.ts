import apiClient from './client';
import type {
  ResumeFilterSettings,
  ResumeFilterSettingsUpdate,
  SuggestedUserFilterSettings,
} from '../types/api';

export const getResumeFilterSettings = async (
  resumeId: string,
): Promise<ResumeFilterSettings> => {
  const response = await apiClient.get<ResumeFilterSettings>(
    `/api/resumes/${resumeId}/filter-settings`,
  );
  return response.data;
};

export const updateResumeFilterSettings = async (
  resumeId: string,
  payload: ResumeFilterSettingsUpdate,
): Promise<ResumeFilterSettings> => {
  const response = await apiClient.put<ResumeFilterSettings>(
    `/api/resumes/${resumeId}/filter-settings`,
    payload,
  );
  return response.data;
};

export const suggestResumeFilterSettings = async (
  resumeId: string,
): Promise<SuggestedUserFilterSettings> => {
  const response = await apiClient.post<SuggestedUserFilterSettings>(
    `/api/resumes/${resumeId}/filter-settings/suggest`,
    {},
  );
  return response.data;
};
