import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

import aiomysql

from app.api.models.post import Post, Comment
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class PostService:
    def __init__(self, pool: aiomysql.Pool):
        self.pool = pool

    async def get_posts(self, skip: int = 0, limit: int = None,
                        task_id: Optional[str] = None, keyword: Optional[str] = None,
                        tag: Optional[str] = None, min_likes: Optional[int] = None) -> Dict[str, Any]:
        """获取帖子列表"""
        # 使用配置的默认值
        if limit is None:
            limit = settings.DEFAULT_PAGE_SIZE

        # 限制页面大小
        limit = min(limit, settings.MAX_PAGE_SIZE)

        # 构建查询条件
        where_conditions = []
        params = []

        if task_id:
            where_conditions.append("task_id = %s")
            params.append(task_id)

        if keyword:
            where_conditions.append("(title LIKE %s OR poster LIKE %s)")
            keyword_pattern = f"%{keyword}%"
            params.extend([keyword_pattern, keyword_pattern])

        if tag:
            where_conditions.append("JSON_CONTAINS(tags, %s)")
            params.append(json.dumps(tag))

        if min_likes is not None:
            where_conditions.append("like_count >= %s")
            params.append(min_likes)

        where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # 计算总数
                count_sql = f"SELECT COUNT(*) FROM {settings.MYSQL_POST_TABLE}{where_clause}"
                await cursor.execute(count_sql, params)
                total = (await cursor.fetchone())[0]

                # 查询数据
                # MySQL中降序排序使用DESC而不是-1
                order_direction = "DESC" if settings.POST_SORT_ORDER == -1 else "ASC"

                query_sql = f"""
                SELECT id, task_id, title, poster, post_time as time, 
                       like_count, comment_count, collect_count, location, tags, image_urls
                FROM {settings.MYSQL_POST_TABLE}
                {where_clause}
                ORDER BY {settings.POST_SORT_FIELD} {order_direction}
                LIMIT %s OFFSET %s
                """

                query_params = params + [limit, skip]
                await cursor.execute(query_sql, query_params)
                rows = await cursor.fetchall()

                # 转换数据格式
                posts = []
                post_ids = []

                for row in rows:
                    # 解析JSON字段
                    tags = json.loads(row[9]) if row[9] else []
                    image_urls = json.loads(row[10]) if row[10] else []

                    post = Post(
                        id=row[0],
                        task_id=row[1],
                        title=row[2] or "",
                        poster=row[3] or "",
                        content="",  # MySQL表中没有content字段，设为空字符串
                        time=row[4] or datetime.now(),
                        like_count=row[5] or 0,
                        comment_count=row[6] or 0,
                        collect_count=row[7] or 0,
                        location=row[8],
                        tags=tags,
                        image_urls=image_urls,
                        comments=[]
                    )
                    posts.append(post)
                    post_ids.append(row[0])

                # 如果有帖子，批量查询评论
                if post_ids:
                    await self._load_comments_for_posts(posts, post_ids)

        # 返回结果
        return {
            "posts": posts,
            "total": total,
            "page": skip // limit + 1,
            "page_size": limit
        }

    async def _load_comments_for_posts(self, posts: List[Post], post_ids: List[str]) -> None:
        """为帖子加载评论"""
        # 创建帖子ID到帖子对象的映射
        post_map = {post.id: post for post in posts}

        # 构建评论查询
        placeholders = ",".join(["%s"] * len(post_ids))
        comment_order_direction = "DESC" if settings.COMMENT_SORT_ORDER == -1 else "ASC"

        comment_sql = f"""
        SELECT id, post_id, commenter, content, comment_time as time, 
               like_count, reply_count, location
        FROM {settings.MYSQL_COMMENT_TABLE}
        WHERE post_id IN ({placeholders})
        ORDER BY {settings.COMMENT_SORT_FIELD} {comment_order_direction}
        """

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(comment_sql, post_ids)
                rows = await cursor.fetchall()

                # 为每个帖子添加评论
                for row in rows:
                    post_id = row[1]
                    if post_id in post_map:
                        # 只加载每个帖子的前N条评论
                        if len(post_map[post_id].comments) < settings.COMMENTS_PER_POST:
                            comment = Comment(
                                id=row[0],
                                commenter=row[2] or "",
                                content=row[3] or "",
                                time=row[4] or datetime.now(),
                                like_count=row[5] or 0,
                                reply_count=row[6] or 0,
                                location=row[7]
                            )
                            post_map[post_id].comments.append(comment)
