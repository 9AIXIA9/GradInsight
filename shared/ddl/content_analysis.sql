-- 内容分析模块数据库表结构
-- 确保使用gradinsight数据库
USE gradinsight;
-- 内容分析结果表
CREATE TABLE IF NOT EXISTS content_analysis_results (
    id VARCHAR(64) PRIMARY KEY COMMENT '分析结果ID',
    task_id VARCHAR(64) DEFAULT NULL COMMENT '关联任务ID',
    analysis_type ENUM(
        'topic_summary',
        'content_clustering',
        'sentiment_analysis',
        'keyword_extraction',
        'university_mention',
        'major_analysis'
    ) NOT NULL COMMENT '分析类型',
    total_posts_analyzed INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '分析的帖子总数',
    processing_time DECIMAL(10, 3) NOT NULL DEFAULT 0.000 COMMENT '处理时间(秒)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '分析时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_task_id (task_id),
    INDEX idx_analysis_type (analysis_type),
    INDEX idx_created_at (created_at)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '内容分析结果表';
-- 话题总结表
CREATE TABLE IF NOT EXISTS topic_summaries (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    analysis_id VARCHAR(64) NOT NULL COMMENT '分析ID',
    topic VARCHAR(255) NOT NULL COMMENT '话题名称',
    summary TEXT NOT NULL COMMENT '话题摘要',
    post_count INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '相关帖子数量',
    main_points JSON DEFAULT NULL COMMENT '主要观点JSON数组',
    sentiment_trend ENUM('positive', 'negative', 'neutral') DEFAULT 'neutral' COMMENT '情感倾向',
    related_universities JSON DEFAULT NULL COMMENT '相关高校JSON数组',
    related_majors JSON DEFAULT NULL COMMENT '相关专业JSON数组',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_analysis_id (analysis_id),
    INDEX idx_topic (topic),
    INDEX idx_post_count (post_count),
    INDEX idx_sentiment_trend (sentiment_trend),
    FOREIGN KEY (analysis_id) REFERENCES content_analysis_results(id) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '话题总结表';
-- 内容聚类表
CREATE TABLE IF NOT EXISTS content_clusters (
    id VARCHAR(64) PRIMARY KEY COMMENT '聚类ID',
    analysis_id VARCHAR(64) NOT NULL COMMENT '分析ID',
    cluster_name VARCHAR(255) NOT NULL COMMENT '聚类名称',
    cluster_summary TEXT NOT NULL COMMENT '聚类内容摘要',
    post_ids JSON NOT NULL COMMENT '包含的帖子ID列表JSON',
    post_count INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '帖子数量',
    similarity_score DECIMAL(5, 4) NOT NULL DEFAULT 0.0000 COMMENT '聚类内相似度得分',
    keywords JSON DEFAULT NULL COMMENT '聚类关键词JSON数组',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_analysis_id (analysis_id),
    INDEX idx_cluster_name (cluster_name),
    INDEX idx_post_count (post_count),
    INDEX idx_similarity_score (similarity_score),
    FOREIGN KEY (analysis_id) REFERENCES content_analysis_results(id) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '内容聚类表';
-- 关键词频率表
CREATE TABLE IF NOT EXISTS keyword_frequencies (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    analysis_id VARCHAR(64) NOT NULL COMMENT '分析ID',
    keyword VARCHAR(255) NOT NULL COMMENT '关键词',
    frequency INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '出现频率',
    importance_score DECIMAL(10, 6) NOT NULL DEFAULT 0.000000 COMMENT '重要性得分',
    related_posts JSON DEFAULT NULL COMMENT '相关帖子ID JSON数组',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_analysis_id (analysis_id),
    INDEX idx_keyword (keyword),
    INDEX idx_frequency (frequency),
    INDEX idx_importance_score (importance_score),
    FOREIGN KEY (analysis_id) REFERENCES content_analysis_results(id) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '关键词频率表';
-- 情感分析表
CREATE TABLE IF NOT EXISTS sentiment_analysis (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    analysis_id VARCHAR(64) NOT NULL COMMENT '分析ID',
    post_id VARCHAR(128) NOT NULL COMMENT '帖子ID',
    sentiment ENUM('positive', 'negative', 'neutral') NOT NULL DEFAULT 'neutral' COMMENT '情感倾向',
    confidence DECIMAL(5, 4) NOT NULL DEFAULT 0.0000 COMMENT '置信度',
    emotion_keywords JSON DEFAULT NULL COMMENT '情感关键词JSON数组',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_analysis_id (analysis_id),
    INDEX idx_post_id (post_id),
    INDEX idx_sentiment (sentiment),
    INDEX idx_confidence (confidence),
    FOREIGN KEY (analysis_id) REFERENCES content_analysis_results(id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '情感分析表';
-- 高校提及分析表
CREATE TABLE IF NOT EXISTS university_mentions (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    analysis_id VARCHAR(64) NOT NULL COMMENT '分析ID',
    university_name VARCHAR(255) NOT NULL COMMENT '高校名称',
    mention_count INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '提及次数',
    sentiment_score DECIMAL(5, 4) NOT NULL DEFAULT 0.0000 COMMENT '情感得分(-1到1)',
    related_topics JSON DEFAULT NULL COMMENT '相关话题JSON数组',
    post_ids JSON DEFAULT NULL COMMENT '相关帖子ID JSON数组',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_analysis_id (analysis_id),
    INDEX idx_university_name (university_name),
    INDEX idx_mention_count (mention_count),
    INDEX idx_sentiment_score (sentiment_score),
    FOREIGN KEY (analysis_id) REFERENCES content_analysis_results(id) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '高校提及分析表';
-- 专业分析表
CREATE TABLE IF NOT EXISTS major_analysis (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    analysis_id VARCHAR(64) NOT NULL COMMENT '分析ID',
    major_name VARCHAR(255) NOT NULL COMMENT '专业名称',
    mention_count INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '提及次数',
    job_prospect_sentiment DECIMAL(5, 4) NOT NULL DEFAULT 0.0000 COMMENT '就业前景情感得分',
    difficulty_level ENUM('easy', 'medium', 'hard') DEFAULT 'medium' COMMENT '难度等级',
    related_universities JSON DEFAULT NULL COMMENT '相关高校JSON数组',
    key_discussions JSON DEFAULT NULL COMMENT '关键讨论点JSON数组',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_analysis_id (analysis_id),
    INDEX idx_major_name (major_name),
    INDEX idx_mention_count (mention_count),
    INDEX idx_job_prospect_sentiment (job_prospect_sentiment),
    INDEX idx_difficulty_level (difficulty_level),
    FOREIGN KEY (analysis_id) REFERENCES content_analysis_results(id) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '专业分析表';
-- 分析洞察表
CREATE TABLE IF NOT EXISTS analysis_insights (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    analysis_id VARCHAR(64) NOT NULL COMMENT '分析ID',
    insight_text TEXT NOT NULL COMMENT '洞察内容',
    insight_type ENUM(
        'keyword',
        'topic',
        'university',
        'major',
        'sentiment',
        'general'
    ) DEFAULT 'general' COMMENT '洞察类型',
    importance_score DECIMAL(5, 4) DEFAULT 0.5000 COMMENT '重要性评分',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_analysis_id (analysis_id),
    INDEX idx_insight_type (insight_type),
    INDEX idx_importance_score (importance_score),
    FOREIGN KEY (analysis_id) REFERENCES content_analysis_results(id) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '分析洞察表';