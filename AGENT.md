# Clouisle Project Status & Architecture

## 📅 Last Updated: 2025-12-25

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
- **UI Library**: shadcn/ui (base-vega style, uses @base-ui/react)
- **Theme**: next-themes
- **i18n**: next-intl (cookie-based locale)

### Frontend Component Structure

```
frontend/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # 认证路由组
│   │   └── login/
│   │       ├── page.tsx
│   │       └── _components/      # 登录页面专属组件
│   ├── (dashboard)/              # 后台管理路由组 (管理员)
│   │   ├── layout.tsx            # SidebarProvider + SidebarInset
│   │   ├── users/
│   │   │   ├── page.tsx
│   │   │   └── _components/      # Users 页面专属组件
│   │   │       ├── user-table.tsx
│   │   │       ├── user-header.tsx
│   │   │       └── index.ts      # 统一导出
│   │   ├── roles/
│   │   │   ├── page.tsx
│   │   │   └── _components/
│   │   ├── teams/
│   │   │   ├── page.tsx
│   │   │   └── _components/
│   │   └── knowledge-bases/      # 知识库管理 (后台)
│   │       ├── [id]/
│   │       │   ├── search/       # 搜索测试页
│   │       │   │   └── _components/
│   │       │   └── _components/
│   │       └── _components/
│   ├── (platform)/               # 中台路由组 (普通用户)
│   │   ├── layout.tsx            # PlatformHeader (64px) + flex main
│   │   └── app/
│   │       └── kb/               # 知识库 (中台)
│   │           └── [id]/
│   │               ├── search/   # 搜索测试页
│   │               │   └── _components/
│   │               └── _components/
├── components/                   # 全局共享组件
│   ├── ui/                       # shadcn/ui 基础组件（不修改）
│   ├── layout/                   # 布局组件 (header, sidebar)
│   └── providers/                # Context Providers
├── hooks/                        # 自定义 Hooks
├── lib/                          # 工具函数
└── messages/                     # 翻译文件 (en.json, zh.json)
```

### 中台与后台隔离规范

项目包含两套独立的用户界面：

| 维度 | 后台 (Dashboard) | 中台 (Platform) |
|------|------------------|-----------------|
| 路由组 | `(dashboard)/` | `(platform)/` |
| 目标用户 | 管理员 | 普通用户 |
| 布局组件 | `SidebarProvider` + `SidebarInset` | `PlatformHeader` (64px) + flex main |
| 圆角处理 | `SidebarInset` 自带 `rounded-xl`，底部固定栏需加 `md:rounded-b-xl` | 无特殊圆角 |
| 路由前缀 | `/users`, `/knowledge-bases` | `/app/kb` |

**隔离原则**：
1. **组件不共享**: 中台和后台的页面组件必须分别放在各自的 `_components/` 目录，**禁止跨路由组引用**
2. **功能同步**: 当两边有相同功能时（如搜索测试），需要分别实现，修改一边时需**同步修改另一边**
3. **样式隔离**: 布局不同导致样式细节不同，不要复制粘贴后忘记调整
4. **API 共享**: `lib/api/` 下的 API 客户端可以共享，类型定义也共享

**布局差异导致的样式注意事项**：

```tsx
// 后台: SidebarInset 提供 h-full，子组件可用 flex h-full
<div className="flex h-full flex-col">
  <div className="flex-1 min-h-0 overflow-auto">...</div>
  <div className="flex-none md:rounded-b-xl">底部栏</div>
</div>

// 中台: layout 的 main 没有高度约束，需要显式计算
<div className="flex flex-col" style={{ height: 'calc(100vh - 64px)' }}>
  <div className="flex-1 min-h-0 overflow-auto">...</div>
  <div className="sticky bottom-0">底部栏</div>
</div>
```

**常见问题排查**：
- 后台底部栏被 SidebarInset 圆角遮挡 → 添加 `md:rounded-b-xl`
- 中台 `h-full` 或 `flex-1` 无效 → 使用 `calc(100vh - 64px)` 显式高度
- sticky 定位失效 → 检查父容器是否有 `overflow: hidden` 或缺少高度约束

**组件化规范**：
- 每个路由目录下创建 `_components/` 文件夹存放页面专属组件
- 使用下划线前缀确保 Next.js 不将其视为路由
- 组件文件使用 kebab-case: `user-table.tsx`
- 组件命名使用 PascalCase: `UserTable`
- 每个 `_components/` 目录需要 `index.ts` 统一导出

**base-ui 注意事项**：
- shadcn/ui base-vega 样式基于 @base-ui/react，**不支持 `asChild` prop**
- TooltipTrigger、DropdownMenuTrigger 等需要使用 `render` prop 渲染自定义元素
- **禁止使用原生 `confirm()`**，必须使用 shadcn 的 `AlertDialog` 组件
- **禁止使用原生 `title` 属性作为提示**，必须使用 shadcn 的 `Tooltip` 组件
- **Select 组件在 Dialog/Modal 中使用时**，必须添加 `alignItemWithTrigger={false}` 属性，否则下拉框会遮盖触发器：
  ```tsx
  <SelectContent side="bottom" alignItemWithTrigger={false}>
    {/* items */}
  </SelectContent>
  ```

**Hydration 处理**：
- 依赖 localStorage 的状态需要使用 `mounted` 状态避免服务端/客户端不匹配
- 参考 `hooks/use-settings.tsx` 的实现模式

**输入处理规范**：
- **中文 IME 处理**: 监听键盘事件时必须检测 `e.nativeEvent.isComposing`，避免输入法组合状态下回车误触发
  ```tsx
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.nativeEvent.isComposing) return  // 中文输入法组合中，忽略
    if (e.key === 'Enter') handleSubmit()
  }
  ```
- **小数输入**: number 类型 input 在某些浏览器无法输入小数点，改用 text + inputMode="decimal" + 正则验证
  ```tsx
  const [value, setValue] = useState('0')
  <Input
    type="text"
    inputMode="decimal"
    value={value}
    onChange={(e) => {
      if (/^\d*\.?\d*$/.test(e.target.value)) setValue(e.target.value)
    }}
  />
  ```

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

## 🌍 Multi-language Support (i18n)

**This project requires full multi-language support for both backend and frontend.**

### Supported Languages
- **English (en)**: Default language
- **Chinese (zh)**: 中文

### Backend i18n
All user-facing messages in the backend API **must** be internationalized:

1. **Response messages**: Use `msg_key` parameter instead of hardcoded strings
2. **Error messages**: Use `t()` function for HTTPException details
3. **Language detection**: Automatically from `Accept-Language` or `X-Language` header

**Implementation**: `app/core/i18n.py`

### Frontend i18n
Frontend should also support language switching (implementation pending):
- UI text and labels
- Error messages
- Date/time formatting

### Adding New Messages
When adding new user-facing text:
1. **Backend**: Add translation key to `TRANSLATIONS` dict in `app/core/i18n.py`
2. **Frontend**: (TBD) Add to frontend i18n configuration

**Important**: Never hardcode user-facing strings. Always use i18n functions.

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

**表单验证错误响应**:
当请求参数验证失败时（Pydantic 验证错误），返回字段级别的错误信息，便于前端精确展示：

```json
{
  "code": 1001,
  "data": {
    "errors": {
      "email": "value is not a valid email address",
      "username": "String should have at least 3 characters"
    }
  },
  "msg": "验证错误"
}
```

- `code`: 固定为 `1001` (VALIDATION_ERROR)
- `data.errors`: 字段名到错误消息的映射，key 为字段名，value 为错误描述
- 前端应遍历 `data.errors` 将错误显示在对应的表单输入框下方
- 嵌套字段使用点号分隔，如 `user.email`

**前端处理示例**:
```typescript
// API 响应类型
interface ValidationErrorResponse {
  code: number
  data: {
    errors: Record<string, string | string[]>
  }
  msg: string
}

// 表单状态
const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})

// 处理提交
try {
  await api.post('/register', formData)
} catch (err) {
  if (err.code === 1001 && err.data?.errors) {
    setFieldErrors(err.data.errors)
  }
}

// 表单渲染
<Input id="email" error={fieldErrors.email} />
```

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

**BusinessError 异常规范**:
在后端接口中抛出业务错误时，**必须**使用 `BusinessError` 异常类，而不是直接使用 `HTTPException`。这样可以确保所有错误都遵循统一的响应格式。

```python
from app.schemas.response import ResponseCode, BusinessError

# ❌ 不推荐：直接使用 HTTPException
raise HTTPException(status_code=404, detail="User not found")

# ✅ 推荐：使用 BusinessError
raise BusinessError(
    code=ResponseCode.USER_NOT_FOUND,
    msg_key="user_not_found",
    status_code=404,
)
```

**BusinessError 参数说明**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `code` | `ResponseCode \| int` | 否 | 业务错误码，默认 `UNKNOWN_ERROR` |
| `msg` | `str` | 否 | 直接指定消息（优先级最高） |
| `msg_key` | `str` | 否 | i18n 翻译 key |
| `status_code` | `int` | 否 | HTTP 状态码，默认 400 |
| `data` | `Any` | 否 | 附加数据 |
| `**kwargs` | | 否 | 传递给 `t()` 函数的格式化参数 |

**使用示例**:
```python
from app.schemas.response import ResponseCode, BusinessError

# 基本用法
raise BusinessError(
    code=ResponseCode.USER_NOT_FOUND,
    msg_key="user_not_found",
    status_code=404,
)

# 带格式化参数
raise BusinessError(
    code=ResponseCode.PERMISSION_DENIED,
    msg_key="operation_not_permitted",
    status_code=403,
    permission="user:manage",  # 传递给 t("operation_not_permitted", permission="user:manage")
)

# 直接指定消息（不使用 i18n）
raise BusinessError(
    code=ResponseCode.VALIDATION_ERROR,
    msg="Custom error message",
    status_code=400,
)

# 带附加数据
raise BusinessError(
    code=ResponseCode.VALIDATION_ERROR,
    msg_key="validation_error",
    data={"field": "email", "reason": "invalid format"},
)
```

**重要规则**:
1. 所有业务错误必须使用 `BusinessError`
2. 优先使用 `msg_key` 配合 i18n，而不是硬编码 `msg`
3. 为每种错误场景使用对应的 `ResponseCode`
4. 正确设置 `status_code`（404 用于资源不存在，403 用于权限不足等）

**Internationalization (i18n)**:
All user-facing messages **must** support internationalization. Use the i18n module from `app/core/i18n.py`:

```python
from app.core.i18n import t
from app.schemas.response import success

# 使用翻译key的成功响应
return success(data=user, msg_key="user_created")

# HTTPException中使用翻译
raise HTTPException(status_code=400, detail=t("username_exists"))

# 带参数的翻译
raise HTTPException(status_code=400, detail=t("role_in_use", count=5))
```

**Language Detection**: The language is automatically detected from the `Accept-Language` or `X-Language` request header. Supported languages: `en` (English), `zh` (Chinese).

**Adding New Translations**: Add new message keys to the `TRANSLATIONS` dict in `app/core/i18n.py`:
```python
TRANSLATIONS = {
    "new_message_key": {
        "en": "English message",
        "zh": "中文消息",
    },
}
```

## 📚 Design Documents

- [RBAC Permission System Design](docs/design/RBAC_SPEC.md)
- [Backend API Documentation](docs/api/BACKEND_API.md)

---

## � Team Model

The project uses a **Team** model for resource isolation and collaboration.

> ⚠️ **TODO: Resource Isolation**
> 
> All business resources (knowledge bases, documents, conversations, etc.) **MUST** be associated with a Team for data isolation. When implementing new resource types:
> 1. Add `team_id` foreign key to the model
> 2. Filter queries by team membership
> 3. Validate team access in API endpoints
> 4. Consider team-level permissions for fine-grained access control

### Data Models
- `Team`: Team entity (name, description, avatar_url, owner, is_default)
- `TeamMember`: User-Team relationship with roles (owner, admin, member, viewer)

### Team Member Roles
| Role | Description |
|------|-------------|
| `owner` | Creator, full control, can delete team or transfer ownership |
| `admin` | Can manage members |
| `member` | Normal member |
| `viewer` | Read-only access |

### Key APIs
- `GET /api/v1/teams/my` - Get user's teams with roles
- `POST /api/v1/teams/` - Create team (creator becomes owner)
- `POST /api/v1/teams/{id}/members` - Add member
- `POST /api/v1/teams/{id}/leave` - Leave team
- `POST /api/v1/teams/{id}/transfer-ownership` - Transfer ownership

### Important Notes
- Team owner cannot leave; must transfer ownership first
- Default team (`is_default=True`) cannot be deleted
- Future resources (knowledge bases, etc.) should be associated with teams for data isolation

---

## 📊 Usage Tracking (Token 用量追踪)

项目支持团队级别的 Token 用量追踪和配额管理。

### 核心组件

| 文件 | 说明 |
|------|------|
| `backend/app/services/usage_tracker.py` | 用量追踪服务 |
| `backend/app/tasks/usage.py` | Celery 定时任务（用量重置） |
| `backend/app/llm/manager.py` | 模型管理器（含团队级方法） |

### 数据模型 (TeamModel)

`TeamModel` 模型包含以下用量相关字段：

| 字段 | 说明 |
|------|------|
| `daily_token_limit` | 每日 Token 配额（null 表示无限制） |
| `monthly_token_limit` | 每月 Token 配额 |
| `daily_request_limit` | 每日请求次数配额 |
| `monthly_request_limit` | 每月请求次数配额 |
| `daily_tokens_used` | 当日已用 Token 数 |
| `monthly_tokens_used` | 当月已用 Token 数 |
| `daily_requests_used` | 当日请求次数 |
| `monthly_requests_used` | 当月请求次数 |
| `daily_reset_at` | 每日用量重置时间 |
| `monthly_reset_at` | 每月用量重置时间 |

### UsageTracker 服务

```python
from app.services.usage_tracker import usage_tracker, QuotaExceededError

# 检查配额是否足够
team_model = await usage_tracker.check_quota(
    team_id="team-uuid",
    model_id="model-uuid",
    tokens_needed=1000,  # 可选，预估需要的 token
)

# 记录用量（不检查配额）
await usage_tracker.record_usage(
    team_id="team-uuid",
    model_id="model-uuid",
    tokens_used=1500,
    request_count=1,
)

# 检查配额并记录用量（推荐）
await usage_tracker.check_and_record_usage(
    team_id="team-uuid",
    model_id="model-uuid",
    tokens_used=1500,
)

# 获取用量统计
stats = await usage_tracker.get_usage_stats(
    team_id="team-uuid",
    model_id="model-uuid",
)
# 返回: {
#   "daily_tokens_used": 1500,
#   "daily_token_limit": 100000,
#   "daily_token_percent": 1.5,
#   ...
# }
```

### 团队级 LLM 调用

`ModelManager` 提供了带用量追踪的团队级方法：

```python
from app.llm import model_manager, QuotaExceededError

# 团队级 Chat（自动追踪用量 + 配额检查）
try:
    response = await model_manager.team_chat(
        team_id="team-uuid",
        messages=[{"role": "user", "content": "Hello!"}],
        model_id="openai/gpt-4o",  # 或 model UUID
    )
except QuotaExceededError as e:
    print(f"配额超限: {e.quota_type}")  # daily_token, monthly_token, etc.

# 团队级流式调用
async for chunk in model_manager.team_chat_stream(
    team_id="team-uuid",
    messages=[...],
    model_id="openai/gpt-4o",
):
    print(chunk.delta.content, end="")

# 团队级 Embedding
vectors = await model_manager.team_embed(
    team_id="team-uuid",
    texts=["text1", "text2"],
    model_id="openai/text-embedding-3-small",
)
```

### 定时任务

用量重置由 Celery Beat 定时任务自动执行：

| 任务 | 执行时间 | 说明 |
|------|----------|------|
| `tasks.reset_daily_usage` | 每天 00:00 | 重置所有团队模型的每日用量 |
| `tasks.reset_monthly_usage` | 每月 1 日 00:05 | 重置所有团队模型的每月用量 |

启动 Celery Beat：
```bash
cd backend
celery -A app.core.celery beat --loglevel=info
```

### 配额超限错误

当配额超限时，会抛出 `QuotaExceededError`，包含以下信息：

| 属性 | 说明 |
|------|------|
| `quota_type` | 超限类型：`daily_token`, `monthly_token`, `daily_request`, `monthly_request` |
| `team_id` | 团队 ID |
| `model` | 模型 ID |
| `code` | 错误码：`quota_exceeded` |

前端应根据 `quota_type` 显示相应的错误提示。

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

---

## ✅ Pre-commit Checklist

**Before committing code, ensure all checks pass:**

### Backend Checks
```bash
cd backend

# Linting & Formatting (Ruff)
uv run ruff check .
uv run ruff format --check .

# Static Type Checking (mypy)
uv run mypy app/
```

### Frontend Checks
```bash
cd frontend

# ESLint
bun run lint

# Build Check (TypeScript & Next.js)
bun run build
```

### Fix Commands
```bash
# Auto-fix ruff issues
cd backend && uv run ruff check . --fix && uv run ruff format .

# Auto-fix ESLint issues
cd frontend && bun run lint --fix
```

**Important**: All checks must pass before pushing to the repository.
