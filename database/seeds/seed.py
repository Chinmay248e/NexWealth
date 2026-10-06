"""
NexWealth Person 1 Database Seeder
====================================
Seeds a controlled Demo Account (demo@example.com) and realistic
Income, Expense, and Transaction records through application services.

Usage:
    python database/seeds/seed.py
"""
import sys
import os
from datetime import date
from decimal import Decimal
from dotenv import load_dotenv

# Ensure backend directory is in path and load environment variables from backend/.env
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "backend"))
ENV_PATH = os.path.join(BACKEND_DIR, ".env")
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models import User, Income, Expense, Transaction
from app.schemas.income import IncomeCreate
from app.schemas.expense import ExpenseCreate
from app.services.income_service import create_income
from app.services.expense_service import create_expense
from app.services.dashboard_service import get_dashboard_summary

DEMO_USER_NAME = "NexWealth Demo"
DEMO_USER_EMAIL = "demo@example.com"
DEMO_USER_PASSWORD = "Demo@12345"

# 4 Realistic Income Records
DEMO_INCOMES = [
    {
        "source": "Primary Tech Salary",
        "amount": Decimal("185000.00"),
        "date": date(2026, 10, 1),
    },
    {
        "source": "Fintech Advisory Retainer",
        "amount": Decimal("45000.00"),
        "date": date(2026, 10, 3),
    },
    {
        "source": "Equity Dividend Payout",
        "amount": Decimal("18500.00"),
        "date": date(2026, 9, 28),
    },
    {
        "source": "Commercial Property Rental",
        "amount": Decimal("32000.00"),
        "date": date(2026, 9, 15),
    },
]

# 12 Realistic Expense Records Across Supported Categories
DEMO_EXPENSES = [
    {
        "description": "Apartment Maintenance & Utilities",
        "amount": Decimal("14500.00"),
        "category": "Bills",
        "date": date(2026, 10, 4),
    },
    {
        "description": "Organic Grocery & Pantry Restock",
        "amount": Decimal("8200.00"),
        "category": "Food",
        "date": date(2026, 10, 3),
    },
    {
        "description": "EV Fast Charging & Highway Tolls",
        "amount": Decimal("3400.00"),
        "category": "Transport",
        "date": date(2026, 10, 3),
    },
    {
        "description": "Cloud AI Pro Subscription",
        "amount": Decimal("6500.00"),
        "category": "Education",
        "date": date(2026, 10, 2),
    },
    {
        "description": "Family Health Insurance Top-up",
        "amount": Decimal("12000.00"),
        "category": "Medical",
        "date": date(2026, 9, 29),
    },
    {
        "description": "Weekend Family Dining",
        "amount": Decimal("4800.00"),
        "category": "Food",
        "date": date(2026, 9, 27),
    },
    {
        "description": "Flight Tickets to Bengaluru",
        "amount": Decimal("15400.00"),
        "category": "Travel",
        "date": date(2026, 9, 24),
    },
    {
        "description": "Noise Canceling Tech Hardware",
        "amount": Decimal("18900.00"),
        "category": "Shopping",
        "date": date(2026, 9, 20),
    },
    {
        "description": "Broadband & Fiber Internet",
        "amount": Decimal("1800.00"),
        "category": "Bills",
        "date": date(2026, 9, 18),
    },
    {
        "description": "IMAX Movie Tickets & Concessions",
        "amount": Decimal("2200.00"),
        "category": "Entertainment",
        "date": date(2026, 9, 14),
    },
    {
        "description": "Gym & Wellness Membership",
        "amount": Decimal("3500.00"),
        "category": "Other",
        "date": date(2026, 9, 10),
    },
    {
        "description": "Metro Card Monthly Pass",
        "amount": Decimal("1600.00"),
        "category": "Transport",
        "date": date(2026, 9, 5),
    },
]


def seed_demo_data(db_session=None):
    """
    Executes idempotent seeding logic for demo@example.com.
    Uses application service layer to guarantee transaction mirroring.
    """
    close_after = False
    if db_session is None:
        db = SessionLocal()
        close_after = True
    else:
        db = db_session

    try:
        print("=" * 60)
        print("NEXWEALTH DATABASE SEEDER (PERSON 1 CORE FINANCE)")
        print("=" * 60)

        # 0. Clean up legacy demo user if exists
        legacy_user = db.query(User).filter(User.email == "demo@nexwealth.local").first()
        if legacy_user:
            print(f"[*] Removing legacy demo user demo@nexwealth.local...")
            db.delete(legacy_user)
            db.commit()

        # 1. Check or Create Demo User
        demo_user = db.query(User).filter(User.email == DEMO_USER_EMAIL).first()
        if not demo_user:
            demo_user = User(
                name=DEMO_USER_NAME,
                email=DEMO_USER_EMAIL,
                passwordHash=get_password_hash(DEMO_USER_PASSWORD),
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
            print(f"[+] Created Demo User: {demo_user.name} ({demo_user.email}) -> ID: {demo_user.id}")
        else:
            print(f"[*] Reusing existing Demo User: {demo_user.name} ({demo_user.email}) -> ID: {demo_user.id}")
            # Ensure password hash is up to date
            demo_user.passwordHash = get_password_hash(DEMO_USER_PASSWORD)
            # Clean existing demo records for this user to make operation idempotent
            db.query(Transaction).filter(Transaction.userId == demo_user.id).delete()
            db.query(Expense).filter(Expense.userId == demo_user.id).delete()
            db.query(Income).filter(Income.userId == demo_user.id).delete()
            db.commit()
            print("  [OK] Cleaned previous demo financial records for pristine re-seed.")

        # 2. Seed Incomes via Income Service (Automatically creates Transactions)
        print(f"\n[*] Seeding {len(DEMO_INCOMES)} Income records via Income Service...")
        for inc_data in DEMO_INCOMES:
            income_in = IncomeCreate(
                source=inc_data["source"],
                amount=inc_data["amount"],
                date=inc_data["date"],
            )
            created_inc = create_income(db=db, user_id=demo_user.id, income_in=income_in)
            print(f"  + [Income] {created_inc.source} | Rs. {created_inc.amount} | {created_inc.date}")

        # 3. Seed Expenses via Expense Service (Automatically creates Transactions)
        print(f"\n[*] Seeding {len(DEMO_EXPENSES)} Expense records via Expense Service...")
        for exp_data in DEMO_EXPENSES:
            expense_in = ExpenseCreate(
                description=exp_data["description"],
                amount=exp_data["amount"],
                category=exp_data["category"],
                date=exp_data["date"],
            )
            created_exp = create_expense(db=db, user_id=demo_user.id, expense_in=expense_in)
            print(f"  + [Expense] {created_exp.description} ({created_exp.category}) | Rs. {created_exp.amount} | {created_exp.date}")

        # 4. Verify Data Counts & Consistency
        income_count = db.query(Income).filter(Income.userId == demo_user.id).count()
        expense_count = db.query(Expense).filter(Expense.userId == demo_user.id).count()
        transaction_count = db.query(Transaction).filter(Transaction.userId == demo_user.id).count()
        income_tx_count = (
            db.query(Transaction)
            .filter(Transaction.userId == demo_user.id, Transaction.type == "income")
            .count()
        )
        expense_tx_count = (
            db.query(Transaction)
            .filter(Transaction.userId == demo_user.id, Transaction.type == "expense")
            .count()
        )

        assert income_count == len(DEMO_INCOMES), f"Income count mismatch: {income_count}"
        assert expense_count == len(DEMO_EXPENSES), f"Expense count mismatch: {expense_count}"
        assert transaction_count == (income_count + expense_count), f"Transaction count mismatch: {transaction_count}"
        assert income_tx_count == income_count, "Income transaction count mismatch"
        assert expense_tx_count == expense_count, "Expense transaction count mismatch"

        # 5. Verify Dashboard Calculations
        summary = get_dashboard_summary(db=db, user_id=demo_user.id)

        print("\n" + "=" * 60)
        print("SEEDING SUMMARY & FINANCIAL METRICS")
        print("=" * 60)
        print(f"  User:               {demo_user.name} ({demo_user.email})")
        print(f"  Income Records:     {income_count}")
        print(f"  Expense Records:    {expense_count}")
        print(f"  Transactions:       {transaction_count} (Income: {income_tx_count}, Expense: {expense_tx_count})")
        print(f"  Total Income:       Rs. {summary.totalIncome:,.2f}")
        print(f"  Total Expenses:     Rs. {summary.totalExpenses:,.2f}")
        print(f"  Available Savings:  Rs. {summary.availableSavings:,.2f}")
        print(f"  Savings Rate:       {summary.savingsRate:.2f}%")
        print(f"  Idempotent:         YES (safely re-runnable)")
        print("=" * 60)
        print("[SUCCESS] Demo seed completed successfully!")

        return {
            "user": demo_user,
            "income_count": income_count,
            "expense_count": expense_count,
            "transaction_count": transaction_count,
            "summary": summary,
        }

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        raise e
    finally:
        if close_after:
            db.close()


if __name__ == "__main__":
    seed_demo_data()
