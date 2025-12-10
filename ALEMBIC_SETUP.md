# Alembic Database Migrations Setup

This document describes the Alembic database migration setup for the GetAnswers project.

## Overview

Alembic has been successfully configured for managing database schema migrations. The setup includes:

- Async PostgreSQL support
- All existing SQLAlchemy models captured in initial migration
- Helper scripts for common migration tasks
- Docker integration for automatic migrations on startup

## Files Created

### Configuration Files

1. **`backend/alembic.ini`**
   - Main Alembic configuration file
   - Logging configuration
   - Migration script location

2. **`backend/alembic/env.py`**
   - Alembic environment setup with async support
   - Imports all models for autogenerate
   - Configured to use settings.DATABASE_URL

3. **`backend/alembic/script.py.mako`**
   - Template for generating new migration files

### Migration Files

4. **`backend/alembic/versions/001_initial_schema.py`**
   - Initial database schema migration
   - Includes all 7 models:
     - `users` - User accounts with authentication
     - `magic_links` - Passwordless auth tokens
     - `objectives` - User missions/goals
     - `policies` - Automation rules
     - `conversations` - Email threads
     - `messages` - Individual emails
     - `agent_actions` - AI action audit logs
   - All tables use UUID primary keys
   - Proper foreign key constraints with CASCADE deletes
   - Indexes on frequently queried columns

### Helper Scripts

5. **`backend/scripts/migrate.py`**
   - Helper script for common migration commands
   - Usage:
     ```bash
     python scripts/migrate.py upgrade      # Apply migrations
     python scripts/migrate.py downgrade    # Rollback one migration
     python scripts/migrate.py revision "msg" # Create new migration
     python scripts/migrate.py current      # Show current version
     python scripts/migrate.py history      # Show migration history
     ```

### Documentation

6. **`backend/alembic/README.md`**
   - Comprehensive guide to using Alembic
   - Common commands and best practices
   - Troubleshooting tips

## Changes Made to Existing Files

### 1. `backend/app/core/database.py`
**Removed:**
- `init_db()` function that auto-created tables
- Tables are now created via Alembic migrations only

**Kept:**
- Session management functions
- Database engine configuration
- `close_db()` function for cleanup

### 2. `backend/app/main.py`
**Updated:**
- Removed `init_db` import
- Removed `init_db()` call from lifespan
- Added log message noting migrations are handled by Alembic

### 3. `backend/Dockerfile`
**Updated:**
- Modified CMD to run `alembic upgrade head` before starting uvicorn
- Ensures database is migrated before API starts
- Only runs migrations for API server (not for worker/beat processes)

**New CMD:**
```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. `backend/requirements.txt`
**Already had:**
- `alembic==1.14.0` (no changes needed)

## Usage Guide

### Initial Setup

1. **Apply initial migration:**
   ```bash
   cd backend
   alembic upgrade head
   ```

2. **Verify migration:**
   ```bash
   alembic current
   # Should show: 001 (head)
   ```

### Creating New Migrations

1. **Modify models in `backend/app/models/`**
   - Add/remove columns
   - Add/remove tables
   - Change constraints

2. **Generate migration:**
   ```bash
   cd backend
   alembic revision --autogenerate -m "add column xyz to users"
   ```

3. **Review generated migration:**
   - Check `backend/alembic/versions/{new_revision}.py`
   - Verify upgrade() and downgrade() functions
   - Make manual adjustments if needed

4. **Apply migration:**
   ```bash
   alembic upgrade head
   ```

### Common Commands

```bash
# Show current database version
alembic current

# Show migration history
alembic history --verbose

# Apply all pending migrations
alembic upgrade head

# Apply specific number of migrations
alembic upgrade +2

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade abc123

# Show SQL that would be executed (without running)
alembic upgrade head --sql

# Stamp database at specific revision (without running migrations)
alembic stamp head
```

### Docker/Production Usage

Migrations run automatically when the container starts:

```bash
# Build and run
docker build -t getanswers-backend .
docker run -p 8000:8000 getanswers-backend

# The container will:
# 1. Run: alembic upgrade head
# 2. Then: uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Database Schema

### Initial Schema (001_initial_schema.py)

All tables use PostgreSQL UUID primary keys and proper timestamps.

**Tables:**
1. **users**
   - Authentication and profile information
   - Autonomy level settings
   - Gmail OAuth credentials (encrypted JSON)

2. **magic_links**
   - Passwordless authentication tokens
   - Expiration tracking
   - Optional FK to users (nullable for new signups)

3. **objectives**
   - User missions/goals
   - Status tracking (waiting_on_you, waiting_on_others, handled, scheduled, muted)

4. **policies**
   - User-defined automation rules
   - JSON rules field for flexibility
   - Active/inactive toggle

5. **conversations**
   - Email thread tracking
   - Gmail thread ID linkage
   - Participant list (JSON array)

6. **messages**
   - Individual emails
   - Direction (incoming/outgoing)
   - Text and HTML body
   - Gmail message ID (unique)

7. **agent_actions**
   - AI action audit log
   - Risk assessment (high/medium/low)
   - Status tracking (pending/approved/rejected/edited)
   - User feedback and edits

### Foreign Key Relationships

```
users (1) -> (N) magic_links
users (1) -> (N) objectives
users (1) -> (N) policies
objectives (1) -> (N) conversations
conversations (1) -> (N) messages
conversations (1) -> (N) agent_actions
```

All foreign keys use `CASCADE` on delete.

### Indexes

- `users.email` (unique)
- `magic_links.token` (unique)
- `magic_links.user_id`
- `objectives.user_id`
- `policies.user_id`
- `conversations.objective_id`
- `conversations.gmail_thread_id`
- `messages.conversation_id`
- `messages.gmail_message_id` (unique)
- `agent_actions.conversation_id`

## Best Practices

1. **Always review auto-generated migrations** before applying
2. **Test migrations on development database first**
3. **Never edit applied migrations** - create a new one instead
4. **Keep migrations small and focused**
5. **Write descriptive migration messages**
6. **Commit migrations with code changes**
7. **Use transactions** (Alembic does this by default)
8. **Backup database before running migrations in production**

## Troubleshooting

### Database out of sync

If you already created tables manually:

```bash
# Stamp database as current without running migrations
alembic stamp head
```

### Migration fails partway

1. Check error message
2. Manually fix database state if needed
3. Fix migration file
4. Re-run migration

### Need to reset database

```bash
# Drop all tables
alembic downgrade base

# Or in PostgreSQL:
# DROP SCHEMA public CASCADE;
# CREATE SCHEMA public;

# Then apply all migrations
alembic upgrade head
```

## Testing

### Test migrations locally

```bash
# Apply migration
alembic upgrade head

# Test rollback
alembic downgrade -1

# Re-apply
alembic upgrade head
```

### Verify schema

```bash
# Connect to PostgreSQL
psql $DATABASE_URL

# List tables
\dt

# Describe table
\d users

# Check migration version
SELECT * FROM alembic_version;
```

## Next Steps

1. **Apply initial migration** to your database
2. **Test the setup** by creating a test migration
3. **Update CI/CD** to run migrations in deployment pipeline
4. **Set up database backups** before running migrations in production
5. **Document any custom migration patterns** your team develops

## References

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [PostgreSQL UUID Type](https://www.postgresql.org/docs/current/datatype-uuid.html)

---

**Setup completed on:** 2025-12-10
**Alembic version:** 1.14.0
**Python version:** 3.12
**Database:** PostgreSQL with asyncpg driver
