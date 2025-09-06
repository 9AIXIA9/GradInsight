from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from datetime import datetime, timedelta

from api.models.requests import CrawlRequest
from api.models.response import CrawlResponse, ResponseModel
from api.models.task import TaskListResponse, TaskDetail
from api.models.user import User
from core.auth import get_admin_user, get_current_user
from core.config import get_settings
from services.crawler_service import CrawlerService
from services.task_service import TaskService
from utils.consul_discovery import ConsulServiceDiscovery, ConsulConfig
from db.single_connection import db_cursor
import logging

router = APIRouter(prefix="/api/crawler", tags=["crawler-management"])
logger = logging.getLogger(__name__)

# 获取设置
settings = get_settings()


def get_crawler_service() -> CrawlerService:
    """依赖注入：获取爬虫服务"""
    # 构建爬虫服务配置
    config = {
        "host": settings.CRAWLER_HOST,
        "port": settings.CRAWLER_PORT,
        "timeout": settings.GRPC_TIMEOUT,
        "max_retries": settings.GRPC_MAX_RETRIES
    }
    return CrawlerService(config)


def get_task_service() -> TaskService:
    """依赖注入：获取任务服务"""
    return TaskService()


def get_consul_discovery() -> ConsulServiceDiscovery:
    """依赖注入：获取Consul服务发现"""
    consul_config = ConsulConfig(
        host=settings.CONSUL_HOST,
        port=settings.CONSUL_PORT,
        timeout=settings.CONSUL_TIMEOUT
    )
    return ConsulServiceDiscovery(consul_config)


@router.post("/start", response_model=CrawlResponse, summary="启动爬虫任务")
async def start_crawl(
    request_data: CrawlRequest,
    crawler_service: CrawlerService = Depends(get_crawler_service),
    current_user: User = Depends(get_admin_user)  # 只有管理��可以启动爬虫任务
):
    """
    启动新的爬虫任务（仅管理员）

    此接口用于启动新的爬虫任务，只有管理员权限的用户才能调用。
    启动后会返回任务ID和状态信息。
    """
    try:
        result = await crawler_service.start_crawl(request_data.model_dump())
        return CrawlResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"爬虫服务调用失败: {str(e)}")


@router.get("/tasks", response_model=TaskListResponse, summary="获取爬虫任务列表")
async def list_tasks(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数量"),
    status: Optional[str] = Query(None, description="任务状态过滤"),
    keyword: Optional[str] = Query(None, description="关键词过滤"),
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_admin_user)  # 只有管理员才能查看任务列表
):
    """
    获取爬虫任务列表（仅限管理员）

    此接口用于获取系统中的爬虫任务列表，包含分页、状态过滤和关键词搜索功能。
    普通用户无权访问此接口，仅限管理员使用。
    """
    try:
        result = await task_service.get_tasks(skip, limit, status, keyword)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {str(e)}")


@router.get("/tasks/{task_id}", response_model=TaskDetail, summary="获取爬虫任务详情")
async def get_task(
    task_id: str,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_admin_user)  # 只有管理员才能查看任务详情
):
    """
    获取爬虫任务详情（仅限管理员）

    此接口用于获取特定爬虫任务的详细信息。
    普通用户无权访问此接口，仅限管理员使用。
    """
    try:
        task = await task_service.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        return task
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务详情失败: {str(e)}")


@router.delete("/tasks/{task_id}", summary="删除爬虫任务")
async def delete_task(
    task_id: str,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_admin_user)  # 只有管理员才能删除任务
):
    """
    删除爬虫任务（仅限管理员）

    此接口用于删除指定的爬虫任务。
    普通用户无权访问此接口，仅限管理员使用。
    """
    try:
        success = await task_service.delete_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="任务不存在")
        return {"message": "任务删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除任务失败: {str(e)}")


@router.get("/status", summary="获取爬虫服务状态")
async def get_crawler_status(
    consul_discovery: ConsulServiceDiscovery = Depends(get_consul_discovery),
    current_user: User = Depends(get_admin_user)  # 只有管理员才能查看服务状态
):
    """
    获取爬虫服务状态（仅限管理员）

    此接口通过Consul服务发现来获取爬虫微服务的运行状态信息。
    普通用户无权访问此接口，仅限管理员使用。
    """
    try:
        # 通过Consul查询爬虫服务状态
        service_name = settings.CRAWLER_SERVICE_NAME
        status = consul_discovery.get_service_health(service_name)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取服务状态失败: {str(e)}")


# ===== 新增的增强功能 =====

@router.get("/tasks/overview", response_model=ResponseModel)
async def get_tasks_overview(
    limit: int = Query(20, ge=1, le=100, description="返回的记录数量"),
    current_user: User = Depends(get_current_user)
) -> ResponseModel:
    """获取任务概览 - 使用直接数据库查询替代视图"""
    try:
        async with db_cursor() as cursor:
            # 直接查询任务信息和统计数据
            await cursor.execute("""
                SELECT 
                    t.id, 
                    t.keyword, 
                    t.posts_collected,
                    t.status,
                    CASE t.status 
                        WHEN 0 THEN '已完成'
                        WHEN 1 THEN '失败'
                        WHEN 2 THEN '运行中'
                        WHEN 3 THEN '待处理'
                        WHEN 4 THEN '分治'
                        ELSE '未知'
                    END as status_desc,
                    t.start_time,
                    t.end_time,
                    CASE 
                        WHEN t.end_time IS NOT NULL AND t.start_time IS NOT NULL 
                        THEN TIMESTAMPDIFF(SECOND, t.start_time, t.end_time)
                        ELSE NULL 
                    END as duration_seconds,
                    t.site
                FROM tasks t
                ORDER BY t.start_time DESC 
                LIMIT %s
            """, [limit])
            results = await cursor.fetchall()
            
            tasks = []
            for row in results:
                (task_id, keyword, posts_collected, status, status_desc, 
                 start_time, end_time, duration_seconds, site) = row
                
                tasks.append({
                    "id": task_id,
                    "keyword": keyword,
                    "collected_posts": posts_collected,
                    "status": status,
                    "status_description": status_desc,
                    "start_time": start_time.isoformat() if start_time else None,
                    "end_time": end_time.isoformat() if end_time else None,
                    "duration_seconds": duration_seconds,
                    "site": site
                })
            
            return ResponseModel(success=True, data=tasks, message="任务概览获取成功")
            
    except Exception as e:
        logger.error(f"获取任务概览失败: {e}")
        raise HTTPException(status_code=500, detail="获取任务概览失败")


@router.get("/tasks/stats", response_model=ResponseModel)
async def get_task_statistics(
    current_user: User = Depends(get_current_user)
) -> ResponseModel:
    """获取任务统计信息 - 使用直接查询替代统计视图"""
    try:
        async with db_cursor() as cursor:
            # 获取任务状态统计
            await cursor.execute("""
                SELECT 
                    COUNT(*) as total_tasks,
                    SUM(CASE WHEN status = 0 THEN 1 ELSE 0 END) as completed_tasks,
                    SUM(CASE WHEN status = 1 THEN 1 ELSE 0 END) as failed_tasks,
                    SUM(CASE WHEN status = 2 THEN 1 ELSE 0 END) as running_tasks,
                    SUM(CASE WHEN status = 3 THEN 1 ELSE 0 END) as pending_tasks,
                    SUM(CASE WHEN status = 4 THEN 1 ELSE 0 END) as divided_tasks,
                    ROUND(
                        SUM(CASE WHEN status = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
                    ) as success_rate
                FROM tasks
            """)
            status_stats = await cursor.fetchone()
            
            # 获取关键词热度统计
            await cursor.execute("""
                SELECT 
                    t.keyword,
                    COUNT(t.id) as task_count,
                    SUM(t.posts_collected) as total_posts_collected,
                    ROUND(
                        SUM(CASE WHEN t.status = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(t.id), 2
                    ) as success_rate
                FROM tasks t
                WHERE t.start_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                GROUP BY t.keyword
                ORDER BY total_posts_collected DESC
                LIMIT 10
            """)
            popular_keywords = await cursor.fetchall()
            
            # 获取最近7天的性能趋势
            await cursor.execute("""
                SELECT 
                    DATE(t.start_time) as task_date,
                    COUNT(t.id) as total_tasks,
                    SUM(t.posts_collected) as total_posts_collected,
                    ROUND(AVG(t.posts_collected), 2) as avg_posts_per_task,
                    SUM(CASE WHEN t.status = 0 THEN 1 ELSE 0 END) as successful_tasks
                FROM tasks t
                WHERE t.start_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                GROUP BY DATE(t.start_time)
                ORDER BY task_date DESC
            """)
            performance_trend = await cursor.fetchall()
            
            stats_data = {}
            
            if status_stats:
                (total_tasks, completed_tasks, failed_tasks, running_tasks,
                 pending_tasks, divided_tasks, success_rate) = status_stats
                
                stats_data["status_overview"] = {
                    "total_tasks": total_tasks or 0,
                    "completed": completed_tasks or 0,
                    "failed": failed_tasks or 0,
                    "running": running_tasks or 0,
                    "pending": pending_tasks or 0,
                    "divided": divided_tasks or 0,
                    "success_rate": success_rate or 0
                }
            
            stats_data["popular_keywords"] = [
                {
                    "keyword": keyword,
                    "task_count": task_count,
                    "total_posts": total_posts,
                    "success_rate": success_rate or 0
                }
                for keyword, task_count, total_posts, success_rate in popular_keywords
            ]
            
            stats_data["performance_trend"] = [
                {
                    "date": task_date.isoformat() if task_date else None,
                    "total_tasks": total_tasks or 0,
                    "total_posts": total_posts or 0,
                    "avg_posts_per_task": avg_posts or 0,
                    "successful_tasks": successful_tasks or 0
                }
                for task_date, total_tasks, total_posts, avg_posts, successful_tasks in performance_trend
            ]
            
            return ResponseModel(success=True, data=stats_data, message="任务统计获取成功")
            
    except Exception as e:
        logger.error(f"获取任务统计失败: {e}")
        raise HTTPException(status_code=500, detail="获取任务统计失败")


@router.get("/tasks/{task_id}/details", response_model=ResponseModel)
async def get_task_details_enhanced(
    task_id: str,
    current_user: User = Depends(get_current_user)
) -> ResponseModel:
    """获取任务详细信息 - 使用直接查询替代存储过程"""
    try:
        async with db_cursor() as cursor:
            # 获取主任务信息
            await cursor.execute("""
                SELECT 
                    id, parent_id, keyword, posts_collected, site, status,
                    CASE status 
                        WHEN 0 THEN '已完成'
                        WHEN 1 THEN '失败'
                        WHEN 2 THEN '运行中'
                        WHEN 3 THEN '待处理'
                        WHEN 4 THEN '分治'
                        ELSE '未知'
                    END as status_desc,
                    start_time, end_time, error_msg,
                    CASE 
                        WHEN end_time IS NOT NULL AND start_time IS NOT NULL 
                        THEN TIMESTAMPDIFF(SECOND, start_time, end_time)
                        ELSE NULL 
                    END as duration_seconds
                FROM tasks 
                WHERE id = %s
            """, [task_id])
            
            main_task = await cursor.fetchone()
            if not main_task:
                raise HTTPException(status_code=404, detail="任务不存在")
            
            # 获取该任务的帖子统计
            await cursor.execute("""
                SELECT COUNT(*) as actual_posts_in_db
                FROM posts 
                WHERE task_id = %s
            """, [task_id])
            post_count_result = await cursor.fetchone()
            actual_posts_in_db = post_count_result[0] if post_count_result else 0
            
            # 获取该任务的评论统计
            await cursor.execute("""
                SELECT COUNT(*) as total_comments
                FROM comments c
                JOIN posts p ON c.post_id = p.id
                WHERE p.task_id = %s
            """, [task_id])
            comment_count_result = await cursor.fetchone()
            total_comments_in_db = comment_count_result[0] if comment_count_result else 0
            
            # 获取子任务信息（如果有）
            await cursor.execute("""
                SELECT 
                    id, keyword, status,
                    CASE status 
                        WHEN 0 THEN '已完成'
                        WHEN 1 THEN '失败'
                        WHEN 2 THEN '运行中'
                        WHEN 3 THEN '待处理'
                        WHEN 4 THEN '分治'
                        ELSE '未知'
                    END as status_desc,
                    posts_collected, start_time, end_time
                FROM tasks 
                WHERE parent_id = %s
            """, [task_id])
            sub_tasks = await cursor.fetchall()
            
            (task_id, parent_id, keyword, posts_collected, site, status,
             status_desc, start_time, end_time, error_msg, duration_seconds) = main_task
            
            task_data = {
                "id": task_id,
                "parent_id": parent_id,
                "keyword": keyword,
                "collected_posts": posts_collected,
                "actual_posts_in_db": actual_posts_in_db,
                "total_comments": total_comments_in_db,
                "site": site,
                "status": status,
                "status_description": status_desc,
                "start_time": start_time.isoformat() if start_time else None,
                "end_time": end_time.isoformat() if end_time else None,
                "duration_seconds": duration_seconds,
                "error_message": error_msg,
                "sub_tasks": [
                    {
                        "id": sub_id,
                        "keyword": sub_keyword,
                        "status": sub_status,
                        "posts_collected": sub_posts,
                        "status_description": sub_status_desc,
                        "start_time": sub_start.isoformat() if sub_start else None,
                        "end_time": sub_end.isoformat() if sub_end else None
                    }
                    for sub_id, sub_keyword, sub_status, sub_status_desc, sub_posts, sub_start, sub_end in sub_tasks
                ]
            }
            
            return ResponseModel(success=True, data=task_data, message="任务详情获取成功")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取任务详情失败: {e}")
        raise HTTPException(status_code=500, detail="获取任务详情失败")


@router.get("/posts/popular", response_model=ResponseModel)
async def get_popular_posts(
    limit: int = Query(10, ge=1, le=50, description="返回的记录数量"),
    current_user: User = Depends(get_current_user)
) -> ResponseModel:
    """获取热门帖子 - 使用直接查询替代视图"""
    try:
        async with db_cursor() as cursor:
            await cursor.execute("""
                SELECT 
                    p.id, p.task_id, 
                    SUBSTRING(p.title, 1, 100) as title_preview,
                    p.poster, p.post_time, p.location,
                    p.like_count, p.comment_count, p.collect_count,
                    -- 简单的热度评分计算
                    (p.like_count * 1.0 + p.comment_count * 2.0 + p.collect_count * 3.0) as popularity_score,
                    p.link
                FROM posts p
                WHERE p.post_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                ORDER BY popularity_score DESC, p.like_count DESC
                LIMIT %s
            """, [limit])
            
            results = await cursor.fetchall()
            
            posts = []
            for row in results:
                (post_id, task_id, title, poster, post_time, location,
                 likes, comments, collects, popularity, link) = row
                
                posts.append({
                    "id": post_id,
                    "task_id": task_id,
                    "title": title,
                    "poster": poster,
                    "post_time": post_time.isoformat() if post_time else None,
                    "location": location,
                    "stats": {
                        "likes": likes or 0,
                        "comments": comments or 0,
                        "collects": collects or 0,
                        "popularity_score": round(popularity or 0, 2)
                    },
                    "link": link
                })
            
            return ResponseModel(success=True, data=posts, message="热门帖子获取成功")
            
    except Exception as e:
        logger.error(f"获取热门帖子失败: {e}")
        raise HTTPException(status_code=500, detail="获取热门帖子失败")


@router.get("/analysis/performance", response_model=ResponseModel)
async def get_performance_report(
    days: int = Query(30, ge=1, le=365, description="分析的天数"),
    current_user: User = Depends(get_admin_user)
) -> ResponseModel:
    """获取性能分析报告 - 使用直接查询替代存储过程"""
    try:
        async with db_cursor() as cursor:
            # 获取指定天数内的基础统计
            await cursor.execute("""
                SELECT 
                    COUNT(*) as total_tasks,
                    SUM(CASE WHEN status = 0 THEN 1 ELSE 0 END) as completed_tasks,
                    SUM(CASE WHEN status = 1 THEN 1 ELSE 0 END) as failed_tasks,
                    SUM(CASE WHEN status = 2 THEN 1 ELSE 0 END) as running_tasks,
                    SUM(CASE WHEN status = 3 THEN 1 ELSE 0 END) as pending_tasks,
                    ROUND(
                        SUM(CASE WHEN status = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
                    ) as success_rate,
                    SUM(posts_collected) as total_posts,
                    ROUND(AVG(posts_collected), 2) as avg_posts
                FROM tasks
                WHERE start_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
            """, [days])
            
            basic_stats = await cursor.fetchone()
            
            # 获取每日趋势数据
            await cursor.execute("""
                SELECT 
                    DATE(start_time) as date,
                    COUNT(*) as daily_tasks,
                    SUM(posts_collected) as daily_posts,
                    ROUND(AVG(posts_collected), 2) as avg_posts,
                    SUM(CASE WHEN status = 0 THEN 1 ELSE 0 END) as successful_tasks,
                    ROUND(
                        SUM(CASE WHEN status = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
                    ) as daily_success_rate
                FROM tasks
                WHERE start_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY DATE(start_time)
                ORDER BY date DESC
            """, [days])
            
            trend_data = await cursor.fetchall()
            
            report_data = {}
            
            if basic_stats:
                (total_tasks, completed_tasks, failed_tasks, running_tasks,
                 pending_tasks, success_rate, total_posts, avg_posts) = basic_stats
                
                report_data["overview"] = {
                    "period_days": days,
                    "total_tasks": total_tasks or 0,
                    "completed_tasks": completed_tasks or 0,
                    "failed_tasks": failed_tasks or 0,
                    "running_tasks": running_tasks or 0,
                    "pending_tasks": pending_tasks or 0,
                    "success_rate": success_rate or 0,
                    "total_posts_collected": total_posts or 0,
                    "avg_posts_per_task": avg_posts or 0
                }
            
            report_data["daily_trend"] = [
                {
                    "date": date.isoformat() if date else None,
                    "daily_tasks": daily_tasks or 0,
                    "daily_posts": daily_posts or 0,
                    "avg_posts_per_task": avg_posts or 0,
                    "successful_tasks": successful_tasks or 0,
                    "daily_success_rate": daily_success_rate or 0
                }
                for date, daily_tasks, daily_posts, avg_posts, successful_tasks, daily_success_rate in trend_data
            ]
            
            return ResponseModel(success=True, data=report_data, message="性能报告获取成功")
            
    except Exception as e:
        logger.error(f"获取性能报告失败: {e}")
        raise HTTPException(status_code=500, detail="获取性能报告失败")


@router.post("/maintenance/cleanup", response_model=ResponseModel)
async def cleanup_old_tasks(
    days_old: int = Query(90, ge=30, le=365, description="删除多少天前的数据"),
    keep_successful: bool = Query(True, description="是否保留成功的任务"),
    current_user: User = Depends(get_admin_user)
) -> ResponseModel:
    """清理旧任务数据 - 使用直接删除替代存储过程"""
    try:
        async with db_cursor() as cursor:
            # 计算截止日期
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            # 构建删除条件
            if keep_successful:
                where_condition = "WHERE start_time < %s AND status != 0"
                params = [cutoff_date]
            else:
                where_condition = "WHERE start_time < %s"
                params = [cutoff_date]
            
            # 首先获取要删除的任务ID
            await cursor.execute(f"""
                SELECT id FROM tasks {where_condition}
            """, params)
            task_ids = [row[0] for row in await cursor.fetchall()]
            
            if not task_ids:
                return ResponseModel(
                    success=True,
                    data={
                        "deleted_tasks": 0,
                        "deleted_posts": 0,
                        "deleted_comments": 0,
                        "summary": "没有找到需要清理的数据"
                    },
                    message="数据清理完成"
                )
            
            # 统计将要删除的数据
            task_ids_str = ','.join([f"'{tid}'" for tid in task_ids])
            
            # 统计评论数量
            await cursor.execute(f"""
                SELECT COUNT(*) FROM comments c
                JOIN posts p ON c.post_id = p.id
                WHERE p.task_id IN ({task_ids_str})
            """)
            comment_count = (await cursor.fetchone())[0]
            
            # 统计帖子数量
            await cursor.execute(f"""
                SELECT COUNT(*) FROM posts
                WHERE task_id IN ({task_ids_str})
            """)
            post_count = (await cursor.fetchone())[0]
            
            # 删除评论（通过外键级联删除）
            # 删除帖子（通过外键级联删除）
            # 删除任务
            await cursor.execute(f"""
                DELETE FROM tasks {where_condition}
            """, params)
            
            deleted_tasks = len(task_ids)
            
            return ResponseModel(
                success=True,
                data={
                    "deleted_tasks": deleted_tasks,
                    "deleted_posts": post_count,
                    "deleted_comments": comment_count,
                    "summary": f"成功清理了{days_old}天前的{deleted_tasks}个任务及相关数据"
                },
                message="数据清理完成"
            )
            
    except Exception as e:
        logger.error(f"清理旧数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"数据清理失败: {str(e)}")
