-- 核心存储过程 - 封装常用业务逻辑
-- 确保使用gradinsight数据库
USE gradinsight;
DELIMITER // -- =================================================
-- 1. 安全创建用户存储过程 - 替换user_service中的重复验证逻辑
-- =================================================
CREATE PROCEDURE sp_create_user_safe(
    IN p_username VARCHAR(50),
    IN p_email VARCHAR(100),
    IN p_password_hash VARCHAR(255),
    IN p_role ENUM('admin', 'user'),
    OUT p_result VARCHAR(255),
    OUT p_user_id INT
) BEGIN
DECLARE v_username_exists INT DEFAULT 0;
DECLARE v_email_exists INT DEFAULT 0;
DECLARE v_error_occurred BOOLEAN DEFAULT FALSE;
DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK;
SET p_result = 'ERROR: 创建用户时发生数据库错误';
SET p_user_id = NULL;
SET v_error_occurred = TRUE;
END;
-- 初始化输出参数
SET p_result = NULL;
SET p_user_id = NULL;
START TRANSACTION;
-- 检查用户名是否已存在
SELECT COUNT(*) INTO v_username_exists
FROM users
WHERE username = p_username;
IF v_username_exists > 0 THEN
SET p_result = 'ERROR: 用户名已存在';
SET p_user_id = NULL;
ROLLBACK;
ELSE -- 检查邮箱是否已存在
SELECT COUNT(*) INTO v_email_exists
FROM users
WHERE email = p_email;
IF v_email_exists > 0 THEN
SET p_result = 'ERROR: 邮箱已存在';
SET p_user_id = NULL;
ROLLBACK;
ELSE -- 创建用户
INSERT INTO users (
        username,
        email,
        password_hash,
        role,
        is_active,
        created_at,
        updated_at
    )
VALUES (
        p_username,
        p_email,
        p_password_hash,
        p_role,
        TRUE,
        NOW(),
        NOW()
    );
SET p_user_id = LAST_INSERT_ID();
SET p_result = 'SUCCESS: 用户创建成功';
COMMIT;
END IF;
END IF;
-- 设置会话变量，方便调用者获取结果
SET @p_result = p_result;
SET @p_user_id = p_user_id;
END // -- =================================================
-- 2. 快速获取统计数据存储过程 - 优化stats.py的多次查询
-- =================================================
CREATE PROCEDURE sp_get_quick_stats() BEGIN -- 返回所有关键统计数据的结果集
SELECT 'overview' as stat_type,
    total_posts,
    total_comments,
    completed_tasks,
    unique_keywords,
    active_users,
    total_post_likes,
    total_comment_likes
FROM v_data_overview
UNION ALL
SELECT 'task_stats' as stat_type,
    total_tasks,
    completed_tasks,
    failed_tasks,
    running_tasks,
    pending_tasks,
    success_rate,
    total_posts_collected
FROM v_task_stats;
END // -- =================================================
-- 3. 批量更新计数字段存储过程 - 修复可能的数据不一致
-- =================================================
CREATE PROCEDURE sp_fix_counters() BEGIN
DECLARE v_updated_tasks INT DEFAULT 0;
DECLARE v_updated_posts INT DEFAULT 0;
-- 修正任务的posts_collected字段
UPDATE tasks t
SET posts_collected = (
        SELECT COUNT(*)
        FROM posts p
        WHERE p.task_id = t.id
    );
SET v_updated_tasks = ROW_COUNT();
-- 修正帖子的comment_count字段
UPDATE posts p
SET comment_count = (
        SELECT COUNT(*)
        FROM comments c
        WHERE c.post_id = p.id
    );
SET v_updated_posts = ROW_COUNT();
-- 返回修正结果
SELECT v_updated_tasks as fixed_tasks,
    v_updated_posts as fixed_posts,
    CONCAT(
        '修正了 ',
        v_updated_tasks,
        ' 个任务和 ',
        v_updated_posts,
        ' 个帖子的计数'
    ) as summary;
END // -- =================================================
-- 4. 获取任务详情存储过程 - 一次查询获取完整任务信息
-- =================================================
CREATE PROCEDURE sp_get_task_details(IN p_task_id VARCHAR(64)) BEGIN
DECLARE v_task_exists INT DEFAULT 0;
-- 检查任务是否存在
SELECT COUNT(*) INTO v_task_exists
FROM tasks
WHERE id = p_task_id;
IF v_task_exists = 0 THEN
SELECT 'ERROR: 任务不存在' as error_message;
ELSE -- 返回任务详细信息
SELECT t.id,
    t.keyword,
    t.post_count as target_posts,
    t.posts_collected,
    ROUND(
        t.posts_collected * 100.0 / NULLIF(t.post_count, 0),
        2
    ) as completion_rate,
    t.status,
    CASE
        WHEN t.status = 0 THEN '已完成'
        WHEN t.status = 1 THEN '失败'
        WHEN t.status = 2 THEN '运行中'
        WHEN t.status = 3 THEN '待处理'
        ELSE '未知'
    END as status_desc,
    t.start_time,
    t.end_time,
    CASE
        WHEN t.end_time IS NOT NULL THEN TIMESTAMPDIFF(SECOND, t.start_time, t.end_time)
        ELSE TIMESTAMPDIFF(SECOND, t.start_time, NOW())
    END as duration_seconds,
    t.site,
    t.min_likes,
    t.include_comments,
    t.include_images,
    t.error_msg,
    t.created_at,
    t.updated_at,
    -- 实际帖子和评论数
    COALESCE(post_stats.actual_posts, 0) as actual_posts,
    COALESCE(post_stats.total_comments, 0) as total_comments,
    COALESCE(post_stats.total_likes, 0) as total_likes
FROM tasks t
    LEFT JOIN (
        SELECT p.task_id,
            COUNT(p.id) as actual_posts,
            SUM(p.comment_count) as total_comments,
            SUM(p.like_count) as total_likes
        FROM posts p
        GROUP BY p.task_id
    ) post_stats ON t.id = post_stats.task_id
WHERE t.id = p_task_id;
END IF;
END // -- =================================================
-- 5. 简单的数据清理存储过程
-- =================================================
CREATE PROCEDURE sp_cleanup_old_data(
    IN p_days_old INT,
    OUT p_deleted_count INT
) BEGIN
DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK;
SET p_deleted_count = -1;
-- 表示出错
END;
START TRANSACTION;
-- 删除旧的失败任务及其相关数据
DELETE FROM tasks
WHERE status = 1
    AND created_at < DATE_SUB(NOW(), INTERVAL p_days_old DAY);
SET p_deleted_count = ROW_COUNT();
COMMIT;
SELECT p_deleted_count as deleted_tasks,
    CONCAT('清理了 ', p_deleted_count, ' 个旧的失败任务') as summary;
END // -- =================================================
-- 6. 计算帖子热度分数存储过程（兼容版本）
-- =================================================
DELIMITER // -- 主版本：返回热度分数作为输出参数
CREATE PROCEDURE sp_calculate_hot_score(
    IN p_post_id VARCHAR(128),
    OUT p_hot_score DECIMAL(10, 4)
) BEGIN
DECLARE v_like_count BIGINT UNSIGNED DEFAULT 0;
DECLARE v_comment_count BIGINT UNSIGNED DEFAULT 0;
DECLARE v_collect_count BIGINT UNSIGNED DEFAULT 0;
DECLARE v_post_time DATETIME;
DECLARE v_hours_since_post DECIMAL(10, 2) DEFAULT 0;
DECLARE v_time_decay_factor DECIMAL(5, 4) DEFAULT 1.0000;
DECLARE v_content_length INT DEFAULT 0;
DECLARE v_content_factor DECIMAL(5, 4) DEFAULT 1.0000;
DECLARE v_post_exists INT DEFAULT 0;
DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN
SET p_hot_score = 0.0000;
END;
-- 检查帖子是否存在
SELECT COUNT(*) INTO v_post_exists
FROM posts
WHERE id = p_post_id;
IF v_post_exists = 0 THEN
SET p_hot_score = 0.0000;
ELSE -- 获取帖子基础数据
SELECT like_count,
    comment_count,
    collect_count,
    post_time,
    CHAR_LENGTH(content) INTO v_like_count,
    v_comment_count,
    v_collect_count,
    v_post_time,
    v_content_length
FROM posts
WHERE id = p_post_id;
-- 计算时间衰减因子（帖子越新热度越高）
SET v_hours_since_post = TIMESTAMPDIFF(HOUR, v_post_time, NOW());
-- 使用指数衰减函数，24小时内保持较高权重
IF v_hours_since_post <= 24 THEN
SET v_time_decay_factor = 1.0000;
ELSEIF v_hours_since_post <= 168 THEN -- 7天内
SET v_time_decay_factor = EXP(- v_hours_since_post / 168.0);
ELSE -- 超过7天
SET v_time_decay_factor = EXP(-1) * EXP(-(v_hours_since_post - 168) / 720.0);
-- 30天完全衰减
END IF;
-- 内容质量因子（基于内容长度）
IF v_content_length < 50 THEN
SET v_content_factor = 0.5000;
ELSEIF v_content_length < 200 THEN
SET v_content_factor = 0.8000;
ELSEIF v_content_length < 500 THEN
SET v_content_factor = 1.0000;
ELSEIF v_content_length < 1000 THEN
SET v_content_factor = 1.2000;
ELSE
SET v_content_factor = 1.5000;
END IF;
-- 计算热度分数
-- 公式: (点赞数 * 1 + 评论数 * 2 + 收藏数 * 3) * 时间衰减 * 内容质量
SET p_hot_score = (
        COALESCE(v_like_count, 0) * 1.0 + COALESCE(v_comment_count, 0) * 2.0 + COALESCE(v_collect_count, 0) * 3.0
    ) * v_time_decay_factor * v_content_factor;
-- 确保分数不为负数
IF p_hot_score < 0 THEN
SET p_hot_score = 0.0000;
END IF;
END IF;
END // -- 兼容版本：只接受一个参数，返回结果集
CREATE PROCEDURE sp_calculate_hot_score_simple(IN p_post_id VARCHAR(128)) BEGIN
DECLARE v_hot_score DECIMAL(10, 4) DEFAULT 0.0000;
-- 调用主版本获取热度分数
CALL sp_calculate_hot_score(p_post_id, v_hot_score);
-- 返回结果集
SELECT v_hot_score as hot_score,
    p_post_id as post_id;
END // -- =================================================
-- 7. 批量计算所有帖子热度分数存储过程
-- =================================================
CREATE PROCEDURE sp_calculate_all_hot_scores(OUT p_updated_count INT) BEGIN
DECLARE done INT DEFAULT FALSE;
DECLARE v_post_id VARCHAR(128);
DECLARE v_hot_score DECIMAL(10, 4);
DECLARE v_count INT DEFAULT 0;
-- 声明游标
DECLARE post_cursor CURSOR FOR
SELECT id
FROM posts
ORDER BY post_time DESC;
DECLARE CONTINUE HANDLER FOR NOT FOUND
SET done = TRUE;
DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK;
SET p_updated_count = -1;
-- 表示出错
END;
START TRANSACTION;
-- 如果posts表没有hot_score字段，先添加字段
-- 注意：这里假设hot_score字段已存在，如果不存在需要先执行ALTER TABLE语句
OPEN post_cursor;
read_loop: LOOP FETCH post_cursor INTO v_post_id;
IF done THEN LEAVE read_loop;
END IF;
-- 计算单个帖子的热度分数
CALL sp_calculate_hot_score(v_post_id, v_hot_score);
-- 更新帖子表（假设已添加hot_score字段）
-- UPDATE posts SET hot_score = v_hot_score WHERE id = v_post_id;
SET v_count = v_count + 1;
END LOOP;
CLOSE post_cursor;
SET p_updated_count = v_count;
COMMIT;
SELECT p_updated_count as updated_posts,
    CONCAT('成功计算了 ', p_updated_count, ' 个帖子的热度分数') as summary;
END // -- =================================================
-- 8. 获取热门帖子存储过程（按热度分数排序）
-- =================================================
CREATE PROCEDURE sp_get_hot_posts(
    IN p_limit INT,
    IN p_min_score DECIMAL(10, 4)
) BEGIN
DECLARE v_limit INT DEFAULT 20;
DECLARE v_min_score DECIMAL(10, 4) DEFAULT 0.0000;
-- 设置默认值
IF p_limit IS NULL
OR p_limit <= 0 THEN
SET v_limit = 20;
ELSE
SET v_limit = p_limit;
END IF;
IF p_min_score IS NULL THEN
SET v_min_score = 0.0000;
ELSE
SET v_min_score = p_min_score;
END IF;
-- 返回热门帖子列表，动态计算热度分数
SELECT p.id,
    p.title,
    p.poster,
    p.post_time,
    p.like_count,
    p.comment_count,
    p.collect_count,
    CASE
        WHEN TIMESTAMPDIFF(HOUR, p.post_time, NOW()) <= 24 THEN (
            p.like_count * 1.0 + p.comment_count * 2.0 + p.collect_count * 3.0
        ) * 1.0000 * CASE
            WHEN CHAR_LENGTH(p.content) < 50 THEN 0.5000
            WHEN CHAR_LENGTH(p.content) < 200 THEN 0.8000
            WHEN CHAR_LENGTH(p.content) < 500 THEN 1.0000
            WHEN CHAR_LENGTH(p.content) < 1000 THEN 1.2000
            ELSE 1.5000
        END
        WHEN TIMESTAMPDIFF(HOUR, p.post_time, NOW()) <= 168 THEN (
            p.like_count * 1.0 + p.comment_count * 2.0 + p.collect_count * 3.0
        ) * EXP(
            - TIMESTAMPDIFF(HOUR, p.post_time, NOW()) / 168.0
        ) * CASE
            WHEN CHAR_LENGTH(p.content) < 50 THEN 0.5000
            WHEN CHAR_LENGTH(p.content) < 200 THEN 0.8000
            WHEN CHAR_LENGTH(p.content) < 500 THEN 1.0000
            WHEN CHAR_LENGTH(p.content) < 1000 THEN 1.2000
            ELSE 1.5000
        END
        ELSE (
            p.like_count * 1.0 + p.comment_count * 2.0 + p.collect_count * 3.0
        ) * EXP(-1) * EXP(
            -(TIMESTAMPDIFF(HOUR, p.post_time, NOW()) - 168) / 720.0
        ) * CASE
            WHEN CHAR_LENGTH(p.content) < 50 THEN 0.5000
            WHEN CHAR_LENGTH(p.content) < 200 THEN 0.8000
            WHEN CHAR_LENGTH(p.content) < 500 THEN 1.0000
            WHEN CHAR_LENGTH(p.content) < 1000 THEN 1.2000
            ELSE 1.5000
        END
    END as hot_score,
    t.keyword as task_keyword,
    TIMESTAMPDIFF(HOUR, p.post_time, NOW()) as hours_since_post
FROM posts p
    JOIN tasks t ON p.task_id = t.id
HAVING hot_score >= v_min_score
ORDER BY hot_score DESC
LIMIT v_limit;
END // -- =================================================
-- 存储过程使用说明
-- =================================================
-- sp_create_user_safe: 替换user_service.py中的用户创建逻辑
-- sp_get_quick_stats: 替换stats.py中的多次查询
-- sp_fix_counters: 修复数据不一致问题
-- sp_get_task_details: 获取完整的任务信息
-- sp_cleanup_old_data: 简单的数据清理
-- sp_calculate_hot_score: 计算单个帖子的热度分数
-- sp_calculate_all_hot_scores: 批量计算所有帖子热度分数
-- sp_get_hot_posts: 获取热门帖子列表
-- 使用示例：
-- CALL sp_create_user_safe('testuser', 'test@example.com', 'hash', 'user', @result, @user_id);
-- CALL sp_get_quick_stats();
-- CALL sp_fix_counters();
-- CALL sp_get_task_details('task_id_here');
-- CALL sp_cleanup_old_data(90, @deleted_count);
-- CALL sp_calculate_hot_score('post_id_here', @hot_score);
-- CALL sp_calculate_all_hot_scores(@updated_count);
-- CALL sp_get_hot_posts(20, 1.0);
-- =================================================
-- 热度分数计算说明
-- =================================================
-- 基础分数 = 点赞数 * 1 + 评论数 * 2 + 收藏数 * 3
-- 时间衰减因子：
--   - 24小时内: 1.0 (无衰减)
--   - 7天内: 指数衰减 exp(-hours/168)
--   - 7天后: 进一步衰减 exp(-1) * exp(-(hours-168)/720)
-- 内容质量因子：
--   - <50字符: 0.5
--   - 50-200字符: 0.8
--   - 200-500字符: 1.0
--   - 500-1000字符: 1.2
--   - >1000字符: 1.5
-- 最终热度分数 = 基础分数 * 时间衰减因子 * 内容质量因子