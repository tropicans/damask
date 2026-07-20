import { apiClient } from './client';
import type { UserResponse } from './auth';

export interface UserListResponse {
  items: UserResponse[];
  total: number;
}

export interface LoginAuditResponse {
  id: string;
  email: string;
  user_id: string | null;
  ip_address: string;
  user_agent: string | null;
  status: string; // "SUCCESS" or "FAILED"
  created_at: string;
}

export interface LoginAuditListResponse {
  items: LoginAuditResponse[];
  total: number;
}

/**
 * Retrieves a paginated list of all users. Admin only.
 */
export const getUsers = async (page = 1, limit = 10): Promise<UserListResponse> => {
  const response = await apiClient.get<UserListResponse>('/api/admin/users', {
    params: { page, limit }
  });
  return response.data;
};

/**
 * Updates the active status of a user. Admin only.
 */
export const updateUserStatus = async (userId: string, isActive: boolean): Promise<UserResponse> => {
  const response = await apiClient.put<UserResponse>(`/api/admin/users/${userId}/status`, {
    is_active: isActive
  });
  return response.data;
};

/**
 * Updates the role of a user. Admin only.
 */
export const updateUserRole = async (userId: string, role: string): Promise<UserResponse> => {
  const response = await apiClient.put<UserResponse>(`/api/admin/users/${userId}/role`, {
    role
  });
  return response.data;
};

/**
 * Retrieves login audit logs. Admin only.
 */
export const getLoginAudits = async (status?: string, page = 1, limit = 10): Promise<LoginAuditListResponse> => {
  const response = await apiClient.get<LoginAuditListResponse>('/api/admin/login-audits', {
    params: { status, page, limit }
  });
  return response.data;
};
