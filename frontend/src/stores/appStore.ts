import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  User,
  ObjectiveStatus,
} from '../types';

// Updated store to work alongside React Query
// React Query now handles server state (queue, stats, conversations)
// Zustand handles UI state and auth state

interface AppState {
  // Auth state (synced with React Query)
  user: User | null;
  isAuthenticated: boolean;

  // UI state
  activeView: ObjectiveStatus | 'needs_decision';
  selectedCardId: string | null;
  selectedObjectiveId: string | null;
  activeFilter: 'all' | 'high_risk' | 'low_confidence';

  // Actions
  setUser: (user: User | null) => void;
  setAuthenticated: (isAuthenticated: boolean) => void;
  setActiveView: (view: ObjectiveStatus | 'needs_decision') => void;
  setActiveFilter: (filter: 'all' | 'high_risk' | 'low_confidence') => void;
  setSelectedCard: (cardId: string | null, objectiveId?: string | null) => void;
  clearSelection: () => void;
  logout: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // Initial state
      user: null,
      isAuthenticated: false,
      activeView: 'needs_decision',
      selectedCardId: null,
      selectedObjectiveId: null,
      activeFilter: 'all',

      // Actions
      setUser: (user) => {
        set({ user, isAuthenticated: !!user });
      },

      setAuthenticated: (isAuthenticated) => {
        set({ isAuthenticated });
      },

      setActiveView: (view) => {
        set({ activeView: view });
      },

      setActiveFilter: (filter) => {
        set({ activeFilter: filter });
      },

      setSelectedCard: (cardId, objectiveId = null) => {
        set({
          selectedCardId: cardId,
          selectedObjectiveId: objectiveId,
        });
      },

      clearSelection: () => {
        set({
          selectedCardId: null,
          selectedObjectiveId: null,
        });
      },

      logout: () => {
        set({
          user: null,
          isAuthenticated: false,
          selectedCardId: null,
          selectedObjectiveId: null,
        });
      },
    }),
    {
      name: 'getanswers-app-store',
      // Only persist UI preferences, not auth state
      partialize: (state) => ({
        activeView: state.activeView,
        activeFilter: state.activeFilter,
      }),
    }
  )
);
