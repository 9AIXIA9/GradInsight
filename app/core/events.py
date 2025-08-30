import logging

from fastapi import FastAPI

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


# 创建事件用于具象服务器将遇到的事件
# 实现应用的生命周期管理

async def startup_event(app: FastAPI) -> None:
    """应用启动事件"""
    # 延迟导入避免循环依赖
    from app.db.single_connection import get_connection_pool

    try:
        # 初始化数据库连接池
        pool = await get_connection_pool()
        logger.info("数据库连接池已初始化")
    except Exception as e:
        logger.error(f"初始化数据库连接池失败: {e}")

    # 发现和注册服务到Consul
    try:
        from app.utils.discovery import discover_service

        await discover_service()
        logger.info("服务已注册到Consul")
    except Exception as e:
        logger.warning(f"服务注册失败: {e}")


async def shutdown_event(app: FastAPI) -> None:
    """应用关闭事件"""
    # 延迟导入避免循环依赖
    from app.db.single_connection import close_connection_pool

    try:
        # 关闭数据库连接池
        await close_connection_pool()
        logger.info("数据库连接池已关闭")
    except Exception as e:
        logger.error(f"关闭数据库连接池失败: {e}")
