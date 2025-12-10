import { QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { TopNav } from './components/layout/TopNav';
import { LeftColumn } from './components/layout/LeftColumn';
import { CenterColumn } from './components/layout/CenterColumn';
import { RightColumn } from './components/layout/RightColumn';
import { LoginPage } from './components/auth/LoginPage';
import { RegisterPage } from './components/auth/RegisterPage';
import { MagicLinkPage } from './components/auth/MagicLinkPage';
import { GmailCallbackPage } from './components/auth/GmailCallbackPage';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { useAppStore } from './stores/appStore';
import { queryClient } from './lib/queryClient';
import { useAuth } from './hooks/useAuth';
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

  // Fetch user data
  const { user } = useAuth();

  // Fetch data using React Query hooks
  const { data: stats, isLoading: statsLoading } = useStats();
  const { approve, override, edit, escalate } = useQueueActions();

  // Handler for card actions with toast notifications
  const handleCardAction = (cardId: string, action: ActionType) => {
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
        // In real implementation, would show modal to get edited content
        console.log('Edit action for card:', cardId);
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
        onSearch={(query) => console.log('Search:', query)}
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
          onTakeOver={() => console.log('Take over thread')}
          onChangePolicy={() => console.log('Change policy')}
        />
      </main>
    </div>
  );
}

// App content with routing
function AppContent() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/auth/verify" element={<MagicLinkPage />} />
        <Route path="/auth/gmail/callback" element={<GmailCallbackPage />} />

        {/* Protected routes */}
        <Route
          path="/"
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
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
}

export default App;
