"""
Dashboard API Comprehensive Test Suite
========================================
Tests for the core financial calculations endpoint:
GET /api/v1/dashboard/summary

Tests coverage:
1. Dashboard summary with income and expenses
2. totalIncome calculation
3. totalExpenses calculation
4. availableSavings calculation
5. savingsRate calculation
6. Zero income -> savingsRate = 0
7. User with no financial records -> all values = 0
8. Multiple income records are summed correctly
9. Multiple expense records are summed correctly
10. Decimal/money precision
11. Unauthorized request -> 401
12. Cross-user isolation
13. Income belonging to another user is not included
14. Expenses belonging to another user are not included
15. Negative available savings is calculated correctly when expenses exceed income
16. Income API integration / verification
17. Expense API integration / verification
18. Transactions API integration / verification

Run: python test_dashboard.py
"""
import sys
import os
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models import User

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
# Test Runner
# -------------------------------------------------------

def run_all_tests():
    USER_A_EMAIL = "dash.tester.a@nexwealth.in"
    USER_B_EMAIL = "dash.tester.b@nexwealth.in"
    USER_EMPTY_EMAIL = "dash.tester.empty@nexwealth.in"
    USER_DEFICIT_EMAIL = "dash.tester.deficit@nexwealth.in"
    USER_ZERO_INC_EMAIL = "dash.tester.zeroinc@nexwealth.in"
    PASSWORD = "SecurePassword@123"

    # Pre-clean
    for email in [USER_A_EMAIL, USER_B_EMAIL, USER_EMPTY_EMAIL, USER_DEFICIT_EMAIL, USER_ZERO_INC_EMAIL]:
        cleanup_user(email)

    passed = 0
    failed = 0

    print("=" * 60)
    print("DASHBOARD API -- COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    try:
        # -----------------------------------------------------------------
        # Setup Users
        # -----------------------------------------------------------------
        user_a = register_and_login(USER_A_EMAIL, "Dash Tester A", PASSWORD)
        user_b = register_and_login(USER_B_EMAIL, "Dash Tester B", PASSWORD)
        user_empty = register_and_login(USER_EMPTY_EMAIL, "Dash Tester Empty", PASSWORD)
        user_deficit = register_and_login(USER_DEFICIT_EMAIL, "Dash Tester Deficit", PASSWORD)
        user_zero_inc = register_and_login(USER_ZERO_INC_EMAIL, "Dash Tester ZeroInc", PASSWORD)

        # -----------------------------------------------------------------
        # TEST 7: User with no financial records -> all values = 0
        # -----------------------------------------------------------------
        print("\n--- TEST 7: User with No Financial Records (All 0) ---")
        res = client.get("/api/v1/dashboard/summary", headers=user_empty["headers"])
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert Decimal(str(data["totalIncome"])) == Decimal("0.00"), f"Expected 0.00, got {data['totalIncome']}"
        assert Decimal(str(data["totalExpenses"])) == Decimal("0.00"), f"Expected 0.00, got {data['totalExpenses']}"
        assert Decimal(str(data["availableSavings"])) == Decimal("0.00"), f"Expected 0.00, got {data['availableSavings']}"
        assert Decimal(str(data["savingsRate"])) == Decimal("0.00"), f"Expected 0.00, got {data['savingsRate']}"
        print("  [PASSED] Fresh user gets totalIncome=0, totalExpenses=0, availableSavings=0, savingsRate=0")
        passed += 1

        # -----------------------------------------------------------------
        # Seed Data for User A:
        # Incomes: 75000.50 + 25000.25 = 100000.75
        # Expenses: 20000.25 + 10000.50 = 30000.75
        # Expected availableSavings = 70000.00
        # Expected savingsRate = (70000.00 / 100000.75) * 100 = 69.9994... -> 70.00%
        # -----------------------------------------------------------------
        client.post("/api/v1/incomes", json={"source": "Salary", "amount": 75000.50, "date": "2026-10-01"}, headers=user_a["headers"])
        client.post("/api/v1/incomes", json={"source": "Freelance", "amount": 25000.25, "date": "2026-10-02"}, headers=user_a["headers"])
        client.post("/api/v1/expenses", json={"description": "Rent", "amount": 20000.25, "category": "Bills", "date": "2026-10-03"}, headers=user_a["headers"])
        client.post("/api/v1/expenses", json={"description": "Groceries", "amount": 10000.50, "category": "Food", "date": "2026-10-04"}, headers=user_a["headers"])

        # Seed Data for User B (to test isolation):
        # Income: 50000.00, Expense: 15000.00
        client.post("/api/v1/incomes", json={"source": "User B Salary", "amount": 50000.00, "date": "2026-10-01"}, headers=user_b["headers"])
        client.post("/api/v1/expenses", json={"description": "User B Bills", "amount": 15000.00, "category": "Bills", "date": "2026-10-01"}, headers=user_b["headers"])

        # -----------------------------------------------------------------
        # TEST 1: Dashboard Summary Endpoint (GET /api/v1/dashboard/summary)
        # -----------------------------------------------------------------
        print("\n--- TEST 1: Dashboard Summary with Income and Expenses ---")
        res_a = client.get("/api/v1/dashboard/summary", headers=user_a["headers"])
        assert res_a.status_code == 200, f"Expected 200, got {res_a.status_code}: {res_a.text}"
        data_a = res_a.json()
        assert "totalIncome" in data_a
        assert "totalExpenses" in data_a
        assert "availableSavings" in data_a
        assert "savingsRate" in data_a
        print("  [PASSED] Dashboard summary returns 200 with all required fields")
        passed += 1

        # -----------------------------------------------------------------
        # TEST 2: totalIncome Calculation
        # -----------------------------------------------------------------
        print("\n--- TEST 2: totalIncome Calculation ---")
        expected_income = Decimal("100000.75")
        actual_income = Decimal(str(data_a["totalIncome"]))
        assert actual_income == expected_income, f"Expected {expected_income}, got {actual_income}"
        print(f"  [PASSED] totalIncome calculated correctly: {actual_income}")
        passed += 1

        # -----------------------------------------------------------------
        # TEST 3: totalExpenses Calculation
        # -----------------------------------------------------------------
        print("\n--- TEST 3: totalExpenses Calculation ---")
        expected_expenses = Decimal("30000.75")
        actual_expenses = Decimal(str(data_a["totalExpenses"]))
        assert actual_expenses == expected_expenses, f"Expected {expected_expenses}, got {actual_expenses}"
        print(f"  [PASSED] totalExpenses calculated correctly: {actual_expenses}")
        passed += 1

        # -----------------------------------------------------------------
        # TEST 4: availableSavings Calculation
        # -----------------------------------------------------------------
        print("\n--- TEST 4: availableSavings Calculation ---")
        expected_savings = Decimal("70000.00")
        actual_savings = Decimal(str(data_a["availableSavings"]))
        assert actual_savings == expected_savings, f"Expected {expected_savings}, got {actual_savings}"
        print(f"  [PASSED] availableSavings calculated correctly (totalIncome - totalExpenses): {actual_savings}")
        passed += 1

        # -----------------------------------------------------------------
        # TEST 5: savingsRate Calculation
        # -----------------------------------------------------------------
        print("\n--- TEST 5: savingsRate Calculation ---")
        # (70000.00 / 100000.75) * 100 = 69.9994... -> 70.00%
        expected_rate = Decimal("70.00")
        actual_rate = Decimal(str(data_a["savingsRate"]))
        assert actual_rate == expected_rate, f"Expected {expected_rate}, got {actual_rate}"
        print(f"  [PASSED] savingsRate calculated correctly: {actual_rate}%")
        passed += 1

        # -----------------------------------------------------------------
        # TEST 6: Zero Income -> savingsRate = 0
        # -----------------------------------------------------------------
        print("\n--- TEST 6: Zero Income -> savingsRate = 0 ---")
        client.post("/api/v1/expenses", json={"description": "Shopping", "amount": 500.00, "category": "Shopping", "date": "2026-10-01"}, headers=user_zero_inc["headers"])
        res_zero = client.get("/api/v1/dashboard/summary", headers=user_zero_inc["headers"])
        assert res_zero.status_code == 200
        data_zero = res_zero.json()
        assert Decimal(str(data_zero["totalIncome"])) == Decimal("0.00")
        assert Decimal(str(data_zero["totalExpenses"])) == Decimal("500.00")
        assert Decimal(str(data_zero["availableSavings"])) == Decimal("-500.00")
        assert Decimal(str(data_zero["savingsRate"])) == Decimal("0.00"), f"Expected 0.00, got {data_zero['savingsRate']}"
        print("  [PASSED] Zero totalIncome results in savingsRate = 0.00")
        passed += 1

        # -----------------------------------------------------------------
        # TEST 8: Multiple Income Records are Summed Correctly
        # -----------------------------------------------------------------
        print("\n--- TEST 8: Multiple Income Records Summed Correctly ---")
        # Add a 3rd income to User A: 15000.25 -> New total: 115001.00
        client.post("/api/v1/incomes", json={"source": "Bonus", "amount": 15000.25, "date": "2026-10-05"}, headers=user_a["headers"])
        res_a_updated = client.get("/api/v1/dashboard/summary", headers=user_a["headers"])
        data_a_updated = res_a_updated.json()
        assert Decimal(str(data_a_updated["totalIncome"])) == Decimal("115001.00"), f"Expected 115001.00, got {data_a_updated['totalIncome']}"
        print("  [PASSED] 3 income records summed to exact 115001.00")
        passed += 1

        # -----------------------------------------------------------------
        # TEST 9: Multiple Expense Records are Summed Correctly
        # -----------------------------------------------------------------
        print("\n--- TEST 9: Multiple Expense Records Summed Correctly ---")
        # Add a 3rd expense to User A: 5000.00 -> New total: 35000.75
        client.post("/api/v1/expenses", json={"description": "Flight Ticket", "amount": 5000.00, "category": "Travel", "date": "2026-10-05"}, headers=user_a["headers"])
        res_a_updated2 = client.get("/api/v1/dashboard/summary", headers=user_a["headers"])
        data_a_updated2 = res_a_updated2.json()
        assert Decimal(str(data_a_updated2["totalExpenses"])) == Decimal("35000.75"), f"Expected 35000.75, got {data_a_updated2['totalExpenses']}"
        print("  [PASSED] 3 expense records summed to exact 35000.75")
        passed += 1

        # -----------------------------------------------------------------
        # TEST 10: Decimal / Money Precision
        # -----------------------------------------------------------------
        print("\n--- TEST 10: Decimal / Money Precision ---")
        # Total Income = 115001.00, Total Expenses = 35000.75
        # Available Savings = 115001.00 - 35000.75 = 80000.25
        assert Decimal(str(data_a_updated2["availableSavings"])) == Decimal("80000.25")
        # Savings Rate = (80000.25 / 115001.00) * 100 = 69.56482987... -> 69.56
        assert Decimal(str(data_a_updated2["savingsRate"])) == Decimal("69.56")
        print("  [PASSED] Exact Decimal precision preserved (no floating-point drift)")
        passed += 1

        # -----------------------------------------------------------------
        # TEST 11: Unauthorized Request -> 401
        # -----------------------------------------------------------------
        print("\n--- TEST 11: Unauthorized Request -> 401 ---")
        res_unauth = client.get("/api/v1/dashboard/summary")
        assert res_unauth.status_code == 401, f"Expected 401, got {res_unauth.status_code}"
        res_invalid_token = client.get("/api/v1/dashboard/summary", headers={"Authorization": "Bearer invalid.token.value"})
        assert res_invalid_token.status_code == 401, f"Expected 401, got {res_invalid_token.status_code}"
        print("  [PASSED] Unauthenticated and invalid token requests rejected with 401")
        passed += 1

        # -----------------------------------------------------------------
        # TEST 12: Cross-User Isolation
        # -----------------------------------------------------------------
        print("\n--- TEST 12: Cross-User Isolation ---")
        res_b = client.get("/api/v1/dashboard/summary", headers=user_b["headers"])
        data_b = res_b.json()
        assert Decimal(str(data_b["totalIncome"])) == Decimal("50000.00"), f"Expected 50000.00, got {data_b['totalIncome']}"
        assert Decimal(str(data_b["totalExpenses"])) == Decimal("15000.00"), f"Expected 15000.00, got {data_b['totalExpenses']}"
        assert Decimal(str(data_b["availableSavings"])) == Decimal("35000.00"), f"Expected 35000.00, got {data_b['availableSavings']}"
        assert Decimal(str(data_b["savingsRate"])) == Decimal("70.00"), f"Expected 70.00, got {data_b['savingsRate']}"
        print("  [PASSED] User B only sees their own summary (50,000 / 15,000 / 35,000 / 70.00%)")
        passed += 1

        # -----------------------------------------------------------------
        # TEST 13: Income Belonging to Another User is Not Included
        # -----------------------------------------------------------------
        print("\n--- TEST 13: Income Belonging to Another User Not Included ---")
        # User A has 115001.00, User B has 50000.00. Total across both is 165001.00.
        # Ensure User A's totalIncome does NOT include User B's 50000.00
        assert Decimal(str(data_a_updated2["totalIncome"])) == Decimal("115001.00")
        assert Decimal(str(data_b["totalIncome"])) == Decimal("50000.00")
        print("  [PASSED] User A totalIncome excludes User B income")
        passed += 1

        # -----------------------------------------------------------------
        # TEST 14: Expenses Belonging to Another User are Not Included
        # -----------------------------------------------------------------
        print("\n--- TEST 14: Expenses Belonging to Another User Not Included ---")
        # User A has 35000.75, User B has 15000.00. Total across both is 50000.75.
        # Ensure User A's totalExpenses does NOT include User B's 15000.00
        assert Decimal(str(data_a_updated2["totalExpenses"])) == Decimal("35000.75")
        assert Decimal(str(data_b["totalExpenses"])) == Decimal("15000.00")
        print("  [PASSED] User A totalExpenses excludes User B expenses")
        passed += 1

        # -----------------------------------------------------------------
        # TEST 15: Negative Available Savings (Expenses Exceed Income)
        # -----------------------------------------------------------------
        print("\n--- TEST 15: Negative Available Savings (Deficit) ---")
        # User Deficit: Income = 10000.00, Expenses = 15000.00
        client.post("/api/v1/incomes", json={"source": "Part-time", "amount": 10000.00, "date": "2026-10-01"}, headers=user_deficit["headers"])
        client.post("/api/v1/expenses", json={"description": "Emergency Repair", "amount": 15000.00, "category": "Bills", "date": "2026-10-02"}, headers=user_deficit["headers"])
        res_def = client.get("/api/v1/dashboard/summary", headers=user_deficit["headers"])
        data_def = res_def.json()
        assert Decimal(str(data_def["totalIncome"])) == Decimal("10000.00")
        assert Decimal(str(data_def["totalExpenses"])) == Decimal("15000.00")
        assert Decimal(str(data_def["availableSavings"])) == Decimal("-5000.00"), f"Expected -5000.00, got {data_def['availableSavings']}"
        assert Decimal(str(data_def["savingsRate"])) == Decimal("-50.00"), f"Expected -50.00, got {data_def['savingsRate']}"
        print("  [PASSED] Deficit correctly calculated: availableSavings = -5000.00, savingsRate = -50.00%")
        passed += 1

        # -----------------------------------------------------------------
        # TEST 16: Existing Income API Verification
        # -----------------------------------------------------------------
        print("\n--- TEST 16: Existing Income API Verification ---")
        res_inc = client.get("/api/v1/incomes", headers=user_a["headers"])
        assert res_inc.status_code == 200
        assert len(res_inc.json()) == 3
        print("  [PASSED] Income API functions normally")
        passed += 1

        # -----------------------------------------------------------------
        # TEST 17: Existing Expense API Verification
        # -----------------------------------------------------------------
        print("\n--- TEST 17: Existing Expense API Verification ---")
        res_exp = client.get("/api/v1/expenses", headers=user_a["headers"])
        assert res_exp.status_code == 200
        assert len(res_exp.json()) == 3
        print("  [PASSED] Expense API functions normally")
        passed += 1

        # -----------------------------------------------------------------
        # TEST 18: Existing Transactions API Verification
        # -----------------------------------------------------------------
        print("\n--- TEST 18: Existing Transactions API Verification ---")
        res_txn = client.get("/api/v1/transactions", headers=user_a["headers"])
        assert res_txn.status_code == 200
        assert len(res_txn.json()) == 6  # 3 incomes + 3 expenses
        print("  [PASSED] Transactions API functions normally (6 synchronized transactions)")
        passed += 1

    except Exception as e:
        failed += 1
        print(f"\n[FAILED] Test failure: {e}")
        import traceback
        traceback.print_exc()
        raise e
    finally:
        # Cleanup
        print("\n--- CLEANUP ---")
        for email in [USER_A_EMAIL, USER_B_EMAIL, USER_EMPTY_EMAIL, USER_DEFICIT_EMAIL, USER_ZERO_INC_EMAIL]:
            cleanup_user(email)
        print("  [OK] Test users cleaned up.")

    print("\n" + "=" * 60)
    print(f"DASHBOARD API TEST RESULTS: {passed}/{passed + failed} PASSED")
    if failed == 0:
        print("ALL TESTS PASSED!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_all_tests()
