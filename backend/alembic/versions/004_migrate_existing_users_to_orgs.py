"""Migrate existing users to personal organizations

Revision ID: 004_migrate_existing_users_to_orgs
Revises: 003_add_multi_tenancy
Create Date: 2024-12-14

This migration creates a personal organization for each existing user
and sets up their organization membership.
"""
from typing import Sequence, Union
import uuid
import secrets
import re
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = '004_migrate_existing_users_to_orgs'
down_revision: Union[str, None] = '003_add_multi_tenancy'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def generate_slug(email: str) -> str:
    """Generate a unique slug from email."""
    base = email.split('@')[0] if email else 'user'
    slug = re.sub(r'[^a-z0-9]+', '-', base.lower()).strip('-')
    slug = f"{slug}-{secrets.token_hex(4)}"
    return slug[:100]


def upgrade() -> None:
    # Get connection
    conn = op.get_bind()

    # Get all users without an organization
    users = conn.execute(
        text("""
            SELECT u.id, u.email, u.name
            FROM users u
            LEFT JOIN organization_members om ON om.user_id = u.id
            WHERE om.id IS NULL
        """)
    ).fetchall()

    now = datetime.utcnow()

    for user in users:
        user_id = user[0]
        email = user[1]
        name = user[2]

        # Create organization
        org_id = uuid.uuid4()
        slug = generate_slug(email)
        org_name = f"{name}'s Workspace"

        conn.execute(
            text("""
                INSERT INTO organizations (id, name, slug, is_personal, is_active, created_at, updated_at)
                VALUES (:id, :name, :slug, true, true, :now, :now)
            """),
            {
                'id': str(org_id),
                'name': org_name,
                'slug': slug,
                'now': now
            }
        )

        # Create membership
        member_id = uuid.uuid4()
        conn.execute(
            text("""
                INSERT INTO organization_members (id, organization_id, user_id, role, is_active, accepted_at, created_at, updated_at)
                VALUES (:id, :org_id, :user_id, 'owner', true, :now, :now, :now)
            """),
            {
                'id': str(member_id),
                'org_id': str(org_id),
                'user_id': str(user_id),
                'now': now
            }
        )

        # Set as user's current organization
        conn.execute(
            text("""
                UPDATE users SET current_organization_id = :org_id WHERE id = :user_id
            """),
            {
                'org_id': str(org_id),
                'user_id': str(user_id)
            }
        )

    print(f"Migrated {len(users)} users to personal organizations")


def downgrade() -> None:
    # Get connection
    conn = op.get_bind()

    # Remove all personal organizations (this will cascade delete memberships)
    conn.execute(text("DELETE FROM organizations WHERE is_personal = true"))

    # Clear current_organization_id from all users
    conn.execute(text("UPDATE users SET current_organization_id = NULL"))
