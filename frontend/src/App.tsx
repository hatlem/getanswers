import { useState } from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route, Navigate, useSearchParams, useNavigate } from 'react-router-dom';
import { TopNav } from './components/layout/TopNav';
import { LeftColumn } from './components/layout/LeftColumn';
import { CenterColumn } from './components/layout/CenterColumn';
import { RightColumn } from './components/layout/RightColumn';
import { LandingPage } from './components/LandingPage';
import { LoginPage } from './components/auth/LoginPage';
import { RegisterPage } from './components/auth/RegisterPage';
import { MagicLinkPage } from './components/auth/MagicLinkPage';
import { GmailCallbackPage } from './components/auth/GmailCallbackPage';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { EditModal } from './components/modals/EditModal';
import { OnboardingModal } from './components/OnboardingModal';
import { ErrorBoundary } from './components/ErrorBoundary';
import { useAppStore } from './stores/appStore';
import { queryClient } from './lib/queryClient';
import { useAuth } from './hooks/useAuth';
import { useAuthStore } from './stores/authStore';
import { useStats } from './hooks/useStats';
import { useQueueActions } from './hooks/useQueue';
import { actionToast } from './lib/toast';
import type { ActionCard, ActionType } from './types';

// Main dashboard component
function Dashboard() {
  const {
    activeView,
    selectedCardId,
    selectedObjectiveId,
    activeFilter,
    setActiveView,
    setActiveFilter,
    setSelectedCard,
  } = useAppStore();

  // Onboarding state - show for new users who haven't completed it
  const ONBOARDING_KEY = 'getanswers_onboarding_complete';
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { connectGmail, gmailConnected } = useAuthStore();

  // Show onboarding if: URL param says start OR user hasn't completed onboarding yet
  const [isOnboardingOpen, setIsOnboardingOpen] = useState(() => {
    const hasCompletedOnboarding = localStorage.getItem(ONBOARDING_KEY) === 'true';
    const urlTriggered = searchParams.get('onboarding') === 'start';
    return urlTriggered || !hasCompletedOnboarding;
  });

  const handleCloseOnboarding = () => {
    // Mark onboarding as complete
    localStorage.setItem(ONBOARDING_KEY, 'true');
    setIsOnboardingOpen(false);
    navigate('/dashboard', { replace: true });
  };

  const handleConnectGmail = () => {
    connectGmail();
  };

  // Edit modal state
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [cardToEdit, setCardToEdit] = useState<ActionCard | null>(null);

  // Fetch user data
  const { user } = useAuth();

  // Fetch data using React Query hooks
  const { data: stats, isLoading: statsLoading } = useStats();
  const { approve, override, edit, escalate, isEditing } = useQueueActions();

  // Handler for card actions with toast notifications
  const handleCardAction = (cardId: string, action: ActionType, card?: ActionCard) => {
    switch (action) {
      case 'approve':
        approve(
          { id: cardId },
          {
            onSuccess: () => actionToast.approve(),
            onError: (error) => actionToast.approveError(error.message),
          }
        );
        break;
      case 'override':
        // In real implementation, would show modal to get reason
        override(
          { id: cardId, reason: 'User override' },
          {
            onSuccess: () => actionToast.override(),
            onError: (error) => actionToast.overrideError(error.message),
          }
        );
        break;
      case 'edit':
        if (card) {
          setCardToEdit(card);
          setEditModalOpen(true);
        }
        break;
      case 'escalate':
        // In real implementation, would show modal to get reason
        escalate(
          { id: cardId, reason: 'User escalation' },
          {
            onSuccess: () => actionToast.escalate(),
            onError: (error) => actionToast.escalateError(error.message),
          }
        );
        break;
    }
  };

  // Handler for card selection
  const handleSelectCard = (card: ActionCard) => {
    setSelectedCard(card.id, card.objectiveId);
  };

  // Handler for edit modal save
  const handleEditSave = (cardId: string, content: string) => {
    edit(
      { id: cardId, content },
      {
        onSuccess: () => {
          actionToast.approve(); // Using approve toast for now
          setEditModalOpen(false);
          setCardToEdit(null);
        },
        onError: (error) => {
          actionToast.approveError(error.message);
        },
      }
    );
  };

  // Show loading state for initial stats load only
  // Queue loading is handled in CenterColumn
  if (statsLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-surface-base">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-cyan mx-auto mb-4"></div>
          <p className="text-text-secondary">Loading GetAnswers...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-surface-base overflow-hidden">
      <TopNav
        user={user || null}
        globalStatus={stats?.globalStatus || null}
      />

      <main className="flex-1 flex min-h-0">
        <LeftColumn
          counts={stats?.navigationCounts}
          stats={stats?.efficiencyStats}
          activeView={activeView}
          onViewChange={setActiveView}
        />

        <CenterColumn
          selectedCardId={selectedCardId ?? undefined}
          onSelectCard={handleSelectCard}
          onAction={handleCardAction}
          activeFilter={activeFilter}
          onFilterChange={setActiveFilter}
          activeView={activeView}
        />

        <RightColumn
          objectiveId={selectedObjectiveId}
        />
      </main>

      {/* Edit Modal */}
      <EditModal
        isOpen={editModalOpen}
        onClose={() => {
          setEditModalOpen(false);
          setCardToEdit(null);
        }}
        card={cardToEdit}
        onSave={handleEditSave}
        isSaving={isEditing}
      />

      {/* Onboarding Modal */}
      <OnboardingModal
        isOpen={isOnboardingOpen}
        onClose={handleCloseOnboarding}
        onConnectGmail={handleConnectGmail}
      />
    </div>
  );
}

// App content with routing
function AppContent() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/auth/verify" element={<MagicLinkPage />} />
        <Route path="/auth/gmail/callback" element={<GmailCallbackPage />} />

        {/* Protected routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* Catch all - redirect to home */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AppContent />
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
