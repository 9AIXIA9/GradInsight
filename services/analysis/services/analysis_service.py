"""
内容分析服务

提供帖子和评论的内容分析功能，包括：
- 情感分析
- 关键词提取
- 学校维度分析
- 标签统计
"""

from models.content_analysis import (
    AnalysisType, AnalysisRequest, ContentAnalysisResult,
    TopicSummary, ContentCluster, KeywordFrequency,
    SentimentAnalysis, UniversityMention, MajorAnalysis
)
from models.post import Post
from services.post_service import PostService
from db.connection import db_cursor
from config import get_settings

import json
import logging
import asyncio
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Set
from collections import Counter, defaultdict
import uuid

logger = logging.getLogger(__name__)
settings = get_settings()


class ContentAnalysisService:
    """内容分析服务"""
    
    def __init__(self):
        self.post_service = PostService()
        # 预定义的高校名称词典
        self.university_keywords = {
            "清华大学", "北京大学", "复旦大学", "上海交通大学", "浙江大学",
            "中山大学", "南京大学", "华中科技大学", "西安交通大学", "同济大学",
            "北京理工大学", "北京航空航天大学", "天津大学", "大连理工大学",
            "东南大学", "华南理工大学", "电子科技大学", "重庆大学", "四川大学",
            "中南大学", "湖南大学", "山东大学", "吉林大学", "厦门大学",
            "中国科学技术大学", "哈尔滨工业大学", "西北工业大学", "中国人民大学",
            "北京师范大学", "南开大学", "武汉大学", "华东师范大学"
        }
        
        # 预定义的专业关��词
        self.major_keywords = {
            "计算机科学与技术", "软件工程", "人工智能", "数据科学", "网络工程",
            "信息安全", "电子信息工程", "通信工程", "自动化", "机械工程",
            "土木工程", "建筑学", "电气工程", "化学工程", "材料科学",
            "生物医学工程", "临床医学", "口腔医学", "药学", "护理学",
            "经济学", "金融学", "会计学", "工商管理", "市场营销",
            "法学", "政治学", "社会学", "新闻传播", "外国语言文学",
            "数学与应用数学", "物理学", "化学", "生物科学", "环境科学"
        }
        
        # 情感词典
        self.positive_words = {
            "好", "棒", "优秀", "不错", "推荐", "喜欢", "满意", "赞",
            "完美", "厉害", "强", "牛", "值得", "优质", "精彩", "出色"
        }
        
        self.negative_words = {
            "差", "烂", "不好", "失望", "糟糕", "垃圾", "坑", "后悔",
            "难", "累", "苦", "无聊", "浪费", "不值", "坑爹", "血亏"
        }

    async def analyze_content(self, request: AnalysisRequest) -> ContentAnalysisResult:
        """执行内容分析"""
        start_time = datetime.now()
        analysis_id = str(uuid.uuid4())
        
        # 处理task_id，如果是空字符串则设为None
        task_id = request.task_id if request.task_id and request.task_id.strip() else None
        
        logger.info(f"开始内容分析: {analysis_id}, 类型: {request.analysis_types}, 任务ID: {task_id}")
        
        try:
            # 获取帖子数据
            posts_data = await self._get_posts_for_analysis(request)
            posts = posts_data.get("posts", [])
            
            if len(posts) < request.min_posts:
                logger.warning(f"帖子数量不足: {len(posts)} < {request.min_posts}")
                return ContentAnalysisResult(
                    analysis_id=analysis_id,
                    task_id=task_id,
                    analysis_type=request.analysis_types[0] if request.analysis_types else AnalysisType.TOPIC_SUMMARY,
                    total_posts_analyzed=len(posts),
                    processing_time=0,
                    insights=["帖子数量不足，无法进行有效分析"]
                )
            
            # 初始化结果
            result = ContentAnalysisResult(
                analysis_id=analysis_id,
                task_id=task_id,
                analysis_type=request.analysis_types[0] if request.analysis_types else AnalysisType.TOPIC_SUMMARY,
                total_posts_analyzed=len(posts),
                processing_time=0.0  # 先设为0，后面会更新
            )
            
            # 执行各种分析
            for analysis_type in request.analysis_types:
                if analysis_type == AnalysisType.TOPIC_SUMMARY:
                    result.topic_summaries = await self._generate_topic_summaries(posts)
                elif analysis_type == AnalysisType.CONTENT_CLUSTERING:
                    result.content_clusters = await self._cluster_content(posts)
                elif analysis_type == AnalysisType.KEYWORD_EXTRACTION:
                    result.keyword_frequencies = await self._extract_keywords(posts)
                elif analysis_type == AnalysisType.SENTIMENT_ANALYSIS:
                    result.sentiment_analysis = await self._analyze_sentiment(posts)
                elif analysis_type == AnalysisType.UNIVERSITY_MENTION:
                    result.university_mentions = await self._analyze_university_mentions(posts)
                elif analysis_type == AnalysisType.MAJOR_ANALYSIS:
                    result.major_analysis = await self._analyze_majors(posts)
            
            # 生成智能洞察
            result.insights = await self._generate_insights(result)
            
            # 计算处理时间
            processing_time = (datetime.now() - start_time).total_seconds()
            result.processing_time = processing_time
            
            # 保存分析结果到数据库
            await self._save_analysis_result(result)
            
            logger.info(f"内容分析完成: {analysis_id}, 耗时: {processing_time:.2f}秒")
            return result
            
        except Exception as e:
            logger.error(f"内容分析出错: {e}", exc_info=True)
            raise

    async def _get_posts_for_analysis(self, request: AnalysisRequest) -> Dict[str, Any]:
        """获取用于分析的帖子数据"""
        # 直接调用 get_posts 方法
        return await self.post_service.get_posts(
            limit=1000,
            task_id=request.task_id,
            keyword=request.keyword_filter
        )

    async def _extract_keywords(self, posts: List[Post]) -> List[KeywordFrequency]:
        """提取关键词"""
        logger.info("开始提取关键词")
        
        # 合并所有文本内容
        all_text = []
        post_texts = {}
        
        for post in posts:
            text = f"{post.title} {' '.join(post.tags)}"
            all_text.append(text)
            post_texts[post.id] = text
            
            # 添加评论内容
            for comment in post.comments:
                comment_text = comment.content
                all_text.append(comment_text)
        
        # 简单的关键词提取（基于词频）
        combined_text = " ".join(all_text)
        
        # 使用正则表达式提取中文词汇
        chinese_words = re.findall(r'[\u4e00-\u9fff]+', combined_text)
        
        # 过滤停用词和短词
        stop_words = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这"}
        filtered_words = [word for word in chinese_words if len(word) >= 2 and word not in stop_words]
        
        # 统计词频
        word_counts = Counter(filtered_words)
        
        # 生成关键词频率列表
        keywords = []
        for word, freq in word_counts.most_common(50):  # 取前50个关键词
            # 计算重要性得分（可以改进为TF-IDF等）
            importance_score = freq / len(posts)
            
            # 查找相关帖子
            related_posts = [
                post.id for post in posts 
                if word in f"{post.title} {' '.join(post.tags)}"
            ]
            
            keywords.append(KeywordFrequency(
                keyword=word,
                frequency=freq,
                importance_score=importance_score,
                related_posts=related_posts[:10]  # 最多返回10个相关帖子
            ))
        
        logger.info(f"提取到 {len(keywords)} 个关键词")
        return keywords

    async def _analyze_sentiment(self, posts: List[Post]) -> List[SentimentAnalysis]:
        """分析情感倾向"""
        logger.info("开始情感分析")
        
        sentiments = []
        
        for post in posts:
            # 合并标题和标签进行分析
            text = f"{post.title} {' '.join(post.tags)}"
            
            # 简单的情感分析（基于情感词典）
            positive_count = sum(1 for word in self.positive_words if word in text)
            negative_count = sum(1 for word in self.negative_words if word in text)
            
            # 确定情感倾向
            if positive_count > negative_count:
                sentiment = "positive"
                confidence = positive_count / (positive_count + negative_count + 1)
            elif negative_count > positive_count:
                sentiment = "negative"
                confidence = negative_count / (positive_count + negative_count + 1)
            else:
                sentiment = "neutral"
                confidence = 0.5
            
            # 提取情感关键词
            emotion_keywords = []
            for word in self.positive_words:
                if word in text:
                    emotion_keywords.append(word)
            for word in self.negative_words:
                if word in text:
                    emotion_keywords.append(word)
            
            sentiments.append(SentimentAnalysis(
                post_id=post.id,
                sentiment=sentiment,
                confidence=confidence,
                emotion_keywords=emotion_keywords[:5]  # 最多5个情感关键词
            ))
        
        logger.info(f"完成 {len(sentiments)} 个帖子的情感分析")
        return sentiments

    async def _analyze_university_mentions(self, posts: List[Post]) -> List[UniversityMention]:
        """分析高校提及情况"""
        logger.info("开始分析��校提及")

        university_data = defaultdict(lambda: {
            'count': 0, 
            'posts': [], 
            'topics': set(), 
            'sentiments': []
        })
        
        for post in posts:
            text = f"{post.title} {' '.join(post.tags)}"
            
            # 检查每个高校是否被提及
            for university in self.university_keywords:
                if university in text or any(keyword in text for keyword in [university[:2], university[:3]]):
                    university_data[university]['count'] += 1
                    university_data[university]['posts'].append(post.id)
                    university_data[university]['topics'].update(post.tags)
                    
                    # 简单的情感评分
                    positive_count = sum(1 for word in self.positive_words if word in text)
                    negative_count = sum(1 for word in self.negative_words if word in text)
                    sentiment_score = (positive_count - negative_count) / max(positive_count + negative_count, 1)
                    university_data[university]['sentiments'].append(sentiment_score)
        
        # 生成结果
        mentions = []
        for university, data in university_data.items():
            if data['count'] > 0:
                avg_sentiment = sum(data['sentiments']) / len(data['sentiments']) if data['sentiments'] else 0
                
                mentions.append(UniversityMention(
                    university_name=university,
                    mention_count=data['count'],
                    sentiment_score=avg_sentiment,
                    related_topics=list(data['topics'])[:10],
                    post_ids=data['posts'][:20]
                ))
        
        # 按提及次数排序
        mentions.sort(key=lambda x: x.mention_count, reverse=True)
        
        logger.info(f"分析了 {len(mentions)} 个高校的提及情况")
        return mentions[:20]  # 返回前20个

    async def _analyze_majors(self, posts: List[Post]) -> List[MajorAnalysis]:
        """分析专业相关信息"""
        logger.info("开始分析专业信息")
        
        major_data = defaultdict(lambda: {
            'count': 0,
            'universities': set(),
            'discussions': [],
            'job_sentiments': [],
            'difficulty_indicators': []
        })
        
        for post in posts:
            text = f"{post.title} {' '.join(post.tags)}"
            
            # 检查专业提及
            for major in self.major_keywords:
                if major in text or any(keyword in text for keyword in [major[:2], major[:3]]):
                    major_data[major]['count'] += 1
                    
                    # 相关高校
                    for university in self.university_keywords:
                        if university in text:
                            major_data[major]['universities'].add(university)
                    
                    # 就业相关的情感分析
                    if any(keyword in text for keyword in ["就业", "工作", "找工作", "毕业", "薪资", "工资"]):
                        positive_count = sum(1 for word in self.positive_words if word in text)
                        negative_count = sum(1 for word in self.negative_words if word in text)
                        job_sentiment = (positive_count - negative_count) / max(positive_count + negative_count, 1)
                        major_data[major]['job_sentiments'].append(job_sentiment)
                    
                    # 难度指标
                    if any(keyword in text for keyword in ["难", "累", "辛苦", "压力"]):
                        major_data[major]['difficulty_indicators'].append("hard")
                    elif any(keyword in text for keyword in ["简单", "轻松", "容易"]):
                        major_data[major]['difficulty_indicators'].append("easy")
                    else:
                        major_data[major]['difficulty_indicators'].append("medium")
                    
                    # 关键讨论点
                    if post.title:
                        major_data[major]['discussions'].append(post.title)
        
        # 生成结果
        analyses = []
        for major, data in major_data.items():
            if data['count'] > 0:
                # 计算就业前景情感得分
                avg_job_sentiment = sum(data['job_sentiments']) / len(data['job_sentiments']) if data['job_sentiments'] else 0
                
                # 确定难度等级
                difficulty_counter = Counter(data['difficulty_indicators'])
                difficulty_level = difficulty_counter.most_common(1)[0][0] if difficulty_counter else "medium"
                
                analyses.append(MajorAnalysis(
                    major_name=major,
                    mention_count=data['count'],
                    job_prospect_sentiment=avg_job_sentiment,
                    difficulty_level=difficulty_level,
                    related_universities=list(data['universities'])[:10],
                    key_discussions=data['discussions'][:10]
                ))
        
        # 按提及次数排序
        analyses.sort(key=lambda x: x.mention_count, reverse=True)
        
        logger.info(f"分析了 {len(analyses)} 个专业")
        return analyses[:15]  # 返回前15个

    async def _generate_topic_summaries(self, posts: List[Post]) -> List[TopicSummary]:
        """生成话题总结"""
        logger.info("开始生成话题总结")
        
        # 基于标签聚合话题
        tag_data = defaultdict(lambda: {
            'posts': [],
            'universities': set(),
            'majors': set(),
            'sentiments': []
        })
        
        for post in posts:
            for tag in post.tags:
                tag_data[tag]['posts'].append(post)
                
                # 分析情感
                text = f"{post.title} {' '.join(post.tags)}"
                positive_count = sum(1 for word in self.positive_words if word in text)
                negative_count = sum(1 for word in self.negative_words if word in text)
                
                if positive_count > negative_count:
                    tag_data[tag]['sentiments'].append("positive")
                elif negative_count > positive_count:
                    tag_data[tag]['sentiments'].append("negative")
                else:
                    tag_data[tag]['sentiments'].append("neutral")
                
                # 提取相关高校和专业
                for university in self.university_keywords:
                    if university in text:
                        tag_data[tag]['universities'].add(university)
                
                for major in self.major_keywords:
                    if major in text:
                        tag_data[tag]['majors'].add(major)
        
        # 生成话题总结
        summaries = []
        for tag, data in tag_data.items():
            if len(data['posts']) >= 3:  # 至少3个帖子才生成总结
                # 确定主要情感倾向
                sentiment_counter = Counter(data['sentiments'])
                main_sentiment = sentiment_counter.most_common(1)[0][0]
                
                # 生成摘要
                titles = [post.title for post in data['posts'][:5]]
                summary = f"关于{tag}的讨论主要包括：" + "；".join(titles[:3]) + "等话题。"
                
                # 提取主要观点
                main_points = []
                for post in data['posts'][:5]:
                    if post.title:
                        main_points.append(post.title)
                
                summaries.append(TopicSummary(
                    topic=tag,
                    summary=summary,
                    post_count=len(data['posts']),
                    main_points=main_points[:5],
                    sentiment_trend=main_sentiment,
                    related_universities=list(data['universities'])[:5],
                    related_majors=list(data['majors'])[:5]
                ))
        
        # 按帖子数量排序
        summaries.sort(key=lambda x: x.post_count, reverse=True)
        
        logger.info(f"生成了 {len(summaries)} 个话题总结")
        return summaries[:10]  # 返回前10个

    async def _cluster_content(self, posts: List[Post]) -> List[ContentCluster]:
        """内容聚类"""
        logger.info("开始内容聚类")
        
        # 简单的基于关键词的聚类
        clusters = defaultdict(lambda: {
            'posts': [],
            'keywords': set(),
            'titles': []
        })
        
        for post in posts:
            # 基于主要关键词进行聚类
            text = f"{post.title} {' '.join(post.tags)}"
            
            # 寻找主要分类关键词
            cluster_key = "其他"
            
            # 教育相关
            if any(keyword in text for keyword in ["高校", "大学", "学院", "招生", "录取"]):
                cluster_key = "高校教育"
            # 专业相关
            elif any(keyword in text for keyword in ["专业", "学科", "课程", "学习"]):
                cluster_key = "专业学习"
            # 就业相关
            elif any(keyword in text for keyword in ["就业", "工作", "职业", "薪资", "面试"]):
                cluster_key = "就业发展"
            # 生活相关
            elif any(keyword in text for keyword in ["生活", "住宿", "食堂", "社团", "活动"]):
                cluster_key = "校园生活"
            
            clusters[cluster_key]['posts'].append(post.id)
            clusters[cluster_key]['keywords'].update(post.tags)
            clusters[cluster_key]['titles'].append(post.title)
        
        # 生成聚类结果
        cluster_results = []
        for cluster_name, data in clusters.items():
            if len(data['posts']) >= 2:  # 至少2个帖子
                cluster_id = str(uuid.uuid4())
                
                # 生成聚类摘要
                summary = f"{cluster_name}相关内容共{len(data['posts'])}个帖子，主要讨论："
                if data['titles']:
                    summary += "；".join(data['titles'][:3]) + "等。"
                
                cluster_results.append(ContentCluster(
                    cluster_id=cluster_id,
                    cluster_name=cluster_name,
                    cluster_summary=summary,
                    post_ids=data['posts'],
                    post_count=len(data['posts']),
                    similarity_score=0.8,  # 简化的相似度得分
                    keywords=list(data['keywords'])[:10]
                ))
        
        # 按帖子数量排序
        cluster_results.sort(key=lambda x: x.post_count, reverse=True)
        
        logger.info(f"生成了 {len(cluster_results)} 个内容聚类")
        return cluster_results

    async def _generate_insights(self, result: ContentAnalysisResult) -> List[str]:
        """生成智能洞察"""
        insights = []
        
        # 基于话题总结的洞察
        if result.topic_summaries:
            top_topic = result.topic_summaries[0]
            insights.append(f"最热门的讨论话题是'{top_topic.topic}'，共有{top_topic.post_count}个相关帖子")
            
            # 情感倾向洞察
            positive_topics = [t for t in result.topic_summaries if t.sentiment_trend == "positive"]
            if positive_topics:
                insights.append(f"用户对{len(positive_topics)}个话题持积极态度，表明整体讨论氛围较好")
        
        # 基于高校提及的洞察
        if result.university_mentions:
            top_university = result.university_mentions[0]
            insights.append(f"'{top_university.university_name}'是讨论最多的高校，被提及{top_university.mention_count}次")
            
            high_sentiment_unis = [u for u in result.university_mentions if u.sentiment_score > 0.3]
            if high_sentiment_unis:
                insights.append(f"有{len(high_sentiment_unis)}所高校获得了较高的用户评价")
        
        # 基于专业分析的洞察
        if result.major_analysis:
            top_major = result.major_analysis[0]
            insights.append(f"'{top_major.major_name}'是讨论最多的专业，被提及{top_major.mention_count}次")
            
            good_job_majors = [m for m in result.major_analysis if m.job_prospect_sentiment > 0.2]
            if good_job_majors:
                insights.append(f"有{len(good_job_majors)}个专业的就业前景评价较为积极")
        
        # 基于内容聚类的洞察（只有在执行了聚类分析时才生成）
        if result.content_clusters and len(result.content_clusters) > 0:
            total_clustered = sum(c.post_count for c in result.content_clusters)
            insights.append(f"内容聚类发现了{len(result.content_clusters)}个主要话题类别，覆盖了{total_clustered}个帖子")
        
        return insights[:5]  # 最多返回5个洞察

    async def _save_analysis_result(self, result: ContentAnalysisResult):
        """保存分析结果到数据库"""
        try:
            async with db_cursor() as cursor:
                # 保存主分析结果
                await cursor.execute("""
                    INSERT INTO content_analysis_results 
                    (id, task_id, analysis_type, total_posts_analyzed, processing_time, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    result.analysis_id,
                    result.task_id,
                    result.analysis_type.value,
                    result.total_posts_analyzed,
                    result.processing_time,
                    result.created_at
                ))
                
                # 保存话题总结
                for topic in result.topic_summaries:
                    await cursor.execute("""
                        INSERT INTO topic_summaries 
                        (analysis_id, topic, summary, post_count, main_points, sentiment_trend, 
                         related_universities, related_majors)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        result.analysis_id,
                        topic.topic,
                        topic.summary,
                        topic.post_count,
                        json.dumps(topic.main_points, ensure_ascii=False),
                        topic.sentiment_trend,
                        json.dumps(topic.related_universities, ensure_ascii=False),
                        json.dumps(topic.related_majors, ensure_ascii=False)
                    ))
                
                # 保存内容聚类
                for cluster in result.content_clusters:
                    await cursor.execute("""
                        INSERT INTO content_clusters 
                        (id, analysis_id, cluster_name, cluster_summary, post_ids, post_count, 
                         similarity_score, keywords)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        cluster.cluster_id,
                        result.analysis_id,
                        cluster.cluster_name,
                        cluster.cluster_summary,
                        json.dumps(cluster.post_ids, ensure_ascii=False),
                        cluster.post_count,
                        cluster.similarity_score,
                        json.dumps(cluster.keywords, ensure_ascii=False)
                    ))
                
                # 保存关键词频率
                for keyword in result.keyword_frequencies:
                    await cursor.execute("""
                        INSERT INTO keyword_frequencies 
                        (analysis_id, keyword, frequency, importance_score, related_posts)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        result.analysis_id,
                        keyword.keyword,
                        keyword.frequency,
                        keyword.importance_score,
                        json.dumps(keyword.related_posts, ensure_ascii=False)
                    ))
                
                # 保存情感分析
                for sentiment in result.sentiment_analysis:
                    await cursor.execute("""
                        INSERT INTO sentiment_analysis 
                        (analysis_id, post_id, sentiment, confidence, emotion_keywords)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        result.analysis_id,
                        sentiment.post_id,
                        sentiment.sentiment,
                        sentiment.confidence,
                        json.dumps(sentiment.emotion_keywords, ensure_ascii=False)
                    ))
                
                # 保存高校提及分析
                for uni in result.university_mentions:
                    await cursor.execute("""
                        INSERT INTO university_mentions 
                        (analysis_id, university_name, mention_count, sentiment_score, 
                         related_topics, post_ids)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        result.analysis_id,
                        uni.university_name,
                        uni.mention_count,
                        uni.sentiment_score,
                        json.dumps(uni.related_topics, ensure_ascii=False),
                        json.dumps(uni.post_ids, ensure_ascii=False)
                    ))
                
                # 保存专业分析
                for major in result.major_analysis:
                    await cursor.execute("""
                        INSERT INTO major_analysis 
                        (analysis_id, major_name, mention_count, job_prospect_sentiment, 
                         difficulty_level, related_universities, key_discussions)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        result.analysis_id,
                        major.major_name,
                        major.mention_count,
                        major.job_prospect_sentiment,
                        major.difficulty_level,
                        json.dumps(major.related_universities, ensure_ascii=False),
                        json.dumps(major.key_discussions, ensure_ascii=False)
                    ))
                
                # 保存分析洞察
                for i, insight in enumerate(result.insights):
                    await cursor.execute("""
                        INSERT INTO analysis_insights 
                        (analysis_id, insight_text, insight_type, importance_score)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        result.analysis_id,
                        insight,
                        'general',
                        1.0 - (i * 0.1)  # 按顺序递减重要性
                    ))
                
                logger.info(f"分析结果 {result.analysis_id} 已保存到数据库")
                
        except Exception as e:
            logger.error(f"保存分析结果失败: {e}", exc_info=True)
            raise

    async def get_analysis_history(self, skip: int = 0, limit: int = 20) -> Dict[str, Any]:
        """获取分析历史记录"""
        try:
            async with db_cursor() as cursor:
                # 查询分析历史
                await cursor.execute("""
                    SELECT car.id, car.task_id, car.analysis_type, car.total_posts_analyzed,
                           car.processing_time, car.created_at,
                           GROUP_CONCAT(ai.insight_text ORDER BY ai.importance_score DESC SEPARATOR '|') as insights
                    FROM content_analysis_results car
                    LEFT JOIN analysis_insights ai ON car.id = ai.analysis_id
                    GROUP BY car.id
                    ORDER BY car.created_at DESC
                    LIMIT %s OFFSET %s
                """, (limit, skip))
                
                results = await cursor.fetchall()
                
                # 查询总数
                await cursor.execute("SELECT COUNT(*) FROM content_analysis_results")
                total_result = await cursor.fetchone()
                total = total_result[0] if total_result else 0
                
                # 转换为响应格式
                analyses = []
                for row in results:
                    insights = row[6].split('|') if row[6] else []
                    analyses.append({
                        "analysis_id": row[0],
                        "task_id": row[1],
                        "analysis_type": row[2],
                        "total_posts_analyzed": row[3],
                        "processing_time": float(row[4]),
                        "created_at": row[5],
                        "insights": insights[:5]  # 最多5个洞察
                    })
                
                return {
                    "analyses": analyses,
                    "total": total,
                    "page": skip // limit + 1,
                    "page_size": limit
                }
                
        except Exception as e:
            logger.error(f"获取分析历史失败: {e}", exc_info=True)
            return {
                "analyses": [],
                "total": 0,
                "page": skip // limit + 1,
                "page_size": limit
            }

    async def get_analysis_by_id(self, analysis_id: str) -> Optional[ContentAnalysisResult]:
        """根据ID获取完整的分析结果"""
        try:
            async with db_cursor() as cursor:
                # 获取主分析记录
                await cursor.execute("""
                    SELECT id, task_id, analysis_type, total_posts_analyzed, processing_time, created_at
                    FROM content_analysis_results
                    WHERE id = %s
                """, (analysis_id,))
                
                main_result = await cursor.fetchone()
                if not main_result:
                    return None
                
                # 构建基础结果对象
                result = ContentAnalysisResult(
                    analysis_id=main_result[0],
                    task_id=main_result[1],
                    analysis_type=AnalysisType(main_result[2]),
                    total_posts_analyzed=main_result[3],
                    processing_time=float(main_result[4]),
                    created_at=main_result[5]
                )
                
                # 获取话题总结
                await cursor.execute("""
                    SELECT topic, summary, post_count, main_points, sentiment_trend, 
                           related_universities, related_majors
                    FROM topic_summaries WHERE analysis_id = %s
                """, (analysis_id,))
                
                topic_rows = await cursor.fetchall()
                for row in topic_rows:
                    result.topic_summaries.append(TopicSummary(
                        topic=row[0],
                        summary=row[1],
                        post_count=row[2],
                        main_points=json.loads(row[3]) if row[3] else [],
                        sentiment_trend=row[4],
                        related_universities=json.loads(row[5]) if row[5] else [],
                        related_majors=json.loads(row[6]) if row[6] else []
                    ))
                
                # 获取关键词频率
                await cursor.execute("""
                    SELECT keyword, frequency, importance_score, related_posts
                    FROM keyword_frequencies WHERE analysis_id = %s
                    ORDER BY frequency DESC
                """, (analysis_id,))
                
                keyword_rows = await cursor.fetchall()
                for row in keyword_rows:
                    result.keyword_frequencies.append(KeywordFrequency(
                        keyword=row[0],
                        frequency=row[1],
                        importance_score=float(row[2]),
                        related_posts=json.loads(row[3]) if row[3] else []
                    ))
                
                # 获取高校提及
                await cursor.execute("""
                    SELECT university_name, mention_count, sentiment_score, related_topics, post_ids
                    FROM university_mentions WHERE analysis_id = %s
                    ORDER BY mention_count DESC
                """, (analysis_id,))
                
                uni_rows = await cursor.fetchall()
                for row in uni_rows:
                    result.university_mentions.append(UniversityMention(
                        university_name=row[0],
                        mention_count=row[1],
                        sentiment_score=float(row[2]),
                        related_topics=json.loads(row[3]) if row[3] else [],
                        post_ids=json.loads(row[4]) if row[4] else []
                    ))
                
                # 获取专业分析
                await cursor.execute("""
                    SELECT major_name, mention_count, job_prospect_sentiment, difficulty_level,
                           related_universities, key_discussions
                    FROM major_analysis WHERE analysis_id = %s
                    ORDER BY mention_count DESC
                """, (analysis_id,))
                
                major_rows = await cursor.fetchall()
                for row in major_rows:
                    result.major_analysis.append(MajorAnalysis(
                        major_name=row[0],
                        mention_count=row[1],
                        job_prospect_sentiment=float(row[2]),
                        difficulty_level=row[3],
                        related_universities=json.loads(row[4]) if row[4] else [],
                        key_discussions=json.loads(row[5]) if row[5] else []
                    ))
                
                # 获取洞察
                await cursor.execute("""
                    SELECT insight_text FROM analysis_insights 
                    WHERE analysis_id = %s
                    ORDER BY importance_score DESC
                """, (analysis_id,))
                
                insight_rows = await cursor.fetchall()
                result.insights = [row[0] for row in insight_rows]
                
                return result
                
        except Exception as e:
            logger.error(f"获取分析结果失败: {e}", exc_info=True)
            return None

    async def delete_analysis(self, analysis_id: str) -> bool:
        """删除分析结果"""
        try:
            async with db_cursor() as cursor:
                # 检查分析是否存在
                await cursor.execute(
                    "SELECT id FROM content_analysis_results WHERE id = %s",
                    (analysis_id,)
                )
                result = await cursor.fetchone()
                
                if not result:
                    return False
                
                # 删除分析结果（由于外键约束，相关数据会级联删除）
                await cursor.execute(
                    "DELETE FROM content_analysis_results WHERE id = %s",
                    (analysis_id,)
                )
                
                logger.info(f"分析结果 {analysis_id} 已删除")
                return True
                
        except Exception as e:
            logger.error(f"删除分析结果失败: {e}", exc_info=True)
            return False
