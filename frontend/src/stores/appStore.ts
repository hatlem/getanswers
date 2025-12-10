import { create } from 'zustand';
import type {
  ActionCard,
  ConversationThread,
  NavigationCount,
  EfficiencyStats,
  GlobalStatus,
  User,
  ObjectiveStatus,
  ActionType,
} from '../types';
import {
  mockUser,
  mockGlobalStatus,
  mockNavigationCounts,
  mockEfficiencyStats,
  mockActionCards,
  mockConversation,
} from '../lib/mockData';

interface AppState {
  // User
  user: User;

  // Global status
  globalStatus: GlobalStatus;

  // Navigation
  activeView: ObjectiveStatus | 'needs_decision';
  navigationCounts: NavigationCount;
  efficiencyStats: EfficiencyStats;

  // Review Queue
  actionCards: ActionCard[];
  selectedCardId: string | null;
  activeFilter: 'all' | 'high_risk' | 'low_confidence';

  // Conversation
  selectedConversation: ConversationThread | null;

  // Actions
  setActiveView: (view: ObjectiveStatus | 'needs_decision') => void;
  setActiveFilter: (filter: 'all' | 'high_risk' | 'low_confidence') => void;
  selectCard: (card: ActionCard) => void;
  clearSelection: () => void;
  handleCardAction: (cardId: string, action: ActionType) => void;
  updateCardConfidence: (cardId: string, confidence: number) => void;
  removeCard: (cardId: string) => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  // Initial state from mock data
  user: mockUser,
  globalStatus: mockGlobalStatus,
  activeView: 'needs_decision',
  navigationCounts: mockNavigationCounts,
  efficiencyStats: mockEfficiencyStats,
  actionCards: mockActionCards,
  selectedCardId: mockActionCards[0]?.id || null,
  activeFilter: 'all',
  selectedConversation: mockConversation,

  // Actions
  setActiveView: (view) => {
    set({ activeView: view });
  },

  setActiveFilter: (filter) => {
    set({ activeFilter: filter });
  },

  selectCard: (card) => {
    // In a real app, this would fetch the conversation for this card
    set({
      selectedCardId: card.id,
      selectedConversation: mockConversation, // Would be fetched based on card.objectiveId
    });
  },

  clearSelection: () => {
    set({
      selectedCardId: null,
      selectedConversation: null,
    });
  },

  handleCardAction: (cardId, action) => {
    const state = get();

    switch (action) {
      case 'approve':
        // Remove the card from the queue (action was approved)
        set({
          actionCards: state.actionCards.filter((c) => c.id !== cardId),
          navigationCounts: {
            ...state.navigationCounts,
            needsDecision: Math.max(0, state.navigationCounts.needsDecision - 1),
            handledByAI: state.navigationCounts.handledByAI + 1,
          },
          globalStatus: {
            ...state.globalStatus,
            pendingCount: Math.max(0, state.globalStatus.pendingCount - 1),
            message:
              state.globalStatus.pendingCount - 1 <= 0
                ? 'All Systems Go.'
                : `${state.globalStatus.pendingCount - 1} Decision${state.globalStatus.pendingCount - 1 !== 1 ? 's' : ''} Pending`,
            status: state.globalStatus.pendingCount - 1 <= 0 ? 'all_clear' : 'pending_decisions',
          },
        });

        // Clear selection if this card was selected
        if (state.selectedCardId === cardId) {
          const remainingCards = state.actionCards.filter((c) => c.id !== cardId);
          set({
            selectedCardId: remainingCards[0]?.id || null,
            selectedConversation: remainingCards.length > 0 ? mockConversation : null,
          });
        }
        break;

      case 'override':
        // Similar to approve but logs as rejected
        set({
          actionCards: state.actionCards.filter((c) => c.id !== cardId),
          navigationCounts: {
            ...state.navigationCounts,
            needsDecision: Math.max(0, state.navigationCounts.needsDecision - 1),
          },
          globalStatus: {
            ...state.globalStatus,
            pendingCount: Math.max(0, state.globalStatus.pendingCount - 1),
            message:
              state.globalStatus.pendingCount - 1 <= 0
                ? 'All Systems Go.'
                : `${state.globalStatus.pendingCount - 1} Decision${state.globalStatus.pendingCount - 1 !== 1 ? 's' : ''} Pending`,
            status: state.globalStatus.pendingCount - 1 <= 0 ? 'all_clear' : 'pending_decisions',
          },
        });

        if (state.selectedCardId === cardId) {
          const remainingCards = state.actionCards.filter((c) => c.id !== cardId);
          set({
            selectedCardId: remainingCards[0]?.id || null,
            selectedConversation: remainingCards.length > 0 ? mockConversation : null,
          });
        }
        break;

      case 'edit':
        // Would open an edit modal in real implementation
        console.log('Edit action for card:', cardId);
        break;

      case 'escalate':
        // Would expand the right column or open detail view
        console.log('Escalate action for card:', cardId);
        break;
    }
  },

  updateCardConfidence: (cardId, confidence) => {
    set({
      actionCards: get().actionCards.map((card) =>
        card.id === cardId ? { ...card, confidenceScore: confidence } : card
      ),
    });
  },

  removeCard: (cardId) => {
    const state = get();
    set({
      actionCards: state.actionCards.filter((c) => c.id !== cardId),
    });
  },
}));
