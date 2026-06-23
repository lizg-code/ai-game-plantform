# 数据模型文档

## ER 图

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│    users     │       │    games     │       │ agent_logs   │
├──────────────┤       ├──────────────┤       ├──────────────┤
│ id       (PK)│◄──┐   │ id       (PK)│◄──┐   │ id       (PK)│
│ email        │   │   │ title        │   │   │ game_id  (FK)│──┐
│ password_hash│   │   │ description  │   │   │ step_name    │  │
│ nickname     │   │   │ cover_url    │   │   │ step_order   │  │
│ avatar_url   │   ├───│ author_id(FK)│   ├───│ status       │  │
│ auth_provider│   │   │ tags (JSON)  │   │   │ input_data   │  │
│ created_at   │   │   │ status       │   │   │ output_data  │  │
│ updated_at   │   │   │ remote_url   │   │   │ error_message│  │
└──────────────┘   │   │ game_type    │   │   │ started_at   │  │
                   │   │ design_doc   │   │   │ finished_at  │  │
                   │   │ user_prompt  │   │   └──────────────┘  │
                   │   │ created_at   │   │                     │
                   │   │ updated_at   │   │   ┌──────────────┐  │
                   │   └──────────────┘   │   │  materials   │  │
                   │                      │   ├──────────────┤  │
                   │                      │   │ id       (PK)│  │
                   │                      │   │ game_id  (FK)│──┘
                   │                      │   │ file_name    │
                   │                      │   │ file_url     │
                   │                      │   │ file_type    │
                   │                      │   │ uploaded_at  │
                   │                      │   └──────────────┘
                   │                      │
                   └──────────────────────┘
                   (1:N)                (1:N)
```

## 表结构详情

### users 表 — 用户

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 用户 ID |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 邮箱（登录凭证） |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt 密码哈希 |
| nickname | VARCHAR(100) | DEFAULT '' | 显示昵称 |
| avatar_url | VARCHAR(500) | DEFAULT '' | 头像 URL |
| auth_provider | ENUM('local','google','github') | DEFAULT 'local' | 注册方式 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW() | 更新时间 |

**索引:**
- `email` — 唯一索引，用于登录查询

---

### games 表 — 游戏

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 游戏 ID |
| title | VARCHAR(200) | NOT NULL | 游戏标题 |
| description | TEXT | DEFAULT '' | 游戏简介 |
| cover_url | VARCHAR(500) | DEFAULT '' | 封面图 URL |
| author_id | INT | FK → users.id | 作者 ID |
| tags | JSON | DEFAULT [] | 标签数组 |
| status | ENUM | DEFAULT 'draft' | 状态: draft/generating/published/failed |
| remote_url | VARCHAR(500) | DEFAULT '' | MinIO 上的游戏 HTML 地址 |
| game_type | VARCHAR(50) | DEFAULT '' | 游戏类型 |
| design_doc | JSON | DEFAULT {} | Agent 生成的设计文档 |
| user_prompt | TEXT | DEFAULT '' | 用户原始创意输入 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW() | 更新时间 |

**状态流转:**
```
draft → generating → draft (成功) → published
                   → failed (失败)
```

**索引:**
- `author_id` — 外键索引
- `status` — 用于筛选已发布游戏

---

### agent_logs 表 — Agent 步骤日志

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 日志 ID |
| game_id | INT | FK → games.id | 关联游戏 |
| step_name | VARCHAR(100) | NOT NULL | 步骤名称 |
| step_order | INT | NOT NULL | 步骤序号 (1-4) |
| status | ENUM | DEFAULT 'pending' | 状态: pending/running/success/failed |
| input_data | JSON | DEFAULT {} | 步骤输入 |
| output_data | JSON | DEFAULT {} | 步骤输出 |
| error_message | TEXT | DEFAULT '' | 错误信息 |
| started_at | DATETIME | NULL | 开始时间 |
| finished_at | DATETIME | NULL | 完成时间 |

**步骤名称:**
- `creative_analysis` — 创意分析
- `game_design` — 游戏设计
- `code_generation` — 代码生成
- `upload` — 上传产物

---

### materials 表 — 上传素材

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 素材 ID |
| game_id | INT | FK → games.id | 关联游戏 |
| file_name | VARCHAR(255) | NOT NULL | 原始文件名 |
| file_url | VARCHAR(500) | NOT NULL | MinIO 地址 |
| file_type | VARCHAR(50) | DEFAULT '' | MIME 类型 |
| uploaded_at | DATETIME | DEFAULT NOW() | 上传时间 |

---

## JSON 字段说明

### games.tags
```json
["adventure", "text-based", "fantasy"]
```

### games.design_doc
```json
{
  "title": "Dragon's Quest",
  "description": "...",
  "ui_layout": "...",
  "gameplay_rules": ["rule1", "rule2"],
  "interaction_model": "click",
  "scoring": "..."
}
```

### agent_logs.input_data / output_data
各步骤的输入输出均为 JSON 对象，具体内容参见 [agent-workflow.md](./agent-workflow.md)
