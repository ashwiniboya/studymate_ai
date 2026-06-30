# Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (SPA)                          │
│  Dashboard │ Chat │ Upload │ Notes │ Flashcards │ Quiz     │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
┌────────────────────────▼────────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌──────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │ API Layer│  │ Service Layer│  │ Agent Orchestration │   │
│  └──────────┘  └──────────────┘  └─────────────────────┘   │
└──────┬──────────────┬──────────────────┬────────────────────┘
       │              │                  │
┌──────▼──────┐ ┌─────▼─────┐  ┌────────▼────────┐
│   SQLite    │ │  ChromaDB  │  │  Google ADK     │
│  Database   │ │  (RAG)     │  │  Agents (x5)    │
└─────────────┘ └───────────┘  └────────┬────────┘
                                        │
                               ┌────────▼────────┐
                               │  Gemini 2.5     │
                               │  Flash Model    │
                               └─────────────────┘
                                        │
                               ┌────────▼────────┐
                               │  MCP Tools (x7) │
                               └─────────────────┘
```

## Component Layers

### 1. Frontend Layer
Single-page application with vanilla HTML/CSS/JS. Communicates with the backend via REST API. Pages: Dashboard, Upload, Chat, Notes, Flashcards, Quiz, Progress.

### 2. API Layer (`app/api/`)
FastAPI routers with Pydantic schemas for request/response validation. Handles HTTP concerns only — delegates to services.

### 3. Service Layer (`app/services/`)
- **DocumentService** — Upload, parse, index documents
- **AgentService** — Orchestrates ADK agent tool functions

### 4. Agent Layer (`app/agents/`)
Five Google ADK agents, each with specialized tools:

| Agent | Tool(s) | Purpose |
|-------|---------|---------|
| Planner | `create_study_plan` | Study plan generation |
| Notes | `generate_notes` | Note generation |
| Quiz | `create_quiz` | Quiz creation |
| Flashcard | `create_flashcards` | Flashcard generation |
| Progress | `get_learning_progress`, `record_activity` | Analytics |

### 5. MCP Layer (`app/mcp/`)
Model Context Protocol server exposing 7 tools as standardized interfaces for document processing and data persistence.

### 6. RAG Layer (`app/rag/`)
- **Chunker** — Splits documents into overlapping chunks
- **Embeddings** — sentence-transformers (`all-MiniLM-L6-v2`)
- **VectorStore** — ChromaDB persistent storage with cosine similarity search

### 7. Database Layer (`app/database/`)
SQLite with SQLAlchemy ORM. Tables: documents, notes, flashcards, quizzes, quiz_questions, progress_records, study_plans.

## Data Flow

### Document Upload Flow
```
Upload → DocumentService → MCP (read_pdf/read_docx) → parse_text
  → SQLite (metadata) → ChromaDB (chunks + embeddings) → track_progress
```

### Chat / Q&A Flow
```
User Question → AgentService.chat → RAG search (ChromaDB)
  → Context + Question → Gemini 2.5 Flash → Response
```

### Notes Generation Flow
```
Request → Notes Agent → RAG retrieve → Gemini generate
  → MCP save_notes → SQLite → track_progress
```

## Design Decisions

1. **Modular agents** — Each agent is independent with its own ADK `Agent` definition, enabling standalone testing via `adk run`.
2. **MCP as tool layer** — Document I/O and persistence exposed as MCP tools, reusable across agents.
3. **RAG for context** — ChromaDB provides semantic search so agents answer from actual document content.
4. **SQLite for simplicity** — Zero-config database suitable for capstone/demo; easily upgraded to PostgreSQL.
5. **Service layer separation** — API routes never call agents directly; services provide a stable interface.

## File Structure

```
app/
├── main.py                 # FastAPI app, CORS, static files
├── config.py               # Pydantic settings
├── agents/
│   ├── utils.py            # Shared Gemini + RAG helpers
│   ├── planner/agent.py
│   ├── notes/agent.py
│   ├── quiz/agent.py
│   ├── flashcard/agent.py
│   └── progress/agent.py
├── api/routes/             # One router per feature
├── database/               # models.py, crud.py, session.py
├── mcp/                    # server.py + tools/
├── rag/                    # chunker, embeddings, vector_store
└── services/               # document_service, agent_service
```
