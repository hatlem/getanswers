#!/usr/bin/env python
"""Database migration helper script.

Usage:
    python scripts/migrate.py upgrade       # Apply all pending migrations
    python scripts/migrate.py downgrade     # Revert last migration
    python scripts/migrate.py revision "msg" # Create new migration
    python scripts/migrate.py current       # Show current revision
    python scripts/migrate.py history       # Show migration history
"""
import subprocess
import sys
import os


def main():
    # Change to backend directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    cmd = sys.argv[1] if len(sys.argv) > 1 else "upgrade"

    if cmd == "upgrade":
        subprocess.run(["alembic", "upgrade", "head"])
    elif cmd == "downgrade":
        subprocess.run(["alembic", "downgrade", "-1"])
    elif cmd == "revision":
        message = sys.argv[2] if len(sys.argv) > 2 else "auto"
        subprocess.run(["alembic", "revision", "--autogenerate", "-m", message])
    elif cmd == "current":
        subprocess.run(["alembic", "current"])
    elif cmd == "history":
        subprocess.run(["alembic", "history"])
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
