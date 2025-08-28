-- 创建plan_check数据库的SQL脚本
-- 使用此脚本在MySQL服务器上创建新数据库

-- 创建数据库
CREATE DATABASE IF NOT EXISTS plan_check 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

-- 选择数据库
USE plan_check;

-- 创建用户并授权（如果需要）
-- CREATE USER 'plan_user'@'%' IDENTIFIED BY 'plan_password';
-- GRANT ALL PRIVILEGES ON plan_check.* TO 'plan_user'@'%';
-- FLUSH PRIVILEGES;

-- 显示数据库信息
SELECT 
    SCHEMA_NAME as '数据库名称',
    CHARACTER_SET_NAME as '字符集',
    COLLATION_NAME as '排序规则'
FROM information_schema.SCHEMATA 
WHERE SCHEMA_NAME = 'plan_check';

-- 显示创建完成信息
SELECT 'plan_check数据库创建完成！' as '状态';
