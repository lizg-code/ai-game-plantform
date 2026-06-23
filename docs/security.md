# 安全方案文档

## 1. 认证方案

### JWT (JSON Web Token)

- **算法:** HS256
- **有效期:** 1440 分钟 (24 小时)
- **Payload:** `{ "sub": "user_id", "email": "user@example.com", "exp": timestamp }`
- **存储:** 前端 localStorage
- **传递:** HTTP Header `Authorization: Bearer <token>`

### 密码安全

- **哈希算法:** bcrypt
- **盐值:** 自动生成 (bcrypt gensalt)
- **存储:** 仅存储哈希值，不明文存储密码

```
注册: password → bcrypt.hashpw → password_hash (存入数据库)
登录: password + password_hash → bcrypt.checkpw → True/False
```

## 2. CORS 策略

```python
allow_origins = [
    "http://localhost:3000",    # 前端开发服务器
    "http://127.0.0.1:3000",
]
allow_methods = ["*"]
allow_headers = ["*"]
allow_credentials = True
```

生产环境应限制 `allow_origins` 为实际域名。

## 3. 文件上传安全

### 类型限制
仅允许以下 MIME 类型:
- 图片: `image/jpeg`, `image/png`, `image/gif`, `image/webp`
- 视频: `video/mp4`, `video/webm`
- 文档: `application/pdf`, `text/plain`

### 大小限制
- 最大 20MB

### 文件名处理
- 使用 UUID 重命名，防止路径遍历攻击
- 保留原始扩展名

```python
unique_name = f"{folder}/{uuid.uuid4().hex}.{ext}"
```

## 4. API 安全

### 认证中间件
- 使用 FastAPI 依赖注入 (`Depends(get_current_user)`)
- 受保护的路由自动验证 JWT
- 未认证请求返回 401

### 权限控制
- 游戏发布: 仅作者本人可发布 (403 if not author)
- 游戏状态: 仅 "draft" 状态可发布 (400 if wrong status)

### 输入验证
- Pydantic Schema 自动验证请求体
- 类型不匹配返回 422

## 5. 数据库安全

### SQL 注入防护
- SQLAlchemy ORM 使用参数化查询
- 不拼接原始 SQL 字符串

### 连接安全
- 使用连接池 (`pool_size=10, max_overflow=20`)
- `pool_pre_ping=True` 自动检测断连

## 6. 对象存储安全

### MinIO 配置
- 开发环境使用默认凭证 (`minioadmin/minioadmin`)
- 生产环境应使用强密码 + IAM 策略

### 访问控制
- 游戏文件 bucket 设置为公开下载 (`mc anonymous set download`)
- 上传需要认证（通过后端 API 代理）

## 7. 已知安全限制

| 问题 | 当前状态 | 生产环境建议 |
|------|---------|-------------|
| JWT 无刷新机制 | token 过期后需重新登录 | 添加 refresh token |
| 无 rate limiting | 无限制 | 添加限流中间件 |
| MinIO 默认凭证 | 开发环境 | 更换强密码 |
| CORS 全开放 | 开发环境 | 限制为实际域名 |
| 无 HTTPS | 开发环境 | 配置 SSL 证书 |
| 无 CSP 头 | 未配置 | 添加 Content-Security-Policy |
