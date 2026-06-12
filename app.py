from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'hospital_management_system_highly_secure_encryption_key'

# --- SAFE DATABASE CONNECTIVITY CONTROLLER ---
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Aasi@1612",  
        database="production_healthcare_db"
    )

# --- PORTAL IDENTIFICATION AND ROUTING GATEWAYS ---
@app.route('/')
def index():
    if 'user_id' in session: 
        return redirect(url_for('dashboard'))
    return render_template('auth.html', view='login')

@app.route('/auth/view/<mode>')
def switch_auth_view(mode):
    return render_template('auth.html', view=mode)

@app.route('/register', methods=['POST'])
def handle_register():
    name = request.form.get('full_name')
    email = request.form.get('email')
    password = request.form.get('password')
    role = 'Patient'  # Enforces that public registrations default entirely to Patient profiles
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (full_name, email, password_hash, role) VALUES (%s, %s, %s, %s)", (name, email, password, role))
        conn.commit()
        
        new_id = cursor.lastrowid
        cursor.execute("INSERT INTO notifications (user_id, message) VALUES (%s, %s)", (new_id, "Patient system authentication profiles initialized successfully."))
        conn.commit()
        
        cursor.close()
        conn.close()
        return redirect(url_for('switch_auth_view', mode='login'))
    except mysql.connector.Error as err:
        return f"<h3>Database Registration Error: {err}</h3>"

@app.route('/login', methods=['POST'])
def handle_login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s AND password_hash = %s", (email, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user:
        session['user_id'] = user['id']
        session['user_name'] = user['full_name']
        session['user_role'] = user['role']
        return redirect(url_for('dashboard'))
    return "<h2>Authentication Failure: Invalid Credentials. <a href='/'>Return to Access Interface</a></h2>"

# --- SYSTEM DASHBOARD CONSOLE ROUTER ---
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: 
        return redirect(url_for('index'))
        
    active_tab = request.args.get('tab', 'home')
    user_id = session['user_id']
    role = session['user_role']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # -------------------------------------------------------------------------
    # 1. ADMIN OPERATIONS WINDOW
    # -------------------------------------------------------------------------
    if role == 'Admin':
        cursor.execute("SELECT COUNT(*) as total FROM users WHERE role='Patient'")
        total_patients = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as total FROM users WHERE role='Doctor'")
        total_doctors = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as total FROM appointments")
        total_appointments = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as total FROM prescriptions")
        total_rx = cursor.fetchone()['total']
        
        # Comprehensive Medication Tracking Analytics Query
        cursor.execute("SELECT medication_name, COUNT(*) as count FROM prescriptions GROUP BY medication_name ORDER BY count DESC LIMIT 5")
        medication_analytics = cursor.fetchall()
        
        # Clinical Engagement Breakdown Logs
        cursor.execute("SELECT status, COUNT(*) as count FROM appointments GROUP BY status")
        status_metrics = cursor.fetchall()
        
        # Fetch Complete Operational Staff Roster
        cursor.execute("SELECT u.id, u.full_name, u.email, dp.specialization, dp.consultation_fee FROM users u JOIN doctor_profiles dp ON u.id = dp.user_id WHERE u.role = 'Doctor'")
        staff_roster = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return render_template('admin.html', active_tab=active_tab, patients_count=total_patients, doctors_count=total_doctors, appt_count=total_appointments, rx_count=total_rx, med_metrics=medication_analytics, status_metrics=status_metrics, admin_doctors=staff_roster)
        
    # -------------------------------------------------------------------------
    # 2. PRACTITIONER (DOCTOR) OPERATIONS WINDOW
    # -------------------------------------------------------------------------
    elif role == 'Doctor':
        cursor.execute("""
            SELECT a.id, p.full_name as patient_name, p.id as patient_id, a.appointment_date, a.appointment_time, a.status 
            FROM appointments a JOIN users p ON a.patient_id = p.id 
            WHERE a.doctor_id = %s ORDER BY a.appointment_date ASC
        """, (user_id,))
        doc_appointments = cursor.fetchall()
        
        # Fetch distinct patients currently linked to this doctor via appointments
        cursor.execute("SELECT DISTINCT p.id, p.full_name FROM appointments a JOIN users p ON a.patient_id = p.id WHERE a.doctor_id = %s", (user_id,))
        linked_patients = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return render_template('doctor.html', active_tab=active_tab, appointments=doc_appointments, patients=linked_patients)

    # -------------------------------------------------------------------------
    # 3. PATIENT OPERATIONS WINDOW
    # -------------------------------------------------------------------------
    else:
        cursor.execute("SELECT u.id, u.full_name, dp.specialization, dp.consultation_fee FROM users u JOIN doctor_profiles dp ON u.id = dp.user_id WHERE u.role = 'Doctor'")
        doctors_directory = cursor.fetchall()
        
        cursor.execute("""
            SELECT a.id, d.full_name as counterpart, dp.specialization, a.appointment_date, a.appointment_time, a.status 
            FROM appointments a JOIN users d ON a.doctor_id = d.id JOIN doctor_profiles dp ON d.id = dp.user_id
            WHERE a.patient_id = %s ORDER BY a.appointment_date ASC
        """, (user_id,))
        user_appointments = cursor.fetchall()
        
        cursor.execute("SELECT p.medication_name, p.dosage, p.frequency, d.full_name as doctor, p.issued_date FROM prescriptions p JOIN users d ON p.doctor_id = d.id WHERE p.patient_id = %s", (user_id,))
        user_prescriptions = cursor.fetchall()
        
        cursor.execute("SELECT mr.id, mr.document_name, mr.department, mr.upload_date, d.full_name as doctor FROM medical_records mr JOIN users d ON mr.doctor_id = d.id WHERE mr.patient_id = %s", (user_id,))
        user_records = cursor.fetchall()
        
        cursor.execute("SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        user_alerts = cursor.fetchall()
        unread_metric = sum(1 for alert in user_alerts if alert['is_unread'])
        
        cursor.close()
        conn.close()
        return render_template('patient.html', active_tab=active_tab, doctors=doctors_directory, appointments=user_appointments, prescriptions=user_prescriptions, records=user_records, alerts=user_alerts, unread_count=unread_metric)


# --- ACTION MODULE CONTROLLERS ---

@app.route('/admin/add-doctor', methods=['POST'])
def add_doctor():
    if session.get('user_role') != 'Admin': 
        return redirect(url_for('index'))
    
    name = request.form.get('full_name')
    email = request.form.get('email')
    password = request.form.get('password')
    spec = request.form.get('specialization')
    fee = request.form.get('fee')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (full_name, email, password_hash, role) VALUES (%s, %s, %s, 'Doctor')", (name, email, password))
        new_doc_id = cursor.lastrowid
        cursor.execute("INSERT INTO doctor_profiles (user_id, specialization, consultation_fee) VALUES (%s, %s, %s)", (new_doc_id, spec, fee))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Operational Exception: {err}")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('dashboard', tab='staff'))

@app.route('/book-appointment', methods=['POST'])
def book_appointment():
    if 'user_id' not in session: 
        return redirect(url_for('index'))
    
    doctor_id = request.form.get('doctor_id')
    appt_date = request.form.get('appt_date')
    appt_time = request.form.get('appt_time')
    patient_id = session['user_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time) VALUES (%s, %s, %s, %s)", (patient_id, doctor_id, appt_date, appt_time))
    
    cursor.execute("SELECT full_name FROM users WHERE id = %s", (doctor_id,))
    doc_name = cursor.fetchone()[0]
    
    # Cascade Notifications to both Patient and Doctor accounts
    cursor.execute("INSERT INTO notifications (user_id, message) VALUES (%s, %s)", (patient_id, f"Appointment confirmed with {doc_name} for {appt_date} at {appt_time}."))
    cursor.execute("INSERT INTO notifications (user_id, message) VALUES (%s, %s)", (doctor_id, f"New clinical booking registered by patient {session['user_name']} for {appt_date}."))
    
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('dashboard', tab='home'))

@app.route('/issue-prescription', methods=['POST'])
def issue_prescription():
    if session.get('user_role') != 'Doctor': 
        return redirect(url_for('index'))
    
    patient_id = request.form.get('patient_id')
    medication = request.form.get('medication_name')
    dosage = request.form.get('dosage')
    freq = request.form.get('frequency')
    doctor_id = session['user_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO prescriptions (patient_id, doctor_id, medication_name, dosage, frequency, issued_date) VALUES (%s, %s, %s, %s, %s, CURDATE())", (patient_id, doctor_id, medication, dosage, freq))
    
    # Notify Patient of incoming prescription updates
    cursor.execute("INSERT INTO notifications (user_id, message) VALUES (%s, %s)", (patient_id, f"Dr. {session['user_name']} has issued a new prescription regimen: {medication}."))
    
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('dashboard', tab='home'))

@app.route('/upload-record', methods=['POST'])
def upload_record():
    if session.get('user_role') != 'Doctor': 
        return redirect(url_for('index'))
    
    patient_id = request.form.get('patient_id')
    doc_name = request.form.get('document_name')
    dept = request.form.get('department')
    doctor_id = session['user_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO medical_records (patient_id, doctor_id, document_name, department, upload_date) VALUES (%s, %s, %s, %s, CURDATE())", (patient_id, doctor_id, doc_name, dept))
    
    # Notify Patient of new diagnostic charts logs additions
    cursor.execute("INSERT INTO notifications (user_id, message) VALUES (%s, %s)", (patient_id, f"New formal laboratory chart update '{doc_name}' added to your electronic medical health archive."))
    
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('dashboard', tab='home'))

@app.route('/notifications/clear')
def clear_notifications():
    if 'user_id' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE notifications SET is_unread = FALSE WHERE user_id = %s", (session['user_id'],))
        conn.commit()
        cursor.close()
        conn.close()
    return redirect(url_for('dashboard', tab='notifications'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=8000)