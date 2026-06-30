-- AI心情日记系统数据库表结构
-- MySQL 8.0

-- 创建数据库
CREATE DATABASE IF NOT EXISTS ai_mood_diary DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE ai_mood_diary;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '密码，bcrypt加密存储',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱',
    nickname VARCHAR(50) COMMENT '昵称',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 日记表
CREATE TABLE IF NOT EXISTS diaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    title VARCHAR(200) NOT NULL COMMENT '日记标题',
    content TEXT NOT NULL COMMENT '日记内容',
    diary_date DATE NOT NULL COMMENT '日记日期',
    mood_tag VARCHAR(50) DEFAULT 'neutral' COMMENT '情绪标签(happy/sad/neutral/anxious/angry/peaceful)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='日记表';

-- 情绪分析结果表
CREATE TABLE IF NOT EXISTS emotion_analyses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    diary_id INT NOT NULL COMMENT '日记ID',
    emotion_label VARCHAR(50) NOT NULL COMMENT 'AI分析的情绪标签',
    emotion_score DECIMAL(3,2) DEFAULT 0.50 COMMENT '情绪得分(0-1)',
    ai_feedback TEXT COMMENT 'AI生成的反馈建议',
    model_name VARCHAR(100) COMMENT '使用的AI模型名称',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '分析时间',
    FOREIGN KEY (diary_id) REFERENCES diaries(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='情绪分析结果表';

-- 创建索引
CREATE INDEX idx_diaries_user_id ON diaries(user_id);
CREATE INDEX idx_diaries_diary_date ON diaries(diary_date);
CREATE INDEX idx_diaries_mood_tag ON diaries(mood_tag);
CREATE INDEX idx_emotion_analyses_diary_id ON emotion_analyses(diary_id);
