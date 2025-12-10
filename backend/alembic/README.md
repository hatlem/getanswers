# Database Migrations with Alembic

This directory contains database migration scripts managed by Alembic.

## Quick Start

### Apply migrations

```bash
# From backend directory
alembic upgrade head

# Or using the helper script
python scripts/migrate.py upgrade
```

### Create a new migration

```bash
# Auto-generate based on model changes
alembic revision --autogenerate -m "description of changes"

# Or using the helper script
python scripts/migrate.py revision "description of changes"
```

### View migration status

```bash
# Show current revision
alembic current

# Show migration history
alembic history --verbose
```

### Rollback a migration

```bash
# Rollback one migration
alembic downgrade -1

# Or using the helper script
python scripts/migrate.py downgrade
```

## Directory Structure

```
alembic/
├── README.md              # This file
├── env.py                 # Alembic environment configuration (async support)
├── script.py.mako         # Template for new migrations
└── versions/              # Migration scripts
    └── 001_initial_schema.py  # Initial database schema
```

## Migration Files

Migration files are in `versions/` and follow the format:
- `{revision_id}_{description}.py`

Each migration has:
- `upgrade()`: Apply the migration
- `downgrade()`: Revert the migration

## Configuration

- **Database URL**: Loaded from `app.core.config.settings.DATABASE_URL`
- **Alembic settings**: Configured in `alembic.ini`
- **Models**: All SQLAlchemy models are imported in `env.py`

## Docker Integration

Migrations run automatically before the application starts:

```dockerfile
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

## Best Practices

1. **Always review auto-generated migrations** before applying them
2. **Test migrations** on a development database first
3. **Write descriptive migration messages**
4. **Never edit applied migrations** - create a new one instead
5. **Keep migrations small and focused** on specific changes
6. **Version control all migrations** - commit them with your code

## Common Tasks

### Initialize a fresh database

```bash
alembic upgrade head
```

### Check what migrations will be applied

```bash
alembic upgrade head --sql
```

### Downgrade to a specific revision

```bash
alembic downgrade <revision_id>
```

### Stamp database at specific revision (without running migrations)

```bash
alembic stamp <revision_id>
```

## Troubleshooting

### "Can't locate revision identified by 'xyz'"

The database's migration version is out of sync. Check:
- What's in the database: `SELECT version_num FROM alembic_version;`
- What migrations exist: `alembic history`

### Migration fails partway through

1. Fix the issue in the migration file
2. Manually revert any partial changes in the database
3. Re-run the migration

### Need to skip a migration

```bash
# Stamp as if migration ran (dangerous!)
alembic stamp +1
```

## Models Included

The initial migration (`001_initial_schema.py`) includes:

- `users` - User accounts and authentication
- `magic_links` - Passwordless authentication tokens
- `objectives` - User missions/goals
- `policies` - User-defined automation rules
- `conversations` - Email threads
- `messages` - Individual emails
- `agent_actions` - AI action audit logs

All tables use UUID primary keys and proper foreign key constraints.
