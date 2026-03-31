"""
Crime Report Portal - Flask Backend (SQLite Demo Version)
Modules: User Registration, Crime Submission, Admin Dashboard, Report Tracking, 
File Upload, Complaint Management, Notifications
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import json
from functools import wraps
from dotenv import load_dotenv
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
DATABASE = 'crime_portal.db'

# Initialize SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DATABASE}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

# ============ DATABASE MODELS ============

class User(db.Model):
    """User Registration and Login Module"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_verified = db.Column(db.Boolean, default=False)
    
    complaints = db.relationship('Complaint', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }


class Complaint(db.Model):
    """Crime Report Submission Module"""
    __tablename__ = 'complaints'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    incident_date = db.Column(db.DateTime, nullable=False)
    
    status = db.Column(db.String(50), default='Submitted')  # Submitted, In Review, Verified, Rejected, Closed
    priority = db.Column(db.String(20), default='Medium')  # Low, Medium, High, Critical
    police_notes = db.Column(db.Text, default='')  # Admin notes
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    evidence_files = db.relationship('EvidenceFile', backref='complaint', lazy=True, cascade='all, delete-orphan')
    tracking_updates = db.relationship('TrackingUpdate', backref='complaint', lazy=True, cascade='all, delete-orphan')
    management_notes = db.relationship('ManagementNote', backref='complaint', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'reporter_email': self.user.email,
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'incident_date': self.incident_date.isoformat(),
            'status': self.status,
            'priority': self.priority,
            'police_notes': self.police_notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class EvidenceFile(db.Model):
    """File Upload Module"""
    __tablename__ = 'evidence_files'
    
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)
    file_size = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'file_type': self.file_type,
            'uploaded_at': self.uploaded_at.isoformat()
        }


class TrackingUpdate(db.Model):
    """Report Tracking Module"""
    __tablename__ = 'tracking_updates'
    
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status,
            'message': self.message,
            'created_at': self.created_at.isoformat()
        }


class ManagementNote(db.Model):
    """Complaint Management System"""
    __tablename__ = 'management_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50))  # 'verify', 'reject', 'assign', 'update'
    note = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    admin = db.relationship('User')


class Notification(db.Model):
    """Notification Module"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'))
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50))  # 'status_update', 'verification', 'rejection', 'general'
    is_read = db.Column(db.Boolean, default=False)
    sent_via = db.Column(db.String(50), default='portal')  # 'portal', 'email', 'both'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'type': self.notification_type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat()
        }


# ============ AUTHENTICATION HELPERS ============

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


# ============ MODULE 1: USER REGISTRATION AND LOGIN ============

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        user = User(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            role='user'
        )
        user.set_password(data.get('password'))
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'Registration successful', 'user_id': user.id}), 201
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        user = User.query.filter_by(email=data.get('email')).first()
        
        if user and user.verify_password(data.get('password')):
            session['user_id'] = user.id
            session['user_role'] = user.role
            user.last_login = datetime.utcnow()
            db.session.commit()
            return jsonify({'message': 'Login successful', 'role': user.role}), 200
        
        return jsonify({'error': 'Invalid email or password'}), 401
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# ============ MODULE 2: CRIME REPORT SUBMISSION ============

@app.route('/api/complaint/submit', methods=['POST'])
@login_required
def submit_complaint():
    user_id = session['user_id']
    data = request.form
    
    complaint = Complaint(
        user_id=user_id,
        category=data.get('category'),
        title=data.get('title'),
        description=data.get('description'),
        location=data.get('location'),
        latitude=data.get('latitude', type=float),
        longitude=data.get('longitude', type=float),
        incident_date=datetime.fromisoformat(data.get('incident_date')),
        priority=data.get('priority', 'Medium')
    )
    
    # Handle file uploads
    if 'evidence_files' in request.files:
        files = request.files.getlist('evidence_files')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(filepath)
                
                evidence = EvidenceFile(
                    filename=filename,
                    file_path=filepath,
                    file_type=filename.rsplit('.', 1)[1].lower(),
                    file_size=len(file.read())
                )
                complaint.evidence_files.append(evidence)
    
    db.session.add(complaint)
    db.session.commit()
    
    # Create initial tracking update
    tracking = TrackingUpdate(
        complaint_id=complaint.id,
        status='Submitted',
        message='Your complaint has been received successfully.'
    )
    db.session.add(tracking)
    
    # Create notification
    notification = Notification(
        user_id=user_id,
        complaint_id=complaint.id,
        title='Crime Report Submitted',
        message='Your crime report has been submitted successfully.',
        notification_type='status_update',
        sent_via='both'
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({'message': 'Complaint submitted successfully', 'complaint_id': complaint.id}), 201


@app.route('/api/complaint/<int:complaint_id>', methods=['GET'])
@login_required
def get_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    
    if complaint.user_id != session['user_id'] and session.get('user_role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = complaint.to_dict()
    data['evidence_files'] = [ef.to_dict() for ef in complaint.evidence_files]
    data['tracking_updates'] = [tu.to_dict() for tu in complaint.tracking_updates]
    
    return jsonify(data), 200


@app.route('/report', methods=['GET'])
@login_required
def submit_report_page():
    return render_template('submit_report.html')


# ============ MODULE 3: ADMIN LOGIN AND DASHBOARD ============

@app.route('/admin/dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    total_complaints = Complaint.query.count()
    submitted = Complaint.query.filter_by(status='Submitted').count()
    in_review = Complaint.query.filter_by(status='In Review').count()
    verified = Complaint.query.filter_by(status='Verified').count()
    
    return render_template('admin_dashboard.html', 
                         total=total_complaints,
                         submitted=submitted,
                         in_review=in_review,
                         verified=verified)


@app.route('/api/admin/complaints', methods=['GET'])
@admin_required
def get_all_complaints():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', None)
    
    query = Complaint.query
    if status:
        query = query.filter_by(status=status)
    
    complaints = query.paginate(page=page, per_page=10)
    
    return jsonify({
        'complaints': [c.to_dict() for c in complaints.items],
        'total': complaints.total,
        'pages': complaints.pages
    }), 200


# ============ MODULE 4: REPORT TRACKING ============

@app.route('/api/complaint/<int:complaint_id>/tracking', methods=['GET'])
@login_required
def get_tracking_updates(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    
    if complaint.user_id != session['user_id'] and session.get('user_role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    updates = TrackingUpdate.query.filter_by(complaint_id=complaint_id).order_by(TrackingUpdate.created_at.desc()).all()
    
    return jsonify({
        'status': complaint.status,
        'priority': complaint.priority,
        'updates': [u.to_dict() for u in updates]
    }), 200


@app.route('/tracking', methods=['GET'])
@login_required
def tracking_page():
    user_id = session['user_id']
    complaints = Complaint.query.filter_by(user_id=user_id).all()
    return render_template('tracking.html', complaints=complaints)


# ============ MODULE 5: FILE UPLOAD ============

@app.route('/api/complaint/<int:complaint_id>/upload', methods=['POST'])
@login_required
def upload_evidence(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    
    if complaint.user_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(filepath)
        
        evidence = EvidenceFile(
            complaint_id=complaint_id,
            filename=filename,
            file_path=filepath,
            file_type=filename.rsplit('.', 1)[1].lower(),
            file_size=os.path.getsize(filepath)
        )
        
        db.session.add(evidence)
        db.session.commit()
        
        return jsonify({'message': 'File uploaded successfully', 'file': evidence.to_dict()}), 201
    
    return jsonify({'error': 'Invalid file type'}), 400


# ============ MODULE 6: COMPLAINT MANAGEMENT SYSTEM ============

@app.route('/api/admin/complaint/<int:complaint_id>/verify', methods=['POST'])
@admin_required
def verify_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    data = request.get_json()
    
    complaint.status = 'Verified'
    
    note = ManagementNote(
        complaint_id=complaint_id,
        admin_id=session['user_id'],
        action='verify',
        note=data.get('note', '')
    )
    
    tracking = TrackingUpdate(
        complaint_id=complaint_id,
        status='Verified',
        message='Your complaint has been verified by authorities.'
    )
    
    notification = Notification(
        user_id=complaint.user_id,
        complaint_id=complaint_id,
        title='Report Verified',
        message='Your crime report has been verified.',
        notification_type='verification',
        sent_via='both'
    )
    
    db.session.add_all([note, tracking, notification])
    db.session.commit()
    
    # Send email notification
    send_email_notification(complaint.user, 'Your crime report has been verified', 
                          'Your report #' + str(complaint_id) + ' has been verified.')
    
    return jsonify({'message': 'Complaint verified'}), 200


@app.route('/api/admin/complaint/<int:complaint_id>/reject', methods=['POST'])
@admin_required
def reject_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    data = request.get_json()
    
    complaint.status = 'Rejected'
    
    note = ManagementNote(
        complaint_id=complaint_id,
        admin_id=session['user_id'],
        action='reject',
        note=data.get('reason', '')
    )
    
    tracking = TrackingUpdate(
        complaint_id=complaint_id,
        status='Rejected',
        message=data.get('reason', 'Your complaint has been rejected.')
    )
    
    notification = Notification(
        user_id=complaint.user_id,
        complaint_id=complaint_id,
        title='Report Rejected',
        message='Your crime report has been rejected. Reason: ' + data.get('reason', 'See details'),
        notification_type='rejection',
        sent_via='both'
    )
    
    db.session.add_all([note, tracking, notification])
    db.session.commit()
    
    send_email_notification(complaint.user, 'Crime Report Rejected', 
                          'Your report #' + str(complaint_id) + ' has been rejected: ' + data.get('reason', ''))
    
    return jsonify({'message': 'Complaint rejected'}), 200


@app.route('/api/admin/complaint/<int:complaint_id>/update-status', methods=['POST'])
@admin_required
def update_complaint_status(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    data = request.get_json()
    
    old_status = complaint.status
    complaint.status = data.get('status')
    complaint.priority = data.get('priority', complaint.priority)
    complaint.police_notes = data.get('police_notes', complaint.police_notes)
    
    tracking = TrackingUpdate(
        complaint_id=complaint_id,
        status=data.get('status'),
        message=data.get('message', f'Status updated from {old_status} to {data.get("status")}')
    )
    
    db.session.add(tracking)
    db.session.commit()
    
    return jsonify({'message': 'Status updated successfully'}), 200


@app.route('/api/admin/update-complaint/<int:complaint_id>', methods=['POST'])
@admin_required
def update_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    data = request.get_json()
    
    old_status = complaint.status
    new_status = data.get('status', complaint.status)
    complaint.status = new_status
    complaint.police_notes = data.get('police_notes', complaint.police_notes)
    
    if old_status != new_status:
        tracking = TrackingUpdate(
            complaint_id=complaint_id,
            status=new_status,
            message=f'Status updated from {old_status} to {new_status}'
        )
        db.session.add(tracking)
    
    db.session.commit()
    
    return jsonify({'message': 'Complaint updated successfully'}), 200


# ============ MODULE 7: NOTIFICATION MODULE ============

def send_email_notification(user, subject, message):
    """Send email notification to user"""
    try:
        sender_email = os.getenv('EMAIL_ADDRESS', 'noreply@crimeportal.com')
        sender_password = os.getenv('EMAIL_PASSWORD', '')
        
        if not sender_password:
            return False
        
        email_message = MIMEMultipart()
        email_message['From'] = sender_email
        email_message['To'] = user.email
        email_message['Subject'] = subject
        
        body = f"""
        Dear {user.name},
        
        {message}
        
        Best regards,
        Crime Report Portal
        """
        
        email_message.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(email_message)
        
        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        return False


@app.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    user_id = session['user_id']
    unread_only = request.args.get('unread', False, type=bool)
    
    query = Notification.query.filter_by(user_id=user_id)
    if unread_only:
        query = query.filter_by(is_read=False)
    
    notifications = query.order_by(Notification.created_at.desc()).limit(20).all()
    
    return jsonify([n.to_dict() for n in notifications]), 200


@app.route('/api/notification/<int:notification_id>/read', methods=['PUT'])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'message': 'Notification marked as read'}), 200


@app.route('/notifications', methods=['GET'])
@login_required
def notifications_page():
    return render_template('notifications.html')


@app.route('/api/user/profile', methods=['GET'])
@login_required
def get_user_profile():
    user = User.query.get(session['user_id'])
    return jsonify(user.to_dict()), 200


# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500


# ============ DATABASE INITIALIZATION ============

def init_db():
    with app.app_context():
        db.create_all()
        
        # Create default admin if not exists
        if not User.query.filter_by(role='admin').first():
            admin = User(
                name='System Admin',
                email='admin@crimeportal.com',
                phone='9999999999',
                role='admin',
                is_verified=True
            )
            admin.set_password('admin@123')
            db.session.add(admin)
            db.session.commit()
            print("Database initialized with default admin user")


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
