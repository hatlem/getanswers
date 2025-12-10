"""Example usage of the AgentService for email processing.

This file demonstrates how to use the Claude AI Agent service in your application.
"""

from datetime import datetime
from uuid import uuid4

from .agent import AgentService
from ..models.message import Message, MessageDirection
from ..models.policy import Policy
from ..models.user import AutonomyLevel
from ..models.agent_action import ActionType, RiskLevel
from ..core.config import settings


async def process_incoming_email_example():
    """Complete example of processing an incoming email with the agent service."""

    # Initialize the agent service
    agent = AgentService(api_key=settings.ANTHROPIC_API_KEY)

    # Mock user data
    user_email = "sarah.chen@company.com"
    user_name = "Sarah Chen"
    user_autonomy = AutonomyLevel.MEDIUM

    # Mock incoming email
    incoming_message = Message(
        id=uuid4(),
        conversation_id=uuid4(),
        gmail_message_id="msg_12345",
        sender_email="john.doe@client.com",
        sender_name="John Doe",
        subject="Q4 Budget Review - Need Your Input",
        body_text="""Hi Sarah,

Hope you're doing well. I wanted to reach out regarding the Q4 budget review meeting scheduled for next week.

Could you please send over:
1. The marketing spend breakdown for Q3
2. Projected expenses for the holiday campaign
3. Any budget adjustments you're planning for Q4

It would be great to have this by EOD Thursday so we can prepare the deck for the exec team.

Let me know if you have any questions!

Thanks,
John""",
        body_html="<html>...</html>",
        direction=MessageDirection.INCOMING,
        sent_at=datetime.utcnow(),
        created_at=datetime.utcnow()
    )

    # Mock conversation context (previous emails in thread)
    conversation_context = [
        Message(
            id=uuid4(),
            conversation_id=incoming_message.conversation_id,
            gmail_message_id="msg_12340",
            sender_email=user_email,
            sender_name=user_name,
            subject="Re: Q4 Planning",
            body_text="Thanks for the update. Let's schedule a review meeting to discuss the budget.",
            body_html="<html>...</html>",
            direction=MessageDirection.OUTGOING,
            sent_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
    ]

    # Mock user policies
    user_policies = [
        Policy(
            id=uuid4(),
            user_id=uuid4(),
            name="Auto-respond to budget requests",
            description="Automatically acknowledge budget-related requests and set expectations",
            rules={
                "conditions": [
                    {"field": "subject", "contains": "budget"},
                    {"field": "category", "equals": "request"}
                ],
                "actions": [
                    {"type": "draft", "template": "acknowledge_and_timeline"}
                ]
            },
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    ]

    # Step 1: Analyze the email
    print("=" * 80)
    print("STEP 1: Analyzing email...")
    print("=" * 80)

    analysis = await agent.analyze_email(
        message=incoming_message,
        conversation_context=conversation_context,
        user_email=user_email,
        user_name=user_name
    )

    print(f"\nIntent: {analysis.intent.primary}")
    print(f"Description: {analysis.intent.description}")
    print(f"Sentiment: {analysis.sentiment}")
    print(f"Urgency: {analysis.urgency}")
    print(f"Category: {analysis.category}")
    print(f"Actionable: {analysis.is_actionable}")
    print(f"Sender relationship: {analysis.sender_relationship}")
    print(f"\nKey Points:")
    for point in analysis.key_points:
        print(f"  - {point}")

    # Step 2: Generate response
    print("\n" + "=" * 80)
    print("STEP 2: Generating response...")
    print("=" * 80)

    user_preferences = {
        "communication_tone": "professional-friendly",
        "response_length": "concise"
    }

    draft = await agent.generate_response(
        message=incoming_message,
        conversation_context=conversation_context,
        analysis=analysis,
        user_email=user_email,
        user_name=user_name,
        user_preferences=user_preferences
    )

    print(f"\nSubject: {draft.subject}")
    print(f"\nBody:\n{draft.body}")
    print(f"\nSuggested action: {draft.suggested_action}")
    print(f"\nReasoning: {draft.reasoning}")

    # Step 3: Assess risk
    print("\n" + "=" * 80)
    print("STEP 3: Assessing risk...")
    print("=" * 80)

    risk_assessment = await agent.assess_risk(
        message=incoming_message,
        analysis=analysis,
        policies=user_policies,
        conversation_context=conversation_context
    )

    print(f"\nRisk level: {risk_assessment.risk_level}")
    print(f"Financial implications: {risk_assessment.has_financial_implications}")
    print(f"Legal implications: {risk_assessment.has_legal_implications}")
    print(f"\nRisk factors:")
    for factor in risk_assessment.risk_factors:
        print(f"  - {factor}")

    # Step 4: Evaluate policies
    print("\n" + "=" * 80)
    print("STEP 4: Evaluating policies...")
    print("=" * 80)

    policy_matches = await agent.evaluate_policies(
        message=incoming_message,
        analysis=analysis,
        policies=user_policies
    )

    if policy_matches:
        for match in policy_matches:
            print(f"\nMatched policy: {match.policy_name}")
            print(f"Rule: {match.matched_rule}")
            print(f"Confidence: {match.confidence:.2%}")
            print(f"Reasoning: {match.reasoning}")
    else:
        print("\nNo policies matched this email.")

    # Step 5: Calculate confidence
    print("\n" + "=" * 80)
    print("STEP 5: Calculating confidence...")
    print("=" * 80)

    confidence = await agent.calculate_confidence(
        message=incoming_message,
        analysis=analysis,
        draft=draft,
        conversation_context=conversation_context,
        user_historical_acceptance_rate=0.85  # 85% historical acceptance
    )

    print(f"\nConfidence score: {confidence:.1f}/100")

    # Step 6: Determine auto-execution
    print("\n" + "=" * 80)
    print("STEP 6: Auto-execution decision...")
    print("=" * 80)

    should_auto_execute = await agent.should_auto_execute(
        confidence=confidence,
        risk_level=risk_assessment.risk_level,
        autonomy_level=user_autonomy,
        action_type=draft.suggested_action
    )

    print(f"\nAuto-execute: {should_auto_execute}")
    print(f"Autonomy level: {user_autonomy}")
    print(f"Action type: {draft.suggested_action}")

    if should_auto_execute:
        print("\nAction: Email response will be sent automatically")
    else:
        print("\nAction: Email draft will be presented to user for review")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"""
Email from: {incoming_message.sender_name}
Intent: {analysis.intent.primary}
Risk: {risk_assessment.risk_level}
Confidence: {confidence:.1f}/100
Auto-execute: {should_auto_execute}

Next steps:
{"- Send response automatically" if should_auto_execute else "- Present draft to user for review"}
- Log action in agent_actions table
- Update conversation status
    """)


async def analyze_urgent_email_example():
    """Example of handling an urgent email."""

    agent = AgentService(api_key=settings.ANTHROPIC_API_KEY)

    urgent_message = Message(
        id=uuid4(),
        conversation_id=uuid4(),
        gmail_message_id="msg_urgent_001",
        sender_email="ceo@company.com",
        sender_name="Amanda Stevens",
        subject="URGENT: Server outage affecting customer orders",
        body_text="""Team,

We have a critical situation. Our payment processing server went down 15 minutes ago and customers are unable to complete orders.

I need an immediate status update on:
1. What caused the outage
2. Current impact assessment
3. ETA for resolution
4. Plan to prevent this in the future

Please respond ASAP - we're losing revenue every minute this is down.

Amanda""",
        body_html="<html>...</html>",
        direction=MessageDirection.INCOMING,
        sent_at=datetime.utcnow(),
        created_at=datetime.utcnow()
    )

    analysis = await agent.analyze_email(
        message=urgent_message,
        conversation_context=[],
        user_email="tech.lead@company.com",
        user_name="Tech Lead"
    )

    print("Urgent Email Analysis:")
    print(f"Urgency: {analysis.urgency}")
    print(f"Requires immediate response: {analysis.requires_immediate_response}")
    print(f"Sender relationship: {analysis.sender_relationship}")
    print(f"Category: {analysis.category}")


async def detect_spam_example():
    """Example of spam detection."""

    agent = AgentService(api_key=settings.ANTHROPIC_API_KEY)

    suspicious_message = Message(
        id=uuid4(),
        conversation_id=uuid4(),
        gmail_message_id="msg_spam_001",
        sender_email="winner@lottery-notifications.biz",
        sender_name="Prize Committee",
        subject="CONGRATULATIONS! You've won $1,000,000!!!",
        body_text="""Dear Lucky Winner,

You have been selected to receive $1,000,000 USD in our international lottery!

To claim your prize, please send your:
- Full name
- Bank account details
- Social security number
- Copy of passport

ACT NOW! This offer expires in 24 hours!

Click here: http://totally-legit-site.xyz

Best regards,
International Prize Committee""",
        body_html="<html>...</html>",
        direction=MessageDirection.INCOMING,
        sent_at=datetime.utcnow(),
        created_at=datetime.utcnow()
    )

    analysis = await agent.analyze_email(
        message=suspicious_message,
        conversation_context=[],
        user_email="user@company.com",
        user_name="User"
    )

    print("Spam Detection:")
    print(f"Is likely spam: {analysis.is_likely_spam}")
    print(f"Sender relationship: {analysis.sender_relationship}")

    risk_assessment = await agent.assess_risk(
        message=suspicious_message,
        analysis=analysis,
        policies=[],
        conversation_context=[]
    )

    print(f"Risk level: {risk_assessment.risk_level}")
    print("Risk factors:")
    for factor in risk_assessment.risk_factors:
        print(f"  - {factor}")


if __name__ == "__main__":
    import asyncio

    print("Running agent service examples...\n")

    # Run examples
    asyncio.run(process_incoming_email_example())
    print("\n\n")
    asyncio.run(analyze_urgent_email_example())
    print("\n\n")
    asyncio.run(detect_spam_example())
