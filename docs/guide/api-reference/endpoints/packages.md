# Packages API

The Packages API provides endpoints for inspecting supported Python libraries and requesting dynamic package installations inside the isolated Bubblewrap code sandbox environment.

---

## Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/packages` | List available sandbox packages and pre-installed dependencies |
| `POST` | `/api/v1/packages/install` | Request package installation into the sandbox environment |

---

## List Packages

Retrieve pre-installed and cached ecosystem libraries supported in the sandbox.

```http
GET /api/v1/packages?search=pandas HTTP/1.1
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
        "name": "pandas",
        "version": "2.2.2",
        "summary": "Powerful data structures for data analysis and statistics",
        "installed": true
      },
      {
        "name": "numpy",
        "version": "2.0.0",
        "summary": "Fundamental package for array computing with Python",
        "installed": true
      }
    ]
  }
}
```

---

## Install Package

Request dynamic installation of a Python package into the sandbox worker environment.

```http
POST /api/v1/packages/install HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "package_name": "seaborn",
  "version": "0.13.2"
}
```

### Response (`200 OK`)

```json
{
  "code": 0,
  "message": "Package installation triggered",
  "data": {
    "package_name": "seaborn",
    "version": "0.13.2",
    "status": "installed"
  }
}
```
