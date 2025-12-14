import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { Loader2, Layers } from 'lucide-react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';

export function OutlookCallbackPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { handleOutlookCallback } = useAuthStore();

  useEffect(() => {
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    const error = searchParams.get('error');
    const errorDescription = searchParams.get('error_description');

    if (error) {
      // Redirect back to main app with error in URL
      navigate('/dashboard?outlook_error=' + encodeURIComponent(errorDescription || error));
      return;
    }

    if (code && state) {
      handleCallback(code, state);
    } else {
      // No code or error, redirect to main app
      navigate('/dashboard');
    }
  }, [searchParams]);

  const handleCallback = async (code: string, state: string) => {
    try {
      await handleOutlookCallback(code, state);
      // Redirect to dashboard with success flag
      navigate('/dashboard?outlook_connected=true');
    } catch (err) {
      // Redirect to dashboard with error
      navigate('/dashboard?outlook_error=connection_failed');
    }
  };

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
          <span className="text-sm font-medium">Connecting Microsoft Outlook...</span>
        </div>
      </motion.div>
    </div>
  );
}
