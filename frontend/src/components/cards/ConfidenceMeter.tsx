import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';

interface ConfidenceMeterProps {
  value: number;
  showLabel?: boolean;
  size?: 'sm' | 'md';
}

export function ConfidenceMeter({ value, showLabel = true, size = 'md' }: ConfidenceMeterProps) {
  const getConfidenceColor = (score: number) => {
    if (score >= 80) return { bar: 'bg-success', text: 'text-success' };
    if (score >= 60) return { bar: 'bg-warning', text: 'text-warning' };
    return { bar: 'bg-critical', text: 'text-critical' };
  };

  const colors = getConfidenceColor(value);
  const isLow = value < 60;

  return (
    <div className={cn(
      'flex items-center gap-2',
      size === 'sm' ? 'gap-1.5' : 'gap-2'
    )}>
      {showLabel && (
        <span className={cn(
          'text-text-muted',
          size === 'sm' ? 'text-[10px]' : 'text-xs'
        )}>
          Confidence
        </span>
      )}
      <div className={cn(
        'rounded-full bg-surface-border overflow-hidden',
        size === 'sm' ? 'w-12 h-1.5' : 'w-16 h-2'
      )}>
        <motion.div
          className={cn('h-full rounded-full', colors.bar)}
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
        />
      </div>
      <span className={cn(
        'font-mono font-medium',
        colors.text,
        size === 'sm' ? 'text-[10px]' : 'text-xs',
        isLow && 'animate-pulse'
      )}>
        {value}%
      </span>
    </div>
  );
}
