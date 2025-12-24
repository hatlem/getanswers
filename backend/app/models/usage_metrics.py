"""Usage metrics model for tracking per-user costs and usage."""
from datetime import datetime, date
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, Integer, BigInteger, Float, ForeignKey, Date, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import Base


class UsageMetrics(Base):
    """
    Monthly usage metrics for cost tracking and billing analysis.

    Tracks per-user resource consumption to:
    - Calculate variable costs per user
    - Identify heavy users
    - Support usage-based billing
    - Detect potential abuse
    """

    __tablename__ = "usage_metrics"

    # Primary key
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # User and organization
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    organization_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Period (first day of month)
    period_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Email metrics
    emails_received: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    emails_sent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    emails_processed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # AI metrics
    ai_requests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ai_responses_generated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ai_tokens_input: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ai_tokens_output: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # API metrics
    api_calls: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    api_calls_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Storage metrics (in bytes)
    storage_used_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    attachments_stored: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Session metrics
    login_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    session_duration_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unique_ips: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unique_devices: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Cost tracking (in cents for precision)
    ai_cost_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    email_cost_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    storage_cost_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_cost_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Flags
    is_over_limit: Mapped[bool] = mapped_column(default=False, nullable=False)
    limit_warning_sent: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="usage_metrics")

    __table_args__ = (
        UniqueConstraint('user_id', 'period_start', name='uq_user_period'),
        Index('ix_usage_metrics_period', 'period_start'),
        Index('ix_usage_metrics_cost', 'total_cost_cents'),
    )

    def __repr__(self) -> str:
        return f"<UsageMetrics(user_id={self.user_id}, period={self.period_start}, cost={self.total_cost_cents})>"

    @property
    def total_cost_dollars(self) -> float:
        """Get total cost in dollars."""
        return self.total_cost_cents / 100.0

    @property
    def ai_cost_dollars(self) -> float:
        """Get AI cost in dollars."""
        return self.ai_cost_cents / 100.0

    @property
    def storage_gb(self) -> float:
        """Get storage in GB."""
        return self.storage_used_bytes / (1024 ** 3)

    def add_ai_usage(self, input_tokens: int, output_tokens: int) -> None:
        """Add AI usage and calculate cost."""
        self.ai_requests += 1
        self.ai_tokens_input += input_tokens
        self.ai_tokens_output += output_tokens

        # Cost calculation (Claude Sonnet pricing: $3/1M input, $15/1M output)
        input_cost = (input_tokens / 1_000_000) * 300  # cents
        output_cost = (output_tokens / 1_000_000) * 1500  # cents
        self.ai_cost_cents += int(input_cost + output_cost)
        self._update_total_cost()

    def add_email_usage(self, sent: int = 0, received: int = 0) -> None:
        """Add email usage and calculate cost."""
        self.emails_sent += sent
        self.emails_received += received
        self.emails_processed += sent + received

        # Cost calculation (~$0.001 per email)
        email_cost = (sent + received) * 0.1  # 0.1 cents per email
        self.email_cost_cents += int(email_cost)
        self._update_total_cost()

    def add_storage(self, bytes_added: int) -> None:
        """Add storage usage and calculate cost."""
        self.storage_used_bytes += bytes_added
        self.attachments_stored += 1

        # Cost calculation (~$0.023 per GB per month, calculate incrementally)
        gb_added = bytes_added / (1024 ** 3)
        storage_cost = gb_added * 2.3  # 2.3 cents per GB
        self.storage_cost_cents += int(storage_cost)
        self._update_total_cost()

    def _update_total_cost(self) -> None:
        """Update total cost from components."""
        self.total_cost_cents = (
            self.ai_cost_cents +
            self.email_cost_cents +
            self.storage_cost_cents
        )
        self.updated_at = datetime.utcnow()


class UsageAlert(Base):
    """
    Usage alerts for notifying users about limits and anomalies.
    """

    __tablename__ = "usage_alerts"

    # Primary key
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # User
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Alert details
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)  # limit_warning, limit_reached, anomaly
    metric_name: Mapped[str] = mapped_column(String(50), nullable=False)  # ai_requests, emails, etc.
    current_value: Mapped[int] = mapped_column(Integer, nullable=False)
    limit_value: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    threshold_percentage: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # e.g., 80, 90, 100

    # Status
    is_acknowledged: Mapped[bool] = mapped_column(default=False, nullable=False)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Notification
    notification_sent: Mapped[bool] = mapped_column(default=False, nullable=False)
    notification_sent_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<UsageAlert(user_id={self.user_id}, type={self.alert_type}, metric={self.metric_name})>"
