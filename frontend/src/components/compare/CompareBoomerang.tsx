import { Check, X, Zap, Target, ArrowRight, Star, Clock, Bot } from 'lucide-react';
import { Link } from 'react-router-dom';

const features = [
  { name: 'AI-Generated Replies', getanswers: true, competitor: false },
  { name: 'Human-in-the-Loop Approval', getanswers: true, competitor: false },
  { name: 'Auto-Draft Responses', getanswers: true, competitor: false },
  { name: 'Email Scheduling', getanswers: true, competitor: true },
  { name: 'Follow-up Reminders', getanswers: true, competitor: true },
  { name: 'Read Receipts', getanswers: true, competitor: true },
  { name: 'Gmail Integration', getanswers: true, competitor: true },
  { name: 'Outlook Integration', getanswers: true, competitor: true },
  { name: 'Respondable AI', getanswers: true, competitor: 'partial' },
  { name: 'Learns Your Style', getanswers: true, competitor: false },
  { name: 'One-Click Actions', getanswers: true, competitor: false },
  { name: 'Email Analytics', getanswers: true, competitor: true },
];

const testimonials = [
  {
    quote: "Boomerang helped me schedule emails and get reminders. But I still wrote every single reply. GetAnswers drafts them for me. It's a completely different level of productivity.",
    author: "Marcus Chen",
    role: "Sales Director",
    metric: "4+ hrs saved daily",
  },
  {
    quote: "I loved Boomerang's scheduling features but GetAnswers actually writes my responses. Respondable told me if my email was good, GetAnswers just writes a good one from scratch.",
    author: "Amanda Foster",
    role: "Account Executive",
    metric: "90% approval rate",
  },
];

const comparisonPoints = [
  {
    title: 'Core Function',
    getanswers: 'AI email agent that reads, understands, and drafts responses for every email. You review and approve.',
    competitor: 'Email scheduling and productivity tools. Schedule sends, set reminders, track opens.',
    winner: 'getanswers',
  },
  {
    title: 'Response Generation',
    getanswers: 'AI generates complete, contextual replies in your voice. One click to approve, edit, or escalate.',
    competitor: 'Respondable gives suggestions on existing drafts. Does not write emails for you.',
    winner: 'getanswers',
  },
  {
    title: 'Email Scheduling',
    getanswers: 'Schedule approved emails for optimal send times. AI can suggest best times based on recipient.',
    competitor: 'Industry-leading email scheduling. Boomerang pioneered "send later" functionality.',
    winner: 'tie',
  },
  {
    title: 'Follow-up Tracking',
    getanswers: 'AI tracks conversations and auto-generates follow-up drafts when no response received.',
    competitor: 'Manual reminders to follow up. You set when to be reminded if no reply.',
    winner: 'getanswers',
  },
  {
    title: 'Pricing',
    getanswers: 'Starts at $29/month for full AI agent capabilities. Unlimited email processing.',
    competitor: 'Free tier available. Paid plans from $4.99/month for scheduling features.',
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

export function CompareBoomerangPage() {
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
              Boomerang
            </span>
          </h1>
          <p className="text-xl text-gray-400 mb-8 max-w-3xl mx-auto">
            Boomerang schedules your emails. GetAnswers writes them. Stop spending hours crafting responses—let AI draft them while you focus on decisions.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/signup"
              className="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-semibold hover:opacity-90 transition-opacity"
            >
              Start Free Trial
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              to="/demo"
              className="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-xl border border-gray-700 text-white font-semibold hover:bg-white/5 transition-colors"
            >
              Request Demo
            </Link>
          </div>
        </div>
      </section>

      {/* Quick Stats */}
      <section className="py-12 px-4 border-y border-gray-800">
        <div className="max-w-4xl mx-auto grid grid-cols-3 gap-8 text-center">
          <div>
            <div className="text-3xl font-bold text-cyan-400">4+ hrs</div>
            <div className="text-gray-500 text-sm">Saved daily vs scheduling alone</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-cyan-400">Auto-draft</div>
            <div className="text-gray-500 text-sm">vs manual reminders</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-cyan-400">AI writes</div>
            <div className="text-gray-500 text-sm">vs you write everything</div>
          </div>
        </div>
      </section>

      {/* Key Differences */}
      <section className="py-20 px-4">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-4">
            Why Switch from Boomerang?
          </h2>
          <p className="text-gray-400 text-center mb-12 max-w-2xl mx-auto">
            Boomerang is great for scheduling. GetAnswers handles everything—including writing the emails.
          </p>

          <div className="space-y-6">
            {comparisonPoints.map((point) => (
              <div
                key={point.title}
                className="bg-slate-800/50 rounded-2xl p-6 border border-gray-700"
              >
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Target className="w-5 h-5 text-cyan-400" />
                  {point.title}
                </h3>
                <div className="grid md:grid-cols-2 gap-6">
                  <div
                    className={`p-4 rounded-xl ${
                      point.winner === 'getanswers' || point.winner === 'tie'
                        ? 'bg-cyan-500/10 border border-cyan-500/30'
                        : 'bg-slate-700/50'
                    }`}
                  >
                    <div className="text-cyan-400 font-medium mb-2">GetAnswers</div>
                    <p className="text-gray-300 text-sm">{point.getanswers}</p>
                  </div>
                  <div
                    className={`p-4 rounded-xl ${
                      point.winner === 'competitor'
                        ? 'bg-orange-500/10 border border-orange-500/30'
                        : 'bg-slate-700/50'
                    }`}
                  >
                    <div className="text-orange-400 font-medium mb-2">Boomerang</div>
                    <p className="text-gray-300 text-sm">{point.competitor}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Feature Table */}
      <section className="py-20 px-4 bg-slate-800/30">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            Feature Comparison
          </h2>
          <div className="overflow-hidden rounded-2xl border border-gray-700">
            <table className="w-full">
              <thead>
                <tr className="bg-slate-800">
                  <th className="text-left py-4 px-6 text-gray-400 font-medium">Feature</th>
                  <th className="text-center py-4 px-6 text-cyan-400 font-medium">GetAnswers</th>
                  <th className="text-center py-4 px-6 text-gray-400 font-medium">Boomerang</th>
                </tr>
              </thead>
              <tbody>
                {features.map((feature, index) => (
                  <tr
                    key={feature.name}
                    className={index % 2 === 0 ? 'bg-slate-900/50' : 'bg-slate-800/30'}
                  >
                    <td className="py-4 px-6 text-gray-300">{feature.name}</td>
                    <td className="py-4 px-6 text-center">
                      {renderFeatureValue(feature.getanswers)}
                    </td>
                    <td className="py-4 px-6 text-center">
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
      <section className="py-20 px-4">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            From Boomerang Users
          </h2>
          <div className="grid md:grid-cols-2 gap-8">
            {testimonials.map((testimonial) => (
              <div
                key={testimonial.author}
                className="bg-slate-800/50 rounded-2xl p-8 border border-gray-700"
              >
                <div className="flex items-center gap-1 mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <p className="text-gray-300 mb-6 italic">"{testimonial.quote}"</p>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-white font-medium">{testimonial.author}</div>
                    <div className="text-gray-500 text-sm">{testimonial.role}</div>
                  </div>
                  <div className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-sm font-medium">
                    {testimonial.metric}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-gradient-to-r from-cyan-500/20 to-blue-500/20 rounded-3xl p-12 border border-cyan-500/30">
            <Clock className="w-12 h-12 text-cyan-400 mx-auto mb-6" />
            <h2 className="text-3xl font-bold text-white mb-4">
              More Than Just Scheduling
            </h2>
            <p className="text-gray-400 mb-8 max-w-xl mx-auto">
              Boomerang helps you send at the right time. GetAnswers writes the email, schedules it, and follows up—all automatically.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/signup"
                className="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-semibold hover:opacity-90 transition-opacity"
              >
                Start Free Trial
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                to="/pricing"
                className="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-xl border border-gray-600 text-white font-semibold hover:bg-white/5 transition-colors"
              >
                View Pricing
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
