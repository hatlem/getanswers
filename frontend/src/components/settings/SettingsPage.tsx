import { motion } from 'framer-motion';
import { Settings, User, Bell, Shield, Palette, Database, CreditCard } from 'lucide-react';
import { Link } from 'react-router-dom';
import { GmailConnect } from '../auth/GmailConnect';
import { useAuthStore } from '../../stores/authStore';
import { Button } from '../ui/button';

export function SettingsPage() {
  const { user, logout } = useAuthStore();

  return (
    <div className="min-h-screen bg-surface-base">
      <div className="max-w-5xl mx-auto px-4 py-6 md:p-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 md:mb-8"
        >
          <h1 className="text-2xl md:text-3xl font-bold text-text-primary mb-2">Settings</h1>
          <p className="text-sm md:text-base text-text-secondary">
            Manage your account preferences and integrations
          </p>
        </motion.div>

        <div className="grid gap-4 md:gap-6">
          {/* Profile Section */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-surface-card border border-surface-border rounded-xl p-4 md:p-6"
          >
            <div className="flex items-center gap-3 mb-4 md:mb-6">
              <div className="w-9 h-9 md:w-10 md:h-10 rounded-lg bg-accent-cyan/20 flex items-center justify-center">
                <User className="w-4 h-4 md:w-5 md:h-5 text-accent-cyan" />
              </div>
              <div>
                <h2 className="text-lg md:text-xl font-semibold text-text-primary">Profile</h2>
                <p className="text-xs md:text-sm text-text-muted">Your account information</p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Name
                </label>
                <div className="text-text-primary">{user?.name || 'User'}</div>
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Email
                </label>
                <div className="text-text-primary">{user?.email || 'user@example.com'}</div>
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Autonomy Level
                </label>
                <div className="flex items-center gap-2">
                  <span className="px-3 py-1 rounded-full bg-accent-cyan/20 text-accent-cyan text-sm font-medium capitalize">
                    {user?.autonomyLevel || 'medium'}
                  </span>
                </div>
              </div>
            </div>
          </motion.section>

          {/* Gmail Integration Section */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <GmailConnect variant="card" showStatus={true} />
          </motion.section>

          {/* Billing Section */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
            className="bg-surface-card border border-surface-border rounded-xl p-4 md:p-6"
          >
            <div className="flex items-center gap-3 mb-4 md:mb-6">
              <div className="w-9 h-9 md:w-10 md:h-10 rounded-lg bg-accent-purple/20 flex items-center justify-center">
                <CreditCard className="w-4 h-4 md:w-5 md:h-5 text-accent-purple" />
              </div>
              <div>
                <h2 className="text-lg md:text-xl font-semibold text-text-primary">Billing & Subscription</h2>
                <p className="text-xs md:text-sm text-text-muted">Manage your plan and payment method</p>
              </div>
            </div>

            <Link to="/billing">
              <Button variant="outline" className="w-full justify-start">
                Manage Subscription
              </Button>
            </Link>
          </motion.section>

          {/* Notifications Section */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-surface-card border border-surface-border rounded-xl p-4 md:p-6"
          >
            <div className="flex items-center gap-3 mb-4 md:mb-6">
              <div className="w-9 h-9 md:w-10 md:h-10 rounded-lg bg-warning/20 flex items-center justify-center">
                <Bell className="w-4 h-4 md:w-5 md:h-5 text-warning" />
              </div>
              <div>
                <h2 className="text-lg md:text-xl font-semibold text-text-primary">Notifications</h2>
                <p className="text-xs md:text-sm text-text-muted">Configure your alert preferences</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium text-text-primary">High Priority Alerts</div>
                  <div className="text-xs text-text-muted">Get notified for urgent emails</div>
                </div>
                <div className="w-12 h-6 bg-accent-cyan rounded-full relative cursor-pointer">
                  <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full" />
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium text-text-primary">Daily Summary</div>
                  <div className="text-xs text-text-muted">Receive daily email digest</div>
                </div>
                <div className="w-12 h-6 bg-surface-border rounded-full relative cursor-pointer">
                  <div className="absolute left-1 top-1 w-4 h-4 bg-text-muted rounded-full" />
                </div>
              </div>
            </div>
          </motion.section>

          {/* Privacy & Security Section */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-surface-card border border-surface-border rounded-xl p-4 md:p-6"
          >
            <div className="flex items-center gap-3 mb-4 md:mb-6">
              <div className="w-9 h-9 md:w-10 md:h-10 rounded-lg bg-success/20 flex items-center justify-center">
                <Shield className="w-4 h-4 md:w-5 md:h-5 text-success" />
              </div>
              <div>
                <h2 className="text-lg md:text-xl font-semibold text-text-primary">Privacy & Security</h2>
                <p className="text-xs md:text-sm text-text-muted">Manage your security settings</p>
              </div>
            </div>

            <div className="space-y-3">
              <Button variant="outline" className="w-full justify-start">
                Change Password
              </Button>
              <Button variant="outline" className="w-full justify-start">
                Two-Factor Authentication
              </Button>
              <Button variant="outline" className="w-full justify-start">
                Active Sessions
              </Button>
            </div>
          </motion.section>

          {/* Danger Zone */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-surface-card border border-critical/30 rounded-xl p-4 md:p-6"
          >
            <h2 className="text-lg md:text-xl font-semibold text-critical mb-4">Danger Zone</h2>
            <div className="space-y-3">
              <Button
                variant="danger"
                onClick={logout}
                className="w-full justify-start"
              >
                Sign Out
              </Button>
              <Button variant="outline" className="w-full justify-start text-critical border-critical/30 hover:border-critical/50">
                Delete Account
              </Button>
            </div>
          </motion.section>
        </div>
      </div>
    </div>
  );
}
