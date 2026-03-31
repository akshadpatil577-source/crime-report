"""
Crime Report Portal - Flask Backend
Simplified Version with JSON Storage (No SQLAlchemy ORM to avoid Python 3.13 issues)
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
DATA_FILE = 'data.json'

# ============ DATA MANAGEMENT ============

def get_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {'users': [], 'complaints': [], 'notifications': []}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

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
        data = get_data()
        user = next((u for u in data['users'] if u['id'] == session['user_id']), None)
        if not user or user['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# ============ ROUTES ============

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data_dict = request.get_json()
        data = get_data()
        
        if any(u['email'] == data_dict.get('email') for u in data['users']):
            return jsonify({'error': 'Email already registered'}), 400
        
        user_id = max([u['id'] for u in data['users']], default=0) + 1
        user = {
            'id': user_id,
            'name': data_dict.get('name'),
            'email': data_dict.get('email'),
            'password_hash': generate_password_hash(data_dict.get('password')),
            'phone': data_dict.get('phone'),
            'role': 'user',
            'created_at': datetime.now().isoformat()
        }
        
        data['users'].append(user)
        save_data(data)
        
        return jsonify({'message': 'Registration successful', 'user_id': user_id}), 201
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data_dict = request.get_json()
        data = get_data()
        
        user = next((u for u in data['users'] if u['email'] == data_dict.get('email')), None)
        
        if user and check_password_hash(user['password_hash'], data_dict.get('password')):
            session['user_id'] = user['id']
            session['user_role'] = user['role']
            return jsonify({'message': 'Login successful', 'role': user['role']}), 200
        
        return jsonify({'error': 'Invalid email or password'}), 401
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/report', methods=['GET'])
@login_required
def submit_report_page():
    return render_template('submit_report.html')

@app.route('/api/complaint/submit', methods=['POST'])
@login_required
def submit_complaint():
    user_id = session['user_id']
    data_dict = get_data()
    
    complaint_id = max([c.get('id', 0) for c in data_dict['complaints']], default=0) + 1
    
    complaint = {
        'id': complaint_id,
        'user_id': user_id,
        'category': request.form.get('category'),
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'location': request.form.get('location'),
        'latitude': request.form.get('latitude'),
        'longitude': request.form.get('longitude'),
        'incident_date': request.form.get('incident_date'),
        'status': 'Submitted',
        'priority': request.form.get('priority', 'Medium'),
        'created_at': datetime.now().isoformat(),
        'evidence_files': [],
        'tracking_updates': [
            {
                'status': 'Submitted',
                'message': 'Your complaint has been received successfully.',
                'created_at': datetime.now().isoformat()
            }
        ]
    }
    
    # Handle file uploads
    if 'evidence_files' in request.files:
        files = request.files.getlist('evidence_files')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(filepath)
                
                complaint['evidence_files'].append({
                    'filename': filename,
                    'file_type': filename.rsplit('.', 1)[1].lower(),
                    'uploaded_at': datetime.now().isoformat()
                })
    
    data_dict['complaints'].append(complaint)
    
    # Create notification
    notification_id = max([n.get('id', 0) for n in data_dict['notifications']], default=0) + 1
    data_dict['notifications'].append({
        'id': notification_id,
        'user_id': user_id,
        'complaint_id': complaint_id,
        'title': 'Crime Report Submitted',
        'message': 'Your crime report has been submitted successfully.',
        'type': 'status_update',
        'is_read': False,
        'created_at': datetime.now().isoformat()
    })
    
    save_data(data_dict)
    
    return jsonify({'message': 'Complaint submitted successfully', 'complaint_id': complaint_id}), 201

@app.route('/tracking', methods=['GET'])
@login_required
def tracking_page():
    data = get_data()
    user_id = session['user_id']
    user_complaints = [c for c in data['complaints'] if c['user_id'] == user_id]
    return render_template('tracking.html', complaints=user_complaints)

@app.route('/api/complaint/<int:complaint_id>/tracking', methods=['GET'])
@login_required
def get_tracking_updates(complaint_id):
    data = get_data()
    complaint = next((c for c in data['complaints'] if c['id'] == complaint_id), None)
    
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404
    
    if complaint['user_id'] != session['user_id'] and session.get('user_role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'status': complaint['status'],
        'priority': complaint['priority'],
        'updates': complaint.get('tracking_updates', [])
    }), 200

@app.route('/admin/dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    data = get_data()
    total = len(data['complaints'])
    submitted = sum(1 for c in data['complaints'] if c['status'] == 'Submitted')
    in_review = sum(1 for c in data['complaints'] if c['status'] == 'In Review')
    verified = sum(1 for c in data['complaints'] if c['status'] == 'Verified')
    
    return render_template('admin_dashboard.html',
                         total=total,
                         submitted=submitted,
                         in_review=in_review,
                         verified=verified)

@app.route('/api/admin/complaints', methods=['GET'])
@admin_required
def get_all_complaints():
    data = get_data()
    status_filter = request.args.get('status')
    
    complaints = data['complaints']
    if status_filter:
        complaints = [c for c in complaints if c['status'] == status_filter]
    
    return jsonify({
        'complaints': complaints,
        'total': len(complaints),
        'pages': 1
    }), 200

@app.route('/notifications', methods=['GET'])
@login_required
def notifications_page():
    return render_template('notifications.html')

@app.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    data = get_data()
    user_id = session['user_id']
    notifications = [n for n in data['notifications'] if n['user_id'] == user_id]
    
    return jsonify(sorted(notifications, key=lambda x: x['created_at'], reverse=True)), 200

@app.route('/api/notification/<int:notification_id>/read', methods=['PUT'])
@login_required
def mark_notification_read(notification_id):
    data = get_data()
    notification = next((n for n in data['notifications'] if n['id'] == notification_id), None)
    
    if not notification:
        return jsonify({'error': 'Not found'}), 404
    
    if notification['user_id'] != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    notification['is_read'] = True
    save_data(data)
    
    return jsonify({'message': 'Marked as read'}), 200

@app.route('/api/admin/complaint/<int:complaint_id>/verify', methods=['POST'])
@admin_required
def verify_complaint(complaint_id):
    data = get_data()
    complaint = next((c for c in data['complaints'] if c['id'] == complaint_id), None)
    
    if not complaint:
        return jsonify({'error': 'Not found'}), 404
    
    complaint['status'] = 'Verified'
    complaint['tracking_updates'].append({
        'status': 'Verified',
        'message': 'Your complaint has been verified by authorities.',
        'created_at': datetime.now().isoformat()
    })
    
    # Add notification
    notif_id = max([n.get('id', 0) for n in data['notifications']], default=0) + 1
    data['notifications'].append({
        'id': notif_id,
        'user_id': complaint['user_id'],
        'complaint_id': complaint_id,
        'title': 'Report Verified',
        'message': 'Your crime report has been verified.',
        'type': 'verification',
        'is_read': False,
        'created_at': datetime.now().isoformat()
    })
    
    save_data(data)
    return jsonify({'message': 'Verified'}), 200

@app.route('/api/admin/complaint/<int:complaint_id>/reject', methods=['POST'])
@admin_required
def reject_complaint(complaint_id):
    data = get_data()
    complaint = next((c for c in data['complaints'] if c['id'] == complaint_id), None)
    
    if not complaint:
        return jsonify({'error': 'Not found'}), 404
    
    req_data = request.get_json()
    reason = req_data.get('reason', 'Your complaint has been rejected.')
    
    complaint['status'] = 'Rejected'
    complaint['tracking_updates'].append({
        'status': 'Rejected',
        'message': reason,
        'created_at': datetime.now().isoformat()
    })
    
    # Add notification
    notif_id = max([n.get('id', 0) for n in data['notifications']], default=0) + 1
    data['notifications'].append({
        'id': notif_id,
        'user_id': complaint['user_id'],
        'complaint_id': complaint_id,
        'title': 'Report Rejected',
        'message': f'Your crime report has been rejected. Reason: {reason}',
        'type': 'rejection',
        'is_read': False,
        'created_at': datetime.now().isoformat()
    })
    
    save_data(data)
    return jsonify({'message': 'Rejected'}), 200

@app.route('/api/admin/update-complaint/<int:complaint_id>', methods=['POST'])
@admin_required
def update_complaint(complaint_id):
    data = get_data()
    complaint = next((c for c in data['complaints'] if c['id'] == complaint_id), None)
    
    if not complaint:
        return jsonify({'error': 'Not found'}), 404
    
    req_data = request.get_json()
    new_status = req_data.get('status', complaint['status'])
    police_notes = req_data.get('police_notes', '')
    
    # Update status if changed
    if new_status != complaint['status']:
        complaint['status'] = new_status
        complaint['tracking_updates'].append({
            'status': new_status,
            'message': f'Status updated to {new_status}',
            'created_at': datetime.now().isoformat()
        })
        
        # Add notification
        notif_id = max([n.get('id', 0) for n in data['notifications']], default=0) + 1
        data['notifications'].append({
            'id': notif_id,
            'user_id': complaint['user_id'],
            'complaint_id': complaint_id,
            'title': f'Report Status Updated',
            'message': f'Your report status has been updated to: {new_status}',
            'type': 'status_update',
            'is_read': False,
            'created_at': datetime.now().isoformat()
        })
    
    # Update police notes
    complaint['police_notes'] = police_notes
    
    save_data(data)
    return jsonify({'message': 'Complaint updated successfully'}), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

def init_data():
    """Initialize default data"""
    if not os.path.exists(DATA_FILE):
        data = {
            'users': [
                {
                    'id': 1,
                    'name': 'Regular User',
                    'email': 'user@example.com',
                    'password_hash': generate_password_hash('user123'),
                    'phone': '9876543210',
                    'role': 'user',
                    'created_at': datetime.now().isoformat()
                },
                {
                    'id': 2,
                    'name': 'System Admin',
                    'email': 'admin@crimeportal.com',
                    'password_hash': generate_password_hash('admin@123'),
                    'phone': '9999999999',
                    'role': 'admin',
                    'created_at': datetime.now().isoformat()
                }
            ],
            'complaints': [],
            'notifications': []
        }
        save_data(data)

if __name__ == '__main__':
    init_data()
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    print("\n" + "="*60)
    print("🚔 CRIME REPORT PORTAL RUNNING")
    print("="*60)
    print("\n📱 Access the application at: http://localhost:5000")
    print("\n👤 Demo Credentials:")
    print("   User: user@example.com / user123")
    print("   Admin: admin@crimeportal.com / admin@123")
    print("\n" + "="*60 + "\n")
    app.run(debug=True, port=5000, use_reloader=False)
