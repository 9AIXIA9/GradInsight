"""
GradInsight Analysis Service — 内容分析微服务（gRPC only）

启动:
  python main.py
"""
import logging

from config import get_settings
from grpc_server import serve

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    settings = get_settings()
    server = serve(port=settings.GRPC_PORT)
    logger.info(f"Analysis gRPC service started on :{settings.GRPC_PORT}")
    server.wait_for_termination()
