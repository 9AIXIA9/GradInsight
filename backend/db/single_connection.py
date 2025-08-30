import aiomysql
import asyncio
import logging
import time
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from backend.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# 全局变量 - 使用连接池
_connection_pool: Optional[aiomysql.Pool] = None
_pool_lock = asyncio.Lock()
_connection_errors = 0
_MAX_ERRORS_BEFORE_RESET = 5
_POOL_RECYCLE_TIME = 3600  # 1小时


async def get_connection_pool() -> aiomysql.Pool:
    """
    获取或创建MySQL连接池
    """
    global _connection_pool

    # 首次检查：无需锁
    if _connection_pool is not None and not _connection_pool.closed:
        return _connection_pool

    # 获取锁
    async with _pool_lock:
        # 二次检查：可能在等待锁期间已创建
        if _connection_pool is not None and not _connection_pool.closed:
            return _connection_pool

        # 创建新连接池
        try:
            logger.info(f"正在创建MySQL连接池: {settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}")
            _connection_pool = await aiomysql.create_pool(
                host=settings.MYSQL_HOST,
                port=settings.MYSQL_PORT,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWORD,
                db=settings.MYSQL_DATABASE,
                charset=settings.MYSQL_CHARSET,
                autocommit=True,
                minsize=2,       # 最小连接数
                maxsize=10,      # 最大连接数
                pool_recycle=_POOL_RECYCLE_TIME,  # 连接回收时间
                echo=settings.DEBUG,
                connect_timeout=10,
                loop=asyncio.get_event_loop()
            )
            logger.info(f"MySQL连接池创建成功，连接数范围: 2-10")
            return _connection_pool
        except Exception as e:
            logger.critical(f"创建MySQL连接池失败: {e}")
            logger.critical(f"连接参数: host={settings.MYSQL_HOST}, port={settings.MYSQL_PORT}, user={settings.MYSQL_USER}, db={settings.MYSQL_DATABASE}")
            raise


async def close_connection_pool():
    """
    关闭MySQL连接池
    """
    global _connection_pool
    async with _pool_lock:
        if _connection_pool is not None:
            try:
                logger.info("正在关闭MySQL连接池...")
                _connection_pool.close()
                await _connection_pool.wait_closed()
                _connection_pool = None
                logger.info("MySQL连接池已关闭")
            except Exception as e:
                logger.error(f"关闭MySQL连接池失败: {e}")
                _connection_pool = None


@asynccontextmanager
async def db_cursor():
    """
    获取数据库游标的上下文管理器 - 使用连接池
    """
    global _connection_errors
    pool = None
    conn = None
    cursor = None

    try:
        # 获取连接池
        pool = await get_connection_pool()

        # 从连接池获取连接
        conn = await asyncio.wait_for(pool.acquire(), timeout=10.0)

        # 创建游标
        cursor = await conn.cursor()

        logger.debug("从连接池获取连接成功")
        yield cursor

        # 如果到这里说明操作成功，重置错误计数
        _connection_errors = 0

    except Exception as e:
        # 连接错误处理
        _connection_errors += 1
        logger.error(f"数据库连接错误: {e}")

        # 如果错误达到阈值，尝试重置连接池
        if _connection_errors >= _MAX_ERRORS_BEFORE_RESET:
            logger.warning("数据库错误次数过多，重置连接池")
            await reset_connection_pool()

        raise

    finally:
        # 确保游标被关闭
        if cursor is not None:
            try:
                await cursor.close()
            except Exception as e:
                logger.error(f"关闭游标失败: {e}")

        # 确保连接被归还到池中
        if conn is not None and pool is not None:
            try:
                pool.release(conn)
                logger.debug("连接已归还到连接池")
            except Exception as e:
                logger.error(f"归还连接到池失败: {e}")


async def reset_connection_pool():
    """
    重置MySQL连接池，用于处理连接池异常情况
    """
    global _connection_pool, _connection_errors

    async with _pool_lock:
        logger.warning("正在重置MySQL连接池...")

        # 如果连接池存在，尝试关闭
        if _connection_pool is not None:
            try:
                if not _connection_pool.closed:
                    _connection_pool.close()
                    await _connection_pool.wait_closed()
                logger.info("旧连接池已关闭")
            except Exception as e:
                logger.error(f"关闭旧连接池时出错: {e}")

        # 将连接池设置为None，下次调用时将创建新的连接池
        _connection_pool = None
        _connection_errors = 0
        logger.info("MySQL连接池已重置")


async def execute_query(query: str, params=None, fetch_type='all'):
    """
    执行查询的便捷方法，自动处理连接管理
    """
    try:
        async with db_cursor() as cursor:
            logger.debug(f"执行查询: {query}")
            if params:
                logger.debug(f"查询参数: {params}")

            await cursor.execute(query, params)

            if fetch_type == 'one':
                result = await cursor.fetchone()
                logger.debug(f"查询结果: {result}")
                return result
            elif fetch_type == 'all':
                result = await cursor.fetchall()
                logger.debug(f"查询结果: {len(result) if result else 0} 条记录")
                return result
            else:
                return None
    except Exception as e:
        logger.error(f"查询执行失败: {query[:100]}..., 错误: {e}")
        raise


async def execute_update(query: str, params=None):
    """
    执行更新操作并返回受影响的行数
    """
    start_time = time.time()
    try:
        async with db_cursor() as cursor:
            await cursor.execute(query, params or ())
            affected = cursor.rowcount
            logger.debug(f"更新执行成功: {query[:100]}..., 影响行数: {affected}, 耗时: {time.time() - start_time:.3f}秒")
            return affected
    except Exception as e:
        logger.error(f"执行更新失败: {query[:100]}..., 错误: {e}")
        raise


async def check_db_health() -> bool:
    """
    检查数据库连接池的健康状态
    """
    try:
        result = await execute_query("SELECT 1 as test", fetch_type='one')
        return result is not None and len(result) > 0 and result[0] == 1
    except Exception as e:
        logger.error(f"数据库健康检查失败: {e}")
        return False


async def test_connection():
    """
    测试数据库连接的独立函数
    """
    try:
        logger.info("开始测试数据库连接...")
        health = await check_db_health()
        if health:
            logger.info("数据库连接测试成功")
            return True
        else:
            logger.error("数据库连接测试失败")
            return False
    except Exception as e:
        logger.error(f"数据库连接测试异常: {e}")
        return False


async def get_pool_status() -> Dict[str, Any]:
    """
    获取连接池状态，用于监控
    """
    global _connection_pool

    if _connection_pool is None:
        return {"initialized": False, "message": "连接池未初始化"}

    if _connection_pool.closed:
        return {"initialized": True, "closed": True, "message": "连接池已关闭"}

    try:
        return {
            "initialized": True,
            "closed": False,
            "minsize": _connection_pool.minsize,
            "maxsize": _connection_pool.maxsize,
            "size": _connection_pool.size,
            "freesize": _connection_pool.freesize,
            "usage": f"{(_connection_pool.size - _connection_pool.freesize) / _connection_pool.maxsize * 100:.1f}%"
        }
    except Exception as e:
        logger.error(f"获取连接池状态时出错: {e}")
        return {"initialized": True, "error": str(e), "message": "无法获取连接池详细状态"}

# 为了向后兼容，提供这些别名
get_connection = get_connection_pool
close_connection = close_connection_pool
