# 🔐 SecureAuth - Production-Grade Authentication System

A complete, enterprise-ready authentication system with **10 critical security features** already implemented. Built with Flask, Supabase, and security best practices.

## 📋 Project Structure

```
secure-auth-system/
├── app.py                    # Main Flask application (700+ lines)
├── config.py                 # Configuration & environment validation
├── security.py               # CSRF, hashing, sanitization, rate limiting
├── email_service.py          # Email sending for verification/reset
├── middleware.py             # Logging, security headers, HTTPS enforcement
├── requirements.txt          # Python dependencies
├── .env.example               # Template for environment variables
├── .env                      # Your actual config (DO NOT COMMIT)
├── logs/
│   └── auth.log             # Authentication event logs (auto-created)
├── templates/               # HTML templates
│   ├── base.html            # Base template with CSS styling
│   ├── login.html           # Login page
│   ├── register.html        # Registration page
│   ├── forgot_password.html # Password recovery
│   ├── reset_password.html  # Password reset form
│   ├── verify_email.html    # Email verification
│   ├── dashboard.html       # Protected dashboard
│   └── error.html           # Error pages
└── README.md                # This file
```

## 🔒 Security Features Implemented

### 1. **CSRF Protection**
- **What**: Unique tokens on all forms, validated server-side
- **Why**: Prevents Cross-Site Request Forgery attacks
- **How**: `CSRFToken.generate()` and `CSRFToken.validate()`
- **Code**: See `security.py` lines 14-37 and `app.py` lines 106-119

### 2. **Rate Limiting**
- **What**: Max 5 login attempts per 15 minutes per IP
- **Why**: Prevents brute force attacks
- **How**: In-memory tracking with timestamp validation
- **Code**: See `security.py` lines 200-264 and `app.py` lines 303-312

### 3. **Email Verification**
- **What**: Send verification email on signup, block login until verified
- **Why**: Confirms user owns the email, prevents spam accounts
- **How**: Generate secure token, send email link, mark verified in DB
- **Code**: See `email_service.py` and `app.py` lines 441-502

### 4. **Password Reset**
- **What**: Forgot password flow with time-limited secure reset tokens
- **Why**: Allows users to recover accounts securely
- **How**: 1-hour expiring tokens, hashed in database
- **Code**: See `app.py` lines 696-832

### 5. **Account Lockout**
- **What**: Lock account for 30 minutes after 5 failed login attempts
- **Why**: Prevents brute force attacks
- **How**: Track failed attempts, set lockout timestamp
- **Code**: See `app.py` lines 604-616 and 652-679

### 6. **HTTPS/SSL Enforcement**
- **What**: Enforce HTTPS, redirect all HTTP to HTTPS
- **Why**: Encrypts data in transit, prevents man-in-the-middle attacks
- **How**: `@enforce_https` decorator on all routes
- **Code**: See `middleware.py` lines 58-74

### 7. **Security Headers**
- **What**: CSP, X-Frame-Options, X-Content-Type-Options, HSTS, etc.
- **Why**: Prevents XSS, clickjacking, MIME-sniffing, weak HTTPS
- **How**: Added via `@after_request` hook on every response
- **Code**: See `middleware.py` lines 85-138

### 8. **Input Sanitization**
- **What**: Validate and sanitize all user inputs
- **Why**: Prevents SQL injection and XSS attacks
- **How**: Regex validation, HTML encoding, length limits
- **Code**: See `security.py` lines 141-270

### 9. **Error Logging**
- **What**: Log all authentication events with timestamps
- **Why**: Enables security monitoring and incident investigation
- **How**: Rotating file handler, separate logs for each event type
- **Code**: See `middleware.py` lines 23-55 and logging calls throughout

### 10. **Environment Validation**
- **What**: Check all required environment variables on startup
- **Why**: Prevents runtime errors, ensures secure configuration
- **How**: `ConfigValidator.validate()` called at app startup
- **Code**: See `config.py` lines 11-54

---

## 🚀 Quick Start

### 1. **Clone & Install**
```bash
cd Secure-Auth-System
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your values:
# - SUPABASE_URL and SUPABASE_KEY
# - SMTP credentials for email sending
# - SECRET_KEY and PEPPER (generate with: python -c "import secrets; print(secrets.token_hex(32))")
```

### 3. **Setup Database**
Create a `users` table in Supabase:
```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    username VARCHAR(32) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(32) NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    verification_token_hash VARCHAR(64),
    verification_token_expires TIMESTAMP,
    password_reset_token_hash VARCHAR(64),
    password_reset_token_expires TIMESTAMP,
    failed_login_attempts INT DEFAULT 0,
    account_locked_until TIMESTAMP,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

### 4. **Run the Application**
```bash
python app.py
```

Visit http://localhost:5000 in your browser.

---

## 📊 Architecture Overview

### Request Flow
```
1. User submits form
   ↓
2. CSRF token validation
   ↓
3. Rate limiting check
   ↓
4. Input sanitization & validation
   ↓
5. Database query (with parameterized statements)
   ↓
6. Security operation (hash, token, etc.)
   ↓
7. Response with security headers
   ↓
8. Event logged to file
```

### Database Schema
```
users
├── id (primary key)
├── username (unique, validated)
├── email (unique, verified)
├── password_hash (bcrypt)
├── salt (random 16 bytes)
├── email_verified (bool)
├── verification_token_hash (SHA-256)
├── verification_token_expires (1-hour TTL)
├── password_reset_token_hash (SHA-256)
├── password_reset_token_expires (24-hour TTL)
├── failed_login_attempts (tracked)
├── account_locked_until (30-min lockout)
├── last_login (timestamp)
└── created_at / updated_at (timestamps)
```

---

## 🔐 Password Security

Passwords are protected with a 3-layer security approach:

```
User's Password
    ↓
+ Salt (16 random bytes per user, stored in DB)
+ Pepper (64-char secret, NOT in DB, from config)
    ↓
bcrypt(password + salt + pepper, cost=12)
    ↓
Stored Hash (never reversible, takes ~100ms to hash)
```

**Why this approach:**
- **Salt**: Prevents rainbow table attacks, unique per user
- **Pepper**: Server-side secret, provides additional protection
- **bcrypt**: Adaptive cost, resistant to GPU brute force attacks

**Never stored in plain text.** Even if database is breached, passwords remain secure.

---

## 📧 Email Service

### Verification Email
- Sent on registration
- Contains unique 24-hour token
- User must verify before login
- Token is hashed in database for security

### Password Reset Email
- Sent on "Forgot Password"
- Contains unique 1-hour token
- User can reset password using token
- Email address not revealed for non-existent accounts (prevents enumeration)

### Account Lockout Email
- Sent when account locked
- Notifies user of suspicious activity
- Recommends immediate password reset

---

## 🛡️ Security Best Practices

### ✅ Do's
- Always use HTTPS in production
- Keep `.env` file in `.gitignore`
- Rotate SECRET_KEY and PEPPER regularly
- Monitor logs for suspicious patterns
- Update dependencies regularly
- Use strong email credentials

### ❌ Don'ts
- Never commit `.env` to version control
- Don't log sensitive data (passwords, tokens)
- Don't expose error messages to users
- Don't use debug mode in production
- Don't hardcode secrets
- Don't store plain text passwords

---

## 📝 Configuration Guide

### Required Environment Variables
```
# Flask
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=<64-char hex string>

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=<your anon key>
SUPABASE_SERVICE_ROLE_KEY=<your service role key>

# Security
PEPPER=<64-char hex string>

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=<app-specific password>
EMAIL_FROM=noreply@secureauth.com
```

### Generate Secure Keys
```python
import secrets
print(secrets.token_hex(32))  # 64-char hex string
```

---

## 🚢 Deployment

### Using Gunicorn (Recommended)
```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
```

### Environment Variables in Production
Set via your hosting platform (Heroku, Railway, Fly.io, etc.):
- Never paste into shell history
- Use platform's secrets manager
- Rotate keys periodically

### Database Backups
- Enable Supabase backups
- Test restore procedures
- Store backups in secure location

### Monitoring
- Monitor `/logs/auth.log` for suspicious patterns
- Set up alerts for multiple failed logins
- Track password reset requests
- Monitor account lockouts

---

## 🧪 Testing

### Manual Testing
1. **Registration**: Create new account, verify email
2. **Login**: Attempt with wrong password (verify rate limiting)
3. **Password Reset**: Forgot password → reset → login with new password
4. **Account Lockout**: Attempt 5 failed logins
5. **Session**: Login → refresh → verify still logged in
6. **Logout**: Logout → attempt to access dashboard

### Security Testing
```bash
# Test CSRF protection
curl -X POST http://localhost:5000/login \
  -d "username=test&password=test"
# Should fail without CSRF token

# Test rate limiting
for i in {1..10}; do
  curl -X POST http://localhost:5000/login \
    -d "username=test&password=wrong"
done
# Should block after 5 attempts

# Check security headers
curl -I http://localhost:5000/login
# Should include HSTS, CSP, X-Frame-Options, etc.
```

---

## 📊 Logging Events

The system logs the following events to `logs/auth.log`:

```
[2024-01-15 10:30:45] INFO - User registered: john_doe
[2024-01-15 10:31:12] INFO - Email verification sent: john_doe@example.com
[2024-01-15 10:35:20] INFO - Email verified: john_doe
[2024-01-15 10:36:00] INFO - Successful login: john_doe from IP: 192.168.1.1
[2024-01-15 10:37:45] WARNING - Failed login attempt - Username: john_doe, IP: 192.168.1.2, Reason: Invalid password
[2024-01-15 10:38:30] WARNING - Login rate limit exceeded for IP: 192.168.1.2
[2024-01-15 10:40:00] WARNING - Account locked - Username: john_doe, IP: 192.168.1.2
[2024-01-15 10:50:15] INFO - Password reset requested: john_doe@example.com
[2024-01-15 10:52:30] INFO - Password reset completed: john_doe
[2024-01-15 10:55:45] INFO - User logged out: john_doe
```

---

## 🔄 Production Checklist

Before going live:

- [ ] Set `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=False`
- [ ] Configure strong `SECRET_KEY`
- [ ] Configure strong `PEPPER`
- [ ] Set up SMTP credentials for email
- [ ] Create Supabase database with proper indexes
- [ ] Enable HTTPS with SSL certificate
- [ ] Configure CORS if needed
- [ ] Set up log monitoring
- [ ] Test all authentication flows
- [ ] Test rate limiting
- [ ] Test email sending
- [ ] Test password reset
- [ ] Test account lockout
- [ ] Review security headers
- [ ] Review environment variables
- [ ] Set up database backups
- [ ] Set up error tracking (Sentry)
- [ ] Document disaster recovery procedures
- [ ] Create admin account for testing

---

## 📚 Technologies Used

- **Framework**: Flask 3.0.0
- **Database**: Supabase (PostgreSQL)
- **Password Hashing**: bcrypt 4.1.2
- **Email**: SMTP with TLS
- **Security**: Flask-Talisman for security headers
- **Rate Limiting**: Custom in-memory tracker
- **Templating**: Jinja2 (Flask built-in)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript

---

## 🤝 Contributing

This is a learning and reference project. Feel free to:
- Study the security implementations
- Use as a template for your projects
- Suggest security improvements
- Report security vulnerabilities responsibly

---

## 📄 License

This project is provided as-is for educational and reference purposes.

---

## 🔗 Resources

- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [Flask Security](https://flask.palletsprojects.com/security/)
- [Bcrypt Documentation](https://github.com/pyca/bcrypt)
- [CSRF Prevention](https://owasp.org/www-community/attacks/csrf)
- [Password Security](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

---

**Built with 🔒 security in mind. Questions? Review the code comments!**
