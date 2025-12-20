import { Check, X, Zap, Mail, Brain, Clock, Bot, Sparkles, ArrowRight, Star, Shield, Users, Inbox, Send } from 'lucide-react';
import { Link } from 'react-router-dom';

const competitors = [
  { name: 'GetAnswers', highlight: true },
  { name: 'SaneBox' },
  { name: 'Superhuman' },
  { name: 'Shortwave' },
  { name: 'Mailbutler' },
];

const features = [
  { name: 'AI-Generated Replies', getanswers: true, sanebox: false, superhuman: false, shortwave: 'partial', mailbutler: 'partial' },
  { name: 'Human-in-the-Loop Approval', getanswers: true, sanebox: false, superhuman: false, shortwave: false, mailbutler: false },
  { name: 'Auto-Draft Responses', getanswers: true, sanebox: false, superhuman: 'partial', shortwave: true, mailbutler: 'partial' },
  { name: 'Smart Email Triage', getanswers: true, sanebox: true, superhuman: true, shortwave: true, mailbutler: false },
  { name: 'Priority Inbox', getanswers: true, sanebox: true, superhuman: true, shortwave: true, mailbutler: 'partial' },
  { name: 'Email Scheduling', getanswers: true, sanebox: false, superhuman: true, shortwave: true, mailbutler: true },
  { name: 'Follow-up Reminders', getanswers: true, sanebox: true, superhuman: true, shortwave: true, mailbutler: true },
  { name: 'Gmail Integration', getanswers: true, sanebox: true, superhuman: true, shortwave: true, mailbutler: true },
  { name: 'Outlook Integration', getanswers: true, sanebox: true, superhuman: false, shortwave: false, mailbutler: true },
  { name: 'Custom IMAP/SMTP', getanswers: true, sanebox: true, superhuman: false, shortwave: false, mailbutler: false },
  { name: 'Team Collaboration', getanswers: true, sanebox: false, superhuman: true, shortwave: true, mailbutler: 'partial' },
  { name: 'Email Analytics', getanswers: true, sanebox: false, superhuman: true, shortwave: true, mailbutler: true },
  { name: 'Learns Your Style', getanswers: true, sanebox: false, superhuman: 'partial', shortwave: true, mailbutler: false },
  { name: 'One-Click Approve/Edit/Escalate', getanswers: true, sanebox: false, superhuman: false, shortwave: false, mailbutler: false },
  { name: 'Enterprise Security', getanswers: true, sanebox: true, superhuman: true, shortwave: true, mailbutler: 'partial' },
];

const keyAdvantages = [
  {
    icon: Brain,
    title: 'AI That Actually Replies',
    description: 'Not just sorting—GetAnswers drafts intelligent responses for every email, learning your voice and preferences.',
  },
  {
    icon: Users,
    title: 'Human-in-the-Loop',
    description: 'You stay in control. Review, approve, edit, or escalate every AI-generated response before it sends.',
  },
  {
    icon: Sparkles,
    title: 'Learns Your Style',
    description: 'The more you use it, the better it gets. Our AI learns your tone, common responses, and business context.',
  },
  {
    icon: Clock,
    title: 'Hours Back Daily',
    description: 'Most users save 2-3 hours per day on email. Focus on work that matters, not inbox management.',
  },
];

const testimonials = [
  {
    quote: "I was drowning in email. Now GetAnswers handles 80% of my inbox automatically. I just review and approve. It's like having a brilliant assistant.",
    author: "Sarah Chen",
    role: "Startup Founder",
    metric: "3 hrs/day saved",
  },
  {
    quote: "We tried Superhuman for speed, but GetAnswers actually writes the emails for us. The human-in-the-loop approval gives us confidence in every response.",
    author: "James Miller",
    role: "Customer Success Lead",
    metric: "5x faster responses",
  },
  {
    quote: "The AI learned our support tone within a week. Now it drafts responses that sound exactly like our team. We just click approve.",
    author: "Lisa Park",
    role: "Support Director",
    metric: "90% approval rate",
  },
];

const renderFeatureValue = (value: boolean | string) => {
  if (value === true) {
    return <Check className="w-5 h-5 text-emerald-500" />;
  }
  if (value === 'partial') {
    return <span className="text-amber-500 text-sm font-medium">Partial</span>;
  }
  return <X className="w-5 h-5 text-gray-400" />;
};

export function ComparePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      {/* Hero Section */}
      <section className="relative py-20 px-4 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 via-transparent to-blue-500/10" />
        <div className="max-w-6xl mx-auto text-center relative">
          <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-cyan-500/20 text-cyan-400 text-sm font-medium mb-6">
            <Zap className="w-4 h-4" />
            Agent-First Email
          </span>
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
            Your Inbox, on
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">
              Autopilot.
            </span>
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto mb-8">
            See how GetAnswers compares to traditional email tools.
            AI that doesn't just organize—it responds. With you in control.
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
              See Demo
            </Link>
          </div>
        </div>
      </section>

      {/* Key Advantages */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-4">
            Why Professionals Choose GetAnswers
          </h2>
          <p className="text-gray-400 text-center mb-12 max-w-2xl mx-auto">
            Other tools help you manage email. We help you conquer it with AI that actually writes your responses.
          </p>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {keyAdvantages.map((advantage, index) => (
              <div
                key={index}
                className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6 hover:border-cyan-500/50 transition-colors"
              >
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-cyan-500/20 to-blue-500/20 flex items-center justify-center mb-4">
                  <advantage.icon className="w-6 h-6 text-cyan-400" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{advantage.title}</h3>
                <p className="text-gray-400 text-sm">{advantage.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Comparison Table */}
      <section className="py-16 px-4 bg-slate-900/50">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-4">
            Feature Comparison
          </h2>
          <p className="text-gray-400 text-center mb-12 max-w-2xl mx-auto">
            From inbox organization to AI-powered response generation. See the difference.
          </p>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-4 px-4 text-gray-400 font-medium">Feature</th>
                  {competitors.map((competitor, index) => (
                    <th
                      key={index}
                      className={`text-center py-4 px-4 font-semibold ${
                        competitor.highlight
                          ? 'text-cyan-400 bg-cyan-500/10'
                          : 'text-gray-300'
                      }`}
                    >
                      {competitor.name}
                      {competitor.highlight && (
                        <span className="block text-xs font-normal text-cyan-400/70 mt-1">
                          Recommended
                        </span>
                      )}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {features.map((feature, index) => (
                  <tr
                    key={index}
                    className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors"
                  >
                    <td className="py-4 px-4 text-gray-300">{feature.name}</td>
                    <td className="text-center py-4 px-4 bg-cyan-500/5">
                      {renderFeatureValue(feature.getanswers)}
                    </td>
                    <td className="text-center py-4 px-4">
                      {renderFeatureValue(feature.sanebox)}
                    </td>
                    <td className="text-center py-4 px-4">
                      {renderFeatureValue(feature.superhuman)}
                    </td>
                    <td className="text-center py-4 px-4">
                      {renderFeatureValue(feature.shortwave)}
                    </td>
                    <td className="text-center py-4 px-4">
                      {renderFeatureValue(feature.mailbutler)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* The Problem Section */}
      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-gradient-to-br from-rose-500/10 to-orange-500/10 border border-rose-500/20 rounded-2xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
              <Inbox className="w-8 h-8 text-rose-400" />
              The Email Trap
            </h2>
            <div className="space-y-4 text-gray-300">
              <p>
                <strong className="text-white">You spend 3+ hours a day on email.</strong> Reading, responding, organizing,
                following up. It's exhausting, and it never ends.
              </p>
              <p>
                <strong className="text-white">Current tools just move the problem around.</strong> SaneBox sorts. Superhuman is faster.
                But you still have to write every response yourself.
              </p>
              <p>
                <strong className="text-white">GetAnswers is different:</strong> AI reads every email. Drafts intelligent responses.
                Shows you what to approve, edit, or escalate. You stay in control. Email becomes manageable again.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-16 px-4 bg-slate-900/50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            The GetAnswers Workflow
          </h2>
          <div className="space-y-6">
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 flex gap-6 items-start">
              <div className="w-12 h-12 rounded-full bg-cyan-500/20 flex items-center justify-center flex-shrink-0">
                <Mail className="w-6 h-6 text-cyan-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">Email Arrives</h3>
                <p className="text-gray-400">New emails hit your inbox. Our AI immediately reads and understands each one.</p>
              </div>
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 flex gap-6 items-start">
              <div className="w-12 h-12 rounded-full bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                <Bot className="w-6 h-6 text-blue-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">AI Drafts Response</h3>
                <p className="text-gray-400">Based on your style, past responses, and context, AI generates a complete reply.</p>
              </div>
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 flex gap-6 items-start">
              <div className="w-12 h-12 rounded-full bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
                <Users className="w-6 h-6 text-emerald-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">You Review</h3>
                <p className="text-gray-400">One click to approve. Or quickly edit. Or escalate to a team member. You're always in control.</p>
              </div>
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 flex gap-6 items-start">
              <div className="w-12 h-12 rounded-full bg-violet-500/20 flex items-center justify-center flex-shrink-0">
                <Send className="w-6 h-6 text-violet-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">Response Sent</h3>
                <p className="text-gray-400">Approved emails send automatically. Hours of work, done in minutes.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            Professionals Reclaiming Their Time
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            {testimonials.map((testimonial, index) => (
              <div
                key={index}
                className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6"
              >
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

      {/* Migration Section */}
      <section className="py-16 px-4 bg-slate-900/50">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/20 text-blue-400 text-sm font-medium mb-6">
            <Shield className="w-4 h-4" />
            Enterprise Security
          </div>
          <h2 className="text-3xl font-bold text-white mb-6">
            Your Data, Protected
          </h2>
          <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
            GetAnswers connects securely to Gmail, Outlook, or any IMAP provider.
            Your emails stay yours. We never train on your data.
          </p>
          <div className="grid md:grid-cols-3 gap-6 mb-12">
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
              <div className="text-3xl font-bold text-cyan-400 mb-2">SOC 2</div>
              <p className="text-gray-400">Type II Compliant</p>
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
              <div className="text-3xl font-bold text-cyan-400 mb-2">256-bit</div>
              <p className="text-gray-400">Encryption at Rest</p>
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
              <div className="text-3xl font-bold text-cyan-400 mb-2">GDPR</div>
              <p className="text-gray-400">Fully Compliant</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to Conquer Your Inbox?
          </h2>
          <p className="text-xl text-gray-400 mb-8">
            Join thousands of professionals saving hours daily with AI-powered email.
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
