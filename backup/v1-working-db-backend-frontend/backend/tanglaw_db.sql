-- ===============================================
-- DATABASE: tanglaw_db
-- Anonymous Counseling Chat Application
-- ===============================================

CREATE DATABASE IF NOT EXISTS tanglaw_db;
USE tanglaw_db;

-- ===============================================
-- 1. USERS TABLE
-- ===============================================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    is_counselor BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===============================================
-- 2. COUNSELOR CODES TABLE
-- ===============================================
CREATE TABLE counselor_codes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    is_used BOOLEAN DEFAULT 0
);

-- Sample counselor codes (you can add/remove later)
INSERT INTO counselor_codes (code) VALUES
('10000001'), ('10000002'), ('10000003'), ('10000004'),
('10000005'), ('10000006'), ('10000007'), ('10000008');

-- ===============================================
-- 3. MESSAGES TABLE
-- ===============================================
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_peer_support BOOLEAN DEFAULT 0,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ===============================================
-- 4. APPOINTMENTS TABLE
-- ===============================================
CREATE TABLE appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    counselor_id INT NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    status ENUM('pending', 'approved', 'completed', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (counselor_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ===============================================
-- 5. PEER GROUPS (optional / future use)
-- ===============================================
CREATE TABLE peer_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===============================================
-- DONE!
-- ===============================================

-- To verify:
-- SHOW TABLES;
-- SELECT * FROM counselor_codes;
