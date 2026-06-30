"""Read DOCX tool - extracts text from Word documents."""

from pathlib import Path

from docx import Document as DocxDocument


def read_docx(file_path: str) -> dict:
    """Read and extract text content from a DOCX file.

    Args:
        file_path: Absolute or relative path to the DOCX file.

    Returns:
        Dictionary with status, text content, and metadata.
    """
    path = Path(file_path)
    if not path.exists():
        return {"status": "error", "message": f"File not found: {file_path}"}
    if path.suffix.lower() not in (".docx", ".doc"):
        return {"status": "error", "message": "File is not a DOCX document"}

    try:
        doc = DocxDocument(str(path))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        full_text = "\n\n".join(paragraphs)

        return {
            "status": "success",
            "text": full_text,
            "paragraph_count": len(paragraphs),
            "filename": path.name,
            "char_count": len(full_text),
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to read DOCX: {e}"}
