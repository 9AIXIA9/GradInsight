-- =============================================
-- 完全重置并重新创建所有数据库对象
-- =============================================
USE gradinsight;
-- =================================================
SELECT '开始删除现有数据库对象...' as status;
-- 删除触发器
DROP TRIGGER IF EXISTS tr_posts_insert_hot_score;
DROP TRIGGER IF EXISTS tr_posts_update_hot_score;
DROP TRIGGER IF EXISTS tr_posts_before_insert;
DROP TRIGGER IF EXISTS tr_posts_before_update;
DROP TRIGGER IF EXISTS tr_posts_after_insert;
DROP TRIGGER IF EXISTS tr_posts_after_delete;
DROP TRIGGER IF EXISTS tr_comments_after_insert;
DROP TRIGGER IF EXISTS tr_comments_after_delete;
DROP TRIGGER IF EXISTS tr_tasks_before_update;
-- 删除存储过程
DROP PROCEDURE IF EXISTS sp_calculate_hot_score;
DROP PROCEDURE IF EXISTS sp_calculate_hot_score_simple;
DROP PROCEDURE IF EXISTS sp_calculate_all_hot_scores;
DROP PROCEDURE IF EXISTS sp_update_all_hot_scores;
DROP PROCEDURE IF EXISTS sp_get_hot_posts;
DROP PROCEDURE IF EXISTS sp_create_user_safe;
DROP PROCEDURE IF EXISTS sp_get_quick_stats;
DROP PROCEDURE IF EXISTS sp_fix_counters;
DROP PROCEDURE IF EXISTS sp_get_task_details;
DROP PROCEDURE IF EXISTS sp_cleanup_old_data;
-- 删除视图
DROP VIEW IF EXISTS v_data_overview;
DROP VIEW IF EXISTS v_task_stats;
DROP VIEW IF EXISTS v_post_stats;
DROP VIEW IF EXISTS v_user_stats;
DROP VIEW IF EXISTS v_post_details;
DROP VIEW IF EXISTS v_hot_posts;
DROP VIEW IF EXISTS v_task_details;