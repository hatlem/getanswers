// Queue Management Hooks
// React Query hooks for queue operations with optimistic updates

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, type QueueParams } from '../lib/api';
import { queryKeys } from '../lib/queryClient';
import type { ActionCard } from '../types';

// Hook to fetch queue items
export function useQueue(params?: QueueParams) {
  return useQuery({
    queryKey: queryKeys.queue.list(params),
    queryFn: () => api.queue.getQueue(params),
    // Refetch every 30 seconds for real-time updates
    refetchInterval: 30 * 1000,
    // Keep previous data while refetching
    placeholderData: (previousData) => previousData,
    staleTime: 10 * 1000, // Consider stale after 10 seconds
  });
}

// Hook to approve a queue item
export function useApprove() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id }: { id: string }) => api.queue.approve(id),
    // Optimistic update
    onMutate: async ({ id }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: queryKeys.queue.all });

      // Snapshot previous value
      const previousQueues = queryClient.getQueriesData({
        queryKey: queryKeys.queue.all,
      });

      // Optimistically remove the item from all queue lists
      queryClient.setQueriesData<ActionCard[]>(
        { queryKey: queryKeys.queue.all },
        (old) => {
          if (!old) return old;
          return old.filter((card) => card.id !== id);
        }
      );

      // Return context with snapshot
      return { previousQueues };
    },
    // If mutation fails, rollback
    onError: (error, _variables, context) => {
      console.error('Approve failed:', error);
      if (context?.previousQueues) {
        context.previousQueues.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data);
        });
      }
    },
    // Always refetch after error or success
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.queue.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.stats.all });
    },
  });
}

// Hook to override a queue item
export function useOverride() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) =>
      api.queue.override(id, reason),
    // Optimistic update
    onMutate: async ({ id }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: queryKeys.queue.all });

      // Snapshot previous value
      const previousQueues = queryClient.getQueriesData({
        queryKey: queryKeys.queue.all,
      });

      // Optimistically remove the item from all queue lists
      queryClient.setQueriesData<ActionCard[]>(
        { queryKey: queryKeys.queue.all },
        (old) => {
          if (!old) return old;
          return old.filter((card) => card.id !== id);
        }
      );

      return { previousQueues };
    },
    onError: (error, _variables, context) => {
      console.error('Override failed:', error);
      if (context?.previousQueues) {
        context.previousQueues.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data);
        });
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.queue.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.stats.all });
    },
  });
}

// Hook to edit a queue item
export function useEdit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, content }: { id: string; content: string }) =>
      api.queue.edit(id, content),
    // Optimistic update
    onMutate: async ({ id, content }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: queryKeys.queue.all });

      // Snapshot previous value
      const previousQueues = queryClient.getQueriesData({
        queryKey: queryKeys.queue.all,
      });

      // Optimistically update the item in all queue lists
      queryClient.setQueriesData<ActionCard[]>(
        { queryKey: queryKeys.queue.all },
        (old) => {
          if (!old) return old;
          return old.map((card) =>
            card.id === id
              ? { ...card, proposedAction: content, updatedAt: new Date().toISOString() }
              : card
          );
        }
      );

      return { previousQueues };
    },
    onError: (error, _variables, context) => {
      console.error('Edit failed:', error);
      if (context?.previousQueues) {
        context.previousQueues.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data);
        });
      }
    },
    onSettled: (_data, _error, variables) => {
      // Refetch the specific item and related queries
      queryClient.invalidateQueries({ queryKey: queryKeys.queue.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.queue.all });
    },
  });
}

// Hook to escalate a queue item
export function useEscalate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) =>
      api.queue.escalate(id, reason),
    onSuccess: (data) => {
      // Update the cache with the escalated item
      queryClient.setQueriesData<ActionCard[]>(
        { queryKey: queryKeys.queue.all },
        (old) => {
          if (!old) return old;
          return old.map((card) => (card.id === data.id ? data : card));
        }
      );
    },
    onError: (error) => {
      console.error('Escalate failed:', error);
    },
    onSettled: (_data, _error, variables) => {
      // Refetch the specific item and related queries
      queryClient.invalidateQueries({ queryKey: queryKeys.queue.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.queue.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.stats.all });
    },
  });
}

// Combined hook for easier queue state management
export function useQueueActions() {
  const approveMutation = useApprove();
  const overrideMutation = useOverride();
  const editMutation = useEdit();
  const escalateMutation = useEscalate();

  return {
    approve: approveMutation.mutate,
    override: overrideMutation.mutate,
    edit: editMutation.mutate,
    escalate: escalateMutation.mutate,
    isApproving: approveMutation.isPending,
    isOverriding: overrideMutation.isPending,
    isEditing: editMutation.isPending,
    isEscalating: escalateMutation.isPending,
    approveError: approveMutation.error,
    overrideError: overrideMutation.error,
    editError: editMutation.error,
    escalateError: escalateMutation.error,
  };
}
