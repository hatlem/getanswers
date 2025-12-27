"""Add microsoft_id to users table

Revision ID: 012_add_microsoft_id
Revises: 011_lead_magnet_leads
Create Date: 2024-12-27

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '012_add_microsoft_id'
down_revision = '011_lead_magnet_leads'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('microsoft_id', sa.String(length=255), nullable=True))
    op.create_index('ix_users_microsoft_id', 'users', ['microsoft_id'])


def downgrade() -> None:
    op.drop_index('ix_users_microsoft_id', table_name='users')
    op.drop_column('users', 'microsoft_id')
