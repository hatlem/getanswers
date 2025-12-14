"""Add google_id to users table

Revision ID: 008_google_oauth
Revises: 007_add_needs_password_setup
Create Date: 2024-12-14

Adds google_id column for Google OAuth authentication.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '008_google_oauth'
down_revision: Union[str, None] = '007_add_needs_password_setup'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add google_id column
    op.add_column('users', sa.Column('google_id', sa.String(255), nullable=True))

    # Add index for faster lookups
    op.create_index('ix_users_google_id', 'users', ['google_id'])


def downgrade() -> None:
    op.drop_index('ix_users_google_id', 'users')
    op.drop_column('users', 'google_id')
