"""Lead magnet model for capturing and tracking lead magnet conversions."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import Base


class LeadMagnetLead(Base):
    """Lead magnet capture tracking model."""

    __tablename__ = "lead_magnet_leads"

    # Primary key
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Contact info
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Source tracking - which lead magnet
    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # e.g., "email-prompts", "triage-framework", "policy-template", "time-calculator", "inbox-checklist"

    # Engagement tracking
    view_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    download_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    # Conversion tracking
    converted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True, index=True)
    converted_to: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # "trial" or "paid"

    converted_user_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # Metadata
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    utm_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    utm_medium: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    utm_campaign: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<LeadMagnetLead(id={self.id}, email={self.email}, source={self.source})>"
