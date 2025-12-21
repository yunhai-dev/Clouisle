# Clouisle Project Status & Architecture

## 📅 Last Updated: 2025-12-21

## 🏗 Architecture Overview

**Type**: Monorepo Full-Stack Application
**Root Path**: `/Users/yunhai/Documents/CodeData/Project/Clouisle`

The project is structured as a monorepo separating the backend API and the frontend client, orchestrated by Docker for infrastructure services.

### Directory Structure
- `backend/`: Python FastAPI application
- `frontend/`: Next.js application
- `docker-compose.yml`: Infrastructure services (PostgreSQL, Redis)

---

## 🛠 Environment & Tooling

### Backend (`/backend`)
- **Language**: Python 3.13
- **Package Manager**: `uv`
- **Framework**: FastAPI

### Frontend (`/frontend`)
- **Runtime/Package Manager**: `bun`
- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Database**: PostgreSQL 16 (with `pgvector` extension)
- **Cache/Queue**: Redis

---

## 📦 Dependencies

### Backend (Python)
Defined in `backend/pyproject.toml`

**Core:**
- `fastapi`: Web framework
- `uvicorn[standard]`: ASGI server
- `tortoise-orm`: Async ORM
- `asyncpg`: PostgreSQL driver
- `celery`: Distributed task queue
- `redis`: Redis client (for Celery backend/broker)
- `pydantic-settings`: Configuration management
- `python-multipart`: File upload support

**Dev Tools:**
- `pytest`: Testing
- `ruff`: Linting & Formatting
- `mypy`: Static Type Checking

### Frontend (TypeScript)
Defined in `frontend/package.json`

**Core:**
- `next`: React framework
- `react` / `react-dom`: UI library
- `shadcn-ui` (via `shadcn` CLI): UI Component library
- `reactflow`: Node-based graph library
- `ai-elements`: AI UI components
- `lucide-react`: Icons
- `tailwindcss`: Utility-first CSS framework

---

## 🌐 Documentation Guidelines

**Multi-language Synchronization**:
When modifying project documentation (especially `README.md`), you **must** synchronously update the corresponding content in other language versions (e.g., `docs/README_zh-CN.md`) to maintain consistency.

---

## 📝 Recent Actions Log

1.  **Project Initialization**:
    - Created `backend` and `frontend` directories.
    - Moved initial `main.py` to `backend/app/main.py`.

2.  **Backend Setup**:
    - Configured `pyproject.toml` with `uv`.
    - Established standard FastAPI directory structure (`app/api`, `app/core`, `app/models`, etc.).

3.  **Frontend Setup**:
    - Initialized Next.js app using `bun create next-app`.
    - Integrated `shadcn-ui`, `reactflow`, and `ai-elements`.
    - Fixed directory nesting issues during initialization.

4.  **Infrastructure**:
    - Created `docker-compose.yml` for PostgreSQL (pgvector) and Redis.

5.  **Configuration**:
    - Updated `.gitignore` to include Python, Node.js, Bun, and Docker ignore patterns.

---

## 🚀 Quick Start Commands

### Backend
```bash
cd backend
uv sync
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
bun install
bun dev
```

### Infrastructure
```bash
docker-compose up -d
```
