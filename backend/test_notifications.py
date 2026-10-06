"""
Notifications API Comprehensive Test Suite
==========================================
Tests for Notifications endpoints:
- Unauthenticated access rejection (401)
- Empty user list (zero notifications)
- Correct listing and newest-first createdAt ordering
- unreadOnly filter parameter
- Get single notification
- Mark one notification as read
- Mark all notifications as read
- Delete notification
- Cross-user data isolation (404)

Run: python test_notifications.py
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models import User
from app.services.notification_service import create_notification

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
USER_A_EMAIL = "notif.tester.a@nexwealth.in"
USER_B_EMAIL = "notif.tester.b@nexwealth.in"
PASSWORD = "TestPassword@123"

def run_tests():
    print("=" * 60)
    print("NOTIFICATIONS API — COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    cleanup_user(USER_A_EMAIL)
    cleanup_user(USER_B_EMAIL)

    user_a = register_and_login(USER_A_EMAIL, "Notif User A", PASSWORD)
    user_b = register_and_login(USER_B_EMAIL, "Notif User B", PASSWORD)
    headers_a = user_a["headers"]
    headers_b = user_b["headers"]
    user_a_id = user_a["user"]["id"]
    user_b_id = user_b["user"]["id"]

    passed_tests = 0
    total_tests = 10

    # ──────────────────────────────────────────────────
    # TEST 1: Unauthenticated Access Rejection (401)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 1: Unauthenticated Access Rejection ---")
    assert client.get("/api/v1/notifications").status_code == 401
    assert client.get("/api/v1/notifications/ntf_dummy").status_code == 401
    assert client.put("/api/v1/notifications/ntf_dummy/read").status_code == 401
    assert client.put("/api/v1/notifications/read-all").status_code == 401
    assert client.delete("/api/v1/notifications/ntf_dummy").status_code == 401
    print("  [PASSED] All 5 endpoints reject unauthenticated access with 401")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 2: Empty User Notifications List
    # ──────────────────────────────────────────────────
    print("\n--- TEST 2: Empty User Notifications List ---")
    res_empty = client.get("/api/v1/notifications", headers=headers_a)
    assert res_empty.status_code == 200
    assert res_empty.json() == []
    print("  [PASSED] Fresh user has empty notifications list")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # Seed Notifications for Testing
    # ──────────────────────────────────────────────────
    db = SessionLocal()
    n1 = create_notification(
        db, user_a_id, type="budget_alert", title="Food Budget Notice", message="You reached 80% of budget.", read=False
    )
    time.sleep(0.01)
    n2 = create_notification(
        db, user_a_id, type="goal_reached", title="Savings Goal Milestone", message="Crossed ₹5,00,000 milestone.", read=False
    )
    time.sleep(0.01)
    n3 = create_notification(
        db, user_a_id, type="system", title="System Maintenance", message="Scheduled upgrade completed.", read=True
    )
    n1_id = n1.id
    n2_id = n2.id
    n3_id = n3.id
    db.close()

    # ──────────────────────────────────────────────────
    # TEST 3: Authenticated List & Newest-First Ordering
    # ──────────────────────────────────────────────────
    print("\n--- TEST 3: List & Ordering (Newest First) ---")
    res = client.get("/api/v1/notifications", headers=headers_a)
    assert res.status_code == 200
    list_a = res.json()
    assert len(list_a) == 3
    # n3 was created last, so it should be first in list
    assert list_a[0]["id"] == n3_id
    assert list_a[1]["id"] == n2_id
    assert list_a[2]["id"] == n1_id
    print("  [PASSED] Notifications returned in descending order of createdAt")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 4: unreadOnly Filter Parameter
    # ──────────────────────────────────────────────────
    print("\n--- TEST 4: unreadOnly Filtering ---")
    res_unread = client.get("/api/v1/notifications?unreadOnly=true", headers=headers_a)
    assert res_unread.status_code == 200
    unread_list = res_unread.json()
    assert len(unread_list) == 2
    assert all(item["read"] is False for item in unread_list)
    assert n3_id not in [item["id"] for item in unread_list]
    print("  [PASSED] unreadOnly filter returned only unread notifications")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 5: Get Single Notification
    # ──────────────────────────────────────────────────
    print("\n--- TEST 5: Get Single Notification ---")
    res_single = client.get(f"/api/v1/notifications/{n1_id}", headers=headers_a)
    assert res_single.status_code == 200
    item = res_single.json()
    assert item["id"] == n1_id
    assert item["userId"] == user_a_id
    assert item["type"] == "budget_alert"
    assert item["title"] == "Food Budget Notice"
    assert item["message"] == "You reached 80% of budget."
    assert item["read"] is False
    assert "createdAt" in item
    print("  [PASSED] Single notification retrieved with all contract fields")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 6: Mark Single Notification as Read
    # ──────────────────────────────────────────────────
    print("\n--- TEST 6: Mark Single Notification as Read ---")
    res_read = client.put(f"/api/v1/notifications/{n1_id}/read", headers=headers_a)
    assert res_read.status_code == 200
    assert res_read.json()["read"] is True

    # Check unread count is now 1 (only n2 is unread)
    res_unread_after = client.get("/api/v1/notifications?unreadOnly=true", headers=headers_a)
    assert len(res_unread_after.json()) == 1
    print("  [PASSED] Notification marked as read and reflected in unread list")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 7: Mark All Notifications as Read
    # ──────────────────────────────────────────────────
    print("\n--- TEST 7: Mark All Notifications as Read ---")
    res_all = client.put("/api/v1/notifications/read-all", headers=headers_a)
    assert res_all.status_code == 200
    assert res_all.json()["count"] == 1  # only n2 was unread

    res_unread_none = client.get("/api/v1/notifications?unreadOnly=true", headers=headers_a)
    assert len(res_unread_none.json()) == 0
    print("  [PASSED] All notifications marked as read successfully")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 8: Delete Notification
    # ──────────────────────────────────────────────────
    print("\n--- TEST 8: Delete Notification ---")
    res_del = client.delete(f"/api/v1/notifications/{n1_id}", headers=headers_a)
    assert res_del.status_code == 200
    assert res_del.json()["id"] == n1_id

    # Subsequent GET returns 404
    assert client.get(f"/api/v1/notifications/{n1_id}", headers=headers_a).status_code == 404
    # Subsequent DELETE returns 404
    assert client.delete(f"/api/v1/notifications/{n1_id}", headers=headers_a).status_code == 404

    # List now has 2
    res_after_del = client.get("/api/v1/notifications", headers=headers_a)
    assert len(res_after_del.json()) == 2
    print("  [PASSED] Notification deleted and subsequent lookups return 404")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 9: Cross-User Isolation
    # ──────────────────────────────────────────────────
    print("\n--- TEST 9: Cross-User Isolation ---")
    # User B should see 0 notifications
    res_b_list = client.get("/api/v1/notifications", headers=headers_b)
    assert res_b_list.status_code == 200
    assert res_b_list.json() == []

    # User B cannot access User A's notification n2
    assert client.get(f"/api/v1/notifications/{n2_id}", headers=headers_b).status_code == 404
    assert client.put(f"/api/v1/notifications/{n2_id}/read", headers=headers_b).status_code == 404
    assert client.delete(f"/api/v1/notifications/{n2_id}", headers=headers_b).status_code == 404
    print("  [PASSED] Strict cross-user isolation enforced across all notification operations")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 10: Missing Notification 404
    # ──────────────────────────────────────────────────
    print("\n--- TEST 10: Non-Existent Notification 404 ---")
    assert client.get("/api/v1/notifications/ntf_nonexistent", headers=headers_a).status_code == 404
    assert client.put("/api/v1/notifications/ntf_nonexistent/read", headers=headers_a).status_code == 404
    assert client.delete("/api/v1/notifications/ntf_nonexistent", headers=headers_a).status_code == 404
    print("  [PASSED] Non-existent notifications safely return 404")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # Cleanup
    # ──────────────────────────────────────────────────
    print("\n--- CLEANUP ---")
    cleanup_user(USER_A_EMAIL)
    cleanup_user(USER_B_EMAIL)
    print("  [OK] Test users cleaned up.")

    print("\n" + "=" * 60)
    print(f"NOTIFICATIONS API TEST RESULTS: {passed_tests}/{total_tests} PASSED")
    print("ALL TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
