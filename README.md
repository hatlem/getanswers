# GetAnswers - AI Email Agent

> **Other tools help you organize email. GetAnswers actually writes your responses.**
>
> An AI agent that drafts complete email replies in your voice. You just approve, edit, or escalate. 80%+ of emails handled autonomously, saving you 2+ hours daily.

## What Makes GetAnswers Different

Unlike traditional email clients (Superhuman, Hey.com) or AI assistants (Ellie, Compose AI), GetAnswers is a **complete AI email agent** with:

- ✅ **Complete AI Response Generation** - Not just suggestions or autocomplete
- ✅ **Approval Queue Workflow** - One-click approve/edit/escalate
- ✅ **Confidence Scoring** - AI tells you how certain it is (0-100%)
- ✅ **Risk Assessment** - Automatic categorization (low/medium/high)
- ✅ **Autonomous Handling** - 80%+ of emails sent without manual work
- ✅ **Complete Audit Trail** - Full history of AI actions

**See detailed comparisons**: [GetAnswers vs Competitors](/compare)

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         RAILWAY                                  │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Frontend   │  │   Backend    │  │    Worker    │          │
│  │   (React)    │──│  (FastAPI)   │──│  (Celery)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                 │                  │                  │
│         │          ┌──────┴──────┐          │                  │
│         │          │             │          │                  │
│         │       ┌──▼────────┐ ┌──▼────────┐                   │
│         │       │PostgreSQL │ │  Redis    │                   │
│         │       └───────────┘ └───────────┘                   │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
        ┌─────▼─────┐   ┌─────▼─────┐   ┌────▼────┐
        │ Gmail API │   │ Claude API│   │ Volume  │
        └───────────┘   └───────────┘   └─────────┘
```

## Tech Stack

- **Frontend**: React + TypeScript + Vite + Tailwind CSS + Framer Motion
- **Backend**: Python FastAPI + SQLAlchemy (async)
- **Database**: PostgreSQL (Railway)
- **Cache/Queue**: Redis (Railway)
- **Auth**: Magic Link + Password (dual option)
- **Email**: Gmail API (OAuth)
- **AI**: Claude API (Anthropic)
- **Deploy**: Railway

## Project Structure

```
getanswers/
├── frontend/                    # React app
│   ├── src/
│   │   ├── components/          # UI components
│   │   │   ├── layout/          # TopNav, LeftColumn, CenterColumn, RightColumn
│   │   │   ├── cards/           # ActionCard, ConfidenceMeter
│   │   │   └── timeline/        # ConversationTimeline, TimelineItem
│   │   ├── stores/              # Zustand state management
│   │   ├── types/               # TypeScript types
│   │   └── lib/                 # Utilities and mock data
│   └── ...
│
├── backend/                     # Python FastAPI
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── api/                 # API routes (auth, queue)
│   │   ├── core/                # Config, database, security
│   │   ├── models/              # SQLAlchemy models
│   │   ├── services/            # Business logic (gmail, agent, triage)
│   │   └── workers/             # Background tasks
│   ├── requirements.txt
│   └── Dockerfile
│
├── railway.json                 # Railway config
└── README.md
```

## Local Development

### Prerequisites

- Node.js 20+
- Python 3.12+
- Railway CLI (`npm i -g @railway/cli`)
- Railway project with PostgreSQL and Redis

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5073
```

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Copy .env.example to .env and fill in Railway database URLs

# Run the server
uvicorn app.main:app --reload --port 8000
```

### Getting Railway Database URLs

```bash
# Link to Railway project
railway link

# Get PostgreSQL URL
railway variables -s postgres

# Get Redis URL
railway variables -s redis
```

## Railway Deployment

### 1. Create Services

In the Railway dashboard, add:
- PostgreSQL database
- Redis database
- Backend service (from /backend directory)
- Frontend service (from /frontend directory)

### 2. Environment Variables

Set these in the backend service:

```
DATABASE_URL=<Railway PostgreSQL URL with asyncpg driver>
REDIS_URL=<Railway Redis URL>
SECRET_KEY=<random string>
ANTHROPIC_API_KEY=<your key>
GMAIL_CLIENT_ID=<Google OAuth client ID>
GMAIL_CLIENT_SECRET=<Google OAuth secret>
APP_URL=<frontend Railway URL>
```

### 3. Deploy

Railway auto-deploys on git push, or:

```bash
railway up
```

## API Endpoints

### Authentication

```
POST /api/auth/register      # Create account (email + password)
POST /api/auth/login         # Login with password
POST /api/auth/magic-link    # Request magic link email
GET  /api/auth/verify        # Verify magic link token
GET  /api/auth/me            # Get current user
```

### Review Queue

```
GET  /api/queue                    # Get items needing decision
POST /api/queue/{id}/approve       # Approve AI action
POST /api/queue/{id}/override      # Reject AI action
POST /api/queue/{id}/edit          # Edit and send
POST /api/queue/{id}/escalate      # Escalate for review
```

### Stats

```
GET /api/stats               # Get efficiency metrics
```

## Core Concepts

### Objective
A "mission" that groups related email threads. Example: "Negotiate Q4 payment terms"

### Conversation
A thread of emails under an objective, linked to Gmail thread ID.

### Agent Action
Every AI decision is logged with confidence score, risk level, and status (pending/approved/rejected).

### Policy
User-defined rules that guide the AI agent's behavior and autonomy level.

## UI States

| State | Description |
|-------|-------------|
| **Needs My Decision** | High-risk or low-confidence items requiring human review |
| **Waiting on Others** | Tracking external dependencies |
| **Handled by AI** | Autonomously processed items (audit trail) |
| **Scheduled & Done** | Confirmed actions (meetings, tasks) |
| **Muted / Ignored** | Low-priority items |

## License

MIT
