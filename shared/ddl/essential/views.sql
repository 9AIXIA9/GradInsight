-- 精简实用视图 - 专门解决当前代码痛点
-- 确保使用gradinsight数据库
USE gradinsight;
-- =================================================
-- 1. 热门关键词统计视图 - 替换stats.py中的复杂JOIN查询
-- =================================================
CREATE OR REPLACE VIEW v_hot_keywords AS
SELECT t.keyword,
    COUNT(p.id) AS post_count,
    COALESCE(SUM(p.like_count), 0) AS total_likes,
    COALESCE(AVG(p.like_count), 0) AS avg_likes,
    COUNT(DISTINCT p.poster) AS unique_posters,
    MAX(t.created_at) AS last_task_time
FROM tasks t
    LEFT JOIN posts p ON t.id = p.task_id
WHERE t.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY t.keyword
HAVING COUNT(p.id) > 0
ORDER BY COUNT(p.id) DESC,
    COALESCE(SUM(p.like_count), 0) DESC;
-- =================================================
-- 2. 任务统计概览视图 - 简化任务状态统计
-- =================================================
CREATE OR REPLACE VIEW v_task_stats AS
SELECT COUNT(*) as total_tasks,
    COUNT(
        CASE
            WHEN status = 0 THEN 1
        END
    ) as completed_tasks,
    COUNT(
        CASE
            WHEN status = 1 THEN 1
        END
    ) as failed_tasks,
    COUNT(
        CASE
            WHEN status = 2 THEN 1
        END
    ) as running_tasks,
    COUNT(
        CASE
            WHEN status = 3 THEN 1
        END
    ) as pending_tasks,
    ROUND(
        COUNT(
            CASE
                WHEN status = 0 THEN 1
            END
        ) * 100.0 / COUNT(*),
        2
    ) as success_rate,
    SUM(posts_collected) as total_posts_collected,
    COUNT(DISTINCT keyword) as unique_keywords
FROM tasks;
-- =================================================
-- 3. 数据概览视图 - 替换stats.py中的多个单独查询
-- =================================================
CREATE OR REPLACE VIEW v_data_overview AS
SELECT (
        SELECT COUNT(*)
        FROM posts
    ) as total_posts,
    (
        SELECT COUNT(*)
        FROM comments
    ) as total_comments,
    (
        SELECT COUNT(*)
        FROM tasks
        WHERE status = 0
    ) as completed_tasks,
    (
        SELECT COUNT(DISTINCT keyword)
        FROM tasks
    ) as unique_keywords,
    (
        SELECT COUNT(*)
        FROM users
        WHERE is_active = TRUE
    ) as active_users,
    (
        SELECT SUM(like_count)
        FROM posts
    ) as total_post_likes,
    (
        SELECT SUM(like_count)
        FROM comments
    ) as total_comment_likes;
-- =================================================
-- 4. 最新任务动态视图 - 用于生成系统动态
-- =================================================
CREATE OR REPLACE VIEW v_recent_activities AS
SELECT 'task' as activity_type,
    t.id as item_id,
    t.keyword as title,
    CONCAT('数据采集任务完成，收集', t.posts_collected, '条帖子') as content,
    t.end_time as activity_time,
    CASE
        WHEN t.status = 0 THEN 'success'
        WHEN t.status = 1 THEN 'error'
        ELSE 'info'
    END as activity_status
FROM tasks t
WHERE t.end_time IS NOT NULL
    AND t.end_time >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
    AND t.status IN (0, 1)
ORDER BY t.end_time DESC;
-- =================================================
-- 5. 用户简单统计视图 - 给用户服务使用
-- =================================================
CREATE OR REPLACE VIEW v_user_stats AS
SELECT COUNT(*) as total_users,
    COUNT(
        CASE
            WHEN is_active = TRUE THEN 1
        END
    ) as active_users,
    COUNT(
        CASE
            WHEN role = 'admin' THEN 1
        END
    ) as admin_count,
    COUNT(
        CASE
            WHEN role = 'user' THEN 1
        END
    ) as user_count
FROM users;
-- =================================================
-- 6. 帖子质量排行视图 - 用于发现优质内容
-- =================================================
CREATE OR REPLACE VIEW v_quality_posts AS
SELECT p.id,
    p.title,
    p.poster,
    p.post_time,
    p.like_count,
    p.comment_count,
    p.collect_count,
    (
        p.like_count + p.comment_count * 2 + p.collect_count * 3
    ) as quality_score,
    t.keyword as task_keyword
FROM posts p
    JOIN tasks t ON p.task_id = t.id
WHERE p.like_count > 0
    OR p.comment_count > 0
    OR p.collect_count > 0
ORDER BY quality_score DESC;
-- =================================================
-- 视图使用说明
-- =================================================
-- v_hot_keywords: 替换stats.py中get_hot_schools的复杂查询
-- v_task_stats: 快速获取任务统计信息
-- v_data_overview: 一次查询获取所有概览数据
-- v_recent_activities: 生成系统动态信息
-- v_user_stats: 用户统计信息
-- v_quality_posts: 发现和展示优质内容