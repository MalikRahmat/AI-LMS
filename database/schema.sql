-- Run once as MySQL root. Tables are created automatically by the Flask app (SQLAlchemy).
CREATE DATABASE IF NOT EXISTS ai_learning CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'ailearn'@'%' IDENTIFIED BY 'ailearn123';
GRANT ALL PRIVILEGES ON ai_learning.* TO 'ailearn'@'%';
FLUSH PRIVILEGES;
