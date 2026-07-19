import axios from 'axios';

/**
 * Base URL for the backend API, loaded from VITE_API_URL or defaulting to localhost:8000.
 */
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

let onUnauthorizedCallback: (() => void) | null = null;

/**
 * Registers a callback to be executed when a 401 Unauthorized response is caught.
 */
export const registerUnauthorizedCallback = (callback: () => void) => {
  onUnauthorizedCallback = callback;
};

/**
 * Axios API client instance with configured base URL and credentials handling.
 */
export const apiClient = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});

/**
 * Request interceptor to extract the CSRF token from the secure_data_csrf cookie
 * and set the X-CSRF-Token header on mutating requests.
 */
apiClient.interceptors.request.use((config) => {
  if (config.method && ['post', 'put', 'delete', 'patch'].includes(config.method.toLowerCase())) {
    const csrfCookie = document.cookie
      .split('; ')
      .find((row) => row.startsWith('secure_data_csrf='));
    if (csrfCookie) {
      const csrfToken = csrfCookie.split('=')[1];
      if (csrfToken) {
        config.headers['X-CSRF-Token'] = decodeURIComponent(csrfToken);
      }
    }
  }
  return config;
});

/**
 * Response interceptor to catch 401 Unauthorized errors globally.
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      if (onUnauthorizedCallback) {
        onUnauthorizedCallback();
      }
    }
    return Promise.reject(error);
  }
);
