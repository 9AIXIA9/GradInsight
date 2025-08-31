import asyncio
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from api.models.task import TaskStatus, TaskDetail
from core.config import get_settings
from db.single_connection import db_cursor

logger = logging.getLogger(__name__)
settings = get_settings()


def map_task_status(status_code: int) -> str:
    """将数据库中的数字状态码映射为字符串状态"""
    # 数据库数字状态码 -> 字符串状态映射
    # 数据库：0=completed, 1=failed, 2=running, 3=pending, 4=divided
    status_map = {
        0: "completed",  # 已完成
        1: "failed",     # 失败
        2: "running",    # 运行中
        3: "pending",    # 等待中
        4: "divided"     # 已分割
    }
    return status_map.get(status_code, "failed")  # 默认为failed


def map_site_code(site_code: int) -> str:
    """将数据库中的数字站点码映射为字符串"""
    # 数��库数字站点码 -> 字符串站点映射
    # 数据库：0=小红书, 1=微博, 2=知乎
    site_map = {
        0: "xiaohongshu",  # 小红书
        1: "weibo",        # 微博
        2: "zhihu"         # 知乎
    }
    return site_map.get(site_code, "xiaohongshu")  # 默认为小红书


class TaskService:
    def __init__(self, pool=None):
        # pool参数保留仅为兼容性，实际不再使用
        # 新的代码直接使用single_connection中的长连接
        pass

    async def get_tasks(self, skip: int = 0, limit: int = None,
                        status: Optional[str] = None, keyword: Optional[str] = None) -> Dict[str, Any]:
        """获取任务列表"""
        try:
            # 记录请求开始
            start_time = datetime.now()
            logger.info(f"开始获取任务列表: skip={skip}, limit={limit}, status={status}, keyword={keyword}")

            # 使用配置的默认值
            if limit is None:
                limit = settings.DEFAULT_PAGE_SIZE

            # 限制页面大小
            limit = min(limit, settings.MAX_PAGE_SIZE)

            # 构建查询条件
            where_conditions = []
            params = []

            if status:
                # 将字符串状态转换为整数状���码
                status_code_map = {
                    "completed": 0,
                    "failed": 1,
                    "running": 2,
                    "pending": 3,
                    "divided": 4
                }
                if status in status_code_map:
                    where_conditions.append("status = %s")
                    params.append(status_code_map[status])

            if keyword:
                where_conditions.append("keyword LIKE %s")
                params.append(f"%{keyword}%")

            where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""

            # 使用单一长连接的游标进行查询
            async with db_cursor() as cursor:
                # 计算总数
                count_sql = f"SELECT COUNT(*) FROM {settings.MYSQL_TASK_TABLE}{where_clause}"
                await cursor.execute(count_sql, params)
                total = (await cursor.fetchone())[0]

                # ��果总数为0，直接返回空结果
                if total == 0:
                    logger.info(f"查询结果为空: {count_sql} {params}")
                    return {
                        "tasks": [],  # API模型期望的是tasks字段
                        "total": 0,
                        "page": skip // limit + 1 if limit > 0 else 1,
                        "page_size": limit
                    }

                # 查询任务数据
                query_sql = f"""
                SELECT id, keyword, site, post_count, include_comments, comments_per_post, 
                       min_likes, comment_min_likes, include_images, status, start_time, end_time, 
                       posts_collected, error_msg
                FROM {settings.MYSQL_TASK_TABLE}
                {where_clause}
                ORDER BY start_time DESC
                LIMIT %s OFFSET %s
                """

                query_params = params + [limit, skip]

                await cursor.execute(query_sql, query_params)
                rows = await cursor.fetchall()

                # 转换数据格式
                tasks = []
                for row in rows:
                    task = {
                        "id": row[0],
                        "task_id": row[0],  # 使用id作为task_id
                        "keyword": row[1],
                        "site": map_site_code(row[2]),  # 转换站点码为字符串
                        "post_count": row[3],
                        "include_comments": bool(row[4]),
                        "comments_per_post": row[5],
                        "min_likes": row[6],
                        "comment_min_likes": row[7],
                        "include_images": bool(row[8]),
                        "status": row[9],  # 直接返回数字状态码，不转换
                        "created_at": row[10],  # start_time
                        "completed_at": row[11],  # end_time
                        "posts_collected": row[12],
                        "error_message": row[13]  # error_msg
                    }
                    tasks.append(task)

            # 计算查询耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"查询任务完成: 总数={total}, 返回={len(tasks)}, 耗时={elapsed:.3f}秒")

            # 返回结果 - 修复数据格式以匹配API模型期望
            return {
                "tasks": tasks,  # API模型期望的是tasks字段，不是items
                "total": total,
                "page": skip // limit + 1 if limit > 0 else 1,
                "page_size": limit
            }
        except Exception as e:
            logger.error(f"查询任务出错: {e}", exc_info=True)
            # 出错时返回空结果
            return {
                "tasks": [],  # API模型期望的是tasks字段
                "total": 0,
                "page": 1,
                "page_size": limit or settings.DEFAULT_PAGE_SIZE,
                "error": "任务查询暂时不可用，请稍后再试"
            }

    async def get_task_detail(self, task_id: str) -> Optional[TaskDetail]:
        """获取任务详情"""
        try:
            logger.info(f"开始获取任务详情: task_id={task_id}")

            # 使用单一长连接的游标进行查询
            async with db_cursor() as cursor:
                query_sql = f"""
                SELECT id, keyword, site, post_count, include_comments, comments_per_post,
                       min_likes, comment_min_likes, include_images, status, start_time, end_time,
                       posts_collected, error_msg
                FROM {settings.MYSQL_TASK_TABLE}
                WHERE id = %s
                """

                await cursor.execute(query_sql, [task_id])
                row = await cursor.fetchone()

                if not row:
                    logger.warning(f"任务不存在: {task_id}")
                    return None

                # 转换数据格式
                task_detail = TaskDetail(
                    id=row[0],
                    task_id=row[0],  # 使用id作为task_id
                    keyword=row[1],
                    site=map_site_code(row[2]),  # 转换站点码为字符串
                    post_count=row[3],
                    include_comments=bool(row[4]),
                    comments_per_post=row[5],
                    min_likes=row[6],
                    comment_min_likes=row[7],
                    include_images=bool(row[8]),
                    status=row[9],  # 保持数字状态码与前端模型一致
                    created_at=row[10],  # start_time
                    completed_at=row[11],  # end_time
                    posts_collected=row[12],
                    error_message=row[13]  # error_msg
                )

                logger.info(f"获取任务详情成功: {task_id}, 状态: {task_detail.status}")
                return task_detail

        except Exception as e:
            logger.error(f"获取任务详情出错: {e}", exc_info=True)
            raise

    async def delete_task(self, task_id: str) -> bool:
        """���除任务"""
        try:
            logger.info(f"开始删除任务: task_id={task_id}")

            async with db_cursor() as cursor:
                delete_sql = f"DELETE FROM {settings.MYSQL_TASK_TABLE} WHERE id = %s"
                await cursor.execute(delete_sql, [task_id])

                # 检查是否有行被删除
                if cursor.rowcount > 0:
                    logger.info(f"任务删除成功: {task_id}")
                    return True
                else:
                    logger.warning(f"任务不存在或删除失败: {task_id}")
                    return False

        except Exception as e:
            logger.error(f"删除任务出错: {e}", exc_info=True)
            raise

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务信息（简化版本）"""
        task_detail = await self.get_task_detail(task_id)
        if task_detail:
            return task_detail.model_dump()
        return None
