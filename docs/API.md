# API Documentation

Base URL: `http://localhost:8000`

## Health

### `GET /health`

Returns application health status.

**Response:**
```json
{
  "status": "healthy",
  "app": "StudyMate AI",
  "version": "1.0.0",
  "model": "gemini-2.5-flash",
  "vector_chunks": 42
}
```

---

## Documents

### `POST /api/documents/upload`

Upload a PDF, DOCX, or TXT file.

**Request:** `multipart/form-data` with `file` field.

**Response:**
```json
{
  "status": "success",
  "message": "Document uploaded",
  "data": {
    "document_id": 1,
    "title": "Biology Notes",
    "filename": "biology.pdf",
    "file_type": "pdf",
    "chunk_count": 15,
    "word_count": 3200
  }
}
```

### `GET /api/documents/`

List all uploaded documents.

### `GET /api/documents/{id}`

Get a specific document.

### `DELETE /api/documents/{id}`

Delete a document and all associated data.

---

## Notes

### `POST /api/notes/generate`

Generate AI study notes from a document.

**Request:**
```json
{
  "document_id": 1,
  "focus_area": "Chapter 3"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Notes saved successfully (ID: 1)",
  "data": {
    "note_id": 1,
    "content": "## Study Notes\n..."
  }
}
```

### `GET /api/notes/`

List all notes. Optional query: `?document_id=1`

### `GET /api/notes/{id}`

Get a specific note with full content.

---

## Flashcards

### `POST /api/flashcards/generate`

Generate flashcards from a document.

**Request:**
```json
{
  "document_id": 1,
  "num_cards": 10
}
```

### `GET /api/flashcards/`

List all flashcards. Optional query: `?document_id=1`

### `POST /api/flashcards/{id}/review`

Record a flashcard review.

**Request:**
```json
{
  "correct": true
}
```

---

## Quiz

### `POST /api/quiz/generate`

Generate a quiz from a document.

**Request:**
```json
{
  "document_id": 1,
  "num_questions": 5,
  "difficulty": "medium"
}
```

### `GET /api/quiz/`

List all quizzes with questions.

### `GET /api/quiz/{id}`

Get a quiz with all questions and options.

### `POST /api/quiz/{id}/submit`

Submit quiz answers and get scored results.

**Request:**
```json
{
  "answers": {
    "1": "Option A",
    "2": "Option C"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Score: 4/5 (80.0%)",
  "data": {
    "score": 80.0,
    "correct": 4,
    "total": 5,
    "results": [...]
  }
}
```

---

## Chat

### `POST /api/chat/`

Ask questions about uploaded documents (RAG-powered).

**Request:**
```json
{
  "message": "What is photosynthesis?",
  "document_id": 1
}
```

**Response:**
```json
{
  "response": "Photosynthesis is the process by which...",
  "context_used": true
}
```

---

## Progress

### `GET /api/progress/summary`

Get learning progress with AI analysis. Optional query: `?document_id=1`

**Response:**
```json
{
  "status": "success",
  "data": {
    "summary": {
      "total_documents": 3,
      "total_notes": 5,
      "total_flashcards": 30,
      "total_quizzes": 2,
      "average_score": 85.0
    },
    "analysis": "You've made great progress..."
  }
}
```

### `GET /api/progress/records`

List activity records.

### `POST /api/progress/plan`

Create a study plan using the Planner Agent.

**Request:**
```json
{
  "document_id": 1,
  "goals": "Prepare for midterm exam"
}
```

---

## Error Responses

| Status | Meaning |
|--------|---------|
| 404 | Resource not found |
| 422 | Validation error (invalid request body) |
| 500 | Server error |

All endpoints return JSON. Agent/MCP operations return `status: "error"` with a `message` field on failure.
