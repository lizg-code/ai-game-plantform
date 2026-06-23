# 🎮 AI Game Platform

AI Native 互动游戏平台 — 玩家可以发现并游玩由社区发布的互动游戏；创作者可以通过自然语言创意与 AI Agent 协作生成可发布、可游玩的互动游戏。

## ✨ 功能特性

- **🔐 用户认证** — 邮箱注册/登录，JWT 无状态认证
- **🏠 游戏发现** — 首页展示已发布游戏，支持标签筛选
- **🤖 AI 创作** — 输入创意文本，Agent 自动生成可运行游戏
- **📤 一键发布** — 预览满意后发布到首页
- **🎮 即开即玩** — 点击游戏卡片直接在浏览器中游玩

## 🛠 技术栈

| 层 | 技术 |
|---|------|
| 前端 | Nuxt 3 + Vue 3 + Tailwind CSS |
| 后端 | FastAPI + SQLAlchemy + Alembic |
| 数据库 | MySQL 8.0 |
| 对象存储 | MinIO (S3 兼容) |
| LLM | Mimo API (mimo-v2.5-pro) |
| 部署 | Docker Compose |

## 🚀 快速启动

### 前置要求

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### 1. 克隆项目

```bash
git clone https://github.com/lizg-code/ai-game-plantform.git
cd ai-game-plantform
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入你的 MIMO_API_KEY
```

### 3. 启动依赖服务

```bash
docker-compose up -d mysql minio minio-init
```

### 4. 启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端 API 文档: http://localhost:8000/docs

### 5. 初始化种子数据

```bash
cd backend
python seed.py
```

这会创建:
- 演示账号: `demo@aigame.com` / `demo123456`
- 3 个示例游戏（文字冒险、记忆翻牌、太空射击）

### 6. 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:3000

### 一条命令启动全部 (Docker)

```bash
docker-compose up -d
```

## 📁 项目结构

```
├── docker-compose.yml
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── main.py          # 入口
│   │   ├── config.py        # 配置
│   │   ├── database.py      # 数据库连接
│   │   ├── models/          # ORM 模型 (User, Game, AgentLog, Material)
│   │   ├── schemas/         # Pydantic 请求/响应模型
│   │   ├── routers/         # API 路由 (auth, games, upload)
│   │   ├── services/        # 业务逻辑 (auth, agent, storage)
│   │   └── utils/           # 工具 (JWT, bcrypt, 依赖注入)
│   ├── alembic/             # 数据库迁移
│   ├── seed.py              # 种子数据脚本
│   └── requirements.txt
├── frontend/                # Nuxt 3 前端
│   ├── pages/               # 页面 (Home, Login, Register, Create, Play)
│   ├── components/          # 组件 (GameCard, ChatInput, AgentLog, GamePreview, Navbar)
│   ├── composables/         # 组合式函数 (useAuth, useApi)
│   └── middleware/           # 路由守卫
└── docs/                    # 系统文档
```

## 🔌 核心 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 邮箱注册 |
| POST | /api/auth/login | 邮箱登录 |
| GET | /api/auth/me | 获取当前用户 |
| GET | /api/games | 游戏列表（支持标签筛选） |
| GET | /api/games/{id} | 游戏详情 |
| POST | /api/games/generate | 触发 Agent 生成 |
| GET | /api/games/{id}/status | 查询生成进度 |
| POST | /api/games/{id}/publish | 发布游戏 |
| POST | /api/upload | 上传文件 |

完整 API 文档: http://localhost:8000/docs

## 🤖 Agent 工作流

Agent 采用 4 步流水线架构：

1. **Creative Analysis** — 解析用户创意为结构化 JSON
2. **Game Design** — 生成游戏设计文档
3. **Code Generation** — 生成可运行的 HTML 游戏
4. **Upload** — 上传到 MinIO 对象存储

每步独立执行，状态实时记录到数据库，前端通过轮询展示进度。

详见 [docs/agent-workflow.md](docs/agent-workflow.md)

## 📝 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| MYSQL_* | MySQL 连接配置 | localhost:3306 |
| MINIO_* | MinIO 对象存储配置 | localhost:9000 |
| MIMO_API_KEY | LLM API Key | (必填) |
| MIMO_BASE_URL | LLM API 地址 | https://token-plan-cn.xiaomimimo.com/v1 |
| LLM_MODEL | LLM 模型名 | mimo-v2.5-pro |
| JWT_SECRET_KEY | JWT 签名密钥 | (建议修改) |

## 📄 文档

- [系统架构](docs/architecture.md)
- [API 接口](docs/api.md)
- [数据模型](docs/data-model.md)
- [Agent 工作流](docs/agent-workflow.md)
- [安全方案](docs/security.md)

## 📊 完成度说明

| 功能 | 状态 | 备注 |
|------|------|------|
| 邮箱注册/登录 | ✅ 完成 | bcrypt + JWT |
| 第三方登录 (Google/GitHub) | 🎨 UI 完成 | mock 设计，未真实接入 |
| Home 首页游戏列表 | ✅ 完成 | 从数据库加载，支持标签筛选 |
| Create 多模态输入 | ✅ 完成 | 文本 + 文件上传 |
| Agent 生成链路 | ✅ 完成 | 4 步 LLM 调用，日志可见 |
| Play 动态加载 | ✅ 完成 | iframe 加载 MinIO 远端文件 |
| 发布流程 | ✅ 完成 | Create → Publish → Home 闭环 |
| 系统设计文档 | ✅ 完成 | 5 份文档 |
| 种子数据 | ✅ 完成 | 3 个示例游戏 |

### 如果再给 1 周，会迭代：

1. 添加 Agent 代码验证步骤（检查生成的 HTML 是否可运行）
2. 实现真实 Google/GitHub OAuth 登录
3. 添加游戏评论和评分系统
4. 添加游戏收藏功能
5. 实现 LLM streaming 实时展示生成过程
6. 添加 rate limiting 和更完善的错误处理
7. 部署到云服务器并配置 CI/CD
