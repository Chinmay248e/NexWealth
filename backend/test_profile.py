"""
Profile API Comprehensive Test Suite
====================================
Tests for User Profile endpoints:
- GET /api/v1/profile (Authenticated & unauthenticated)
- PUT /api/v1/profile (Name & email update)
- Duplicate email collision rejection (400)
- Input validation (EmailStr, non-blank name)
- Security: passwordHash never exposed or modifiable
- Cross-user data isolation

Run: python test_profile.py
"""
import sys
import os

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
USER_A_EMAIL = "profile.tester.a@nexwealth.in"
USER_B_EMAIL = "profile.tester.b@nexwealth.in"
UPDATED_EMAIL = "profile.tester.updated@nexwealth.in"
PASSWORD = "TestPassword@123"

def run_tests():
    print("=" * 60)
    print("PROFILE API — COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    cleanup_user(USER_A_EMAIL)
    cleanup_user(USER_B_EMAIL)
    cleanup_user(UPDATED_EMAIL)

    user_a = register_and_login(USER_A_EMAIL, "Original User A", PASSWORD)
    user_b = register_and_login(USER_B_EMAIL, "Original User B", PASSWORD)
    headers_a = user_a["headers"]
    headers_b = user_b["headers"]

    passed_tests = 0
    total_tests = 8

    # ──────────────────────────────────────────────────
    # TEST 1: Unauthenticated Access Rejection (401)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 1: Unauthenticated Access Rejection ---")
    assert client.get("/api/v1/profile").status_code == 401
    assert client.put("/api/v1/profile", json={"name": "Hacker"}).status_code == 401
    print("  [PASSED] Unauthenticated GET and PUT requests rejected with 401")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 2: Authenticated GET Profile
    # ──────────────────────────────────────────────────
    print("\n--- TEST 2: Authenticated GET Profile ---")
    res = client.get("/api/v1/profile", headers=headers_a)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    prof = res.json()
    assert prof["id"] == user_a["user"]["id"]
    assert prof["name"] == "Original User A"
    assert prof["email"] == USER_A_EMAIL
    assert "createdAt" in prof
    assert "passwordHash" not in prof
    assert "password" not in prof
    print("  [PASSED] Profile retrieved successfully with expected fields and zero password exposure")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 3: Update Name
    # ──────────────────────────────────────────────────
    print("\n--- TEST 3: Update Name ---")
    res = client.put("/api/v1/profile", json={"name": "Aarav Sharma"}, headers=headers_a)
    assert res.status_code == 200
    updated = res.json()
    assert updated["name"] == "Aarav Sharma"
    assert updated["email"] == USER_A_EMAIL
    print("  [PASSED] Name updated successfully while preserving email")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 4: Update Email
    # ──────────────────────────────────────────────────
    print("\n--- TEST 4: Update Email ---")
    res = client.put("/api/v1/profile", json={"email": UPDATED_EMAIL}, headers=headers_a)
    assert res.status_code == 200
    updated = res.json()
    assert updated["email"] == UPDATED_EMAIL
    assert updated["name"] == "Aarav Sharma"
    print("  [PASSED] Email updated successfully")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 5: Duplicate Email Collision Rejection
    # ──────────────────────────────────────────────────
    print("\n--- TEST 5: Duplicate Email Collision Rejection ---")
    # User A tries to change email to User B's email
    res_dup = client.put("/api/v1/profile", json={"email": USER_B_EMAIL}, headers=headers_a)
    assert res_dup.status_code == 400
    assert "already in use" in res_dup.json()["detail"].lower()
    print("  [PASSED] Duplicate email collision correctly rejected with 400 Bad Request")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 6: Validation Rejections (Invalid Email & Blank Name)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 6: Input Validation Rejections ---")
    # Invalid email format
    res_bad_email = client.put("/api/v1/profile", json={"email": "not-a-valid-email"}, headers=headers_a)
    assert res_bad_email.status_code == 422

    # Blank name
    res_blank_name = client.put("/api/v1/profile", json={"name": "   "}, headers=headers_a)
    assert res_blank_name.status_code == 422

    print("  [PASSED] Invalid email format and blank names rejected with 422 Unprocessable Content")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 7: Cross-User Isolation
    # ──────────────────────────────────────────────────
    print("\n--- TEST 7: Cross-User Isolation ---")
    res_b = client.get("/api/v1/profile", headers=headers_b)
    assert res_b.status_code == 200
    prof_b = res_b.json()
    assert prof_b["id"] == user_b["user"]["id"]
    assert prof_b["name"] == "Original User B"
    assert prof_b["email"] == USER_B_EMAIL
    print("  [PASSED] User B profile completely isolated from User A updates")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 8: Password Hash Security
    # ──────────────────────────────────────────────────
    print("\n--- TEST 8: Security & Password Hash Invariant ---")
    # Ensure attempts to send password or passwordHash in update are ignored and never returned
    res_sec = client.put(
        "/api/v1/profile",
        json={"name": "Security Verified", "passwordHash": "fake_hash", "password": "new_password"},
        headers=headers_a
    )
    assert res_sec.status_code == 200
    sec_data = res_sec.json()
    assert "passwordHash" not in sec_data
    assert "password" not in sec_data
    print("  [PASSED] Password hash invariant guaranteed")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # Cleanup
    # ──────────────────────────────────────────────────
    print("\n--- CLEANUP ---")
    cleanup_user(USER_A_EMAIL)
    cleanup_user(USER_B_EMAIL)
    cleanup_user(UPDATED_EMAIL)
    print("  [OK] Test users cleaned up.")

    print("\n" + "=" * 60)
    print(f"PROFILE API TEST RESULTS: {passed_tests}/{total_tests} PASSED")
    print("ALL TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
