from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import logging

from api.models.content_analysis import (
    AnalysisRequest, ContentAnalysisResult, AnalysisListResponse, AnalysisType
)
from api.models.response import ResponseModel
from services.content_analysis_service import ContentAnalysisService
from core.auth import get_current_user
from api.models.user import User

router = APIRouter(prefix="/analysis", tags=["content-analysis"])
logger = logging.getLogger(__name__)


def get_analysis_service() -> ContentAnalysisService:
    """获取内容分析服务实例"""
    return ContentAnalysisService()


@router.post("/analyze", response_model=ResponseModel)
async def analyze_content(
    request: AnalysisRequest,
    analysis_service: ContentAnalysisService = Depends(get_analysis_service),
    current_user: User = Depends(get_current_user)
) -> ResponseModel:
    """
    执行内容分析
    
    对指定的帖子内容进行智能分析，包括：
    - 话题总结：自动生成热门话题的摘要和观点
    - 内容聚类：将相似内容进行分组
    - 关键词提取：识别高频和重要关键词
    - 情感分析：分析用户对不同话题的情感倾向
    - 高校提及分析：统计和分析各高校的讨论情况
    - 专业分析：分析不同专业的讨论热度和就业前景
    """
    try:
        logger.info(f"用户 {current_user.username} 请求内容分析: {request.analysis_types}")
        
        # 验证分析类型
        if not request.analysis_types:
            raise HTTPException(
                status_code=400,
                detail="至少需要指定一种分析类型"
            )
        
        # 执行分析
        result = await analysis_service.analyze_content(request)
        
        logger.info(f"内容分析完成: {result.analysis_id}, 处理了{result.total_posts_analyzed}个帖子")
        
        return ResponseModel(
            success=True,
            message="内容分析完成",
            data=result
        )
        
    except Exception as e:
        logger.error(f"内容分析失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"内容分析失败: {str(e)}"
        )


@router.get("/types", response_model=ResponseModel)
async def get_analysis_types() -> ResponseModel:
    """
    获取支持的分析类型列表
    
    返回当前系统支持的所有内容分析类型及其说明
    """
    analysis_types = [
        {
            "type": AnalysisType.TOPIC_SUMMARY,
            "name": "话题总结",
            "description": "自动生成热门话题的摘要和主要观点"
        },
        {
            "type": AnalysisType.CONTENT_CLUSTERING,
            "name": "内容聚类",
            "description": "将相似内容进行智能分组"
        },
        {
            "type": AnalysisType.KEYWORD_EXTRACTION,
            "name": "关键词提取",
            "description": "识别高频关键词和重要术语"
        },
        {
            "type": AnalysisType.SENTIMENT_ANALYSIS,
            "name": "情感分析",
            "description": "分析用户对不同话题的情感倾向"
        },
        {
            "type": AnalysisType.UNIVERSITY_MENTION,
            "name": "高校提及分析",
            "description": "统计和分析各高校的讨论情况"
        },
        {
            "type": AnalysisType.MAJOR_ANALYSIS,
            "name": "专业分析",
            "description": "分析不同专业的讨论热度和发展趋势"
        }
    ]
    
    return ResponseModel(
        success=True,
        message="获取分析类型成功",
        data=analysis_types
    )


@router.get("/history", response_model=ResponseModel)
async def get_analysis_history(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页大小"),
    analysis_service: ContentAnalysisService = Depends(get_analysis_service),
    current_user: User = Depends(get_current_user)
) -> ResponseModel:
    """
    获取内容分析历史记录
    
    查看之前执行的内容分析结果，支持分页查询
    """
    try:
        skip = (page - 1) * page_size
        result = await analysis_service.get_analysis_history(skip=skip, limit=page_size)
        
        return ResponseModel(
            success=True,
            message="获取分析历史成功",
            data=result
        )
        
    except Exception as e:
        logger.error(f"获取分析历史失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取分析历史失败: {str(e)}"
        )


@router.post("/quick-analysis", response_model=ResponseModel)
async def quick_analysis(
    task_id: Optional[str] = None,
    keyword: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    analysis_service: ContentAnalysisService = Depends(get_analysis_service)
) -> ResponseModel:
    """
    快速分析
    
    执行预设的快速分析，包含话题总结、关键词提取和情感分析
    """
    try:
        # 构建快速分析请求
        request = AnalysisRequest(
            task_id=task_id,
            analysis_types=[
                AnalysisType.TOPIC_SUMMARY,
                AnalysisType.KEYWORD_EXTRACTION,
                AnalysisType.SENTIMENT_ANALYSIS,
                AnalysisType.UNIVERSITY_MENTION
            ],
            keyword_filter=keyword,
            min_posts=5
        )
        
        result = await analysis_service.analyze_content(request)
        
        # 简化返回结果，只包含关键信息
        simplified_result = {
            "analysis_id": result.analysis_id,
            "total_posts_analyzed": result.total_posts_analyzed,
            "processing_time": result.processing_time,
            "top_keywords": result.keyword_frequencies[:10],
            "top_topics": result.topic_summaries[:5],
            "university_mentions": result.university_mentions[:5],
            "insights": result.insights
        }
        
        return ResponseModel(
            success=True,
            message="快速分析完成",
            data=simplified_result
        )
        
    except Exception as e:
        logger.error(f"快速分析失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"快速分析失败: {str(e)}"
        )


@router.get("/summary/{task_id}", response_model=ResponseModel)
async def get_task_summary(
    task_id: str,
    current_user: User = Depends(get_current_user),
    analysis_service: ContentAnalysisService = Depends(get_analysis_service)
) -> ResponseModel:
    """
    获取特定任务的内容摘要
    
    为指定的爬虫任务生成内容摘要，包括关键统计和主要发现
    """
    try:
        # 构建摘要分析请求
        request = AnalysisRequest(
            task_id=task_id,
            analysis_types=[
                AnalysisType.TOPIC_SUMMARY,
                AnalysisType.KEYWORD_EXTRACTION,
                AnalysisType.UNIVERSITY_MENTION,
                AnalysisType.MAJOR_ANALYSIS
            ],
            min_posts=1
        )
        
        result = await analysis_service.analyze_content(request)
        
        # 生成任务摘要
        summary = {
            "task_id": task_id,
            "total_posts": result.total_posts_analyzed,
            "analysis_time": result.created_at,
            "processing_time": result.processing_time,
            "key_insights": result.insights,
            "top_keywords": [kw.keyword for kw in result.keyword_frequencies[:10]],
            "main_topics": [t.topic for t in result.topic_summaries[:5]],
            "mentioned_universities": [u.university_name for u in result.university_mentions[:5]],
            "discussed_majors": [m.major_name for m in result.major_analysis[:5]]
        }
        
        return ResponseModel(
            success=True,
            message="任务摘要生成成功",
            data=summary
        )
        
    except Exception as e:
        logger.error(f"生成任务摘要失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"生成任务摘要失败: {str(e)}"
        )


@router.get("/{analysis_id}", response_model=ResponseModel)
async def get_analysis_detail(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    analysis_service: ContentAnalysisService = Depends(get_analysis_service)
) -> ResponseModel:
    """
    获取分析详情
    
    根据分析ID获取完整的分析结果详情
    """
    try:
        result = await analysis_service.get_analysis_by_id(analysis_id)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="分析结果不存在"
            )
        
        return ResponseModel(
            success=True,
            message="获取分析详情成功",
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取分析详情失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取分析详情失败: {str(e)}"
        )


@router.delete("/{analysis_id}", response_model=ResponseModel)
async def delete_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    analysis_service: ContentAnalysisService = Depends(get_analysis_service)
) -> ResponseModel:
    """
    删除分析结果
    
    删除指定的分析结果及其所有相关数据
    """
    try:
        success = await analysis_service.delete_analysis(analysis_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="分析结果不存在"
            )
        
        return ResponseModel(
            success=True,
            message="分析结果已删除"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除分析结果失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"删除分析结果失败: {str(e)}"
        )


# 兼容其他语言微服务的轻量端点（无需用户认证），供 Java/gRPC 网关直接调用
@router.post("/cluster")
async def cluster_proxy(payload: dict, analysis_service: ContentAnalysisService = Depends(get_analysis_service)) -> ResponseModel:
    """
    兼容接口：执行内容聚类（并可同时返回关键词），对外开放给内部服务调用（无需JWT）。
    支持payload字段：`task_id`, `keyword_filter`, `min_posts`。
    """
    try:
        task_id = payload.get('task_id') if payload.get('task_id') else None
        keyword = payload.get('keyword_filter') or payload.get('keyword')
        min_posts = int(payload.get('min_posts', 2))

        request = AnalysisRequest(
            task_id=task_id,
            analysis_types=[AnalysisType.CONTENT_CLUSTERING, AnalysisType.KEYWORD_EXTRACTION],
            keyword_filter=keyword,
            min_posts=min_posts
        )

        result = await analysis_service.analyze_content(request)
        return ResponseModel(success=True, message="cluster analysis complete", data=result)

    except Exception as e:
        logger.error(f"cluster proxy failed: {e}", exc_info=True)
        return ResponseModel(success=False, message=str(e), data=None)


@router.post("/keywords")
async def keywords_proxy(payload: dict, analysis_service: ContentAnalysisService = Depends(get_analysis_service)) -> ResponseModel:
    """兼容接口：提取关键词（Keywords）"""
    try:
        task_id = payload.get('task_id') if payload.get('task_id') else None
        keyword = payload.get('keyword_filter') or payload.get('keyword')
        min_posts = int(payload.get('min_posts', 2))

        request = AnalysisRequest(
            task_id=task_id,
            analysis_types=[AnalysisType.KEYWORD_EXTRACTION],
            keyword_filter=keyword,
            min_posts=min_posts
        )

        result = await analysis_service.analyze_content(request)
        return ResponseModel(success=True, message="keyword extraction complete", data=result)

    except Exception as e:
        logger.error(f"keywords proxy failed: {e}", exc_info=True)
        return ResponseModel(success=False, message=str(e), data=None)


@router.post("/sentiment")
async def sentiment_proxy(payload: dict, analysis_service: ContentAnalysisService = Depends(get_analysis_service)) -> ResponseModel:
    """兼容接口：情感分析（Sentiment）"""
    try:
        task_id = payload.get('task_id') if payload.get('task_id') else None
        keyword = payload.get('keyword_filter') or payload.get('keyword')
        min_posts = int(payload.get('min_posts', 2))

        request = AnalysisRequest(
            task_id=task_id,
            analysis_types=[AnalysisType.SENTIMENT_ANALYSIS],
            keyword_filter=keyword,
            min_posts=min_posts
        )

        result = await analysis_service.analyze_content(request)
        return ResponseModel(success=True, message="sentiment analysis complete", data=result)

    except Exception as e:
        logger.error(f"sentiment proxy failed: {e}", exc_info=True)
        return ResponseModel(success=False, message=str(e), data=None)
