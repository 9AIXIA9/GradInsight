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
                       │    Consul       │    │     Redis       │
                       │   Port: 8500    │    │   Port: 6379   │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │    MySQL        │    │ Cache Redis     │
                       │   Port: 3306   │    │   Port: 6379   │
                       └─────────────────┘    └─────────────────┘
```

## 环境要求

### 软件依赖

- **Node.js**: >= 18.0.0
- **Python**: >= 3.8
- **Go**: >= 1.24.1
- **MySQL**: >= 8.0
- **Redis**: >= 6.0（爬虫服务缓存）
- **Consul**: >= 1.0.0
- **Chrome/Chromium**: 最新版本（爬虫服务需要）

## 快速开始

### 基础服务启动

#### 启动 MySQL 服务

确保 MySQL 服务正在运行，创建数据库：

```sql
CREATE DATABASE gradinsight CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 启动 Redis 服务（爬虫服务需要）

#### 启动 Consul 服务（用于服务发现）

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

# 存储过程、触发器、视图
mysql -u root -p gradinsight < shared/ddl/essential/procedures.sql
mysql -u root -p gradinsight < shared/ddl/essential/triggers.sql
mysql -u root -p gradinsight < shared/ddl/essential/views.sql
```

执行后会有默认用户
默认管理员:{
	name:admin,
	password:admin123
}

默认用户:{
	name:testuser,
	password:user123456
}

### 3. 环境配置

#### 后端配置

复制并编辑后端环境配置：

```bash
cd backend
cp .env.example .env
```

#### 前端配置

复制并编辑前端环境配置：

```bash
cd frontend
cp .env.example .env
```

#### 爬虫服务配置

复制并编辑爬虫服务环境配置：

```bash
cd services/crawler
cp .env.example .env
```

## 服务启动

> **重要提示**：请按照以下顺序启动服务，确保依赖服务先启动

**启动顺序：**

1. MySQL 数据库
2. Redis 缓存服务
3. Consul 服务发现
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



## API 文档

### 认证接口

| 方法   | 路径                 | 描述       |
|------|--------------------|----------|
| POST | /api/auth/register | 用户注册     |
| POST | /api/auth/login    | 用户登录     |
| POST | /api/auth/logout   | 用户登出     |
| GET  | /api/auth/me       | 获取当前用户信息 |

### 爬虫接口

| 方法     | 路径                      | 描述     |
|--------|-------------------------|--------|
| POST   | /api/crawler/tasks      | 创建爬虫任务 |
| GET    | /api/crawler/tasks      | 获取任务列表 |
| GET    | /api/crawler/tasks/{id} | 获取任务详情 |
| DELETE | /api/crawler/tasks/{id} | 删除任务   |

### 内容接口

| 方法   | 路径                 | 描述     |
|------|--------------------|--------|
| GET  | /api/posts         | 获取帖子列表 |
| GET  | /api/posts/{id}    | 获取帖子详情 |
| POST | /api/analysis      | 创建分析任务 |
| GET  | /api/analysis/{id} | 获取分析结果 |

### 统计接口

| 方法  | 路径                          | 描述     |
|-----|-----------------------------|--------|
| GET | /api/stats/platform-summary | 平台统计摘要 |
| GET | /api/stats/keyword-trends   | 关键词趋势  |
| GET | /api/stats/user-activity    | 用户活动统计 |

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

## 端口配置总览

| 服务     | 端口   | 协议   | 描述           |
|--------|------|------|--------------|
| 前端应用   | 3000 | HTTP | Vue.js 开发服务器 |
| 后端API  | 8000 | HTTP | FastAPI 服务   |
| 爬虫服务   | 8999 | gRPC | Go 爬虫服务      |
| MySQL  | 3306 | TCP  | 数据库          |
| Redis  | 6379 | TCP  | 缓存服务         |
| Consul | 8500 | HTTP | 服务发现         |

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