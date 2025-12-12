import { useState, useEffect } from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import type { ActionCard } from '../../types';

export interface EditModalProps {
  isOpen: boolean;
  onClose: () => void;
  card: ActionCard | null;
  onSave: (cardId: string, content: string) => void;
  isSaving?: boolean;
}

export function EditModal({
  isOpen,
  onClose,
  card,
  onSave,
  isSaving = false,
}: EditModalProps) {
  const [editedContent, setEditedContent] = useState('');

  // Update content when card changes
  useEffect(() => {
    if (card) {
      setEditedContent(card.proposedAction);
    }
  }, [card]);

  const handleSave = () => {
    if (card && editedContent.trim()) {
      onSave(card.id, editedContent.trim());
    }
  };

  const handleClose = () => {
    onClose();
    // Reset content after closing animation
    setTimeout(() => setEditedContent(''), 200);
  };

  if (!card) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Edit Proposed Action"
      size="lg"
    >
      <div className="space-y-4">
        {/* Card info */}
        <div className="p-3 bg-surface-card rounded-lg border border-surface-border">
          <p className="text-sm text-text-secondary mb-1">Editing action for:</p>
          <p className="text-sm font-medium text-text-primary">{card.summary}</p>
        </div>

        {/* Edit textarea */}
        <div>
          <label
            htmlFor="edit-content"
            className="block text-sm font-medium text-text-secondary mb-2"
          >
            Proposed Action Content
          </label>
          <textarea
            id="edit-content"
            value={editedContent}
            onChange={(e) => setEditedContent(e.target.value)}
            rows={8}
            className="w-full px-4 py-3 rounded-lg bg-surface-card border border-surface-border text-text-primary placeholder:text-text-muted text-sm focus:outline-none focus:border-accent-cyan/50 focus:ring-1 focus:ring-accent-cyan/20 transition-all resize-none"
            placeholder="Enter the edited action content..."
          />
          <p className="mt-2 text-xs text-text-muted">
            Edit the AI's proposed action. This will update what gets sent when approved.
          </p>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-3 pt-2">
          <Button
            variant="outline"
            onClick={handleClose}
            disabled={isSaving}
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleSave}
            isLoading={isSaving}
            disabled={!editedContent.trim() || editedContent === card.proposedAction}
          >
            Save Changes
          </Button>
        </div>
      </div>
    </Modal>
  );
}
