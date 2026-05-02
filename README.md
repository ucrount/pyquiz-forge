# pyquiz-forge

> **多语言编程练习题自动生成系统** — 一个工具搞定题库生产、管理、评分与导出。

把知识点交给它，大模型给你回结构化的练习题：题干、提示、标准答案、参考代码、测试用例、解析、易错点 ——
13 个字段一次到位。配合多维质量评分和题库导出，几个小时就能产出一份高质量练习册。

🌐 **支持 4 种语言**：Python / Java / Go / JavaScript
🤖 **支持 5 家大模型**：OpenAI / DeepSeek / Qwen / Moonshot / Claude
🐳 **单 Docker 容器**部署，前后端一体，SQLite 零运维。

---

## 管理后台一览

```
┌──────────────────────────────────────────────────────────────────────────┐
│ ⚒️ pyquiz-forge   概览                       [Python ▼]  激活: deepseek │
├────────────┬─────────────────────────────────────────────────────────────┤
│ 概览        │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐         │
│ 学习路线    │  │ Python  │ │ Python  │ │ Python  │ │ 激活 LLM│         │
│ 题目生成    │  │ 章节    │ │ 知识点  │ │ 题目    │ │         │         │
│ 题库管理    │  │   12    │ │   59    │ │   24    │ │ deepseek│         │
│ 大模型配置  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘         │
│ 生成日志    │                                                            │
│ 导出题库    │  最近生成日志              │  快捷入口                    │
│            │  #15 Python/3.1 basic ✓   │  [+ 生成题目]  [⚙️ LLM 配置]  │
│            │  #14 Python/2.5 advanced  │  [📚 题库]    [⬇️ 导出]      │
└────────────┴─────────────────────────────────────────────────────────────┘
```

7 个页面：**概览** / **学习路线**（可编辑） / **题目生成** / **题库管理**（含编辑器+评分） /
**大模型配置** / **生成日志** / **导出题库**。

---

## 功能特性

### 题目生产
- 内置 **4 语言学习路线**：30 章 / 134 知识点
- **7 种题型**：选择题、填空题、判断题、代码阅读题、代码补全题、编程实现题、Debug 修错题
- **5 个难度**：入门 / 基础 / 中级 / 进阶 / 综合
- 单题或**批量生成**（一次出数十道）
- 生成失败自动留日志（看原始返回排查 prompt 问题）

### 题目管理
- 完整 **13 字段编辑器**（含可增删的测试用例）
- **多维质量评分**：清晰度 / 正确性 / 难度匹配 / 教学价值，1-10 分
- 重新生成 / 状态切换（草稿 / 已发布 / 已归档）
- 多条件筛选（语言 / 难度 / 题型 / 状态 / 最低分） + 分页 + 批量操作

### 学习路线编辑器
- 在浏览器直接增删改**章节**和**知识点**
- 删除前自动统计下游影响（含 N 个知识点 / M 道题目）

### LLM 配置
- 多套配置随时切换激活
- **OpenAI / DeepSeek / Qwen / Moonshot / Claude** 5 家
- 一键测试连通性
- API Key 自动脱敏显示

### 导出
- **JSON / Markdown** 双格式
- 按语言 / 难度 / 题型 / 状态 / 最低分多维过滤
- 浏览器一键下载

### 部署
- **单 Docker 容器**：前端 build 产物自动注入后端镜像，FastAPI 同时服务 SPA + API
- **SQLite** 文件型数据库（零运维）
- 启动自动建表 + 种子学习路线 + 平滑迁移（旧数据库自动加列）

---

## 快速开始（Docker · 3 步上线）

要求：Docker 20.10+ / docker compose v2。

```bash
git clone https://github.com/ucrount/pyquiz-forge.git
cd pyquiz-forge
cp .env.example .env                    # 编辑 .env，至少填一个 LLM API Key
docker compose up -d --build
```

完成后打开浏览器：

| 入口 | 地址 |
|------|------|
| 🌐 管理后台 | http://localhost:8765/ |
| 📘 Swagger UI（API 调试） | http://localhost:8765/docs |
| ❤️ 健康检查 | http://localhost:8765/api/v1/health |

> 没填 `DEFAULT_LLM_API_KEY` 也能起服务，进管理后台手动建配置即可。

---

## 第一次使用（5 分钟出第一道题）

### ① 配 LLM

管理后台左栏 → **大模型配置** → 右上「新建」

| 字段 | 推荐值 |
|------|--------|
| Provider | `deepseek`（国内便宜，~¥1/百万 token） |
| API Key | 从 [platform.deepseek.com](https://platform.deepseek.com) 申请 |
| 其余字段 | **自动填好**（api_base / model 都按 provider 推荐值预填） |

保存 → 列表里点「**测试**」连通 → 点「**激活**」。

> 想用 Claude？Provider 选 `claude`，填 `sk-ant-...` Key 即可，prompt 已为 Claude API 适配。

### ② 选语言（可选）

头部右上角下拉切换 **Python / Java / Go / JavaScript**。
默认 Python，选择会持久化到浏览器（刷新不丢）。

### ③ 生成第一道题

**学习路线** → 点想出题的知识点（如「列表 list」）→ 详情面板「**用此知识点生成题目**」

或：**题目生成**页 → 知识点级联选择 → 难度 / 题型 → 「生成题目」按钮。

20–60 秒后看到题目，自带语法高亮代码、测试用例表格、解析、易错点。

### ④ 评分

**题库管理** → 任意行的「评分」按钮，或勾多行后「批量评分」 → LLM 多维评估 → 出现彩色分数徽标
（绿 ≥ 8.5，蓝 ≥ 7，黄 ≥ 5，红 < 5）。

### ⑤ 导出

**导出题库** → 选筛选条件 + 最低分 → 「下载 Markdown」或「下载 JSON」 → 题库到手 ✓

---

## 多语言支持

| 语言 | 章节 | 知识点 | code 前缀 | 默认 prompt 提示 |
|------|------|--------|----------|------------------|
| **Python** | 12 | 59 | （无前缀，legacy） | 使用 Python 3.10+ 语法 |
| **Java** | 6 | 27 | `java-` | 使用 Java 17+ 语法，含 main 类骨架 |
| **Go** | 6 | 23 | `go-` | 使用 Go 1.21+ 语法，含 package main |
| **JavaScript** | 6 | 25 | `js-` | 使用 ES2022+ 语法 |

### 自定义学习路线

**推荐**：管理后台 → 学习路线 → 直接增删改章节和知识点（不需要重启）。

**或**编辑 `app/data/learning_path_<lang>.json`，重启容器自动生效（upsert，不会丢已有题目）。

### 加新语言

例如要加 Rust：

1. 复制 `app/data/learning_path_python.json` → `app/data/learning_path_rust.json`
2. 改顶层 `language: "rust"` 和 `language_label: "Rust"`，章节代码加 `rust-` 前缀
3. `frontend/src/types/common.ts` 在 `LANGUAGE_LABEL` 加一行 `rust: 'Rust'`
4. （可选）`app/llm/prompts.py` 在 `LANGUAGE_NOTES` 加 Rust 专属说明
5. 重启服务

---

## 本地开发

需要 Python 3.11+ 和 Node.js 20+。

### 后端

```bash
python -m venv .venv
source .venv/bin/activate                  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                       # 填 LLM API Key
uvicorn app.main:app --reload --port 8000
```

后端单独跑时根路径返回元信息 JSON；`/docs` 仍可访问。

### 前端（HMR 模式）

新开一个终端：

```bash
cd frontend
npm install
npm run dev
```

打开 http://localhost:5173/。Vite 自动把 `/api/*`、`/docs`、`/openapi.json` 代理到 `127.0.0.1:8000`。

### 本地复现"单服务"模式

```bash
cd frontend && npm run build && cd ..
rm -rf app/static && cp -r frontend/dist app/static
uvicorn app.main:app --port 8000
```

http://localhost:8000/ 同时服务前后端（生产部署的本地预览）。

---

## 配置项 .env

| 变量 | 说明 | 默认 |
|------|------|------|
| `APP_NAME` | 应用名 | `pyquiz-forge` |
| `APP_ENV` | 环境标记 | `production` |
| `LOG_LEVEL` | 日志级别（DEBUG/INFO/WARNING/ERROR） | `INFO` |
| `API_PREFIX` | API 路径前缀 | `/api/v1` |
| `DATABASE_URL` | SQLAlchemy URL | `sqlite:///./data/pyquiz.db` |
| `CORS_ORIGINS` | 允许的跨域来源（逗号分隔，`*` = 全部） | `*` |
| `DEFAULT_LLM_PROVIDER` | 首启时种子配置的 provider | `deepseek` |
| `DEFAULT_LLM_API_KEY` | 首启时种子的 API Key（必填才会种子） | — |
| `DEFAULT_LLM_API_BASE` | API Base URL | `https://api.deepseek.com/v1` |
| `DEFAULT_LLM_MODEL` | 模型名 | `deepseek-chat` |
| `DEFAULT_LLM_TEMPERATURE` | 默认温度 | `0.7` |
| `DEFAULT_LLM_MAX_TOKENS` | 最大输出 token 数 | `2048` |

> `DEFAULT_LLM_*` 仅在数据库**没有任何 LLM 配置**时种子写入并激活；如果数据库已有配置，它们会被忽略。

### 支持的 provider 取值

- `openai` / `deepseek` / `qwen` / `moonshot` —— 使用 OpenAI 兼容 Chat Completions API
- `claude` —— 使用 Anthropic Messages API（自动转换 system 字段、token 计数）

新建配置时前端会按 provider **自动填充推荐值**：
- OpenAI → `https://api.openai.com/v1` + `gpt-4o-mini`
- DeepSeek → `https://api.deepseek.com/v1` + `deepseek-chat`
- Qwen → `https://dashscope.aliyuncs.com/compatible-mode/v1` + `qwen-plus`
- Moonshot → `https://api.moonshot.cn/v1` + `moonshot-v1-8k`
- Claude → `https://api.anthropic.com` + `claude-sonnet-4-6`

---

## 部署到 Linux 服务器

任意 Linux 发行版，仅需 Docker。

### 1. 装 Docker

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
# 重新登录使组生效
docker --version && docker compose version
```

### 2. 上传代码

```bash
# 推荐 git
cd /opt
sudo git clone https://github.com/ucrount/pyquiz-forge.git
sudo chown -R $USER:$USER pyquiz-forge

# 或 rsync
rsync -avz --exclude '.venv' --exclude 'data' --exclude 'logs' \
    --exclude 'frontend/node_modules' --exclude 'frontend/dist' \
    ./pyquiz-forge/ user@your-server:/opt/pyquiz-forge/
```

### 3. 配置 + 启动

```bash
cd /opt/pyquiz-forge
cp .env.example .env
vim .env                         # 填 DEFAULT_LLM_API_KEY 等
docker compose up -d --build
docker compose logs -f
```

### 4. 防火墙 / 安全组

```bash
sudo ufw allow 8765/tcp          # ufw 用户
# 云厂商安全组也要放行 8765
```

访问：`http://<服务器 IP>:8765/`

### 5. 升级

```bash
cd /opt/pyquiz-forge
git pull
docker compose up -d --build
```

数据在挂载的 `./data/pyquiz.db`，**升级不丢数据**（且自动迁移新增列）。

### ⚠️ 安全建议

公网暴露 = LLM Token 也对外开放。生产环境强烈建议：

- **仅本机端口** + 反代加 Auth：把 compose 端口改为 `"127.0.0.1:8765:8000"`，用 Nginx/Caddy 加 Basic Auth
- **关闭 Swagger**：`app/main.py` 改 `docs_url=None, redoc_url=None`
- **加 IP 白名单**：在反代上限制源 IP

---

## API 速查

完整请求/响应字段以 [Swagger UI](http://localhost:8765/docs) 为准。

### 系统
| 方法 | 路径 |
|------|------|
| GET | `/api/v1/health` |
| GET | `/api/v1/version` |

### 学习路线（含编辑器）
| 方法 | 路径 |
|------|------|
| GET | `/api/v1/learning-path?language=` |
| GET | `/api/v1/chapters?language=` |
| POST | `/api/v1/chapters` |
| PUT | `/api/v1/chapters/{id}` |
| DELETE | `/api/v1/chapters/{id}` |
| GET | `/api/v1/chapters/{id}/cascade-info` |
| GET | `/api/v1/knowledge-points?language=&chapter_id=` |
| POST | `/api/v1/knowledge-points` |
| PUT | `/api/v1/knowledge-points/{id}` |
| DELETE | `/api/v1/knowledge-points/{id}` |
| GET | `/api/v1/knowledge-points/{id}/cascade-info` |
| GET | `/api/v1/learning-path/next-order?language=&chapter_id=` |

### LLM 配置
| 方法 | 路径 |
|------|------|
| GET / POST | `/api/v1/llm-configs` |
| GET / PUT / DELETE | `/api/v1/llm-configs/{id}` |
| POST | `/api/v1/llm-configs/{id}/activate` |
| POST | `/api/v1/llm-configs/{id}/test` |

### 题目生成
| 方法 | 路径 |
|------|------|
| POST | `/api/v1/exercises/generate` |
| POST | `/api/v1/exercises/generate/batch` |
| POST | `/api/v1/exercises/{id}/regenerate` |

### 题目管理
| 方法 | 路径 |
|------|------|
| GET | `/api/v1/exercises?language=&difficulty=&question_type=&min_score=&page=&size=` |
| GET / PATCH / DELETE | `/api/v1/exercises/{id}` |
| POST | `/api/v1/exercises/bulk-delete` |

### 质量评分
| 方法 | 路径 |
|------|------|
| POST | `/api/v1/exercises/{id}/score` |
| POST | `/api/v1/exercises/score/batch` |

### 导出
| 方法 | 路径 |
|------|------|
| GET | `/api/v1/export/json?language=&min_score=...` |
| GET | `/api/v1/export/markdown?language=&min_score=...` |

### 生成日志
| 方法 | 路径 |
|------|------|
| GET | `/api/v1/generation-logs?page=&size=` |
| GET | `/api/v1/generation-logs/{id}` |

---

## 数据持久化与备份

数据全在 `./data/pyquiz.db`（容器内是 `/app/data/pyquiz.db`），通过 docker volume 挂载到宿主机。

**强烈建议每天备份**：

```bash
# crontab -e
0 3 * * * cp /opt/pyquiz-forge/data/pyquiz.db /opt/backups/pyquiz-$(date +\%F).db && find /opt/backups -name 'pyquiz-*.db' -mtime +30 -delete
```

数据库 schema 升级（如新版本新增列）会在容器启动时自动平滑迁移（见 `app/core/migrations.py`）。

---

## 常见问题

<details>
<summary><b>Q1：调用生成接口报 "No active LLM config"</b></summary>

先到「大模型配置」页创建一条配置并点「激活」，或调用 API：
`POST /api/v1/llm-configs/{id}/activate`。
</details>

<details>
<summary><b>Q2：生成接口返回 400「Failed to parse LLM response as JSON」</b></summary>

模型偶尔返回多余文字（含解释或 Markdown 围栏）。系统已做 3 层降级解析，仍失败时：

1. 「生成日志」页看原始响应
2. 把 LLM 配置的 `temperature` 调到 0.3 ～ 0.5
3. 试更强的模型（DeepSeek-Chat → DeepSeek-Reasoner，或换 Claude Sonnet）
</details>

<details>
<summary><b>Q3：怎么修改学习路线？</b></summary>

**简单方式**：管理后台「学习路线」页直接编辑（推荐）。

**批量方式**：编辑 `app/data/learning_path_<lang>.json`，重启服务即可（按 code 做 upsert，不删旧数据）。
</details>

<details>
<summary><b>Q4：怎么接 Claude？</b></summary>

「大模型配置」新建 → Provider 选 `claude` → 前端自动填 `https://api.anthropic.com` + `claude-sonnet-4-6`
→ 填 `sk-ant-...` API Key → 激活即可。生成、评分、批量、Claude provider 全支持。
</details>

<details>
<summary><b>Q5：API Key 怎么保护？</b></summary>

MVP 阶段是明文存 SQLite，文件权限是宿主机 user 私有。要更高安全：

- 用 `cryptography.Fernet` 加密 `api_key` 字段，主密钥从 env 读
- 不要在公网暴露 `/api/v1/llm-configs` 的 GET 接口（虽然 api_key 已脱敏，但 model/api_base 仍可见）
- 加 API Key 中间件，仅特定 header 才放行
</details>

<details>
<summary><b>Q6：SQLite 报 "database is locked"</b></summary>

MVP 用 `--workers 1`，单进程下不应出现。如果你改成多 worker，要么换 PostgreSQL，要么调大 `connect_args` 里的 `timeout`。
</details>

<details>
<summary><b>Q7：Docker 镜像构建慢 / 失败（npm install）</b></summary>

Dockerfile 第一阶段在 Node 20-alpine 构建前端。慢通常是 npm 网络问题，可以：

```dockerfile
# 在 frontend-builder 阶段加：
RUN npm config set registry https://registry.npmmirror.com
```
</details>

---

## 项目结构

```
pyquiz-forge/
├── app/                                # 后端
│   ├── main.py                         # FastAPI 入口 + StaticFiles + SPA fallback
│   ├── core/
│   │   ├── config.py                   # Pydantic Settings
│   │   ├── database.py                 # SQLAlchemy engine / session
│   │   ├── logger.py                   # 日志（stdout + 旋转文件）
│   │   └── migrations.py               # 启动时自动 ALTER TABLE
│   ├── models/                         # SQLAlchemy ORM
│   ├── schemas/                        # Pydantic 请求/响应模型
│   ├── crud/                           # 数据访问层
│   ├── api/v1/
│   │   ├── learning_path.py            # 章节 + 知识点 CRUD + cascade
│   │   ├── llm_config.py               # LLM 配置 CRUD + activate + test
│   │   ├── generation.py               # 单题/批量生成 + 重生
│   │   ├── scoring.py                  # 多维质量评分
│   │   ├── exercise.py                 # 题目 CRUD + 批量
│   │   ├── export.py                   # JSON / Markdown 导出
│   │   └── system.py                   # health / version
│   ├── services/
│   │   ├── generation_service.py       # 组装 prompt → 调 LLM → 解析 → 入库
│   │   ├── scoring_service.py          # 多维评分服务
│   │   ├── export_service.py           # 导出渲染
│   │   └── seed_service.py             # 启动时种子学习路线
│   ├── llm/
│   │   ├── base.py                     # BaseLLMClient + LLMResponse
│   │   ├── factory.py                  # provider → client 工厂
│   │   ├── openai_compatible.py        # OpenAI/DeepSeek/Qwen/Moonshot
│   │   ├── claude.py                   # Anthropic Messages API
│   │   └── prompts.py                  # 多语言 prompt 模板
│   ├── data/
│   │   ├── learning_path_python.json
│   │   ├── learning_path_java.json
│   │   ├── learning_path_go.json
│   │   └── learning_path_javascript.json
│   └── static/                         # 前端构建产物（Docker 自动注入）
├── frontend/                           # Vue 3 + TypeScript
│   ├── src/
│   │   ├── api/                        # axios 封装
│   │   ├── types/                      # TS 类型（与后端 schema 对齐）
│   │   ├── stores/                     # Pinia (LLM / language)
│   │   ├── components/                 # ChapterDialog / KPDialog / ExerciseEditor / ScoreBadge / CodeBlock 等
│   │   ├── views/                      # 7 个页面
│   │   ├── layouts/                    # AdminLayout（含语言切换）
│   │   ├── router/
│   │   └── utils/
│   ├── package.json
│   └── vite.config.ts
├── scripts/init_db.py                  # 建表 + 种子（脚本入口）
├── data/                               # 运行时数据（挂载，gitignored）
├── logs/                               # 运行日志（挂载，gitignored）
├── .env.example  .gitignore  .dockerignore
├── Dockerfile                          # 多阶段：Node 构建前端 → Python 运行后端
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 技术栈

**后端**：Python 3.11 · FastAPI · SQLAlchemy 2.0 · Pydantic 2 · openai SDK · anthropic SDK · tenacity
**前端**：Vue 3 · Vite · TypeScript · Element Plus · Pinia · Vue Router · axios · highlight.js
**数据库**：SQLite（默认）· 也支持 PostgreSQL（改 `DATABASE_URL` 即可）
**部署**：Docker 多阶段构建 · uvicorn · 单容器同时服务前后端

---

## License

MIT — 自用项目，自由使用与修改。Issue / PR 欢迎。
