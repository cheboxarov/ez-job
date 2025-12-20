// User импортируется отдельно из ./user

export interface LoginRequest {
  username: string; // FastAPI Users использует username вместо email
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface VacancyRequest {
  resume_id: string;
  page_indices?: number[] | null;
  min_confidence_for_cover_letter: number;
  order_by?: string | null;
}

export interface Vacancy {
  vacancy_id: number;
  name: string;
  company_name?: string | null;
  area_name?: string | null;
  compensation?: string | null;
  publication_date?: string | null;
  work_experience?: string | null;
  employment?: string | null;
  work_formats?: string[] | null;
  schedule_by_days?: string[] | null;
  working_hours?: string[] | null;
  link?: string | null;
  key_skills?: string[] | null;
  description_html?: string | null;
  confidence: number;
  reason?: string | null;
  cover_letter?: string | null;
}

export interface VacanciesResponse {
  count: number;
  items: Vacancy[];
}

// Типы для list-вакансий (листовое представление)
export interface VacanciesListRequest {
  resume_id: string;
  page_indices?: number[] | null;
  min_confidence?: number | null;
  order_by?: string | null;
}

export interface VacancyListItem {
  vacancy_id: number;
  name: string;
  area_name?: string | null;
  publication_time_iso?: string | null;
  alternate_url?: string | null;
  company_name?: string | null;
  salary_from?: number | null;
  salary_to?: number | null;
  salary_currency?: string | null;
  salary_gross?: boolean | null;
  schedule_name?: string | null;
  snippet_requirement?: string | null;
  snippet_responsibility?: string | null;
  vacancy_type_name?: string | null;
  response_letter_required?: boolean | null;
  has_test?: boolean | null;
  address_city?: string | null;
  address_street?: string | null;
  professional_roles?: string[] | null;
  confidence: number;
  reason?: string | null;
}

export interface VacanciesListResponse {
  count: number;
  items: VacancyListItem[];
}

export interface UpdateUserRequest {
  // User теперь содержит только id и email, обновлять нечего
}

export interface UserFilterSettings {
  user_id: string;
  text?: string | null;
  resume_id?: string | null;
  experience?: string[] | null;
  employment?: string[] | null;
  schedule?: string[] | null;
  professional_role?: string[] | null;
  area?: string | null;
  salary?: number | null;
  currency?: string | null;
  only_with_salary: boolean;
  order_by?: string | null;
  period?: number | null;
  date_from?: string | null;
  date_to?: string | null;
}

export interface UserFilterSettingsUpdate {
  text?: string | null;
  resume_id?: string | null;
  experience?: string[] | null;
  employment?: string[] | null;
  schedule?: string[] | null;
  professional_role?: string[] | null;
  area?: string | null;
  salary?: number | null;
  currency?: string | null;
  only_with_salary?: boolean | null;
  order_by?: string | null;
  period?: number | null;
  date_from?: string | null;
  date_to?: string | null;
}

// Типы для Resume
export interface Resume {
  id: string;
  user_id: string;
  content: string;
  user_parameters?: string | null;
  external_id?: string | null;
  headhunter_hash?: string | null;
  is_auto_reply: boolean;
}

export interface ResumesListResponse {
  count: number;
  items: Resume[];
}

export interface CreateResumeRequest {
  content: string;
  user_parameters?: string | null;
}

export interface UpdateResumeRequest {
  content?: string | null;
  user_parameters?: string | null;
  is_auto_reply?: boolean | null;
}

// Типы для ResumeFilterSettings
export interface ResumeFilterSettings {
  resume_id: string;
  text?: string | null;
  hh_resume_id?: string | null;
  experience?: string[] | null;
  employment?: string[] | null;
  schedule?: string[] | null;
  professional_role?: string[] | null;
  area?: string | null;
  salary?: number | null;
  currency?: string | null;
  only_with_salary: boolean;
  order_by?: string | null;
  period?: number | null;
  date_from?: string | null;
  date_to?: string | null;
}

export interface ResumeFilterSettingsUpdate {
  text?: string | null;
  hh_resume_id?: string | null;
  experience?: string[] | null;
  employment?: string[] | null;
  schedule?: string[] | null;
  professional_role?: string[] | null;
  area?: string | null;
  salary?: number | null;
  currency?: string | null;
  only_with_salary?: boolean | null;
  order_by?: string | null;
  period?: number | null;
  date_from?: string | null;
  date_to?: string | null;
}

export interface SuggestedUserFilterSettings {
  text?: string | null;
  salary?: number | null;
  currency?: string | null;
}

// Deprecated: старые типы для обратной совместимости (будут удалены после миграции)
/** @deprecated Используйте ResumeFilterSettings */
export interface UserFilterSettings {
  user_id: string;
  text?: string | null;
  resume_id?: string | null;
  experience?: string[] | null;
  employment?: string[] | null;
  schedule?: string[] | null;
  professional_role?: string[] | null;
  area?: string | null;
  salary?: number | null;
  currency?: string | null;
  only_with_salary: boolean;
  order_by?: string | null;
  period?: number | null;
  date_from?: string | null;
  date_to?: string | null;
}

/** @deprecated Используйте ResumeFilterSettingsUpdate */
export interface UserFilterSettingsUpdate {
  text?: string | null;
  resume_id?: string | null;
  experience?: string[] | null;
  employment?: string[] | null;
  schedule?: string[] | null;
  professional_role?: string[] | null;
  area?: string | null;
  salary?: number | null;
  currency?: string | null;
  only_with_salary?: boolean | null;
  order_by?: string | null;
  period?: number | null;
  date_from?: string | null;
  date_to?: string | null;
}

// Типы для откликов на вакансии
export interface VacancyResponseItem {
  id: string;
  vacancy_id: number;
  vacancy_name: string;
  vacancy_url?: string | null;
  cover_letter: string;
  created_at: string;
}

export interface VacancyResponsesListResponse {
  items: VacancyResponseItem[];
  total: number;
  offset: number;
  limit: number;
}


