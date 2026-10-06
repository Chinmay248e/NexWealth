"""
Investments API Comprehensive Test Suite
========================================
Tests for all Person 3 Investment CRUD endpoints, authentication enforcement,
cross-user isolation, Decimal monetary precision, and input validation.

Run: python test_investments.py
"""
import sys
import os
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models import User, Investment

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
USER_A_EMAIL = "inv.tester.a@nexwealth.in"
USER_B_EMAIL = "inv.tester.b@nexwealth.in"
PASSWORD = "TestPassword@123"

def run_tests():
    print("=" * 60)
    print("INVESTMENTS API — COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    # Clean up any leftover users from previous test runs
    cleanup_user(USER_A_EMAIL)
    cleanup_user(USER_B_EMAIL)

    user_a = register_and_login(USER_A_EMAIL, "Investor A", PASSWORD)
    user_b = register_and_login(USER_B_EMAIL, "Investor B", PASSWORD)
    headers_a = user_a["headers"]
    headers_b = user_b["headers"]

    passed_tests = 0
    total_tests = 10

    # ──────────────────────────────────────────────────
    # TEST 1: Create Investment (POST /api/v1/investments)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 1: Create Investment (POST /api/v1/investments) ---")
    payload_1 = {
        "name": "Nifty 50 Index Fund",
        "type": "Mutual Fund",
        "investedAmount": 200000.00,
        "currentValue": 248500.50,
        "date": "2025-11-15",
    }
    res = client.post("/api/v1/investments", json=payload_1, headers=headers_a)
    assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"
    inv_1 = res.json()
    assert inv_1["id"].startswith("inv_"), f"Invalid ID prefix: {inv_1['id']}"
    assert inv_1["userId"] == user_a["user"]["id"]
    assert inv_1["name"] == "Nifty 50 Index Fund"
    assert inv_1["type"] == "Mutual Fund"
    assert Decimal(str(inv_1["investedAmount"])) == Decimal("200000.00")
    assert Decimal(str(inv_1["currentValue"])) == Decimal("248500.50")
    assert inv_1["date"] == "2025-11-15"
    assert "createdAt" in inv_1
    print("  [PASSED] Investment created successfully with all contract fields")
    passed_tests += 1

    # Create a second investment for User A
    payload_2 = {
        "name": "Sovereign Gold Bond 2026-I",
        "type": "Gold",
        "investedAmount": 150000.00,
        "currentValue": 172000.00,
        "date": "2026-01-10",
    }
    res2 = client.post("/api/v1/investments", json=payload_2, headers=headers_a)
    assert res2.status_code == 201
    inv_2 = res2.json()

    # ──────────────────────────────────────────────────
    # TEST 2: List Investments (GET /api/v1/investments)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 2: List Investments (GET /api/v1/investments) ---")
    res = client.get("/api/v1/investments", headers=headers_a)
    assert res.status_code == 200
    incomes_list = res.json()
    assert len(incomes_list) == 2
    # Verify descending date order (2026-01-10 should be before 2025-11-15)
    assert incomes_list[0]["id"] == inv_2["id"]
    assert incomes_list[1]["id"] == inv_1["id"]
    print("  [PASSED] Listed all user investments in correct descending date order")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 3: Get Single Investment (GET /api/v1/investments/{id})
    # ──────────────────────────────────────────────────
    print("\n--- TEST 3: Get Single Investment (GET /api/v1/investments/{id}) ---")
    res = client.get(f"/api/v1/investments/{inv_1['id']}", headers=headers_a)
    assert res.status_code == 200
    fetched = res.json()
    assert fetched["id"] == inv_1["id"]
    assert fetched["name"] == "Nifty 50 Index Fund"
    print("  [PASSED] Retrieved correct investment by ID")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 4: Update Investment (PUT /api/v1/investments/{id})
    # ──────────────────────────────────────────────────
    print("\n--- TEST 4: Update Investment (PUT /api/v1/investments/{id}) ---")
    update_payload = {
        "currentValue": 265000.75,
        "name": "Nifty 50 Direct Plan Growth",
    }
    res = client.put(f"/api/v1/investments/{inv_1['id']}", json=update_payload, headers=headers_a)
    assert res.status_code == 200
    updated = res.json()
    assert updated["name"] == "Nifty 50 Direct Plan Growth"
    assert Decimal(str(updated["currentValue"])) == Decimal("265000.75")
    # Unchanged fields remain preserved
    assert updated["type"] == "Mutual Fund"
    assert Decimal(str(updated["investedAmount"])) == Decimal("200000.00")
    print("  [PASSED] Investment updated successfully (partial update)")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 5: Unauthorized Access (No Token / Invalid)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 5: Unauthorized Access (401 Rejection) ---")
    assert client.post("/api/v1/investments", json=payload_1).status_code == 401
    assert client.get("/api/v1/investments").status_code == 401
    assert client.get(f"/api/v1/investments/{inv_1['id']}").status_code == 401
    assert client.put(f"/api/v1/investments/{inv_1['id']}", json=update_payload).status_code == 401
    assert client.delete(f"/api/v1/investments/{inv_1['id']}").status_code == 401
    print("  [PASSED] All 5 endpoints reject unauthenticated requests with 401")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 6: Cross-User Access Isolation
    # ──────────────────────────────────────────────────
    print("\n--- TEST 6: Cross-User Access Isolation ---")
    # User B should see 0 investments
    res_b_list = client.get("/api/v1/investments", headers=headers_b)
    assert res_b_list.status_code == 200
    assert len(res_b_list.json()) == 0

    # User B cannot GET User A's investment
    res_b_get = client.get(f"/api/v1/investments/{inv_1['id']}", headers=headers_b)
    assert res_b_get.status_code == 404

    # User B cannot PUT User A's investment
    res_b_put = client.put(f"/api/v1/investments/{inv_1['id']}", json={"currentValue": 300000}, headers=headers_b)
    assert res_b_put.status_code == 404

    # User B cannot DELETE User A's investment
    res_b_del = client.delete(f"/api/v1/investments/{inv_1['id']}", headers=headers_b)
    assert res_b_del.status_code == 404

    print("  [PASSED] Cross-user access strictly isolated (404 for unauthorized reads/writes)")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 7: Input Validation (Amounts)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 7: Input Validation (Amounts) ---")
    # Negative investedAmount -> 422
    res_neg_inv = client.post("/api/v1/investments", json={**payload_1, "investedAmount": -5000}, headers=headers_a)
    assert res_neg_inv.status_code == 422

    # Zero investedAmount -> 422 (must be positive)
    res_zero_inv = client.post("/api/v1/investments", json={**payload_1, "investedAmount": 0}, headers=headers_a)
    assert res_zero_inv.status_code == 422

    # Negative currentValue -> 422
    res_neg_val = client.post("/api/v1/investments", json={**payload_1, "currentValue": -100}, headers=headers_a)
    assert res_neg_val.status_code == 422

    # Zero currentValue -> 201 (Valid: e.g. an asset whose value dropped to 0)
    res_zero_val = client.post("/api/v1/investments", json={**payload_1, "name": "Defunct Token", "currentValue": 0}, headers=headers_a)
    assert res_zero_val.status_code == 201
    assert Decimal(str(res_zero_val.json()["currentValue"])) == Decimal("0.00")

    print("  [PASSED] Amount validation rules enforced (positive investedAmount, non-negative currentValue)")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 8: Input Validation (Required Fields & Blanks)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 8: Input Validation (Required Fields & Blanks) ---")
    # Blank name -> 422
    res_blank_name = client.post("/api/v1/investments", json={**payload_1, "name": "   "}, headers=headers_a)
    assert res_blank_name.status_code == 422

    # Blank type -> 422
    res_blank_type = client.post("/api/v1/investments", json={**payload_1, "type": "   "}, headers=headers_a)
    assert res_blank_type.status_code == 422

    # Missing name -> 422
    p_no_name = {k: v for k, v in payload_1.items() if k != "name"}
    res_no_name = client.post("/api/v1/investments", json=p_no_name, headers=headers_a)
    assert res_no_name.status_code == 422

    print("  [PASSED] Blank strings and missing required fields rejected with 422")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 9: Decimal Precision
    # ──────────────────────────────────────────────────
    print("\n--- TEST 9: Exact Decimal Precision ---")
    decimal_payload = {
        "name": "High Precision Asset",
        "type": "Stock",
        "investedAmount": 123456.78,
        "currentValue": 987654.32,
        "date": "2026-03-01",
    }
    res_dec = client.post("/api/v1/investments", json=decimal_payload, headers=headers_a)
    assert res_dec.status_code == 201
    dec_obj = res_dec.json()
    assert Decimal(str(dec_obj["investedAmount"])) == Decimal("123456.78")
    assert Decimal(str(dec_obj["currentValue"])) == Decimal("987654.32")
    print("  [PASSED] Exact Decimal precision preserved without floating-point distortion")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 10: Delete Investment (DELETE /api/v1/investments/{id})
    # ──────────────────────────────────────────────────
    print("\n--- TEST 10: Delete Investment (DELETE /api/v1/investments/{id}) ---")
    del_res = client.delete(f"/api/v1/investments/{inv_1['id']}", headers=headers_a)
    assert del_res.status_code == 200
    del_data = del_res.json()
    assert del_data["id"] == inv_1["id"]
    assert "deleted successfully" in del_data["message"].lower()

    # Subsequent GET returns 404
    get_after_del = client.get(f"/api/v1/investments/{inv_1['id']}", headers=headers_a)
    assert get_after_del.status_code == 404

    # Subsequent DELETE returns 404
    del_again = client.delete(f"/api/v1/investments/{inv_1['id']}", headers=headers_a)
    assert del_again.status_code == 404

    print("  [PASSED] Investment deleted successfully and subsequent accesses return 404")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # Cleanup
    # ──────────────────────────────────────────────────
    print("\n--- CLEANUP ---")
    cleanup_user(USER_A_EMAIL)
    cleanup_user(USER_B_EMAIL)
    print("  [OK] Test users cleaned up.")

    print("\n" + "=" * 60)
    print(f"INVESTMENTS API TEST RESULTS: {passed_tests}/{total_tests} PASSED")
    print("ALL TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
