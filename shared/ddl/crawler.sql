-- MySQL数据库表结构定义
-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS gradinsight DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE gradinsight;
-- 任务表
CREATE TABLE IF NOT EXISTS tasks
(
    id                VARCHAR(64) PRIMARY KEY COMMENT '任务ID',
    parent_id         VARCHAR(64)              DEFAULT NULL COMMENT '父任务ID',
    wait_sub_count    BIGINT UNSIGNED          DEFAULT 0 COMMENT '等待的子任务数',
    status            INT             NOT NULL DEFAULT 0 COMMENT '任务状态: 0-已完成, 1-失败, 2-运行中, 3-待处理, 4-分治',
    posts_collected   INT UNSIGNED             DEFAULT 0 COMMENT '已收集的帖子数',
    start_time        DATETIME        NOT NULL COMMENT '开始时间',
    end_time          DATETIME                 DEFAULT NULL COMMENT '结束时间',
    error_msg         TEXT                     DEFAULT NULL COMMENT '错误信息',
    -- 任务请求参数
    site              INT             NOT NULL COMMENT '站点类型',
    keyword           VARCHAR(255)    NOT NULL COMMENT '关键词',
    post_count        BIGINT UNSIGNED NOT NULL COMMENT '帖子数量',
    min_likes         BIGINT UNSIGNED          DEFAULT 0 COMMENT '最小点赞数',
    comment_min_likes BIGINT UNSIGNED          DEFAULT 0 COMMENT '评论最小点赞数',
    comments_per_post BIGINT UNSIGNED          DEFAULT 0 COMMENT '每个帖子的评论数',
    include_comments  BOOLEAN                  DEFAULT FALSE COMMENT '是否包含评论',
    include_images    BOOLEAN                  DEFAULT FALSE COMMENT '是否包含图片',
    created_at        TIMESTAMP                DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at        TIMESTAMP                DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_parent_id (parent_id),
    INDEX idx_status (status),
    INDEX idx_keyword (keyword),
    INDEX idx_start_time (start_time)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT = '爬虫任务表';
-- 帖子表
CREATE TABLE IF NOT EXISTS posts
(
    id            VARCHAR(128) PRIMARY KEY COMMENT '帖子ID',
    task_id       VARCHAR(64)  NOT NULL COMMENT '任务ID',
    title         TEXT         NOT NULL COMMENT '帖子标题',
    content       LONGTEXT     NOT NULL COMMENT '帖子内容',
    poster        VARCHAR(255) NOT NULL COMMENT '发帖人',
    post_time     DATETIME     NOT NULL COMMENT '发帖时间',
    location      VARCHAR(255)    DEFAULT NULL COMMENT '位置',
    link          TEXT         NOT NULL COMMENT '帖子链接',
    tags          JSON            DEFAULT NULL COMMENT '标签数组',
    like_count    BIGINT UNSIGNED DEFAULT 0 COMMENT '点赞数',
    comment_count BIGINT UNSIGNED DEFAULT 0 COMMENT '评论数',
    collect_count BIGINT UNSIGNED DEFAULT 0 COMMENT '收藏数',
    image_urls    JSON            DEFAULT NULL COMMENT '图片URL数组',
    hot_score     DECIMAL(10, 4)  DEFAULT 0.0000 COMMENT '热度分数',
    created_at    TIMESTAMP       DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at    TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_task_id (task_id),
    INDEX idx_poster (poster),
    INDEX idx_post_time (post_time),
    INDEX idx_like_count (like_count),
    INDEX idx_comment_count (comment_count),
    FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT = '帖子表';
-- 评论表
CREATE TABLE IF NOT EXISTS comments
(
    id           VARCHAR(128) PRIMARY KEY COMMENT '评论ID',
    task_id      VARCHAR(64)  NOT NULL COMMENT '任务ID',
    post_id      VARCHAR(128) NOT NULL COMMENT '帖子ID',
    commenter    VARCHAR(255) NOT NULL COMMENT '评论者',
    comment_time DATETIME     NOT NULL COMMENT '评论时间',
    location     VARCHAR(255)    DEFAULT NULL COMMENT '位置',
    content      TEXT         NOT NULL COMMENT '评论内容',
    like_count   BIGINT UNSIGNED DEFAULT 0 COMMENT '点赞数',
    reply_count  BIGINT UNSIGNED DEFAULT 0 COMMENT '回复数',
    created_at   TIMESTAMP       DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_task_id (task_id),
    INDEX idx_post_id (post_id),
    INDEX idx_commenter (commenter),
    INDEX idx_comment_time (comment_time),
    INDEX idx_like_count (like_count),
    FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT = '评论表';