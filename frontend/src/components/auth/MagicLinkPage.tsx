import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Mail, Sparkles, Loader2, CheckCircle2, XCircle, ArrowRight, Layers } from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';

type ViewState = 'request' | 'verifying' | 'success' | 'error' | 'sent';

export function MagicLinkPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { requestMagicLink, verifyMagicLink, isLoading, error, clearError } = useAuthStore();

  const [email, setEmail] = useState('');
  const [validationError, setValidationError] = useState('');
  const [viewState, setViewState] = useState<ViewState>('request');
  const [errorMessage, setErrorMessage] = useState('');

  // Check if there's a token in the URL
  useEffect(() => {
    const token = searchParams.get('token');
    if (token) {
      handleVerifyToken(token);
    }
  }, [searchParams]);

  const handleVerifyToken = async (token: string) => {
    setViewState('verifying');
    try {
      await verifyMagicLink(token);
      setViewState('success');
      // Redirect to main app after success
      setTimeout(() => {
        navigate('/');
      }, 2000);
    } catch (err) {
      setViewState('error');
      setErrorMessage(error || 'Failed to verify magic link. The link may have expired.');
    }
  };

  const validateEmail = (email: string) => {
    if (!email) {
      setValidationError('Email is required');
      return false;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setValidationError('Please enter a valid email');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setValidationError('');

    if (!validateEmail(email)) return;

    try {
      await requestMagicLink(email);
      setViewState('sent');
    } catch (err) {
      setErrorMessage(error || 'Failed to send magic link. Please try again.');
    }
  };

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
    if (validationError) {
      setValidationError('');
    }
  };

  // Verifying state
  if (viewState === 'verifying') {
    return (
      <div className="min-h-screen bg-surface-base flex items-center justify-center p-4 md:p-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-md"
        >
          <div className="bg-surface-card border border-surface-border rounded-2xl p-6 md:p-8 text-center">
            <div className="w-14 h-14 md:w-16 md:h-16 rounded-full bg-accent-cyan/20 flex items-center justify-center mx-auto mb-4">
              <Loader2 className="w-7 h-7 md:w-8 md:h-8 text-accent-cyan animate-spin" />
            </div>
            <h2 className="text-xl md:text-2xl font-bold text-text-primary mb-2">Verifying...</h2>
            <p className="text-text-secondary">
              Please wait while we verify your magic link
            </p>
          </div>
        </motion.div>
      </div>
    );
  }

  // Success state
  if (viewState === 'success') {
    return (
      <div className="min-h-screen bg-surface-base flex items-center justify-center p-4 md:p-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-md"
        >
          <div className="bg-surface-card border border-success/30 rounded-2xl p-6 md:p-8 text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring' }}
              className="w-14 h-14 md:w-16 md:h-16 rounded-full bg-success/20 flex items-center justify-center mx-auto mb-4"
            >
              <CheckCircle2 className="w-7 h-7 md:w-8 md:h-8 text-success" />
            </motion.div>
            <h2 className="text-xl md:text-2xl font-bold text-text-primary mb-2">Success!</h2>
            <p className="text-text-secondary mb-4">
              You've been successfully authenticated
            </p>
            <p className="text-sm text-text-muted">
              Redirecting to your dashboard...
            </p>
          </div>
        </motion.div>
      </div>
    );
  }

  // Error state
  if (viewState === 'error') {
    return (
      <div className="min-h-screen bg-surface-base flex items-center justify-center p-4 md:p-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-md"
        >
          <div className="bg-surface-card border border-critical/30 rounded-2xl p-6 md:p-8 text-center">
            <div className="w-14 h-14 md:w-16 md:h-16 rounded-full bg-critical/20 flex items-center justify-center mx-auto mb-4">
              <XCircle className="w-7 h-7 md:w-8 md:h-8 text-critical" />
            </div>
            <h2 className="text-xl md:text-2xl font-bold text-text-primary mb-2">Verification Failed</h2>
            <p className="text-text-secondary mb-6">
              {errorMessage}
            </p>
            <Button
              variant="primary"
              onClick={() => {
                setViewState('request');
                setErrorMessage('');
                clearError();
              }}
              className="w-full"
            >
              Request New Link
            </Button>
            <div className="mt-4">
              <Link
                to="/login"
                className="text-sm text-accent-cyan hover:text-accent-cyan/80 transition-colors"
              >
                Back to Login
              </Link>
            </div>
          </div>
        </motion.div>
      </div>
    );
  }

  // Sent state
  if (viewState === 'sent') {
    return (
      <div className="min-h-screen bg-surface-base flex items-center justify-center p-4 md:p-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-md"
        >
          <div className="bg-surface-card border border-surface-border rounded-2xl p-6 md:p-8 text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring' }}
              className="w-14 h-14 md:w-16 md:h-16 rounded-full bg-success/20 flex items-center justify-center mx-auto mb-4"
            >
              <Mail className="w-7 h-7 md:w-8 md:h-8 text-success" />
            </motion.div>
            <h2 className="text-xl md:text-2xl font-bold text-text-primary mb-2">Check Your Email</h2>
            <p className="text-text-secondary mb-2">
              We've sent a magic link to
            </p>
            <p className="font-medium text-text-primary mb-6">{email}</p>
            <p className="text-sm text-text-muted mb-6">
              Click the link in your email to sign in. The link will expire in 15 minutes.
            </p>
            <div className="flex flex-col gap-3">
              <Button
                variant="outline"
                onClick={() => {
                  setViewState('request');
                  setEmail('');
                }}
                className="w-full"
              >
                Use a Different Email
              </Button>
              <Link
                to="/login"
                className="text-sm text-accent-cyan hover:text-accent-cyan/80 transition-colors"
              >
                Back to Login
              </Link>
            </div>
          </div>
        </motion.div>
      </div>
    );
  }

  // Request state (default)
  return (
    <div className="min-h-screen bg-surface-base flex items-center justify-center p-4 md:p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <div className="flex items-center justify-center gap-2 md:gap-3 mb-6 md:mb-8">
          <div className="w-10 h-10 md:w-12 md:h-12 rounded-xl bg-gradient-to-br from-accent-cyan to-accent-purple flex items-center justify-center">
            <Layers className="w-6 h-6 md:w-7 md:h-7 text-white" />
          </div>
          <span className="text-xl md:text-2xl font-bold text-text-primary tracking-tight">
            GetAnswers
          </span>
        </div>

        {/* Main Card */}
        <div className="bg-surface-card border border-surface-border rounded-2xl p-6 md:p-8">
          <div className="text-center mb-6 md:mb-8">
            <div className="w-12 h-12 md:w-14 md:h-14 rounded-full bg-accent-purple/20 flex items-center justify-center mx-auto mb-4">
              <Sparkles className="w-6 h-6 md:w-7 md:h-7 text-accent-purple" />
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-text-primary mb-2">
              Magic Link Login
            </h1>
            <p className="text-sm md:text-base text-text-secondary">
              Enter your email and we'll send you a secure link to sign in
            </p>
          </div>

          {/* Error Message */}
          {errorMessage && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 p-4 bg-critical-muted border border-critical-border rounded-lg"
            >
              <p className="text-sm text-critical">{errorMessage}</p>
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <Input
              label="Email Address"
              type="email"
              placeholder="you@company.com"
              value={email}
              onChange={handleEmailChange}
              error={validationError}
              disabled={isLoading}
              autoComplete="email"
              autoFocus
            />

            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={isLoading}
              className="w-full"
              icon={<Sparkles className="w-4 h-4" />}
            >
              Send Magic Link
            </Button>
          </form>

          {/* Benefits */}
          <div className="mt-6 p-4 bg-surface-hover rounded-lg border border-surface-border">
            <p className="text-xs font-medium text-text-secondary mb-2">Why use a magic link?</p>
            <ul className="space-y-1.5 text-xs text-text-muted">
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-3 h-3 text-success flex-shrink-0" />
                No password to remember
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-3 h-3 text-success flex-shrink-0" />
                More secure than passwords
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-3 h-3 text-success flex-shrink-0" />
                Works from any device
              </li>
            </ul>
          </div>

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-text-muted">
              Prefer to use a password?{' '}
              <Link
                to="/login"
                className="text-accent-cyan hover:text-accent-cyan/80 font-medium transition-colors"
              >
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
