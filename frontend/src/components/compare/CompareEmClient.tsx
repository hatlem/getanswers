import { Check, X, Zap, Target, ArrowRight, Star, Bot, Monitor } from 'lucide-react';
import { Link } from 'react-router-dom';
import { ComparisonSEO } from '../SEO';

const features = [
  { name: 'AI-Generated Replies', getanswers: true, competitor: false },
  { name: 'Human-in-the-Loop Approval', getanswers: true, competitor: false },
  { name: 'Desktop App', getanswers: false, competitor: true },
  { name: 'Calendar Integration', getanswers: false, competitor: true },
  { name: 'PGP Encryption', getanswers: false, competitor: true },
  { name: 'Multi-Account Support', getanswers: true, competitor: true },
  { name: 'Smart Inbox', getanswers: true, competitor: false },
  { name: 'Contact Management', getanswers: true, competitor: true },
  { name: 'Learns Your Style', getanswers: true, competitor: false },
  { name: 'Gmail Integration', getanswers: true, competitor: true },
  { name: 'Outlook Integration', getanswers: true, competitor: true },
  { name: 'One-Time Purchase', getanswers: false, competitor: true },
];

const testimonials = [
  {
    quote: "eM Client is great desktop software, but it doesn't help me write faster. GetAnswers actually writes my responses.",
    author: "Martin Dvorak",
    role: "IT Consultant, Czech Republic",
    metric: "4 hrs saved daily",
  },
  {
    quote: "I used eM Client for years. Switching to GetAnswers was like going from typing to dictating—AI does the work.",
    author: "Anna Kowalska",
    role: "Business Owner, Poland",
    metric: "80% auto-handled",
  },
];

const comparisonPoints = [
  {
    title: 'Core Approach',
    getanswers: 'AI reads and responds to emails. You review and approve.',
    competitor: 'Full-featured desktop email client. You write everything manually.',
    winner: 'getanswers',
  },
  {
    title: 'Desktop Experience',
    getanswers: 'Web-first with native-like experience. No installation needed.',
    competitor: 'Native Windows/Mac app with calendar, contacts, and tasks.',
    winner: 'competitor',
  },
  {
    title: 'Privacy & Security',
    getanswers: 'Secure cloud processing with enterprise-grade encryption.',
    competitor: 'Local storage with PGP encryption support.',
    winner: 'competitor',
  },
];

const renderFeatureValue = (value: boolean | string) => {
  if (value === true) return <Check className="w-5 h-5 text-emerald-500" />;
  if (value === 'partial') return <span className="text-amber-500 text-sm font-medium">Partial</span>;
  return <X className="w-5 h-5 text-gray-500" />;
};

export function CompareEmClient() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      <ComparisonSEO
        competitor="eM Client"
        competitorDescription="eM Client is a desktop email app. GetAnswers is AI that writes your email responses automatically."
        slug="em-client"
      />

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
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">eM Client</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto mb-8">
            Czech desktop email client vs AI that writes your emails.
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
              <strong className="text-white">eM Client</strong> is a powerful Czech desktop email client with calendar and contacts.
              <strong className="text-white"> GetAnswers</strong> uses AI to write your emails automatically. Need a full desktop PIM? eM Client. Want AI handling your responses? GetAnswers.
            </p>
          </div>
        </div>
      </section>

      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">AI Responses vs Desktop Power</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-cyan-500/10 border border-cyan-500/30 rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <Bot className="w-8 h-8 text-cyan-400" />
                <h3 className="text-xl font-semibold text-cyan-400">GetAnswers: AI Response</h3>
              </div>
              <ul className="space-y-3 text-gray-300">
                <li className="flex items-start gap-2"><Check className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" /><span>AI writes complete responses</span></li>
                <li className="flex items-start gap-2"><Check className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" /><span>Access from any device</span></li>
                <li className="flex items-start gap-2"><Check className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" /><span>Hours saved daily</span></li>
              </ul>
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <Monitor className="w-8 h-8 text-gray-400" />
                <h3 className="text-xl font-semibold text-gray-400">eM Client: Desktop PIM</h3>
              </div>
              <ul className="space-y-3 text-gray-300">
                <li className="flex items-start gap-2"><Check className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" /><span>Native desktop experience</span></li>
                <li className="flex items-start gap-2"><Check className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" /><span>Calendar & contacts included</span></li>
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
                      <span className="font-semibold text-gray-400">eM Client</span>
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
                  <th className="text-center py-4 px-4 text-gray-300">eM Client</th>
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
          <h2 className="text-3xl font-bold text-white text-center mb-12">Why Users Upgrade</h2>
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
          <h2 className="text-4xl font-bold text-white mb-6">Let AI Handle Your Email</h2>
          <p className="text-xl text-gray-400 mb-8">More than a client—an AI assistant that writes for you.</p>
          <Link to="/register" className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-semibold rounded-lg hover:from-cyan-600 hover:to-blue-600 transition-all">
            Start Free Trial <ArrowRight className="w-5 h-5" />
          </Link>
          <p className="text-gray-500 mt-6 text-sm">14-day free trial • No credit card required</p>
        </div>
      </section>
    </div>
  );
}
