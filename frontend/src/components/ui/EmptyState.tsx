import { motion } from 'framer-motion';
import type { LucideIcon } from 'lucide-react';
import { CheckCircle2, Inbox, Search, Filter } from 'lucide-react';
import { cn } from '../../lib/utils';

interface EmptyStateProps {
  title: string;
  description: string;
  icon?: LucideIcon;
  action?: {
    label: string;
    onClick: () => void;
  };
  variant?: 'default' | 'success' | 'search' | 'filter';
  className?: string;
}

const variantConfig = {
  default: {
    icon: Inbox,
    iconBg: 'bg-surface-card',
    iconColor: 'text-text-muted',
  },
  success: {
    icon: CheckCircle2,
    iconBg: 'bg-success-muted',
    iconColor: 'text-success',
  },
  search: {
    icon: Search,
    iconBg: 'bg-info-muted',
    iconColor: 'text-info',
  },
  filter: {
    icon: Filter,
    iconBg: 'bg-warning-muted',
    iconColor: 'text-warning',
  },
};

export function EmptyState({
  title,
  description,
  icon,
  action,
  variant = 'default',
  className,
}: EmptyStateProps) {
  const config = variantConfig[variant];
  const Icon = icon || config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className={cn('flex flex-col items-center justify-center py-16 text-center', className)}
    >
      {/* Icon */}
      <div
        className={cn(
          'w-16 h-16 rounded-full flex items-center justify-center mb-4 border',
          config.iconBg,
          variant === 'default' ? 'border-surface-border' : 'border-transparent'
        )}
      >
        <Icon className={cn('w-8 h-8', config.iconColor)} />
      </div>

      {/* Title */}
      <h3 className="text-lg font-semibold text-text-primary mb-2">{title}</h3>

      {/* Description */}
      <p className="text-sm text-text-secondary max-w-md mb-6">{description}</p>

      {/* Action Button */}
      {action && (
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={action.onClick}
          className="px-5 py-2.5 rounded-lg bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/20 hover:bg-accent-cyan/20 hover:border-accent-cyan/30 transition-all font-medium text-sm"
        >
          {action.label}
        </motion.button>
      )}
    </motion.div>
  );
}

// Predefined empty states for common scenarios
export function EmptyQueueState() {
  return (
    <EmptyState
      title="All Clear"
      description="No items match the current filter. Your AI agent is handling everything autonomously."
      variant="success"
    />
  );
}

export function NoConversationState() {
  return (
    <EmptyState
      title="No Conversation Selected"
      description="Select an action card to view the conversation timeline and context."
      variant="default"
    />
  );
}

export function NoSearchResultsState({ onClear }: { onClear?: () => void }) {
  return (
    <EmptyState
      title="No Results Found"
      description="Try adjusting your search terms or filters to find what you're looking for."
      variant="search"
      action={
        onClear
          ? {
              label: 'Clear Search',
              onClick: onClear,
            }
          : undefined
      }
    />
  );
}

export function NoFilterResultsState({ onClear }: { onClear: () => void }) {
  return (
    <EmptyState
      title="No Items Match Filter"
      description="Try selecting a different filter to see more items in your queue."
      variant="filter"
      action={{
        label: 'Clear Filters',
        onClick: onClear,
      }}
    />
  );
}
