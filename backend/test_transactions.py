"""
Transactions API Comprehensive Test Suite
==========================================
Tests for the unified read-only Transactions API with filtering,
ordering, authentication, cross-user isolation, and verification
that transactions are properly created through Income/Expense APIs.

Run: python test_transactions.py
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models import User, Income, Expense, Transaction

client = TestClient(app)

# -------------------------------------------------------
# Helpers
# -------------------------------------------------------

def register_and_login(email: str, name: str, password: str) -> dict:
    """Register a new user and return their auth headers + user data."""
    client.post("/api/v1/auth/register", json={
        "name": name,
        "email": email,
        "password": password,
    })
    res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password,
    })
    data = res.json()
    token = data.get("access_token") or data.get("accessToken")
    return {
        "headers": {"Authorization": f"Bearer {token}"},
        "user": data["user"],
        "token": token,
    }


def cleanup_user(email: str):
    """Remove a user and all cascading records by email."""
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if user:
        db.delete(user)
        db.commit()
    db.close()


# -------------------------------------------------------
# Test Data
# -------------------------------------------------------
USER_A_EMAIL = "txn.tester.a@nexwealth.in"
USER_B_EMAIL = "txn.tester.b@nexwealth.in"
PASSWORD = "TestPassword@123"
passed = 0
failed = 0


def check(label, condition, message=""):
    global passed, failed
    if condition:
        print(f"  [PASSED] {label}")
        passed += 1
    else:
        print(f"  [FAILED] {label} -- {message}")
        failed += 1
    return condition


def run_tests():
    global passed, failed

    print("=" * 60)
    print("TRANSACTIONS API -- COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    # Pre-clean
    cleanup_user(USER_A_EMAIL)
    cleanup_user(USER_B_EMAIL)

    # Setup: register two users
    user_a = register_and_login(USER_A_EMAIL, "Aarav Txn", PASSWORD)
    user_b = register_and_login(USER_B_EMAIL, "Bharat Txn", PASSWORD)

    headers_a = user_a["headers"]
    headers_b = user_b["headers"]

    # -------------------------------------------------------
    # Seed data via Income and Expense APIs
    # -------------------------------------------------------
    print("\n--- SEEDING TEST DATA ---")

    # User A: 3 incomes on different dates
    inc1 = client.post("/api/v1/incomes", json={
        "source": "Monthly Salary",
        "amount": "75000.00",
        "date": "2026-09-01",
    }, headers=headers_a).json()
    time.sleep(0.05)  # ensure createdAt ordering

    inc2 = client.post("/api/v1/incomes", json={
        "source": "Freelance Project",
        "amount": "15000.00",
        "date": "2026-09-15",
    }, headers=headers_a).json()
    time.sleep(0.05)

    inc3 = client.post("/api/v1/incomes", json={
        "source": "Dividend Income",
        "amount": "5000.00",
        "date": "2026-10-01",
    }, headers=headers_a).json()
    time.sleep(0.05)

    # User A: 3 expenses on different dates
    exp1 = client.post("/api/v1/expenses", json={
        "description": "Grocery shopping",
        "amount": "2500.00",
        "category": "Food",
        "date": "2026-09-05",
    }, headers=headers_a).json()
    time.sleep(0.05)

    exp2 = client.post("/api/v1/expenses", json={
        "description": "Electricity bill",
        "amount": "1800.00",
        "category": "Bills",
        "date": "2026-09-15",
    }, headers=headers_a).json()
    time.sleep(0.05)

    exp3 = client.post("/api/v1/expenses", json={
        "description": "Movie tickets",
        "amount": "600.00",
        "category": "Entertainment",
        "date": "2026-10-01",
    }, headers=headers_a).json()
    time.sleep(0.05)

    # User A: 2 items on the SAME date to test createdAt ordering
    same_date_inc = client.post("/api/v1/incomes", json={
        "source": "Bonus Payment",
        "amount": "10000.00",
        "date": "2026-09-15",
    }, headers=headers_a).json()
    time.sleep(0.05)

    # User B: 1 income (to test cross-user isolation)
    inc_b = client.post("/api/v1/incomes", json={
        "source": "User B Salary",
        "amount": "50000.00",
        "date": "2026-09-01",
    }, headers=headers_b).json()

    print("  Seeded 7 transactions for User A, 1 for User B")

    # ==================================================
    # TEST 1: List Transactions
    # ==================================================
    print("\n--- TEST 1: List Transactions (GET /api/v1/transactions) ---")
    res = client.get("/api/v1/transactions", headers=headers_a)
    all_txns = res.json()
    check(
        "List returns 200 with correct count",
        res.status_code == 200 and len(all_txns) == 7,
        f"status={res.status_code}, count={len(all_txns)}, expected 7",
    )

    # ==================================================
    # TEST 2: Get Single Transaction
    # ==================================================
    print("\n--- TEST 2: Get Single Transaction (GET /api/v1/transactions/{id}) ---")
    if all_txns:
        txn_id = all_txns[0]["id"]
        res = client.get(f"/api/v1/transactions/{txn_id}", headers=headers_a)
        data = res.json()
        check(
            "Get single transaction returns 200 with all fields",
            res.status_code == 200
            and data["id"] == txn_id
            and all(k in data for k in ["id", "userId", "type", "description", "amount", "category", "date", "source", "createdAt"]),
            f"status={res.status_code}",
        )
    else:
        check("Get single transaction", False, "No transactions to test")

    # ==================================================
    # TEST 3: Income Transactions Appear Correctly
    # ==================================================
    print("\n--- TEST 3: Income Transactions Appear Correctly ---")
    income_txns = [t for t in all_txns if t["type"] == "income"]
    check(
        "All 4 income transactions present",
        len(income_txns) == 4,
        f"found {len(income_txns)}, expected 4",
    )

    # ==================================================
    # TEST 4: Expense Transactions Appear Correctly
    # ==================================================
    print("\n--- TEST 4: Expense Transactions Appear Correctly ---")
    expense_txns = [t for t in all_txns if t["type"] == "expense"]
    check(
        "All 3 expense transactions present",
        len(expense_txns) == 3,
        f"found {len(expense_txns)}, expected 3",
    )

    # ==================================================
    # TEST 5: Results Ordered by Date Descending
    # ==================================================
    print("\n--- TEST 5: Results Ordered by Date Descending ---")
    dates = [t["date"] for t in all_txns]
    check(
        "Transactions sorted by date descending",
        all(dates[i] >= dates[i + 1] for i in range(len(dates) - 1)),
        f"dates={dates}",
    )

    # ==================================================
    # TEST 6: Same-Date Transactions Ordered by createdAt Descending
    # ==================================================
    print("\n--- TEST 6: Same-Date createdAt Ordering ---")
    # Filter to Sep 15 transactions (should be 3: Freelance, Electricity bill, Bonus)
    sep15_txns = [t for t in all_txns if t["date"] == "2026-09-15"]
    created_ats = [t["createdAt"] for t in sep15_txns]
    check(
        "Same-date transactions sorted by createdAt descending",
        len(sep15_txns) == 3 and all(created_ats[i] >= created_ats[i + 1] for i in range(len(created_ats) - 1)),
        f"count={len(sep15_txns)}, createdAts={created_ats}",
    )

    # ==================================================
    # TEST 7: Filter by type=income
    # ==================================================
    print("\n--- TEST 7: Filter by type=income ---")
    res = client.get("/api/v1/transactions?type=income", headers=headers_a)
    data = res.json()
    check(
        "type=income returns only income transactions",
        res.status_code == 200
        and len(data) == 4
        and all(t["type"] == "income" for t in data),
        f"status={res.status_code}, count={len(data)}",
    )

    # ==================================================
    # TEST 8: Filter by type=expense
    # ==================================================
    print("\n--- TEST 8: Filter by type=expense ---")
    res = client.get("/api/v1/transactions?type=expense", headers=headers_a)
    data = res.json()
    check(
        "type=expense returns only expense transactions",
        res.status_code == 200
        and len(data) == 3
        and all(t["type"] == "expense" for t in data),
        f"status={res.status_code}, count={len(data)}",
    )

    # ==================================================
    # TEST 9: Filter by Category
    # ==================================================
    print("\n--- TEST 9: Filter by Category ---")
    res = client.get("/api/v1/transactions?category=Food", headers=headers_a)
    data = res.json()
    check(
        "category=Food returns only Food transactions",
        res.status_code == 200
        and len(data) == 1
        and data[0]["category"] == "Food",
        f"status={res.status_code}, count={len(data)}",
    )

    # ==================================================
    # TEST 10: Filter by date_from
    # ==================================================
    print("\n--- TEST 10: Filter by date_from ---")
    res = client.get("/api/v1/transactions?date_from=2026-10-01", headers=headers_a)
    data = res.json()
    check(
        "date_from=2026-10-01 returns only Oct+ transactions",
        res.status_code == 200
        and len(data) == 2
        and all(t["date"] >= "2026-10-01" for t in data),
        f"status={res.status_code}, count={len(data)}",
    )

    # ==================================================
    # TEST 11: Filter by date_to
    # ==================================================
    print("\n--- TEST 11: Filter by date_to ---")
    res = client.get("/api/v1/transactions?date_to=2026-09-05", headers=headers_a)
    data = res.json()
    check(
        "date_to=2026-09-05 returns only Sep 1-5 transactions",
        res.status_code == 200
        and len(data) == 2
        and all(t["date"] <= "2026-09-05" for t in data),
        f"status={res.status_code}, count={len(data)}",
    )

    # ==================================================
    # TEST 12: Combined Filters
    # ==================================================
    print("\n--- TEST 12: Combined Filters ---")
    res = client.get(
        "/api/v1/transactions?type=expense&date_from=2026-09-01&date_to=2026-09-30",
        headers=headers_a,
    )
    data = res.json()
    check(
        "Combined type=expense + date range returns correct results",
        res.status_code == 200
        and len(data) == 2
        and all(t["type"] == "expense" and "2026-09-01" <= t["date"] <= "2026-09-30" for t in data),
        f"status={res.status_code}, count={len(data)}, data={[t['description'] for t in data]}",
    )

    # ==================================================
    # TEST 13: Invalid Transaction Type
    # ==================================================
    print("\n--- TEST 13: Invalid Transaction Type ---")
    res = client.get("/api/v1/transactions?type=invalid", headers=headers_a)
    check(
        "Invalid type returns 422",
        res.status_code == 422,
        f"status={res.status_code}",
    )

    # ==================================================
    # TEST 14: Invalid Date Range (date_from > date_to)
    # ==================================================
    print("\n--- TEST 14: Invalid Date Range ---")
    res = client.get(
        "/api/v1/transactions?date_from=2026-10-31&date_to=2026-09-01",
        headers=headers_a,
    )
    check(
        "date_from > date_to returns 422",
        res.status_code == 422,
        f"status={res.status_code}",
    )

    # ==================================================
    # TEST 15: Unauthorized Access (No Token)
    # ==================================================
    print("\n--- TEST 15: Unauthorized Access ---")
    res_list = client.get("/api/v1/transactions")
    res_get = client.get("/api/v1/transactions/fake_id")
    check(
        "Both endpoints reject unauthenticated requests (401)",
        res_list.status_code == 401 and res_get.status_code == 401,
        f"list={res_list.status_code}, get={res_get.status_code}",
    )

    # ==================================================
    # TEST 16: Cross-User Isolation
    # ==================================================
    print("\n--- TEST 16: Cross-User Isolation ---")
    # User B should only see their own 1 transaction
    res_b_list = client.get("/api/v1/transactions", headers=headers_b)
    b_txns = res_b_list.json()

    # User B tries to access User A's transaction by ID
    a_txn_id = all_txns[0]["id"] if all_txns else "fake"
    res_b_get = client.get(f"/api/v1/transactions/{a_txn_id}", headers=headers_b)

    check(
        "User B sees only their own transactions (1), cannot access User A's (404)",
        res_b_list.status_code == 200
        and len(b_txns) == 1
        and b_txns[0]["source"] == "User B Salary"
        and res_b_get.status_code == 404,
        f"B list count={len(b_txns)}, B get A's txn={res_b_get.status_code}",
    )

    # ==================================================
    # TEST 17: Transaction Created Through Income API is Visible
    # ==================================================
    print("\n--- TEST 17: Income Transaction Visible ---")
    # Create a new income and verify the transaction appears
    new_inc = client.post("/api/v1/incomes", json={
        "source": "Visibility Test Income",
        "amount": "9999.00",
        "date": "2026-10-05",
    }, headers=headers_a).json()

    res = client.get("/api/v1/transactions?type=income&category=Income", headers=headers_a)
    data = res.json()
    found = any(t["source"] == "Visibility Test Income" and t["amount"] == "9999.00" for t in data)
    check(
        "Transaction from Income API appears in Transactions listing",
        found,
        f"searched {len(data)} transactions",
    )

    # ==================================================
    # TEST 18: Transaction Created Through Expense API is Visible
    # ==================================================
    print("\n--- TEST 18: Expense Transaction Visible ---")
    new_exp = client.post("/api/v1/expenses", json={
        "description": "Visibility Test Expense",
        "amount": "888.00",
        "category": "Travel",
        "date": "2026-10-05",
    }, headers=headers_a).json()

    res = client.get("/api/v1/transactions?type=expense&category=Travel", headers=headers_a)
    data = res.json()
    found = any(t["description"] == "Visibility Test Expense" and t["amount"] == "888.00" for t in data)
    check(
        "Transaction from Expense API appears in Transactions listing",
        found,
        f"searched {len(data)} transactions",
    )

    # ==================================================
    # TEST 19: No Duplicate Transactions Introduced
    # ==================================================
    print("\n--- TEST 19: No Duplicate Transactions ---")
    db = SessionLocal()
    user_id_a = user_a["user"]["id"]
    total_txns = db.query(Transaction).filter(Transaction.userId == user_id_a).count()
    total_incomes = db.query(Income).filter(Income.userId == user_id_a).count()
    total_expenses = db.query(Expense).filter(Expense.userId == user_id_a).count()
    db.close()

    # Each income creates 1 txn, each expense creates 1 txn
    expected = total_incomes + total_expenses
    check(
        f"Transaction count ({total_txns}) == Income ({total_incomes}) + Expense ({total_expenses}) = {expected}",
        total_txns == expected,
        f"total_txns={total_txns}, expected={expected}",
    )

    # -------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------
    print("\n--- CLEANUP ---")
    cleanup_user(USER_A_EMAIL)
    cleanup_user(USER_B_EMAIL)
    print("  [OK] Test users cleaned up.")

    # -------------------------------------------------------
    # Final Report
    # -------------------------------------------------------
    total = passed + failed
    print("\n" + "=" * 60)
    print(f"TRANSACTIONS API TEST RESULTS: {passed}/{total} PASSED")
    if failed == 0:
        print("ALL TESTS PASSED!")
    else:
        print(f"{failed} TEST(S) FAILED")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
