import { useState } from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route, Navigate, useSearchParams, useNavigate } from 'react-router-dom';
import { TopNav } from './components/layout/TopNav';
import { LeftColumn } from './components/layout/LeftColumn';
import { CenterColumn } from './components/layout/CenterColumn';
import { RightColumn } from './components/layout/RightColumn';
import { LandingPage } from './components/LandingPage';
import { CompareIndexPage } from './components/compare/CompareIndexPage';
import { CompareSaneboxPage } from './components/compare/CompareSaneboxPage';
import { CompareSuperhuman } from './components/compare/CompareSuperhuman';
import { CompareShortwave } from './components/compare/CompareShortwave';
import { CompareMailbutler } from './components/compare/CompareMailbutler';
import { CompareFront } from './components/compare/CompareFront';
import { CompareSpark } from './components/compare/CompareSpark';
import { CompareMissive } from './components/compare/CompareMissive';
import { CompareHelpScout } from './components/compare/CompareHelpScout';
import { CompareBoomerangPage } from './components/compare/CompareBoomerang';
import { CompareZohoMailPage } from './components/compare/CompareZohoMail';
import { CompareMailbird } from './components/compare/CompareMailbird';
import { CompareNewtonMail } from './components/compare/CompareNewtonMail';
import { ComparePolymail } from './components/compare/ComparePolymail';
import { CompareEmClient } from './components/compare/CompareEmClient';
import { CompareMailspring } from './components/compare/CompareMailspring';
import { CompareBlueMail } from './components/compare/CompareBlueMail';
import { CompareEllie } from './components/compare/CompareEllie';
import { CompareAddyAI } from './components/compare/CompareAddyAI';
import { CompareComposeAI } from './components/compare/CompareComposeAI';
import { CompareReadyToSend } from './components/compare/CompareReadyToSend';
import { CompareLavender } from './components/compare/CompareLavender';
import { CompareHey } from './components/compare/CompareHey';
import { CompareCanaryMail } from './components/compare/CompareCanaryMail';
import { LoginPage } from './components/auth/LoginPage';
import { RegisterPage } from './components/auth/RegisterPage';
import OnboardingPage from './pages/OnboardingPage';
import { MagicLinkPage } from './components/auth/MagicLinkPage';
import { GmailCallbackPage } from './components/auth/GmailCallbackPage';
import { OutlookCallbackPage } from './components/auth/OutlookCallbackPage';
import { GoogleAuthCallbackPage } from './components/auth/GoogleAuthCallbackPage';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { EditModal } from './components/modals/EditModal';
import { OnboardingModal } from './components/OnboardingModal';
import { PasswordSetupModal } from './components/PasswordSetupModal';
import { BillingPage } from './components/billing/BillingPage';
import { SettingsPage } from './components/settings/SettingsPage';
import { AdminPage } from './components/admin/AdminPage';
import { FreeToolsPage } from './components/FreeToolsPage';
import { FreeToolsThankYouPage } from './components/FreeToolsThankYouPage';
import EmailPromptsPage from './pages/EmailPromptsPage';
import TriageFrameworkPage from './pages/TriageFrameworkPage';
import PolicyTemplatePage from './pages/PolicyTemplatePage';
import TimeCalculatorPage from './pages/TimeCalculatorPage';
import InboxChecklistPage from './pages/InboxChecklistPage';
import LeadMagnetThankYouPage from './pages/LeadMagnetThankYouPage';
import ResponseTimeCalculator from './pages/lead-magnets/ResponseTimeCalculator';
import { ErrorBoundary } from './components/ErrorBoundary';
import { useAppStore } from './stores/appStore';
import { queryClient } from './lib/queryClient';
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
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user, connectGmail, connectOutlook, connectSMTP, completeOnboarding } = useAuthStore();

  // Show onboarding if: URL param says start OR user hasn't completed onboarding yet (from database)
  const urlTriggered = searchParams.get('onboarding') === 'start';
  const hasCompletedOnboarding = user?.onboarding_completed ?? false;
  const needsPasswordSetup = user?.needs_password_setup ?? false;
  const [isOnboardingOpen, setIsOnboardingOpen] = useState(urlTriggered || !hasCompletedOnboarding);
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);

  const handleCloseOnboarding = async () => {
    // Mark onboarding as complete in the database
    await completeOnboarding();
    setIsOnboardingOpen(false);
    navigate('/dashboard', { replace: true });

    // After onboarding, prompt user to set password if needed
    if (needsPasswordSetup) {
      setIsPasswordModalOpen(true);
    }
  };

  const handlePasswordSetupComplete = () => {
    setIsPasswordModalOpen(false);
  };

  const handleConnectGmail = () => {
    connectGmail();
  };

  const handleConnectOutlook = () => {
    connectOutlook();
  };

  const handleConnectSMTP = async (credentials: {
    email: string;
    password: string;
    imap_server: string;
    imap_port: number;
    smtp_server: string;
    smtp_port: number;
    use_ssl: boolean;
  }) => {
    await connectSMTP(credentials);
  };

  // Edit modal state
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [cardToEdit, setCardToEdit] = useState<ActionCard | null>(null);

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
        onConnectOutlook={handleConnectOutlook}
        onConnectSMTP={handleConnectSMTP}
      />

      {/* Password Setup Modal - shown after onboarding for quick signup users */}
      {isPasswordModalOpen && (
        <PasswordSetupModal onComplete={handlePasswordSetupComplete} />
      )}
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
        <Route path="/compare" element={<CompareIndexPage />} />
        <Route path="/compare/sanebox" element={<CompareSaneboxPage />} />
        <Route path="/compare/superhuman" element={<CompareSuperhuman />} />
        <Route path="/compare/shortwave" element={<CompareShortwave />} />
        <Route path="/compare/mailbutler" element={<CompareMailbutler />} />
        <Route path="/compare/front" element={<CompareFront />} />
        <Route path="/compare/spark" element={<CompareSpark />} />
        <Route path="/compare/missive" element={<CompareMissive />} />
        <Route path="/compare/helpscout" element={<CompareHelpScout />} />
        <Route path="/compare/boomerang" element={<CompareBoomerangPage />} />
        <Route path="/compare/zoho-mail" element={<CompareZohoMailPage />} />
        <Route path="/compare/mailbird" element={<CompareMailbird />} />
        <Route path="/compare/newton-mail" element={<CompareNewtonMail />} />
        <Route path="/compare/polymail" element={<ComparePolymail />} />
        <Route path="/compare/em-client" element={<CompareEmClient />} />
        <Route path="/compare/mailspring" element={<CompareMailspring />} />
        <Route path="/compare/bluemail" element={<CompareBlueMail />} />
        <Route path="/compare/ellie" element={<CompareEllie />} />
        <Route path="/compare/addy-ai" element={<CompareAddyAI />} />
        <Route path="/compare/compose-ai" element={<CompareComposeAI />} />
        <Route path="/compare/ready-to-send" element={<CompareReadyToSend />} />
        <Route path="/compare/lavender" element={<CompareLavender />} />
        <Route path="/compare/hey" element={<CompareHey />} />
        <Route path="/compare/canary-mail" element={<CompareCanaryMail />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/onboarding" element={<OnboardingPage />} />
        <Route path="/auth/verify" element={<MagicLinkPage />} />
        <Route path="/auth/gmail/callback" element={<GmailCallbackPage />} />
        <Route path="/auth/outlook/callback" element={<OutlookCallbackPage />} />
        <Route path="/api/auth/callback/google" element={<GoogleAuthCallbackPage />} />
        <Route path="/free-tools" element={<FreeToolsPage />} />
        <Route path="/free-tools/thank-you" element={<FreeToolsThankYouPage />} />

        {/* Lead Magnet routes */}
        <Route path="/lead-magnets/email-prompts" element={<EmailPromptsPage />} />
        <Route path="/lead-magnets/triage-framework" element={<TriageFrameworkPage />} />
        <Route path="/lead-magnets/policy-template" element={<PolicyTemplatePage />} />
        <Route path="/lead-magnets/time-calculator" element={<TimeCalculatorPage />} />
        <Route path="/lead-magnets/inbox-checklist" element={<InboxChecklistPage />} />
        <Route path="/lead-magnets/response-time-calculator" element={<ResponseTimeCalculator />} />
        <Route path="/lead-magnets/thank-you" element={<LeadMagnetThankYouPage />} />

        {/* Protected routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/billing"
          element={
            <ProtectedRoute>
              <BillingPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <SettingsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <ProtectedRoute requireSuperAdmin>
              <AdminPage />
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
