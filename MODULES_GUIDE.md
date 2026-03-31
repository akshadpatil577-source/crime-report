# Crime Report Portal - Modules Implementation Guide

## Module 1: User Registration and Login ✅

### Location: `app.py` (lines 155-195)

### Implementation Details:

**Routes:**
- `GET/POST /register` - Registration endpoint
- `GET/POST /login` - Login endpoint
- `GET /logout` - Logout endpoint
- `GET /api/user/profile` - User profile retrieval

**Database Operations:**
- Creates new User records with hashed passwords
- Validates existing emails
- Manages session data
- Tracks last login

**Security:**
- Password hashing using `werkzeug.security.generate_password_hash`
- Password verification using `check_password_hash`
- Session-based authentication
- Login required decorator for protected routes

**Frontend:**
- Registration form (`templates/register.html`)
- Login form (`templates/login.html`)
- Form validation and error handling
- Redirect based on user role

---

## Module 2: Crime Report Submission ✅

### Location: `app.py` (lines 197-280)

### Implementation Details:

**Routes:**
- `GET /report` - Report submission page
- `POST /api/complaint/submit` - Submit new complaint

**Form Fields:**
- Category (dropdown: Theft, Assault, Fraud, Cyber Crime, etc.)
- Title (brief summary)
- Description (detailed narrative)
- Location (textual description)
- Latitude/Longitude (optional GPS coordinates)
- Incident Date & Time
- Priority Level (Low, Medium, High, Critical)
- Evidence Files (optional multi-file upload)

**Backend Processing:**
1. Validates user is logged in
2. Creates Complaint record
3. Processes file uploads
4. Creates initial tracking update
5. Generates notification
6. Returns complaint ID

**File Upload:**
- Validates file types (pdf, png, jpg, jpeg, gif, doc, docx)
- Enforces file size limit (16MB)
- Sanitizes filenames
- Stores in `uploads/` directory
- Creates EvidenceFile records

**Database Operations:**
- Creates Complaint record
- Creates EvidenceFile records for attachments
- Creates initial TrackingUpdate
- Creates Notification record

**Frontend Features:**
- Dropdown selections for category and priority
- Textarea for detailed description
- Multi-file upload with progress
- Geolocation detection button
- Form validation before submission
- Success confirmation with complaint ID

---

## Module 3: Admin Login and Dashboard ✅

### Location: `app.py` (lines 282-314)

### Implementation Details:

**Routes:**
- `GET /admin/dashboard` - Dashboard page
- `GET /api/admin/complaints` - Get complaints (paginated)

**Dashboard Features:**
- Total complaints count
- Status-wise breakdown:
  - Submitted count
  - In Review count
  - Verified count
  - Rejected count (derived)
- Pagination support (10 complaints per page)
- Filter by status
- Search functionality

**Database Queries:**
```python
Complaint.query.count()  # Total
Complaint.query.filter_by(status='Submitted').count()
Complaint.query.filter_by(status='In Review').count()
Complaint.query.filter_by(status='Verified').count()
```

**Access Control:**
- `@admin_required` decorator enforces admin-only access
- Role validation on every protected route
- Unauthorized access returns 403 error

**Frontend:**
- Statistics cards showing counts
- Filter controls (status, priority, search)
- Complaints table with:
  - Complaint ID
  - Category
  - Title
  - Location
  - Status badge
  - Priority indicator
  - Submission date
  - Action buttons

**Admin Actions:**
- View complaint details
- Verify/Reject complaints
- Update status and priority

---

## Module 4: Report Tracking Module ✅

### Location: `app.py` (lines 316-354)

### Implementation Details:

**Routes:**
- `GET /tracking` - User tracking page
- `GET /api/complaint/<id>/tracking` - Get tracking updates

**Tracking Data:**
- Current complaint status
- Priority level
- Chronological updates
- Timestamps for each update

**Status Progression:**
```
Submitted → In Review → [Verified OR Rejected] → Closed
```

**Database Operations:**
- Fetches Complaint record
- Retrieves all TrackingUpdate records
- Validates user authorization
- Filters by user ownership or admin role

**Frontend Features:**
- Complaint listing with quick status view
- Detail modal showing:
  - Complete complaint information
  - Timeline of updates
  - Evidence files
  - Status badges
  - Priority indicators
- Real-time status display
- Timestamp for each update
- Color-coded status indicators

**Tracking Information:**
- Each update includes:
  - Status name
  - Message/description
  - Timestamp
  - Automatic generation on status changes

---

## Module 5: File Upload Module ✅

### Location: `app.py` (lines 356-391)

### Implementation Details:

**Routes:**
- `POST /api/complaint/<id>/upload` - Upload evidence file

**File Handling:**
- Multi-file upload support
- File type validation (whitelist approach)
- File size enforcement (16MB max)
- Secure filename generation using `secure_filename()`
- Directory creation if needed

**Allowed File Types:**
- Images: .pdf, .png, .jpg, .jpeg, .gif
- Documents: .doc, .docx

**Backend Process:**
1. Validate user ownership of complaint
2. Check file provided
3. Validate file extension
4. Create secure filename
5. Save to `uploads/` directory
6. Create EvidenceFile record
7. Return file metadata

**Database Model:**
```python
EvidenceFile:
  - id
  - complaint_id (FK)
  - filename (original)
  - file_path (storage path)
  - file_type (extension)
  - file_size (bytes)
  - uploaded_at (timestamp)
```

**Security:**
- Filename sanitization prevents path traversal
- File type validation prevents executable upload
- Size limit prevents disk exhaustion
- Ownership verification prevents unauthorized access
- Files stored outside web root in `uploads/`

**Frontend:**
- File input with multiple selection
- File preview list with sizes
- Progress indication
- Error handling for large files
- Success confirmation

---

## Module 6: Complaint Management System ✅

### Location: `app.py` (lines 393-476)

### Implementation Details:

**Routes:**
- `POST /api/admin/complaint/<id>/verify` - Verify complaint
- `POST /api/admin/complaint/<id>/reject` - Reject complaint
- `POST /api/admin/complaint/<id>/update-status` - Update status

**Admin Actions:**

### Verify Action:
```python
POST /api/admin/complaint/1/verify
{
  "note": "Verification details"
}
```

**Process:**
1. Update complaint status to "Verified"
2. Create ManagementNote with verification details
3. Create TrackingUpdate for user visibility
4. Send notification to complainant
5. Send verification email

### Reject Action:
```python
POST /api/admin/complaint/1/reject
{
  "reason": "Detailed rejection reason"
}
```

**Process:**
1. Update complaint status to "Rejected"
2. Create ManagementNote with rejection reason
3. Create TrackingUpdate with reason message
4. Send notification with reason
5. Send rejection email with explanation

### Update Status Action:
```python
POST /api/admin/complaint/1/update-status
{
  "status": "In Review",
  "priority": "High",
  "message": "Status update message"
}
```

**Database Operations:**
- Updates Complaint status and priority
- Creates ManagementNote for audit trail
- Creates TrackingUpdate for user notification
- Generates Notification record
- Triggers email notification

**Management Notes:**
- Admin ID (who made the decision)
- Action type (verify, reject, assign, update)
- Detailed note/reason
- Timestamp

**Audit Trail:**
- Complete history of admin actions
- Timestamps for each action
- User accountability
- Decision documentation

---

## Module 7: Notification Module ✅

### Location: `app.py` (lines 478-549)

### Implementation Details:

**Routes:**
- `GET /api/notifications` - Get user notifications
- `PUT /api/notification/<id>/read` - Mark as read
- `GET /notifications` - Notifications page

**Notification Features:**

### Types:
- **status_update** - When complaint status changes
- **verification** - When complaint is verified
- **rejection** - When complaint is rejected
- **general** - System announcements

### Channels:
- **portal** - In-app notification
- **email** - Email notification
- **both** - Portal + Email

**Database Model:**
```python
Notification:
  - id
  - user_id (FK)
  - complaint_id (FK)
  - title
  - message
  - notification_type
  - is_read (boolean)
  - sent_via (portal/email/both)
  - created_at
```

### Email Notifications:
**Configuration** (via .env):
```
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

**Email Features:**
- Automated emails on key events
- Personalized greeting with user name
- Clear action description
- Complaint reference number
- Professional formatting

**SMTP Settings:**
- Server: smtp.gmail.com
- Port: 465 (SSL/TLS)
- Authentication: Email + App Password

**Notification Flow:**

1. **On Verification:**
   ```
   Title: "Report Verified"
   Message: "Your crime report has been verified."
   Type: verification
   Channel: both (portal + email)
   ```

2. **On Rejection:**
   ```
   Title: "Report Rejected"
   Message: "Your crime report has been rejected. Reason: [admin reason]"
   Type: rejection
   Channel: both (portal + email)
   ```

3. **On Status Update:**
   ```
   Title: "Status Update"
   Message: "Your report status changed to [new status]"
   Type: status_update
   Channel: both (portal + email)
   ```

**Frontend Features:**
- Notification list with newest first
- Unread badge indicator
- Mark as read functionality
- Mark all as read option
- Filter by notification type
- Timestamp display
- Notification detail view

**Notification Management:**
- Unread notification count
- Read/unread status tracking
- Pagination for large lists
- Archive/delete functionality

---

## API Authentication & Security

### Session Management:
```python
@login_required        # User must be logged in
@admin_required       # User must be admin
```

### Error Handling:
- 400: Bad Request (validation errors)
- 401: Unauthorized (invalid credentials)
- 403: Forbidden (insufficient permissions)
- 404: Not Found (resource doesn't exist)
- 500: Server Error

---

## Database Relationships

```
User (1) ──→ (M) Complaint
User (1) ──→ (M) Notification
User (1) ──→ (M) ManagementNote (as admin)

Complaint (1) ──→ (M) EvidenceFile
Complaint (1) ──→ (M) TrackingUpdate
Complaint (1) ──→ (M) ManagementNote
Complaint (1) ──→ (M) Notification
```

---

## Testing Module Integration

### Test Sequence:
1. Register new user
2. Login with credentials
3. Submit crime report with files
4. View report in tracking
5. Login as admin
6. View dashboard
7. Verify/reject complaints
8. Check notifications received
9. Upload additional evidence
10. Verify all updates appear

---

## Module Completeness Checklist

✅ Module 1: User Registration and Login
  - Secure registration
  - Login with hashed passwords
  - Role-based access
  - Session management

✅ Module 2: Crime Report Submission
  - Detailed form with all fields
  - Multiple file upload
  - Location detection
  - Status tracking initialization

✅ Module 3: Admin Login and Dashboard
  - Admin-only access
  - Statistics display
  - Complaint filtering
  - Status overview

✅ Module 4: Report Tracking
  - Real-time status updates
  - Timeline view
  - Status history
  - User-visible updates

✅ Module 5: File Upload
  - Multi-file support
  - Type validation
  - Size enforcement
  - Secure storage

✅ Module 6: Complaint Management
  - Verify functionality
  - Reject functionality
  - Status updates
  - Audit trail

✅ Module 7: Notification Module
  - Portal notifications
  - Email notifications
  - Multi-channel delivery
  - Read/unread tracking

All modules are fully implemented and integrated!
