# NexWealth Database Management

This directory contains database schema migrations and seed scripts for PostgreSQL using Alembic and SQLAlchemy.

## Structure
- `migrations/`: Alembic migration environment and versioned revisions.
- `seeds/`: Seed scripts for initial development data adhering to `NEXWEALTH_DATA_CONTRACT.md`.

## PostgreSQL Setup
1. Ensure PostgreSQL 14+ is running locally or on a remote cluster.
2. Create the target database:
   ```sql
   CREATE DATABASE nexwealth;
   ```
3. Configure connection string in `backend/.env`:
   ```env
   DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/nexwealth
   ```

## Running Migrations
From the `backend/` directory with active virtual environment:
```bash
# Generate a new migration revision
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

## Running Seeds
```bash
python ../database/seeds/seed.py
```
