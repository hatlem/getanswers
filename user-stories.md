# GetAnswers - Comprehensive User Journey Stories

This document outlines 10 comprehensive user journey stories covering different user types, scenarios, and workflows within the GetAnswers AI Email Agent platform.

---

## User Story 1: First-Time User Registration and Onboarding

**Title:** New User Complete Onboarding with Gmail Integration

**As a** busy professional drowning in email

**I want to** create an account and connect my Gmail to GetAnswers

**So that** I can start having AI handle my routine email responses automatically

### Acceptance Criteria
- User can register using email/password or Google OAuth
- User is guided through a clear 3-step onboarding process (Welcome, Connect Email, Preferences)
- Gmail OAuth flow completes successfully with proper token storage
- Personal organization/workspace is automatically created for the user
- AI learning analysis is triggered after onboarding completes (if user has 3+ sent emails)

### User Journey Steps
1. **Landing Page Discovery**: User arrives at getanswers.co and reads about the AI email agent capabilities, including the promise of 80%+ emails handled autonomously
2. **Registration Initiation**: User clicks "Get Started" and chooses to register via Google OAuth for faster signup
3. **Account Creation**: System creates user account, generates personal organization workspace, and redirects to dashboard
4. **Onboarding Modal - Welcome**: User sees welcome screen explaining the 3-step setup: Connect email, AI learns your style, Reclaim your time
5. **Onboarding Modal - Connect Email**: User clicks "Connect with Google" button, is redirected to Google OAuth consent screen
6. **Gmail Authorization**: User grants read/write access to Gmail, Google redirects back with authorization code
7. **Token Exchange**: Backend exchanges auth code for access/refresh tokens, stores credentials securely in user profile, validates by fetching Gmail profile
8. **Onboarding Modal - Preferences**: User configures initial preferences: auto-reply to routine emails, daily digest summary, priority inbox sorting
9. **Complete Onboarding**: User clicks "Get Started", onboarding is marked complete, Celery task queued to analyze writing style from sent emails
10. **Dashboard Ready**: User sees main dashboard with empty review queue, ready for email sync to begin

---

## User Story 2: Reviewing and Approving AI-Generated Email Responses

**Title:** Review Queue Decision Making for Pending Actions

**As a** GetAnswers user with emails in my review queue

**I want to** quickly review AI-proposed responses and approve or modify them

**So that** emails are sent efficiently while maintaining my personal voice and accuracy

### Acceptance Criteria
- Review queue displays pending actions sorted by priority score (urgency + risk + confidence)
- Each action card shows sender info, summary, confidence score (0-100%), and risk level badge
- User can approve with one click, sending the email automatically
- User can edit the response before sending if adjustments are needed
- Approved/edited emails are sent via Gmail API and logged in conversation history

### User Journey Steps
1. **Dashboard Access**: User logs in and sees "Needs My Decision" count of 5 in left navigation with efficiency stats showing 73% handled by AI
2. **Queue View**: User clicks to view review queue, sees 5 action cards ordered by priority - high-risk financial email at top
3. **Card Selection**: User clicks on first card from "Sarah Chen at Acme Corp" regarding invoice payment terms
4. **Context Panel**: Right column shows full conversation timeline with 3 previous messages, AI analysis summary, and related invoice attachments
5. **Response Review**: User reads AI-proposed response: "Hi Sarah, Thanks for following up on invoice #1234..." with 78% confidence score
6. **Approve Action**: User determines response is accurate, clicks green "Approve" checkmark button
7. **Email Execution**: Backend receives approve request, marks action as approved, triggers Celery task to send email via Gmail API
8. **Success Notification**: Toast notification appears "Email sent successfully", card animates out of queue
9. **Queue Update**: Queue refreshes showing 4 remaining items, stats update to show 74% efficiency rate
10. **Audit Trail**: Action is logged in agent_actions table with timestamp, status=approved, linked to conversation and objective

---

## User Story 3: Editing AI Draft Before Sending

**Title:** Modifying AI-Generated Response with Custom Content

**As a** user who received an AI draft that needs adjustments

**I want to** edit the proposed email content before approving it for sending

**So that** I can add specific details or correct inaccuracies while still saving time

### Acceptance Criteria
- Edit modal displays original AI-generated content in a rich text editor
- Both original and edited content are stored for AI learning purposes
- Edited response is sent via the same execution pipeline as approved responses
- Edit action is tracked separately from pure approval for edit pattern analysis
- AI learning system captures edit patterns for future improvement

### User Journey Steps
1. **Identify Edit Need**: User reviews AI draft for meeting rescheduling request - response says "Tuesday at 2pm" but user knows they have a conflict
2. **Open Edit Modal**: User clicks pencil/edit icon on action card, modal opens with AI draft in editable text area
3. **Review Original**: Modal shows original subject "Re: Project Sync Meeting" and body proposing Tuesday 2pm
4. **Make Corrections**: User changes "Tuesday at 2pm" to "Wednesday at 3pm" and adds "I'll send a calendar invite shortly"
5. **Preview Changes**: User reviews modified response in preview pane, verifies all other content is appropriate
6. **Save and Send**: User clicks "Save & Send" button, triggering edit action with new content
7. **Backend Processing**: Action status set to "edited", user_edit field stores modified content, original preserved in proposed_content
8. **Email Dispatch**: Celery task sends email using user_edit content via Gmail API
9. **Learning Capture**: Edit is logged for edit_learning service analysis - tracks pattern of time/scheduling corrections
10. **Profile Update**: If user has writing_style_profile, edit patterns may trigger background job to update style preferences

---

## User Story 4: Overriding AI Decision for Complex Situations

**Title:** Rejecting AI Response and Handling Email Manually

**As a** user dealing with a sensitive negotiation email

**I want to** reject the AI's proposed response entirely

**So that** I can craft a careful manual reply for this high-stakes communication

### Acceptance Criteria
- Override action requires a reason to be provided for learning purposes
- Action is marked as rejected with the override reason stored
- Objective status changes to "waiting_on_you" for manual follow-up
- Override reasons are used to improve future AI decisions
- User is not locked out from viewing the rejected AI draft

### User Journey Steps
1. **High-Risk Detection**: User notices a card with red "High Risk" badge from opposing legal counsel regarding contract terms
2. **Review AI Draft**: AI proposed a standard acknowledgment response with 45% confidence score (flagged as uncertain)
3. **Recognize Sensitivity**: User realizes AI doesn't understand the nuanced negotiation position required for this response
4. **Initiate Override**: User clicks red "Override" button to reject the AI's proposal
5. **Reason Entry**: Modal prompts for override reason - user enters "Legal negotiation requires strategic response - involving counsel"
6. **Confirm Override**: User submits override, action status changes to "rejected" with reason stored
7. **Objective Update**: Conversation's objective status changes to "waiting_on_you", appears in different queue section
8. **Manual Handling**: User drafts response outside GetAnswers with legal team, sends via Gmail directly
9. **Learning Integration**: Override reason logged for AI learning - pattern detected: legal/contract emails often need override
10. **Policy Suggestion**: System may later suggest creating a policy rule for "legal@" domain senders to always require review

---

## User Story 5: Escalating Email for Team Review

**Title:** Flagging Email for Additional Context or Team Input

**As a** user unsure how to respond to a complex customer issue

**I want to** escalate the email for team review

**So that** I can get input from colleagues before responding

### Acceptance Criteria
- Escalate action elevates the item's risk level to "high"
- Optional escalation reason can be provided
- Optional team notification can be triggered
- Item remains in queue with elevated priority for visibility
- Escalation is logged in audit trail for accountability

### User Journey Steps
1. **Complex Request**: User sees email from VIP client requesting feature that may require product team input
2. **Uncertainty Recognition**: AI drafted a non-committal response but user feels client deserves better answer
3. **Initiate Escalation**: User clicks orange "Escalate" button on action card
4. **Escalation Details**: Modal offers optional reason field and "Notify team members" checkbox
5. **Provide Context**: User enters "Need product roadmap confirmation before committing - Sarah should weigh in"
6. **Enable Notification**: User checks "Notify team members" to alert relevant colleagues
7. **Submit Escalation**: Action's risk_level updated to HIGH, escalation_note stored
8. **Notification Dispatch**: Celery task triggered to send_action_notification to team (if organization has team members)
9. **Priority Boost**: Item appears at top of review queue due to high risk level affecting priority_score
10. **Collaborative Resolution**: Team member reviews, provides input via comments, original user can then approve/edit

---

## User Story 6: Connecting SMTP/IMAP Email Provider

**Title:** Setting Up Non-OAuth Email Provider via SMTP/IMAP

**As a** user with a custom business email domain

**I want to** connect my email via SMTP/IMAP credentials

**So that** I can use GetAnswers with any email provider, not just Gmail/Outlook

### Acceptance Criteria
- SMTP preset configurations available for common providers (Gmail, Outlook, Yahoo, iCloud)
- Custom server option allows manual IMAP/SMTP server configuration
- Connection test validates credentials before saving
- Error messages clearly indicate connection failures and solutions
- Credentials are stored securely in user profile

### User Journey Steps
1. **Connection Need**: User with company email on custom domain needs to connect during onboarding
2. **Select SMTP Option**: On connect email step, user clicks "Connect with SMTP/IMAP" button
3. **Provider Selection**: Modal shows provider dropdown - user selects "Custom Server" for their Exchange-compatible server
4. **Enter Credentials**: User fills in email address (user@company.com) and app password
5. **Configure Servers**: User enters custom IMAP server (mail.company.com:993) and SMTP server (mail.company.com:587)
6. **SSL Settings**: User confirms SSL/TLS enabled checkbox is checked
7. **Test Connection**: User clicks "Connect" button, loading spinner shows "Testing Connection..."
8. **Connection Validation**: Backend attempts IMAP login and SMTP handshake to verify credentials
9. **Error Handling**: If connection fails, clear error message displayed: "IMAP authentication failed - check password"
10. **Success Storage**: On success, credentials stored encrypted in user.smtp_credentials, redirects to preferences step

---

## User Story 7: Viewing and Managing AI Learning Profile

**Title:** Understanding and Optimizing AI Writing Style Learning

**As a** user who wants the AI to better match my communication style

**I want to** view my AI learning profile and trigger re-analysis

**So that** AI responses sound more authentically like me

### Acceptance Criteria
- AI Learning page displays current writing style profile characteristics
- Profile shows confidence level, sample size, and last updated timestamp
- User can manually trigger new style analysis from sent emails
- User can delete profile to reset AI learning
- Edit insights show how user corrections are improving the AI

### User Journey Steps
1. **Access AI Learning**: User clicks "AI Learning" in navigation to view /ai-learning page
2. **View Profile Status**: Page shows current profile with 76% confidence based on 47 emails analyzed
3. **Review Characteristics**: Profile displays learned traits: formal tone, concise responses, common greeting "Hi", closing "Best regards"
4. **Check Recommendations**: System recommends "Analyze 10 more sent emails to improve accuracy"
5. **Trigger Re-analysis**: User clicks "Analyze Writing Style" button to refresh profile from recent sent emails
6. **Processing State**: Button shows loading state while WritingStyleService analyzes last 50-90 sent emails
7. **View Results**: New analysis complete - confidence increased to 82%, detected preference for bullet points in long responses
8. **Review Edit Insights**: User checks "Edit Patterns" tab showing 15 edits analyzed, common pattern: "adds specific dates/times"
9. **Understanding Improvements**: System explains how edit patterns are being incorporated into future response generation
10. **Profile Management**: If needed, user can click "Delete Profile" to reset and start fresh learning

---

## User Story 8: Handling Magic Link Authentication

**Title:** Passwordless Login via Magic Link Email

**As a** user who prefers passwordless authentication

**I want to** log in using a magic link sent to my email

**So that** I don't have to remember yet another password

### Acceptance Criteria
- Magic link request creates database record with unique token and expiration
- Rate limiting prevents abuse (3 requests per hour per email)
- Magic link expires after configured time (default 15 minutes)
- Token is single-use and marked as used after verification
- User receives access token upon successful verification

### User Journey Steps
1. **Login Page**: User navigates to /login and sees options for password, Google OAuth, or magic link
2. **Request Magic Link**: User enters email address and clicks "Send Magic Link"
3. **Rate Limit Check**: Backend checks Redis for rate limiting - under 3 requests in past hour
4. **Token Generation**: Secure magic link token generated, stored in magic_links table with 15-min expiry
5. **Email Dispatch**: Email service sends magic link with format: getanswers.co/auth/verify?token=xxx
6. **User Checks Email**: User opens email, sees professional-looking magic link email with button "Sign in to GetAnswers"
7. **Click Magic Link**: User clicks link, browser opens /auth/verify page with token in URL
8. **Token Verification**: Backend validates token exists, not expired, not used
9. **Mark Token Used**: Token marked as used (used_at timestamp set) to prevent replay
10. **Session Creation**: JWT access token created, user redirected to dashboard with active session

### Edge Cases
- **Expired Token**: User clicks link after 15 minutes - shown error "Magic link has expired" with option to request new one
- **Used Token**: User clicks link twice - shown error "Magic link has already been used"
- **Rate Limited**: User requests 4th magic link in 1 hour - shown error "Too many requests, please try again later"

---

## User Story 9: Admin Monitoring Platform-Wide AI Learning

**Title:** Super Admin Reviewing AI Learning Metrics Across Users

**As a** super admin responsible for platform health

**I want to** monitor AI learning statistics across all users

**So that** I can identify users needing assistance and track overall learning effectiveness

### Acceptance Criteria
- Admin AI Learning page accessible only to super_admin users
- Dashboard shows aggregate metrics: total profiles, average confidence, stale profile count
- Quality distribution chart shows confidence levels across user base
- Per-user table shows individual profile status with manual trigger option
- Admin can manually trigger analysis for specific users

### User Journey Steps
1. **Admin Access**: Super admin user navigates to /admin, sees admin navigation with AI Learning section
2. **Overview Dashboard**: Admin sees platform metrics: 150 total users, 89 with profiles, 72% avg confidence
3. **Stale Profile Alert**: Dashboard highlights 12 profiles older than 30 days needing refresh
4. **Quality Distribution**: Chart shows confidence distribution: 15% below 50%, 45% at 50-80%, 40% above 80%
5. **User Details Table**: Table lists all users with columns: email, profile status, confidence, sample size, last updated
6. **Identify Issues**: Admin sorts by confidence to find users with low-quality profiles or no profile
7. **Manual Trigger**: Admin clicks "Trigger Analysis" for user john@example.com who has 0% confidence
8. **Celery Task Queued**: Backend queues initial_writing_analysis task for that user
9. **Monitor Progress**: Admin refreshes page to see analysis complete, user now at 68% confidence
10. **Bulk Actions**: Admin can use filters to find all stale profiles and trigger batch refresh jobs

---

## User Story 10: Auto-Execution of Low-Risk High-Confidence Actions

**Title:** Autonomous Email Handling Without Human Review

**As a** power user with high autonomy settings

**I want** routine emails to be handled automatically without my review

**So that** I can focus only on complex communications while AI handles the rest

### Acceptance Criteria
- Auto-execution decision based on confidence threshold (70% for high autonomy, 85% for medium)
- Only low-risk actions are eligible for auto-execution
- Send actions require higher confidence threshold (+10%)
- Auto-executed actions are logged with full audit trail
- User can adjust autonomy level in settings

### User Journey Steps
1. **High Autonomy Setting**: User has configured autonomy_level to HIGH in settings, enabling auto-execution at 70%+ confidence
2. **New Email Arrives**: Routine meeting confirmation email received from known colleague
3. **Inbox Sync**: Celery beat triggers periodic inbox sync, fetches new message via Gmail API
4. **Message Processing**: TriageService.process_new_email() starts 10-step pipeline
5. **AI Analysis**: AgentService.analyze_email() classifies: intent=confirmation, urgency=low, risk=low, sentiment=positive
6. **Response Generation**: AgentService.generate_response() creates draft: "Thanks for confirming! See you then. Best, [User]"
7. **Confidence Calculation**: calculate_confidence() returns 88% based on clear intent, known sender, familiar context
8. **Risk Assessment**: assess_risk() returns LOW - routine scheduling, no financial/legal implications
9. **Auto-Execute Decision**: should_auto_execute() checks: 88% >= 70% threshold, risk=LOW, action=SEND (+10 = 80% threshold, 88% passes)
10. **Autonomous Execution**: execute_action() sends email via Gmail API without queuing for review, logs as approved with auto_executed=True

### Edge Case Handling
- **Medium Risk**: Same email but mentions budget - risk elevated to MEDIUM, auto-execution blocked despite high confidence
- **Send Threshold**: Draft action type would only need 70% confidence, but Send needs 80% (+10)
- **Low Confidence**: Similar email but from unknown sender - confidence drops to 62%, queued for review
- **User Override**: If user had autonomy_level=LOW, no auto-execution regardless of confidence/risk

---

## Summary

These 10 user stories cover the complete user journey through GetAnswers:

1. **Registration & Onboarding** - New user setup with Gmail OAuth
2. **Approve Actions** - Standard review queue workflow
3. **Edit Before Sending** - Modifying AI drafts
4. **Override/Reject** - Handling manually for complex cases
5. **Escalate for Team** - Collaborative review process
6. **SMTP/IMAP Setup** - Non-OAuth email providers
7. **AI Learning Profile** - Understanding and managing personalization
8. **Magic Link Auth** - Passwordless login flow
9. **Admin Monitoring** - Platform-wide AI learning oversight
10. **Auto-Execution** - Autonomous handling of routine emails

Each story represents real functionality implemented in the codebase, covering happy paths, edge cases, and error handling scenarios that users may encounter.
