"""
Income API Comprehensive Test Suite
====================================
Tests for all Income CRUD endpoints, transaction synchronization,
authentication enforcement, cross-user isolation, and input validation.

Run: python test_income.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models import User, Income, Transaction

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
USER_A_EMAIL = "income.tester.a@nexwealth.in"
USER_B_EMAIL = "income.tester.b@nexwealth.in"
PASSWORD = "TestPassword@123"
passed = 0
failed = 0


def run_tests():
    global passed, failed

    print("=" * 60)
    print("INCOME API — COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    # Pre-clean
    cleanup_user(USER_A_EMAIL)
    cleanup_user(USER_B_EMAIL)

    # Setup: register two users
    user_a = register_and_login(USER_A_EMAIL, "Aarav Test", PASSWORD)
    user_b = register_and_login(USER_B_EMAIL, "Bharat Test", PASSWORD)

    headers_a = user_a["headers"]
    headers_b = user_b["headers"]

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TEST 1: Create Income
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def test_create_income():
        global passed, failed
        print("\n--- TEST 1: Create Income (POST /api/v1/incomes) ---")
        payload = {
            "source": "Monthly Salary",
            "amount": "75000.00",
            "date": "2026-10-01",
        }
        res = client.post("/api/v1/incomes", json=payload, headers=headers_a)
        print(f"  Status: {res.status_code}")
        data = res.json()
        print(f"  Response: {data}")

        try:
            assert res.status_code == 201, f"Expected 201, got {res.status_code}"
            assert data["source"] == "Monthly Salary"
            assert data["amount"] == "75000.00"
            assert data["date"] == "2026-10-01"
            assert data["userId"] == user_a["user"]["id"]
            assert "id" in data
            assert data["id"].startswith("inc_")
            print("  [PASSED] Income created successfully")
            passed += 1
            return data["id"]
        except AssertionError as e:
            print(f"  [FAILED] {e}")
            failed += 1
            return None

    income_id = test_create_income()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TEST 2: Transaction Synchronization on Create
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def test_transaction_sync_create():
        global passed, failed
        print("\n--- TEST 2: Transaction Sync on Create ---")
        db = SessionLocal()
        txns = (
            db.query(Transaction)
            .filter(
                Transaction.userId == user_a["user"]["id"],
                Transaction.type == "income",
                Transaction.source == "Monthly Salary",
            )
            .all()
        )
        db.close()
        print(f"  Found {len(txns)} matching transaction(s)")

        try:
            assert len(txns) == 1, f"Expected exactly 1 transaction, found {len(txns)}"
            txn = txns[0]
            assert str(txn.amount) == "75000.00", f"Transaction amount mismatch: {txn.amount}"
            assert txn.type == "income"
            assert txn.source == "Monthly Salary"
            assert txn.description == "Income: Monthly Salary"
            assert txn.category == "Income"
            print("  [PASSED] Exactly one mirrored transaction created")
            passed += 1
        except AssertionError as e:
            print(f"  [FAILED] {e}")
            failed += 1

    test_transaction_sync_create()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TEST 3: List Incomes
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def test_list_incomes():
        global passed, failed
        print("\n--- TEST 3: List Incomes (GET /api/v1/incomes) ---")
        # Create a second income
        client.post("/api/v1/incomes", json={
            "source": "Freelance Work",
            "amount": "15000.50",
            "date": "2026-10-05",
        }, headers=headers_a)

        res = client.get("/api/v1/incomes", headers=headers_a)
        print(f"  Status: {res.status_code}")
        data = res.json()
        print(f"  Found {len(data)} income(s)")

        try:
            assert res.status_code == 200, f"Expected 200, got {res.status_code}"
            assert len(data) >= 2, f"Expected at least 2 incomes, got {len(data)}"
            # Should be ordered by date desc (Oct 5 before Oct 1)
            assert data[0]["date"] >= data[-1]["date"], "Incomes not sorted by date desc"
            print("  [PASSED] Listed all user incomes in correct order")
            passed += 1
        except AssertionError as e:
            print(f"  [FAILED] {e}")
            failed += 1

    test_list_incomes()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TEST 4: Get Single Income
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def test_get_income():
        global passed, failed
        print("\n--- TEST 4: Get Single Income (GET /api/v1/incomes/{id}) ---")
        if not income_id:
            print("  [SKIPPED] No income_id from TEST 1")
            return
        res = client.get(f"/api/v1/incomes/{income_id}", headers=headers_a)
        print(f"  Status: {res.status_code}")
        data = res.json()

        try:
            assert res.status_code == 200, f"Expected 200, got {res.status_code}"
            assert data["id"] == income_id
            assert data["source"] == "Monthly Salary"
            assert data["userId"] == user_a["user"]["id"]
            print("  [PASSED] Retrieved correct income by ID")
            passed += 1
        except AssertionError as e:
            print(f"  [FAILED] {e}")
            failed += 1

    test_get_income()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TEST 5: Update Income
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def test_update_income():
        global passed, failed
        print("\n--- TEST 5: Update Income (PUT /api/v1/incomes/{id}) ---")
        if not income_id:
            print("  [SKIPPED] No income_id from TEST 1")
            return
        update_payload = {
            "source": "Updated Salary",
            "amount": "80000.00",
        }
        res = client.put(f"/api/v1/incomes/{income_id}", json=update_payload, headers=headers_a)
        print(f"  Status: {res.status_code}")
        data = res.json()
        print(f"  Response: {data}")

        try:
            assert res.status_code == 200, f"Expected 200, got {res.status_code}"
            assert data["source"] == "Updated Salary"
            assert data["amount"] == "80000.00"
            assert data["date"] == "2026-10-01"  # unchanged
            print("  [PASSED] Income updated successfully (partial update)")
            passed += 1
        except AssertionError as e:
            print(f"  [FAILED] {e}")
            failed += 1

    test_update_income()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TEST 6: Transaction Synchronization on Update
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def test_transaction_sync_update():
        global passed, failed
        print("\n--- TEST 6: Transaction Sync on Update ---")
        db = SessionLocal()
        txns = (
            db.query(Transaction)
            .filter(
                Transaction.userId == user_a["user"]["id"],
                Transaction.type == "income",
                Transaction.source == "Updated Salary",
            )
            .all()
        )
        db.close()
        print(f"  Found {len(txns)} matching transaction(s)")

        try:
            assert len(txns) == 1, f"Expected 1 transaction, found {len(txns)}"
            assert str(txns[0].amount) == "80000.00", f"Transaction amount not updated: {txns[0].amount}"
            assert txns[0].description == "Income: Updated Salary"
            print("  [PASSED] Transaction updated in sync with income")
            passed += 1
        except AssertionError as e:
            print(f"  [FAILED] {e}")
            failed += 1

    test_transaction_sync_update()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TEST 7: Unauthorized Access (No Token)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def test_unauthorized_access():
        global passed, failed
        print("\n--- TEST 7: Unauthorized Access (No Token) ---")
        endpoints = [
            ("POST", "/api/v1/incomes"),
            ("GET", "/api/v1/incomes"),
            ("GET", "/api/v1/incomes/fake_id"),
            ("PUT", "/api/v1/incomes/fake_id"),
            ("DELETE", "/api/v1/incomes/fake_id"),
        ]
        all_pass = True
        for method, url in endpoints:
            if method == "POST":
                res = client.post(url, json={"source": "test", "amount": "100.00", "date": "2026-01-01"})
            elif method == "PUT":
                res = client.put(url, json={"source": "test"})
            elif method == "DELETE":
                res = client.delete(url)
            else:
                res = client.get(url)

            if res.status_code != 401:
                print(f"  [FAILED] {method} {url} returned {res.status_code}, expected 401")
                all_pass = False

        try:
            assert all_pass, "Not all endpoints returned 401 without token"
            print("  [PASSED] All 5 endpoints reject unauthenticated requests (401)")
            passed += 1
        except AssertionError as e:
            print(f"  [FAILED] {e}")
            failed += 1

    test_unauthorized_access()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TEST 8: Cross-User Access (User B cannot access User A's income)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def test_cross_user_access():
        global passed, failed
        print("\n--- TEST 8: Cross-User Access Isolation ---")
        if not income_id:
            print("  [SKIPPED] No income_id from TEST 1")
            return

        # User B tries to GET User A's income
        res_get = client.get(f"/api/v1/incomes/{income_id}", headers=headers_b)
        # User B tries to UPDATE User A's income
        res_put = client.put(f"/api/v1/incomes/{income_id}", json={"source": "Hacked"}, headers=headers_b)
        # User B tries to DELETE User A's income
        res_del = client.delete(f"/api/v1/incomes/{income_id}", headers=headers_b)

        print(f"  GET by User B: {res_get.status_code}")
        print(f"  PUT by User B: {res_put.status_code}")
        print(f"  DELETE by User B: {res_del.status_code}")

        # User B lists their own incomes — should be empty
        res_list = client.get("/api/v1/incomes", headers=headers_b)

        try:
            assert res_get.status_code == 404, f"GET should be 404, got {res_get.status_code}"
            assert res_put.status_code == 404, f"PUT should be 404, got {res_put.status_code}"
            assert res_del.status_code == 404, f"DELETE should be 404, got {res_del.status_code}"
            assert res_list.status_code == 200
            assert len(res_list.json()) == 0, f"User B should have 0 incomes, got {len(res_list.json())}"
            print("  [PASSED] Cross-user access correctly blocked (404 + empty list)")
            passed += 1
        except AssertionError as e:
            print(f"  [FAILED] {e}")
            failed += 1

    test_cross_user_access()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TEST 9: Invalid / Negative Amount
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def test_invalid_amount():
        global passed, failed
        print("\n--- TEST 9: Invalid / Negative Amount ---")
        invalid_payloads = [
            ({"source": "Bad", "amount": "-500.00", "date": "2026-01-01"}, "negative"),
            ({"source": "Bad", "amount": "0", "date": "2026-01-01"}, "zero"),
            ({"source": "Bad", "amount": "not_a_number", "date": "2026-01-01"}, "non-numeric"),
        ]
        all_rejected = True
        for payload, label in invalid_payloads:
            res = client.post("/api/v1/incomes", json=payload, headers=headers_a)
            if res.status_code != 422:
                print(f"  [FAILED] {label} amount returned {res.status_code}, expected 422")
                all_rejected = False
            else:
                print(f"  {label} amount -> 422 OK")

        try:
            assert all_rejected, "Not all invalid amounts were rejected"
            print("  [PASSED] All invalid amounts rejected with 422")
            passed += 1
        except AssertionError as e:
            print(f"  [FAILED] {e}")
            failed += 1

    test_invalid_amount()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TEST 10: Duplicate Transaction Prevention
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def test_no_duplicate_transactions():
        global passed, failed
        print("\n--- TEST 10: Duplicate Transaction Prevention ---")
        db = SessionLocal()
        user_id_a = user_a["user"]["id"]

        # Count total income transactions for user A
        total_income_txns = (
            db.query(Transaction)
            .filter(
                Transaction.userId == user_id_a,
                Transaction.type == "income",
            )
            .count()
        )
        total_incomes = (
            db.query(Income)
            .filter(Income.userId == user_id_a)
            .count()
        )
        db.close()

        print(f"  Income records: {total_incomes}")
        print(f"  Income transactions: {total_income_txns}")

        try:
            assert total_income_txns == total_incomes, (
                f"Transaction count ({total_income_txns}) != Income count ({total_incomes})"
            )
            print("  [PASSED] No duplicate transactions — counts match perfectly")
            passed += 1
        except AssertionError as e:
            print(f"  [FAILED] {e}")
            failed += 1

    test_no_duplicate_transactions()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TEST 11: Delete Income + Transaction Sync
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def test_delete_income():
        global passed, failed
        print("\n--- TEST 11: Delete Income (DELETE /api/v1/incomes/{id}) ---")
        if not income_id:
            print("  [SKIPPED] No income_id from TEST 1")
            return

        res = client.delete(f"/api/v1/incomes/{income_id}", headers=headers_a)
        print(f"  Status: {res.status_code}")
        data = res.json()
        print(f"  Response: {data}")

        try:
            assert res.status_code == 200, f"Expected 200, got {res.status_code}"
            assert data["id"] == income_id
            assert "deleted" in data["message"].lower()
            print("  [PASSED] Income deleted successfully")
            passed += 1
        except AssertionError as e:
            print(f"  [FAILED] {e}")
            failed += 1

        # Verify income is gone
        res_get = client.get(f"/api/v1/incomes/{income_id}", headers=headers_a)
        try:
            assert res_get.status_code == 404, f"Deleted income still accessible: {res_get.status_code}"
            print("  [PASSED] Deleted income returns 404")
            passed += 1
        except AssertionError as e:
            print(f"  [FAILED] {e}")
            failed += 1

        # Verify transaction was also deleted
        db = SessionLocal()
        txn = (
            db.query(Transaction)
            .filter(
                Transaction.userId == user_a["user"]["id"],
                Transaction.type == "income",
                Transaction.source == "Updated Salary",
            )
            .first()
        )
        db.close()

        try:
            assert txn is None, "Transaction for deleted income still exists!"
            print("  [PASSED] Corresponding transaction also deleted")
            passed += 1
        except AssertionError as e:
            print(f"  [FAILED] {e}")
            failed += 1

    test_delete_income()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Cleanup
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n--- CLEANUP ---")
    cleanup_user(USER_A_EMAIL)
    cleanup_user(USER_B_EMAIL)
    print("  [OK] Test users cleaned up.")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Final Report
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    total = passed + failed
    print("\n" + "=" * 60)
    print(f"INCOME API TEST RESULTS: {passed}/{total} PASSED")
    if failed == 0:
        print("ALL TESTS PASSED!")
    else:
        print(f"{failed} TEST(S) FAILED")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
