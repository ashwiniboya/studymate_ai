# Kaggle Submission Write-up

## Project Title
**StudyMate AI — An AI-Powered Study Assistant Built with Google ADK**

## Overview

StudyMate AI is a production-ready study assistant that helps students learn from uploaded documents. Built as a Google AI Agents Capstone project, it demonstrates multi-agent orchestration, retrieval-augmented generation (RAG), and the Model Context Protocol (MCP) in a cohesive, deployable application.

## Problem Statement

Students struggle to efficiently extract, organize, and retain information from lengthy course materials. Manual note-taking, flashcard creation, and self-testing are time-consuming. StudyMate AI automates these tasks using specialized AI agents that work together to create a complete study workflow.

## Solution

A modular web application with five Google ADK agents, each responsible for a specific study task:

| Agent | Capability |
|-------|-----------|
| Planner Agent | Personalized study plans with time estimates |
| Notes Agent | Structured markdown study notes |
| Quiz Agent | Multiple-choice quizzes with explanations |
| Flashcard Agent | Term/definition flashcards with review tracking |
| Progress Agent | Learning analytics with AI feedback |

## Technical Architecture

- **Google ADK** — Agent framework with tool-calling and Gemini 2.5 Flash
- **MCP** — Seven standardized tools for document I/O and persistence
- **ChromaDB + RAG** — Semantic search over document chunks for grounded responses
- **FastAPI** — REST API backend with automatic OpenAPI docs
- **SQLite** — Lightweight persistence for notes, quizzes, flashcards, and progress

## Key Features Demonstrated

1. **Multi-agent system** — Five specialized agents with distinct tools and instructions
2. **RAG pipeline** — Document chunking → embedding → ChromaDB → context retrieval → Gemini generation
3. **MCP integration** — Tools exposed via FastMCP for interoperability
4. **Full-stack application** — Responsive frontend with 7 functional pages
5. **Automated testing** — 50+ unit and integration tests across all layers

## How It Works

1. Student uploads a PDF/DOCX/TXT document
2. MCP tools extract and clean the text
3. Text is chunked and embedded into ChromaDB
4. Student requests notes, flashcards, or a quiz
5. The relevant agent retrieves context via RAG
6. Gemini 2.5 Flash generates the content
7. MCP tools persist results to SQLite
8. Progress Agent tracks all activities and provides feedback

## Results

- End-to-end document-to-study-material pipeline in seconds
- Grounded Q&A that references actual document content
- Quiz scoring with detailed explanations
- Flashcard review tracking with accuracy metrics
- AI-generated study plans tailored to student goals

## Future Enhancements

- Multi-user authentication and cloud deployment
- Spaced repetition algorithm for flashcards
- Collaborative study groups
- Voice-based interaction
- Support for more document formats (PPTX, images with OCR)

## Repository Structure

```
studymate_ai/
├── app/agents/     # 5 ADK agents
├── app/mcp/        # MCP server + 7 tools
├── app/rag/        # ChromaDB RAG pipeline
├── app/api/        # FastAPI REST endpoints
├── frontend/       # Responsive SPA
├── tests/          # Comprehensive test suite
└── docs/           # Full documentation
```

## Conclusion

StudyMate AI showcases how Google ADK agents, MCP tools, and RAG can be combined to build a practical, student-facing application. The modular architecture makes each component independently testable and extensible, following production engineering best practices.
