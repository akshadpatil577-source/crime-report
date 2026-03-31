# Crime Report Portal - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.8+
- pip installed
- Modern web browser

### Step 1: Install Dependencies (1 min)
```bash
cd "d:\Crime Report"
pip install -r requirements.txt
```

### Step 2: Start the Application (30 seconds)
```bash
python app.py
```

You should see:
```
* Running on http://127.0.0.1:5000
* Debug mode: on
```

### Step 3: Open in Browser (10 seconds)
Visit: `http://localhost:5000`

### Step 4: Login with Demo Account (1 min)

**Option A: Regular User**
- Email: user@example.com
- Password: user123
- Can: File reports, track status, view notifications

**Option B: Admin User**
- Email: admin@crimeportal.com
- Password: admin@123
- Can: View dashboard, verify/reject reports, manage complaints

---

## 📋 Quick Feature Demo

### As Regular User:

1. **File a Crime Report**
   - Click "Report Crime"
   - Fill in crime details
   - Upload evidence (optional)
   - Click "Submit Report"
   - Note your Complaint ID

2. **Track Your Report**
   - Click "Track Report"
   - See your complaint with status
   - Click "View Details & Updates"
   - Check timeline of updates

3. **View Notifications**
   - Click "Notifications"
   - See status updates
   - Mark as read when viewed

### As Admin User:

1. **View Dashboard**
   - See statistics overview
   - Check complaint breakdown
   - Review latest submissions

2. **Manage Complaints**
   - Filter by status
   - Search complaints
   - Click "View" to see details
   - Click "Verify" to verify
   - Click "Reject" to reject with reason

3. **Track Admin Actions**
   - See all complaints
   - Note status changes
   - Review management notes

---

## 📁 Project Structure

```
d:\Crime Report\
├── app.py                    ← Main application (start here)
├── requirements.txt          ← Dependencies
├── .env                      ← Configuration
├── README.md                 ← Full documentation
├── MODULES_GUIDE.md         ← Module details
├── DATABASE_SCHEMA.txt      ← Database info
├── templates/               ← HTML pages
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── submit_report.html
│   ├── tracking.html
│   ├── admin_dashboard.html
│   └── notifications.html
├── static/
│   ├── styles.css           ← CSS styling
│   └── app.js               ← Frontend JS
├── uploads/                 ← Evidence files
└── crime_portal.db          ← SQLite database
```

---

## 🔧 Common Tasks

### Change Port
Edit `app.py`, last line:
```python
app.run(debug=True, port=5001)  # Change 5000 to 5001
```

### Reset Database
```bash
python
>>> import os
>>> os.remove('crime_portal.db')
>>> from app import init_db
>>> init_db()
>>> exit()
```

### Enable Email Notifications
Edit `.env`:
```
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

### Add Crime Category
Edit `templates/submit_report.html`, find this section:
```html
<select id="category" name="category" required>
    <option value="">Select Category</option>
    <option value="Theft">Theft</option>
    <!-- Add here -->
    <option value="Your New Category">Your New Category</option>
</select>
```

---

## 🐛 Troubleshooting

### Error: "Port 5000 already in use"
```bash
# Find what's using port 5000
netstat -ano | findstr :5000

# Kill that process (replace PID)
taskkill /PID <PID> /F

# Or just use different port (see "Change Port" above)
```

### Error: "No module named 'flask'"
```bash
pip install -r requirements.txt
```

### Error: "Database is locked"
```bash
# Delete the database and reinitialize
python -c "import os; os.remove('crime_portal.db'); from app import init_db; init_db()"
```

### Files not uploading
- Check file size (max 16MB)
- Check file type (.pdf, .jpg, .png, .gif, .doc, .docx only)
- Check `uploads/` folder exists and is writable

---

## 📊 Database Tables

The system automatically creates these tables on first run:

| Table | Purpose |
|-------|---------|
| users | User accounts and authentication |
| complaints | Crime reports |
| evidence_files | Uploaded evidence |
| tracking_updates | Status history timeline |
| management_notes | Admin notes and actions |
| notifications | User notifications |

View database:
```bash
# Using SQLite
sqlite3 crime_portal.db

# List all tables
sqlite> .tables

# View users
sqlite> SELECT * FROM users;

# Exit
sqlite> .exit
```

---

## 🔐 Security Notes

1. **Change SECRET_KEY in .env** for production
2. **Never commit .env with real passwords**
3. **Use app-specific passwords for Gmail**
4. **Enable HTTPS in production**
5. **Implement rate limiting in production**
6. **Regular database backups**

---

## 📱 Responsive Design

The application works on:
- Desktop (Chrome, Firefox, Safari, Edge)
- Tablet (iOS Safari, Android Chrome)
- Mobile (iOS Safari, Android Chrome)

---

## 📞 Support

### Check Logs
```bash
# Terminal will show debug info
# Look for errors in the output
```

### Test Endpoints
```bash
# PowerShell
$uri = "http://localhost:5000/api/user/profile"
Invoke-WebRequest -Uri $uri -Method Get
```

### Reset Everything
```bash
# Stop the app (Ctrl+C)
# Delete database
del crime_portal.db

# Delete uploads
rmdir uploads /s

# Restart
python app.py
```

---

## ✨ Features Overview

| Feature | User | Admin |
|---------|------|-------|
| Register/Login | ✅ | ✅ |
| File Crime Report | ✅ | - |
| Upload Evidence | ✅ | - |
| Track Status | ✅ | - |
| View Dashboard | - | ✅ |
| Verify Reports | - | ✅ |
| Reject Reports | - | ✅ |
| View Notifications | ✅ | ✅ |
| Manage Notes | - | ✅ |

---

## 🎓 Learning Resources

- Check `MODULES_GUIDE.md` for implementation details
- Read `README.md` for full documentation
- View `DATABASE_SCHEMA.txt` for data structure
- Examine `app.py` for backend code
- Check `templates/` for frontend code

---

## 📈 Next Steps

1. **Understand the modules** - Read MODULES_GUIDE.md
2. **Customize the design** - Edit static/styles.css
3. **Add features** - Extend app.py and templates
4. **Deploy** - Use Flask with production server
5. **Scale** - Switch to PostgreSQL and add caching

---

## 🎉 You're All Set!

Your Crime Report Portal is ready to use!

- Visit: http://localhost:5000
- Login as admin to manage
- Register to file reports
- Track status in real-time

Happy reporting! 🚔
