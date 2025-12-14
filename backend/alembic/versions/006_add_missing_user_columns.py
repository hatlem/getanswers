"""Add missing user columns (outlook_credentials, smtp_credentials, email_provider)

Revision ID: 006_add_missing_user_columns
Revises: 005_add_onboarding_completed
Create Date: 2025-12-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = '006_add_missing_user_columns'
down_revision = '005_add_onboarding_completed'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing columns to users table
    op.add_column(
        'users',
        sa.Column('outlook_credentials', JSON, nullable=True)
    )
    op.add_column(
        'users',
        sa.Column('smtp_credentials', JSON, nullable=True)
    )
    op.add_column(
        'users',
        sa.Column('email_provider', sa.String(20), nullable=True)
    )


def downgrade() -> None:
    # Remove columns from users table
    op.drop_column('users', 'email_provider')
    op.drop_column('users', 'smtp_credentials')
    op.drop_column('users', 'outlook_credentials')
