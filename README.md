# InterviewGPT 

An end-to-end, AI-powered mock interview platform that simulates real-world hiring loops. Using LLMs, vector search, automatic speech recognition (ASR), and structured evaluation techniques, InterviewGPT evaluates candidate resumes, conducts adaptive oral/technical/coding interviews, and provides comprehensive performance analytics.

---

## Key Features

- ** AI-Powered Resume Parser**: Extracts structured profiles (skills, experience, projects, education) from PDF and DOCX uploads using PDFPlumber/PyPDF2 and LLM-driven schema parsing.
- ** Multi-Disciplinary Interview Tracks**: Configurable mock sessions tailored to:
  - **HR & Behavioral**: Assessed using the **STAR Method** (Situation, Task, Action, Result).
  - **Technical Q&A**: Knowledge-based questions mapped to resume skills and targeted roles.
  - **Data Structures & Algorithms (DSA)**: Coding environment with syntax check and complexity analysis.
  - **System Design**: Architecture and scalability discussion.
  - **Project Discussion**: Deep dive into resume projects.
- ** Speech-to-Text (ASR) Integration**: Voice answer support transcribed in real-time using **Faster Whisper**.
- ** Semantic Retrieval & RAG**: Vectorizes parsed resume data and stores it in **ChromaDB** to enable hyper-personalized, context-aware interview questions.
- ** Professional Grading & Analytics**: Generates detailed candidate feedback reports, covering communication skills, technical capabilities, improvement areas, and custom learning paths, complete with downloadable **PDF Reports**.
- ** Dockerized Orchestration**: Streamlined local setup utilizing `docker-compose` for the frontend, backend, database, and vector store.

##  Detailed Tech Stack

### Frontend Architecture
- **Framework**: **Next.js (React 19)** (App Router) — Provides server-side rendering, optimized page routing, and high performance for the candidate dashboards.
- **Styling & Animations**:
  - **Tailwind CSS (v4)** — For responsive utility-first layout styling.
  - **Framer Motion** — Provides micro-interactions and smooth transitions during voice conversations and coding questions.
- **State Management & Client State**: **TanStack React Query** — Manages client-side cache, query state, asynchronous API polling, and database sync.
- **Components & Icons**: **Shadcn UI**, **Base UI**, and **Lucide React** — Standardized design systems and modern icon libraries.

### Backend Architecture
- **Web Framework**: **FastAPI** (Python 3.11+) — Asynchronous HTTP REST framework with automatic Swagger generation, fast processing times, and low latency.
- **Database & Data Relational Mapping**:
  - **SQLAlchemy (Async)** — For robust Pythonic database interactions.
  - **Alembic** — Handles backend schema migrations.
  - **Prisma** — Provides a centralized database schema (`prisma/schema.prisma`) for relational sync.
  - **PostgreSQL** — Main transactional database storing user accounts, interview sessions, questions, evaluations, and grading reports.
- **Agentic & Vector Retrieval Flow**:
  - **LangChain & LangGraph** — Orchestrates the multi-turn conversational interview state machine, prompts, and memory retention.
  - **ChromaDB** — Vector database storing embedded resume fragments to enable Retrieval-Augmented Generation (RAG) during interviews.
- **Ingestion & Processing Engines**:
  - **Faster Whisper** — Transcribes oral responses in real-time.
  - **PDFPlumber / PyPDF2 / python-docx** — Parses raw text from user uploaded resumes.
  - **WeasyPrint** — Compiles structured evaluations into print-ready PDF reports.

---

##  Project Structure in Detail

```text
├── backend/                             # FastAPI Backend Service
│   ├── admin/                           # Endpoints and services for system administrator dashboards
│   ├── analytics/                       # Core metrics calculation and reporting engines
│   ├── auth/                            # JWT token generation, routing dependencies, and hashing rules
│   │   ├── dependencies.py              # User dependency verification and JWT authentication checks
│   │   └── router.py                    # Login and registration controllers
│   ├── database/                        # Database engine setups and model mappings
│   │   ├── models.py                    # SQLAlchemy database tables (User, Resume, Interview, etc.)
│   │   └── session.py                   # Async session makers and local context provider
│   ├── evaluation/                      # Multi-disciplinary grading modules
│   │   ├── behavioral.py                # STAR methodology feedback scoring
│   │   ├── coding.py                    # Code submission compilation, correctness and efficiency analysis
│   │   └── technical.py                 # Core domain expertise evaluation logic
│   ├── interviews/                      # Interview process logic and session routing
│   │   ├── router.py                    # REST entry points for interview setup, progression, and answers
│   │   ├── schemas.py                   # Pydantic schemas validating payload contracts
│   │   └── service.py                   # Core interview status machine transitions
│   ├── llm/                             # Language Model configurations and LLM agent steps
│   │   ├── agent.py                     # LangGraph workflow compiler and agentic decision trees
│   │   ├── chains.py                    # Basic prompts helper chains
│   │   └── prompts.py                   # Platform instructions and grading rubric prompts
│   ├── rag/                             # Vector search and RAG indexing functions
│   │   ├── chunking.py                  # Sentence/word splitter logic for PDF indexing
│   │   ├── embeddings.py                # Local/Ollama embedding creation interfaces
│   │   └── retriever.py                 # ChromaDB search handlers
│   ├── resumes/                         # User resume parsing controllers
│   │   ├── parser.py                    # Extractors utilizing PDFPlumber and python-docx
│   │   ├── router.py                    # Uploading and document deletion endpoints
│   │   └── service.py                   # Chroma DB sync and document storage processes
│   ├── speech/                          # Speech to Text interfaces
│   │   ├── router.py                    # Audio upload endpoint processing audio bytes
│   │   └── transcriber.py               # Transcribing audio inputs using Faster Whisper
│   ├── users/                           # User profile managers
│   ├── main.py                          # Main application runner configuration (CORS, app lifespan, routes)
│   └── requirements.txt                 # Absolute listing of python libraries
│
├── frontend/                            # Next.js Frontend App
│   ├── public/                          # Static icons, vector graphics, and layouts
│   ├── src/                             # Main UI application files
│   │   ├── app/                         # App router file layouts
│   │   │   ├── (dashboard)/             # Protected layout views
│   │   │   │   ├── admin/               # Administrator operations pages
│   │   │   │   ├── analytics/           # Candidate capability heatmaps and charts
│   │   │   │   ├── dashboard/           # Home dashboard displaying resumes and active sessions
│   │   │   │   ├── interviews/          # Active interview panel (mock screens, voice and code editors)
│   │   │   │   ├── reports/             # Rendered feedback reports and grade summaries
│   │   │   │   └── settings/            # Account profiles and API configurations
│   │   │   ├── login/                   # User login UI
│   │   │   ├── register/                # User signup UI
│   │   │   ├── globals.css              # Global styles and tailwind imports
│   │   │   └── page.tsx                 # Landing marketing index page
│   │   ├── components/                  # Reusable UI elements (dialogs, file upload dropzones, graphs)
│   │   ├── hooks/                       # Custom hooks (e.g. web audio API capture, context wrappers)
│   │   ├── lib/                         # Utilities (e.g. class mergers, axios connectors)
│   │   └── services/                    # API client layer wrapping backend routes
│   └── package.json                     # Frontend build configurations, scripts, and libraries
│
├── prisma/                              # Unified Schema Storage
│   └── schema.prisma                    # Database definitions shared between the stack components
│
├── docker-compose.yml                   # Top level configuration to orchestrate services locally
└── README.md                            # High level documentation overview
```

---

## Getting Started

### Prerequisites
Make sure you have the following installed on your machine:
- [Docker & Docker Compose](https://www.docker.com/products/docker-desktop/)
- [Node.js](https://nodejs.org/) (v18+) & [npm](https://www.npmjs.com/)
- [Python 3.11+](https://www.python.org/downloads/) (if running services locally without Docker)
- [Ollama](https://ollama.com/) (for local LLM inference)

---

### Run with Docker Compose (Recommended)

1. **Clone the repository** and navigate to the project directory:
   ```bash
   git clone <repository-url>
   cd ai-interviewer
   ```

2. **Configure Environment Variables**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Open the `.env` file and customize settings (e.g., your database credentials, Ollama configurations, and keys).

3. **Start the containers**:
   ```bash
   docker compose up --build
   ```

4. **Access the Services**:
   - **Frontend**: [http://localhost:3000](http://localhost:3000)
   - **Backend API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **ChromaDB Web API**: [http://localhost:8100](http://localhost:8100)

---

### Local Development Setup

If you prefer to run services individually without Docker:

#### 1. Setup PostgreSQL & ChromaDB
Ensure you have running instances of PostgreSQL and ChromaDB. You can start just the database services using Docker Compose:
```bash
docker compose up -d db chromadb
```

#### 2. Run Backend Setup
1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run migrations & start development server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

#### 3. Run Frontend Setup
1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the Next.js development server:
   ```bash
   npm run dev
   ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser.

---

##  Database Migrations

This project uses Prisma to manage schemas and database clients:

- **Generate Client**:
  ```bash
  npx prisma generate
  ```
- **Run Migrations**:
  ```bash
  npx prisma migrate dev --name init
  ```

---

## Contributing

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add some amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

---

## Developer
Hitesh Umesh
