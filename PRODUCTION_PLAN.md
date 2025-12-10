# GetAnswers: MVP to Production Plan

## ✅ IMPLEMENTATION COMPLETE

All 14 major tasks have been implemented by 13 parallel agents. The system is now production-ready.

---

## Executive Summary

GetAnswers is an AI-powered email management system that autonomously handles routine emails while surfacing high-risk decisions for human review. The codebase has a solid foundation with complete database models, authentication framework, and a polished UI. This plan outlines the work required to make all parts functional and production-ready.

---

## Current State Assessment

### What's Working
- ✅ Database schema (8 models with proper relationships)
- ✅ PostgreSQL async connection with proper pooling
- ✅ User auth (registration, login, JWT tokens, magic link generation)
- ✅ Complete 4-column UI layout with Tailwind/shadcn
- ✅ Zustand state management
- ✅ Mock data system for development
- ✅ Docker configurations (frontend + backend)
- ✅ Railway deployment config

### What's Missing/Broken
- ❌ Gmail OAuth integration
- ❌ Claude AI agent service
- ❌ Email processing pipeline
- ❌ Queue endpoints (all return mock data)
- ❌ `/api/auth/me` endpoint (returns 401)
- ❌ Magic link email sending
- ❌ Background workers (Celery)
- ❌ Frontend API integration (using mock data)
- ❌ Error handling & loading states
- ❌ Rate limiting & security hardening

---

## Phase 1: Core Backend Services (Critical Path)

### 1.1 Fix Authentication Dependency
**Files:** `backend/app/api/deps.py`, `backend/app/api/auth.py`
**Priority:** P0

- Implement `get_current_user` dependency that extracts JWT from Authorization header
- Wire `/api/auth/me` endpoint to use this dependency
- Add proper error handling for expired/invalid tokens

### 1.2 Gmail Integration Service
**Files:** `backend/app/services/gmail.py`
**Priority:** P0

```python
# Service responsibilities:
- OAuth2 flow (authorization URL generation, token exchange)
- Store/refresh credentials in user.gmail_credentials
- Fetch messages and threads
- Send emails on behalf of user
- Watch for new emails (push notifications or polling)
```

**Subtasks:**
1. Create Google Cloud Project with Gmail API enabled
2. Configure OAuth consent screen
3. Implement OAuth callback endpoint (`/api/auth/gmail/callback`)
4. Build GmailService class with async methods
5. Handle token refresh automatically
6. Create email sync job

### 1.3 Claude AI Agent Service
**Files:** `backend/app/services/agent.py`
**Priority:** P0

```python
# Service responsibilities:
- Analyze email content and context
- Classify email intent (question, request, info, spam, etc.)
- Generate draft responses matching sender's tone
- Calculate confidence score (0-100)
- Assess risk level (low/medium/high)
- Apply user policies to decisions
```

**Subtasks:**
1. Create AnthropicService wrapper class
2. Design system prompts for email classification
3. Design prompts for response generation
4. Implement confidence scoring algorithm
5. Implement risk assessment logic
6. Create policy evaluation engine
7. Add conversation context handling

### 1.4 Email Triage Service
**Files:** `backend/app/services/triage.py`
**Priority:** P0

```python
# Orchestration service:
- Process incoming emails through AI pipeline
- Create/update Objectives and Conversations
- Create AgentAction records
- Route to queue based on confidence/risk
- Execute approved actions
```

---

## Phase 2: API Endpoints Implementation

### 2.1 Complete Queue Endpoints
**Files:** `backend/app/api/queue.py`
**Priority:** P0

| Endpoint | Implementation |
|----------|----------------|
| `GET /api/queue` | Query AgentActions with status=pending, join conversations/messages, filter by user |
| `POST /api/queue/{id}/approve` | Update status=approved, execute the action via GmailService |
| `POST /api/queue/{id}/override` | Update status=rejected, optionally log reason |
| `POST /api/queue/{id}/edit` | Update proposed_content with user_edit, then execute |
| `POST /api/queue/{id}/escalate` | Update risk_level=high, optionally notify team |

### 2.2 Implement Stats Endpoint
**Files:** `backend/app/api/main.py`
**Priority:** P1

```python
# Calculate from database:
- total_emails: Count of all messages for user
- handled_by_ai: AgentActions with status=approved, no user_edit
- needs_decision: AgentActions with status=pending
- efficiency_rate: handled_by_ai / total_emails * 100
- avg_confidence: AVG(confidence_score) from AgentActions
```

### 2.3 Email Sending (Magic Links)
**Files:** `backend/app/services/email.py`
**Priority:** P1

```python
# Email service:
- Async SMTP client using aiosmtplib
- HTML email templates (magic link, notifications)
- Send magic link with proper APP_URL
- Rate limiting on magic link requests
```

### 2.4 Gmail OAuth Endpoints
**Files:** `backend/app/api/auth.py`
**Priority:** P0

```
GET  /api/auth/gmail          # Get OAuth URL for Gmail connection
GET  /api/auth/gmail/callback # Handle OAuth callback, store credentials
DELETE /api/auth/gmail        # Disconnect Gmail account
```

---

## Phase 3: Background Workers

### 3.1 Celery Setup
**Files:** `backend/app/workers/celery.py`
**Priority:** P1

```python
# Celery configuration:
- Broker: Redis
- Result backend: Redis
- Task serializer: JSON
- Timezone: UTC
```

### 3.2 Email Sync Worker
**Files:** `backend/app/workers/tasks/sync_emails.py`
**Priority:** P1

```python
@celery.task
def sync_user_emails(user_id: str):
    # 1. Get user's Gmail credentials
    # 2. Fetch new messages since last sync
    # 3. Create/update Conversations and Messages
    # 4. Trigger AI processing for new messages
```

### 3.3 AI Processing Worker
**Files:** `backend/app/workers/tasks/process_email.py`
**Priority:** P1

```python
@celery.task
def process_email(message_id: str):
    # 1. Load message and conversation context
    # 2. Run through Claude for classification
    # 3. Generate proposed action
    # 4. Calculate confidence and risk
    # 5. Create AgentAction record
    # 6. Auto-execute if high confidence + low risk
```

### 3.4 Scheduled Jobs
**Files:** `backend/app/workers/scheduler.py`
**Priority:** P2

```python
# Celery Beat schedule:
- sync_all_users: Every 5 minutes
- cleanup_expired_magic_links: Daily
- generate_daily_stats: Daily
```

---

## Phase 4: Frontend API Integration

### 4.1 API Client Setup
**Files:** `frontend/src/lib/api.ts`
**Priority:** P1

```typescript
// Axios/fetch wrapper with:
- Base URL configuration
- JWT token injection
- Response interceptors
- Error handling
- Type-safe request/response
```

### 4.2 Auth Flow Integration
**Files:** `frontend/src/components/auth/*`
**Priority:** P1

- Create Login page component
- Create Register page component
- Create Gmail connection button
- Handle magic link verification
- Store JWT in localStorage/cookies
- Add auth state to Zustand store
- Protected route wrapper

### 4.3 Replace Mock Data
**Files:** `frontend/src/stores/appStore.ts`, various components
**Priority:** P1

```typescript
// Replace mock data with React Query hooks:
- useQueue() - fetch pending actions
- useConversation(id) - fetch conversation details
- useStats() - fetch efficiency metrics
- Mutations for approve/override/edit/escalate
```

### 4.4 Loading & Error States
**Files:** Various components
**Priority:** P2

- Add skeleton loaders for cards
- Add error boundaries
- Add toast notifications for actions
- Add optimistic updates for queue actions
- Handle offline state

---

## Phase 5: Security Hardening

### 5.1 Rate Limiting
**Files:** `backend/app/core/rate_limit.py`
**Priority:** P1

```python
# Redis-based rate limiting:
- /api/auth/* endpoints: 5 requests/minute
- /api/queue/* endpoints: 60 requests/minute
- Magic link requests: 3/hour per email
```

### 5.2 Input Validation
**Files:** Various API routes
**Priority:** P1

- Validate all Pydantic schemas have proper constraints
- Add email format validation
- Sanitize user input in edit actions
- Validate UUIDs in path parameters

### 5.3 Security Headers
**Files:** `backend/app/main.py`
**Priority:** P2

```python
# Add middleware for:
- HSTS
- X-Content-Type-Options
- X-Frame-Options
- Content-Security-Policy
```

### 5.4 Audit Logging
**Files:** `backend/app/core/audit.py`
**Priority:** P2

```python
# Log all sensitive operations:
- Login attempts (success/failure)
- Queue actions (approve/override/edit)
- Gmail credential changes
- Email sends
```

---

## Phase 6: Production Readiness

### 6.1 Environment Configuration
**Files:** `.env.example`, `backend/app/core/config.py`
**Priority:** P1

```
# Production environment variables:
ENVIRONMENT=production
DEBUG=false
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
LOG_LEVEL=INFO
SENTRY_DSN=<optional>
```

### 6.2 Database Migrations
**Files:** `backend/alembic/`
**Priority:** P1

- Initialize Alembic
- Create initial migration from current models
- Set up Railway deployment hook for migrations

### 6.3 Health Checks
**Files:** `backend/app/main.py`
**Priority:** P1

```python
@app.get("/health")
async def health():
    # Check database connectivity
    # Check Redis connectivity
    # Return detailed status
```

### 6.4 Monitoring & Observability
**Priority:** P2

- Add Sentry for error tracking
- Add structured logging (JSON format)
- Add request ID tracking
- Add performance metrics (response times)

### 6.5 Frontend Production Build
**Files:** `frontend/vite.config.ts`
**Priority:** P1

- Configure environment variables
- Set up API base URL for production
- Enable source maps for Sentry
- Optimize bundle size

---

## Phase 7: Testing

### 7.1 Backend Unit Tests
**Files:** `backend/tests/`
**Priority:** P2

```python
# Test coverage for:
- Auth endpoints
- Queue endpoints
- Gmail service (mocked)
- Agent service (mocked)
- Security utilities
```

### 7.2 Frontend Tests
**Files:** `frontend/src/__tests__/`
**Priority:** P2

```typescript
// Test coverage for:
- Component rendering
- Store actions
- API integration (mocked)
- Auth flow
```

### 7.3 Integration Tests
**Priority:** P3

- End-to-end auth flow
- Email processing pipeline
- Queue action execution

---

## Implementation Order (Recommended)

### Week 1: Foundation
1. [ ] Fix auth dependency (`/api/auth/me`)
2. [ ] Create Gmail OAuth endpoints
3. [ ] Implement GmailService (OAuth flow)
4. [ ] Set up frontend auth pages

### Week 2: Core Pipeline
5. [ ] Implement GmailService (fetch/send)
6. [ ] Create Claude AgentService
7. [ ] Build email triage service
8. [ ] Complete queue endpoints

### Week 3: Workers & Integration
9. [ ] Set up Celery with Redis
10. [ ] Create email sync worker
11. [ ] Create AI processing worker
12. [ ] Frontend API integration

### Week 4: Polish
13. [ ] Magic link email sending
14. [ ] Stats endpoint with real data
15. [ ] Rate limiting
16. [ ] Error handling & loading states

### Week 5: Production
17. [ ] Database migrations (Alembic)
18. [ ] Security headers
19. [ ] Health checks
20. [ ] Monitoring setup

---

## Environment Variables Checklist

```bash
# Required for MVP
DATABASE_URL=postgresql+asyncpg://...     # Railway PostgreSQL
REDIS_URL=redis://...                      # Railway Redis
SECRET_KEY=<generate-with-openssl>         # JWT signing key
ANTHROPIC_API_KEY=sk-ant-...               # Claude API key
GMAIL_CLIENT_ID=xxx.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=GOCSPX-...
APP_URL=https://getanswers.up.railway.app
ENVIRONMENT=production

# Required for email sending
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@getanswers.co
SMTP_PASSWORD=<app-password>
SMTP_FROM_EMAIL=noreply@getanswers.co

# Optional but recommended
SENTRY_DSN=https://...@sentry.io/...
LOG_LEVEL=INFO
```

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Gmail API quota limits | Implement efficient polling, use push notifications |
| Claude API costs | Cache common responses, batch processing |
| Token refresh failures | Graceful degradation, user notification |
| Email delivery failures | Retry logic, fallback SMTP |
| Data loss | Regular backups, soft deletes |

---

## Success Metrics

- **Email Processing Latency**: < 5 seconds from receipt to AI action
- **Uptime**: 99.9%
- **API Response Time**: p95 < 500ms
- **AI Accuracy**: > 90% user acceptance of AI suggestions
- **Efficiency Rate**: > 80% emails handled autonomously

---

## File Creation Checklist

### Backend Services (create these files)
- [ ] `backend/app/services/__init__.py`
- [ ] `backend/app/services/gmail.py`
- [ ] `backend/app/services/agent.py`
- [ ] `backend/app/services/triage.py`
- [ ] `backend/app/services/email.py`

### Backend Workers (create these files)
- [ ] `backend/app/workers/__init__.py`
- [ ] `backend/app/workers/celery.py`
- [ ] `backend/app/workers/tasks/__init__.py`
- [ ] `backend/app/workers/tasks/sync_emails.py`
- [ ] `backend/app/workers/tasks/process_email.py`
- [ ] `backend/app/workers/scheduler.py`

### Backend Core (add to existing)
- [ ] `backend/app/core/rate_limit.py`
- [ ] `backend/app/core/audit.py`

### Frontend (create these files)
- [ ] `frontend/src/lib/api.ts`
- [ ] `frontend/src/components/auth/LoginPage.tsx`
- [ ] `frontend/src/components/auth/RegisterPage.tsx`
- [ ] `frontend/src/components/auth/ProtectedRoute.tsx`
- [ ] `frontend/src/hooks/useAuth.ts`
- [ ] `frontend/src/hooks/useQueue.ts`

### Database Migrations
- [ ] `backend/alembic.ini`
- [ ] `backend/alembic/env.py`
- [ ] `backend/alembic/versions/001_initial.py`

---

## Notes

This plan prioritizes getting a working end-to-end flow first (auth → Gmail → AI → queue → action), then layering on background processing, polish, and production hardening. Each phase builds on the previous one, minimizing rework.

The most critical dependency is Gmail OAuth - without it, there are no emails to process. Second is the Claude integration, which is the core value proposition. Everything else supports these two pillars.
