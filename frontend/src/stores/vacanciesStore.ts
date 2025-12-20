import { create } from 'zustand';
import type { VacancyListItem } from '../types/api';

interface VacanciesState {
  vacancies: VacancyListItem[];
  setVacancies: (vacancies: VacancyListItem[]) => void;
  clearVacancies: () => void;
}

export const useVacanciesStore = create<VacanciesState>((set) => ({
  vacancies: [],

  setVacancies: (vacancies: VacancyListItem[]) => {
    set({ vacancies });
  },

  clearVacancies: () => {
    set({ vacancies: [] });
  },
}));


