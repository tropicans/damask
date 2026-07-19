import axios from 'axios';

/**
 * Base URL for the backend API, loaded from VITE_API_URL or defaulting to localhost:8000.
 */
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Axios API client instance with configured base URL and request interceptor.
 */
export const apiClient = axios.create({
  baseURL: API_URL,
});

/**
 * Request interceptor to automatically inject the Bearer JWT token from localStorage 
 * into outgoing request headers if it exists.
 */
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
