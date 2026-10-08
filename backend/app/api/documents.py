"""
Document API Router — Protected document vault endpoints for Person 2.

All endpoints require JWT authentication via `get_current_user`.
"""
import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentDeleteResponse,
)
from app.services.document_service import (
    create_document,
    get_documents,
    get_document_by_id,
    update_document,
    delete_document,
    validate_file_safety,
    get_document_storage_dir,
    MAX_FILE_SIZE_BYTES,
)

document_router = APIRouter(prefix="/documents", tags=["Documents"])


@document_router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create document metadata record",
)
def create_document_endpoint(
    doc_in: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a Document metadata entry for the authenticated user.
    """
    return create_document(db=db, user_id=current_user.id, doc_in=doc_in)


@document_router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload physical document file with metadata",
)
async def upload_document_endpoint(
    file: UploadFile = File(...),
    documentType: str = Form("Other"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a document file to the user's isolated storage and record metadata.
    """
    safe_filename = validate_file_safety(file)

    # Read and check size limit
    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB.",
        )

    # Create DB entry
    doc_in = DocumentCreate(
        fileName=safe_filename,
        documentType=documentType.strip() or "Other",
        status="uploaded",
    )
    document = create_document(db=db, user_id=current_user.id, doc_in=doc_in)

    # Save to disk
    user_storage_dir = get_document_storage_dir(current_user.id)
    saved_path = os.path.join(user_storage_dir, f"{document.id}_{safe_filename}")
    with open(saved_path, "wb") as f:
        f.write(content)

    return document


@document_router.get(
    "",
    response_model=List[DocumentResponse],
    status_code=status.HTTP_200_OK,
    summary="List all documents for current user",
)
def list_documents_endpoint(
    documentType: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all Document records belonging to the authenticated user.
    """
    return get_documents(db=db, user_id=current_user.id, document_type=documentType)


@document_router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a specific document by ID",
)
def get_document_endpoint(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a specific Document by ID. Returns 404 if not found or not owned.
    """
    document = get_document_by_id(db=db, document_id=document_id, user_id=current_user.id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document record not found.",
        )
    return document


@document_router.put(
    "/{document_id}",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update document metadata",
)
def update_document_endpoint(
    document_id: str,
    doc_in: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update document metadata.
    """
    document = get_document_by_id(db=db, document_id=document_id, user_id=current_user.id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document record not found.",
        )
    return update_document(db=db, document=document, doc_in=doc_in)


@document_router.delete(
    "/{document_id}",
    response_model=DocumentDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a document record",
)
def delete_document_endpoint(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a Document record and clean up stored file.
    """
    document = get_document_by_id(db=db, document_id=document_id, user_id=current_user.id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document record not found.",
        )
    deleted_id = document.id
    delete_document(db=db, document=document)
    return DocumentDeleteResponse(
        message="Document record deleted successfully.",
        id=deleted_id,
    )
