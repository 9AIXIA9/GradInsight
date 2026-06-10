"""
GradInsight Analysis Service — gRPC Server

实现 analysis.proto 中定义的 AnalysisService。
"""
import asyncio
import logging
import sys
import os
from concurrent import futures

import grpc

# 将 proto 目录加入 sys.path，使 analysis_pb2_grpc.py 内部的 import analysis_pb2 能正常工作
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'proto'))

import analysis_pb2
import analysis_pb2_grpc

from models.content_analysis import AnalysisRequest, AnalysisType
from services.analysis_service import ContentAnalysisService

logger = logging.getLogger(__name__)


class AnalysisServicer(analysis_pb2_grpc.AnalysisServiceServicer):

    def Analyze(self, request: analysis_pb2.AnalyzeRequest, context) -> analysis_pb2.AnalyzeResponse:
        try:
            types = [AnalysisType(t) for t in request.analysis_types]
            analysis_request = AnalysisRequest(
                task_id=None,
                analysis_types=types,
                keyword_filter=request.keyword_filter or None,
                min_posts=request.min_posts if request.min_posts > 0 else 5,
            )

            service = ContentAnalysisService()
            from db import connection as dbc
            dbc._connection_pool = None  # 每次请求重建连接池
            result = asyncio.run(service.analyze_content(analysis_request))

            # Python model → proto
            data = analysis_pb2.AnalysisResultData(
                analysis_id=result.analysis_id,
                task_id=result.task_id or "",
                total_posts_analyzed=result.total_posts_analyzed,
                processing_time=result.processing_time,
                topic_summaries=[
                    analysis_pb2.TopicSummary(
                        topic=ts.topic,
                        summary=ts.summary,
                        post_count=ts.post_count,
                        main_points=ts.main_points,
                        sentiment_trend=ts.sentiment_trend,
                        related_universities=ts.related_universities,
                        related_majors=ts.related_majors,
                    ) for ts in result.topic_summaries
                ],
                content_clusters=[
                    analysis_pb2.ContentCluster(
                        cluster_id=cc.cluster_id,
                        cluster_name=cc.cluster_name,
                        cluster_summary=cc.cluster_summary,
                        post_ids=cc.post_ids,
                        post_count=cc.post_count,
                        similarity_score=cc.similarity_score,
                        keywords=cc.keywords,
                    ) for cc in result.content_clusters
                ],
                keyword_frequencies=[
                    analysis_pb2.KeywordFrequency(
                        keyword=kf.keyword,
                        frequency=kf.frequency,
                        importance_score=kf.importance_score,
                        related_posts=kf.related_posts,
                    ) for kf in result.keyword_frequencies
                ],
                sentiment_analysis=[
                    analysis_pb2.SentimentResult(
                        post_id=sa.post_id,
                        sentiment=sa.sentiment,
                        confidence=sa.confidence,
                        emotion_keywords=sa.emotion_keywords,
                    ) for sa in result.sentiment_analysis
                ],
                university_mentions=[
                    analysis_pb2.UniversityMention(
                        university_name=um.university_name,
                        mention_count=um.mention_count,
                        sentiment_score=um.sentiment_score,
                        related_topics=um.related_topics,
                        post_ids=um.post_ids,
                    ) for um in result.university_mentions
                ],
                major_analysis=[
                    analysis_pb2.MajorAnalysis(
                        major_name=ma.major_name,
                        mention_count=ma.mention_count,
                        job_prospect_sentiment=ma.job_prospect_sentiment,
                        difficulty_level=ma.difficulty_level,
                        related_universities=ma.related_universities,
                        key_discussions=ma.key_discussions,
                    ) for ma in result.major_analysis
                ],
                insights=result.insights,
            )

            return analysis_pb2.AnalyzeResponse(success=True, message="ok", data=data)

        except Exception as e:
            logger.error(f"Analyze gRPC failed: {e}", exc_info=True)
            return analysis_pb2.AnalyzeResponse(success=False, message=str(e))


def serve(port: int = 5001):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    analysis_pb2_grpc.add_AnalysisServiceServicer_to_server(AnalysisServicer(), server)
    server.add_insecure_port(f"0.0.0.0:{port}")
    server.start()
    logger.info(f"gRPC server listening on :{port}")
    return server
