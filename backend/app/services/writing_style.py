"""Writing Style Learning Service - Learns and applies user's writing patterns.

This service analyzes a user's historical sent emails to learn their unique writing style,
then uses this profile to generate more personalized AI responses.

Key Features:
- Analyzes tone, formality, length preferences
- Learns common phrases and sign-offs
- Detects communication patterns
- Stores writing style profile
- Provides personalized system prompts
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from uuid import UUID
import json

import anthropic
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from ..models.message import Message, MessageDirection
from ..models.conversation import Conversation
from ..models.objective import Objective
from ..models.user import User


# =============================================================================
# Pydantic Models for Writing Style Analysis
# =============================================================================

class WritingStyleProfile(BaseModel):
    """Comprehensive writing style profile for a user."""

    # Tone characteristics
    overall_tone: str = Field(description="Overall communication tone (professional, casual, friendly, formal)")
    formality_level: int = Field(description="Formality on scale 1-5", ge=1, le=5)
    warmth_level: int = Field(description="Warmth/friendliness on scale 1-5", ge=1, le=5)

    # Length preferences
    avg_email_length: int = Field(description="Average email length in words")
    prefers_concise: bool = Field(description="Prefers brief, to-the-point emails")
    uses_bullet_points: bool = Field(description="Frequently uses bullet points")

    # Communication patterns
    common_greetings: List[str] = Field(description="Common greeting phrases", default_factory=list)
    common_closings: List[str] = Field(description="Common closing phrases", default_factory=list)
    common_phrases: List[str] = Field(description="Frequently used phrases", default_factory=list)

    # Structural preferences
    uses_paragraphs: bool = Field(description="Breaks content into paragraphs")
    includes_subject_lines: bool = Field(description="Writes descriptive subject lines")
    acknowledges_receipt: bool = Field(description="Typically acknowledges receiving emails")

    # Personality markers
    uses_exclamation: bool = Field(description="Uses exclamation marks")
    uses_emojis: bool = Field(description="Uses emojis in communication")
    shows_enthusiasm: bool = Field(description="Shows enthusiasm in writing")

    # Response patterns
    typical_response_time: str = Field(description="Typical response time (immediate, same-day, 1-2 days)")
    handles_multiple_questions: str = Field(description="How they handle multiple questions (numbered, bullets, paragraphs)")

    # Metadata
    sample_size: int = Field(description="Number of emails analyzed")
    confidence: float = Field(description="Confidence in this profile (0-1)")
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    # Examples
    example_emails: List[str] = Field(description="Example emails (truncated)", default_factory=list, max_items=3)


class StyleAnalysisResult(BaseModel):
    """Result of analyzing a batch of emails."""
    profile: WritingStyleProfile
    insights: List[str] = Field(description="Key insights about writing style")
    recommendations: List[str] = Field(description="Recommendations for AI to match this style")


# =============================================================================
# Writing Style Learning Service
# =============================================================================

class WritingStyleService:
    """Service for learning and applying user writing styles.

    This service:
    1. Analyzes user's historical sent emails
    2. Extracts writing style characteristics
    3. Stores style profile
    4. Generates personalized system prompts for AI
    5. Updates profile as more emails are sent
    """

    # Model configuration
    MODEL_NAME = "claude-opus-4-5-20251101"
    MAX_TOKENS = 4096
    TEMPERATURE = 0.3  # Lower temperature for consistent analysis

    def __init__(self, api_key: str):
        """Initialize the writing style service.

        Args:
            api_key: Anthropic API key for Claude access
        """
        self.client = anthropic.Anthropic(api_key=api_key)

    async def analyze_user_writing_style(
        self,
        db: AsyncSession,
        user_id: UUID,
        lookback_days: int = 90,
        max_emails: int = 50
    ) -> StyleAnalysisResult:
        """Analyze user's writing style from their sent emails.

        Args:
            db: Database session
            user_id: ID of the user to analyze
            lookback_days: How far back to look for sent emails
            max_emails: Maximum number of emails to analyze

        Returns:
            StyleAnalysisResult with profile and insights
        """
        # Get user's sent emails
        sent_emails = await self._get_sent_emails(
            db=db,
            user_id=user_id,
            lookback_days=lookback_days,
            max_emails=max_emails
        )

        if not sent_emails:
            # Return default profile if no sent emails
            return self._create_default_profile()

        # Prepare emails for analysis
        email_texts = []
        for msg in sent_emails:
            email_text = f"Subject: {msg.subject}\n\nBody:\n{msg.body_text[:1000]}"
            email_texts.append(email_text)

        # Use Claude to analyze writing style
        system_prompt = self._build_style_analysis_prompt()
        user_prompt = self._build_analysis_user_prompt(email_texts)

        response = self.client.messages.create(
            model=self.MODEL_NAME,
            max_tokens=self.MAX_TOKENS,
            temperature=self.TEMPERATURE,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            tools=[
                {
                    "name": "analyze_writing_style",
                    "description": "Provide comprehensive writing style analysis",
                    "input_schema": StyleAnalysisResult.model_json_schema()
                }
            ],
            tool_choice={"type": "tool", "name": "analyze_writing_style"}
        )

        # Extract the tool use result
        tool_use = next(block for block in response.content if block.type == "tool_use")
        analysis_data = tool_use.input

        return StyleAnalysisResult(**analysis_data)

    async def get_personalized_system_prompt(
        self,
        db: AsyncSession,
        user: User,
        base_prompt: str
    ) -> str:
        """Generate a personalized system prompt based on user's writing style.

        Args:
            db: Database session
            user: The user to personalize for
            base_prompt: Base system prompt to enhance

        Returns:
            Personalized system prompt with style guidance
        """
        # Check if we have a cached style profile
        if user.writing_style_profile:
            try:
                profile = WritingStyleProfile(**json.loads(user.writing_style_profile))
            except:
                # Profile is corrupted or outdated, re-analyze
                result = await self.analyze_user_writing_style(db, user.id)
                profile = result.profile
                # Cache it
                user.writing_style_profile = profile.model_dump_json()
                await db.commit()
        else:
            # Analyze and cache
            result = await self.analyze_user_writing_style(db, user.id)
            profile = result.profile
            user.writing_style_profile = profile.model_dump_json()
            await db.commit()

        # Build personalized prompt
        style_guidance = self._build_style_guidance(profile)

        return f"""{base_prompt}

WRITING STYLE PROFILE FOR {user.name}:
{style_guidance}

CRITICAL: Match this writing style closely. Your responses should sound like they were written by {user.name}, not by an AI."""

    def _build_style_guidance(self, profile: WritingStyleProfile) -> str:
        """Build style guidance text from profile."""
        guidance = []

        # Tone and formality
        guidance.append(f"- Overall tone: {profile.overall_tone}")
        guidance.append(f"- Formality level: {profile.formality_level}/5 ({'Very formal' if profile.formality_level >= 4 else 'Casual' if profile.formality_level <= 2 else 'Professional'})")
        guidance.append(f"- Warmth level: {profile.warmth_level}/5 ({'Very warm' if profile.warmth_level >= 4 else 'Reserved' if profile.warmth_level <= 2 else 'Balanced'})")

        # Length
        if profile.prefers_concise:
            guidance.append(f"- Length: Prefers concise emails (~{profile.avg_email_length} words)")
        else:
            guidance.append(f"- Length: Writes detailed emails (~{profile.avg_email_length} words)")

        # Greetings and closings
        if profile.common_greetings:
            guidance.append(f"- Common greetings: {', '.join(profile.common_greetings[:3])}")
        if profile.common_closings:
            guidance.append(f"- Common closings: {', '.join(profile.common_closings[:3])}")

        # Structure
        if profile.uses_bullet_points:
            guidance.append("- Frequently uses bullet points for clarity")
        if profile.uses_paragraphs:
            guidance.append("- Organizes content in clear paragraphs")

        # Personality
        if profile.uses_exclamation:
            guidance.append("- Uses exclamation marks to show enthusiasm")
        if profile.uses_emojis:
            guidance.append("- Occasionally uses emojis")
        if profile.shows_enthusiasm:
            guidance.append("- Shows enthusiasm and positive energy")

        # Response patterns
        if profile.acknowledges_receipt:
            guidance.append("- Typically acknowledges receipt of emails")
        if profile.handles_multiple_questions:
            guidance.append(f"- Handles multiple questions using: {profile.handles_multiple_questions}")

        # Common phrases
        if profile.common_phrases:
            guidance.append(f"- Frequently uses phrases like: {', '.join(profile.common_phrases[:5])}")

        return "\n".join(guidance)

    async def _get_sent_emails(
        self,
        db: AsyncSession,
        user_id: UUID,
        lookback_days: int,
        max_emails: int
    ) -> List[Message]:
        """Get user's sent emails for analysis."""
        time_threshold = datetime.utcnow() - timedelta(days=lookback_days)

        query = (
            select(Message)
            .join(Message.conversation)
            .join(Conversation.objective)
            .where(
                and_(
                    Objective.user_id == user_id,
                    Message.direction == MessageDirection.OUTGOING,
                    Message.created_at >= time_threshold,
                    Message.body_text != "",  # Exclude empty messages
                )
            )
            .order_by(Message.sent_at.desc())
            .limit(max_emails)
        )

        result = await db.execute(query)
        return list(result.scalars().all())

    def _build_style_analysis_prompt(self) -> str:
        """Build system prompt for style analysis."""
        return """You are an expert communication analyst specializing in writing style analysis.

Your role is to analyze a person's email writing style to help an AI match their unique communication patterns.

Analyze the following aspects:
1. Tone and formality - How do they communicate?
2. Length and structure - Do they write concise or detailed emails?
3. Greetings and closings - What phrases do they use?
4. Personality markers - Exclamation marks, emojis, enthusiasm
5. Communication patterns - How do they structure responses?
6. Common phrases and vocabulary

Be precise and evidence-based. Provide specific examples from the emails.

The goal is to create a profile that allows an AI to write emails that sound authentically like this person."""

    def _build_analysis_user_prompt(self, email_texts: List[str]) -> str:
        """Build user prompt for style analysis."""
        emails_section = "\n\n---\n\n".join(email_texts[:20])  # Limit to avoid token limits

        return f"""Analyze the writing style from these emails:

{emails_section}

Please provide a comprehensive writing style analysis using the analyze_writing_style tool.

Focus on:
- Concrete patterns you observe
- Specific examples from the emails
- Characteristics that make this person's writing unique
- How an AI should mimic this style"""

    def _create_default_profile(self) -> StyleAnalysisResult:
        """Create a default profile when no sent emails are available."""
        profile = WritingStyleProfile(
            overall_tone="professional",
            formality_level=3,
            warmth_level=3,
            avg_email_length=150,
            prefers_concise=True,
            uses_bullet_points=False,
            common_greetings=["Hi", "Hello"],
            common_closings=["Best regards", "Thanks"],
            common_phrases=[],
            uses_paragraphs=True,
            includes_subject_lines=True,
            acknowledges_receipt=True,
            uses_exclamation=False,
            uses_emojis=False,
            shows_enthusiasm=False,
            typical_response_time="same-day",
            handles_multiple_questions="paragraphs",
            sample_size=0,
            confidence=0.3,  # Low confidence for default
            example_emails=[]
        )

        return StyleAnalysisResult(
            profile=profile,
            insights=["No sent emails available - using default professional style"],
            recommendations=["Maintain professional, concise communication"]
        )
