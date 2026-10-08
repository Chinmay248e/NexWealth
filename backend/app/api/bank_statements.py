"""
Bank Statement API Router — Ingestion, parsing, and transaction creation for Person 2.

All endpoints require JWT authentication.
"""
import os
from decimal import Decimal
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.bank_statement import (
    BankStatementCreate,
    BankStatementResponse,
    BankStatementDeleteResponse,
    BankStatementParseResult,
    ImportTransactionsRequest,
    ImportTransactionsResponse,
)
from app.services.bank_statement_service import (
    create_bank_statement,
    get_bank_statements,
    get_bank_statement_by_id,
    delete_bank_statement,
    validate_statement_file,
    get_statement_storage_dir,
    parse_statement_content,
    import_parsed_transactions,
    MAX_STATEMENT_SIZE_BYTES,
)

bank_statement_router = APIRouter(prefix="/bank-statements", tags=["Bank Statements"])


@bank_statement_router.post(
    "",
    response_model=BankStatementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create bank statement metadata record",
)
def create_statement_endpoint(
    stmt_in: BankStatementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a BankStatement metadata entry.
    """
    return create_bank_statement(db=db, user_id=current_user.id, stmt_in=stmt_in)


@bank_statement_router.post(
    "/upload",
    response_model=BankStatementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload bank statement file and initiate extraction",
)
async def upload_statement_endpoint(
    file: UploadFile = File(...),
    accountName: str = Form("HDFC Salary Account"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a bank statement file (CSV, Excel, etc.) and save to user storage.
    """
    safe_filename = validate_statement_file(file)

    content = await file.read()
    if len(content) > MAX_STATEMENT_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Statement exceeds maximum allowed size of {MAX_STATEMENT_SIZE_BYTES // (1024 * 1024)}MB.",
        )

    # Initial record creation
    stmt_in = BankStatementCreate(
        fileName=safe_filename,
        accountName=accountName.strip() or "Bank Account",
        status="uploaded",
    )
    statement = create_bank_statement(db=db, user_id=current_user.id, stmt_in=stmt_in)

    # Save physical file
    user_storage_dir = get_statement_storage_dir(current_user.id)
    saved_path = os.path.join(user_storage_dir, f"{statement.id}_{safe_filename}")
    with open(saved_path, "wb") as f:
        f.write(content)

    # Try quick parse test to update status if successful
    parsed_items = parse_statement_content(content, safe_filename, statement.accountName)
    if parsed_items:
        statement.status = "parsed"
        db.commit()
        db.refresh(statement)

    return statement


@bank_statement_router.get(
    "",
    response_model=List[BankStatementResponse],
    status_code=status.HTTP_200_OK,
    summary="List all bank statements for current user",
)
def list_statements_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all BankStatement records belonging to the authenticated user.
    """
    return get_bank_statements(db=db, user_id=current_user.id)


@bank_statement_router.get(
    "/{statement_id}",
    response_model=BankStatementResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a specific bank statement by ID",
)
def get_statement_endpoint(
    statement_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a specific BankStatement by ID. Returns 404 if not found or unauthorized.
    """
    statement = get_bank_statement_by_id(db=db, statement_id=statement_id, user_id=current_user.id)
    if not statement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank statement not found.",
        )
    return statement


@bank_statement_router.get(
    "/{statement_id}/parse",
    response_model=BankStatementParseResult,
    status_code=status.HTTP_200_OK,
    summary="Extract and preview transactions from statement file",
)
def parse_statement_endpoint(
    statement_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Parse transactions from the statement file without saving to database yet.
    """
    statement = get_bank_statement_by_id(db=db, statement_id=statement_id, user_id=current_user.id)
    if not statement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank statement not found.",
        )

    user_storage_dir = get_statement_storage_dir(current_user.id)
    saved_path = os.path.join(user_storage_dir, f"{statement.id}_{statement.fileName}")

    if not os.path.exists(saved_path):
        return BankStatementParseResult(
            statementId=statement.id,
            fileName=statement.fileName,
            accountName=statement.accountName,
            status=statement.status,
            transactionCount=0,
            totalCredits=Decimal("0.00"),
            totalDebits=Decimal("0.00"),
            transactions=[],
        )

    with open(saved_path, "rb") as f:
        content = f.read()

    transactions = parse_statement_content(content, statement.fileName, statement.accountName)
    total_credits = sum((t.amount for t in transactions if t.type == "income"), Decimal("0.00"))
    total_debits = sum((t.amount for t in transactions if t.type == "expense"), Decimal("0.00"))

    return BankStatementParseResult(
        statementId=statement.id,
        fileName=statement.fileName,
        accountName=statement.accountName,
        status=statement.status,
        transactionCount=len(transactions),
        totalCredits=total_credits,
        totalDebits=total_debits,
        transactions=transactions,
    )


@bank_statement_router.post(
    "/{statement_id}/import",
    response_model=ImportTransactionsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Import parsed statement transactions into unified ledger",
)
def import_transactions_endpoint(
    statement_id: str,
    import_req: ImportTransactionsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Import transactions extracted from a bank statement into the user's ledger.
    """
    statement = get_bank_statement_by_id(db=db, statement_id=statement_id, user_id=current_user.id)
    if not statement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank statement not found.",
        )

    imported_count = import_parsed_transactions(
        db=db,
        user_id=current_user.id,
        statement=statement,
        transactions_in=import_req.transactions,
    )

    return ImportTransactionsResponse(
        message=f"Successfully imported {imported_count} transactions into ledger.",
        importedCount=imported_count,
        statementId=statement.id,
    )


@bank_statement_router.delete(
    "/{statement_id}",
    response_model=BankStatementDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a bank statement record",
)
def delete_statement_endpoint(
    statement_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a BankStatement record and stored file.
    """
    statement = get_bank_statement_by_id(db=db, statement_id=statement_id, user_id=current_user.id)
    if not statement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank statement not found.",
        )
    deleted_id = statement.id
    delete_bank_statement(db=db, statement=statement)
    return BankStatementDeleteResponse(
        message="Bank statement deleted successfully.",
        id=deleted_id,
    )

