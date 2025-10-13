/**
 * API Client Configuration
 * 
 * This file configures the generated API client with authentication,
 * error handling, and request interceptors.
 * 
 * Usage:
 * ```typescript
 * import { api } from './api/client';
 * 
 * // List sites
 * const sites = await api.sites.listSites({ limit: 20, offset: 0 });
 * 
 * // Search
 * const results = await api.search.search({ q: 'truth', limit: 10 });
 * 
 * // Authenticate
 * const tokens = await api.auth.login({
 *   email_or_username: 'user@example.com',
 *   password: 'password'
 * });
 * ```
 */

import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Create configured axios instance for API calls.
 */
export const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor - add auth token
  client.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor - handle errors and token refresh
  client.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;

      // Handle 401 - try to refresh token
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        try {
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            // TODO: Implement token refresh endpoint
            // const response = await client.post('/v1/auth/refresh', { refresh_token: refreshToken });
            // localStorage.setItem('access_token', response.data.access_token);
            // originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;
            // return client(originalRequest);
          }
        } catch (refreshError) {
          // Refresh failed, redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }

      // Handle rate limiting
      if (error.response?.status === 429) {
        const retryAfter = error.response.headers['retry-after'];
        console.warn(`Rate limit exceeded. Retry after ${retryAfter} seconds.`);
      }

      return Promise.reject(error);
    }
  );

  return client;
};

export const apiClient = createApiClient();

/**
 * Helper to set authentication tokens.
 */
export const setAuthTokens = (accessToken: string, refreshToken: string) => {
  localStorage.setItem('access_token', accessToken);
  localStorage.setItem('refresh_token', refreshToken);
};

/**
 * Helper to clear authentication tokens.
 */
export const clearAuthTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

/**
 * Check if user is authenticated.
 */
export const isAuthenticated = (): boolean => {
  return !!localStorage.getItem('access_token');
};
