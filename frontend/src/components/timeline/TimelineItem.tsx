import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { cn, formatTime } from '../../lib/utils';
import type { TimelineItem as TimelineItemType } from '../../types';

interface TimelineItemProps {
  item: TimelineItemType;
  isLast?: boolean;
}

const typeStyles = {
  incoming: {
    marker: 'bg-info',
    label: 'text-info',
  },
  outgoing: {
    marker: 'bg-success',
    label: 'text-success',
  },
  agent_action: {
    marker: 'bg-accent-purple',
    label: 'text-accent-purple',
  },
};

const badgeStyles: Record<string, string> = {
  auto: 'bg-accent-purple/20 text-accent-purple',
  sent: 'bg-success/20 text-success',
  pending: 'bg-warning/20 text-warning animate-pulse',
  new: 'bg-info/20 text-info',
};

export function TimelineItem({ item, isLast }: TimelineItemProps) {
  const [isExpanded, setIsExpanded] = useState(!item.isCollapsed);
  const styles = typeStyles[item.type];
  const hasFullContent = item.fullContent && item.fullContent !== item.content;
  const isPending = item.badge === 'pending';

  return (
    <motion.div
      className="flex gap-4"
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Timeline Marker */}
      <div className="flex flex-col items-center">
        <div className={cn(
          'w-3 h-3 rounded-full shrink-0',
          styles.marker,
          isPending && 'ring-2 ring-warning/30 animate-pulse'
        )} />
        {!isLast && (
          <div className="w-0.5 flex-1 bg-surface-border mt-2" />
        )}
      </div>

      {/* Content */}
      <div className={cn('flex-1 pb-6', isLast && 'pb-0')}>
        {/* Meta */}
        <div className="flex items-center gap-2 mb-1.5">
          <span className={cn('text-sm font-medium', styles.label)}>
            {item.sender}
          </span>
          <span className="text-xs text-text-muted">
            {formatTime(item.timestamp)}
          </span>
          {item.badge && (
            <span className={cn(
              'px-2 py-0.5 rounded text-[10px] font-medium uppercase tracking-wide',
              badgeStyles[item.badge]
            )}>
              {item.badge === 'auto' && 'Auto-drafted'}
              {item.badge === 'sent' && 'Sent'}
              {item.badge === 'pending' && 'Pending Approval'}
              {item.badge === 'new' && 'New'}
            </span>
          )}
        </div>

        {/* Message */}
        <div className={cn(
          'p-3 rounded-lg border text-sm leading-relaxed',
          item.type === 'agent_action'
            ? 'bg-accent-purple/5 border-accent-purple/20 text-text-secondary'
            : 'bg-surface-card border-surface-border text-text-secondary',
          isPending && 'border-warning/30 bg-warning/5'
        )}>
          <AnimatePresence mode="wait">
            {isExpanded && hasFullContent ? (
              <motion.div
                key="full"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="whitespace-pre-wrap"
              >
                {item.fullContent}
              </motion.div>
            ) : (
              <motion.p
                key="short"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                {item.content}
              </motion.p>
            )}
          </AnimatePresence>

          {hasFullContent && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="mt-2 flex items-center gap-1 text-xs text-accent-cyan hover:text-accent-cyan/80 transition-colors"
            >
              {isExpanded ? (
                <>
                  <ChevronUp className="w-3 h-3" />
                  <span>Show less</span>
                </>
              ) : (
                <>
                  <ChevronDown className="w-3 h-3" />
                  <span>Show full message</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </motion.div>
  );
}
