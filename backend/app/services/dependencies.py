"""Dependency injection utilities for services.

This module provides FastAPI dependency functions for service initialization.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status

from .agent import AgentService
from .gmail import GmailService, GmailAuthError
from ..core.config import settings


# Global service instances (optional - can be initialized per request)
_agent_service: Optional[AgentService] = None
_gmail_service: Optional[GmailService] = None


def get_agent_service() -> AgentService:
    """Get or create an AgentService instance.

    This is a FastAPI dependency that can be used in route handlers.

    Usage:
        @router.post("/analyze")
        async def analyze_email(
            agent: AgentService = Depends(get_agent_service)
        ):
            analysis = await agent.analyze_email(...)
            return analysis

    Raises:
        HTTPException: If ANTHROPIC_API_KEY is not configured

    Returns:
        Initialized AgentService instance
    """
    global _agent_service

    if not settings.ANTHROPIC_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not configured. Please set ANTHROPIC_API_KEY."
        )

    # Reuse existing instance or create new one
    if _agent_service is None:
        _agent_service = AgentService(api_key=settings.ANTHROPIC_API_KEY)

    return _agent_service


def reset_agent_service():
    """Reset the global agent service instance.

    Useful for testing or when configuration changes.
    """
    global _agent_service
    _agent_service = None


# Alternative: Create new instance per request (more resource intensive)
def get_agent_service_fresh() -> AgentService:
    """Get a fresh AgentService instance for each request.

    Use this instead of get_agent_service() if you want a new instance
    per request rather than a singleton.

    Raises:
        HTTPException: If ANTHROPIC_API_KEY is not configured

    Returns:
        New AgentService instance
    """
    if not settings.ANTHROPIC_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not configured. Please set ANTHROPIC_API_KEY."
        )

    return AgentService(api_key=settings.ANTHROPIC_API_KEY)


def get_gmail_service() -> GmailService:
    """Get or create a GmailService instance.

    This is a FastAPI dependency that can be used in route handlers.

    Usage:
        @router.get("/gmail/messages")
        async def get_messages(
            gmail: GmailService = Depends(get_gmail_service)
        ):
            messages = await gmail.get_messages(...)
            return messages

    Raises:
        HTTPException: If Gmail OAuth credentials are not configured

    Returns:
        Initialized GmailService instance
    """
    global _gmail_service

    try:
        # Reuse existing instance or create new one
        if _gmail_service is None:
            _gmail_service = GmailService(
                client_id=settings.GMAIL_CLIENT_ID,
                client_secret=settings.GMAIL_CLIENT_SECRET
            )
        return _gmail_service
    except GmailAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Gmail service not configured: {str(e)}"
        )
