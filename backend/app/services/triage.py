"""Email Triage Service - Orchestrates the email processing pipeline.

This service is the heart of GetAnswers, coordinating:
1. Email sync from Gmail
2. Message parsing and conversation threading
3. Smart objective grouping
4. AI analysis and response generation
5. Action creation and execution
6. Auto-execution decisions based on confidence and risk
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID
import asyncio

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload, joinedload

from ..models.user import User, AutonomyLevel
from ..models.message import Message, MessageDirection
from ..models.conversation import Conversation
from ..models.objective import Objective, ObjectiveStatus
from ..models.agent_action import AgentAction, ActionType, RiskLevel, ActionStatus
from ..models.policy import Policy
from .agent import AgentService, EmailAnalysis, DraftResponse
from .gmail import GmailService, GmailServiceError

# Configure logging
logger = logging.getLogger(__name__)


# =============================================================================
# Pydantic Models for Service Responses
# =============================================================================

class SyncResult(BaseModel):
    """Result of a Gmail inbox sync operation."""

    new_messages: int = Field(description="Number of new messages fetched")
    processed: int = Field(description="Number of messages successfully processed")
    errors: int = Field(description="Number of messages that failed processing")
    duration_seconds: float = Field(description="Time taken for sync operation")
    last_sync_time: datetime = Field(description="Timestamp of this sync")
    error_details: List[str] = Field(default_factory=list, description="List of error messages")


class ExecutionResult(BaseModel):
    """Result of executing an agent action."""

    success: bool = Field(description="Whether execution succeeded")
    action_id: UUID = Field(description="ID of the executed action")
    gmail_message_id: Optional[str] = Field(None, description="Gmail message ID if sent")
    gmail_thread_id: Optional[str] = Field(None, description="Gmail thread ID")
    error: Optional[str] = Field(None, description="Error message if failed")
    executed_at: datetime = Field(default_factory=datetime.utcnow)


class ProcessingResult(BaseModel):
    """Result of processing a single email message."""

    action_id: UUID = Field(description="ID of the created action")
    conversation_id: UUID = Field(description="ID of the conversation")
    objective_id: UUID = Field(description="ID of the objective")
    confidence: float = Field(description="Confidence score (0-100)")
    risk_level: RiskLevel = Field(description="Assessed risk level")
    auto_executed: bool = Field(description="Whether action was auto-executed")
    action_type: ActionType = Field(description="Type of action proposed")


class ObjectiveGroupingResult(BaseModel):
    """Result of objective grouping analysis."""

    objective_id: UUID = Field(description="ID of the matched or created objective")
    is_new: bool = Field(description="Whether this is a newly created objective")
    title: str = Field(description="Objective title")
    confidence: float = Field(description="Confidence in the grouping (0-1)")
    reasoning: str = Field(description="Why this grouping was chosen")


# =============================================================================
# Gmail Helper Methods
# =============================================================================

def _parse_gmail_message(gmail_message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse raw Gmail API message into our expected format.

    Args:
        gmail_message: Raw message from Gmail API

    Returns:
        Parsed message dict with standardized fields
    """
    import base64
    import email

    payload = gmail_message.get('payload', {})
    headers = {h['name']: h['value'] for h in payload.get('headers', [])}

    # Extract sender information
    from_header = headers.get('From', '')
    # Parse "Name <email@example.com>" format
    import re
    match = re.match(r'(.+?)\s*<(.+?)>', from_header)
    if match:
        sender_name = match.group(1).strip('"')
        sender_email = match.group(2)
    else:
        sender_name = from_header
        sender_email = from_header

    # Extract body
    body_text = ''
    body_html = ''

    def get_body_recursive(parts):
        """Recursively extract body from message parts."""
        nonlocal body_text, body_html

        if 'parts' in parts:
            for part in parts['parts']:
                get_body_recursive(part)
        elif 'body' in parts and 'data' in parts['body']:
            mime_type = parts.get('mimeType', '')
            data = parts['body']['data']
            decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

            if mime_type == 'text/plain':
                body_text += decoded
            elif mime_type == 'text/html':
                body_html += decoded

    get_body_recursive(payload)

    # Parse date
    date_str = headers.get('Date', '')
    sent_at = datetime.utcnow()
    if date_str:
        try:
            from email.utils import parsedate_to_datetime
            sent_at = parsedate_to_datetime(date_str)
        except:
            pass

    return {
        'id': gmail_message['id'],
        'threadId': gmail_message.get('threadId', gmail_message['id']),
        'from': {
            'name': sender_name,
            'email': sender_email
        },
        'to': headers.get('To', ''),
        'subject': headers.get('Subject', '(No subject)'),
        'body_text': body_text or '(No text content)',
        'body_html': body_html or body_text,
        'sent_at': sent_at,
        'labels': gmail_message.get('labelIds', [])
    }


# =============================================================================
# Triage Service - Main Orchestration
# =============================================================================

class TriageService:
    """
    Orchestrates the email processing pipeline.

    This is the central service that coordinates all email triage operations:
    - Syncing emails from Gmail
    - Processing new messages through AI analysis
    - Creating and grouping conversations into objectives
    - Generating proposed actions
    - Auto-executing low-risk actions
    - Managing the review queue
    """

    def __init__(
        self,
        db: AsyncSession,
        gmail_service: GmailService,
        agent_service: AgentService
    ):
        """
        Initialize the triage service.

        Args:
            db: Database session
            gmail_service: Gmail API service for fetching/sending emails
            agent_service: AI agent service for analysis and response generation
        """
        self.db = db
        self.gmail = gmail_service
        self.agent = agent_service
        logger.info("TriageService initialized")

    # =========================================================================
    # Main Email Processing Pipeline
    # =========================================================================

    async def process_new_email(
        self,
        user_id: UUID,
        gmail_message: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Main entry point for processing a new email message.

        Pipeline:
        1. Parse Gmail message into our Message model
        2. Find or create Conversation (by thread_id)
        3. Find or create Objective (group related conversations)
        4. Get conversation context (previous messages)
        5. Run through AI agent for analysis
        6. Generate proposed action
        7. Calculate confidence and risk
        8. Create AgentAction record
        9. Auto-execute if appropriate, otherwise queue for review

        Args:
            user_id: ID of the user who owns this email
            gmail_message: Raw Gmail message dict from Gmail API

        Returns:
            ProcessingResult with action details

        Raises:
            ValueError: If message is malformed or missing required fields
            Exception: If processing fails critically
        """
        start_time = datetime.utcnow()
        logger.info(f"Processing new email for user {user_id}: {gmail_message.get('subject', 'No subject')}")

        try:
            # Step 1: Check for duplicate
            gmail_msg_id = gmail_message.get('id')
            if not gmail_msg_id:
                raise ValueError("Gmail message missing 'id' field")

            existing = await self._check_duplicate_message(gmail_msg_id)
            if existing:
                logger.warning(f"Duplicate message detected: {gmail_msg_id}, skipping")
                # Return existing action if available
                existing_action = await self._get_action_for_conversation(existing.conversation_id)
                if existing_action:
                    return ProcessingResult(
                        action_id=existing_action.id,
                        conversation_id=existing.conversation_id,
                        objective_id=existing.conversation.objective_id,
                        confidence=existing_action.confidence_score * 100,
                        risk_level=existing_action.risk_level,
                        auto_executed=existing_action.status == ActionStatus.APPROVED,
                        action_type=existing_action.action_type
                    )

            # Step 2: Find or create conversation
            conversation = await self._find_or_create_conversation(
                user_id=user_id,
                gmail_thread_id=gmail_message.get('threadId', gmail_msg_id)
            )

            # Step 3: Parse and save message
            message = await self._parse_and_save_message(
                gmail_message=gmail_message,
                conversation_id=conversation.id
            )

            # Step 4: Find or create objective (smart grouping)
            objective = await self.find_or_create_objective(
                user_id=user_id,
                message=message
            )

            # Update conversation's objective if needed
            if conversation.objective_id != objective.id:
                conversation.objective_id = objective.id
                await self.db.commit()

            # Step 5: Get conversation context
            context_messages = await self._get_conversation_context(conversation.id)

            # Step 6: Get user and policies
            user = await self._get_user(user_id)
            policies = await self._get_active_policies(user_id)

            # Step 7: AI Analysis
            logger.info(f"Running AI analysis for message {message.id}")
            analysis = await self.agent.analyze_email(
                message=message,
                conversation_context=context_messages,
                user_email=user.email,
                user_name=user.name
            )

            # Step 8: Generate response draft
            logger.info(f"Generating response draft for message {message.id}")
            draft = await self.agent.generate_response(
                message=message,
                conversation_context=context_messages,
                analysis=analysis,
                user_email=user.email,
                user_name=user.name,
                user_preferences=None
            )

            # Step 9: Assess risk
            logger.info(f"Assessing risk for message {message.id}")
            risk_assessment = await self.agent.assess_risk(
                message=message,
                analysis=analysis,
                policies=policies,
                conversation_context=context_messages
            )

            # Step 10: Calculate confidence
            logger.info(f"Calculating confidence for message {message.id}")

            # Get historical acceptance rate
            historical_rate = await self._get_user_acceptance_rate(user_id)

            confidence = await self.agent.calculate_confidence(
                message=message,
                analysis=analysis,
                draft=draft,
                conversation_context=context_messages,
                user_historical_acceptance_rate=historical_rate
            )

            # Step 11: Evaluate policies
            policy_matches = await self.agent.evaluate_policies(
                message=message,
                analysis=analysis,
                policies=policies
            )

            # Step 12: Determine priority
            priority = self._calculate_priority(
                analysis=analysis,
                risk_level=risk_assessment.risk_level,
                confidence=confidence
            )

            # Step 13: Create AgentAction
            action = AgentAction(
                conversation_id=conversation.id,
                action_type=draft.suggested_action,
                proposed_content=draft.body,
                confidence_score=confidence / 100.0,  # Store as 0-1
                risk_level=risk_assessment.risk_level,
                priority_score=priority,
                status=ActionStatus.PENDING
            )

            self.db.add(action)
            await self.db.commit()
            await self.db.refresh(action)

            logger.info(
                f"Created action {action.id}: type={action.action_type}, "
                f"confidence={confidence:.1f}, risk={risk_assessment.risk_level}"
            )

            # Step 14: Check if should auto-execute
            should_auto_execute = await self.agent.should_auto_execute(
                confidence=confidence,
                risk_level=risk_assessment.risk_level,
                autonomy_level=user.autonomy_level,
                action_type=draft.suggested_action
            )

            auto_executed = False
            if should_auto_execute:
                logger.info(f"Auto-executing action {action.id}")
                try:
                    execution_result = await self.execute_action(
                        action_id=action.id,
                        auto_executed=True
                    )
                    auto_executed = execution_result.success

                    if auto_executed:
                        # Update objective status
                        await self.update_objective_status(objective.id)

                except Exception as e:
                    logger.error(f"Auto-execution failed for action {action.id}: {e}")
                    # Don't fail the whole pipeline, just queue for review
                    auto_executed = False
            else:
                logger.info(
                    f"Action {action.id} requires review: "
                    f"confidence={confidence:.1f}, risk={risk_assessment.risk_level}, "
                    f"autonomy={user.autonomy_level}"
                )
                # Update objective status to waiting on user
                objective.status = ObjectiveStatus.WAITING_ON_YOU
                await self.db.commit()

            # Calculate processing time
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Email processed in {duration:.2f}s: action_id={action.id}")

            return ProcessingResult(
                action_id=action.id,
                conversation_id=conversation.id,
                objective_id=objective.id,
                confidence=confidence,
                risk_level=risk_assessment.risk_level,
                auto_executed=auto_executed,
                action_type=draft.suggested_action
            )

        except Exception as e:
            logger.error(f"Error processing email for user {user_id}: {e}", exc_info=True)
            raise

    # =========================================================================
    # Gmail Sync
    # =========================================================================

    async def sync_user_inbox(
        self,
        user_id: UUID,
        max_messages: int = 50
    ) -> SyncResult:
        """
        Sync emails from Gmail for a user.

        Pipeline:
        1. Get user's Gmail credentials
        2. Fetch new messages since last sync
        3. Process each new message through the pipeline
        4. Update last_sync timestamp
        5. Return sync statistics

        Args:
            user_id: ID of the user to sync
            max_messages: Maximum number of messages to fetch per sync

        Returns:
            SyncResult with sync statistics

        Raises:
            ValueError: If user doesn't have Gmail credentials
            Exception: If sync fails critically
        """
        start_time = datetime.utcnow()
        logger.info(f"Starting inbox sync for user {user_id}")

        new_messages = 0
        processed = 0
        errors = 0
        error_details = []

        try:
            # Get user with credentials
            user = await self._get_user(user_id)

            if not user.gmail_credentials:
                raise ValueError(f"User {user_id} has no Gmail credentials configured")

            # Determine last sync time (sync last 7 days of messages)
            since = datetime.utcnow() - timedelta(days=7)

            # Build Gmail query for recent messages
            query = f"after:{int(since.timestamp())}"

            # Fetch message list from Gmail
            logger.info(f"Fetching messages since {since}")
            result = await self.gmail.get_messages(
                credentials=user.gmail_credentials,
                max_results=max_messages,
                query=query
            )

            message_list = result.get('messages', [])
            new_messages = len(message_list)
            logger.info(f"Fetched {new_messages} new messages")

            # Process each message
            for msg_ref in message_list:
                # Fetch full message details
                gmail_msg_raw = await self.gmail.get_message(
                    credentials=user.gmail_credentials,
                    message_id=msg_ref['id']
                )

                # Parse into our format
                gmail_msg = _parse_gmail_message(gmail_msg_raw)
                try:
                    await self.process_new_email(
                        user_id=user_id,
                        gmail_message=gmail_msg
                    )
                    processed += 1

                    # Add small delay to avoid rate limiting
                    await asyncio.sleep(0.1)

                except Exception as e:
                    errors += 1
                    error_msg = f"Failed to process message {gmail_msg.get('id', 'unknown')}: {str(e)}"
                    logger.error(error_msg)
                    error_details.append(error_msg)

                    # Continue processing other messages
                    continue

            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(
                f"Inbox sync complete for user {user_id}: "
                f"{processed}/{new_messages} processed, {errors} errors, "
                f"{duration:.2f}s"
            )

            return SyncResult(
                new_messages=new_messages,
                processed=processed,
                errors=errors,
                duration_seconds=duration,
                last_sync_time=datetime.utcnow(),
                error_details=error_details
            )

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Inbox sync failed for user {user_id}: {e}", exc_info=True)

            return SyncResult(
                new_messages=new_messages,
                processed=processed,
                errors=errors + 1,
                duration_seconds=duration,
                last_sync_time=datetime.utcnow(),
                error_details=error_details + [str(e)]
            )

    # =========================================================================
    # Action Execution
    # =========================================================================

    async def execute_action(
        self,
        action_id: UUID,
        auto_executed: bool = False
    ) -> ExecutionResult:
        """
        Execute an approved action.

        Pipeline:
        1. Load the AgentAction with relationships
        2. Determine content to send (edited or original)
        3. Based on action_type:
           - send: Use Gmail to send the response
           - draft: Create draft in Gmail
           - file: Archive/label the email
           - schedule: Create calendar event (future)
        4. Update action status to 'executed' or 'approved'
        5. Update conversation/objective status

        Args:
            action_id: ID of the action to execute
            auto_executed: Whether this is an auto-execution (vs manual approval)

        Returns:
            ExecutionResult with execution details

        Raises:
            ValueError: If action not found or invalid
            Exception: If execution fails
        """
        logger.info(f"Executing action {action_id} (auto={auto_executed})")

        try:
            # Load action with all relationships
            query = (
                select(AgentAction)
                .options(
                    joinedload(AgentAction.conversation)
                    .joinedload(Conversation.messages),
                    joinedload(AgentAction.conversation)
                    .joinedload(Conversation.objective)
                )
                .where(AgentAction.id == action_id)
            )

            result = await self.db.execute(query)
            action = result.unique().scalar_one_or_none()

            if not action:
                raise ValueError(f"Action {action_id} not found")

            # Get the message to reply to (latest incoming message)
            reply_to_message = None
            for msg in sorted(action.conversation.messages, key=lambda m: m.sent_at, reverse=True):
                if msg.direction == MessageDirection.INCOMING:
                    reply_to_message = msg
                    break

            if not reply_to_message:
                raise ValueError(f"No incoming message found for conversation {action.conversation_id}")

            # Determine content to send
            content = action.user_edit if action.user_edit else action.proposed_content

            # Execute based on action type
            gmail_message_id = None
            gmail_thread_id = action.conversation.gmail_thread_id

            if action.action_type == ActionType.SEND:
                # Send email via Gmail
                logger.info(f"Sending email for action {action_id}")

                # Get user for credentials
                user = action.conversation.objective.user

                gmail_result = await self.gmail.send_message(
                    credentials=user.gmail_credentials,
                    to=reply_to_message.sender_email,
                    subject=f"Re: {reply_to_message.subject}",
                    body=content,
                    thread_id=gmail_thread_id,
                    message_type='html' if '<html>' in content.lower() else 'plain'
                )

                gmail_message_id = gmail_result.get('id')
                gmail_thread_id = gmail_result.get('threadId')

                # Save sent message to our database
                sent_message = Message(
                    conversation_id=action.conversation_id,
                    gmail_message_id=gmail_message_id,
                    sender_email=action.conversation.objective.user.email,
                    sender_name=action.conversation.objective.user.name,
                    subject=f"Re: {reply_to_message.subject}",
                    body_text=content,
                    body_html=content,
                    direction=MessageDirection.OUTGOING,
                    sent_at=datetime.utcnow()
                )

                self.db.add(sent_message)

            elif action.action_type == ActionType.DRAFT:
                # Create draft in Gmail
                logger.info(f"Creating draft for action {action_id}")

                # Get user for credentials
                user = action.conversation.objective.user

                gmail_result = await self.gmail.create_draft(
                    credentials=user.gmail_credentials,
                    to=reply_to_message.sender_email,
                    subject=f"Re: {reply_to_message.subject}",
                    body=content,
                    thread_id=gmail_thread_id,
                    message_type='html' if '<html>' in content.lower() else 'plain'
                )

                gmail_message_id = gmail_result.get('id')

            elif action.action_type == ActionType.FILE:
                # Archive/label the email
                logger.info(f"Filing email for action {action_id}")

                # Get user for credentials
                user = action.conversation.objective.user

                # Archive by removing from inbox
                await self.gmail.modify_labels(
                    credentials=user.gmail_credentials,
                    message_id=reply_to_message.gmail_message_id,
                    remove_labels=['INBOX']
                )

            elif action.action_type == ActionType.SCHEDULE:
                # Calendar integration - mark as scheduled, actual calendar event pending
                logger.info(f"Action {action_id} scheduled (calendar integration pending)")

            else:
                raise ValueError(f"Unknown action type: {action.action_type}")

            # Update action status
            if auto_executed:
                action.status = ActionStatus.APPROVED
                action.approved_at = datetime.utcnow()

            action.resolved_at = datetime.utcnow()

            # Update objective status
            objective = action.conversation.objective
            if action.action_type in [ActionType.SEND, ActionType.DRAFT]:
                objective.status = ObjectiveStatus.WAITING_ON_OTHERS
            else:
                objective.status = ObjectiveStatus.HANDLED

            await self.db.commit()

            logger.info(
                f"Action {action_id} executed successfully: "
                f"type={action.action_type}, gmail_msg_id={gmail_message_id}"
            )

            return ExecutionResult(
                success=True,
                action_id=action_id,
                gmail_message_id=gmail_message_id,
                gmail_thread_id=gmail_thread_id,
                executed_at=datetime.utcnow()
            )

        except Exception as e:
            logger.error(f"Failed to execute action {action_id}: {e}", exc_info=True)

            return ExecutionResult(
                success=False,
                action_id=action_id,
                error=str(e),
                executed_at=datetime.utcnow()
            )

    # =========================================================================
    # Smart Objective Grouping
    # =========================================================================

    async def find_or_create_objective(
        self,
        user_id: UUID,
        message: Message
    ) -> Objective:
        """
        Smart objective grouping using AI and heuristics.

        Logic:
        1. Same thread_id = same conversation = same objective (always)
        2. Check for recent objectives with similar:
           - Subject lines (fuzzy match)
           - Participants (same sender/recipients)
           - Timeframe (within 7 days)
        3. Use AI to determine if message belongs to existing objective
        4. Create new objective if no match

        Args:
            user_id: ID of the user
            message: The message to group

        Returns:
            Objective that this message belongs to
        """
        logger.info(f"Finding or creating objective for message {message.id}")

        try:
            # Check if conversation already has an objective
            if message.conversation and message.conversation.objective_id:
                objective = message.conversation.objective
                logger.info(f"Using existing objective {objective.id} from conversation")
                return objective

            # Look for recent objectives (last 7 days) for this user
            time_threshold = datetime.utcnow() - timedelta(days=7)

            query = (
                select(Objective)
                .where(
                    and_(
                        Objective.user_id == user_id,
                        Objective.created_at >= time_threshold,
                        Objective.status != ObjectiveStatus.HANDLED,
                        Objective.status != ObjectiveStatus.MUTED
                    )
                )
                .options(selectinload(Objective.conversations))
                .order_by(desc(Objective.updated_at))
                .limit(10)  # Check last 10 active objectives
            )

            result = await self.db.execute(query)
            recent_objectives = result.scalars().all()

            # Check for matches
            best_match = None
            best_score = 0.0

            for objective in recent_objectives:
                score = await self._calculate_objective_match_score(
                    objective=objective,
                    message=message
                )

                if score > best_score:
                    best_score = score
                    best_match = objective

            # Use match if confidence is high enough (>0.7)
            if best_match and best_score > 0.7:
                logger.info(
                    f"Matched message to existing objective {best_match.id} "
                    f"(score={best_score:.2f})"
                )
                return best_match

            # Create new objective
            logger.info(f"Creating new objective for message {message.id}")

            # Generate title from subject
            title = message.subject[:200] if message.subject else f"Email from {message.sender_name}"

            objective = Objective(
                user_id=user_id,
                title=title,
                status=ObjectiveStatus.WAITING_ON_YOU
            )

            self.db.add(objective)
            await self.db.commit()
            await self.db.refresh(objective)

            logger.info(f"Created new objective {objective.id}: {title}")

            return objective

        except Exception as e:
            logger.error(f"Error in find_or_create_objective: {e}", exc_info=True)
            raise

    async def update_objective_status(self, objective_id: UUID) -> None:
        """
        Update objective status based on conversation states.

        Rules:
        - waiting_on_you: has pending actions
        - waiting_on_others: sent and awaiting reply
        - handled: all actions complete
        - scheduled: has scheduled actions

        Args:
            objective_id: ID of the objective to update
        """
        logger.info(f"Updating status for objective {objective_id}")

        try:
            # Load objective with conversations and actions
            query = (
                select(Objective)
                .options(
                    selectinload(Objective.conversations)
                    .selectinload(Conversation.agent_actions)
                )
                .where(Objective.id == objective_id)
            )

            result = await self.db.execute(query)
            objective = result.scalar_one_or_none()

            if not objective:
                logger.warning(f"Objective {objective_id} not found")
                return

            # Check all actions across all conversations
            has_pending = False
            has_executed = False
            all_handled = True

            for conversation in objective.conversations:
                for action in conversation.agent_actions:
                    if action.status == ActionStatus.PENDING:
                        has_pending = True
                        all_handled = False
                    elif action.status in [ActionStatus.APPROVED, ActionStatus.EDITED]:
                        has_executed = True
                        if action.action_type in [ActionType.SEND, ActionType.DRAFT]:
                            # Waiting for response
                            all_handled = False

            # Determine new status
            if has_pending:
                objective.status = ObjectiveStatus.WAITING_ON_YOU
            elif has_executed and not all_handled:
                objective.status = ObjectiveStatus.WAITING_ON_OTHERS
            elif all_handled:
                objective.status = ObjectiveStatus.HANDLED

            objective.updated_at = datetime.utcnow()

            await self.db.commit()

            logger.info(f"Updated objective {objective_id} status to {objective.status}")

        except Exception as e:
            logger.error(f"Error updating objective status: {e}", exc_info=True)
            raise

    # =========================================================================
    # Helper Methods
    # =========================================================================

    async def _check_duplicate_message(self, gmail_message_id: str) -> Optional[Message]:
        """Check if message already exists in database."""
        query = (
            select(Message)
            .options(selectinload(Message.conversation))
            .where(Message.gmail_message_id == gmail_message_id)
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _find_or_create_conversation(
        self,
        user_id: UUID,
        gmail_thread_id: str
    ) -> Conversation:
        """Find existing conversation or create new one."""
        # Try to find existing conversation by thread ID
        query = (
            select(Conversation)
            .join(Conversation.objective)
            .where(
                and_(
                    Conversation.gmail_thread_id == gmail_thread_id,
                    Objective.user_id == user_id
                )
            )
            .options(selectinload(Conversation.messages))
        )

        result = await self.db.execute(query)
        conversation = result.scalar_one_or_none()

        if conversation:
            return conversation

        # Create temporary objective (will be replaced during processing)
        temp_objective = Objective(
            user_id=user_id,
            title="Processing...",
            status=ObjectiveStatus.WAITING_ON_YOU
        )
        self.db.add(temp_objective)
        await self.db.flush()

        # Create new conversation
        conversation = Conversation(
            objective_id=temp_objective.id,
            gmail_thread_id=gmail_thread_id,
            participants=[]
        )

        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)

        return conversation

    async def _parse_and_save_message(
        self,
        gmail_message: Dict[str, Any],
        conversation_id: UUID
    ) -> Message:
        """Parse Gmail message dict and save to database."""
        from_email = gmail_message.get('from', {})

        message = Message(
            conversation_id=conversation_id,
            gmail_message_id=gmail_message['id'],
            sender_email=from_email.get('email', 'unknown@example.com'),
            sender_name=from_email.get('name', 'Unknown'),
            subject=gmail_message.get('subject', '(No subject)'),
            body_text=gmail_message.get('body_text', ''),
            body_html=gmail_message.get('body_html', ''),
            direction=MessageDirection.INCOMING,
            sent_at=gmail_message.get('sent_at', datetime.utcnow())
        )

        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)

        # Update conversation participants
        conversation = await self._get_conversation(conversation_id)
        if message.sender_email not in conversation.participants:
            conversation.participants.append(message.sender_email)
            await self.db.commit()

        return message

    async def _get_conversation_context(
        self,
        conversation_id: UUID,
        limit: int = 10
    ) -> List[Message]:
        """Get recent messages in the conversation for context."""
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.sent_at.desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        messages = result.scalars().all()

        # Return in chronological order
        return list(reversed(messages))

    async def _get_user(self, user_id: UUID) -> User:
        """Get user by ID."""
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError(f"User {user_id} not found")

        return user

    async def _get_active_policies(self, user_id: UUID) -> List[Policy]:
        """Get active policies for user."""
        query = (
            select(Policy)
            .where(
                and_(
                    Policy.user_id == user_id,
                    Policy.is_active == True
                )
            )
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def _get_conversation(self, conversation_id: UUID) -> Conversation:
        """Get conversation by ID."""
        query = select(Conversation).where(Conversation.id == conversation_id)
        result = await self.db.execute(query)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")

        return conversation

    async def _get_action_for_conversation(
        self,
        conversation_id: UUID
    ) -> Optional[AgentAction]:
        """Get most recent action for conversation."""
        query = (
            select(AgentAction)
            .where(AgentAction.conversation_id == conversation_id)
            .order_by(AgentAction.created_at.desc())
            .limit(1)
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_user_acceptance_rate(self, user_id: UUID) -> Optional[float]:
        """Calculate user's historical acceptance rate for confidence scoring."""
        # Query for approved/edited vs rejected actions
        approved_query = (
            select(func.count(AgentAction.id))
            .join(AgentAction.conversation)
            .join(Conversation.objective)
            .where(
                and_(
                    Objective.user_id == user_id,
                    or_(
                        AgentAction.status == ActionStatus.APPROVED,
                        AgentAction.status == ActionStatus.EDITED
                    )
                )
            )
        )

        total_query = (
            select(func.count(AgentAction.id))
            .join(AgentAction.conversation)
            .join(Conversation.objective)
            .where(
                and_(
                    Objective.user_id == user_id,
                    AgentAction.status != ActionStatus.PENDING
                )
            )
        )

        approved_result = await self.db.execute(approved_query)
        approved = approved_result.scalar() or 0

        total_result = await self.db.execute(total_query)
        total = total_result.scalar() or 0

        if total == 0:
            return None

        return approved / total

    def _calculate_priority(
        self,
        analysis: EmailAnalysis,
        risk_level: RiskLevel,
        confidence: float
    ) -> int:
        """
        Calculate priority score (0-100) for action.

        Factors:
        - Urgency (0-40 points)
        - Risk level (0-30 points)
        - Requires immediate response (0-20 points)
        - Confidence (0-10 points, inverted - lower confidence = higher priority)
        """
        priority = 50  # Base priority

        # Urgency
        urgency_map = {
            'critical': 40,
            'high': 30,
            'medium': 15,
            'low': 0
        }
        priority += urgency_map.get(analysis.urgency, 15)

        # Risk level (high risk = high priority for review)
        risk_map = {
            RiskLevel.HIGH: 30,
            RiskLevel.MEDIUM: 15,
            RiskLevel.LOW: 0
        }
        priority += risk_map.get(risk_level, 0)

        # Requires immediate response
        if analysis.requires_immediate_response:
            priority += 20

        # Lower confidence = higher priority for review
        if confidence < 60:
            priority += 10

        return min(100, max(0, priority))

    async def _calculate_objective_match_score(
        self,
        objective: Objective,
        message: Message
    ) -> float:
        """
        Calculate how well a message matches an existing objective.

        Factors:
        - Subject similarity (0-0.4)
        - Participant overlap (0-0.3)
        - Timeframe recency (0-0.3)

        Returns:
            Score from 0-1
        """
        score = 0.0

        # Subject similarity (simple keyword match)
        if objective.conversations:
            # Get subjects from objective's conversations
            objective_subjects = []
            for conv in objective.conversations:
                if conv.messages:
                    for msg in conv.messages[:1]:  # First message
                        objective_subjects.append(msg.subject.lower())

            message_subject = message.subject.lower()

            # Simple keyword overlap
            message_words = set(message_subject.split())
            max_overlap = 0.0

            for obj_subject in objective_subjects:
                obj_words = set(obj_subject.split())

                if obj_words and message_words:
                    overlap = len(message_words & obj_words) / len(message_words | obj_words)
                    max_overlap = max(max_overlap, overlap)

            score += max_overlap * 0.4

        # Participant overlap
        if objective.conversations:
            objective_participants = set()
            for conv in objective.conversations:
                objective_participants.update(conv.participants)

            if message.sender_email in objective_participants:
                score += 0.3

        # Recency (objectives updated recently are more likely matches)
        time_diff = (datetime.utcnow() - objective.updated_at).total_seconds()
        recency_score = max(0, 1 - (time_diff / (7 * 24 * 3600)))  # Decay over 7 days
        score += recency_score * 0.3

        return min(1.0, score)
