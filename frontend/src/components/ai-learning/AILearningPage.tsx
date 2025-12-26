/**
 * AI Learning Page - Shows users how the AI is learning from their behavior
 *
 * This page displays:
 * - Writing style profile
 * - Edit pattern insights
 * - Learning statistics
 * - Ability to trigger analysis
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Brain, Sparkles, TrendingUp, RefreshCw, Check, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

// API types
interface WritingProfile {
  overall_tone: string;
  formality_level: number;
  warmth_level: number;
  avg_email_length: number;
  prefers_concise: boolean;
  uses_bullet_points: boolean;
  common_greetings: string[];
  common_closings: string[];
  sample_size: number;
  confidence: number;
  last_updated: string;
}

interface StyleProfileResponse {
  has_profile: boolean;
  profile?: WritingProfile;
  last_updated?: string;
  sample_size: number;
  confidence: number;
}

interface LearningStats {
  has_writing_profile: boolean;
  writing_profile_confidence: number;
  writing_profile_sample_size: number;
  total_edits_analyzed: number;
  avg_edit_percentage: number;
  has_sufficient_data: boolean;
  recommendations: string[];
}

// API functions
const apiClient = {
  getProfile: async (): Promise<StyleProfileResponse> => {
    const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/ai-learning/profile`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });
    if (!response.ok) throw new Error('Failed to fetch profile');
    return response.json();
  },

  analyzeStyle: async (): Promise<any> => {
    const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/ai-learning/analyze`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({}),
    });
    if (!response.ok) throw new Error('Failed to analyze style');
    return response.json();
  },

  getStats: async (): Promise<LearningStats> => {
    const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/ai-learning/stats`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });
    if (!response.ok) throw new Error('Failed to fetch stats');
    return response.json();
  },
};

export function AILearningPage() {
  const queryClient = useQueryClient();
  const [analyzing, setAnalyzing] = useState(false);

  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ['aiProfile'],
    queryFn: apiClient.getProfile,
  });

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['aiStats'],
    queryFn: apiClient.getStats,
  });

  const analyzeMutation = useMutation({
    mutationFn: apiClient.analyzeStyle,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['aiProfile'] });
      queryClient.invalidateQueries({ queryKey: ['aiStats'] });
      setAnalyzing(false);
    },
    onError: () => {
      setAnalyzing(false);
    },
  });

  const handleAnalyze = () => {
    setAnalyzing(true);
    analyzeMutation.mutate();
  };

  return (
    <div className="min-h-screen bg-surface-base p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-text-primary flex items-center gap-3">
              <Brain className="w-8 h-8 text-accent-cyan" />
              AI Learning Center
            </h1>
            <p className="text-text-secondary mt-1">
              See how GetAnswers learns from your writing style and edits
            </p>
          </div>

          <Button
            onClick={handleAnalyze}
            disabled={analyzing || analyzeMutation.isPending}
            className="bg-accent-cyan hover:bg-accent-cyan/90"
          >
            {analyzing || analyzeMutation.isPending ? (
              <>
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 mr-2" />
                Analyze Now
              </>
            )}
          </Button>
        </div>

        {/* Stats Overview */}
        {!statsLoading && stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="border-surface-border bg-surface-card">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm text-text-secondary">Writing Profile</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-text-primary">
                    {stats.has_writing_profile ? Math.round(stats.writing_profile_confidence * 100) : 0}%
                  </span>
                  <span className="text-sm text-text-muted">confidence</span>
                </div>
                <p className="text-xs text-text-secondary mt-2">
                  Based on {stats.writing_profile_sample_size} sent emails
                </p>
              </CardContent>
            </Card>

            <Card className="border-surface-border bg-surface-card">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm text-text-secondary">Edits Analyzed</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-text-primary">
                    {stats.total_edits_analyzed}
                  </span>
                  <span className="text-sm text-text-muted">total</span>
                </div>
                <p className="text-xs text-text-secondary mt-2">
                  {stats.total_edits_analyzed >= 5 ? 'Sufficient for learning' : `Need ${5 - stats.total_edits_analyzed} more`}
                </p>
              </CardContent>
            </Card>

            <Card className="border-surface-border bg-surface-card">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm text-text-secondary">Learning Status</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  {stats.has_sufficient_data ? (
                    <>
                      <Check className="w-6 h-6 text-success" />
                      <span className="text-sm font-medium text-success">Optimized</span>
                    </>
                  ) : (
                    <>
                      <TrendingUp className="w-6 h-6 text-warning" />
                      <span className="text-sm font-medium text-warning">Learning</span>
                    </>
                  )}
                </div>
                <p className="text-xs text-text-secondary mt-2">
                  {stats.has_sufficient_data ? 'AI is fully trained' : 'AI is still learning'}
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Recommendations */}
        {stats && stats.recommendations.length > 0 && (
          <Card className="border-l-4 border-l-info bg-info-muted/20">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-info" />
                Recommendations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {stats.recommendations.map((rec, i) => (
                  <li key={i} className="text-sm text-text-secondary flex items-start gap-2">
                    <span className="text-info mt-0.5">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        {/* Writing Style Profile */}
        {!profileLoading && profile && profile.has_profile && profile.profile && (
          <Card className="border-surface-border bg-surface-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-accent-cyan" />
                Your Writing Style
              </CardTitle>
              <CardDescription>
                How the AI understands your communication preferences
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Tone & Formality */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-sm font-semibold text-text-primary mb-3">Communication Style</h4>
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between text-xs text-text-secondary mb-1">
                        <span>Overall Tone</span>
                        <span className="font-medium text-text-primary capitalize">
                          {profile.profile.overall_tone}
                        </span>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-xs text-text-secondary mb-1">
                        <span>Formality</span>
                        <span className="font-medium text-text-primary">
                          {profile.profile.formality_level}/5
                        </span>
                      </div>
                      <div className="h-2 bg-surface-border rounded-full overflow-hidden">
                        <motion.div
                          className="h-full bg-accent-cyan"
                          initial={{ width: 0 }}
                          animate={{ width: `${(profile.profile.formality_level / 5) * 100}%` }}
                          transition={{ duration: 0.5 }}
                        />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-xs text-text-secondary mb-1">
                        <span>Warmth</span>
                        <span className="font-medium text-text-primary">
                          {profile.profile.warmth_level}/5
                        </span>
                      </div>
                      <div className="h-2 bg-surface-border rounded-full overflow-hidden">
                        <motion.div
                          className="h-full bg-success"
                          initial={{ width: 0 }}
                          animate={{ width: `${(profile.profile.warmth_level / 5) * 100}%` }}
                          transition={{ duration: 0.5, delay: 0.1 }}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-text-primary mb-3">Writing Preferences</h4>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm">
                      <Check className={`w-4 h-4 ${profile.profile.prefers_concise ? 'text-success' : 'text-text-muted'}`} />
                      <span className="text-text-secondary">
                        Prefers concise emails (~{profile.profile.avg_email_length} words)
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Check className={`w-4 h-4 ${profile.profile.uses_bullet_points ? 'text-success' : 'text-text-muted'}`} />
                      <span className="text-text-secondary">Uses bullet points</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Common Phrases */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {profile.profile.common_greetings.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-text-primary mb-2">Common Greetings</h4>
                    <div className="flex flex-wrap gap-2">
                      {profile.profile.common_greetings.map((greeting, i) => (
                        <span
                          key={i}
                          className="px-3 py-1 bg-accent-cyan/10 text-accent-cyan text-sm rounded-full border border-accent-cyan/20"
                        >
                          {greeting}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {profile.profile.common_closings.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-text-primary mb-2">Common Closings</h4>
                    <div className="flex flex-wrap gap-2">
                      {profile.profile.common_closings.map((closing, i) => (
                        <span
                          key={i}
                          className="px-3 py-1 bg-success/10 text-success text-sm rounded-full border border-success/20"
                        >
                          {closing}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Metadata */}
              <div className="pt-4 border-t border-surface-border text-xs text-text-muted">
                <p>
                  Profile confidence: {Math.round(profile.profile.confidence * 100)}% •
                  Based on {profile.profile.sample_size} emails •
                  Last updated: {new Date(profile.profile.last_updated).toLocaleDateString()}
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* No Profile State */}
        {!profileLoading && profile && !profile.has_profile && (
          <Card className="border-surface-border bg-surface-card">
            <CardContent className="py-12 text-center">
              <Brain className="w-16 h-16 text-text-muted mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-text-primary mb-2">
                No Writing Profile Yet
              </h3>
              <p className="text-text-secondary mb-6 max-w-md mx-auto">
                Send a few emails through GetAnswers, then click "Analyze Now" to let the AI learn your writing style.
              </p>
              <Button onClick={handleAnalyze} disabled={analyzing} className="bg-accent-cyan hover:bg-accent-cyan/90">
                <Sparkles className="w-4 h-4 mr-2" />
                Analyze My Writing Style
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
