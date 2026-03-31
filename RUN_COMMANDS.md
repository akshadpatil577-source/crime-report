# RUN_COMMANDS.md

## 🚀 Quick Start (Windows - PowerShell) ✅
1. Create/activate virtual environment
```powershell
python -m venv .venv
& ".venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip
```
2. Install dependencies
```powershell
pip install -r requirements.txt
```
3. (Optional) Create or edit `.env` for configuration
- Add email settings, secret keys, etc. (project includes `.env`)

4. Run the app
```powershell
python app.py
# Open http://localhost:5000
```

---

## 🖥️ Quick Start (Windows - CMD)
```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## 🐧 Quick Start (macOS / Linux / Git Bash)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

---

## 🔧 Useful Commands
- Reset the database (removes DB file & recreates):
```bash
python -c "import os; os.remove('crime_portal.db'); from app import init_db; init_db()"
```
- View SQLite DB (if sqlite3 installed):
```bash
sqlite3 crime_portal.db
```
- Run Flask CLI (if preferred):
```bash
# Linux/macOS
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --port=5000
# Windows (PowerShell)
$env:FLASK_APP='app.py'
$env:FLASK_ENV='development'
flask run --port=5000
```
- Run on a different port (example 8000):
```bash
flask run --port=8000
# or adjust your app run command if app.py accepts args
```

---

## 🛡️ Production Server Examples
- Recommended: use a production WSGI server (Linux):
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```
- Windows-friendly option: Waitress
```bash
pip install waitress
waitress-serve --listen=*:8000 app:app
```

---

## ⚠️ Troubleshooting & Tips
- If PowerShell blocks activation: run as admin or set execution policy (use with caution)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
- If port 5000 is in use (Windows):
```powershell
netstat -ano | findstr :5000
# then kill the PID if needed: taskkill /PID <pid> /F
```
- If dependency errors occur, ensure you activated the correct virtualenv and rerun:
```bash
pip install -r requirements.txt
```
- Remove uploaded test files:
```powershell
Remove-Item -Recurse -Force uploads\*
```

---

## 📌 Notes
- The project auto-creates a default admin user on first run (see docs).
- Check `QUICKSTART.md`, `README.md`, and `START_HERE.md` for more details or troubleshooting steps.

---

Created for: Crime Report Portal — d:\Crime Report
