// Statistics Hooks
// React Query hooks for fetching application statistics

import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import { queryKeys } from '../lib/queryClient';

// Hook to fetch statistics
export function useStats() {
  return useQuery({
    queryKey: queryKeys.stats.summary,
    queryFn: api.stats.get,
    // Refetch stats every 15 seconds for real-time dashboard
    refetchInterval: 15 * 1000,
    // Keep previous data while refetching to avoid UI flashing
    placeholderData: (previousData) => previousData,
    // Consider stale after 10 seconds
    staleTime: 10 * 1000,
    // Refetch on window focus to ensure fresh data
    refetchOnWindowFocus: true,
  });
}

// Hook for navigation counts only
export function useNavigationCounts() {
  const { data: stats, isLoading, error } = useStats();

  return {
    counts: stats?.navigationCounts,
    isLoading,
    error,
  };
}

// Hook for efficiency stats only
export function useEfficiencyStats() {
  const { data: stats, isLoading, error } = useStats();

  return {
    stats: stats?.efficiencyStats,
    isLoading,
    error,
  };
}

// Hook for global status only
export function useGlobalStatus() {
  const { data: stats, isLoading, error } = useStats();

  return {
    status: stats?.globalStatus,
    isLoading,
    error,
  };
}
