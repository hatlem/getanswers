"""add lead magnet leads table

Revision ID: 007
Revises: 006
Create Date: 2024-12-21

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create lead_magnet_leads table
    op.create_table(
        'lead_magnet_leads',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('company', sa.String(length=255), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('download_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_seen_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('converted_at', sa.DateTime(), nullable=True),
        sa.Column('converted_to', sa.String(length=50), nullable=True),
        sa.Column('converted_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('utm_source', sa.String(length=100), nullable=True),
        sa.Column('utm_medium', sa.String(length=100), nullable=True),
        sa.Column('utm_campaign', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['converted_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_lead_magnet_leads_email', 'lead_magnet_leads', ['email'])
    op.create_index('ix_lead_magnet_leads_source', 'lead_magnet_leads', ['source'])
    op.create_index('ix_lead_magnet_leads_converted_at', 'lead_magnet_leads', ['converted_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_lead_magnet_leads_converted_at', table_name='lead_magnet_leads')
    op.drop_index('ix_lead_magnet_leads_source', table_name='lead_magnet_leads')
    op.drop_index('ix_lead_magnet_leads_email', table_name='lead_magnet_leads')

    # Drop table
    op.drop_table('lead_magnet_leads')
