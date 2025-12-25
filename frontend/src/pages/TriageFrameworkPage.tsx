import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { CheckCircle, Filter, Clock, AlertCircle, Archive, Trash2, Flag } from "lucide-react";

export default function TriageFrameworkPage() {
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
          source: 'triage-framework'
        })
      });

      const data = await response.json();

      if (data.success) {
        localStorage.setItem('lead_magnet_triage_framework', data.lead_id);
        navigate("/lead-magnets/thank-you?source=triage-framework");
      }
    } catch (error) {
      console.error('Lead capture failed:', error);
      alert('Something went wrong. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-50 to-white">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 md:py-24">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <span className="inline-block bg-purple-100 text-purple-700 px-4 py-1 rounded-full text-sm font-medium mb-4">
              FREE DECISION FRAMEWORK
            </span>
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Email Triage Decision Framework
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              The exact 4-step framework top executives use to process 200+ emails per day in under 30 minutes.
            </p>

            <div className="space-y-4 mb-8">
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>4-category classification system</span>
              </div>
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>2-minute decision rule</span>
              </div>
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>Priority matrix template</span>
              </div>
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>Auto-response guidelines</span>
              </div>
            </div>
          </div>

          {/* Signup Form */}
          <Card className="shadow-xl border-0">
            <CardHeader className="text-center pb-2">
              <CardTitle className="text-2xl">Download Free Framework</CardTitle>
              <CardDescription>
                Get instant access to the PDF guide
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <Input
                    type="text"
                    placeholder="Your first name"
                    value={name}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setName(e.target.value)}
                    className="h-12"
                  />
                </div>
                <div>
                  <Input
                    type="email"
                    placeholder="Your email address"
                    value={email}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
                    required
                    className="h-12"
                  />
                </div>
                <Button
                  type="submit"
                  className="w-full h-12 text-lg bg-purple-600 hover:bg-purple-700"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? "Sending..." : "Get Free Framework →"}
                </Button>
                <p className="text-xs text-gray-500 text-center">
                  No spam, ever. Unsubscribe anytime.
                </p>
              </form>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Framework Preview */}
      <section className="bg-gray-50 py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">The 4-Category System</h2>

          <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            <Card className="border-2 border-red-200 bg-red-50">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                    <Flag className="h-6 w-6 text-red-600" />
                  </div>
                  <CardTitle className="text-red-900">Urgent & Important</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700">
                  Deal with immediately. Crisis, deadlines, critical decisions. Process first.
                </p>
              </CardContent>
            </Card>

            <Card className="border-2 border-orange-200 bg-orange-50">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                    <Clock className="h-6 w-6 text-orange-600" />
                  </div>
                  <CardTitle className="text-orange-900">Not Urgent but Important</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700">
                  Schedule time blocks. Strategic work, planning, relationship building.
                </p>
              </CardContent>
            </Card>

            <Card className="border-2 border-yellow-200 bg-yellow-50">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                    <AlertCircle className="h-6 w-6 text-yellow-600" />
                  </div>
                  <CardTitle className="text-yellow-900">Urgent but Not Important</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700">
                  Delegate or automate. Interruptions, some calls, routine requests.
                </p>
              </CardContent>
            </Card>

            <Card className="border-2 border-gray-200 bg-gray-50">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                    <Archive className="h-6 w-6 text-gray-600" />
                  </div>
                  <CardTitle className="text-gray-900">Neither Urgent nor Important</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700">
                  Archive or delete. Time wasters, busy work, some newsletters.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">What's Inside</h2>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <Card>
              <CardHeader>
                <Filter className="h-8 w-8 text-purple-600 mb-2" />
                <CardTitle>Decision Rules</CardTitle>
              </CardHeader>
              <CardContent className="text-gray-600">
                Clear criteria for each category with real examples from executives processing 200+ emails daily.
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Clock className="h-8 w-8 text-purple-600 mb-2" />
                <CardTitle>Time Budgets</CardTitle>
              </CardHeader>
              <CardContent className="text-gray-600">
                How to allocate your email processing time across categories for maximum efficiency.
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Trash2 className="h-8 w-8 text-purple-600 mb-2" />
                <CardTitle>Automation Guide</CardTitle>
              </CardHeader>
              <CardContent className="text-gray-600">
                Which emails to automate, delegate, or eliminate completely from your workflow.
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-purple-600 py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Process Your Inbox 3x Faster
          </h2>
          <p className="text-purple-100 mb-8 max-w-2xl mx-auto">
            This framework has helped thousands of professionals achieve inbox zero. Download now.
          </p>
          <Button
            size="lg"
            variant="secondary"
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          >
            Get Free Framework Now
          </Button>
        </div>
      </section>
    </div>
  );
}
