"""Add needs_password_setup field to users table

Revision ID: 007_add_needs_password_setup
Revises: 006_add_missing_user_columns
Create Date: 2025-12-14

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007_add_needs_password_setup'
down_revision = '006_add_missing_user_columns'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add needs_password_setup column to users table
    op.add_column(
        'users',
        sa.Column('needs_password_setup', sa.Boolean(), nullable=False, server_default='false')
    )


def downgrade() -> None:
    # Remove needs_password_setup column from users table
    op.drop_column('users', 'needs_password_setup')
