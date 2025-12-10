import { useState } from 'react';
import { motion } from 'framer-motion';
import { Mail, Lock, ArrowRight, Layers, Sparkles } from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { Link, useNavigate } from 'react-router-dom';

export function LoginPage() {
  const navigate = useNavigate();
  const { login, requestMagicLink, isLoading, error, clearError } = useAuthStore();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showMagicLink, setShowMagicLink] = useState(false);
  const [magicLinkSent, setMagicLinkSent] = useState(false);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

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
        navigate('/');
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
      <div className="min-h-screen bg-surface-base flex items-center justify-center p-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-md"
        >
          <div className="bg-surface-card border border-surface-border rounded-2xl p-8 text-center">
            <div className="w-16 h-16 rounded-full bg-success/20 flex items-center justify-center mx-auto mb-4">
              <Mail className="w-8 h-8 text-success" />
            </div>
            <h2 className="text-2xl font-bold text-text-primary mb-2">Check Your Email</h2>
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
    <div className="min-h-screen bg-surface-base flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <div className="flex items-center justify-center gap-3 mb-8">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-cyan to-accent-purple flex items-center justify-center">
            <Layers className="w-7 h-7 text-white" />
          </div>
          <span className="text-2xl font-bold text-text-primary tracking-tight">
            GetAnswers
          </span>
        </div>

        {/* Main Card */}
        <div className="bg-surface-card border border-surface-border rounded-2xl p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-text-primary mb-2">
              {showMagicLink ? 'Magic Link Login' : 'Welcome Back'}
            </h1>
            <p className="text-text-secondary">
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
            disabled={isLoading}
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
