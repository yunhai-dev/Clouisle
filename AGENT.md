# Clouisle Project Status & Architecture

## 📅 Last Updated: 2025-12-21

## 🏗 Architecture Overview

**Type**: Monorepo Full-Stack Application
**Root Path**: `/Users/yunhai/Documents/CodeData/Project/Clouisle`

The project is structured as a monorepo separating the backend API and the frontend client, orchestrated by Docker for infrastructure services.

### Directory Structure
- `backend/`: Python FastAPI application
- `frontend/`: Next.js application
- `deploy/docker-compose.yml`: Infrastructure services (PostgreSQL, Redis)

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

## ⚙️ Backend Development Guidelines

**Migration & Cold Start Data**:
Database migrations and initial data seeding (cold start) must be implemented to execute automatically upon backend startup. The application should check for the existence of necessary schemas and data; if missing, it must automatically apply migrations and populate the initial dataset.

**Unified API Response Format**:
All API endpoints **must** return responses in the following unified format:

```json
{
  "code": 0,        // 0 = success, non-zero = error code
  "data": {...},    // Response payload (can be null)
  "msg": "success"  // Human-readable message
}
```

For **paginated** responses, the `data` field should follow this structure:

```json
{
  "code": 0,
  "data": {
    "items": [...],     // List of items
    "total": 100,       // Total count
    "page": 1,          // Current page number
    "page_size": 20     // Items per page
  },
  "msg": "success"
}
```

Use the helper functions from `app/schemas/response.py`:
- `success(data=..., msg="...")` for successful responses
- `error(code=..., msg="...", data=...)` for error responses
- `Response[T]` generic type for type hints
- `PageData[T]` for paginated data structures

**Response Code Standards**:
Use `ResponseCode` enum from `app/schemas/response.py` for all error codes:

| 范围 | 类别 | 枚举值示例 |
|------|------|-----------|
| 0 | 成功 | `SUCCESS` |
| 1000-1999 | 通用错误 | `UNKNOWN_ERROR`, `VALIDATION_ERROR` |
| 2000-2999 | 认证错误 | `UNAUTHORIZED`, `INVALID_TOKEN`, `TOKEN_EXPIRED`, `INVALID_CREDENTIALS`, `INACTIVE_USER` |
| 3000-3999 | 权限错误 | `PERMISSION_DENIED`, `INSUFFICIENT_PRIVILEGES` |
| 4000-4999 | 资源错误 | `NOT_FOUND`, `USER_NOT_FOUND`, `ROLE_NOT_FOUND`, `PERMISSION_NOT_FOUND` |
| 5000-5999 | 业务逻辑错误 | `USERNAME_EXISTS`, `EMAIL_EXISTS`, `CANNOT_DELETE_SYSTEM_ROLE`, `ROLE_IN_USE` |

**Usage Example**:
```python
from app.schemas.response import ResponseCode, success, error

# 成功响应
return success(data=user, msg="User created")

# 错误响应（自动获取默认消息）
return error(code=ResponseCode.USERNAME_EXISTS)

# 错误响应（自定义消息）
return error(code=ResponseCode.NOT_FOUND, msg="User not found")
```

**Adding New Codes**: When adding new error scenarios, add the code to `ResponseCode` enum and its default message to `CODE_MESSAGES` dict.

## 📚 Design Documents

- [RBAC Permission System Design](docs/design/RBAC_SPEC.md)
- [Backend API Documentation](docs/api/BACKEND_API.md)

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
docker-compose -f deploy/docker-compose.yml up -d
```
