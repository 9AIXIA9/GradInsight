-- 关键触发器 - 自动维护计数字段，避免数据不一致
-- 确保使用gradinsight数据库
USE gradinsight;

DELIMITER //

-- =================================================
-- 1. 帖子插入后自动更新任务的posts_collected
-- =================================================
CREATE TRIGGER tr_posts_after_insert
AFTER INSERT ON posts 
FOR EACH ROW 
BEGIN 
    -- 只更新任务计数，不处理热度分数（避免循环更新问题）
    UPDATE tasks
    SET posts_collected = posts_collected + 1,
        updated_at = NOW()
    WHERE id = NEW.task_id;
END //

-- =================================================
-- 2. 帖子删除后自动更新任务的posts_collected
-- =================================================
CREATE TRIGGER tr_posts_after_delete
AFTER DELETE ON posts 
FOR EACH ROW 
BEGIN 
    -- 自动减少任务的帖子收集数
    UPDATE tasks
    SET posts_collected = GREATEST(posts_collected - 1, 0),
        updated_at = NOW()
    WHERE id = OLD.task_id;
END //

-- =================================================
-- 3. 评论插入后自动更新帖子的comment_count
-- =================================================
CREATE TRIGGER tr_comments_after_insert
AFTER INSERT ON comments 
FOR EACH ROW 
BEGIN 
    -- 自动增加帖子的评论数
    UPDATE posts
    SET comment_count = comment_count + 1,
        updated_at = NOW()
    WHERE id = NEW.post_id;
END //

-- =================================================
-- 4. 评论删除后自动更新帖子的comment_count
-- =================================================
CREATE TRIGGER tr_comments_after_delete
AFTER DELETE ON comments 
FOR EACH ROW 
BEGIN 
    -- 自动减少帖子的评论数
    UPDATE posts
    SET comment_count = GREATEST(comment_count - 1, 0),
        updated_at = NOW()
    WHERE id = OLD.post_id;
END //

-- =================================================
-- 5. 任务状态更新时自动设置完成时间
-- =================================================
CREATE TRIGGER tr_tasks_before_update 
BEFORE UPDATE ON tasks 
FOR EACH ROW 
BEGIN 
    -- 如果任务变为完成状态，自动设置结束时间
    IF NEW.status = 0 AND OLD.status != 0 AND NEW.end_time IS NULL THEN
        SET NEW.end_time = NOW();
    END IF;
    
    -- 如果任务从完成状态变为其他状态，清除结束时间
    IF NEW.status != 0 AND OLD.status = 0 THEN
        SET NEW.end_time = NULL;
    END IF;
    
    -- 如果收集的帖子数等于目标数且任务正在运行，自动完成
    IF NEW.posts_collected = NEW.post_count 
       AND NEW.posts_collected > 0 
       AND NEW.status = 2 THEN
        SET NEW.status = 0;
        SET NEW.end_time = NOW();
    END IF;
END //

DELIMITER ;

-- =================================================
-- 触发器使用说明
-- =================================================
-- 这些触发器解决了以下问题：
-- 1. 自动维护posts_collected字段，避免手动更新
-- 2. 自动维护comment_count字段，确保数据一致性
-- 3. 自动处理任务完成逻辑，减少业务代码复杂度
-- 4. 确保时间戳字段的准确性
