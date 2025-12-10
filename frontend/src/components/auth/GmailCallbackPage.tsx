import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { Loader2, Layers } from 'lucide-react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';

export function GmailCallbackPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { handleGmailCallback } = useAuthStore();

  useEffect(() => {
    const code = searchParams.get('code');
    const error = searchParams.get('error');

    if (error) {
      // Redirect back to main app with error in URL
      navigate('/?gmail_error=' + error);
      return;
    }

    if (code) {
      handleCallback(code);
    } else {
      // No code or error, redirect to main app
      navigate('/');
    }
  }, [searchParams]);

  const handleCallback = async (code: string) => {
    try {
      await handleGmailCallback(code);
      // Redirect to main app with success flag
      navigate('/?gmail_connected=true');
    } catch (err) {
      // Redirect to main app with error
      navigate('/?gmail_error=connection_failed');
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
          <span className="text-sm font-medium">Connecting Gmail...</span>
        </div>
      </motion.div>
    </div>
  );
}
