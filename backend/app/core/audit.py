"""Audit logging for security monitoring and compliance."""

import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from enum import Enum

# Configure audit logger
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)


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

    # Resource access
    RESOURCE_ACCESS = "resource_access"
    RESOURCE_CREATE = "resource_create"
    RESOURCE_UPDATE = "resource_update"
    RESOURCE_DELETE = "resource_delete"

    # Queue actions
    ACTION_APPROVE = "action_approve"
    ACTION_REJECT = "action_reject"
    ACTION_EDIT = "action_edit"
    ACTION_ESCALATE = "action_escalate"

    # Security events
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PERMISSION_DENIED = "permission_denied"
    INVALID_TOKEN = "invalid_token"

    # API access
    API_REQUEST = "api_request"


class AuditLog:
    """
    Centralized audit logging for security and compliance.

    All security-relevant events should be logged through this class.
    Logs are structured for easy parsing and analysis.
    """

    @staticmethod
    def _log_event(
        event_type: AuditEventType,
        user_id: Optional[str],
        email: Optional[str],
        ip_address: str,
        success: bool,
        details: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
    ) -> None:
        """
        Internal method to log an audit event.

        Args:
            event_type: Type of audit event
            user_id: User ID if authenticated
            email: User email if available
            ip_address: Client IP address
            success: Whether the action succeeded
            details: Additional event details
            message: Human-readable message
        """
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type.value,
            "user_id": user_id,
            "email": email,
            "ip_address": ip_address,
            "success": success,
            "details": details or {},
        }

        log_message = message or f"{event_type.value}: {'success' if success else 'failure'}"

        if success:
            audit_logger.info(log_message, extra=log_data)
        else:
            audit_logger.warning(log_message, extra=log_data)

    @staticmethod
    async def log_login_attempt(
        email: str,
        success: bool,
        ip_address: str,
        user_id: Optional[str] = None,
        failure_reason: Optional[str] = None,
    ) -> None:
        """
        Log authentication attempt.

        Args:
            email: Email address used for login
            success: Whether login succeeded
            ip_address: Client IP address
            user_id: User ID if login succeeded
            failure_reason: Reason for failure (e.g., "invalid_password", "user_not_found")

        Example:
            await AuditLog.log_login_attempt(
                email="user@example.com",
                success=True,
                ip_address="192.168.1.1",
                user_id="user-123"
            )
        """
        details = {}
        if failure_reason:
            details["failure_reason"] = failure_reason

        AuditLog._log_event(
            event_type=AuditEventType.LOGIN_SUCCESS if success else AuditEventType.LOGIN_FAILURE,
            user_id=user_id,
            email=email,
            ip_address=ip_address,
            success=success,
            details=details,
            message=f"Login attempt for {email}: {'success' if success else 'failure'}",
        )

    @staticmethod
    async def log_magic_link_request(
        email: str,
        ip_address: str,
        success: bool = True,
    ) -> None:
        """
        Log magic link request.

        Args:
            email: Email address requesting magic link
            ip_address: Client IP address
            success: Whether request succeeded
        """
        AuditLog._log_event(
            event_type=AuditEventType.MAGIC_LINK_REQUEST,
            user_id=None,
            email=email,
            ip_address=ip_address,
            success=success,
            message=f"Magic link requested for {email}",
        )

    @staticmethod
    async def log_magic_link_verify(
        email: str,
        ip_address: str,
        success: bool,
        user_id: Optional[str] = None,
        failure_reason: Optional[str] = None,
    ) -> None:
        """
        Log magic link verification attempt.

        Args:
            email: Email address from magic link
            ip_address: Client IP address
            success: Whether verification succeeded
            user_id: User ID if verification succeeded
            failure_reason: Reason for failure (e.g., "expired", "already_used", "invalid_token")
        """
        details = {}
        if failure_reason:
            details["failure_reason"] = failure_reason

        AuditLog._log_event(
            event_type=AuditEventType.MAGIC_LINK_VERIFY_SUCCESS if success else AuditEventType.MAGIC_LINK_VERIFY_FAILURE,
            user_id=user_id,
            email=email,
            ip_address=ip_address,
            success=success,
            details=details,
            message=f"Magic link verification for {email}: {'success' if success else 'failure'}",
        )

    @staticmethod
    async def log_registration(
        email: str,
        ip_address: str,
        success: bool,
        user_id: Optional[str] = None,
    ) -> None:
        """
        Log user registration.

        Args:
            email: Email address for new user
            ip_address: Client IP address
            success: Whether registration succeeded
            user_id: User ID if registration succeeded
        """
        AuditLog._log_event(
            event_type=AuditEventType.REGISTER,
            user_id=user_id,
            email=email,
            ip_address=ip_address,
            success=success,
            message=f"User registration for {email}: {'success' if success else 'failure'}",
        )

    @staticmethod
    async def log_action(
        user_id: str,
        action_type: str,
        resource_type: str,
        resource_id: str,
        ip_address: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log user action on a resource.

        Args:
            user_id: User performing the action
            action_type: Type of action (approve, reject, edit, etc.)
            resource_type: Type of resource (action, conversation, etc.)
            resource_id: ID of the resource
            ip_address: Client IP address
            details: Additional action details

        Example:
            await AuditLog.log_action(
                user_id="user-123",
                action_type="approve",
                resource_type="agent_action",
                resource_id="action-456",
                ip_address="192.168.1.1",
                details={"notes": "Looks good"}
            )
        """
        event_type_map = {
            "approve": AuditEventType.ACTION_APPROVE,
            "reject": AuditEventType.ACTION_REJECT,
            "override": AuditEventType.ACTION_REJECT,
            "edit": AuditEventType.ACTION_EDIT,
            "escalate": AuditEventType.ACTION_ESCALATE,
            "create": AuditEventType.RESOURCE_CREATE,
            "update": AuditEventType.RESOURCE_UPDATE,
            "delete": AuditEventType.RESOURCE_DELETE,
        }

        event_type = event_type_map.get(action_type.lower(), AuditEventType.RESOURCE_ACCESS)

        action_details = {
            "action_type": action_type,
            "resource_type": resource_type,
            "resource_id": resource_id,
            **(details or {}),
        }

        AuditLog._log_event(
            event_type=event_type,
            user_id=user_id,
            email=None,
            ip_address=ip_address,
            success=True,
            details=action_details,
            message=f"User {user_id} performed {action_type} on {resource_type}:{resource_id}",
        )

    @staticmethod
    async def log_api_access(
        user_id: Optional[str],
        endpoint: str,
        method: str,
        status_code: int,
        ip_address: str,
        response_time_ms: Optional[float] = None,
    ) -> None:
        """
        Log API access for monitoring and security analysis.

        Args:
            user_id: User ID if authenticated
            endpoint: API endpoint path
            method: HTTP method (GET, POST, etc.)
            status_code: HTTP status code
            ip_address: Client IP address
            response_time_ms: Response time in milliseconds

        Example:
            await AuditLog.log_api_access(
                user_id="user-123",
                endpoint="/api/queue",
                method="GET",
                status_code=200,
                ip_address="192.168.1.1",
                response_time_ms=45.2
            )
        """
        details = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
        }

        if response_time_ms is not None:
            details["response_time_ms"] = response_time_ms

        success = 200 <= status_code < 300

        AuditLog._log_event(
            event_type=AuditEventType.API_REQUEST,
            user_id=user_id,
            email=None,
            ip_address=ip_address,
            success=success,
            details=details,
            message=f"{method} {endpoint} - {status_code}",
        )

    @staticmethod
    async def log_unauthorized_access(
        endpoint: str,
        ip_address: str,
        reason: str,
        attempted_user_id: Optional[str] = None,
    ) -> None:
        """
        Log unauthorized access attempt.

        Args:
            endpoint: API endpoint attempted
            ip_address: Client IP address
            reason: Reason for denial (e.g., "invalid_token", "permission_denied")
            attempted_user_id: User ID if token was provided but invalid
        """
        event_type = (
            AuditEventType.PERMISSION_DENIED
            if attempted_user_id
            else AuditEventType.UNAUTHORIZED_ACCESS
        )

        AuditLog._log_event(
            event_type=event_type,
            user_id=attempted_user_id,
            email=None,
            ip_address=ip_address,
            success=False,
            details={"endpoint": endpoint, "reason": reason},
            message=f"Unauthorized access attempt to {endpoint}: {reason}",
        )

    @staticmethod
    async def log_rate_limit_exceeded(
        endpoint: str,
        ip_address: str,
        limit: int,
        window_seconds: int,
        user_id: Optional[str] = None,
    ) -> None:
        """
        Log rate limit exceeded event.

        Args:
            endpoint: API endpoint that was rate limited
            ip_address: Client IP address
            limit: Rate limit threshold
            window_seconds: Time window for rate limit
            user_id: User ID if authenticated
        """
        AuditLog._log_event(
            event_type=AuditEventType.RATE_LIMIT_EXCEEDED,
            user_id=user_id,
            email=None,
            ip_address=ip_address,
            success=False,
            details={
                "endpoint": endpoint,
                "limit": limit,
                "window_seconds": window_seconds,
            },
            message=f"Rate limit exceeded for {endpoint} from {ip_address}",
        )


def configure_audit_logging(log_file: Optional[str] = None) -> None:
    """
    Configure audit logging with file handler.

    Args:
        log_file: Path to audit log file. If None, only console output.

    Example:
        configure_audit_logging("/var/log/getanswers/audit.log")
    """
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(extras)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    audit_logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        audit_logger.addHandler(file_handler)

    audit_logger.info("Audit logging configured")
