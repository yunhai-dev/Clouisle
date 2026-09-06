# Memories API

The Memories API provides endpoints for accessing, reviewing, and managing user-specific long-term conversational memory extracted across agent sessions.

---

## Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/memories` | List conversation memories for the authenticated user |
| `GET` | `/api/v1/memories/{memory_id}` | Get details of a specific memory item |
| `PUT` | `/api/v1/memories/{memory_id}` | Update or correct a memory item |
| `DELETE` | `/api/v1/memories/{memory_id}` | Delete a memory item |

---

## List Memories

Retrieve long-term memory facts extracted for the current authenticated user and team.

```http
GET /api/v1/memories?page=1&page_size=20&search=preference HTTP/1.1
Authorization: Bearer <token>
```

### Response (`200 OK`)

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "mem_01j7abcde",
        "user_id": "usr_123",
        "content": "User prefers concise Python code snippets using async/await syntax.",
        "importance": 0.85,
        "source_agent_id": "agent_456",
        "created_at": "2026-03-02T08:30:00Z",
        "updated_at": "2026-03-02T08:30:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20
  }
}
```

---

## Update Memory

```http
PUT /api/v1/memories/mem_01j7abcde HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "User prefers concise TypeScript/Node.js snippets using standard ES modules.",
  "importance": 0.9
}
```

---

## Delete Memory

```http
DELETE /api/v1/memories/mem_01j7abcde HTTP/1.1
Authorization: Bearer <token>
```

### Response (`200 OK`)

```json
{
  "code": 0,
  "message": "Memory deleted successfully"
}
```
