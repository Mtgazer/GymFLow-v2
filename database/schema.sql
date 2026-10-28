-- =======================================================
-- GymFlow-v2 MySQL Database Schema Initialization Script
-- =======================================================

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS gym_flow
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE gym_flow;

-- =======================================================
-- Table: members
-- =======================================================
CREATE TABLE IF NOT EXISTS members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    age INT DEFAULT 0,
    gender VARCHAR(20) DEFAULT 'Unknown',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_member_phone (phone),
    INDEX idx_member_name (full_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =======================================================
-- Table: plans
-- =======================================================
CREATE TABLE IF NOT EXISTS plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    duration_days INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =======================================================
-- Table: subscriptions
-- =======================================================
CREATE TABLE IF NOT EXISTS subscriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    plan_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    payment_status ENUM('Paid', 'Pending', 'Cancelled') NOT NULL DEFAULT 'Paid',
    price_paid DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_subscription_member
        FOREIGN KEY (member_id) REFERENCES members (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_subscription_plan
        FOREIGN KEY (plan_id) REFERENCES plans (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    INDEX idx_sub_member (member_id),
    INDEX idx_sub_plan (plan_id),
    INDEX idx_sub_dates (start_date, end_date),
    INDEX idx_sub_status (payment_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =======================================================
-- Table: activity_logs (Audit trail for operations)
-- =======================================================
CREATE TABLE IF NOT EXISTS activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action_type VARCHAR(50) NOT NULL,
    entity_name VARCHAR(50) NOT NULL,
    entity_id INT DEFAULT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_log_action (action_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =======================================================
-- Seed Initial Plans
-- =======================================================
INSERT INTO plans (name, duration_days, price)
VALUES 
    ('Basic', 30, 250.00),
    ('Premium', 30, 350.00),
    ('Gold', 30, 500.00),
    ('VIP Annual', 365, 3500.00)
ON DUPLICATE KEY UPDATE 
    duration_days = VALUES(duration_days),
    price = VALUES(price);
