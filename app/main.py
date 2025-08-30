import sys
import os
import logging
from contextlib import asynccontextmanager

# 将当前目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

from api.routes import crawler
from api.routes import post
from api.routes import task
from api.routes import auth
from api.routes import stats
from core.config import get_settings
from core.events import startup_event, shutdown_event

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

settings = get_settings()

# 调试CORS配置
print(f"CORS Origins: {settings.get_cors_origins()}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动事件
    await startup_event(app)
    yield
    # 关闭事件
    await shutdown_event(app)


# 自定义CORS处理中间件
class CORSDebugMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print(f"Request method: {request.method}")
        print(f"Request URL: {request.url}")
        print(f"Request headers: {dict(request.headers)}")

        # 处理OPTIONS预检请求
        if request.method == "OPTIONS":
            origin = request.headers.get("origin")
            print(f"OPTIONS request from origin: {origin}")

            response = Response()
            response.headers["Access-Control-Allow-Origin"] = origin or "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Max-Age"] = "86400"
            return response

        response = await call_next(request)
        return response

# 创建应用
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
    # 使用默认文档路径
    docs_url="/docs",  # 默认Swagger UI路径
    redoc_url="/redoc",  # 默认ReDoc路径
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,  # 用于控制跨域请求是否可以携带凭据信息（如 cookies、HTTP 认证和客户端 SSL 证书）
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# 添加自定义CORS调试中间件
app.add_middleware(CORSDebugMiddleware)

# 自定义OpenAPI文档
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=f"{settings.APP_NAME} - API文档",
        version=settings.APP_VERSION,
        description="GradInsight API 文档\n\n提供了用于高校数据分析的RESTful接口。\n\n**主要功能**\n\n* 用户认证与授权\n* 爬虫任务管理\n* 高校数据查询\n\n详细的API使用指南请参阅 `/docs` 页面。",
        routes=app.routes,
    )

    # 添加安全定义
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# 配置模板引擎
templates = Jinja2Templates(directory="templates")

# 提供静态文件访问
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception as e:
    logging.error(f"静态文件目录挂载失败: {e}")

# 注册路由
app.include_router(auth.router)  # 添加认证路由
app.include_router(crawler.router)
app.include_router(task.router)
app.include_router(post.router)
app.include_router(stats.router)  # 添加统计API路由

# 添加前端路由 - 必须放在API路由之后
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/{path:path}", response_class=HTMLResponse)
async def serve_frontend(request: Request, path: str):
    # 对API路径的请求不处理，让它们通过API路由处理
    if path.startswith("api/") or path.startswith("docs") or path.startswith("redoc"):
        raise HTTPException(status_code=404)

    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn

    # 运行和管理FastAPI创建的Web应用
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
