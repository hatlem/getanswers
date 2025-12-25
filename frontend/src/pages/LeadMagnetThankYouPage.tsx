import { useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { Card, CardContent } from "@/components/ui/card";
import { CheckCircle, Download, ArrowRight, Mail, Bot, Zap, MessageSquare } from "lucide-react";
import { SEO } from "@/components/SEO";

const LEAD_MAGNET_CONFIG: Record<string, {
  title: string;
  fileName: string;
  description: string;
  color: string;
}> = {
  'email-prompts': {
    title: '50+ AI Email Prompts',
    fileName: 'email-automation-prompts.pdf',
    description: 'Ready-to-use AI prompts for email automation',
    color: 'blue'
  },
  'triage-framework': {
    title: 'Email Triage Framework',
    fileName: 'email-triage-framework.pdf',
    description: 'The 4-category decision system',
    color: 'purple'
  },
  'policy-template': {
    title: 'AI Email Agent Policy',
    fileName: 'ai-email-policy-template.pdf',
    description: 'Complete policy template for AI agents',
    color: 'green'
  },
  'time-calculator': {
    title: 'Email Time Calculator',
    fileName: 'email-time-roi-calculator.xlsx',
    description: 'Interactive ROI calculation spreadsheet',
    color: 'orange'
  },
  'inbox-checklist': {
    title: '30-Day Inbox Zero Checklist',
    fileName: 'inbox-zero-30-day-checklist.pdf',
    description: 'Daily tasks and weekly reviews',
    color: 'teal'
  }
};

export default function LeadMagnetThankYouPage() {
  const [searchParams] = useSearchParams();
  const source = searchParams.get('source') || 'email-prompts';
  const config = LEAD_MAGNET_CONFIG[source] || LEAD_MAGNET_CONFIG['email-prompts'];

  const colorClasses = {
    blue: { bg: 'bg-blue-50', border: 'border-blue-200', button: 'bg-blue-500 hover:bg-blue-600' },
    purple: { bg: 'bg-purple-50', border: 'border-purple-200', button: 'bg-purple-500 hover:bg-purple-600' },
    green: { bg: 'bg-green-50', border: 'border-green-200', button: 'bg-green-500 hover:bg-green-600' },
    orange: { bg: 'bg-orange-50', border: 'border-orange-200', button: 'bg-orange-500 hover:bg-orange-600' },
    teal: { bg: 'bg-teal-50', border: 'border-teal-200', button: 'bg-teal-500 hover:bg-teal-600' },
  };

  const colors = colorClasses[config.color as keyof typeof colorClasses];

  // Track download when page loads
  useEffect(() => {
    const leadId = localStorage.getItem(`lead_magnet_${source}`);
    if (leadId) {
      fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/lead-magnets/track-download/${leadId}`, {
        method: 'POST'
      }).catch(err => console.error('Failed to track download:', err));
    }
  }, [source]);

  const handleDownload = () => {
    // In production, this would trigger actual file download
    console.log(`Downloading: ${config.fileName}`);
    // You could also track additional downloads here
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      <SEO
        title={`Download ${config.title} - GetAnswers`}
        description={`Your free ${config.title} is ready to download. ${config.description}. Get started with AI-powered email automation.`}
        canonical="/lead-magnets/thank-you"
        noindex={true}
      />

      <div className="container mx-auto px-4 py-16 md:py-24">
        <div className="max-w-2xl mx-auto text-center">
          {/* Success Icon */}
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-8">
            <CheckCircle className="h-10 w-10 text-green-500" />
          </div>

          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Success! Your Download is Ready
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Get your free {config.title} below.
          </p>

          {/* Download Card */}
          <div className="mb-12">
            <Card className={`border-2 ${colors.border} ${colors.bg}`}>
              <CardContent className="flex items-center justify-between p-6">
                <div className="text-left flex-1">
                  <h3 className="font-semibold text-lg">{config.title}</h3>
                  <p className="text-gray-500 text-sm">{config.description}</p>
                </div>
                <Button
                  onClick={handleDownload}
                  className={`${colors.button} ml-4`}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Email Notice */}
          <Card className="bg-blue-50 border-blue-200 mb-12">
            <CardContent className="p-6">
              <div className="flex items-start gap-4">
                <Mail className="h-6 w-6 text-blue-500 mt-1" />
                <div className="text-left">
                  <h3 className="font-semibold text-blue-900">Check your inbox</h3>
                  <p className="text-blue-700 text-sm">
                    We've also sent the download link to your email. Check your spam folder if you don't see it.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Next Steps - GetAnswers CTA */}
          <div className="text-left bg-white rounded-xl p-8 shadow-lg border">
            <h2 className="text-2xl font-bold mb-4">Ready to Automate Your Email?</h2>
            <p className="text-gray-600 mb-6">
              GetAnswers is an AI-powered email agent that handles routine emails autonomously,
              so you can focus on what matters. It uses the same frameworks you just downloaded.
            </p>

            <div className="space-y-4 mb-6">
              <div className="flex items-center gap-3">
                <Bot className="h-5 w-5 text-cyan-600" />
                <span>AI drafts responses for your review</span>
              </div>
              <div className="flex items-center gap-3">
                <Zap className="h-5 w-5 text-cyan-600" />
                <span>Automatic email triage & categorization</span>
              </div>
              <div className="flex items-center gap-3">
                <MessageSquare className="h-5 w-5 text-cyan-600" />
                <span>Context-aware conversation tracking</span>
              </div>
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>Customizable autonomy levels</span>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              <Link to="/register" className="flex-1">
                <Button className="w-full bg-cyan-600 hover:bg-cyan-700">
                  Start Free Trial
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
              <Link to="/" className="flex-1">
                <Button variant="outline" className="w-full">
                  Learn More
                </Button>
              </Link>
            </div>

            <p className="text-xs text-gray-500 mt-4 text-center">
              No credit card required. 14-day free trial.
            </p>
          </div>

          {/* Additional Resources */}
          <div className="mt-12 text-center">
            <h3 className="text-lg font-semibold mb-4">More Free Resources</h3>
            <div className="flex flex-wrap gap-3 justify-center">
              {Object.entries(LEAD_MAGNET_CONFIG)
                .filter(([key]) => key !== source)
                .slice(0, 3)
                .map(([key, value]) => (
                  <Link
                    key={key}
                    to={`/lead-magnets/${key}`}
                    className="text-cyan-600 hover:text-cyan-700 text-sm underline"
                  >
                    {value.title}
                  </Link>
                ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
