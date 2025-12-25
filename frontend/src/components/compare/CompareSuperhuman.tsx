import { Check, X, Zap, Target, ArrowRight, Star, Gauge, Bot } from 'lucide-react';
import { Link } from 'react-router-dom';
import { ComparisonSEO } from '../SEO';

const features = [
  { name: 'AI-Generated Replies', getanswers: true, competitor: false },
  { name: 'Human-in-the-Loop Approval', getanswers: true, competitor: false },
  { name: 'Auto-Draft Responses', getanswers: true, competitor: 'partial' },
  { name: 'Smart Email Triage', getanswers: true, competitor: true },
  { name: 'Priority Inbox', getanswers: true, competitor: true },
  { name: 'Keyboard Shortcuts', getanswers: true, competitor: true },
  { name: 'Split Inbox', getanswers: true, competitor: true },
  { name: 'Email Scheduling', getanswers: true, competitor: true },
  { name: 'Read Receipts', getanswers: false, competitor: true },
  { name: 'Gmail Integration', getanswers: true, competitor: true },
  { name: 'Outlook Integration', getanswers: true, competitor: false },
  { name: 'Learns Your Style', getanswers: true, competitor: 'partial' },
  { name: 'One-Click Actions', getanswers: true, competitor: false },
  { name: 'Team Collaboration', getanswers: true, competitor: true },
];

const testimonials = [
  {
    quote: "Superhuman made me faster at writing emails. GetAnswers means I barely write emails at all. The AI drafts them, I just approve. Way bigger time savings.",
    author: "Alex Rodriguez",
    role: "VP of Sales",
    metric: "4 hrs saved daily",
  },
  {
    quote: "I loved Superhuman's speed, but GetAnswers is intelligence over speed. It doesn't just help me send faster—it actually thinks and responds for me.",
    author: "Rachel Kim",
    role: "CEO, Tech Startup",
    metric: "90% auto-handled",
  },
];

const comparisonPoints = [
  {
    title: 'Core Philosophy',
    getanswers: 'AI does the work. Reads emails, drafts responses, you approve. The AI handles, you oversee.',
    competitor: 'You do the work, faster. Optimized for speed with keyboard shortcuts and clean UI.',
    winner: 'getanswers',
  },
  {
    title: 'Response Generation',
    getanswers: 'Full AI-generated responses in your voice. Context-aware, learning from your style.',
    competitor: 'AI snippets and autocomplete suggestions. You still compose the actual response.',
    winner: 'getanswers',
  },
  {
    title: 'Speed & UX',
    getanswers: 'Clean interface with one-click actions. Optimized for reviewing and approving AI responses.',
    competitor: 'Best-in-class speed UI. Sub-100ms interactions. Keyboard-first design.',
    winner: 'competitor',
  },
  {
    title: 'Email Tracking',
    getanswers: 'Focus on response generation and automation rather than tracking.',
    competitor: 'Read receipts, open tracking, and engagement insights for every email.',
    winner: 'competitor',
  },
  {
    title: 'Pricing',
    getanswers: 'Starts at $29/month for full AI capabilities.',
    competitor: '$30/month for speed features. Premium positioning.',
    winner: 'tie',
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

export function CompareSuperhuman() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      <ComparisonSEO
        competitor="Superhuman"
        competitorDescription="Superhuman makes you faster at writing emails. GetAnswers means you barely write emails at all - AI drafts them, you approve."
        slug="superhuman"
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
              Superhuman
            </span>
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto mb-8">
            Superhuman makes you faster at email. GetAnswers makes email automatic.
            Speed vs intelligence—see the difference.
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
              <strong className="text-white">Superhuman</strong> is the fastest email client on the market—
              beautiful design, keyboard shortcuts, and sub-100ms interactions.
              <strong className="text-white"> GetAnswers</strong> takes a different approach:
              <span className="text-cyan-400"> AI writes your emails for you</span>. You don't need to be
              faster when the AI does the work.
            </p>
          </div>
        </div>
      </section>

      {/* Approach Comparison */}
      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            Intelligence vs Speed
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-cyan-500/10 border border-cyan-500/30 rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <Bot className="w-8 h-8 text-cyan-400" />
                <h3 className="text-xl font-semibold text-cyan-400">GetAnswers: Intelligence</h3>
              </div>
              <ul className="space-y-3 text-gray-300">
                <li className="flex items-start gap-2">
                  <Check className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
                  <span>AI writes complete responses</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
                  <span>One-click approve/edit/escalate</span>
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
                <Gauge className="w-8 h-8 text-gray-400" />
                <h3 className="text-xl font-semibold text-gray-400">Superhuman: Speed</h3>
              </div>
              <ul className="space-y-3 text-gray-300">
                <li className="flex items-start gap-2">
                  <Check className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" />
                  <span>Fastest email experience</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" />
                  <span>Keyboard-first navigation</span>
                </li>
                <li className="flex items-start gap-2">
                  <X className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" />
                  <span>You still write every email</span>
                </li>
                <li className="flex items-start gap-2">
                  <X className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" />
                  <span>Faster, but same workload</span>
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
                  <div className={`p-6 ${point.winner === 'competitor' ? 'bg-violet-500/5' : ''}`}>
                    <div className="flex items-center gap-2 mb-3">
                      <span className="font-semibold text-gray-400">Superhuman</span>
                      {point.winner === 'competitor' && (
                        <span className="px-2 py-0.5 bg-violet-500/20 text-violet-400 text-xs rounded-full">Winner</span>
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
                  <th className="text-center py-4 px-4 text-gray-300 font-semibold">Superhuman</th>
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
            Why Professionals Choose GetAnswers Over Superhuman
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
            Stop Writing Emails. Start Approving Them.
          </h2>
          <p className="text-xl text-gray-400 mb-8">
            Why be faster at email when AI can handle it for you?
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
