import { motion } from 'framer-motion';
import { Box } from 'lucide-react';
import { TimelineItem } from '../timeline/TimelineItem';
import { ConversationHeaderSkeleton, AgentSummarySkeleton, TimelineSkeleton } from '../ui/Skeleton';
import { InlineError } from '../ui/ErrorState';
import { NoConversationState } from '../ui/EmptyState';
import { useConversationByObjective } from '../../hooks/useConversations';
import { cn } from '../../lib/utils';

interface RightColumnProps {
  objectiveId: string | null;
}

const statusStyles = {
  waiting_on_you: {
    dot: 'bg-warning animate-pulse',
    text: 'text-warning',
    label: 'Waiting on You',
  },
  waiting_on_others: {
    dot: 'bg-info',
    text: 'text-info',
    label: 'Waiting on Others',
  },
  handled: {
    dot: 'bg-success',
    text: 'text-success',
    label: 'Handled',
  },
  scheduled: {
    dot: 'bg-accent-cyan',
    text: 'text-accent-cyan',
    label: 'Scheduled',
  },
  muted: {
    dot: 'bg-text-muted',
    text: 'text-text-muted',
    label: 'Muted',
  },
};

export function RightColumn({ objectiveId }: RightColumnProps) {
  // Fetch conversation by objective ID
  const {
    data: conversation,
    isLoading,
    error,
    refetch,
  } = useConversationByObjective(objectiveId);

  // No objective selected
  if (!objectiveId) {
    return (
      <aside className="w-96 bg-surface-elevated border-l border-surface-border flex flex-col items-center justify-center p-8 shrink-0">
        <NoConversationState />
      </aside>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <aside className="w-96 bg-surface-elevated border-l border-surface-border flex flex-col shrink-0">
        <ConversationHeaderSkeleton />
        <AgentSummarySkeleton />
        <div className="flex-1 overflow-y-auto p-5">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-text-muted mb-4">
            Conversation Timeline
          </h3>
          <TimelineSkeleton count={4} />
        </div>
      </aside>
    );
  }

  // Error state
  if (error || !conversation) {
    return (
      <aside className="w-96 bg-surface-elevated border-l border-surface-border flex flex-col shrink-0">
        <div className="p-5">
          <InlineError error={error} onRetry={() => refetch()} />
        </div>
      </aside>
    );
  }

  const status = statusStyles[conversation.objectiveStatus];

  return (
    <aside className="w-96 bg-surface-elevated border-l border-surface-border flex flex-col shrink-0">
      {/* Objective Header */}
      <motion.div
        className="p-5 border-b border-surface-border"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="flex items-start justify-between gap-3">
          <div>
            <span className="text-[10px] font-semibold uppercase tracking-wider text-text-muted">
              Objective
            </span>
            <h2 className="text-base font-semibold text-text-primary mt-1 leading-snug">
              {conversation.objectiveTitle}
            </h2>
          </div>
          <div className="flex items-center gap-2 px-2.5 py-1.5 rounded-full bg-surface-card border border-surface-border shrink-0">
            <div className={cn('w-2 h-2 rounded-full', status.dot)} />
            <span className={cn('text-xs font-medium', status.text)}>
              {status.label}
            </span>
          </div>
        </div>
      </motion.div>

      {/* Agent Summary */}
      <motion.div
        className="p-5 border-b border-surface-border"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.1 }}
      >
        <div className="flex items-center gap-2 mb-3">
          <div className="w-6 h-6 rounded-md bg-accent-purple/20 flex items-center justify-center">
            <Box className="w-3.5 h-3.5 text-accent-purple" />
          </div>
          <span className="text-sm font-medium text-text-primary">Agent Summary</span>
        </div>
        <p className="text-sm text-text-secondary leading-relaxed">
          {conversation.agentSummary.split(/(\*\*.*?\*\*)/).map((part, i) => {
            if (part.startsWith('**') && part.endsWith('**')) {
              return (
                <strong key={i} className="text-text-primary font-semibold">
                  {part.slice(2, -2)}
                </strong>
              );
            }
            return part;
          })}
        </p>
      </motion.div>

      {/* Timeline */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-5">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-text-muted mb-4">
            Conversation Timeline
          </h3>
          <div className="space-y-0">
            {conversation.timeline.map((item, index) => (
              <TimelineItem
                key={item.id}
                item={item}
                isLast={index === conversation.timeline.length - 1}
              />
            ))}
          </div>
        </div>
      </div>

    </aside>
  );
}
