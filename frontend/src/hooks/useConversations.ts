// Conversation Hooks
// React Query hooks for fetching conversation threads

import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import { queryKeys } from '../lib/queryClient';

// Hook to fetch a specific conversation by ID
export function useConversation(id: string | null | undefined) {
  return useQuery({
    queryKey: queryKeys.conversations.detail(id || ''),
    queryFn: () => api.conversations.get(id!),
    enabled: !!id, // Only fetch if ID is provided
    staleTime: 30 * 1000, // Consider stale after 30 seconds
    // Refetch on window focus for important conversation data
    refetchOnWindowFocus: true,
  });
}

// Hook to fetch conversation by objective ID
export function useConversationByObjective(objectiveId: string | null | undefined) {
  return useQuery({
    queryKey: queryKeys.conversations.byObjective(objectiveId || ''),
    queryFn: () => api.conversations.getByObjectiveId(objectiveId!),
    enabled: !!objectiveId, // Only fetch if objectiveId is provided
    staleTime: 30 * 1000,
    refetchOnWindowFocus: true,
  });
}
