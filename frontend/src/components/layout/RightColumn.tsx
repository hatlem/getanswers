import { motion } from 'framer-motion';
import { Box, RefreshCcw, Settings } from 'lucide-react';
import { TimelineItem } from '../timeline/TimelineItem';
import { cn } from '../../lib/utils';
import type { ConversationThread } from '../../types';

interface RightColumnProps {
  conversation: ConversationThread | null;
  onTakeOver?: () => void;
  onChangePolicy?: () => void;
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

export function RightColumn({ conversation, onTakeOver, onChangePolicy }: RightColumnProps) {
  if (!conversation) {
    return (
      <aside className="w-96 bg-surface-elevated border-l border-surface-border flex flex-col items-center justify-center p-8 shrink-0">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <div className="w-16 h-16 rounded-full bg-surface-card border border-surface-border flex items-center justify-center mx-auto mb-4">
            <Box className="w-7 h-7 text-text-muted" />
          </div>
          <h3 className="text-sm font-medium text-text-primary mb-1">
            No Conversation Selected
          </h3>
          <p className="text-xs text-text-muted max-w-[200px]">
            Select an action card to view the conversation timeline and context.
          </p>
        </motion.div>
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

      {/* Controls */}
      <motion.div
        className="p-4 border-t border-surface-border space-y-2"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.2 }}
      >
        <button
          onClick={onTakeOver}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-surface-card border border-surface-border text-text-secondary hover:text-text-primary hover:border-accent-cyan/30 transition-all text-sm font-medium"
        >
          <RefreshCcw className="w-4 h-4" />
          <span>Take Over Thread</span>
        </button>
        <button
          onClick={onChangePolicy}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-surface-card border border-surface-border text-text-secondary hover:text-text-primary hover:border-accent-purple/30 transition-all text-sm font-medium"
        >
          <Settings className="w-4 h-4" />
          <span>Change Policy for Sender</span>
        </button>
      </motion.div>
    </aside>
  );
}
