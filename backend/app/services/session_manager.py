"""Session management service for tracking and limiting user sessions."""
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import UUID
import hashlib

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from user_agents import parse as parse_user_agent

from app.core.config import settings
from app.core.logging import logger
from app.models import User, UserSession, DeviceHistory, TrustLevel, AuditLogEntry, AuditEventType, AuditSeverity


# Configuration
MAX_CONCURRENT_SESSIONS = 2  # Maximum active sessions per user
SESSION_EXPIRY_HOURS = 24 * 7  # 7 days
NEW_DEVICE_THRESHOLD_DAYS = 30  # Device considered "new" if not seen in 30 days


class SessionManager:
    """
    Manages user sessions with concurrent session limiting and device tracking.

    Features:
    - Limits concurrent sessions per user
    - Tracks device fingerprints and IP addresses
    - Detects new devices and suspicious activity
    - Supports server-side session invalidation
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def generate_jti() -> str:
        """Generate a unique JWT ID (jti)."""
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_device_fingerprint(user_agent: str, ip_address: str) -> str:
        """Generate a device fingerprint from user agent and IP."""
        # Use hash of user agent for fingerprint (IP can change)
        data = f"{user_agent}".encode('utf-8')
        return hashlib.sha256(data).hexdigest()[:32]

    @staticmethod
    def parse_user_agent_info(user_agent: str) -> dict:
        """Parse user agent string into device info."""
        try:
            ua = parse_user_agent(user_agent)
            return {
                "device_type": "mobile" if ua.is_mobile else ("tablet" if ua.is_tablet else "desktop"),
                "browser": f"{ua.browser.family} {ua.browser.version_string}",
                "os": f"{ua.os.family} {ua.os.version_string}",
            }
        except Exception:
            return {
                "device_type": "unknown",
                "browser": "unknown",
                "os": "unknown",
            }

    async def create_session(
        self,
        user: User,
        ip_address: str,
        user_agent: str = None,
        city: str = None,
        country: str = None,
        country_code: str = None,
    ) -> Tuple[UserSession, str, bool]:
        """
        Create a new session for a user.

        Returns:
            Tuple of (session, jti, is_new_device)

        Side effects:
            - May revoke oldest session if max concurrent sessions exceeded
            - Updates device history
            - Creates audit log entry
        """
        jti = self.generate_jti()
        device_fingerprint = self.generate_device_fingerprint(user_agent or "", ip_address)
        ua_info = self.parse_user_agent_info(user_agent or "")

        # Check if this is a new device
        is_new_device, device = await self._check_device(
            user.id, device_fingerprint, ip_address, user_agent, city, country, country_code
        )

        # Check concurrent session limit
        await self._enforce_session_limit(user.id)

        # Check if this is a new location
        is_new_location = await self._is_new_location(user.id, country_code)

        # Create new session
        session = UserSession(
            user_id=user.id,
            token_jti=jti,
            device_fingerprint=device_fingerprint,
            user_agent=user_agent,
            device_type=ua_info["device_type"],
            browser=ua_info["browser"],
            os=ua_info["os"],
            ip_address=ip_address,
            city=city,
            country=country,
            country_code=country_code,
            is_active=True,
            is_new_device=is_new_device,
            is_new_location=is_new_location,
            expires_at=datetime.utcnow() + timedelta(hours=SESSION_EXPIRY_HOURS),
            trust_score=device.trust_level == TrustLevel.TRUSTED if device else 0.5,
        )

        self.db.add(session)

        # Create audit log entry
        audit_entry = AuditLogEntry.create(
            event_type=AuditEventType.SESSION_CREATED,
            severity=AuditSeverity.INFO,
            user_id=user.id,
            user_email=user.email,
            session_id=session.id,
            token_jti=jti,
            ip_address=ip_address,
            user_agent=user_agent,
            city=city,
            country=country,
            success=True,
            details={
                "is_new_device": is_new_device,
                "is_new_location": is_new_location,
                "device_type": ua_info["device_type"],
            }
        )
        self.db.add(audit_entry)

        await self.db.flush()

        logger.info(f"Created session for user {user.email} (new_device={is_new_device})")

        return session, jti, is_new_device

    async def validate_session(self, jti: str) -> Optional[UserSession]:
        """
        Validate a session by its JWT ID.

        Returns:
            UserSession if valid and active, None otherwise
        """
        result = await self.db.execute(
            select(UserSession).where(
                and_(
                    UserSession.token_jti == jti,
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.utcnow()
                )
            )
        )
        session = result.scalar_one_or_none()

        if session:
            # Update last activity
            session.update_activity()
            await self.db.flush()

        return session

    async def revoke_session(
        self,
        jti: str,
        reason: str = "manual_revoke",
        user_id: UUID = None
    ) -> bool:
        """
        Revoke a session by its JWT ID.

        Returns:
            True if session was found and revoked, False otherwise
        """
        query = select(UserSession).where(UserSession.token_jti == jti)
        if user_id:
            query = query.where(UserSession.user_id == user_id)

        result = await self.db.execute(query)
        session = result.scalar_one_or_none()

        if not session:
            return False

        session.revoke(reason)

        # Create audit log entry
        audit_entry = AuditLogEntry.create(
            event_type=AuditEventType.SESSION_REVOKED,
            severity=AuditSeverity.INFO,
            user_id=session.user_id,
            session_id=session.id,
            token_jti=jti,
            ip_address=session.ip_address,
            success=True,
            details={"reason": reason}
        )
        self.db.add(audit_entry)

        await self.db.flush()

        logger.info(f"Revoked session {jti} for user {session.user_id}: {reason}")
        return True

    async def revoke_all_sessions(
        self,
        user_id: UUID,
        except_jti: str = None,
        reason: str = "logout_all"
    ) -> int:
        """
        Revoke all active sessions for a user.

        Args:
            user_id: User whose sessions to revoke
            except_jti: Optional JTI to exclude (keep current session)
            reason: Reason for revocation

        Returns:
            Number of sessions revoked
        """
        query = select(UserSession).where(
            and_(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            )
        )

        if except_jti:
            query = query.where(UserSession.token_jti != except_jti)

        result = await self.db.execute(query)
        sessions = result.scalars().all()

        for session in sessions:
            session.revoke(reason)

        if sessions:
            # Create audit log entry
            audit_entry = AuditLogEntry.create(
                event_type=AuditEventType.SESSION_REVOKED,
                severity=AuditSeverity.WARNING,
                user_id=user_id,
                success=True,
                details={
                    "reason": reason,
                    "sessions_revoked": len(sessions),
                    "except_jti": except_jti,
                }
            )
            self.db.add(audit_entry)

        await self.db.flush()

        logger.info(f"Revoked {len(sessions)} sessions for user {user_id}: {reason}")
        return len(sessions)

    async def get_active_sessions(self, user_id: UUID) -> list[UserSession]:
        """Get all active sessions for a user."""
        result = await self.db.execute(
            select(UserSession).where(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.utcnow()
                )
            ).order_by(UserSession.last_activity.desc())
        )
        return list(result.scalars().all())

    async def get_session_count(self, user_id: UUID) -> int:
        """Get count of active sessions for a user."""
        result = await self.db.execute(
            select(func.count(UserSession.id)).where(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.utcnow()
                )
            )
        )
        return result.scalar() or 0

    async def _enforce_session_limit(self, user_id: UUID) -> None:
        """Revoke oldest sessions if user exceeds max concurrent sessions."""
        # Get all active sessions ordered by last activity
        result = await self.db.execute(
            select(UserSession).where(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.utcnow()
                )
            ).order_by(UserSession.last_activity.asc())
        )
        sessions = list(result.scalars().all())

        # If at or over limit, revoke oldest sessions
        sessions_to_revoke = len(sessions) - MAX_CONCURRENT_SESSIONS + 1  # +1 for new session
        if sessions_to_revoke > 0:
            for session in sessions[:sessions_to_revoke]:
                session.revoke("concurrent_session_limit")

                # Create audit log entry
                audit_entry = AuditLogEntry.create(
                    event_type=AuditEventType.CONCURRENT_SESSION_LIMIT,
                    severity=AuditSeverity.WARNING,
                    user_id=user_id,
                    session_id=session.id,
                    token_jti=session.token_jti,
                    ip_address=session.ip_address,
                    success=True,
                    message=f"Session revoked due to concurrent session limit ({MAX_CONCURRENT_SESSIONS})"
                )
                self.db.add(audit_entry)

            logger.info(f"Revoked {sessions_to_revoke} sessions for user {user_id} due to limit")

    async def _check_device(
        self,
        user_id: UUID,
        device_fingerprint: str,
        ip_address: str,
        user_agent: str,
        city: str,
        country: str,
        country_code: str,
    ) -> Tuple[bool, Optional[DeviceHistory]]:
        """
        Check device history and update or create entry.

        Returns:
            Tuple of (is_new_device, device_history)
        """
        # Look for existing device
        result = await self.db.execute(
            select(DeviceHistory).where(
                and_(
                    DeviceHistory.user_id == user_id,
                    DeviceHistory.device_fingerprint == device_fingerprint
                )
            )
        )
        device = result.scalar_one_or_none()

        if device:
            # Update existing device
            device.record_login(ip_address, city, country)
            is_new = False

            # Check if device hasn't been seen in a while
            if device.last_seen:
                days_since_seen = (datetime.utcnow() - device.last_seen).days
                if days_since_seen > NEW_DEVICE_THRESHOLD_DAYS:
                    is_new = True  # Treat as new if not seen recently

        else:
            # Create new device entry
            ua_info = self.parse_user_agent_info(user_agent or "")
            device = DeviceHistory(
                user_id=user_id,
                device_fingerprint=device_fingerprint,
                user_agent=user_agent,
                device_type=ua_info["device_type"],
                browser=ua_info["browser"],
                os=ua_info["os"],
                last_ip_address=ip_address,
                last_city=city,
                last_country=country,
                last_country_code=country_code,
                trust_level=TrustLevel.UNKNOWN,
            )
            self.db.add(device)
            is_new = True

            # Create audit log for new device
            audit_entry = AuditLogEntry.create(
                event_type=AuditEventType.NEW_DEVICE_DETECTED,
                severity=AuditSeverity.WARNING,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                city=city,
                country=country,
                success=True,
                details={
                    "device_fingerprint": device_fingerprint,
                    "device_type": ua_info["device_type"],
                }
            )
            self.db.add(audit_entry)

        return is_new, device

    async def _is_new_location(self, user_id: UUID, country_code: str) -> bool:
        """Check if this is a new location for the user."""
        if not country_code:
            return False

        # Check if user has logged in from this country before
        result = await self.db.execute(
            select(UserSession).where(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.country_code == country_code
                )
            ).limit(1)
        )

        return result.scalar_one_or_none() is None

    async def check_impossible_travel(
        self,
        user_id: UUID,
        current_city: str,
        current_country: str,
        current_lat: float = None,
        current_lon: float = None,
    ) -> bool:
        """
        Check for impossible travel (login from geographically distant location in short time).

        Returns:
            True if impossible travel detected, False otherwise
        """
        # Get most recent session
        result = await self.db.execute(
            select(UserSession).where(
                UserSession.user_id == user_id
            ).order_by(UserSession.created_at.desc()).limit(1)
        )
        last_session = result.scalar_one_or_none()

        if not last_session:
            return False

        # If different country within 1 hour, flag as suspicious
        time_since_last = datetime.utcnow() - last_session.created_at
        if time_since_last.total_seconds() < 3600:  # 1 hour
            if last_session.country_code and current_country:
                if last_session.country_code != current_country[:2].upper():
                    # Different country within 1 hour - impossible travel
                    audit_entry = AuditLogEntry.create(
                        event_type=AuditEventType.IMPOSSIBLE_TRAVEL,
                        severity=AuditSeverity.WARNING,
                        user_id=user_id,
                        success=True,
                        details={
                            "previous_country": last_session.country_code,
                            "current_country": current_country,
                            "time_between_logins_seconds": time_since_last.total_seconds(),
                        }
                    )
                    self.db.add(audit_entry)

                    logger.warning(
                        f"Impossible travel detected for user {user_id}: "
                        f"{last_session.country_code} -> {current_country} in {time_since_last.total_seconds()}s"
                    )
                    return True

        return False


# Singleton-like access for dependency injection
async def get_session_manager(db: AsyncSession) -> SessionManager:
    """Get a session manager instance."""
    return SessionManager(db)
