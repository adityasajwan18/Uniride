-- =====================================================
-- UniRide Database Schema
-- MySQL 8.x
-- =====================================================

DROP DATABASE IF EXISTS uniride;
CREATE DATABASE uniride CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE uniride;

-- ---------- Users ----------
CREATE TABLE users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(150) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    college     VARCHAR(150) DEFAULT 'GEHU Dehradun',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------- Rides ----------
CREATE TABLE rides (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    driver_name  VARCHAR(100) NOT NULL,
    contact_number VARCHAR(20),
    source       VARCHAR(100) NOT NULL,
    destination  VARCHAR(100) NOT NULL,
    time         VARCHAR(20)  NOT NULL,
    seats        INT NOT NULL DEFAULT 1,
    distance     FLOAT DEFAULT 0,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_source (source),
    INDEX idx_destination (destination)
);

-- ---------- Bookings ----------
CREATE TABLE bookings (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    ride_id         INT NOT NULL,
    passenger_name  VARCHAR(100) NOT NULL,
    booking_time    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status          ENUM('pending', 'confirmed', 'cancelled') DEFAULT 'confirmed',
    FOREIGN KEY (ride_id) REFERENCES rides(id) ON DELETE CASCADE
);

-- ---------- Seed Data ----------
INSERT INTO users (name, email, password, college) VALUES
('Aarav Sharma', 'aarav@gehu.ac.in', 'hashed_pw_1', 'GEHU Dehradun'),
('Priya Negi',   'priya@gehu.ac.in', 'hashed_pw_2', 'GEHU Dehradun'),
('Rohan Bisht',  'rohan@gehu.ac.in', 'hashed_pw_3', 'GEHU Dehradun');

INSERT INTO rides (driver_name, source, destination, time, seats, distance) VALUES
('Aarav Sharma',  'Kargi Chowk',    'GEHU', '08:30', 3, 14),
('Priya Negi',    'ISBT',           'GEHU', '09:00', 2, 11),
('Rohan Bisht',   'Clock Tower',    'GEHU', '08:45', 4, 13),
('Ishaan Rawat',  'Subhash Nagar',  'GEHU', '09:15', 1, 8),
('Megha Joshi',   'Balliwala',      'GEHU', '08:50', 3, 6),
('Karan Thapa',   'Prem Nagar',     'GEHU', '09:10', 2, 3);
