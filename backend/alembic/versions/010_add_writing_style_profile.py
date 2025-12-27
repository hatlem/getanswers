"""add writing_style_profile to users

Revision ID: 010_add_writing_style_profile
Revises: 009_security_compliance_tables
Create Date: 2025-12-26

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '010_add_writing_style_profile'
down_revision = '009_security_compliance'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add writing_style_profile column to users table
    op.add_column('users', sa.Column('writing_style_profile', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove writing_style_profile column from users table
    op.drop_column('users', 'writing_style_profile')
