import apiClient from './client';

// Тип одной ноды дерева регионов HH (упрощённый, только то, что реально используем)
export interface HhArea {
  id: string;
  name: string;
  parent_id?: string | null;
  areas?: HhArea[];
  [key: string]: unknown;
}

export const getAreas = async (): Promise<HhArea[]> => {
  const response = await apiClient.get<HhArea[]>('/api/dictionaries/areas');
  return response.data;
};

