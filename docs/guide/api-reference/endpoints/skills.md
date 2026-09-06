# Skills API

The Skills API provides endpoints for managing custom team skills, code implementations, metadata, and asset files.

---

## Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/skills` | List skills (paginated, team-filtered) |
| `POST` | `/api/v1/skills` | Create a new skill |
| `GET` | `/api/v1/skills/{skill_id}` | Get skill details |
| `PUT` | `/api/v1/skills/{skill_id}` | Update skill configuration |
| `DELETE` | `/api/v1/skills/{skill_id}` | Delete a skill |
| `POST` | `/api/v1/skills/{skill_id}/files` | Upload skill asset/resource files |
| `GET` | `/api/v1/skills/{skill_id}/files/{filename}` | Retrieve a skill asset file |
| `DELETE` | `/api/v1/skills/{skill_id}/files/{filename}` | Delete a skill asset file |

---

## List Skills

Retrieve a paginated list of skills accessible to your team.

```http
GET /api/v1/skills?page=1&page_size=20&team_id=team_123&search=python HTTP/1.1
Authorization: Bearer <token>
```

### Query Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `page` | `integer` | No | Page number (default: 1) |
| `page_size` | `integer` | No | Items per page (default: 20, max: 100) |
| `team_id` | `string` | No | Filter by team ID |
| `search` | `string` | No | Filter by skill name or description |
| `category` | `string` | No | Filter by category |

### Response (`200 OK`)

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "skill_01h8abcde",
        "team_id": "team_123",
        "name": "data_analysis_skill",
        "display_name": "Data Analysis Skill",
        "description": "Analyzes tabular CSV datasets and generates statistical charts",
        "category": "analysis",
        "version": "1.0.0",
        "created_at": "2026-03-01T12:00:00Z",
        "updated_at": "2026-03-01T12:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20
  }
}
```

---

## Create Skill

```http
POST /api/v1/skills HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "team_id": "team_123",
  "name": "data_analysis_skill",
  "display_name": "Data Analysis Skill",
  "description": "Analyzes tabular CSV datasets",
  "category": "analysis",
  "code": "def run(params):\n    return {'status': 'ok'}"
}
```

---

## Upload Skill Asset Files

Upload auxiliary scripts, templates, or dataset definitions associated with a skill.

```http
POST /api/v1/skills/skill_01h8abcde/files HTTP/1.1
Authorization: Bearer <token>
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="template.py"
Content-Type: text/x-python

# Custom helper code
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```
