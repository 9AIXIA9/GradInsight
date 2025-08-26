import logging
from datetime import datetime
from typing import Dict, Optional, Any

import aiomysql

from app.api.models.task import TaskStatus, TaskDetail
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def map_task_status(status_code: int) -> str:
    """将整数状态码映射到字符串状态"""
    status_map = {
        0: "completed",
        1: "failed",
        2: "running",
        3: "pending",
        4: "divided"
    }
    return status_map.get(status_code, "unknown")


class TaskService:
    def __init__(self, pool: aiomysql.Pool):
        self.pool = pool

    async def get_tasks(self, skip: int = 0, limit: int = None,
                        status: Optional[str] = None, keyword: Optional[str] = None) -> Dict[str, Any]:
        """获取任务列表"""
        # 使用配置的默认值
        if limit is None:
            limit = settings.DEFAULT_PAGE_SIZE

        # 限制页面大小
        limit = min(limit, settings.MAX_PAGE_SIZE)

        # 构建查询条件
        where_conditions = []
        params = []

        if status:
            # 将字符串状态转换为整数状态码
            status_code_map = {
                "completed": 0,
                "failed": 1,
                "running": 2,
                "pending": 3,
                "divided": 4
            }
            status_code = status_code_map.get(status)
            if status_code is not None:
                where_conditions.append("status = %s")
                params.append(status_code)

        if keyword:
            where_conditions.append("keyword LIKE %s")
            params.append(f"%{keyword}%")

        where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # 计算总数
                count_sql = f"SELECT COUNT(*) FROM {settings.MYSQL_TASK_TABLE}{where_clause}"
                await cursor.execute(count_sql, params)
                total = (await cursor.fetchone())[0]

                # 查询数据
                order_direction = "DESC" if settings.POST_SORT_ORDER == -1 else "ASC"

                query_sql = f"""
                SELECT id, keyword, site, status, start_time, end_time, posts_collected
                FROM {settings.MYSQL_TASK_TABLE}
                {where_clause}
                ORDER BY start_time {order_direction}
                LIMIT %s OFFSET %s
                """

                query_params = params + [limit, skip]
                await cursor.execute(query_sql, query_params)
                rows = await cursor.fetchall()

                # 转换数据格式
                tasks = []
                for row in rows:
                    task = {
                        "task_id": row[0],
                        "keyword": row[1] or "",
                        "site": row[2] or 0,
                        "status": self._convert_status(row[3] if row[3] is not None else 3),
                        "created_at": row[4] or datetime.now(),
                        "completed_at": row[5],
                        "posts_collected": row[6] or 0
                    }
                    tasks.append(task)

        # 返回结果
        return {
            "tasks": tasks,
            "total": total,
            "page": skip // limit + 1,
            "page_size": limit
        }

    def _convert_status(self, status_code: int) -> str:
        """将状态码转换为字符串表示"""
        status_map = {
            0: "completed",
            1: "failed",
            2: "running",
            3: "pending",
            4: "divided"
        }
        return status_map.get(status_code, "pending")

    async def get_task(self, task_id: str) -> Optional[TaskDetail]:
        """获取任务详情"""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query_sql = f"""
                SELECT id, keyword, site, status, start_time, end_time, posts_collected,
                       post_count, include_comments, min_likes, comments_per_post, 
                       comment_min_likes, include_images, error_msg
                FROM {settings.MYSQL_TASK_TABLE}
                WHERE id = %s
                """

                await cursor.execute(query_sql, [task_id])
                row = await cursor.fetchone()

                if not row:
                    return None

                return TaskDetail(
                    task_id=row[0],
                    keyword=row[1],
                    site=row[2],
                    status=TaskStatus(map_task_status(row[3])),
                    created_at=row[4],
                    completed_at=row[5],
                    posts_collected=row[6] or 0,
                    post_count=row[7],
                    include_comments=bool(row[8]),
                    min_likes=row[9],
                    comments_per_post=row[10],
                    comment_min_likes=row[11],
                    include_images=bool(row[12]),
                    error_message=row[13] if row[13] else None
                )
