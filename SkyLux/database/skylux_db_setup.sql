-- SkyLux Airlines Database Setup
-- This SQL file creates the database and tables for the SkyLux Airlines application

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS skylux_airlines;

-- Use the skylux_airlines database
USE skylux_airlines;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create airports table
CREATE TABLE IF NOT EXISTS airports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(3) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    timezone VARCHAR(50) NOT NULL
);

-- Create aircraft table
CREATE TABLE IF NOT EXISTS aircraft (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model VARCHAR(50) NOT NULL,
    capacity INT NOT NULL,
    first_class_seats INT NOT NULL,
    business_seats INT NOT NULL,
    economy_seats INT NOT NULL
);

-- Create flights table
CREATE TABLE IF NOT EXISTS flights (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flight_number VARCHAR(10) NOT NULL UNIQUE,
    origin_airport_id INT NOT NULL,
    destination_airport_id INT NOT NULL,
    aircraft_id INT NOT NULL,
    departure_time DATETIME NOT NULL,
    arrival_time DATETIME NOT NULL,
    economy_price DECIMAL(10, 2) NOT NULL,
    business_price DECIMAL(10, 2) NOT NULL,
    first_class_price DECIMAL(10, 2) NOT NULL,
    status ENUM('Scheduled', 'On Time', 'Delayed', 'Boarding', 'Departed', 'Arrived', 'Cancelled') DEFAULT 'Scheduled',
    gate VARCHAR(10),
    terminal VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (origin_airport_id) REFERENCES airports(id),
    FOREIGN KEY (destination_airport_id) REFERENCES airports(id),
    FOREIGN KEY (aircraft_id) REFERENCES aircraft(id)
);

-- Create bookings table
CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_reference VARCHAR(6) NOT NULL UNIQUE,
    user_id INT,
    flight_id INT NOT NULL,
    passenger_name VARCHAR(100) NOT NULL,
    passenger_email VARCHAR(100) NOT NULL,
    travel_class ENUM('economy', 'business', 'first') NOT NULL,
    seat_number VARCHAR(4),
    booking_status ENUM('Pending', 'Confirmed', 'Cancelled') DEFAULT 'Pending',
    total_amount DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (flight_id) REFERENCES flights(id)
);

-- Create cancellations table
CREATE TABLE IF NOT EXISTS cancellations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    cancellation_id VARCHAR(8) NOT NULL UNIQUE,
    refund_amount DECIMAL(10, 2),
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id)
);

-- Insert admin user (password is hashed in Python code)
-- INSERT INTO users (name, email, password, role)
-- VALUES ('Admin User', 'admin@skylux.com', 'HASHED_PASSWORD', 'admin');

-- Sample data is inserted by the Python script 