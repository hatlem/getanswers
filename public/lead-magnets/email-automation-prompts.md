# Email Automation Prompt Library
## 100+ Production-Ready Prompts for AI Email Triage & Response

Transform your inbox from chaos to control with these battle-tested prompts for email automation.

---

## Table of Contents
1. [Classification Prompts](#classification-prompts)
2. [Priority Scoring Prompts](#priority-scoring-prompts)
3. [Intent Detection Prompts](#intent-detection-prompts)
4. [Auto-Response Templates](#auto-response-templates)
5. [Escalation Decision Trees](#escalation-decision-trees)
6. [Sentiment Analysis Prompts](#sentiment-analysis-prompts)
7. [Entity Extraction Prompts](#entity-extraction-prompts)
8. [Routing Rules](#routing-rules)
9. [Follow-up Generation](#follow-up-generation)
10. [Summary Generation](#summary-generation)

---

## Classification Prompts

### CL-001: Master Email Classifier
```
Analyze the following email and classify it into ONE primary category.

CATEGORIES:
- URGENT_SUPPORT: Critical issues, outages, blocking problems
- ROUTINE_SUPPORT: General help requests, how-to questions
- SALES_INQUIRY: Pricing, demo requests, product questions from prospects
- BILLING: Invoices, payment issues, refund requests
- COMPLAINT: Negative feedback, dissatisfaction
- FEEDBACK: Suggestions, positive reviews, feature requests
- SPAM: Promotional, phishing, irrelevant
- ADMINISTRATIVE: Account changes, access requests
- PARTNERSHIP: Business proposals, collaboration requests
- INTERNAL: From team members, system notifications

EMAIL:
{{email_content}}

Respond with JSON:
{
  "category": "CATEGORY_NAME",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}
```

### CL-002: Support Ticket Classifier
```
Classify this support email into a specific issue type.

ISSUE TYPES:
- LOGIN_ACCESS: Password reset, account lockout, authentication
- FEATURE_QUESTION: How to use features, capabilities
- BUG_REPORT: Something not working as expected
- INTEGRATION: API, third-party connections, webhooks
- PERFORMANCE: Slow loading, timeouts, errors
- DATA_ISSUE: Missing data, incorrect data, exports
- BILLING_SUPPORT: Subscription, charges, invoices
- ACCOUNT_CHANGES: Upgrades, downgrades, cancellation
- SECURITY: Suspicious activity, breach concerns
- OTHER: Doesn't fit other categories

EMAIL:
{{email_content}}

Output:
{
  "issue_type": "TYPE",
  "sub_category": "specific aspect if applicable",
  "product_area": "which product/feature",
  "confidence": 0.0-1.0
}
```

### CL-003: Sales Lead Classifier
```
Analyze this email for sales qualification.

LEAD TYPES:
- HOT: Ready to buy, asking for pricing/contract
- WARM: Interested, researching, comparing options
- COLD: Early research, general inquiry
- EXISTING_CUSTOMER: Current customer with question
- PARTNER_PROSPECT: Potential partnership/reseller
- NOT_A_LEAD: Spam, job seeker, vendor pitch

SIGNALS TO DETECT:
- Budget mentions
- Timeline indicators
- Decision-maker language
- Competitor mentions
- Pain point descriptions

EMAIL:
{{email_content}}

Output:
{
  "lead_type": "TYPE",
  "buying_signals": ["signal1", "signal2"],
  "pain_points": ["pain1", "pain2"],
  "timeline": "immediate/30_days/90_days/unknown",
  "company_size_indicators": "small/medium/enterprise/unknown",
  "next_action": "suggested action"
}
```

### CL-004: Multi-Intent Email Classifier
```
Emails often contain multiple intents. Identify ALL intents in this email.

POSSIBLE INTENTS:
- ASK_QUESTION: Seeking information
- REPORT_PROBLEM: Something is wrong
- REQUEST_ACTION: Wants something done
- PROVIDE_INFORMATION: Sharing data/context
- EXPRESS_EMOTION: Frustration, appreciation, etc.
- SCHEDULE_MEETING: Wants to set up a call
- FOLLOW_UP: Checking on previous request
- CANCEL_SERVICE: Wants to end subscription
- UPGRADE_REQUEST: Wants more features
- NEGOTIATE: Discussing terms/pricing

EMAIL:
{{email_content}}

Output:
{
  "primary_intent": "MAIN_INTENT",
  "secondary_intents": ["INTENT1", "INTENT2"],
  "action_items": ["specific action needed"],
  "questions_asked": ["question1", "question2"],
  "response_urgency": "immediate/today/week/low"
}
```

### CL-005: Language & Tone Classifier
```
Analyze the language characteristics of this email.

DETECT:
1. Language: English, Spanish, French, German, etc.
2. Formality: Formal, Semi-formal, Casual, Very casual
3. Technical level: Non-technical, Some technical, Very technical
4. Emotional tone: Neutral, Positive, Negative, Urgent, Frustrated

EMAIL:
{{email_content}}

Output:
{
  "language": "language_code",
  "formality": "level",
  "technical_level": "level",
  "emotional_tone": "primary_tone",
  "suggested_response_style": "how to match their style"
}
```

---

## Priority Scoring Prompts

### PR-001: Priority Score Calculator
```
Calculate a priority score (1-10) for this email based on multiple factors.

SCORING FACTORS:
- Urgency indicators (+2): "urgent", "ASAP", "emergency", "critical"
- Revenue impact (+2): From paying customer, mentions renewal/churn
- Executive sender (+2): C-level, VP, Director titles
- SLA breach risk (+1): Mentions deadlines, contracts
- Repeat contact (+1): "following up", "again", "still waiting"
- Emotional intensity (+1): Frustration, disappointment
- Simple question (-1): Easy to answer, FAQ topic
- Low-value indicators (-1): Free tier, trial user

EMAIL:
{{email_content}}

SENDER INFO:
{{sender_name}}, {{sender_company}}, {{account_tier}}

Output:
{
  "priority_score": 1-10,
  "factors_applied": ["+2: urgency", "-1: simple question"],
  "recommended_sla": "1_hour/4_hours/24_hours/48_hours",
  "escalate": true/false,
  "reasoning": "why this score"
}
```

### PR-002: Business Impact Scorer
```
Evaluate the potential business impact of this email.

IMPACT DIMENSIONS:
- REVENUE: Could affect revenue (churn, upsell, new deal)
- REPUTATION: Could affect brand/public perception
- LEGAL: Could have legal/compliance implications
- OPERATIONAL: Could affect business operations
- NONE: Routine with no significant impact

EMAIL:
{{email_content}}

ACCOUNT DATA:
- Account Value: {{mrr}}
- Account Age: {{months}}
- Health Score: {{health}}

Output:
{
  "impact_level": "CRITICAL/HIGH/MEDIUM/LOW/NONE",
  "impact_types": ["REVENUE", "REPUTATION"],
  "risk_description": "what could go wrong",
  "opportunity_description": "potential upside",
  "recommended_owner": "team/role to handle",
  "executive_notification": true/false
}
```

### PR-003: Time-Sensitivity Detector
```
Determine how time-sensitive this email is.

TIME INDICATORS:
- IMMEDIATE: System down, blocking issue, explicit deadline today
- URGENT: Needs response within hours, important deadline
- STANDARD: Normal business timeframe (24-48 hours)
- LOW: Informational, no deadline, can wait

DETECT:
- Explicit deadlines ("by Friday", "end of day")
- Implicit urgency ("waiting to proceed", "blocking our launch")
- Business cycle timing ("before quarter end", "month close")
- Event-driven ("conference tomorrow", "meeting in 2 hours")

EMAIL:
{{email_content}}

Output:
{
  "time_sensitivity": "IMMEDIATE/URGENT/STANDARD/LOW",
  "deadline_detected": "specific date/time or null",
  "blocking_indicator": true/false,
  "response_window": "recommended timeframe",
  "auto_reminder": "when to follow up if no response"
}
```

### PR-004: Customer Value Scorer
```
Score this email based on customer value signals.

VALUE SIGNALS:
- Account tier mentions (Enterprise, Pro, etc.)
- Company name recognition
- Multiple users/seats mentioned
- Long-term customer indicators
- Growth potential indicators
- Referral/advocacy mentions

EMAIL:
{{email_content}}

Output:
{
  "estimated_value_tier": "ENTERPRISE/MID-MARKET/SMB/INDIVIDUAL",
  "value_signals_found": ["signal1", "signal2"],
  "expansion_potential": true/false,
  "churn_risk_indicators": ["indicator1"],
  "recommended_treatment": "white_glove/standard/self_serve"
}
```

### PR-005: Queue Position Optimizer
```
Given multiple emails, determine optimal processing order.

Consider:
- Priority scores
- Time sensitivity
- Customer value
- Response complexity (quick wins first)
- Dependencies (some may need info before responding)

EMAILS:
{{email_list_with_metadata}}

Output ordered list:
[
  {
    "email_id": "id",
    "position": 1,
    "reasoning": "why first",
    "estimated_handle_time": "minutes"
  },
  ...
]
```

---

## Intent Detection Prompts

### IN-001: Question Extractor
```
Extract all questions from this email, both explicit and implicit.

QUESTION TYPES:
- EXPLICIT: Direct questions with question marks
- IMPLICIT: Statements that require answers ("I need to know...")
- CLARIFICATION: Questions about previous communication
- RHETORICAL: Not requiring actual answer

EMAIL:
{{email_content}}

Output:
{
  "questions": [
    {
      "text": "exact question text",
      "type": "EXPLICIT/IMPLICIT/CLARIFICATION/RHETORICAL",
      "topic": "what the question is about",
      "answer_complexity": "simple/moderate/complex",
      "can_auto_answer": true/false
    }
  ],
  "total_questions": number,
  "main_question": "the primary thing they want answered"
}
```

### IN-002: Action Request Extractor
```
Identify all action requests in this email.

ACTION TYPES:
- PROVIDE_INFO: Send documentation, explain something
- MAKE_CHANGE: Update settings, modify account
- FIX_ISSUE: Resolve a problem
- CONNECT_PERSON: Introduction, transfer, meeting
- PROCESS_REQUEST: Refund, upgrade, cancellation
- CREATE_SOMETHING: New account, new feature, new report

EMAIL:
{{email_content}}

Output:
{
  "actions_requested": [
    {
      "action": "description of what they want",
      "action_type": "TYPE",
      "specificity": "clear/vague",
      "can_self_serve": true/false,
      "requires_approval": true/false,
      "estimated_effort": "minutes"
    }
  ],
  "primary_action": "the main thing they want done",
  "dependencies": "what's needed before action can be taken"
}
```

### IN-003: Complaint Detector
```
Analyze this email for complaint signals.

COMPLAINT INDICATORS:
- Direct complaints
- Frustration expressions
- Negative comparisons
- Threat signals (cancel, lawyer, public)
- Sarcasm or passive aggression

SEVERITY LEVELS:
- SEVERE: Legal threats, public exposure threats, executive escalation
- HIGH: Multiple issues, repeated problems, strong language
- MEDIUM: Single issue, moderate frustration
- LOW: Minor inconvenience, constructive criticism
- NONE: Not a complaint

EMAIL:
{{email_content}}

Output:
{
  "is_complaint": true/false,
  "severity": "SEVERITY_LEVEL",
  "complaint_subjects": ["what they're complaining about"],
  "specific_grievances": ["detailed issues"],
  "desired_resolution": "what they want",
  "threat_indicators": ["any threats detected"],
  "de_escalation_priority": true/false,
  "suggested_approach": "how to respond"
}
```

### IN-004: Meeting Request Detector
```
Detect if this email contains a meeting request.

MEETING SIGNALS:
- Direct meeting requests ("Can we schedule...")
- Availability questions ("Are you free...")
- Calendar-related language ("Let's find a time...")
- Call/video/coffee mentions

EMAIL:
{{email_content}}

Output:
{
  "meeting_requested": true/false,
  "meeting_type": "video/phone/in_person/unspecified",
  "proposed_times": ["any times mentioned"],
  "duration_hint": "if mentioned",
  "meeting_purpose": "what they want to discuss",
  "participants_mentioned": ["other people to include"],
  "scheduling_action": "send_calendar/request_availability/confirm_time"
}
```

### IN-005: Churn Risk Detector
```
Analyze this email for churn risk signals.

CHURN SIGNALS:
- Cancellation mentions
- Competitor mentions
- Dissatisfaction with value
- Usage decrease mentions
- Contract end approaching
- "Last chance" language
- Payment issues

EMAIL:
{{email_content}}

ACCOUNT DATA:
{{account_info}}

Output:
{
  "churn_risk": "HIGH/MEDIUM/LOW/NONE",
  "churn_signals": ["signal1", "signal2"],
  "churn_type": "IMMINENT/CONSIDERING/EXPLORING/NONE",
  "save_opportunity": true/false,
  "intervention_urgency": "immediate/soon/proactive",
  "recommended_action": "specific retention action",
  "escalate_to_csm": true/false
}
```

---

## Auto-Response Templates

### AR-001: Acknowledgment Response Generator
```
Generate an acknowledgment response for this email.

REQUIREMENTS:
- Confirm receipt
- Set expectation for response time
- Provide immediate value if possible
- Match sender's tone

EMAIL:
{{email_content}}

CONTEXT:
- SLA: {{response_sla}}
- Business hours: {{hours}}
- Self-serve resources: {{resources}}

Generate response that:
1. Acknowledges their specific issue/question
2. Sets realistic timeline
3. Provides relevant self-serve option if applicable
4. Sounds human, not robotic
```

### AR-002: FAQ Auto-Responder
```
If this email matches a FAQ, generate an appropriate response.

FAQ DATABASE:
{{faq_entries}}

EMAIL:
{{email_content}}

MATCHING RULES:
- Confidence must be > 0.85 to auto-respond
- If multiple FAQs match, combine answers
- If partial match, acknowledge and offer to clarify

Output:
{
  "auto_respond": true/false,
  "matched_faqs": ["faq_id1", "faq_id2"],
  "match_confidence": 0.0-1.0,
  "generated_response": "full response text",
  "follow_up_offer": "would you like more info about X?"
}
```

### AR-003: Out-of-Office Aware Responder
```
Generate a response considering the sender may be OOO or in a different timezone.

EMAIL METADATA:
- Sent time: {{timestamp}}
- Sender timezone: {{timezone}}
- Sender OOO status: {{ooo_if_known}}

EMAIL:
{{email_content}}

Consider:
- If sent outside business hours, they may not expect immediate response
- If they mention travel/vacation, adjust expectations
- If timezone differs significantly, note async communication

Generate appropriate response considering these factors.
```

### AR-004: Password/Access Reset Auto-Handler
```
Handle common password and access requests automatically.

REQUEST TYPE:
Analyze if this is a legitimate password/access request.

SECURITY CHECKS:
- Email matches account email
- No suspicious indicators
- Standard reset language

EMAIL:
{{email_content}}

SENDER VERIFICATION:
{{sender_email}}
{{account_email_on_file}}

Output:
{
  "request_type": "PASSWORD_RESET/ACCESS_REQUEST/MFA_HELP/ACCOUNT_UNLOCK",
  "auto_handle": true/false,
  "security_concerns": ["any red flags"],
  "action": "send_reset_link/verify_identity/escalate_security",
  "response": "generated response if auto-handling"
}
```

### AR-005: Simple Question Auto-Responder
```
For simple factual questions, provide immediate answers.

SIMPLE QUESTION CRITERIA:
- Has definitive, factual answer
- Answer is in knowledge base
- No account-specific lookup needed
- Low risk of incorrect answer causing harm

KNOWLEDGE BASE:
{{knowledge_base}}

EMAIL:
{{email_content}}

Output:
{
  "is_simple_question": true/false,
  "question_extracted": "the question",
  "answer_found": true/false,
  "answer": "the answer",
  "confidence": 0.0-1.0,
  "source": "where answer came from",
  "auto_respond": true/false,
  "response": "full response if auto-responding"
}
```

### AR-006: Status Update Responder
```
Generate status update responses for common request types.

REQUEST STATUS DATA:
{{ticket_status}}
{{order_status}}
{{request_history}}

EMAIL:
{{email_content}}

Generate response that:
1. Provides current status clearly
2. Explains next steps
3. Sets expectation for completion
4. Offers tracking method if available

Include:
- Current status in plain language
- What's been done
- What's pending
- Expected resolution date
- Who to contact if urgent
```

---

## Escalation Decision Trees

### ES-001: Escalation Evaluator
```
Determine if this email requires escalation and to whom.

ESCALATION TRIGGERS:
- Legal mentions
- Executive sender
- Media/PR threats
- Security incidents
- Regulatory mentions
- Revenue at risk > $X
- Repeated failures
- SLA breach

EMAIL:
{{email_content}}

ACCOUNT DATA:
{{account_info}}

Output:
{
  "escalate": true/false,
  "escalation_level": "L1/L2/L3/EXECUTIVE/LEGAL/SECURITY",
  "escalation_reason": "primary trigger",
  "escalate_to": "specific person/team",
  "urgency": "immediate/today/24_hours",
  "briefing": "summary for escalation recipient",
  "original_owner_action": "what should happen before escalation"
}
```

### ES-002: Management Alert Generator
```
Determine if this situation warrants management notification.

ALERT TRIGGERS:
- Customer threatening to churn (>$10k ARR)
- Legal/compliance mentions
- PR/social media threats
- Multiple related escalations
- System outage reports
- Security incident indicators

EMAIL:
{{email_content}}

CONTEXT:
{{related_tickets}}
{{account_value}}
{{account_health}}

Output:
{
  "alert_management": true/false,
  "alert_type": "INFORMATIONAL/ACTION_NEEDED/URGENT",
  "summary": "30-word summary for executive",
  "risk_assessment": "what's at stake",
  "recommended_action": "suggested management action",
  "time_sensitivity": "response window"
}
```

### ES-003: Legal Review Trigger
```
Identify if this email requires legal team review.

LEGAL TRIGGERS:
- Explicit legal threats ("lawyer", "sue", "legal action")
- Regulatory body mentions (FTC, GDPR, SEC, etc.)
- Contract dispute language
- IP infringement claims
- Harassment allegations
- Data breach concerns
- Subpoena or legal process

EMAIL:
{{email_content}}

Output:
{
  "legal_review_needed": true/false,
  "trigger_type": "THREAT/REGULATORY/CONTRACT/IP/OTHER",
  "specific_triggers": ["exact phrases that triggered"],
  "hold_response": true/false,
  "urgency": "immediate/24_hours/review",
  "recommended_action": "what to do before legal reviews",
  "draft_acknowledgment": "safe acknowledgment if needed"
}
```

### ES-004: Technical Escalation Router
```
Route technical issues to appropriate engineering team.

TECHNICAL CATEGORIES:
- INFRASTRUCTURE: Outages, performance, availability
- SECURITY: Vulnerabilities, breaches, access issues
- DATA: Data integrity, migrations, exports
- INTEGRATION: APIs, webhooks, third-party
- FRONTEND: UI bugs, display issues
- BACKEND: Processing errors, logic bugs
- MOBILE: App-specific issues

EMAIL:
{{email_content}}

SYSTEM STATUS:
{{current_incidents}}
{{maintenance_windows}}

Output:
{
  "is_technical_issue": true/false,
  "category": "CATEGORY",
  "severity": "P1/P2/P3/P4",
  "affected_systems": ["system1", "system2"],
  "route_to": "team name",
  "related_incidents": ["existing incident IDs"],
  "customer_workaround": "temporary solution if any",
  "engineering_context": "technical details for engineers"
}
```

### ES-005: VIP Handling Detector
```
Identify if sender requires VIP handling.

VIP INDICATORS:
- Executive title (CEO, CTO, VP, Director)
- Company recognition (Fortune 500, known brands)
- High-value account
- Known influencer/analyst
- Board member/investor connection
- Previous VIP flag

EMAIL:
{{email_content}}

SENDER DATA:
{{sender_info}}

Output:
{
  "vip_handling": true/false,
  "vip_type": "EXECUTIVE/ENTERPRISE/INFLUENCER/INVESTOR/OTHER",
  "vip_signals": ["detected signals"],
  "handling_protocol": "white_glove/expedited/standard",
  "assign_to": "senior rep or specific person",
  "response_sla": "accelerated SLA",
  "notification": "who should be informed"
}
```

---

## Sentiment Analysis Prompts

### SE-001: Sentiment Scorer
```
Analyze the emotional sentiment of this email.

SENTIMENT SCALE:
-5 to +5 where:
- -5: Extremely negative (rage, threats)
- -3: Very negative (frustrated, angry)
- -1: Slightly negative (disappointed, concerned)
- 0: Neutral (matter of fact)
- +1: Slightly positive (satisfied)
- +3: Very positive (happy, grateful)
- +5: Extremely positive (thrilled, advocate)

EMAIL:
{{email_content}}

Output:
{
  "sentiment_score": -5 to +5,
  "primary_emotion": "main emotion detected",
  "secondary_emotions": ["other emotions"],
  "intensity": "LOW/MEDIUM/HIGH",
  "volatility": "stable/escalating/de-escalating",
  "emotional_triggers": ["what caused the emotion"],
  "response_tone_recommendation": "how to respond"
}
```

### SE-002: Frustration Level Detector
```
Specifically measure frustration level and causes.

FRUSTRATION INDICATORS:
- ALL CAPS usage
- Multiple exclamation marks
- Exasperated language
- Repeated contact mentions
- Time elapsed complaints
- Competitive comparisons
- Sarcasm

EMAIL:
{{email_content}}

TICKET HISTORY:
{{previous_interactions}}

Output:
{
  "frustration_level": 1-10,
  "frustration_causes": [
    {
      "cause": "specific frustration source",
      "severity": "primary/contributing",
      "addressable": true/false
    }
  ],
  "frustration_trend": "increasing/stable/decreasing",
  "de_escalation_priority": true/false,
  "recommended_approach": "how to address frustration"
}
```

### SE-003: Satisfaction Predictor
```
Predict likely customer satisfaction after resolution.

PREDICTION FACTORS:
- Current sentiment
- Issue complexity
- Resolution feasibility
- Previous CSAT scores
- Effort required from customer

EMAIL:
{{email_content}}

RESOLUTION PLAN:
{{planned_response}}

Output:
{
  "predicted_csat": 1-5,
  "prediction_confidence": 0.0-1.0,
  "risk_factors": ["factors that could lower satisfaction"],
  "enhancement_opportunities": ["ways to exceed expectations"],
  "follow_up_recommended": true/false,
  "survey_timing": "when to send satisfaction survey"
}
```

---

## Entity Extraction Prompts

### EX-001: Contact Information Extractor
```
Extract all contact information from this email.

EXTRACT:
- Email addresses (and their purpose)
- Phone numbers (and type: mobile, office, fax)
- Physical addresses
- Social media handles
- Company names
- Person names and titles

EMAIL:
{{email_content}}

Output:
{
  "contacts": [
    {
      "name": "person name",
      "title": "job title",
      "company": "company name",
      "email": "email address",
      "phone": "phone number",
      "phone_type": "mobile/office",
      "address": "physical address"
    }
  ],
  "primary_contact": "main person to respond to",
  "cc_contacts": ["people to keep informed"]
}
```

### EX-002: Date & Deadline Extractor
```
Extract all temporal references from this email.

EXTRACT:
- Explicit dates ("January 15th", "12/31/2024")
- Relative dates ("next Monday", "in 2 weeks")
- Deadlines ("by end of week", "before the meeting")
- Time references ("3pm EST", "morning")
- Duration mentions ("for 3 months", "30-day trial")

EMAIL:
{{email_content}}

Output:
{
  "dates_mentioned": [
    {
      "reference": "original text",
      "interpreted_date": "YYYY-MM-DD",
      "is_deadline": true/false,
      "context": "what this date relates to"
    }
  ],
  "primary_deadline": "most important date",
  "calendar_suggestions": ["events to schedule"]
}
```

### EX-003: Product & Feature Extractor
```
Identify products, features, and technical terms mentioned.

EXTRACT:
- Product names (yours and competitors)
- Feature names
- Plan/tier mentions
- Integration names
- Technical terms
- Error codes/messages

EMAIL:
{{email_content}}

PRODUCT CATALOG:
{{your_products}}

Output:
{
  "your_products": ["product mentions"],
  "competitor_products": ["competitor mentions"],
  "features_discussed": ["feature names"],
  "technical_terms": ["technical references"],
  "error_references": ["error codes or messages"],
  "documentation_links": ["relevant docs to share"]
}
```

### EX-004: Order & Account Extractor
```
Extract transaction and account identifiers.

EXTRACT:
- Order numbers
- Invoice numbers
- Ticket/case numbers
- Account IDs
- Subscription IDs
- Transaction IDs
- Reference numbers

EMAIL:
{{email_content}}

Output:
{
  "identifiers": [
    {
      "type": "ORDER/INVOICE/TICKET/ACCOUNT/OTHER",
      "value": "the identifier",
      "validated": true/false,
      "lookup_result": "if validated, what was found"
    }
  ],
  "primary_reference": "main identifier to use",
  "cross_references": ["related identifiers found in system"]
}
```

### EX-005: Monetary Value Extractor
```
Extract all monetary references.

EXTRACT:
- Explicit amounts ("$5,000", "50 dollars")
- Percentage references ("20% off", "50% discount")
- Revenue mentions ("$100k deal", "6-figure contract")
- Budget references ("budget of $10k")
- Loss/refund amounts

EMAIL:
{{email_content}}

Output:
{
  "monetary_references": [
    {
      "amount": number,
      "currency": "USD/EUR/etc",
      "context": "what this amount relates to",
      "type": "PAYMENT/REFUND/BUDGET/REVENUE/DISCOUNT"
    }
  ],
  "total_value_at_stake": number,
  "financial_urgency": "HIGH/MEDIUM/LOW"
}
```

---

## Routing Rules

### RO-001: Department Router
```
Route this email to the appropriate department.

DEPARTMENTS:
- SALES: New business, pricing, demos
- SUPPORT: Technical help, how-to, troubleshooting
- BILLING: Payments, invoices, refunds
- SUCCESS: Account health, renewals, expansion
- PRODUCT: Feature requests, feedback, beta
- LEGAL: Contracts, compliance, disputes
- EXECUTIVE: C-level correspondence
- SPAM: Junk, phishing, irrelevant

EMAIL:
{{email_content}}

Output:
{
  "department": "DEPARTMENT",
  "confidence": 0.0-1.0,
  "secondary_department": "if multiple apply",
  "specific_queue": "sub-queue if applicable",
  "skill_tags": ["required skills to handle"],
  "routing_notes": "special instructions"
}
```

### RO-002: Agent Skill Matcher
```
Match this email to agent skills required.

SKILL CATEGORIES:
- TECHNICAL: API, integrations, debugging
- PRODUCT: Feature expertise
- BILLING: Financial systems
- ENTERPRISE: Large account handling
- LANGUAGES: Spanish, French, German, etc.
- INDUSTRY: Healthcare, Finance, Retail, etc.
- ESCALATION: De-escalation, complaint handling
- SALES: Negotiation, closing

EMAIL:
{{email_content}}

AVAILABLE AGENTS:
{{agent_skills}}

Output:
{
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["nice to have"],
  "complexity": "L1/L2/L3",
  "best_match_agent": "agent_id",
  "alternative_agents": ["agent_id2"],
  "workload_consideration": "factor in current queues"
}
```

### RO-003: SLA Assignment
```
Assign SLA based on email analysis.

SLA TIERS:
- CRITICAL: 1 hour response (system down, legal, security)
- HIGH: 4 hours response (paying customer urgent)
- STANDARD: 24 hours response (normal business)
- LOW: 48 hours response (general inquiry)

FACTORS:
- Customer tier
- Issue severity
- Business impact
- Time sensitivity detected
- Previous SLA breaches

EMAIL:
{{email_content}}

ACCOUNT:
{{account_tier}}

Output:
{
  "sla_tier": "TIER",
  "response_deadline": "timestamp",
  "resolution_target": "timestamp",
  "sla_factors": ["reasons for this SLA"],
  "breach_risk": "LOW/MEDIUM/HIGH",
  "escalation_trigger": "when to escalate if unresolved"
}
```

---

## Follow-up Generation

### FU-001: Follow-up Timing Calculator
```
Determine optimal follow-up timing for this thread.

CONSIDER:
- Issue type and complexity
- Customer timezone
- Previous response patterns
- Business days vs calendar days
- Urgency level

THREAD:
{{email_thread}}

Output:
{
  "follow_up_needed": true/false,
  "follow_up_date": "YYYY-MM-DD",
  "follow_up_time": "HH:MM timezone",
  "follow_up_type": "CHECK_IN/REMINDER/ESCALATION/CLOSE_LOOP",
  "follow_up_message": "suggested content"
}
```

### FU-002: Thread Closure Detector
```
Determine if this email thread can be closed.

CLOSURE SIGNALS:
- "Thanks, that solved it"
- No response needed language
- Confirmation received
- Issue marked resolved
- No outstanding questions

KEEP OPEN SIGNALS:
- Unanswered questions
- Pending actions
- Partial resolution
- Ambiguous response

EMAIL:
{{email_content}}

THREAD HISTORY:
{{thread}}

Output:
{
  "can_close": true/false,
  "closure_confidence": 0.0-1.0,
  "outstanding_items": ["items preventing closure"],
  "closure_message": "optional closing response",
  "survey_appropriate": true/false,
  "archive_category": "RESOLVED/ANSWERED/NO_RESPONSE_NEEDED"
}
```

---

## Summary Generation

### SU-001: Email Thread Summarizer
```
Summarize this email thread for quick understanding.

INCLUDE:
- Original issue/request
- Key back-and-forth points
- Current status
- Outstanding items
- Customer sentiment trend

THREAD:
{{email_thread}}

Output:
{
  "summary": "2-3 sentence summary",
  "original_request": "what they initially wanted",
  "resolution_status": "RESOLVED/PENDING/BLOCKED",
  "key_points": ["important developments"],
  "outstanding_actions": ["what's still needed"],
  "sentiment_journey": "how sentiment changed",
  "next_step": "recommended next action"
}
```

### SU-002: Handoff Summary Generator
```
Create a summary for agent-to-agent handoff.

INCLUDE:
- Customer context
- Issue summary
- What's been tried
- Current status
- Customer mood
- Next steps

THREAD:
{{email_thread}}

ACCOUNT DATA:
{{account_info}}

Output:
{
  "customer_summary": "who they are and their value",
  "issue_summary": "what's wrong",
  "attempted_solutions": ["what's been tried"],
  "current_status": "where things stand",
  "customer_mood": "how they're feeling",
  "critical_context": "must-know information",
  "next_steps": "what the new agent should do",
  "avoid": "pitfalls or sensitive areas"
}
```

### SU-003: Daily Digest Generator
```
Generate a summary of email activity for reporting.

ANALYZE:
{{day_emails}}

Output:
{
  "total_received": number,
  "by_category": {"SUPPORT": x, "SALES": y},
  "by_priority": {"HIGH": x, "STANDARD": y},
  "average_sentiment": -5 to +5,
  "escalations": number,
  "notable_issues": ["significant items"],
  "trends": ["patterns observed"],
  "recommendations": ["suggested improvements"]
}
```

---

## Quick Reference

### Prompt Selection Guide

| Scenario | Primary Prompt | Supporting Prompts |
|----------|---------------|-------------------|
| New email arrives | CL-001 + PR-001 | RO-001 |
| Support ticket | CL-002 + ES-004 | AR-001 |
| Sales inquiry | CL-003 + SQ signals | AR-002 |
| Angry customer | SE-002 + ES-001 | AR-001 |
| Simple question | IN-001 + AR-005 | FU-002 |
| Account change | EX-004 + AR-004 | - |
| Thread handoff | SU-002 | RO-002 |

### Classification Quick Reference

| Category | Route To | SLA | Auto-Response |
|----------|----------|-----|---------------|
| URGENT_SUPPORT | Support L2 | 1hr | Acknowledgment |
| ROUTINE_SUPPORT | Support L1 | 24hr | FAQ if matched |
| SALES_INQUIRY | Sales | 4hr | Acknowledgment |
| BILLING | Billing | 24hr | Status if found |
| COMPLAINT | Support L2 | 4hr | Empathetic ack |
| SPAM | Archive | None | None |

---

*Powered by GetAnswers - AI that actually answers.*
---

## Pro Upgrade: Prompt Ops Playbook
Make prompt output consistent and useful for email automation and inbox productivity.

### Prompting Rules
- Provide context: goal, audience, and constraints.
- Ask for structured output.
- Include examples of good vs. bad output.

### Quality Rubric
| Dimension | 1 | 3 | 5 |
| --- | --- | --- | --- |
| Accuracy | Generic | Mostly right | Verified and precise |
| Actionability | Vague | Some steps | Clear next actions |
| Brand Fit | Off tone | Acceptable | On-brand and sharp |

### Review Loop
- Run 3 sample prompts weekly.
- Log gaps and refine prompt wording.
- Save best outputs to a shared library.

### Stakeholders to Involve
- ops.
- support.
- sales.
- founders.

