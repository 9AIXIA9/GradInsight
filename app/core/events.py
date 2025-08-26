import logging

from fastapi import FastAPI

from app.core.config import get_settings
from app.db.mysql import connect_to_mysql, close_mysql_connection
from app.utils.discovery import discover_service

settings = get_settings()
logger = logging.getLogger(__name__)


# 创建事件用于具象服务器将遇到的事件
# 实现应用的生命周期管理

async def startup_event(app: FastAPI) -> None:
    """应用启动事件"""
    # 连接MySQL
    app.state.mysql_pool = await connect_to_mysql()

    # 服务发现
    crawler_host, crawler_port = await discover_service()
    config = {
        "host": crawler_host,
        "port": crawler_port,
        "timeout": settings.GRPC_TIMEOUT,
        "max_retries": settings.GRPC_MAX_RETRIES
    }
    app.state.crawler_config = config

    # 创建并保存服务实例
    from app.services.crawler_service import CrawlerService
    app.state.crawler_service = CrawlerService(config)

    logger.info(f"爬虫服务配置: {crawler_host}:{crawler_port}")


async def shutdown_event(app: FastAPI) -> None:
    """应用关闭事件"""
    # 关闭数据库连接
    await close_mysql_connection()

    # 关闭grpc连接
    if hasattr(app.state, "crawler_service") and app.state.crawler_service and app.state.crawler_service.client:
        try:
            app.state.crawler_service.client.close()
        except Exception as e:
            logger.error(f"关闭爬虫服务连接失败: {e}")
