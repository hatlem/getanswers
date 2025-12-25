import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { CheckCircle, Clock, TrendingDown, DollarSign, BarChart3, Calculator } from "lucide-react";

export default function TimeCalculatorPage() {
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
          source: 'time-calculator'
        })
      });

      const data = await response.json();

      if (data.success) {
        localStorage.setItem('lead_magnet_time_calculator', data.lead_id);
        navigate("/lead-magnets/thank-you?source=time-calculator");
      }
    } catch (error) {
      console.error('Lead capture failed:', error);
      alert('Something went wrong. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-orange-50 to-white">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 md:py-24">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <span className="inline-block bg-orange-100 text-orange-700 px-4 py-1 rounded-full text-sm font-medium mb-4">
              FREE ROI CALCULATOR
            </span>
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Email Response Time Calculator
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Calculate exactly how much time you're spending on email and what AI automation could save you. Interactive spreadsheet included.
            </p>

            <div className="space-y-4 mb-8">
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>Time spent per email category</span>
              </div>
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>ROI calculator for automation</span>
              </div>
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>Cost analysis framework</span>
              </div>
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>Productivity benchmarks</span>
              </div>
            </div>
          </div>

          {/* Signup Form */}
          <Card className="shadow-xl border-0">
            <CardHeader className="text-center pb-2">
              <CardTitle className="text-2xl">Get Free Calculator</CardTitle>
              <CardDescription>
                Download the interactive spreadsheet
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
                  className="w-full h-12 text-lg bg-orange-600 hover:bg-orange-700"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? "Sending..." : "Get Free Calculator →"}
                </Button>
                <p className="text-xs text-gray-500 text-center">
                  No spam, ever. Unsubscribe anytime.
                </p>
              </form>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Stats Preview */}
      <section className="bg-gray-50 py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-4">Did You Know?</h2>
          <p className="text-center text-gray-600 mb-12 max-w-2xl mx-auto">
            The average professional spends these amounts on email:
          </p>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <Card className="text-center border-2 border-orange-200">
              <CardContent className="pt-6">
                <Clock className="h-12 w-12 text-orange-600 mx-auto mb-4" />
                <div className="text-4xl font-bold text-gray-900 mb-2">2.5 hrs</div>
                <div className="text-gray-600">per day on email</div>
              </CardContent>
            </Card>

            <Card className="text-center border-2 border-orange-200">
              <CardContent className="pt-6">
                <DollarSign className="h-12 w-12 text-orange-600 mx-auto mb-4" />
                <div className="text-4xl font-bold text-gray-900 mb-2">$15k</div>
                <div className="text-gray-600">annual cost per employee</div>
              </CardContent>
            </Card>

            <Card className="text-center border-2 border-orange-200">
              <CardContent className="pt-6">
                <TrendingDown className="h-12 w-12 text-orange-600 mx-auto mb-4" />
                <div className="text-4xl font-bold text-gray-900 mb-2">28%</div>
                <div className="text-gray-600">of workday lost to email</div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Calculator Features */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">What's Inside the Calculator</h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <Card>
              <CardHeader>
                <Calculator className="h-8 w-8 text-orange-600 mb-2" />
                <CardTitle>Time Audit</CardTitle>
              </CardHeader>
              <CardContent className="text-gray-600">
                Input your daily email volume and get a breakdown of time spent on reading, writing, and managing emails.
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <BarChart3 className="h-8 w-8 text-orange-600 mb-2" />
                <CardTitle>Category Analysis</CardTitle>
              </CardHeader>
              <CardContent className="text-gray-600">
                Break down time by email type: urgent, important, routine, and spam/noise.
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <DollarSign className="h-8 w-8 text-orange-600 mb-2" />
                <CardTitle>ROI Calculator</CardTitle>
              </CardHeader>
              <CardContent className="text-gray-600">
                Calculate the dollar value of time saved with different automation levels.
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <TrendingDown className="h-8 w-8 text-orange-600 mb-2" />
                <CardTitle>Automation Impact</CardTitle>
              </CardHeader>
              <CardContent className="text-gray-600">
                See potential time savings with low, medium, and high autonomy AI settings.
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Clock className="h-8 w-8 text-orange-600 mb-2" />
                <CardTitle>Response Metrics</CardTitle>
              </CardHeader>
              <CardContent className="text-gray-600">
                Track your average response time, email backlog, and inbox zero achievement.
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CheckCircle className="h-8 w-8 text-orange-600 mb-2" />
                <CardTitle>Benchmarks</CardTitle>
              </CardHeader>
              <CardContent className="text-gray-600">
                Compare your metrics against industry averages and best-in-class performers.
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="bg-gray-50 py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Perfect For</h2>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <Card>
              <CardContent className="pt-6">
                <h3 className="font-bold text-lg mb-3">Executives</h3>
                <p className="text-gray-600 text-sm">
                  Justify AI email tools to your team by showing concrete ROI numbers and time savings.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <h3 className="font-bold text-lg mb-3">Operations Teams</h3>
                <p className="text-gray-600 text-sm">
                  Identify bottlenecks in email workflows and prioritize automation opportunities.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <h3 className="font-bold text-lg mb-3">Individual Contributors</h3>
                <p className="text-gray-600 text-sm">
                  Understand where your time goes and make data-driven decisions about email habits.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-orange-600 py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Know Your Numbers
          </h2>
          <p className="text-orange-100 mb-8 max-w-2xl mx-auto">
            You can't improve what you don't measure. Get your free calculator now.
          </p>
          <Button
            size="lg"
            variant="secondary"
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          >
            Download Free Calculator
          </Button>
        </div>
      </section>
    </div>
  );
}
