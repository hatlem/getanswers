import { motion, AnimatePresence } from 'framer-motion';
import { ActionCard } from '../cards/ActionCard';
import { ActionCardSkeleton } from '../ui/Skeleton';
import { ErrorState } from '../ui/ErrorState';
import { EmptyQueueState, NoFilterResultsState } from '../ui/EmptyState';
import { useQueue } from '../../hooks/useQueue';
import type { ActionCard as ActionCardType, ActionType, ObjectiveStatus } from '../../types';

interface CenterColumnProps {
  selectedCardId?: string;
  onSelectCard: (card: ActionCardType) => void;
  onAction: (cardId: string, action: ActionType) => void;
  activeFilter: 'all' | 'high_risk' | 'low_confidence';
  onFilterChange: (filter: 'all' | 'high_risk' | 'low_confidence') => void;
  activeView: ObjectiveStatus | 'needs_decision';
}

const filterButtons = [
  { id: 'all' as const, label: 'All' },
  { id: 'high_risk' as const, label: 'High Risk' },
  { id: 'low_confidence' as const, label: 'Low Confidence' },
];

export function CenterColumn({
  selectedCardId,
  onSelectCard,
  onAction,
  activeFilter,
  onFilterChange,
  activeView,
}: CenterColumnProps) {
  // Fetch queue data
  const {
    data: cards = [],
    isLoading,
    error,
    refetch
  } = useQueue({
    filter: activeFilter,
    status: activeView === 'needs_decision' ? 'needs_decision' : activeView,
  });

  // Filter cards based on active filter
  const filteredCards = cards.filter((card) => {
    if (activeFilter === 'all') return true;
    if (activeFilter === 'high_risk') return card.riskLevel === 'high';
    if (activeFilter === 'low_confidence') return card.confidenceScore < 60;
    return true;
  });

  return (
    <section className="flex-1 flex flex-col min-w-0 overflow-hidden">
      {/* Header */}
      <motion.div
        className="px-6 py-5 border-b border-surface-border bg-surface-elevated/50"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-text-primary">Review Queue</h1>
            <p className="text-sm text-text-secondary mt-0.5">
              {filteredCards.length} item{filteredCards.length !== 1 ? 's' : ''} require{filteredCards.length === 1 ? 's' : ''} your decision
            </p>
          </div>

          <div className="flex items-center gap-1.5 p-1 rounded-lg bg-surface-card border border-surface-border">
            {filterButtons.map((btn) => (
              <button
                key={btn.id}
                onClick={() => onFilterChange(btn.id)}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                  activeFilter === btn.id
                    ? 'bg-accent-cyan/10 text-accent-cyan'
                    : 'text-text-secondary hover:text-text-primary hover:bg-surface-hover'
                }`}
              >
                {btn.label}
              </button>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Cards List */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="space-y-4 max-w-3xl mx-auto">
          {/* Loading State */}
          {isLoading && (
            <>
              {Array.from({ length: 3 }).map((_, i) => (
                <ActionCardSkeleton key={i} index={i} />
              ))}
            </>
          )}

          {/* Error State */}
          {error && !isLoading && (
            <ErrorState error={error} onRetry={() => refetch()} />
          )}

          {/* Cards or Empty State */}
          {!isLoading && !error && (
            <AnimatePresence mode="popLayout">
              {filteredCards.length > 0 ? (
                filteredCards.map((card, index) => (
                  <ActionCard
                    key={card.id}
                    card={card}
                    index={index}
                    isSelected={selectedCardId === card.id}
                    onSelect={onSelectCard}
                    onAction={onAction}
                  />
                ))
              ) : activeFilter !== 'all' ? (
                <NoFilterResultsState onClear={() => onFilterChange('all')} />
              ) : (
                <EmptyQueueState />
              )}
            </AnimatePresence>
          )}
        </div>
      </div>
    </section>
  );
}
