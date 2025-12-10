import { motion, AnimatePresence } from 'framer-motion';
import { ActionCard } from '../cards/ActionCard';
import type { ActionCard as ActionCardType, ActionType } from '../../types';

interface CenterColumnProps {
  cards: ActionCardType[];
  selectedCardId?: string;
  onSelectCard: (card: ActionCardType) => void;
  onAction: (cardId: string, action: ActionType) => void;
  activeFilter: 'all' | 'high_risk' | 'low_confidence';
  onFilterChange: (filter: 'all' | 'high_risk' | 'low_confidence') => void;
}

const filterButtons = [
  { id: 'all' as const, label: 'All' },
  { id: 'high_risk' as const, label: 'High Risk' },
  { id: 'low_confidence' as const, label: 'Low Confidence' },
];

export function CenterColumn({
  cards,
  selectedCardId,
  onSelectCard,
  onAction,
  activeFilter,
  onFilterChange,
}: CenterColumnProps) {
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
            ) : (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex flex-col items-center justify-center py-16 text-center"
              >
                <div className="w-16 h-16 rounded-full bg-success-muted flex items-center justify-center mb-4">
                  <svg
                    className="w-8 h-8 text-success"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-text-primary mb-1">
                  All Clear
                </h3>
                <p className="text-sm text-text-secondary max-w-xs">
                  No items match the current filter. Your AI agent is handling everything autonomously.
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </section>
  );
}
