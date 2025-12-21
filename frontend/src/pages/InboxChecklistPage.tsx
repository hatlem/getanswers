import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle, ListChecks, Trash2, Archive, Star, Calendar } from "lucide-react";

export default function InboxChecklistPage() {
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
          source: 'inbox-checklist'
        })
      });

      const data = await response.json();

      if (data.success) {
        localStorage.setItem('lead_magnet_inbox_checklist', data.lead_id);
        navigate("/lead-magnets/thank-you?source=inbox-checklist");
      }
    } catch (error) {
      console.error('Lead capture failed:', error);
      alert('Something went wrong. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-teal-50 to-white">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 md:py-24">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <span className="inline-block bg-teal-100 text-teal-700 px-4 py-1 rounded-full text-sm font-medium mb-4">
              FREE DAILY CHECKLIST
            </span>
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              30-Day Inbox Zero Checklist
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Follow this proven 30-day system to achieve and maintain inbox zero. Daily tasks, weekly reviews, and accountability tracking.
            </p>

            <div className="space-y-4 mb-8">
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>Daily 15-minute routine</span>
              </div>
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>Weekly cleanup checklist</span>
              </div>
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>Habit tracking template</span>
              </div>
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>Progress milestones</span>
              </div>
            </div>
          </div>

          {/* Signup Form */}
          <Card className="shadow-xl border-0">
            <CardHeader className="text-center pb-2">
              <CardTitle className="text-2xl">Get Free Checklist</CardTitle>
              <CardDescription>
                Start your inbox zero journey today
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
                  className="w-full h-12 text-lg bg-teal-600 hover:bg-teal-700"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? "Sending..." : "Get Free Checklist →"}
                </Button>
                <p className="text-xs text-gray-500 text-center">
                  No spam, ever. Unsubscribe anytime.
                </p>
              </form>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* 30-Day Journey */}
      <section className="bg-gray-50 py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Your 30-Day Journey</h2>

          <div className="grid md:grid-cols-4 gap-6 max-w-6xl mx-auto">
            <Card className="border-2 border-teal-200">
              <CardHeader>
                <div className="text-3xl font-bold text-teal-600 mb-2">Week 1</div>
                <CardTitle className="text-lg">Foundation</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-gray-600">
                <ul className="space-y-1">
                  <li>• Set up filters & folders</li>
                  <li>• Unsubscribe from noise</li>
                  <li>• Create response templates</li>
                  <li>• Archive old emails</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-2 border-teal-200">
              <CardHeader>
                <div className="text-3xl font-bold text-teal-600 mb-2">Week 2</div>
                <CardTitle className="text-lg">Habits</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-gray-600">
                <ul className="space-y-1">
                  <li>• Morning email routine</li>
                  <li>• Batch processing times</li>
                  <li>• 2-minute rule practice</li>
                  <li>• Zero notifications</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-2 border-teal-200">
              <CardHeader>
                <div className="text-3xl font-bold text-teal-600 mb-2">Week 3</div>
                <CardTitle className="text-lg">Optimization</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-gray-600">
                <ul className="space-y-1">
                  <li>• Automation rules</li>
                  <li>• AI-assisted triage</li>
                  <li>• Smart scheduling</li>
                  <li>• Delegation workflows</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-2 border-teal-200 bg-teal-50">
              <CardHeader>
                <div className="text-3xl font-bold text-teal-600 mb-2">Week 4</div>
                <CardTitle className="text-lg">Mastery</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-gray-600">
                <ul className="space-y-1">
                  <li>• Maintain inbox zero</li>
                  <li>• Weekly reviews</li>
                  <li>• Continuous improvement</li>
                  <li>• Help others succeed</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Daily Routine Preview */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Daily 15-Minute Routine</h2>

          <div className="max-w-3xl mx-auto">
            <Card className="border-2 border-teal-200">
              <CardContent className="pt-6">
                <div className="space-y-4">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-teal-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Trash2 className="h-6 w-6 text-teal-600" />
                    </div>
                    <div>
                      <h3 className="font-bold mb-1">1. Quick Delete (3 min)</h3>
                      <p className="text-gray-600 text-sm">
                        Scan for obvious spam, newsletters you don't read, and irrelevant emails. Delete immediately.
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-teal-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Star className="h-6 w-6 text-teal-600" />
                    </div>
                    <div>
                      <h3 className="font-bold mb-1">2. Star Urgent (2 min)</h3>
                      <p className="text-gray-600 text-sm">
                        Flag emails requiring immediate attention or response today. These go to your action list.
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-teal-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Archive className="h-6 w-6 text-teal-600" />
                    </div>
                    <div>
                      <h3 className="font-bold mb-1">3. Archive FYI (3 min)</h3>
                      <p className="text-gray-600 text-sm">
                        For-your-info emails with no action needed. Read if time permits, archive immediately.
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-teal-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Calendar className="h-6 w-6 text-teal-600" />
                    </div>
                    <div>
                      <h3 className="font-bold mb-1">4. Schedule Non-Urgent (4 min)</h3>
                      <p className="text-gray-600 text-sm">
                        Important but not urgent emails get scheduled for batch processing later this week.
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-teal-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <ListChecks className="h-6 w-6 text-teal-600" />
                    </div>
                    <div>
                      <h3 className="font-bold mb-1">5. Quick Wins (3 min)</h3>
                      <p className="text-gray-600 text-sm">
                        Handle any emails that take less than 2 minutes to respond to. Do them now.
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* What's Included */}
      <section className="bg-gray-50 py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Checklist Includes</h2>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <Card>
              <CardHeader>
                <ListChecks className="h-8 w-8 text-teal-600 mb-2" />
                <CardTitle>Daily Tasks</CardTitle>
              </CardHeader>
              <CardContent className="text-gray-600">
                Specific actions to complete each day, organized by priority and time commitment.
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Calendar className="h-8 w-8 text-teal-600 mb-2" />
                <CardTitle>Weekly Reviews</CardTitle>
              </CardHeader>
              <CardContent className="text-gray-600">
                End-of-week reflection prompts to identify what's working and what needs adjustment.
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CheckCircle className="h-8 w-8 text-teal-600 mb-2" />
                <CardTitle>Progress Tracker</CardTitle>
              </CardHeader>
              <CardContent className="text-gray-600">
                Visual habit tracker to maintain accountability and celebrate small wins daily.
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-teal-600 py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Start Your Inbox Zero Journey
          </h2>
          <p className="text-teal-100 mb-8 max-w-2xl mx-auto">
            Thousands of people have achieved inbox zero using this exact checklist. Your turn.
          </p>
          <Button
            size="lg"
            variant="secondary"
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          >
            Get Your Free Checklist
          </Button>
        </div>
      </section>
    </div>
  );
}
