-- 用户认证系统数据库表结构定义

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS gradinsight DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE gradinsight;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    email VARCHAR(100) UNIQUE NOT NULL COMMENT '邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    role ENUM('admin', 'user') DEFAULT 'user' COMMENT '用户角色',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_is_active (is_active),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 插入默认管理员账户（密码: admin123）
INSERT INTO users (username, email, password_hash, role) VALUES
('admin', 'admin@gradinsight.com', '$2b$12$mRmR.Bp10JQRe0Yy5t1UB.FBOwXQRQWKd8/LFjQPMap4xS/ym5qYi', 'admin')
ON DUPLICATE KEY UPDATE username=username;

-- 插入默认普通用户账户（密码: user123456）
INSERT INTO users (username, email, password_hash, role) VALUES
('testuser', 'user@gradinsight.com', '$2b$12$wge4pcUw0nhjD7LtwrRpDeSJ4uS5WEG1lTJ7VKFOK.pNjBWI/VnDu', 'user')
ON DUPLICATE KEY UPDATE username=username;

-- 查看表结构
SHOW CREATE TABLE users;

-- 查看用户数据
SELECT id, username, email, role, is_active, created_at FROM users;
