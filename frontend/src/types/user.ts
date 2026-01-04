export interface User {
  id: string;
  email: string;
  phone?: string | null;
  hh_user_id?: string | null;
  is_superuser?: boolean;
}

