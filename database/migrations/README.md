# Alembic Database Migrations

This folder is configured for Alembic schema tracking.

### Commands
- `alembic init migrations` (already configured)
- `alembic revision --autogenerate -m "create_tables"`
- `alembic upgrade head`
- `alembic downgrade -1`
