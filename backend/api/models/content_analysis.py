from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field


class AnalysisType(str, Enum):
    """内容分析类型"""
    TOPIC_SUMMARY = "topic_summary"  # 话题总结
    CONTENT_CLUSTERING = "content_clustering"  # 内容聚类
    SENTIMENT_ANALYSIS = "sentiment_analysis"  # 情感分析
    KEYWORD_EXTRACTION = "keyword_extraction"  # 关键词提取
    UNIVERSITY_MENTION = "university_mention"  # 高校提及分析
    MAJOR_ANALYSIS = "major_analysis"  # 专业分析


class ContentCluster(BaseModel):
    """内容聚类结果"""
    cluster_id: str = Field(..., description="聚类ID")
    cluster_name: str = Field(..., description="聚类名称")
    cluster_summary: str = Field(..., description="聚类内容摘要")
    post_ids: List[str] = Field(..., description="包含的帖子ID列表")
    post_count: int = Field(..., description="帖子数量")
    similarity_score: float = Field(..., description="聚类内相似度得分")
    keywords: List[str] = Field(default_factory=list, description="聚类关键词")


class TopicSummary(BaseModel):
    """话题总结"""
    topic: str = Field(..., description="话题名称")
    summary: str = Field(..., description="话题摘要")
    post_count: int = Field(..., description="相关帖子数量")
    main_points: List[str] = Field(..., description="主要观点")
    sentiment_trend: str = Field(..., description="情感倾向: positive/negative/neutral")
    related_universities: List[str] = Field(default_factory=list, description="相关高校")
    related_majors: List[str] = Field(default_factory=list, description="相关专业")


class KeywordFrequency(BaseModel):
    """关键词频率"""
    keyword: str = Field(..., description="关键词")
    frequency: int = Field(..., description="出现频率")
    importance_score: float = Field(..., description="重要性得分")
    related_posts: List[str] = Field(..., description="相关帖子ID")


class SentimentAnalysis(BaseModel):
    """情感分析结果"""
    post_id: str = Field(..., description="帖子ID")
    sentiment: str = Field(..., description="情感倾向: positive/negative/neutral")
    confidence: float = Field(..., description="置信度")
    emotion_keywords: List[str] = Field(default_factory=list, description="情感关键词")


class UniversityMention(BaseModel):
    """高校提及分析"""
    university_name: str = Field(..., description="高校名称")
    mention_count: int = Field(..., description="提及次数")
    sentiment_score: float = Field(..., description="情感得分 (-1到1)")
    related_topics: List[str] = Field(..., description="相关话题")
    post_ids: List[str] = Field(..., description="相关帖子ID")


class MajorAnalysis(BaseModel):
    """专业分析"""
    major_name: str = Field(..., description="专业名称")
    mention_count: int = Field(..., description="提及次数")
    job_prospect_sentiment: float = Field(..., description="就业前景情感得分")
    difficulty_level: str = Field(..., description="难度等级: easy/medium/hard")
    related_universities: List[str] = Field(..., description="相关高校")
    key_discussions: List[str] = Field(..., description="关键讨论点")


class ContentAnalysisResult(BaseModel):
    """内容分析综合结果"""
    analysis_id: str = Field(..., description="分析ID")
    task_id: Optional[str] = Field(None, description="关联任务ID")
    analysis_type: AnalysisType = Field(..., description="分析类型")
    created_at: datetime = Field(default_factory=datetime.now, description="分析时间")
    
    # 各种分析结果
    topic_summaries: List[TopicSummary] = Field(default_factory=list, description="话题总结")
    content_clusters: List[ContentCluster] = Field(default_factory=list, description="内容聚类")
    keyword_frequencies: List[KeywordFrequency] = Field(default_factory=list, description="关键词频率")
    sentiment_analysis: List[SentimentAnalysis] = Field(default_factory=list, description="情感分析")
    university_mentions: List[UniversityMention] = Field(default_factory=list, description="高校提及")
    major_analysis: List[MajorAnalysis] = Field(default_factory=list, description="专业分析")
    
    # 总体统计
    total_posts_analyzed: int = Field(..., description="分析的帖子总数")
    processing_time: float = Field(..., description="处理时间(秒)")
    insights: List[str] = Field(default_factory=list, description="智能洞察")


class AnalysisRequest(BaseModel):
    """内容分析请求"""
    task_id: Optional[str] = Field(None, description="指定任务ID")
    analysis_types: List[AnalysisType] = Field(..., description="分析类型列表")
    keyword_filter: Optional[str] = Field(None, description="关键词过滤")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="时间范围")
    min_posts: int = Field(default=10, description="最少帖子数量")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "task_id": "task_12345",
                "analysis_types": ["topic_summary", "content_clustering", "sentiment_analysis"],
                "keyword_filter": "计算机",
                "date_range": {
                    "start": "2024-01-01T00:00:00",
                    "end": "2024-12-31T23:59:59"
                },
                "min_posts": 20
            }
        }
    }


class AnalysisListResponse(BaseModel):
    """分析结果列表响应"""
    analyses: List[ContentAnalysisResult] = Field(..., description="分析结果列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="每页大小")
