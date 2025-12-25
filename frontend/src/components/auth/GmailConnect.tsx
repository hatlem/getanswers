import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mail, CheckCircle2, AlertCircle, Loader2, Link as LinkIcon, Unlink } from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';
import { Button } from '../ui/button';
import { useSearchParams, useNavigate } from 'react-router-dom';

interface GmailConnectProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
  variant?: 'card' | 'inline';
  showStatus?: boolean;
}

export function GmailConnect({
  onSuccess,
  onError,
  variant = 'card',
  showStatus = true,
}: GmailConnectProps) {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { gmailConnected, connectGmail, disconnectGmail, handleGmailCallback, isLoading } = useAuthStore();

  const [localLoading, setLocalLoading] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Handle OAuth callback
  useEffect(() => {
    const code = searchParams.get('code');
    const errorParam = searchParams.get('error');

    if (code) {
      handleCallback(code);
    } else if (errorParam) {
      const errorMessage = errorParam === 'access_denied'
        ? 'Gmail connection was cancelled'
        : 'Failed to connect Gmail';
      setError(errorMessage);
      onError?.(errorMessage);
      // Clean up URL
      searchParams.delete('error');
      setSearchParams(searchParams);
    }
  }, [searchParams]);

  const handleCallback = async (code: string) => {
    setLocalLoading(true);
    setError(null);

    try {
      await handleGmailCallback(code);
      setShowSuccess(true);
      onSuccess?.();

      // Clean up URL
      searchParams.delete('code');
      searchParams.delete('state');
      setSearchParams(searchParams);

      // Hide success message after 3 seconds
      setTimeout(() => setShowSuccess(false), 3000);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to connect Gmail';
      setError(errorMessage);
      onError?.(errorMessage);
    } finally {
      setLocalLoading(false);
    }
  };

  const handleConnect = () => {
    setError(null);
    connectGmail();
  };

  const handleDisconnect = async () => {
    setLocalLoading(true);
    setError(null);

    try {
      await disconnectGmail();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to disconnect Gmail';
      setError(errorMessage);
      onError?.(errorMessage);
    } finally {
      setLocalLoading(false);
    }
  };

  const isProcessing = isLoading || localLoading;

  if (variant === 'inline') {
    return (
      <div className="space-y-3">
        {showStatus && gmailConnected && (
          <div className="flex items-center gap-2 p-3 bg-success-muted border border-success-border rounded-lg">
            <CheckCircle2 className="w-4 h-4 text-success flex-shrink-0" />
            <span className="text-sm text-success font-medium">Gmail Connected</span>
          </div>
        )}

        {error && (
          <div className="flex items-center gap-2 p-3 bg-critical-muted border border-critical-border rounded-lg">
            <AlertCircle className="w-4 h-4 text-critical flex-shrink-0" />
            <span className="text-sm text-critical">{error}</span>
          </div>
        )}

        {gmailConnected ? (
          <Button
            variant="outline"
            onClick={handleDisconnect}
            isLoading={isProcessing}
            icon={<Unlink className="w-4 h-4" />}
            className="w-full"
          >
            Disconnect Gmail
          </Button>
        ) : (
          <Button
            variant="primary"
            onClick={handleConnect}
            isLoading={isProcessing}
            icon={<Mail className="w-4 h-4" />}
            className="w-full"
          >
            Connect Gmail
          </Button>
        )}
      </div>
    );
  }

  // Card variant
  return (
    <div className="bg-surface-card border border-surface-border rounded-xl p-4 md:p-6">
      {/* Header */}
      <div className="flex items-start gap-3 md:gap-4 mb-4">
        <div className="w-10 h-10 md:w-12 md:h-12 rounded-lg bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center flex-shrink-0">
          <Mail className="w-5 h-5 md:w-6 md:h-6 text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-base md:text-lg font-semibold text-text-primary mb-1">
            Gmail Integration
          </h3>
          <p className="text-xs md:text-sm text-text-secondary">
            {gmailConnected
              ? 'Your Gmail account is connected and active'
              : 'Connect your Gmail to start managing emails with AI'}
          </p>
        </div>
      </div>

      {/* Status Messages */}
      <AnimatePresence mode="wait">
        {showSuccess && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mb-4 p-3 bg-success-muted border border-success-border rounded-lg flex items-center gap-2"
          >
            <CheckCircle2 className="w-4 h-4 text-success flex-shrink-0" />
            <span className="text-sm text-success font-medium">
              Gmail connected successfully!
            </span>
          </motion.div>
        )}

        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mb-4 p-3 bg-critical-muted border border-critical-border rounded-lg flex items-center gap-2"
          >
            <AlertCircle className="w-4 h-4 text-critical flex-shrink-0" />
            <span className="text-sm text-critical">{error}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Connection Status */}
      {showStatus && (
        <div className="mb-4 p-4 bg-surface-hover rounded-lg border border-surface-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-text-secondary">Status</span>
            <div className="flex items-center gap-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  gmailConnected ? 'bg-success animate-pulse' : 'bg-text-muted'
                }`}
              />
              <span className={`text-sm font-medium ${
                gmailConnected ? 'text-success' : 'text-text-muted'
              }`}>
                {gmailConnected ? 'Connected' : 'Not Connected'}
              </span>
            </div>
          </div>

          {gmailConnected && (
            <div className="space-y-2 mt-3 pt-3 border-t border-surface-border">
              <div className="flex items-center justify-between text-xs">
                <span className="text-text-muted">Emails syncing</span>
                <span className="text-success font-medium">Active</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-text-muted">AI assistance</span>
                <span className="text-success font-medium">Enabled</span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Features */}
      {!gmailConnected && (
        <div className="mb-4 p-4 bg-surface-hover rounded-lg border border-surface-border">
          <p className="text-xs font-medium text-text-secondary mb-2">What you'll get:</p>
          <ul className="space-y-2 text-xs text-text-muted">
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-3 h-3 text-accent-cyan flex-shrink-0" />
              Automatic email monitoring and categorization
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-3 h-3 text-accent-cyan flex-shrink-0" />
              AI-powered response suggestions
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-3 h-3 text-accent-cyan flex-shrink-0" />
              Smart priority detection and alerts
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-3 h-3 text-accent-cyan flex-shrink-0" />
              Autonomous handling of routine emails
            </li>
          </ul>
        </div>
      )}

      {/* Action Button */}
      {gmailConnected ? (
        <Button
          variant="outline"
          onClick={handleDisconnect}
          isLoading={isProcessing}
          icon={<Unlink className="w-4 h-4" />}
          className="w-full"
        >
          Disconnect Gmail
        </Button>
      ) : (
        <Button
          variant="primary"
          onClick={handleConnect}
          isLoading={isProcessing}
          icon={<LinkIcon className="w-4 h-4" />}
          className="w-full"
        >
          Connect Gmail Account
        </Button>
      )}

      {/* Security Note */}
      <p className="mt-3 text-xs text-text-muted text-center">
        We use OAuth 2.0 for secure authentication. We never store your password.
      </p>
    </div>
  );
}
