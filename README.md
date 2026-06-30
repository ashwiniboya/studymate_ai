# StudyMate AI

An AI-powered study assistant that helps students learn from uploaded documents using Google ADK agents, Gemini 2.5 Flash, RAG with ChromaDB, and the Model Context Protocol (MCP).

## Features

- **Upload Documents** — PDF, DOCX, and TXT support
- **Generate Notes** — AI-structured study notes from your materials
- **Generate Flashcards** — Interactive flashcards with spaced review tracking
- **Generate Quiz** — Multiple-choice quizzes with scoring and explanations
- **Chat** — Ask questions about your documents (RAG-powered)
- **Track Progress** — Learning analytics with AI-powered feedback
- **Study Plans** — Personalized study plans from the Planner Agent

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Agents | Google ADK + Gemini 2.5 Flash |
| Backend | FastAPI |
| Database | SQLite |
| Vector Store | ChromaDB |
| Embeddings | sentence-transformers |
| Protocol | Model Context Protocol (MCP) |
| Frontend | HTML, CSS, JavaScript |

## Agents

1. **Planner Agent** — Creates personalized study plans
2. **Notes Agent** — Generates structured study notes
3. **Quiz Agent** — Creates multiple-choice quizzes
4. **Flashcard Agent** — Generates study flashcards
5. **Progress Agent** — Tracks and analyzes learning progress

## Quick Start

```bash
# Clone and enter project
cd studymate_ai

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and set GOOGLE_API_KEY

# Run the server
python run.py
```

Open **http://localhost:8000** in your browser.

## Project Structure

```
studymate_ai/
├── app/
│   ├── agents/          # ADK agents (planner, notes, quiz, flashcard, progress)
│   ├── api/             # FastAPI routes and schemas
│   ├── database/        # SQLAlchemy models, CRUD, session
│   ├── mcp/             # MCP server and tools
│   ├── rag/             # ChromaDB vector store, chunking, embeddings
│   ├── services/        # Business logic layer
│   ├── config.py        # Application settings
│   └── main.py          # FastAPI entry point
├── frontend/            # HTML/CSS/JS single-page app
├── tests/               # Unit and integration tests
├── docs/                # Documentation
├── data/                # SQLite DB, uploads, ChromaDB (auto-created)
├── requirements.txt
└── run.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/documents/upload` | Upload a document |
| GET | `/api/documents/` | List documents |
| POST | `/api/notes/generate` | Generate study notes |
| POST | `/api/flashcards/generate` | Generate flashcards |
| POST | `/api/quiz/generate` | Generate a quiz |
| POST | `/api/quiz/{id}/submit` | Submit quiz answers |
| POST | `/api/chat/` | Chat about documents |
| GET | `/api/progress/summary` | Get progress with AI analysis |
| POST | `/api/progress/plan` | Create a study plan |

## Running Tests

```bash
pytest tests/ -v
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `read_pdf` | Extract text from PDF files |
| `read_docx` | Extract text from DOCX files |
| `parse_text` | Clean and structure raw text |
| `save_notes` | Persist study notes |
| `generate_quiz` | Store quiz questions |
| `store_flashcards` | Save flashcards |
| `track_progress` | Record learning activity |

Run the MCP server standalone:

```bash
python -m app.mcp.server
```

## Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [Architecture](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [User Guide](docs/USER_GUIDE.md)
- [Kaggle Submission](docs/KAGGLE_SUBMISSION.md)
- [Demo Script](docs/DEMO_SCRIPT.md)

## License

Apache 2.0
