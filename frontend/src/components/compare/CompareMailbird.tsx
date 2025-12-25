import { Check, X, Zap, Target, ArrowRight, Star, Inbox, Bot } from 'lucide-react';
import { Link } from 'react-router-dom';
import { ComparisonSEO } from '../SEO';

const features = [
  { name: 'AI-Generated Replies', getanswers: true, competitor: 'partial' },
  { name: 'Human-in-the-Loop Approval', getanswers: true, competitor: false },
  { name: 'Auto-Draft Responses', getanswers: true, competitor: 'partial' },
  { name: 'Smart Inbox', getanswers: true, competitor: true },
  { name: 'Email Bundles', getanswers: true, competitor: true },
  { name: 'Priority Sender Detection', getanswers: true, competitor: true },
  { name: 'Team Collaboration', getanswers: true, competitor: true },
  { name: 'Email Scheduling', getanswers: true, competitor: true },
  { name: 'Multi-Platform (iOS, Mac, Android)', getanswers: 'partial', competitor: true },
  { name: 'Gmail Integration', getanswers: true, competitor: true },
  { name: 'Outlook Integration', getanswers: true, competitor: true },
  { name: 'Learns Your Style', getanswers: true, competitor: false },
  { name: 'One-Click Actions', getanswers: true, competitor: false },
  { name: '+AI Writing Assistant', getanswers: true, competitor: true },
];

const testimonials = [
  {
    quote: "Spark's smart inbox is nice, but I still had to write every email. GetAnswers flipped the script—now AI writes, and I just approve or edit. Way more efficient.",
    author: "Kevin Lee",
    role: "Freelance Consultant",
    metric: "2.5 hrs saved daily",
  },
  {
    quote: "I loved Spark on mobile, but GetAnswers' AI responses changed how I think about email. I'm reviewing AI drafts instead of starting from scratch.",
    author: "Sophie Chen",
    role: "Project Manager",
    metric: "85% auto-handled",
  },
];

const comparisonPoints = [
  {
    title: 'Core Function',
    getanswers: 'AI email agent that writes responses for you. Review queue with approve/edit/escalate workflow.',
    competitor: 'Smart email client with AI features. Beautiful interface, cross-platform, team features.',
    winner: 'getanswers',
  },
  {
    title: 'Response Generation',
    getanswers: 'AI writes complete responses in your voice. One-click to approve and send.',
    competitor: '+AI writing assistant helps compose. Suggestions and rewrites, but you still drive.',
    winner: 'getanswers',
  },
  {
    title: 'Mobile Experience',
    getanswers: 'Web-based with responsive design. Mobile apps in development.',
    competitor: 'Excellent native apps for iOS, Mac, Android, Windows. Best-in-class mobile.',
    winner: 'competitor',
  },
  {
    title: 'Smart Inbox',
    getanswers: 'Categories by action needed: needs decision, waiting, handled by AI.',
    competitor: 'Smart inbox with bundles, priority sender detection, newsletter grouping.',
    winner: 'tie',
  },
  {
    title: 'Time Savings',
    getanswers: 'AI handles 80%+ of emails. Hours saved daily, not minutes.',
    competitor: 'Faster email management. Smart features save time but you write everything.',
    winner: 'getanswers',
  },
];

const renderFeatureValue = (value: boolean | string) => {
  if (value === true) {
    return <Check className="w-5 h-5 text-emerald-500" />;
  }
  if (value === 'partial') {
    return <span className="text-amber-500 text-sm font-medium">Partial</span>;
  }
  return <X className="w-5 h-5 text-gray-500" />;
};

export function CompareMailbird() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      <ComparisonSEO
        competitor="Mailbird"
        competitorDescription="Mailbird is a desktop email client. GetAnswers is AI that writes your email responses for you."
        slug="mailbird"
      />

      {/* Hero Section */}
      <section className="relative py-20 px-4 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 via-transparent to-blue-500/10" />
        <div className="max-w-6xl mx-auto text-center relative">
          <Link
            to="/compare"
            className="inline-flex items-center gap-2 text-gray-400 hover:text-white mb-6 transition-colors"
          >
            ← All Comparisons
          </Link>
          <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-cyan-500/20 text-cyan-400 text-sm font-medium mb-6 ml-4">
            <Zap className="w-4 h-4" />
            Head-to-Head Comparison
          </span>
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
            GetAnswers vs
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">
              Spark
            </span>
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto mb-8">
            Spark is a smart email client. GetAnswers is an AI email agent.
            See why agents beat clients.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register"
              className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-semibold rounded-lg hover:from-cyan-600 hover:to-blue-600 transition-all"
            >
              Try GetAnswers Free <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Quick Verdict */}
      <section className="py-12 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border border-cyan-500/20 rounded-2xl p-8">
            <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
              <Target className="w-8 h-8 text-cyan-400" />
              The Verdict
            </h2>
            <p className="text-gray-300 text-lg">
              <strong className="text-white">Spark</strong> is a beautifully designed email client with
              smart inbox features and excellent mobile apps.
              <strong className="text-white"> GetAnswers</strong> isn't just a client—
              <span className="text-cyan-400"> it's an AI agent that writes your emails</span>.
              You review and approve. Different category entirely.
            </p>
          </div>
        </div>
      </section>

      {/* Approach Comparison */}
      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            AI Agent vs Smart Client
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-cyan-500/10 border border-cyan-500/30 rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <Bot className="w-8 h-8 text-cyan-400" />
                <h3 className="text-xl font-semibold text-cyan-400">GetAnswers: AI Agent</h3>
              </div>
              <ul className="space-y-3 text-gray-300">
                <li className="flex items-start gap-2">
                  <Check className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
                  <span>AI writes your emails</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
                  <span>One-click approve workflow</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
                  <span>Learns your voice and style</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
                  <span>Hours saved, not minutes</span>
                </li>
              </ul>
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <Inbox className="w-8 h-8 text-gray-400" />
                <h3 className="text-xl font-semibold text-gray-400">Spark: Smart Client</h3>
              </div>
              <ul className="space-y-3 text-gray-300">
                <li className="flex items-start gap-2">
                  <Check className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" />
                  <span>Beautiful cross-platform apps</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" />
                  <span>Smart inbox organization</span>
                </li>
                <li className="flex items-start gap-2">
                  <X className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" />
                  <span>You write every email</span>
                </li>
                <li className="flex items-start gap-2">
                  <X className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" />
                  <span>AI assists, doesn't replace</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Detailed Comparison */}
      <section className="py-16 px-4 bg-slate-900/50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            Detailed Comparison
          </h2>
          <div className="space-y-8">
            {comparisonPoints.map((point, index) => (
              <div key={index} className="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden">
                <div className="bg-slate-800 px-6 py-4 border-b border-slate-700">
                  <h3 className="text-lg font-semibold text-white">{point.title}</h3>
                </div>
                <div className="grid md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-slate-700">
                  <div className={`p-6 ${point.winner === 'getanswers' ? 'bg-cyan-500/5' : ''}`}>
                    <div className="flex items-center gap-2 mb-3">
                      <span className="font-semibold text-cyan-400">GetAnswers</span>
                      {point.winner === 'getanswers' && (
                        <span className="px-2 py-0.5 bg-cyan-500/20 text-cyan-400 text-xs rounded-full">Winner</span>
                      )}
                    </div>
                    <p className="text-gray-300 text-sm">{point.getanswers}</p>
                  </div>
                  <div className={`p-6 ${point.winner === 'competitor' ? 'bg-blue-500/5' : ''}`}>
                    <div className="flex items-center gap-2 mb-3">
                      <span className="font-semibold text-gray-400">Spark</span>
                      {point.winner === 'competitor' && (
                        <span className="px-2 py-0.5 bg-blue-500/20 text-blue-400 text-xs rounded-full">Winner</span>
                      )}
                    </div>
                    <p className="text-gray-300 text-sm">{point.competitor}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Feature Table */}
      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-4">
            Feature Comparison
          </h2>
          <p className="text-gray-400 text-center mb-12">
            A side-by-side look at what each platform offers
          </p>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-4 px-4 text-gray-400 font-medium">Feature</th>
                  <th className="text-center py-4 px-4 text-cyan-400 font-semibold bg-cyan-500/10">GetAnswers</th>
                  <th className="text-center py-4 px-4 text-gray-300 font-semibold">Spark</th>
                </tr>
              </thead>
              <tbody>
                {features.map((feature, index) => (
                  <tr key={index} className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors">
                    <td className="py-4 px-4 text-gray-300">{feature.name}</td>
                    <td className="text-center py-4 px-4 bg-cyan-500/5">
                      {renderFeatureValue(feature.getanswers)}
                    </td>
                    <td className="text-center py-4 px-4">
                      {renderFeatureValue(feature.competitor)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-16 px-4 bg-slate-900/50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            Why Professionals Switch from Spark
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                <div className="flex gap-1 mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 text-cyan-400 fill-cyan-400" />
                  ))}
                </div>
                <p className="text-gray-300 mb-6 italic">"{testimonial.quote}"</p>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white font-semibold">{testimonial.author}</p>
                    <p className="text-gray-500 text-sm">{testimonial.role}</p>
                  </div>
                  <span className="px-3 py-1 bg-cyan-500/20 text-cyan-400 text-sm font-medium rounded-full">
                    {testimonial.metric}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Upgrade from Smart to Autonomous
          </h2>
          <p className="text-xl text-gray-400 mb-8">
            Don't just organize email smarter. Let AI handle it.
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
