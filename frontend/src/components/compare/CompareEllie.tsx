import { Check, X, Zap, Target, ArrowRight, Star, Bot, Brain } from 'lucide-react';
import { Link } from 'react-router-dom';

const features = [
  { name: 'AI-Generated Replies', getanswers: true, competitor: true },
  { name: 'Human-in-the-Loop Approval Queue', getanswers: true, competitor: false },
  { name: 'Auto-Draft Responses', getanswers: true, competitor: true },
  { name: 'Learns Your Writing Style', getanswers: true, competitor: true },
  { name: 'Context-Aware Responses', getanswers: true, competitor: 'partial' },
  { name: 'Confidence Scoring', getanswers: true, competitor: false },
  { name: 'Risk Assessment', getanswers: true, competitor: false },
  { name: 'One-Click Approve/Edit/Escalate', getanswers: true, competitor: false },
  { name: 'Email Thread Understanding', getanswers: true, competitor: 'partial' },
  { name: 'Gmail Integration', getanswers: true, competitor: true },
  { name: 'Outlook Integration', getanswers: true, competitor: false },
  { name: 'Custom Autonomy Levels', getanswers: true, competitor: false },
  { name: 'Audit Trail of AI Actions', getanswers: true, competitor: false },
  { name: 'Team Collaboration', getanswers: true, competitor: false },
];

const testimonials = [
  {
    quote: "Ellie generates replies but I still had to manage everything myself. GetAnswers queues decisions for me—I just approve or edit. It's like having an actual assistant, not just a writing tool.",
    author: "Sarah Chen",
    role: "Product Manager",
    metric: "5 hrs saved weekly",
  },
  {
    quote: "Both use AI to draft, but GetAnswers understands context better. It tracks entire conversations, knows what's high-risk, and only surfaces what truly needs my attention.",
    author: "Marcus Johnson",
    role: "Consultant",
    metric: "92% approval rate",
  },
];

const comparisonPoints = [
  {
    title: 'Core Approach',
    getanswers: 'Complete email management system with AI agent, approval queue, and autonomous handling. Human-in-the-loop by design.',
    competitor: 'Chrome extension that suggests AI-generated replies. You copy/paste or edit the suggestion.',
    winner: 'getanswers',
  },
  {
    title: 'Response Quality',
    getanswers: 'Context-aware with full conversation understanding. Confidence scoring tells you how certain the AI is. Risk assessment flags high-stakes emails.',
    competitor: 'Learns your style and generates contextual replies. Quality is good but no confidence metrics or risk assessment.',
    winner: 'getanswers',
  },
  {
    title: 'Workflow Integration',
    getanswers: 'Dedicated platform with approval queue, decision tracking, and audit trail. Automated workflow from triage to sending.',
    competitor: 'Browser extension that works within Gmail. Manual workflow—you still manage everything yourself.',
    winner: 'getanswers',
  },
  {
    title: 'Learning & Adaptation',
    getanswers: 'Learns from your edits, approvals, and policies. Improves over time with feedback loops. Custom autonomy settings per sender/topic.',
    competitor: 'Learns your writing style from your sent emails. Gets better with use but limited customization.',
    winner: 'tie',
  },
  {
    title: 'Pricing',
    getanswers: 'Starts at $29/month for full platform with unlimited AI processing and team features.',
    competitor: 'Starts at $19/month for basic plan. $39/month for pro. Good value for simple AI replies.',
    winner: 'competitor',
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

export function CompareEllie() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
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
              Ellie
            </span>
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto mb-8">
            Ellie generates AI replies. GetAnswers manages your entire inbox with AI.
            See why a full platform beats a browser extension.
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
              <strong className="text-white">Ellie</strong> is a solid Chrome extension that generates AI-powered
              email replies you can use in Gmail.
              <strong className="text-white"> GetAnswers</strong> is a complete email management platform:
              <span className="text-cyan-400"> AI agent + approval queue + autonomous handling + team features</span>.
              Ellie gives you AI suggestions. GetAnswers runs your inbox.
            </p>
          </div>
        </div>
      </section>

      {/* Approach Comparison */}
      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            Full Platform vs Browser Extension
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-cyan-500/10 border border-cyan-500/30 rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <Brain className="w-8 h-8 text-cyan-400" />
                <h3 className="text-xl font-semibold text-cyan-400">GetAnswers: Full Platform</h3>
              </div>
              <ul className="space-y-3 text-gray-300">
                <li className="flex items-start gap-2">
                  <Check className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
                  <span>Approval queue for review decisions</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
                  <span>Confidence scoring & risk assessment</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
                  <span>Autonomous handling (80%+ emails)</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
                  <span>Complete audit trail</span>
                </li>
              </ul>
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <Bot className="w-8 h-8 text-gray-400" />
                <h3 className="text-xl font-semibold text-gray-400">Ellie: Chrome Extension</h3>
              </div>
              <ul className="space-y-3 text-gray-300">
                <li className="flex items-start gap-2">
                  <Check className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" />
                  <span>Generates AI reply suggestions</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" />
                  <span>Works directly in Gmail</span>
                </li>
                <li className="flex items-start gap-2">
                  <X className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" />
                  <span>No approval queue or workflow</span>
                </li>
                <li className="flex items-start gap-2">
                  <X className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" />
                  <span>You manage everything manually</span>
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
                      <span className="font-semibold text-gray-400">Ellie</span>
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
                  <th className="text-center py-4 px-4 text-gray-300 font-semibold">Ellie</th>
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
            Why Users Switch from Ellie to GetAnswers
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
            Ready for a Full Email Management Platform?
          </h2>
          <p className="text-xl text-gray-400 mb-8">
            Stop copying AI suggestions. Start approving decisions in an intelligent queue.
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
