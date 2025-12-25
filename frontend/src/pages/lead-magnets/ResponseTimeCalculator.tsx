import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { Clock, Mail, TrendingUp, Download, Calculator } from "lucide-react";

export default function ResponseTimeCalculator() {
  const navigate = useNavigate();

  // Calculator inputs
  const [emailsPerDay, setEmailsPerDay] = useState(50);
  const [avgReadTime, setAvgReadTime] = useState(2); // minutes
  const [avgResponseTime, setAvgResponseTime] = useState(5); // minutes
  const [hourlyRate, setHourlyRate] = useState(50); // dollars

  // Lead capture
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [showEmailCapture, setShowEmailCapture] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Calculations
  const totalMinutesPerDay = emailsPerDay * (avgReadTime + avgResponseTime);
  const hoursPerDay = (totalMinutesPerDay / 60).toFixed(1);
  const hoursPerWeek = (parseFloat(hoursPerDay) * 5).toFixed(1);
  const costPerDay = (parseFloat(hoursPerDay) * hourlyRate).toFixed(0);
  const costPerMonth = (parseFloat(costPerDay) * 22).toFixed(0);
  const costPerYear = (parseFloat(costPerMonth) * 12).toFixed(0);

  // AI savings potential (assume 40% time savings)
  const aiSavingsHoursPerWeek = (parseFloat(hoursPerWeek) * 0.4).toFixed(1);
  const aiSavingsCostPerMonth = (parseFloat(costPerMonth) * 0.4).toFixed(0);
  const aiSavingsCostPerYear = (parseFloat(costPerYear) * 0.4).toFixed(0);

  const handleDownload = () => {
    setShowEmailCapture(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api/lead-magnets/capture`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email,
            name: name || undefined,
            source: "response-time-calculator",
          }),
        }
      );

      const data = await response.json();

      if (data.success) {
        localStorage.setItem("lead_magnet_calculator", data.lead_id);
        navigate("/lead-magnets/thank-you?source=response-time-calculator");
      }
    } catch (error) {
      console.error("Lead capture failed:", error);
      alert("Something went wrong. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <span className="inline-block bg-blue-100 text-blue-700 px-4 py-1 rounded-full text-sm font-medium mb-4">
            FREE INTERACTIVE CALCULATOR
          </span>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Email Response Time Calculator
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Calculate exactly how much time and money you're spending on email,
            and discover your AI automation savings potential.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
          {/* Calculator */}
          <div className="bg-white rounded-lg shadow-lg p-8 border border-gray-200">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <Calculator className="h-6 w-6 text-blue-600" />
              Your Email Metrics
            </h2>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Emails per day:{" "}
                  <span className="text-blue-600 font-bold">{emailsPerDay}</span>
                </label>
                <input
                  type="range"
                  min="10"
                  max="200"
                  value={emailsPerDay}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmailsPerDay(parseInt(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>10</span>
                  <span>200</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Avg. read time (minutes):{" "}
                  <span className="text-blue-600 font-bold">{avgReadTime}</span>
                </label>
                <input
                  type="range"
                  min="0.5"
                  max="10"
                  step="0.5"
                  value={avgReadTime}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setAvgReadTime(parseFloat(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>0.5</span>
                  <span>10</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Avg. response time (minutes):{" "}
                  <span className="text-blue-600 font-bold">{avgResponseTime}</span>
                </label>
                <input
                  type="range"
                  min="1"
                  max="30"
                  value={avgResponseTime}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setAvgResponseTime(parseInt(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>1</span>
                  <span>30</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Your hourly rate ($):{" "}
                  <span className="text-blue-600 font-bold">${hourlyRate}</span>
                </label>
                <input
                  type="range"
                  min="25"
                  max="300"
                  step="5"
                  value={hourlyRate}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setHourlyRate(parseInt(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>$25</span>
                  <span>$300</span>
                </div>
              </div>
            </div>
          </div>

          {/* Results */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-lg p-8 border border-gray-200">
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                <Clock className="h-6 w-6 text-orange-600" />
                Time Investment
              </h2>

              <div className="space-y-4">
                <div className="flex justify-between items-center pb-3 border-b">
                  <span className="text-gray-600">Per Day</span>
                  <span className="text-2xl font-bold text-gray-900">
                    {hoursPerDay} hrs
                  </span>
                </div>
                <div className="flex justify-between items-center pb-3 border-b">
                  <span className="text-gray-600">Per Week</span>
                  <span className="text-2xl font-bold text-gray-900">
                    {hoursPerWeek} hrs
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Per Month (22 days)</span>
                  <span className="text-2xl font-bold text-gray-900">
                    {(parseFloat(hoursPerDay) * 22).toFixed(0)} hrs
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-8 border border-gray-200">
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                <Mail className="h-6 w-6 text-red-600" />
                Cost Analysis
              </h2>

              <div className="space-y-4">
                <div className="flex justify-between items-center pb-3 border-b">
                  <span className="text-gray-600">Per Month</span>
                  <span className="text-2xl font-bold text-gray-900">
                    ${costPerMonth}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Per Year</span>
                  <span className="text-2xl font-bold text-gray-900">
                    ${costPerYear}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg shadow-lg p-8 border-2 border-green-200">
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                <TrendingUp className="h-6 w-6 text-green-600" />
                AI Automation Savings
              </h2>

              <div className="space-y-4">
                <div className="flex justify-between items-center pb-3 border-b border-green-200">
                  <span className="text-gray-700">Time saved/week</span>
                  <span className="text-2xl font-bold text-green-700">
                    {aiSavingsHoursPerWeek} hrs
                  </span>
                </div>
                <div className="flex justify-between items-center pb-3 border-b border-green-200">
                  <span className="text-gray-700">Cost saved/month</span>
                  <span className="text-2xl font-bold text-green-700">
                    ${aiSavingsCostPerMonth}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-700">Cost saved/year</span>
                  <span className="text-3xl font-bold text-green-700">
                    ${aiSavingsCostPerYear}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        {!showEmailCapture ? (
          <div className="mt-12 text-center bg-blue-600 rounded-lg p-8 max-w-2xl mx-auto">
            <h3 className="text-2xl font-bold text-white mb-4">
              Download Full ROI Report
            </h3>
            <p className="text-blue-100 mb-6">
              Get a detailed breakdown of your email costs, time savings
              opportunities, and personalized automation recommendations.
            </p>
            <Button
              onClick={handleDownload}
              size="lg"
              variant="secondary"
              icon={<Download className="h-5 w-5" />}
            >
              Download Free Report
            </Button>
          </div>
        ) : (
          <div className="mt-12 max-w-md mx-auto bg-white rounded-lg shadow-xl p-8 border border-gray-200">
            <h3 className="text-2xl font-bold mb-4 text-center">
              Get Your Free Report
            </h3>
            <p className="text-gray-600 mb-6 text-center">
              Enter your email to receive the full analysis
            </p>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                type="text"
                placeholder="Your first name"
                value={name}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setName(e.target.value)}
              />
              <Input
                type="email"
                placeholder="Your email address"
                value={email}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
                required
              />
              <Button type="submit" className="w-full" isLoading={isSubmitting}>
                {isSubmitting ? "Sending..." : "Send Me the Report"}
              </Button>
              <p className="text-xs text-gray-500 text-center">
                No spam, ever. Unsubscribe anytime.
              </p>
            </form>
          </div>
        )}
      </section>
    </div>
  );
}
