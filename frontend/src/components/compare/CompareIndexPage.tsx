import { Zap, ArrowRight, Brain, Users, Mail, Filter, Bot, Inbox, Clock, Monitor, Code, Smartphone } from 'lucide-react';
import { Link } from 'react-router-dom';
import { SEO } from '../SEO';

const competitors = [
  // Major competitors
  {
    name: 'SaneBox',
    slug: 'sanebox',
    description: 'Email filtering vs AI email agent',
    icon: Filter,
  },
  {
    name: 'Superhuman',
    slug: 'superhuman',
    description: 'Speed vs intelligence',
    icon: Zap,
  },
  {
    name: 'Shortwave',
    slug: 'shortwave',
    description: 'AI summaries vs AI responses',
    icon: Bot,
  },
  {
    name: 'Mailbutler',
    slug: 'mailbutler',
    description: 'Email tools vs email automation',
    icon: Mail,
  },
  {
    name: 'Front',
    slug: 'front',
    description: 'Shared inbox vs AI inbox',
    icon: Users,
  },
  {
    name: 'Spark',
    slug: 'spark',
    description: 'Smart inbox vs AI agent',
    icon: Inbox,
  },
  {
    name: 'Missive',
    slug: 'missive',
    description: 'Team collaboration vs AI automation',
    icon: Users,
  },
  {
    name: 'Help Scout',
    slug: 'helpscout',
    description: 'Help desk vs AI-first inbox',
    icon: Mail,
  },
  {
    name: 'Boomerang',
    slug: 'boomerang',
    description: 'Email scheduling vs AI responses',
    icon: Clock,
  },
  {
    name: 'Zoho Mail',
    slug: 'zoho-mail',
    description: 'Business email vs AI-first inbox',
    icon: Mail,
  },
  {
    name: 'Mailbird',
    slug: 'mailbird',
    description: 'Desktop client vs AI automation',
    icon: Monitor,
  },
  // Local/smaller competitors
  {
    name: 'Newton Mail',
    slug: 'newton-mail',
    description: 'Beautiful client vs AI that writes',
    icon: Smartphone,
  },
  {
    name: 'Polymail',
    slug: 'polymail',
    description: 'Sales tracking vs AI responses',
    icon: Users,
  },
  {
    name: 'eM Client',
    slug: 'em-client',
    description: 'Desktop PIM vs AI automation',
    icon: Monitor,
  },
  {
    name: 'Mailspring',
    slug: 'mailspring',
    description: 'Open source vs AI writing',
    icon: Code,
  },
  {
    name: 'BlueMail',
    slug: 'bluemail',
    description: 'Cross-platform vs AI-first inbox',
    icon: Smartphone,
  },
];

export function CompareIndexPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      <SEO
        title="Email Automation Comparison - GetAnswers vs Competitors"
        description="Compare GetAnswers with popular email tools like SaneBox, Superhuman, Shortwave, and more. See why teams choose AI-powered email automation over traditional inbox management."
        canonical="/compare"
        keywords={[
          'email automation comparison',
          'best email tools',
          'SaneBox alternative',
          'Superhuman alternative',
          'AI email comparison',
          'inbox management tools',
        ]}
        jsonLd={{
          '@context': 'https://schema.org',
          '@type': 'CollectionPage',
          name: 'GetAnswers Competitor Comparisons',
          description: 'Compare GetAnswers AI email automation with traditional email management tools',
          mainEntity: {
            '@type': 'ItemList',
            itemListElement: [
              { '@type': 'ListItem', position: 1, name: 'GetAnswers vs SaneBox', url: 'https://getanswers.co/compare/sanebox' },
              { '@type': 'ListItem', position: 2, name: 'GetAnswers vs Superhuman', url: 'https://getanswers.co/compare/superhuman' },
              { '@type': 'ListItem', position: 3, name: 'GetAnswers vs Shortwave', url: 'https://getanswers.co/compare/shortwave' },
            ],
          },
        }}
      />

      {/* Hero Section */}
      <section className="relative py-20 px-4 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 via-transparent to-blue-500/10" />
        <div className="max-w-6xl mx-auto text-center relative">
          <Link
            to="/"
            className="inline-flex items-center gap-2 text-gray-400 hover:text-white mb-6 transition-colors"
          >
            ← Back to Home
          </Link>
          <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-cyan-500/20 text-cyan-400 text-sm font-medium mb-6 ml-4">
            <Zap className="w-4 h-4" />
            Compare Solutions
          </span>
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
            GetAnswers vs
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">
              The Competition
            </span>
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto mb-8">
            See how GetAnswers' AI-first approach compares to traditional email tools.
            Other tools organize your inbox. We actually respond to it.
          </p>
        </div>
      </section>

      {/* Why GetAnswers Section */}
      <section className="py-12 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border border-cyan-500/20 rounded-2xl p-8">
            <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
              <Brain className="w-8 h-8 text-cyan-400" />
              Why GetAnswers is Different
            </h2>
            <p className="text-gray-300 text-lg">
              Most email tools help you manage your inbox faster. GetAnswers is an{' '}
              <span className="text-cyan-400">AI email agent</span> that actually reads, understands,
              and responds to your emails. You review and approve—the AI does the work.
            </p>
          </div>
        </div>
      </section>

      {/* Competitor Grid */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-4">
            Choose a Comparison
          </h2>
          <p className="text-gray-400 text-center mb-12 max-w-2xl mx-auto">
            Click on any competitor to see a detailed side-by-side comparison
          </p>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {competitors.map((competitor) => (
              <Link
                key={competitor.slug}
                to={`/compare/${competitor.slug}`}
                className="group bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:border-cyan-500/50 hover:bg-slate-800/80 transition-all"
              >
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-cyan-500/20 to-blue-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <competitor.icon className="w-6 h-6 text-cyan-400" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
                  vs {competitor.name}
                  <ArrowRight className="w-4 h-4 text-cyan-400 opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
                </h3>
                <p className="text-gray-400 text-sm">{competitor.description}</p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to Put Your Inbox on Autopilot?
          </h2>
          <p className="text-xl text-gray-400 mb-8">
            Stop managing email. Start approving AI-generated responses.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register"
              className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-semibold rounded-lg hover:from-cyan-600 hover:to-blue-600 transition-all"
            >
              Start Free Trial <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              to="/login"
              className="inline-flex items-center justify-center gap-2 px-8 py-4 border border-gray-700 text-white font-semibold rounded-lg hover:bg-gray-800 transition-all"
            >
              Watch Demo
            </Link>
          </div>
          <p className="text-gray-500 mt-6 text-sm">
            14-day free trial • No credit card required • Cancel anytime
          </p>
        </div>
      </section>
    </div>
  );
}
