# AI-Powered Role-Based Candidate Screening System

A full-stack web application that conducts intelligent, personalised technical interviews using **Retrieval-Augmented Generation (RAG)**. Candidates upload their résumé, select a target role, and receive a fully customised AI-driven interview — grounded in role-specific knowledge from real textbooks.

Built as part of the **PGAGI AI/ML & Backend Engineering Internship** assignment.

---

## What It Does

1. **Candidate uploads a PDF résumé** → LLM extracts skills, technologies, and domain knowledge
2. **RAG pipeline retrieves relevant knowledge** from role-specific textbooks stored in ChromaDB
3. **AI generates tailored questions** grounded in both the candidate's background and the knowledge base
4. **Candidate answers questions** through an interactive UI — 8 questions per session with adaptive difficulty (easy → medium → hard)
5. **AI generates a final report** with an overall score (0–100), strengths, weaknesses, per-question scores, and a **Hire / Maybe / Reject** recommendation

---

## System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                        Browser                           │
│       Next.js 15  ·  TypeScript  ·  Tailwind CSS        │
└───────────────────────────┬──────────────────────────────┘
                            │  REST / JSON
┌───────────────────────────▼──────────────────────────────┐
│                  FastAPI  (Python 3.11)                  │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │Resume Parser│  │Interview     │  │Report Generator│  │
│  │(pdfplumber +│  │Engine        │  │(Groq LLM +     │  │
│  │ Groq LLM)  │  │(RAG-grounded)│  │ structured JSON)│  │
│  └──────┬──────┘  └──────┬───────┘  └───────┬────────┘  │
│         │                │                  │            │
│  ┌──────▼────────────────▼──────────────────▼────────┐  │
│  │              Service Layer                        │  │
│  └──────┬────────────────────────────┬───────────────┘  │
│         │                            │                   │
│  ┌──────▼────────┐          ┌────────▼──────────┐        │
│  │  PostgreSQL   │          │     ChromaDB      │        │
│  │ (SQLAlchemy 2 │          │ (sentence-        │        │
│  │   async)      │          │  transformers)    │        │
│  └───────────────┘          └───────────────────┘        │
│                                                          │
│              Groq API  (llama-3.3-70b-versatile)         │
└──────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 15 (App Router), TypeScript, Tailwind CSS |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy 2 (async) |
| **Database** | PostgreSQL 16 (via asyncpg) |
| **Vector Store** | ChromaDB (persistent, per-role collections) |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` (local, no API cost) |
| **LLM** | Groq API — `llama-3.3-70b-versatile` (OpenAI-compatible SDK) |
| **PDF Parsing** | pdfplumber |
| **Config** | Pydantic Settings v2 (`.env`) |
| **Containerisation** | Docker + Docker Compose |

---

## RAG Pipeline

```
knowledge_base/<role>/*.pdf
        │
        ▼  pdfplumber — extract raw text
   raw text
        │
        ▼  512-word chunks with 64-word overlap
   text chunks
        │
        ▼  all-MiniLM-L6-v2  →  384-dim embeddings
   embeddings
        │
        ▼  ChromaDB upsert (one collection per role)
   vector store  ←──── persists to disk in chroma_db/
        │
   At interview time:
        │
        ▼  build query from candidate skills + role
   query embedding
        │
        ▼  cosine similarity top-k retrieval
   relevant chunks
        │
        ▼  injected into Groq LLM prompt
   personalised question
```

**Design choices:**
- **ChromaDB** — embedded (no extra server in dev), same client API for prod `HttpClient` mode
- **all-MiniLM-L6-v2** — runs locally, fast inference, excellent recall for technical text
- **512-word / 64-overlap chunks** — balances context granularity vs. embedding quality

---

## Project Structure

```
candidate-screening-system/
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   │   ├── resume.py          # POST /api/v1/resume/upload
│   │   │   ├── interview.py       # start · question · answer · end
│   │   │   └── report.py          # GET /api/v1/report/{session_id}
│   │   ├── database/
│   │   │   ├── base.py            # DeclarativeBase
│   │   │   └── session.py         # async engine + get_db
│   │   ├── models/                # SQLAlchemy ORM models
│   │   │   ├── candidate.py
│   │   │   ├── session.py
│   │   │   ├── question.py
│   │   │   ├── answer.py
│   │   │   └── report.py
│   │   ├── rag/
│   │   │   ├── embeddings.py      # sentence-transformers singleton
│   │   │   ├── vector_store.py    # ChromaDB wrapper
│   │   │   ├── ingestion.py       # PDF → chunks → embeddings → store
│   │   │   └── retriever.py       # query builder + top-k retrieval
│   │   ├── resume_parser/
│   │   │   ├── extractor.py       # PDF text → LLM → structured JSON
│   │   │   └── schemas.py         # ParsedResume Pydantic model
│   │   ├── interview/
│   │   │   ├── prompts.py         # All LLM prompt templates
│   │   │   ├── question_generator.py
│   │   │   └── report_generator.py
│   │   ├── services/              # Business logic layer
│   │   │   ├── candidate_service.py
│   │   │   ├── interview_service.py
│   │   │   └── report_service.py
│   │   ├── utils/
│   │   │   ├── config.py          # Pydantic Settings
│   │   │   └── logger.py
│   │   └── main.py                # FastAPI app + lifespan
│   ├── knowledge_base/
│   │   ├── ai_ml/                 # ML textbooks
│   │   ├── backend/               # Backend / system design books
│   │   ├── frontend/
│   │   ├── fullstack/
│   │   ├── devops/
│   │   └── data_science/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx           # Step 1: upload résumé + select role
│   │   │   ├── interview/page.tsx # Step 2: live interview
│   │   │   └── results/page.tsx   # Step 3: final report
│   │   ├── lib/
│   │   │   ├── api.ts             # Typed fetch wrappers
│   │   │   └── utils.ts           # Tailwind helpers
│   │   └── types/index.ts         # Shared TypeScript types
│   ├── package.json
│   └── Dockerfile
│
└── docker-compose.yml
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/resume/upload` | Upload PDF résumé (multipart/form-data) |
| `POST` | `/api/v1/interview/start` | Start session — returns `session_id` |
| `GET`  | `/api/v1/interview/question/{session_id}` | Get next question (RAG + LLM on demand) |
| `POST` | `/api/v1/interview/answer` | Submit an answer |
| `POST` | `/api/v1/interview/end/{session_id}` | Mark session complete |
| `GET`  | `/api/v1/report/{session_id}` | Generate (or retrieve) full report |
| `GET`  | `/health` | Health check |

Interactive docs available at `http://localhost:8000/docs` when running.

---

## Database Schema

```
candidates         — id, name, email, resume_path, parsed_resume (JSON), created_at
interview_sessions — id, candidate_id, selected_role, status, current_question_idx, start_time, end_time
questions          — id, session_id, question_text, source_context, difficulty, order_index, is_follow_up
answers            — id, question_id, answer_text, quality_score (0.0–1.0), submitted_at
reports            — id, session_id, summary, strengths (JSON), weaknesses (JSON), overall_score, recommendation, generated_at
```

---

## Local Setup (Without Docker)

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 16 running on `localhost:5432`
- Free Groq API key — sign up at [console.groq.com](https://console.groq.com)

### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — fill in DATABASE_URL and LLM_API_KEY

# Start the API server
# (DB tables and knowledge-base ingestion run automatically on startup)
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

---

## Docker Setup (Recommended)

```bash
# 1. Copy and configure environment
cp backend/.env.example backend/.env
# Set LLM_API_KEY=gsk_... in backend/.env

# 2. Build and start everything
docker compose up --build
```

Services started:
- `db` — PostgreSQL 16 on port 5432
- `backend` — FastAPI on port 8000
- `frontend` — Next.js on port 3000

---

## Knowledge Base Setup

Drop role-specific PDFs into the matching subfolder before starting the server:

```
backend/knowledge_base/
├── ai_ml/          ← ML textbooks (Mitchell, Géron, Bishop…)
├── backend/        ← System design, clean code, DB internals
├── frontend/       ← React, browser performance, accessibility
├── fullstack/      ← Combined frontend + backend resources
├── devops/         ← Kubernetes, CI/CD, observability
└── data_science/   ← Statistics, pandas, SQL, visualisation
```

To re-run ingestion manually:

```bash
cd backend
python -m app.rag.ingestion
```

Embeddings persist in `backend/chroma_db/` between restarts.

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | — | `postgresql+asyncpg://user:pass@host/db` |
| `LLM_API_KEY` | Yes | — | Groq API key (`gsk_...`) |
| `LLM_BASE_URL` | Yes | — | `https://api.groq.com/openai/v1` |
| `LLM_MODEL` | No | `llama-3.3-70b-versatile` | Groq model ID |
| `LLM_TEMPERATURE` | No | `0.7` | Generation temperature |
| `EMBEDDING_MODEL` | No | `all-MiniLM-L6-v2` | sentence-transformers model |
| `QUESTIONS_PER_SESSION` | No | `8` | Questions per interview |
| `TOP_K_CHUNKS` | No | `5` | RAG chunks retrieved per question |
| `UPLOAD_DIR` | No | `uploads` | Directory for uploaded résumés |
| `CHROMA_PATH` | No | `chroma_db` | ChromaDB persistence directory |
| `DEBUG` | No | `false` | Enable verbose SQLAlchemy logging |

---

## Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| **LLM Provider** | Groq (llama-3.3-70b-versatile) | Free tier, ~300 tok/s, OpenAI-compatible — no SDK change needed |
| **Embeddings** | all-MiniLM-L6-v2 (local) | No API cost per call, 384-dim, strong semantic recall for tech text |
| **Vector DB** | ChromaDB (persistent) | Zero infrastructure in dev; same API scales to hosted mode in prod |
| **ORM** | SQLAlchemy 2 async | Native async, fully typed, battle-tested |
| **API** | FastAPI | Auto OpenAPI docs, Pydantic v2 integration, native async |
| **Frontend** | Next.js 15 App Router | File-based routing, TypeScript-first, Turbopack dev server |
| **Chunking** | 512 words / 64 overlap | Balances context granularity vs. relevance score dilution |

---

## Production Considerations

- **Authentication** — add JWT middleware before exposing APIs publicly
- **Rate limiting** — add `slowapi` or an API gateway (LLM calls are expensive per session)
- **ChromaDB** — switch `PersistentClient` → `HttpClient` for a standalone container
- **Migrations** — replace `create_all` in lifespan with `alembic upgrade head`
- **File storage** — replace local `uploads/` with S3 or Azure Blob for horizontal scaling
- **Observability** — add OpenTelemetry traces around LLM calls and DB queries

---

## Author

**Thanuj Raja** — [thanujraja1234@gmail.com](mailto:thanujraja1234@gmail.com)
