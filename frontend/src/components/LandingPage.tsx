import { motion, useScroll, useTransform } from 'framer-motion';
import { useRef, useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import {
  Layers,
  Zap,
  Shield,
  Clock,
  CheckCircle2,
  ArrowRight,
  Sparkles,
  Mail,
  Brain,
  Target,
  ChevronDown,
  Loader2,
} from 'lucide-react';

// Animated gradient orb background
function GradientOrbs() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      <motion.div
        className="absolute -top-1/4 -right-1/4 w-[800px] h-[800px] rounded-full opacity-30"
        style={{
          background: 'radial-gradient(circle, rgba(6, 182, 212, 0.4) 0%, transparent 70%)',
        }}
        animate={{
          scale: [1, 1.2, 1],
          x: [0, 50, 0],
          y: [0, 30, 0],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />
      <motion.div
        className="absolute -bottom-1/4 -left-1/4 w-[600px] h-[600px] rounded-full opacity-25"
        style={{
          background: 'radial-gradient(circle, rgba(139, 92, 246, 0.5) 0%, transparent 70%)',
        }}
        animate={{
          scale: [1, 1.3, 1],
          x: [0, -30, 0],
          y: [0, -50, 0],
        }}
        transition={{
          duration: 25,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />
      <motion.div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1000px] h-[1000px] rounded-full opacity-10"
        style={{
          background: 'radial-gradient(circle, rgba(6, 182, 212, 0.3) 0%, transparent 50%)',
        }}
        animate={{
          rotate: [0, 360],
        }}
        transition={{
          duration: 60,
          repeat: Infinity,
          ease: 'linear',
        }}
      />
    </div>
  );
}

// Animated grid pattern
function GridPattern() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-[0.03]">
      <div
        className="absolute inset-0"
        style={{
          backgroundImage: `
            linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)
          `,
          backgroundSize: '100px 100px',
        }}
      />
    </div>
  );
}

// Floating particles
function Particles() {
  const particles = Array.from({ length: 20 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: Math.random() * 4 + 2,
    duration: Math.random() * 10 + 15,
    delay: Math.random() * 5,
  }));

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {particles.map((p) => (
        <motion.div
          key={p.id}
          className="absolute rounded-full bg-accent-cyan/30"
          style={{
            left: `${p.x}%`,
            top: `${p.y}%`,
            width: p.size,
            height: p.size,
          }}
          animate={{
            y: [0, -100, 0],
            opacity: [0, 1, 0],
          }}
          transition={{
            duration: p.duration,
            repeat: Infinity,
            delay: p.delay,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  );
}

// Feature card component
function FeatureCard({
  icon: Icon,
  title,
  description,
  index,
}: {
  icon: React.ElementType;
  title: string;
  description: string;
  index: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-100px' }}
      transition={{ duration: 0.6, delay: index * 0.1 }}
      className="group relative"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-accent-cyan/10 to-accent-purple/10 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
      <div className="relative p-8 rounded-2xl border border-surface-border bg-surface-card/50 backdrop-blur-sm hover:border-accent-cyan/30 transition-all duration-300">
        <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-accent-cyan/20 to-accent-purple/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
          <Icon className="w-7 h-7 text-accent-cyan" />
        </div>
        <h3 className="text-xl font-bold text-text-primary mb-3">{title}</h3>
        <p className="text-text-secondary leading-relaxed">{description}</p>
      </div>
    </motion.div>
  );
}

// Stat display
function StatDisplay({
  value,
  label,
  suffix = '',
  index,
}: {
  value: string;
  label: string;
  suffix?: string;
  index: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      whileInView={{ opacity: 1, scale: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      className="text-center"
    >
      <div className="flex items-baseline justify-center gap-1 mb-2">
        <span className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-accent-cyan to-accent-purple bg-clip-text text-transparent font-mono">
          {value}
        </span>
        <span className="text-2xl md:text-3xl font-bold text-accent-cyan">{suffix}</span>
      </div>
      <p className="text-text-secondary text-sm uppercase tracking-wider font-medium">{label}</p>
    </motion.div>
  );
}

// Mock dashboard preview
function DashboardPreview() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 60 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-100px' }}
      transition={{ duration: 0.8 }}
      className="relative"
    >
      {/* Glow effect */}
      <div className="absolute -inset-4 bg-gradient-to-r from-accent-cyan/20 via-accent-purple/20 to-accent-cyan/20 rounded-3xl blur-2xl opacity-50" />

      {/* Browser frame */}
      <div className="relative rounded-2xl border border-surface-border bg-surface-elevated overflow-hidden shadow-2xl">
        {/* Browser header */}
        <div className="flex items-center gap-2 px-4 py-3 border-b border-surface-border bg-surface-card">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-critical/60" />
            <div className="w-3 h-3 rounded-full bg-warning/60" />
            <div className="w-3 h-3 rounded-full bg-success/60" />
          </div>
          <div className="flex-1 mx-4">
            <div className="mx-auto max-w-md h-7 rounded-lg bg-surface-base border border-surface-border flex items-center justify-center">
              <span className="text-xs text-text-muted font-mono">getanswers.co/dashboard</span>
            </div>
          </div>
        </div>

        {/* Dashboard content mock */}
        <div className="p-6 bg-surface-base min-h-[400px]">
          {/* Top nav mock */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-cyan to-accent-purple" />
              <div className="w-24 h-4 rounded bg-surface-border" />
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface-card border border-surface-border">
              <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
              <span className="text-xs text-success font-mono">All Clear</span>
            </div>
          </div>

          {/* Three column layout mock */}
          <div className="flex gap-4">
            {/* Left column */}
            <div className="w-56 space-y-3">
              <div className="h-4 w-20 rounded bg-surface-border mb-4" />
              {[
                { color: 'bg-critical', label: 'Needs Decision', count: '3' },
                { color: 'bg-warning', label: 'Waiting', count: '7' },
                { color: 'bg-success', label: 'Handled by AI', count: '142' },
              ].map((item, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.3 + i * 0.1 }}
                  className="flex items-center gap-3 p-2.5 rounded-lg bg-surface-card border border-surface-border"
                >
                  <div className={`w-2 h-2 rounded-full ${item.color}`} />
                  <span className="text-xs text-text-secondary flex-1">{item.label}</span>
                  <span className="text-xs font-mono text-text-primary">{item.count}</span>
                </motion.div>
              ))}

              {/* Efficiency stat */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.6 }}
                className="mt-6 p-4 rounded-xl bg-surface-card border border-surface-border"
              >
                <div className="text-[10px] uppercase tracking-wider text-text-muted mb-2">Today's Efficiency</div>
                <div className="text-2xl font-bold text-success font-mono">94%</div>
                <div className="text-xs text-text-secondary mb-2">Handled autonomously</div>
                <div className="h-1.5 rounded-full bg-surface-border overflow-hidden">
                  <motion.div
                    className="h-full rounded-full bg-gradient-to-r from-success to-accent-cyan"
                    initial={{ width: 0 }}
                    whileInView={{ width: '94%' }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.8, duration: 1 }}
                  />
                </div>
              </motion.div>
            </div>

            {/* Center column - cards */}
            <div className="flex-1 space-y-3">
              <div className="h-4 w-32 rounded bg-surface-border mb-4" />
              {[1, 2, 3].map((_, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.4 + i * 0.1 }}
                  className="p-4 rounded-xl bg-surface-card border border-surface-border"
                >
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-info to-accent-purple" />
                    <div className="flex-1">
                      <div className="h-3 w-32 rounded bg-surface-border mb-2" />
                      <div className="h-2 w-full rounded bg-surface-border mb-1" />
                      <div className="h-2 w-2/3 rounded bg-surface-border" />
                    </div>
                  </div>
                  <div className="flex gap-2 mt-4">
                    <div className="h-7 w-20 rounded-lg bg-success/20 border border-success/30" />
                    <div className="h-7 w-16 rounded-lg bg-surface-border" />
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Right column - context */}
            <div className="w-64 space-y-3">
              <div className="h-4 w-24 rounded bg-surface-border mb-4" />
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.5 }}
                className="p-4 rounded-xl bg-surface-card border border-surface-border"
              >
                <div className="h-3 w-20 rounded bg-surface-border mb-3" />
                <div className="space-y-2">
                  <div className="h-2 w-full rounded bg-surface-border" />
                  <div className="h-2 w-full rounded bg-surface-border" />
                  <div className="h-2 w-3/4 rounded bg-surface-border" />
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// Pricing card
function PricingCard({
  name,
  price,
  description,
  features,
  highlighted = false,
  index,
}: {
  name: string;
  price: string;
  description: string;
  features: string[];
  highlighted?: boolean;
  index: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6, delay: index * 0.15 }}
      className={`relative rounded-2xl p-8 ${
        highlighted
          ? 'bg-gradient-to-br from-accent-cyan/10 via-surface-card to-accent-purple/10 border-2 border-accent-cyan/30'
          : 'bg-surface-card border border-surface-border'
      }`}
    >
      {highlighted && (
        <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-gradient-to-r from-accent-cyan to-accent-purple text-xs font-bold uppercase tracking-wider text-white">
          Most Popular
        </div>
      )}

      <h3 className="text-2xl font-bold text-text-primary mb-2">{name}</h3>
      <p className="text-text-secondary mb-6">{description}</p>

      <div className="flex items-baseline gap-1 mb-6">
        <span className="text-4xl font-bold text-text-primary font-mono">{price}</span>
        {price !== 'Custom' && <span className="text-text-muted">/month</span>}
      </div>

      <ul className="space-y-3 mb-8">
        {features.map((feature, i) => (
          <li key={i} className="flex items-center gap-3 text-text-secondary">
            <CheckCircle2 className="w-5 h-5 text-success flex-shrink-0" />
            <span>{feature}</span>
          </li>
        ))}
      </ul>

      <Link
        to="/register"
        className={`block w-full py-3 rounded-lg font-medium text-center transition-all ${
          highlighted
            ? 'bg-gradient-to-r from-accent-cyan to-accent-purple text-white hover:opacity-90'
            : 'bg-surface-hover text-text-primary border border-surface-border hover:border-accent-cyan/30'
        }`}
      >
        Get Started
      </Link>
    </motion.div>
  );
}

export function LandingPage() {
  const heroRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const { register } = useAuthStore();
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const { scrollYProgress } = useScroll({
    target: heroRef,
    offset: ['start start', 'end start'],
  });

  const heroOpacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);
  const heroScale = useTransform(scrollYProgress, [0, 0.5], [1, 0.95]);

  const handleEmailSubmit = async (e: FormEvent) => {
    e.preventDefault();

    const trimmedEmail = email.trim();
    if (!trimmedEmail || !trimmedEmail.includes('@')) {
      setError('Please enter a valid email address');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      // Generate a random password that meets requirements
      const randomPart = Math.random().toString(36).substring(2, 10);
      const randomPassword = `${randomPart}Abc123!@`;

      // Use email prefix as name
      const name = trimmedEmail.split('@')[0].charAt(0).toUpperCase() + trimmedEmail.split('@')[0].slice(1);

      await register(name, trimmedEmail, randomPassword);

      // Redirect to dashboard with onboarding param
      navigate('/dashboard?onboarding=start');
    } catch (err: unknown) {
      const error = err as { message?: string };
      const errorMessage = error?.message || 'Registration failed. Please try again.';

      // Check if user already exists
      if (
        errorMessage.toLowerCase().includes('already') ||
        errorMessage.toLowerCase().includes('exists')
      ) {
        setError('An account with this email already exists. Redirecting to sign in...');
        setTimeout(() => navigate('/login'), 2000);
      } else {
        setError(errorMessage);
      }
      setIsSubmitting(false);
    }
  };

  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Triage',
      description: 'Smart categorization that learns your preferences. Handle routine items automatically while escalating what matters.',
    },
    {
      icon: Shield,
      title: 'Policy-Based Control',
      description: 'Define rules for how different types of messages should be handled. Full transparency into every AI decision.',
    },
    {
      icon: Zap,
      title: 'Instant Actions',
      description: 'One-click approve, override, or escalate. Batch operations for power users. Keyboard shortcuts for everything.',
    },
    {
      icon: Clock,
      title: 'Time Reclaimed',
      description: 'Average users save 2+ hours daily. Focus on strategic work while AI handles the routine.',
    },
    {
      icon: Mail,
      title: 'Email Integration',
      description: 'Connect Gmail, Outlook, and more. Unified inbox for all your communications in one mission control.',
    },
    {
      icon: Target,
      title: 'Objective Tracking',
      description: 'Group related messages by project or goal. See progress at a glance and never lose context.',
    },
  ];

  const pricingPlans = [
    {
      name: 'Starter',
      price: '$29',
      description: 'Perfect for individuals',
      features: [
        'Up to 1,000 messages/month',
        'Basic AI categorization',
        'Email integration',
        'Mobile app access',
      ],
    },
    {
      name: 'Pro',
      price: '$79',
      description: 'For power users',
      features: [
        'Unlimited messages',
        'Advanced AI with learning',
        'Custom policies',
        'Priority support',
        'API access',
      ],
      highlighted: true,
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      description: 'For teams and organizations',
      features: [
        'Everything in Pro',
        'Team collaboration',
        'SSO & advanced security',
        'Dedicated account manager',
        'Custom integrations',
      ],
    },
  ];

  return (
    <div className="min-h-screen bg-surface-base text-text-primary overflow-x-hidden">
      {/* Navigation */}
      <motion.nav
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="fixed top-0 left-0 right-0 z-50 px-6 py-4"
      >
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-cyan to-accent-purple flex items-center justify-center">
              <Layers className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight">GetAnswers</span>
          </div>

          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-text-secondary hover:text-text-primary transition-colors">Features</a>
            <a href="#how-it-works" className="text-text-secondary hover:text-text-primary transition-colors">How it Works</a>
            <a href="#pricing" className="text-text-secondary hover:text-text-primary transition-colors">Pricing</a>
          </div>

          <div className="flex items-center gap-4">
            <Link to="/login" className="text-text-secondary hover:text-text-primary transition-colors">
              Sign In
            </Link>
            <Link
              to="/register"
              className="px-5 py-2.5 rounded-lg bg-gradient-to-r from-accent-cyan to-accent-purple text-white font-medium hover:opacity-90 transition-opacity"
            >
              Get Started
            </Link>
          </div>
        </div>
      </motion.nav>

      {/* Hero Section */}
      <section ref={heroRef} className="relative min-h-screen flex items-center justify-center pt-20 pb-32 px-6">
        <GradientOrbs />
        <GridPattern />
        <Particles />

        <motion.div
          style={{ opacity: heroOpacity, scale: heroScale }}
          className="relative z-10 max-w-5xl mx-auto text-center"
        >
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-surface-card/50 border border-surface-border backdrop-blur-sm mb-8"
          >
            <Sparkles className="w-4 h-4 text-accent-cyan" />
            <span className="text-sm text-text-secondary">AI-Powered Email Command Center</span>
          </motion.div>

          {/* Main headline */}
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="text-5xl md:text-7xl lg:text-8xl font-bold leading-[0.95] mb-8"
          >
            <span className="block">Your inbox.</span>
            <span className="block bg-gradient-to-r from-accent-cyan via-accent-purple to-accent-cyan bg-clip-text text-transparent bg-[length:200%_auto] animate-gradient">
              On autopilot.
            </span>
          </motion.h1>

          {/* Subheadline */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="text-xl md:text-2xl text-text-secondary max-w-2xl mx-auto mb-12 leading-relaxed"
          >
            GetAnswers uses AI to triage, categorize, and handle your emails automatically.
            You only see what truly needs your attention.
          </motion.p>

          {/* Email signup form */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="max-w-lg mx-auto mb-8"
          >
            <form onSubmit={handleEmailSubmit} className="flex flex-col sm:flex-row gap-3">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                required
                disabled={isSubmitting}
                className="flex-1 px-5 py-4 text-base rounded-xl bg-surface-card/80 border border-surface-border text-text-primary placeholder-text-muted focus:border-accent-cyan focus:ring-2 focus:ring-accent-cyan/20 focus:outline-none transition-all disabled:opacity-50 disabled:cursor-not-allowed backdrop-blur-sm"
              />
              <button
                type="submit"
                disabled={isSubmitting}
                className="group flex items-center justify-center gap-2 px-8 py-4 rounded-xl bg-gradient-to-r from-accent-cyan to-accent-purple text-white font-semibold text-lg hover:opacity-90 transition-all disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    Get started
                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </button>
            </form>
            {error && (
              <p className="text-critical mt-3 text-sm text-center">{error}</p>
            )}
            <p className="text-text-muted mt-4 text-sm text-center">
              No credit card required • 14-day free trial
            </p>

            {/* Secondary CTA */}
            <div className="flex items-center justify-center gap-4 mt-6">
              <a
                href="#how-it-works"
                className="text-sm text-text-secondary hover:text-text-primary transition-colors"
              >
                See how it works
              </a>
              <span className="text-text-muted">•</span>
              <Link
                to="/login"
                className="text-sm text-text-secondary hover:text-text-primary transition-colors"
              >
                Already have an account?
              </Link>
            </div>
          </motion.div>

          {/* Scroll indicator */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
            className="absolute bottom-8 left-1/2 -translate-x-1/2"
          >
            <motion.div
              animate={{ y: [0, 10, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="flex flex-col items-center gap-2 text-text-muted"
            >
              <span className="text-xs uppercase tracking-wider">Scroll to explore</span>
              <ChevronDown className="w-5 h-5" />
            </motion.div>
          </motion.div>
        </motion.div>
      </section>

      {/* Stats Section */}
      <section className="py-24 px-6 border-y border-surface-border bg-surface-elevated/50">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 md:gap-12">
            <StatDisplay value="94" suffix="%" label="Automation Rate" index={0} />
            <StatDisplay value="2.5" suffix="h" label="Saved Daily" index={1} />
            <StatDisplay value="10" suffix="k+" label="Users" index={2} />
            <StatDisplay value="50" suffix="M" label="Emails Processed" index={3} />
          </div>
        </div>
      </section>

      {/* Dashboard Preview Section */}
      <section id="how-it-works" className="py-32 px-6">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Mission Control for Your Inbox
            </h2>
            <p className="text-xl text-text-secondary max-w-2xl mx-auto">
              A single dashboard to see what needs your attention, what's waiting on others,
              and what AI has already handled for you.
            </p>
          </motion.div>

          <DashboardPreview />
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-32 px-6 bg-surface-elevated/30">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Everything You Need
            </h2>
            <p className="text-xl text-text-secondary max-w-2xl mx-auto">
              Powerful features that put you back in control of your communications.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <FeatureCard key={feature.title} {...feature} index={index} />
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-32 px-6">
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-text-secondary max-w-2xl mx-auto">
              Start free. Upgrade when you're ready. No hidden fees.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {pricingPlans.map((plan, index) => (
              <PricingCard key={plan.name} {...plan} index={index} />
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-32 px-6 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-accent-cyan/10 via-transparent to-accent-purple/10" />
        <GradientOrbs />

        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="relative z-10 max-w-3xl mx-auto text-center"
        >
          <h2 className="text-4xl md:text-6xl font-bold mb-6">
            Ready to reclaim your time?
          </h2>
          <p className="text-xl text-text-secondary mb-10">
            Join thousands of professionals who've put their inbox on autopilot.
            Start your free trial today.
          </p>

          {/* Email signup form */}
          <div className="max-w-lg mx-auto">
            <form onSubmit={handleEmailSubmit} className="flex flex-col sm:flex-row gap-3">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                required
                disabled={isSubmitting}
                className="flex-1 px-5 py-4 text-base rounded-xl bg-surface-card/80 border border-surface-border text-text-primary placeholder-text-muted focus:border-accent-cyan focus:ring-2 focus:ring-accent-cyan/20 focus:outline-none transition-all disabled:opacity-50 disabled:cursor-not-allowed backdrop-blur-sm"
              />
              <button
                type="submit"
                disabled={isSubmitting}
                className="group flex items-center justify-center gap-2 px-8 py-4 rounded-xl bg-gradient-to-r from-accent-cyan to-accent-purple text-white font-semibold text-lg hover:opacity-90 transition-all disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    Get started
                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </button>
            </form>
            {error && (
              <p className="text-critical mt-3 text-sm">{error}</p>
            )}
          </div>

          <p className="mt-6 text-text-muted text-sm">
            No credit card required. 14-day free trial.
          </p>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-surface-border bg-surface-elevated">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-cyan to-accent-purple flex items-center justify-center">
                <Layers className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold">GetAnswers</span>
            </div>

            <div className="flex items-center gap-8 text-sm text-text-secondary">
              <a href="#" className="hover:text-text-primary transition-colors">Privacy</a>
              <a href="#" className="hover:text-text-primary transition-colors">Terms</a>
              <a href="#" className="hover:text-text-primary transition-colors">Contact</a>
            </div>

            <p className="text-sm text-text-muted">
              &copy; {new Date().getFullYear()} GetAnswers. All rights reserved.
            </p>
          </div>
        </div>
      </footer>

      {/* CSS for gradient animation */}
      <style>{`
        @keyframes gradient {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
        .animate-gradient {
          animation: gradient 8s ease infinite;
        }
      `}</style>
    </div>
  );
}
