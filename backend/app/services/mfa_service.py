"""MFA service for multi-factor authentication (TOTP)."""
import secrets
import hashlib
from datetime import datetime
from typing import Optional, Tuple, List
from uuid import UUID
import base64
import io

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import encrypt_string, decrypt_string
from app.core.logging import logger
from app.models import User, UserMFA, AuditLogEntry, AuditEventType, AuditSeverity

# TOTP Configuration
TOTP_DIGITS = 6
TOTP_INTERVAL = 30  # seconds
TOTP_VALID_WINDOW = 1  # Allow ±1 interval for clock skew
BACKUP_CODES_COUNT = 8


class MFAService:
    """
    Multi-Factor Authentication service supporting TOTP.

    Features:
    - TOTP (Time-based One-Time Password) compatible with Google Authenticator
    - Encrypted secret storage
    - Backup codes for account recovery
    - Rate limiting for failed attempts
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def generate_totp_secret() -> str:
        """Generate a cryptographically secure TOTP secret."""
        # 20 bytes = 160 bits, standard for TOTP
        return base64.b32encode(secrets.token_bytes(20)).decode('utf-8')

    @staticmethod
    def generate_totp_code(secret: str, time_step: int = None) -> str:
        """
        Generate a TOTP code from a secret.

        Args:
            secret: Base32-encoded secret
            time_step: Optional time step override (for testing)

        Returns:
            6-digit TOTP code
        """
        import hmac
        import struct
        import time

        # Decode secret
        try:
            key = base64.b32decode(secret.upper())
        except Exception:
            return ""

        # Get current time step
        if time_step is None:
            time_step = int(time.time()) // TOTP_INTERVAL

        # Pack time as big-endian 8-byte integer
        time_bytes = struct.pack(">Q", time_step)

        # HMAC-SHA1
        hmac_hash = hmac.new(key, time_bytes, hashlib.sha1).digest()

        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        code_int = struct.unpack(">I", hmac_hash[offset:offset + 4])[0]
        code_int &= 0x7FFFFFFF  # Remove sign bit
        code = code_int % (10 ** TOTP_DIGITS)

        return str(code).zfill(TOTP_DIGITS)

    @staticmethod
    def verify_totp_code(secret: str, code: str) -> bool:
        """
        Verify a TOTP code against a secret.

        Allows for clock skew by checking adjacent time windows.

        Args:
            secret: Base32-encoded secret
            code: User-provided 6-digit code

        Returns:
            True if code is valid, False otherwise
        """
        import time

        if not code or len(code) != TOTP_DIGITS:
            return False

        current_time_step = int(time.time()) // TOTP_INTERVAL

        # Check current and adjacent time windows
        for offset in range(-TOTP_VALID_WINDOW, TOTP_VALID_WINDOW + 1):
            expected = MFAService.generate_totp_code(secret, current_time_step + offset)
            if secrets.compare_digest(code, expected):
                return True

        return False

    @staticmethod
    def generate_backup_codes(count: int = BACKUP_CODES_COUNT) -> List[dict]:
        """
        Generate a list of backup codes.

        Returns:
            List of dicts with 'code' (plaintext) and 'hash' (for storage)
        """
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = secrets.token_hex(4).upper()  # 8 hex chars
            code_hash = hashlib.sha256(code.encode()).hexdigest()
            codes.append({
                "code": code,
                "hash": code_hash,
                "used": False,
                "used_at": None,
            })
        return codes

    def generate_qr_code_uri(self, email: str, secret: str) -> str:
        """
        Generate a TOTP URI for QR code generation.

        Format: otpauth://totp/GetAnswers:email?secret=XXX&issuer=GetAnswers

        Args:
            email: User's email address
            secret: Base32-encoded TOTP secret

        Returns:
            TOTP URI string
        """
        from urllib.parse import quote

        issuer = "GetAnswers"
        label = f"{issuer}:{email}"

        return (
            f"otpauth://totp/{quote(label)}"
            f"?secret={secret}"
            f"&issuer={quote(issuer)}"
            f"&digits={TOTP_DIGITS}"
            f"&period={TOTP_INTERVAL}"
        )

    async def setup_mfa(self, user: User) -> Tuple[str, str, List[str]]:
        """
        Initialize MFA setup for a user.

        Returns:
            Tuple of (secret, qr_uri, backup_codes_plaintext)

        Note: Secret is returned for QR display but should not be stored
        in logs or sent to client except for initial setup.
        """
        # Generate new secret
        secret = self.generate_totp_secret()

        # Generate backup codes
        backup_codes = self.generate_backup_codes()
        backup_codes_plaintext = [c["code"] for c in backup_codes]

        # Check if user already has MFA record
        result = await self.db.execute(
            select(UserMFA).where(UserMFA.user_id == user.id)
        )
        mfa = result.scalar_one_or_none()

        if mfa:
            # Update existing (but not enabled yet)
            mfa.totp_secret = encrypt_string(secret)
            mfa.backup_codes = {
                "codes": [{"hash": c["hash"], "used": False, "used_at": None} for c in backup_codes]
            }
            mfa.backup_codes_generated_at = datetime.utcnow()
            mfa.backup_codes_remaining = len(backup_codes)
        else:
            # Create new MFA record
            mfa = UserMFA(
                user_id=user.id,
                totp_secret=encrypt_string(secret),
                totp_enabled=False,
                backup_codes={
                    "codes": [{"hash": c["hash"], "used": False, "used_at": None} for c in backup_codes]
                },
                backup_codes_generated_at=datetime.utcnow(),
                backup_codes_remaining=len(backup_codes),
            )
            self.db.add(mfa)

        await self.db.flush()

        # Generate QR code URI
        qr_uri = self.generate_qr_code_uri(user.email, secret)

        logger.info(f"MFA setup initiated for user {user.email}")

        return secret, qr_uri, backup_codes_plaintext

    async def confirm_mfa_setup(self, user: User, code: str) -> bool:
        """
        Confirm MFA setup by verifying the first code.

        Args:
            user: User to enable MFA for
            code: TOTP code to verify

        Returns:
            True if setup confirmed, False if verification failed
        """
        result = await self.db.execute(
            select(UserMFA).where(UserMFA.user_id == user.id)
        )
        mfa = result.scalar_one_or_none()

        if not mfa or not mfa.totp_secret:
            return False

        # Decrypt and verify
        secret = decrypt_string(mfa.totp_secret)
        if not self.verify_totp_code(secret, code):
            mfa.record_failed_attempt()
            await self.db.flush()
            return False

        # Enable MFA
        mfa.totp_enabled = True
        mfa.totp_verified_at = datetime.utcnow()
        mfa.record_successful_verification()

        # Create audit log
        audit_entry = AuditLogEntry.create(
            event_type=AuditEventType.MFA_ENABLED,
            severity=AuditSeverity.INFO,
            user_id=user.id,
            user_email=user.email,
            success=True,
            message="TOTP MFA enabled successfully"
        )
        self.db.add(audit_entry)

        await self.db.flush()

        logger.info(f"MFA enabled for user {user.email}")
        return True

    async def verify_mfa(
        self,
        user: User,
        code: str,
        ip_address: str = None,
        user_agent: str = None,
    ) -> Tuple[bool, str]:
        """
        Verify an MFA code during login.

        Args:
            user: User to verify
            code: TOTP or backup code
            ip_address: Client IP for audit logging
            user_agent: Client user agent for audit logging

        Returns:
            Tuple of (success, error_message)
        """
        result = await self.db.execute(
            select(UserMFA).where(UserMFA.user_id == user.id)
        )
        mfa = result.scalar_one_or_none()

        if not mfa or not mfa.is_enabled:
            return True, ""  # MFA not enabled, allow through

        # Check if locked
        if mfa.is_locked:
            return False, "MFA temporarily locked due to too many failed attempts"

        # Try TOTP first
        if mfa.totp_enabled and mfa.totp_secret:
            secret = decrypt_string(mfa.totp_secret)
            if self.verify_totp_code(secret, code):
                mfa.record_successful_verification()

                # Audit log
                audit_entry = AuditLogEntry.create(
                    event_type=AuditEventType.MFA_VERIFY_SUCCESS,
                    severity=AuditSeverity.INFO,
                    user_id=user.id,
                    user_email=user.email,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=True,
                    details={"method": "totp"}
                )
                self.db.add(audit_entry)

                await self.db.flush()
                return True, ""

        # Try backup code
        if await self._verify_backup_code(mfa, code):
            # Audit log
            audit_entry = AuditLogEntry.create(
                event_type=AuditEventType.MFA_BACKUP_CODE_USED,
                severity=AuditSeverity.WARNING,
                user_id=user.id,
                user_email=user.email,
                ip_address=ip_address,
                user_agent=user_agent,
                success=True,
                details={"remaining_codes": mfa.backup_codes_remaining}
            )
            self.db.add(audit_entry)

            await self.db.flush()
            return True, ""

        # Failed verification
        mfa.record_failed_attempt()

        # Audit log
        audit_entry = AuditLogEntry.create(
            event_type=AuditEventType.MFA_VERIFY_FAILURE,
            severity=AuditSeverity.WARNING,
            user_id=user.id,
            user_email=user.email,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            details={"failed_attempts": mfa.failed_attempts}
        )
        self.db.add(audit_entry)

        # Check if now locked
        if mfa.is_locked:
            lock_audit = AuditLogEntry.create(
                event_type=AuditEventType.MFA_LOCKED,
                severity=AuditSeverity.ERROR,
                user_id=user.id,
                user_email=user.email,
                ip_address=ip_address,
                success=False,
                message="MFA locked due to excessive failed attempts"
            )
            self.db.add(lock_audit)

        await self.db.flush()

        return False, "Invalid verification code"

    async def _verify_backup_code(self, mfa: UserMFA, code: str) -> bool:
        """Verify and consume a backup code."""
        if not mfa.backup_codes or "codes" not in mfa.backup_codes:
            return False

        code_hash = hashlib.sha256(code.upper().encode()).hexdigest()

        for i, stored_code in enumerate(mfa.backup_codes["codes"]):
            if not stored_code.get("used") and stored_code.get("hash") == code_hash:
                # Mark as used
                mfa.use_backup_code(i)
                mfa.record_successful_verification()
                return True

        return False

    async def disable_mfa(
        self,
        user: User,
        verification_code: str = None,
    ) -> bool:
        """
        Disable MFA for a user.

        Args:
            user: User to disable MFA for
            verification_code: Optional code to verify before disabling

        Returns:
            True if disabled, False if verification failed
        """
        result = await self.db.execute(
            select(UserMFA).where(UserMFA.user_id == user.id)
        )
        mfa = result.scalar_one_or_none()

        if not mfa or not mfa.is_enabled:
            return True  # Already disabled

        # Verify code if provided
        if verification_code:
            secret = decrypt_string(mfa.totp_secret)
            if not self.verify_totp_code(secret, verification_code):
                return False

        # Disable MFA
        mfa.totp_enabled = False
        mfa.email_mfa_enabled = False
        mfa.totp_secret = None
        mfa.backup_codes = None

        # Audit log
        audit_entry = AuditLogEntry.create(
            event_type=AuditEventType.MFA_DISABLED,
            severity=AuditSeverity.WARNING,
            user_id=user.id,
            user_email=user.email,
            success=True,
            message="MFA disabled for user account"
        )
        self.db.add(audit_entry)

        await self.db.flush()

        logger.info(f"MFA disabled for user {user.email}")
        return True

    async def regenerate_backup_codes(self, user: User) -> List[str]:
        """
        Generate new backup codes for a user.

        Returns:
            List of new backup codes (plaintext, for display only)
        """
        result = await self.db.execute(
            select(UserMFA).where(UserMFA.user_id == user.id)
        )
        mfa = result.scalar_one_or_none()

        if not mfa:
            raise ValueError("MFA not configured for user")

        backup_codes = self.generate_backup_codes()
        mfa.backup_codes = {
            "codes": [{"hash": c["hash"], "used": False, "used_at": None} for c in backup_codes]
        }
        mfa.backup_codes_generated_at = datetime.utcnow()
        mfa.backup_codes_remaining = len(backup_codes)

        await self.db.flush()

        logger.info(f"Backup codes regenerated for user {user.email}")

        return [c["code"] for c in backup_codes]

    async def get_mfa_status(self, user: User) -> dict:
        """Get MFA status for a user."""
        result = await self.db.execute(
            select(UserMFA).where(UserMFA.user_id == user.id)
        )
        mfa = result.scalar_one_or_none()

        if not mfa:
            return {
                "enabled": False,
                "totp_enabled": False,
                "email_mfa_enabled": False,
                "backup_codes_remaining": 0,
            }

        return {
            "enabled": mfa.is_enabled,
            "totp_enabled": mfa.totp_enabled,
            "email_mfa_enabled": mfa.email_mfa_enabled,
            "backup_codes_remaining": mfa.backup_codes_remaining,
            "last_used": mfa.last_used.isoformat() if mfa.last_used else None,
        }

    async def is_mfa_required(self, user: User) -> bool:
        """Check if MFA verification is required for a user."""
        result = await self.db.execute(
            select(UserMFA).where(UserMFA.user_id == user.id)
        )
        mfa = result.scalar_one_or_none()

        return mfa is not None and mfa.is_enabled


async def get_mfa_service(db: AsyncSession) -> MFAService:
    """Get an MFA service instance."""
    return MFAService(db)
