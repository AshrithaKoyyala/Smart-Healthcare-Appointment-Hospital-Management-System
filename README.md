# Smart-Healthcare-Appointment-Hospital-Management-System

# 🏥 SmartCare Enterprise Hospital Management System

A production-grade, multi-tier healthcare platform designed to streamline hospital operations, patient bookings, and electronic health record (EHR) management. Built with Python, Flask, and MySQL, this system features three completely isolated operational sandboxes with role-based access control and a real-time notification engine.

---

## ✨ Core Architecture & Features

### 1. 📊 Executive Administration Deck
* **System Analytics:** Real-time metrics tracking patient volume, appointment traffic, and medication distribution.
* **Staff Provisioning:** Secure portal for administrators to generate and assign credentials for new medical staff (restricting public users from creating unauthorized doctor profiles).

### 2. 👨‍⚕️ Medical Practitioner Workspace
* **Shift Ingestion Manifest:** Doctors can view their actively scheduled patients and upcoming consultation windows.
* **Clinical Operations:** Direct capabilities to authorize medical prescriptions and upload diagnostic charts/EHRs directly into a patient's secure file.

### 3. 👩‍💻 Patient Command Center
* **Booking Engine:** Dynamically populates available specialists, allowing patients to secure consultation slots.
* **Health Archive:** Patients can review active medical formulations (prescriptions) and download verified medical records uploaded by their doctor.
* **Automated Dispatch:** Cross-platform notification system that alerts patients when appointments are booked, prescriptions are issued, or files are uploaded.

---

## 🛠️ Technology Stack
* **Backend:** Python 3, Flask
* **Database:** MySQL (Relational Database Management)
* **Frontend:** HTML5, CSS3, Jinja2 Templating
* **Integration:** `mysql-connector-python`

---

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/AshrithaKoyyala/Smart-Healthcare-Appointment-Hospital-Management-System.git](https://github.com/AshrithaKoyyala/Smart-Healthcare-Appointment-Hospital-Management-System.git)
