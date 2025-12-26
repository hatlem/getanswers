# GetAnswers AI Learning System - Deployment Guide

**Quick Start Guide for Deploying AI Learning Features**
**Branch**: `claude/research-competitors-4DsqA`
**Last Updated**: December 26, 2025

---

## Pre-Deployment Checklist

### 1. Environment Setup

**Required Environment Variables:**
```bash
# Already configured (verify):
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://...
SECRET_KEY=your-secret-key

# Must add:
ANTHROPIC_API_KEY=sk-ant-...   # ← NEW! Required for AI learning
```

**Get Anthropic API Key:**
1. Sign up at https://console.anthropic.com
2. Create API key
3. Add to Railway/environment config
4. Set billing limit (recommended: $100/month for testing)

---

### 2. Database Migration

**Run migration to add `writing_style_profile` column:**

```bash
# Option A: Automatic (Railway)
# Migration runs automatically on deploy via railway.json

# Option B: Manual (Local/Testing)
cd backend
alembic upgrade head
```

**Verify migration:**
```sql
-- Should show writing_style_profile column
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'users' AND column_name = 'writing_style_profile';
```

---

### 3. Deploy Backend

**Railway Deployment** (Recommended):

```bash
# Push to deploy (if Railway linked to GitHub)
git push origin claude/research-competitors-4DsqA

# OR manual deploy via Railway CLI
railway up --service backend
```

**Verify backend health:**
```bash
curl https://your-backend.railway.app/health

# Should return:
{
  "status": "healthy",
  "version": "...",
  "checks": {
    "api": true,
    "database": true,
    "redis": true
  }
}
```

---

### 4. Start Celery Workers

**Railway requires separate services for workers.**

**Option A: Railway Services** (Production):

Create two new services in Railway:

**Service 1: Celery Worker**
```json
{
  "name": "celery-worker",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "backend/Dockerfile"
  },
  "deploy": {
    "startCommand": "celery -A app.workers.celery worker --loglevel=info --concurrency=4"
  }
}
```

**Service 2: Celery Beat**
```json
{
  "name": "celery-beat",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "backend/Dockerfile"
  },
  "deploy": {
    "startCommand": "celery -A app.workers.celery beat --loglevel=info"
  }
}
```

**Option B: Local Development**:

```bash
# Terminal 1: Worker
cd backend
source .venv/bin/activate
celery -A app.workers.celery worker --loglevel=debug

# Terminal 2: Beat
cd backend
source .venv/bin/activate
celery -A app.workers.celery beat --loglevel=debug
```

**Verify Celery:**
```bash
# Check worker is connected
celery -A app.workers.celery inspect active

# Check scheduled tasks
celery -A app.workers.celery inspect scheduled
```

---

### 5. Deploy Frontend

**Railway Deployment:**

```bash
railway up --service frontend
```

**Verify frontend:**
- Visit https://your-frontend.railway.app
- Navigate to `/ai-learning`
- Should see AI Learning dashboard (may show "No Profile Yet")

---

## Post-Deployment Verification

### 1. Test API Endpoints

```bash
# Get your auth token first
TOKEN="your-jwt-token"

# Test AI learning profile endpoint
curl https://your-backend.railway.app/api/ai-learning/profile \
  -H "Authorization: Bearer $TOKEN"

# Should return:
{
  "has_profile": false,
  "profile": null,
  "sample_size": 0,
  "confidence": 0.0
}
```

---

### 2. Test Analysis (Manual Trigger)

**Trigger analysis for a test user:**

```bash
# Option A: Via API
curl -X POST https://your-backend.railway.app/api/ai-learning/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'

# Option B: Via admin endpoint (super admin only)
curl -X POST https://your-backend.railway.app/api/admin/ai-learning/trigger-analysis/USER_ID \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Expected:**
- Returns `{ "success": true, "message": "Successfully analyzed X emails" }`
- Or `{ "success": false, "reason": "Insufficient sent emails" }` if user has <3 emails

---

### 3. Monitor Background Tasks

**Check Celery logs:**

```bash
# Railway: View logs in dashboard for celery-worker service

# Local: See terminal output

# Look for:
[INFO] Writing style analyzed for user {...}
[INFO] Queued initial AI learning analysis for user {...}
[INFO] Auto edit analysis completed: X analyses queued
```

**Check task success:**
```bash
# In Python console or admin endpoint
from app.workers.celery import celery_app
result = celery_app.control.inspect().stats()
print(result)  # Should show worker stats
```

---

### 4. Test Full User Flow

**End-to-end test:**

1. **Create test user**
   - Sign up at `/signup`
   - Complete onboarding

2. **Send test emails**
   - Connect Gmail
   - Send 3+ test emails through GetAnswers

3. **Wait for analysis**
   - Check Celery logs for task execution
   - Should see "Queued initial AI learning analysis"
   - Analysis completes in 10-30 seconds

4. **View profile**
   - Navigate to `/ai-learning`
   - Should see profile with confidence score
   - Should see greetings, closings, tone

5. **Test edit learning**
   - Let AI draft a response
   - Edit the draft (change tone, add phrases)
   - Approve
   - After 5 edits, edit analysis should trigger

---

## Monitoring & Observability

### 1. Admin Dashboard

**Access admin analytics:**
```bash
curl https://your-backend.railway.app/api/admin/ai-learning/overview \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Should return:**
```json
{
  "total_users": 10,
  "users_with_profiles": 5,
  "profile_coverage_percent": 50.0,
  "avg_profile_confidence": 0.82,
  "total_edits_all_time": 45,
  "stale_profiles_count": 2,
  "users_needing_analysis": 3
}
```

---

### 2. Cost Monitoring

**Set up Anthropic alerts:**
1. Go to https://console.anthropic.com
2. Navigate to Billing → Usage
3. Set monthly budget alert (e.g., $100)
4. Monitor daily spend

**Expected costs (1000 users):**
- Writing style analysis: $0.30 per user
- Cache duration: 30 days
- Monthly refresh: ~$10-30/month
- Very cost-effective!

---

### 3. Performance Metrics

**Track these metrics weekly:**

```sql
-- Profile coverage
SELECT
  COUNT(*) FILTER (WHERE writing_style_profile IS NOT NULL) * 100.0 / COUNT(*) as coverage_percent
FROM users
WHERE email_provider IS NOT NULL;

-- Average confidence
SELECT
  AVG((writing_style_profile::json->>'confidence')::float) as avg_confidence
FROM users
WHERE writing_style_profile IS NOT NULL;

-- Recent analyses
SELECT
  DATE(writing_style_profile::json->>'last_updated') as date,
  COUNT(*) as profiles_updated
FROM users
WHERE writing_style_profile IS NOT NULL
GROUP BY date
ORDER BY date DESC
LIMIT 7;
```

---

### 4. Error Monitoring

**Common issues and fixes:**

**Issue**: "Anthropic API key not configured"
```bash
# Fix: Add environment variable
railway variables set ANTHROPIC_API_KEY=sk-ant-...
```

**Issue**: Celery worker not processing tasks
```bash
# Fix: Restart worker service
railway restart --service celery-worker
```

**Issue**: Analysis always fails
```bash
# Check logs for specific error
railway logs --service celery-worker

# Common causes:
# - Invalid API key
# - Rate limiting (increase retry delay)
# - Network issues (check Redis connection)
```

---

## Rollout Strategy

### Phase 1: Soft Launch (Week 1)

**Enable for 10% of users:**
```python
# In onboarding endpoint, add flag:
if user.id.int % 10 == 0:  # 10% sample
    initial_writing_analysis_for_new_user_task.delay(str(user.id))
```

**Monitor:**
- Profile creation success rate
- Analysis duration
- Error rates
- User feedback

**Success Criteria:**
- >90% analysis success rate
- <30 second average duration
- <5% error rate
- Positive user feedback

---

### Phase 2: Gradual Rollout (Weeks 2-3)

**Increase to 50%, then 100%:**
```python
# Week 2: 50%
if user.id.int % 2 == 0:
    initial_writing_analysis_for_new_user_task.delay(str(user.id))

# Week 3: 100%
# Remove flag, enable for all
initial_writing_analysis_for_new_user_task.delay(str(user.id))
```

---

### Phase 3: Existing Users (Week 4)

**Backfill for existing users:**
```bash
# Use admin endpoint to trigger bulk analysis
curl -X POST https://your-backend.railway.app/api/admin/ai-learning/trigger-bulk-analysis \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"only_missing": true}'
```

**Or let background tasks handle it:**
- Daily task will automatically analyze users without profiles
- Spread over 7-14 days to avoid cost spike

---

## Rollback Procedure

**If critical issues occur:**

### 1. Stop New Analyses
```bash
# Stop Celery beat (prevents periodic tasks)
railway stop --service celery-beat

# Stop Celery worker (prevents new tasks)
railway stop --service celery-worker
```

### 2. Revert API Changes
```bash
# Deploy previous version
git checkout <previous-commit>
railway up --service backend
```

### 3. Database Rollback (if needed)
```bash
# Rollback migration
alembic downgrade -1

# This removes writing_style_profile column
# Existing profiles are lost (acceptable in rollback)
```

### 4. Frontend Rollback
```bash
# Frontend continues to work
# /ai-learning page will show 404 (acceptable)
# No user-facing breakage
```

**Note**: AI learning is non-critical. Rollback has minimal user impact.

---

## Launch Communication

### Internal Team

**Engineering:**
- Share `AI_LEARNING_SYSTEM.md`
- Demo admin dashboard
- Review Celery monitoring

**Product:**
- Share `COMPETITIVE_ENHANCEMENTS_SUMMARY.md`
- Review user dashboard
- Discuss metrics

**Sales:**
- Share `SALES_BATTLECARDS.md`
- Demo AI learning in calls
- Review competitive positioning

**Marketing:**
- Use comparison pages
- Blog post draft
- Social media assets

---

### External (Users)

**Email announcement template:**

```
Subject: GetAnswers Now Learns Your Writing Style 🤖

Hi {name},

We've added something no other AI email tool has: **AI that learns your unique writing style**.

What's new:
- Analyzes your sent emails to learn your tone and patterns
- Generates responses that sound authentically like you
- Improves continuously from your edits
- Complete transparency - see what it learned at /ai-learning

This means:
✓ Less editing needed
✓ Higher quality first drafts
✓ Better autonomous handling

Visit your AI Learning dashboard to see your profile:
{app_url}/ai-learning

Questions? Reply to this email.

- The GetAnswers Team
```

---

## Success Metrics Dashboard

**Track weekly:**

| Metric | Week 1 | Week 2 | Week 3 | Week 4 | Target |
|--------|--------|--------|--------|--------|--------|
| Profile Coverage % | __% | __% | __% | __% | 70% |
| Avg Confidence | __ | __ | __ | __ | 0.75 |
| Analysis Success % | __% | __% | __% | __% | 95% |
| Edit Rate Reduction | __% | __% | __% | __% | 15% |
| Monthly AI Cost | $__ | $__ | $__ | $__ | <$100 |
| User NPS | __ | __ | __ | __ | 50+ |

---

## Quick Reference

### Essential Commands

```bash
# Deploy everything
railway up

# Check health
curl https://api.getanswers.co/health

# View Celery logs
railway logs --service celery-worker

# Trigger analysis
curl -X POST https://api.getanswers.co/api/ai-learning/analyze \
  -H "Authorization: Bearer $TOKEN"

# Admin dashboard
curl https://api.getanswers.co/api/admin/ai-learning/overview \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

### Support Contacts

- **Engineering Issues**: Check `AI_LEARNING_SYSTEM.md` → Troubleshooting
- **Celery Problems**: Check worker/beat logs
- **API Errors**: Check Sentry error tracking
- **Cost Concerns**: Check Anthropic dashboard billing

---

## Next Steps After Deployment

1. **Monitor for 24 hours** - Watch logs, check errors
2. **Analyze metrics** - Review admin dashboard daily
3. **Gather feedback** - Ask early users about AI quality
4. **Iterate** - Adjust based on data
5. **Scale** - Increase rollout percentage
6. **Celebrate** - You shipped a competitive moat! 🎉

---

**Deployment Status**: Ready for production ✅
**Estimated Deployment Time**: 2-4 hours
**Risk Level**: Low (graceful degradation built-in)

---

**Questions?** See `AI_LEARNING_SYSTEM.md` for detailed technical docs.
