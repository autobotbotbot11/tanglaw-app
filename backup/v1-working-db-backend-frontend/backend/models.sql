CREATE DATABASE tanglaw_db;
USE tanglaw_db;

-- All users (students & counselors)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('user','counselor') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Predefined counselor codes
CREATE TABLE counselor_codes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    is_used BOOLEAN DEFAULT FALSE
);

INSERT INTO counselor_codes (code) VALUES ('10000001'), ('10000002');
