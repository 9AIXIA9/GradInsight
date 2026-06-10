"""
GradInsight Analysis Service — 内容分析微服务

启动方式:
  python main.py          # gRPC:5001 + REST:5000
  python main.py --grpc-only   # 仅 gRPC:5001
"""
import argparse
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from db.connection import connect_to_mysql, close_connection_pool
from routes.analysis import router as analysis_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mysql()
    yield
    await close_connection_pool()


app = FastAPI(
    title="GradInsight Analysis Service",
    version="2.0.0",
    lifespan=lifespan,
)
app.include_router(analysis_router)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--grpc-only", action="store_true")
    args = parser.parse_args()

    from grpc_server import serve

    server = serve(port=5001)
    logger.info("gRPC server started on port 5001")

    if args.grpc_only:
        logger.info("gRPC-only mode, press Ctrl+C to stop")
        server.wait_for_termination()
    else:
        import uvicorn
        logger.info("Starting REST on port 5000...")
        uvicorn.run(app, host="0.0.0.0", port=5000)
        server.stop(grace=None)
