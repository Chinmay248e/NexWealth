"""
Analytics API Comprehensive Test Suite
======================================
Tests for Analytics Summary endpoint GET /api/v1/analytics/summary:
- Authentication enforcement (401)
- Fresh user empty/zero-safe response
- Correct income, expense, and savings calculations
- Correct category aggregation & percentage distribution
- Correct chronological monthly cashflow aggregation
- Correct investment totals, gain/loss, and ROI %
- Cross-user data isolation

Run: python test_analytics.py
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

# ──────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────

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


# ──────────────────────────────────────────────────
# Test Data
# ──────────────────────────────────────────────────
USER_A_EMAIL = "analytics.tester.a@nexwealth.in"
USER_B_EMAIL = "analytics.tester.b@nexwealth.in"
PASSWORD = "TestPassword@123"

def run_tests():
    print("=" * 60)
    print("ANALYTICS API — COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    cleanup_user(USER_A_EMAIL)
    cleanup_user(USER_B_EMAIL)

    user_a = register_and_login(USER_A_EMAIL, "Analytics User A", PASSWORD)
    user_b = register_and_login(USER_B_EMAIL, "Analytics User B", PASSWORD)
    headers_a = user_a["headers"]
    headers_b = user_b["headers"]

    passed_tests = 0
    total_tests = 8

    # ──────────────────────────────────────────────────
    # TEST 1: Unauthenticated Access (401)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 1: Unauthenticated Access Rejection ---")
    res = client.get("/api/v1/analytics/summary")
    assert res.status_code == 401, f"Expected 401, got {res.status_code}"
    print("  [PASSED] Unauthenticated request rejected with 401")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 2: Empty/Zero-Data User Behavior
    # ──────────────────────────────────────────────────
    print("\n--- TEST 2: Empty User Zero-Safe Analytics ---")
    res = client.get("/api/v1/analytics/summary", headers=headers_a)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    ov = data["overview"]
    assert Decimal(str(ov["totalIncome"])) == Decimal("0.00")
    assert Decimal(str(ov["totalExpenses"])) == Decimal("0.00")
    assert Decimal(str(ov["availableSavings"])) == Decimal("0.00")
    assert Decimal(str(ov["savingsRate"])) == Decimal("0.00")
    assert data["categoryBreakdown"] == []
    assert data["monthlyCashflow"] == []
    inv_ov = data["investmentOverview"]
    assert Decimal(str(inv_ov["totalInvested"])) == Decimal("0.00")
    assert Decimal(str(inv_ov["currentValue"])) == Decimal("0.00")
    assert Decimal(str(inv_ov["gainLoss"])) == Decimal("0.00")
    assert Decimal(str(inv_ov["returnPercent"])) == Decimal("0.00")
    print("  [PASSED] Fresh user with 0 records safely returns zero values and empty lists")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 3: Financial Overview with Real Data
    # ──────────────────────────────────────────────────
    print("\n--- TEST 3: Financial Overview Calculations ---")
    # Seed Incomes for User A
    client.post("/api/v1/incomes", json={"source": "Salary", "amount": 80000.00, "date": "2026-09-01"}, headers=headers_a)
    client.post("/api/v1/incomes", json={"source": "Freelance", "amount": 20000.00, "date": "2026-10-05"}, headers=headers_a)

    # Seed Expenses for User A
    client.post("/api/v1/expenses", json={"description": "Groceries", "amount": 15000.00, "category": "Food", "date": "2026-09-10"}, headers=headers_a)
    client.post("/api/v1/expenses", json={"description": "Electricity", "amount": 10000.00, "category": "Bills", "date": "2026-09-15"}, headers=headers_a)
    client.post("/api/v1/expenses", json={"description": "Dinner Out", "amount": 5000.00, "category": "Food", "date": "2026-10-02"}, headers=headers_a)

    res = client.get("/api/v1/analytics/summary", headers=headers_a)
    assert res.status_code == 200
    data = res.json()
    ov = data["overview"]

    # totalIncome = 80000 + 20000 = 100000.00
    assert Decimal(str(ov["totalIncome"])) == Decimal("100000.00")
    # totalExpenses = 15000 + 10000 + 5000 = 30000.00
    assert Decimal(str(ov["totalExpenses"])) == Decimal("30000.00")
    # availableSavings = 100000 - 30000 = 70000.00
    assert Decimal(str(ov["availableSavings"])) == Decimal("70000.00")
    # savingsRate = (70000 / 100000) * 100 = 70.00%
    assert Decimal(str(ov["savingsRate"])) == Decimal("70.00")
    print("  [PASSED] Overview totals and savings rate correctly calculated")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 4: Category Breakdown Aggregation
    # ──────────────────────────────────────────────────
    print("\n--- TEST 4: Category Breakdown Aggregation ---")
    cats = {c["category"]: c for c in data["categoryBreakdown"]}
    assert "Food" in cats
    assert "Bills" in cats
    # Food total: 15000 + 5000 = 20000.00 (66.67%)
    assert Decimal(str(cats["Food"]["amount"])) == Decimal("20000.00")
    assert Decimal(str(cats["Food"]["percentage"])) == Decimal("66.67")
    # Bills total: 10000.00 (33.33%)
    assert Decimal(str(cats["Bills"]["amount"])) == Decimal("10000.00")
    assert Decimal(str(cats["Bills"]["percentage"])) == Decimal("33.33")
    print("  [PASSED] Expense categories aggregated with accurate percentages")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 5: Chronological Monthly Cashflow
    # ──────────────────────────────────────────────────
    print("\n--- TEST 5: Chronological Monthly Cashflow ---")
    months = data["monthlyCashflow"]
    assert len(months) == 2
    # Month 1: 2026-09
    assert months[0]["month"] == "2026-09"
    assert Decimal(str(months[0]["income"])) == Decimal("80000.00")
    assert Decimal(str(months[0]["expenses"])) == Decimal("25000.00")
    assert Decimal(str(months[0]["savings"])) == Decimal("55000.00")
    # Month 2: 2026-10
    assert months[1]["month"] == "2026-10"
    assert Decimal(str(months[1]["income"])) == Decimal("20000.00")
    assert Decimal(str(months[1]["expenses"])) == Decimal("5000.00")
    assert Decimal(str(months[1]["savings"])) == Decimal("15000.00")
    print("  [PASSED] Monthly cashflow grouped and ordered chronologically with exact net savings")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 6: Investment Overview Aggregation
    # ──────────────────────────────────────────────────
    print("\n--- TEST 6: Investment Overview Aggregation ---")
    client.post("/api/v1/investments", json={
        "name": "Nifty Index Fund",
        "type": "Mutual Fund",
        "investedAmount": 150000.00,
        "currentValue": 180000.00,
        "date": "2025-10-01"
    }, headers=headers_a)
    client.post("/api/v1/investments", json={
        "name": "SGB Gold",
        "type": "Gold",
        "investedAmount": 50000.00,
        "currentValue": 70000.00,
        "date": "2026-01-15"
    }, headers=headers_a)

    res = client.get("/api/v1/analytics/summary", headers=headers_a)
    assert res.status_code == 200
    inv = res.json()["investmentOverview"]
    # Total Invested: 150000 + 50000 = 200000.00
    assert Decimal(str(inv["totalInvested"])) == Decimal("200000.00")
    # Current Value: 180000 + 70000 = 250000.00
    assert Decimal(str(inv["currentValue"])) == Decimal("250000.00")
    # Gain/Loss: 250000 - 200000 = 50000.00
    assert Decimal(str(inv["gainLoss"])) == Decimal("50000.00")
    # Return %: (50000 / 200000) * 100 = 25.00%
    assert Decimal(str(inv["returnPercent"])) == Decimal("25.00")
    print("  [PASSED] Investment total invested, current valuation, gain/loss, and ROI % aggregated correctly")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 7: Cross-User Data Isolation
    # ──────────────────────────────────────────────────
    print("\n--- TEST 7: Cross-User Data Isolation ---")
    # Seed User B with their own separate data
    client.post("/api/v1/incomes", json={"source": "User B Salary", "amount": 50000.00, "date": "2026-10-01"}, headers=headers_b)
    client.post("/api/v1/expenses", json={"description": "Rent", "amount": 15000.00, "category": "Bills", "date": "2026-10-02"}, headers=headers_b)

    res_b = client.get("/api/v1/analytics/summary", headers=headers_b)
    assert res_b.status_code == 200
    data_b = res_b.json()
    ov_b = data_b["overview"]
    assert Decimal(str(ov_b["totalIncome"])) == Decimal("50000.00")
    assert Decimal(str(ov_b["totalExpenses"])) == Decimal("15000.00")
    assert Decimal(str(ov_b["availableSavings"])) == Decimal("35000.00")
    # User B has no investments
    assert Decimal(str(data_b["investmentOverview"]["totalInvested"])) == Decimal("0.00")

    # User A data must remain unaffected
    res_a_again = client.get("/api/v1/analytics/summary", headers=headers_a)
    assert Decimal(str(res_a_again.json()["overview"]["totalIncome"])) == Decimal("100000.00")
    print("  [PASSED] Complete data isolation between User A and User B")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 8: Negative Savings / Deficit Scenario
    # ──────────────────────────────────────────────────
    print("\n--- TEST 8: Deficit Scenario (Expenses > Income) ---")
    # Add huge expense for User B
    client.post("/api/v1/expenses", json={"description": "Emergency Hospital", "amount": 60000.00, "category": "Medical", "date": "2026-10-03"}, headers=headers_b)
    res_b_def = client.get("/api/v1/analytics/summary", headers=headers_b)
    ov_b_def = res_b_def.json()["overview"]
    # Total income: 50,000, Total expenses: 15,000 + 60,000 = 75,000
    # Available savings: -25,000.00
    assert Decimal(str(ov_b_def["availableSavings"])) == Decimal("-25000.00")
    assert Decimal(str(ov_b_def["savingsRate"])) == Decimal("-50.00")
    print("  [PASSED] Negative available savings and negative savings rate handled cleanly")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # Cleanup
    # ──────────────────────────────────────────────────
    print("\n--- CLEANUP ---")
    cleanup_user(USER_A_EMAIL)
    cleanup_user(USER_B_EMAIL)
    print("  [OK] Test users cleaned up.")

    print("\n" + "=" * 60)
    print(f"ANALYTICS API TEST RESULTS: {passed_tests}/{total_tests} PASSED")
    print("ALL TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
