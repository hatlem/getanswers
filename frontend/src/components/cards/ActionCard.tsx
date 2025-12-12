import { motion } from 'framer-motion';
import { Check, Pencil, XCircle, Search, Zap, HelpCircle } from 'lucide-react';
import { cn, getInitials } from '../../lib/utils';
import { ConfidenceMeter } from './ConfidenceMeter';
import type { ActionCard as ActionCardType, ActionType } from '../../types';

interface ActionCardProps {
  card: ActionCardType;
  isSelected?: boolean;
  onSelect?: (card: ActionCardType) => void;
  onAction?: (cardId: string, action: ActionType, card: ActionCardType) => void;
  index?: number;
}

const riskBadgeStyles = {
  high: 'bg-critical-muted text-critical border-critical-border',
  medium: 'bg-warning-muted text-warning border-warning-border',
  low: 'bg-success-muted text-success border-success-border',
};

const categoryStyles: Record<string, string> = {
  finance: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  client: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  hr: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  legal: 'bg-red-500/10 text-red-400 border-red-500/20',
  internal: 'bg-gray-500/10 text-gray-400 border-gray-500/20',
  partner: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
};

const tagTypeStyles: Record<string, string> = {
  vip: 'bg-amber-500/20 text-amber-300',
  key: 'bg-blue-500/20 text-blue-300',
  new: 'bg-emerald-500/20 text-emerald-300',
  blocked: 'bg-red-500/20 text-red-300',
  custom: 'bg-gray-500/20 text-gray-300',
};

export function ActionCard({ card, isSelected, onSelect, onAction, index = 0 }: ActionCardProps) {
  const handleAction = (e: React.MouseEvent, action: ActionType) => {
    e.stopPropagation();
    onAction?.(card.id, action, card);
  };

  return (
    <motion.article
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20, scale: 0.95 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
      whileHover={{ scale: 1.01 }}
      onClick={() => onSelect?.(card)}
      className={cn(
        'rounded-xl border cursor-pointer transition-all',
        'bg-surface-card hover:bg-surface-hover',
        isSelected
          ? 'border-accent-cyan/50 shadow-glow-info'
          : 'border-surface-border hover:border-surface-hover',
        card.riskLevel === 'high' && !isSelected && 'border-l-2 border-l-critical'
      )}
    >
      {/* Header: Risk + Category + Confidence */}
      <div className="flex items-center justify-between px-5 pt-4 pb-3">
        <div className="flex items-center gap-2">
          <span className={cn(
            'px-2.5 py-1 rounded text-[10px] font-bold uppercase tracking-wider border',
            riskBadgeStyles[card.riskLevel]
          )}>
            {card.riskLevel} Risk
          </span>
          <span className={cn(
            'px-2 py-1 rounded text-[10px] font-medium capitalize border',
            categoryStyles[card.category] || categoryStyles.internal
          )}>
            {card.category}
          </span>
        </div>
        <ConfidenceMeter value={card.confidenceScore} />
      </div>

      {/* Body: Summary + Proposed Action */}
      <div className="px-5 pb-4">
        <h2 className="text-base font-semibold text-text-primary leading-snug mb-3">
          {card.summary}
        </h2>
        <div className={cn(
          'flex gap-3 p-3 rounded-lg border',
          card.isUncertain
            ? 'bg-warning-muted/50 border-warning-border'
            : 'bg-accent-cyan/5 border-accent-cyan/20'
        )}>
          <div className={cn(
            'w-6 h-6 rounded-md flex items-center justify-center shrink-0 mt-0.5',
            card.isUncertain ? 'bg-warning/20' : 'bg-accent-cyan/20'
          )}>
            {card.isUncertain ? (
              <HelpCircle className="w-3.5 h-3.5 text-warning" />
            ) : (
              <Zap className="w-3.5 h-3.5 text-accent-cyan" />
            )}
          </div>
          <p className="text-sm text-text-secondary leading-relaxed">
            {card.proposedAction}
          </p>
        </div>
      </div>

      {/* Context: Sender + Related Items */}
      <div className="px-5 pb-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div
            className="w-9 h-9 rounded-full flex items-center justify-center text-xs font-semibold text-white shrink-0"
            style={{ background: card.sender.avatarColor || 'linear-gradient(135deg, #6366f1, #8b5cf6)' }}
          >
            {getInitials(card.sender.name)}
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-text-primary truncate">
                {card.sender.name}
              </span>
              {card.sender.tags.map((tag, i) => (
                <span
                  key={i}
                  className={cn(
                    'px-1.5 py-0.5 rounded text-[9px] font-medium uppercase tracking-wide',
                    tagTypeStyles[tag.type] || tagTypeStyles.custom
                  )}
                >
                  {tag.label}
                </span>
              ))}
            </div>
            <span className="text-xs text-text-muted truncate block">
              {card.sender.organization}
            </span>
          </div>
        </div>

        {card.relatedItems.length > 0 && (
          <div className="flex items-center gap-2 text-xs">
            <span className="text-text-muted">Related:</span>
            {card.relatedItems.slice(0, 2).map((item, i) => (
              <a
                key={item.id}
                href={item.href}
                onClick={(e) => e.stopPropagation()}
                className="text-accent-cyan hover:text-accent-cyan/80 hover:underline transition-colors"
              >
                {item.label}
              </a>
            ))}
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="px-5 py-3 border-t border-surface-border flex items-center gap-2">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={(e) => handleAction(e, 'approve')}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-success/10 text-success border border-success/20 hover:bg-success/20 hover:border-success/30 transition-all font-medium text-sm"
        >
          <Check className="w-4 h-4" strokeWidth={2.5} />
          <span>Approve</span>
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={(e) => handleAction(e, 'edit')}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-surface-hover text-text-secondary border border-surface-border hover:text-text-primary hover:border-accent-cyan/30 transition-all font-medium text-sm"
        >
          <Pencil className="w-4 h-4" />
          <span>Edit Reply</span>
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={(e) => handleAction(e, 'override')}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-surface-hover text-text-secondary border border-surface-border hover:text-critical hover:border-critical/30 transition-all font-medium text-sm"
        >
          <XCircle className="w-4 h-4" />
          <span>Override</span>
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={(e) => handleAction(e, 'escalate')}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-surface-hover text-text-secondary border border-surface-border hover:text-info hover:border-info/30 transition-all font-medium text-sm"
        >
          <Search className="w-4 h-4" />
          <span>Escalate</span>
        </motion.button>
      </div>
    </motion.article>
  );
}
