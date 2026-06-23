# API 接口文档

## 基础信息

- Base URL: `http://localhost:8000`
- 认证方式: Bearer Token (JWT)
- Content-Type: application/json
- Swagger 文档: http://localhost:8000/docs

---

## 认证接口 (Auth)

### POST /api/auth/register — 邮箱注册

**请求体:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "nickname": "Player1"
}
```

**响应 (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**错误:**
- 400: `{"detail": "Email already registered"}`

---

### POST /api/auth/login — 邮箱登录

**请求体:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**响应 (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**错误:**
- 401: `{"detail": "Invalid email or password"}`

---

### GET /api/auth/me — 获取当前用户

**Headers:** `Authorization: Bearer <token>`

**响应 (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "nickname": "Player1",
  "avatar_url": "",
  "auth_provider": "local",
  "created_at": "2026-06-23T12:00:00"
}
```

**错误:**
- 401: `{"detail": "Not authenticated"}`

---

## 游戏接口 (Games)

### GET /api/games — 获取已发布游戏列表

**Query 参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| tag | string | 否 | 按标签筛选 |
| page | int | 否 | 页码，默认 1 |
| size | int | 否 | 每页数量，默认 20 |

**响应 (200):**
```json
{
  "total": 3,
  "games": [
    {
      "id": 1,
      "title": "Dragon's Quest",
      "description": "An epic text adventure...",
      "cover_url": "https://picsum.photos/seed/dragon/400/300",
      "author_id": 1,
      "author_nickname": "Demo Creator",
      "tags": ["adventure", "text-based", "fantasy"],
      "status": "published",
      "remote_url": "http://localhost:9000/games/abc123.html",
      "game_type": "text_adventure",
      "created_at": "2026-06-23T12:00:00",
      "updated_at": "2026-06-23T12:00:00"
    }
  ]
}
```

---

### GET /api/games/{game_id} — 获取单个游戏详情

**响应 (200):** 同单个游戏对象

**错误:**
- 404: `{"detail": "Game not found"}`

---

### POST /api/games/generate — 触发 Agent 生成

**Headers:** `Authorization: Bearer <token>`

**请求体:**
```json
{
  "user_prompt": "A memory card matching game with emojis",
  "materials": ["http://example.com/ref.png"]
}
```

**响应 (200):**
```json
{
  "game_id": 42,
  "status": "generating",
  "message": "Game generation started. Poll /api/games/{id}/status for progress."
}
```

---

### GET /api/games/{game_id}/status — 查询生成进度

**响应 (200):**
```json
{
  "game_id": 42,
  "status": "draft",
  "remote_url": "http://localhost:9000/games/abc123.html",
  "logs": [
    {
      "id": 1,
      "game_id": 42,
      "step_name": "creative_analysis",
      "step_order": 1,
      "status": "success",
      "input_data": {},
      "output_data": {"gameplay": "...", "style": "..."},
      "error_message": "",
      "started_at": "2026-06-23T12:00:01",
      "finished_at": "2026-06-23T12:00:05"
    },
    {
      "id": 2,
      "game_id": 42,
      "step_name": "game_design",
      "step_order": 2,
      "status": "success",
      "input_data": {},
      "output_data": {"title": "...", "gameplay_rules": [...]},
      "error_message": "",
      "started_at": "2026-06-23T12:00:05",
      "finished_at": "2026-06-23T12:00:10"
    },
    {
      "id": 3,
      "game_id": 42,
      "step_name": "code_generation",
      "step_order": 3,
      "status": "success",
      "input_data": {},
      "output_data": {"html_length": 4523},
      "error_message": "",
      "started_at": "2026-06-23T12:00:10",
      "finished_at": "2026-06-23T12:00:20"
    },
    {
      "id": 4,
      "game_id": 42,
      "step_name": "upload",
      "step_order": 4,
      "status": "success",
      "input_data": {},
      "output_data": {"remote_url": "http://localhost:9000/games/abc123.html"},
      "error_message": "",
      "started_at": "2026-06-23T12:00:20",
      "finished_at": "2026-06-23T12:00:21"
    }
  ]
}
```

---

### POST /api/games/{game_id}/publish — 发布游戏

**Headers:** `Authorization: Bearer <token>`

**前置条件:** 游戏 status 必须为 "draft"

**响应 (200):** 返回更新后的游戏对象

**错误:**
- 403: `{"detail": "Not the game author"}`
- 400: `{"detail": "Cannot publish game with status 'generating'"}`

---

## 文件上传接口 (Upload)

### POST /api/upload — 上传文件

**Headers:** `Authorization: Bearer <token>`

**请求体:** `multipart/form-data`
| 字段 | 类型 | 说明 |
|------|------|------|
| file | File | 图片/视频/文档 |
| game_id | int | 可选，关联游戏 ID |

**限制:**
- 文件大小: 最大 20MB
- 允许类型: jpeg, png, gif, webp, mp4, webm, pdf, txt

**响应 (200):**
```json
{
  "file_url": "http://localhost:9000/games/materials/abc123.png",
  "file_name": "screenshot.png",
  "file_type": "image/png"
}
```

---

## 系统接口

### GET / — API 信息

### GET /health — 健康检查

---

## 状态码说明

| 状态码 | 含义 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证（token 缺失或过期） |
| 403 | 无权限（非作者尝试发布） |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 游戏状态流转

```
draft → generating → draft (生成完成) → published
                    → failed (生成失败)
```
