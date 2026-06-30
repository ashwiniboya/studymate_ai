# Demo Script

**Duration:** ~5 minutes  
**Prerequisites:** Server running (`python run.py`), sample document ready (any PDF or TXT)

---

## 1. Introduction (30 seconds)

> "This is StudyMate AI — an AI-powered study assistant built with Google ADK and Gemini 2.5 Flash. It helps students learn from uploaded documents by generating notes, flashcards, quizzes, and personalized study plans."

Open **http://localhost:8000** and show the Dashboard.

---

## 2. Upload a Document (45 seconds)

1. Navigate to **Upload**
2. Drag and drop a sample PDF or TXT file
3. Point out the success toast and document appearing in the list
4. Mention: "The document is parsed, chunked, and indexed in ChromaDB for semantic search"

---

## 3. Generate Study Notes (45 seconds)

1. Go to **Notes**
2. Select the uploaded document
3. Enter a focus area: "Key Concepts"
4. Click **Generate Notes**
5. Wait for generation, then click the note to view
6. Highlight the structured markdown with headings and bullet points

> "The Notes Agent uses RAG to retrieve relevant context, then Gemini generates organized study notes."

---

## 4. Create Flashcards (30 seconds)

1. Go to **Flashcards**
2. Select document, set 10 cards
3. Click **Generate Flashcards**
4. Click the card to flip it
5. Mark "Got it" and show the next card

---

## 5. Take a Quiz (45 seconds)

1. Go to **Quiz**
2. Select document, 5 questions, medium difficulty
3. Click **Generate Quiz**, then **Start**
4. Answer a few questions
5. Click **Submit Answers**
6. Show the score and highlighted correct/incorrect answers

---

## 6. Chat with Documents (30 seconds)

1. Go to **Chat**
2. Select the document
3. Ask: "What are the main topics in this document?"
4. Show the RAG-powered response

---

## 7. Progress & Study Plan (45 seconds)

1. Go to **Progress**
2. Show the stats dashboard
3. Select a document and enter goals: "Prepare for exam"
4. Click **Create Study Plan**
5. Show the AI-generated plan and progress analysis

---

## 8. Architecture Highlight (30 seconds)

> "Under the hood, StudyMate AI uses five Google ADK agents — Planner, Notes, Quiz, Flashcard, and Progress — connected through seven MCP tools. Documents are indexed with ChromaDB for retrieval-augmented generation, and everything is backed by a FastAPI REST API with comprehensive tests."

Optionally show:
```bash
pytest tests/ -v
curl http://localhost:8000/health
```

---

## 9. Closing (15 seconds)

> "StudyMate AI demonstrates a complete multi-agent study workflow — from document upload to personalized learning — built with Google ADK, MCP, and Gemini 2.5 Flash. Thank you!"

---

## Backup Demo Tips

- If Gemini API is slow, pre-generate notes/flashcards before the demo
- Keep a small TXT file ready as a fast upload alternative
- Run `pytest tests/ -v` beforehand to show all tests passing
- Health endpoint confirms the system is ready: `curl localhost:8000/health`
