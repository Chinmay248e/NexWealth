"""
Documents API Comprehensive Test Suite (Person 2)
==================================================
Tests for Document Vault endpoints, file uploads, type filtering,
authentication enforcement, cross-user isolation, and validation.

Run: python test_documents.py
"""
import sys
import os
import io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models import User, Document

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
USER_A_EMAIL = "doc.tester.a@nexwealth.in"
USER_B_EMAIL = "doc.tester.b@nexwealth.in"
PASSWORD = "TestPassword@123"

def run_tests():
    print("=" * 60)
    print("DOCUMENTS API — COMPREHENSIVE TEST SUITE (PERSON 2)")
    print("=" * 60)

    # Clean up any leftover users from previous test runs
    cleanup_user(USER_A_EMAIL)
    cleanup_user(USER_B_EMAIL)

    user_a = register_and_login(USER_A_EMAIL, "Doc User A", PASSWORD)
    user_b = register_and_login(USER_B_EMAIL, "Doc User B", PASSWORD)
    headers_a = user_a["headers"]
    headers_b = user_b["headers"]

    passed_tests = 0
    total_tests = 11

    # ──────────────────────────────────────────────────
    # TEST 1: Create Document Metadata (POST /api/v1/documents)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 1: Create Document Metadata (POST /api/v1/documents) ---")
    payload_1 = {
        "fileName": "tax_return_ay26_27.pdf",
        "documentType": "Tax Return",
        "status": "uploaded",
    }
    res = client.post("/api/v1/documents", json=payload_1, headers=headers_a)
    assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"
    doc_1 = res.json()
    assert doc_1["id"].startswith("doc_"), f"Invalid ID prefix: {doc_1['id']}"
    assert doc_1["userId"] == user_a["user"]["id"]
    assert doc_1["fileName"] == "tax_return_ay26_27.pdf"
    assert doc_1["documentType"] == "Tax Return"
    assert doc_1["status"] == "uploaded"
    assert "uploadedAt" in doc_1
    assert "createdAt" in doc_1
    print("  [PASSED] Document metadata created successfully with all contract fields")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 2: Upload File (POST /api/v1/documents/upload)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 2: Upload Document File (POST /api/v1/documents/upload) ---")
    file_bytes = b"%PDF-1.4 Mock PDF Content For Health Insurance Policy 2026"
    files = {
        "file": ("health_policy_2026.pdf", io.BytesIO(file_bytes), "application/pdf")
    }
    data = {"documentType": "Insurance"}
    res_upload = client.post(
        "/api/v1/documents/upload",
        files=files,
        data=data,
        headers=headers_a,
    )
    assert res_upload.status_code == 201, f"Expected 201, got {res_upload.status_code}: {res_upload.text}"
    doc_2 = res_upload.json()
    assert doc_2["id"].startswith("doc_")
    assert doc_2["fileName"] == "health_policy_2026.pdf"
    assert doc_2["documentType"] == "Insurance"
    print("  [PASSED] Physical document file uploaded and metadata registered")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 3: List Documents (GET /api/v1/documents)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 3: List Documents (GET /api/v1/documents) ---")
    res = client.get("/api/v1/documents", headers=headers_a)
    assert res.status_code == 200
    docs_list = res.json()
    assert len(docs_list) == 2
    print("  [PASSED] Listed all user documents")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 4: Filter Documents by Type (GET /api/v1/documents?documentType=...)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 4: Filter Documents by Category ---")
    res_filter = client.get("/api/v1/documents?documentType=Insurance", headers=headers_a)
    assert res_filter.status_code == 200
    filtered_list = res_filter.json()
    assert len(filtered_list) == 1
    assert filtered_list[0]["id"] == doc_2["id"]
    print("  [PASSED] Filter by documentType returned expected single record")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 5: Get Single Document (GET /api/v1/documents/{id})
    # ──────────────────────────────────────────────────
    print("\n--- TEST 5: Get Single Document (GET /api/v1/documents/{id}) ---")
    res_single = client.get(f"/api/v1/documents/{doc_1['id']}", headers=headers_a)
    assert res_single.status_code == 200
    assert res_single.json()["id"] == doc_1["id"]
    print("  [PASSED] Retrieved single document by ID")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 6: Update Document (PUT /api/v1/documents/{id})
    # ──────────────────────────────────────────────────
    print("\n--- TEST 6: Update Document (PUT /api/v1/documents/{id}) ---")
    res_update = client.put(
        f"/api/v1/documents/{doc_1['id']}",
        json={"status": "verified", "documentType": "Income Tax"},
        headers=headers_a,
    )
    assert res_update.status_code == 200
    updated_doc = res_update.json()
    assert updated_doc["status"] == "verified"
    assert updated_doc["documentType"] == "Income Tax"
    print("  [PASSED] Document status updated to 'verified'")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 7: Unauthorized Access (No Token)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 7: Unauthorized Access (401 Rejection) ---")
    assert client.post("/api/v1/documents", json=payload_1).status_code == 401
    assert client.get("/api/v1/documents").status_code == 401
    assert client.get(f"/api/v1/documents/{doc_1['id']}").status_code == 401
    assert client.put(f"/api/v1/documents/{doc_1['id']}", json={"status": "pending"}).status_code == 401
    assert client.delete(f"/api/v1/documents/{doc_1['id']}").status_code == 401
    print("  [PASSED] Unauthenticated requests rejected with 401")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 8: Cross-User Access Isolation
    # ──────────────────────────────────────────────────
    print("\n--- TEST 8: Cross-User Access Isolation ---")
    res_b_list = client.get("/api/v1/documents", headers=headers_b)
    assert res_b_list.status_code == 200
    assert len(res_b_list.json()) == 0

    assert client.get(f"/api/v1/documents/{doc_1['id']}", headers=headers_b).status_code == 404
    assert client.put(f"/api/v1/documents/{doc_1['id']}", json={"status": "hacked"}, headers=headers_b).status_code == 404
    assert client.delete(f"/api/v1/documents/{doc_1['id']}", headers=headers_b).status_code == 404
    print("  [PASSED] Strict cross-user isolation enforced (404 on foreign documents)")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 9: Invalid File Type Rejection
    # ──────────────────────────────────────────────────
    print("\n--- TEST 9: Invalid File Type Rejection ---")
    bad_files = {
        "file": ("malicious_script.exe", io.BytesIO(b"MZ executable header"), "application/octet-stream")
    }
    res_bad = client.post(
        "/api/v1/documents/upload",
        files=bad_files,
        data={"documentType": "Other"},
        headers=headers_a,
    )
    assert res_bad.status_code == 400
    assert "unsupported file format" in res_bad.json()["detail"].lower()
    print("  [PASSED] Executable file upload rejected with 400 Bad Request")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 10: Validation for Blank Filename
    # ──────────────────────────────────────────────────
    print("\n--- TEST 10: Input Validation (Blank Name) ---")
    res_blank = client.post(
        "/api/v1/documents",
        json={"fileName": "   ", "documentType": "Tax"},
        headers=headers_a,
    )
    assert res_blank.status_code == 422
    print("  [PASSED] Blank filename rejected with 422")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 11: Delete Document (DELETE /api/v1/documents/{id})
    # ──────────────────────────────────────────────────
    print("\n--- TEST 11: Delete Document (DELETE /api/v1/documents/{id}) ---")
    del_res = client.delete(f"/api/v1/documents/{doc_1['id']}", headers=headers_a)
    assert del_res.status_code == 200
    assert del_res.json()["id"] == doc_1["id"]

    # Verify subsequent GET returns 404
    assert client.get(f"/api/v1/documents/{doc_1['id']}", headers=headers_a).status_code == 404
    print("  [PASSED] Document deleted and subsequent lookup returns 404")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # Cleanup
    # ──────────────────────────────────────────────────
    print("\n--- CLEANUP ---")
    cleanup_user(USER_A_EMAIL)
    cleanup_user(USER_B_EMAIL)
    print("  [OK] Test users cleaned up.")

    print("\n" + "=" * 60)
    print(f"DOCUMENTS API TEST RESULTS: {passed_tests}/{total_tests} PASSED")
    print("ALL TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
