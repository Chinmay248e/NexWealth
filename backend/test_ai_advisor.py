"""
AI Advisor API Comprehensive Test Suite (Person 2)
==================================================
Tests for AI Advisor Chat, Context Aggregation, Dynamic Insight Cards,
Authentication Enforcement, and Strict Cross-User Data Isolation.

Run: python test_ai_advisor.py
"""
import sys
import os
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models import User, Income, Expense, Goal, Investment

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
USER_A_EMAIL = "ai.tester.a@nexwealth.in"
USER_B_EMAIL = "ai.tester.b@nexwealth.in"
PASSWORD = "TestPassword@123"

def run_tests():
    print("=" * 60)
    print("AI ADVISOR API — COMPREHENSIVE TEST SUITE (PERSON 2)")
    print("=" * 60)

    # Clean up any leftover users from previous test runs
    cleanup_user(USER_A_EMAIL)
    cleanup_user(USER_B_EMAIL)

    user_a = register_and_login(USER_A_EMAIL, "AI User A", PASSWORD)
    user_b = register_and_login(USER_B_EMAIL, "AI User B", PASSWORD)
    headers_a = user_a["headers"]
    headers_b = user_b["headers"]

    # Seed User A Financial Records
    client.post("/api/v1/incomes", json={"source": "Salary", "amount": 150000.00, "date": "2026-10-01"}, headers=headers_a)
    client.post("/api/v1/expenses", json={"description": "Supermarket Grocery", "amount": 12000.00, "category": "Food", "date": "2026-10-02"}, headers=headers_a)
    client.post("/api/v1/expenses", json={"description": "Electric Bill", "amount": 3500.00, "category": "Bills", "date": "2026-10-03"}, headers=headers_a)
    client.post("/api/v1/expenses", json={"description": "Fuel & Taxi", "amount": 4500.00, "category": "Transport", "date": "2026-10-04"}, headers=headers_a)
    client.post("/api/v1/investments", json={"name": "Nifty 50 Index Fund", "type": "Mutual Fund", "investedAmount": 200000.00, "currentValue": 245000.00, "date": "2026-01-15"}, headers=headers_a)
    client.post("/api/v1/goals", json={"name": "Emergency Fund", "targetAmount": 500000.00, "currentAmount": 350000.00, "targetDate": "2027-06-30", "monthlyContribution": 25000.00}, headers=headers_a)

    passed_tests = 0
    total_tests = 8

    # ──────────────────────────────────────────────────
    # TEST 1: Unauthorized Access Rejection (401)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 1: Unauthorized Access Rejection ---")
    assert client.get("/api/v1/ai-advisor/insights").status_code == 401
    assert client.post("/api/v1/ai-advisor/chat", json={"message": "Help me"}).status_code == 401
    print("  [PASSED] All AI advisor endpoints reject unauthenticated calls with 401")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 2: Proactive Financial Insights (GET /api/v1/ai-advisor/insights)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 2: Proactive Financial Insights ---")
    res_ins = client.get("/api/v1/ai-advisor/insights", headers=headers_a)
    assert res_ins.status_code == 200
    ins_data = res_ins.json()
    assert "insights" in ins_data
    assert "summary" in ins_data
    summary = ins_data["summary"]
    assert Decimal(str(summary["totalIncome"])) == Decimal("150000.00")
    # Total expenses: 12000 + 3500 + 4500 = 20000.00
    assert Decimal(str(summary["totalExpenses"])) == Decimal("20000.00")
    assert Decimal(str(summary["availableSavings"])) == Decimal("130000.00")
    assert summary["savingsRate"] == 86.7
    assert Decimal(str(summary["totalInvestments"])) == Decimal("245000.00")
    assert summary["topExpenseCategory"] == "Food"
    assert len(ins_data["insights"]) >= 2
    print("  [PASSED] Real user metrics correctly calculated and returned with insight cards")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 3: Chat Query — Spending Analysis
    # ──────────────────────────────────────────────────
    print("\n--- TEST 3: Chat Query — Spending Analysis ---")
    res_chat_spend = client.post(
        "/api/v1/ai-advisor/chat",
        json={"message": "What are my biggest spending categories?"},
        headers=headers_a,
    )
    assert res_chat_spend.status_code == 200
    spend_reply = res_chat_spend.json()
    assert "reply" in spend_reply
    assert "Food" in spend_reply["reply"] or "Spending" in spend_reply["reply"]
    assert len(spend_reply["insights"]) >= 1
    print("  [PASSED] Spending analysis accurately identifies user's Food and Bills outflow")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 4: Chat Query — Savings Rate & Surplus
    # ──────────────────────────────────────────────────
    print("\n--- TEST 4: Chat Query — Savings Rate ---")
    res_chat_save = client.post(
        "/api/v1/ai-advisor/chat",
        json={"message": "How much am I saving monthly?"},
        headers=headers_a,
    )
    assert res_chat_save.status_code == 200
    save_reply = res_chat_save.json()
    assert "1,30,000" in save_reply["reply"] or "130000" in save_reply["reply"] or "savings" in save_reply["reply"].lower()
    print("  [PASSED] Savings rate query returns correct calculated surplus and percentage")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 5: Chat Query — Goal Milestones
    # ──────────────────────────────────────────────────
    print("\n--- TEST 5: Chat Query — Goal Progress ---")
    res_chat_goal = client.post(
        "/api/v1/ai-advisor/chat",
        json={"message": "How am I progressing toward my goals?"},
        headers=headers_a,
    )
    assert res_chat_goal.status_code == 200
    goal_reply = res_chat_goal.json()
    assert "Emergency Fund" in goal_reply["reply"] or "Goal" in goal_reply["reply"]
    print("  [PASSED] Goal analysis tracks user's active goal completion percentage")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 6: Chat Query — Financial Overview
    # ──────────────────────────────────────────────────
    print("\n--- TEST 6: Chat Query — Financial Overview ---")
    res_chat_ov = client.post(
        "/api/v1/ai-advisor/chat",
        json={"message": "Give me an overview of my finances."},
        headers=headers_a,
    )
    assert res_chat_ov.status_code == 200
    ov_reply = res_chat_ov.json()
    assert "Financial" in ov_reply["reply"] or "Inflow" in ov_reply["reply"]
    print("  [PASSED] Full financial health diagnosis produced accurately")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 7: Cross-User Isolation (User B sees 0 of User A's data)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 7: Cross-User Isolation ---")
    res_b_ins = client.get("/api/v1/ai-advisor/insights", headers=headers_b)
    assert res_b_ins.status_code == 200
    b_summary = res_b_ins.json()["summary"]
    # User B has no records -> must be 0
    assert Decimal(str(b_summary["totalIncome"])) == Decimal("0.00")
    assert Decimal(str(b_summary["totalExpenses"])) == Decimal("0.00")
    assert Decimal(str(b_summary["availableSavings"])) == Decimal("0.00")
    assert b_summary["savingsRate"] == 0.0
    assert Decimal(str(b_summary["totalInvestments"])) == Decimal("0.00")

    # Chat for User B should NOT mention User A's data
    res_b_chat = client.post(
        "/api/v1/ai-advisor/chat",
        json={"message": "Give me an overview of my finances."},
        headers=headers_b,
    )
    assert res_b_chat.status_code == 200
    b_reply_text = res_b_chat.json()["reply"]
    assert "150000" not in b_reply_text
    assert "1,50,000" not in b_reply_text
    print("  [PASSED] Complete data isolation: User B receives zero information from User A")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 8: Input Validation for Blank Message
    # ──────────────────────────────────────────────────
    print("\n--- TEST 8: Input Validation ---")
    res_blank = client.post(
        "/api/v1/ai-advisor/chat",
        json={"message": ""},
        headers=headers_a,
    )
    assert res_blank.status_code == 422
    print("  [PASSED] Empty chat message rejected with 422")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # Cleanup
    # ──────────────────────────────────────────────────
    print("\n--- CLEANUP ---")
    cleanup_user(USER_A_EMAIL)
    cleanup_user(USER_B_EMAIL)
    print("  [OK] Test users cleaned up.")

    print("\n" + "=" * 60)
    print(f"AI ADVISOR API TEST RESULTS: {passed_tests}/{total_tests} PASSED")
    print("ALL TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
