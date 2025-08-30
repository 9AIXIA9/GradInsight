import aiomysql
import logging
import asyncio
from typing import Optional, Dict, Any

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

_mysql_pool: Optional[aiomysql.Pool] = None
_pool_lock = asyncio.Lock()  # 用于同步连接池的创建


async def connect_to_mysql() -> aiomysql.Pool:
    """连接到MySQL数据库"""
    global _mysql_pool

    # 如果已经存在连接池并且没有关闭，直接返回
    if _mysql_pool is not None and not _mysql_pool.closed:
        return _mysql_pool

    # 使用锁确保连接池只被创建一次
    async with _pool_lock:
        # 再次检查连接池是否已经被创建（可能在等待锁的过程中被其他协程创建）
        if _mysql_pool is not None and not _mysql_pool.closed:
            return _mysql_pool

        try:
            logger.info("正在创建MySQL连接池...")
            _mysql_pool = await aiomysql.create_pool(
                host=settings.MYSQL_HOST,
                port=settings.MYSQL_PORT,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWORD,
                db=settings.MYSQL_DATABASE,
                charset=settings.MYSQL_CHARSET,
                autocommit=True,
                minsize=2,       # 降低最小连接数
                maxsize=10,      # 降低最大连接数
                pool_recycle=3600,  # 连接回收时间，每1小时回收一次
                echo=settings.DEBUG,  # 调试模式下打印SQL语句
                loop=asyncio.get_event_loop(),  # 明确指定事件循环
                # 添加连接超时配置
                connect_timeout=10,  # 连接超时时间
                # 添加ping检查
                ping_interval=300,   # 5分钟ping一次检查连接
            )
            logger.info(f"MySQL连接池创建成功: {settings.MYSQL_HOST}:{settings.MYSQL_PORT}, 连接数范围: {2}-{10}")

            # 初始检查连接池状态
            pool_status = await get_pool_status()
            logger.info(f"连接池初始状态: {pool_status}")

            return _mysql_pool
        except Exception as e:
            logger.error(f"连接MySQL失败: {e}")
            raise


async def close_mysql_connection():
    """关闭MySQL连接池"""
    global _mysql_pool
    if _mysql_pool is not None:
        logger.info("开始关闭MySQL连接池...")
        pool_status = await get_pool_status()
        logger.info(f"关闭前连接池状态: {pool_status}")

        _mysql_pool.close()
        await _mysql_pool.wait_closed()
        _mysql_pool = None
        logger.info("MySQL连接池已关闭")


async def get_mysql_connection(retry_count=0, max_retries=2):
    """获取MySQL连接，支持自动重试"""
    try:
        pool = await connect_to_mysql()

        # 检查连接池状态
        if pool.closed:
            logger.warning("连接池已关闭，正在重新创建...")
            await reset_connection_pool()
            pool = await connect_to_mysql()

        # 设置更长的获取连接超时时间，避免频繁超时
        conn = await asyncio.wait_for(pool.acquire(), timeout=10.0)
        logger.debug("已从连接池获取MySQL连接")

        # 验证连接是否可用
        try:
            async with conn.cursor() as test_cursor:
                await test_cursor.execute("SELECT 1")
                await test_cursor.fetchone()
        except Exception as test_e:
            logger.warning(f"连接验证失败: {test_e}")
            # 如果连接验证失败，释放连接并抛出异常
            try:
                pool.release(conn)
            except:
                pass
            raise

        return conn
    except asyncio.TimeoutError:
        if retry_count < max_retries:
            logger.warning(f"获取MySQL连接超时，正在重试... ({retry_count + 1}/{max_retries})")
            # 延迟重试，避免立即重试导致的问题
            await asyncio.sleep(1.0 * (retry_count + 1))
            return await get_mysql_connection(retry_count + 1, max_retries)
        else:
            logger.error("获取MySQL连接超时，重试次数已达上限")
            # 尝试重置连接池
            await reset_connection_pool()
            raise Exception("数据库连接不可用，请稍后再试")
    except Exception as e:
        logger.error(f"获取MySQL连接失败: {e}")
        if retry_count < max_retries:
            logger.warning(f"正在重试获取MySQL连接... ({retry_count + 1}/{max_retries})")
            await asyncio.sleep(1.0 * (retry_count + 1))
            return await get_mysql_connection(retry_count + 1, max_retries)
        raise


async def release_mysql_connection(conn):
    """释放MySQL连接"""
    global _mysql_pool
    # 如果连接为None，直接返回
    if conn is None:
        logger.debug("尝试释放空连接，已忽略")
        return

    try:
        # 确保连接池存在且未关闭
        if _mysql_pool is not None and not _mysql_pool.closed:
            _mysql_pool.release(conn)
            logger.debug("MySQL连接已返回到连接池")
        else:
            # 如果连接池不存在或已关闭，尝试直接关闭连接
            if not conn.closed:
                conn.close()
            logger.debug("连接池不可用，MySQL连接已直接关闭")
    except Exception as e:
        logger.error(f"释放MySQL连接时出错: {e}")
        # 作为备选方案，尝试直接关闭连接
        try:
            if not conn.closed:
                conn.close()
            logger.debug("MySQL连接已直接关闭")
        except Exception as close_err:
            logger.error(f"关闭MySQL连接失败: {close_err}")
        # 不抛出异常，避免影响主流程


async def reset_connection_pool():
    """重置连接池，用于处理连接池异常情况"""
    global _mysql_pool

    logger.warning("正在重置MySQL连接池...")

    # 使用锁确保重置过程是线程安全的
    async with _pool_lock:
        # 如果连接池存在，尝试关闭
        if _mysql_pool is not None:
            try:
                if not _mysql_pool.closed:
                    _mysql_pool.close()
                    await _mysql_pool.wait_closed()
            except Exception as e:
                logger.error(f"关闭旧连接池时出错: {e}")

        # 将连接池设置为None，下次调用connect_to_mysql时将创建新的连接池
        _mysql_pool = None
        logger.info("MySQL连接池已重置")


async def get_pool_status() -> Dict[str, Any]:
    """获取连接池状态，用于监控"""
    global _mysql_pool

    if _mysql_pool is None:
        return {"initialized": False, "message": "连接池未初始化"}

    if _mysql_pool.closed:
        return {"initialized": True, "closed": True, "message": "连接池已关闭"}

    try:
        return {
            "initialized": True,
            "closed": False,
            "minsize": _mysql_pool.minsize,
            "maxsize": _mysql_pool.maxsize,
            "size": _mysql_pool.size,
            "freesize": _mysql_pool.freesize,
            "usage": f"{(_mysql_pool.size - _mysql_pool.freesize) / _mysql_pool.maxsize * 100:.1f}%"
        }
    except Exception as e:
        logger.error(f"获取连接池状态时出错: {e}")
        return {"initialized": True, "error": str(e), "message": "无法获取连接池详细状态"}
