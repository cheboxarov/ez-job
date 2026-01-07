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
  autolike_threshold: number;
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
  autolike_threshold?: number | null;
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

// Типы для подписок
export interface SubscriptionPlanResponse {
  id: string;
  name: string;
  response_limit: number;
  reset_period_seconds: number;
  duration_days: number;
  price: number;
}

export interface UserSubscriptionResponse {
  plan_id: string;
  plan_name: string;
  response_limit: number;
  reset_period_seconds: number;
  responses_count: number;
  period_started_at: string | null;
  next_reset_at: string | null;
  seconds_until_reset: number | null;
  started_at: string;
  expires_at: string | null;
  days_remaining: number | null;
}

export interface DailyResponsesResponse {
  count: number;
  limit: number;
  remaining: number;
  period_started_at: string | null;
  seconds_until_reset: number | null;
}

export interface PlansListResponse {
  plans: SubscriptionPlanResponse[];
}

// Типы для статистики откликов
export interface StatisticsDataPoint {
  date: string; // ISO date string
  count: number;
}

export interface StatisticsResponse {
  data: StatisticsDataPoint[];
}

// Типы для чатов
export interface WorkflowTransition {
  id: number;
  topic_id: number;
  applicant_state: string;
  declined_by_applicant: boolean;
}

export interface ParticipantDisplay {
  name: string;
  is_bot: boolean;
}

export interface ChatMessage {
  id: number;
  chat_id: number;
  creation_time: string;
  text: string;
  type: string;
  can_edit: boolean;
  can_delete: boolean;
  only_visible_for_my_type: boolean;
  has_content: boolean;
  hidden: boolean;
  workflow_transition_id?: number | null;
  workflow_transition?: WorkflowTransition | null;
  participant_display?: ParticipantDisplay | null;
  participant_id?: string | null;
  resources?: Record<string, string[]> | null;
}

export interface ChatDisplayInfo {
  title: string;
  subtitle?: string | null;
  icon?: string | null;
}

export interface ChatListItem {
  id: number;
  type: string;
  unread_count: number;
  pinned: boolean;
  notification_enabled: boolean;
  creation_time: string;
  idempotency_key: string;
  owner_violates_rules: boolean;
  untrusted_employer_restrictions_applied: boolean;
  current_participant_id: string;
  last_activity_time?: string | null;
  last_message?: ChatMessage | null;
  last_viewed_by_opponent_message_id?: number | null;
  last_viewed_by_current_user_message_id?: number | null;
  resources?: Record<string, string[]> | null;
  participants_ids?: string[] | null;
  online_until_time?: string | null;
  block_chat_info?: Record<string, unknown>[] | null;
  display_info?: ChatDisplayInfo | null;
}

// Типы для действий агента
export interface AgentAction {
  id: string;
  type: string;
  entity_type: string;
  entity_id: number;
  created_by: string;
  user_id: string;
  resume_hash: string | null;
  data: {
    dialog_id: number;
    message_to?: number;
    message_text?: string;
    event_type?: string;
    message?: string;
    sended?: boolean;
  };
  created_at: string;
  updated_at: string;
  is_read: boolean;
}

export interface AgentActionsListResponse {
  items: AgentAction[];
}

export interface AgentActionsUnreadCountResponse {
  unread_count: number;
}

export interface ChatListResponse {
  count: number;
  items: ChatListItem[];
}

export interface ChatMessages {
  items: ChatMessage[];
  has_more: boolean;
}

export interface ChatDetailedResponse {
  id: number;
  type: string;
  unread_count: number;
  pinned: boolean;
  notification_enabled: boolean;
  creation_time: string;
  owner_violates_rules: boolean;
  untrusted_employer_restrictions_applied: boolean;
  current_participant_id: string;
  last_activity_time?: string | null;
  messages?: ChatMessages | null;
  last_viewed_by_opponent_message_id?: number | null;
  last_viewed_by_current_user_message_id?: number | null;
  resources?: Record<string, string[]> | null;
  write_possibility?: Record<string, unknown> | null;
  operations?: Record<string, unknown> | null;
  participants_ids?: string[] | null;
  online_until_time?: string | null;
  block_chat_info?: Record<string, unknown>[] | null;
}

// Типы для Telegram уведомлений
export interface TelegramNotificationSettings {
  id: string;
  user_id: string;
  telegram_chat_id: number | null;
  telegram_username: string | null;
  is_enabled: boolean;
  notify_call_request: boolean;
  notify_external_action: boolean;
  notify_question_answered: boolean;
  notify_message_suggestion: boolean;
  notify_vacancy_response: boolean;
  linked_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface UpdateTelegramNotificationSettingsRequest {
  is_enabled?: boolean | null;
  notify_call_request?: boolean | null;
  notify_external_action?: boolean | null;
  notify_question_answered?: boolean | null;
  notify_message_suggestion?: boolean | null;
  notify_vacancy_response?: boolean | null;
}

export interface UserAutomationSettings {
  id: string;
  user_id: string;
  auto_reply_to_questions_in_chats: boolean;
  created_at: string;
  updated_at: string;
}

export interface UpdateUserAutomationSettingsRequest {
  auto_reply_to_questions_in_chats?: boolean | null;
}

export interface GenerateTelegramLinkTokenResponse {
  link: string;
  expires_at: string;
}

export interface SendTestNotificationResponse {
  success: boolean;
}


