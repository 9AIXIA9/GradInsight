"""
分析服务 API 路由

暴露给 Java 后端调用的 3 个代理端点（无需鉴权），以及健康检查。
"""

import logging

from fastapi import APIRouter

from models.content_analysis import (
    AnalysisRequest, AnalysisType, ContentAnalysisResult,
)
from services.analysis_service import ContentAnalysisService
from db.connection import check_db_health

router = APIRouter()
logger = logging.getLogger(__name__)


# ---- 供 Java 调用的代理端点（无需鉴权）----

@router.post("/cluster")
async def cluster_proxy(payload: dict) -> dict:
    """
    内容聚类 + 关键词提取。
    Java AnalysisService.java -> POST /cluster
    """
    try:
        task_id = payload.get("task_id") if payload.get("task_id") else None
        keyword = payload.get("keyword_filter") or payload.get("keyword")
        min_posts = int(payload.get("min_posts", 2))

        analysis_service = ContentAnalysisService()
        request = AnalysisRequest(
            task_id=task_id,
            analysis_types=[AnalysisType.CONTENT_CLUSTERING, AnalysisType.KEYWORD_EXTRACTION],
            keyword_filter=keyword,
            min_posts=min_posts,
        )
        result = await analysis_service.analyze_content(request)
        return {"success": True, "message": "cluster analysis complete", "data": result.model_dump()}
    except Exception as e:
        logger.error(f"cluster proxy failed: {e}", exc_info=True)
        return {"success": False, "message": str(e), "data": None}


@router.post("/keywords")
async def keywords_proxy(payload: dict) -> dict:
    """
    关键词提取。
    Java AnalysisService.java -> POST /keywords
    """
    try:
        task_id = payload.get("task_id") if payload.get("task_id") else None
        keyword = payload.get("keyword_filter") or payload.get("keyword")
        min_posts = int(payload.get("min_posts", 2))

        analysis_service = ContentAnalysisService()
        request = AnalysisRequest(
            task_id=task_id,
            analysis_types=[AnalysisType.KEYWORD_EXTRACTION],
            keyword_filter=keyword,
            min_posts=min_posts,
        )
        result = await analysis_service.analyze_content(request)
        return {"success": True, "message": "keyword extraction complete", "data": result.model_dump()}
    except Exception as e:
        logger.error(f"keywords proxy failed: {e}", exc_info=True)
        return {"success": False, "message": str(e), "data": None}


@router.post("/sentiment")
async def sentiment_proxy(payload: dict) -> dict:
    """
    情感分析。
    Java AnalysisService.java -> POST /sentiment
    """
    try:
        task_id = payload.get("task_id") if payload.get("task_id") else None
        keyword = payload.get("keyword_filter") or payload.get("keyword")
        min_posts = int(payload.get("min_posts", 2))

        analysis_service = ContentAnalysisService()
        request = AnalysisRequest(
            task_id=task_id,
            analysis_types=[AnalysisType.SENTIMENT_ANALYSIS],
            keyword_filter=keyword,
            min_posts=min_posts,
        )
        result = await analysis_service.analyze_content(request)
        return {"success": True, "message": "sentiment analysis complete", "data": result.model_dump()}
    except Exception as e:
        logger.error(f"sentiment proxy failed: {e}", exc_info=True)
        return {"success": False, "message": str(e), "data": None}


# ---- 健康检查 ----

@router.get("/health")
async def health_check() -> dict:
    """健康检查 + 数据库连接测试"""
    db_ok = await check_db_health()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
    }
