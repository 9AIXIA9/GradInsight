# GradInsight 操作指南

## 项目概述

GradInsight 是一个面向高考生和家长的高校信息与志愿决策辅助平台，由以下几个服务组成：

- **前端（Frontend）**: Vue.js + Vite 构建的用户界面
- **后端 API（Backend）**: FastAPI 构建的 RESTful API 服务
- **爬虫服务（Crawler Service）**: Go + gRPC 实现的数据爬取服务
- **共享数据（Shared）**: 数据库结构和协议定义

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │  Crawler        │
│   (Vue.js)      │◄──►│   (FastAPI)     │◄──►│  (Go gRPC)      │
│   Port: 3000    │    │   Port: 8000    │    │  Port: 8999     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │    MySQL        │    │     Redis       │
                       │   Port: 3306    │    │   Port: 6379    │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │    Consul       │
                       │   Port: 8500    │
                       └─────────────────┘
                                ▼                       │
                       ┌─────────────────┐              │
                       │    MySQL        │              │
                       │   Port: 13306   │◄─────────────┤
                       └─────────────────┘              │
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │     Redis       │
                                               │   Port: 16379   │
                                               └─────────────────┘
```

## 环境要求

### 软件依赖

- **Node.js**: >= 18.0.0
- **Python**: >= 3.8
- **Go**: >= 1.24.1
- **MySQL**: >= 8.0
- **Redis**: >= 6.0（爬虫服务缓存）
- **Consul**: >= 1.0.0（服务发现，可选）
- **Chrome/Chromium**: 最新版本（爬虫服务需要）

## 快速开始

### 1. 基础服务启动

#### 启动 MySQL 服务

确保 MySQL 服务正在运行，创建数据库：

```sql
CREATE DATABASE gradinsight CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 启动 Redis 服务（爬虫服务需要）

```bash
# Windows
redis-server

# Linux/Mac
sudo systemctl start redis
# 或
redis-server /etc/redis/redis.conf
```

#### 启动 Consul 服务（可选，用于服务发现）

```bash
# 开发模式启动
consul agent -dev -client=0.0.0.0
```

### 2. 数据库初始化

#### 执行数据库脚本
按顺序执行以下SQL文件：

```bash
# 基础表结构
mysql -u root -p gradinsight < shared/ddl/users.sql
mysql -u root -p gradinsight < shared/ddl/crawler.sql
mysql -u root -p gradinsight < shared/ddl/content_analysis.sql

# 存储过程、触发器、视图等（可选）
mysql -u root -p gradinsight < shared/ddl/essential/procedures.sql
mysql -u root -p gradinsight < shared/ddl/essential/triggers.sql
mysql -u root -p gradinsight < shared/ddl/essential/views.sql
```

### 3. 环境配置

#### 后端配置

复制并编辑后端环境配置：

```bash
cd backend
cp .env.example .env
```

编辑 `.env` 文件，配置数据库连接等信息：

```env
# 应用配置
APP_NAME=GradInsight
APP_VERSION=1.0.0
APP_DESCRIPTION=高校数据分析平台
DEBUG=true
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# MySQL数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASS=your_mysql_password
MYSQL_DATABASE=gradinsight

# JWT配置
SECRET_KEY=your-super-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Consul服务发现配置
CONSUL_HOST=127.0.0.1
CONSUL_PORT=8500

# 爬虫服务配置
CRAWLER_HOST=127.0.0.1
CRAWLER_PORT=8999

# CORS配置
CORS_ORIGINS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000,http://127.0.0.1:3000
```

#### 前端配置

复制并编辑前端环境配置：

```bash
cd frontend
cp .env.example .env
```

编辑 `.env` 文件：

```env
# API配置
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=GradInsight
```

#### 爬虫服务配置

复制并编辑爬虫服务环境配置：

```bash
cd services/crawler
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 服务器配置
SERVER_LISTEN_ON=0.0.0.0:8999
APP_MODE=dev
LOG_LEVEL=debug

# Consul服务发现配置
CONSUL_HOST=127.0.0.1:8500
CONSUL_SERVICE_KEY=consul-crawler.rpc

# MySQL数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASS=your_mysql_password
MYSQL_DATABASE=gradinsight

# Redis配置（缓存和队列）
REDIS_HOST=127.0.0.1:6379
REDIS_PASS=your_redis_password
REDIS_DB=0

# 缓存Redis配置
CACHE_REDIS_HOST=127.0.0.1
CACHE_REDIS_PORT=6379
CACHE_REDIS_PASSWORD=your_cache_redis_password

# 浏览器配置
RESOURCE_DATA_BASE_PATH=./browser_data
RESOURCE_BROWSER_PATH=/path/to/your_browser.exe
RESOURCE_HEADLESS=false
RESOURCE_MAX_SIZE=5

# 任务队列配置
TASK_QUEUE_MAX_WORKERS=5
TASK_QUEUE_WORK_QUEUE_SIZE=100

# SnowflakeID配置
SNOWFLAKE_MACHINE_NODE=1
```
TASK_QUEUE_WORK_QUEUE_SIZE=100
```

## 服务启动

> **重要提示**：请按照以下顺序启动服务，确保依赖服务先启动

**启动顺序：**
1. MySQL 数据库
2. Redis 缓存服务
3. Consul 服务发现（可选）
4. 后端 API 服务
5. 爬虫 gRPC 服务  
6. 前端应用

### 1. 启动后端 API 服务

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

服务启动后，可访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/api/health

### 2. 启动前端服务

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务启动后，可访问：<http://localhost:3000>

### 3. 启动爬虫服务

```bash
cd services/crawler

# 安装依赖
go mod tidy

# 启动服务
go run crawler.go
```

爬虫服务启动后，监听 gRPC 端口：localhost:8999

## 必需的外部服务

### 1. MySQL 数据库

确保 MySQL 服务运行在端口 13306：

```bash
# 如果使用Docker启动MySQL
docker run --name gradinsight-mysql -e MYSQL_ROOT_PASSWORD=root -p 13306:3306 -d mysql:8.0
```

### 2. Redis 缓存服务

爬虫服务需要 Redis 用于缓存和任务队列：

```bash
# 如果使用Docker启动Redis
docker run --name gradinsight-redis -p 16379:6379 -d redis:6-alpine --requirepass your_redis_password
```

### 3. Consul 服务发现（可选）

如果需要服务发现功能：

```bash
# 如果使用Docker启动Consul
docker run --name gradinsight-consul -p 8500:8500 -d consul:1.9.5
```

## 核心功能使用

### 1. 用户认证

#### 注册新用户
```http
POST /api/auth/register
Content-Type: application/json

{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
}
```

#### 用户登录
```http
POST /api/auth/login
Content-Type: application/json

{
    "username": "testuser",
    "password": "password123"
}
```

### 2. 爬虫任务管理

#### 创建爬虫任务
```http
POST /api/crawler/tasks
Content-Type: application/json
Authorization: Bearer <token>

{
    "platform": "xiaohongshu",
    "keywords": "北京大学",
    "max_posts": 100
}
```

#### 查询任务状态
```http
GET /api/crawler/tasks/{task_id}
Authorization: Bearer <token>
```

### 3. 内容分析

#### 创建分析任务
```http
POST /api/analysis
Content-Type: application/json
Authorization: Bearer <token>

{
    "posts": ["post_id_1", "post_id_2"],
    "analysis_type": "sentiment"
}
```

### 4. 数据查询

#### 获取帖子数据
```http
GET /api/posts?platform=xiaohongshu&keyword=清华大学&page=1&limit=20
Authorization: Bearer <token>
```

#### 获取统计数据
```http
GET /api/stats/platform-summary
Authorization: Bearer <token>
```

## 开发指南

### 前端开发

#### 项目结构
```
frontend/
├── src/
│   ├── components/     # 可复用组件
│   ├── views/         # 页面组件
│   ├── router/        # 路由配置
│   ├── stores/        # 状态管理(Pinia)
│   ├── services/      # API服务
│   └── assets/        # 静态资源
├── public/            # 公共文件
└── dist/             # 构建输出
```

#### 常用命令
```bash
# 开发模式
npm run dev

# 生产构建
npm run build

# 预览构建结果
npm run preview

# 代码检查
npm run lint
```

### 后端开发

#### 项目结构
```
backend/
├── api/
│   ├── models/        # 数据模型
│   └── routes/        # API路由
├── core/              # 核心配置
├── services/          # 业务逻辑
├── db/               # 数据库操作
└── utils/            # 工具函数
```

#### 常用命令
```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python main.py

# 启动uvicorn服务器
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 爬虫服务开发

#### 项目结构

```text
services/crawler/
├── internal/
│   ├── config/       # 配置管理
│   ├── domain/       # 业务领域
│   ├── infra/        # 基础设施
│   ├── control/      # 控制器
│   ├── logic/        # 业务逻辑
│   ├── model/        # 数据模型
│   ├── server/       # gRPC服务器
│   └── svc/          # 服务上下文
├── proto/            # gRPC协议定义
├── etc/              # 配置文件
├── browser_data/     # 浏览器数据目录
└── crawlerservice/   # 服务实现
```

#### 常用命令

```bash
# 安装依赖
go mod tidy

# 生成gRPC代码（如果修改了proto文件）
protoc --go_out=. --go-grpc_out=. shared/protos/*.proto

# 启动服务
go run crawler.go

# 或使用配置文件启动
go run crawler.go -config etc/crawler.yaml -env .env
```

## 部署指南

### 生产环境配置

#### 1. 环境变量配置
- 设置 `DEBUG=false`
- 配置生产数据库连接
- 设置安全的JWT密钥
- 配置正确的CORS域名

#### 2. 前端构建部署
```bash
cd frontend
npm run build
# 将 dist/ 目录部署到 Web 服务器
```

#### 3. 后端服务部署
```bash
cd backend
# 使用 Gunicorn 或 uWSGI 部署
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

#### 4. 爬虫服务部署
```bash
cd services/crawler
go build -o crawler
./crawler
```

### Docker 部署（推荐）

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: gradinsight
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - mysql
    environment:
      - DATABASE_URL=mysql+aiomysql://root:rootpassword@mysql:3306/gradinsight

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  crawler:
    build: ./services/crawler
    ports:
      - "9001:9001"
    depends_on:
      - mysql

volumes:
  mysql_data:
```

启动：
```bash
docker-compose up -d
```

## 监控与维护

### 1. 日志管理
- 后端日志：检查应用日志和错误信息
- 爬虫日志：监控爬取任务状态和异常
- 数据库日志：监控慢查询和错误

### 2. 性能监控
- API响应时间监控
- 数据库查询性能分析
- 爬虫任务执行效率

### 3. 数据备份
- 定期备份MySQL数据库
- 备份重要的配置文件
- 保留关键的日志文件

## 常见问题排查

### 1. 服务启动失败
- 检查端口是否被占用
- 验证环境配置是否正确
- 检查依赖是否完整安装

### 2. 数据库连接问题
- 确认MySQL服务状态
- 检查连接字符串配置
- 验证数据库权限设置

### 3. 爬虫服务异常
- 检查Chrome浏览器安装
- 验证网络连接状态
- 查看反爬虫策略限制

### 4. 前端页面异常
- 检查API服务可用性
- 验证跨域配置
- 查看浏览器控制台错误

## API 文档

### 认证接口
| 方法 | 路径               | 描述             |
| ---- | ------------------ | ---------------- |
| POST | /api/auth/register | 用户注册         |
| POST | /api/auth/login    | 用户登录         |
| POST | /api/auth/logout   | 用户登出         |
| GET  | /api/auth/me       | 获取当前用户信息 |

### 爬虫接口
| 方法   | 路径                    | 描述         |
| ------ | ----------------------- | ------------ |
| POST   | /api/crawler/tasks      | 创建爬虫任务 |
| GET    | /api/crawler/tasks      | 获取任务列表 |
| GET    | /api/crawler/tasks/{id} | 获取任务详情 |
| DELETE | /api/crawler/tasks/{id} | 删除任务     |

### 内容接口
| 方法 | 路径               | 描述         |
| ---- | ------------------ | ------------ |
| GET  | /api/posts         | 获取帖子列表 |
| GET  | /api/posts/{id}    | 获取帖子详情 |
| POST | /api/analysis      | 创建分析任务 |
| GET  | /api/analysis/{id} | 获取分析结果 |

### 统计接口
| 方法 | 路径                        | 描述         |
| ---- | --------------------------- | ------------ |
| GET  | /api/stats/platform-summary | 平台统计摘要 |
| GET  | /api/stats/keyword-trends   | 关键词趋势   |
| GET  | /api/stats/user-activity    | 用户活动统计 |

## 端口配置总览

| 服务     | 端口 | 协议 | 描述              |
| -------- | ---- | ---- | ----------------- |
| 前端应用 | 3000 | HTTP | Vue.js 开发服务器 |
| 后端API  | 8000 | HTTP | FastAPI 服务      |
| 爬虫服务 | 8999 | gRPC | Go 爬虫服务       |
| MySQL    | 3306 | TCP  | 数据库            |
| Redis    | 6379 | TCP  | 缓存服务          |
| Consul   | 8500 | HTTP | 服务发现（可选）  |

## 技术栈详情

### 前端技术栈

- **Vue.js 3**: 渐进式JavaScript框架
- **Vite**: 现代化构建工具
- **Vue Router**: 路由管理
- **Pinia**: 状态管理
- **Axios**: HTTP客户端
- **Bootstrap 5**: UI框架

### 后端技术栈

- **FastAPI**: 现代Python Web框架
- **Pydantic**: 数据验证和设置管理
- **aiomysql**: 异步MySQL数据库驱动
- **python-jose**: JWT令牌处理
- **bcrypt**: 密码加密
- **python-consul**: Consul服务发现客户端
- **grpcio**: gRPC通信框架

### 爬虫技术栈

- **Go**: 高性能编程语言
- **go-zero**: 微服务框架
- **chromedp**: Chrome DevTools Protocol 客户端
- **gRPC**: 高性能RPC框架
- **MySQL**: 数据存储
- **Redis**: 缓存和消息队列
- **Consul**: 服务注册与发现

## 联系与支持

如果遇到问题或需要技术支持，请：

1. 查看本操作指南
2. 检查项目 Issues
3. 查阅 API 文档
4. 联系开发团队

---

*最后更新时间：2025年9月6日*
*版本：v1.0.0*
