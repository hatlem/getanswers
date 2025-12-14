"""Add onboarding_completed field to users table

Revision ID: 005_add_onboarding_completed
Revises: 004_user_orgs
Create Date: 2025-12-14

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005_add_onboarding_completed'
down_revision = '004_user_orgs'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add onboarding_completed column to users table
    op.add_column(
        'users',
        sa.Column('onboarding_completed', sa.Boolean(), nullable=False, server_default='false')
    )


def downgrade() -> None:
    # Remove onboarding_completed column from users table
    op.drop_column('users', 'onboarding_completed')
