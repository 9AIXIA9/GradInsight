# GradInsight API 文档

## 目录

- [简介](#简介)
- [接口基础信息](#接口基础信息)
- [快速开始](#快速开始)
- [认证与授权](#认证与授权)
  - [注册普通用户](#注册普通用户)
  - [用户登录](#用户登录)
  - [创建管理员账户](#创建管理员账户)
  - [获取当前用户信息](#获取当前用户信息)
- [爬虫任务管理](#爬虫任务管理)
  - [创建爬虫任务](#创建爬虫任务)
  - [获取任务列表](#获取任务列表)
  - [获取任务详情](#获取任务详情)
- [高校数据查询](#高校数据查询)
  - [获取帖子列表](#获取帖子列表)
- [错误码说明](#错误码说明)
- [示例代码](#示例代码)

## 简介

GradInsight API 是一套用于高校数据分析的 RESTful 接口，提供用户认证、爬虫任务管理和高校数据查询等功能。本文档详细介绍了每个接口的功能、参数和使用方法，并提供了完整的测试示例。

## 接口基础信息

- **基础 URL**: `http://localhost:8000`
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON
- **时间格式**: ISO 8601 (例如: `2024-01-01T10:00:00`)

## 快速开始

以下是使用 GradInsight API 的基本流程：

1. 注册用户账户
2. 登录并获取访问令牌
3. 使用访问令牌调用其他 API
4. 创建爬虫任务（需要管理员权限）
5. 查询任务状态和数据

## 认证与授权

### 注册普通用户

创建一个新的普通用户账户。

- **URL**: `/api/auth/register`
- **方法**: `POST`
- **权限**: 无需认证
- **Content-Type**: `application/json`

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 | 示例 |
|-------|-----|------|------|------|
| username | string | 是 | 用户名，长度3-50字符 | "testuser" |
| password | string | 是 | 密码，长度至少6位 | "test123456" |
| email | string | 是 | 邮箱地址，必须符合邮箱格式 | "test@example.com" |

**请求示例**:

```json
{
  "username": "testuser",
  "password": "test123456",
  "email": "test@example.com"
}
```

**curl命令**:

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test123456",
    "email": "test@example.com"
  }'
```

**成功响应** (200 OK):

```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00"
}
```

**错误响应**:

- 400 Bad Request: 用户名已存在
```json
{
  "detail": "用户名已存在"
}
```

- 422 Unprocessable Entity: 请求参数验证失败
```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "字符串长度应至少为3个字符",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

### 用户登录

用户登录并获取访问令牌。

- **URL**: `/api/auth/login`
- **方法**: `POST`
- **权限**: 无需认证
- **Content-Type**: `application/x-www-form-urlencoded`

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 | 示例 |
|-------|-----|------|------|------|
| username | string | 是 | 用户名 | "testuser" |
| password | string | 是 | 密码 | "test123456" |

**curl命令**:

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=test123456"
```

**成功响应** (200 OK):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**错误响应**:

- 401 Unauthorized: 用户名或密码错误
```json
{
  "detail": "用户名或密码错误"
}
```

### 创建管理员账户

创建一个新的管理员账户（仅限现有管理员操作）。

- **URL**: `/api/auth/register-admin`
- **方法**: `POST`
- **权限**: 需要管理员权限
- **Content-Type**: `application/json`
- **Authorization**: Bearer Token

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 | 示例 |
|-------|-----|------|------|------|
| username | string | 是 | 用户名，长度3-50字符 | "newadmin" |
| password | string | 是 | 密码，长度至少6位 | "admin123456" |
| email | string | 是 | 邮箱地址，必须符合邮箱格式 | "admin@example.com" |
| role | string | 是 | 用户角色，必须为"admin" | "admin" |

**请求示例**:

```json
{
  "username": "newadmin",
  "password": "admin123456",
  "email": "admin@example.com",
  "role": "admin"
}
```

**curl命令**:

```bash
curl -X POST "http://localhost:8000/api/auth/register-admin" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "username": "newadmin",
    "password": "admin123456",
    "email": "admin@example.com",
    "role": "admin"
  }'
```

**成功响应** (200 OK):

```json
{
  "id": 2,
  "username": "newadmin",
  "email": "admin@example.com",
  "role": "admin",
  "is_active": true,
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00"
}
```

**错误响应**:

- 400 Bad Request: 用户名已存在
```json
{
  "detail": "用户名已存在"
}
```

- 401 Unauthorized: 无效的认证凭据
```json
{
  "detail": "无效的认证凭据"
}
```

- 403 Forbidden: 权限不足
```json
{
  "detail": "权限不足，需要管理员权限"
}
```

### 获取当前用户信息

获取当前登录用户的详细信息。

- **URL**: `/api/auth/me`
- **方法**: `GET`
- **权限**: 需要用户认证
- **Authorization**: Bearer Token

**curl命令**:

```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**成功响应** (200 OK):

```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00"
}
```

**错误响应**:

- 401 Unauthorized: 无效的认证凭据
```json
{
  "detail": "无效的认证凭据"
}
```

## 爬虫任务管理

### 创建爬虫任务

创建一个新的爬虫任务（仅限管理员）。

- **URL**: `/api/crawl`
- **方法**: `POST`
- **权限**: 需要管理员权限
- **Content-Type**: `application/json`
- **Authorization**: Bearer Token

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 | 示例 |
|-------|-----|------|------|------|
| keyword | string | 是 | 搜索关键词 | "计算机科学" |
| site | integer | 是 | 目标网站ID (0: 知乎, 1: 微博) | 0 |
| post_count | integer | 否 | 爬取帖子数量，默认为10 | 20 |
| include_comments | boolean | 否 | 是否包含评论，默认为true | true |
| min_likes | integer | 否 | 最小点赞数，默认为0 | 10 |
| comments_per_post | integer | 否 | 每个帖子爬取的评论数，默认为5 | 10 |
| comment_min_likes | integer | 否 | 评论最小点赞数，默认为0 | 5 |
| include_images | boolean | 否 | 是否包含图片，默认为false | false |

**请求示例**:

```json
{
  "keyword": "计算机科学",
  "site": 0,
  "post_count": 20,
  "include_comments": true,
  "min_likes": 10,
  "comments_per_post": 10,
  "comment_min_likes": 5,
  "include_images": false
}
```

**curl命令**:

```bash
curl -X POST "http://localhost:8000/api/crawl" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "keyword": "计算机科学",
    "site": 0,
    "post_count": 20,
    "include_comments": true,
    "min_likes": 10,
    "comments_per_post": 10,
    "comment_min_likes": 5,
    "include_images": false
  }'
```

**成功响应** (200 OK):

```json
{
  "task_id": "task_12345",
  "status": "pending",
  "message": "爬虫任务已创建，正在处理中"
}
```

**错误响应**:

- 401 Unauthorized: 无效的认证凭据
```json
{
  "detail": "无效的认证凭据"
}
```

- 403 Forbidden: 权限不足
```json
{
  "detail": "权限不足，需要管理员权限"
}
```

- 500 Internal Server Error: 爬虫服务调用失败
```json
{
  "detail": "爬虫服务调用失败: [错误详情]"
}
```

### 获取任务列表

获取爬虫任务列表（需要登录）。

- **URL**: `/api/tasks`
- **方法**: `GET`
- **权限**: 需要用户认证
- **Authorization**: Bearer Token

**查询参数**:

| 参数名 | 类型 | 必填 | 描述 | 示例 |
|-------|-----|------|------|------|
| skip | integer | 否 | 跳过的记录数，默认为0 | 0 |
| limit | integer | 否 | 返回的记录数量，默认为20，最大为100 | 20 |
| status | string | 否 | 任务状态过滤 (completed, failed, running, pending, divided) | "completed" |
| keyword | string | 否 | 关键词过滤 | "计算机" |

**curl命令**:

```bash
curl -X GET "http://localhost:8000/api/tasks?skip=0&limit=20&status=completed&keyword=计算机" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**成功响应** (200 OK):

```json
{
  "tasks": [
    {
      "task_id": "task_12345",
      "keyword": "计算机科学",
      "site": 0,
      "status": "completed",
      "created_at": "2024-01-01T10:00:00",
      "completed_at": "2024-01-01T10:05:00",
      "posts_collected": 20
    },
    ...
  ],
  "total": 35,
  "page": 1,
  "page_size": 20
}
```

**错误响应**:

- 401 Unauthorized: 无效的认证凭据
```json
{
  "detail": "无效的认证凭据"
}
```

### 获取任务详情

获取特定爬虫任务的详细信息（需要登录）。

- **URL**: `/api/tasks/{task_id}`
- **方法**: `GET`
- **权限**: 需要用户认证
- **Authorization**: Bearer Token

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 | 示例 |
|-------|-----|------|------|------|
| task_id | string | 是 | 任务ID | "task_12345" |

**curl命令**:

```bash
curl -X GET "http://localhost:8000/api/tasks/task_12345" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**成功响应** (200 OK):

```json
{
  "task_id": "task_12345",
  "keyword": "计算机科学",
  "site": 0,
  "status": "completed",
  "created_at": "2024-01-01T10:00:00",
  "completed_at": "2024-01-01T10:05:00",
  "posts_collected": 20,
  "post_count": 20,
  "include_comments": true,
  "min_likes": 10,
  "comments_per_post": 10,
  "comment_min_likes": 5,
  "include_images": false,
  "error_message": null
}
```

**错误响应**:

- 401 Unauthorized: 无效的认证凭据
```json
{
  "detail": "无效的认证凭据"
}
```

- 404 Not Found: 任务不存在
```json
{
  "detail": "任务不存在"
}
```

## 高校数据查询

### 获取帖子列表

获取爬虫任务收集的帖子列表（需要登录）。

- **URL**: `/api/posts`
- **方法**: `GET`
- **权限**: 需要用户认证
- **Authorization**: Bearer Token

**查询参数**:

| 参数名 | 类型 | 必填 | 描述 | 示例 |
|-------|-----|------|------|------|
| skip | integer | 否 | 跳过的记录数，默认为0 | 0 |
| limit | integer | 否 | 返回的记录数量，默认为20，最大为100 | 20 |
| task_id | string | 否 | 按任务ID过滤 | "task_12345" |
| keyword | string | 否 | 按标题或发帖者过滤 | "计算机" |
| tag | string | 否 | 按标签过滤 | "学术" |
| min_likes | integer | 否 | 最小点赞数过滤 | 10 |

**curl命令**:

```bash
curl -X GET "http://localhost:8000/api/posts?skip=0&limit=20&task_id=task_12345&min_likes=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**成功响应** (200 OK):

```json
{
  "posts": [
    {
      "id": "post_67890",
      "task_id": "task_12345",
      "title": "浅谈计算机科学的未来发展",
      "poster": "张三",
      "content": "随着人工智能的发展...",
      "time": "2024-01-01T08:00:00",
      "like_count": 150,
      "comment_count": 25,
      "collect_count": 30,
      "location": "北京",
      "tags": ["学术", "计算机", "人工智能"],
      "image_urls": [],
      "comments": [
        {
          "id": "comment_12345",
          "commenter": "李四",
          "content": "非常赞同您的观点",
          "time": "2024-01-01T08:30:00",
          "like_count": 20,
          "reply_count": 5,
          "location": "上海"
        },
        ...
      ]
    },
    ...
  ],
  "total": 42,
  "page": 1,
  "page_size": 20
}
```

**错误响应**:

- 401 Unauthorized: 无效的认证凭据
```json
{
  "detail": "无效的认证凭据"
}
```

## 错误码说明

| 状态码 | 错误类型 | 描述 |
|-------|---------|------|
| 400 | Bad Request | 请求参数错误或资源已存在 |
| 401 | Unauthorized | 认证失败或认证凭据无效 |
| 403 | Forbidden | 权限不足，无法执行操作 |
| 404 | Not Found | 请求的资源不存在 |
| 422 | Unprocessable Entity | 请求参数验证失败 |
| 500 | Internal Server Error | 服务器内部错误 |

## 示例代码

### Python 示例

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. 用户注册
def register_user():
    data = {
        "username": "testuser",
        "password": "test123456",
        "email": "test@example.com"
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
    print(f"注册结果: {response.status_code}")
    print(response.json())
    return response.json()

# 2. 用户登录
def login_user(username, password):
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", data=data)
    print(f"登录结果: {response.status_code}")
    result = response.json()
    print(f"Token: {result.get('access_token')}")
    return result.get('access_token')

# 3. 获取用户信息
def get_user_info(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    print(f"用户信息: {response.status_code}")
    print(response.json())

# 4. 获取任务列表
def get_tasks(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/tasks", headers=headers)
    print(f"任务列表: {response.status_code}")
    print(response.json())

# 执行测试
if __name__ == "__main__":
    # 注册新用户
    # user = register_user()
    
    # 登录获取令牌
    token = login_user("testuser", "test123456")
    
    # 获取用户信息
    get_user_info(token)
    
    # 获取任务列表
    get_tasks(token)
```

### JavaScript 示例

```javascript
const BASE_URL = "http://localhost:8000";

// 1. 用户注册
async function registerUser() {
  const data = {
    username: "testuser",
    password: "test123456",
    email: "test@example.com"
  };
  
  try {
    const response = await fetch(`${BASE_URL}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    
    const result = await response.json();
    console.log(`注册结果: ${response.status}`);
    console.log(result);
    return result;
  } catch (error) {
    console.error('注册失败:', error);
  }
}

// 2. 用户登录
async function loginUser(username, password) {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  
  try {
    const response = await fetch(`${BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: formData
    });
    
    const result = await response.json();
    console.log(`登录结果: ${response.status}`);
    console.log(`Token: ${result.access_token}`);
    return result.access_token;
  } catch (error) {
    console.error('登录失败:', error);
  }
}

// 3. 获取用户信息
async function getUserInfo(token) {
  try {
    const response = await fetch(`${BASE_URL}/api/auth/me`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const result = await response.json();
    console.log(`用户信息: ${response.status}`);
    console.log(result);
  } catch (error) {
    console.error('获取用户信息失败:', error);
  }
}

// 4. 获取任务列表
async function getTasks(token) {
  try {
    const response = await fetch(`${BASE_URL}/api/tasks`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const result = await response.json();
    console.log(`任务列表: ${response.status}`);
    console.log(result);
  } catch (error) {
    console.error('获取任务列表失败:', error);
  }
}

// 执行测试
(async () => {
  // 注册新用户
  // await registerUser();
  
  // 登录获取令牌
  const token = await loginUser("testuser", "test123456");
  
  // 获取用户信息
  await getUserInfo(token);
  
  // 获取任务列表
  await getTasks(token);
})();
```
