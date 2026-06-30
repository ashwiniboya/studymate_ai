# Installation Guide

## Prerequisites

- **Python 3.10+**
- **pip** (Python package manager)
- **Google AI Studio API Key** — [Get one here](https://aistudio.google.com/apikey)

## Step-by-Step Installation

### 1. Clone or Download the Project

```bash
cd studymate_ai
```

### 2. Create a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** The first run downloads the `sentence-transformers` embedding model (~80MB). This happens automatically on first document upload.

### 4. Configure Environment Variables

```bash
copy .env.example .env    # Windows
cp .env.example .env      # macOS/Linux
```

Edit `.env`:

```env
GOOGLE_API_KEY=your_actual_api_key_here
DATABASE_URL=sqlite:///./data/studymate.db
CHROMA_PERSIST_DIR=./data/chroma
UPLOAD_DIR=./data/uploads
MODEL_NAME=gemini-2.5-flash
```

### 5. Run the Application

```bash
python run.py
```

The server starts at **http://localhost:8000**.

### 6. Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# Run tests
pytest tests/ -v
```

## Running ADK Agents Standalone

Each agent can be run with the ADK CLI:

```bash
adk run app/agents/notes
adk web app/agents
```

## Running the MCP Server

```bash
python -m app.mcp.server
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `GOOGLE_API_KEY` not set | Add your key to `.env` |
| Port 8000 in use | Change port in `run.py` |
| ChromaDB errors | Delete `data/chroma/` and restart |
| Embedding model slow | First download is one-time; subsequent runs are fast |
| PDF extraction empty | Some scanned PDFs lack text layers; use OCR tools first |

## System Requirements

- **RAM:** 4GB minimum (8GB recommended for embedding model)
- **Disk:** ~500MB for dependencies + models
- **Network:** Required for Gemini API calls
