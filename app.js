// ============ INITIALIZATION ============

let users = [];
let complaints = [];
let currentUser = null;
let isRegistering = false;

function initDemo() {
    users = [
        { 
            id: 1, 
            name: 'John Doe', 
            email: 'user@example.com', 
            password: 'user123', 
            phone: '9876543210', 
            role: 'user' 
        },
        { 
            id: 2, 
            name: 'Inspector Sharma', 
            email: 'admin@example.com', 
            password: 'admin123', 
            phone: '9999999999', 
            role: 'admin' 
        }
    ];
    
    complaints = [
        { 
            id: 1, 
            userId: 1, 
            category: 'Theft', 
            date: '2025-12-01', 
            time: '14:30', 
            location: 'Main Street Market', 
            description: 'Motorcycle stolen from parking lot near market', 
            status: 'Submitted', 
            evidence: 'motorcycle_photo.jpg', 
            createdAt: new Date().toISOString() 
        },
        { 
            id: 2, 
            userId: 1, 
            category: 'Cyber Crime', 
            date: '2025-11-28', 
            time: '10:15', 
            location: 'Online', 
            description: 'Fraudulent transaction detected on bank account', 
            status: 'In Review', 
            evidence: 'bank_statement.pdf', 
            createdAt: new Date().toISOString() 
        }
    ];
    
    localStorage.setItem('users', JSON.stringify(users));
    localStorage.setItem('complaints', JSON.stringify(complaints));
}

initDemo();

// ============ PAGE NAVIGATION ============

function showPage(page) {
    const pages = document.querySelectorAll('.page');
    pages.forEach(p => {
        p.style.animation = 'fadeInUp 0.3s ease';
        p.classList.add('hidden');
    });

    setTimeout(() => {
        const targetPage = document.getElementById(page + '-page');
        targetPage.classList.remove('hidden');
        targetPage.style.animation = 'fadeInUp 0.6s ease';

        if (page === 'auth') {
            isRegistering = false;
            toggleAuthMode();
        }

        if (page === 'dashboard' && currentUser) {
            updateDashboard();
        }

        if (page === 'home') {
            const featureCards = document.querySelectorAll('.feature-card');
            featureCards.forEach((card, index) => {
                card.style.animation = `fadeInUp 0.6s ease ${(index + 0.4) * 0.15}s backwards`;
            });
        }

        window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 150);
}

// ============ AUTHENTICATION ============

function toggleAuthMode() {
    isRegistering = !isRegistering;

    const title = document.getElementById('authTitle');
    const subtitle = document.getElementById('authSubtitle');
    const toggleText = document.getElementById('toggleText');
    const loginFields = document.getElementById('loginFields');
    const registerFields = document.getElementById('registerFields');
    const submitBtn = document.querySelector('#authForm button');

    if (isRegistering) {
        title.textContent = 'Create New Account';
        subtitle.textContent = 'Join thousands of citizens reporting safely';
        loginFields.classList.add('hidden');
        registerFields.classList.remove('hidden');
        submitBtn.textContent = '✓ Create Account';
        toggleText.innerHTML = 'Already have an account? <a href="#" onclick="toggleAuthMode()" class="link-hover">Sign in</a>';
    } else {
        title.textContent = 'Welcome Back';
        subtitle.textContent = 'Sign in to your account';
        registerFields.classList.add('hidden');
        loginFields.classList.remove('hidden');
        submitBtn.textContent = 'Sign In';
        toggleText.innerHTML = "Don't have an account? <a href=\"#\" onclick=\"toggleAuthMode()\" class=\"link-hover\">Register now</a>";
    }
}

function handleAuth(e) {
    e.preventDefault();

    if (isRegistering) {
        const name = document.getElementById('regName').value.trim();
        const email = document.getElementById('regEmail').value.trim().toLowerCase();
        const phone = document.getElementById('regPhone').value.trim();
        const password = document.getElementById('regPassword').value.trim();
        const confirm = document.getElementById('regConfirm').value.trim();

        if (!name || !email || !phone || !password || !confirm) {
            showNotification('❌ Please fill all fields!', 'error');
            return;
        }

        if (password.length < 6) {
            showNotification('❌ Password must be at least 6 characters!', 'error');
            return;
        }

        if (password !== confirm) {
            showNotification('❌ Passwords do not match!', 'error');
            return;
        }

        if (users.some(u => u.email === email)) {
            showNotification('❌ Email already registered!', 'error');
            return;
        }

        const newUser = {
            id: Math.max(...users.map(u => u.id), 0) + 1,
            name,
            email,
            phone,
            password,
            role: 'user'
        };

        users.push(newUser);
        localStorage.setItem('users', JSON.stringify(users));
        showNotification('✅ Registration successful! Please login.', 'success');
        
        setTimeout(() => {
            isRegistering = false;
            toggleAuthMode();
        }, 1000);
    } else {
        const email = document.getElementById('loginEmail').value.trim().toLowerCase();
        const password = document.getElementById('loginPassword').value;
        const role = document.getElementById('loginRole').value;

        if (!email || !password) {
            showNotification('❌ Please enter email and password!', 'error');
            return;
        }

        const user = users.find(u => u.email === email && u.password === password && u.role === role);

        if (user) {
            currentUser = user;
            document.getElementById('userName').textContent = user.name;
            document.getElementById('navLinks').innerHTML = `
                <li><a href="#" onclick="showPage('dashboard')">Dashboard</a></li>
                <li><a href="#" onclick="handleLogout()">Logout</a></li>
            `;
            showNotification(`👋 Welcome back, ${user.name}!`, 'success');
            
            setTimeout(() => {
                showPage('dashboard');
            }, 1000);
        } else {
            showNotification('❌ Invalid credentials or role!', 'error');
        }
    }
}

// ============ DASHBOARD ============

function updateDashboard() {
    if (currentUser.role === 'user') {
        document.getElementById('userDashboard').classList.remove('hidden');
        document.getElementById('adminDashboard').classList.add('hidden');
        
        const userComplaints = complaints.filter(c => c.userId === currentUser.id);
        const pending = userComplaints.filter(c => c.status === 'Submitted' || c.status === 'In Review').length;
        const resolved = userComplaints.filter(c => c.status === 'Accepted' || c.status === 'Closed').length;

        animateCounter('totalComplaints', userComplaints.length);
        animateCounter('pendingComplaints', pending);
        animateCounter('resolvedComplaints', resolved);

        renderUserComplaints(userComplaints);
    } else {
        document.getElementById('userDashboard').classList.add('hidden');
        document.getElementById('adminDashboard').classList.remove('hidden');

        const pending = complaints.filter(c => c.status === 'Submitted').length;
        const accepted = complaints.filter(c => c.status === 'Accepted').length;
        const rejected = complaints.filter(c => c.status === 'Rejected').length;

        animateCounter('adminTotal', complaints.length);
        animateCounter('adminPending', pending);
        animateCounter('adminAccepted', accepted);
        animateCounter('adminRejected', rejected);

        renderAdminComplaints();
    }
}

function animateCounter(elementId, finalValue) {
    const element = document.getElementById(elementId);
    const startValue = 0;
    const duration = 500;
    const increment = finalValue / (duration / 16);
    let currentValue = 0;

    const counter = setInterval(() => {
        currentValue += increment;
        if (currentValue >= finalValue) {
            currentValue = finalValue;
            clearInterval(counter);
        }
        element.textContent = Math.round(currentValue);
    }, 16);
}

function renderUserComplaints(userComplaints) {
    const container = document.getElementById('userComplaints');
    
    if (userComplaints.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <svg class="empty-icon" viewBox="0 0 64 64">
                    <circle cx="32" cy="32" r="30" fill="none" stroke="#e5e7eb" stroke-width="2"/>
                    <path fill="#e5e7eb" d="M20 28h24v4H20z"/>
                    <path fill="#e5e7eb" d="M20 36h24v4H20z"/>
                </svg>
                <h3>No reports filed yet</h3>
                <p>File your first report above to get started</p>
            </div>
        `;
        return;
    }

    let tableHtml = `
        <table>
            <thead>
                <tr>
                    <th>Report ID</th>
                    <th>Category</th>
                    <th>Date</th>
                    <th>Status</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
    `;

    userComplaints.forEach(c => {
        tableHtml += `
            <tr>
                <td><strong>#${c.id}</strong></td>
                <td>${c.category}</td>
                <td>${formatDate(c.date)}</td>
                <td><span class="badge badge-${c.status.toLowerCase().replace(' ', '-')}">${c.status}</span></td>
                <td><button class="btn btn-primary btn-sm" onclick="showComplaintDetails(${c.id})">View Details</button></td>
            </tr>
        `;
    });

    tableHtml += `
            </tbody>
        </table>
    `;

    container.innerHTML = tableHtml;
}

function renderAdminComplaints() {
    const container = document.getElementById('adminComplaints');
    
    if (complaints.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <svg class="empty-icon" viewBox="0 0 64 64">
                    <circle cx="32" cy="32" r="30" fill="none" stroke="#e5e7eb" stroke-width="2"/>
                    <path fill="#e5e7eb" d="M20 28h24v4H20z"/>
                    <path fill="#e5e7eb" d="M20 36h24v4H20z"/>
                </svg>
                <h3>No reports pending</h3>
                <p>All reports have been reviewed</p>
            </div>
        `;
        return;
    }

    let tableHtml = `
        <table>
            <thead>
                <tr>
                    <th>Report ID</th>
                    <th>Reporter</th>
                    <th>Category</th>
                    <th>Date</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

    complaints.forEach(c => {
        const reporter = users.find(u => u.id === c.userId);
        tableHtml += `
            <tr>
                <td><strong>#${c.id}</strong></td>
                <td>${reporter ? reporter.name : 'Unknown'}</td>
                <td>${c.category}</td>
                <td>${formatDate(c.date)}</td>
                <td><span class="badge badge-${c.status.toLowerCase().replace(' ', '-')}">${c.status}</span></td>
                <td>
                    <button class="btn btn-primary btn-sm" onclick="showComplaintDetails(${c.id})">Review</button>
                    <button class="btn btn-success btn-sm" onclick="updateComplaintStatus(${c.id}, 'Accepted')">✓</button>
                    <button class="btn btn-danger btn-sm" onclick="updateComplaintStatus(${c.id}, 'Rejected')">✕</button>
                </td>
            </tr>
        `;
    });

    tableHtml += `
            </tbody>
        </table>
    `;

    container.innerHTML = tableHtml;
}

// ============ COMPLAINT DETAILS ============

function showComplaintDetails(complaintId) {
    const complaint = complaints.find(c => c.id === complaintId);
    const reporter = users.find(u => u.id === complaint.userId);

    const modalBody = document.getElementById('modalBody');
    const modalTitle = document.getElementById('modalTitle');
    
    modalTitle.textContent = `Report #${complaint.id}`;
    
    modalBody.innerHTML = `
        <div style="margin-bottom: 20px;">
            <h3 style="margin-bottom: 12px; color: var(--primary); font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">Reported By</h3>
            <p><strong>Name:</strong> ${reporter ? reporter.name : 'Unknown'}</p>
            <p><strong>Email:</strong> ${reporter ? reporter.email : 'N/A'}</p>
            <p><strong>Phone:</strong> ${reporter ? reporter.phone : 'N/A'}</p>
        </div>
        
        <hr>
        
        <div style="margin-bottom: 20px;">
            <h3 style="margin-bottom: 12px; color: var(--primary); font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">Report Details</h3>
            <p><strong>Category:</strong> ${complaint.category}</p>
            <p><strong>Date & Time:</strong> ${formatDate(complaint.date)} at ${complaint.time}</p>
            <p><strong>Location:</strong> ${complaint.location}</p>
            <p><strong>Status:</strong> <span class="badge badge-${complaint.status.toLowerCase().replace(' ', '-')}">${complaint.status}</span></p>
        </div>
        
        <hr>
        
        <div style="margin-bottom: 20px;">
            <h3 style="margin-bottom: 12px; color: var(--primary); font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">Description</h3>
            <p>${complaint.description}</p>
        </div>
        
        ${complaint.evidence ? `
            <hr>
            <div>
                <h3 style="margin-bottom: 12px; color: var(--primary); font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">Evidence</h3>
                <p>📎 ${complaint.evidence}</p>
            </div>
        ` : ''}
    `;
    
    document.getElementById('detailsModal').classList.add('show');
}

function updateComplaintStatus(complaintId, newStatus) {
    const complaint = complaints.find(c => c.id === complaintId);
    if (complaint) {
        complaint.status = newStatus;
        localStorage.setItem('complaints', JSON.stringify(complaints));
        updateDashboard();
        closeModal();
        showNotification(`✅ Report status updated to: ${newStatus}`, 'success');
    }
}

// ============ COMPLAINT SUBMISSION ============

function handleComplaintSubmit(e) {
    e.preventDefault();

    const category = document.getElementById('crimeCategory').value;
    const date = document.getElementById('crimeDate').value;
    const time = document.getElementById('crimeTime').value;
    const location = document.getElementById('crimeLocation').value;
    const description = document.getElementById('crimeDescription').value;
    const evidence = document.getElementById('crimeEvidence').files[0];

    if (!category || !date || !time || !location || !description) {
        showNotification('❌ Please fill all required fields!', 'error');
        return;
    }

    const newComplaint = {
        id: Math.max(...complaints.map(c => c.id), 0) + 1,
        userId: currentUser.id,
        category,
        date,
        time,
        location,
        description,
        status: 'Submitted',
        evidence: evidence ? evidence.name : null,
        createdAt: new Date().toISOString()
    };

    complaints.push(newComplaint);
    localStorage.setItem('complaints', JSON.stringify(complaints));

    showNotification(`🎉 Report #${newComplaint.id} submitted successfully!`, 'success');
    document.getElementById('complaintForm').reset();
    updateDashboard();
    
    setTimeout(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 500);
}

// ============ LOGOUT ============

function handleLogout() {
    currentUser = null;
    isRegistering = false;
    document.getElementById('navLinks').innerHTML = `
        <li><a href="#" onclick="showPage('home')">Home</a></li>
        <li><a href="#" onclick="showPage('auth')">Login</a></li>
    `;
    showNotification('👋 Logged out successfully', 'success');
    showPage('home');
}

// ============ MODALS ============

function closeModal() {
    document.getElementById('detailsModal').classList.remove('show');
}

window.onclick = function(event) {
    const modal = document.getElementById('detailsModal');
    if (event.target === modal) {
        modal.classList.remove('show');
    }
}

// ============ NOTIFICATIONS ============

function showNotification(message, type = 'info') {
    const container = document.getElementById('notificationContainer');
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    container.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'fadeInUp 0.3s ease reverse';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 4000);
}

function showDemoInfo() {
    const message = `
👤 Citizen Demo:
Email: user@example.com
Password: user123

👮 Police Officer Demo:
Email: admin@example.com
Password: admin123
    `;
    alert(message);
}

// ============ UTILITIES ============

function formatDate(dateStr) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateStr).toLocaleDateString('en-US', options);
}

// ============ INITIALIZATION ============

document.addEventListener('DOMContentLoaded', () => {
    showPage('home');
});
