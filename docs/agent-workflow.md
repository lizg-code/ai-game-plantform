# Agent 工作流文档

## 概述

Agent 模块负责将用户的自然语言创意转化为可运行的互动游戏。采用**多步 LLM 调用**架构，每步独立执行并记录日志。

## 工作流图

```
用户输入创意文本 + 素材文件
        │
        ▼
  POST /api/games/generate
  创建 Game 记录 (status=generating)
  创建 4 条 AgentLog (status=pending)
        │
        ▼
  Background Task 启动
        │
        ▼
┌─────────────────────────────────────┐
│ Step 1: Creative Analysis           │
│ 角色: 游戏设计分析师                   │
│ 输入: 用户创意文本                     │
│ 输出: 结构化 JSON (玩法/风格/类型)      │
│ LLM: Mimo mimo-v2.5-pro             │
│ 耗时: ~3-5s                          │
└──────────────┬──────────────────────┘
               │ success → 继续
               │ failed → 终止，status=failed
               ▼
┌─────────────────────────────────────┐
│ Step 2: Game Design                 │
│ 角色: 游戏设计师                      │
│ 输入: Step 1 的 JSON                 │
│ 输出: 游戏设计文档 (标题/规则/UI布局)    │
│ LLM: Mimo mimo-v2.5-pro             │
│ 耗时: ~3-5s                          │
└──────────────┬──────────────────────┘
               │ success → 继续
               │ failed → 终止
               ▼
┌─────────────────────────────────────┐
│ Step 3: Code Generation             │
│ 角色: Web 游戏开发工程师               │
│ 输入: Step 2 的设计文档               │
│ 输出: 完整 HTML 文件 (CSS+JS inline)  │
│ LLM: Mimo mimo-v2.5-pro             │
│ 耗时: ~10-20s                        │
└──────────────┬──────────────────────┘
               │ success → 继续
               │ failed → 终止
               ▼
┌─────────────────────────────────────┐
│ Step 4: Upload                      │
│ 无 LLM 调用                          │
│ 操作: 上传 HTML 到 MinIO              │
│ 输出: MinIO 公开 URL                 │
│ 更新: Game.remote_url, Game.status   │
│ 耗时: <1s                            │
└──────────────┬──────────────────────┘
               │
               ▼
        Game.status = "draft"
        可预览、可发布
```

## 各步骤 Prompt 设计

### Step 1: Creative Analysis

**System Prompt:**
```
You are a game design analyst.
```

**User Prompt 模板:**
```
Analyze the following creative input and extract structured game concepts.

User's creative idea:
{user_prompt}

Respond in the following JSON format ONLY:
{
  "gameplay": "brief description of core gameplay mechanics",
  "style": "visual/art style",
  "characters": ["list of character names or roles"],
  "win_condition": "how the player wins",
  "lose_condition": "how the player loses",
  "game_type": "category (puzzle, adventure, action, trivia)",
  "mood": "overall mood/tone"
}
```

**设计思路:** 将模糊的自然语言转化为精确的结构化数据，便于后续步骤使用。

---

### Step 2: Game Design

**System Prompt:**
```
You are a game designer.
```

**User Prompt 模板:**
```
Based on the following game concept, create a detailed game design document.

Game Concept:
{step1_output_json}

Respond in JSON format:
{
  "title": "game title",
  "description": "player-facing description",
  "ui_layout": "screen layout description",
  "gameplay_rules": ["rule1", "rule2"],
  "levels": ["level descriptions"],
  "assets_needed": ["visual/audio assets"],
  "interaction_model": "click/keyboard/drag",
  "scoring": "scoring system",
  "difficulty_curve": "difficulty progression"
}
```

**设计思路:** 生成足够详细的文档，让代码生成步骤有明确的实现目标。

---

### Step 3: Code Generation

**System Prompt:**
```
You are an expert web game developer.
```

**User Prompt 模板:**
```
Generate a complete runnable HTML file for an interactive browser game.

Game Design:
{step2_output_json}

Requirements:
1. Single self-contained HTML file with all CSS and JS inline
2. Fully playable in browser
3. Use Canvas or DOM manipulation
4. Include instructions and score system
5. Game over screen with restart option
6. Visually appealing CSS styling
7. No external dependencies or CDN links

Output ONLY the HTML code starting with <!DOCTYPE html>.
```

**设计思路:** 严格的约束条件确保产物是单文件、可直接运行的 HTML。

---

## JSON 解析策略

LLM 返回的 JSON 可能包含 markdown 代码块，解析策略：

1. 检测是否以 ` ``` ` 开头
2. 如果是，移除首尾的代码块标记
3. 尝试 `json.loads()` 解析
4. 如果失败，查找第一个 `{` 和最后一个 `}` 之间的内容
5. 再次尝试解析

## 错误处理

| 场景 | 处理方式 |
|------|---------|
| LLM 返回非法 JSON | 标记该步骤 failed，终止流程 |
| LLM API 超时 (120s) | httpx 抛出异常，标记 failed |
| LLM API 返回错误 | raise_for_status() 抛出异常 |
| MinIO 上传失败 | 标记 Step 4 failed |
| 任意步骤失败 | Game.status = "failed"，流程终止 |

## 扩展方向

1. **增加验证 Agent**: 在 Step 3 之后增加代码验证步骤，检查 HTML 语法
2. **增加优化 Agent**: 对生成的游戏进行 UI 美化和性能优化
3. **并行生成**: 同时生成多个版本，选择最佳方案
4. **真实 Multi-Agent**: 使用 LangChain 等框架实现 Agent 之间的协作
5. **流式输出**: 使用 LLM streaming 实时展示生成过程
