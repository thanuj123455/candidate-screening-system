# AI-Powered Role-Based Candidate Screening System

A production-grade web application that conducts intelligent, personalised technical interviews using **Retrieval-Augmented Generation (RAG)**. Candidates upload their résumé, pick a target role, and receive a custom interview powered by Claude AI — grounded in role-specific knowledge.

---

## Architecture Overview

```
┌────────────────────────────────────────────────────────────┐
│                        Browser                             │
│         Next.js 15  ·  TypeScript  ·  Tailwind CSS        │
└─────────────────────────────┬──────────────────────────────┘
                              │ REST / JSON
┌─────────────────────────────▼──────────────────────────────┐
│                   FastAPI  (Python 3.11)                   │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌─────────┐  │
│  │  Resume  │  │ Interview │  │   RAG    │  │ Report  │  │
│  │  Parser  │  │  Engine   │  │ Pipeline │  │   Gen   │  │
│  └────┬─────┘  └─────┬─────┘  └────┬─────┘  └────┬────┘  │
│       │              │             │              │        │
│  ┌────▼──────────────▼─────────────▼──────────────▼────┐  │
│  │             Service Layer (dependency injection)     │  │
│  └────┬──────────────────────────────────┬─────────────┘  │
│       │                                  │                 │
│  ┌────▼────┐                       ┌─────▼──────┐         │
│  │PostgreSQL│                      │  ChromaDB  │         │
│  │(SQLAlch.) │                     │ (Embeddings)│        │
│  └──────────┘                      └────────────┘         │
│                                                            │
│             Claude Sonnet (via Anthropic API)              │
└────────────────────────────────────────────────────────────┘
```

---

## Folder Structure

```
candidate-screening-system/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── resume.py        # POST /resume/upload
│   │   │   │   ├── interview.py     # POST /interview/start · GET /question/{id} · POST /answer
│   │   │   │   └── report.py        # GET /report/{session_id}
│   │   │   └── schemas.py           # Pydantic request/response models
│   │   ├── database/
│   │   │   ├── base.py              # SQLAlchemy DeclarativeBase
│   │   │   └── session.py           # Async engine + session factory
│   │   ├── models/                  # ORM models
│   │   │   ├── candidate.py
│   │   │   ├── session.py
│   │   │   ├── question.py
│   │   │   ├── answer.py
│   │   │   └── report.py
│   │   ├── rag/
│   │   │   ├── embeddings.py        # sentence-transformers singleton
│   │   │   ├── vector_store.py      # ChromaDB wrapper (per-role collections)
│   │   │   ├── ingestion.py         # PDF → chunks → embeddings → ChromaDB
│   │   │   └── retriever.py         # Query builder + top-k retrieval
│   │   ├── resume_parser/
│   │   │   ├── extractor.py         # PDF text → LLM → structured JSON
│   │   │   └── schemas.py           # ParsedResume Pydantic model
│   │   ├── interview/
│   │   │   ├── prompts.py           # All LLM prompt templates
│   │   │   ├── question_generator.py
│   │   │   └── report_generator.py
│   │   ├── services/                # Business logic (service layer)
│   │   │   ├── candidate_service.py
│   │   │   ├── interview_service.py
│   │   │   └── report_service.py
│   │   ├── utils/
│   │   │   ├── config.py            # Pydantic Settings (env vars)
│   │   │   └── logger.py
│   │   └── main.py                  # FastAPI app + lifespan
│   ├── knowledge_base/              # Drop PDFs here (by role subfolder)
│   │   ├── ai_ml/
│   │   ├── backend/
│   │   ├── frontend/
│   │   ├── fullstack/
│   │   ├── devops/
│   │   └── data_science/
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx           # Root layout + header
│   │   │   ├── page.tsx             # Candidate page (upload + role select)
│   │   │   ├── interview/page.tsx   # Live interview
│   │   │   └── results/page.tsx     # Final report
│   │   ├── lib/
│   │   │   ├── api.ts               # Typed fetch wrappers
│   │   │   └── utils.ts             # cn(), difficultyColor(), etc.
│   │   ├── hooks/
│   │   │   └── useInterview.ts      # Interview state machine hook
│   │   └── types/index.ts           # Shared TypeScript types
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── next.config.ts
│   └── Dockerfile
│
└── docker-compose.yml
```

---

## Database Schema

```sql
candidates
  id            UUID PK
  name          VARCHAR(255)
  email         VARCHAR(255) UNIQUE
  resume_path   VARCHAR(512)
  parsed_resume TEXT (JSON)
  created_at    TIMESTAMPTZ

interview_sessions
  id                   UUID PK
  candidate_id         UUID FK → candidates
  selected_role        VARCHAR(128)
  status               ENUM (pending|active|completed|aborted)
  current_question_idx VARCHAR(8)
  start_time           TIMESTAMPTZ
  end_time             TIMESTAMPTZ

questions
  id            UUID PK
  session_id    UUID FK → interview_sessions
  question_text TEXT
  source_context TEXT        -- RAG chunks used
  topic_area    VARCHAR(256)
  difficulty    ENUM (easy|medium|hard)
  order_index   INT
  is_follow_up  VARCHAR(1)

answers
  id            UUID PK
  question_id   UUID FK → questions UNIQUE
  answer_text   TEXT
  quality_score FLOAT         -- 0.0–1.0, set during report generation
  submitted_at  TIMESTAMPTZ

reports
  id             UUID PK
  session_id     UUID FK → interview_sessions UNIQUE
  summary        TEXT
  strengths      TEXT (JSON array)
  weaknesses     TEXT (JSON array)
  overall_score  FLOAT
  recommendation VARCHAR(64)  -- Hire | Maybe | Reject
  generated_at   TIMESTAMPTZ
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/resume/upload` | Upload PDF résumé (multipart form) |
| `POST` | `/api/v1/interview/start` | Start a session for a candidate + role |
| `GET`  | `/api/v1/interview/question/{session_id}` | Get next question (generates on demand) |
| `POST` | `/api/v1/interview/answer` | Submit an answer |
| `POST` | `/api/v1/interview/end/{session_id}` | Mark session complete |
| `GET`  | `/api/v1/report/{session_id}` | Generate (or retrieve) the full report |
| `GET`  | `/health` | Health check |

---

## RAG Pipeline

```
knowledge_base/ai_ml/*.pdf
        │
        ▼  pdfplumber
   raw text
        │
        ▼  512-word chunks, 64-word overlap
   text chunks
        │
        ▼  sentence-transformers (all-MiniLM-L6-v2)
   384-dim embeddings
        │
        ▼  ChromaDB (cosine similarity, per-role collection)
   vector store
        │
   At interview time:
        │
        ▼  build query from resume skills + role
   query embedding
        │
        ▼  top-k similarity search
   retrieved chunks
        │
        ▼  Claude Sonnet prompt
   personalised interview question
```

**Why these choices:**
- **ChromaDB** — embedded (no separate server in dev), scales to a hosted instance in prod. Alternatives: Pinecone (managed, cost), Weaviate (more features, heavier).
- **all-MiniLM-L6-v2** — fast, low memory, excellent semantic retrieval for technical text. Alternative: `text-embedding-3-small` (OpenAI, better quality, adds API cost/latency).
- **512-word chunks / 64 overlap** — balances context granularity vs. token budget. Too small = fragmented; too large = diluted relevance score.

---

## Quick Start (Local)

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 16 running on `localhost:5432`
- Anthropic API key

### Backend

```bash
cd backend

# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — set ANTHROPIC_API_KEY and DATABASE_URL

# 4. (Optional) Ingest knowledge base PDFs
#    Drop PDFs into knowledge_base/ai_ml/, knowledge_base/backend/, etc.
python -m app.rag.ingestion

# 5. Start the API server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### Docker (Full Stack)

```bash
# Copy and edit backend env
cp backend/.env.example backend/.env
# Set ANTHROPIC_API_KEY in backend/.env

docker compose up --build
```

---

## Knowledge Base Setup

Place role-specific PDFs into the corresponding subfolder:

```
backend/knowledge_base/
├── ai_ml/          ← ML textbooks, papers, TensorFlow/PyTorch docs
├── backend/        ← System design, DB internals, API design guides
├── frontend/       ← React, browser internals, accessibility
├── fullstack/      ← Mix of backend + frontend
├── devops/         ← Kubernetes, CI/CD, observability
└── data_science/   ← Statistics, pandas, SQL, visualisation
```

Then run the ingestion script once:

```bash
cd backend
python -m app.rag.ingestion
```

The embeddings persist in `backend/chroma_db/` between restarts.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://...` | Async PostgreSQL connection string |
| `ANTHROPIC_API_KEY` | — | **Required.** Your Anthropic API key |
| `LLM_MODEL` | `claude-sonnet-4-6` | Claude model to use |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence-transformers model |
| `QUESTIONS_PER_SESSION` | `8` | Number of questions per interview |
| `TOP_K_CHUNKS` | `5` | RAG chunks retrieved per question |
| `UPLOAD_DIR` | `uploads` | Directory to store uploaded PDFs |
| `DEBUG` | `false` | Enable SQLAlchemy query logging |

---

## Running Tests

```bash
cd backend
pip install pytest pytest-asyncio
pytest tests/ -v
```

---

## Technology Decisions

| Decision | Choice | Why | Alternative considered |
|---|---|---|---|
| **LLM** | Claude Sonnet (Anthropic) | Superior instruction-following, consistent JSON output | GPT-4o (higher cost), Gemini (worse structured output) |
| **Embeddings** | all-MiniLM-L6-v2 | Local, fast, 384-dim, excellent for technical text | OpenAI text-embedding-3-small (API cost per call) |
| **Vector DB** | ChromaDB (persistent) | Zero-infra in dev, same API for prod HttpClient | Pinecone (managed cost), pgvector (fewer index options) |
| **ORM** | SQLAlchemy 2 async | Native async, type-safe, battle-tested | Tortoise ORM (less ecosystem), SQLModel (thin wrapper) |
| **API** | FastAPI | Auto OpenAPI docs, Pydantic v2, native async | Django REST (heavier), Flask (no async) |
| **Frontend** | Next.js 15 App Router | RSC, built-in routing, Turbopack | Vite + React (more config), Remix (smaller ecosystem) |
| **CSS** | Tailwind CSS | Utility-first, zero runtime | CSS Modules (verbose), Styled Components (runtime cost) |

---

## Production Considerations

- **Auth**: Add JWT middleware (FastAPI-Users or custom) before exposing APIs publicly.
- **Rate limiting**: Add `slowapi` or an API gateway in front of question generation (LLM calls are expensive).
- **ChromaDB**: Switch `PersistentClient` → `HttpClient` pointing at a dedicated ChromaDB container.
- **Alembic**: Replace `create_all` in lifespan with proper Alembic migrations (`alembic upgrade head`).
- **Observability**: Add OpenTelemetry traces around LLM calls and DB queries.
- **File storage**: Replace local `uploads/` with S3 or Azure Blob for horizontal scaling.
