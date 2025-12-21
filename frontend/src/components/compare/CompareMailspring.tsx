import { Check, X, Zap, Target, ArrowRight, Star, Bot, Code } from 'lucide-react';
import { Link } from 'react-router-dom';

const features = [
  { name: 'AI-Generated Replies', getanswers: true, competitor: false },
  { name: 'Human-in-the-Loop Approval', getanswers: true, competitor: false },
  { name: 'Open Source', getanswers: false, competitor: true },
  { name: 'Desktop App', getanswers: false, competitor: true },
  { name: 'Read Receipts', getanswers: false, competitor: true },
  { name: 'Multi-Account Support', getanswers: true, competitor: true },
  { name: 'Smart Inbox', getanswers: true, competitor: false },
  { name: 'Send Later', getanswers: true, competitor: true },
  { name: 'Learns Your Style', getanswers: true, competitor: false },
  { name: 'Gmail Integration', getanswers: true, competitor: true },
  { name: 'Self-Hostable', getanswers: false, competitor: true },
  { name: 'Free Tier', getanswers: true, competitor: true },
];

const testimonials = [
  {
    quote: "I loved Mailspring for its open-source nature, but GetAnswers saves me hours by writing responses. Different tools for different needs.",
    author: "Erik Johansson",
    role: "Developer, Sweden",
    metric: "3 hrs saved daily",
  },
  {
    quote: "Mailspring is great free software. But when I needed AI to handle my inbox, GetAnswers was the clear choice.",
    author: "Laura Schmidt",
    role: "Freelance Designer",
    metric: "75% auto-drafted",
  },
];

const comparisonPoints = [
  {
    title: 'Core Approach',
    getanswers: 'AI writes your email responses. You review, edit, and approve.',
    competitor: 'Open-source desktop email client. You write everything.',
    winner: 'getanswers',
  },
  {
    title: 'Open Source & Privacy',
    getanswers: 'SaaS platform with enterprise security. Transparent privacy policy.',
    competitor: 'Fully open source. Can review code and self-host.',
    winner: 'competitor',
  },
  {
    title: 'Cost',
    getanswers: 'Subscription model with free trial. AI features require payment.',
    competitor: 'Free core features. Pro features at low cost.',
    winner: 'competitor',
  },
];

const renderFeatureValue = (value: boolean | string) => {
  if (value === true) return <Check className="w-5 h-5 text-emerald-500" />;
  if (value === 'partial') return <span className="text-amber-500 text-sm font-medium">Partial</span>;
  return <X className="w-5 h-5 text-gray-500" />;
};

export function CompareMailspring() {
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
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">Mailspring</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto mb-8">
            Open-source email client vs AI that writes your responses.
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
              <strong className="text-white">Mailspring</strong> is a beautiful open-source email client for those who value transparency.
              <strong className="text-white"> GetAnswers</strong> uses AI to automate responses. Different philosophies—control vs automation. Choose what matters to you.
            </p>
          </div>
        </div>
      </section>

      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">AI Automation vs Open Source</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-cyan-500/10 border border-cyan-500/30 rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <Bot className="w-8 h-8 text-cyan-400" />
                <h3 className="text-xl font-semibold text-cyan-400">GetAnswers: AI Writing</h3>
              </div>
              <ul className="space-y-3 text-gray-300">
                <li className="flex items-start gap-2"><Check className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" /><span>AI drafts all responses</span></li>
                <li className="flex items-start gap-2"><Check className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" /><span>Learns your voice and style</span></li>
                <li className="flex items-start gap-2"><Check className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" /><span>Hours saved every day</span></li>
              </ul>
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <Code className="w-8 h-8 text-gray-400" />
                <h3 className="text-xl font-semibold text-gray-400">Mailspring: Open Source</h3>
              </div>
              <ul className="space-y-3 text-gray-300">
                <li className="flex items-start gap-2"><Check className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" /><span>Fully open source</span></li>
                <li className="flex items-start gap-2"><Check className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" /><span>Free core features</span></li>
                <li className="flex items-start gap-2"><X className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" /><span>No AI capabilities</span></li>
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
                      <span className="font-semibold text-gray-400">Mailspring</span>
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
                  <th className="text-center py-4 px-4 text-gray-300">Mailspring</th>
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
          <h2 className="text-3xl font-bold text-white text-center mb-12">Why Developers Switch</h2>
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
          <h2 className="text-4xl font-bold text-white mb-6">AI-Powered Email Response</h2>
          <p className="text-xl text-gray-400 mb-8">Let AI handle your inbox while you focus on what matters.</p>
          <Link to="/register" className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-semibold rounded-lg hover:from-cyan-600 hover:to-blue-600 transition-all">
            Start Free Trial <ArrowRight className="w-5 h-5" />
          </Link>
          <p className="text-gray-500 mt-6 text-sm">14-day free trial • No credit card required</p>
        </div>
      </section>
    </div>
  );
}
