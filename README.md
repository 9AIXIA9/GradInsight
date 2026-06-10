# GradInsight

高校社媒数据采集与分析平台。从小红书爬取高校相关帖子和评论，支持话题总结、内容聚类、关键词提取、情感分析、高校提及分析和专业分析。

## 架构

```
┌──────────────────────────────────────────┐
│              Vue 3 前端                   │
│            :3000 (Vite)                   │
└──────────────┬───────────────────────────┘
               │ REST
┌──────────────▼───────────────────────────┐
│        Java Spring Boot 网关              │
│            :8080                          │
│  · 认证 (JWT) · 路由鉴权                 │
│  · 分析代理 · 爬虫调度 · 统计            │
└───┬────────────────────────┬─────────────┘
    │ gRPC                   │ gRPC
┌───▼─────────────┐  ┌───────▼─────────────┐
│  Python 分析    │  │   Go 爬虫引擎       │
│    :5001        │  │      :8999          │
│                 │  │                     │
│  · 聚类         │  │  · 浏览器池         │
│  · 关键词       │  │  · 并发批次认领     │
│  · 情感分析     │  │  · 原子进度累加     │
│  · 高校/专业    │  │  · 布隆去重         │
└───┬─────────────┘  └───┬─────────────────┘
    │                    │
    └────────┬───────────┘
             │
    ┌────────▼────────┐
    │     MySQL       │
    │  (共享数据库)    │
    └─────────────────┘
```

## 技术栈

| 层         | 技术                                                   |
|-----------|------------------------------------------------------|
| 前端        | Vue 3, Vite, Pinia, Axios, Bootstrap 5               |
| Java 网关   | Spring Boot 3.1, Spring Security, JWT, gRPC          |
| Python 分析 | Python 3, gRPC, aiomysql, Pydantic                   |
| Go 爬虫     | go-zero, gRPC, chromedp, Redis Bloom, go-zero/consul |

## 项目结构

```
GradInsight/
├── frontend/                # Vue 3 前端
│   └── src/
│       ├── views/           # 页面
│       ├── services/        # API 调用
│       ├── stores/          # Pinia 状态
│       └── router/          # 路由配置
│
├── backend-java/            # Java Spring Boot 网关
│   └── src/main/java/.../
│       ├── controller/      # REST 接口
│       ├── service/         # 业务逻辑
│       ├── grpc/            # gRPC 客户端
│       ├── security/        # JWT / Security
│       └── config/          # 配置
│
├── services/
│   ├── crawler/             # Go 爬虫微服务
│   │   └── internal/
│   │       ├── infra/       # 资源池、仓储、爬虫实现
│   │       ├── domain/      # 领域模型
│   │       ├── model/       # DB 模型
│   │       └── logic/       # 业务逻辑
│   │
│   └── analysis/            # Python 分析微服务
│       ├── services/        # 分析逻辑
│       ├── models/          # 数据模型
│       ├── db/              # DB 连接
│       └── proto/           # 生成的 gRPC 桩
│
└── shared/
    ├── protos/              # gRPC 协议定义
    │   ├── crawler.proto
    │   └── analysis.proto
    └── ddl/                 # 数据库脚本
```

## 快速启动

### 依赖

- MySQL 8.0+
- Redis（爬虫布隆过滤器）
- Consul（服务注册，爬虫）
- Chrome/Chromium（爬虫浏览器）

### 1. 数据库

```sql
CREATE DATABASE gradinsight CHARACTER SET utf8mb4;
source shared/ddl/crawler.sql;
source shared/ddl/users.sql;
source shared/ddl/content_analysis.sql;
```

### 2. 环境变量

各服务从 `.env.example` 复制为 `.env` 并修改数据库连接：

| 服务     | 路径                       |
|--------|--------------------------|
| Java   | `backend-java/.env`      |
| Python | `services/analysis/.env` |
| Go     | `services/crawler/.env`  |

### 3. Go 爬虫

```powershell
cd services/crawler
go build .
.\crawler.exe -config etc/crawler.yaml -env .env
```

### 4. Python 分析

```powershell
cd services/analysis
pip install -r requirements.txt
python -m grpc_tools.protoc -I../../shared/protos --python_out=./proto --grpc_python_out=./proto ../../shared/protos/analysis.proto
python main.py
```

### 5. Java 网关

```powershell
cd backend-java
mvn spring-boot:run
```

### 6. 前端

```powershell
cd frontend
npm install
npm run dev
```

访问 `http://localhost:3000`，默认管理员 `admin` / `admin123`。

## 主要功能

### 爬虫

- 小红书关键词搜索采集
- 多浏览器并发 + 批次认领
- 原子 SQL 进度累加
- 布隆过滤器链接去重
- 启动时自动恢复未完成任务

### 内容分析

- 话题总结 — 识别热门话题及情感倾向
- 内容聚类 — 相似帖子智能分组
- 关键词提取 — TF-IDF 高频词
- 情感分析 — 正面/负面/中性
- 高校提及 — 各高校讨论频率及情感
- 专业分析 — 专业热度及就业前景

### 数据展示

- 帖子浏览（网格/列表、图片轮播）
- 图片代理（绕过防盗链）
- 分析结果标签云
- 首页数据概览

## gRPC 服务

| 服务                        | 端口   | 协议               |
|---------------------------|------|------------------|
| CrawlerService.StartCrawl | 8999 | `crawler.proto`  |
| AnalysisService.Analyze   | 5001 | `analysis.proto` |

协议文件在 `shared/protos/`，Java 和 Python 分别通过 Maven 插件和 `grpc-tools` 生成桩代码。
