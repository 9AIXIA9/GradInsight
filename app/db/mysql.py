import aiomysql
import logging
from typing import Optional

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

_mysql_pool: Optional[aiomysql.Pool] = None


async def connect_to_mysql() -> aiomysql.Pool:
    """连接到MySQL数据库"""
    global _mysql_pool
    if _mysql_pool is None:
        try:
            _mysql_pool = await aiomysql.create_pool(
                host=settings.MYSQL_HOST,
                port=settings.MYSQL_PORT,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWORD,
                db=settings.MYSQL_DATABASE,
                charset=settings.MYSQL_CHARSET,
                autocommit=True,
                minsize=1,
                maxsize=20
            )
            logger.info(f"MySQL连接池创建成功: {settings.MYSQL_HOST}:{settings.MYSQL_PORT}")
        except Exception as e:
            logger.error(f"连接MySQL失败: {e}")
            raise
    return _mysql_pool


async def close_mysql_connection():
    """关闭MySQL连接池"""
    global _mysql_pool
    if _mysql_pool is not None:
        _mysql_pool.close()
        await _mysql_pool.wait_closed()
        _mysql_pool = None
        logger.info("MySQL连接池已关闭")


async def get_mysql_connection():
    """获取MySQL连接"""
    pool = await connect_to_mysql()
    return await pool.acquire()


async def release_mysql_connection(conn):
    """释放MySQL连接"""
    if conn:
        await conn.close()
