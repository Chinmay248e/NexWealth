import sys
import os
import unittest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.core.database import SessionLocal
from app.models import User, Income, Expense, Transaction

client = TestClient(app)

def run_tests():
    print("==================================================")
    print("PERSON 1 AUTHENTICATION & SECURITY TEST SUITE")
    print("==================================================")

    test_email = "test.person1@nexwealth.in"
    test_password = "SecurePassword@123"
    test_name = "Aarav Sharma"

    # Clean up test user if exists from prior runs
    db = SessionLocal()
    existing = db.query(User).filter(User.email == test_email).first()
    if existing:
        db.delete(existing)
        db.commit()
    db.close()

    # ----------------------------------------------------
    # TEST 1: Successful Registration
    # ----------------------------------------------------
    print("\n--- TEST 1: Registration (POST /api/v1/auth/register) ---")
    reg_payload = {
        "name": test_name,
        "email": test_email,
        "password": test_password
    }
    res_reg = client.post("/api/v1/auth/register", json=reg_payload)
    print(f"Status Code: {res_reg.status_code}")
    print(f"Response: {res_reg.json()}")

    assert res_reg.status_code == 201, f"Expected 201 Created, got {res_reg.status_code}"
    reg_data = res_reg.json()
    assert "id" in reg_data, "Missing user ID in response"
    assert reg_data["email"] == test_email, "Email mismatch"
    assert reg_data["name"] == test_name, "Name mismatch"
    assert "password" not in reg_data, "SECURITY FLAW: Plaintext password leaked in response!"
    assert "passwordHash" not in reg_data, "SECURITY FLAW: passwordHash leaked in response!"
    user_id = reg_data["id"]
    print(f"[SUCCESS] User registered with ID: {user_id}. No password leaked.")

    # Verify newly registered user has zero financial records
    db = SessionLocal()
    user_incomes = db.query(Income).filter(Income.userId == user_id).all()
    user_expenses = db.query(Expense).filter(Expense.userId == user_id).all()
    user_txns = db.query(Transaction).filter(Transaction.userId == user_id).all()
    assert len(user_incomes) == 0, "New user has unexpected income records"
    assert len(user_expenses) == 0, "New user has unexpected expense records"
    assert len(user_txns) == 0, "New user has unexpected transaction records"
    db.close()
    print("[SUCCESS] Verified newly registered user has 0 financial records.")

    # ----------------------------------------------------
    # TEST 2: Duplicate Email Rejection
    # ----------------------------------------------------
    print("\n--- TEST 2: Duplicate Email Rejection ---")
    res_dup = client.post("/api/v1/auth/register", json=reg_payload)
    print(f"Status Code: {res_dup.status_code}")
    print(f"Response: {res_dup.json()}")
    assert res_dup.status_code == 400, f"Expected 400 Bad Request, got {res_dup.status_code}"
    assert "already exists" in res_dup.json()["detail"].lower()
    print("[SUCCESS] Duplicate email rejected with 400 Bad Request.")

    # ----------------------------------------------------
    # TEST 3: Successful Login
    # ----------------------------------------------------
    print("\n--- TEST 3: Login (POST /api/v1/auth/login) ---")
    login_payload = {
        "email": test_email,
        "password": test_password
    }
    res_login = client.post("/api/v1/auth/login", json=login_payload)
    print(f"Status Code: {res_login.status_code}")
    print(f"Response (masked token): {res_login.json().get('token_type', '')} token returned")
    assert res_login.status_code == 200, f"Expected 200 OK, got {res_login.status_code}"
    login_data = res_login.json()
    token = login_data.get("access_token") or login_data.get("accessToken")
    assert token, "Missing access_token in login response"
    assert login_data["user"]["id"] == user_id, "User ID mismatch in login user payload"
    assert "passwordHash" not in login_data["user"], "SECURITY FLAW: passwordHash in login response!"
    print(f"[SUCCESS] Login successful. JWT token received for userId: {user_id}.")

    # ----------------------------------------------------
    # TEST 4: Wrong Password Rejection
    # ----------------------------------------------------
    print("\n--- TEST 4: Wrong Password Rejection ---")
    bad_login_payload = {
        "email": test_email,
        "password": "IncorrectPassword999"
    }
    res_bad_login = client.post("/api/v1/auth/login", json=bad_login_payload)
    print(f"Status Code: {res_bad_login.status_code}")
    print(f"Response: {res_bad_login.json()}")
    assert res_bad_login.status_code == 401, f"Expected 401 Unauthorized, got {res_bad_login.status_code}"
    print("[SUCCESS] Wrong password rejected with 401 Unauthorized.")

    # ----------------------------------------------------
    # TEST 5: Protected Endpoint without Token
    # ----------------------------------------------------
    print("\n--- TEST 5: Protected Endpoint without Token ---")
    res_no_token = client.get("/api/v1/auth/me")
    print(f"Status Code: {res_no_token.status_code}")
    print(f"Response: {res_no_token.json()}")
    assert res_no_token.status_code == 401, f"Expected 401 Unauthorized, got {res_no_token.status_code}"
    print("[SUCCESS] Missing token rejected with 401 Unauthorized.")

    # ----------------------------------------------------
    # TEST 6: Protected Endpoint with Invalid Token
    # ----------------------------------------------------
    print("\n--- TEST 6: Protected Endpoint with Invalid Token ---")
    headers_invalid = {"Authorization": "Bearer invalid.jwt.signature123"}
    res_inv = client.get("/api/v1/auth/me", headers=headers_invalid)
    print(f"Status Code: {res_inv.status_code}")
    print(f"Response: {res_inv.json()}")
    assert res_inv.status_code == 401, f"Expected 401 Unauthorized, got {res_inv.status_code}"
    print("[SUCCESS] Invalid token rejected with 401 Unauthorized.")

    # ----------------------------------------------------
    # TEST 7: Protected Endpoint with Valid Token
    # ----------------------------------------------------
    print("\n--- TEST 7: Protected Endpoint with Valid Token ---")
    headers_valid = {"Authorization": f"Bearer {token}"}
    res_valid = client.get("/api/v1/auth/me", headers=headers_valid)
    print(f"Status Code: {res_valid.status_code}")
    print(f"Response: {res_valid.json()}")
    assert res_valid.status_code == 200, f"Expected 200 OK, got {res_valid.status_code}"
    me_data = res_valid.json()
    assert me_data["id"] == user_id, "User ID mismatch on protected /me route"
    assert me_data["email"] == test_email, "Email mismatch on /me route"
    assert "passwordHash" not in me_data, "SECURITY FLAW: passwordHash on /me route"
    print(f"[SUCCESS] Valid token successfully authenticated user '{me_data['name']}' ({me_data['id']}).")

    # Clean up test user
    db = SessionLocal()
    u = db.query(User).filter(User.id == user_id).first()
    if u:
        db.delete(u)
        db.commit()
    db.close()
    print("[SUCCESS] Cleaned up temporary test user.")

    print("\n==================================================")
    print("ALL 7 AUTHENTICATION TESTS PASSED PERFECTLY!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
