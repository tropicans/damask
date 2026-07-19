import { apiClient } from './client';

export interface UserResponse {
  id: string;
  username: string;
  email: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: UserResponse;
}

export const registerUser = async (username: string, email: string, password: string): Promise<UserResponse> => {
  const response = await apiClient.post<UserResponse>('/api/auth/register', {
    username,
    email,
    password,
  });
  return response.data;
};

export const loginUser = async (email: string, password: string): Promise<TokenResponse> => {
  const response = await apiClient.post<TokenResponse>('/api/auth/login', {
    email,
    password,
  });
  return response.data;
};

export const getCurrentUser = async (): Promise<UserResponse> => {
  const response = await apiClient.get<UserResponse>('/api/auth/me');
  return response.data;
};
