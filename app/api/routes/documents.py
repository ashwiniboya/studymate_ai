"""Document API routes."""

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api.schemas import DocumentResponse, StatusResponse
from app.database.crud import get_document, list_documents
from app.database.session import get_db
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])
doc_service = DocumentService()


@router.post("/upload", response_model=StatusResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload a PDF, DOCX, or TXT file for study."""
    content = await file.read()
    result = doc_service.upload_and_process(db, file.filename or "unknown", content)
    return StatusResponse(
        status=result["status"],
        message=result.get("message", "Document uploaded"),
        data={k: v for k, v in result.items() if k not in ("status", "message")},
    )


@router.get("/", response_model=list[DocumentResponse])
def get_documents(db: Session = Depends(get_db)):
    """List all uploaded documents."""
    return list_documents(db)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document_by_id(document_id: int, db: Session = Depends(get_db)):
    """Get a specific document by ID."""
    doc = get_document(db, document_id)
    if not doc:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/{document_id}", response_model=StatusResponse)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document and all associated data."""
    result = doc_service.delete_document(db, document_id)
    return StatusResponse(status=result["status"], message=result.get("message", ""))
