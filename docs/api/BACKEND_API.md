# Clouisle Backend API 文档

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API Prefix**: `/api/v1`
- **认证方式**: Bearer Token (JWT)

---

## 统一响应格式

所有接口返回统一格式：

```json
{
  "code": 0,        // 0=成功, 非0=错误码
  "data": {...},    // 响应数据
  "msg": "success"  // 消息
}
```

### 分页响应

```json
{
  "code": 0,
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20
  },
  "msg": "success"
}
```

---

## 认证接口 (Auth)

### 登录

获取访问令牌。

- **URL**: `POST /api/v1/login/access-token`
- **Content-Type**: `application/x-www-form-urlencoded`
- **认证**: 不需要

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/login/access-token" \
  -d "username=admin&password=admin123"
```

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
  },
  "msg": "Login successful"
}
```

---

### 注册

注册新用户。系统第一个注册的用户将自动成为超级管理员。

- **URL**: `POST /api/v1/register`
- **Content-Type**: `application/json`
- **认证**: 不需要

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| email | string | 是 | 邮箱 |
| password | string | 是 | 密码 |

**请求示例**:
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "password123"
}
```

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "newuser",
    "email": "newuser@example.com",
    "is_active": true,
    "is_superuser": false,
    "roles": []
  },
  "msg": "Registration successful"
}
```

**特殊说明**: 
- 第一个注册的用户将自动获得 `is_superuser=true` 和 `Super Admin` 角色

---

## 用户接口 (Users)

### 获取当前用户信息

- **URL**: `GET /api/v1/users/me`
- **认证**: 需要

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "admin",
    "email": "admin@example.com",
    "is_active": true,
    "is_superuser": true,
    "created_at": "2025-12-22T10:00:00Z",
    "roles": [
      {
        "id": "...",
        "name": "Super Admin",
        "permissions": [
          {"id": "...", "code": "*", "scope": "system"}
        ]
      }
    ]
  },
  "msg": "success"
}
```

---

### 获取用户列表

- **URL**: `GET /api/v1/users/`
- **认证**: 需要
- **权限**: `user:read`

**查询参数**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | int | 1 | 页码 |
| page_size | int | 20 | 每页数量 |

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "items": [...],
    "total": 50,
    "page": 1,
    "page_size": 20
  },
  "msg": "success"
}
```

---

### 获取指定用户

- **URL**: `GET /api/v1/users/{user_id}`
- **认证**: 需要
- **权限**: `user:read`

---

### 创建用户

- **URL**: `POST /api/v1/users/`
- **认证**: 需要
- **权限**: `user:create`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| email | string | 是 | 邮箱 |
| password | string | 是 | 密码 |
| is_active | bool | 否 | 是否激活，默认 true |
| is_superuser | bool | 否 | 是否超管，默认 false |

---

### 更新用户

- **URL**: `PUT /api/v1/users/{user_id}`
- **认证**: 需要
- **权限**: `user:update`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| email | string | 否 | 邮箱 |
| password | string | 否 | 新密码 |
| is_active | bool | 否 | 是否激活 |
| roles | string[] | 否 | 角色名称列表 |

---

### 删除用户

- **URL**: `DELETE /api/v1/users/{user_id}`
- **认证**: 需要
- **权限**: `user:delete`

**限制**: 超级管理员用户不可删除

---

## 角色接口 (Roles)

### 获取角色列表

- **URL**: `GET /api/v1/roles/`
- **认证**: 需要

**查询参数**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | int | 1 | 页码 |
| page_size | int | 50 | 每页数量 |

---

### 获取指定角色

- **URL**: `GET /api/v1/roles/{role_id}`
- **认证**: 需要

---

### 创建角色

- **URL**: `POST /api/v1/roles/`
- **认证**: 需要
- **权限**: `user:manage`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 角色名称 |
| description | string | 否 | 描述 |
| permissions | string[] | 否 | 权限代码列表 |

**请求示例**:
```json
{
  "name": "Editor",
  "description": "Can edit content",
  "permissions": ["user:read", "user:update"]
}
```

---

### 更新角色

- **URL**: `PUT /api/v1/roles/{role_id}`
- **认证**: 需要
- **权限**: `user:manage`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 否 | 角色名称 |
| description | string | 否 | 描述 |

**限制**: 系统角色不可修改

---

### 更新角色权限

- **URL**: `PUT /api/v1/roles/{role_id}/permissions`
- **认证**: 需要
- **权限**: `user:manage`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| permissions | string[] | 是 | 权限代码列表（全量替换） |

**请求示例**:
```json
{
  "permissions": ["user:read", "user:create", "user:update"]
}
```

**限制**: 系统角色权限不可修改

---

### 删除角色

- **URL**: `DELETE /api/v1/roles/{role_id}`
- **认证**: 需要
- **权限**: `user:manage`

**限制**: 
- 系统角色不可删除
- 已分配给用户的角色不可删除

---

## 权限接口 (Permissions)

### 获取权限列表

- **URL**: `GET /api/v1/permissions/`
- **认证**: 需要

**查询参数**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | int | 1 | 页码 |
| page_size | int | 50 | 每页数量 |
| scope | string | - | 按 scope 筛选 |

---

### 获取指定权限

- **URL**: `GET /api/v1/permissions/{permission_id}`
- **认证**: 需要

---

### 创建权限

- **URL**: `POST /api/v1/permissions/`
- **认证**: 需要
- **权限**: `user:manage`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | 是 | 权限代码，格式: `scope:action` |
| scope | string | 是 | 权限范围 |
| description | string | 否 | 描述 |

**请求示例**:
```json
{
  "code": "kb:create",
  "scope": "kb",
  "description": "Create knowledge base"
}
```

---

### 更新权限

- **URL**: `PUT /api/v1/permissions/{permission_id}`
- **认证**: 需要
- **权限**: `user:manage`

---

### 删除权限

- **URL**: `DELETE /api/v1/permissions/{permission_id}`
- **认证**: 需要
- **权限**: `user:manage`

**限制**: 通配符权限 `*` 不可删除

---

## 内置数据

### 系统权限

| Code | Scope | 说明 |
|------|-------|------|
| `*` | system | 所有权限（超级管理员） |
| `user:read` | user | 读取用户 |
| `user:create` | user | 创建用户 |
| `user:update` | user | 更新用户 |
| `user:delete` | user | 删除用户 |
| `user:manage` | user | 管理用户、角色、权限 |

### 系统角色

| 名称 | 权限 | 说明 |
|------|------|------|
| Super Admin | `*` | 完全控制，拥有所有权限 |
| Viewer | `user:read` | 只读访问 |

---

## 错误响应

```json
{
  "detail": "Error message here"
}
```

### 常见 HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 400 | 请求错误（参数错误、业务规则违反） |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 认证使用

在需要认证的接口中，添加 Header:

```
Authorization: Bearer <access_token>
```

示例:
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```
