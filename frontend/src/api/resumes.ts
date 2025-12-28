import apiClient from './client';
import type {
  Resume,
  ResumesListResponse,
  CreateResumeRequest,
  UpdateResumeRequest,
} from '../types/api';

export const listResumes = async (): Promise<ResumesListResponse> => {
  const response = await apiClient.get<ResumesListResponse>('/api/resumes');
  return response.data;
};

export const getResume = async (resumeId: string): Promise<Resume> => {
  const response = await apiClient.get<Resume>(`/api/resumes/${resumeId}`);
  return response.data;
};

export const createResume = async (payload: CreateResumeRequest): Promise<Resume> => {
  const response = await apiClient.post<Resume>('/api/resumes', payload);
  return response.data;
};

export const updateResume = async (
  resumeId: string,
  payload: UpdateResumeRequest,
): Promise<Resume> => {
  const response = await apiClient.put<Resume>(`/api/resumes/${resumeId}`, payload);
  return response.data;
};

export const deleteResume = async (resumeId: string): Promise<void> => {
  await apiClient.delete(`/api/resumes/${resumeId}`);
};

export const importResumesFromHH = async (): Promise<ResumesListResponse> => {
  const response = await apiClient.post<ResumesListResponse>('/api/resumes/import-from-hh');
  return response.data;
};

export const evaluateResume = async (resumeId: string): Promise<any> => {
  const response = await apiClient.post<any>(`/api/resumes/${resumeId}/evaluate`);
  return response.data;
};
