import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Mail, ArrowRight, CheckCircle2, Loader2 } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { useAuthStore } from '../stores/authStore';

export default function OnboardingPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);

  const emailFromUrl = searchParams.get('email');

  // Store email in sessionStorage for later use
  useEffect(() => {
    if (emailFromUrl) {
      sessionStorage.setItem('signup_email', emailFromUrl);
    }
  }, [emailFromUrl]);

  // If already logged in, redirect to dashboard
  useEffect(() => {
    if (user) {
      navigate('/');
    }
  }, [user, navigate]);

  const handleGetStarted = () => {
    setIsLoading(true);
    const params = new URLSearchParams();
    if (emailFromUrl) {
      params.set('email', emailFromUrl);
    }
    navigate(`/register?${params.toString()}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
          <div className="text-center space-y-6">
            {/* Icon */}
            <div className="mx-auto w-16 h-16 rounded-2xl bg-blue-100 flex items-center justify-center">
              <Mail className="w-8 h-8 text-blue-600" />
            </div>

            {/* Welcome text */}
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Welcome to GetAnswers</h1>
              <p className="mt-3 text-gray-600">
                {emailFromUrl
                  ? 'Complete your signup to access your resources'
                  : 'AI-powered email assistant that saves you hours'
                }
              </p>
            </div>

            {/* Email confirmation */}
            {emailFromUrl && (
              <div className="bg-blue-50 rounded-xl p-4 flex items-center gap-3">
                <CheckCircle2 className="w-6 h-6 text-blue-600 flex-shrink-0" />
                <div className="text-sm text-left">
                  <p className="font-medium text-gray-900">Account prepared for:</p>
                  <p className="text-gray-600">{emailFromUrl}</p>
                </div>
              </div>
            )}

            {/* CTA */}
            <div className="space-y-4">
              <Button
                onClick={handleGetStarted}
                disabled={isLoading}
                className="w-full h-12 flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <>
                    Get Started
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </Button>

              <button
                onClick={() => navigate('/login')}
                className="w-full py-3 text-gray-600 hover:text-gray-900 text-sm"
              >
                Already have an account? Sign in
              </button>
            </div>

            {/* Terms */}
            <p className="text-xs text-gray-500">
              By continuing, you agree to our{' '}
              <a href="/terms" className="text-blue-600 hover:underline">
                Terms
              </a>{' '}
              and{' '}
              <a href="/privacy" className="text-blue-600 hover:underline">
                Privacy Policy
              </a>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
