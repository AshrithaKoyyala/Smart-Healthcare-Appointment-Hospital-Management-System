-- 1. Wipe the old database clean to prevent duplicate errors
DROP DATABASE IF EXISTS production_healthcare_db;
CREATE DATABASE production_healthcare_db;
USE production_healthcare_db;

-- 2. Unified Identity Framework
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('Patient', 'Doctor', 'Admin') DEFAULT 'Patient',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Extended Doctor Metadata Profile Catalog
CREATE TABLE doctor_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE,
    specialization VARCHAR(100) NOT NULL,
    consultation_fee DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. Core Encounter Scheduling Log
CREATE TABLE appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    status ENUM('Scheduled', 'Completed', 'Cancelled') DEFAULT 'Scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 5. Prescription Lifecycle Tracking Logs
CREATE TABLE prescriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    medication_name VARCHAR(150) NOT NULL,
    dosage VARCHAR(50) NOT NULL,
    frequency VARCHAR(100) NOT NULL,
    issued_date DATE NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 6. Structured Medical Records Directory
CREATE TABLE medical_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    document_name VARCHAR(150) NOT NULL,
    department VARCHAR(100) NOT NULL,
    upload_date DATE NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 7. Cross-Platform Automated Alert Pipes
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    is_unread BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- --- EXTENSIVE SYSTEM DATA SEEDING PASS ---

-- Seed Core Administrator
INSERT INTO users (full_name, email, password_hash, role) 
VALUES ('System Administrator', 'admin@hospital.com', 'admin2026', 'Admin');

-- 🚨 UPDATED: Seed 6 Multi-Department Medical Practitioners from your screenshot
INSERT INTO users (full_name, email, password_hash, role) VALUES 
('Dr. Sarah chowdary', 'sarah2026@hospital.com', 'sarah2026', 'Doctor'),
('Dr. Robert Chen', 'robert2026@hospital.com', 'robert2026', 'Doctor'),
('Dr. Anita Desai', 'anita2026@hospital.com', 'anita2026', 'Doctor'),
('Dr. David Miller', 'david2026@hospital.com', 'david2026', 'Doctor'),
('Dr. Elena divvela', 'elena2026@hospital.com', 'elena2026', 'Doctor'),
('Dr. Deepak desai', 'deepak2026@hospital.com', 'deepak2026', 'Doctor');

-- Link Professional Specialty Profiles
INSERT INTO doctor_profiles (user_id, specialization, consultation_fee) VALUES 
(2, 'Cardiology', 180.00),
(3, 'Pediatrics', 120.00),
(4, 'Neurology', 250.00),
(5, 'Orthopedics', 160.00),
(6, 'Dermatology', 140.00),
(7, 'Oncology', 300.00);

-- Seed Default Patient for Immediate Core Operations Verification
INSERT INTO users (full_name, email, password_hash, role) 
VALUES ('Ashritha Koyyala', 'ashritha@patient.com', 'patient2026', 'Patient');

-- Pre-seed an appointment to verify dashboard elements instantly
INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, status)
VALUES (8, 2, '2026-06-15', '10:30:00', 'Scheduled');

INSERT INTO notifications (user_id, message) 
VALUES (8, 'Welcome to the SmartCare Portal. Your profile setup is fully complete.');

COMMIT;

