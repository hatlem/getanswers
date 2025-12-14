"""Add multi-tenancy support with organizations

Revision ID: 003_multitenancy
Revises: 002_billing_features
Create Date: 2024-12-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003_multitenancy'
down_revision: Union[str, None] = '002_billing_features'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), unique=True, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('settings', postgresql.JSON, nullable=True),
        sa.Column('logo_url', sa.String(512), nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('is_personal', sa.Boolean, default=False, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_organizations_slug', 'organizations', ['slug'])

    # Create organization_members table
    op.create_table(
        'organization_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False, default='member'),
        sa.Column('permissions', postgresql.JSON, nullable=True),
        sa.Column('invited_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('invited_at', sa.DateTime, nullable=True),
        sa.Column('accepted_at', sa.DateTime, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_org_member_org_user', 'organization_members', ['organization_id', 'user_id'], unique=True)
    op.create_index('ix_org_member_user', 'organization_members', ['user_id'])

    # Create organization_invites table
    op.create_table(
        'organization_invites',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('role', sa.String(20), nullable=False, default='member'),
        sa.Column('token', sa.String(255), unique=True, nullable=False),
        sa.Column('invited_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('accepted_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_organization_invites_email', 'organization_invites', ['email'])
    op.create_index('ix_organization_invites_token', 'organization_invites', ['token'])

    # Add columns to users table
    op.add_column('users', sa.Column('is_super_admin', sa.Boolean, default=False, nullable=False, server_default='false'))
    op.add_column('users', sa.Column('current_organization_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_users_current_organization',
        'users', 'organizations',
        ['current_organization_id'], ['id'],
        ondelete='SET NULL'
    )

    # Add organization_id to subscriptions table
    op.add_column('subscriptions', sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_subscriptions_organization',
        'subscriptions', 'organizations',
        ['organization_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_index('ix_subscriptions_organization_id', 'subscriptions', ['organization_id'])

    # Make user_id nullable on subscriptions (can be either user or org subscription)
    op.alter_column('subscriptions', 'user_id', nullable=True)

    # Drop unique constraint on user_id (since we now have org subscriptions too)
    # Note: This depends on how the constraint was named in the original migration
    try:
        op.drop_constraint('subscriptions_user_id_key', 'subscriptions', type_='unique')
    except:
        pass  # Constraint may have different name or not exist


def downgrade() -> None:
    # Remove foreign key and column from subscriptions
    op.drop_constraint('fk_subscriptions_organization', 'subscriptions', type_='foreignkey')
    op.drop_index('ix_subscriptions_organization_id', 'subscriptions')
    op.drop_column('subscriptions', 'organization_id')

    # Make user_id required again
    op.alter_column('subscriptions', 'user_id', nullable=False)

    # Try to recreate unique constraint
    try:
        op.create_unique_constraint('subscriptions_user_id_key', 'subscriptions', ['user_id'])
    except:
        pass

    # Remove columns from users table
    op.drop_constraint('fk_users_current_organization', 'users', type_='foreignkey')
    op.drop_column('users', 'current_organization_id')
    op.drop_column('users', 'is_super_admin')

    # Drop organization_invites table
    op.drop_index('ix_organization_invites_token', 'organization_invites')
    op.drop_index('ix_organization_invites_email', 'organization_invites')
    op.drop_table('organization_invites')

    # Drop organization_members table
    op.drop_index('ix_org_member_user', 'organization_members')
    op.drop_index('ix_org_member_org_user', 'organization_members')
    op.drop_table('organization_members')

    # Drop organizations table
    op.drop_index('ix_organizations_slug', 'organizations')
    op.drop_table('organizations')
