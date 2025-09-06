import asyncio
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import json
from api.models.post import Post, Comment
from core.config import get_settings
from db.single_connection import db_cursor, execute_query

logger = logging.getLogger(__name__)
settings = get_settings()


class PostService:
    def __init__(self, pool=None):
        # pool参数保留仅为兼容性，实际不再使用
        # 新的代码直接使用single_connection中的长连接
        pass

    async def get_posts(self, skip: int = 0, limit: int = None,
                        task_id: Optional[str] = None, keyword: Optional[str] = None,
                        tag: Optional[str] = None, min_likes: Optional[int] = None,
                        min_comments: Optional[int] = None, sort_by: Optional[str] = None,
                        sort_order: Optional[str] = None) -> Dict[str, Any]:
        """获取帖子列表"""
        try:
            # 记录请求开始
            start_time = datetime.now()
            logger.info(f"开始获取帖子列表: skip={skip}, limit={limit}, task_id={task_id}, keyword={keyword}, tag={tag}, min_likes={min_likes}, min_comments={min_comments}, sort_by={sort_by}, sort_order={sort_order}")

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
                where_conditions.append("(title LIKE %s OR content LIKE %s OR poster LIKE %s)")
                keyword_pattern = f"%{keyword}%"
                params.extend([keyword_pattern, keyword_pattern, keyword_pattern])

            if tag:
                where_conditions.append("JSON_CONTAINS(tags, %s)")
                params.append(json.dumps(tag))

            if min_likes is not None:
                where_conditions.append("like_count >= %s")
                params.append(min_likes)

            if min_comments is not None:
                where_conditions.append("comment_count >= %s")
                params.append(min_comments)

            where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""

            # 排序字段映射
            sort_field_map = {
                "time": "post_time",
                "like_count": "like_count",
                "comment_count": "comment_count",
                "collect_count": "collect_count",
                "hot_score": "hot_score"
            }
            
            # 设置排序字段，默认按时间排序
            if sort_by and sort_by in sort_field_map:
                order_field = sort_field_map[sort_by]
            else:
                order_field = "post_time"
            
            # 设置排序方向，默认降序
            if sort_order and sort_order.lower() in ["asc", "desc"]:
                order_direction = sort_order.upper()
            else:
                order_direction = "DESC"

            logger.warning(f"[DEBUG] 排序参数: sort_by={sort_by}, sort_order={sort_order}, order_field={order_field}, order_direction={order_direction}")

            # 使用单一长连接的游标进行查询
            # 先计算总数
            count_sql = f"SELECT COUNT(*) FROM {settings.MYSQL_POST_TABLE}{where_clause}"

            async with db_cursor() as cursor:
                await cursor.execute(count_sql, params)
                total = (await cursor.fetchone())[0]

                # 如果总数为0，直接返回空结果
                if total == 0:
                    logger.info(f"查询结果为空: {count_sql} {params}")
                    return {
                        "posts": [],  # 改为posts以匹配模型
                        "total": 0,
                        "page": skip // limit + 1 if limit > 0 else 1,
                        "page_size": limit
                    }

                # 查询帖子数据
                query_sql = f"""
                SELECT id, task_id, title, content, poster, post_time as time, 
                       like_count, comment_count, collect_count, location, tags, image_urls, link, hot_score
                FROM {settings.MYSQL_POST_TABLE}
                {where_clause}
                ORDER BY {order_field} {order_direction}
                LIMIT %s OFFSET %s
                """

                query_params = params + [limit, skip]
                logger.warning(f"[DEBUG] 执行SQL查询: {query_sql}")
                logger.warning(f"[DEBUG] 查询参数: {query_params}")

                # 使用同一游标执行查询
                await cursor.execute(query_sql, query_params)
                rows = await cursor.fetchall()

                if not rows:
                    logger.warning(f"查询返回0行结果，但总数为{total}: {query_sql} {query_params}")
                    return {
                        "posts": [],  # 改为posts以匹配模型
                        "total": total,
                        "page": skip // limit + 1 if limit > 0 else 1,
                        "page_size": limit
                    }

                # 转换数据格式
                posts = []
                post_ids = []

                for row in rows:
                    # 解析JSON字段
                    try:
                        tags = json.loads(row[10]) if row[10] else []
                    except json.JSONDecodeError:
                        logger.warning(f"帖子 {row[0]} 的标签JSON解析失败: {row[10]}")
                        tags = []

                    try:
                        image_urls = json.loads(row[11]) if row[11] else []
                    except json.JSONDecodeError:
                        logger.warning(f"帖子 {row[0]} 的图片URL JSON解析失败: {row[11]}")
                        image_urls = []

                    # 处理标题为空的情况，使用内容前20个字符作为标题
                    title = row[2] or ""
                    if not title.strip() and row[3]:  # 如果标题为空但内容不为空
                        content = row[3] or ""
                        # 取内容前20个字符作为标题，去除换行符和多余空格
                        title = content.replace('\n', ' ').replace('\r', ' ').strip()[:20]
                        if len(content) > 20:
                            title += "..."

                    post = Post(
                        id=row[0],
                        task_id=row[1],
                        title=title or "无标题",
                        content=row[3] or "",
                        poster=row[4] or "",
                        time=row[5] or datetime.now(),
                        like_count=row[6] or 0,
                        comment_count=row[7] or 0,
                        collect_count=row[8] or 0,
                        location=row[9],
                        tags=tags,
                        image_urls=image_urls,
                        link=row[12],  # 添加link字段
                        hot_score=float(row[13]) if row[13] is not None else 0.0,  # 添加hot_score字段
                        comments=[]
                    )
                    posts.append(post)
                    post_ids.append(row[0])

                # 如果有帖子，在同一个游标中加载评论
                if post_ids:
                    await self._load_comments_for_posts(cursor, posts, post_ids)

            # 计算查询耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"查询帖子完成: 总数={total}, 返回={len(posts)}, 耗时={elapsed:.3f}秒")

            # 返回结果
            return {
                "posts": posts,  # 改回posts以匹配PostList模型
                "total": total,
                "page": skip // limit + 1 if limit > 0 else 1,
                "page_size": limit
            }

        except Exception as e:
            logger.error(f"查询帖子出错: {e}", exc_info=True)
            # 出错时返回空结果，避免前端崩溃
            return {
                "posts": [],  # 改回posts
                "total": 0,
                "page": 1,
                "page_size": limit or settings.DEFAULT_PAGE_SIZE,
                "error": "数据查询暂时不可用，请稍后再试"
            }

    async def _load_comments_for_posts(self, cursor, posts: List[Post], post_ids: List[str]) -> None:
        """
        为帖子加载评论，使用已存在的数据库游标
        注意：此方法需要在调用者提供的游标上下文中使用
        """
        try:
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

            # 使用传入的游标执行查询
            await cursor.execute(comment_sql, post_ids)
            rows = await cursor.fetchall()

            logger.info(f"加载了 {len(rows)} 条评论，帖子数: {len(post_ids)}")

            # 为每个帖子添加评论
            comment_count = 0
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
                        comment_count += 1

            logger.info(f"成功添加 {comment_count} 条评论到帖子中")

        except Exception as e:
            logger.error(f"加载评论出错: {e}", exc_info=True)
            # 出错时不影响主流程，继续返回帖子数据

    async def calculate_hot_score(self, post_id: str) -> float:
        """计算单个帖子的热度分数"""
        try:
            async with db_cursor() as cursor:
                # 调用存储过程计算热度分数，使用正确的语法
                await cursor.execute("CALL sp_calculate_hot_score(%s, @hot_score)", [post_id])
                
                # 获取输出参数
                await cursor.execute("SELECT @hot_score as hot_score")
                result = await cursor.fetchone()
                
                hot_score = float(result[0]) if result and result[0] is not None else 0.0
                logger.info(f"计算帖子 {post_id} 热度分数: {hot_score}")
                
                return hot_score
                
        except Exception as e:
            logger.error(f"计算帖子热度分数出错: {e}", exc_info=True)
            return 0.0

    async def get_hot_posts(self, limit: int = 20, min_score: float = 0.0) -> List[Dict[str, Any]]:
        """获取热门帖子列表"""
        try:
            # 限制页面大小
            limit = min(limit, settings.MAX_PAGE_SIZE)
            
            async with db_cursor() as cursor:
                # 调用存储过程获取热门帖子
                await cursor.callproc('sp_get_hot_posts', [limit, min_score])
                
                # 获取结果集
                rows = await cursor.fetchall()
                
                hot_posts = []
                for row in rows:
                    post_data = {
                        "id": row[0],
                        "title": row[1],
                        "poster": row[2],
                        "post_time": row[3],
                        "like_count": row[4] or 0,
                        "comment_count": row[5] or 0,
                        "collect_count": row[6] or 0,
                        "hot_score": float(row[7]) if row[7] is not None else 0.0,
                        "task_keyword": row[8],
                        "hours_since_post": row[9] or 0
                    }
                    hot_posts.append(post_data)
                
                logger.info(f"获取热门帖子列表: 返回{len(hot_posts)}个帖子，最低分数:{min_score}")
                return hot_posts
                
        except Exception as e:
            logger.error(f"获取热门帖子列表出错: {e}", exc_info=True)
            return []

    async def update_all_hot_scores(self) -> Dict[str, Any]:
        """批量更新所有帖子的热度分数（需要先添加hot_score字段）"""
        try:
            async with db_cursor() as cursor:
                # 调用存储过程批量计算热度分数
                await cursor.callproc('sp_calculate_all_hot_scores', [0])
                
                # 获取输出参数
                await cursor.execute("SELECT @_sp_calculate_all_hot_scores_0 as updated_count")
                result = await cursor.fetchone()
                
                updated_count = int(result[0]) if result and result[0] is not None else 0
                
                if updated_count >= 0:
                    logger.info(f"批量更新热度分数完成: 更新了{updated_count}个帖子")
                    return {
                        "success": True,
                        "updated_count": updated_count,
                        "message": f"成功更新了 {updated_count} 个帖子的热度分数"
                    }
                else:
                    logger.error("批量更新热度分数失败")
                    return {
                        "success": False,
                        "updated_count": 0,
                        "message": "批量更新热度分数时发生错误"
                    }
                
        except Exception as e:
            logger.error(f"批量更新热度分数出错: {e}", exc_info=True)
            return {
                "success": False,
                "updated_count": 0,
                "message": f"批量更新热度分数失败: {str(e)}"
            }
