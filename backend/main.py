import sys
import os
import logging
from contextlib import asynccontextmanager

# 将当前目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import crawler
from api.routes import post
from api.routes import task
from api.routes import auth
from api.routes import stats
from api.routes import content_analysis
from core.config import get_settings
from core.events import startup_event, shutdown_event

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动事件
    await startup_event(app)
    yield
    # 关闭事件
    await shutdown_event(app)

# 创建应用
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # 前端开发服务器地址
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(auth.router)
app.include_router(crawler.router)
app.include_router(task.router)
app.include_router(post.router)
app.include_router(stats.router)
app.include_router(content_analysis.router)

# 健康检查
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "API服务运行正常"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
