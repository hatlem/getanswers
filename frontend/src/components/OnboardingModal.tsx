import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ArrowRight, ArrowLeft, Check, Mail, Zap, Shield, Sparkles, Server } from 'lucide-react';

type OnboardingStep = 'welcome' | 'connect' | 'smtp' | 'preferences';

interface OnboardingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConnectGmail: () => void;
  onConnectOutlook?: () => void;
  onConnectSMTP?: (credentials: SMTPCredentials) => Promise<void>;
}

interface SMTPCredentials {
  email: string;
  password: string;
  imap_server: string;
  imap_port: number;
  smtp_server: string;
  smtp_port: number;
  use_ssl: boolean;
}

const SMTP_PRESETS: Record<string, Omit<SMTPCredentials, 'email' | 'password'> & { note: string }> = {
  gmail: {
    imap_server: 'imap.gmail.com',
    imap_port: 993,
    smtp_server: 'smtp.gmail.com',
    smtp_port: 587,
    use_ssl: true,
    note: 'Use an App Password from Google Account settings'
  },
  outlook: {
    imap_server: 'outlook.office365.com',
    imap_port: 993,
    smtp_server: 'smtp.office365.com',
    smtp_port: 587,
    use_ssl: true,
    note: 'May require app password if 2FA is enabled'
  },
  yahoo: {
    imap_server: 'imap.mail.yahoo.com',
    imap_port: 993,
    smtp_server: 'smtp.mail.yahoo.com',
    smtp_port: 587,
    use_ssl: true,
    note: 'Generate an app password in Yahoo Account Security'
  },
  icloud: {
    imap_server: 'imap.mail.me.com',
    imap_port: 993,
    smtp_server: 'smtp.mail.me.com',
    smtp_port: 587,
    use_ssl: true,
    note: 'Generate an app-specific password in Apple ID settings'
  },
  custom: {
    imap_server: '',
    imap_port: 993,
    smtp_server: '',
    smtp_port: 587,
    use_ssl: true,
    note: 'Enter your mail server details'
  }
};

export function OnboardingModal({ isOpen, onClose, onConnectGmail, onConnectOutlook, onConnectSMTP }: OnboardingModalProps) {
  const [currentStep, setCurrentStep] = useState<OnboardingStep>('welcome');
  const [preferences, setPreferences] = useState({
    autoReply: true,
    dailyDigest: true,
    priorityInbox: true,
  });

  // SMTP form state
  const [smtpProvider, setSmtpProvider] = useState<string>('gmail');
  const [smtpCredentials, setSmtpCredentials] = useState<SMTPCredentials>({
    email: '',
    password: '',
    ...SMTP_PRESETS.gmail
  });
  const [smtpError, setSmtpError] = useState<string | null>(null);
  const [smtpLoading, setSmtpLoading] = useState(false);

  const handleNext = () => {
    if (currentStep === 'welcome') {
      setCurrentStep('connect');
    } else if (currentStep === 'connect') {
      setCurrentStep('preferences');
    } else if (currentStep === 'smtp') {
      setCurrentStep('preferences');
    } else {
      onClose();
    }
  };

  const handleBack = () => {
    if (currentStep === 'connect') {
      setCurrentStep('welcome');
    } else if (currentStep === 'smtp') {
      setCurrentStep('connect');
    } else if (currentStep === 'preferences') {
      setCurrentStep('connect');
    }
  };

  const handleProviderChange = (provider: string) => {
    setSmtpProvider(provider);
    const preset = SMTP_PRESETS[provider];
    if (preset) {
      setSmtpCredentials(prev => ({
        ...prev,
        imap_server: preset.imap_server,
        imap_port: preset.imap_port,
        smtp_server: preset.smtp_server,
        smtp_port: preset.smtp_port,
        use_ssl: preset.use_ssl,
      }));
    }
  };

  const handleSMTPConnect = async () => {
    if (!onConnectSMTP) {
      // Skip to preferences if no handler provided
      handleNext();
      return;
    }

    setSmtpError(null);
    setSmtpLoading(true);

    try {
      await onConnectSMTP(smtpCredentials);
      setCurrentStep('preferences');
    } catch (error) {
      setSmtpError(error instanceof Error ? error.message : 'Connection failed');
    } finally {
      setSmtpLoading(false);
    }
  };

  const stepIndex = currentStep === 'welcome' ? 0 : currentStep === 'connect' || currentStep === 'smtp' ? 1 : 2;

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        className="bg-surface-elevated rounded-2xl shadow-2xl w-full max-w-xl overflow-hidden border border-surface-border max-h-[90vh] flex flex-col"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-surface-border flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-cyan to-accent-purple flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-text-primary">
                {currentStep === 'welcome' && 'Welcome to GetAnswers'}
                {currentStep === 'connect' && 'Connect Your Email'}
                {currentStep === 'smtp' && 'SMTP/IMAP Setup'}
                {currentStep === 'preferences' && 'Set Your Preferences'}
              </h2>
              <p className="text-sm text-text-muted">Step {stepIndex + 1} of 3</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-text-muted hover:text-text-primary hover:bg-surface-hover rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto flex-1">
          <AnimatePresence mode="wait">
            {/* Step 1: Welcome */}
            {currentStep === 'welcome' && (
              <motion.div
                key="welcome"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
                className="space-y-6"
              >
                <div className="text-center py-4">
                  <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-accent-cyan/20 to-accent-purple/20 flex items-center justify-center">
                    <Zap className="w-10 h-10 text-accent-cyan" />
                  </div>
                  <h3 className="text-2xl font-bold text-text-primary mb-3">
                    Your inbox, on autopilot
                  </h3>
                  <p className="text-text-secondary max-w-sm mx-auto">
                    GetAnswers uses AI to triage, categorize, and handle your emails automatically.
                    Let's get you set up in just a few steps.
                  </p>
                </div>

                <div className="space-y-3">
                  {[
                    { icon: Mail, title: 'Connect your email', desc: 'Gmail, Outlook, or any IMAP/SMTP server' },
                    { icon: Shield, title: 'AI learns your style', desc: 'Smart responses that sound like you' },
                    { icon: Zap, title: 'Reclaim your time', desc: 'Focus on what matters most' },
                  ].map((item, i) => (
                    <div key={i} className="flex items-center gap-4 p-4 rounded-xl bg-surface-card border border-surface-border">
                      <div className="w-10 h-10 rounded-lg bg-accent-cyan/10 flex items-center justify-center flex-shrink-0">
                        <item.icon className="w-5 h-5 text-accent-cyan" />
                      </div>
                      <div>
                        <p className="font-medium text-text-primary">{item.title}</p>
                        <p className="text-sm text-text-muted">{item.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Step 2: Connect Email */}
            {currentStep === 'connect' && (
              <motion.div
                key="connect"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
                className="space-y-6"
              >
                <div className="text-center py-4">
                  <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-accent-cyan/20 to-accent-purple/20 flex items-center justify-center">
                    <Mail className="w-10 h-10 text-accent-cyan" />
                  </div>
                  <h3 className="text-xl font-bold text-text-primary mb-2">
                    Connect your inbox
                  </h3>
                  <p className="text-text-secondary text-sm">
                    We need access to read and organize your emails. Your data is secure and encrypted.
                  </p>
                </div>

                <div className="space-y-3">
                  {/* Google */}
                  <button
                    onClick={onConnectGmail}
                    className="w-full flex items-center justify-center gap-3 p-4 rounded-xl bg-white border-2 border-surface-border hover:border-accent-cyan/50 transition-all group"
                  >
                    <svg className="w-6 h-6" viewBox="0 0 24 24">
                      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                    </svg>
                    <span className="font-medium text-gray-700 group-hover:text-gray-900">Connect with Google</span>
                  </button>

                  {/* Microsoft/Outlook */}
                  <button
                    onClick={onConnectOutlook}
                    className="w-full flex items-center justify-center gap-3 p-4 rounded-xl bg-white border-2 border-surface-border hover:border-accent-cyan/50 transition-all group"
                  >
                    <svg className="w-6 h-6" viewBox="0 0 24 24">
                      <path fill="#0078D4" d="M24 7.387v10.478c0 .23-.08.424-.238.576-.16.154-.352.23-.578.23h-8.547v-6.959l1.6 1.229c.11.085.24.127.393.127.152 0 .283-.042.39-.127l7.218-5.57c.15-.113.224-.262.224-.449 0-.15-.05-.282-.152-.393-.102-.11-.232-.165-.392-.165H15.9l8.1 6.234V7.387c0-.23.08-.424.238-.577.16-.153.352-.23.578-.23h8.547c.226 0 .418.077.578.23.158.153.237.347.237.577z"/>
                      <path fill="#0078D4" d="M14.637 13.712v6.96H.8c-.225 0-.417-.077-.577-.23-.16-.153-.238-.347-.238-.577V7.387c0-.23.078-.424.238-.577.16-.153.352-.23.577-.23h13.837v7.132z"/>
                      <path fill="#28A8EA" d="M14.637 5.769v7.943H.015V4.672l7.311 4.508 7.311-4.508v1.097z"/>
                      <path fill="#0078D4" d="M14.637 4.672v1.097L7.326 10.28.015 4.672V3.575c0-.23.078-.423.238-.576.16-.154.352-.23.577-.23h13.03c.225 0 .417.076.577.23.16.153.238.346.238.576v1.097h-.038z"/>
                      <path fill="#50D9FF" d="M7.326 10.28l7.311 4.509v-1.077L7.326 9.18.015 13.712v1.077l7.311-4.509z"/>
                    </svg>
                    <span className="font-medium text-gray-700 group-hover:text-gray-900">Connect with Microsoft</span>
                  </button>

                  {/* SMTP/IMAP */}
                  <button
                    onClick={() => setCurrentStep('smtp')}
                    className="w-full flex items-center justify-center gap-3 p-4 rounded-xl bg-surface-card border-2 border-surface-border hover:border-accent-cyan/50 transition-all group"
                  >
                    <Server className="w-6 h-6 text-text-secondary group-hover:text-text-primary" />
                    <span className="font-medium text-text-secondary group-hover:text-text-primary">Connect with SMTP/IMAP</span>
                  </button>
                </div>

                <p className="text-center text-xs text-text-muted">
                  By connecting, you agree to our Terms of Service and Privacy Policy.
                  You can disconnect at any time.
                </p>
              </motion.div>
            )}

            {/* Step 2b: SMTP Setup */}
            {currentStep === 'smtp' && (
              <motion.div
                key="smtp"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
                className="space-y-4"
              >
                <div className="text-center py-2">
                  <h3 className="text-xl font-bold text-text-primary mb-2">
                    SMTP/IMAP Configuration
                  </h3>
                  <p className="text-text-secondary text-sm">
                    Connect any email provider using SMTP and IMAP.
                  </p>
                </div>

                {/* Provider preset selector */}
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-2">Email Provider</label>
                  <select
                    value={smtpProvider}
                    onChange={(e) => handleProviderChange(e.target.value)}
                    className="w-full p-3 rounded-lg bg-surface-card border border-surface-border text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-cyan/50"
                  >
                    <option value="gmail">Gmail</option>
                    <option value="outlook">Outlook / Office 365</option>
                    <option value="yahoo">Yahoo Mail</option>
                    <option value="icloud">iCloud Mail</option>
                    <option value="custom">Custom Server</option>
                  </select>
                  {SMTP_PRESETS[smtpProvider]?.note && (
                    <p className="mt-1 text-xs text-accent-cyan">{SMTP_PRESETS[smtpProvider].note}</p>
                  )}
                </div>

                {/* Credentials */}
                <div className="grid gap-3">
                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-1">Email Address</label>
                    <input
                      type="email"
                      value={smtpCredentials.email}
                      onChange={(e) => setSmtpCredentials(prev => ({ ...prev, email: e.target.value }))}
                      placeholder="you@example.com"
                      className="w-full p-3 rounded-lg bg-surface-card border border-surface-border text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent-cyan/50"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-1">Password / App Password</label>
                    <input
                      type="password"
                      value={smtpCredentials.password}
                      onChange={(e) => setSmtpCredentials(prev => ({ ...prev, password: e.target.value }))}
                      placeholder="Enter password or app password"
                      className="w-full p-3 rounded-lg bg-surface-card border border-surface-border text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent-cyan/50"
                    />
                  </div>
                </div>

                {/* Server settings (collapsible for custom) */}
                {smtpProvider === 'custom' && (
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-text-secondary mb-1">IMAP Server</label>
                      <input
                        type="text"
                        value={smtpCredentials.imap_server}
                        onChange={(e) => setSmtpCredentials(prev => ({ ...prev, imap_server: e.target.value }))}
                        placeholder="imap.example.com"
                        className="w-full p-2 rounded-lg bg-surface-card border border-surface-border text-text-primary text-sm focus:outline-none focus:ring-2 focus:ring-accent-cyan/50"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-text-secondary mb-1">IMAP Port</label>
                      <input
                        type="number"
                        value={smtpCredentials.imap_port}
                        onChange={(e) => setSmtpCredentials(prev => ({ ...prev, imap_port: parseInt(e.target.value) || 993 }))}
                        className="w-full p-2 rounded-lg bg-surface-card border border-surface-border text-text-primary text-sm focus:outline-none focus:ring-2 focus:ring-accent-cyan/50"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-text-secondary mb-1">SMTP Server</label>
                      <input
                        type="text"
                        value={smtpCredentials.smtp_server}
                        onChange={(e) => setSmtpCredentials(prev => ({ ...prev, smtp_server: e.target.value }))}
                        placeholder="smtp.example.com"
                        className="w-full p-2 rounded-lg bg-surface-card border border-surface-border text-text-primary text-sm focus:outline-none focus:ring-2 focus:ring-accent-cyan/50"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-text-secondary mb-1">SMTP Port</label>
                      <input
                        type="number"
                        value={smtpCredentials.smtp_port}
                        onChange={(e) => setSmtpCredentials(prev => ({ ...prev, smtp_port: parseInt(e.target.value) || 587 }))}
                        className="w-full p-2 rounded-lg bg-surface-card border border-surface-border text-text-primary text-sm focus:outline-none focus:ring-2 focus:ring-accent-cyan/50"
                      />
                    </div>
                  </div>
                )}

                {smtpError && (
                  <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
                    {smtpError}
                  </div>
                )}

                <button
                  onClick={handleSMTPConnect}
                  disabled={smtpLoading || !smtpCredentials.email || !smtpCredentials.password}
                  className="w-full flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-accent-cyan to-accent-purple text-white font-medium hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {smtpLoading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Testing Connection...
                    </>
                  ) : (
                    <>
                      Connect
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </motion.div>
            )}

            {/* Step 3: Preferences */}
            {currentStep === 'preferences' && (
              <motion.div
                key="preferences"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
                className="space-y-6"
              >
                <div className="text-center py-4">
                  <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-accent-cyan/20 to-accent-purple/20 flex items-center justify-center">
                    <Shield className="w-10 h-10 text-accent-cyan" />
                  </div>
                  <h3 className="text-xl font-bold text-text-primary mb-2">
                    Customize your experience
                  </h3>
                  <p className="text-text-secondary text-sm">
                    Set your preferences. You can change these anytime in settings.
                  </p>
                </div>

                <div className="space-y-3">
                  {[
                    { key: 'autoReply', title: 'Auto-reply to routine emails', desc: 'Let AI handle common responses' },
                    { key: 'dailyDigest', title: 'Daily digest summary', desc: 'Get a morning overview of your inbox' },
                    { key: 'priorityInbox', title: 'Priority inbox sorting', desc: 'Important emails rise to the top' },
                  ].map((item) => (
                    <label
                      key={item.key}
                      className="flex items-center justify-between p-4 rounded-xl bg-surface-card border border-surface-border cursor-pointer hover:border-accent-cyan/30 transition-colors"
                    >
                      <div>
                        <p className="font-medium text-text-primary">{item.title}</p>
                        <p className="text-sm text-text-muted">{item.desc}</p>
                      </div>
                      <div className="relative">
                        <input
                          type="checkbox"
                          checked={preferences[item.key as keyof typeof preferences]}
                          onChange={(e) => setPreferences(prev => ({ ...prev, [item.key]: e.target.checked }))}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-surface-border rounded-full peer peer-checked:bg-accent-cyan transition-colors" />
                        <div className="absolute left-0.5 top-0.5 w-5 h-5 bg-white rounded-full shadow peer-checked:translate-x-5 transition-transform" />
                      </div>
                    </label>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Footer */}
        <div className="border-t border-surface-border p-6 flex-shrink-0">
          {/* Progress dots */}
          <div className="flex items-center justify-center gap-2 mb-4">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className={`w-2 h-2 rounded-full transition-colors ${
                  i === stepIndex ? 'bg-accent-cyan' : 'bg-surface-border'
                }`}
              />
            ))}
          </div>

          {/* Buttons */}
          {currentStep !== 'smtp' && (
            <div className="flex gap-3">
              {currentStep !== 'welcome' && (
                <button
                  onClick={handleBack}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl border border-surface-border text-text-secondary hover:bg-surface-hover transition-colors"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Back
                </button>
              )}
              <button
                onClick={handleNext}
                className={`flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-accent-cyan to-accent-purple text-white font-medium hover:opacity-90 transition-opacity ${
                  currentStep === 'welcome' ? 'w-full' : 'flex-1'
                }`}
              >
                {currentStep === 'preferences' ? (
                  <>
                    Get Started
                    <Check className="w-4 h-4" />
                  </>
                ) : (
                  <>
                    Continue
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>
          )}

          {currentStep === 'smtp' && (
            <button
              onClick={handleBack}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl border border-surface-border text-text-secondary hover:bg-surface-hover transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to connection options
            </button>
          )}

          {currentStep === 'connect' && (
            <button
              onClick={handleNext}
              className="w-full mt-3 text-center text-sm text-text-muted hover:text-text-secondary transition-colors"
            >
              Skip for now
            </button>
          )}
        </div>
      </motion.div>
    </div>
  );
}

export default OnboardingModal;
