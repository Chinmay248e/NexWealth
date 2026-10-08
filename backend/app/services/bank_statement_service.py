"""
Bank Statement Service — Business logic for Person 2 Bank Statement processing.

Handles statement metadata, secure file storage, multi-bank statement parsing
(CSV/Excel/Text/Structured data using Pandas), and importing validated transactions.
All operations strictly enforce user isolation.
"""
import os
import re
import io
import csv
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timezone, date as date_type
from decimal import Decimal
import pandas as pd
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status

from app.core.config import settings
from app.models.bank_statement import BankStatement
from app.models.transaction import Transaction
from app.schemas.bank_statement import (
    BankStatementCreate,
    BankStatementUpdate,
    ParsedTransactionItem,
    BankStatementParseResult,
)

ALLOWED_STATEMENT_EXTENSIONS = {".csv", ".xlsx", ".xls", ".txt", ".tsv", ".pdf"}
MAX_STATEMENT_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

# Smart category auto-detection keywords for Indian financial transactions
CATEGORY_KEYWORDS: Dict[str, str] = {
    "food": "Food",
    "swiggy": "Food",
    "zomato": "Food",
    "blinkit": "Food",
    "zepto": "Food",
    "supermarket": "Food",
    "grocery": "Food",
    "restaurant": "Food",
    "amazon": "Shopping",
    "flipkart": "Shopping",
    "myntra": "Shopping",
    "shopping": "Shopping",
    "retail": "Shopping",
    "uber": "Transport",
    "ola": "Transport",
    "metro": "Transport",
    "fuel": "Transport",
    "petrol": "Transport",
    "diesel": "Transport",
    "electricity": "Bills",
    "bescom": "Bills",
    "airtel": "Bills",
    "jio": "Bills",
    "broadband": "Bills",
    "water": "Bills",
    "netflix": "Entertainment",
    "spotify": "Entertainment",
    "prime": "Entertainment",
    "movie": "Entertainment",
    "cinema": "Entertainment",
    "hospital": "Medical",
    "pharmacy": "Medical",
    "apollo": "Medical",
    "medplus": "Medical",
    "doctor": "Medical",
    "flight": "Travel",
    "irctc": "Travel",
    "hotel": "Travel",
    "makemytrip": "Travel",
    "school": "Education",
    "college": "Education",
    "course": "Education",
    "udemy": "Education",
    "salary": "Salary",
    "interest": "Dividend",
    "dividend": "Dividend",
    "refund": "Refund",
}


def get_statement_storage_dir(user_id: str) -> str:
    """
    Get user-specific isolated storage directory for bank statements.
    """
    safe_user_dir = re.sub(r"[^a-zA-Z0-9_\-]", "", user_id)
    statement_dir = os.path.join(settings.UPLOAD_DIR, "statements", safe_user_dir)
    os.makedirs(statement_dir, exist_ok=True)
    return statement_dir


def sanitize_statement_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal.
    """
    base = os.path.basename(filename)
    clean = re.sub(r"[^\w\.\-\s]", "_", base)
    return clean[:255] if clean else "statement.csv"


def validate_statement_file(file: UploadFile) -> str:
    """
    Validate extension and clean filename.
    """
    filename = file.filename or "statement.csv"
    clean_name = sanitize_statement_filename(filename)
    _, ext = os.path.splitext(clean_name)
    ext = ext.lower()

    if ext not in ALLOWED_STATEMENT_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported statement format '{ext}'. Allowed formats: {', '.join(sorted(ALLOWED_STATEMENT_EXTENSIONS))}",
        )
    return clean_name


def auto_categorize(narration: str, txn_type: str) -> str:
    """
    Determine category based on narration keywords.
    """
    lower = narration.lower()
    for kw, cat in CATEGORY_KEYWORDS.items():
        if kw in lower:
            return cat
    return "Other" if txn_type == "expense" else "Income"


def normalize_date_string(date_val: Any) -> str:
    """
    Parse varied date formats to ISO YYYY-MM-DD.
    """
    if pd.isna(date_val) or date_val is None:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if isinstance(date_val, (datetime, date_type)):
        return date_val.strftime("%Y-%m-%d")
    
    date_str = str(date_val).strip()
    if not date_str or date_str.lower() in ("nan", "none", "nat"):
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Clean date string (strip time part if present e.g. '2026-09-01 00:00:00' or '2026-09-01T00:00:00')
    if " " in date_str and len(date_str) > 10:
        parts = date_str.split(" ")
        if len(parts[0]) >= 8:
            date_str = parts[0]
    elif "T" in date_str and len(date_str) > 10:
        parts = date_str.split("T")
        if len(parts[0]) >= 8:
            date_str = parts[0]

    for fmt in (
        "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d",
        "%d-%b-%Y", "%d %b %Y", "%d-%B-%Y", "%d %B %Y",
        "%m/%d/%Y", "%m-%d-%Y", "%d.%m.%Y", "%Y.%m.%d",
    ):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
            
    # Try pandas to_datetime as fallback
    try:
        dt = pd.to_datetime(date_str, dayfirst=True)
        if pd.notna(dt):
            return dt.strftime("%Y-%m-%d")
    except Exception:
        pass

    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def clean_amount_str(val: Any) -> Tuple[Decimal, Optional[str]]:
    """
    Parses an amount string/number, extracting the absolute Decimal amount
    and an optional inferred type ('income' or 'expense') if suffixes like 'Cr', 'Dr', or negative sign exist.
    """
    if pd.isna(val) or val is None:
        return Decimal("0.00"), None
    
    if isinstance(val, (int, float, Decimal)):
        fval = float(val)
        inferred = "expense" if fval < 0 else "income"
        return Decimal(str(abs(fval))).quantize(Decimal("0.01")), inferred

    s = str(val).strip()
    if not s or s.lower() in ("nan", "none", "null", "-", ""):
        return Decimal("0.00"), None
    
    inferred = None
    lower_s = s.lower()
    if "cr" in lower_s or "credit" in lower_s:
        inferred = "income"
    elif "dr" in lower_s or "debit" in lower_s:
        inferred = "expense"

    # Check parentheses for negative: (100.00)
    if s.startswith("(") and s.endswith(")"):
        inferred = "expense"
        s = s[1:-1]
    elif s.startswith("-"):
        inferred = "expense"
        s = s[1:]
    elif s.startswith("+"):
        inferred = "income"
        s = s[1:]

    # Remove currency symbols (₹, $, €, £, Rs, INR) and commas
    cleaned = re.sub(r"[^\d.]", "", s)
    if not cleaned:
        return Decimal("0.00"), inferred
    
    try:
        amt = Decimal(cleaned).quantize(Decimal("0.01"))
        return amt, inferred
    except Exception:
        return Decimal("0.00"), inferred


def detect_and_normalize_csv_text(raw_text: str) -> Tuple[str, str]:
    """
    Normalizes raw CSV/text content by stripping fully-quoted rows
    (e.g., '"Date,Description,Amount,Type"' -> 'Date,Description,Amount,Type')
    and detecting the most appropriate delimiter (comma, tab, semicolon, pipe).
    """
    lines = raw_text.splitlines()
    cleaned_lines = []
    
    for line in lines:
        s = line.strip()
        if not s:
            continue
        
        # Check for fully quoted row like "Date,Description,Amount,Type"
        # Avoid unquoting lines that have field-delimiting quote sequences like '","' or '";"'
        if (s.startswith('"') and s.endswith('"') and len(s) >= 2):
            if not any(sep_seq in s for sep_seq in ['","', '";"', '"\t"', '"|"']):
                inner = s[1:-1]
                if any(delim in inner for delim in [",", ";", "\t", "|"]) and inner.count('"') % 2 == 0:
                    s = inner
        elif (s.startswith("'") and s.endswith("'") and len(s) >= 2):
            if not any(sep_seq in s for sep_seq in ["','", "';'", "'\t'", "'|'"]):
                inner = s[1:-1]
                if any(delim in inner for delim in [",", ";", "\t", "|"]) and inner.count("'") % 2 == 0:
                    s = inner
        
        cleaned_lines.append(s)
        
    cleaned_text = "\n".join(cleaned_lines)
    
    # Delimiter detection
    delimiter = ","
    if cleaned_lines:
        sample = "\n".join(cleaned_lines[:10])
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=[",", "\t", ";", "|"])
            delimiter = dialect.delimiter
        except Exception:
            # Fallback heuristic: count delimiters in first line
            first_line = cleaned_lines[0]
            counts = {
                ",": first_line.count(","),
                "\t": first_line.count("\t"),
                ";": first_line.count(";"),
                "|": first_line.count("|"),
            }
            best_delim = max(counts, key=counts.get)
            if counts[best_delim] > 0:
                delimiter = best_delim
                
    return cleaned_text, delimiter


def parse_statement_content(content: bytes, filename: str, account_name: str) -> List[ParsedTransactionItem]:
    """
    Extract structured transactions from CSV, TSV, or spreadsheet content using Pandas.
    Robustly handles:
    - Standard CSV, TSV, semicolon, pipe files
    - Fully-quoted CSV rows (e.g. '"Date,Description,Amount,Type"')
    - Excel spreadsheets (.xlsx, .xls)
    - Varied Indian date formats and amount notations (e.g. ₹50,000.00, Dr/Cr)
    """
    _, ext = os.path.splitext(filename.lower())
    transactions: List[ParsedTransactionItem] = []

    try:
        if ext in (".xlsx", ".xls"):
            df = pd.read_excel(io.BytesIO(content))
        else:
            # Decode bytes with fallback encoding strategy
            decoded_text = ""
            for enc in ("utf-8-sig", "utf-8", "latin1", "cp1252"):
                try:
                    decoded_text = content.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue

            if not decoded_text:
                decoded_text = content.decode("utf-8", errors="ignore")

            cleaned_text, detected_delim = detect_and_normalize_csv_text(decoded_text)
            if ext == ".tsv":
                detected_delim = "\t"

            # Parse with pandas
            try:
                df = pd.read_csv(io.StringIO(cleaned_text), sep=detected_delim, engine="python")
            except Exception:
                try:
                    df = pd.read_csv(io.StringIO(cleaned_text), sep=None, engine="python")
                except Exception:
                    df = pd.read_csv(io.StringIO(cleaned_text))

            # Safety fallback: if reading resulted in a single column that contains delimiters, split it
            if len(df.columns) == 1:
                first_col_name = str(df.columns[0])
                for candidate_delim in (",", ";", "\t", "|"):
                    if candidate_delim in first_col_name:
                        try:
                            df = pd.read_csv(io.StringIO(cleaned_text), sep=candidate_delim, engine="python")
                            break
                        except Exception:
                            pass

        # Normalize column names for flexible matching
        col_map = {str(c).strip().lower(): c for c in df.columns}
        
        # Identify date column
        date_col = None
        for key in (
            "date", "txn date", "transaction date", "value date", "posting date",
            "trans date", "txndate", "transaction_date", "value_date", "trade date"
        ):
            if key in col_map:
                date_col = col_map[key]
                break
        
        # Identify description column
        desc_col = None
        for key in (
            "description", "narration", "particulars", "details", "remarks",
            "memo", "transaction details", "transaction_details", "payee", "beneficiary", "name"
        ):
            if key in col_map:
                desc_col = col_map[key]
                break

        # Identify amount / debit / credit columns
        amount_col = None
        debit_col = None
        credit_col = None
        type_col = None

        for key in (
            "amount", "transaction amount", "amt", "total",
            "amount (inr)", "amount(inr)", "amount (rs)", "amount(rs)", "transaction_amount"
        ):
            if key in col_map:
                amount_col = col_map[key]
                break

        for key in (
            "debit", "withdrawal", "dr", "withdrawals", "debit amount",
            "debit (inr)", "withdrawal (inr)", "dr amount", "debit_amount", "withdrawal_amount"
        ):
            if key in col_map:
                debit_col = col_map[key]
                break

        for key in (
            "credit", "deposit", "cr", "deposits", "credit amount",
            "credit (inr)", "deposit (inr)", "cr amount", "credit_amount", "deposit_amount"
        ):
            if key in col_map:
                credit_col = col_map[key]
                break

        for key in (
            "type", "txn type", "cr/dr", "cr / dr", "transaction type",
            "transaction_type", "d/c", "dr/cr", "type (cr/dr)"
        ):
            if key in col_map:
                type_col = col_map[key]
                break

        # Fallback if no matching columns: take positional
        if date_col is None and len(df.columns) >= 1:
            date_col = df.columns[0]
        if desc_col is None and len(df.columns) >= 2:
            desc_col = df.columns[1]
        if amount_col is None and debit_col is None and len(df.columns) >= 3:
            amount_col = df.columns[2]

        for _, row in df.iterrows():
            raw_date = row.get(date_col) if date_col else datetime.now(timezone.utc).strftime("%Y-%m-%d")
            raw_desc = str(row.get(desc_col, "")).strip() if desc_col else "Bank Transaction"
            if not raw_desc or raw_desc.lower() in ("nan", "none", "null"):
                continue

            iso_date = normalize_date_string(raw_date)
            txn_type = "expense"
            amt_val = Decimal("0.00")

            # Case 1: Separate Debit & Credit columns
            has_debit = False
            has_credit = False

            if debit_col and pd.notna(row.get(debit_col)):
                deb_val, _ = clean_amount_str(row.get(debit_col))
                if deb_val > 0:
                    has_debit = True
                    amt_val = deb_val
                    txn_type = "expense"

            if not has_debit and credit_col and pd.notna(row.get(credit_col)):
                cred_val, _ = clean_amount_str(row.get(credit_col))
                if cred_val > 0:
                    has_credit = True
                    amt_val = cred_val
                    txn_type = "income"

            # Case 2: Unified Amount column
            if not has_debit and not has_credit and amount_col and pd.notna(row.get(amount_col)):
                parsed_amt, inferred_type = clean_amount_str(row.get(amount_col))
                amt_val = parsed_amt

                if type_col and pd.notna(row.get(type_col)):
                    raw_type_str = str(row.get(type_col, "")).strip().lower()
                    if raw_type_str in ("cr", "credit", "income", "deposit", "c", "+"):
                        txn_type = "income"
                    elif raw_type_str in ("dr", "debit", "expense", "withdrawal", "d", "-"):
                        txn_type = "expense"
                    elif inferred_type:
                        txn_type = inferred_type
                    else:
                        txn_type = "expense"
                elif inferred_type:
                    txn_type = inferred_type
                else:
                    txn_type = "expense"

            if amt_val > 0:
                category = auto_categorize(raw_desc, txn_type)
                transactions.append(
                    ParsedTransactionItem(
                        date=iso_date,
                        description=raw_desc,
                        amount=amt_val,
                        type=txn_type,
                        category=category,
                        source=account_name,
                    )
                )
    except Exception:
        pass

    return transactions


def create_bank_statement(db: Session, user_id: str, stmt_in: BankStatementCreate) -> BankStatement:
    """
    Create a BankStatement record.
    """
    statement = BankStatement(
        userId=user_id,
        fileName=stmt_in.fileName,
        accountName=stmt_in.accountName,
        status=stmt_in.status or "uploaded",
        uploadedAt=datetime.now(timezone.utc),
    )
    db.add(statement)
    db.commit()
    db.refresh(statement)
    return statement


def get_bank_statements(db: Session, user_id: str) -> List[BankStatement]:
    """
    Retrieve all BankStatement records for a user.
    """
    return (
        db.query(BankStatement)
        .filter(BankStatement.userId == user_id)
        .order_by(BankStatement.uploadedAt.desc(), BankStatement.createdAt.desc())
        .all()
    )


def get_bank_statement_by_id(db: Session, statement_id: str, user_id: str) -> Optional[BankStatement]:
    """
    Retrieve a single BankStatement by ID, scoped to user.
    """
    return (
        db.query(BankStatement)
        .filter(BankStatement.id == statement_id, BankStatement.userId == user_id)
        .first()
    )


def update_bank_statement(db: Session, statement: BankStatement, stmt_in: BankStatementUpdate) -> BankStatement:
    """
    Update BankStatement metadata.
    """
    update_data = stmt_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(statement, field, value)

    db.commit()
    db.refresh(statement)
    return statement


def delete_bank_statement(db: Session, statement: BankStatement) -> None:
    """
    Delete BankStatement and clean up stored file.
    """
    storage_dir = get_statement_storage_dir(statement.userId)
    file_path = os.path.join(storage_dir, f"{statement.id}_{statement.fileName}")
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass

    db.delete(statement)
    db.commit()


def import_parsed_transactions(
    db: Session,
    user_id: str,
    statement: BankStatement,
    transactions_in: List[ParsedTransactionItem],
) -> int:
    """
    Insert validated parsed transactions into the user's unified Transactions ledger.
    """
    count = 0
    for item in transactions_in:
        txn = Transaction(
            userId=user_id,
            type=item.type,
            description=item.description,
            amount=item.amount,
            category=item.category,
            date=datetime.strptime(item.date, "%Y-%m-%d").date(),
            source=item.source or statement.accountName,
        )
        db.add(txn)
        count += 1

    statement.status = "parsed"
    db.commit()
    return count
