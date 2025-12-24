"""Audit log model for persistent security and compliance logging."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from enum import Enum

from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSON

from .base import Base


class AuditEventType(str, Enum):
    """Types of audit events."""
    # Authentication events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    MAGIC_LINK_REQUEST = "magic_link_request"
    MAGIC_LINK_VERIFY_SUCCESS = "magic_link_verify_success"
    MAGIC_LINK_VERIFY_FAILURE = "magic_link_verify_failure"
    REGISTER = "register"
    TOKEN_REFRESH = "token_refresh"

    # Session events
    SESSION_CREATED = "session_created"
    SESSION_REVOKED = "session_revoked"
    SESSION_EXPIRED = "session_expired"
    CONCURRENT_SESSION_LIMIT = "concurrent_session_limit"

    # MFA events
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    MFA_VERIFY_SUCCESS = "mfa_verify_success"
    MFA_VERIFY_FAILURE = "mfa_verify_failure"
    MFA_BACKUP_CODE_USED = "mfa_backup_code_used"
    MFA_LOCKED = "mfa_locked"

    # Device events
    NEW_DEVICE_DETECTED = "new_device_detected"
    DEVICE_TRUSTED = "device_trusted"
    DEVICE_BLOCKED = "device_blocked"
    SUSPICIOUS_DEVICE_ACTIVITY = "suspicious_device_activity"

    # Account sharing indicators
    IMPOSSIBLE_TRAVEL = "impossible_travel"
    EXCESSIVE_DEVICES = "excessive_devices"
    UNUSUAL_ACTIVITY_PATTERN = "unusual_activity_pattern"
    SHARING_SCORE_ELEVATED = "sharing_score_elevated"

    # Resource access
    RESOURCE_ACCESS = "resource_access"
    RESOURCE_CREATE = "resource_create"
    RESOURCE_UPDATE = "resource_update"
    RESOURCE_DELETE = "resource_delete"

    # Security events
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PERMISSION_DENIED = "permission_denied"
    INVALID_TOKEN = "invalid_token"
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET_REQUEST = "password_reset_request"

    # API events
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"
    API_REQUEST = "api_request"

    # Subscription events
    SUBSCRIPTION_CREATED = "subscription_created"
    SUBSCRIPTION_UPDATED = "subscription_updated"
    SUBSCRIPTION_CANCELED = "subscription_canceled"


class AuditSeverity(str, Enum):
    """Severity levels for audit events."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditLogEntry(Base):
    """
    Persistent audit log entry for security and compliance.

    Stores all security-relevant events in the database for:
    - Compliance auditing
    - Security incident investigation
    - User activity monitoring
    - Account sharing detection
    """

    __tablename__ = "audit_logs"

    # Primary key
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    # Event classification
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(
        String(20),
        default=AuditSeverity.INFO,
        nullable=False,
        index=True
    )
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # auth, security, resource, api

    # Actor information
    user_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)
    user_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    organization_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)

    # Session information
    session_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    token_jti: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Request information
    request_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True, index=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    endpoint: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    method: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Response information
    status_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    success: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Location information
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country_code: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)

    # Event details
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    failure_reason: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Resource information (for resource events)
    resource_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    __table_args__ = (
        Index('ix_audit_logs_user_time', 'user_id', 'timestamp'),
        Index('ix_audit_logs_event_type_time', 'event_type', 'timestamp'),
        Index('ix_audit_logs_severity_time', 'severity', 'timestamp'),
        Index('ix_audit_logs_ip_time', 'ip_address', 'timestamp'),
        Index('ix_audit_logs_org_time', 'organization_id', 'timestamp'),
    )

    def __repr__(self) -> str:
        return f"<AuditLogEntry(id={self.id}, event={self.event_type}, user_id={self.user_id})>"

    @classmethod
    def create(
        cls,
        event_type: AuditEventType,
        severity: AuditSeverity = AuditSeverity.INFO,
        user_id: UUID = None,
        user_email: str = None,
        organization_id: UUID = None,
        session_id: UUID = None,
        request_id: str = None,
        ip_address: str = None,
        user_agent: str = None,
        endpoint: str = None,
        method: str = None,
        status_code: int = None,
        response_time_ms: float = None,
        success: bool = True,
        city: str = None,
        country: str = None,
        message: str = None,
        details: dict = None,
        failure_reason: str = None,
        resource_type: str = None,
        resource_id: str = None,
        **kwargs
    ) -> "AuditLogEntry":
        """Factory method for creating audit log entries."""
        return cls(
            event_type=event_type.value if isinstance(event_type, AuditEventType) else event_type,
            severity=severity.value if isinstance(severity, AuditSeverity) else severity,
            user_id=user_id,
            user_email=user_email,
            organization_id=organization_id,
            session_id=session_id,
            request_id=request_id,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms,
            success=success,
            city=city,
            country=country,
            message=message,
            details=details,
            failure_reason=failure_reason,
            resource_type=resource_type,
            resource_id=resource_id,
            **kwargs
        )
