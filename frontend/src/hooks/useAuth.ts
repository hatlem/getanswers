// Authentication Hooks
// React Query hooks for authentication operations

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, type AuthResponse } from '../lib/api';
import { queryKeys } from '../lib/queryClient';
import type { User } from '../types';

// Hook to get current user
export function useCurrentUser() {
  return useQuery({
    queryKey: queryKeys.auth.user,
    queryFn: api.auth.me,
    // Don't retry on 401 (unauthenticated)
    retry: (failureCount, error) => {
      if (error instanceof Error && error.message.includes('401')) {
        return false;
      }
      return failureCount < 2;
    },
    // Consider user data stale after 1 minute
    staleTime: 60 * 1000,
  });
}

// Hook for login mutation
export function useLogin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      api.auth.login(email, password),
    onSuccess: (data: AuthResponse) => {
      // Set the user data in cache
      queryClient.setQueryData(queryKeys.auth.user, data.user);
      // Invalidate to ensure fresh data
      queryClient.invalidateQueries({ queryKey: queryKeys.auth.user });
    },
    onError: (error) => {
      console.error('Login failed:', error);
    },
  });
}

// Hook for registration mutation
export function useRegister() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      email,
      password,
      name,
    }: {
      email: string;
      password: string;
      name: string;
    }) => api.auth.register(email, password, name),
    onSuccess: (data: AuthResponse) => {
      // Set the user data in cache
      queryClient.setQueryData(queryKeys.auth.user, data.user);
      // Invalidate to ensure fresh data
      queryClient.invalidateQueries({ queryKey: queryKeys.auth.user });
    },
    onError: (error) => {
      console.error('Registration failed:', error);
    },
  });
}

// Hook for logout mutation
export function useLogout() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => {
      api.auth.logout();
      return Promise.resolve();
    },
    onSuccess: () => {
      // Clear all queries on logout
      queryClient.clear();
      // Redirect to login
      window.location.href = '/login';
    },
  });
}

// Hook to request magic link
export function useRequestMagicLink() {
  return useMutation({
    mutationFn: ({ email }: { email: string }) => api.auth.requestMagicLink(email),
    onError: (error) => {
      console.error('Magic link request failed:', error);
    },
  });
}

// Hook to verify magic link
export function useVerifyMagicLink() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ token }: { token: string }) => api.auth.verifyMagicLink(token),
    onSuccess: (data: AuthResponse) => {
      // Set the user data in cache
      queryClient.setQueryData(queryKeys.auth.user, data.user);
      // Invalidate to ensure fresh data
      queryClient.invalidateQueries({ queryKey: queryKeys.auth.user });
    },
    onError: (error) => {
      console.error('Magic link verification failed:', error);
    },
  });
}

// Hook to get Gmail authorization URL
export function useGmailAuthUrl() {
  return useQuery({
    queryKey: queryKeys.auth.gmailUrl,
    queryFn: api.auth.getGmailAuthUrl,
    enabled: false, // Only fetch when explicitly requested
    staleTime: 5 * 60 * 1000, // Auth URL is valid for 5 minutes
  });
}

// Hook to connect Gmail
export function useGmailConnect() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ code, state }: { code: string; state: string }) =>
      api.auth.handleGmailCallback(code, state),
    onSuccess: () => {
      // Refresh user data to get updated Gmail connection status
      queryClient.invalidateQueries({ queryKey: queryKeys.auth.user });
    },
    onError: (error) => {
      console.error('Gmail connection failed:', error);
    },
  });
}

// Hook to disconnect Gmail
export function useGmailDisconnect() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.auth.disconnectGmail,
    onSuccess: () => {
      // Refresh user data to get updated Gmail connection status
      queryClient.invalidateQueries({ queryKey: queryKeys.auth.user });
    },
    onError: (error) => {
      console.error('Gmail disconnection failed:', error);
    },
  });
}

// Combined hook for easier authentication state management
export function useAuth() {
  const { data: user, isLoading, error } = useCurrentUser();
  const loginMutation = useLogin();
  const logoutMutation = useLogout();
  const registerMutation = useRegister();

  return {
    user,
    isAuthenticated: !!user,
    isLoading,
    error,
    login: loginMutation.mutate,
    logout: logoutMutation.mutate,
    register: registerMutation.mutate,
    isLoginLoading: loginMutation.isPending,
    isLogoutLoading: logoutMutation.isPending,
    isRegisterLoading: registerMutation.isPending,
    loginError: loginMutation.error,
    logoutError: logoutMutation.error,
    registerError: registerMutation.error,
  };
}
