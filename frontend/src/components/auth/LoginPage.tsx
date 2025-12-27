import { useState } from 'react';
import { motion } from 'framer-motion';
import { Mail, Lock, ArrowRight, Layers, Sparkles } from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Link, useNavigate } from 'react-router-dom';
import { apiClient } from '../../lib/api';

export function LoginPage() {
  const navigate = useNavigate();
  const { login, requestMagicLink, isLoading, error, clearError } = useAuthStore();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showMagicLink, setShowMagicLink] = useState(false);
  const [magicLinkSent, setMagicLinkSent] = useState(false);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const [isMicrosoftLoading, setIsMicrosoftLoading] = useState(false);

  const handleGoogleSignIn = async () => {
    setIsGoogleLoading(true);
    clearError();
    try {
      const response = await apiClient.get<{ url: string }>('/api/auth/google');
      // Redirect to Google OAuth
      window.location.href = response.url;
    } catch (err) {
      console.error('Failed to get Google auth URL:', err);
      setIsGoogleLoading(false);
    }
  };

  const handleMicrosoftSignIn = async () => {
    setIsMicrosoftLoading(true);
    clearError();
    try {
      const response = await apiClient.get<{ url: string }>('/api/auth/microsoft');
      // Redirect to Microsoft OAuth
      window.location.href = response.url;
    } catch (err) {
      console.error('Failed to get Microsoft auth URL:', err);
      setIsMicrosoftLoading(false);
    }
  };

  const validateForm = () => {
    const errors: Record<string, string> = {};

    if (!email) {
      errors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errors.email = 'Please enter a valid email';
    }

    if (!showMagicLink && !password) {
      errors.password = 'Password is required';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();

    if (!validateForm()) return;

    try {
      if (showMagicLink) {
        await requestMagicLink(email);
        setMagicLinkSent(true);
      } else {
        await login(email, password);
        navigate('/dashboard');
      }
    } catch (err) {
      // Error is handled by the store
    }
  };

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
    if (validationErrors.email) {
      setValidationErrors({ ...validationErrors, email: '' });
    }
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPassword(e.target.value);
    if (validationErrors.password) {
      setValidationErrors({ ...validationErrors, password: '' });
    }
  };

  if (magicLinkSent) {
    return (
      <div className="min-h-screen bg-surface-base flex items-center justify-center p-4 md:p-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-md"
        >
          <div className="bg-surface-card border border-surface-border rounded-2xl p-6 md:p-8 text-center">
            <div className="w-14 h-14 md:w-16 md:h-16 rounded-full bg-success/20 flex items-center justify-center mx-auto mb-4">
              <Mail className="w-7 h-7 md:w-8 md:h-8 text-success" />
            </div>
            <h2 className="text-xl md:text-2xl font-bold text-text-primary mb-2">Check Your Email</h2>
            <p className="text-text-secondary mb-6">
              We've sent a magic link to <span className="font-medium text-text-primary">{email}</span>.
              Click the link to sign in.
            </p>
            <Button
              variant="outline"
              onClick={() => {
                setMagicLinkSent(false);
                setShowMagicLink(false);
              }}
              className="w-full"
            >
              Back to Login
            </Button>
          </div>
        </motion.div>
      </div>
    );
  }

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
            <h1 className="text-2xl md:text-3xl font-bold text-text-primary mb-2">
              {showMagicLink ? 'Magic Link Login' : 'Welcome Back'}
            </h1>
            <p className="text-sm md:text-base text-text-secondary">
              {showMagicLink
                ? 'Enter your email to receive a magic link'
                : 'Sign in to access your AI mission control'}
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 p-4 bg-critical-muted border border-critical-border rounded-lg"
            >
              <p className="text-sm text-critical">{error}</p>
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <Input
              label="Email"
              type="email"
              placeholder="you@company.com"
              value={email}
              onChange={handleEmailChange}
              error={validationErrors.email}
              disabled={isLoading}
              autoComplete="email"
            />

            {!showMagicLink && (
              <Input
                label="Password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={handlePasswordChange}
                error={validationErrors.password}
                disabled={isLoading}
                autoComplete="current-password"
              />
            )}

            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={isLoading}
              className="w-full"
              icon={showMagicLink ? <Sparkles className="w-4 h-4" /> : <ArrowRight className="w-4 h-4" />}
            >
              {showMagicLink ? 'Send Magic Link' : 'Sign In'}
            </Button>
          </form>

          {/* Divider */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-surface-border" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-surface-card px-2 text-text-muted">Or</span>
            </div>
          </div>

          {/* Google Sign In */}
          <Button
            type="button"
            variant="outline"
            className="w-full flex items-center justify-center gap-3"
            onClick={handleGoogleSignIn}
            disabled={isLoading || isGoogleLoading || isMicrosoftLoading}
          >
            {isGoogleLoading ? (
              <div className="w-5 h-5 border-2 border-text-muted border-t-transparent rounded-full animate-spin" />
            ) : (
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
            )}
            Continue with Google
          </Button>

          {/* Microsoft Sign In */}
          <Button
            type="button"
            variant="outline"
            className="w-full flex items-center justify-center gap-3 mt-3"
            onClick={handleMicrosoftSignIn}
            disabled={isLoading || isGoogleLoading || isMicrosoftLoading}
          >
            {isMicrosoftLoading ? (
              <div className="w-5 h-5 border-2 border-text-muted border-t-transparent rounded-full animate-spin" />
            ) : (
              <svg className="w-5 h-5" viewBox="0 0 23 23">
                <path fill="#f25022" d="M0 0h11v11H0z"/>
                <path fill="#00a4ef" d="M0 12h11v11H0z"/>
                <path fill="#7fba00" d="M12 0h11v11H12z"/>
                <path fill="#ffb900" d="M12 12h11v11H12z"/>
              </svg>
            )}
            Continue with Microsoft
          </Button>

          {/* Toggle Magic Link */}
          <Button
            type="button"
            variant="ghost"
            className="w-full"
            onClick={() => {
              setShowMagicLink(!showMagicLink);
              setValidationErrors({});
              clearError();
            }}
            disabled={isLoading || isGoogleLoading || isMicrosoftLoading}
          >
            {showMagicLink ? (
              <>
                <Lock className="w-4 h-4" />
                Sign in with password
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Request Magic Link
              </>
            )}
          </Button>

          {/* Register Link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-text-muted">
              Don't have an account?{' '}
              <Link
                to="/register"
                className="text-accent-cyan hover:text-accent-cyan/80 font-medium transition-colors"
              >
                Create one
              </Link>
            </p>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-xs text-text-muted mt-6">
          By signing in, you agree to our Terms of Service and Privacy Policy
        </p>
      </motion.div>
    </div>
  );
}
