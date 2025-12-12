import { motion } from 'framer-motion';
import { Search, Shield, ChevronDown, Layers } from 'lucide-react';
import { cn, getInitials } from '../../lib/utils';
import type { GlobalStatus, User } from '../../types';

interface TopNavProps {
  user: User | null;
  globalStatus: GlobalStatus | null;
  onSearch?: (query: string) => void;
}

export function TopNav({ user, globalStatus, onSearch }: TopNavProps) {
  // Default values for when data is not yet loaded
  const displayUser = user || { name: 'Loading...', autonomyLevel: 'moderate' as const };
  const displayStatus = globalStatus || { status: 'all_clear' as const, message: 'Loading...', pendingCount: 0 };
  const statusStyles = {
    all_clear: {
      indicator: 'bg-success',
      text: 'text-success',
    },
    pending_decisions: {
      indicator: 'bg-warning animate-pulse',
      text: 'text-warning',
    },
    urgent: {
      indicator: 'bg-critical animate-pulse',
      text: 'text-critical',
    },
  };

  const currentStatus = statusStyles[displayStatus.status];

  return (
    <header className="h-16 bg-surface-elevated border-b border-surface-border flex items-center justify-between px-6 shrink-0">
      {/* Left: Logo + Status */}
      <div className="flex items-center gap-6">
        <motion.div
          className="flex items-center gap-3"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
        >
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-accent-cyan to-accent-purple flex items-center justify-center">
            <Layers className="w-5 h-5 text-white" />
          </div>
          <span className="text-lg font-semibold text-text-primary tracking-tight">
            GetAnswers
          </span>
        </motion.div>

        <motion.div
          className="flex items-center gap-2.5 px-4 py-2 rounded-full bg-surface-card border border-surface-border"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          <div className={cn('w-2 h-2 rounded-full', currentStatus.indicator)} />
          <span className={cn('text-sm font-medium font-mono', currentStatus.text)}>
            {displayStatus.message}
          </span>
        </motion.div>
      </div>

      {/* Center: Search */}
      <motion.div
        className="flex-1 max-w-xl mx-8"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.15 }}
      >
        <div className="relative group">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4.5 h-4.5 text-text-muted group-focus-within:text-accent-cyan transition-colors" />
          <input
            type="text"
            placeholder="Search by Objective, Sender, or Policy..."
            className="w-full h-11 pl-12 pr-20 rounded-xl bg-surface-card border border-surface-border text-text-primary placeholder:text-text-muted text-sm focus:outline-none focus:border-accent-cyan/50 focus:ring-1 focus:ring-accent-cyan/20 transition-all"
            onChange={(e) => onSearch?.(e.target.value)}
          />
          <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1">
            <kbd className="px-1.5 py-0.5 text-[10px] font-mono text-text-muted bg-surface-border rounded">⌘</kbd>
            <kbd className="px-1.5 py-0.5 text-[10px] font-mono text-text-muted bg-surface-border rounded">K</kbd>
          </div>
        </div>
      </motion.div>

      {/* Right: Autonomy + User */}
      <motion.div
        className="flex items-center gap-4"
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3, delay: 0.2 }}
      >
        <button className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-surface-card border border-surface-border hover:border-accent-cyan/30 hover:bg-surface-hover transition-all group">
          <Shield className="w-4 h-4 text-accent-cyan" />
          <span className="text-sm text-text-secondary group-hover:text-text-primary transition-colors">
            Autonomy: <span className="font-semibold text-text-primary capitalize">{displayUser.autonomyLevel}</span>
          </span>
        </button>

        <button className="flex items-center gap-3 px-3 py-1.5 rounded-lg hover:bg-surface-hover transition-colors group">
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold text-white"
            style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' }}
          >
            {getInitials(displayUser.name)}
          </div>
          <span className="text-sm text-text-secondary group-hover:text-text-primary transition-colors">
            {displayUser.name}
          </span>
          <ChevronDown className="w-4 h-4 text-text-muted group-hover:text-text-secondary transition-colors" />
        </button>
      </motion.div>
    </header>
  );
}
