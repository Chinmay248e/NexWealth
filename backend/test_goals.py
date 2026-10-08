"""
Goals API Comprehensive Test Suite (Person 2)
==============================================
Tests for all Goal CRUD and add-funds endpoints, authentication enforcement,
cross-user isolation, Decimal monetary precision, and input validation.

Run: python test_goals.py
"""
import sys
import os
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models import User, Goal

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
USER_A_EMAIL = "goal.tester.a@nexwealth.in"
USER_B_EMAIL = "goal.tester.b@nexwealth.in"
PASSWORD = "TestPassword@123"

def run_tests():
    print("=" * 60)
    print("GOALS API — COMPREHENSIVE TEST SUITE (PERSON 2)")
    print("=" * 60)

    # Clean up any leftover users from previous test runs
    cleanup_user(USER_A_EMAIL)
    cleanup_user(USER_B_EMAIL)

    user_a = register_and_login(USER_A_EMAIL, "Goal User A", PASSWORD)
    user_b = register_and_login(USER_B_EMAIL, "Goal User B", PASSWORD)
    headers_a = user_a["headers"]
    headers_b = user_b["headers"]

    passed_tests = 0
    total_tests = 11

    # ──────────────────────────────────────────────────
    # TEST 1: Create Goal (POST /api/v1/goals)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 1: Create Goal (POST /api/v1/goals) ---")
    payload_1 = {
        "name": "Emergency Liquidity Reserve",
        "targetAmount": 500000.00,
        "currentAmount": 175000.50,
        "targetDate": "2027-03-31",
        "monthlyContribution": 25000.00,
    }
    res = client.post("/api/v1/goals", json=payload_1, headers=headers_a)
    assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"
    goal_1 = res.json()
    assert goal_1["id"].startswith("gol_"), f"Invalid ID prefix: {goal_1['id']}"
    assert goal_1["userId"] == user_a["user"]["id"]
    assert goal_1["name"] == "Emergency Liquidity Reserve"
    assert Decimal(str(goal_1["targetAmount"])) == Decimal("500000.00")
    assert Decimal(str(goal_1["currentAmount"])) == Decimal("175000.50")
    assert goal_1["targetDate"] == "2027-03-31"
    assert Decimal(str(goal_1["monthlyContribution"])) == Decimal("25000.00")
    assert "createdAt" in goal_1
    print("  [PASSED] Goal created successfully with all contract fields")
    passed_tests += 1

    # Create a second goal for User A
    payload_2 = {
        "name": "Electric Vehicle Fund",
        "targetAmount": 1500000.00,
        "currentAmount": 300000.00,
        "targetDate": "2028-12-31",
        "monthlyContribution": 40000.00,
    }
    res2 = client.post("/api/v1/goals", json=payload_2, headers=headers_a)
    assert res2.status_code == 201
    goal_2 = res2.json()

    # ──────────────────────────────────────────────────
    # TEST 2: List Goals (GET /api/v1/goals)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 2: List Goals (GET /api/v1/goals) ---")
    res = client.get("/api/v1/goals", headers=headers_a)
    assert res.status_code == 200
    goals_list = res.json()
    assert len(goals_list) == 2
    # Verify target date order (2027-03-31 should be before 2028-12-31)
    assert goals_list[0]["id"] == goal_1["id"]
    assert goals_list[1]["id"] == goal_2["id"]
    print("  [PASSED] Listed all user goals in correct ascending targetDate order")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 3: Get Single Goal (GET /api/v1/goals/{id})
    # ──────────────────────────────────────────────────
    print("\n--- TEST 3: Get Single Goal (GET /api/v1/goals/{id}) ---")
    res = client.get(f"/api/v1/goals/{goal_1['id']}", headers=headers_a)
    assert res.status_code == 200
    fetched = res.json()
    assert fetched["id"] == goal_1["id"]
    assert fetched["name"] == "Emergency Liquidity Reserve"
    print("  [PASSED] Retrieved correct goal by ID")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 4: Update Goal (PUT /api/v1/goals/{id})
    # ──────────────────────────────────────────────────
    print("\n--- TEST 4: Update Goal (PUT /api/v1/goals/{id}) ---")
    update_payload = {
        "name": "Emergency Fund Enhanced",
        "targetAmount": 600000.00,
    }
    res = client.put(f"/api/v1/goals/{goal_1['id']}", json=update_payload, headers=headers_a)
    assert res.status_code == 200
    updated = res.json()
    assert updated["name"] == "Emergency Fund Enhanced"
    assert Decimal(str(updated["targetAmount"])) == Decimal("600000.00")
    # Unchanged fields remain preserved
    assert Decimal(str(updated["currentAmount"])) == Decimal("175000.50")
    print("  [PASSED] Goal updated successfully (partial update)")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 5: Add Funds to Goal (POST /api/v1/goals/{id}/add-funds)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 5: Add Funds to Goal (POST /api/v1/goals/{id}/add-funds) ---")
    fund_res = client.post(
        f"/api/v1/goals/{goal_1['id']}/add-funds",
        json={"amount": 25000.50},
        headers=headers_a,
    )
    assert fund_res.status_code == 200
    funded = fund_res.json()
    # 175000.50 + 25000.50 = 200001.00
    assert Decimal(str(funded["currentAmount"])) == Decimal("200001.00")
    print("  [PASSED] Funds added to goal successfully (currentAmount incremented)")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 6: Unauthorized Access (No Token / Invalid)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 6: Unauthorized Access (401 Rejection) ---")
    assert client.post("/api/v1/goals", json=payload_1).status_code == 401
    assert client.get("/api/v1/goals").status_code == 401
    assert client.get(f"/api/v1/goals/{goal_1['id']}").status_code == 401
    assert client.put(f"/api/v1/goals/{goal_1['id']}", json=update_payload).status_code == 401
    assert client.post(f"/api/v1/goals/{goal_1['id']}/add-funds", json={"amount": 100}).status_code == 401
    assert client.delete(f"/api/v1/goals/{goal_1['id']}").status_code == 401
    print("  [PASSED] All 6 endpoints reject unauthenticated requests with 401")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 7: Cross-User Access Isolation
    # ──────────────────────────────────────────────────
    print("\n--- TEST 7: Cross-User Access Isolation ---")
    # User B should see 0 goals
    res_b_list = client.get("/api/v1/goals", headers=headers_b)
    assert res_b_list.status_code == 200
    assert len(res_b_list.json()) == 0

    # User B cannot GET User A's goal
    res_b_get = client.get(f"/api/v1/goals/{goal_1['id']}", headers=headers_b)
    assert res_b_get.status_code == 404

    # User B cannot PUT User A's goal
    res_b_put = client.put(f"/api/v1/goals/{goal_1['id']}", json={"name": "Hacked"}, headers=headers_b)
    assert res_b_put.status_code == 404

    # User B cannot add funds to User A's goal
    res_b_fund = client.post(f"/api/v1/goals/{goal_1['id']}/add-funds", json={"amount": 1000}, headers=headers_b)
    assert res_b_fund.status_code == 404

    # User B cannot DELETE User A's goal
    res_b_del = client.delete(f"/api/v1/goals/{goal_1['id']}", headers=headers_b)
    assert res_b_del.status_code == 404

    print("  [PASSED] Cross-user access strictly isolated (404 for unauthorized reads/writes)")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 8: Input Validation (Amounts)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 8: Input Validation (Amounts) ---")
    # Negative targetAmount -> 422
    res_neg_tgt = client.post("/api/v1/goals", json={**payload_1, "targetAmount": -5000}, headers=headers_a)
    assert res_neg_tgt.status_code == 422

    # Zero targetAmount -> 422 (must be positive)
    res_zero_tgt = client.post("/api/v1/goals", json={**payload_1, "targetAmount": 0}, headers=headers_a)
    assert res_zero_tgt.status_code == 422

    # Negative currentAmount -> 422
    res_neg_cur = client.post("/api/v1/goals", json={**payload_1, "currentAmount": -100}, headers=headers_a)
    assert res_neg_cur.status_code == 422

    # Negative monthlyContribution -> 422
    res_neg_mth = client.post("/api/v1/goals", json={**payload_1, "monthlyContribution": -100}, headers=headers_a)
    assert res_neg_mth.status_code == 422

    print("  [PASSED] Amount validation rules enforced (positive targetAmount, non-negative current/monthly)")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 9: Input Validation (Blank Name & Missing Fields)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 9: Input Validation (Required Fields & Blanks) ---")
    # Blank name -> 422
    res_blank_name = client.post("/api/v1/goals", json={**payload_1, "name": "   "}, headers=headers_a)
    assert res_blank_name.status_code == 422

    # Missing targetDate -> 422
    p_no_date = {k: v for k, v in payload_1.items() if k != "targetDate"}
    res_no_date = client.post("/api/v1/goals", json=p_no_date, headers=headers_a)
    assert res_no_date.status_code == 422

    print("  [PASSED] Blank strings and missing required fields rejected with 422")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 10: Decimal Precision
    # ──────────────────────────────────────────────────
    print("\n--- TEST 10: Exact Decimal Precision ---")
    decimal_payload = {
        "name": "High Precision Goal",
        "targetAmount": 987654.32,
        "currentAmount": 123456.78,
        "targetDate": "2029-06-30",
        "monthlyContribution": 11111.11,
    }
    res_dec = client.post("/api/v1/goals", json=decimal_payload, headers=headers_a)
    assert res_dec.status_code == 201
    dec_obj = res_dec.json()
    assert Decimal(str(dec_obj["targetAmount"])) == Decimal("987654.32")
    assert Decimal(str(dec_obj["currentAmount"])) == Decimal("123456.78")
    assert Decimal(str(dec_obj["monthlyContribution"])) == Decimal("11111.11")
    print("  [PASSED] Exact Decimal precision preserved without floating-point distortion")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 11: Delete Goal (DELETE /api/v1/goals/{id})
    # ──────────────────────────────────────────────────
    print("\n--- TEST 11: Delete Goal (DELETE /api/v1/goals/{id}) ---")
    del_res = client.delete(f"/api/v1/goals/{goal_1['id']}", headers=headers_a)
    assert del_res.status_code == 200
    del_data = del_res.json()
    assert del_data["id"] == goal_1["id"]
    assert "deleted successfully" in del_data["message"].lower()

    # Subsequent GET returns 404
    get_after_del = client.get(f"/api/v1/goals/{goal_1['id']}", headers=headers_a)
    assert get_after_del.status_code == 404

    # Subsequent DELETE returns 404
    del_again = client.delete(f"/api/v1/goals/{goal_1['id']}", headers=headers_a)
    assert del_again.status_code == 404

    print("  [PASSED] Goal deleted successfully and subsequent accesses return 404")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # Cleanup
    # ──────────────────────────────────────────────────
    print("\n--- CLEANUP ---")
    cleanup_user(USER_A_EMAIL)
    cleanup_user(USER_B_EMAIL)
    print("  [OK] Test users cleaned up.")

    print("\n" + "=" * 60)
    print(f"GOALS API TEST RESULTS: {passed_tests}/{total_tests} PASSED")
    print("ALL TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
