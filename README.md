# Crime Report Portal - Complete Project Documentation

## Project Overview

A comprehensive web-based crime reporting system that allows citizens to file complaints, track their status in real-time, and enables police/admin officials to manage and verify reports.

## Technology Stack

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Responsive styling with CSS variables
- **JavaScript (Vanilla)** - Client-side interactions without external libraries

### Backend
- **Python 3.8+** - Programming language
- **Flask** - Web framework
- **SQLAlchemy** - ORM for database operations
- **SQLite** - Lightweight relational database
- **Jinja2** - Template engine for HTML rendering

## Seven Core Modules

### 1. User Registration and Login (Module 1)
**Features:**
- Secure user registration with password hashing
- Email-based login system
- Role-based access (User/Admin)
- Session management
- Password verification

**Endpoints:**
- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout
- `GET /api/user/profile` - Get user profile

**Database Tables:**
- `users` - Stores user information with hashed passwords

---

### 2. Crime Report Submission (Module 2)
**Features:**
- Submit detailed crime reports with:
  - Crime category selection
  - Detailed description
  - Incident date and time
  - Exact location (with optional GPS coordinates)
  - Priority level setting
- Real-time form validation
- Location auto-detection using Geolocation API

**Endpoints:**
- `GET /report` - Report submission form
- `POST /api/complaint/submit` - Submit new complaint

**Database Tables:**
- `complaints` - Stores crime report details

**Supported Crime Categories:**
- Theft
- Assault
- Fraud
- Cyber Crime
- Property Damage
- Harassment
- Other

---

### 3. Admin Login and Dashboard (Module 3)
**Features:**
- Dedicated admin login portal
- Comprehensive dashboard with:
  - Total complaints count
  - Status-wise breakdown (Submitted, In Review, Verified, Rejected)
  - Statistics visualization
- Role-based protection (only admins can access)

**Endpoints:**
- `GET /admin/dashboard` - Admin dashboard page
- `GET /api/admin/complaints` - Get all complaints (paginated)

**Admin Capabilities:**
- View all complaints in the system
- Filter by status and priority
- Search functionality
- Pagination support

---

### 4. Report Tracking Module (Module 4)
**Features:**
- Real-time status tracking for users
- Timeline view of complaint updates
- Status progression (Submitted → In Review → Verified/Rejected → Closed)
- Complaint details viewing
- Historical tracking updates

**Endpoints:**
- `GET /tracking` - User tracking page
- `GET /api/complaint/<id>/tracking` - Get tracking updates

**Tracking Statuses:**
- Submitted - Initial submission
- In Review - Being reviewed by authorities
- Verified - Complaint verified as legitimate
- Rejected - Complaint rejected with reason
- Closed - Case closed

---

### 5. File Upload Module (Module 5)
**Features:**
- Upload multiple evidence files
- Support for various file types (images, documents)
- File size validation (max 16MB)
- Secure file storage
- File metadata tracking

**Supported File Types:**
- Images: JPG, PNG, GIF
- Documents: PDF, DOC, DOCX

**Endpoints:**
- `POST /api/complaint/<id>/upload` - Upload evidence file

**Database Tables:**
- `evidence_files` - Stores file metadata and references

---

### 6. Complaint Management System (Module 6)
**Features:**
- Admin-only complaint management
- Verify legitimate complaints
- Reject invalid complaints with reasons
- Update complaint status and priority
- Add management notes
- Automatic status tracking

**Admin Actions:**
- **Verify** - Mark complaint as verified
- **Reject** - Reject with detailed reason
- **Update Status** - Change status and priority
- **Add Notes** - Internal management notes

**Endpoints:**
- `POST /api/admin/complaint/<id>/verify` - Verify complaint
- `POST /api/admin/complaint/<id>/reject` - Reject complaint
- `POST /api/admin/complaint/<id>/update-status` - Update status

**Database Tables:**
- `management_notes` - Admin actions and notes
- `tracking_updates` - Auto-generated status updates

---

### 7. Notification Module (Module 7)
**Features:**
- Multi-channel notifications (Portal & Email)
- Automatic notification generation on key events
- Mark as read functionality
- Notification filtering by type
- Email integration for important updates

**Notification Types:**
- Status Updates - When complaint status changes
- Verification - When complaint is verified
- Rejection - When complaint is rejected
- General - System messages

**Endpoints:**
- `GET /api/notifications` - Get user notifications
- `PUT /api/notification/<id>/read` - Mark as read
- `GET /notifications` - Notifications page

**Email Features:**
- Automated email on verification
- Rejection reason in email
- Status change notifications
- Configurable via .env file

**Database Tables:**
- `notifications` - Stores all notifications

---

## Project Structure

```
crime-report/
├── app.py                      # Main Flask application with all modules
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration
├── DATABASE_SCHEMA.txt         # Database schema documentation
├── README.md                   # This file
├── templates/
│   ├── base.html              # Base template with navigation
│   ├── index.html             # Home page
│   ├── register.html          # User registration page
│   ├── login.html             # User login page
│   ├── submit_report.html     # Crime report submission form
│   ├── tracking.html          # Report tracking page
│   ├── admin_dashboard.html   # Admin dashboard
│   └── notifications.html     # Notifications page
├── static/
│   ├── styles.css             # CSS styling
│   └── app.js                 # Frontend JavaScript
├── uploads/                   # Evidence file storage (auto-created)
└── crime_portal.db            # SQLite database (auto-created)
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Web browser (Chrome, Firefox, Safari, Edge)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment
Edit `.env` file with your settings:
```
SECRET_KEY=your-secure-key
FLASK_ENV=development
FLASK_DEBUG=True
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

### Step 3: Initialize Database
```bash
python
>>> from app import init_db
>>> init_db()
>>> exit()
```

### Step 4: Run Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Default Login Credentials

**Regular User:**
- Email: user@example.com
- Password: user123

**Admin User:**
- Email: admin@crimeportal.com
- Password: admin@123

## API Documentation

### Authentication
All protected endpoints require user to be logged in. Session is managed via Flask sessions.

### Response Format
All API responses are JSON:
```json
{
  "message": "Success message",
  "data": { /* response data */ }
}
```

### Error Handling
```json
{
  "error": "Error message",
  "status": 400
}
```

## Security Features

1. **Password Security**
   - Passwords hashed using Werkzeug's security module
   - PBKDF2 hashing algorithm

2. **Session Management**
   - Secure session cookies
   - Session expiration support
   - CSRF protection ready

3. **File Upload Security**
   - File type validation
   - File size limits
   - Secure filename sanitization

4. **Database Security**
   - SQL injection prevention via SQLAlchemy ORM
   - Input validation on all forms

## Database Models

### User Model
- Stores user registration and authentication data
- Maintains login history
- Role-based access control

### Complaint Model
- Core crime report data
- Linked to user and tracking updates
- Supports multiple evidence files

### Evidence File Model
- Tracks uploaded evidence
- File metadata storage
- Associated with complaints

### Tracking Update Model
- Maintains complaint status history
- Automatic timeline creation
- User-visible status changes

### Management Note Model
- Admin-only notes and actions
- Tracks verification/rejection decisions
- Audit trail for complaints

### Notification Model
- Multi-channel notification system
- Read/unread status tracking
- Type categorization

## Usage Examples

### File a Crime Report
1. Register or login
2. Click "Report Crime"
3. Fill in crime details
4. Optionally upload evidence
5. Submit report
6. Receive complaint ID for tracking

### Track a Report
1. Login to your account
2. Go to "Track Report"
3. View all your complaints
4. Click "View Details" for timeline
5. Check for status updates

### Admin Dashboard (Admin Only)
1. Login with admin credentials
2. View dashboard statistics
3. Filter complaints by status
4. Verify legitimate complaints
5. Reject invalid complaints
6. Add management notes

## Customization

### Adding Crime Categories
Edit the category dropdown in `templates/submit_report.html`:
```html
<option value="New Category">New Category</option>
```

### Email Configuration
Set up Gmail App Password:
1. Enable 2FA on Gmail account
2. Generate app-specific password
3. Add to `.env` file:
```
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

### Theme Customization
Edit CSS variables in `static/styles.css`:
```css
:root {
    --primary: #0066cc;
    --success: #059669;
    --error: #dc2626;
    /* ... more colors */
}
```

## Testing

### Test User Registration
```bash
POST http://localhost:5000/register
Content-Type: application/json

{
  "name": "Test User",
  "email": "test@example.com",
  "phone": "9876543210",
  "password": "TestPass123"
}
```

### Test Crime Report Submission
```bash
POST http://localhost:5000/api/complaint/submit
(Requires login and multipart/form-data)
```

### Test Admin Verification
```bash
POST http://localhost:5000/api/admin/complaint/1/verify
Content-Type: application/json
(Requires admin role)

{
  "note": "Verified legitimate complaint"
}
```

## Troubleshooting

### Database Issues
If you encounter database errors:
```bash
rm crime_portal.db
python -c "from app import init_db; init_db()"
```

### Port Already in Use
Change port in `app.py`:
```python
app.run(debug=True, port=5001)
```

### Email Not Sending
- Verify .env file has correct credentials
- Enable "Less secure apps" in Gmail settings
- Use app-specific password for 2FA accounts

## Performance Considerations

1. **Database Indexing** - Add indexes on frequently queried fields
2. **Pagination** - Complaints list is paginated (10 per page)
3. **File Upload** - Max size limited to 16MB
4. **Caching** - Implement browser caching for static files

## Future Enhancements

1. Advanced analytics and reporting
2. Map integration for location visualization
3. Mobile app development
4. SMS notifications
5. Video evidence streaming
6. AI-powered complaint classification
7. Case assignment to specific officers
8. Complaints export (PDF/Excel)
9. Multi-language support
10. Blockchain for evidence integrity

## License

This project is for educational and government use.

## Support

For issues or questions, contact the development team.

## Version History

- **v1.0.0** (2026-01-30) - Initial release with all 7 modules
