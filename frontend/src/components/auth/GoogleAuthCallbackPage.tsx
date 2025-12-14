import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Loader2, Layers, AlertCircle } from 'lucide-react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';
import { apiClient } from '../../lib/api-client';
import { Button } from '../ui/Button';

export function GoogleAuthCallbackPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { setUser, setToken } = useAuthStore();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    const errorParam = searchParams.get('error');

    if (errorParam) {
      setError(`Google authentication failed: ${errorParam}`);
      return;
    }

    if (code && state) {
      handleCallback(code, state);
    } else {
      setError('Missing authentication parameters');
    }
  }, [searchParams]);

  const handleCallback = async (code: string, state: string) => {
    try {
      const response = await apiClient.post<{
        user: {
          id: string;
          email: string;
          name: string;
          is_super_admin: boolean;
          current_organization: {
            id: string;
            name: string;
            slug: string;
            is_personal: boolean;
          } | null;
          onboarding_completed: boolean;
          needs_password_setup: boolean;
          created_at: string;
        };
        access_token: string;
      }>('/api/auth/google/callback', {
        code,
        state,
        redirect_uri: `${window.location.origin}/auth/google/callback`,
      });

      // Store the token and user
      setToken(response.access_token);
      setUser(response.user);

      // Redirect to dashboard
      navigate('/dashboard', { replace: true });
    } catch (err: any) {
      console.error('Google auth callback error:', err);
      setError(err.message || 'Failed to authenticate with Google');
    }
  };

  if (error) {
    return (
      <div className="h-screen bg-surface-base flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center max-w-md mx-auto p-6"
        >
          <div className="w-16 h-16 rounded-xl bg-critical/20 flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-9 h-9 text-critical" />
          </div>
          <h2 className="text-xl font-bold text-text-primary mb-2">Authentication Failed</h2>
          <p className="text-text-secondary mb-6">{error}</p>
          <Button
            variant="primary"
            onClick={() => navigate('/login')}
            className="w-full"
          >
            Back to Login
          </Button>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-surface-base flex items-center justify-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="text-center"
      >
        <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-accent-cyan to-accent-purple flex items-center justify-center mx-auto mb-4">
          <Layers className="w-9 h-9 text-white" />
        </div>
        <div className="flex items-center justify-center gap-2 text-text-secondary">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span className="text-sm font-medium">Signing in with Google...</span>
        </div>
      </motion.div>
    </div>
  );
}
