"""AI Learning API endpoints - Writing style and edit pattern analysis.

This module exposes the AI learning capabilities to users, allowing them to:
- Analyze their writing style
- View their learned profile
- See edit patterns and insights
- Manually trigger profile updates
"""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.core.database import get_db
from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging import logger
from app.core.config import settings
from app.api.deps import get_current_user
from app.models.user import User
from app.services.writing_style import WritingStyleService, WritingStyleProfile, StyleAnalysisResult
from app.services.edit_learning import EditLearningService, EditAnalysis


router = APIRouter()


# =============================================================================
# Pydantic Schemas
# =============================================================================

class AnalyzeStyleRequest(BaseModel):
    """Request to analyze writing style."""
    lookback_days: int = Field(default=90, ge=7, le=365, description="Days to look back for sent emails")
    max_emails: int = Field(default=50, ge=10, le=100, description="Maximum emails to analyze")


class StyleProfileResponse(BaseModel):
    """Response with user's writing style profile."""
    profile: Optional[WritingStyleProfile] = None
    has_profile: bool = Field(description="Whether user has a profile")
    last_updated: Optional[datetime] = None
    sample_size: int = Field(default=0, description="Number of emails analyzed")
    confidence: float = Field(default=0.0, description="Confidence in profile (0-1)")


class AnalyzeStyleResponse(BaseModel):
    """Response from style analysis."""
    success: bool
    message: str
    profile: Optional[WritingStyleProfile] = None
    insights: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class EditInsightsResponse(BaseModel):
    """Response with edit learning insights."""
    has_insights: bool = Field(description="Whether sufficient edit data exists")
    analysis: Optional[EditAnalysis] = None
    message: str


class LearningStatsResponse(BaseModel):
    """Overall learning statistics."""
    has_writing_profile: bool
    writing_profile_confidence: float
    writing_profile_sample_size: int
    writing_profile_last_updated: Optional[datetime]

    total_edits_analyzed: int
    avg_edit_percentage: float
    heavy_edit_rate: float

    has_sufficient_data: bool = Field(description="Whether we have enough data to learn effectively")
    recommendations: list[str] = Field(default_factory=list)


# =============================================================================
# API Endpoints
# =============================================================================

@router.get("/profile", response_model=StyleProfileResponse)
async def get_writing_style_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the user's learned writing style profile.

    Returns the cached profile if available, or indicates that analysis is needed.
    """
    if not current_user.writing_style_profile:
        return StyleProfileResponse(
            has_profile=False,
            last_updated=None,
            sample_size=0,
            confidence=0.0
        )

    try:
        import json
        profile_data = json.loads(current_user.writing_style_profile)
        profile = WritingStyleProfile(**profile_data)

        return StyleProfileResponse(
            profile=profile,
            has_profile=True,
            last_updated=profile.last_updated,
            sample_size=profile.sample_size,
            confidence=profile.confidence
        )
    except Exception as e:
        logger.error(f"Failed to parse writing style profile for user {current_user.id}: {e}")
        return StyleProfileResponse(
            has_profile=False,
            last_updated=None,
            sample_size=0,
            confidence=0.0
        )


@router.post("/analyze", response_model=AnalyzeStyleResponse)
async def analyze_writing_style(
    request: AnalyzeStyleRequest = AnalyzeStyleRequest(),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Analyze the user's writing style from their sent emails.

    This endpoint:
    1. Analyzes recent sent emails (last 30-90 days)
    2. Extracts writing style characteristics
    3. Caches the profile for future use
    4. Returns insights and recommendations

    Note: This is a compute-intensive operation and should not be called frequently.
    """
    try:
        # Initialize writing style service
        if not settings.ANTHROPIC_API_KEY:
            raise ValidationError("AI services not configured")

        writing_service = WritingStyleService(api_key=settings.ANTHROPIC_API_KEY)

        # Analyze writing style
        logger.info(f"Analyzing writing style for user {current_user.id}")
        result: StyleAnalysisResult = await writing_service.analyze_user_writing_style(
            db=db,
            user_id=current_user.id,
            lookback_days=request.lookback_days,
            max_emails=request.max_emails
        )

        # Cache the profile
        current_user.writing_style_profile = result.profile.model_dump_json()
        await db.commit()

        logger.info(
            f"Writing style analyzed for user {current_user.id}: "
            f"{result.profile.sample_size} emails, confidence {result.profile.confidence}"
        )

        return AnalyzeStyleResponse(
            success=True,
            message=f"Successfully analyzed {result.profile.sample_size} emails",
            profile=result.profile,
            insights=result.insights,
            recommendations=result.recommendations
        )

    except Exception as e:
        logger.error(f"Failed to analyze writing style for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze writing style: {str(e)}"
        )


@router.delete("/profile")
async def delete_writing_style_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete the user's cached writing style profile.

    This will cause the AI to revert to default writing style until a new analysis is performed.
    """
    current_user.writing_style_profile = None
    await db.commit()

    logger.info(f"Deleted writing style profile for user {current_user.id}")

    return {
        "success": True,
        "message": "Writing style profile deleted"
    }


@router.get("/edit-insights", response_model=EditInsightsResponse)
async def get_edit_insights(
    lookback_days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get insights from the user's edit patterns.

    Analyzes how the user edits AI-generated responses to identify patterns
    and improve future responses.

    Requires at least 5 edits in the lookback period.
    """
    try:
        # Initialize edit learning service
        if not settings.ANTHROPIC_API_KEY:
            raise ValidationError("AI services not configured")

        edit_service = EditLearningService(api_key=settings.ANTHROPIC_API_KEY)

        # Analyze edit patterns
        logger.info(f"Analyzing edit patterns for user {current_user.id}")
        analysis = await edit_service.analyze_user_edit_patterns(
            db=db,
            user_id=current_user.id,
            lookback_days=lookback_days,
            min_edits=5
        )

        if not analysis:
            return EditInsightsResponse(
                has_insights=False,
                message=f"Insufficient edit data (need at least 5 edits in last {lookback_days} days)"
            )

        # Update writing style profile based on edit patterns if we have one
        if current_user.writing_style_profile:
            await edit_service.update_writing_style_from_edits(
                db=db,
                user=current_user,
                edit_analysis=analysis
            )
            logger.info(f"Updated writing style profile for user {current_user.id} based on edit patterns")

        return EditInsightsResponse(
            has_insights=True,
            analysis=analysis,
            message=f"Successfully analyzed {analysis.sample_size} edits"
        )

    except Exception as e:
        logger.error(f"Failed to analyze edit patterns for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze edit patterns: {str(e)}"
        )


@router.get("/stats", response_model=LearningStatsResponse)
async def get_learning_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get overall AI learning statistics for the user.

    Provides a summary of:
    - Writing style profile status
    - Edit pattern analysis status
    - Data sufficiency for learning
    - Recommendations for improving AI performance
    """
    recommendations = []

    # Writing profile stats
    has_writing_profile = bool(current_user.writing_style_profile)
    writing_confidence = 0.0
    writing_sample_size = 0
    writing_last_updated = None

    if has_writing_profile:
        try:
            import json
            profile_data = json.loads(current_user.writing_style_profile)
            writing_confidence = profile_data.get("confidence", 0.0)
            writing_sample_size = profile_data.get("sample_size", 0)
            writing_last_updated = profile_data.get("last_updated")
            if writing_last_updated:
                writing_last_updated = datetime.fromisoformat(writing_last_updated)
        except:
            pass
    else:
        recommendations.append("Analyze your writing style to personalize AI responses")

    # Edit stats - would need to query database
    from sqlalchemy import select, func, and_
    from app.models.agent_action import AgentAction, ActionStatus
    from app.models.conversation import Conversation
    from app.models.objective import Objective

    # Count total edits
    total_edits_query = (
        select(func.count(AgentAction.id))
        .join(AgentAction.conversation)
        .join(Conversation.objective)
        .where(
            and_(
                Objective.user_id == current_user.id,
                AgentAction.status == ActionStatus.EDITED,
                AgentAction.user_edit.isnot(None)
            )
        )
    )

    result = await db.execute(total_edits_query)
    total_edits = result.scalar() or 0

    # Placeholder for edit metrics (would need to calculate from database)
    avg_edit_percentage = 0.0
    heavy_edit_rate = 0.0

    if total_edits < 5:
        recommendations.append(f"Edit {5 - total_edits} more AI responses to enable edit pattern learning")

    if writing_sample_size < 20:
        recommendations.append("Send more emails to improve writing style accuracy")

    # Check if profile is stale (>30 days old)
    if writing_last_updated:
        days_old = (datetime.utcnow() - writing_last_updated).days
        if days_old > 30:
            recommendations.append(f"Writing style profile is {days_old} days old - consider refreshing")

    has_sufficient_data = has_writing_profile and total_edits >= 5 and writing_sample_size >= 10

    if not recommendations:
        recommendations.append("AI learning is optimized! Keep using GetAnswers to maintain accuracy.")

    return LearningStatsResponse(
        has_writing_profile=has_writing_profile,
        writing_profile_confidence=writing_confidence,
        writing_profile_sample_size=writing_sample_size,
        writing_profile_last_updated=writing_last_updated,
        total_edits_analyzed=total_edits,
        avg_edit_percentage=avg_edit_percentage,
        heavy_edit_rate=heavy_edit_rate,
        has_sufficient_data=has_sufficient_data,
        recommendations=recommendations
    )
