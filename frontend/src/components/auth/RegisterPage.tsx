import { useState } from 'react';
import { motion } from 'framer-motion';
import { User, Mail, Lock, ArrowRight, Layers, CheckCircle2 } from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { Link, useNavigate } from 'react-router-dom';
import { apiClient } from '../../lib/api-client';

export function RegisterPage() {
  const navigate = useNavigate();
  const { register, isLoading, error, clearError } = useAuthStore();

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);

  const handleGoogleSignUp = async () => {
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

  const validateForm = () => {
    const errors: Record<string, string> = {};

    if (!formData.name.trim()) {
      errors.name = 'Name is required';
    } else if (formData.name.trim().length < 2) {
      errors.name = 'Name must be at least 2 characters';
    }

    if (!formData.email) {
      errors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'Please enter a valid email';
    }

    if (!formData.password) {
      errors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      errors.password = 'Password must be at least 8 characters';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      errors.password = 'Password must contain uppercase, lowercase, and a number';
    }

    if (!formData.confirmPassword) {
      errors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
    }

    if (!acceptedTerms) {
      errors.terms = 'You must accept the terms and conditions';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();

    if (!validateForm()) return;

    try {
      await register(formData.name, formData.email, formData.password);
      navigate('/dashboard');
    } catch (err) {
      // Error is handled by the store
    }
  };

  const handleChange = (field: keyof typeof formData) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [field]: e.target.value });
    if (validationErrors[field]) {
      setValidationErrors({ ...validationErrors, [field]: '' });
    }
  };

  const passwordStrength = () => {
    const password = formData.password;
    if (!password) return { strength: 0, label: '', color: '' };

    let strength = 0;
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    if (/(?=.*[a-z])(?=.*[A-Z])/.test(password)) strength++;
    if (/(?=.*\d)/.test(password)) strength++;
    if (/(?=.*[!@#$%^&*])/.test(password)) strength++;

    if (strength <= 2) return { strength, label: 'Weak', color: 'bg-critical' };
    if (strength <= 3) return { strength, label: 'Fair', color: 'bg-warning' };
    if (strength <= 4) return { strength, label: 'Good', color: 'bg-info' };
    return { strength, label: 'Strong', color: 'bg-success' };
  };

  const strength = passwordStrength();

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
              Create Account
            </h1>
            <p className="text-text-secondary">
              Start managing your emails with AI
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
              label="Full Name"
              type="text"
              placeholder="John Doe"
              value={formData.name}
              onChange={handleChange('name')}
              error={validationErrors.name}
              disabled={isLoading}
              autoComplete="name"
            />

            <Input
              label="Email"
              type="email"
              placeholder="you@company.com"
              value={formData.email}
              onChange={handleChange('email')}
              error={validationErrors.email}
              disabled={isLoading}
              autoComplete="email"
            />

            <div>
              <Input
                label="Password"
                type="password"
                placeholder="Create a strong password"
                value={formData.password}
                onChange={handleChange('password')}
                error={validationErrors.password}
                disabled={isLoading}
                autoComplete="new-password"
              />
              {formData.password && !validationErrors.password && (
                <div className="mt-2">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-text-muted">Password strength</span>
                    <span className={`text-xs font-medium ${strength.color.replace('bg-', 'text-')}`}>
                      {strength.label}
                    </span>
                  </div>
                  <div className="flex gap-1 h-1">
                    {[...Array(5)].map((_, i) => (
                      <div
                        key={i}
                        className={`flex-1 rounded-full transition-colors ${
                          i < strength.strength ? strength.color : 'bg-surface-border'
                        }`}
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>

            <Input
              label="Confirm Password"
              type="password"
              placeholder="Re-enter your password"
              value={formData.confirmPassword}
              onChange={handleChange('confirmPassword')}
              error={validationErrors.confirmPassword}
              disabled={isLoading}
              autoComplete="new-password"
            />

            {/* Terms Checkbox */}
            <div className="flex items-start gap-3">
              <button
                type="button"
                onClick={() => {
                  setAcceptedTerms(!acceptedTerms);
                  if (validationErrors.terms) {
                    setValidationErrors({ ...validationErrors, terms: '' });
                  }
                }}
                className={`mt-0.5 w-5 h-5 rounded border-2 flex items-center justify-center transition-all ${
                  acceptedTerms
                    ? 'bg-accent-cyan border-accent-cyan'
                    : validationErrors.terms
                    ? 'border-critical'
                    : 'border-surface-border'
                }`}
                disabled={isLoading}
              >
                {acceptedTerms && <CheckCircle2 className="w-3.5 h-3.5 text-white" strokeWidth={3} />}
              </button>
              <label className="text-sm text-text-muted">
                I agree to the{' '}
                <a href="#" className="text-accent-cyan hover:text-accent-cyan/80 transition-colors">
                  Terms of Service
                </a>{' '}
                and{' '}
                <a href="#" className="text-accent-cyan hover:text-accent-cyan/80 transition-colors">
                  Privacy Policy
                </a>
              </label>
            </div>
            {validationErrors.terms && (
              <p className="text-xs text-critical -mt-3">{validationErrors.terms}</p>
            )}

            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={isLoading}
              className="w-full"
              icon={<ArrowRight className="w-4 h-4" />}
              disabled={isGoogleLoading}
            >
              Create Account
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

          {/* Google Sign Up */}
          <Button
            type="button"
            variant="outline"
            className="w-full flex items-center justify-center gap-3"
            onClick={handleGoogleSignUp}
            disabled={isLoading || isGoogleLoading}
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

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-text-muted">
              Already have an account?{' '}
              <Link
                to="/login"
                className="text-accent-cyan hover:text-accent-cyan/80 font-medium transition-colors"
              >
                Sign in
              </Link>
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center">
          <p className="text-xs text-text-muted mb-4">
            Your data is encrypted and secure
          </p>
          <div className="flex items-center justify-center gap-2 text-xs text-text-muted">
            <Lock className="w-3 h-3" />
            <span>256-bit SSL encryption</span>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
