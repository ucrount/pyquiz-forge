# pyquiz-forge

> Python 练习题自动生成系统

一个面向个人/小团队的 Python 练习题"题库生产工具"。给它一个知识点、难度和题型，它通过大模型自动产出结构化、可直接用于教学的练习题，并以题库形式管理和导出。

- **后端**：Python 3.11 + FastAPI + SQLAlchemy 2.0 + Pydantic 2
- **前端**：Vue 3 + Vite + TypeScript + Element Plus
- **数据库**：SQLite（文件型，零运维）
- **大模型**：兼容 OpenAI 协议（DeepSeek / OpenAI / Qwen / Moonshot 等），Claude 接口预留
- **部署**：单 Docker 容器同时服务前后端

---

## 目录

- [功能](#功能)
- [快速开始（Docker，推荐）](#快速开始docker推荐)
- [本地开发运行](#本地开发运行)
- [配置项 .env](#配置项-env)
- [核心使用流程](#核心使用流程)
- [API 端点速查](#api-端点速查)
- [服务器部署](#服务器部署)
- [数据持久化与备份](#数据持久化与备份)
- [常见问题](#常见问题)
- [项目结构](#项目结构)

---

## 功能

- 内置 12 章 59 个知识点的 Python 学习路线
- LLM 配置管理（多套配置可切换，支持连通性测试）
- 单题 / 批量生成练习题
- 题目列表（按知识点/难度/题型/状态过滤 + 分页）
- 题目详情、修改、删除、批量删除
- 题目重新生成（新建 or 覆盖）
- 题库导出 JSON / Markdown
- 完整生成日志（prompt、原始返回、Token、耗时）
- **管理后台 UI**（侧栏 + 概览 + 学习路线 + 配置 + 生成 + 题库 + 日志 + 导出）

---

## 快速开始（Docker，推荐）

要求：宿主机已装 Docker（20.10+）和 docker compose（v2）。

```bash
# 1. 克隆/复制项目
cd /opt
# 假设你已经把代码放到了 /opt/pyquiz-forge

cd pyquiz-forge

# 2. 准备配置
cp .env.example .env
# 用编辑器打开 .env，至少把 DEFAULT_LLM_API_KEY 填上
# vim .env

# 3. 构建并启动
docker compose up -d --build

# 4. 查看启动日志
docker compose logs -f pyquiz-forge

# 5. 测试健康检查
curl http://localhost:8765/api/v1/health
# {"status":"ok"}
```

打开浏览器访问：

- **管理后台**：http://localhost:8765/
- **Swagger UI**：http://localhost:8765/docs

---

## 本地开发运行

要求：Python 3.11+，Node.js 20+。

### 后端

```bash
# 1. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 准备配置
cp .env.example .env
# 编辑 .env 填入 LLM API Key

# 4. 启动后端
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端单独跑时，根路径返回元信息 JSON；`/docs` 仍可访问。

### 前端（开发模式，HMR）

新开一个终端：

```bash
cd frontend
npm install
npm run dev
```

打开 http://localhost:5173/ 。Vite dev server 自动把 `/api/*`、`/docs`、`/openapi.json` 代理到 `http://127.0.0.1:8000`，所以前后端协作开发零 CORS 配置。

### 前端构建并由后端服务

如果你想在本地复现"单服务"模式（不开 Vite）：

```bash
cd frontend && npm run build && cd ..
rm -rf app/static && cp -r frontend/dist app/static
uvicorn app.main:app --port 8000
```

打开 http://localhost:8000/ ，整个管理后台由 FastAPI 用 StaticFiles 提供。

---

## 配置项 .env

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `APP_NAME` | 应用名 | `pyquiz-forge` |
| `APP_ENV` | 环境标记 | `production` |
| `LOG_LEVEL` | 日志级别（DEBUG/INFO/WARNING/ERROR） | `INFO` |
| `API_PREFIX` | API 路径前缀 | `/api/v1` |
| `DATABASE_URL` | SQLAlchemy URL | `sqlite:///./data/pyquiz.db` |
| `CORS_ORIGINS` | 允许的跨域来源（逗号分隔，`*` 表示全部） | `*` |
| `DEFAULT_LLM_PROVIDER` | 首启时种子配置的 provider | `deepseek` |
| `DEFAULT_LLM_API_KEY` | 首启时种子配置的 API Key（必填才会种子） | — |
| `DEFAULT_LLM_API_BASE` | API Base URL | `https://api.deepseek.com/v1` |
| `DEFAULT_LLM_MODEL` | 模型名 | `deepseek-chat` |
| `DEFAULT_LLM_TEMPERATURE` | 默认温度 | `0.7` |
| `DEFAULT_LLM_MAX_TOKENS` | 最大输出 token 数 | `2048` |

> **说明**：`DEFAULT_LLM_*` 仅在数据库中**没有任何 LLM 配置**时种子写入并自动激活；如果数据库已有配置，它们会被忽略。后续配置请通过 API 管理。

### 支持的 provider 取值

- `openai` / `deepseek` / `qwen` / `moonshot` — 使用 OpenAI 兼容协议
- `claude` — 接口预留，调用会返回 NotImplementedError（V2 实现）

---

## 核心使用流程

打开 `/docs`，按以下顺序操作：

### 1. 浏览学习路线

```
GET /api/v1/learning-path
```

返回所有章节 + 知识点。记下你想出题的 `knowledge_point_id`（或者 `code`）。

### 2. 配置 LLM

如果首启时已通过 `.env` 种子了一条配置，可跳过。否则：

```
POST /api/v1/llm-configs
{
  "name": "deepseek-default",
  "provider": "deepseek",
  "api_key": "sk-xxxxxxx",
  "api_base": "https://api.deepseek.com/v1",
  "model": "deepseek-chat",
  "temperature": 0.7,
  "max_tokens": 2048
}
```

激活：

```
POST /api/v1/llm-configs/{id}/activate
```

测试连通性：

```
POST /api/v1/llm-configs/{id}/test
```

### 3. 生成题目

单题：

```
POST /api/v1/exercises/generate
{
  "knowledge_point_id": 12,
  "difficulty": "basic",
  "question_type": "program"
}
```

批量：

```
POST /api/v1/exercises/generate/batch
{
  "knowledge_point_id": 12,
  "items": [
    {"difficulty": "entry", "question_type": "choice", "count": 2},
    {"difficulty": "basic", "question_type": "program", "count": 3}
  ]
}
```

### 4. 查看 / 管理题目

- 列表：`GET /api/v1/exercises?knowledge_point_id=12&difficulty=basic`
- 详情：`GET /api/v1/exercises/{id}`
- 修改：`PATCH /api/v1/exercises/{id}`
- 删除：`DELETE /api/v1/exercises/{id}`
- 重新生成：`POST /api/v1/exercises/{id}/regenerate` body: `{"mode": "new"}`

### 5. 导出题库

- 浏览器直接访问会下载文件：
  - `GET /api/v1/export/json`
  - `GET /api/v1/export/markdown`
- 支持过滤：`?knowledge_point_id=12&difficulty=basic`

---

## API 端点速查

| 分类 | 方法 | 路径 |
|------|------|------|
| 系统 | GET | `/api/v1/health` |
| 系统 | GET | `/api/v1/version` |
| 学习路线 | GET | `/api/v1/learning-path` |
| 学习路线 | GET | `/api/v1/chapters` |
| 学习路线 | GET | `/api/v1/chapters/{id}/knowledge-points` |
| 学习路线 | GET | `/api/v1/knowledge-points` |
| 学习路线 | GET | `/api/v1/knowledge-points/{id}` |
| LLM 配置 | GET | `/api/v1/llm-configs` |
| LLM 配置 | POST | `/api/v1/llm-configs` |
| LLM 配置 | GET | `/api/v1/llm-configs/{id}` |
| LLM 配置 | PUT | `/api/v1/llm-configs/{id}` |
| LLM 配置 | DELETE | `/api/v1/llm-configs/{id}` |
| LLM 配置 | POST | `/api/v1/llm-configs/{id}/activate` |
| LLM 配置 | POST | `/api/v1/llm-configs/{id}/test` |
| 生成 | POST | `/api/v1/exercises/generate` |
| 生成 | POST | `/api/v1/exercises/generate/batch` |
| 生成 | POST | `/api/v1/exercises/{id}/regenerate` |
| 题目 | GET | `/api/v1/exercises` |
| 题目 | GET | `/api/v1/exercises/{id}` |
| 题目 | PATCH | `/api/v1/exercises/{id}` |
| 题目 | DELETE | `/api/v1/exercises/{id}` |
| 题目 | POST | `/api/v1/exercises/bulk-delete` |
| 导出 | GET | `/api/v1/export/json` |
| 导出 | GET | `/api/v1/export/markdown` |
| 日志 | GET | `/api/v1/generation-logs` |
| 日志 | GET | `/api/v1/generation-logs/{id}` |

完整的请求/响应字段以 Swagger UI 为准。

---

## 服务器部署

支持任意 Linux 服务器（Debian / Ubuntu / CentOS / Rocky 等），仅需 Docker。

### 1. 准备服务器

```bash
# 安装 docker（以 Debian/Ubuntu 为例）
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
# 退出再登录使 docker 组生效

# 验证
docker --version
docker compose version
```

### 2. 上传代码

任选其一：

```bash
# 方式 A：git
cd /opt
sudo git clone <your-repo-url> pyquiz-forge
sudo chown -R $USER:$USER pyquiz-forge

# 方式 B：rsync
rsync -avz --exclude '.venv' --exclude 'data' --exclude 'logs' \
    ./pyquiz-forge user@your-server:/opt/

# 方式 C：scp
scp -r pyquiz-forge user@your-server:/opt/
```

### 3. 配置环境变量

```bash
cd /opt/pyquiz-forge
cp .env.example .env
vim .env
# 至少设置：
#   DEFAULT_LLM_API_KEY=sk-xxxxx
#   CORS_ORIGINS=http://your-domain   # 或保持 *
```

### 4. 启动

```bash
docker compose up -d --build
docker compose logs -f
```

### 5. 防火墙 / 安全组

```bash
# 如果用 ufw
sudo ufw allow 8765/tcp

# 云厂商安全组也要放行 8765
```

访问：`http://<服务器 IP>:8765/docs`

### 6. 升级

```bash
cd /opt/pyquiz-forge
git pull          # 或重新上传代码
docker compose up -d --build
```

SQLite 文件在挂载的 `./data` 目录里，升级不会丢数据。

### 安全建议（重要）

管理后台 + Swagger UI 暴露公网相当于把 LLM API 调用接口对外开放——任何人都能消耗你的 Token 配额。生产环境强烈建议至少做以下之一：

- **仅本机端口**：把 compose 端口改为 `"127.0.0.1:8765:8000"`，再用 Nginx/Caddy 反代加 Basic Auth 或 API Key
- **关闭 Swagger**：在 `app/main.py` 中传 `docs_url=None, redoc_url=None`
- **加 IP 白名单**：在反代上配置

---

## 数据持久化与备份

数据全在 `./data/pyquiz.db`（容器内是 `/app/data/pyquiz.db`），通过 docker volume 挂载到宿主机。

**强烈建议每天备份**：

```bash
# crontab -e
0 3 * * * cp /opt/pyquiz-forge/data/pyquiz.db /opt/backups/pyquiz-$(date +\%F).db && find /opt/backups -name 'pyquiz-*.db' -mtime +30 -delete
```

---

## 常见问题

### Q1：调用生成接口报 "No active LLM config"

A：先创建一条 LLM 配置，然后调 `POST /api/v1/llm-configs/{id}/activate` 激活。

### Q2：生成接口返回 400，提示 "Failed to parse LLM response as JSON"

A：模型偶尔会返回多余文字（例如 Markdown 代码块外有解释）。系统已经做了多种解析策略，仍解析失败时：

1. 查看 `GET /api/v1/generation-logs` 看原始响应
2. 把 LLM 配置的 `temperature` 降到 0.3 ～ 0.5
3. 重试

### Q3：SQLite 报 "database is locked"

A：MVP 用 `--workers 1`，单进程下不应出现。如果你改成多 worker，要么换 PostgreSQL，要么调整 `connect_args` 里的 `timeout`。

### Q4：怎么修改学习路线？

A：编辑 `app/data/learning_path.json`，重启服务即可（会做 upsert，不删旧数据，但会更新 title/description/keywords）。

### Q5：怎么接 Claude？

A：`app/llm/claude.py` 已经留好类结构。实现 `chat()` 方法即可：用 `anthropic` SDK，把 messages 转成 Claude 格式，再把响应映射到 `LLMResponse` 即可。

### Q6：API Key 怎么保护？

A：MVP 阶段是明文存 SQLite，文件权限是宿主机 user 私有的 `data/`。要更高安全：

- 用 `cryptography.Fernet` 加密 `api_key` 字段
- 主密钥从环境变量读
- 不要在公网暴露 `/api/v1/llm-configs` 的 GET 接口（虽然 api_key 已脱敏，但能看到 model/api_base 信息）

---

## 项目结构

```
pyquiz-forge/
├── app/                              # 后端
│   ├── main.py                       # FastAPI 入口 + StaticFiles + SPA fallback
│   ├── core/                         # config / database / logger
│   ├── models/                       # SQLAlchemy ORM 模型
│   ├── schemas/                      # Pydantic 请求/响应模型
│   ├── crud/                         # 数据访问层
│   ├── api/v1/                       # 路由层
│   ├── services/                     # 业务逻辑（生成、导出、种子）
│   ├── llm/                          # LLM 调用层（OpenAI 兼容 + Claude stub）
│   ├── data/learning_path.json       # 学习路线种子数据
│   └── static/                       # ⬅ 前端构建产物（Docker 构建时自动注入）
├── frontend/                         # Vue 3 + TypeScript 前端
│   ├── src/
│   │   ├── api/                      # axios 封装
│   │   ├── types/                    # TS 类型定义（与后端 schema 对齐）
│   │   ├── stores/                   # Pinia
│   │   ├── components/               # 公共组件
│   │   ├── views/                    # 页面
│   │   ├── layouts/                  # AdminLayout
│   │   ├── router/
│   │   └── utils/
│   ├── package.json
│   └── vite.config.ts
├── scripts/init_db.py                # 建表 + 种子脚本
├── data/                             # 运行时数据（挂载）
├── logs/                             # 运行日志（挂载）
├── .env.example  .gitignore  .dockerignore
├── Dockerfile                        # 多阶段：Node 构建前端 → Python 运行后端
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## License

MIT — 自用项目，自由使用与修改。
