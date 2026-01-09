export interface AdminUser {
  id: string;
  email: string;
  phone: string | null;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface AdminUserListResponse {
  items: AdminUser[];
  total: number;
  page: number;
  page_size: number;
}

export interface AdminUserDetailResponse {
  id: string;
  email: string | null;
  phone: string | null;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
  subscription: {
    plan_id: string;
    plan_name: string;
  } | null;
}

export interface AdminUserFlagsUpdateRequest {
  is_active?: boolean;
  is_verified?: boolean;
}

export interface AdminChangeUserPlanRequest {
  plan_name: string;
}

export interface AdminPlan {
  id: string;
  name: string;
  response_limit: number;
  reset_period_seconds: number;
  duration_days: number;
  price: number;
}

export interface AdminPlansListResponse {
  plans: AdminPlan[];
  total: number;
  page: number;
  page_size: number;
}

export interface AdminPlanUpsertRequest {
  name: string;
  response_limit: number;
  reset_period_seconds: number;
  duration_days: number;
  price: number;
  is_active?: boolean;
}

// LLM Calls
export interface LlmCall {
  id: string;
  call_id: string;
  attempt_number: number;
  agent_name: string;
  model: string;
  user_id: string | null;
  prompt: Array<Record<string, any>>;
  response: string;
  temperature: number;
  response_format: Record<string, string> | null;
  status: string;
  error_type: string | null;
  error_message: string | null;
  duration_ms: number | null;
  prompt_tokens: number | null;
  completion_tokens: number | null;
  total_tokens: number | null;
  response_size_bytes: number | null;
  cost_usd: number | null;
  context: Record<string, any> | null;
  created_at: string;
}

export interface LlmCallListResponse {
  items: LlmCall[];
  total: number;
  page: number;
  page_size: number;
}

// Metrics
export interface LlmPeriodMetric {
  period_start: string;
  calls_count: number;
  total_tokens: number;
  unique_users: number;
}

export interface LlmTotalMetrics {
  calls_count: number;
  total_tokens: number;
  unique_users: number;
  avg_tokens_per_user: number;
}

export interface LlmUsageMetricsResponse {
  metrics_by_period: LlmPeriodMetric[];
  total_metrics: LlmTotalMetrics;
}

export interface VacancyResponsePeriodMetric {
  period_start: string;
  responses_count: number;
  unique_users: number;
}

export interface VacancyResponseTotalMetrics {
  responses_count: number;
  unique_users: number;
  avg_responses_per_user: number;
}

export interface VacancyResponsesMetricsResponse {
  metrics_by_period: VacancyResponsePeriodMetric[];
  total_metrics: VacancyResponseTotalMetrics;
}

export interface PaidUsersMetrics {
  paid_users_count: number;
  total_cost_for_paid_users: number;
  avg_cost_per_paid_user: number;
}

export interface CombinedMetricsResponse {
  llm_metrics: LlmUsageMetricsResponse;
  responses_metrics: VacancyResponsesMetricsResponse;
  paid_users_metrics: PaidUsersMetrics;
}
