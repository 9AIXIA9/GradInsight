"""
GradInsight Analysis Service — 内容分析微服务

独立部署的内容分析服务，通过 REST 供 Java 后端调用。
启动: python main.py  (默认 5000 端口)
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from routes.analysis import router as analysis_router
from db.connection import connect_to_mysql, close_connection_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时：连接数据库
    await connect_to_mysql()
    yield
    # 关闭时：释放数据库连接
    await close_connection_pool()


app = FastAPI(
    title="GradInsight Analysis Service",
    version="1.0.0",
    description="内容分析微服务 — 聚类 / 关键词提取 / 情感分析",
    lifespan=lifespan,
)

app.include_router(analysis_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000)
