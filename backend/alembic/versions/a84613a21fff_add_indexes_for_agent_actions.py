"""add_indexes_for_agent_actions

Revision ID: a84613a21fff
Revises: a753499c54b6
Create Date: 2025-12-11 14:09:38.931474

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a84613a21fff'
down_revision: Union[str, None] = 'a753499c54b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add index on agent_actions.status for filtering queries
    op.create_index(
        'ix_agent_actions_status',
        'agent_actions',
        ['status'],
        unique=False
    )

    # Note: conversation_id already has an index from the model definition
    # (index=True in the ForeignKey column), so we don't need to add it again


def downgrade() -> None:
    # Drop the indexes in reverse order
    op.drop_index('ix_agent_actions_status', table_name='agent_actions')
