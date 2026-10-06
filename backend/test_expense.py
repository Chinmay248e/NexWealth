"""
Expense API Comprehensive Test Suite
======================================
Tests for all Expense CRUD endpoints, transaction synchronization,
authentication enforcement, cross-user isolation, input validation,
invalid categories, and duplicate transaction prevention.

Run: python test_expense.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models import User, Expense, Transaction

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
USER_A_EMAIL = "expense.tester.a@nexwealth.in"
USER_B_EMAIL = "expense.tester.b@nexwealth.in"
PASSWORD = "TestPassword@123"
passed = 0
failed = 0


def run_tests():
    global passed, failed

    print("=" * 60)
    print("EXPENSE API -- COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    # Pre-clean
    cleanup_user(USER_A_EMAIL)
    cleanup_user(USER_B_EMAIL)

    # Setup: register two users
    user_a = register_and_login(USER_A_EMAIL, "Aarav Expense", PASSWORD)
    user_b = register_and_login(USER_B_EMAIL, "Bharat Expense", PASSWORD)

    headers_a = user_a["headers"]
    headers_b = user_b["headers"]

    # ==================================================
    # TEST 1: Create Expense
    # ==================================================
    def test_create_expense():
        global passed, failed
        print("\n--- TEST 1: Create Expense (POST /api/v1/expenses) ---")
        payload = {
            "description": "Grocery shopping at BigBasket",
            "amount": "2450.75",
            "category": "Food",
            "date": "2026-10-01",
        }
        res = client.post("/api/v1/expenses", json=payload, headers=headers_a)
        print(f"  Status: {res.status_code}")
        data = res.json()
        print(f"  Response: {data}")

        try:
            assert res.status_code == 201, f"Expected 201, got {res.status_code}"
            assert data["description"] == "Grocery shopping at BigBasket"
            assert data["amount"] == "2450.75"
            assert data["category"] == "Food"
            assert data["date"] == "2026-10-01"
            assert data["userId"] == user_a["user"]["id"]
            assert "id" in data
            assert data["id"].startswith("exp_")
            print("  [PASSED] Expense created successfully")
            passed += 1
            return data["id"]
        except AssertionError as e:
            print(f"  [FAILED] {e}")
            failed += 1
            return None

    expense_id = test_create_expense()

    # ==================================================
    # TEST 2: Transaction Synchronization on Create
    # ==================================================
    def test_transaction_sync_create():
        global passed, failed
        print("\n--- TEST 2: Transaction Sync on Create ---")
        db = SessionLocal()
        txns = (
            db.query(Transaction)
            .filter(
                Transaction.userId == user_a["user"]["id"],
                Transaction.type == "expense",
                Transaction.description == "Grocery shopping at BigBasket",
            )
            .all()
        )
        db.close()
        print(f"  Found {len(txns)} matching transaction(s)")

        try:
            assert len(txns) == 1, f"Expected exactly 1 transaction, found {len(txns)}"
            txn = txns[0]
            assert str(txn.amount) == "2450.75", f"Transaction amount mismatch: {txn.amount}"
            assert txn.type == "expense"
            assert txn.category == "Food"
            assert txn.description == "Grocery shopping at BigBasket"
            assert str(txn.date) == "2026-10-01"
            assert txn.userId == user_a["user"]["id"]
            print("  [PASSED] Exactly one mirrored transaction created with matching fields")
            passed += 1
        except AssertionError as e:
            print(f"  [FAILED] {e}")
            failed += 1

    test_transaction_sync_create()

    # ==================================================
    # TEST 3: List Expenses
    # ==================================================
    def test_list_expenses():
        global passed, failed
        print("\n--- TEST 3: List Expenses (GET /api/v1/expenses) ---")
        # Create a second expense
        client.post("/api/v1/expenses", json={
            "description": "Uber ride to office",
            "amount": "350.00",
            "category": "Transport",
            "date": "2026-10-05",
        }, headers=headers_a)

        res = client.get("/api/v1/expenses", headers=headers_a)
        print(f"  Status: {res.status_code}")
        data = res.json()
        print(f"  Found {len(data)} expense(s)")

        try:
            assert res.status_code == 200, f"Expected 200, got {res.status_code}"
            assert len(data) >= 2, f"Expected at least 2 expenses, got {len(data)}"
            # Should be ordered by date desc (Oct 5 before Oct 1)
            assert data[0]["date"] >= data[-1]["date"], "Expenses not sorted by date desc"
            print("  [PASSED] Listed all user expenses in correct order")
            passed += 1
        except AssertionError as e:
            print(f"  [FAILED] {e}")
            failed += 1

    test_list_expenses()

    # ==================================================
    # TEST 4: Get Single Expense
    # ==================================================
    def test_get_expense():
        global passed, failed
        print("\n--- TEST 4: Get Single Expense (GET /api/v1/expenses/{id}) ---")
        if not expense_id:
            print("  [SKIPPED] No expense_id from TEST 1")
            return
        res = client.get(f"/api/v1/expenses/{expense_id}", headers=headers_a)
        print(f"  Status: {res.status_code}")
        data = res.json()

        try:
            assert res.status_code == 200, f"Expected 200, got {res.status_code}"
            assert data["id"] == expense_id
            assert data["description"] == "Grocery shopping at BigBasket"
            assert data["userId"] == user_a["user"]["id"]
            print("  [PASSED] Retrieved correct expense by ID")
            passed += 1
        except AssertionError as e:
            print(f"  [FAILED] {e}")
            failed += 1

    test_get_expense()

    # ==================================================
    # TEST 5: Update Expense
    # ==================================================
    def test_update_expense():
        global passed, failed
        print("\n--- TEST 5: Update Expense (PUT /api/v1/expenses/{id}) ---")
        if not expense_id:
            print("  [SKIPPED] No expense_id from TEST 1")
            return
        update_payload = {
            "description": "Updated grocery bill",
            "amount": "3000.00",
            "category": "Shopping",
        }
        res = client.put(f"/api/v1/expenses/{expense_id}", json=update_payload, headers=headers_a)
        print(f"  Status: {res.status_code}")
        data = res.json()
        print(f"  Response: {data}")

        try:
            assert res.status_code == 200, f"Expected 200, got {res.status_code}"
            assert data["description"] == "Updated grocery bill"
            assert data["amount"] == "3000.00"
            assert data["category"] == "Shopping"
            assert data["date"] == "2026-10-01"  # unchanged
            print("  [PASSED] Expense updated successfully (partial update)")
            passed += 1
        except AssertionError as e:
            print(f"  [FAILED] {e}")
            failed += 1

    test_update_expense()

    # ==================================================
    # TEST 6: Transaction Synchronization on Update
    # ==================================================
    def test_transaction_sync_update():
        global passed, failed
        print("\n--- TEST 6: Transaction Sync on Update ---")
        db = SessionLocal()
        txns = (
            db.query(Transaction)
            .filter(
                Transaction.userId == user_a["user"]["id"],
                Transaction.type == "expense",
                Transaction.description == "Updated grocery bill",
            )
            .all()
        )
        db.close()
        print(f"  Found {len(txns)} matching transaction(s)")

        try:
            assert len(txns) == 1, f"Expected 1 transaction, found {len(txns)}"
            assert str(txns[0].amount) == "3000.00", f"Transaction amount not updated: {txns[0].amount}"
            assert txns[0].category == "Shopping"
            assert txns[0].description == "Updated grocery bill"
            print("  [PASSED] Transaction updated in sync with expense")
            passed += 1
        except AssertionError as e:
            print(f"  [FAILED] {e}")
            failed += 1

    test_transaction_sync_update()

    # ==================================================
    # TEST 7: Unauthorized Access (No Token)
    # ==================================================
    def test_unauthorized_access():
        global passed, failed
        print("\n--- TEST 7: Unauthorized Access (No Token) ---")
        endpoints = [
            ("POST", "/api/v1/expenses"),
            ("GET", "/api/v1/expenses"),
            ("GET", "/api/v1/expenses/fake_id"),
            ("PUT", "/api/v1/expenses/fake_id"),
            ("DELETE", "/api/v1/expenses/fake_id"),
        ]
        all_pass = True
        for method, url in endpoints:
            if method == "POST":
                res = client.post(url, json={
                    "description": "test", "amount": "100.00",
                    "category": "Food", "date": "2026-01-01",
                })
            elif method == "PUT":
                res = client.put(url, json={"description": "test"})
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

    # ==================================================
    # TEST 8: Cross-User Access (User B cannot access User A's expense)
    # ==================================================
    def test_cross_user_access():
        global passed, failed
        print("\n--- TEST 8: Cross-User Access Isolation ---")
        if not expense_id:
            print("  [SKIPPED] No expense_id from TEST 1")
            return

        # User B tries to GET User A's expense
        res_get = client.get(f"/api/v1/expenses/{expense_id}", headers=headers_b)
        # User B tries to UPDATE User A's expense
        res_put = client.put(
            f"/api/v1/expenses/{expense_id}",
            json={"description": "Hacked"},
            headers=headers_b,
        )
        # User B tries to DELETE User A's expense
        res_del = client.delete(f"/api/v1/expenses/{expense_id}", headers=headers_b)

        print(f"  GET by User B: {res_get.status_code}")
        print(f"  PUT by User B: {res_put.status_code}")
        print(f"  DELETE by User B: {res_del.status_code}")

        # User B lists their own expenses -- should be empty
        res_list = client.get("/api/v1/expenses", headers=headers_b)

        try:
            assert res_get.status_code == 404, f"GET should be 404, got {res_get.status_code}"
            assert res_put.status_code == 404, f"PUT should be 404, got {res_put.status_code}"
            assert res_del.status_code == 404, f"DELETE should be 404, got {res_del.status_code}"
            assert res_list.status_code == 200
            assert len(res_list.json()) == 0, f"User B should have 0 expenses, got {len(res_list.json())}"
            print("  [PASSED] Cross-user access correctly blocked (404 + empty list)")
            passed += 1
        except AssertionError as e:
            print(f"  [FAILED] {e}")
            failed += 1

    test_cross_user_access()

    # ==================================================
    # TEST 9: Invalid / Negative / Zero Amount
    # ==================================================
    def test_invalid_amount():
        global passed, failed
        print("\n--- TEST 9: Invalid / Negative / Zero Amount ---")
        invalid_payloads = [
            ({"description": "Bad", "amount": "-500.00", "category": "Food", "date": "2026-01-01"}, "negative"),
            ({"description": "Bad", "amount": "0", "category": "Food", "date": "2026-01-01"}, "zero"),
            ({"description": "Bad", "amount": "not_a_number", "category": "Food", "date": "2026-01-01"}, "non-numeric"),
        ]
        all_rejected = True
        for payload, label in invalid_payloads:
            res = client.post("/api/v1/expenses", json=payload, headers=headers_a)
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

    # ==================================================
    # TEST 10: Invalid Category
    # ==================================================
    def test_invalid_category():
        global passed, failed
        print("\n--- TEST 10: Invalid Category ---")
        invalid_categories = ["Gambling", "food", "FOOD", "InvalidCat", ""]
        all_rejected = True
        for cat in invalid_categories:
            payload = {
                "description": "Test",
                "amount": "100.00",
                "category": cat,
                "date": "2026-01-01",
            }
            res = client.post("/api/v1/expenses", json=payload, headers=headers_a)
            if res.status_code != 422:
                print(f"  [FAILED] category='{cat}' returned {res.status_code}, expected 422")
                all_rejected = False
            else:
                print(f"  category='{cat}' -> 422 OK")

        try:
            assert all_rejected, "Not all invalid categories were rejected"
            print("  [PASSED] All invalid categories rejected with 422")
            passed += 1
        except AssertionError as e:
            print(f"  [FAILED] {e}")
            failed += 1

    test_invalid_category()

    # ==================================================
    # TEST 11: Duplicate Transaction Prevention
    # ==================================================
    def test_no_duplicate_transactions():
        global passed, failed
        print("\n--- TEST 11: Duplicate Transaction Prevention ---")
        db = SessionLocal()
        user_id_a = user_a["user"]["id"]

        # Count total expense transactions for user A
        total_expense_txns = (
            db.query(Transaction)
            .filter(
                Transaction.userId == user_id_a,
                Transaction.type == "expense",
            )
            .count()
        )
        total_expenses = (
            db.query(Expense)
            .filter(Expense.userId == user_id_a)
            .count()
        )
        db.close()

        print(f"  Expense records: {total_expenses}")
        print(f"  Expense transactions: {total_expense_txns}")

        try:
            assert total_expense_txns == total_expenses, (
                f"Transaction count ({total_expense_txns}) != Expense count ({total_expenses})"
            )
            print("  [PASSED] No duplicate transactions -- counts match perfectly")
            passed += 1
        except AssertionError as e:
            print(f"  [FAILED] {e}")
            failed += 1

    test_no_duplicate_transactions()

    # ==================================================
    # TEST 12: Delete Expense + Transaction Sync
    # ==================================================
    def test_delete_expense():
        global passed, failed
        print("\n--- TEST 12: Delete Expense (DELETE /api/v1/expenses/{id}) ---")
        if not expense_id:
            print("  [SKIPPED] No expense_id from TEST 1")
            return

        res = client.delete(f"/api/v1/expenses/{expense_id}", headers=headers_a)
        print(f"  Status: {res.status_code}")
        data = res.json()
        print(f"  Response: {data}")

        try:
            assert res.status_code == 200, f"Expected 200, got {res.status_code}"
            assert data["id"] == expense_id
            assert "deleted" in data["message"].lower()
            print("  [PASSED] Expense deleted successfully")
            passed += 1
        except AssertionError as e:
            print(f"  [FAILED] {e}")
            failed += 1

        # Verify expense is gone
        res_get = client.get(f"/api/v1/expenses/{expense_id}", headers=headers_a)
        try:
            assert res_get.status_code == 404, f"Deleted expense still accessible: {res_get.status_code}"
            print("  [PASSED] Deleted expense returns 404")
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
                Transaction.type == "expense",
                Transaction.description == "Updated grocery bill",
            )
            .first()
        )
        db.close()

        try:
            assert txn is None, "Transaction for deleted expense still exists!"
            print("  [PASSED] Corresponding transaction also deleted")
            passed += 1
        except AssertionError as e:
            print(f"  [FAILED] {e}")
            failed += 1

    test_delete_expense()

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
    print(f"EXPENSE API TEST RESULTS: {passed}/{total} PASSED")
    if failed == 0:
        print("ALL TESTS PASSED!")
    else:
        print(f"{failed} TEST(S) FAILED")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
