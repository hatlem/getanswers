import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { CheckCircle, Download, ArrowRight, Mail, Bot, Zap, MessageSquare } from "lucide-react";

export default function LeadMagnetThankYou() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      <div className="container mx-auto px-4 py-16 md:py-24">
        <div className="max-w-2xl mx-auto text-center">
          {/* Success Icon */}
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-8">
            <CheckCircle className="h-10 w-10 text-green-500" />
          </div>

          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Your Guide is Ready!
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Download your inbox zero guide below.
          </p>

          {/* Download Card */}
          <div className="mb-12">
            <Card className="border-2 border-green-200">
              <CardContent className="flex items-center justify-between p-6">
                <div className="text-left">
                  <h3 className="font-semibold text-lg">Inbox Zero Guide</h3>
                  <p className="text-gray-500 text-sm">Complete methodology & templates</p>
                </div>
                <a href="/lead-magnets/inbox-zero-guide.md" download className="inline-flex">
                  <Button className="bg-green-500 hover:bg-green-600">
                    <Download className="h-4 w-4 mr-2" />
                    Download
                  </Button>
                </a>
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
                    We've also sent the download link to your email.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Next Steps */}
          <div className="text-left bg-white rounded-xl p-8 shadow-lg border">
            <h2 className="text-2xl font-bold mb-6">Want AI to Handle Your Emails?</h2>

            <div className="space-y-4 mb-6">
              <div className="flex items-center gap-3">
                <Bot className="h-5 w-5 text-cyan-600" />
                <span>AI-powered email responses</span>
              </div>
              <div className="flex items-center gap-3">
                <Zap className="h-5 w-5 text-cyan-600" />
                <span>Smart inbox categorization</span>
              </div>
              <div className="flex items-center gap-3">
                <MessageSquare className="h-5 w-5 text-cyan-600" />
                <span>Automated follow-ups</span>
              </div>
            </div>

            <p className="text-gray-600 text-sm mb-6">
              GetAnswers uses AI to draft replies, categorize emails, and help you maintain inbox zero automatically.
            </p>

            <Link to="/pricing">
              <Button className="bg-cyan-600 hover:bg-cyan-700">
                Start Free Trial
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
