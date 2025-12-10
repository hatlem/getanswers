import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';

// Base skeleton component
interface SkeletonProps {
  className?: string;
  animate?: boolean;
}

export function Skeleton({ className, animate = true }: SkeletonProps) {
  return (
    <motion.div
      className={cn('bg-surface-border rounded', className)}
      animate={
        animate
          ? {
              opacity: [0.5, 0.8, 0.5],
            }
          : undefined
      }
      transition={
        animate
          ? {
              duration: 1.5,
              repeat: Infinity,
              ease: 'easeInOut',
            }
          : undefined
      }
    />
  );
}

// Action card skeleton
export function ActionCardSkeleton({ index = 0 }: { index?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
      className="rounded-xl border border-surface-border bg-surface-card p-5"
    >
      {/* Header: Risk + Category + Confidence */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Skeleton className="h-6 w-20" />
          <Skeleton className="h-6 w-16" />
        </div>
        <Skeleton className="h-8 w-20" />
      </div>

      {/* Summary */}
      <div className="mb-3">
        <Skeleton className="h-5 w-full mb-2" />
        <Skeleton className="h-5 w-3/4" />
      </div>

      {/* Proposed Action Box */}
      <div className="p-3 rounded-lg border border-surface-border mb-4">
        <Skeleton className="h-4 w-full mb-2" />
        <Skeleton className="h-4 w-5/6 mb-2" />
        <Skeleton className="h-4 w-4/5" />
      </div>

      {/* Sender Info */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <Skeleton className="w-9 h-9 rounded-full" />
          <div>
            <Skeleton className="h-4 w-32 mb-1" />
            <Skeleton className="h-3 w-24" />
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-2 pt-3 border-t border-surface-border">
        <Skeleton className="flex-1 h-10 rounded-lg" />
        <Skeleton className="flex-1 h-10 rounded-lg" />
        <Skeleton className="flex-1 h-10 rounded-lg" />
        <Skeleton className="flex-1 h-10 rounded-lg" />
      </div>
    </motion.div>
  );
}

// Timeline item skeleton
export function TimelineItemSkeleton() {
  return (
    <div className="flex gap-3 pb-6 last:pb-0">
      <div className="flex flex-col items-center">
        <Skeleton className="w-8 h-8 rounded-lg shrink-0" />
        <div className="w-px h-full bg-surface-border mt-2" />
      </div>
      <div className="flex-1 pt-1">
        <div className="flex items-center gap-2 mb-2">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-3 w-20" />
        </div>
        <Skeleton className="h-4 w-full mb-2" />
        <Skeleton className="h-4 w-5/6 mb-2" />
        <Skeleton className="h-4 w-4/5" />
      </div>
    </div>
  );
}

// Timeline skeleton (multiple items)
export function TimelineSkeleton({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-0">
      {Array.from({ length: count }).map((_, i) => (
        <TimelineItemSkeleton key={i} />
      ))}
    </div>
  );
}

// Stats card skeleton
export function StatsSkeleton() {
  return (
    <div className="p-4 rounded-xl bg-surface-card border border-surface-border">
      <div className="flex items-center justify-between mb-3">
        <Skeleton className="h-3 w-32" />
      </div>
      <Skeleton className="h-9 w-20 mb-1" />
      <Skeleton className="h-4 w-40 mb-3" />
      <Skeleton className="h-2 w-full rounded-full" />
    </div>
  );
}

// Navigation item skeleton
export function NavItemSkeleton() {
  return (
    <div className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg">
      <Skeleton className="w-8 h-8 rounded-lg" />
      <Skeleton className="flex-1 h-4" />
      <Skeleton className="w-8 h-5 rounded-full" />
    </div>
  );
}

// Conversation header skeleton
export function ConversationHeaderSkeleton() {
  return (
    <div className="p-5 border-b border-surface-border">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <Skeleton className="h-3 w-16 mb-2" />
          <Skeleton className="h-5 w-full mb-1" />
          <Skeleton className="h-5 w-3/4" />
        </div>
        <Skeleton className="w-24 h-7 rounded-full" />
      </div>
    </div>
  );
}

// Agent summary skeleton
export function AgentSummarySkeleton() {
  return (
    <div className="p-5 border-b border-surface-border">
      <div className="flex items-center gap-2 mb-3">
        <Skeleton className="w-6 h-6 rounded-md" />
        <Skeleton className="h-4 w-28" />
      </div>
      <Skeleton className="h-4 w-full mb-2" />
      <Skeleton className="h-4 w-full mb-2" />
      <Skeleton className="h-4 w-5/6 mb-2" />
      <Skeleton className="h-4 w-4/5" />
    </div>
  );
}
