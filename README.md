# GradInsight

GradInsight 是一个面向高校场景的数据分析平台，采用“前端 + Python API 网关 + Go 爬虫微服务”的分层架构。

项目核心目标：**把“社媒内容采集 -> 数据入库 -> 分析展示”串成可扩展链路**，支持任务化抓取、状态追踪、统计可视化和内容分析。

---

## 项目介绍

GradInsight 由 3 个主要服务组成：

- **前端（Vue3 + Vite）**：提供任务管理、统计展示、分析页面。
- **后端 API（FastAPI）**：提供业务接口、鉴权、任务管理、对接爬虫 gRPC。
- **Go 爬虫微服务（重点）**：负责高并发爬取、任务队列调度、浏览器资源池管理、去重与持久化。

### 服务调用关系（简化）

```text
Vue Frontend
   -> FastAPI Backend (/api/*)
      -> gRPC Crawler Service (Go)
         -> Browser Pool + Redis Bloom + MySQL
```

---

## 核心技术栈

### 前端

- Vue 3
- Vue Router
- Pinia
- Axios
- Vite
- Bootstrap / Bootstrap Icons

### 后端（API 网关）

- Python 3.8+
- FastAPI + Uvicorn
- Pydantic / pydantic-settings
- aiomysql
- grpcio（调用爬虫服务）
- python-consul（服务发现）
- JWT（python-jose + passlib/bcrypt）

### Go 爬虫微服务（重点）

- Go 1.24.1（`services/crawler/go.mod`）
- go-zero（RPC / 配置 / 日志 / 并发工具）
- gRPC + protobuf
- chromedp（浏览器自动化采集）
- Redis Bloom（基于 go-zero bloom）
- MySQL（任务/帖子/评论持久化）
- Consul（服务注册）
- Snowflake（分布式 ID）

---

## 核心亮点（着重 Go 爬虫微服务）

### 1) 任务队列 + 并发 Worker 调度

- `TaskQueue` 通过 `taskChan + workerPool` 控制并发，支持任务生命周期管理。
- 支持“大任务分治”，将任务拆分为子任务并汇总进度。
- 获取资源超时会自动重入队列，提升高负载下的可用性。

参考：`services/crawler/internal/infra/ctrl/taskQueue.go`

### 2) 浏览器资源池（高成本资源复用）

- 维护可复用浏览器资源单元，按需创建、回收和健康检查。
- 提供刷新/销毁机制，避免不健康实例长期污染服务。
- 支持负载均衡策略、指纹/IP/数据目录组合，便于抗风控与隔离运行。

参考：`services/crawler/internal/infra/resource/pool.go`

### 3) 去重与数据质量控制

- 使用 Redis Bloom Filter 做链接去重，减少重复抓取。
- 任务维度支持最小点赞数、评论数、是否抓图等采集参数。

参考：`services/crawler/internal/svc/serviceContext.go`

### 4) 微服务注册与发现

- Go 爬虫启动时向 Consul 注册，后端通过 Consul/配置发现服务地址。
- 前后端解耦，爬虫可独立扩容。

参考：`services/crawler/crawler.go`、`backend/utils/discovery.py`

### 5) 协议清晰（gRPC）

- `CrawlerService.StartCrawl` 提供统一任务启动入口。
- 契约集中在 proto 文件，便于多语言调用与演进。

参考：`shared/protos/crawler.proto`

---

## 快速启动

### 0. 准备依赖

- MySQL（先创建 `gradinsight` 数据库）
- Redis
- Consul
- 可用 Chrome/Chromium 浏览器（供爬虫服务调用）

### 1. 初始化环境变量

在三个子项目中从示例复制配置：

```powershell
copy backend\.env.example backend\.env
copy frontend\.env.example frontend\.env
copy services\crawler\.env.example services\crawler\.env
```

重点检查：

- `services/crawler/.env` 中的 `RESOURCE_BROWSER_PATH`
- MySQL/Redis/Consul 地址与密码
- 各服务端口是否冲突（默认前端 3000、后端 8000、爬虫 8999）

### 2. 初始化数据库

按需执行 SQL（至少包含用户与爬虫相关表）：

- `shared/ddl/users.sql`
- `shared/ddl/crawler.sql`
- `shared/ddl/content_analysis.sql`

### 3. 启动 Go 爬虫微服务（建议先启动）

```powershell
cd services\crawler
go mod tidy
go run .\crawler.go -config .\etc\crawler.yaml -env .\.env
```

### 4. 启动 Python 后端

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python .\main.py
```

### 5. 启动前端

```powershell
cd frontend
npm install
npm run dev
```

启动后可访问：

- 前端：`http://localhost:3000`
- 后端文档：`http://localhost:8000/docs`

---

## 项目结构

```text
GradInsight/
|- frontend/                 # Vue3 前端
|  |- src/
|  |  |- views/              # 页面
|  |  |- services/           # API 调用封装
|  |  |- stores/             # Pinia 状态管理
|  |- vite.config.js
|
|- backend/                  # FastAPI 业务 API
|  |- api/routes/            # 路由层（auth/crawler/task/stats/...）
|  |- services/              # 业务服务层
|  |- db/                    # 数据库连接与访问
|  |- core/                  # 配置、鉴权、生命周期事件
|  |- grpc_client/           # gRPC 客户端与 proto
|  |- main.py
|
|- services/
|  |- crawler/               # Go 爬虫微服务（核心）
|     |- crawler.go          # 服务入口（加载配置、注册 Consul、启动 gRPC）
|     |- etc/crawler.yaml    # go-zero 配置
|     |- internal/
|     |  |- control/         # 应用编排
|     |  |- infra/           # 任务队列、资源池、仓储、工具
|     |  |- logic/           # gRPC 业务逻辑
|     |  |- model/           # 数据模型访问
|     |  |- server/          # gRPC 服务实现
|     |  |- svc/             # ServiceContext 依赖装配
|     |- proto/              # Go 侧生成的 protobuf 代码
|
|- shared/
|  |- protos/                # 跨服务共享 proto（协议源文件）
|  |- ddl/                   # 数据库初始化脚本
```