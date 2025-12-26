# AI Learning System - Developer Guide

**Last Updated**: 2025-12-26
**Version**: 1.0.0

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [API Reference](#api-reference)
5. [Background Tasks](#background-tasks)
6. [Database Schema](#database-schema)
7. [Frontend Integration](#frontend-integration)
8. [Configuration](#configuration)
9. [Monitoring & Metrics](#monitoring--metrics)
10. [Troubleshooting](#troubleshooting)
11. [Development Guide](#development-guide)

---

## Overview

The AI Learning System enables GetAnswers to learn from user behavior and continuously improve response quality through:

- **Writing Style Learning**: Analyzes sent emails to understand user's unique communication style
- **Edit Pattern Recognition**: Learns from how users modify AI-generated responses
- **Automated Profile Refresh**: Keeps learning models current without user intervention
- **Complete Transparency**: Shows users exactly what the AI has learned

### Business Value

- **Increased Autonomous Handling**: Better first drafts = higher confidence = more auto-execution
- **Reduced Edit Rate**: AI matches user style from day 1, fewer corrections needed
- **User Trust**: Transparency into learning builds confidence in AI decisions
- **Competitive Moat**: No competitor has this level of personalized learning

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       User Actions                           │
│  (Sends emails, Edits AI drafts, Triggers analysis)         │
└────────────┬──────────────────────────────┬─────────────────┘
             │                               │
             ▼                               ▼
┌────────────────────────┐      ┌────────────────────────────┐
│   Writing Style        │      │   Edit Learning            │
│   Service              │      │   Service                  │
│                        │      │                            │
│ - Analyzes sent emails │      │ - Analyzes edit diffs      │
│ - Extracts style       │      │ - Identifies patterns      │
│ - Uses Claude Opus 4.5 │      │ - Uses Claude Sonnet 4.5   │
└────────────┬───────────┘      └──────────┬─────────────────┘
             │                               │
             ▼                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  User.writing_style_profile                  │
│                  (Cached JSON in Database)                   │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Triage Service                            │
│  (Uses profile to personalize AI response generation)       │
└─────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                Approval Queue (Draft Review)                 │
│         User approves/edits → Learning loop closes           │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Initial Learning**:
   - User sends 3+ emails through GetAnswers
   - Background task triggers style analysis
   - Profile cached in `user.writing_style_profile`

2. **Continuous Improvement**:
   - User edits AI draft
   - Edit diff stored in `agent_action.user_edit`
   - Weekly task analyzes patterns → updates profile

3. **Profile Refresh**:
   - Daily task checks for profiles >30 days old
   - Re-analyzes recent sent emails
   - Updates cached profile

4. **Personalized Responses**:
   - Triage service loads cached profile
   - Passes preferences to Claude AI
   - Generates response matching user's style

---

## Core Components

### 1. WritingStyleService

**Location**: `backend/app/services/writing_style.py`

**Purpose**: Analyzes user's sent emails to extract writing style characteristics.

**Key Methods**:

```python
async def analyze_user_writing_style(
    db: AsyncSession,
    user_id: UUID,
    lookback_days: int = 90,
    max_emails: int = 50
) -> StyleAnalysisResult
```

Analyzes recent sent emails and returns comprehensive style profile.

**Profile Schema** (`WritingStyleProfile`):
```python
{
    "overall_tone": str,              # "professional", "casual", "friendly", "formal"
    "formality_level": int,           # 1-5 scale
    "warmth_level": int,              # 1-5 scale
    "avg_email_length": int,          # Average words per email
    "prefers_concise": bool,          # True if emails are typically short
    "uses_bullet_points": bool,       # Frequently uses bullet points
    "common_greetings": List[str],    # ["Hi", "Hello", "Hey"]
    "common_closings": List[str],     # ["Best regards", "Thanks", "Cheers"]
    "common_phrases": List[str],      # Frequently used phrases
    "uses_paragraphs": bool,          # Organizes in paragraphs
    "uses_exclamation": bool,         # Uses exclamation marks
    "uses_emojis": bool,              # Uses emojis
    "shows_enthusiasm": bool,         # Shows enthusiasm in writing
    "acknowledges_receipt": bool,     # Typically acknowledges emails
    "sample_size": int,               # Number of emails analyzed
    "confidence": float,              # 0-1 confidence in profile
    "last_updated": datetime          # When profile was generated
}
```

**AI Model**: Claude Opus 4.5 (for comprehensive analysis)

**Cost**: ~$0.30 per analysis (50 emails @ ~500 words each)

**Cache Duration**: 30 days (profile stored in database)

---

### 2. EditLearningService

**Location**: `backend/app/services/edit_learning.py`

**Purpose**: Analyzes user edits to identify patterns and improve future responses.

**Key Methods**:

```python
async def analyze_edit(
    original_draft: str,
    user_edit: str,
    context: Optional[str] = None
) -> EditFeedback
```

Analyzes a single edit to understand what changed.

```python
async def analyze_user_edit_patterns(
    db: AsyncSession,
    user_id: UUID,
    lookback_days: int = 30,
    min_edits: int = 5
) -> Optional[EditAnalysis]
```

Identifies patterns across multiple edits (requires minimum 5 edits).

**Edit Analysis Schema** (`EditAnalysis`):
```python
{
    "makes_more_formal": bool,        # User increases formality
    "makes_more_casual": bool,        # User decreases formality
    "adds_warmth": bool,              # User adds friendliness
    "makes_more_concise": bool,       # User shortens responses
    "adds_details": bool,             # User adds more information
    "changes_structure": bool,        # User reorganizes content
    "adds_acknowledgments": bool,     # User adds "Thanks for your email"
    "adds_next_steps": bool,          # User clarifies action items
    "softens_language": bool,         # User makes language less direct
    "avg_edit_percentage": float,     # Average % of content changed
    "heavy_edit_rate": float,         # % of edits changing >50%
    "patterns": List[EditPattern],    # Identified patterns
    "recommendations": List[str],     # How to improve AI
    "sample_size": int                # Number of edits analyzed
}
```

**AI Model**: Claude Sonnet 4.5 (for fast, cost-effective analysis)

**Cost**: ~$0.05 per analysis (50 edits)

**Trigger**: Weekly background task if user has 5+ edits

---

### 3. Triage Service Integration

**Location**: `backend/app/services/triage.py`

**Integration Point**: `process_new_email()` method

```python
# Get personalized writing style preferences if available
user_preferences = None
if self.writing_style and user.writing_style_profile:
    try:
        profile = json.loads(user.writing_style_profile)
        user_preferences = {
            "communication_tone": profile.get("overall_tone", "professional"),
            "response_length": "concise" if profile.get("prefers_concise", True) else "detailed",
            "formality_level": profile.get("formality_level", 3),
            "uses_bullet_points": profile.get("uses_bullet_points", False),
            "common_greetings": profile.get("common_greetings", []),
            "common_closings": profile.get("common_closings", []),
        }
    except Exception as e:
        logger.warning(f"Failed to load writing style profile: {e}")

draft = await self.agent.generate_response(
    message=message,
    conversation_context=context_messages,
    analysis=analysis,
    user_email=user.email,
    user_name=user.name,
    user_preferences=user_preferences  # ← Passed to AI
)
```

**Impact**: AI generates responses matching user's style from first draft.

---

## API Reference

### Base URL
```
/api/ai-learning
```

All endpoints require authentication via Bearer token.

---

### GET /profile

Get user's cached writing style profile.

**Response**:
```json
{
  "has_profile": true,
  "profile": {
    "overall_tone": "professional",
    "formality_level": 4,
    "warmth_level": 3,
    "avg_email_length": 150,
    "prefers_concise": true,
    "uses_bullet_points": false,
    "common_greetings": ["Hi", "Hello"],
    "common_closings": ["Best regards", "Thanks"],
    "sample_size": 42,
    "confidence": 0.85,
    "last_updated": "2025-12-26T10:30:00Z"
  },
  "last_updated": "2025-12-26T10:30:00Z",
  "sample_size": 42,
  "confidence": 0.85
}
```

**Status Codes**:
- `200 OK`: Profile retrieved successfully
- `401 Unauthorized`: Invalid/missing token

---

### POST /analyze

Trigger writing style analysis for current user.

**Request Body**:
```json
{
  "lookback_days": 90,  // Optional, default 90
  "max_emails": 50      // Optional, default 50
}
```

**Response**:
```json
{
  "success": true,
  "message": "Successfully analyzed 42 emails",
  "profile": { /* WritingStyleProfile */ },
  "insights": [
    "User prefers concise, professional emails",
    "Uses standard business greetings",
    "Rarely uses bullet points"
  ],
  "recommendations": [
    "Keep responses under 200 words",
    "Use 'Hi' or 'Hello' for greetings",
    "Use 'Best regards' for closings"
  ]
}
```

**Status Codes**:
- `200 OK`: Analysis completed
- `401 Unauthorized`: Invalid/missing token
- `500 Internal Server Error`: Analysis failed

**Note**: This is a compute-intensive operation (5-30 seconds). Should not be called frequently.

---

### DELETE /profile

Delete user's cached writing style profile.

**Response**:
```json
{
  "success": true,
  "message": "Writing style profile deleted"
}
```

**Status Codes**:
- `200 OK`: Profile deleted
- `401 Unauthorized`: Invalid/missing token

---

### GET /edit-insights

Analyze user's edit patterns to identify learning opportunities.

**Query Parameters**:
- `lookback_days` (int, default 30): Days to look back for edits

**Response**:
```json
{
  "has_insights": true,
  "analysis": {
    "makes_more_formal": false,
    "makes_more_casual": true,
    "adds_warmth": true,
    "avg_edit_percentage": 25.5,
    "heavy_edit_rate": 15.0,
    "patterns": [
      {
        "pattern_type": "tone",
        "description": "User frequently adds warmth/friendliness",
        "frequency": 12,
        "confidence": 0.8
      }
    ],
    "recommendations": [
      "Increase warmth in AI responses",
      "Use more friendly language"
    ],
    "sample_size": 28
  },
  "message": "Successfully analyzed 28 edits"
}
```

**Status Codes**:
- `200 OK`: Analysis completed or insufficient data
- `401 Unauthorized`: Invalid/missing token
- `500 Internal Server Error`: Analysis failed

**Requirements**: Minimum 5 edits in lookback period

---

### GET /stats

Get overall AI learning statistics for user.

**Response**:
```json
{
  "has_writing_profile": true,
  "writing_profile_confidence": 0.85,
  "writing_profile_sample_size": 42,
  "writing_profile_last_updated": "2025-12-26T10:30:00Z",
  "total_edits_analyzed": 28,
  "avg_edit_percentage": 25.5,
  "heavy_edit_rate": 15.0,
  "has_sufficient_data": true,
  "recommendations": [
    "AI learning is optimized! Keep using GetAnswers to maintain accuracy."
  ]
}
```

**Status Codes**:
- `200 OK`: Stats retrieved
- `401 Unauthorized`: Invalid/missing token

---

## Background Tasks

All background tasks are defined in `backend/app/workers/tasks/ai_learning.py`.

### Task: `analyze_user_writing_style_task`

**Purpose**: Analyze a specific user's writing style from sent emails.

**Signature**:
```python
def analyze_user_writing_style_task(user_id: str) -> dict
```

**Trigger**:
- Manual via API (`POST /api/ai-learning/analyze`)
- After user sends 3+ emails (onboarding)
- Daily refresh for stale profiles

**Execution Time**: 10-30 seconds

**Retries**: 3 attempts with 5-minute delays

---

### Task: `analyze_user_edit_patterns_task`

**Purpose**: Analyze user's edit patterns to improve future responses.

**Signature**:
```python
def analyze_user_edit_patterns_task(user_id: str) -> dict
```

**Trigger**:
- Manual via API (`GET /api/ai-learning/edit-insights`)
- Weekly auto-analysis for users with 5+ edits

**Execution Time**: 5-15 seconds

**Retries**: 3 attempts with 5-minute delays

---

### Task: `refresh_stale_writing_profiles_task` (Periodic)

**Purpose**: Refresh writing style profiles older than 30 days.

**Schedule**: Daily at 2 AM UTC

**Execution Time**: 5-60 minutes (depends on user count)

**Logic**:
1. Find all users with profiles >30 days old
2. Queue individual analysis tasks
3. Return statistics

---

### Task: `auto_analyze_new_edits_task` (Periodic)

**Purpose**: Automatically analyze edit patterns for active users.

**Schedule**: Weekly on Sundays at 3 AM UTC

**Execution Time**: 2-30 minutes (depends on active editors)

**Logic**:
1. Find users with 5+ edits in last 7 days
2. Queue individual edit analysis tasks
3. Update writing profiles based on findings

---

### Task: `initial_writing_analysis_for_new_user_task`

**Purpose**: Trigger initial analysis for new users after onboarding.

**Signature**:
```python
def initial_writing_analysis_for_new_user_task(user_id: str) -> dict
```

**Trigger**: After user completes onboarding and sends 3+ emails

**Logic**:
1. Check if user already has profile (skip if yes)
2. Count sent emails (need minimum 3)
3. Queue analysis task

---

## Database Schema

### User Model Updates

**Table**: `users`

**New Column**:
```sql
writing_style_profile TEXT NULL
```

**Migration**: `backend/alembic/versions/010_add_writing_style_profile.py`

**Storage**: JSON string of `WritingStyleProfile`

**Example**:
```json
{
  "overall_tone": "professional",
  "formality_level": 4,
  "warmth_level": 3,
  "avg_email_length": 150,
  "prefers_concise": true,
  "uses_bullet_points": false,
  "common_greetings": ["Hi", "Hello"],
  "common_closings": ["Best regards", "Thanks"],
  "common_phrases": [],
  "uses_paragraphs": true,
  "includes_subject_lines": true,
  "acknowledges_receipt": true,
  "uses_exclamation": false,
  "uses_emojis": false,
  "shows_enthusiasm": false,
  "typical_response_time": "same-day",
  "handles_multiple_questions": "paragraphs",
  "sample_size": 42,
  "confidence": 0.85,
  "last_updated": "2025-12-26T10:30:00Z",
  "example_emails": []
}
```

**Indexing**: Not indexed (JSON blob, queried by user_id only)

**Size**: ~1-2 KB per profile

---

### Existing Schema (Edit Tracking)

**Table**: `agent_actions`

**Relevant Columns**:
```sql
proposed_content TEXT NOT NULL       -- AI-generated draft
user_edit TEXT NULL                  -- User's edited version
status VARCHAR(20)                   -- 'edited' when user modifies
approved_at TIMESTAMP                -- When user approved/edited
```

**Query for Edits**:
```sql
SELECT
  proposed_content,
  user_edit,
  approved_at
FROM agent_actions
WHERE
  conversation_id IN (
    SELECT c.id FROM conversations c
    JOIN objectives o ON c.objective_id = o.id
    WHERE o.user_id = :user_id
  )
  AND status = 'edited'
  AND user_edit IS NOT NULL
  AND approved_at >= NOW() - INTERVAL '30 days'
ORDER BY approved_at DESC
LIMIT 50;
```

---

## Frontend Integration

### Route

```typescript
/ai-learning
```

**Component**: `frontend/src/components/ai-learning/AILearningPage.tsx`

**Protection**: Requires authentication (`<ProtectedRoute>`)

---

### Features

1. **Writing Style Profile Display**
   - Tone, formality, warmth meters
   - Common greetings/closings tags
   - Metadata (confidence, sample size, last updated)

2. **Learning Statistics Cards**
   - Profile confidence percentage
   - Edits analyzed count
   - Learning status (Optimized/Learning)

3. **Recommendations Panel**
   - Actionable suggestions based on data
   - Auto-updates when stats change

4. **Manual Trigger**
   - "Analyze Now" button
   - Loading states during analysis
   - Success/error toast notifications

---

### State Management

**React Query Keys**:
```typescript
['aiProfile']       // Writing style profile
['aiStats']         // Learning statistics
```

**Mutations**:
```typescript
analyzeMutation     // POST /api/ai-learning/analyze
```

**Invalidation**:
```typescript
// After successful analysis:
queryClient.invalidateQueries({ queryKey: ['aiProfile'] });
queryClient.invalidateQueries({ queryKey: ['aiStats'] });
```

---

## Configuration

### Environment Variables

**Required**:
```bash
ANTHROPIC_API_KEY=sk-ant-...    # For Claude AI analysis
REDIS_URL=redis://...           # For Celery task queue
DATABASE_URL=postgresql://...   # For profile storage
```

**Optional**:
```bash
# Celery worker configuration
CELERY_WORKER_CONCURRENCY=4
CELERY_TASK_TIME_LIMIT=300      # 5 minutes max per task
```

---

### Celery Beat Schedule

Defined in `backend/app/workers/celery.py`:

```python
celery_app.conf.beat_schedule = {
    "refresh-stale-writing-profiles": {
        "task": "refresh_stale_writing_profiles",
        "schedule": 86400.0,  # Every 24 hours
        "options": {"expires": 3600},
    },
    "auto-analyze-new-edits": {
        "task": "auto_analyze_new_edits",
        "schedule": 604800.0,  # Every 7 days
        "options": {"expires": 3600},
    },
}
```

**To start Celery Beat**:
```bash
celery -A app.workers.celery beat --loglevel=info
```

---

## Monitoring & Metrics

### Key Metrics to Track

1. **Profile Coverage**:
   - % of users with writing profiles
   - Average profile confidence
   - Average sample size

2. **Learning Effectiveness**:
   - Average edit percentage (lower is better)
   - Heavy edit rate (>50% changes, lower is better)
   - Autonomous handling rate (higher is better)

3. **System Performance**:
   - Analysis task duration
   - Analysis task failure rate
   - API endpoint latency

4. **Cost Metrics**:
   - Claude API calls per day
   - Average cost per user analysis
   - Monthly AI spend

---

### Logging

**Log Levels**:
```python
logger.info("Writing style analyzed for user {user_id}: {sample_size} emails, confidence {confidence}")
logger.warning("Failed to load writing style profile for user {user_id}: {error}")
logger.error("Failed to analyze writing style for user {user_id}: {error}", exc_info=True)
```

**Important Events**:
- Profile created/updated
- Edit pattern analysis completed
- Background task execution
- API errors

---

### Admin Queries

**Find users without profiles**:
```sql
SELECT
  id, email, name, email_provider
FROM users
WHERE
  writing_style_profile IS NULL
  AND email_provider IS NOT NULL  -- Has email connected
  AND onboarding_completed = true
LIMIT 100;
```

**Find stale profiles**:
```sql
SELECT
  id, email,
  writing_style_profile::json->>'last_updated' as last_updated,
  writing_style_profile::json->>'sample_size' as sample_size
FROM users
WHERE
  writing_style_profile IS NOT NULL
  AND (writing_style_profile::json->>'last_updated')::timestamp < NOW() - INTERVAL '30 days'
ORDER BY (writing_style_profile::json->>'last_updated')::timestamp ASC;
```

**Count edits per user**:
```sql
SELECT
  o.user_id,
  u.email,
  COUNT(aa.id) as edit_count
FROM agent_actions aa
JOIN conversations c ON aa.conversation_id = c.id
JOIN objectives o ON c.objective_id = o.id
JOIN users u ON o.user_id = u.id
WHERE
  aa.status = 'edited'
  AND aa.user_edit IS NOT NULL
  AND aa.approved_at >= NOW() - INTERVAL '30 days'
GROUP BY o.user_id, u.email
HAVING COUNT(aa.id) >= 5
ORDER BY edit_count DESC;
```

---

## Troubleshooting

### Issue: Analysis fails with "Anthropic API key not configured"

**Cause**: `ANTHROPIC_API_KEY` environment variable not set.

**Solution**:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

Restart Celery workers.

---

### Issue: Profile always shows 0% confidence

**Cause**: User has no sent emails in the database.

**Solution**: User needs to send emails through GetAnswers first. Check:
```sql
SELECT COUNT(*) FROM messages m
JOIN conversations c ON m.conversation_id = c.id
JOIN objectives o ON c.objective_id = o.id
WHERE o.user_id = :user_id AND m.direction = 'outgoing';
```

---

### Issue: Background tasks not executing

**Cause**: Celery worker or beat not running.

**Solution**:
```bash
# Start worker
celery -A app.workers.celery worker --loglevel=info

# Start beat (in separate terminal)
celery -A app.workers.celery beat --loglevel=info
```

---

### Issue: High Claude API costs

**Cause**: Too many analyses being triggered.

**Solution**:
1. Check Celery task frequency
2. Implement rate limiting on `/analyze` endpoint
3. Increase profile cache duration
4. Monitor with:
```sql
SELECT
  DATE(writing_style_profile::json->>'last_updated') as date,
  COUNT(*) as profiles_updated
FROM users
WHERE writing_style_profile IS NOT NULL
GROUP BY DATE(writing_style_profile::json->>'last_updated')
ORDER BY date DESC;
```

---

## Development Guide

### Local Setup

1. **Install dependencies**:
```bash
pip install anthropic celery redis
```

2. **Run migrations**:
```bash
alembic upgrade head
```

3. **Start Redis**:
```bash
docker run -d -p 6379:6379 redis:alpine
```

4. **Start Celery worker**:
```bash
celery -A app.workers.celery worker --loglevel=debug
```

5. **Start Celery beat**:
```bash
celery -A app.workers.celery beat --loglevel=debug
```

6. **Test API**:
```bash
curl -X POST http://localhost:8000/api/ai-learning/analyze \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

### Adding New Learning Features

**To add a new style characteristic**:

1. Update `WritingStyleProfile` in `writing_style.py`
2. Update analysis prompt in `_build_style_analysis_prompt()`
3. Update frontend display in `AILearningPage.tsx`
4. Create migration if needed

**To add new edit pattern**:

1. Update `EditPattern` or `EditAnalysis` in `edit_learning.py`
2. Update analysis prompt in `_build_pattern_analysis_prompt()`
3. Update profile update logic in `update_writing_style_from_edits()`

---

### Testing

**Unit tests**:
```bash
pytest tests/services/test_writing_style.py
pytest tests/services/test_edit_learning.py
```

**Integration tests**:
```bash
pytest tests/api/test_ai_learning.py
```

**Manual testing**:
1. Create test user
2. Send 3+ emails
3. Trigger analysis via API
4. Check profile in database
5. Edit some AI drafts
6. Trigger edit analysis
7. Verify profile updated

---

## Best Practices

1. **Cache Aggressively**: Writing profiles are expensive to compute (~$0.30). Cache for 30 days minimum.

2. **Batch Operations**: Use background tasks for expensive operations. Never block API requests.

3. **Graceful Degradation**: If profile fails to load, fall back to default style. Don't block email processing.

4. **Monitor Costs**: Claude API calls add up. Set up billing alerts in Anthropic dashboard.

5. **Privacy First**: Never log full email content. Sanitize logs to remove PII.

6. **Incremental Updates**: Update profiles incrementally based on edits rather than full re-analysis.

7. **User Control**: Always let users delete profiles and opt out of learning.

---

## Future Enhancements

- [ ] A/B testing framework to measure learning effectiveness
- [ ] Per-sender style profiles (different style for different recipients)
- [ ] Sentiment analysis to match emotional tone
- [ ] Industry-specific terminology learning
- [ ] Multi-language support
- [ ] Real-time learning (update profile after each edit)
- [ ] Confidence calibration (track AI accuracy vs confidence scores)
- [ ] Export/import profiles between accounts

---

## Support

For questions or issues:
- **Documentation**: This file + inline code comments
- **API Docs**: http://localhost:8000/docs (when running locally)
- **Team Chat**: #engineering-ai-learning
- **Bug Reports**: GitHub Issues

---

**Last Updated**: 2025-12-26
**Maintained by**: Engineering Team
**Review Cycle**: Quarterly
