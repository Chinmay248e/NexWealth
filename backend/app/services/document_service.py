"""
Document Service — Business logic for Person 2 Document Vault.

Manages document metadata in PostgreSQL and secure local file storage.
All operations enforce strict user isolation.
"""
import os
import re
from typing import List, Optional, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status

from app.core.config import settings
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate

ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".csv", ".xlsx", ".txt", ".docx"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def get_document_storage_dir(user_id: str) -> str:
    """
    Get user-specific isolated storage directory for documents.
    """
    # Sanitize user_id for filesystem safety
    safe_user_dir = re.sub(r"[^a-zA-Z0-9_\-]", "", user_id)
    doc_dir = os.path.join(settings.UPLOAD_DIR, "documents", safe_user_dir)
    os.makedirs(doc_dir, exist_ok=True)
    return doc_dir


def sanitize_filename(filename: str) -> str:
    """
    Sanitize uploaded filename to prevent directory traversal attacks.
    """
    base = os.path.basename(filename)
    clean = re.sub(r"[^\w\.\-\s]", "_", base)
    return clean[:255] if clean else "document.pdf"


def validate_file_safety(file: UploadFile) -> str:
    """
    Validate extension and sanitize filename.
    """
    filename = file.filename or "document.pdf"
    clean_name = sanitize_filename(filename)
    _, ext = os.path.splitext(clean_name)
    ext = ext.lower()

    if ext not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(sorted(ALLOWED_DOCUMENT_EXTENSIONS))}",
        )
    return clean_name


def create_document(db: Session, user_id: str, doc_in: DocumentCreate) -> Document:
    """
    Create a Document record for metadata tracking.
    """
    document = Document(
        userId=user_id,
        fileName=doc_in.fileName,
        documentType=doc_in.documentType,
        status=doc_in.status or "uploaded",
        uploadedAt=datetime.now(timezone.utc),
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def get_documents(db: Session, user_id: str, document_type: Optional[str] = None) -> List[Document]:
    """
    Retrieve all Documents for a given user, optionally filtered by documentType.
    """
    query = db.query(Document).filter(Document.userId == user_id)
    if document_type:
        query = query.filter(Document.documentType == document_type)
    return query.order_by(Document.uploadedAt.desc(), Document.createdAt.desc()).all()


def get_document_by_id(db: Session, document_id: str, user_id: str) -> Optional[Document]:
    """
    Retrieve a single Document by ID, scoped to the authenticated user.
    """
    return (
        db.query(Document)
        .filter(Document.id == document_id, Document.userId == user_id)
        .first()
    )


def update_document(db: Session, document: Document, doc_in: DocumentUpdate) -> Document:
    """
    Update an existing Document metadata record.
    """
    update_data = doc_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document, field, value)

    db.commit()
    db.refresh(document)
    return document


def delete_document(db: Session, document: Document) -> None:
    """
    Delete a Document record and clean up stored file from disk if present.
    """
    storage_dir = get_document_storage_dir(document.userId)
    file_path = os.path.join(storage_dir, f"{document.id}_{document.fileName}")
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass

    db.delete(document)
    db.commit()
