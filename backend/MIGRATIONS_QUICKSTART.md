# Database Migrations Quick Start

Quick reference for common Alembic migration tasks.

## First Time Setup

```bash
cd backend
alembic upgrade head
```

## Daily Workflow

### 1. After changing models

```bash
# Generate migration from model changes
alembic revision --autogenerate -m "description of changes"

# Review the generated file in alembic/versions/
# Edit if needed

# Apply migration
alembic upgrade head
```

### 2. After pulling code with new migrations

```bash
# Apply all pending migrations
alembic upgrade head
```

### 3. Testing a migration

```bash
# Apply migration
alembic upgrade head

# Test your code...

# If something's wrong, rollback
alembic downgrade -1

# Fix the migration file
# Re-apply
alembic upgrade head
```

## Most Common Commands

```bash
# Check current version
alembic current

# See pending migrations
alembic history

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Create new migration (manual)
alembic revision -m "add column xyz"

# Create migration from model changes (auto)
alembic revision --autogenerate -m "description"
```

## Using Helper Script

```bash
cd backend

# Apply migrations
python scripts/migrate.py upgrade

# Rollback
python scripts/migrate.py downgrade

# Create new migration
python scripts/migrate.py revision "description"

# Check current version
python scripts/migrate.py current

# View history
python scripts/migrate.py history
```

## Docker

Migrations run automatically on container start for API server.

```bash
# Just build and run - migrations happen automatically
docker build -t getanswers-backend .
docker run -p 8000:8000 getanswers-backend
```

## Troubleshooting

### "Can't locate revision"
Database is out of sync. Check version:
```bash
# Show what database thinks it is
alembic current

# Show available migrations
alembic history
```

### Tables already exist
Stamp database without running migrations:
```bash
alembic stamp head
```

### Migration failed halfway
1. Note the error
2. Fix database manually if needed
3. Fix migration file
4. Re-run: `alembic upgrade head`

## Best Practices

- Always review auto-generated migrations before applying
- Test on development database first
- Never edit migrations that have been applied
- Write clear, descriptive migration messages
- Keep migrations small and focused
- Commit migrations with your code changes

## File Locations

```
backend/
├── alembic.ini              # Configuration
├── alembic/
│   ├── env.py              # Environment setup
│   ├── script.py.mako      # Template
│   ├── README.md           # Detailed docs
│   └── versions/           # Migration files
│       └── 001_*.py        # Initial schema
└── scripts/
    └── migrate.py          # Helper script
```

## Need Help?

- Full documentation: `backend/alembic/README.md`
- Setup details: `ALEMBIC_SETUP.md` (root directory)
- Alembic docs: https://alembic.sqlalchemy.org/
