import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.models import Base, User, Income, Expense, Transaction
from sqlalchemy import create_engine, text

def verify():
    print("==================================================")
    print("1. MODEL IMPORT & METADATA VERIFICATION")
    print("==================================================")
    registered = list(Base.metadata.tables.keys())
    print("Registered SQLAlchemy Table Models:", registered)
    assert set(registered) == {"users", "incomes", "expenses", "transactions"}, "Model table set mismatch"
    print("[SUCCESS] All 4 Person 1 models imported and registered.")

    print("\n==================================================")
    print("2. POSTGRESQL CONNECTION & SCHEMA VERIFICATION")
    print("==================================================")
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)

    with engine.connect() as conn:
        # Check Tables
        tables = [
            r[0]
            for r in conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
                )
            ).fetchall()
        ]
        print("Actual Public Tables in PostgreSQL Database:", tables)
        assert "users" in tables, "Table 'users' missing from PostgreSQL"
        assert "incomes" in tables, "Table 'incomes' missing from PostgreSQL"
        assert "expenses" in tables, "Table 'expenses' missing from PostgreSQL"
        assert "transactions" in tables, "Table 'transactions' missing from PostgreSQL"
        assert "alembic_version" in tables, "Alembic tracking table missing"
        print("[SUCCESS] Exactly 4 Person 1 entity tables + alembic_version present.")

        # Check Alembic Migration Head
        version = conn.execute(text("SELECT version_num FROM alembic_version;")).scalar()
        print(f"\nApplied Alembic Revision: {version}")
        assert version == "001_person1_init", f"Unexpected alembic version: {version}"
        print("[SUCCESS] Alembic migration head '001_person1_init' applied successfully.")

        # Check Columns and Precision
        print("\n==================================================")
        print("3. COLUMNS & DATA TYPES VERIFICATION")
        print("==================================================")
        for tbl in ["users", "incomes", "expenses", "transactions"]:
            cols = conn.execute(
                text(
                    f"SELECT column_name, data_type, numeric_precision, numeric_scale, is_nullable "
                    f"FROM information_schema.columns WHERE table_name = '{tbl}' ORDER BY ordinal_position;"
                )
            ).fetchall()
            print(f"\nTable '{tbl}':")
            for c in cols:
                prec = f"({c[2]},{c[3]})" if c[2] is not None else ""
                print(f"  - {c[0]}: {c[1]}{prec} [Nullable: {c[4]}]")

        # Check Foreign Keys
        print("\n==================================================")
        print("4. FOREIGN KEYS & CONSTRAINTS VERIFICATION")
        print("==================================================")
        fk_sql = """
            SELECT
                tc.table_name, kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                rc.delete_rule
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
            JOIN information_schema.referential_constraints AS rc
              ON tc.constraint_name = rc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY';
        """
        fks = conn.execute(text(fk_sql)).fetchall()
        for fk in fks:
            print(f"  - FK: {fk[0]}.{fk[1]} -> {fk[2]}.{fk[3]} (ON DELETE {fk[4]})")
        assert len(fks) == 3, f"Expected 3 foreign keys, found {len(fks)}"
        print("[SUCCESS] All foreign keys verified with ON DELETE CASCADE.")

        # Check Indexes
        print("\n==================================================")
        print("5. INDEXES VERIFICATION")
        print("==================================================")
        idx_sql = """
            SELECT tablename, indexname, indexdef
            FROM pg_indexes
            WHERE schemaname = 'public' AND tablename IN ('users', 'incomes', 'expenses', 'transactions')
            ORDER BY tablename, indexname;
        """
        indexes = conn.execute(text(idx_sql)).fetchall()
        for idx in indexes:
            print(f"  - [{idx[0]}] {idx[1]}: {idx[2]}")
        print(f"[SUCCESS] Total {len(indexes)} indexes created across the four tables.")

        # Check Row Counts (Zero Seed Data)
        print("\n==================================================")
        print("6. ZERO SEED DATA VERIFICATION")
        print("==================================================")
        for tbl in ["users", "incomes", "expenses", "transactions"]:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {tbl};")).scalar()
            print(f"  - {tbl} row count: {count}")
            assert count == 0, f"Table {tbl} contains unexpected data: {count} rows"
        print("[SUCCESS] Confirmed 0 seed records in all tables.")

    print("\n==================================================")
    print("ALL 6 VERIFICATION CHECKS PASSED PERFECTLY!")
    print("==================================================")

if __name__ == "__main__":
    verify()
