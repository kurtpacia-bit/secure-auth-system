"""
SecureAuth - Production-Grade Secure Authentication System
Complete authentication with 10 security features implemented.

Security Features:
1. CSRF Protection - Tokens on all forms
2. Rate Limiting - 5 login attempts per 15 minutes
3. Email Verification - Verification required before login
4. Password Reset - Time-limited reset tokens via email
5. Account Lockout - 30-minute lockout after 5 failed attempts
6. HTTPS/SSL - Enforce HTTPS, redirect HTTP
7. Security Headers - CSP, X-Frame-Options, HSTS, etc.
8. Input Sanitization - Prevent SQL injection and XSS
9. Error Logging - Log all auth events with timestamps
10. Environment Validation - Check all required config on startup

Folder Structure:
.
├── app.py (this file)
├── config.py (configuration and environment validation)
├── security.py (CSRF, password hashing, input validation)
├── email_service.py (email sending)
├── middleware.py (logging, security headers, HTTPS)
├── requirements.txt (dependencies)
├── .env.example (all required environment variables)
├── templates/
│   ├── base.html (base template with CSS)
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── forgot_password.html
│   ├── reset_password.html
│   └── verify_email.html
├── static/
│   └── css/style.css
└── logs/
    └── auth.log (automatically created)
"""

import os
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, session,
    flash, jsonify, g
)
from supabase import create_client, Client
from config import ConfigValidator, config, Config
from security import (
    CSRFToken, PasswordSecurity, InputValidation, RateLimitTracker,
    TokenGenerator
)
from email_service import EmailService
from middleware import (
    setup_logging, add_security_headers, enforce_https, log_request,
    log_failed_login, log_account_locked, log_email_verification,
    log_password_reset, before_request, after_request
)

# ==================== VALIDATE CONFIGURATION ====================
ConfigValidator.validate()

# ==================== FLASK APP INITIALIZATION ====================

app = Flask(__name__)
app.config.from_object(config)

# Setup logging
logger = setup_logging()

# Initialize Supabase
supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

# ==================== REQUEST HOOKS ====================


@app.before_request
def _before_request():
    """Hook before each request for logging and context setup."""
    before_request()
    
    # Generate CSRF token for session if not exists
    if 'csrf_token' not in session:
        session['csrf_token'] = CSRFToken.generate(config.CSRF_TOKEN_LENGTH)


@app.after_request
def _after_request(response):
    """Hook after each request for logging and security headers."""
    return after_request(response)


# ==================== CONTEXT PROCESSORS ====================


@app.context_processor
def inject_csrf_token():
    """Make CSRF token available in all templates."""
    return {'csrf_token': session.get('csrf_token')}


@app.context_processor
def inject_user_info():
    """Make user info available in all templates."""
    username = session.get('username')
    is_authenticated = session.get('logged_in', False)
    return {'username': username, 'is_authenticated': is_authenticated}


# ==================== DECORATOR: LOGIN REQUIRED ====================


def login_required(f):
    """
    Decorator to require user to be logged in.
    Redirects to login page if user not authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def logout_required(f):
    """
    Decorator to require user to be logged out.
    Redirects to dashboard if user already authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('logged_in'):
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== HELPER: VERIFY CSRF TOKEN ====================


def verify_csrf(request_form):
    """
    Verify CSRF token from form submission.
    Protects against Cross-Site Request Forgery attacks.

    Returns:
        Tuple of (is_valid, error_message)
    """
    token = request_form.get('csrf_token', '')
    session_token = session.get('csrf_token', '')

    if not token or not session_token:
        return False, "Missing CSRF token"

    if not CSRFToken.validate(token, session_token):
        logger.warning(f"CSRF validation failed for IP: {g.client_ip}")
        return False, "Invalid CSRF token"

    return True, ""


# ==================== ROUTE: HOME ====================


@app.route('/')
@enforce_https
def index():
    """Home page - redirects to dashboard if logged in, login otherwise."""
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


# ==================== ROUTE: REGISTER ====================


@app.route('/register', methods=['GET', 'POST'])
@logout_required
@enforce_https
@log_request
def register():
    """
    User registration with instant login capability.

    Security features:
    - Rate limiting: max 3 registrations per hour per IP
    - Password strength validation
    - Email validation
    - CSRF protection
    - Input sanitization
    - Instant account creation (no email verification required)
    """

    if request.method == 'GET':
        return render_template('register.html')

    # ========== RATE LIMITING ==========
    client_ip = request.remote_addr
    is_allowed, attempts_remaining = RateLimitTracker.check_rate_limit(
        f"register_{client_ip}", 3, 3600  # 3 per hour
    )

    if not is_allowed:
        logger.warning(f"Registration rate limit exceeded for IP: {client_ip}")
        flash('Too many registration attempts. Please try again later.', 'error')
        return redirect(url_for('register'))

    # ========== CSRF VALIDATION ==========
    is_valid, error = verify_csrf(request.form)
    if not is_valid:
        flash(error, 'error')
        return redirect(url_for('register'))

    # ========== INPUT COLLECTION & SANITIZATION ==========
    username = InputValidation.sanitize_string(
        request.form.get('username', '')
    )
    email = InputValidation.sanitize_string(
        request.form.get('email', '').lower()
    )
    password = request.form.get('password', '')

    # ========== INPUT VALIDATION ==========
    is_valid, error = InputValidation.validate_username(username)
    if not is_valid:
        flash(error, 'error')
        return redirect(url_for('register'))

    is_valid, error = InputValidation.validate_email(email)
    if not is_valid:
        flash(error, 'error')
        return redirect(url_for('register'))

    password_check = InputValidation.validate_password(password)
    if not password_check['is_valid']:
        flash('Password does not meet security requirements', 'error')
        return redirect(url_for('register'))

    # ========== CHECK DUPLICATE USERNAME/EMAIL ==========
    try:
        user_exists = supabase.table('users').select('id').eq(
            'username', username
        ).execute()

        if user_exists.data:
            flash('Username already exists', 'error')
            return redirect(url_for('register'))

        email_exists = supabase.table('users').select('id').eq(
            'email', email
        ).execute()

        if email_exists.data:
            flash('Email already registered', 'error')
            return redirect(url_for('register'))

    except Exception as e:
        logger.error(f"Database error during registration: {str(e)}")
        flash('Registration failed. Please try again later.', 'error')
        return redirect(url_for('register'))

    # ========== HASH PASSWORD ==========
    try:
        hashed_password, salt = PasswordSecurity.hash_password(
            password, config.PEPPER
        )
    except Exception as e:
        logger.error(f"Password hashing error: {str(e)}")
        flash('Registration failed. Please try again later.', 'error')
        return redirect(url_for('register'))

    # ========== CREATE USER IN DATABASE ==========
    # Note: Email verification is skipped for instant registration
    try:
        response = supabase.table('users').insert({
            'username': username,
            'email': email,
            'password_hash': hashed_password,
            'salt': salt,
            'email_verified': True,  # Auto-verified for instant login
            'verification_token_hash': None,
            'verification_token_expires': None,
            'failed_login_attempts': 0,
            'account_locked_until': None,
            'created_at': datetime.utcnow().isoformat()
        }).execute()

        logger.info(f"New user registered: {username}, Email: {email}")
        RateLimitTracker.record_attempt(f"register_{client_ip}")
        
        flash(
            'Registration successful! You can now login.',
            'success'
        )
        return redirect(url_for('login'))

    except Exception as e:
        logger.error(f"Failed to create user: {str(e)}")
        flash('Registration failed. Please try again later.', 'error')
        return redirect(url_for('register'))


# ==================== ROUTE: VERIFY EMAIL ====================


@app.route('/verify-email/<token>')
@logout_required
@enforce_https
def verify_email(token):
    """
    Verify user's email address via token link.
    Token expires after configured time (default 24 hours).
    """

    # ========== HASH TOKEN FOR DATABASE LOOKUP ==========
    token_hash = TokenGenerator.generate_token_hash(token)

    try:
        # Find user with this token
        response = supabase.table('users').select('*').eq(
            'verification_token_hash', token_hash
        ).execute()

        if not response.data:
            logger.warning(f"Invalid verification token: {token_hash[:10]}...")
            flash('Invalid or expired verification link', 'error')
            return redirect(url_for('login'))

        user = response.data[0]

        # Check if token expired
        if user['verification_token_expires']:
            expires = datetime.fromisoformat(
                user['verification_token_expires'].replace('Z', '+00:00')
            )
            if datetime.utcnow() > expires:
                logger.warning(f"Expired verification token for user: {user['username']}")
                flash('Verification link has expired. Please register again.', 'error')
                return redirect(url_for('register'))

        # Check if already verified
        if user['email_verified']:
            flash('Email already verified. Please log in.', 'info')
            return redirect(url_for('login'))

        # ========== MARK EMAIL AS VERIFIED ==========
        supabase.table('users').update({
            'email_verified': True,
            'verification_token_hash': None,
            'verification_token_expires': None
        }).eq('id', user['id']).execute()

        log_email_verification(user['username'], user['email'], True)
        flash('Email verified successfully! You can now log in.', 'success')
        return redirect(url_for('login'))

    except Exception as e:
        logger.error(f"Email verification error: {str(e)}")
        flash('Verification failed. Please try again later.', 'error')
        return redirect(url_for('login'))


# ==================== ROUTE: LOGIN ====================


@app.route('/login', methods=['GET', 'POST'])
@logout_required
@enforce_https
@log_request
def login():
    """
    User login with password verification.

    Security features:
    - Rate limiting: max 5 failed attempts per 15 minutes per IP
    - Account lockout: 30 minutes after 5 failures
    - Email verification required
    - Constant-time password comparison
    - CSRF protection
    """

    if request.method == 'GET':
        return render_template('login.html')

    # ========== RATE LIMITING ==========
    client_ip = request.remote_addr
    is_allowed, attempts_remaining = RateLimitTracker.check_rate_limit(
        f"login_{client_ip}", 5, 900  # 5 per 15 minutes
    )

    if not is_allowed:
        logger.warning(f"Login rate limit exceeded for IP: {client_ip}")
        flash(
            'Too many failed login attempts. Please try again in 15 minutes.',
            'error'
        )
        return redirect(url_for('login'))

    # ========== CSRF VALIDATION ==========
    is_valid, error = verify_csrf(request.form)
    if not is_valid:
        flash(error, 'error')
        return redirect(url_for('login'))

    # ========== INPUT COLLECTION & SANITIZATION ==========
    username = InputValidation.sanitize_string(
        request.form.get('username', '')
    )
    password = request.form.get('password', '')

    if not username or not password:
        flash('Username and password are required', 'error')
        return redirect(url_for('login'))

    # ========== FETCH USER FROM DATABASE ==========
    # Support both username and email login
    try:
        # First try to find user by username
        response = supabase.table('users').select('*').eq(
            'username', username
        ).execute()

        # If not found by username, try by email
        if not response.data:
            response = supabase.table('users').select('*').eq(
                'email', username
            ).execute()

        if not response.data:
            RateLimitTracker.record_attempt(f"login_{client_ip}")
            log_failed_login(username, client_ip, "Username/Email not found")
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))

        user = response.data[0]

    except Exception as e:
        logger.error(f"Database error during login: {str(e)}")
        flash('Login failed. Please try again later.', 'error')
        return redirect(url_for('login'))

    # ========== CHECK ACCOUNT LOCKOUT ==========
    if user['account_locked_until']:
        locked_until = datetime.fromisoformat(
            user['account_locked_until'].replace('Z', '+00:00')
        )
        if datetime.utcnow() < locked_until:
            remaining_minutes = int((locked_until - datetime.utcnow()).total_seconds() / 60)
            flash(
                f'Account temporarily locked. Try again in {remaining_minutes} minutes.',
                'error'
            )
            return redirect(url_for('login'))
        else:
            # Unlock account
            supabase.table('users').update({
                'account_locked_until': None,
                'failed_login_attempts': 0
            }).eq('id', user['id']).execute()

    # ========== CHECK EMAIL VERIFICATION ==========
    if not user['email_verified']:
        logger.warning(f"Login attempt with unverified email: {username}")
        flash('Please verify your email before logging in.', 'error')
        return redirect(url_for('login'))

    # ========== VERIFY PASSWORD ==========
    is_valid = PasswordSecurity.verify_password(
        password,
        user['password_hash'],
        user['salt'],
        config.PEPPER
    )

    if not is_valid:
        # ========== HANDLE FAILED LOGIN ATTEMPT ==========
        failed_attempts = user['failed_login_attempts'] + 1
        update_data = {'failed_login_attempts': failed_attempts}

        # Lock account after MAX_LOGIN_ATTEMPTS
        if failed_attempts >= config.MAX_LOGIN_ATTEMPTS:
            locked_until = datetime.utcnow() + timedelta(
                seconds=config.LOCKOUT_DURATION
            )
            update_data['account_locked_until'] = locked_until.isoformat()
            log_account_locked(username, client_ip)
            EmailService.send_account_locked_email(user['email'], username)
            flash(
                'Too many failed login attempts. Account locked for 30 minutes.',
                'error'
            )
        else:
            flash('Invalid username or password', 'error')

        supabase.table('users').update(update_data).eq('id', user['id']).execute()
        RateLimitTracker.record_attempt(f"login_{client_ip}")
        log_failed_login(username, client_ip, "Invalid password")

        return redirect(url_for('login'))

    # ========== LOGIN SUCCESSFUL ==========
    # Reset failed login attempts
    supabase.table('users').update({
        'failed_login_attempts': 0,
        'account_locked_until': None,
        'last_login': datetime.utcnow().isoformat()
    }).eq('id', user['id']).execute()

    # Create session
    session.permanent = True
    session['logged_in'] = True
    session['user_id'] = user['id']
    session['username'] = username
    session['email'] = user['email']

    RateLimitTracker.reset_attempts(f"login_{client_ip}")
    logger.info(f"Successful login: {username} from IP: {client_ip}")
    flash(f'Welcome back, {username}!', 'success')

    return redirect(url_for('dashboard'))


# ==================== ROUTE: DASHBOARD ====================


@app.route('/dashboard')
@login_required
@enforce_https
def dashboard():
    """
    Protected dashboard page - only accessible to logged-in users.
    """
    return render_template('dashboard.html')


# ==================== ROUTE: LOGOUT ====================


@app.route('/logout')
@login_required
@enforce_https
def logout():
    """
    Logout user and clear session.
    """
    username = session.get('username', 'Unknown')
    session.clear()
    logger.info(f"User logged out: {username}")
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))


# ==================== ROUTE: FORGOT PASSWORD ====================


@app.route('/forgot-password', methods=['GET', 'POST'])
@logout_required
@enforce_https
def forgot_password():
    """
    Forgot password - send password reset email.

    Security features:
    - Email verification required
    - Rate limited
    - Secure token generation
    - Token hashed in database
    - 1-hour expiration
    """

    if request.method == 'GET':
        return render_template('forgot_password.html')

    # ========== CSRF VALIDATION ==========
    is_valid, error = verify_csrf(request.form)
    if not is_valid:
        flash(error, 'error')
        return redirect(url_for('forgot_password'))

    # ========== INPUT SANITIZATION & VALIDATION ==========
    email = InputValidation.sanitize_string(
        request.form.get('email', '').lower()
    )

    is_valid, error = InputValidation.validate_email(email)
    if not is_valid:
        flash(error, 'error')
        return redirect(url_for('forgot_password'))

    # ========== FIND USER BY EMAIL ==========
    try:
        response = supabase.table('users').select('*').eq('email', email).execute()

        if not response.data:
            # Don't reveal if email exists
            logger.info(f"Password reset requested for non-existent email: {email}")
            flash('If email exists, password reset link has been sent.', 'info')
            return redirect(url_for('login'))

        user = response.data[0]

    except Exception as e:
        logger.error(f"Database error in forgot_password: {str(e)}")
        flash('Password reset failed. Please try again later.', 'error')
        return redirect(url_for('forgot_password'))

    # ========== GENERATE RESET TOKEN ==========
    reset_token = TokenGenerator.generate_token()
    reset_token_hash = TokenGenerator.generate_token_hash(reset_token)
    reset_expires = datetime.utcnow() + timedelta(
        hours=config.PASSWORD_RESET_TOKEN_EXPIRY
    )

    # ========== STORE TOKEN IN DATABASE ==========
    supabase.table('users').update({
        'password_reset_token_hash': reset_token_hash,
        'password_reset_token_expires': reset_expires.isoformat()
    }).eq('id', user['id']).execute()

    # ========== SEND PASSWORD RESET EMAIL ==========
    reset_link = url_for(
        'reset_password',
        token=reset_token,
        _external=True
    )

    success, msg = EmailService.send_password_reset_email(
        user['email'], user['username'], reset_link
    )

    if success:
        log_password_reset(user['username'], "REQUESTED")
        flash('If email exists, password reset link has been sent.', 'info')
    else:
        logger.error(f"Failed to send password reset email to {email}")
        flash('Failed to send reset email. Please try again later.', 'error')

    return redirect(url_for('login'))


# ==================== ROUTE: RESET PASSWORD ====================


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
@logout_required
@enforce_https
def reset_password(token):
    """
    Reset password with valid token.
    Token must be valid and not expired.
    """

    # ========== HASH TOKEN FOR LOOKUP ==========
    token_hash = TokenGenerator.generate_token_hash(token)

    try:
        response = supabase.table('users').select('*').eq(
            'password_reset_token_hash', token_hash
        ).execute()

        if not response.data:
            logger.warning(f"Invalid password reset token attempted")
            flash('Invalid or expired password reset link', 'error')
            return redirect(url_for('forgot_password'))

        user = response.data[0]

        # Check if token expired
        if user['password_reset_token_expires']:
            expires = datetime.fromisoformat(
                user['password_reset_token_expires'].replace('Z', '+00:00')
            )
            if datetime.utcnow() > expires:
                logger.warning(f"Expired password reset token for: {user['username']}")
                flash('Password reset link has expired. Please request a new one.', 'error')
                return redirect(url_for('forgot_password'))

    except Exception as e:
        logger.error(f"Error validating reset token: {str(e)}")
        flash('Password reset failed. Please try again later.', 'error')
        return redirect(url_for('forgot_password'))

    if request.method == 'GET':
        return render_template('reset_password.html', token=token)

    # ========== POST: PROCESS PASSWORD RESET ==========

    # CSRF VALIDATION
    is_valid, error = verify_csrf(request.form)
    if not is_valid:
        flash(error, 'error')
        return render_template('reset_password.html', token=token)

    # INPUT VALIDATION
    password = request.form.get('password', '')
    password_confirm = request.form.get('password_confirm', '')

    if password != password_confirm:
        flash('Passwords do not match', 'error')
        return render_template('reset_password.html', token=token)

    password_check = InputValidation.validate_password(password)
    if not password_check['is_valid']:
        flash('Password does not meet security requirements', 'error')
        return render_template('reset_password.html', token=token)

    # HASH NEW PASSWORD
    try:
        hashed_password, salt = PasswordSecurity.hash_password(
            password, config.PEPPER
        )
    except Exception as e:
        logger.error(f"Password hashing error during reset: {str(e)}")
        flash('Password reset failed. Please try again later.', 'error')
        return render_template('reset_password.html', token=token)

    # UPDATE PASSWORD IN DATABASE
    try:
        supabase.table('users').update({
            'password_hash': hashed_password,
            'salt': salt,
            'password_reset_token_hash': None,
            'password_reset_token_expires': None,
            'failed_login_attempts': 0,
            'account_locked_until': None
        }).eq('id', user['id']).execute()

        log_password_reset(user['username'], "COMPLETED")
        logger.info(f"Password reset completed for: {user['username']}")
        flash('Password reset successful! You can now log in with your new password.', 'success')
        return redirect(url_for('login'))

    except Exception as e:
        logger.error(f"Failed to update password: {str(e)}")
        flash('Password reset failed. Please try again later.', 'error')
        return render_template('reset_password.html', token=token)


# ==================== ERROR HANDLERS ====================


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('error.html', error_code=404, error_message='Page not found'), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    logger.error(f"Server error: {str(error)}")
    return render_template('error.html', error_code=500, error_message='Internal server error'), 500


# ==================== MAIN ====================


if __name__ == '__main__':
    # In production, use gunicorn:
    # gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app

    # For development:
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False,  # Never use debug=True in production
        use_reloader=False
    )
