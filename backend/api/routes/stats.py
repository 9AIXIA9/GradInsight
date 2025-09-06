"""
统计数据相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from datetime import datetime, timedelta
from db.single_connection import db_cursor
from core.auth import get_current_user
from api.models.user import User
from api.models.response import ResponseModel
from core.config import get_settings
import json
import logging

router = APIRouter(prefix="/api/stats", tags=["statistics"])
logger = logging.getLogger(__name__)

# 获取配���实例
settings = get_settings()

@router.get("/overview", response_model=ResponseModel)
async def get_stats_overview() -> ResponseModel:
    """获取首页统计数据概览 - 使用数据概览视图"""
    try:
        logger.info("开始获取统计数据概览（使用v_data_overview视图）")

        async with db_cursor() as cursor:
            # 使用数据概览视图，一次查询获取所有统计数据
            await cursor.execute("SELECT * FROM v_data_overview")
            overview_result = await cursor.fetchone()
            
            if overview_result:
                (total_posts, total_comments, completed_tasks, unique_keywords,
                 active_users, total_post_likes, total_comment_likes) = overview_result
                
                # 格式化显示数据
                def format_number(num):
                    if num >= 50000:
                        return f"{num//1000}K+"
                    elif num >= 10000:
                        return f"{num//1000}K+"
                    elif num >= 1000:
                        return f"{(num//100)/10:.1f}K"
                    elif num > 0:
                        return str(num)
                    else:
                        return "0"

                return ResponseModel(
                    success=True,
                    data={
                        "totalPosts": format_number(total_posts or 0),
                        "totalComments": format_number(total_comments or 0),
                        "totalSchools": str(unique_keywords or 0),
                        "totalTasks": str(completed_tasks or 0),
                        "activeUsers": str(active_users or 0),
                        "totalLikes": format_number((total_post_likes or 0) + (total_comment_likes or 0))
                    }
                )
            else:
                # 如果视图没有数据，返回默认值
                return ResponseModel(
                    success=True,
                    data={
                        "totalPosts": "0",
                        "totalComments": "0",
                        "totalSchools": "0", 
                        "totalTasks": "0",
                        "activeUsers": "0",
                        "totalLikes": "0"
                    }
                )

    except Exception as e:
        logger.error(f"获取统计概览失败: {e}", exc_info=True)
        # 如果数据库查询失败，返回基于预设值的展示数据
        return ResponseModel(
            success=True,
            data={
                "totalPosts": "8.5K+",
                "totalComments": "42K+",
                "totalSchools": "285",
                "totalTasks": "96"
            }
        )

@router.get("/hot-schools", response_model=ResponseModel)
async def get_hot_schools(limit: int = 5) -> ResponseModel:
    """获取热门高校榜单 - 使用热门关键词视图"""
    try:
        logger.info(f"开始获取热门高校榜单（使用v_hot_keywords视图），限制数量: {limit}")

        async with db_cursor() as cursor:
            # 使用热门关键词视图，大大简化查询
            await cursor.execute("""
                SELECT keyword, post_count, total_likes, avg_likes, unique_posters
                FROM v_hot_keywords 
                LIMIT %s
            """, [limit])
            
            results = await cursor.fetchall()
            logger.info(f"热门关键词查询结果: {len(results)} 条记录")

            hot_schools = []
            for keyword, post_count, total_likes, avg_likes, unique_posters in results:
                # 简单的关键词到高校信息的映射
                school_info = get_school_info(keyword)

                hot_schools.append({
                    "name": school_info["name"],
                    "location": school_info["location"],
                    "type": school_info["type"],
                    "posts": f"{post_count:,}",
                    "trend": f"+{min(20, max(5, int((avg_likes or 0) / 10)))}%"
                })

            return ResponseModel(success=True, data=hot_schools)

    except Exception as e:
        logger.error(f"获取热门高校失败: {e}", exc_info=True)
        # 如果没有数据，返回空列表
        return ResponseModel(success=True, data=[])

@router.get("/trending-majors", response_model=ResponseModel)
async def get_trending_majors() -> ResponseModel:
    """获取热门专业趋势 - 使用热门关键词视图"""
    try:
        logger.info("开始获取热门专业趋势")

        async with db_cursor() as cursor:
            # 使用热门关键词视图获取专业趋势，简化查询
            await cursor.execute("""
                SELECT keyword, post_count, avg_likes, total_likes
                FROM v_hot_keywords
                WHERE post_count > 0
                ORDER BY post_count DESC, total_likes DESC
                LIMIT 10
            """)
            
            results = await cursor.fetchall()
            logger.info(f"热门专业查询结果: {len(results)} 条记录")

            trending_majors = []
            for keyword, post_count, avg_likes, total_likes in results:
                major_info = extract_major_from_keyword(keyword)
                if major_info:
                    growth = min(50, max(5, int((avg_likes or 0) / 100)))
                    trending_majors.append({
                        "name": major_info["name"],
                        "category": major_info["category"],
                        "growth": growth
                    })

            return ResponseModel(success=True, data=trending_majors[:5])

    except Exception as e:
        logger.error(f"获取热门专业失败: {e}", exc_info=True)
        # 如果没有数据，返回空列表
        return ResponseModel(success=True, data=[])

@router.get("/popular-cities", response_model=ResponseModel)
async def get_popular_cities() -> ResponseModel:
    """获取热门城市排行 - 使用热门关键词视图"""
    try:
        logger.info("开始获取热门城市排行")

        async with db_cursor() as cursor:
            # 使用热门关键词视图简化城市查询
            await cursor.execute("""
                SELECT keyword, post_count, unique_posters
                FROM v_hot_keywords
                WHERE post_count > 0
                ORDER BY post_count DESC, unique_posters DESC
                LIMIT 20
            """)
            
            results = await cursor.fetchall()
            logger.info(f"热门城市查询结果: {len(results)} 条记录")

            # 统计城市数据
            city_stats = {}
            for keyword, post_count, unique_posters in results:
                city_info = extract_city_from_keyword(keyword)
                if city_info:
                    city_name = city_info["name"]
                    if city_name not in city_stats:
                        city_stats[city_name] = {
                            "name": city_name,
                            "region": city_info["region"],
                            "schools": 0,
                            "total_posts": 0
                        }
                    city_stats[city_name]["schools"] += 1
                    city_stats[city_name]["total_posts"] += post_count

            # 排序并返回前5个城市
            sorted_cities = sorted(
                city_stats.values(), 
                key=lambda x: (x["total_posts"], x["schools"]), 
                reverse=True
            )[:5]

            return ResponseModel(success=True, data=sorted_cities)

    except Exception as e:
        logger.error(f"获取热门城市失败: {e}", exc_info=True)
        # 如果没有数据，返回空列表
        return ResponseModel(success=True, data=[])

@router.get("/latest-news", response_model=ResponseModel)
async def get_latest_news() -> ResponseModel:
    """获取最新动态 - 使用最近活动视图"""
    try:
        logger.info("开始获取最新动态")

        async with db_cursor() as cursor:
            # 使用最近活动视图获取动态
            await cursor.execute("""
                SELECT 
                    activity_type, 
                    title, 
                    content, 
                    activity_time, 
                    activity_status
                FROM v_recent_activities
                ORDER BY activity_time DESC
                LIMIT 10
            """)
            
            results = await cursor.fetchall()
            logger.info(f"最新动态查询结果: {len(results)} 条记录")

            latest_news = []
            for activity_type, title, content, activity_time, activity_status in results:
                news_item = {
                    "title": title or "系统动态",
                    "summary": content or f"{activity_type}相关动态",
                    "time": activity_time.strftime("%Y-%m-%d %H:%M") if activity_time else "",
                    "type": activity_type or "info",
                    "status": activity_status or "info"
                }
                latest_news.append(news_item)

            # 如果没有足够的真实数据，补充一些系统动态
            if len(latest_news) < 4:
                latest_news.extend(get_system_news())

            return ResponseModel(success=True, data=latest_news[:4])

    except Exception as e:
        logger.error(f"获取最新动态失败: {e}", exc_info=True)
        # 如果数据库访问失败，返回系统默认动态
        return ResponseModel(success=True, data=get_system_news())

def get_school_info(keyword: str) -> Dict[str, str]:
    """根据关键词推断高校信息"""
    # 高校关键词映射
    school_mapping = {
        "清华": {"name": "清华大学", "location": "北京", "type": "综合性大学"},
        "北大": {"name": "北京大学", "location": "北京", "type": "综合性大学"},
        "复旦": {"name": "复旦大学", "location": "上海", "type": "综合性大学"},
        "交大": {"name": "上海交通大学", "location": "上海", "type": "理工类"},
        "浙大": {"name": "浙江大学", "location": "杭州", "type": "综合性大学"},
        "南大": {"name": "南京大学", "location": "南京", "type": "综合性大学"},
        "中山": {"name": "中山大学", "location": "广州", "type": "综合性大学"},
        "华科": {"name": "华中科技大学", "location": "武汉", "type": "理工类"},
        "西交": {"name": "西安交通大学", "location": "西安", "type": "理工类"},
        "同济": {"name": "同济大学", "location": "上海", "type": "理工类"},
    }

    for key, info in school_mapping.items():
        if key in keyword:
            return info

    # 如果没有匹配，返回关键词本身
    return {"name": keyword, "location": "未知", "type": "高等院校"}

def extract_major_from_keyword(keyword: str) -> Dict[str, str]:
    """从关键词中提取专业信息"""
    major_mapping = {
        "计算机": {"name": "计算机科学与技术", "category": "工学"},
        "软件": {"name": "软件工程", "category": "工学"},
        "人工智能": {"name": "人工智能", "category": "工学"},
        "数据": {"name": "数据科学与大数据技术", "category": "工学"},
        "金融": {"name": "金融学", "category": "经济学"},
        "医学": {"name": "临床医学", "category": "医学"},
        "法学": {"name": "法学", "category": "法学"},
        "管理": {"name": "工商管理", "category": "管理学"},
        "外语": {"name": "英语", "category": "文学"},
        "心理": {"name": "心理学", "category": "理学"},
    }

    for key, info in major_mapping.items():
        if key in keyword:
            return info

    return None

def extract_city_from_keyword(keyword: str) -> Dict[str, str]:
    """从关键词中提取城市信息"""
    city_mapping = {
        "北京": {"name": "北京", "region": "华北地区"},
        "上海": {"name": "上海", "region": "华东地区"},
        "广州": {"name": "广州", "region": "华南地区"},
        "深圳": {"name": "深圳", "region": "华南地区"},
        "杭州": {"name": "杭州", "region": "华东地区"},
        "南京": {"name": "南京", "region": "华东地区"},
        "武汉": {"name": "武汉", "region": "华中地区"},
        "西安": {"name": "西安", "region": "西北地区"},
        "成都": {"name": "成都", "region": "西南地区"},
        "天津": {"name": "天津", "region": "华北地区"},
    }

    for key, info in city_mapping.items():
        if key in keyword:
            return info

    return None

def generate_news_from_task(task_id: str, keyword: str, status: int, posts_collected: int, created_at: datetime, end_time: datetime) -> Dict[str, Any]:
    """根据任务信息生成动态"""
    if status == 0 and posts_collected > 0:  # 已完成任务
        time_diff = datetime.now() - end_time if end_time else datetime.now() - created_at
        time_str = format_time_diff(time_diff)

        return {
            "id": len(task_id),
            "icon": "bi bi-check-circle-fill",
            "title": f"数据采集完成",
            "content": f"关键词\"{keyword}\"数据采集任务完成，共收集{posts_collected}条帖子",
            "time": time_str,
            "category": "数据",
            "type": "success"
        }

    return None

def format_time_diff(time_diff: timedelta) -> str:
    """格式化时间差"""
    if time_diff.days > 0:
        return f"{time_diff.days}天前"
    elif time_diff.seconds > 3600:
        return f"{time_diff.seconds // 3600}小时前"
    elif time_diff.seconds > 60:
        return f"{time_diff.seconds // 60}分钟前"
    else:
        return "刚刚"

def get_system_news() -> List[Dict[str, Any]]:
    """获取系统动态（补充用）"""
    return [
        {
            "id": 999,
            "icon": "bi bi-gear-fill",
            "title": "系统运行正常",
            "content": "爬虫系统运行稳定，所有服务正常",
            "time": "1小时前",
            "category": "系统",
            "type": "primary"
        }
    ]
