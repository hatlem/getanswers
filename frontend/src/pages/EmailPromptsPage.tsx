import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle, Bot, Zap, Mail, MessageSquare, FileText, Target } from "lucide-react";
import { LeadMagnetSEO } from "@/components/SEO";

export default function EmailPromptsPage() {
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/lead-magnets/capture`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          name: name || undefined,
          source: 'email-prompts'
        })
      });

      const data = await response.json();

      if (data.success) {
        // Store access token in localStorage
        localStorage.setItem('lead_magnet_email_prompts', data.lead_id);
        navigate("/lead-magnets/thank-you?source=email-prompts");
      }
    } catch (error) {
      console.error('Lead capture failed:', error);
      alert('Something went wrong. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <LeadMagnetSEO
        title="50+ AI Email Automation Prompts - Free Download"
        description="Ready-to-use AI prompts for email triage, responses, and automation. Perfect for inbox zero and AI-powered email management. Free download."
        slug="email-prompts"
        keywords={['AI email prompts', 'email automation prompts', 'inbox zero prompts', 'AI email templates']}
      />

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 md:py-24">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <span className="inline-block bg-blue-100 text-blue-700 px-4 py-1 rounded-full text-sm font-medium mb-4">
              FREE AI PROMPTS LIBRARY
            </span>
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              50+ AI Email Automation Prompts
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Ready-to-use AI prompts for email triage, responses, and automation. Perfect for inbox zero and AI-powered email management.
            </p>

            <div className="space-y-4 mb-8">
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>50+ copy-paste AI prompts</span>
              </div>
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>Email triage & categorization</span>
              </div>
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>Auto-response templates</span>
              </div>
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>Priority scoring & routing</span>
              </div>
            </div>
          </div>

          {/* Signup Form */}
          <Card className="shadow-xl border-0">
            <CardHeader className="text-center pb-2">
              <CardTitle className="text-2xl">Get Free Prompts</CardTitle>
              <CardDescription>
                Enter your email to download instantly
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <Input
                    type="text"
                    placeholder="Your first name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="h-12"
                  />
                </div>
                <div>
                  <Input
                    type="email"
                    placeholder="Your email address"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="h-12"
                  />
                </div>
                <Button
                  type="submit"
                  className="w-full h-12 text-lg bg-blue-600 hover:bg-blue-700"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? "Sending..." : "Get Free Prompts →"}
                </Button>
                <p className="text-xs text-gray-500 text-center">
                  No spam, ever. Unsubscribe anytime.
                </p>
              </form>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* What's Inside Section */}
      <section className="bg-gray-50 py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">What You'll Get</h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="border-2 hover:border-blue-200 transition-colors">
              <CardHeader>
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                  <Bot className="h-6 w-6 text-blue-600" />
                </div>
                <CardTitle>Email Triage</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-gray-600">
                  <li className="flex items-center gap-2">
                    <Target className="h-4 w-4" />
                    Urgency detection prompts
                  </li>
                  <li className="flex items-center gap-2">
                    <Target className="h-4 w-4" />
                    Category classification
                  </li>
                  <li className="flex items-center gap-2">
                    <Target className="h-4 w-4" />
                    Spam filtering AI
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-2 hover:border-blue-200 transition-colors">
              <CardHeader>
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                  <MessageSquare className="h-6 w-6 text-blue-600" />
                </div>
                <CardTitle>Smart Responses</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-gray-600">
                  <li className="flex items-center gap-2">
                    <Zap className="h-4 w-4" />
                    Quick reply generation
                  </li>
                  <li className="flex items-center gap-2">
                    <Zap className="h-4 w-4" />
                    Tone adjustment
                  </li>
                  <li className="flex items-center gap-2">
                    <Zap className="h-4 w-4" />
                    Follow-up templates
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-2 hover:border-blue-200 transition-colors">
              <CardHeader>
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                  <FileText className="h-6 w-6 text-blue-600" />
                </div>
                <CardTitle>Automation Workflows</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-gray-600">
                  <li className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    Auto-filing rules
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    Meeting extraction
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    Task detection
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-blue-600 py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Stop Drowning in Email
          </h2>
          <p className="text-blue-100 mb-8 max-w-2xl mx-auto">
            These AI prompts will help you process your inbox 3x faster. Get started in minutes.
          </p>
          <Button
            size="lg"
            variant="secondary"
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          >
            Get Your Free Prompts Now
          </Button>
        </div>
      </section>
    </div>
  );
}
