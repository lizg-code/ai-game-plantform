# 系统架构设计

## 1. 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户浏览器                                │
│                   http://localhost:3000                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Nuxt 3 前端服务                               │
│              Vue 3 + Tailwind CSS + SSR                         │
│                                                                 │
│  pages/          components/         composables/               │
│  ├─ index.vue    ├─ GameCard.vue     ├─ useAuth.ts              │
│  ├─ login.vue    ├─ ChatInput.vue    └─ useApi.ts               │
│  ├─ register.vue ├─ AgentLog.vue                                │
│  ├─ create.vue   ├─ GamePreview.vue                             │
│  └─ play/[id]    └─ Navbar.vue                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │ REST API (JSON)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI 后端服务                               │
│                http://localhost:8000                             │
│                                                                 │
│  routers/        services/           utils/                     │
│  ├─ auth.py      ├─ auth_service.py  ├─ security.py (JWT/bcrypt)│
│  ├─ games.py     ├─ agent_service.py └─ deps.py (依赖注入)       │
│  └─ upload.py    └─ storage_service.py                          │
│                                                                 │
│  models/         schemas/                                       │
│  ├─ User         ├─ AuthSchema                                  │
│  ├─ Game         └─ GameSchema                                  │
│  ├─ AgentLog                                                    │
│  └─ Material                                                    │
└────────┬───────────────────┬───────────────────┬────────────────┘
         │                   │                   │
         ▼                   ▼                   ▼
   ┌──────────┐      ┌──────────┐       ┌──────────────┐
   │  MySQL   │      │  MinIO   │       │  Mimo LLM    │
   │  :3306   │      │  :9000   │       │  API         │
   │  数据库   │      │  对象存储  │       │  (OpenAI兼容) │
   └──────────┘      └──────────┘       └──────────────┘
```

## 2. 技术栈

| 层 | 技术 | 版本 | 用途 |
|---|------|------|------|
| 前端框架 | Nuxt 3 | 3.13+ | Vue 3 全栈框架，SSR 支持 |
| UI 样式 | Tailwind CSS | 3.x | 原子化 CSS，快速搭建 UI |
| 后端框架 | FastAPI | 0.115+ | 异步 Python Web 框架 |
| ORM | SQLAlchemy | 2.0+ | Python SQL 工具包和 ORM |
| 数据库 | MySQL | 8.0 | 关系型数据库 |
| 对象存储 | MinIO | latest | S3 兼容的对象存储 |
| 认证 | JWT + bcrypt | - | 无状态认证 + 密码哈希 |
| LLM 服务 | Mimo API | mimo-v2.5-pro | 小米大模型，OpenAI 兼容格式 |
| 容器化 | Docker Compose | 3.8 | 一键启动全部依赖 |

## 3. 部署架构

### 开发环境

```
docker-compose up -d mysql minio minio-init   # 启动依赖
cd backend && uvicorn app.main:app --reload    # 启动后端
cd frontend && npm run dev                     # 启动前端
```

### 生产环境（扩展方向）

```
                    ┌─────────┐
                    │  Nginx  │
                    │ 反向代理  │
                    └────┬────┘
                    ┌────┴────┐
              ┌─────┴───┐ ┌──┴──────┐
              │ Frontend │ │ Backend │
              │ (Nuxt)   │ │(FastAPI)│
              └──────────┘ └────┬────┘
                          ┌─────┴─────┐
                    ┌─────┴──┐  ┌─────┴──┐
                    │ MySQL  │  │ MinIO/ │
                    │ (RDS)  │  │  S3    │
                    └────────┘  └────────┘
```

## 4. 目录结构

```
ai-game-platform/
├── docker-compose.yml          # 容器编排
├── .env                        # 环境变量（不提交）
├── .env.example                # 环境变量模板
├── .gitignore
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── main.py             # 入口
│   │   ├── config.py           # 配置管理
│   │   ├── database.py         # 数据库连接
│   │   ├── models/             # ORM 模型
│   │   ├── schemas/            # Pydantic 模型
│   │   ├── routers/            # API 路由
│   │   ├── services/           # 业务逻辑
│   │   └── utils/              # 工具函数
│   ├── alembic/                # 数据库迁移
│   ├── seed.py                 # 种子数据
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # Nuxt 3 前端
│   ├── pages/                  # 页面路由
│   ├── components/             # 通用组件
│   ├── composables/            # 组合式函数
│   ├── middleware/             # 路由中间件
│   ├── layouts/                # 布局
│   ├── nuxt.config.ts
│   ├── package.json
│   └── Dockerfile
└── docs/                       # 系统文档
```
