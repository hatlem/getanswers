import { motion, AnimatePresence } from 'framer-motion';
import { Box, X } from 'lucide-react';
import { TimelineItem } from '../timeline/TimelineItem';
import { ConversationHeaderSkeleton, AgentSummarySkeleton, TimelineSkeleton } from '../ui/Skeleton';
import { InlineError } from '../ui/ErrorState';
import { NoConversationState } from '../ui/EmptyState';
import { useConversationByObjective } from '../../hooks/useConversations';
import { useAppStore } from '../../stores/appStore';
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
  const { isMobileDetailOpen, setMobileDetailOpen } = useAppStore();

  // Fetch conversation by objective ID
  const {
    data: conversation,
    isLoading,
    error,
    refetch,
  } = useConversationByObjective(objectiveId);

  // Content based on state
  const renderContent = () => {
    // No objective selected
    if (!objectiveId) {
      return (
        <div className="flex-1 flex flex-col items-center justify-center p-8">
          <NoConversationState />
        </div>
      );
    }

    // Loading state
    if (isLoading) {
      return (
        <>
          <ConversationHeaderSkeleton />
          <AgentSummarySkeleton />
          <div className="flex-1 overflow-y-auto p-5">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-text-muted mb-4">
              Conversation Timeline
            </h3>
            <TimelineSkeleton count={4} />
          </div>
        </>
      );
    }

    // Error state
    if (error || !conversation) {
      return (
        <div className="p-5">
          <InlineError error={error} onRetry={() => refetch()} />
        </div>
      );
    }

    const status = statusStyles[conversation.objectiveStatus];

    return (
      <>
        {/* Objective Header */}
        <motion.div
          className="p-4 md:p-5 border-b border-surface-border"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0 flex-1">
              <span className="text-[10px] font-semibold uppercase tracking-wider text-text-muted">
                Objective
              </span>
              <h2 className="text-sm md:text-base font-semibold text-text-primary mt-1 leading-snug">
                {conversation.objectiveTitle}
              </h2>
            </div>
            <div className="flex items-center gap-2 px-2 md:px-2.5 py-1 md:py-1.5 rounded-full bg-surface-card border border-surface-border shrink-0">
              <div className={cn('w-2 h-2 rounded-full', status.dot)} />
              <span className={cn('text-[10px] md:text-xs font-medium', status.text)}>
                {status.label}
              </span>
            </div>
          </div>
        </motion.div>

        {/* Agent Summary */}
        <motion.div
          className="p-4 md:p-5 border-b border-surface-border"
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
          <div className="p-4 md:p-5">
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
      </>
    );
  };

  return (
    <>
      {/* Desktop panel */}
      <aside className="hidden lg:flex w-96 bg-surface-elevated border-l border-surface-border flex-col shrink-0">
        {renderContent()}
      </aside>

      {/* Mobile drawer */}
      <AnimatePresence>
        {isMobileDetailOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              onClick={() => setMobileDetailOpen(false)}
              className="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
            />

            {/* Drawer */}
            <motion.aside
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
              className="lg:hidden fixed right-0 top-0 h-full w-full max-w-md bg-surface-elevated border-l border-surface-border flex flex-col z-50"
            >
              {/* Mobile drawer header */}
              <div className="h-14 px-4 flex items-center justify-between border-b border-surface-border">
                <span className="text-lg font-semibold text-text-primary">Details</span>
                <button
                  onClick={() => setMobileDetailOpen(false)}
                  className="p-2 rounded-lg hover:bg-surface-hover transition-colors"
                >
                  <X className="w-5 h-5 text-text-muted" />
                </button>
              </div>
              {renderContent()}
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
