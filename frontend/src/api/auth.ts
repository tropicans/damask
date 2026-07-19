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

/**
 * Registers a new user account with the backend.
 * @param username - Display name of the user.
 * @param email - Unique email address of the user.
 * @param password - Authentication password.
 * @returns A promise resolving to the user profile response.
 */
export const registerUser = async (username: string, email: string, password: string): Promise<UserResponse> => {
  const response = await apiClient.post<UserResponse>('/api/auth/register', {
    username,
    email,
    password,
  });
  return response.data;
};

/**
 * Log in a user by verifying their credentials.
 * @param email - Authenticated email address.
 * @param password - Account password.
 * @returns A promise resolving to the user profile response.
 */
export const loginUser = async (email: string, password: string): Promise<UserResponse> => {
  const response = await apiClient.post<UserResponse>('/api/auth/login', {
    email,
    password,
  });
  return response.data;
};

/**
 * Log out the currently authenticated user session.
 */
export const logoutUser = async (): Promise<void> => {
  await apiClient.post('/api/auth/logout');
};

/**
 * Queries active profile details for the currently logged-in user session.
 * @returns A promise resolving to the active user's profile.
 */
export const getCurrentUser = async (): Promise<UserResponse> => {
  const response = await apiClient.get<UserResponse>('/api/auth/me');
  return response.data;
};
