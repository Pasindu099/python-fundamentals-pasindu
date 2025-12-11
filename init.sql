CREATE DATABASE IF NOT EXISTS python_db;

USE python_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO users (username, email, age) VALUES
('pasindu', 'pasindu@example.com', 26),
('divya', 'divya@example.com', 27),
('lakshmi', 'lakshmi@example.com', 58),
('amitha', 'amitha@example.com', 58),
('devi', 'devi@example.com', 80),
('sunil', 'sunil@example.com', 35);