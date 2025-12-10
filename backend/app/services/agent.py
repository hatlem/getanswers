"""Claude AI agent service for email processing and response generation.

This service leverages Claude's advanced language understanding to:
- Analyze email intent, sentiment, and urgency
- Generate contextually appropriate responses
- Assess risk levels based on content and policies
- Match user-defined policies to incoming emails
- Calculate confidence scores for automated actions
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
import json

import anthropic
from pydantic import BaseModel, Field

from ..models.message import Message, MessageDirection
from ..models.policy import Policy
from ..models.agent_action import RiskLevel, ActionType
from ..models.user import AutonomyLevel


# =============================================================================
# Pydantic Models for AI Analysis
# =============================================================================

class ExtractedEntity(BaseModel):
    """Entity extracted from email content."""
    type: str = Field(description="Entity type (person, organization, date, amount, etc.)")
    value: str = Field(description="The extracted value")
    confidence: float = Field(description="Confidence score 0-1")


class EmailIntent(BaseModel):
    """The identified intent of the email."""
    primary: str = Field(description="Primary intent (request, question, fyi, invitation, etc.)")
    secondary: Optional[str] = Field(default=None, description="Secondary intent if applicable")
    description: str = Field(description="Brief description of what the sender wants")


class EmailAnalysis(BaseModel):
    """Comprehensive analysis of an email."""

    # Intent analysis
    intent: EmailIntent = Field(description="What the sender wants")

    # Sentiment and tone
    sentiment: str = Field(description="Overall sentiment (positive, neutral, negative, urgent)")
    tone: str = Field(description="Communication tone (formal, casual, friendly, demanding, etc.)")

    # Urgency assessment
    urgency: str = Field(description="Urgency level (critical, high, medium, low)")
    requires_immediate_response: bool = Field(description="Whether this needs immediate attention")

    # Classification
    category: str = Field(description="Email category (meeting, task, question, update, sales, support, etc.)")
    is_actionable: bool = Field(description="Whether this requires action")

    # Key information
    extracted_entities: list[ExtractedEntity] = Field(default_factory=list, description="Key entities extracted")
    key_points: list[str] = Field(description="Main points from the email")

    # Sender assessment
    sender_relationship: str = Field(description="Relationship type (colleague, client, vendor, unknown, etc.)")
    is_likely_spam: bool = Field(default=False, description="Whether this appears to be spam")

    # Context
    context_summary: str = Field(description="Summary of the conversation context")


class DraftResponse(BaseModel):
    """A generated email response draft."""

    subject: str = Field(description="Email subject line")
    body: str = Field(description="Email body text")

    suggested_action: ActionType = Field(description="Suggested action type")
    reasoning: str = Field(description="Why this response is appropriate")

    # Alternative approaches
    alternative_tone: Optional[str] = Field(default=None, description="Alternative tone suggestion if needed")
    key_considerations: list[str] = Field(default_factory=list, description="Important points to consider")


class PolicyMatch(BaseModel):
    """A matched user policy."""

    policy_id: UUID = Field(description="ID of the matched policy")
    policy_name: str = Field(description="Name of the policy")
    matched_rule: str = Field(description="Which rule was matched")
    confidence: float = Field(description="Match confidence 0-1")
    action_override: Optional[str] = Field(default=None, description="Suggested action from policy")
    reasoning: str = Field(description="Why this policy applies")


class RiskAssessment(BaseModel):
    """Risk assessment for an email and proposed action."""

    risk_level: RiskLevel = Field(description="Overall risk level")
    risk_factors: list[str] = Field(description="Identified risk factors")
    mitigation_suggestions: list[str] = Field(default_factory=list, description="How to mitigate risks")

    # Specific risk categories
    has_financial_implications: bool = Field(default=False)
    has_legal_implications: bool = Field(default=False)
    has_confidential_content: bool = Field(default=False)
    involves_unknown_party: bool = Field(default=False)


# =============================================================================
# Agent Service
# =============================================================================

class AgentService:
    """Claude AI agent for intelligent email processing.

    This service acts as an expert executive assistant, capable of:
    - Understanding complex email threads and context
    - Generating human-like responses that match user's style
    - Identifying urgent matters and VIP communications
    - Assessing risk and determining appropriate autonomy levels
    - Enforcing user-defined policies and preferences
    """

    # Model configuration
    MODEL_NAME = "claude-opus-4-5-20251101"  # Latest and most capable Claude model
    MAX_TOKENS = 4096
    TEMPERATURE = 0.7  # Balanced between creativity and consistency

    def __init__(self, api_key: str):
        """Initialize the agent service.

        Args:
            api_key: Anthropic API key for Claude access
        """
        self.client = anthropic.Anthropic(api_key=api_key)

    # =========================================================================
    # Email Analysis
    # =========================================================================

    async def analyze_email(
        self,
        message: Message,
        conversation_context: list[Message],
        user_email: str,
        user_name: str
    ) -> EmailAnalysis:
        """Analyze email intent, sentiment, urgency, and required action.

        Args:
            message: The email message to analyze
            conversation_context: Previous messages in the thread
            user_email: The user's email address
            user_name: The user's name

        Returns:
            Comprehensive email analysis
        """
        system_prompt = self._build_analysis_system_prompt(user_email, user_name)
        user_prompt = self._build_analysis_user_prompt(message, conversation_context)

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
                    "name": "analyze_email",
                    "description": "Provide comprehensive analysis of the email",
                    "input_schema": EmailAnalysis.model_json_schema()
                }
            ],
            tool_choice={"type": "tool", "name": "analyze_email"}
        )

        # Extract the tool use result
        tool_use = next(block for block in response.content if block.type == "tool_use")
        analysis_data = tool_use.input

        return EmailAnalysis(**analysis_data)

    # =========================================================================
    # Response Generation
    # =========================================================================

    async def generate_response(
        self,
        message: Message,
        conversation_context: list[Message],
        analysis: EmailAnalysis,
        user_email: str,
        user_name: str,
        user_preferences: Optional[dict] = None
    ) -> DraftResponse:
        """Generate a contextually appropriate response draft.

        Args:
            message: The email message to respond to
            conversation_context: Previous messages in the thread
            analysis: The email analysis
            user_email: The user's email address
            user_name: The user's name
            user_preferences: Optional user preferences for tone, style, etc.

        Returns:
            Draft response with reasoning
        """
        system_prompt = self._build_response_system_prompt(
            user_email, user_name, user_preferences
        )
        user_prompt = self._build_response_user_prompt(
            message, conversation_context, analysis
        )

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
                    "name": "draft_response",
                    "description": "Generate an email response draft",
                    "input_schema": DraftResponse.model_json_schema()
                }
            ],
            tool_choice={"type": "tool", "name": "draft_response"}
        )

        # Extract the tool use result
        tool_use = next(block for block in response.content if block.type == "tool_use")
        draft_data = tool_use.input

        return DraftResponse(**draft_data)

    # =========================================================================
    # Confidence Scoring
    # =========================================================================

    async def calculate_confidence(
        self,
        message: Message,
        analysis: EmailAnalysis,
        draft: DraftResponse,
        conversation_context: list[Message],
        user_historical_acceptance_rate: Optional[float] = None
    ) -> float:
        """Calculate confidence score (0-100) for the proposed action.

        The confidence score is based on multiple factors:
        - Clarity of email intent
        - Quality of response match
        - Similarity to previously handled emails
        - User's historical acceptance rate
        - Risk factors present

        Args:
            message: The email message
            analysis: The email analysis
            draft: The draft response
            conversation_context: Previous messages
            user_historical_acceptance_rate: User's past acceptance rate (0-1)

        Returns:
            Confidence score from 0-100
        """
        # Base confidence factors
        factors = {}

        # Intent clarity (0-25 points)
        intent_clarity = self._assess_intent_clarity(analysis)
        factors['intent_clarity'] = intent_clarity * 25

        # Response quality (0-25 points)
        response_quality = self._assess_response_quality(message, analysis, draft)
        factors['response_quality'] = response_quality * 25

        # Context familiarity (0-20 points)
        context_score = self._assess_context_familiarity(
            message, conversation_context, analysis
        )
        factors['context_familiarity'] = context_score * 20

        # Historical performance (0-20 points)
        if user_historical_acceptance_rate is not None:
            factors['historical_performance'] = user_historical_acceptance_rate * 20
        else:
            factors['historical_performance'] = 10  # Neutral default

        # Risk adjustment (0-10 points, or negative)
        risk_adjustment = self._calculate_risk_adjustment(analysis)
        factors['risk_adjustment'] = risk_adjustment * 10

        # Calculate total confidence
        total_confidence = sum(factors.values())

        # Ensure bounds
        return max(0.0, min(100.0, total_confidence))

    # =========================================================================
    # Risk Assessment
    # =========================================================================

    async def assess_risk(
        self,
        message: Message,
        analysis: EmailAnalysis,
        policies: list[Policy],
        conversation_context: list[Message]
    ) -> RiskAssessment:
        """Assess risk level based on content and policies.

        Args:
            message: The email message
            analysis: The email analysis
            policies: User's active policies
            conversation_context: Previous messages

        Returns:
            Detailed risk assessment
        """
        system_prompt = self._build_risk_assessment_prompt()
        user_prompt = self._build_risk_user_prompt(
            message, analysis, policies, conversation_context
        )

        response = self.client.messages.create(
            model=self.MODEL_NAME,
            max_tokens=2048,
            temperature=0.3,  # Lower temperature for more consistent risk assessment
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            tools=[
                {
                    "name": "assess_risk",
                    "description": "Assess the risk level of this email and proposed actions",
                    "input_schema": RiskAssessment.model_json_schema()
                }
            ],
            tool_choice={"type": "tool", "name": "assess_risk"}
        )

        # Extract the tool use result
        tool_use = next(block for block in response.content if block.type == "tool_use")
        risk_data = tool_use.input

        return RiskAssessment(**risk_data)

    # =========================================================================
    # Policy Evaluation
    # =========================================================================

    async def evaluate_policies(
        self,
        message: Message,
        analysis: EmailAnalysis,
        policies: list[Policy]
    ) -> list[PolicyMatch]:
        """Check which user policies apply to this message.

        Args:
            message: The email message
            analysis: The email analysis
            policies: User's active policies

        Returns:
            List of matched policies with confidence scores
        """
        if not policies:
            return []

        system_prompt = self._build_policy_evaluation_prompt()
        user_prompt = self._build_policy_user_prompt(message, analysis, policies)

        # Define the schema for policy matches
        policy_matches_schema = {
            "type": "object",
            "properties": {
                "matches": {
                    "type": "array",
                    "items": PolicyMatch.model_json_schema()
                }
            },
            "required": ["matches"]
        }

        response = self.client.messages.create(
            model=self.MODEL_NAME,
            max_tokens=2048,
            temperature=0.3,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            tools=[
                {
                    "name": "evaluate_policies",
                    "description": "Identify which policies match this email",
                    "input_schema": policy_matches_schema
                }
            ],
            tool_choice={"type": "tool", "name": "evaluate_policies"}
        )

        # Extract the tool use result
        tool_use = next(block for block in response.content if block.type == "tool_use")
        matches_data = tool_use.input.get("matches", [])

        return [PolicyMatch(**match) for match in matches_data]

    # =========================================================================
    # Auto-Execution Decision
    # =========================================================================

    async def should_auto_execute(
        self,
        confidence: float,
        risk_level: RiskLevel,
        autonomy_level: AutonomyLevel,
        action_type: ActionType
    ) -> bool:
        """Determine if action can be auto-executed based on user preferences.

        Decision matrix:
        - HIGH autonomy: Auto-execute low-risk actions with confidence >= 70
        - MEDIUM autonomy: Auto-execute low-risk actions with confidence >= 85
        - LOW autonomy: Never auto-execute, always require approval

        Special cases:
        - SEND actions require higher confidence threshold (+10)
        - MEDIUM/HIGH risk always requires approval
        - Critical urgency may lower threshold by 5 points

        Args:
            confidence: Confidence score (0-100)
            risk_level: Assessed risk level
            autonomy_level: User's autonomy preference
            action_type: The type of action being proposed

        Returns:
            True if action should be auto-executed, False if approval needed
        """
        # Never auto-execute medium or high risk actions
        if risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH]:
            return False

        # Never auto-execute with low autonomy setting
        if autonomy_level == AutonomyLevel.LOW:
            return False

        # Determine confidence threshold based on autonomy level
        if autonomy_level == AutonomyLevel.HIGH:
            threshold = 70.0
        else:  # MEDIUM
            threshold = 85.0

        # Sending emails requires higher confidence
        if action_type == ActionType.SEND:
            threshold += 10.0

        return confidence >= threshold

    # =========================================================================
    # System Prompt Builders
    # =========================================================================

    def _build_analysis_system_prompt(self, user_email: str, user_name: str) -> str:
        """Build system prompt for email analysis."""
        return f"""You are an expert executive assistant AI analyzing emails on behalf of {user_name} ({user_email}).

Your role is to provide comprehensive, accurate analysis of incoming emails to help automate email management.

Key responsibilities:
1. Identify the sender's primary intent and what they need
2. Assess urgency and whether immediate response is required
3. Classify the email type and extract key information
4. Evaluate the sender's relationship and communication tone
5. Detect potential spam or suspicious content
6. Provide context-aware analysis considering the full conversation thread

Guidelines:
- Be precise and objective in your analysis
- Consider cultural and professional context
- Flag anything unusual or potentially concerning
- Extract actionable information and key entities
- Assess urgency based on content, not just keywords
- Understand the difference between formal and casual business communication
- Recognize VIP senders (executives, major clients, partners)

Your analysis will be used to generate appropriate responses and determine automation confidence levels."""

    def _build_analysis_user_prompt(
        self,
        message: Message,
        conversation_context: list[Message]
    ) -> str:
        """Build user prompt for email analysis."""
        context_str = self._format_conversation_context(conversation_context)

        return f"""Analyze this email:

FROM: {message.sender_name} <{message.sender_email}>
SUBJECT: {message.subject}
SENT: {message.sent_at.isoformat()}

MESSAGE:
{message.body_text}

CONVERSATION CONTEXT:
{context_str if context_str else "This is the first message in the thread."}

Please provide a comprehensive analysis of this email using the analyze_email tool."""

    def _build_response_system_prompt(
        self,
        user_email: str,
        user_name: str,
        user_preferences: Optional[dict] = None
    ) -> str:
        """Build system prompt for response generation."""
        preferences_str = ""
        if user_preferences:
            tone_pref = user_preferences.get("communication_tone", "professional")
            length_pref = user_preferences.get("response_length", "concise")
            preferences_str = f"""
User Preferences:
- Communication tone: {tone_pref}
- Response length: {length_pref}
"""

        return f"""You are an expert executive assistant AI writing emails on behalf of {user_name} ({user_email}).

Your role is to compose professional, contextually appropriate email responses that sound natural and human.

Key principles:
1. Match the tone and formality level of the incoming email
2. Be concise but complete - answer all questions and address all points
3. Use the user's natural communication style (based on their past emails in the thread)
4. Be professional but warm and personable
5. Get to the point quickly - busy professionals appreciate brevity
6. Use proper email etiquette (greeting, body, closing)
7. Proofread for grammar, spelling, and clarity
{preferences_str}

Email writing guidelines:
- Start with an appropriate greeting (Hi/Hello for casual, Dear for formal)
- Acknowledge receipt if responding to a question or request
- Be direct about next steps or actions
- Use bullet points for multiple items when appropriate
- Close professionally (Best regards, Thanks, etc.)
- Never make commitments you're unsure about - suggest checking or confirming instead
- If uncertain, draft a conservative response that keeps options open

Tone matching:
- Formal email → Professional, structured response
- Casual email → Friendly, conversational response
- Urgent email → Direct, action-oriented response
- Long detailed email → Thorough, comprehensive response
- Short quick email → Brief, to-the-point response

Remember: You're representing {user_name}, so maintain their professional reputation and relationships."""

    def _build_response_user_prompt(
        self,
        message: Message,
        conversation_context: list[Message],
        analysis: EmailAnalysis
    ) -> str:
        """Build user prompt for response generation."""
        context_str = self._format_conversation_context(conversation_context)

        # Format analysis insights
        analysis_summary = f"""
Email Analysis:
- Intent: {analysis.intent.primary} - {analysis.intent.description}
- Sentiment: {analysis.sentiment}
- Tone: {analysis.tone}
- Urgency: {analysis.urgency}
- Category: {analysis.category}
- Requires action: {analysis.is_actionable}
- Key points: {', '.join(analysis.key_points[:3])}
"""

        return f"""Generate a response to this email:

FROM: {message.sender_name} <{message.sender_email}>
SUBJECT: {message.subject}

MESSAGE:
{message.body_text}

CONVERSATION CONTEXT:
{context_str if context_str else "This is the first message in the thread."}

{analysis_summary}

Please draft an appropriate response using the draft_response tool. The response should:
1. Address all points raised in the email
2. Match the sender's communication style
3. Be clear about next steps or actions
4. Maintain professional relationships
5. Sound natural and human, not robotic"""

    def _build_risk_assessment_prompt(self) -> str:
        """Build system prompt for risk assessment."""
        return """You are a risk assessment AI specializing in email security and business risk evaluation.

Your role is to identify potential risks in email communications and proposed responses.

Risk categories to evaluate:
1. Financial implications (payments, contracts, pricing, commitments)
2. Legal implications (agreements, obligations, liability, compliance)
3. Confidential content (sensitive data, private information, trade secrets)
4. Unknown parties (new contacts, unverified senders, suspicious origins)
5. Reputational risk (public statements, commitments, controversial topics)
6. Operational risk (system access, process changes, resource allocation)

Risk levels:
- LOW: Routine communication with known parties, no significant implications
- MEDIUM: Involves some commitment, new parties, or requires careful wording
- HIGH: Financial/legal implications, confidential matters, major commitments

Be conservative but not paranoid. Most business emails are low risk.
Focus on actual material risks, not theoretical possibilities."""

    def _build_risk_user_prompt(
        self,
        message: Message,
        analysis: EmailAnalysis,
        policies: list[Policy],
        conversation_context: list[Message]
    ) -> str:
        """Build user prompt for risk assessment."""
        context_str = self._format_conversation_context(conversation_context)

        policies_str = ""
        if policies:
            policies_str = "Active Policies:\n" + "\n".join(
                f"- {p.name}: {p.description}" for p in policies[:5]
            )

        return f"""Assess the risk level for this email and any proposed response:

FROM: {message.sender_name} <{message.sender_email}>
SUBJECT: {message.subject}

MESSAGE:
{message.body_text}

ANALYSIS:
- Intent: {analysis.intent.primary}
- Category: {analysis.category}
- Sender relationship: {analysis.sender_relationship}
- Is spam: {analysis.is_likely_spam}
- Key points: {', '.join(analysis.key_points[:3])}

CONTEXT:
{context_str if context_str else "First message in thread."}

{policies_str}

Please assess the risk level using the assess_risk tool."""

    def _build_policy_evaluation_prompt(self) -> str:
        """Build system prompt for policy evaluation."""
        return """You are a policy matching AI that evaluates whether user-defined automation policies apply to incoming emails.

Your role is to accurately match emails against policy rules and determine if policies should be triggered.

When evaluating policies:
1. Read the policy rules carefully and literally
2. Check if the email content matches the conditions
3. Consider both explicit matches and semantic/intent matches
4. Assign confidence scores based on match quality
5. Explain which specific rule matched and why

Policy rule types you may encounter:
- Sender-based (specific addresses or domains)
- Keyword-based (presence of specific terms)
- Category-based (type of email)
- Intent-based (what the sender wants)
- Urgency-based (time-sensitive matters)
- Conditional (if X then Y logic)

Be precise but not overly strict. Use common sense for semantic matching."""

    def _build_policy_user_prompt(
        self,
        message: Message,
        analysis: EmailAnalysis,
        policies: list[Policy]
    ) -> str:
        """Build user prompt for policy evaluation."""
        policies_str = "\n\n".join(
            f"Policy: {p.name}\n"
            f"Description: {p.description}\n"
            f"Rules: {json.dumps(p.rules, indent=2)}"
            for p in policies
        )

        return f"""Evaluate which policies match this email:

FROM: {message.sender_name} <{message.sender_email}>
SUBJECT: {message.subject}

MESSAGE:
{message.body_text}

ANALYSIS:
- Intent: {analysis.intent.primary} - {analysis.intent.description}
- Category: {analysis.category}
- Urgency: {analysis.urgency}
- Sender relationship: {analysis.sender_relationship}
- Key points: {', '.join(analysis.key_points)}

USER POLICIES:
{policies_str}

Please identify which policies match this email using the evaluate_policies tool.
Only include policies that clearly match based on the rules defined."""

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _format_conversation_context(self, messages: list[Message]) -> str:
        """Format conversation history for context."""
        if not messages:
            return ""

        formatted = []
        for msg in messages[-5:]:  # Last 5 messages for context
            direction = "SENT" if msg.direction == MessageDirection.OUTGOING else "RECEIVED"
            formatted.append(
                f"[{msg.sent_at.strftime('%Y-%m-%d %H:%M')}] {direction} - "
                f"{msg.sender_name}: {msg.subject}\n"
                f"{msg.body_text[:200]}{'...' if len(msg.body_text) > 200 else ''}"
            )

        return "\n\n".join(formatted)

    def _assess_intent_clarity(self, analysis: EmailAnalysis) -> float:
        """Assess how clear the email intent is (0-1)."""
        score = 0.5  # Base score

        # Clear intent increases score
        if analysis.intent.description:
            score += 0.2

        # Actionable emails with clear requests
        if analysis.is_actionable and analysis.intent.primary in [
            "request", "question", "invitation", "task"
        ]:
            score += 0.2

        # FYI emails are usually clear
        if analysis.intent.primary == "fyi":
            score += 0.1

        # Spam or unclear emails reduce score
        if analysis.is_likely_spam:
            score -= 0.3

        return max(0.0, min(1.0, score))

    def _assess_response_quality(
        self,
        message: Message,
        analysis: EmailAnalysis,
        draft: DraftResponse
    ) -> float:
        """Assess quality of generated response (0-1)."""
        score = 0.6  # Base score for AI-generated content

        # Good reasoning increases confidence
        if len(draft.reasoning) > 50:
            score += 0.15

        # Appropriate action type
        if analysis.is_actionable and draft.suggested_action != ActionType.DRAFT:
            score += 0.1

        # Has key considerations
        if draft.key_considerations:
            score += 0.1

        # Response has substance
        if len(draft.body) > 100:
            score += 0.05

        return min(1.0, score)

    def _assess_context_familiarity(
        self,
        message: Message,
        conversation_context: list[Message],
        analysis: EmailAnalysis
    ) -> float:
        """Assess familiarity with conversation context (0-1)."""
        score = 0.3  # Base score

        # Existing conversation increases familiarity
        if conversation_context:
            score += 0.3

            # Long conversation
            if len(conversation_context) >= 3:
                score += 0.1

        # Known sender relationship
        if analysis.sender_relationship in ["colleague", "client", "vendor"]:
            score += 0.2

        # Clear category
        if analysis.category not in ["unknown", "other"]:
            score += 0.1

        return min(1.0, score)

    def _calculate_risk_adjustment(self, analysis: EmailAnalysis) -> float:
        """Calculate risk adjustment factor (-0.5 to 1.0)."""
        adjustment = 0.0

        # Low urgency routine emails are safer
        if analysis.urgency == "low" and not analysis.requires_immediate_response:
            adjustment += 0.3

        # Known sender increases safety
        if analysis.sender_relationship in ["colleague", "client"]:
            adjustment += 0.2

        # Spam or unknown senders reduce confidence
        if analysis.is_likely_spam:
            adjustment -= 0.5

        if analysis.sender_relationship == "unknown":
            adjustment -= 0.2

        # Negative sentiment may need careful handling
        if analysis.sentiment == "negative":
            adjustment -= 0.1

        return max(-0.5, min(1.0, adjustment))
