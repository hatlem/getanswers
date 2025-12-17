import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Link, useSearchParams } from 'react-router-dom';
import {
  CreditCard,
  Check,
  Crown,
  Zap,
  Building2,
  ArrowLeft,
  ExternalLink,
  Loader2,
  AlertCircle,
  Sparkles,
  CheckCircle2,
} from 'lucide-react';
import { billingApi, type SubscriptionInfo } from '../../lib/api';
import { Button } from '../ui/Button';
import { cn } from '../../lib/utils';

// Plan info for display only - actual plan changes happen in Stripe Portal
const planInfo: Record<string, { name: string; icon: React.ReactNode; color: string }> = {
  free: { name: 'Free', icon: <Zap className="w-5 h-5" />, color: 'text-text-secondary' },
  starter: { name: 'Starter', icon: <Crown className="w-5 h-5" />, color: 'text-warning' },
  pro: { name: 'Pro', icon: <Sparkles className="w-5 h-5" />, color: 'text-accent-cyan' },
  enterprise: { name: 'Enterprise', icon: <Building2 className="w-5 h-5" />, color: 'text-accent-purple' },
};

// Price IDs for initial checkout (upgrades from free happen via Stripe Portal after first sub)
const priceIds: Record<string, string> = {
  starter: 'price_1Sf5GfEa0arIvkZgrqkuw3JC',
  pro: 'price_1Sf5GgEa0arIvkZgrurYHlZ5',
  enterprise: 'price_1Sf5GgEa0arIvkZg50suMbMP',
};

export function BillingPage() {
  const [searchParams] = useSearchParams();
  const [checkoutLoading, setCheckoutLoading] = useState<string | null>(null);
  const success = searchParams.get('success') === 'true';
  const canceled = searchParams.get('canceled') === 'true';

  const { data: subscription, isLoading, refetch } = useQuery({
    queryKey: ['subscription'],
    queryFn: billingApi.getSubscription,
  });

  // For users on free plan who want to subscribe
  const checkoutMutation = useMutation({
    mutationFn: async (priceId: string) => {
      const baseUrl = window.location.origin;
      return billingApi.createCheckout(
        priceId,
        `${baseUrl}/billing?success=true`,
        `${baseUrl}/billing?canceled=true`
      );
    },
    onSuccess: (data) => {
      window.location.href = data.checkout_url;
    },
    onError: (error) => {
      console.error('Checkout error:', error);
      setCheckoutLoading(null);
    },
  });

  // For existing subscribers - opens Stripe Portal for all billing management
  const portalMutation = useMutation({
    mutationFn: async () => {
      const returnUrl = window.location.href.split('?')[0]; // Remove query params
      return billingApi.createPortal(returnUrl);
    },
    onSuccess: (data) => {
      window.location.href = data.portal_url;
    },
  });

  const handleSubscribe = (planId: string) => {
    const priceId = priceIds[planId];
    if (!priceId) return;
    if (planId === 'enterprise') {
      window.location.href = 'mailto:sales@getanswers.co?subject=Enterprise%20Plan%20Inquiry';
      return;
    }
    setCheckoutLoading(planId);
    checkoutMutation.mutate(priceId);
  };

  const handleManageBilling = () => {
    portalMutation.mutate();
  };

  const currentPlan = subscription?.plan || 'free';
  const isActive = subscription?.is_active ?? true;
  const hasPaidPlan = currentPlan !== 'free';
  const plan = planInfo[currentPlan] || planInfo.free;

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return null;
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-surface-base flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-accent-cyan mx-auto mb-4" />
          <p className="text-text-secondary">Loading billing information...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-surface-base">
      <div className="max-w-3xl mx-auto px-4 py-6 md:p-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 md:mb-8"
        >
          <Link
            to="/dashboard"
            className="inline-flex items-center gap-2 text-sm md:text-base text-text-secondary hover:text-text-primary transition-colors mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
          <h1 className="text-2xl md:text-3xl font-bold text-text-primary mb-2">Billing & Subscription</h1>
          <p className="text-sm md:text-base text-text-secondary">
            Manage your subscription and billing preferences
          </p>
        </motion.div>

        {/* Success/Cancel Messages */}
        {success && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-success/10 border border-success/30 rounded-lg p-4 mb-6 flex items-center gap-3"
          >
            <CheckCircle2 className="w-5 h-5 text-success" />
            <span className="text-sm text-success">
              Payment successful! Your subscription is now active.
            </span>
          </motion.div>
        )}

        {canceled && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-warning/10 border border-warning/30 rounded-lg p-4 mb-6 flex items-center gap-3"
          >
            <AlertCircle className="w-5 h-5 text-warning" />
            <span className="text-sm text-warning">
              Checkout was canceled. No charges were made.
            </span>
          </motion.div>
        )}

        {/* Stripe Mode Indicator (for testing) */}
        {subscription?.stripe_mode === 'test' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-warning/10 border border-warning/30 rounded-lg p-4 mb-6 flex items-center gap-3"
          >
            <AlertCircle className="w-5 h-5 text-warning" />
            <span className="text-sm text-warning">
              Stripe is in <strong>test mode</strong>. Use test card 4242 4242 4242 4242 for testing.
            </span>
          </motion.div>
        )}

        {/* Current Plan Status */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-surface-card border border-surface-border rounded-xl p-4 md:p-6 mb-4 md:mb-6"
        >
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3 md:gap-4">
              <div className={cn(
                'w-12 h-12 md:w-14 md:h-14 rounded-xl flex items-center justify-center shrink-0',
                hasPaidPlan ? 'bg-accent-cyan/20' : 'bg-surface-border'
              )}>
                <span className={plan.color}>{plan.icon}</span>
              </div>
              <div>
                <h2 className="text-lg md:text-xl font-semibold text-text-primary mb-1">
                  {plan.name} Plan
                </h2>
                <div className="flex flex-wrap items-center gap-2 md:gap-3">
                  <span className={cn(
                    'px-2 py-0.5 rounded-full text-xs font-medium',
                    isActive ? 'bg-success/20 text-success' : 'bg-warning/20 text-warning'
                  )}>
                    {subscription?.status || 'active'}
                  </span>
                  {subscription?.cancel_at_period_end && (
                    <span className="text-xs md:text-sm text-warning">
                      Cancels at period end
                    </span>
                  )}
                </div>
                {subscription?.current_period_end && (
                  <p className="text-xs md:text-sm text-text-muted mt-2">
                    {subscription.cancel_at_period_end ? 'Access until' : 'Next billing date'}:{' '}
                    {formatDate(subscription.current_period_end)}
                  </p>
                )}
              </div>
            </div>
          </div>
        </motion.section>

        {/* Actions Section */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-surface-card border border-surface-border rounded-xl p-4 md:p-6 mb-4 md:mb-6"
        >
          {hasPaidPlan ? (
            <>
              <h3 className="text-base md:text-lg font-semibold text-text-primary mb-3 md:mb-4">Manage Subscription</h3>
              <p className="text-sm md:text-base text-text-secondary mb-4">
                Use the Stripe billing portal to update your plan, change payment methods, view invoices, or cancel your subscription.
              </p>
              <Button
                variant="primary"
                onClick={handleManageBilling}
                disabled={portalMutation.isPending}
                className="w-full sm:w-auto"
              >
                {portalMutation.isPending ? (
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                ) : (
                  <ExternalLink className="w-4 h-4 mr-2" />
                )}
                Open Billing Portal
              </Button>
              <p className="text-xs text-text-muted mt-3">
                In the portal you can: upgrade/downgrade plans, update payment method, view invoices, cancel subscription
              </p>
            </>
          ) : (
            <>
              <h3 className="text-base md:text-lg font-semibold text-text-primary mb-3 md:mb-4">Upgrade to Get More</h3>
              <p className="text-sm md:text-base text-text-secondary mb-4 md:mb-6">
                Unlock more emails, AI responses, and advanced features with a paid plan.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-4">
                {/* Starter Plan */}
                <div className="border border-surface-border rounded-lg p-4 hover:border-warning/50 transition-colors">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 rounded-lg bg-warning/20 flex items-center justify-center">
                      <Crown className="w-5 h-5 text-warning" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-text-primary">Starter</h4>
                      <p className="text-lg font-bold text-text-primary">$29<span className="text-sm font-normal text-text-muted">/mo</span></p>
                    </div>
                  </div>
                  <ul className="space-y-1 mb-4 text-sm text-text-secondary">
                    <li className="flex items-center gap-2"><Check className="w-3.5 h-3.5 text-success" /> 500 emails/month</li>
                    <li className="flex items-center gap-2"><Check className="w-3.5 h-3.5 text-success" /> 200 AI responses</li>
                    <li className="flex items-center gap-2"><Check className="w-3.5 h-3.5 text-success" /> Email scheduling</li>
                  </ul>
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => handleSubscribe('starter')}
                    disabled={checkoutLoading === 'starter'}
                  >
                    {checkoutLoading === 'starter' ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      'Get Started'
                    )}
                  </Button>
                </div>

                {/* Pro Plan */}
                <div className="border border-accent-cyan rounded-lg p-4 bg-accent-cyan/5 relative">
                  <div className="absolute -top-2.5 left-4 px-2 py-0.5 bg-accent-cyan text-white text-xs font-semibold rounded">
                    Popular
                  </div>
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 rounded-lg bg-accent-cyan/20 flex items-center justify-center">
                      <Sparkles className="w-5 h-5 text-accent-cyan" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-text-primary">Pro</h4>
                      <p className="text-lg font-bold text-text-primary">$79<span className="text-sm font-normal text-text-muted">/mo</span></p>
                    </div>
                  </div>
                  <ul className="space-y-1 mb-4 text-sm text-text-secondary">
                    <li className="flex items-center gap-2"><Check className="w-3.5 h-3.5 text-success" /> 5,000 emails/month</li>
                    <li className="flex items-center gap-2"><Check className="w-3.5 h-3.5 text-success" /> 2,000 AI responses</li>
                    <li className="flex items-center gap-2"><Check className="w-3.5 h-3.5 text-success" /> API access + tracking</li>
                  </ul>
                  <Button
                    variant="primary"
                    className="w-full"
                    onClick={() => handleSubscribe('pro')}
                    disabled={checkoutLoading === 'pro'}
                  >
                    {checkoutLoading === 'pro' ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      'Get Pro'
                    )}
                  </Button>
                </div>
              </div>

              <p className="text-sm text-text-muted mt-4 text-center">
                Need more? <a href="mailto:sales@getanswers.co" className="text-accent-cyan hover:underline">Contact us</a> for Enterprise pricing.
              </p>
            </>
          )}
        </motion.section>

        {/* Features by Plan (condensed) */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-surface-card border border-surface-border rounded-xl p-4 md:p-6"
        >
          <h3 className="text-base md:text-lg font-semibold text-text-primary mb-4">What's Included</h3>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-xs md:text-sm">
            <div>
              <h4 className="font-medium text-text-muted mb-2">Free</h4>
              <ul className="space-y-1 text-text-secondary">
                <li>50 emails/mo</li>
                <li>20 AI responses</li>
                <li>3 policies</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-warning mb-2">Starter</h4>
              <ul className="space-y-1 text-text-secondary">
                <li>500 emails/mo</li>
                <li>200 AI responses</li>
                <li>10 policies</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-accent-cyan mb-2">Pro</h4>
              <ul className="space-y-1 text-text-secondary">
                <li>5,000 emails/mo</li>
                <li>2,000 AI responses</li>
                <li>Unlimited policies</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-accent-purple mb-2">Enterprise</h4>
              <ul className="space-y-1 text-text-secondary">
                <li>Unlimited</li>
                <li>Dedicated support</li>
                <li>Custom SLA</li>
              </ul>
            </div>
          </div>
        </motion.section>
      </div>
    </div>
  );
}
