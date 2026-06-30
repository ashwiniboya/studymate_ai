"""Document upload and processing service."""

import shutil
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.database import crud
from app.mcp.tools.parse_text import parse_text
from app.mcp.tools.read_docx import read_docx
from app.mcp.tools.read_pdf import read_pdf
from app.mcp.tools.track_progress import track_progress_tool
from app.rag.vector_store import get_vector_store


class DocumentService:
    """Handles document upload, parsing, and indexing."""

    SUPPORTED_TYPES = {".pdf": "pdf", ".docx": "docx", ".doc": "docx", ".txt": "txt"}

    def __init__(self) -> None:
        self.upload_dir = settings.upload_path
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def upload_and_process(self, db: Session, filename: str, file_content: bytes) -> dict:
        """Upload a file, extract text, index in vector store, and save to DB."""
        ext = Path(filename).suffix.lower()
        if ext not in self.SUPPORTED_TYPES:
            return {
                "status": "error",
                "message": f"Unsupported file type: {ext}. Supported: {', '.join(self.SUPPORTED_TYPES)}",
            }

        unique_name = f"{uuid.uuid4().hex}{ext}"
        file_path = self.upload_dir / unique_name
        file_path.write_bytes(file_content)

        file_type = self.SUPPORTED_TYPES[ext]
        text = self._extract_text(str(file_path), file_type)
        if not text:
            file_path.unlink(missing_ok=True)
            return {"status": "error", "message": "Could not extract text from file"}

        parsed = parse_text(text)
        clean_text = parsed.get("text", text)
        title = Path(filename).stem.replace("_", " ").replace("-", " ").title()

        doc = crud.create_document(
            db,
            filename=filename,
            file_path=str(file_path),
            file_type=file_type,
            title=title,
            content_preview=clean_text[:500],
        )

        store = get_vector_store()
        chunk_count = store.add_document(doc.id, clean_text, metadata={"title": title, "filename": filename})
        doc.chunk_count = chunk_count
        db.commit()

        track_progress_tool(
            document_id=doc.id,
            activity_type="document_uploaded",
            details=f"Uploaded: {filename}",
        )

        return {
            "status": "success",
            "document_id": doc.id,
            "title": doc.title,
            "filename": filename,
            "file_type": file_type,
            "chunk_count": chunk_count,
            "word_count": parsed.get("word_count", 0),
            "preview": parsed.get("preview", ""),
        }

    def delete_document(self, db: Session, document_id: int) -> dict:
        """Delete a document and its vector store entries."""
        doc = crud.get_document(db, document_id)
        if not doc:
            return {"status": "error", "message": "Document not found"}

        get_vector_store().delete_document(document_id)
        Path(doc.file_path).unlink(missing_ok=True)
        crud.delete_document(db, document_id)
        return {"status": "success", "message": "Document deleted"}

    def _extract_text(self, file_path: str, file_type: str) -> str:
        if file_type == "pdf":
            result = read_pdf(file_path)
        elif file_type == "docx":
            result = read_docx(file_path)
        elif file_type == "txt":
            result = {"status": "success", "text": Path(file_path).read_text(encoding="utf-8", errors="ignore")}
        else:
            return ""

        return result.get("text", "") if result.get("status") == "success" else ""
