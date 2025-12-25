"""Add security and compliance tables

Revision ID: 009_security_compliance
Revises: a84613a21fff
Create Date: 2024-12-24

Adds tables for:
- user_sessions: Session management with device tracking
- device_history: Device fingerprint history
- user_mfa: Multi-factor authentication configuration
- audit_logs: Persistent audit log entries
- usage_metrics: Per-user usage and cost tracking
- usage_alerts: Usage limit notifications
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

# revision identifiers, used by Alembic.
revision: str = '009_security_compliance'
down_revision: Union[str, None] = 'a84613a21fff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_sessions table
    op.create_table(
        'user_sessions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_jti', sa.String(64), unique=True, nullable=False),
        sa.Column('device_fingerprint', sa.String(256), nullable=True),
        sa.Column('user_agent', sa.String(512), nullable=True),
        sa.Column('device_type', sa.String(50), nullable=True),
        sa.Column('browser', sa.String(100), nullable=True),
        sa.Column('os', sa.String(100), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=False),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('country_code', sa.String(2), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.Column('revoked_reason', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_activity', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_new_device', sa.Boolean(), default=False, nullable=False),
        sa.Column('is_new_location', sa.Boolean(), default=False, nullable=False),
        sa.Column('trust_score', sa.Float(), nullable=True),
    )

    # Create indexes for user_sessions
    op.create_index('ix_user_sessions_user_id', 'user_sessions', ['user_id'])
    op.create_index('ix_user_sessions_token_jti', 'user_sessions', ['token_jti'])
    op.create_index('ix_user_sessions_user_active', 'user_sessions', ['user_id', 'is_active'])
    op.create_index('ix_user_sessions_expires', 'user_sessions', ['expires_at'])
    op.create_index('ix_user_sessions_ip', 'user_sessions', ['ip_address'])

    # Create device_history table
    op.create_table(
        'device_history',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('device_fingerprint', sa.String(256), nullable=False),
        sa.Column('user_agent', sa.String(512), nullable=True),
        sa.Column('device_type', sa.String(50), nullable=True),
        sa.Column('browser', sa.String(100), nullable=True),
        sa.Column('os', sa.String(100), nullable=True),
        sa.Column('device_name', sa.String(100), nullable=True),
        sa.Column('last_ip_address', sa.String(45), nullable=True),
        sa.Column('last_city', sa.String(100), nullable=True),
        sa.Column('last_country', sa.String(100), nullable=True),
        sa.Column('last_country_code', sa.String(2), nullable=True),
        sa.Column('last_latitude', sa.Float(), nullable=True),
        sa.Column('last_longitude', sa.Float(), nullable=True),
        sa.Column('trust_level', sa.String(20), default='unknown', nullable=False),
        sa.Column('is_verified', sa.Boolean(), default=False, nullable=False),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.Column('login_count', sa.Integer(), default=1, nullable=False),
        sa.Column('first_seen', sa.DateTime(), nullable=False),
        sa.Column('last_seen', sa.DateTime(), nullable=False),
        sa.Column('suspicious_activity_count', sa.Integer(), default=0, nullable=False),
        sa.Column('last_suspicious_activity', sa.DateTime(), nullable=True),
    )

    # Create indexes for device_history
    op.create_index('ix_device_history_user_id', 'device_history', ['user_id'])
    op.create_index('ix_device_history_fingerprint', 'device_history', ['device_fingerprint'])
    op.create_index('ix_device_history_user_trust', 'device_history', ['user_id', 'trust_level'])
    op.create_index('ix_device_history_last_seen', 'device_history', ['last_seen'])
    op.create_unique_constraint('uq_user_device', 'device_history', ['user_id', 'device_fingerprint'])

    # Create user_mfa table
    op.create_table(
        'user_mfa',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('totp_secret', sa.String(256), nullable=True),
        sa.Column('totp_enabled', sa.Boolean(), default=False, nullable=False),
        sa.Column('totp_verified_at', sa.DateTime(), nullable=True),
        sa.Column('backup_codes', JSON, nullable=True),
        sa.Column('backup_codes_generated_at', sa.DateTime(), nullable=True),
        sa.Column('backup_codes_remaining', sa.Integer(), default=0, nullable=False),
        sa.Column('email_mfa_enabled', sa.Boolean(), default=False, nullable=False),
        sa.Column('failed_attempts', sa.Integer(), default=0, nullable=False),
        sa.Column('last_failed_attempt', sa.DateTime(), nullable=True),
        sa.Column('locked_until', sa.DateTime(), nullable=True),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.Column('total_verifications', sa.Integer(), default=0, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # Create index for user_mfa
    op.create_index('ix_user_mfa_user_id', 'user_mfa', ['user_id'])

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), default='info', nullable=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=True),
        sa.Column('user_email', sa.String(255), nullable=True),
        sa.Column('organization_id', UUID(as_uuid=True), nullable=True),
        sa.Column('session_id', UUID(as_uuid=True), nullable=True),
        sa.Column('token_jti', sa.String(64), nullable=True),
        sa.Column('request_id', sa.String(64), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(512), nullable=True),
        sa.Column('endpoint', sa.String(200), nullable=True),
        sa.Column('method', sa.String(10), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('response_time_ms', sa.Float(), nullable=True),
        sa.Column('success', sa.Boolean(), default=True, nullable=False),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('country_code', sa.String(2), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('details', JSON, nullable=True),
        sa.Column('failure_reason', sa.String(100), nullable=True),
        sa.Column('resource_type', sa.String(50), nullable=True),
        sa.Column('resource_id', sa.String(64), nullable=True),
    )

    # Create indexes for audit_logs
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'])
    op.create_index('ix_audit_logs_event_type', 'audit_logs', ['event_type'])
    op.create_index('ix_audit_logs_severity', 'audit_logs', ['severity'])
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_organization_id', 'audit_logs', ['organization_id'])
    op.create_index('ix_audit_logs_request_id', 'audit_logs', ['request_id'])
    op.create_index('ix_audit_logs_ip_address', 'audit_logs', ['ip_address'])
    op.create_index('ix_audit_logs_user_time', 'audit_logs', ['user_id', 'timestamp'])
    op.create_index('ix_audit_logs_event_type_time', 'audit_logs', ['event_type', 'timestamp'])
    op.create_index('ix_audit_logs_severity_time', 'audit_logs', ['severity', 'timestamp'])
    op.create_index('ix_audit_logs_ip_time', 'audit_logs', ['ip_address', 'timestamp'])
    op.create_index('ix_audit_logs_org_time', 'audit_logs', ['organization_id', 'timestamp'])

    # Create usage_metrics table
    op.create_table(
        'usage_metrics',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('emails_received', sa.Integer(), default=0, nullable=False),
        sa.Column('emails_sent', sa.Integer(), default=0, nullable=False),
        sa.Column('emails_processed', sa.Integer(), default=0, nullable=False),
        sa.Column('ai_requests', sa.Integer(), default=0, nullable=False),
        sa.Column('ai_responses_generated', sa.Integer(), default=0, nullable=False),
        sa.Column('ai_tokens_input', sa.Integer(), default=0, nullable=False),
        sa.Column('ai_tokens_output', sa.Integer(), default=0, nullable=False),
        sa.Column('api_calls', sa.Integer(), default=0, nullable=False),
        sa.Column('api_calls_failed', sa.Integer(), default=0, nullable=False),
        sa.Column('storage_used_bytes', sa.BigInteger(), default=0, nullable=False),
        sa.Column('attachments_stored', sa.Integer(), default=0, nullable=False),
        sa.Column('login_count', sa.Integer(), default=0, nullable=False),
        sa.Column('session_duration_minutes', sa.Integer(), default=0, nullable=False),
        sa.Column('unique_ips', sa.Integer(), default=0, nullable=False),
        sa.Column('unique_devices', sa.Integer(), default=0, nullable=False),
        sa.Column('ai_cost_cents', sa.Integer(), default=0, nullable=False),
        sa.Column('email_cost_cents', sa.Integer(), default=0, nullable=False),
        sa.Column('storage_cost_cents', sa.Integer(), default=0, nullable=False),
        sa.Column('total_cost_cents', sa.Integer(), default=0, nullable=False),
        sa.Column('is_over_limit', sa.Boolean(), default=False, nullable=False),
        sa.Column('limit_warning_sent', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # Create indexes for usage_metrics
    op.create_index('ix_usage_metrics_user_id', 'usage_metrics', ['user_id'])
    op.create_index('ix_usage_metrics_organization_id', 'usage_metrics', ['organization_id'])
    op.create_index('ix_usage_metrics_period', 'usage_metrics', ['period_start'])
    op.create_index('ix_usage_metrics_cost', 'usage_metrics', ['total_cost_cents'])
    op.create_unique_constraint('uq_user_period', 'usage_metrics', ['user_id', 'period_start'])

    # Create usage_alerts table
    op.create_table(
        'usage_alerts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('alert_type', sa.String(50), nullable=False),
        sa.Column('metric_name', sa.String(50), nullable=False),
        sa.Column('current_value', sa.Integer(), nullable=False),
        sa.Column('limit_value', sa.Integer(), nullable=True),
        sa.Column('threshold_percentage', sa.Integer(), nullable=True),
        sa.Column('is_acknowledged', sa.Boolean(), default=False, nullable=False),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('notification_sent', sa.Boolean(), default=False, nullable=False),
        sa.Column('notification_sent_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # Create index for usage_alerts
    op.create_index('ix_usage_alerts_user_id', 'usage_alerts', ['user_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_usage_alerts_user_id', 'usage_alerts')
    op.drop_table('usage_alerts')

    op.drop_constraint('uq_user_period', 'usage_metrics', type_='unique')
    op.drop_index('ix_usage_metrics_cost', 'usage_metrics')
    op.drop_index('ix_usage_metrics_period', 'usage_metrics')
    op.drop_index('ix_usage_metrics_organization_id', 'usage_metrics')
    op.drop_index('ix_usage_metrics_user_id', 'usage_metrics')
    op.drop_table('usage_metrics')

    op.drop_index('ix_audit_logs_org_time', 'audit_logs')
    op.drop_index('ix_audit_logs_ip_time', 'audit_logs')
    op.drop_index('ix_audit_logs_severity_time', 'audit_logs')
    op.drop_index('ix_audit_logs_event_type_time', 'audit_logs')
    op.drop_index('ix_audit_logs_user_time', 'audit_logs')
    op.drop_index('ix_audit_logs_ip_address', 'audit_logs')
    op.drop_index('ix_audit_logs_request_id', 'audit_logs')
    op.drop_index('ix_audit_logs_organization_id', 'audit_logs')
    op.drop_index('ix_audit_logs_user_id', 'audit_logs')
    op.drop_index('ix_audit_logs_severity', 'audit_logs')
    op.drop_index('ix_audit_logs_event_type', 'audit_logs')
    op.drop_index('ix_audit_logs_timestamp', 'audit_logs')
    op.drop_table('audit_logs')

    op.drop_index('ix_user_mfa_user_id', 'user_mfa')
    op.drop_table('user_mfa')

    op.drop_constraint('uq_user_device', 'device_history', type_='unique')
    op.drop_index('ix_device_history_last_seen', 'device_history')
    op.drop_index('ix_device_history_user_trust', 'device_history')
    op.drop_index('ix_device_history_fingerprint', 'device_history')
    op.drop_index('ix_device_history_user_id', 'device_history')
    op.drop_table('device_history')

    op.drop_index('ix_user_sessions_ip', 'user_sessions')
    op.drop_index('ix_user_sessions_expires', 'user_sessions')
    op.drop_index('ix_user_sessions_user_active', 'user_sessions')
    op.drop_index('ix_user_sessions_token_jti', 'user_sessions')
    op.drop_index('ix_user_sessions_user_id', 'user_sessions')
    op.drop_table('user_sessions')
