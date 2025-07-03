-- =============================================================================
-- GradInsight 毕业季小红书数据分析平台 - Database Schema
-- Version: 1.0
-- Created: 2025-07-03
-- Description: 毕业季小红书数据分析平台完整数据库架构设计(16张表)
-- =============================================================================
-- Drop existing database (use with caution)
-- DROP DATABASE IF EXISTS gradInsight;
-- Create database
CREATE DATABASE IF NOT EXISTS gradInsight CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE gradInsight;
-- =============================================================================
-- 1. User Management Tables
-- =============================================================================
-- Users table
CREATE TABLE users (
    id VARCHAR(64) PRIMARY KEY COMMENT 'User ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT 'Username',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT 'Email address',
    password_hash VARCHAR(255) NOT NULL COMMENT 'Password hash',
    role ENUM('admin', 'teacher', 'student', 'researcher') DEFAULT 'student' COMMENT 'User role',
    university_id VARCHAR(64) COMMENT 'Associated university ID',
    real_name VARCHAR(50) COMMENT 'Real name',
    phone VARCHAR(20) COMMENT 'Phone number',
    avatar_url VARCHAR(500) COMMENT 'Avatar URL',
    status ENUM('active', 'inactive', 'banned') DEFAULT 'active' COMMENT 'Account status',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
    last_login_at TIMESTAMP NULL COMMENT 'Last login time',
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_university_id (university_id),
    INDEX idx_role (role),
    INDEX idx_status (status)
) ENGINE = InnoDB COMMENT = 'User basic information table';
-- User permissions table
CREATE TABLE user_permissions (
    id VARCHAR(64) PRIMARY KEY COMMENT 'Permission ID',
    user_id VARCHAR(64) NOT NULL COMMENT 'User ID',
    permission_code VARCHAR(100) NOT NULL COMMENT 'Permission code',
    resource_type VARCHAR(50) COMMENT 'Resource type',
    resource_id VARCHAR(64) COMMENT 'Resource ID',
    granted_by VARCHAR(64) COMMENT 'Granted by user ID',
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Granted time',
    expires_at TIMESTAMP NULL COMMENT 'Expiration time',
    status ENUM('active', 'revoked') DEFAULT 'active' COMMENT 'Permission status',
    INDEX idx_user_id (user_id),
    INDEX idx_permission_code (permission_code),
    INDEX idx_resource_type (resource_type),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE = InnoDB COMMENT = 'User permissions table';
-- =============================================================================
-- 2. University Management Tables
-- =============================================================================
-- Universities table
CREATE TABLE universities (
    id VARCHAR(64) PRIMARY KEY COMMENT 'University ID',
    name VARCHAR(200) NOT NULL COMMENT 'University name',
    short_name VARCHAR(50) COMMENT 'University short name',
    university_type ENUM(
        '985',
        '211',
        'double_first_class',
        'provincial',
        'private',
        'other'
    ) COMMENT 'University type',
    province VARCHAR(50) COMMENT 'Province',
    city VARCHAR(50) COMMENT 'City',
    established_year INT COMMENT 'Established year',
    website_url VARCHAR(500) COMMENT 'Official website',
    logo_url VARCHAR(500) COMMENT 'Logo URL',
    description TEXT COMMENT 'University description',
    student_count INT COMMENT 'Student count',
    teacher_count INT COMMENT 'Teacher count',
    campus_area DECIMAL(10, 2) COMMENT 'Campus area (acres)',
    ranking_national INT COMMENT 'National ranking',
    ranking_qs INT COMMENT 'QS world ranking',
    status ENUM('active', 'inactive') DEFAULT 'active' COMMENT 'Status',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
    INDEX idx_name (name),
    INDEX idx_province (province),
    INDEX idx_city (city),
    INDEX idx_university_type (university_type),
    INDEX idx_ranking_national (ranking_national)
) ENGINE = InnoDB COMMENT = 'University basic information table';
-- University majors table
CREATE TABLE university_majors (
    id VARCHAR(64) PRIMARY KEY COMMENT 'Major ID',
    university_id VARCHAR(64) NOT NULL COMMENT 'University ID',
    major_name VARCHAR(100) NOT NULL COMMENT 'Major name',
    major_code VARCHAR(20) COMMENT 'Major code',
    category VARCHAR(50) COMMENT 'Major category',
    degree_type ENUM('bachelor', 'master', 'phd') COMMENT 'Degree type',
    college_name VARCHAR(100) COMMENT 'College name',
    enrollment_quota INT COMMENT 'Enrollment quota',
    tuition_fee DECIMAL(10, 2) COMMENT 'Tuition fee',
    description TEXT COMMENT 'Major description',
    employment_rate DECIMAL(5, 2) COMMENT 'Employment rate (%)',
    average_salary DECIMAL(10, 2) COMMENT 'Average salary',
    status ENUM('active', 'inactive') DEFAULT 'active' COMMENT 'Status',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
    INDEX idx_university_id (university_id),
    INDEX idx_major_name (major_name),
    INDEX idx_category (category),
    INDEX idx_degree_type (degree_type),
    FOREIGN KEY (university_id) REFERENCES universities(id) ON DELETE CASCADE
) ENGINE = InnoDB COMMENT = 'University major information table';
-- =============================================================================
-- 3. Crawler Task Tables
-- =============================================================================
-- Crawler tasks table
CREATE TABLE crawler_tasks (
    id VARCHAR(64) PRIMARY KEY COMMENT 'Task ID',
    parent_id VARCHAR(64) NULL COMMENT 'Parent task ID (for divided tasks)',
    user_id VARCHAR(64) NOT NULL COMMENT 'Creator user ID',
    task_name VARCHAR(200) COMMENT 'Task name',
    status ENUM(
        'pending',
        'running',
        'completed',
        'failed',
        'divided'
    ) DEFAULT 'pending' COMMENT 'Task status',
    site TINYINT NOT NULL COMMENT 'Crawl site (1: XiaoHongShu)',
    keyword VARCHAR(500) NOT NULL COMMENT 'Keywords',
    post_count BIGINT DEFAULT 0 COMMENT 'Target post count',
    posts_collected INT DEFAULT 0 COMMENT 'Collected posts count',
    min_likes BIGINT DEFAULT 0 COMMENT 'Minimum likes',
    comment_min_likes BIGINT DEFAULT 0 COMMENT 'Comment minimum likes',
    comments_per_post INT DEFAULT 10 COMMENT 'Comments per post',
    include_comments BOOLEAN DEFAULT TRUE COMMENT 'Include comments',
    include_images BOOLEAN DEFAULT TRUE COMMENT 'Include images',
    wait_sub_count INT DEFAULT 0 COMMENT 'Waiting subtask count',
    start_time TIMESTAMP NULL COMMENT 'Start time',
    end_time TIMESTAMP NULL COMMENT 'End time',
    error_message TEXT COMMENT 'Error message',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
    INDEX idx_user_id (user_id),
    INDEX idx_parent_id (parent_id),
    INDEX idx_status (status),
    INDEX idx_site (site),
    INDEX idx_keyword (keyword),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES crawler_tasks(id) ON DELETE CASCADE
) ENGINE = InnoDB COMMENT = 'Crawler tasks table';
-- Task execution logs table
CREATE TABLE task_execution_logs (
    id VARCHAR(64) PRIMARY KEY COMMENT 'Log ID',
    task_id VARCHAR(64) NOT NULL COMMENT 'Task ID',
    log_level ENUM('INFO', 'WARN', 'ERROR', 'DEBUG') DEFAULT 'INFO' COMMENT 'Log level',
    message TEXT NOT NULL COMMENT 'Log message',
    details JSON COMMENT 'Detailed information (JSON format)',
    execution_time BIGINT COMMENT 'Execution time (milliseconds)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
    INDEX idx_task_id (task_id),
    INDEX idx_log_level (log_level),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (task_id) REFERENCES crawler_tasks(id) ON DELETE CASCADE
) ENGINE = InnoDB COMMENT = 'Task execution logs table';
-- =============================================================================
-- 4. Content Data Tables
-- =============================================================================
-- Posts table
CREATE TABLE posts (
    id VARCHAR(64) PRIMARY KEY COMMENT 'Post ID',
    task_id VARCHAR(64) NOT NULL COMMENT 'Task ID',
    title TEXT NOT NULL COMMENT 'Post title',
    poster VARCHAR(100) NOT NULL COMMENT 'Poster name',
    content LONGTEXT COMMENT 'Post content',
    post_time TIMESTAMP NOT NULL COMMENT 'Post time',
    location VARCHAR(200) COMMENT 'Geographic location',
    link VARCHAR(1000) NOT NULL COMMENT 'Post link',
    like_count BIGINT DEFAULT 0 COMMENT 'Like count',
    comment_count BIGINT DEFAULT 0 COMMENT 'Comment count',
    collect_count BIGINT DEFAULT 0 COMMENT 'Collect count',
    share_count BIGINT DEFAULT 0 COMMENT 'Share count',
    view_count BIGINT DEFAULT 0 COMMENT 'View count',
    sentiment_score DECIMAL(3, 2) COMMENT 'Sentiment score (-1 to 1)',
    university_mentioned VARCHAR(200) COMMENT 'Mentioned university',
    major_mentioned VARCHAR(100) COMMENT 'Mentioned major',
    graduation_year INT COMMENT 'Graduation year',
    is_verified BOOLEAN DEFAULT FALSE COMMENT 'Is verified user',
    platform_source TINYINT DEFAULT 1 COMMENT 'Platform source (1: XiaoHongShu)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
    INDEX idx_task_id (task_id),
    INDEX idx_poster (poster),
    INDEX idx_post_time (post_time),
    INDEX idx_like_count (like_count),
    INDEX idx_university_mentioned (university_mentioned),
    INDEX idx_graduation_year (graduation_year),
    INDEX idx_sentiment_score (sentiment_score),
    FULLTEXT idx_title_content (title, content),
    FOREIGN KEY (task_id) REFERENCES crawler_tasks(id) ON DELETE CASCADE
) ENGINE = InnoDB COMMENT = 'Post information table';
-- Post tags table
CREATE TABLE post_tags (
    id VARCHAR(64) PRIMARY KEY COMMENT 'Tag ID',
    post_id VARCHAR(64) NOT NULL COMMENT 'Post ID',
    tag VARCHAR(100) NOT NULL COMMENT 'Tag content',
    tag_type ENUM('system', 'user', 'extracted') DEFAULT 'extracted' COMMENT 'Tag type',
    confidence DECIMAL(3, 2) COMMENT 'Confidence score (0-1)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
    INDEX idx_post_id (post_id),
    INDEX idx_tag (tag),
    INDEX idx_tag_type (tag_type),
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
) ENGINE = InnoDB COMMENT = 'Post tags table';
-- Post images table
CREATE TABLE post_images (
    id VARCHAR(64) PRIMARY KEY COMMENT 'Image ID',
    post_id VARCHAR(64) NOT NULL COMMENT 'Post ID',
    image_url VARCHAR(1000) NOT NULL COMMENT 'Image URL',
    image_order INT DEFAULT 0 COMMENT 'Image order',
    image_width INT COMMENT 'Image width',
    image_height INT COMMENT 'Image height',
    file_size BIGINT COMMENT 'File size (bytes)',
    image_hash VARCHAR(64) COMMENT 'Image hash',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
    INDEX idx_post_id (post_id),
    INDEX idx_image_order (image_order),
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
) ENGINE = InnoDB COMMENT = 'Post images table';
-- Comments table
CREATE TABLE comments (
    id VARCHAR(64) PRIMARY KEY COMMENT 'Comment ID',
    task_id VARCHAR(64) NOT NULL COMMENT 'Task ID',
    post_id VARCHAR(64) NOT NULL COMMENT 'Post ID',
    commenter VARCHAR(100) NOT NULL COMMENT 'Commenter name',
    content TEXT NOT NULL COMMENT 'Comment content',
    comment_time TIMESTAMP NOT NULL COMMENT 'Comment time',
    location VARCHAR(200) COMMENT 'Geographic location',
    like_count BIGINT DEFAULT 0 COMMENT 'Like count',
    reply_count BIGINT DEFAULT 0 COMMENT 'Reply count',
    sentiment_score DECIMAL(3, 2) COMMENT 'Sentiment score (-1 to 1)',
    is_verified BOOLEAN DEFAULT FALSE COMMENT 'Is verified user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
    INDEX idx_task_id (task_id),
    INDEX idx_post_id (post_id),
    INDEX idx_commenter (commenter),
    INDEX idx_comment_time (comment_time),
    INDEX idx_like_count (like_count),
    INDEX idx_sentiment_score (sentiment_score),
    FULLTEXT idx_content (content),
    FOREIGN KEY (task_id) REFERENCES crawler_tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
) ENGINE = InnoDB COMMENT = 'Comments table';
-- =============================================================================
-- 5. Data Analysis Tables
-- =============================================================================
-- University influence analysis table
CREATE TABLE university_influence_analysis (
    id VARCHAR(64) PRIMARY KEY COMMENT 'Analysis ID',
    university_id VARCHAR(64) NOT NULL COMMENT 'University ID',
    analysis_date DATE NOT NULL COMMENT 'Analysis date',
    mention_count INT DEFAULT 0 COMMENT 'Mention count',
    positive_mention_count INT DEFAULT 0 COMMENT 'Positive mention count',
    negative_mention_count INT DEFAULT 0 COMMENT 'Negative mention count',
    neutral_mention_count INT DEFAULT 0 COMMENT 'Neutral mention count',
    total_likes BIGINT DEFAULT 0 COMMENT 'Total likes',
    total_comments BIGINT DEFAULT 0 COMMENT 'Total comments',
    total_shares BIGINT DEFAULT 0 COMMENT 'Total shares',
    influence_score DECIMAL(10, 2) COMMENT 'Influence score',
    ranking_position INT COMMENT 'Ranking position',
    hot_topics JSON COMMENT 'Hot topics (JSON array)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
    INDEX idx_university_id (university_id),
    INDEX idx_analysis_date (analysis_date),
    INDEX idx_influence_score (influence_score),
    INDEX idx_ranking_position (ranking_position),
    FOREIGN KEY (university_id) REFERENCES universities(id) ON DELETE CASCADE
) ENGINE = InnoDB COMMENT = 'University influence analysis table';
-- Employment trend analysis table
CREATE TABLE employment_trend_analysis (
    id VARCHAR(64) PRIMARY KEY COMMENT 'Analysis ID',
    major_id VARCHAR(64) COMMENT 'Major ID',
    industry VARCHAR(100) COMMENT 'Industry',
    city VARCHAR(50) COMMENT 'City',
    analysis_date DATE NOT NULL COMMENT 'Analysis date',
    graduation_year INT COMMENT 'Graduation year',
    mention_count INT DEFAULT 0 COMMENT 'Mention count',
    salary_mentions JSON COMMENT 'Salary mentions (JSON)',
    job_satisfaction_score DECIMAL(3, 2) COMMENT 'Job satisfaction score',
    employment_difficulty_score DECIMAL(3, 2) COMMENT 'Employment difficulty score',
    hot_companies JSON COMMENT 'Hot companies (JSON array)',
    skill_requirements JSON COMMENT 'Skill requirements (JSON array)',
    trend_score DECIMAL(10, 2) COMMENT 'Trend score',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
    INDEX idx_major_id (major_id),
    INDEX idx_industry (industry),
    INDEX idx_city (city),
    INDEX idx_analysis_date (analysis_date),
    INDEX idx_graduation_year (graduation_year),
    FOREIGN KEY (major_id) REFERENCES university_majors(id) ON DELETE
    SET NULL
) ENGINE = InnoDB COMMENT = 'Employment trend analysis table';
-- Sentiment analysis statistics table
CREATE TABLE sentiment_analysis_stats (
    id VARCHAR(64) PRIMARY KEY COMMENT 'Statistics ID',
    analysis_date DATE NOT NULL COMMENT 'Analysis date',
    analysis_type ENUM('university', 'major', 'overall', 'graduation') COMMENT 'Analysis type',
    target_id VARCHAR(64) COMMENT 'Target ID (University ID/Major ID etc.)',
    target_name VARCHAR(200) COMMENT 'Target name',
    total_posts INT DEFAULT 0 COMMENT 'Total posts',
    total_comments INT DEFAULT 0 COMMENT 'Total comments',
    positive_count INT DEFAULT 0 COMMENT 'Positive sentiment count',
    negative_count INT DEFAULT 0 COMMENT 'Negative sentiment count',
    neutral_count INT DEFAULT 0 COMMENT 'Neutral sentiment count',
    average_sentiment DECIMAL(3, 2) COMMENT 'Average sentiment score',
    sentiment_distribution JSON COMMENT 'Sentiment distribution (JSON)',
    keyword_sentiment JSON COMMENT 'Keyword sentiment (JSON)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
    INDEX idx_analysis_date (analysis_date),
    INDEX idx_analysis_type (analysis_type),
    INDEX idx_target_id (target_id),
    INDEX idx_average_sentiment (average_sentiment)
) ENGINE = InnoDB COMMENT = 'Sentiment analysis statistics table';
-- System configurations table
CREATE TABLE system_configs (
    id VARCHAR(64) PRIMARY KEY COMMENT 'Configuration ID',
    config_key VARCHAR(100) NOT NULL UNIQUE COMMENT 'Configuration key',
    config_value TEXT COMMENT 'Configuration value',
    config_type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string' COMMENT 'Configuration type',
    description TEXT COMMENT 'Configuration description',
    is_public BOOLEAN DEFAULT FALSE COMMENT 'Is public configuration',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
    INDEX idx_config_key (config_key),
    INDEX idx_is_public (is_public)
) ENGINE = InnoDB COMMENT = 'System configurations table';
-- =============================================================================
-- Stored Procedures
-- =============================================================================
DELIMITER //
-- Get university influence ranking
CREATE PROCEDURE sp_get_university_ranking(
    IN p_analysis_date DATE,
    IN p_limit_count INT
)
BEGIN
    -- 设置默认值
    IF p_limit_count IS NULL THEN
        SET p_limit_count = 20;
    END IF;
    SELECT u.id,
        u.name,
        u.short_name,
        nia.influence_score,
        nia.ranking_position,
        nia.mention_count,
        nia.positive_mention_count,
        nia.negative_mention_count
    FROM universities u
        INNER JOIN university_influence_analysis nia ON u.id = nia.university_id
    WHERE nia.analysis_date = p_analysis_date
    ORDER BY nia.ranking_position ASC
    LIMIT p_limit_count;
END //

-- Get employment trend by major
CREATE PROCEDURE sp_get_employment_trend(
    IN p_major_id VARCHAR(64),
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    SELECT eta.analysis_date,
        eta.mention_count,
        eta.job_satisfaction_score,
        eta.employment_difficulty_score,
        eta.trend_score,
        um.major_name,
        u.name as university_name
    FROM employment_trend_analysis eta
        LEFT JOIN university_majors um ON eta.major_id = um.id
        LEFT JOIN universities u ON um.university_id = u.id
    WHERE eta.major_id = p_major_id
        AND eta.analysis_date BETWEEN p_start_date AND p_end_date
    ORDER BY eta.analysis_date DESC;
END //

-- Calculate sentiment statistics
CREATE PROCEDURE sp_calculate_sentiment_stats(
    IN p_target_type VARCHAR(50),  -- 修改: ENUM类型改为VARCHAR
    IN p_target_id VARCHAR(64),
    IN p_analysis_date DATE
)
BEGIN
    DECLARE v_total_posts INT DEFAULT 0;
    DECLARE v_positive_count INT DEFAULT 0;
    DECLARE v_negative_count INT DEFAULT 0;
    DECLARE v_neutral_count INT DEFAULT 0;
    DECLARE v_avg_sentiment DECIMAL(3, 2) DEFAULT 0;

    -- 增加参数验证
    IF p_target_type NOT IN ('university', 'major', 'overall') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid target type';
    END IF;

    -- Calculate statistics based on target type
    IF p_target_type = 'university' THEN
        SELECT COUNT(*),
            SUM(
                CASE
                    WHEN sentiment_score > 0.1 THEN 1
                    ELSE 0
                END
            ),
            SUM(
                CASE
                    WHEN sentiment_score < -0.1 THEN 1
                    ELSE 0
                END
            ),
            SUM(
                CASE
                    WHEN sentiment_score BETWEEN -0.1 AND 0.1 THEN 1
                    ELSE 0
                END
            ),
            AVG(sentiment_score) INTO v_total_posts,
            v_positive_count,
            v_negative_count,
            v_neutral_count,
            v_avg_sentiment
        FROM posts
        WHERE university_mentioned = (
                SELECT name
                FROM universities
                WHERE id = p_target_id
            )
            AND DATE(post_time) = p_analysis_date;
    END IF;

    -- Insert or update statistics
    INSERT INTO sentiment_analysis_stats (
            id,
            analysis_date,
            analysis_type,
            target_id,
            total_posts,
            positive_count,
            negative_count,
            neutral_count,
            average_sentiment
        )
    VALUES (
            CONCAT(
                'stat_',
                UNIX_TIMESTAMP(),
                '_',
                FLOOR(RAND() * 1000)
            ),
            p_analysis_date,
            p_target_type,
            p_target_id,
            v_total_posts,
            v_positive_count,
            v_negative_count,
            v_neutral_count,
            v_avg_sentiment
        ) ON DUPLICATE KEY
    UPDATE total_posts = v_total_posts,
        positive_count = v_positive_count,
        negative_count = v_negative_count,
        neutral_count = v_neutral_count,
        average_sentiment = v_avg_sentiment;
END //

-- Update task statistics
CREATE PROCEDURE sp_update_task_statistics(IN p_task_id VARCHAR(64))
BEGIN
    UPDATE crawler_tasks
    SET posts_collected = (
            SELECT COUNT(*)
            FROM posts
            WHERE task_id = p_task_id
        )
    WHERE id = p_task_id;
END //

-- Archive old data
CREATE PROCEDURE sp_archive_old_data(IN p_days_to_keep INT)
BEGIN
    DECLARE v_cutoff_date DATE;

    -- 设置默认值
    IF p_days_to_keep IS NULL THEN
        SET p_days_to_keep = 365;
    END IF;

    SET v_cutoff_date = DATE_SUB(CURDATE(), INTERVAL p_days_to_keep DAY);

    -- Archive old posts
    DELETE FROM posts
    WHERE created_at < v_cutoff_date;

    -- Archive old comments
    DELETE FROM comments
    WHERE created_at < v_cutoff_date;

    -- Archive old task logs
    DELETE FROM task_execution_logs
    WHERE created_at < v_cutoff_date;
END //

DELIMITER ;

-- =============================================================================
-- Triggers
-- =============================================================================
DELIMITER //

-- Update post count when new post is inserted
CREATE TRIGGER tr_post_insert_update_task
AFTER INSERT ON posts FOR EACH ROW
BEGIN
    UPDATE crawler_tasks
    SET posts_collected = posts_collected + 1
    WHERE id = NEW.task_id;
END //

-- Update comment count when new comment is inserted
CREATE TRIGGER tr_comment_insert_update_post
AFTER INSERT ON comments FOR EACH ROW
BEGIN
    UPDATE posts
    SET comment_count = comment_count + 1
    WHERE id = NEW.post_id;
END //

-- Log task status changes
CREATE TRIGGER tr_task_status_log
AFTER UPDATE ON crawler_tasks FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO task_execution_logs (
                id,
                task_id,
                log_level,
                message,
                created_at
            )
        VALUES (
                CONCAT(
                    'log_',
                    UNIX_TIMESTAMP(),
                    '_',
                    FLOOR(RAND() * 1000)
                ),
                NEW.id,
                'INFO',
                CONCAT(
                    'Task status changed from ',
                    OLD.status,
                    ' to ',
                    NEW.status
                ),
                NOW()
            );
    END IF;
END //

-- Update timestamps
CREATE TRIGGER tr_user_update_timestamp
BEFORE UPDATE ON users FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END //

-- Validate sentiment score range
CREATE TRIGGER tr_post_sentiment_validation
BEFORE INSERT ON posts FOR EACH ROW
BEGIN
    IF NEW.sentiment_score IS NOT NULL
        AND (
            NEW.sentiment_score < -1
            OR NEW.sentiment_score > 1
        ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Sentiment score must be between -1 and 1';
    END IF;
END //

-- Auto-generate task name if not provided
CREATE TRIGGER tr_task_auto_name
BEFORE INSERT ON crawler_tasks FOR EACH ROW
BEGIN
    IF NEW.task_name IS NULL
        OR NEW.task_name = '' THEN
        SET NEW.task_name = CONCAT(
            'Task_',
            NEW.keyword,
            '_',
            DATE_FORMAT(NOW(), '%Y%m%d_%H%i%s')
        );
    END IF;
END //

DELIMITER ;

-- =============================================================================
-- Views
-- =============================================================================
-- University ranking view
CREATE VIEW v_university_ranking AS
SELECT u.id,
    u.name,
    u.short_name,
    u.university_type,
    u.province,
    u.city,
    nia.influence_score,
    nia.ranking_position,
    nia.mention_count,
    nia.analysis_date
FROM universities u
    LEFT JOIN university_influence_analysis nia ON u.id = nia.university_id
WHERE nia.analysis_date = (
        SELECT MAX(analysis_date)
        FROM university_influence_analysis
        WHERE university_id = u.id
    );
-- Active tasks summary view
CREATE VIEW v_active_tasks_summary AS
SELECT ct.id,
    ct.task_name,
    ct.status,
    ct.keyword,
    ct.posts_collected,
    ct.post_count,
    u.username as creator,
    ct.created_at,
    CASE
        WHEN ct.post_count > 0 THEN ROUND((ct.posts_collected / ct.post_count) * 100, 2)
        ELSE 0
    END as progress_percentage
FROM crawler_tasks ct
    JOIN users u ON ct.user_id = u.id
WHERE ct.status IN ('pending', 'running', 'divided');
-- Posts with engagement metrics view
CREATE VIEW v_posts_engagement AS
SELECT p.id,
    p.title,
    p.poster,
    p.post_time,
    p.like_count,
    p.comment_count,
    p.collect_count,
    p.share_count,
    p.sentiment_score,
    p.university_mentioned,
    (
        p.like_count + p.comment_count * 2 + p.collect_count * 3 + p.share_count * 2
    ) as engagement_score,
    COUNT(pt.id) as tag_count
FROM posts p
    LEFT JOIN post_tags pt ON p.id = pt.post_id
GROUP BY p.id;
-- User activity summary view
CREATE VIEW v_user_activity_summary AS
SELECT u.id,
    u.username,
    u.role,
    u.status,
    COUNT(DISTINCT ct.id) as total_tasks,
    COUNT(
        DISTINCT CASE
            WHEN ct.status = 'completed' THEN ct.id
        END
    ) as completed_tasks,
    COUNT(
        DISTINCT CASE
            WHEN ct.status = 'running' THEN ct.id
        END
    ) as running_tasks,
    COALESCE(SUM(ct.posts_collected), 0) as total_posts_collected,
    u.last_login_at,
    u.created_at
FROM users u
    LEFT JOIN crawler_tasks ct ON u.id = ct.user_id
GROUP BY u.id;
-- Sentiment analysis overview view
CREATE VIEW v_sentiment_overview AS
SELECT sas.analysis_date,
    sas.analysis_type,
    sas.target_name,
    sas.total_posts,
    sas.positive_count,
    sas.negative_count,
    sas.neutral_count,
    sas.average_sentiment,
    CASE
        WHEN sas.total_posts > 0 THEN ROUND((sas.positive_count / sas.total_posts) * 100, 2)
        ELSE 0
    END as positive_percentage,
    CASE
        WHEN sas.total_posts > 0 THEN ROUND((sas.negative_count / sas.total_posts) * 100, 2)
        ELSE 0
    END as negative_percentage
FROM sentiment_analysis_stats sas
ORDER BY sas.analysis_date DESC;
-- Hot topics view
CREATE VIEW v_hot_topics AS
SELECT pt.tag,
    COUNT(*) as mention_count,
    AVG(p.sentiment_score) as avg_sentiment,
    AVG(p.like_count) as avg_likes,
    DATE(p.post_time) as topic_date
FROM post_tags pt
    JOIN posts p ON pt.post_id = p.id
WHERE p.post_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
GROUP BY pt.tag,
    DATE(p.post_time)
HAVING mention_count >= 5
ORDER BY mention_count DESC,
    topic_date DESC;
-- Task performance metrics view
CREATE VIEW v_task_performance AS
SELECT ct.id,
    ct.task_name,
    ct.status,
    ct.posts_collected,
    ct.start_time,
    ct.end_time,
    CASE
        WHEN ct.end_time IS NOT NULL
        AND ct.start_time IS NOT NULL THEN TIMESTAMPDIFF(MINUTE, ct.start_time, ct.end_time)
        ELSE NULL
    END as duration_minutes,
    CASE
        WHEN ct.end_time IS NOT NULL
        AND ct.start_time IS NOT NULL
        AND ct.posts_collected > 0 THEN ROUND(
            ct.posts_collected / TIMESTAMPDIFF(MINUTE, ct.start_time, ct.end_time),
            2
        )
        ELSE 0
    END as posts_per_minute
FROM crawler_tasks ct
WHERE ct.status IN ('completed', 'failed');
-- Major employment insights view
CREATE VIEW v_major_employment_insights AS
SELECT um.id as major_id,
    um.major_name,
    u.name as university_name,
    um.category,
    um.employment_rate,
    um.average_salary,
    eta.job_satisfaction_score,
    eta.employment_difficulty_score,
    eta.trend_score,
    eta.analysis_date
FROM university_majors um
    JOIN universities u ON um.university_id = u.id
    LEFT JOIN employment_trend_analysis eta ON um.id = eta.major_id
WHERE eta.analysis_date = (
        SELECT MAX(analysis_date)
        FROM employment_trend_analysis
        WHERE major_id = um.id
    );
-- System health dashboard view
CREATE VIEW v_system_health_dashboard AS
SELECT (
        SELECT COUNT(*)
        FROM users
        WHERE status = 'active'
    ) as active_users,
    (
        SELECT COUNT(*)
        FROM crawler_tasks
        WHERE status = 'running'
    ) as running_tasks,
    (
        SELECT COUNT(*)
        FROM crawler_tasks
        WHERE status = 'pending'
    ) as pending_tasks,
    (
        SELECT COUNT(*)
        FROM posts
        WHERE DATE(created_at) = CURDATE()
    ) as posts_today,
    (
        SELECT COUNT(*)
        FROM comments
        WHERE DATE(created_at) = CURDATE()
    ) as comments_today,
    (
        SELECT COUNT(*)
        FROM task_execution_logs
        WHERE log_level = 'ERROR'
            AND DATE(created_at) = CURDATE()
    ) as errors_today;
-- Content quality metrics view
CREATE VIEW v_content_quality_metrics AS
SELECT DATE(p.post_time) as content_date,
    COUNT(*) as total_posts,
    AVG(p.like_count) as avg_likes,
    AVG(p.comment_count) as avg_comments,
    AVG(p.sentiment_score) as avg_sentiment,
    COUNT(
        CASE
            WHEN p.sentiment_score > 0.3 THEN 1
        END
    ) as high_positive_posts,
    COUNT(
        CASE
            WHEN p.sentiment_score < -0.3 THEN 1
        END
    ) as high_negative_posts,
    COUNT(
        CASE
            WHEN p.like_count > 1000 THEN 1
        END
    ) as viral_posts
FROM posts p
GROUP BY DATE(p.post_time)
ORDER BY content_date DESC;
-- Geographic distribution view
CREATE VIEW v_geographic_distribution AS
SELECT u.province,
    u.city,
    COUNT(DISTINCT u.id) as university_count,
    COUNT(DISTINCT p.id) as post_count,
    AVG(p.sentiment_score) as avg_sentiment,
    SUM(p.like_count) as total_likes
FROM universities u
    LEFT JOIN posts p ON u.name = p.university_mentioned
GROUP BY u.province,
    u.city
ORDER BY post_count DESC;
-- =============================================================================
-- Indexes for Performance Optimization
-- =============================================================================
-- Additional composite indexes
CREATE INDEX idx_posts_time_sentiment ON posts(post_time, sentiment_score);
CREATE INDEX idx_posts_university_year ON posts(university_mentioned, graduation_year);
CREATE INDEX idx_comments_time_likes ON comments(comment_time, like_count);
CREATE INDEX idx_tasks_status_created ON crawler_tasks(status, created_at);
CREATE INDEX idx_tags_type_confidence ON post_tags(tag_type, confidence);
-- =============================================================================
-- End of Enhanced Schema
-- =============================================================================
-- Show created tables
SHOW TABLES;
-- Show database information
SELECT TABLE_NAME as 'Table Name',
    TABLE_COMMENT as 'Table Comment',
    TABLE_ROWS as 'Estimated Rows'
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'gradInsight'
ORDER BY TABLE_NAME;
