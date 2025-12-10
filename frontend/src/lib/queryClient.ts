// React Query Client Configuration
// Centralized query client with default options for caching and refetching

import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Stale time: 30 seconds
      // Data is considered fresh for 30 seconds before refetching
      staleTime: 30 * 1000,

      // Cache time: 5 minutes
      // Inactive queries are garbage collected after 5 minutes
      gcTime: 5 * 60 * 1000,

      // Refetch on window focus for important data
      refetchOnWindowFocus: true,

      // Don't refetch on mount if data is fresh
      refetchOnMount: false,

      // Retry failed requests 2 times
      retry: 2,

      // Exponential backoff for retries
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
    mutations: {
      // Retry mutations once on failure
      retry: 1,

      // Don't retry mutations that fail with 4xx errors
      // Only retry on network errors or 5xx
      retryDelay: 1000,
    },
  },
});

// Query Keys Factory
// Centralized place for all query keys to ensure consistency
export const queryKeys = {
  // Auth keys
  auth: {
    user: ['auth', 'user'] as const,
    gmailUrl: ['auth', 'gmail-url'] as const,
  },

  // Queue keys
  queue: {
    all: ['queue'] as const,
    list: (params?: Record<string, unknown>) =>
      ['queue', 'list', params] as const,
    detail: (id: string) => ['queue', 'detail', id] as const,
  },

  // Stats keys
  stats: {
    all: ['stats'] as const,
    summary: ['stats', 'summary'] as const,
  },

  // Conversation keys
  conversations: {
    all: ['conversations'] as const,
    detail: (id: string) => ['conversations', 'detail', id] as const,
    byObjective: (objectiveId: string) =>
      ['conversations', 'by-objective', objectiveId] as const,
  },
};

export default queryClient;
