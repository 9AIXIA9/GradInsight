"""
数据库连接层 — 合并自 backend/db/single_connection.py + backend/db/mysql.py

提供：
- db_cursor() — 异步上下文管理器，获取数据库游标
- execute_query() — 便捷查询方法
- 连接池生命周期管理
"""

import aiomysql
import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any

from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# ---- 连接池 ----
_connection_pool: Optional[aiomysql.Pool] = None
_pool_lock = asyncio.Lock()
_connection_errors = 0
_MAX_ERRORS_BEFORE_RESET = 5
_POOL_RECYCLE_TIME = 3600  # 1 小时


async def connect_to_mysql() -> aiomysql.Pool:
    """创建或返回 MySQL 连接池"""
    global _connection_pool

    if _connection_pool is not None and not _connection_pool.closed:
        return _connection_pool

    async with _pool_lock:
        if _connection_pool is not None and not _connection_pool.closed:
            return _connection_pool

        try:
            logger.info(f"创建 MySQL 连接池: {settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}")
            _connection_pool = await aiomysql.create_pool(
                host=settings.MYSQL_HOST,
                port=settings.MYSQL_PORT,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASS,
                db=settings.MYSQL_DATABASE,
                charset=settings.MYSQL_CHARSET,
                autocommit=True,
                minsize=2,
                maxsize=10,
                pool_recycle=_POOL_RECYCLE_TIME,
                echo=settings.DEBUG,
                connect_timeout=10,
                loop=asyncio.get_event_loop(),
            )
            logger.info("MySQL 连接池创建成功")
            return _connection_pool
        except Exception as e:
            logger.critical(f"创建 MySQL 连接池失败: {e}")
            raise


async def close_connection_pool():
    """关闭 MySQL 连接池"""
    global _connection_pool
    async with _pool_lock:
        if _connection_pool is not None:
            try:
                logger.info("正在关闭 MySQL 连接池...")
                _connection_pool.close()
                await _connection_pool.wait_closed()
                _connection_pool = None
                logger.info("MySQL 连接池已关闭")
            except Exception as e:
                logger.error(f"关闭 MySQL 连接池失败: {e}")
                _connection_pool = None


async def reset_connection_pool():
    """重置连接池（出错时调用）"""
    global _connection_pool, _connection_errors
    async with _pool_lock:
        logger.warning("正在重置 MySQL 连接池...")
        if _connection_pool is not None:
            try:
                if not _connection_pool.closed:
                    _connection_pool.close()
                    await _connection_pool.wait_closed()
            except Exception as e:
                logger.error(f"关闭旧连接池失败: {e}")
        _connection_pool = None
        _connection_errors = 0
        logger.info("MySQL 连接池已重置")


@asynccontextmanager
async def db_cursor():
    """
    获取数据库游标的异步上下文管理器

    用法:
        async with db_cursor() as cursor:
            await cursor.execute("SELECT ...")
            rows = await cursor.fetchall()
    """
    global _connection_errors
    pool = None
    conn = None
    cursor = None

    try:
        pool = await connect_to_mysql()
        conn = await asyncio.wait_for(pool.acquire(), timeout=10.0)
        cursor = await conn.cursor()
        logger.debug("从连接池获取连接成功")
        yield cursor
        _connection_errors = 0
    except Exception as e:
        _connection_errors += 1
        logger.error(f"数据库连接错误: {e}")
        if _connection_errors >= _MAX_ERRORS_BEFORE_RESET:
            logger.warning("数据库错误次数过多，重置连接池")
            await reset_connection_pool()
        raise
    finally:
        if cursor is not None:
            try:
                await cursor.close()
            except Exception as e:
                logger.error(f"关闭游标失败: {e}")
        if conn is not None and pool is not None:
            try:
                pool.release(conn)
            except Exception as e:
                logger.error(f"归还连接到池失败: {e}")


async def execute_query(query: str, params=None, fetch_type='all'):
    """执行查询的便捷方法"""
    try:
        async with db_cursor() as cursor:
            await cursor.execute(query, params)
            if fetch_type == 'one':
                return await cursor.fetchone()
            elif fetch_type == 'all':
                return await cursor.fetchall()
            else:
                return None
    except Exception as e:
        logger.error(f"查询执行失败: {query[:100]}..., 错误: {e}")
        raise


async def check_db_health() -> bool:
    """检查数据库连接健康状态"""
    try:
        result = await execute_query("SELECT 1 as test", fetch_type='one')
        return result is not None and len(result) > 0 and result[0] == 1
    except Exception as e:
        logger.error(f"数据库健康检查失败: {e}")
        return False
