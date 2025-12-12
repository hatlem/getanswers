"""add_missing_agent_action_columns

Revision ID: a753499c54b6
Revises: 001
Create Date: 2025-12-11 12:15:14.664545

This migration adds columns that were missing from the agent_actions table.
These columns exist in the SQLAlchemy model but were not in the database.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a753499c54b6'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing columns to agent_actions table
    # Using IF NOT EXISTS pattern for idempotency (columns may already exist from manual fix)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name = 'agent_actions' AND column_name = 'priority_score') THEN
                ALTER TABLE agent_actions ADD COLUMN priority_score INTEGER NOT NULL DEFAULT 50;
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name = 'agent_actions' AND column_name = 'override_reason') THEN
                ALTER TABLE agent_actions ADD COLUMN override_reason TEXT;
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name = 'agent_actions' AND column_name = 'escalation_note') THEN
                ALTER TABLE agent_actions ADD COLUMN escalation_note TEXT;
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name = 'agent_actions' AND column_name = 'approved_at') THEN
                ALTER TABLE agent_actions ADD COLUMN approved_at TIMESTAMP;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    # Remove the columns added in upgrade
    op.drop_column('agent_actions', 'approved_at')
    op.drop_column('agent_actions', 'escalation_note')
    op.drop_column('agent_actions', 'override_reason')
    op.drop_column('agent_actions', 'priority_score')
