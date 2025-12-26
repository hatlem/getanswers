"""Edit Learning Service - Learns from user edits to improve AI responses.

This service analyzes user edits to understand patterns and improve future AI-generated responses.

Key Features:
- Analyzes differences between AI drafts and user edits
- Identifies common correction patterns
- Updates writing style profile based on edits
- Provides feedback to improve AI confidence
- Tracks edit metrics for quality improvement
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from uuid import UUID
import difflib

import anthropic
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from ..models.agent_action import AgentAction, ActionStatus
from ..models.conversation import Conversation
from ..models.objective import Objective
from ..models.user import User


# =============================================================================
# Pydantic Models for Edit Analysis
# =============================================================================

class EditPattern(BaseModel):
    """A pattern identified in user edits."""
    pattern_type: str = Field(description="Type of edit pattern (tone, length, formality, content, structure)")
    description: str = Field(description="Description of the pattern")
    frequency: int = Field(description="How often this pattern occurs")
    examples: List[str] = Field(description="Example edits demonstrating this pattern", max_items=3)
    confidence: float = Field(description="Confidence in this pattern (0-1)")


class EditAnalysis(BaseModel):
    """Analysis of a user's edit behavior."""

    # Common patterns
    patterns: List[EditPattern] = Field(description="Identified edit patterns")

    # Tone adjustments
    makes_more_formal: bool = Field(description="User tends to make responses more formal")
    makes_more_casual: bool = Field(description="User tends to make responses more casual")
    adds_warmth: bool = Field(description="User adds warmth/friendliness")

    # Content adjustments
    makes_more_concise: bool = Field(description="User tends to shorten responses")
    adds_details: bool = Field(description="User tends to add more details")
    changes_structure: bool = Field(description="User reorganizes response structure")

    # Specific corrections
    adds_acknowledgments: bool = Field(description="User adds acknowledgment of receipt")
    adds_next_steps: bool = Field(description="User clarifies next steps")
    softens_language: bool = Field(description="User softens direct language")

    # Quality metrics
    avg_edit_percentage: float = Field(description="Average percentage of response edited (0-100)")
    heavy_edit_rate: float = Field(description="Percentage of responses with >50% edits")

    # Recommendations
    recommendations: List[str] = Field(description="Recommendations for improving AI responses")

    # Metadata
    sample_size: int = Field(description="Number of edits analyzed")
    time_period: str = Field(description="Time period covered by analysis")


class EditFeedback(BaseModel):
    """Feedback from analyzing a single edit."""

    edit_type: str = Field(description="Type of edit (minor, moderate, major, rewrite)")
    edit_percentage: float = Field(description="Percentage of content changed (0-100)")

    tone_changed: bool = Field(description="User changed the tone")
    length_changed: bool = Field(description="User changed the length significantly")
    structure_changed: bool = Field(description="User reorganized the response")

    key_changes: List[str] = Field(description="Key changes made by user")
    learning_points: List[str] = Field(description="What the AI should learn from this edit")

    suggested_confidence_adjustment: float = Field(description="Suggested adjustment to confidence (-10 to +10)")


# =============================================================================
# Edit Learning Service
# =============================================================================

class EditLearningService:
    """Service for learning from user edits to improve AI responses.

    This service:
    1. Analyzes individual edits when they happen
    2. Identifies patterns across multiple edits
    3. Updates writing style profile based on edits
    4. Provides feedback for AI confidence calibration
    5. Tracks metrics for quality improvement
    """

    # Model configuration
    MODEL_NAME = "claude-sonnet-4-5-20250929"  # Sonnet for faster analysis
    MAX_TOKENS = 2048
    TEMPERATURE = 0.3  # Lower temperature for consistent analysis

    def __init__(self, api_key: str):
        """Initialize the edit learning service.

        Args:
            api_key: Anthropic API key for Claude access
        """
        self.client = anthropic.Anthropic(api_key=api_key)

    async def analyze_edit(
        self,
        original_draft: str,
        user_edit: str,
        context: Optional[str] = None
    ) -> EditFeedback:
        """Analyze a single user edit to understand what changed and why.

        Args:
            original_draft: The AI-generated draft
            user_edit: The user's edited version
            context: Optional context about the email (subject, sender, etc.)

        Returns:
            EditFeedback with analysis of the edit
        """
        # Calculate edit percentage using difflib
        edit_percentage = self._calculate_edit_percentage(original_draft, user_edit)

        # Use Claude to analyze the semantic changes
        system_prompt = self._build_edit_analysis_prompt()
        user_prompt = self._build_edit_user_prompt(original_draft, user_edit, edit_percentage, context)

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
                    "name": "analyze_edit",
                    "description": "Analyze the user's edit to understand what changed",
                    "input_schema": EditFeedback.model_json_schema()
                }
            ],
            tool_choice={"type": "tool", "name": "analyze_edit"}
        )

        # Extract the tool use result
        tool_use = next(block for block in response.content if block.type == "tool_use")
        feedback_data = tool_use.input

        return EditFeedback(**feedback_data)

    async def analyze_user_edit_patterns(
        self,
        db: AsyncSession,
        user_id: UUID,
        lookback_days: int = 30,
        min_edits: int = 5
    ) -> Optional[EditAnalysis]:
        """Analyze patterns in a user's edits over time.

        Args:
            db: Database session
            user_id: ID of the user to analyze
            lookback_days: How far back to look for edits
            min_edits: Minimum number of edits required for analysis

        Returns:
            EditAnalysis with identified patterns, or None if insufficient data
        """
        # Get user's edited actions
        edited_actions = await self._get_edited_actions(
            db=db,
            user_id=user_id,
            lookback_days=lookback_days
        )

        if len(edited_actions) < min_edits:
            return None

        # Prepare data for analysis
        edits_data = []
        for action in edited_actions:
            edit_data = {
                "original": action.proposed_content[:500],  # Limit for token efficiency
                "edited": action.user_edit[:500] if action.user_edit else "",
                "edit_percentage": self._calculate_edit_percentage(
                    action.proposed_content,
                    action.user_edit or ""
                )
            }
            edits_data.append(edit_data)

        # Use Claude to identify patterns
        system_prompt = self._build_pattern_analysis_prompt()
        user_prompt = self._build_pattern_user_prompt(edits_data, len(edited_actions), lookback_days)

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
                    "name": "analyze_patterns",
                    "description": "Identify patterns in user edits",
                    "input_schema": EditAnalysis.model_json_schema()
                }
            ],
            tool_choice={"type": "tool", "name": "analyze_patterns"}
        )

        # Extract the tool use result
        tool_use = next(block for block in response.content if block.type == "tool_use")
        analysis_data = tool_use.input

        return EditAnalysis(**analysis_data)

    async def update_writing_style_from_edits(
        self,
        db: AsyncSession,
        user: User,
        edit_analysis: EditAnalysis
    ) -> None:
        """Update user's writing style profile based on edit patterns.

        Args:
            db: Database session
            user: The user to update
            edit_analysis: Analysis of user's edit patterns
        """
        import json

        # Get current profile
        current_profile = {}
        if user.writing_style_profile:
            try:
                current_profile = json.loads(user.writing_style_profile)
            except:
                pass

        # Apply adjustments based on edit patterns
        adjustments = {}

        # Formality adjustments
        if edit_analysis.makes_more_formal:
            adjustments["formality_level"] = min(5, current_profile.get("formality_level", 3) + 1)
        elif edit_analysis.makes_more_casual:
            adjustments["formality_level"] = max(1, current_profile.get("formality_level", 3) - 1)

        # Warmth adjustments
        if edit_analysis.adds_warmth:
            adjustments["warmth_level"] = min(5, current_profile.get("warmth_level", 3) + 1)

        # Length adjustments
        if edit_analysis.makes_more_concise:
            adjustments["prefers_concise"] = True
        elif edit_analysis.adds_details:
            adjustments["prefers_concise"] = False

        # Acknowledgment preference
        if edit_analysis.adds_acknowledgments:
            adjustments["acknowledges_receipt"] = True

        # Update profile
        updated_profile = {**current_profile, **adjustments}
        user.writing_style_profile = json.dumps(updated_profile)

        await db.commit()

    def _calculate_edit_percentage(self, original: str, edited: str) -> float:
        """Calculate percentage of text that was changed.

        Uses difflib's SequenceMatcher to compute similarity.

        Args:
            original: Original text
            edited: Edited text

        Returns:
            Percentage changed (0-100)
        """
        if not original or not edited:
            return 100.0

        matcher = difflib.SequenceMatcher(None, original, edited)
        similarity = matcher.ratio()

        return round((1 - similarity) * 100, 1)

    async def _get_edited_actions(
        self,
        db: AsyncSession,
        user_id: UUID,
        lookback_days: int
    ) -> List[AgentAction]:
        """Get user's edited actions for analysis."""
        time_threshold = datetime.utcnow() - timedelta(days=lookback_days)

        query = (
            select(AgentAction)
            .join(AgentAction.conversation)
            .join(Conversation.objective)
            .where(
                and_(
                    Objective.user_id == user_id,
                    AgentAction.status == ActionStatus.EDITED,
                    AgentAction.user_edit.isnot(None),
                    AgentAction.approved_at >= time_threshold
                )
            )
            .order_by(AgentAction.approved_at.desc())
            .limit(50)  # Limit to recent 50 edits for performance
        )

        result = await db.execute(query)
        return list(result.scalars().all())

    def _build_edit_analysis_prompt(self) -> str:
        """Build system prompt for edit analysis."""
        return """You are an expert AI response quality analyst.

Your role is to analyze user edits to AI-generated email responses to understand:
1. What the user changed and why
2. Whether it was a tone/style change or content correction
3. What patterns emerge from the edit
4. How the AI should adjust future responses

Be specific and actionable in your analysis. Focus on concrete learnings that will help improve future AI responses."""

    def _build_edit_user_prompt(
        self,
        original: str,
        edited: str,
        edit_percentage: float,
        context: Optional[str]
    ) -> str:
        """Build user prompt for edit analysis."""
        context_str = f"\n\nCONTEXT:\n{context}" if context else ""

        return f"""Analyze this user edit to understand what changed:

ORIGINAL AI DRAFT:
{original}

USER'S EDITED VERSION:
{edited}

EDIT PERCENTAGE: {edit_percentage}%{context_str}

Please analyze the edit using the analyze_edit tool. Focus on:
- What changed (tone, content, structure, length)
- Why the user might have made these changes
- What the AI should learn from this edit
- Whether confidence should be adjusted for similar situations"""

    def _build_pattern_analysis_prompt(self) -> str:
        """Build system prompt for pattern analysis."""
        return """You are an expert pattern recognition analyst for AI-generated content.

Your role is to identify consistent patterns in how a user edits AI-generated email responses.

Look for:
1. Consistent tone adjustments (more formal, more casual, warmer)
2. Length preferences (more concise, more detailed)
3. Structural changes (adds/removes sections, uses bullets)
4. Content patterns (adds acknowledgments, clarifies next steps)

Your goal is to identify actionable patterns that will help the AI generate better first-draft responses that need fewer edits."""

    def _build_pattern_user_prompt(
        self,
        edits_data: List[Dict],
        total_edits: int,
        lookback_days: int
    ) -> str:
        """Build user prompt for pattern analysis."""
        # Show sample of edits (limited for tokens)
        samples_str = ""
        for i, edit in enumerate(edits_data[:10], 1):
            samples_str += f"\n--- Edit {i} (Changed {edit['edit_percentage']}%) ---\n"
            samples_str += f"Original: {edit['original'][:200]}...\n"
            samples_str += f"Edited: {edit['edited'][:200]}...\n"

        return f"""Analyze patterns in this user's edits over the last {lookback_days} days:

TOTAL EDITS ANALYZED: {total_edits}

SAMPLE EDITS:
{samples_str}

Please identify consistent patterns using the analyze_patterns tool. Focus on:
- What types of changes does this user consistently make?
- Are there tone/formality patterns?
- Are there length/structure patterns?
- Are there content patterns (acknowledgments, next steps, etc.)?
- What recommendations would improve AI responses for this user?"""
