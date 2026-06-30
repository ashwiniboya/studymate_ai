"""MCP Server for StudyMate AI tools."""

from mcp.server.fastmcp import FastMCP

from app.mcp.tools.generate_quiz import generate_quiz
from app.mcp.tools.parse_text import parse_text
from app.mcp.tools.read_docx import read_docx
from app.mcp.tools.read_pdf import read_pdf
from app.mcp.tools.save_notes import save_notes
from app.mcp.tools.store_flashcards import store_flashcards_tool
from app.mcp.tools.track_progress import track_progress_tool

mcp = FastMCP("StudyMate AI")


@mcp.tool()
def read_pdf_tool(file_path: str) -> dict:
    """Read and extract text content from a PDF file."""
    return read_pdf(file_path)


@mcp.tool()
def read_docx_tool(file_path: str) -> dict:
    """Read and extract text content from a DOCX Word document."""
    return read_docx(file_path)


@mcp.tool()
def parse_text_tool(text: str, max_length: int = 50000) -> dict:
    """Clean, normalize, and structure raw text for processing."""
    return parse_text(text, max_length=max_length)


@mcp.tool()
def save_notes_tool(document_id: int, title: str, content: str) -> dict:
    """Save study notes for a document to the database."""
    return save_notes(document_id, title, content)


@mcp.tool()
def generate_quiz_tool(document_id: int, title: str, questions_json: str) -> dict:
    """Generate and store a quiz from structured question JSON data."""
    return generate_quiz(document_id, title, questions_json)


@mcp.tool()
def store_flashcards(document_id: int, cards_json: str) -> dict:
    """Store flashcards for a document in the database."""
    return store_flashcards_tool(document_id, cards_json)


@mcp.tool()
def track_progress(document_id: int, activity_type: str, score: float = 0.0, details: str = "") -> dict:
    """Track a learning activity for progress monitoring."""
    return track_progress_tool(document_id, activity_type, score, details)


def run_server() -> None:
    """Run the MCP server via stdio transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_server()
