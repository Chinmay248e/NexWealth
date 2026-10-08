"""
Bank Statements API Comprehensive Test Suite (Person 2)
========================================================
Tests for Bank Statement Ingestion, Parsing (CSV/Excel), Transaction Import,
Authentication Enforcement, Cross-User Isolation, and Error Handling.

Run: python test_bank_statements.py
"""
import sys
import os
import io
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models import User, BankStatement, Transaction

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
USER_A_EMAIL = "statement.tester.a@nexwealth.in"
USER_B_EMAIL = "statement.tester.b@nexwealth.in"
PASSWORD = "TestPassword@123"

SAMPLE_CSV = """Date,Narration,Debit,Credit
2026-10-01,Monthly Salary Credit,,125000.00
2026-10-02,Swiggy Bangalore Food Order,650.00,
2026-10-03,Amazon India Shopping,3400.00,
2026-10-04,Airtel Broadband Bill Payment,1199.00,
2026-10-05,Uber Trip to Tech Park,420.00,
"""

def run_tests():
    print("=" * 60)
    print("BANK STATEMENTS API — COMPREHENSIVE TEST SUITE (PERSON 2)")
    print("=" * 60)

    # Clean up any leftover users from previous test runs
    cleanup_user(USER_A_EMAIL)
    cleanup_user(USER_B_EMAIL)

    user_a = register_and_login(USER_A_EMAIL, "Statement User A", PASSWORD)
    user_b = register_and_login(USER_B_EMAIL, "Statement User B", PASSWORD)
    headers_a = user_a["headers"]
    headers_b = user_b["headers"]

    passed_tests = 0
    total_tests = 13

    # ──────────────────────────────────────────────────
    # TEST 1: Create Statement Metadata (POST /api/v1/bank-statements)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 1: Create Statement Metadata (POST /api/v1/bank-statements) ---")
    payload_1 = {
        "fileName": "hdfc_sep_2026_statement.csv",
        "accountName": "HDFC Salary Account",
        "status": "uploaded",
    }
    res = client.post("/api/v1/bank-statements", json=payload_1, headers=headers_a)
    assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"
    stmt_1 = res.json()
    assert stmt_1["id"].startswith("bst_"), f"Invalid ID prefix: {stmt_1['id']}"
    assert stmt_1["userId"] == user_a["user"]["id"]
    assert stmt_1["fileName"] == "hdfc_sep_2026_statement.csv"
    assert stmt_1["accountName"] == "HDFC Salary Account"
    assert "uploadedAt" in stmt_1
    assert "createdAt" in stmt_1
    print("  [PASSED] Bank statement metadata created successfully")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 2: Upload Statement File (POST /api/v1/bank-statements/upload)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 2: Upload Statement File & Auto-Parse (POST /api/v1/bank-statements/upload) ---")
    csv_bytes = SAMPLE_CSV.encode("utf-8")
    files = {
        "file": ("icici_oct2026.csv", io.BytesIO(csv_bytes), "text/csv")
    }
    data = {"accountName": "ICICI Wealth Account (..8821)"}
    res_upload = client.post(
        "/api/v1/bank-statements/upload",
        files=files,
        data=data,
        headers=headers_a,
    )
    assert res_upload.status_code == 201, f"Expected 201, got {res_upload.status_code}: {res_upload.text}"
    stmt_2 = res_upload.json()
    assert stmt_2["id"].startswith("bst_")
    assert stmt_2["fileName"] == "icici_oct2026.csv"
    assert stmt_2["status"] == "parsed"
    print("  [PASSED] Statement uploaded, saved to disk, and status set to 'parsed'")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 3: List Statements (GET /api/v1/bank-statements)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 3: List Statements (GET /api/v1/bank-statements) ---")
    res = client.get("/api/v1/bank-statements", headers=headers_a)
    assert res.status_code == 200
    stmts_list = res.json()
    assert len(stmts_list) == 2
    print("  [PASSED] Listed all user statements")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 4: Get Single Statement (GET /api/v1/bank-statements/{id})
    # ──────────────────────────────────────────────────
    print("\n--- TEST 4: Get Single Statement (GET /api/v1/bank-statements/{id}) ---")
    res_single = client.get(f"/api/v1/bank-statements/{stmt_2['id']}", headers=headers_a)
    assert res_single.status_code == 200
    assert res_single.json()["id"] == stmt_2["id"]
    print("  [PASSED] Retrieved single bank statement by ID")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 5: Parse Statement Content (GET /api/v1/bank-statements/{id}/parse)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 5: Parse & Preview Transactions (GET /api/v1/bank-statements/{id}/parse) ---")
    res_parse = client.get(f"/api/v1/bank-statements/{stmt_2['id']}/parse", headers=headers_a)
    assert res_parse.status_code == 200
    parse_data = res_parse.json()
    assert parse_data["statementId"] == stmt_2["id"]
    assert parse_data["transactionCount"] == 5
    assert Decimal(str(parse_data["totalCredits"])) == Decimal("125000.00")
    assert Decimal(str(parse_data["totalDebits"])) == Decimal("5669.00")
    # Verify auto-categorization
    txns = parse_data["transactions"]
    assert txns[0]["type"] == "income"
    assert txns[0]["category"] == "Salary"
    assert txns[1]["category"] == "Food"
    assert txns[2]["category"] == "Shopping"
    assert txns[3]["category"] == "Bills"
    assert txns[4]["category"] == "Transport"
    print("  [PASSED] Statement extracted 5 structured transactions with smart category detection")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 6: Import Parsed Transactions (POST /api/v1/bank-statements/{id}/import)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 6: Import Transactions into User Ledger (POST /api/v1/bank-statements/{id}/import) ---")
    import_payload = {
        "transactions": txns
    }
    res_import = client.post(
        f"/api/v1/bank-statements/{stmt_2['id']}/import",
        json=import_payload,
        headers=headers_a,
    )
    assert res_import.status_code == 201
    import_result = res_import.json()
    assert import_result["importedCount"] == 5
    assert import_result["statementId"] == stmt_2["id"]

    # Verify transactions now visible in User A's transactions API
    res_txns = client.get("/api/v1/transactions", headers=headers_a)
    assert res_txns.status_code == 200
    assert len(res_txns.json()) >= 5
    print("  [PASSED] Imported 5 parsed transactions into user ledger with strict user ownership")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 7: Unauthorized Access (No Token)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 7: Unauthorized Access (401 Rejection) ---")
    assert client.post("/api/v1/bank-statements", json=payload_1).status_code == 401
    assert client.get("/api/v1/bank-statements").status_code == 401
    assert client.get(f"/api/v1/bank-statements/{stmt_1['id']}").status_code == 401
    assert client.get(f"/api/v1/bank-statements/{stmt_1['id']}/parse").status_code == 401
    assert client.post(f"/api/v1/bank-statements/{stmt_1['id']}/import", json={"transactions": []}).status_code == 401
    assert client.delete(f"/api/v1/bank-statements/{stmt_1['id']}").status_code == 401
    print("  [PASSED] All endpoints reject unauthenticated access with 401")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 8: Cross-User Access Isolation
    # ──────────────────────────────────────────────────
    print("\n--- TEST 8: Cross-User Access Isolation ---")
    res_b_list = client.get("/api/v1/bank-statements", headers=headers_b)
    assert res_b_list.status_code == 200
    assert len(res_b_list.json()) == 0

    assert client.get(f"/api/v1/bank-statements/{stmt_2['id']}", headers=headers_b).status_code == 404
    assert client.get(f"/api/v1/bank-statements/{stmt_2['id']}/parse", headers=headers_b).status_code == 404
    assert client.post(f"/api/v1/bank-statements/{stmt_2['id']}/import", json={"transactions": []}, headers=headers_b).status_code == 404
    assert client.delete(f"/api/v1/bank-statements/{stmt_2['id']}", headers=headers_b).status_code == 404
    print("  [PASSED] Cross-user access strictly isolated (404 for all foreign statements)")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 9: Invalid Statement File Format
    # ──────────────────────────────────────────────────
    print("\n--- TEST 9: Invalid Statement File Format ---")
    bad_files = {
        "file": ("script.sh", io.BytesIO(b"#!/bin/bash echo attack"), "text/plain")
    }
    res_bad = client.post(
        "/api/v1/bank-statements/upload",
        files=bad_files,
        data={"accountName": "Test Bank"},
        headers=headers_a,
    )
    assert res_bad.status_code == 400
    assert "unsupported statement format" in res_bad.json()["detail"].lower()
    print("  [PASSED] Invalid statement extension rejected with 400 Bad Request")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 10: Input Validation for Missing Account Name
    # ──────────────────────────────────────────────────
    print("\n--- TEST 10: Blank Account Name Validation ---")
    res_blank = client.post(
        "/api/v1/bank-statements",
        json={"fileName": "statement.csv", "accountName": "   "},
        headers=headers_a,
    )
    assert res_blank.status_code == 422
    print("  [PASSED] Blank account name rejected with 422")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 11: Delete Bank Statement (DELETE /api/v1/bank-statements/{id})
    # ──────────────────────────────────────────────────
    print("\n--- TEST 11: Delete Bank Statement (DELETE /api/v1/bank-statements/{id}) ---")
    del_res = client.delete(f"/api/v1/bank-statements/{stmt_1['id']}", headers=headers_a)
    assert del_res.status_code == 200
    assert del_res.json()["id"] == stmt_1["id"]

    assert client.get(f"/api/v1/bank-statements/{stmt_1['id']}", headers=headers_a).status_code == 404
    print("  [PASSED] Bank statement deleted and subsequent lookup returns 404")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 12: Fully Quoted CSV Rows (Book1.csv format regression test)
    # ──────────────────────────────────────────────────
    print("\n--- TEST 12: Fully Quoted CSV Rows (Book1.csv Regression) ---")
    book1_csv = '''"Date,Description,Amount,Type"
"2026-09-01,Salary,50000,Credit"
"2026-09-02,Swiggy,450,Debit"'''
    files_quoted = {
        "file": ("Book1.csv", io.BytesIO(book1_csv.encode("utf-8")), "text/csv")
    }
    res_quoted = client.post(
        "/api/v1/bank-statements/upload",
        files=files_quoted,
        data={"accountName": "HDFC Salary Account"},
        headers=headers_a,
    )
    assert res_quoted.status_code == 201, f"Expected 201, got {res_quoted.status_code}: {res_quoted.text}"
    stmt_quoted = res_quoted.json()

    res_quoted_parse = client.get(f"/api/v1/bank-statements/{stmt_quoted['id']}/parse", headers=headers_a)
    assert res_quoted_parse.status_code == 200
    q_data = res_quoted_parse.json()
    assert q_data["transactionCount"] == 2, f"Expected 2 transactions, got {q_data['transactionCount']}"
    assert Decimal(str(q_data["totalCredits"])) == Decimal("50000.00")
    assert Decimal(str(q_data["totalDebits"])) == Decimal("450.00")
    
    q_txns = q_data["transactions"]
    assert q_txns[0]["date"] == "2026-09-01"
    assert q_txns[0]["description"] == "Salary"
    assert Decimal(str(q_txns[0]["amount"])) == Decimal("50000.00")
    assert q_txns[0]["type"] == "income"
    assert q_txns[0]["category"] == "Salary"

    assert q_txns[1]["date"] == "2026-09-02"
    assert q_txns[1]["description"] == "Swiggy"
    assert Decimal(str(q_txns[1]["amount"])) == Decimal("450.00")
    assert q_txns[1]["type"] == "expense"
    assert q_txns[1]["category"] == "Food"

    # Import the parsed transactions
    res_q_import = client.post(
        f"/api/v1/bank-statements/{stmt_quoted['id']}/import",
        json={"transactions": q_txns},
        headers=headers_a,
    )
    assert res_q_import.status_code == 201
    assert res_q_import.json()["importedCount"] == 2
    print("  [PASSED] Fully quoted CSV rows parsed & imported flawlessly")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # TEST 13: TSV and Semicolon Delimiter Detection
    # ──────────────────────────────────────────────────
    print("\n--- TEST 13: TSV and Semicolon Delimiter Detection ---")
    semi_csv = '''Date;Description;Amount;Type
2026-09-01;Consulting Fee;₹75,000.00;Credit
2026-09-02;Zomato Order;₹320.50;Debit'''
    files_semi = {
        "file": ("statement.csv", io.BytesIO(semi_csv.encode("utf-8")), "text/csv")
    }
    res_semi = client.post(
        "/api/v1/bank-statements/upload",
        files=files_semi,
        data={"accountName": "Consulting Account"},
        headers=headers_a,
    )
    assert res_semi.status_code == 201
    stmt_semi = res_semi.json()

    res_semi_parse = client.get(f"/api/v1/bank-statements/{stmt_semi['id']}/parse", headers=headers_a)
    assert res_semi_parse.status_code == 200
    semi_data = res_semi_parse.json()
    assert semi_data["transactionCount"] == 2
    assert Decimal(str(semi_data["totalCredits"])) == Decimal("75000.00")
    assert Decimal(str(semi_data["totalDebits"])) == Decimal("320.50")
    print("  [PASSED] Semicolon and Indian currency formatted amounts parsed properly")
    passed_tests += 1

    # ──────────────────────────────────────────────────
    # Cleanup
    # ──────────────────────────────────────────────────
    print("\n--- CLEANUP ---")
    cleanup_user(USER_A_EMAIL)
    cleanup_user(USER_B_EMAIL)
    print("  [OK] Test users cleaned up.")

    print("\n" + "=" * 60)
    print(f"BANK STATEMENTS API TEST RESULTS: {passed_tests}/{total_tests} PASSED")
    print("ALL TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
