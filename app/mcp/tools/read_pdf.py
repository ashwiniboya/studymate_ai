"""Read PDF tool - extracts text from PDF files."""

from pathlib import Path

from pypdf import PdfReader


def read_pdf(file_path: str) -> dict:
    """Read and extract text content from a PDF file.

    Args:
        file_path: Absolute or relative path to the PDF file.

    Returns:
        Dictionary with status, text content, page count, and metadata.
    """
    path = Path(file_path)
    if not path.exists():
        return {"status": "error", "message": f"File not found: {file_path}"}
    if path.suffix.lower() != ".pdf":
        return {"status": "error", "message": "File is not a PDF"}

    try:
        reader = PdfReader(str(path))
        pages_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)

        full_text = "\n\n".join(pages_text)
        return {
            "status": "success",
            "text": full_text,
            "page_count": len(reader.pages),
            "filename": path.name,
            "char_count": len(full_text),
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to read PDF: {e}"}
