/**
 * React Query hooks for API calls.
 * 
 * These hooks provide caching, automatic refetching, and optimistic updates
 * for API operations.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';

/**
 * Hook to fetch sites list with pagination.
 */
export const useSites = (params: { limit?: number; offset?: number; status?: string } = {}) => {
  return useQuery({
    queryKey: ['sites', params],
    queryFn: async () => {
      const response = await apiClient.get('/v1/sites', { params });
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook to fetch a single site by slug.
 */
export const useSite = (slug: string) => {
  return useQuery({
    queryKey: ['sites', slug],
    queryFn: async () => {
      const response = await apiClient.get(`/v1/sites/${slug}`);
      return response.data;
    },
    enabled: !!slug,
  });
};

/**
 * Hook to search across sites and pages.
 */
export const useSearch = (query: string, params: { limit?: number; offset?: number; type_filter?: string } = {}) => {
  return useQuery({
    queryKey: ['search', query, params],
    queryFn: async () => {
      const response = await apiClient.get('/v1/search', { 
        params: { q: query, ...params } 
      });
      return response.data;
    },
    enabled: query.length > 0,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

/**
 * Hook to fetch social posts.
 */
export const usePosts = (params: { limit?: number; offset?: number } = {}) => {
  return useQuery({
    queryKey: ['posts', params],
    queryFn: async () => {
      const response = await apiClient.get('/v1/social/posts', { params });
      return response.data;
    },
  });
};

/**
 * Hook to login.
 */
export const useLogin = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (credentials: { email_or_username: string; password: string }) => {
      const response = await apiClient.post('/v1/auth/login', credentials);
      return response.data;
    },
    onSuccess: (data) => {
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      queryClient.invalidateQueries({ queryKey: ['user'] });
    },
  });
};

/**
 * Hook to get current user profile.
 */
export const useCurrentUser = () => {
  return useQuery({
    queryKey: ['user'],
    queryFn: async () => {
      const response = await apiClient.get('/v1/auth/me');
      return response.data;
    },
    retry: false,
  });
};

/**
 * Hook to signup.
 */
export const useSignup = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: {
      email: string;
      username: string;
      display_name: string;
      password: string;
    }) => {
      const response = await apiClient.post('/v1/auth/signup', data);
      return response.data;
    },
    onSuccess: (data) => {
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      queryClient.invalidateQueries({ queryKey: ['user'] });
    },
  });
};

/**
 * Hook to get social insights.
 */
export const useSocialInsights = (limit: number = 20) => {
  return useQuery({
    queryKey: ['social-insights', limit],
    queryFn: async () => {
      const response = await apiClient.get('/v1/social/insights', { params: { limit } });
      return response.data;
    },
    staleTime: 1 * 60 * 1000, // 1 minute
  });
};
