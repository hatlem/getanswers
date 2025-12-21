import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle, Shield, FileText, Settings, Lock, Users } from "lucide-react";

export default function PolicyTemplatePage() {
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
          source: 'policy-template'
        })
      });

      const data = await response.json();

      if (data.success) {
        localStorage.setItem('lead_magnet_policy_template', data.lead_id);
        navigate("/lead-magnets/thank-you?source=policy-template");
      }
    } catch (error) {
      console.error('Lead capture failed:', error);
      alert('Something went wrong. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 md:py-24">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <span className="inline-block bg-green-100 text-green-700 px-4 py-1 rounded-full text-sm font-medium mb-4">
              FREE POLICY TEMPLATE
            </span>
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              AI Email Agent Policy Template
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Set clear guardrails for your AI email agent. Define what it can handle autonomously vs. what requires human approval.
            </p>

            <div className="space-y-4 mb-8">
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>Autonomy level configurations</span>
              </div>
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>Risk threshold settings</span>
              </div>
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>Approval workflow templates</span>
              </div>
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>Compliance guidelines</span>
              </div>
            </div>
          </div>

          {/* Signup Form */}
          <Card className="shadow-xl border-0">
            <CardHeader className="text-center pb-2">
              <CardTitle className="text-2xl">Get Free Template</CardTitle>
              <CardDescription>
                Download the complete policy framework
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
                  className="w-full h-12 text-lg bg-green-600 hover:bg-green-700"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? "Sending..." : "Download Template →"}
                </Button>
                <p className="text-xs text-gray-500 text-center">
                  No spam, ever. Unsubscribe anytime.
                </p>
              </form>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Policy Levels */}
      <section className="bg-gray-50 py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">3 Autonomy Levels Included</h2>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <Card className="border-2 border-blue-200">
              <CardHeader>
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                  <Shield className="h-6 w-6 text-blue-600" />
                </div>
                <CardTitle>Low Autonomy</CardTitle>
                <CardDescription>High human oversight</CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-gray-600 text-sm">
                  <li>• AI suggests, you approve all</li>
                  <li>• Review every response</li>
                  <li>• Best for sensitive industries</li>
                  <li>• Maximum control & safety</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-2 border-green-200 bg-green-50">
              <CardHeader>
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                  <Settings className="h-6 w-6 text-green-600" />
                </div>
                <CardTitle>Medium Autonomy</CardTitle>
                <CardDescription>Balanced approach</CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-gray-600 text-sm">
                  <li>• Auto-handle routine emails</li>
                  <li>• Human approval for risks</li>
                  <li>• Most popular setting</li>
                  <li>• 70% time savings</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-2 border-purple-200">
              <CardHeader>
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                  <Lock className="h-6 w-6 text-purple-600" />
                </div>
                <CardTitle>High Autonomy</CardTitle>
                <CardDescription>Trust but verify</CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-gray-600 text-sm">
                  <li>• AI handles most emails</li>
                  <li>• Audit trail & rollback</li>
                  <li>• For experienced users</li>
                  <li>• 90% automation rate</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* What's Inside */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Template Includes</h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <Card>
              <CardHeader>
                <FileText className="h-8 w-8 text-green-600 mb-2" />
                <CardTitle>Risk Categories</CardTitle>
              </CardHeader>
              <CardContent className="text-gray-600">
                Pre-defined risk levels for different email types with clear escalation rules.
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Users className="h-8 w-8 text-green-600 mb-2" />
                <CardTitle>Approval Workflows</CardTitle>
              </CardHeader>
              <CardContent className="text-gray-600">
                Who approves what, when to escalate, and how to handle edge cases.
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Shield className="h-8 w-8 text-green-600 mb-2" />
                <CardTitle>Compliance Checklist</CardTitle>
              </CardHeader>
              <CardContent className="text-gray-600">
                Ensure your AI agent meets regulatory requirements for your industry.
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Settings className="h-8 w-8 text-green-600 mb-2" />
                <CardTitle>Configuration Guide</CardTitle>
              </CardHeader>
              <CardContent className="text-gray-600">
                Step-by-step setup instructions to implement the policy in your organization.
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Lock className="h-8 w-8 text-green-600 mb-2" />
                <CardTitle>Security Rules</CardTitle>
              </CardHeader>
              <CardContent className="text-gray-600">
                Data handling policies, PII protection, and security best practices.
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CheckCircle className="h-8 w-8 text-green-600 mb-2" />
                <CardTitle>Testing Scenarios</CardTitle>
              </CardHeader>
              <CardContent className="text-gray-600">
                Real-world examples to validate your policy is working correctly.
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-green-600 py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Deploy AI Email Agents Safely
          </h2>
          <p className="text-green-100 mb-8 max-w-2xl mx-auto">
            This policy template is battle-tested by teams managing 10,000+ emails per month.
          </p>
          <Button
            size="lg"
            variant="secondary"
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          >
            Get Your Free Template
          </Button>
        </div>
      </section>
    </div>
  );
}
