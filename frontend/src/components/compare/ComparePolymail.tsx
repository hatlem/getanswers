import { Check, X, Zap, Target, ArrowRight, Star, Bot, Users } from 'lucide-react';
import { Link } from 'react-router-dom';

const features = [
  { name: 'AI-Generated Replies', getanswers: true, competitor: false },
  { name: 'Human-in-the-Loop Approval', getanswers: true, competitor: false },
  { name: 'Email Tracking', getanswers: false, competitor: true },
  { name: 'Team Collaboration', getanswers: true, competitor: true },
  { name: 'Shared Templates', getanswers: true, competitor: true },
  { name: 'CRM Integration', getanswers: true, competitor: true },
  { name: 'Send Later', getanswers: true, competitor: true },
  { name: 'Email Analytics', getanswers: true, competitor: true },
  { name: 'Smart Inbox', getanswers: true, competitor: false },
  { name: 'Learns Your Style', getanswers: true, competitor: false },
  { name: 'Gmail Integration', getanswers: true, competitor: true },
  { name: 'Contact Insights', getanswers: true, competitor: true },
];

const testimonials = [
  {
    quote: "Polymail was our sales team's go-to for tracking. GetAnswers is now our go-to because AI drafts our follow-ups automatically.",
    author: "Marcus Johnson",
    role: "Sales Team Lead",
    metric: "2x more replies",
  },
  {
    quote: "We needed more than email tracking. GetAnswers writes contextual responses that sound like each team member.",
    author: "Jennifer Park",
    role: "Customer Success Manager",
    metric: "70% auto-drafted",
  },
];

const comparisonPoints = [
  {
    title: 'Core Value',
    getanswers: 'AI writes responses in your voice. Review and send with one click.',
    competitor: 'Email productivity with tracking, templates, and team collaboration.',
    winner: 'getanswers',
  },
  {
    title: 'Sales Focus',
    getanswers: 'AI drafts follow-ups and responses. Great for high-volume sales communication.',
    competitor: 'Built for sales teams with tracking, CRM sync, and contact insights.',
    winner: 'tie',
  },
  {
    title: 'Team Features',
    getanswers: 'AI learns from team patterns. Consistent voice across the team.',
    competitor: 'Shared templates, team analytics, and collaborative inbox.',
    winner: 'competitor',
  },
];

const renderFeatureValue = (value: boolean | string) => {
  if (value === true) return <Check className="w-5 h-5 text-emerald-500" />;
  if (value === 'partial') return <span className="text-amber-500 text-sm font-medium">Partial</span>;
  return <X className="w-5 h-5 text-gray-500" />;
};

export function ComparePolymail() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      <section className="relative py-20 px-4 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 via-transparent to-blue-500/10" />
        <div className="max-w-6xl mx-auto text-center relative">
          <Link to="/compare" className="inline-flex items-center gap-2 text-gray-400 hover:text-white mb-6 transition-colors">
            ← All Comparisons
          </Link>
          <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-cyan-500/20 text-cyan-400 text-sm font-medium mb-6 ml-4">
            <Zap className="w-4 h-4" />Comparison
          </span>
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
            GetAnswers vs<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">Polymail</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto mb-8">
            Sales email tracking vs AI that writes your sales responses.
          </p>
          <Link to="/register" className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-semibold rounded-lg hover:from-cyan-600 hover:to-blue-600 transition-all">
            Try GetAnswers Free <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      <section className="py-12 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border border-cyan-500/20 rounded-2xl p-8">
            <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
              <Target className="w-8 h-8 text-cyan-400" />The Verdict
            </h2>
            <p className="text-gray-300 text-lg">
              <strong className="text-white">Polymail</strong> is excellent for sales teams who need email tracking and CRM integration.
              <strong className="text-white"> GetAnswers</strong> goes further—AI writes the actual responses. Know when emails are opened, or have AI handle responses? Choose your priority.
            </p>
          </div>
        </div>
      </section>

      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">AI Writing vs Email Tracking</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-cyan-500/10 border border-cyan-500/30 rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <Bot className="w-8 h-8 text-cyan-400" />
                <h3 className="text-xl font-semibold text-cyan-400">GetAnswers: AI Writing</h3>
              </div>
              <ul className="space-y-3 text-gray-300">
                <li className="flex items-start gap-2"><Check className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" /><span>AI drafts follow-up emails</span></li>
                <li className="flex items-start gap-2"><Check className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" /><span>Context-aware responses</span></li>
                <li className="flex items-start gap-2"><Check className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" /><span>Consistent team voice</span></li>
              </ul>
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <Users className="w-8 h-8 text-gray-400" />
                <h3 className="text-xl font-semibold text-gray-400">Polymail: Sales Tools</h3>
              </div>
              <ul className="space-y-3 text-gray-300">
                <li className="flex items-start gap-2"><Check className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" /><span>Read receipts & link tracking</span></li>
                <li className="flex items-start gap-2"><Check className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" /><span>CRM integration</span></li>
                <li className="flex items-start gap-2"><X className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" /><span>You write every email</span></li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <section className="py-16 px-4 bg-slate-900/50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">Detailed Comparison</h2>
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
                      {point.winner === 'getanswers' && <span className="px-2 py-0.5 bg-cyan-500/20 text-cyan-400 text-xs rounded-full">Winner</span>}
                    </div>
                    <p className="text-gray-300 text-sm">{point.getanswers}</p>
                  </div>
                  <div className={`p-6 ${point.winner === 'competitor' ? 'bg-violet-500/5' : ''}`}>
                    <div className="flex items-center gap-2 mb-3">
                      <span className="font-semibold text-gray-400">Polymail</span>
                      {point.winner === 'competitor' && <span className="px-2 py-0.5 bg-violet-500/20 text-violet-400 text-xs rounded-full">Winner</span>}
                    </div>
                    <p className="text-gray-300 text-sm">{point.competitor}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">Feature Comparison</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-4 px-4 text-gray-400">Feature</th>
                  <th className="text-center py-4 px-4 text-cyan-400 bg-cyan-500/10">GetAnswers</th>
                  <th className="text-center py-4 px-4 text-gray-300">Polymail</th>
                </tr>
              </thead>
              <tbody>
                {features.map((f, i) => (
                  <tr key={i} className="border-b border-slate-800">
                    <td className="py-4 px-4 text-gray-300">{f.name}</td>
                    <td className="text-center py-4 px-4 bg-cyan-500/5">{renderFeatureValue(f.getanswers)}</td>
                    <td className="text-center py-4 px-4">{renderFeatureValue(f.competitor)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section className="py-16 px-4 bg-slate-900/50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">Why Sales Teams Switch</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {testimonials.map((t, i) => (
              <div key={i} className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                <div className="flex gap-1 mb-4">{[...Array(5)].map((_, j) => <Star key={j} className="w-4 h-4 text-cyan-400 fill-cyan-400" />)}</div>
                <p className="text-gray-300 mb-6 italic">"{t.quote}"</p>
                <div className="flex justify-between">
                  <div>
                    <p className="text-white font-semibold">{t.author}</p>
                    <p className="text-gray-500 text-sm">{t.role}</p>
                  </div>
                  <span className="px-3 py-1 bg-cyan-500/20 text-cyan-400 text-sm rounded-full h-fit">{t.metric}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-6">AI-Powered Sales Email</h2>
          <p className="text-xl text-gray-400 mb-8">Let AI write your follow-ups and responses.</p>
          <Link to="/register" className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-semibold rounded-lg hover:from-cyan-600 hover:to-blue-600 transition-all">
            Start Free Trial <ArrowRight className="w-5 h-5" />
          </Link>
          <p className="text-gray-500 mt-6 text-sm">14-day free trial • No credit card required</p>
        </div>
      </section>
    </div>
  );
}
