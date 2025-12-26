import { motion, AnimatePresence } from 'framer-motion';
import {
  AlertTriangle,
  Clock,
  CheckCircle2,
  Calendar,
  VolumeX,
  Settings,
  MessageSquare,
  X,
  Brain,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { cn } from '../../lib/utils';
import { NavItemSkeleton, StatsSkeleton } from '../ui/Skeleton';
import { useAppStore } from '../../stores/appStore';
import type { NavigationCount, EfficiencyStats, ObjectiveStatus } from '../../types';

interface LeftColumnProps {
  counts?: NavigationCount;
  stats?: EfficiencyStats;
  activeView: ObjectiveStatus | 'needs_decision';
  onViewChange: (view: ObjectiveStatus | 'needs_decision') => void;
}

interface NavItem {
  id: ObjectiveStatus | 'needs_decision';
  label: string;
  icon: React.ReactNode;
  count?: number;
  variant: 'critical' | 'waiting' | 'success' | 'scheduled' | 'muted' | 'default';
  badge?: string;
}

const variantStyles = {
  critical: {
    icon: 'text-critical',
    iconBg: 'bg-critical-muted',
    count: 'bg-critical text-white',
    active: 'border-critical/50 bg-critical-muted',
  },
  waiting: {
    icon: 'text-warning',
    iconBg: 'bg-warning-muted',
    count: 'bg-surface-border text-text-secondary',
    active: 'border-warning/50 bg-warning-muted',
  },
  success: {
    icon: 'text-success',
    iconBg: 'bg-success-muted',
    count: 'bg-success-muted text-success',
    active: 'border-success/50 bg-success-muted',
  },
  scheduled: {
    icon: 'text-info',
    iconBg: 'bg-info-muted',
    count: 'bg-surface-border text-text-secondary',
    active: 'border-info/50 bg-info-muted',
  },
  muted: {
    icon: 'text-text-muted',
    iconBg: 'bg-surface-border',
    count: 'bg-surface-border text-text-muted',
    active: 'border-surface-border bg-surface-hover',
  },
  default: {
    icon: 'text-accent-purple',
    iconBg: 'bg-accent-purple/10',
    count: 'bg-surface-border text-text-secondary',
    active: 'border-accent-purple/50 bg-accent-purple/10',
  },
};

export function LeftColumn({ counts, stats, activeView, onViewChange }: LeftColumnProps) {
  const { isMobileMenuOpen, setMobileMenuOpen, closeMobileDrawers } = useAppStore();

  const handleViewChange = (view: ObjectiveStatus | 'needs_decision') => {
    onViewChange(view);
    closeMobileDrawers();
  };

  const activeMissions: NavItem[] = [
    {
      id: 'needs_decision',
      label: 'Needs My Decision',
      icon: <AlertTriangle className="w-[18px] h-[18px]" />,
      count: counts?.needsDecision,
      variant: 'critical',
    },
    {
      id: 'waiting_on_others',
      label: 'Waiting on Others',
      icon: <Clock className="w-[18px] h-[18px]" />,
      count: counts?.waitingOnOthers,
      variant: 'waiting',
    },
  ];

  const auditViews: NavItem[] = [
    {
      id: 'handled',
      label: 'Handled by AI',
      icon: <CheckCircle2 className="w-[18px] h-[18px]" />,
      count: counts?.handledByAI,
      variant: 'success',
    },
    {
      id: 'scheduled',
      label: 'Scheduled & Done',
      icon: <Calendar className="w-[18px] h-[18px]" />,
      count: counts?.scheduledDone,
      variant: 'scheduled',
    },
    {
      id: 'muted',
      label: 'Muted / Ignored',
      icon: <VolumeX className="w-[18px] h-[18px]" />,
      count: counts?.muted,
      variant: 'muted',
    },
  ];

  const systemLinks = [
    {
      to: '/ai-learning',
      label: 'AI Learning',
      icon: <Brain className="w-[18px] h-[18px]" />,
      variant: 'default' as const,
      badge: 'New',
    },
    {
      to: '#',
      label: 'Policy Editor',
      icon: <Settings className="w-[18px] h-[18px]" />,
      variant: 'default' as const,
    },
    {
      to: '#',
      label: 'Raw Messages',
      icon: <MessageSquare className="w-[18px] h-[18px]" />,
      variant: 'default' as const,
      badge: 'Advanced',
    },
  ];

  const renderNavItem = (item: NavItem, index: number) => {
    const styles = variantStyles[item.variant];
    const isActive = activeView === item.id;

    return (
      <motion.li
        key={`${item.id}-${item.label}`}
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.2, delay: index * 0.05 }}
      >
        <button
          onClick={() => handleViewChange(item.id)}
          className={cn(
            'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg border border-transparent transition-all group',
            isActive ? styles.active : 'hover:bg-surface-hover hover:border-surface-border'
          )}
        >
          <div className={cn('w-8 h-8 rounded-lg flex items-center justify-center', styles.iconBg)}>
            <span className={styles.icon}>{item.icon}</span>
          </div>
          <span className={cn(
            'flex-1 text-left text-sm transition-colors',
            isActive ? 'text-text-primary font-medium' : 'text-text-secondary group-hover:text-text-primary'
          )}>
            {item.label}
          </span>
          {item.count !== undefined && (
            <span className={cn(
              'px-2 py-0.5 rounded-full text-xs font-mono font-medium',
              styles.count
            )}>
              {item.count}
            </span>
          )}
          {item.badge && (
            <span className="px-2 py-0.5 rounded text-[10px] font-medium uppercase tracking-wider text-text-muted bg-surface-border">
              {item.badge}
            </span>
          )}
        </button>
      </motion.li>
    );
  };

  const renderSystemLink = (item: typeof systemLinks[0], index: number) => {
    const styles = variantStyles[item.variant];

    return (
      <motion.li
        key={item.label}
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.2, delay: index * 0.05 }}
      >
        <Link
          to={item.to}
          onClick={() => closeMobileDrawers()}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg border border-transparent transition-all group hover:bg-surface-hover hover:border-surface-border"
        >
          <div className={cn('w-8 h-8 rounded-lg flex items-center justify-center', styles.iconBg)}>
            <span className={styles.icon}>{item.icon}</span>
          </div>
          <span className="flex-1 text-left text-sm transition-colors text-text-secondary group-hover:text-text-primary">
            {item.label}
          </span>
          {item.badge && (
            <span className="px-2 py-0.5 rounded text-[10px] font-medium uppercase tracking-wider text-accent-cyan bg-accent-cyan/10">
              {item.badge}
            </span>
          )}
        </Link>
      </motion.li>
    );
  };

  // Sidebar content - shared between desktop and mobile
  const sidebarContent = (
    <>
      <nav className="flex-1 p-4 space-y-6 overflow-y-auto">
        {/* Active Missions */}
        <div>
          <h3 className="px-3 mb-2 text-[11px] font-semibold uppercase tracking-wider text-text-muted">
            Active Missions
          </h3>
          <ul className="space-y-1">
            {activeMissions.map((item, i) => renderNavItem(item, i))}
          </ul>
        </div>

        {/* Audit & Archive */}
        <div>
          <h3 className="px-3 mb-2 text-[11px] font-semibold uppercase tracking-wider text-text-muted">
            Audit & Archive
          </h3>
          <ul className="space-y-1">
            {auditViews.map((item, i) => renderNavItem(item, i + activeMissions.length))}
          </ul>
        </div>

        {/* System */}
        <div>
          <h3 className="px-3 mb-2 text-[11px] font-semibold uppercase tracking-wider text-text-muted">
            System
          </h3>
          <ul className="space-y-1">
            {systemLinks.map((item, i) => renderSystemLink(item, i + activeMissions.length + auditViews.length))}
          </ul>
        </div>
      </nav>

      {/* Efficiency Stats */}
      <motion.div
        className="p-4 border-t border-surface-border"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.3 }}
      >
        {!stats ? (
          <StatsSkeleton />
        ) : (
          <div className="p-4 rounded-xl bg-surface-card border border-surface-border">
            <div className="flex items-center justify-between mb-3">
              <span className="text-[10px] font-semibold uppercase tracking-wider text-text-muted">
                Today's Efficiency
              </span>
            </div>
            <div className="flex items-baseline gap-1 mb-1">
              <span className="text-3xl font-bold text-success font-mono">{stats.percentage}%</span>
            </div>
            <p className="text-xs text-text-secondary mb-3">Handled autonomously</p>
            <div className="h-2 rounded-full bg-surface-border overflow-hidden">
              <motion.div
                className="h-full rounded-full bg-gradient-to-r from-success to-accent-cyan"
                initial={{ width: 0 }}
                animate={{ width: `${stats.percentage}%` }}
                transition={{ duration: 1, delay: 0.5, ease: 'easeOut' }}
              />
            </div>
          </div>
        )}
      </motion.div>
    </>
  );

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden lg:flex w-72 bg-surface-elevated border-r border-surface-border flex-col shrink-0">
        {sidebarContent}
      </aside>

      {/* Mobile drawer */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              onClick={() => setMobileMenuOpen(false)}
              className="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
            />

            {/* Drawer */}
            <motion.aside
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
              className="lg:hidden fixed left-0 top-0 h-full w-72 max-w-[85vw] bg-surface-elevated border-r border-surface-border flex flex-col z-50"
            >
              {/* Mobile drawer header */}
              <div className="h-14 px-4 flex items-center justify-between border-b border-surface-border">
                <span className="text-lg font-semibold text-text-primary">Menu</span>
                <button
                  onClick={() => setMobileMenuOpen(false)}
                  className="p-2 rounded-lg hover:bg-surface-hover transition-colors"
                >
                  <X className="w-5 h-5 text-text-muted" />
                </button>
              </div>
              {sidebarContent}
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
